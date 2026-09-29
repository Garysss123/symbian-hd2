#!/usr/bin/env python3
"""Correlate each CPU display frame with MatrixMenu/EikCore startup stage.

Iterations 590-591 prove the final white logical-screen redraw survives both
region-aware copying and retirement of MatrixMenu's empty view initialization.
Publish the latest MatrixMenu/EikCore stage through one MatrixMenu-owned P&S
integer and sample it at every CPU frame.  This changes no UI, scheduling,
render region or error policy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MENU_MARKER = "HTCLEO_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1"
EIK_MARKER = "HTCLEO_EIKCORE_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1"
DISPLAY_MARKER = "HTCLEO_DISPLAY_FRAME_STAGE_CORRELATION_V1"

MENU_INCLUDE = '#include <f32file.h>\n'
MENU_INCLUDE_NEW = '#include <f32file.h>\n#include <e32property.h>\n'
MENU_ENTRY = r'''void HtcleoMenuLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;'''
MENU_ENTRY_NEW = r'''void HtcleoMenuLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // HTCLEO_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1
    const TUid htcleoFrameStageCategory = {0x101F4CD2};
    const TUint htcleoFrameStageKey = 0x7F4D5702u;
    const TInt htcleoDefineResult = RProperty::Define(
        htcleoFrameStageCategory, htcleoFrameStageKey, RProperty::EInt);
    if (htcleoDefineResult == KErrNone
            || htcleoDefineResult == KErrAlreadyExists)
        {
        (void)RProperty::Set(
            htcleoFrameStageCategory, htcleoFrameStageKey, (TInt)aStage);
        }
    RFs fs;'''

EIK_ENTRY = r'''static void HtcleoEikCoreMatrixMenuTrace(TUint32 aStage, TInt aResult)
    {
    RFs fs;'''
EIK_ENTRY_NEW = r'''static void HtcleoEikCoreMatrixMenuTrace(TUint32 aStage, TInt aResult)
    {
    // HTCLEO_EIKCORE_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1
    const TUid htcleoFrameStageCategory = {0x101F4CD2};
    const TUint htcleoFrameStageKey = 0x7F4D5702u;
    const TInt htcleoDefineResult = RProperty::Define(
        htcleoFrameStageCategory, htcleoFrameStageKey, RProperty::EInt);
    if (htcleoDefineResult == KErrNone
            || htcleoDefineResult == KErrAlreadyExists)
        {
        (void)RProperty::Set(
            htcleoFrameStageCategory, htcleoFrameStageKey,
            (TInt)(0x4D4D0000u | (aStage & 0xFFFFu)));
        }
    RFs fs;'''

DISPLAY_INCLUDE = '#include <e32event_private.h>\n'
DISPLAY_INCLUDE_NEW = (
    '#include <e32event_private.h>\n'
    '#include <e32property.h>\n'
)
DISPLAY_ANCHOR = r'''    HtcleoDsprLog(0x00001930u, (TInt)htcleoSourceNonWhite,
        htcleoSourceHash);

    TPckgBuf<TScreenInfoV01> screenInfoPackage;'''
DISPLAY_REPLACEMENT = r'''    HtcleoDsprLog(0x00001930u, (TInt)htcleoSourceNonWhite,
        htcleoSourceHash);

    // HTCLEO_DISPLAY_FRAME_STAGE_CORRELATION_V1
    TInt htcleoUiStage = 0;
    const TInt htcleoUiStageResult = RProperty::Get(
        TUid::Uid(0x101F4CD2), 0x7F4D5702u, htcleoUiStage);
    HtcleoDsprLog(0x00001933u, htcleoUiStageResult,
        (TUint32)htcleoUiStage);

    TPckgBuf<TScreenInfoV01> screenInfoPackage;'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    menu_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/htcleomenulog.cpp"
    )
    eik_path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    display_path = (
        args.root
        / "sf/os/graphics/windowing/windowserverplugins/openwfc/src/displayrenderstage.cpp"
    )
    menu = menu_path.read_text(encoding="latin-1")
    eik = eik_path.read_text(encoding="latin-1")
    display = display_path.read_text(encoding="utf-8")

    if MENU_MARKER not in menu:
        menu = replace_once(menu, MENU_INCLUDE, MENU_INCLUDE_NEW, "menu include")
        menu = replace_once(menu, MENU_ENTRY, MENU_ENTRY_NEW, "menu breadcrumb")
    if EIK_MARKER not in eik:
        eik = replace_once(eik, EIK_ENTRY, EIK_ENTRY_NEW, "Eik breadcrumb")
    if DISPLAY_MARKER not in display:
        display = replace_once(
            display, DISPLAY_INCLUDE, DISPLAY_INCLUDE_NEW, "display include"
        )
        display = replace_once(
            display, DISPLAY_ANCHOR, DISPLAY_REPLACEMENT, "frame correlation"
        )

    checks = {
        "menu marker": menu.count(MENU_MARKER) == 1,
        "Eik marker": eik.count(EIK_MARKER) == 1,
        "display marker": display.count(DISPLAY_MARKER) == 1,
        "shared key": (
            menu.count("0x7F4D5702u") == 1
            and eik.count("0x7F4D5702u") == 1
            and display.count("0x7F4D5702u") == 1
        ),
        "shared category": (
            menu.count("0x101F4CD2") >= 1
            and eik.count("0x101F4CD2") >= 1
            and display.count("0x101F4CD2") == 1
        ),
        "set only in UI": (
            menu.count("RProperty::Set(") == 1
            and eik.count("htcleoFrameStageCategory, htcleoFrameStageKey") >= 2
        ),
        "display read only": (
            display.count("RProperty::Get(") == 1
            and display.count("RProperty::Set(") == 0
        ),
        "stage 1933": display.count("0x00001933u") == 1,
        "existing signatures": all(
            display.count(f"0x0000{stage:04X}u") == 1
            for stage in (0x1930, 0x1931, 0x1932)
        ),
        "no UI or scheduling mutation": all(
            token not in MENU_ENTRY_NEW + EIK_ENTRY_NEW + DISPLAY_REPLACEMENT
            for token in (
                "User::After",
                "RTimer",
                "MakeVisible",
                "CreateWindow",
                "ActivateTopView",
                "TransferPixels",
                "RequestComplete",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "UI/frame stage-correlation verification failed: "
            + ", ".join(failed)
        )

    menu_path.write_text(menu, encoding="latin-1")
    eik_path.write_text(eik, encoding="latin-1")
    display_path.write_text(display, encoding="utf-8")
    print(
        "HTCLEO_UI_FRAME_STAGE_CORRELATION="
        "matrixmenu-eikcore-property-7f4d5702-dspr1933"
    )


if __name__ == "__main__":
    main()
