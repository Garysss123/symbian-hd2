#!/usr/bin/env python3
"""Scale MatrixMenu status-pane subcontrols to HTC Leo coordinates.

MatrixMenu's client rectangle is now mapped from the Nokia 360x640 logical
layout to the 480x800 panel, but the status pane is an independent control tree.
Scale each stock layout-node rectangle in the existing visitor, preserving the
same relative position and size.  Other processes retain stock rectangles.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_SCALE_V1"

OLD = r'''            cont->SetRect( aNode->Rect() );
            cont->MakeVisible( iStatusPane->IsVisible() );'''

NEW = r'''            // HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_SCALE_V1
            TRect htcleoPaneRect( aNode->Rect() );
            if ( RProcess().SecureId().iId == 0x101F4CD2u &&
                 htcleoPaneRect.iTl.iX >= 0 && htcleoPaneRect.iTl.iY >= 0 &&
                 htcleoPaneRect.iBr.iX <= 360 &&
                 htcleoPaneRect.iBr.iY <= 640 &&
                 !htcleoPaneRect.IsEmpty() )
                {
                HtcleoStatusPaneLog(0x0000B712u,
                    ( (htcleoPaneRect.iTl.iX & 0xFFFF) << 16 ) |
                    ( htcleoPaneRect.iTl.iY & 0xFFFF ),
                    ( (TUint32)(htcleoPaneRect.Width() & 0xFFFF) << 16 ) |
                    (TUint32)(htcleoPaneRect.Height() & 0xFFFF));
                htcleoPaneRect.iTl.iX =
                    ( htcleoPaneRect.iTl.iX * 480 + 180 ) / 360;
                htcleoPaneRect.iBr.iX =
                    ( htcleoPaneRect.iBr.iX * 480 + 180 ) / 360;
                htcleoPaneRect.iTl.iY =
                    ( htcleoPaneRect.iTl.iY * 800 + 320 ) / 640;
                htcleoPaneRect.iBr.iY =
                    ( htcleoPaneRect.iBr.iY * 800 + 320 ) / 640;
                HtcleoStatusPaneLog(0x0000B713u,
                    ( (htcleoPaneRect.iTl.iX & 0xFFFF) << 16 ) |
                    ( htcleoPaneRect.iTl.iY & 0xFFFF ),
                    ( (TUint32)(htcleoPaneRect.Width() & 0xFFFF) << 16 ) |
                    (TUint32)(htcleoPaneRect.Height() & 0xFFFF));
                }
            cont->SetRect( htcleoPaneRect );
            cont->MakeVisible( iStatusPane->IsVisible() );'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/uifw/EikStd/coctlsrc/eikspane.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing status-pane source: {path}")

    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu status-pane scale anchor: expected one, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    homescreen_geometry = (
        "HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE_V1" in text
    )
    checks = {
        "single marker": text.count(MARKER) == 1,
        "scaled shell scope": (
            text.count("htcleoPaneSid == 0x101F4CD2u") == 1
            and text.count("htcleoPaneSid == 0x102750F0u") == 1
            if homescreen_geometry
            else text.count(
                "if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n"
                "                 htcleoPaneRect.iTl.iX >= 0"
            ) == 1
        ),
        "logical bounds": (
            "htcleoPaneRect.iBr.iX <= 360" in text
            and "htcleoPaneRect.iBr.iY <= 640" in text
        ),
        "proportional scale": all(
            token in text
            for token in (
                "htcleoPaneRect.iTl.iX * 480",
                "htcleoPaneRect.iBr.iX * 480",
                "htcleoPaneRect.iTl.iY * 800",
                "htcleoPaneRect.iBr.iY * 800",
            )
        ),
        "scaled rect used": text.count("cont->SetRect( htcleoPaneRect );") == 1,
        "old direct rect absent": OLD not in text,
        "stages": all(
            text.count(f"0x0000B{stage}u") == 1
            for stage in ("712", "713")
        ),
        "stock visibility retained": text.count(
            "cont->MakeVisible( iStatusPane->IsVisible() );"
        ) == 1,
        "no fake control pixels or delay": all(
            token not in NEW
            for token in (
                "CreateWindow", "SetHandle", "SetBrushColor", "DrawRect",
                "User::After", "RTimer",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu status-pane scale verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_STATUSPANE_SCALE="
        "subpane-logical-360x640-to-480x800-b712-b713"
    )


if __name__ == "__main__":
    main()
