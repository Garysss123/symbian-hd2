#!/usr/bin/env python3
"""Redraw MatrixMenu's real button-group control through its wrapper.

Hardware 608 proves the CBA screen-space contract is correct at (0,724),
480x76 and the wrapper reports visible, yet no CBA-sized render frame is
submitted.  Hardware 609 proves parameterless DrawDeferred/DrawNow is still
limited by the clean redraw region, and hardware 610 proves an explicit
DrawNow rectangle alone also creates no region.  For MatrixMenu only, reuse the
wrapper's existing SizeChanged rect contract, invalidate the owning real
window over a local full rectangle, then draw that rectangle on the actual
ButtonGroupAsControl.  No command, button, window, pixel or input event is
fabricated.
"""

from __future__ import annotations

import argparse
from pathlib import Path


V1_MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V1"
V2_MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V2"
MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V3"

OLD = r'''void CEikButtonGroupContainer::MakeVisible(TBool aVisible)
    {
    ButtonGroupAsControl()->MakeVisible(aVisible);
    CCoeControl::MakeVisible(aVisible);
    }'''

NEW = r'''void CEikButtonGroupContainer::MakeVisible(TBool aVisible)
    {
    CCoeControl* const htcleoRealButtonGroup = ButtonGroupAsControl();
    htcleoRealButtonGroup->MakeVisible(aVisible);
    CCoeControl::MakeVisible(aVisible);
    // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V3
    if ( aVisible &&
         RProcess().SecureId().iId == 0x101F4CD2u )
        {
        // Same wrapper-to-inner rectangle contract as SizeChanged().
        htcleoRealButtonGroup->SetRect(Rect());
        const TRect htcleoRedrawRect(
            TPoint(0, 0), htcleoRealButtonGroup->Size());
        RDrawableWindow* const htcleoDrawableWindow =
            htcleoRealButtonGroup->DrawableWindow();
        if ( htcleoDrawableWindow )
            {
            static_cast<RWindow*>(htcleoDrawableWindow)->Invalidate(
                htcleoRedrawRect);
            }
        htcleoRealButtonGroup->DrawDeferred();
        htcleoRealButtonGroup->DrawNow(htcleoRedrawRect);
        }
    }'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/uifw/EikStd/coctlsrc/EIKBTGPC.CPP"
    )
    if not path.is_file():
        raise SystemExit(f"missing button-group wrapper source: {path}")

    text = path.read_text(encoding="latin-1")
    protected_invalidate = r'''        htcleoRealButtonGroup->Window().Invalidate(htcleoRedrawRect);'''
    public_invalidate = r'''        RDrawableWindow* const htcleoDrawableWindow =
            htcleoRealButtonGroup->DrawableWindow();
        if ( htcleoDrawableWindow )
            {
            static_cast<RWindow*>(htcleoDrawableWindow)->Invalidate(
                htcleoRedrawRect);
            }'''
    if MARKER in text and protected_invalidate in text:
        if text.count(protected_invalidate) != 1:
            raise SystemExit("MatrixMenu CBA protected-window migration mismatch")
        text = text.replace(protected_invalidate, public_invalidate, 1)
    if V1_MARKER in text:
        text = text.replace(V1_MARKER, V2_MARKER, 1)
        old_draw = r'''        htcleoRealButtonGroup->DrawDeferred();
        htcleoRealButtonGroup->DrawNow();'''
        new_draw = r'''        htcleoRealButtonGroup->DrawDeferred();
        htcleoRealButtonGroup->DrawNow(
            TRect(TPoint(0, 0), htcleoRealButtonGroup->Size()));'''
        if text.count(old_draw) != 1:
            raise SystemExit("MatrixMenu CBA wrapper V1 draw anchor mismatch")
        text = text.replace(old_draw, new_draw, 1)
    if V2_MARKER in text:
        text = text.replace(V2_MARKER, MARKER, 1)
        old_explicit = r'''        htcleoRealButtonGroup->SetRect(Rect());
        htcleoRealButtonGroup->DrawDeferred();
        htcleoRealButtonGroup->DrawNow(
            TRect(TPoint(0, 0), htcleoRealButtonGroup->Size()));'''
        new_explicit = r'''        htcleoRealButtonGroup->SetRect(Rect());
        const TRect htcleoRedrawRect(
            TPoint(0, 0), htcleoRealButtonGroup->Size());
        RDrawableWindow* const htcleoDrawableWindow =
            htcleoRealButtonGroup->DrawableWindow();
        if ( htcleoDrawableWindow )
            {
            static_cast<RWindow*>(htcleoDrawableWindow)->Invalidate(
                htcleoRedrawRect);
            }
        htcleoRealButtonGroup->DrawDeferred();
        htcleoRealButtonGroup->DrawNow(htcleoRedrawRect);'''
        if text.count(old_explicit) != 1:
            raise SystemExit("MatrixMenu CBA wrapper V2 invalidate anchor mismatch")
        text = text.replace(old_explicit, new_explicit, 1)
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu CBA wrapper redraw anchor: expected one, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    homescreen_geometry = (
        "HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE_V1" in text
    )
    checks = {
        "single marker": text.count(MARKER) == 1,
        "old markers absent": (
            V1_MARKER not in text and V2_MARKER not in text
        ),
        "scaled shell scope": (
            text.count("htcleoCbaWrapperSid == 0x101F4CD2u") == 1
            and text.count("htcleoCbaWrapperSid == 0x102750F0u") == 1
            if homescreen_geometry
            else text.count(
                "RProcess().SecureId().iId == 0x101F4CD2u"
            ) == 1
        ),
        "real inner control": (
            text.count(
                "CCoeControl* const htcleoRealButtonGroup = "
                "ButtonGroupAsControl();"
            ) == 1
            and text.count("htcleoRealButtonGroup->SetRect(Rect());") == 1
            and text.count("htcleoRealButtonGroup->DrawableWindow();") == 1
            and text.count(
                "static_cast<RWindow*>(htcleoDrawableWindow)->Invalidate("
            ) == 1
            and text.count("htcleoRealButtonGroup->DrawDeferred();") == 1
            and text.count(
                "htcleoRealButtonGroup->DrawNow(htcleoRedrawRect);"
            ) == 1
        ),
        "stock visibility retained": (
            text.count("htcleoRealButtonGroup->MakeVisible(aVisible);") == 1
            and text.count("CCoeControl::MakeVisible(aVisible);") == 1
        ),
        "stock size contract retained": text.count(
            "ButtonGroupAsControl()->SetRect(rect);"
        ) == 1,
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
            "MatrixMenu CBA wrapper redraw verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_CBA_WRAPPER_REDRAW="
        "actual-window-invalidate-fullrect-drawnow-matrixmenu-only"
    )


if __name__ == "__main__":
    main()
