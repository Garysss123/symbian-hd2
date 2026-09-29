#!/usr/bin/env python3
"""Lay out and redraw the existing inner CEikCba for MatrixMenu.

Hardware 605 proves the outer button-group wrapper has a valid scaled rectangle
but submits no frame.  Hardware 606 re-runs the stock pane refresh and produces
only StatusPane frames: CEikCba is already visible and clean, so its normal
MakeVisible(ETrue) path skips DrawNow.  Hardware 607 proves that Rect() inside
MakeVisible is not a screen-space layout rectangle: scaling it there places the
CBA over the StatusPane.  Instead scale the real screen-space control-pane
layout in SetBoundingRect and SizeChangedInControlPane, then mark only the
existing MatrixMenu CBA as needing redraw.  The stock CEikCba draw, command
controls and skin remain in charge of all pixels and input behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V1"
MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V2"
BOUNDING_MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_BOUNDING_SCALE_V1"
SIZE_MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_SIZE_SCALE_V1"

OLD = r'''    if ( aVisible )
        {
        TBool redrawNeeded( EFalse );

        if ( AknLayoutUtils::PenEnabled() )'''

NEW = r'''    if ( aVisible )
        {
        // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V2
        // The CPU fallback has no z-composition.  If the full MatrixMenu grid
        // was drawn after this real CBA, force the existing inner control to
        // take its normal DrawNow path even though it is already visible.
        const TBool htcleoMatrixMenuCba =
            RProcess().SecureId().iId == 0x101F4CD2u;
        TBool redrawNeeded( htcleoMatrixMenuCba );

        if ( AknLayoutUtils::PenEnabled() )'''

V1_SCALING = r'''        const TBool htcleoMatrixMenuCba =
            RProcess().SecureId().iId == 0x101F4CD2u;
        TBool redrawNeeded( htcleoMatrixMenuCba );
        if ( htcleoMatrixMenuCba )
            {
            TRect htcleoCbaRect( Rect() );
            if ( htcleoCbaRect.iTl.iX >= 0 &&
                 htcleoCbaRect.iTl.iY >= 0 &&
                 htcleoCbaRect.iBr.iX <= 360 &&
                 htcleoCbaRect.iBr.iY <= 640 &&
                 !htcleoCbaRect.IsEmpty() )
                {
                htcleoCbaRect.iTl.iX =
                    ( htcleoCbaRect.iTl.iX * 480 + 180 ) / 360;
                htcleoCbaRect.iBr.iX =
                    ( htcleoCbaRect.iBr.iX * 480 + 180 ) / 360;
                htcleoCbaRect.iTl.iY =
                    ( htcleoCbaRect.iTl.iY * 800 + 320 ) / 640;
                htcleoCbaRect.iBr.iY =
                    ( htcleoCbaRect.iBr.iY * 800 + 320 ) / 640;
                SetRect( htcleoCbaRect );
                }
            }
'''

V2_REDRAW = r'''        const TBool htcleoMatrixMenuCba =
            RProcess().SecureId().iId == 0x101F4CD2u;
        TBool redrawNeeded( htcleoMatrixMenuCba );
'''

BOUNDING_OLD = r'''        cbarect.LayoutRect( screen, controlPane );
        
        SetRect( cbarect.Rect() );'''

BOUNDING_NEW = r'''        cbarect.LayoutRect( screen, controlPane );

        // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_BOUNDING_SCALE_V1
        // cbarect is screen-space here, so both position and size scale.
        TRect htcleoCbaScreenRect( cbarect.Rect() );
        if ( RProcess().SecureId().iId == 0x101F4CD2u &&
             htcleoCbaScreenRect.iTl.iX >= 0 &&
             htcleoCbaScreenRect.iTl.iY >= 0 &&
             htcleoCbaScreenRect.iBr.iX <= 360 &&
             htcleoCbaScreenRect.iBr.iY <= 640 &&
             !htcleoCbaScreenRect.IsEmpty() )
            {
            htcleoCbaScreenRect.iTl.iX =
                ( htcleoCbaScreenRect.iTl.iX * 480 + 180 ) / 360;
            htcleoCbaScreenRect.iBr.iX =
                ( htcleoCbaScreenRect.iBr.iX * 480 + 180 ) / 360;
            htcleoCbaScreenRect.iTl.iY =
                ( htcleoCbaScreenRect.iTl.iY * 800 + 320 ) / 640;
            htcleoCbaScreenRect.iBr.iY =
                ( htcleoCbaScreenRect.iBr.iY * 800 + 320 ) / 640;
            }
        SetRect( htcleoCbaScreenRect );'''

SIZE_OLD = r'''    TAknLayoutRect cbarect;
    cbarect.LayoutRect( screen, controlPane.LayoutLine() );
    TRect rect( cbarect.Rect().Size() );

    TRect posInScreen( cbarect.Rect() );'''

SIZE_NEW = r'''    TAknLayoutRect cbarect;
    cbarect.LayoutRect( screen, controlPane.LayoutLine() );
    // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_SIZE_SCALE_V1
    TRect htcleoCbaScreenRect( cbarect.Rect() );
    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         htcleoCbaScreenRect.iTl.iX >= 0 &&
         htcleoCbaScreenRect.iTl.iY >= 0 &&
         htcleoCbaScreenRect.iBr.iX <= 360 &&
         htcleoCbaScreenRect.iBr.iY <= 640 &&
         !htcleoCbaScreenRect.IsEmpty() )
        {
        htcleoCbaScreenRect.iTl.iX =
            ( htcleoCbaScreenRect.iTl.iX * 480 + 180 ) / 360;
        htcleoCbaScreenRect.iBr.iX =
            ( htcleoCbaScreenRect.iBr.iX * 480 + 180 ) / 360;
        htcleoCbaScreenRect.iTl.iY =
            ( htcleoCbaScreenRect.iTl.iY * 800 + 320 ) / 640;
        htcleoCbaScreenRect.iBr.iY =
            ( htcleoCbaScreenRect.iBr.iY * 800 + 320 ) / 640;
        }
    TRect rect( htcleoCbaScreenRect.Size() );

    TRect posInScreen( htcleoCbaScreenRect );'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/uifw/EikStd/coctlsrc/eikcba.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing CEikCba source: {path}")

    text = path.read_text(encoding="latin-1")
    if OLD_MARKER in text:
        text = text.replace(OLD_MARKER, MARKER, 1)
        if text.count(V1_SCALING) != 1:
            raise SystemExit("MatrixMenu CBA V1 coordinate migration mismatch")
        text = text.replace(V1_SCALING, V2_REDRAW, 1)
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu inner CBA redraw anchor: expected one, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)
    if BOUNDING_MARKER not in text:
        if text.count(BOUNDING_OLD) != 1:
            raise SystemExit("MatrixMenu CBA bounding anchor mismatch")
        text = text.replace(BOUNDING_OLD, BOUNDING_NEW, 1)
    if SIZE_MARKER not in text:
        if text.count(SIZE_OLD) != 1:
            raise SystemExit("MatrixMenu CBA size anchor mismatch")
        text = text.replace(SIZE_OLD, SIZE_NEW, 1)

    homescreen_geometry = (
        "HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE_V1" in text
    )
    checks = {
        "single marker": text.count(MARKER) == 1,
        "old marker absent": OLD_MARKER not in text,
        "layout markers": (
            text.count(BOUNDING_MARKER) == 1
            and text.count(SIZE_MARKER) == 1
        ),
        "scaled shell scope": (
            text.count("== 0x102750F0u") == 3
            and text.count("== 0x101F4CD2u") >= 3
            if homescreen_geometry
            else text.count(
                "RProcess().SecureId().iId == 0x101F4CD2u"
            ) == 3
        ),
        "screen layout scaled": (
            text.count("SetRect( htcleoCbaScreenRect );") == 1
            and text.count("TRect rect( htcleoCbaScreenRect.Size() );") == 1
            and text.count("TRect posInScreen( htcleoCbaScreenRect );") == 1
            and text.count("htcleoCbaScreenRect.iBr.iX <= 360") == 2
            and text.count("htcleoCbaScreenRect.iBr.iY <= 640") == 2
            and text.count("htcleoCbaScreenRect.iTl.iX * 480") == 2
            and text.count("htcleoCbaScreenRect.iTl.iY * 800") == 2
        ),
        "wrong local scaling absent": "htcleoCbaRect( Rect() )" not in text,
        "stock redraw condition retained": text.count(
            "if ( redrawNeeded || !isVisible || IsEmpty() )"
        ) == 1,
        "stock draw retained": text.count("DrawNow();") >= 1,
        "visibility flow retained": (
            text.count("CEikControlGroup::MakeVisible( aVisible );") == 2
            and text.count("ReportContentChangedEvent();") >= 1
        ),
        "no fabricated UI timing or normalization": all(
            token not in NEW
            for token in (
                "CreateWindowL", "SetCommandL", "AddCommand", "DrawRect",
                "TransferPixels", "User::After", "RTimer", "TRAP_IGNORE",
                "KErrNone",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu inner CBA redraw verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_CBA_INNER_REDRAW="
        "screen-bounding-scale-and-existing-drawnow-matrixmenu-only"
    )


if __name__ == "__main__":
    main()
