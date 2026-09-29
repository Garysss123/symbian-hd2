#!/usr/bin/env python3
"""Keep MatrixMenu's CPU background in the unused grid area.

Hardware 600 draws the Haze CPU background over the full 360x548 view, but
CAknGridView::DrawUnusedViewPortion subsequently redraws the empty area through
the broken NVG path.  Only the five occupied icon cells retain Haze.  Skip that
second background clear for MatrixMenu; all other processes remain stock.
Iteration 729 also exposed ClearUnusedItemSpace's later per-cell skin/white
clear. MMWidgets paints the current damage before either pass; preserve it.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNGRID_MATRIXMENU_PRESERVE_CPU_BACKGROUND_V1"
CELL_MARKER = "HTCLEO_AKNGRID_MATRIXMENU_PRESERVE_EMPTY_CELLS_V1"

OLD = r'''void CAknGridView::DrawUnusedViewPortion() const
    {
    _AKNTRACE_FUNC_ENTER;
    TInt gapWidth = iGridDetails.iSizeBetweenItems.iWidth;'''

NEW = r'''void CAknGridView::DrawUnusedViewPortion() const
    {
    _AKNTRACE_FUNC_ENTER;
    // HTCLEO_AKNGRID_MATRIXMENU_PRESERVE_CPU_BACKGROUND_V1
    // MMWidgets has already painted the complete Haze background.  The stock
    // unused-area pass asks NVG for the same background again and its failed
    // conversion overwrites the empty grid area with transparent white.
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        _AKNTRACE_FUNC_EXIT;
        return;
        }
    TInt gapWidth = iGridDetails.iSizeBetweenItems.iWidth;'''

CELL_OLD = '''EXPORT_C void CAknGridView::ClearUnusedItemSpace(TInt aStartItemIndex, TInt aEndItemIndex) const
\t{
\t_AKNTRACE_FUNC_ENTER;'''

CELL_NEW = CELL_OLD + '''
    // HTCLEO_AKNGRID_MATRIXMENU_PRESERVE_EMPTY_CELLS_V1
    // CMmGrid/CMmWidgetContainer painted the cached wallpaper for this damage.
    // The stock empty-cell skin fallback must not clear it after the icons.
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        _AKNTRACE_FUNC_EXIT;
        return;
        }'''


def patch(text: str) -> str:
    for marker, old, new in ((MARKER, OLD, NEW), (CELL_MARKER, CELL_OLD, CELL_NEW)):
        if marker not in text:
            if text.count(old) != 1:
                raise SystemExit(f"AknGrid preserve-background anchor mismatch: {marker}")
            text = text.replace(old, new, 1)
    return text


def verify(text: str) -> None:
    if text.count(MARKER) != 1 or text.count(CELL_MARKER) != 1:
        raise SystemExit("AknGrid preserve-background markers missing")
    if text.count("RProcess().SecureId().iId == 0x101F4CD2u") != 2:
        raise SystemExit("AknGrid preserve-background SID guards changed")
    if CELL_NEW not in text or NEW not in text:
        raise SystemExit("AknGrid preserve-background early-return guards changed")
    start = text.index(CELL_OLD)
    end = text.index("EXPORT_C void CAknGridView::UpdateHScrollOffsetBasedOnTopItemIndex", start)
    section = text[start:end]
    if "AknsDrawUtils::Background( skin," not in section or "iGc->Clear(blankRect);" not in section:
        raise SystemExit("non-Matrix empty-cell rendering must remain stock")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/uifw/AvKon/src/akngridview.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing Avkon grid source: {path}")

    text = path.read_text(encoding="latin-1")
    text = patch(text)
    verify(text)

    checks = {
        "single marker": text.count(MARKER) == 1,
        "matrixmenu only": text.count(
            "RProcess().SecureId().iId == 0x101F4CD2u"
        ) == 2,
        "stock unused draw retained": (
            text.count("void CAknGridView::DrawUnusedViewPortion() const") == 1
            and text.count("AknsDrawUtils::BackgroundBetweenRects(") >= 2
        ),
        "narrow early return": (
            "if ( RProcess().SecureId().iId == 0x101F4CD2u )" in text
            and "TInt gapWidth = iGridDetails.iSizeBetweenItems.iWidth;" in text
        ),
        "no fake pixels window or delay": all(
            token not in NEW
            for token in ("SetBrushColor", "DrawRect", "CreateWindow", "User::After")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknGrid preserve-background verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_AKNGRID_CPU_BACKGROUND_PRESERVE="
        "matrixmenu-skip-broken-nvg-unused-area-redraw"
    )
    print("HTCLEO_AKNGRID_EMPTY_CELL_BACKGROUND=matrixmenu-preserve-mmwidgets-wallpaper-stock-other-apps")


if __name__ == "__main__":
    main()
