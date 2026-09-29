#!/usr/bin/env python3
"""Trace source/destination pixel signatures for HTC Leo CPU frames.

Iteration 588 proves MatrixMenu already owns focus, has visible real panes and
container, and successfully finishes WServ, yet the real five-icon frame is
still replaced.  Expand the existing DSPR log and record sparse deterministic
fingerprints of every mapped flicker source and copied RGB565 framebuffer.
This is observation-only: transfer, scanout, regions and completion semantics
remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


CAPACITY_MARKER = "HTCLEO_DSPR_LOG_CAPACITY_2048_V1"
SIGNATURE_MARKER = "HTCLEO_DISPLAY_FRAME_SIGNATURE_TRACE_V1"

OLD_CAPACITY = "\tif(r == KErrNone && position < (256 * 42))\n"
NEW_CAPACITY = r'''	// HTCLEO_DSPR_LOG_CAPACITY_2048_V1
	if(r == KErrNone && position < (2048 * 42))
'''

HELPER_ANCHOR = r'''// HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_V1
// HTCLEO_FLICKER_CPU_FRAMEBUFFER_EXPORT_V1
TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, TInt aScreenNumber)
    {'''

HELPER_REPLACEMENT = r'''// HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_V1
// HTCLEO_FLICKER_CPU_FRAMEBUFFER_EXPORT_V1
// HTCLEO_DISPLAY_FRAME_SIGNATURE_TRACE_V1
static void HtcleoSparseFrameSignature(const TUint8* aBytes, TInt aLength,
    TUint32& aHash, TUint32& aNonWhiteSamples)
    {
    aHash = 2166136261u;
    aNonWhiteSamples = 0u;
    if (!aBytes || aLength <= 0)
        {
        return;
        }
    // 257 is coprime to the usual 16/32-bpp row sizes and samples roughly
    // six thousand bytes from a 480x800 32-bpp frame.
    for (TInt offset = 0; offset < aLength; offset += 257)
        {
        const TUint8 value = aBytes[offset];
        aHash = (aHash ^ value) * 16777619u;
        if (value != 0xFFu)
            {
            ++aNonWhiteSamples;
            }
        }
    }

TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, TInt aScreenNumber)
    {'''

SOURCE_ANCHOR = r'''    if (result != KErrNone)
        {
        return result;
        }

    TPckgBuf<TScreenInfoV01> screenInfoPackage;'''

SOURCE_REPLACEMENT = r'''    if (result != KErrNone)
        {
        return result;
        }

    TUint32 htcleoSourceHash = 0u;
    TUint32 htcleoSourceNonWhite = 0u;
    HtcleoSparseFrameSignature(
        static_cast<const TUint8*>(sourceAddress),
        sourceStride * size.iHeight,
        htcleoSourceHash,
        htcleoSourceNonWhite);
    HtcleoDsprLog(0x00001930u, (TInt)htcleoSourceNonWhite,
        htcleoSourceHash);

    TPckgBuf<TScreenInfoV01> screenInfoPackage;'''

DESTINATION_ANCHOR = r'''    HtcleoDsprLog(0x00001904u, result, 480u * 800u * 2u);

    const TInt unmapResult = aTarget.Unmap();'''

DESTINATION_REPLACEMENT = r'''    HtcleoDsprLog(0x00001904u, result, 480u * 800u * 2u);

    TUint32 htcleoDestinationHash = 0u;
    TUint32 htcleoDestinationNonWhite = 0u;
    if (result == KErrNone)
        {
        HtcleoSparseFrameSignature(
            static_cast<const TUint8*>(screenInfo.iScreenAddress),
            480 * 800 * 2,
            htcleoDestinationHash,
            htcleoDestinationNonWhite);
        }
    HtcleoDsprLog(0x00001931u,
        result == KErrNone ? (TInt)htcleoDestinationNonWhite : result,
        htcleoDestinationHash);

    const TInt unmapResult = aTarget.Unmap();'''


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
    logger_path = component / "src/stdplugin.cpp"
    display_path = component / "src/displayrenderstage.cpp"
    if not logger_path.is_file() or not display_path.is_file():
        raise SystemExit("missing OpenWFC display sources")

    logger = logger_path.read_text(encoding="utf-8")
    display = display_path.read_text(encoding="utf-8")
    if CAPACITY_MARKER not in logger:
        logger = replace_once(
            logger, OLD_CAPACITY, NEW_CAPACITY, "DSPR capacity"
        )
    if SIGNATURE_MARKER not in display:
        display = replace_once(
            display, HELPER_ANCHOR, HELPER_REPLACEMENT, "signature helper"
        )
        display = replace_once(
            display, SOURCE_ANCHOR, SOURCE_REPLACEMENT, "source signature"
        )
        display = replace_once(
            display,
            DESTINATION_ANCHOR,
            DESTINATION_REPLACEMENT,
            "destination signature",
        )

    checks = {
        "capacity marker": logger.count(CAPACITY_MARKER) == 1,
        "capacity 2048": logger.count("position < (2048 * 42)") == 1,
        "old capacity gone": "position < (256 * 42)" not in logger,
        "signature marker": display.count(SIGNATURE_MARKER) == 1,
        "single helper": display.count("HtcleoSparseFrameSignature(") == (
            4
            if (
                "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V1" in display
                or "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V2" in display
                or "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V3" in display
            )
            else 3
        ),
        "signature stages": all(
            display.count(f"0x0000{stage:04X}u") == 1
            for stage in (0x1930, 0x1931)
        ),
        "transfer retained": display.count("SgUtils::TransferPixels(") == (
            2 if "HTCLEO_DISPLAY_REGION_AWARE_BLIT_V1" in display else 1
        ),
        "unmap retained": display.count("aTarget.Unmap()") == 1,
        "screen switch retained": display.count(
            "EDisplayHalWsSwitchOnScreen"
        ) == 1,
        "sparse only": (
            display.count("offset += 257") == 1
            and "User::After" not in HELPER_REPLACEMENT
            and "RTimer" not in HELPER_REPLACEMENT
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "display frame-signature verification failed: "
            + ", ".join(failed)
        )

    logger_path.write_text(logger, encoding="utf-8")
    display_path.write_text(display, encoding="utf-8")
    print(
        "HTCLEO_DISPLAY_FRAME_SIGNATURE="
        "source-1930-destination-1931-sparse-fnv-dspr2048"
    )


if __name__ == "__main__":
    main()
