#!/usr/bin/env python3
"""Preserve prior CPU framebuffer pixels across partial WServ updates.

Iteration 589 proves the RGB565 destination faithfully follows the WServ
flicker source, but that source contains only the layers redrawn in each dirty
region.  The HTC Leo CPU fallback incorrectly copied the whole temporary
target on every frame, replacing untouched layers with white.  Pass the real
update region into the existing helper and transfer only those rectangles into
the persistent legacy framebuffer, matching the stock downstream clipped draw
semantics.  No window, item or pixel content is fabricated.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_DISPLAY_REGION_AWARE_BLIT_V1"

OLD_DEFINITION = (
    "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, "
    "TInt aScreenNumber)\n"
)
NEW_DEFINITION = (
    "// HTCLEO_DISPLAY_REGION_AWARE_BLIT_V1\n"
    "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, "
    "TInt aScreenNumber, const TRegion* aUpdateRegion)\n"
)

OLD_DECLARATION = (
    "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, "
    "TInt aScreenNumber);\n"
)
NEW_DECLARATION = (
    "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, "
    "TInt aScreenNumber, const TRegion* aUpdateRegion);\n"
)

OLD_DISPLAY_CALL = (
    "? HtcleoCpuFramebufferBlit(*iRenderTarget, ScreenNumber())\n"
    "\t\t: KErrNone;"
)
NEW_DISPLAY_CALL = (
    "? HtcleoCpuFramebufferBlit(*iRenderTarget, ScreenNumber(),\n"
    "\t\t\tiUpdateRegion)\n"
    "\t\t: KErrNone;"
)

OLD_FLICKER_CALL = r'''? HtcleoCpuFramebufferBlit(
			*iRenderTarget, iNextScreenDevice->ScreenNumber())
		: KErrNone;'''
NEW_FLICKER_CALL = r'''? HtcleoCpuFramebufferBlit(
			*iRenderTarget, iNextScreenDevice->ScreenNumber(),
			iUpdateRegion)
		: KErrNone;'''

OLD_TRANSFER = r'''    else
        {
        const TRect fullScreen(TPoint(0, 0), size);
        result = SgUtils::TransferPixels(
            screenInfo.iScreenAddress,
            480 * 2,
            EUidPixelFormatRGB_565,
            sourceAddress,
            sourceStride,
            sourceFormat,
            fullScreen);
        }
    HtcleoDsprLog(0x00001904u, result, 480u * 800u * 2u);'''

NEW_TRANSFER = r'''    else
        {
        const TRect fullScreen(TPoint(0, 0), size);
        const TBool htcleoRegionValid =
            aUpdateRegion && !aUpdateRegion->CheckError()
            && !aUpdateRegion->IsEmpty();
        const TInt htcleoRectCount = htcleoRegionValid
            ? aUpdateRegion->Count() : 0;
        const TRect htcleoBounds = htcleoRegionValid
            ? aUpdateRegion->BoundingRect() : fullScreen;
        HtcleoDsprLog(0x00001932u, htcleoRectCount,
            ((TUint32)(htcleoBounds.Width() & 0xFFFF) << 16)
            | (TUint32)(htcleoBounds.Height() & 0xFFFF));

        result = KErrNone;
        if (htcleoRectCount > 0)
            {
            const TRect* htcleoRects = aUpdateRegion->RectangleList();
            for (TInt index = 0;
                    index < htcleoRectCount && result == KErrNone;
                    ++index)
                {
                TRect rect(htcleoRects[index]);
                rect.Intersection(fullScreen);
                if (rect.IsEmpty())
                    {
                    continue;
                    }
                TUint8* destination =
                    static_cast<TUint8*>(screenInfo.iScreenAddress)
                    + rect.iTl.iY * (480 * 2)
                    + rect.iTl.iX * 2;
                result = SgUtils::TransferPixels(
                    destination,
                    480 * 2,
                    EUidPixelFormatRGB_565,
                    sourceAddress,
                    sourceStride,
                    sourceFormat,
                    rect);
                }
            }
        else
            {
            result = SgUtils::TransferPixels(
                screenInfo.iScreenAddress,
                480 * 2,
                EUidPixelFormatRGB_565,
                sourceAddress,
                sourceStride,
                sourceFormat,
                fullScreen);
            }
        }
    HtcleoDsprLog(0x00001904u, result, 480u * 800u * 2u);'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/os/graphics/windowing/windowserverplugins/openwfc"
    display_path = component / "src/displayrenderstage.cpp"
    flicker_path = component / "src/fbrenderstage.cpp"
    display = display_path.read_text(encoding="utf-8")
    flicker = flicker_path.read_text(encoding="utf-8")

    if MARKER not in display:
        display = replace_once(
            display, OLD_DEFINITION, NEW_DEFINITION, "helper definition"
        )
        display = replace_once(
            display, OLD_DISPLAY_CALL, NEW_DISPLAY_CALL, "display call"
        )
        display = replace_once(
            display, OLD_TRANSFER, NEW_TRANSFER, "region transfer"
        )
        flicker = replace_once(
            flicker, OLD_DECLARATION, NEW_DECLARATION, "helper declaration"
        )
        flicker = replace_once(
            flicker, OLD_FLICKER_CALL, NEW_FLICKER_CALL, "flicker call"
        )

    checks = {
        "single marker": display.count(MARKER) == 1,
        "region helper": display.count(
            "TInt aScreenNumber, const TRegion* aUpdateRegion)"
        ) == 1,
        "matching declaration": flicker.count(
            "TInt aScreenNumber, const TRegion* aUpdateRegion);"
        ) == 1,
        "both real regions passed": (
            display.count("ScreenNumber(),\n\t\t\tiUpdateRegion)") == 1
            and flicker.count(
                "iNextScreenDevice->ScreenNumber(),\n\t\t\tiUpdateRegion)"
            ) == 1
        ),
        "rectangle list": (
            display.count("aUpdateRegion->RectangleList()") == 1
            and display.count("aUpdateRegion->Count()") == 1
            and display.count("rect.Intersection(fullScreen);") == 1
        ),
        "destination offset": (
            display.count("rect.iTl.iY * (480 * 2)") == 1
            and display.count("rect.iTl.iX * 2") == 1
        ),
        "one transfer site per branch": display.count(
            "SgUtils::TransferPixels("
        ) == 2,
        "region stage": display.count("0x00001932u") == 1,
        "signatures retained": all(
            display.count(f"0x0000{stage:04X}u") == 1
            for stage in (0x1930, 0x1931)
        ),
        "fallback full frame": display.count("fullScreen);") >= 2,
        "no fake wait clear or window": all(
            token not in NEW_TRANSFER
            for token in (
                "User::After",
                "RTimer",
                "Mem::Fill",
                "CreateWindow",
                "MakeVisible",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "display region-aware blit verification failed: "
            + ", ".join(failed)
        )

    display_path.write_text(display, encoding="utf-8")
    flicker_path.write_text(flicker, encoding="utf-8")
    print(
        "HTCLEO_DISPLAY_REGION_AWARE_BLIT="
        "dirty-rect-preserve-framebuffer-1932"
    )


if __name__ == "__main__":
    main()
