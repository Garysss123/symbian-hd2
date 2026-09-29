#!/usr/bin/env python3
"""Scale MatrixMenu's Nokia 360x640 client rectangle to the HTC Leo panel.

The framebuffer and CAknAppUiBase application rectangle are 480x800, but the
underlying CCoeScreenDevice still reports 360x640.  LafAppUi therefore returns
a 360x640-layout client rectangle (360x548 on the current status/CBA layout).
For MatrixMenu, scale those logical coordinates directly after the stock
toolbar and split-input reductions, preserving the chrome proportions.
"""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V1"
MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V2"

OLD = r'''        rect.iTl.iY = 0;
        }

    return rect;
    }'''

NEW = r'''        rect.iTl.iY = 0;
        }

    // HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V2
    // Keep the stock Laf reductions, then map the resulting Nokia 360x640
    // logical rectangle onto the known HTC Leo 480x800 framebuffer.  Do not
    // gate on CCoeScreenDevice: hardware 601 proves it still reports 360x640.
    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         rect.iTl.iX >= 0 && rect.iTl.iY >= 0 &&
         rect.iBr.iX <= 360 && rect.iBr.iY <= 640 &&
         !rect.IsEmpty() )
        {
        HtcleoEikAppInfoLog(0x0000B710u,
            ( (rect.iTl.iX & 0xFFFF) << 16 ) |
            ( rect.iTl.iY & 0xFFFF ),
            ( (TUint32)(rect.Width() & 0xFFFF) << 16 ) |
            (TUint32)(rect.Height() & 0xFFFF));
        rect.iTl.iX = ( rect.iTl.iX * 480 + 180 ) / 360;
        rect.iBr.iX = ( rect.iBr.iX * 480 + 180 ) / 360;
        rect.iTl.iY = ( rect.iTl.iY * 800 + 320 ) / 640;
        rect.iBr.iY = ( rect.iBr.iY * 800 + 320 ) / 640;
        HtcleoEikAppInfoLog(0x0000B711u,
            ( (rect.iTl.iX & 0xFFFF) << 16 ) |
            ( rect.iTl.iY & 0xFFFF ),
            ( (TUint32)(rect.Width() & 0xFFFF) << 16 ) |
            (TUint32)(rect.Height() & 0xFFFF));
        }

    return rect;
    }'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/uifw/EikStd/coctlsrc/EIKCOLIB.CPP"
    )
    if not path.is_file():
        raise SystemExit(f"missing EikStd source: {path}")

    text = path.read_text(encoding="latin-1")
    if OLD_MARKER in text:
        text = text.replace(OLD_MARKER, MARKER, 1)
        old_guard = r'''    const TSize htcleoPhysicalSize = env->ScreenDevice()->SizeInPixels();
    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         htcleoPhysicalSize == TSize( 480, 800 ) &&
'''
        new_guard = r'''    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
'''
        count = text.count(old_guard)
        if count != 1:
            raise SystemExit(
                "MatrixMenu client-rect V1 guard: expected one, "
                f"found {count}"
            )
        text = text.replace(old_guard, new_guard, 1)
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu client-rect anchor: expected one, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    homescreen_geometry = (
        "HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE_V1" in text
    )
    checks = {
        "single marker": text.count(MARKER) == 1,
        "old marker absent": OLD_MARKER not in text,
        "scaled shell scope": (
            text.count("htcleoGeometrySid == 0x101F4CD2u") == 1
            and text.count("htcleoGeometrySid == 0x102750F0u") == 1
            if homescreen_geometry
            else text.count(
                "RProcess().SecureId().iId == 0x101F4CD2u"
            ) == 1
        ),
        "no stale physical guard": (
            "htcleoPhysicalSize" not in text
            and "ScreenDevice()->SizeInPixels()" not in NEW
        ),
        "logical bounds": (
            "rect.iBr.iX <= 360" in text and "rect.iBr.iY <= 640" in text
        ),
        "proportional scale": all(
            token in text
            for token in (
                "rect.iTl.iX * 480", "rect.iBr.iX * 480",
                "rect.iTl.iY * 800", "rect.iBr.iY * 800",
            )
        ),
        "stages": all(
            text.count(f"0x0000B{stage}u") == 1
            for stage in ("710", "711")
        ),
        "stock client calculation retained": (
            text.count("TRect rect = LafAppUi::ClientRect( *env, *this );") == 1
            and text.count("toolbar->ReduceRect( rect );") == 1
        ),
        "no delay handle or fake success": all(
            token not in NEW
            for token in ("User::After", "RTimer", "SetHandle", "KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu client-rect scale verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_CLIENTRECT_SCALE="
        "matrixmenu-direct-logical-360x640-to-480x800-b710-b711"
    )


if __name__ == "__main__":
    main()
