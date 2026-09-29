#!/usr/bin/env python3
"""Trace the real MatrixMenu CBA-to-HomeScreen transition without bypasses."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_SHELL_TRANSITION_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_once(
        text,
        """void CMmAppUi::HandleCommandL( TInt aCommand )
    {
    DEBUG((\"_Mm_:CMmAppUi::HandleCommandL IN\"));""",
        """void CMmAppUi::HandleCommandL( TInt aCommand )
    {
    // HTCLEO_MATRIXMENU_SHELL_TRANSITION_TRACE_V1
    const TUint32 htcleoCommandState =
        (iCurrentContainer ? 0x01u : 0u)
        | (iCurrentSuiteModel ? 0x02u : 0u)
        | ((iCurrentContainer && iCurrentContainer->IsVisible()) ? 0x04u : 0u)
        | (IsForeground() ? 0x08u : 0u);
    HtcleoMenuLog(0x4D4D1400u, aCommand, htcleoCommandState);
    DEBUG((\"_Mm_:CMmAppUi::HandleCommandL IN\"));""",
        "HandleCommandL entry",
    )
    text = replace_once(
        text,
        """    ClearTransitionFromEditModeFlag();

    switch( aCommand )""",
        """    ClearTransitionFromEditModeFlag();
    HtcleoMenuLog(0x4D4D1401u, KErrNone, htcleoCommandState);

    switch( aCommand )""",
        "command pre-switch",
    )
    text = replace_once(
        text,
        """            DEBUG((\"\\t_Mm_:EAknSoftkeyExit\"));
            ExitMatrix( EExitToPhone );""",
        """            DEBUG((\"\\t_Mm_:EAknSoftkeyExit\"));
            HtcleoMenuLog(0x4D4D1410u, aCommand, EExitToPhone);
            ExitMatrix( EExitToPhone );
            HtcleoMenuLog(0x4D4D1411u, KErrNone, EExitToPhone);""",
        "exit softkey",
    )
    text = replace_once(
        text,
        """        case EAknSoftkeyBack:
            {
            StartLayoutSwitchFullScreen( EMenuCloseFolderEffect );""",
        """        case EAknSoftkeyBack:
            {
            HtcleoMenuLog(0x4D4D1412u, aCommand,
                iCurrentSuiteModel ? (TUint32)iCurrentSuiteModel->ExitMode() : 0u);
            StartLayoutSwitchFullScreen( EMenuCloseFolderEffect );""",
        "back softkey",
    )
    text = replace_once(
        text,
        """        default:
            {
            ForwardEventToHNL( aCommand );""",
        """        default:
            {
            HtcleoMenuLog(0x4D4D141Fu, aCommand, htcleoCommandState);
            ForwardEventToHNL( aCommand );""",
        "default command",
    )
    text = replace_once(
        text,
        """        }
    DEBUG((\"_Mm_:CMmAppUi::HandleCommandL OUT\"));
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
void CMmAppUi::HandleBackCommandL()""",
        """        }
    HtcleoMenuLog(0x4D4D1402u, KErrNone, htcleoCommandState);
    DEBUG((\"_Mm_:CMmAppUi::HandleCommandL OUT\"));
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
void CMmAppUi::HandleBackCommandL()""",
        "HandleCommandL exit",
    )

    text = replace_once(
        text,
        """void CMmAppUi::ExitMatrix( TExitType aExitType )
    {
    DEBUG((\"_Mm_:CMmAppUi::ExitMatrix - IN\"));""",
        """void CMmAppUi::ExitMatrix( TExitType aExitType )
    {
    HtcleoMenuLog(0x4D4D1420u, aExitType,
        (iCurrentContainer ? 1u : 0u) | (IsForeground() ? 2u : 0u));
    DEBUG((\"_Mm_:CMmAppUi::ExitMatrix - IN\"));""",
        "ExitMatrix entry",
    )
    text = replace_once(
        text,
        """        TRAP_IGNORE( PrepareHomescreenForMatrixExitL() );
        //ShowHomescreenL( aExitType );
        //if we got exit cmd from OS, let's really exit.
        Exit();""",
        """        TRAPD(htcleoPrepareResult, PrepareHomescreenForMatrixExitL());
        HtcleoMenuLog(0x4D4D1421u, htcleoPrepareResult, aExitType);
        //ShowHomescreenL( aExitType );
        //if we got exit cmd from OS, let's really exit.
        HtcleoMenuLog(0x4D4D1422u, KErrNone, aExitType);
        Exit();
        HtcleoMenuLog(0x4D4D1423u, KErrNone, aExitType);""",
        "real exit path",
    )
    text = replace_once(
        text,
        """        GfxTransEffect::AbortFullScreen();
        iIsKastorEffectStarted = EFalse;
        StartLayoutSwitchFullScreen( AknTransEffect::EApplicationExit );

        TRAP_IGNORE( ShowHomescreenL( aExitType ) );
        TRAP_IGNORE( CleanupForExitL( EExitKeyRed ) );""",
        """        HtcleoMenuLog(0x4D4D1424u, KErrNone, aExitType);
        GfxTransEffect::AbortFullScreen();
        iIsKastorEffectStarted = EFalse;
        StartLayoutSwitchFullScreen( AknTransEffect::EApplicationExit );
        HtcleoMenuLog(0x4D4D1425u, KErrNone, aExitType);

        TRAPD(htcleoHomeResult, ShowHomescreenL( aExitType ));
        HtcleoMenuLog(0x4D4D1426u, htcleoHomeResult, aExitType);
        TRAPD(htcleoCleanupResult, CleanupForExitL( EExitKeyRed ));
        HtcleoMenuLog(0x4D4D1427u, htcleoCleanupResult, aExitType);""",
        "normal home transition",
    )
    text = replace_once(
        text,
        """    DEBUG((\"_Mm_:CMmAppUi::ExitMatrix - OUT\"));
    }""",
        """    HtcleoMenuLog(0x4D4D1428u, KErrNone, aExitType);
    DEBUG((\"_Mm_:CMmAppUi::ExitMatrix - OUT\"));
    }""",
        "ExitMatrix exit",
    )

    text = replace_once(
        text,
        """void CMmAppUi::ShowHomescreenL( TExitType  aExitType  )
    {
    TInt appToShowUid(0);""",
        """void CMmAppUi::ShowHomescreenL( TExitType  aExitType  )
    {
    HtcleoMenuLog(0x4D4D1430u, aExitType, 0u);
    TInt appToShowUid(0);""",
        "ShowHomescreen entry",
    )
    text = replace_once(
        text,
        """            User::LeaveIfError( RProperty::Get( KPSUidAiInformation,
                    KActiveIdleUid, appToShowUid ) );
            OpenAppL( TUid::Uid( appToShowUid ) );""",
        """            TInt htcleoIdleUidResult = RProperty::Get(
                    KPSUidAiInformation, KActiveIdleUid, appToShowUid );
            HtcleoMenuLog(0x4D4D1431u, htcleoIdleUidResult,
                (TUint32)appToShowUid);
            // HTCLEO_MATRIXMENU_HOMESCREEN_UID_BOOTSTRAP_V1
            // Stock SSM starts ailaunch in parallel with MatrixMenu.  Keep the
            // real P&S producer, but close the short first-boot race with the
            // product's fixed HomeScreen UID rather than hiding the menu over
            // an empty destination.
            if ( (htcleoIdleUidResult == KErrNotFound ||
                  htcleoIdleUidResult == KErrNotReady ||
                  appToShowUid == 0) )
                {
                appToShowUid = 0x102750F0;
                htcleoIdleUidResult = KErrNone;
                HtcleoMenuLog(0x4D4D1436u, KErrNone,
                    (TUint32)appToShowUid);
                }
            User::LeaveIfError( htcleoIdleUidResult );
            HtcleoMenuLog(0x4D4D1432u, KErrNone, (TUint32)appToShowUid);
            OpenAppL( TUid::Uid( appToShowUid ) );
            HtcleoMenuLog(0x4D4D1433u, KErrNone, (TUint32)appToShowUid);""",
        "active idle UID",
    )
    text = replace_once(
        text,
        """            ShowHomescreenL( EExitToIdle );
            }
            break;""",
        """            HtcleoMenuLog(0x4D4D1434u, KErrNone, EExitToIdle);
            ShowHomescreenL( EExitToIdle );
            HtcleoMenuLog(0x4D4D1435u, KErrNone, EExitToIdle);
            }
            break;""",
        "phone fallback",
    )
    text = replace_once(
        text,
        """        default:
            ShowHomescreenL( EExitToPhone );
        }
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
void CMmAppUi::PrepareHomescreenForMatrixExitL()""",
        """        default:
            ShowHomescreenL( EExitToPhone );
        }
    HtcleoMenuLog(0x4D4D143Fu, KErrNone, aExitType);
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
void CMmAppUi::PrepareHomescreenForMatrixExitL()""",
        "ShowHomescreen exit",
    )

    text = replace_once(
        text,
        """void CMmAppUi::OpenAppL( const TUid aUid )
    {
    DEBUG((\"_Mm_:CMmAppUi::OpenAppL - IN\"));""",
        """void CMmAppUi::OpenAppL( const TUid aUid )
    {
    HtcleoMenuLog(0x4D4D1440u, KErrNone, (TUint32)aUid.iUid);
    DEBUG((\"_Mm_:CMmAppUi::OpenAppL - IN\"));""",
        "OpenApp entry",
    )
    text = replace_once(
        text,
        """    TApaTask task = taskList->FindRootApp( aUid );
    delete taskList;

    if ( task.Exists() )""",
        """    TApaTask task = taskList->FindRootApp( aUid );
    delete taskList;
    const TBool htcleoTaskExists = task.Exists();
    HtcleoMenuLog(0x4D4D1441u,
        htcleoTaskExists ? KErrNone : KErrNotFound,
        htcleoTaskExists ? (TUint32)task.WgId() : 0u);

    if ( htcleoTaskExists )""",
        "existing task lookup",
    )
    text = replace_once(
        text,
        """        CAknSgcClient::MoveApp( task.WgId(), ESgcMoveAppToForeground );
        }
    else""",
        """        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
        CAknSgcClient::MoveApp( task.WgId(), ESgcMoveAppToForeground );
        HtcleoMenuLog(0x4D4D1443u, KErrNone, (TUint32)task.WgId());
        }
    else""",
        "existing task foreground",
    )
    text = replace_once(
        text,
        """        RApaLsSession lsSession;
        User::LeaveIfError( lsSession.Connect() );
        CleanupClosePushL( lsSession );
        User::LeaveIfError( lsSession.GetAppInfo( appInfo, aUid ) );
        User::LeaveIfError(
                lsSession.GetAppCapability( capabilityBuf, aUid ) );""",
        """        RApaLsSession lsSession;
        const TInt htcleoLsConnect = lsSession.Connect();
        HtcleoMenuLog(0x4D4D1444u, htcleoLsConnect, (TUint32)aUid.iUid);
        User::LeaveIfError( htcleoLsConnect );
        CleanupClosePushL( lsSession );
        const TInt htcleoAppInfo = lsSession.GetAppInfo( appInfo, aUid );
        HtcleoMenuLog(0x4D4D1445u, htcleoAppInfo,
            htcleoAppInfo == KErrNone ? (TUint32)appInfo.iFullName.Length() : 0u);
        User::LeaveIfError( htcleoAppInfo );
        const TInt htcleoCapability =
                lsSession.GetAppCapability( capabilityBuf, aUid );
        HtcleoMenuLog(0x4D4D1446u, htcleoCapability, (TUint32)aUid.iUid);
        User::LeaveIfError( htcleoCapability );""",
        "AppArc metadata",
    )
    text = replace_once(
        text,
        """        User::LeaveIfError( lsSession.StartApp( *cmdLine ) );

        CleanupStack::PopAndDestroy( cmdLine );""",
        """        HtcleoMenuLog(0x4D4D1447u, KErrNone,
            caps.iLaunchInBackground ? 1u : 0u);
        const TInt htcleoStartResult = lsSession.StartApp( *cmdLine );
        HtcleoMenuLog(0x4D4D1448u, htcleoStartResult,
            (TUint32)aUid.iUid);
        User::LeaveIfError( htcleoStartResult );

        CleanupStack::PopAndDestroy( cmdLine );""",
        "StartApp result",
    )
    text = replace_once(
        text,
        """        CleanupStack::PopAndDestroy( &lsSession );
        }

    DEBUG((\"_Mm_:CMmAppUi::OpenAppL - OUT\"));""",
        """        CleanupStack::PopAndDestroy( &lsSession );
        }

    HtcleoMenuLog(0x4D4D1449u, KErrNone, (TUint32)aUid.iUid);
    DEBUG((\"_Mm_:CMmAppUi::OpenAppL - OUT\"));""",
        "OpenApp exit",
    )
    return text


def verify(text: str) -> None:
    stages = [0x1400, 0x1401, 0x1402, 0x1410, 0x1411, 0x1412, 0x141F]
    stages += list(range(0x1420, 0x1429))
    stages += [0x1430, 0x1431, 0x1432, 0x1433, 0x1434, 0x1435, 0x1436, 0x143F]
    stages += list(range(0x1440, 0x144A))
    checks = {
        "marker": text.count(MARKER) == 1,
        "unique stages": all(text.count(f"0x4D4D{stage:04X}u") == 1 for stage in stages),
        "raw active-idle property": text.count("htcleoIdleUidResult") >= 6,
        "HomeScreen UID bootstrap": (
            text.count("HTCLEO_MATRIXMENU_HOMESCREEN_UID_BOOTSTRAP_V1") == 1
            and text.count("appToShowUid = 0x102750F0;") == 1
        ),
        "raw app info": text.count("htcleoAppInfo") >= 4,
        "raw capability": text.count("htcleoCapability") == 3,
        "raw StartApp": text.count("htcleoStartResult") == 3,
        "stock calls retained": all(
            text.count(call) >= 1
            for call in (
                "ExitMatrix( EExitToPhone );",
                "ShowHomescreenL( aExitType )",
                "OpenAppL( TUid::Uid( appToShowUid ) );",
                "lsSession.StartApp( *cmdLine )",
            )
        ),
        "no fabricated UI or wait": all(
            token not in text[text.index(MARKER) :]
            for token in ("User::After", "RTimer", "CreateWindowL", "SetPixel")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MatrixMenu shell trace failed: " + "; ".join(failed))


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
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_SHELL_TRANSITION_TRACE="
        "command-exit-idleuid-apparc-startapp-1400-1449"
    )


if __name__ == "__main__":
    main()
