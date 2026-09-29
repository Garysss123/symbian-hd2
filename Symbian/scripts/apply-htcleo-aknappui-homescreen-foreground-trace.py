#!/usr/bin/env python3
"""Trace HomeScreen foreground handling in Avkon and its active view."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_HOMESCREEN_FOREGROUND_TRACE_V1"
LOGGER_PREREQUISITE = "HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1"
ROUTE_PREREQUISITE = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


APPUI_OLD = r'''EXPORT_C void CAknAppUi::HandleForegroundEventL(TBool aForeground)
    {
#ifdef RD_SCALABLE_UI_V2
    TVwsViewId viewId;
    TInt err = GetActiveViewId( viewId );
    if ( ( err == KErrNotFound || viewId.iAppUid == viewId.iViewUid ) && CurrentFixedToolbar() )
        {
        CurrentFixedToolbar()->HandleResourceChange( KAknToolbarSetVisible ); 
        }
#endif 
    if ( KeySounds() && IsForeground() ) // IsForeground() used because aForeground may already be out of date
        {
        KeySounds()->BringToForeground();
        }

#ifdef RD_SCALABLE_UI_V2
    if ( TouchPane() && aForeground )
        {
        TouchPane()->RefreshL();
        }

    if ( !aForeground )
        {  
        HandleStackedControlsResourceChange(KAknMessageFocusLost);            
        }
#endif

    if (aForeground && iExtension->iFlags[CAknAppUiExtension::EAppIsHiddenInBackground])
        {
        HideApplicationFromFSW(EFalse);
        iExtension->iFlags.Clear(CAknAppUiExtension::EAppIsHiddenInBackground);
        }
        
    CEikAppUi::HandleForegroundEventL(aForeground);
    }'''


APPUI_NEW = r'''EXPORT_C void CAknAppUi::HandleForegroundEventL(TBool aForeground)
    {
    const TBool htcleoHomeForegroundTrace =
        (RProcess().SecureId().iId == 0x102750F0u);
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C580u, aForeground,
            (TUint32)this);
#ifdef RD_SCALABLE_UI_V2
    TVwsViewId viewId;
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C581u, KErrNone, 0u);
    TInt err = GetActiveViewId( viewId );
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C582u, err,
            (TUint32)viewId.iViewUid.iUid);
    CAknToolbar* htcleoFixedToolbar = CurrentFixedToolbar();
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C583u, KErrNone,
            (TUint32)htcleoFixedToolbar);
    if ( ( err == KErrNotFound || viewId.iAppUid == viewId.iViewUid ) && htcleoFixedToolbar )
        {
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C584u, KErrNone,
                (TUint32)htcleoFixedToolbar);
        htcleoFixedToolbar->HandleResourceChange( KAknToolbarSetVisible );
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C585u, KErrNone,
                (TUint32)htcleoFixedToolbar);
        }
#endif 
    CAknKeySoundSystem* htcleoKeySounds = KeySounds();
    const TBool htcleoIsForeground = IsForeground();
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C586u, htcleoIsForeground,
            (TUint32)htcleoKeySounds);
    if ( htcleoKeySounds && htcleoIsForeground ) // IsForeground() used because aForeground may already be out of date
        {
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C587u, KErrNone,
                (TUint32)htcleoKeySounds);
        htcleoKeySounds->BringToForeground();
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C588u, KErrNone,
                (TUint32)htcleoKeySounds);
        }

#ifdef RD_SCALABLE_UI_V2
    CAknTouchPane* htcleoTouchPane = TouchPane();
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C589u, aForeground,
            (TUint32)htcleoTouchPane);
    if ( htcleoTouchPane && aForeground )
        {
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C58Au, KErrNone,
                (TUint32)htcleoTouchPane);
        htcleoTouchPane->RefreshL();
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C58Bu, KErrNone,
                (TUint32)htcleoTouchPane);
        }

    if ( !aForeground )
        {
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C58Cu, KErrNone, 0u);
        HandleStackedControlsResourceChange(KAknMessageFocusLost);
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C58Du, KErrNone, 0u);
        }
#endif

    const TBool htcleoHiddenBackground = aForeground &&
        iExtension->iFlags[CAknAppUiExtension::EAppIsHiddenInBackground];
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C58Eu, htcleoHiddenBackground,
            (TUint32)iExtension);
    if (htcleoHiddenBackground)
        {
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C58Fu, KErrNone,
                (TUint32)iExtension);
        HideApplicationFromFSW(EFalse);
        iExtension->iFlags.Clear(CAknAppUiExtension::EAppIsHiddenInBackground);
        if (htcleoHomeForegroundTrace)
            HtcleoAknAppUiBaseLog(0x0000C590u, KErrNone,
                (TUint32)iExtension);
        }

    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C591u, aForeground, 0u);
    CEikAppUi::HandleForegroundEventL(aForeground);
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C592u, aForeground, 0u);
    if (htcleoHomeForegroundTrace)
        HtcleoAknAppUiBaseLog(0x0000C593u, KErrNone,
            (TUint32)this);
    }'''


VIEW_OLD = '''EXPORT_C void CAknViewAppUi::HandleForegroundEventL( TBool aForeground )
\t{
\tCAknAppUi::HandleForegroundEventL( aForeground );
\t
\tif ( iView )
\t    {
\t\tiView->ProcessForegroundEventL( aForeground );
\t    }
\t}'''


VIEW_NEW = '''EXPORT_C void CAknViewAppUi::HandleForegroundEventL( TBool aForeground )
\t{
\tconst TBool htcleoHomeViewForegroundTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tif (htcleoHomeViewForegroundTrace)
\t\tHtcleoAknAppUiBaseLog(0x0000C598u, aForeground, (TUint32)iView);
\tif (htcleoHomeViewForegroundTrace)
\t\tHtcleoAknAppUiBaseLog(0x0000C599u, KErrNone, (TUint32)this);
\tCAknAppUi::HandleForegroundEventL( aForeground );
\tif (htcleoHomeViewForegroundTrace)
\t\tHtcleoAknAppUiBaseLog(0x0000C59Au, KErrNone, (TUint32)this);
\t
\tif (htcleoHomeViewForegroundTrace)
\t\tHtcleoAknAppUiBaseLog(0x0000C59Bu, iView ? 1 : 0,
\t\t\t(TUint32)iView);
\tif ( iView )
\t    {
\t\tif (htcleoHomeViewForegroundTrace)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C59Cu, aForeground,
\t\t\t\t(TUint32)iView);
\t\tiView->ProcessForegroundEventL( aForeground );
\t\tif (htcleoHomeViewForegroundTrace)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C59Du, aForeground,
\t\t\t\t(TUint32)iView);
\t    }
\tif (htcleoHomeViewForegroundTrace)
\t\tHtcleoAknAppUiBaseLog(0x0000C59Eu, KErrNone, (TUint32)iView);
\t}'''


def install_appui(text: str) -> str:
    text = replace_once(
        text,
        f"// {LOGGER_PREREQUISITE}\n",
        f"// {LOGGER_PREREQUISITE}\n// {MARKER}\n",
        "Avkon foreground marker",
    )
    return replace_once(text, APPUI_OLD, APPUI_NEW, "Avkon foreground handler")


def install_view(text: str) -> str:
    text = replace_once(
        text,
        '#include "aknViewAppUi.h"\n',
        '#include "aknViewAppUi.h"\n\n'
        f'// {MARKER}\n'
        'extern void HtcleoAknAppUiBaseLog(TUint32 aStage, TInt aResult,\n'
        '    TUint32 aDetail);\n',
        "view logger declaration",
    )
    return replace_once(text, VIEW_OLD, VIEW_NEW, "view foreground handler")


def verify(appui: str, view: str) -> None:
    checks = {
        "markers": appui.count(MARKER) == 1 and view.count(MARKER) == 1,
        "logger prerequisite": appui.count(LOGGER_PREREQUISITE) == 1,
        "route prerequisite": appui.count(ROUTE_PREREQUISITE) == 1,
        "AppUi stages": all(
            appui.count(f"0x0000C{stage:03X}u") == 1
            for stage in range(0x580, 0x594)
        ),
        "view stages": all(
            view.count(f"0x0000C{stage:03X}u") == 1
            for stage in range(0x598, 0x59F)
        ),
        "cross object logger": view.count(
            "extern void HtcleoAknAppUiBaseLog("
        ) == 1,
        "real foreground calls retained": (
            appui.count("CEikAppUi::HandleForegroundEventL(aForeground);") == 1
            and view.count(
                "CAknAppUi::HandleForegroundEventL( aForeground );"
            ) == 1
            and view.count(
                "iView->ProcessForegroundEventL( aForeground );"
            ) == 1
        ),
        "real optional calls retained": (
            appui.count("htcleoKeySounds->BringToForeground();") == 1
            and appui.count("htcleoTouchPane->RefreshL();") == 1
            and appui.count("HideApplicationFromFSW(EFalse);") >= 1
        ),
        "HomeScreen only": (
            appui.count("0x102750F0u") >= 1
            and view.count("0x102750F0u") == 1
        ),
        "no bypass or timer": all(
            token not in APPUI_NEW + VIEW_NEW
            for token in ("TRAP_IGNORE", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen Avkon foreground trace audit failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/classicui/uifw/AvKon/src"
    appui_path = base / "AknAppUi.cpp"
    view_path = base / "AknViewAppUi.cpp"
    for path in (appui_path, view_path):
        if not path.is_file():
            raise SystemExit(f"missing Avkon source: {path}")
    appui = appui_path.read_text(encoding="latin-1")
    view = view_path.read_text(encoding="latin-1")
    if MARKER not in appui:
        appui = install_appui(appui)
    if MARKER not in view:
        view = install_view(view)
    verify(appui, view)
    appui_path.write_text(appui, encoding="latin-1")
    view_path.write_text(view, encoding="latin-1")
    print(
        "HTCLEO_AKNAPPUI_HOMESCREEN_FOREGROUND_TRACE="
        "HSXML-C580-C593-view-C598-C59E-behavior-neutral"
    )


if __name__ == "__main__":
    main()
