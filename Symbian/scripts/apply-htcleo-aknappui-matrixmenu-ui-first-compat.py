#!/usr/bin/env python3
"""Apply proven fixed-panel UI-first policy to MatrixMenu BaseConstructL.

Iteration 512 reaches CMmAppUi::ConstructL and stops inside the first
CAknAppUiBase::BaseConstructL call at 4D4D0302.  EikSrv already needs the same
fixed-screen, no-haptics and no-transition policy on HTC HD2.  Extend only
those safe policies to MatrixMenu, suppress its unused phone dialler launcher,
and enable the existing durable BaseConstruct checkpoints for MatrixMenu.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_MATRIXMENU_UI_FIRST_COMPAT_V1"

LOGGER_OLD = r'''    // Keep this shared Avkon DLL silent for every process except EikSrv.
    if (RProcess().SecureId().iId != 0x10003A4A)
        {
        return;
        }

    // HTCLEO_AKNAPPUI_LOG_FRONTIER_B51C_B520_V1
    // Iteration 483 hardware-proved every earlier checkpoint through B51B.
    // Keep only the five still-unproven BaseConstruct tail records so the
    // diagnostic file traffic does not become the boot blocker itself.
    if (aStage < 0x0000B51Cu || aStage > 0x0000B520u)
        {
        return;
        }
'''

LOGGER_NEW = r'''    // Keep this shared Avkon DLL silent outside EikSrv and MatrixMenu.
    const TUint32 htcleoLogSid = RProcess().SecureId().iId;
    const TBool htcleoLogEikSrv = htcleoLogSid == 0x10003A4Au;
    const TBool htcleoLogMatrixMenu = htcleoLogSid == 0x101F4CD2u;
    if (!htcleoLogEikSrv && !htcleoLogMatrixMenu)
        {
        return;
        }

    // HTCLEO_AKNAPPUI_LOG_FRONTIER_B51C_B520_V1
    // Preserve the already-minimised EikSrv scope.  MatrixMenu is at a new
    // BaseConstruct frontier, so retain B500-B520 until hardware brackets it.
    if (htcleoLogEikSrv &&
        (aStage < 0x0000B51Cu || aStage > 0x0000B520u))
        {
        return;
        }
'''

SCREEN_OLD = r'''    TInt htcleoScreenChangeResult = KErrNotSupported;
    if (!(RProcess().SecureId().iId == 0x10003A4A))
        {
        htcleoScreenChangeResult =
            iEikonEnv->RootWin().EnableScreenChangeEvents();
        }
'''

SCREEN_NEW = r'''    // HTCLEO_AKNAPPUI_MATRIXMENU_UI_FIRST_COMPAT_V1
    const TUint32 htcleoAppSid = RProcess().SecureId().iId;
    const TBool htcleoMatrixMenuUiFirst =
        htcleoAppSid == 0x101F4CD2u;
    const TBool htcleoUiFirstFixedPanel =
        htcleoAppSid == 0x10003A4Au || htcleoMatrixMenuUiFirst;
    TInt htcleoScreenChangeResult = KErrNotSupported;
    if (!htcleoUiFirstFixedPanel)
        {
        htcleoScreenChangeResult =
            iEikonEnv->RootWin().EnableScreenChangeEvents();
        }
'''

SIZE_OLD = r'''    const TBool htcleoUseFixedScreenSize =
        RProcess().SecureId().iId == 0x10003A4A;
'''

SIZE_NEW = r'''    const TBool htcleoUseFixedScreenSize =
        htcleoUiFirstFixedPanel;
'''

DIAL_OLD = r'''    if ( !iAppUiBaseExtension->iDiallerLauncher )
        {
'''

DIAL_NEW = r'''    // MatrixMenu has no telephony UI role on the non-cellular HTCLEO profile.
    if (!htcleoMatrixMenuUiFirst &&
        !iAppUiBaseExtension->iDiallerLauncher)
        {
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(source, LOGGER_OLD, LOGGER_NEW, "logger scope")
    source = replace_once(source, SCREEN_OLD, SCREEN_NEW, "screen policy")
    source = replace_once(source, SIZE_OLD, SIZE_NEW, "fixed size policy")
    source = replace_once(source, DIAL_OLD, DIAL_NEW, "dialler policy")
    return source


def verify(source: str) -> None:
    homescreen_trace = (
        "HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1" in source
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        "matrixmenu target": source.count("0x101F4CD2u") >= 2,
        "eiksrv target retained": source.count("0x10003A4Au") >= 2,
        "diagnostic logger gate": (
            source.count(
                "if (!htcleoLogEikSrv && !htcleoLogMatrixMenu &&"
            ) == 1
            and source.count("!htcleoLogHomeScreen") == 1
            if homescreen_trace
            else source.count(
                "if (!htcleoLogEikSrv && !htcleoLogMatrixMenu)"
            ) == 1
        ),
        "eiksrv frontier filter retained": source.count(
            "if (htcleoLogEikSrv &&"
        ) == 1,
        "matrixmenu full base trace": source.count(
            "MatrixMenu is at a new\n    // BaseConstruct frontier"
        ) == 1,
        "fixed panel policy": (
            source.count("const TBool htcleoUiFirstFixedPanel =") == 1
            and source.count("if (!htcleoUiFirstFixedPanel)") == 1
            and source.count("htcleoUiFirstFixedPanel;") == 1
        ),
        "safe optional policies inherit fixed panel": (
            source.count(
                "const TBool htcleoDeferTactileFeedback = htcleoUseFixedScreenSize;"
            ) == 1
            and source.count(
                "const TBool htcleoDeferTransitionEffects ="
            ) == 1
        ),
        "matrixmenu dialler bypass": source.count(
            "if (!htcleoMatrixMenuUiFirst &&"
        ) == 1,
        "stock calls retained for other processes": (
            source.count(
                "iEikonEnv->RootWin().EnableScreenChangeEvents();"
            ) == 1
            and source.count("CTouchFeedbackAdaptation::NewL();") == 1
            and source.count("CAknDiallerLauncher::NewL(") == 2
            and source.count(
                "iAvkonEnv->TransitionEvent(KAknTransitionEventFlags);"
            ) == 1
            and source.count(
                "iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);"
            ) == 1
        ),
        "old eiksrv-only forms absent": (
            "if (!(RProcess().SecureId().iId == 0x10003A4A))" not in source
            and "RProcess().SecureId().iId != 0x10003A4A" not in source
        ),
        "no timer display fake handle or fake success": all(
            token not in (LOGGER_NEW + SCREEN_NEW + SIZE_NEW + DIAL_NEW)
            for token in (
                "User::After", "RTimer", "HalFunction", "SetHandle",
                "KErrNone; // fake",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu UI-first compatibility verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root / "sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing Avkon input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNAPPUI_MATRIXMENU_UI_FIRST="
        "fixed-panel no-haptics no-transitions no-dialler b500-b520-log"
    )


if __name__ == "__main__":
    main()
