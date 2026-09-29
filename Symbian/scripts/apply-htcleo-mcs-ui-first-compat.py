#!/usr/bin/env python3
"""Keep MenuContent's initial app-list path while deferring Nokia-only services.

The first mandatory MatrixMenu GetList currently starts mcsmenuserver.exe, but
the server dies while constructing its per-content engine.  That constructor
eagerly connects SAT, widget, running-app, DRM, folder-notification and other
dynamic services which are not required to build the first native/Java menu.

This transform keeps the menu engine, AppArc session/scanner, attribute cache,
MMC history and the real GetList implementation.  It defers only dynamic or
hardware-specific services and adds NULL-safe fallbacks at their direct use
sites.  The server-owned MCSLOG is diagnostic only and never changes control
flow.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MARKER = "HTCLEO_MCS_UI_FIRST_COMPAT_V1"
LIFETIME_MARKER = "HTCLEO_MCS_ENGINE_PERSISTENT_LIFETIME_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, new: str, label: str) -> str:
    updated, count = re.subn(pattern, new, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return updated


LOGGER = r'''
#include <f32file.h>

// HTCLEO_MCS_UI_FIRST_COMPAT_V1
static void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x200113DDu)
        {
        return;
        }
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }
    _LIT(KHtcleoMcsDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMcsPath, "C:\\Symbian3\\MCSLOG.TXT");
    r = fs.MkDirAll(KHtcleoMcsDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }
    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMcsPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMcsPath, EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoMcsPrefix, "HTCLEO_MCS ");
        TBuf8<96> record;
        record.Append(KHtcleoMcsPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        file.Write(record);
        }
    file.Close();
    fs.Close();
    }
'''


def patch_engine(text: str) -> str:
    text = replace_once(
        text,
        '#include <mcsmenufilter.h>\n',
        '#include <mcsmenufilter.h>\n' + LOGGER,
        "MCS logger include",
    )
    text = replace_once(
        text,
        """void CMenuSrvEng::ConstructL( const TDesC& aContentName )
    {
    if ( !aContentName.Length() )
        {
        // A name is required - only dead engines have empty name.
        User::Leave( KErrArgument );
        }

    iContentName.CreateL( aContentName );
    iTimedClose = CTimeout::NewL
        ( CActive::EPriorityStandard, TCallBack( CloseSrvEng, (TAny*)this ) );
    iEng = CMenuEng::NewL( iContentName, *this );
    if ( iContentName.Length() )
        {
        iCMenuSrvEngUtils = CMenuSrvEngUtils::NewL( *iEng );

        iCacheHandler = CMcsCacheHandler::NewL( *iEng, *iCMenuSrvEngUtils );

        iMcsSatMonitor = CMcsSatMonitor::NewL( *iEng );
    #ifndef __TEST_DISABLE_APPSCAN
        // Start automatic update.
        iAppScanner = CMenuSrvAppScanner::NewL( *iEng, *iCMenuSrvEngUtils );
        // Start automatic update.
        iFolderNotifier =  CMenuSrvFolderCrNotifier::NewL( *iEng );
    #endif
        iRunningAppsHandler = CMcsRunningAppsHandler::NewL(
                *iEng, *iCacheHandler );

        iDrmHander = CMcsDrmHandler::NewL(
                *this, *iCMenuSrvEngUtils, *iCacheHandler );

        iChildrenHandler = CMcsChildrenHandler::NewL( *this, *iCacheHandler);

        iTimedClose->Cancel();
        iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );
        }
    }
""",
        """void CMenuSrvEng::ConstructL( const TDesC& aContentName )
    {
    HtcleoMcsLog(0x4D430100u, KErrNone,
        (TUint32)aContentName.Length());
    if ( !aContentName.Length() )
        {
        // A name is required - only dead engines have empty name.
        User::Leave( KErrArgument );
        }

    iContentName.CreateL( aContentName );
    HtcleoMcsLog(0x4D430101u, KErrNone, 0u);
    iTimedClose = CTimeout::NewL
        ( CActive::EPriorityStandard, TCallBack( CloseSrvEng, (TAny*)this ) );
    HtcleoMcsLog(0x4D430102u, KErrNone, 0u);
    iEng = CMenuEng::NewL( iContentName, *this );
    HtcleoMcsLog(0x4D430103u, KErrNone, iEng ? 1u : 0u);
    if ( iContentName.Length() )
        {
        HtcleoMcsLog(0x4D430110u, KErrNone, 0u);
        iCMenuSrvEngUtils = CMenuSrvEngUtils::NewL( *iEng );
        HtcleoMcsLog(0x4D430111u, KErrNone,
            iCMenuSrvEngUtils ? 1u : 0u);

        iCacheHandler = CMcsCacheHandler::NewL( *iEng, *iCMenuSrvEngUtils );
        HtcleoMcsLog(0x4D430112u, KErrNone,
            iCacheHandler ? 1u : 0u);

        // SIM Application Toolkit is absent and irrelevant on HTC Leo.
        iMcsSatMonitor = NULL;
        HtcleoMcsLog(0x4D430120u, KErrNotSupported, 0x53415420u);
    #ifndef __TEST_DISABLE_APPSCAN
        // AppArc scanning is core: it supplies native and Java applications.
        HtcleoMcsLog(0x4D430121u, KErrNone, 0u);
        iAppScanner = CMenuSrvAppScanner::NewL( *iEng, *iCMenuSrvEngUtils );
        HtcleoMcsLog(0x4D430122u, KErrNone,
            iAppScanner ? 1u : 0u);
        // Runtime folder-repository notifications are not initial menu data.
        iFolderNotifier = NULL;
        HtcleoMcsLog(0x4D430123u, KErrNotSupported, 0x464F4C44u);
    #endif
        // Dynamic running-state, DRM and child-count observers are deferred;
        // the real menu tree, AppArc scan, cache and GetList remain active.
        iRunningAppsHandler = NULL;
        HtcleoMcsLog(0x4D430124u, KErrNotSupported, 0x52554E20u);
        iDrmHander = NULL;
        HtcleoMcsLog(0x4D430125u, KErrNotSupported, 0x44524D20u);
        iChildrenHandler = NULL;
        HtcleoMcsLog(0x4D430126u, KErrNotSupported, 0x43484C44u);

        iTimedClose->Cancel();
        iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );
        HtcleoMcsLog(0x4D430127u, KErrNone, 0u);
        }
    }
""",
        "CMenuSrvEng ConstructL",
    )
    text = replace_once(
        text,
        """void CMenuSrvEng::GetRunningAppsL( RArray<TUid>& aArray )
    {
\tiRunningAppsHandler->GetRunningAppsL( aArray );
\t}
""",
        """void CMenuSrvEng::GetRunningAppsL( RArray<TUid>& aArray )
    {
    if ( iRunningAppsHandler )
        {
        iRunningAppsHandler->GetRunningAppsL( aArray );
        }
    }
""",
        "running-app list guard",
    )
    text = replace_once(
        text,
        """    else if ( KErrNone == aAttrName.Compare( KMenuAttrDrmProtection ) )
        {
        AppDrmProtectionL( aId, aAttrExists, aAttrVal );
        }
""",
        """    else if ( KErrNone == aAttrName.Compare( KMenuAttrDrmProtection ) )
        {
        // DRM status is not part of the HTC Leo UI milestone.  Avoid the
        // Nokia DRM/Java rights servers while keeping the item itself.
        aAttrExists = EFalse;
        aAttrVal = KNullDesC();
        }
""",
        "DRM attribute defer",
    )
    text = replace_once(
        text,
        """ void CMenuSrvEng::GetAppRunningL( TInt aId, TBool& aExists, TDes& aAttrVal )
\t {
\t aExists = iRunningAppsHandler->GetRunningStatusL(aId);
\t if(aExists)
\t\t {
\t\t aAttrVal.Append(KRunning16());
\t\t }
\t else
\t\t {
\t\t aAttrVal.Append(KNullDesC());
\t\t }
\t }
""",
        """ void CMenuSrvEng::GetAppRunningL( TInt aId, TBool& aExists, TDes& aAttrVal )
\t {
     aExists = EFalse;
     if ( iRunningAppsHandler )
         {
         aExists = iRunningAppsHandler->GetRunningStatusL(aId);
         }
\t if(aExists)
\t\t {
\t\t aAttrVal.Append(KRunning16());
\t\t }
\t else
\t\t {
\t\t aAttrVal.Append(KNullDesC());
\t\t }
\t }
""",
        "running-status guard",
    )
    return text


def patch_utils(text: str) -> str:
    text = replace_once(
        text,
        """void CMenuSrvEngUtils::ConstructL()
    {
    User::LeaveIfError( iApaLsSession.Connect() );
    User::LeaveIfError( iWidgetSession.Connect() );
    User::LeaveIfError( iWsSession.Connect() );
    iSatHandler = CMcsSatHandler::NewL();
    }
""",
        """void CMenuSrvEngUtils::ConstructL()
    {
    // AppArc is the only initial-menu dependency.  Web widgets, a private
    // WServ session and SAT metadata are not needed for native/Java entries.
    User::LeaveIfError( iApaLsSession.Connect() );
    iWidgetSession.Close();
    iWsSession.Close();
    iSatHandler = NULL;
    }
""",
        "CMenuSrvEngUtils ConstructL",
    )
    text = replace_once(
        text,
        """TInt CMenuSrvEngUtils::GetSatAppInfo( TApaAppInfo& aAppInfo ) const
    {
    TBuf<KApaMaxAppCaption> aBuf;
    TInt err = iSatHandler->GetName( aBuf );
    if( err == KErrNone )
        {
        aAppInfo.iShortCaption = aBuf;
        aAppInfo.iCaption = aBuf;
        }
    return err;
    }
""",
        """TInt CMenuSrvEngUtils::GetSatAppInfo( TApaAppInfo& aAppInfo ) const
    {
    if ( !iSatHandler )
        {
        return KErrNotSupported;
        }
    TBuf<KApaMaxAppCaption> aBuf;
    TInt err = iSatHandler->GetName( aBuf );
    if( err == KErrNone )
        {
        aAppInfo.iShortCaption = aBuf;
        aAppInfo.iCaption = aBuf;
        }
    return err;
    }
""",
        "SAT info guard",
    )
    text = replace_once(
        text,
        """        else if( iWidgetSession.IsWidget( appInfo.iUid ) )
            {
            appAtributes->SetAppType( CMenuEngObject::EWidgetApp );
            }
        else
""",
        """        else
""",
        "widget classification defer",
    )
    return text


def patch_scanner(text: str) -> str:
    text = replace_once(
        text,
        """\tiCenRepNotifyHandlerHiddenApps = CCenRepNotifyHandler::NewL(
\t    *this, *iCenRepSession,
\t\tCCenRepNotifyHandler::EStringKey, KMenuHideApplication );
\tiCenRepNotifyHandlerCPHiddenApps = CCenRepNotifyHandler::NewL(
\t    *this, *iCenRepSession,
\t\tCCenRepNotifyHandler::EStringKey, KMenuHideCPApplication );

\tiCenRepNotifyHandlerCPHiddenFolders = CCenRepNotifyHandler::NewL(
\t    *this, *iCenRepSession,
\t\tCCenRepNotifyHandler::EStringKey, KMenuHideCPFolder );

\tiCenRepNotifyHandlerHiddenApps->StartListeningL();
\tiCenRepNotifyHandlerCPHiddenApps->StartListeningL();
\tiCenRepNotifyHandlerCPHiddenFolders->StartListeningL();

\tiMcsSatNotifier = CMcsSatNotifier::NewL(
\t                this, KCRUidMenu, KMenuShowSatUI );

\tiFreeSpaceObserver = CMcsFreeSpaceObserver::NewL( *this );
""",
        """    // Keep the repository itself for the initial hide lists, but
    // defer change listeners, SAT visibility and free-space monitoring.
    iCenRepNotifyHandlerHiddenApps = NULL;
    iCenRepNotifyHandlerCPHiddenApps = NULL;
    iCenRepNotifyHandlerCPHiddenFolders = NULL;
    iMcsSatNotifier = NULL;
    iFreeSpaceObserver = NULL;
""",
        "app-scanner optional observers",
    )
    text = replace_regex_once(
        text,
        r"        if\( appuid == KSatUid \)\n            \{\n.*?            \}\n        else\n",
        """        if( appuid == KSatUid )
            {
            // SAT is intentionally absent on the HTC Leo UI-first port.
            }
        else
""",
        "SAT item creation defer",
    )
    text = replace_once(
        text,
        """\tif ( aApaItem.GetUid() == KSatUid )
\t\t{
\t\tif (itemHidden == CMcsSatHandler::CheckVisibility())
\t\t\t{
\t\t\tiEng.ModifiableObjectL(aItem.Id(), RMenuNotifier::EItemsAddedRemoved).
\t\t\t\tSetFlags( TMenuItem::EHidden, !CMcsSatHandler::CheckVisibility());
\t\t\t}
\t\t}
""",
        """\tif ( aApaItem.GetUid() == KSatUid )
\t\t{
        // HTC Leo has no usable Symbian SAT/telephony stack; keep the
        // irrelevant entry hidden without contacting the SAT service.
        if ( !itemHidden )
            {
            iEng.ModifiableObjectL(aItem.Id(), RMenuNotifier::EItemsAddedRemoved).
                SetFlags( TMenuItem::EHidden, ETrue );
            }
\t\t}
""",
        "SAT visibility defer",
    )
    return text


CONSTRUCT_TIMER_TAIL = r'''        iTimedClose->Cancel();
        iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );
        HtcleoMcsLog(0x4D430127u, KErrNone, 0u);
        }'''


CONSTRUCT_PERSISTENT_TAIL = r'''        // HTCLEO_MCS_ENGINE_PERSISTENT_LIFETIME_V1
        // Keep the core MenuContent engine alive between the initial GetList
        // session and HN's later notification session.  On HTC Leo the stock
        // ten-second close races the slower AppArc save and loses its event.
        iTimedClose->Cancel();
        HtcleoMcsLog(0x4D430127u, KErrNone, 0u);
        HtcleoMcsLog(0x4D430131u, KErrNone, 0x4B454550u);
        }'''


CONTENT_NAME_CREATE = r'''    iContentName.CreateL( aContentName );
    HtcleoMcsLog(0x4D430101u, KErrNone, 0u);'''


CONTENT_NAME_CREATE_TAGGED = r'''    iContentName.CreateL( aContentName );
    HtcleoMcsLog(0x4D430101u, KErrNone, 0u);
    TUint32 htcleoContentTag = 0u;
    const TInt htcleoContentTagLength = Min(iContentName.Length(), 4);
    for (TInt htcleoContentIndex = 0;
            htcleoContentIndex < htcleoContentTagLength;
            ++htcleoContentIndex)
        {
        htcleoContentTag = (htcleoContentTag << 8)
            | (TUint32)(iContentName[htcleoContentIndex] & 0xFF);
        }
    HtcleoMcsLog(0x4D430135u, iContentName.Length(), htcleoContentTag);'''


ADD_SESSION_TAIL = r'''    iSessions.AppendL( aSession );
    Open(); // Increase refcount.
    iTimedClose->Cancel(); // Stay alive.
    }'''


ADD_SESSION_PERSISTENT_TAIL = r'''    iSessions.AppendL( aSession );
    Open(); // Increase refcount.
    iTimedClose->Cancel(); // Stay alive.
    HtcleoMcsLog(0x4D430132u, KErrNone, (TUint32)iSessions.Count());
    }'''


REMOVE_SESSION = r'''void CMenuSrvEng::RemoveSession( CMenuSrvSession* aSession )
    {
    TInt i = iSessions.Find( aSession );
    if ( KErrNotFound != i )
        {
        iSessions.Remove( i );
        Close(); // Decrease refcount.
        }
    if ( !iSessions.Count() )
        {
    	iTimedClose->Cancel();
        CActiveScheduler* currentScheduler = CActiveScheduler::Current();
        // No more sessions; schedule self-deletion.
        if (currentScheduler)
        	{
            // No more sessions; schedule self-deletion.
        	iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );
        	}
        else
        	{
        	// for Backup&Restore ActiveScheduler is closed ealier so we need
        	// to decrease refcount here (not in CloseSrvEng())
        	Close();
        	}
        }
    }'''


REMOVE_SESSION_PERSISTENT = r'''void CMenuSrvEng::RemoveSession( CMenuSrvSession* aSession )
    {
    TInt i = iSessions.Find( aSession );
    if ( KErrNotFound != i )
        {
        iSessions.Remove( i );
        Close(); // Decrease refcount.
        }
    HtcleoMcsLog(0x4D430133u, KErrNone, (TUint32)iSessions.Count());
    if ( !iSessions.Count() )
        {
        // The base/container reference remains.  Keep this healthy engine and
        // its completed AppArc model alive for the next HN notifier session.
        // EngineError retains the stock timed deletion/recovery path.
        iTimedClose->Cancel();
        HtcleoMcsLog(0x4D430134u, KErrNone, 0x4B454550u);
        }
    }'''


def patch_persistent_lifetime(text: str) -> str:
    if LIFETIME_MARKER in text:
        return text
    text = replace_once(
        text,
        CONTENT_NAME_CREATE,
        CONTENT_NAME_CREATE_TAGGED,
        "content-name tag",
    )
    text = replace_once(
        text,
        CONSTRUCT_TIMER_TAIL,
        CONSTRUCT_PERSISTENT_TAIL,
        "persistent constructor lifetime",
    )
    text = replace_once(
        text,
        ADD_SESSION_TAIL,
        ADD_SESSION_PERSISTENT_TAIL,
        "persistent AddSession trace",
    )
    text = replace_once(
        text,
        REMOVE_SESSION,
        REMOVE_SESSION_PERSISTENT,
        "persistent RemoveSession lifetime",
    )
    return text


def verify(engine: str, utils: str, scanner: str) -> None:
    checks = {
        "marker": engine.count(MARKER) == 1,
        "MCSLOG path": engine.count("C:\\\\Symbian3\\\\MCSLOG.TXT") == 1,
        "server SID gate": engine.count("0x200113DDu") == 1,
        "core engine retained": engine.count("iEng = CMenuEng::NewL") == 1,
        "core utils retained": engine.count("CMenuSrvEngUtils::NewL") >= 1,
        "core cache retained": engine.count("CMcsCacheHandler::NewL") >= 1,
        "scanner retained or later deferred": (
            engine.count("CMenuSrvAppScanner::NewL") >= 1
            or "HTCLEO_MCS_APPARC_UI_FIRST_FAILOPEN_V1" in utils
        ),
        "getlist retained": engine.count("CMcsGetlistHandler::NewL") == 1,
        "SAT monitor deferred": engine.count("iMcsSatMonitor = NULL;") >= 2,
        "folder notify deferred": engine.count("iFolderNotifier = NULL;") >= 2,
        "running guard": engine.count("if ( iRunningAppsHandler )") >= 1,
        "DRM attribute deferred": "AppDrmProtectionL( aId, aAttrExists" not in engine,
        "utils AppArc retained": (
            utils.count("iApaLsSession.Connect()")
            == (
                3
                if "HTCLEO_MCS_APPARC_SERVER_RESTART_V1" in utils
                else (
                    2
                    if "HTCLEO_MCS_APPARC_SCANNER_RESTORE_V1" in utils
                    else 1
                )
            )
        ),
        "widget connect retired": "iWidgetSession.Connect()" not in utils,
        "WServ connect retired": "iWsSession.Connect()" not in utils,
        "SAT NewL retired": "iSatHandler = CMcsSatHandler::NewL()" not in utils,
        "widget lookup retired": "iWidgetSession.IsWidget" not in utils,
        "CenRep retained": scanner.count("iCenRepSession = CRepository::NewL") == 1,
        "AppArc notifier retained": scanner.count("CApaAppListNotifier::NewL") == 1,
        "scan retained": scanner.count("ScheduleScan();") >= 2,
        "CenRep listener retired": "StartListeningL()" not in scanner,
        "SAT notifier retired": "CMcsSatNotifier::NewL" not in scanner,
        "free-space observer retired": "CMcsFreeSpaceObserver::NewL" not in scanner,
        "SAT visibility call retired": "CMcsSatHandler::CheckVisibility" not in scanner,
        "persistent core lifetime": (
            engine.count(LIFETIME_MARKER) == 1
            and engine.count("0x4D430131u") == 1
            and engine.count("0x4D430132u") == 1
            and engine.count("0x4D430133u") == 1
            and engine.count("0x4D430134u") == 1
            and engine.count("0x4D430135u") == 1
            and engine.count("0x4B454550u") == 2
            and engine.count(
                "iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );"
            ) == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MCS UI-first compatibility verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    engine_path = component / "srvsrc/menusrveng.cpp"
    utils_path = component / "srvsrc/menusrvengutils.cpp"
    scanner_path = component / "srvsrc/menusrvappscanner.cpp"
    if not all(path.is_file() for path in (engine_path, utils_path, scanner_path)):
        raise SystemExit("missing MenuContent server sources")

    engine = engine_path.read_text(encoding="latin-1")
    utils = utils_path.read_text(encoding="latin-1")
    scanner = scanner_path.read_text(encoding="latin-1")
    if MARKER not in engine:
        engine = patch_engine(engine)
        utils = patch_utils(utils)
        scanner = patch_scanner(scanner)
    engine = patch_persistent_lifetime(engine)
    verify(engine, utils, scanner)
    engine_path.write_text(engine, encoding="latin-1")
    utils_path.write_text(utils, encoding="latin-1")
    scanner_path.write_text(scanner, encoding="latin-1")
    print(
        "HTCLEO_MCS_UI_FIRST_COMPAT=installed "
        "core=menu-engine,cache,getlist,native-java-static "
        "lifetime=persistent-normal-fatal-timed-recovery "
        "deferred=sat,widget,folder-notify,running,drm,children,cenrep-notify,freespace"
    )


if __name__ == "__main__":
    main()
