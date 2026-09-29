#!/usr/bin/env python3
"""Invalidate and draw the complete real MatrixMenu grid window once.

Hardware 600/601 proves MMWidgets receives a full logical view rectangle, but
only occupied icon cells reach the framebuffer.  The WServ redraw region is
still item-sized.  Before the first committed frame, invalidate the complete
existing grid control with DrawDeferred and call the real widget DrawNow(rect);
no window or UI is fabricated.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION_V1"

OLD = r'''        iCurrentContainer->Widget()->View()->SetDisableRedraw(EFalse);
        HtcleoMenuLog(0x4D4D032Bu, KErrNone, 1u);
        iCurrentContainer->DrawNow();
        HtcleoMenuLog(0x4D4D032Cu, KErrNone, 1u);'''

NEW = r'''        iCurrentContainer->Widget()->View()->SetDisableRedraw(EFalse);
        HtcleoMenuLog(0x4D4D032Bu, KErrNone, 1u);

        // HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION_V1
        const TRect htcleoFullGridRect(
            TPoint(0, 0), iCurrentContainer->Widget()->Size());
        iCurrentContainer->Widget()->DrawDeferred();
        HtcleoMenuLog(0x4D4D0370u, KErrNone,
            ( (TUint32)(htcleoFullGridRect.Width() & 0xFFFF) << 16 ) |
            (TUint32)(htcleoFullGridRect.Height() & 0xFFFF));
        iCurrentContainer->Widget()->DrawNow(htcleoFullGridRect);
        const TInt htcleoFullGridFinish = iCoeEnv->WsSession().Finish();
        HtcleoMenuLog(0x4D4D0371u, htcleoFullGridFinish, 0x46554C4Cu);
        HtcleoMenuLog(0x4D4D032Cu, KErrNone, 1u);'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu AppUi source: {path}")

    text = path.read_text(encoding="latin-1")
    old_calls = (
        "        RDrawableWindow* htcleoGridWindow =\n"
        "            iCurrentContainer->Widget()->DrawableWindow();\n"
        "        if (htcleoGridWindow)\n"
        "            {\n"
        "            htcleoGridWindow->Invalidate(htcleoFullGridRect);\n"
        "            }\n"
        "        HtcleoMenuLog(0x4D4D0370u,\n"
        "            htcleoGridWindow ? KErrNone : KErrNotReady,\n"
    )
    deferred_call = (
        "        iCurrentContainer->Widget()->DrawDeferred();\n"
        "        HtcleoMenuLog(0x4D4D0370u, KErrNone,\n"
    )
    if MARKER in text and old_calls in text:
        text = text.replace(old_calls, deferred_call, 1)
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu full-grid anchor: expected one, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    checks = {
        "single marker": text.count(MARKER) == 1,
        "real widget window": text.count(
            "iCurrentContainer->Widget()->DrawDeferred();"
        ) == 1,
        "real bounded draw": text.count(
            "iCurrentContainer->Widget()->DrawNow(htcleoFullGridRect);"
        ) == 1,
        "finish retained": text.count("htcleoFullGridFinish") == 2,
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in (0x0370, 0x0371)
        ),
        "lifecycle retained": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in (0x032B, 0x032C)
        ),
        "no fake pixels window or delay": all(
            token not in NEW
            for token in (
                "CreateWindow", "Mem::Fill", "SetBrushColor",
                "User::After", "RTimer", "SetHandle",
            )
        ),
        "no protected Window call": (
            "Widget()->Window().Invalidate" not in text
            and "DrawableWindow" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu full-grid verification failed: " + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION="
        "real-widget-drawdeferred-fullrect-draw-finish-0370-0371"
    )


if __name__ == "__main__":
    main()
