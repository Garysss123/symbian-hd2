#!/usr/bin/env python3
"""Render the stock Haze screen gradient in the CPU MatrixMenu path.

Hardware 599 is byte-for-byte identical to 598r1 even after MMWidgets requests
Haze's real QsnBgScreen item.  The stock NVG render stage initializes, but its
DrawNvg result is ignored and failed vector conversion leaves transparent white
pixels.  Draw Haze's source-defined black-to-#52A2A5 background in the existing
MatrixMenu background draw, before the real grid items are painted.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MMWIDGETS_CPU_HAZE_BACKGROUND_V1"

INCLUDE_OLD = '#include "hnextbmpiconholder.h"\n'
INCLUDE_NEW = '#include "hnextbmpiconholder.h"\n#include "htcleommwlog.h"\n'

ANCHOR = r'''// -----------------------------------------------------------------------------
//
// -----------------------------------------------------------------------------
//
void CMmListBoxItemDrawer::DrawBackground( const TRect& aItemTextRect ) const
    {'''

HELPER_AND_ANCHOR = r'''// HTCLEO_MMWIDGETS_CPU_HAZE_BACKGROUND_V1
static TInt HtcleoDrawCpuHazeBackground(
        CGraphicsContext& aGc, const TRect& aRect )
    {
    if ( aRect.IsEmpty() )
        {
        return KErrArgument;
        }

    // Haze qsn_bg_screen.svg is black with a #52A2A5 glow at its upper edge.
    // Use 32 RGB bands over the upper third; the remainder stays true black.
    const TInt KFadeBands = 32;
    const TInt fadeHeight = Max( 1, aRect.Height() / 3 );
    aGc.SetPenStyle( CGraphicsContext::ENullPen );
    aGc.SetBrushStyle( CGraphicsContext::ESolidBrush );
    aGc.SetBrushColor( KRgbBlack );
    aGc.DrawRect( aRect );

    for ( TInt band = 0; band < KFadeBands; ++band )
        {
        const TInt remaining = KFadeBands - 1 - band;
        const TRgb colour(
            ( 0x52 * remaining ) / ( KFadeBands - 1 ),
            ( 0xA2 * remaining ) / ( KFadeBands - 1 ),
            ( 0xA5 * remaining ) / ( KFadeBands - 1 ) );
        const TInt top = aRect.iTl.iY +
            ( band * fadeHeight ) / KFadeBands;
        TInt bottom = aRect.iTl.iY +
            ( ( band + 1 ) * fadeHeight ) / KFadeBands;
        if ( bottom <= top )
            {
            bottom = top + 1;
            }
        aGc.SetBrushColor( colour );
        aGc.DrawRect( TRect(
            TPoint( aRect.iTl.iX, top ),
            TPoint( aRect.iBr.iX, Min( bottom, aRect.iBr.iY ) ) ) );
        }

    aGc.SetBrushStyle( CGraphicsContext::ENullBrush );
    aGc.SetPenStyle( CGraphicsContext::ESolidPen );
    return KErrNone;
    }

// -----------------------------------------------------------------------------
//
// -----------------------------------------------------------------------------
//
void CMmListBoxItemDrawer::DrawBackground( const TRect& aItemTextRect ) const
    {'''

DRAW_OLD = r'''        if( !bgDrawn )
            {
            iGc->Clear( aItemTextRect );
            }
#ifdef RD_UI_TRANSITION_EFFECTS_LIST'''

DRAW_NEW = r'''        HtcleoMmwLog(0x4D570170u,
            bgDrawn ? KErrNone : KErrNotFound,
            ( (TUint32)(aItemTextRect.Width() & 0xFFFF) << 16 ) |
            (TUint32)(aItemTextRect.Height() & 0xFFFF));

        // The native Haze/NVG path is retained above for later repair.  The
        // CPU result is drawn last because the current NVG failure reports a
        // successful background while leaving transparent-white pixels.
        const TInt htcleoCpuHazeResult =
            HtcleoDrawCpuHazeBackground( *iGc, aItemTextRect );
        HtcleoMmwLog(0x4D570171u, htcleoCpuHazeResult, 0x52A2A500u);
#ifdef RD_UI_TRANSITION_EFFECTS_LIST'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/mmwidgets/src/"
        "mmlistboxitemdrawer.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MMWidgets item drawer source: {path}")

    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        text = replace_once(text, INCLUDE_OLD, INCLUDE_NEW, "logger include")
        text = replace_once(
            text, ANCHOR, HELPER_AND_ANCHOR, "background helper"
        )
        text = replace_once(text, DRAW_OLD, DRAW_NEW, "CPU Haze draw")

    checks = {
        "single marker": text.count(MARKER) == 1,
        "logger include": text.count('#include "htcleommwlog.h"') == 1,
        "single helper": text.count("HtcleoDrawCpuHazeBackground(") == 2,
        "native background retained": text.count(
            "bgDrawn = AknsDrawUtils::Background("
        ) >= 2,
        "no white clear fallback": DRAW_OLD not in text,
        "source Haze colour": (
            "0x52 * remaining" in text
            and "0xA2 * remaining" in text
            and "0xA5 * remaining" in text
        ),
        "bounded draw": (
            "KFadeBands = 32" in text
            and "for ( TInt band = 0; band < KFadeBands; ++band )" in text
        ),
        "stages": all(
            text.count(f"0x4D57{stage:04X}u") == 1
            for stage in (0x0170, 0x0171)
        ),
        "no delay or fake window": all(
            token not in HELPER_AND_ANCHOR + DRAW_NEW
            for token in ("User::After", "RTimer", "CreateWindow")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MMWidgets CPU Haze verification failed: " + ", ".join(failed)
        )

    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_MMWIDGETS_CPU_HAZE_BACKGROUND="
        "source-black-52a2a5-32-band-software-draw-0170-0171"
    )


if __name__ == "__main__":
    main()
