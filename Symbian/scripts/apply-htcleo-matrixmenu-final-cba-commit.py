#!/usr/bin/env python3
"""Commit the real MatrixMenu CBA after the full grid redraw.

The CPU framebuffer fallback preserves per-window draw order rather than
performing OpenWFC z-composition.  MatrixMenu currently makes its real CBA
visible before drawing the full grid, so the grid overwrites the bottom
softkey layer even though Cba()->IsVisible() remains true.  Hardware 605 proves
that drawing the outer wrapper alone submits no frame.  Hardware 611 proves
that even invalidating the real CBA window submits no final frame while the
later-created normal-priority MatrixMenu grid fully occludes it.  Re-run the
stock pane refresh after the grid and raise only the existing MatrixMenu CBA
window to the standard high furniture priority before drawing it.  No button,
command, window, pixel or input event is fabricated.
"""

from __future__ import annotations

import argparse
from pathlib import Path


V1_MARKER = "HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V1"
V2_MARKER = "HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V2"
V3_MARKER = "HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V3"
MARKER = "HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V4"
PREREQUISITES = (
    "HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1",
    "HTCLEO_MATRIXMENU_FULL_GRID_INVALIDATION_V1",
)

OLD = r'''    iCurrentContainer->MakeVisible(ETrue);
    iCurrentContainer->DrawNow();
    HtcleoMenuLog(0x4D4D0353u, KErrNone,
        iCurrentContainer->IsVisible() ? 1u : 0u);
    const TInt htcleoForegroundFinish = htcleoWs.Finish();'''

NEW = r'''    iCurrentContainer->MakeVisible(ETrue);
    iCurrentContainer->DrawNow();
    HtcleoMenuLog(0x4D4D0353u, KErrNone,
        iCurrentContainer->IsVisible() ? 1u : 0u);

    // HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V4
    // The full grid is the last large client draw.  Recommit the existing
    // real CBA afterwards so the CPU fallback preserves the softkey layer.
    TRect htcleoCbaRect(Cba()->Rect());
    HtcleoMenuLog(0x4D4D0372u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    Cba()->SetBoundingRect(TRect(TPoint(0, 0), TSize(480, 800)));
    RDrawableWindow* const htcleoCbaWindow = Cba()->DrawableWindow();
    if (htcleoCbaWindow)
        {
        htcleoCbaWindow->SetOrdinalPosition(0, ECoeWinPriorityHigh);
        }
    HtcleoMenuLog(0x4D4D0375u,
        htcleoCbaWindow ? KErrNone : KErrNotFound,
        htcleoCbaWindow ? (TUint32)htcleoCbaWindow->OrdinalPosition() : 0u);
    Cba()->MakeVisible(ETrue);
    RefreshUiPanesL();
    Cba()->DrawNow();
    htcleoCbaRect = Cba()->Rect();
    HtcleoMenuLog(0x4D4D0373u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    HtcleoMenuLog(0x4D4D0374u,
        Cba()->IsVisible() ? KErrNone : KErrNotReady, 0u);
    const TInt htcleoForegroundFinish = htcleoWs.Finish();'''

V2_BLOCK = r'''    // HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V2
    // The full grid is the last large client draw.  Recommit the existing
    // real CBA afterwards so the CPU fallback preserves the softkey layer.
    TRect htcleoCbaRect(Cba()->Rect());
    HtcleoMenuLog(0x4D4D0372u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    if (htcleoCbaRect.iTl.iX >= 0 && htcleoCbaRect.iTl.iY >= 0 &&
        htcleoCbaRect.iBr.iX <= 360 && htcleoCbaRect.iBr.iY <= 640 &&
        !htcleoCbaRect.IsEmpty())
        {
        htcleoCbaRect.iTl.iX =
            (htcleoCbaRect.iTl.iX * 480 + 180) / 360;
        htcleoCbaRect.iBr.iX =
            (htcleoCbaRect.iBr.iX * 480 + 180) / 360;
        htcleoCbaRect.iTl.iY =
            (htcleoCbaRect.iTl.iY * 800 + 320) / 640;
        htcleoCbaRect.iBr.iY =
            (htcleoCbaRect.iBr.iY * 800 + 320) / 640;
        Cba()->SetRect(htcleoCbaRect);
        }
    Cba()->MakeVisible(ETrue);
    RefreshUiPanesL();
    Cba()->DrawNow();
    HtcleoMenuLog(0x4D4D0373u,
        Cba()->IsVisible() ? KErrNone : KErrNotReady,
        ( (TUint32)(Cba()->Rect().Width() & 0xFFFF) << 16 ) |
        (TUint32)(Cba()->Rect().Height() & 0xFFFF));'''

V3_BLOCK = r'''    // HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V3
    // The full grid is the last large client draw.  Recommit the existing
    // real CBA afterwards so the CPU fallback preserves the softkey layer.
    TRect htcleoCbaRect(Cba()->Rect());
    HtcleoMenuLog(0x4D4D0372u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    Cba()->SetBoundingRect(TRect(TPoint(0, 0), TSize(480, 800)));
    Cba()->MakeVisible(ETrue);
    RefreshUiPanesL();
    Cba()->DrawNow();
    htcleoCbaRect = Cba()->Rect();
    HtcleoMenuLog(0x4D4D0373u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    HtcleoMenuLog(0x4D4D0374u,
        Cba()->IsVisible() ? KErrNone : KErrNotReady, 0u);'''

V4_BLOCK = r'''    // HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT_V4
    // The full grid is the last large client draw.  Recommit the existing
    // real CBA afterwards so the CPU fallback preserves the softkey layer.
    TRect htcleoCbaRect(Cba()->Rect());
    HtcleoMenuLog(0x4D4D0372u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    Cba()->SetBoundingRect(TRect(TPoint(0, 0), TSize(480, 800)));
    RDrawableWindow* const htcleoCbaWindow = Cba()->DrawableWindow();
    if (htcleoCbaWindow)
        {
        htcleoCbaWindow->SetOrdinalPosition(0, ECoeWinPriorityHigh);
        }
    HtcleoMenuLog(0x4D4D0375u,
        htcleoCbaWindow ? KErrNone : KErrNotFound,
        htcleoCbaWindow ? (TUint32)htcleoCbaWindow->OrdinalPosition() : 0u);
    Cba()->MakeVisible(ETrue);
    RefreshUiPanesL();
    Cba()->DrawNow();
    htcleoCbaRect = Cba()->Rect();
    HtcleoMenuLog(0x4D4D0373u,
        ( (htcleoCbaRect.iTl.iX & 0xFFFF) << 16 ) |
        ( htcleoCbaRect.iTl.iY & 0xFFFF ),
        ( (TUint32)(htcleoCbaRect.Width() & 0xFFFF) << 16 ) |
        (TUint32)(htcleoCbaRect.Height() & 0xFFFF));
    HtcleoMenuLog(0x4D4D0374u,
        Cba()->IsVisible() ? KErrNone : KErrNotReady, 0u);'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu AppUi source: {path}")

    text = path.read_text(encoding="latin-1")
    if V1_MARKER in text:
        text = text.replace(V1_MARKER, V2_MARKER, 1)
        old_refresh = r'''    Cba()->MakeVisible(ETrue);
    Cba()->DrawNow();
    HtcleoMenuLog(0x4D4D0373u,'''
        new_refresh = r'''    Cba()->MakeVisible(ETrue);
    RefreshUiPanesL();
    Cba()->DrawNow();
    HtcleoMenuLog(0x4D4D0373u,'''
        if text.count(old_refresh) != 1:
            raise SystemExit("MatrixMenu final CBA V1 refresh anchor mismatch")
        text = text.replace(old_refresh, new_refresh, 1)
    if V2_MARKER in text:
        if text.count(V2_BLOCK) != 1:
            raise SystemExit("MatrixMenu final CBA V2 bounding migration mismatch")
        text = text.replace(V2_BLOCK, V3_BLOCK, 1)
    if V3_MARKER in text:
        if text.count(V3_BLOCK) != 1:
            raise SystemExit("MatrixMenu final CBA V3 ordinal migration mismatch")
        text = text.replace(V3_BLOCK, V4_BLOCK, 1)
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu final CBA commit anchor: expected one, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    checks = {
        "prerequisites": all(text.count(item) == 1 for item in PREREQUISITES),
        "single marker": text.count(MARKER) == 1,
        "old markers absent": (
            V1_MARKER not in text
            and V2_MARKER not in text
            and V3_MARKER not in text
        ),
        "real CBA only": (
            NEW.count("Cba()->SetBoundingRect(") == 1
            and NEW.count("Cba()->MakeVisible(ETrue);") == 1
            and NEW.count("RefreshUiPanesL();") == 1
            and NEW.count("Cba()->DrawNow();") == 1
            and NEW.count("Cba()->DrawableWindow();") == 1
            and NEW.count(
                "htcleoCbaWindow->SetOrdinalPosition(0, ECoeWinPriorityHigh);"
            ) == 1
        ),
        "bounding contract": (
            NEW.count(
                "Cba()->SetBoundingRect(TRect(TPoint(0, 0), TSize(480, 800)));"
            ) == 1
            and "Cba()->SetRect(htcleoCbaRect);" not in text
        ),
        "after grid before finish": text.count(NEW) == 1,
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in (0x0372, 0x0373, 0x0374, 0x0375)
        ),
        "no fabricated UI or timing": all(
            token not in NEW
            for token in (
                "CreateWindowL", "SetCommandL", "AddCommand", "DrawRect",
                "TransferPixels", "User::After", "RTimer", "TRAP_IGNORE",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu final CBA commit verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_FINAL_CBA_COMMIT="
        "high-priority-real-cba-refresh-after-grid-0372-0375"
    )


if __name__ == "__main__":
    main()
