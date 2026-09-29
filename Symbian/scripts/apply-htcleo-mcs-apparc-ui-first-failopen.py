#!/usr/bin/env python3
"""Keep the real menu tree and restore AppArc scanning once AppArc is ready.

Iteration 538 proves the first MenuContent engine and AppArc connection work,
then later engines stop while CMenuSrvEngUtils reconnects to AppArc.  Dynamic
caption/native/JAR refresh is not required to return the already parsed ROM/RAM
menu tree.  Only NotFound/ServerTerminated connect failures are made optional;
all other AppArc failures remain fail-closed, and every direct use is guarded.
After later bring-up proves AppArc healthy, restore its app scanner and allow a
previously closed utility session to reconnect during the asynchronous scan.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_APPARC_UI_FIRST_FAILOPEN_V1"
RESTORE_MARKER = "HTCLEO_MCS_APPARC_SCANNER_RESTORE_V1"
LOGGER_EXPORT_MARKER = "HTCLEO_MCS_LOGGER_EXPORT_V1"
SCANNER_TRACE_MARKER = "HTCLEO_MCS_APPARC_SCANNER_TRACE_V1"
SYNC_INITIAL_MARKER = "HTCLEO_MCS_APPARC_SCANNER_SYNC_INITIAL_V1"
INITIAL_WAIT_MARKER = "HTCLEO_MCS_APPARC_SCANNER_INITIAL_WAIT_V1"
BOUNDED_WAIT_MARKER = "HTCLEO_MCS_APPARC_SCANNER_BOUNDED_WAIT_V1"
ASYNC_NOTIFY_MARKER = "HTCLEO_MCS_APPARC_SCANNER_ASYNC_NOTIFY_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_utils(text: str) -> str:
    text = replace_once(
        text,
        """    // AppArc is the only initial-menu dependency.  Web widgets, a private
    // WServ session and SAT metadata are not needed for native/Java entries.
    User::LeaveIfError( iApaLsSession.Connect() );
    iWidgetSession.Close();
""",
        """    // HTCLEO_MCS_APPARC_UI_FIRST_FAILOPEN_V1
    // The real menu XML is already parsed before this utility is created.
    // Repeated AppArc connects may fail after the first engine; keep static
    // menu items and disable only dynamic attributes in that case.
    const TInt htcleoApaResult = iApaLsSession.Connect();
    if (htcleoApaResult == KErrNotFound ||
        htcleoApaResult == KErrServerTerminated)
        {
        iApaLsSession.Close();
        }
    else
        {
        User::LeaveIfError(htcleoApaResult);
        }
    iWidgetSession.Close();
""",
        "AppArc connect fail-open",
    )
    text = replace_once(
        text,
        """TInt CMenuSrvEngUtils::GetAppInfoL( const CMenuEngObject& aEngObj, TApaAppInfo& aAppInfo ) const
    {
    TUid appUid;
""",
        """TInt CMenuSrvEngUtils::GetAppInfoL( const CMenuEngObject& aEngObj, TApaAppInfo& aAppInfo ) const
    {
    if (!iApaLsSession.Handle())
        {
        return KErrNotSupported;
        }
    TUid appUid;
""",
        "GetAppInfo guard",
    )
    text = replace_once(
        text,
        """TInt CMenuSrvEngUtils::IsNativeL( TUid aAppUid, TBool& aIsNative )
\t{
    TInt error( KErrNotFound );
""",
        """TInt CMenuSrvEngUtils::IsNativeL( TUid aAppUid, TBool& aIsNative )
\t{
    aIsNative = EFalse;
    if (!iApaLsSession.Handle())
        {
        return KErrNotSupported;
        }
    TInt error( KErrNotFound );
""",
        "IsNative guard",
    )
    text = replace_once(
        text,
        """TBool CMenuSrvEngUtils::IsMiddlet( const TUid aAppUid ) const
\t{
    const TUid KMidletType = { 0x10210E26 };
""",
        """TBool CMenuSrvEngUtils::IsMiddlet( const TUid aAppUid ) const
\t{
    if (!iApaLsSession.Handle())
        {
        return EFalse;
        }
    const TUid KMidletType = { 0x10210E26 };
""",
        "IsMiddlet guard",
    )
    text = replace_once(
        text,
        """void CMenuSrvEngUtils::ReloadApaItemsL()
    {
    iAppAttributes.ResetAndDestroy();
""",
        """void CMenuSrvEngUtils::ReloadApaItemsL()
    {
    iAppAttributes.ResetAndDestroy();
    if (!iApaLsSession.Handle())
        {
        return;
        }
""",
        "ReloadApaItems guard",
    )
    return text


def patch_server(text: str) -> str:
    return replace_once(
        text,
        """    #ifndef __TEST_DISABLE_APPSCAN
        // AppArc scanning is core: it supplies native and Java applications.
        HtcleoMcsLog(0x4D430121u, KErrNone, 0u);
        iAppScanner = CMenuSrvAppScanner::NewL( *iEng, *iCMenuSrvEngUtils );
        HtcleoMcsLog(0x4D430122u, KErrNone,
            iAppScanner ? 1u : 0u);
        // Runtime folder-repository notifications are not initial menu data.
        iFolderNotifier = NULL;
""",
        """    #ifndef __TEST_DISABLE_APPSCAN
        // Dynamic AppArc rescans are deferred for the UI milestone.  The
        // parsed ROM/RAM tree and its executable UIDs remain intact.
        iAppScanner = NULL;
        HtcleoMcsLog(0x4D430121u, KErrNotSupported, 0x41505053u);
        HtcleoMcsLog(0x4D430122u, KErrNotSupported, 0x41505053u);
        // Runtime folder-repository notifications are not initial menu data.
        iFolderNotifier = NULL;
""",
        "AppScanner defer",
    )


DISABLED_SCANNER = r'''    #ifndef __TEST_DISABLE_APPSCAN
        // Dynamic AppArc rescans are deferred for the UI milestone.  The
        // parsed ROM/RAM tree and its executable UIDs remain intact.
        iAppScanner = NULL;
        HtcleoMcsLog(0x4D430121u, KErrNotSupported, 0x41505053u);
        HtcleoMcsLog(0x4D430122u, KErrNotSupported, 0x41505053u);
        // Runtime folder-repository notifications are not initial menu data.
        iFolderNotifier = NULL;
        HtcleoMcsLog(0x4D430123u, KErrNotSupported, 0x464F4C44u);
    #endif'''


RESTORED_SCANNER = r'''    #ifndef __TEST_DISABLE_APPSCAN
        // HTCLEO_MCS_APPARC_SCANNER_RESTORE_V1
        // AppArc now completes its first scan.  Restore the only producer of
        // native/JAR menu entries while retaining the optional-service cuts.
        HtcleoMcsLog(0x4D430121u, KErrNone, 0u);
        TRAPD(htcleoAppScannerResult,
            iAppScanner = CMenuSrvAppScanner::NewL(
                *iEng, *iCMenuSrvEngUtils));
        HtcleoMcsLog(0x4D430122u, htcleoAppScannerResult,
            iAppScanner ? 1u : 0u);
        if (htcleoAppScannerResult != KErrNone)
            {
            iAppScanner = NULL;
            if (htcleoAppScannerResult != KErrNotFound
                    && htcleoAppScannerResult != KErrServerTerminated)
                {
                User::Leave(htcleoAppScannerResult);
                }
            }
        // Runtime folder-repository notifications are not initial menu data.
        iFolderNotifier = NULL;
        HtcleoMcsLog(0x4D430123u, KErrNotSupported, 0x464F4C44u);
    #endif'''


RELOAD_GUARD = r'''void CMenuSrvEngUtils::ReloadApaItemsL()
    {
    iAppAttributes.ResetAndDestroy();
    if (!iApaLsSession.Handle())
        {
        return;
        }
    TApaAppInfo appInfo;'''


RELOAD_RECONNECT = r'''void CMenuSrvEngUtils::ReloadApaItemsL()
    {
    iAppAttributes.ResetAndDestroy();
    // HTCLEO_MCS_APPARC_SCANNER_RESTORE_V1
    TInt htcleoApaReconnectResult = KErrNone;
    if (!iApaLsSession.Handle())
        {
        htcleoApaReconnectResult = iApaLsSession.Connect();
        }
    HtcleoMcsLog(0x4D43012Bu, htcleoApaReconnectResult,
        iApaLsSession.Handle() ? 1u : 0u);
    if (htcleoApaReconnectResult != KErrNone
            || !iApaLsSession.Handle())
        {
        return;
        }
    TApaAppInfo appInfo;'''


RELOAD_TAIL = r'''        iAppAttributes.AppendL( appAtributes );
        CleanupStack::Pop( appAtributes );
        }
    }'''


RELOAD_TAIL_LOGGED = r'''        iAppAttributes.AppendL( appAtributes );
        CleanupStack::Pop( appAtributes );
        }
    HtcleoMcsLog(0x4D43012Cu, KErrNone,
        (TUint32)iAppAttributes.Count());
    }'''


SCANNER_INCLUDE = '#include "menuutil.h"\n'
SCANNER_INCLUDE_LOG = r'''#include "menuutil.h"

// HTCLEO_MCS_APPARC_SCANNER_TRACE_V1
void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
'''


SCANNER_OPERATION = r'''void CMenuSrvAppScanner::RunMenuEngOperationL()
    {
    UpdateApplicationItemsL();
    UpdateApplicationWithHideIfInstalledItemsL();
    UpdateLinkItemsL();
    iOpStatus = EFalse;
    }'''


SCANNER_OPERATION_LOGGED = r'''void CMenuSrvAppScanner::RunMenuEngOperationL()
    {
    HtcleoMcsLog(0x4D430128u, KErrNone, 0u);
    UpdateApplicationItemsL();
    HtcleoMcsLog(0x4D430129u, KErrNone,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    UpdateApplicationWithHideIfInstalledItemsL();
    UpdateLinkItemsL();
    iOpStatus = EFalse;
    HtcleoMcsLog(0x4D43012Au, KErrNone, 0u);
    }'''


SCANNER_CONSTRUCT_TAIL = r'''    //SetActive();
	ScheduleScan();
    //iOpStatus = ETrue;
    }'''


SCANNER_CONSTRUCT_SYNC = r'''    // HTCLEO_MCS_APPARC_SCANNER_SYNC_INITIAL_V1
    // AppArc is already hardware-ready.  Populate the real menu engine before
    // the first HN GetList snapshot; later AppArc notifier updates stay stock.
    HtcleoMcsLog(0x4D43012Du, KErrNone, 0u);
    TRAPD(htcleoInitialScanResult, RunMenuEngOperationL());
    HtcleoMcsLog(0x4D43012Eu, htcleoInitialScanResult,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    if (htcleoInitialScanResult == KErrNotFound
            || htcleoInitialScanResult == KErrServerTerminated)
        {
        ScheduleScan();
        }
    else
        {
        User::LeaveIfError(htcleoInitialScanResult);
        }
    HtcleoMcsLog(0x4D43012Fu, KErrNone,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    }'''


SCANNER_CONSTRUCT_WAIT = r'''    // HTCLEO_MCS_APPARC_SCANNER_INITIAL_WAIT_V1
    // Queue through CMenuEng so its lock/save/notification contract remains
    // intact, then wait only for this proven first operation to complete.
    iHtcleoInitialScanResult = KErrNone;
    iHtcleoInitialScanWait = new(ELeave) CActiveSchedulerWait();
    HtcleoMcsLog(0x4D43012Du, KErrNone, 0u);
    ScheduleScan();
    if (iOpStatus && !iHtcleoInitialScanWait->IsStarted())
        {
        iHtcleoInitialScanWait->Start();
        }
    HtcleoMcsLog(0x4D43012Eu, iHtcleoInitialScanResult,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    const TInt htcleoInitialScanResult = iHtcleoInitialScanResult;
    delete iHtcleoInitialScanWait;
    iHtcleoInitialScanWait = NULL;
    User::LeaveIfError(htcleoInitialScanResult);
    HtcleoMcsLog(0x4D43012Fu, KErrNone,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    }'''


SCANNER_COMPLETED = r'''void CMenuSrvAppScanner::CompletedMenuEngOperation( TInt /*aErr*/ )
    {
    iOpStatus = EFalse;
    }'''


SCANNER_COMPLETED_WAIT = r'''void CMenuSrvAppScanner::CompletedMenuEngOperation( TInt aErr )
    {
    iOpStatus = EFalse;
    if (iHtcleoInitialScanWait)
        {
        iHtcleoInitialScanResult = aErr;
        if (iHtcleoInitialScanWait->IsStarted())
            {
            iHtcleoInitialScanWait->AsyncStop();
            }
        }
    }'''


SCANNER_RUNERROR = r'''TInt CMenuSrvAppScanner::RunError( TInt /*aError*/ )
    {
    // Ignore the error (what else could we do?).
    // When next AppArc update occurs, we will run again.
    return KErrNone;
    }'''


SCANNER_RUNERROR_WAIT = r'''TInt CMenuSrvAppScanner::RunError( TInt aError )
    {
    iOpStatus = EFalse;
    if (iHtcleoInitialScanWait)
        {
        iHtcleoInitialScanResult = aError;
        if (iHtcleoInitialScanWait->IsStarted())
            {
            iHtcleoInitialScanWait->AsyncStop();
            }
        }
    // Later AppArc notifier events retain the stock retry opportunity.
    return KErrNone;
    }'''


SCANNER_DESTRUCTOR = r'''CMenuSrvAppScanner::~CMenuSrvAppScanner()
    {
    Cancel();'''


SCANNER_DESTRUCTOR_WAIT = r'''CMenuSrvAppScanner::~CMenuSrvAppScanner()
    {
    Cancel();
    if (iHtcleoInitialScanWait && iHtcleoInitialScanWait->IsStarted())
        {
        iHtcleoInitialScanWait->AsyncStop();
        }
    delete iHtcleoInitialScanWait;
    iHtcleoInitialScanWait = NULL;'''


SCANNER_HEADER_STATE = r'''    TBool iOpStatus;
    };'''


SCANNER_HEADER_WAIT = r'''    TBool iOpStatus;

    // HTCLEO_MCS_APPARC_SCANNER_INITIAL_WAIT_V1
    CActiveSchedulerWait* iHtcleoInitialScanWait;
    TInt iHtcleoInitialScanResult;
    };'''


SCANNER_CONSTRUCT_BOUNDED = r'''    // HTCLEO_MCS_APPARC_SCANNER_INITIAL_WAIT_V1
    // HTCLEO_MCS_APPARC_SCANNER_BOUNDED_WAIT_V1
    // Queue through CMenuEng so its lock/save/notification contract remains
    // intact.  Bound the first wait so a broken optional scanner cannot block
    // the MenuContent server or regress the already-visible ROM UI.
    iHtcleoInitialScanResult = KErrNone;
    iHtcleoInitialScanWait = new(ELeave) CActiveSchedulerWait();
    iHtcleoInitialScanTimeout = CPeriodic::NewL(CActive::EPriorityHigh);
    HtcleoMcsLog(0x4D43012Du, KErrNone, 0u);
    ScheduleScan();
    if (iOpStatus && !iHtcleoInitialScanWait->IsStarted())
        {
        const TInt KHTCLEOInitialAppScanTimeoutUs = 5000000;
        iHtcleoInitialScanTimeout->Start(
            KHTCLEOInitialAppScanTimeoutUs,
            KHTCLEOInitialAppScanTimeoutUs,
            TCallBack(HtcleoInitialScanTimeout, this));
        iHtcleoInitialScanWait->Start();
        }
    iHtcleoInitialScanTimeout->Cancel();
    HtcleoMcsLog(0x4D43012Eu, iHtcleoInitialScanResult,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    const TInt htcleoInitialScanResult = iHtcleoInitialScanResult;
    delete iHtcleoInitialScanTimeout;
    iHtcleoInitialScanTimeout = NULL;
    delete iHtcleoInitialScanWait;
    iHtcleoInitialScanWait = NULL;
    HtcleoMcsLog(0x4D43012Fu, htcleoInitialScanResult,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    }'''


SCANNER_COMPLETED_BOUNDED = r'''void CMenuSrvAppScanner::HtcleoCompleteInitialScan(TInt aResult)
    {
    if (iHtcleoInitialScanWait)
        {
        iHtcleoInitialScanResult = aResult;
        if (iHtcleoInitialScanWait->IsStarted())
            {
            iHtcleoInitialScanWait->AsyncStop();
            }
        }
    }

TInt CMenuSrvAppScanner::HtcleoInitialScanTimeout(TAny* aSelf)
    {
    CMenuSrvAppScanner* self =
        static_cast<CMenuSrvAppScanner*>(aSelf);
    if (self)
        {
        self->HtcleoCompleteInitialScan(KErrTimedOut);
        }
    return KErrNone;
    }

void CMenuSrvAppScanner::CompletedMenuEngOperation( TInt aErr )
    {
    iOpStatus = EFalse;
    HtcleoCompleteInitialScan(aErr);
    }'''


SCANNER_RUNERROR_BOUNDED = r'''TInt CMenuSrvAppScanner::RunError( TInt aError )
    {
    iOpStatus = EFalse;
    HtcleoCompleteInitialScan(aError);
    // Later AppArc notifier events retain the stock retry opportunity.
    return KErrNone;
    }'''


SCANNER_RUNL_WAIT = r'''void CMenuSrvAppScanner::RunL()
    {
    User::LeaveIfError( iStatus.Int() ); // Handle errors in RunL.
    // AppArc app scan complete, we have the app list.
    // Now queue this operation to be executed by the Engine.
    if ( !MenuUtil::BackupInProgressL() )
        {
        iEng.QueueOperationL( *this );
        }
    else
        {
        iOpStatus = EFalse;
        }
    }'''


SCANNER_RUNL_BOUNDED = r'''void CMenuSrvAppScanner::RunL()
    {
    User::LeaveIfError( iStatus.Int() ); // Handle errors in RunL.
    // AppArc app scan complete, we have the app list.
    // Now queue this operation to be executed by the Engine.
    if ( !MenuUtil::BackupInProgressL() )
        {
        iEng.QueueOperationL( *this );
        }
    else
        {
        iOpStatus = EFalse;
        HtcleoCompleteInitialScan(KErrNotReady);
        }
    }'''


SCANNER_DESTRUCTOR_BOUNDED = r'''CMenuSrvAppScanner::~CMenuSrvAppScanner()
    {
    if (iHtcleoInitialScanWait && iHtcleoInitialScanWait->IsStarted())
        {
        iHtcleoInitialScanWait->AsyncStop();
        }
    if (iHtcleoInitialScanTimeout)
        {
        iHtcleoInitialScanTimeout->Cancel();
        }
    delete iHtcleoInitialScanTimeout;
    iHtcleoInitialScanTimeout = NULL;
    delete iHtcleoInitialScanWait;
    iHtcleoInitialScanWait = NULL;
    Cancel();'''


SCANNER_CONSTRUCTOR = r'''CMenuSrvAppScanner::CMenuSrvAppScanner(
        CMenuEng& aEng, CMenuSrvEngUtils& aSrvEngUtils )
: CActive( CActive::EPriorityStandard ), iEng( aEng ),
  iSrvEngUtils( aSrvEngUtils )'''


SCANNER_CONSTRUCTOR_BOUNDED = r'''CMenuSrvAppScanner::CMenuSrvAppScanner(
        CMenuEng& aEng, CMenuSrvEngUtils& aSrvEngUtils )
: CActive( CActive::EPriorityStandard ), iEng( aEng ),
  iSrvEngUtils( aSrvEngUtils ),
  iHtcleoInitialScanWait( NULL ),
  iHtcleoInitialScanTimeout( NULL ),
  iHtcleoInitialScanResult( KErrNone )'''


SCANNER_HEADER_BOUNDED = r'''    TBool iOpStatus;

    // HTCLEO_MCS_APPARC_SCANNER_INITIAL_WAIT_V1
    // HTCLEO_MCS_APPARC_SCANNER_BOUNDED_WAIT_V1
    static TInt HtcleoInitialScanTimeout(TAny* aSelf);
    void HtcleoCompleteInitialScan(TInt aResult);
    CActiveSchedulerWait* iHtcleoInitialScanWait;
    CPeriodic* iHtcleoInitialScanTimeout;
    TInt iHtcleoInitialScanResult;
    };'''


SCANNER_CONSTRUCT_ASYNC_NOTIFY = r'''    // HTCLEO_MCS_APPARC_SCANNER_ASYNC_NOTIFY_V1
    // Do not run a nested scheduler while CMenuSrvEng is still being
    // constructed: GetEngineL has not registered it yet and another client
    // can otherwise create a duplicate engine.  Queue the stock scan and let
    // the HN subscribe-then-requery path close the first-snapshot race.
    HtcleoMcsLog(0x4D43012Du, KErrNone, 0u);
    ScheduleScan();
    HtcleoMcsLog(0x4D43012Eu, KErrNone, iOpStatus ? 1u : 0u);
    }'''


SCANNER_COMPLETED_ASYNC_NOTIFY = r'''void CMenuSrvAppScanner::CompletedMenuEngOperation( TInt aErr )
    {
    iOpStatus = EFalse;
    HtcleoMcsLog(0x4D43012Fu, aErr, 0u);
    }'''


SCANNER_RUNERROR_ASYNC_NOTIFY = r'''TInt CMenuSrvAppScanner::RunError( TInt aError )
    {
    iOpStatus = EFalse;
    HtcleoMcsLog(0x4D430130u, aError, 0u);
    // Later AppArc notifier events retain the stock retry opportunity.
    return KErrNone;
    }'''


def restore_scanner(
    server: str, utils: str, scanner: str, scanner_header: str
) -> tuple[str, str, str, str]:
    if RESTORE_MARKER not in server:
        server = replace_once(
            server, DISABLED_SCANNER, RESTORED_SCANNER, "AppScanner restore"
        )
    if LOGGER_EXPORT_MARKER not in server:
        server = replace_once(
            server,
            "static void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)",
            "// HTCLEO_MCS_LOGGER_EXPORT_V1\n"
            "void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)",
            "MCS logger export",
        )
    if RESTORE_MARKER not in utils:
        utils = replace_once(
            utils, RELOAD_GUARD, RELOAD_RECONNECT, "AppArc reconnect"
        )
        utils = replace_once(
            utils, RELOAD_TAIL, RELOAD_TAIL_LOGGED, "AppArc app count"
        )
        utils = replace_once(
            utils,
            '#include "menusrvengutils.h"\n',
            '#include "menusrvengutils.h"\n\n'
            'void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n',
            "utils logger declaration",
        )
    if SCANNER_TRACE_MARKER not in scanner:
        scanner = replace_once(
            scanner, SCANNER_INCLUDE, SCANNER_INCLUDE_LOG, "scanner logger declaration"
        )
        scanner = replace_once(
            scanner,
            SCANNER_OPERATION,
            SCANNER_OPERATION_LOGGED,
            "scanner operation trace",
        )
    if INITIAL_WAIT_MARKER not in scanner and ASYNC_NOTIFY_MARKER not in scanner:
        if SYNC_INITIAL_MARKER in scanner:
            scanner = replace_once(
                scanner,
                SCANNER_CONSTRUCT_SYNC,
                SCANNER_CONSTRUCT_WAIT,
                "queued initial AppArc wait upgrade",
            )
        else:
            scanner = replace_once(
                scanner,
                SCANNER_CONSTRUCT_TAIL,
                SCANNER_CONSTRUCT_WAIT,
                "queued initial AppArc wait",
            )
        scanner = replace_once(
            scanner,
            SCANNER_COMPLETED,
            SCANNER_COMPLETED_WAIT,
            "initial AppArc completion",
        )
        scanner = replace_once(
            scanner,
            SCANNER_RUNERROR,
            SCANNER_RUNERROR_WAIT,
            "initial AppArc RunError",
        )
        scanner = replace_once(
            scanner,
            SCANNER_DESTRUCTOR,
            SCANNER_DESTRUCTOR_WAIT,
            "initial AppArc wait cleanup",
        )
    if (
        INITIAL_WAIT_MARKER not in scanner_header
        and ASYNC_NOTIFY_MARKER not in scanner
    ):
        scanner_header = replace_once(
            scanner_header,
            SCANNER_HEADER_STATE,
            SCANNER_HEADER_WAIT,
            "initial AppArc wait state",
        )
    if BOUNDED_WAIT_MARKER not in scanner and ASYNC_NOTIFY_MARKER not in scanner:
        scanner = replace_once(
            scanner,
            SCANNER_CONSTRUCT_WAIT,
            SCANNER_CONSTRUCT_BOUNDED,
            "bounded initial AppArc wait",
        )
        scanner = replace_once(
            scanner,
            SCANNER_COMPLETED_WAIT,
            SCANNER_COMPLETED_BOUNDED,
            "bounded initial AppArc completion",
        )
        scanner = replace_once(
            scanner,
            SCANNER_RUNERROR_WAIT,
            SCANNER_RUNERROR_BOUNDED,
            "bounded initial AppArc RunError",
        )
        scanner = replace_once(
            scanner,
            SCANNER_RUNL_WAIT,
            SCANNER_RUNL_BOUNDED,
            "backup-safe initial AppArc wait",
        )
        scanner = replace_once(
            scanner,
            SCANNER_DESTRUCTOR_WAIT,
            SCANNER_DESTRUCTOR_BOUNDED,
            "bounded initial AppArc cleanup",
        )
        scanner = replace_once(
            scanner,
            SCANNER_CONSTRUCTOR,
            SCANNER_CONSTRUCTOR_BOUNDED,
            "initial AppArc pointer initialization",
        )
    if (
        BOUNDED_WAIT_MARKER not in scanner_header
        and ASYNC_NOTIFY_MARKER not in scanner
    ):
        scanner_header = replace_once(
            scanner_header,
            SCANNER_HEADER_WAIT,
            SCANNER_HEADER_BOUNDED,
            "bounded initial AppArc state",
        )
    if ASYNC_NOTIFY_MARKER not in scanner:
        scanner = replace_once(
            scanner,
            SCANNER_CONSTRUCT_BOUNDED,
            SCANNER_CONSTRUCT_ASYNC_NOTIFY,
            "remove constructor nested wait",
        )
        scanner = replace_once(
            scanner,
            SCANNER_COMPLETED_BOUNDED,
            SCANNER_COMPLETED_ASYNC_NOTIFY,
            "async notification completion",
        )
        scanner = replace_once(
            scanner,
            SCANNER_RUNERROR_BOUNDED,
            SCANNER_RUNERROR_ASYNC_NOTIFY,
            "async notification RunError",
        )
        scanner = replace_once(
            scanner,
            SCANNER_RUNL_BOUNDED,
            SCANNER_RUNL_WAIT,
            "restore stock queue RunL",
        )
        scanner = replace_once(
            scanner,
            SCANNER_DESTRUCTOR_BOUNDED,
            SCANNER_DESTRUCTOR,
            "remove nested wait cleanup",
        )
        scanner = replace_once(
            scanner,
            SCANNER_CONSTRUCTOR_BOUNDED,
            SCANNER_CONSTRUCTOR,
            "remove nested wait members",
        )
        scanner_header = replace_once(
            scanner_header,
            SCANNER_HEADER_BOUNDED,
            SCANNER_HEADER_STATE,
            "remove nested wait state",
        )
    return server, utils, scanner, scanner_header


def verify(server: str, utils: str, scanner: str, scanner_header: str) -> None:
    checks = {
        "marker": utils.count(MARKER) == 1,
        "connect retained": utils.count("iApaLsSession.Connect()")
        == (
            3
            if "HTCLEO_MCS_APPARC_SERVER_RESTART_V1" in utils
            else 2
        ),
        "narrow not-found": utils.count("htcleoApaResult == KErrNotFound") == 1,
        "narrow terminated": utils.count("htcleoApaResult == KErrServerTerminated") == 1,
        "session guards": utils.count("!iApaLsSession.Handle()") == 5,
        "scanner restore": (
            server.count(RESTORE_MARKER) == 1
            and server.count("CMenuSrvAppScanner::NewL") == 1
            and server.count("TRAPD(htcleoAppScannerResult") == 1
            and "0x41505053u" not in server
        ),
        "narrow scanner fail-open": (
            server.count("htcleoAppScannerResult != KErrNotFound") == 1
            and server.count("htcleoAppScannerResult != KErrServerTerminated") == 1
        ),
        "reconnect and count": (
            utils.count(RESTORE_MARKER) == 1
            and utils.count("0x4D43012Bu") == 1
            and utils.count("0x4D43012Cu") == 1
        ),
        "scanner trace": (
            scanner.count(SCANNER_TRACE_MARKER) == 1
            and all(
                scanner.count(f"0x4D430{stage:03X}u") == 1
                for stage in range(0x128, 0x12B)
            )
        ),
        "async marker": scanner.count(ASYNC_NOTIFY_MARKER) == 1,
        "nested wait markers removed": (
            scanner_header.count(INITIAL_WAIT_MARKER) == 0
            and scanner.count(INITIAL_WAIT_MARKER) == 0
            and scanner.count(BOUNDED_WAIT_MARKER) == 0
        ),
        "stock queue retained": scanner.count("iEng.QueueOperationL( *this );") == 1,
        "async stages": all(
            scanner.count(f"0x4D430{stage:03X}u") == 1
            for stage in range(0x12D, 0x130)
        ) and scanner.count("0x4D430130u") == 1,
        "nested wait implementation removed": (
            "TRAPD(htcleoInitialScanResult" not in scanner
            and "User::LeaveIfError(htcleoInitialScanResult)" not in scanner
            and "iHtcleoInitialScanWait->Start();" not in scanner
            and "CActiveSchedulerWait" not in scanner
            and "CPeriodic" not in scanner
            and "CActiveSchedulerWait" not in scanner_header
            and "CPeriodic" not in scanner_header
            and "iHtcleoInitialScanResult" not in scanner
        ),
        "shared logger": (
            server.count(LOGGER_EXPORT_MARKER) == 1
            and "static void HtcleoMcsLog" not in server
            and scanner.count("void HtcleoMcsLog(") == 1
            and utils.count("void HtcleoMcsLog(") == 1
        ),
        "real menu engine": server.count("iEng = CMenuEng::NewL") == 1,
        "real GetList": server.count("CMcsGetlistHandler::NewL") == 1,
        "no delay": (
            "User::After" not in server
            and "User::After" not in utils
            and "User::After" not in scanner
        ),
        "no display probe": (
            "HalFunction" not in server
            and "HalFunction" not in utils
            and "HalFunction" not in scanner
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MCS AppArc fail-open verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    server_path = component / "srvsrc/menusrveng.cpp"
    utils_path = component / "srvsrc/menusrvengutils.cpp"
    scanner_path = component / "srvsrc/menusrvappscanner.cpp"
    scanner_header_path = component / "srvinc/menusrvappscanner.h"
    if (
        not server_path.is_file()
        or not utils_path.is_file()
        or not scanner_path.is_file()
        or not scanner_header_path.is_file()
    ):
        raise SystemExit("missing MenuContent AppArc sources")
    server = server_path.read_text(encoding="latin-1")
    utils = utils_path.read_text(encoding="latin-1")
    scanner = scanner_path.read_text(encoding="latin-1")
    scanner_header = scanner_header_path.read_text(encoding="latin-1")
    if MARKER not in utils:
        server = patch_server(server)
        utils = patch_utils(utils)
    server, utils, scanner, scanner_header = restore_scanner(
        server, utils, scanner, scanner_header
    )
    verify(server, utils, scanner, scanner_header)
    server_path.write_text(server, encoding="latin-1")
    utils_path.write_text(utils, encoding="latin-1")
    scanner_path.write_text(scanner, encoding="latin-1")
    scanner_header_path.write_text(scanner_header, encoding="latin-1")
    print(
        "HTCLEO_MCS_APPARC_FAILOPEN=installed "
        "policy=scanner-restored-async-queue-notify-requery-reconnect-failopen-128-130"
    )


if __name__ == "__main__":
    main()
