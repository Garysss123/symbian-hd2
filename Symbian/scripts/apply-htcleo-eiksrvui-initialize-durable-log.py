#!/usr/bin/env python3
"""Trace the EikSrvUi base InitializeL frontier and apply bounded UI-first policy.

Iteration 467 exhausts all 64 compact client readiness polls while the sole
server child reaches E775 and never reaches E776.  Those stages bracket
CEikServAppUiBase::InitializeL.  Reuse the established fail-open EIKSRV logger
to divide that function at its existing synchronous calls.  The original trace
changes no policy.  After iteration 484 hardware-proves E7DB but not E7DC, an
explicit reversible UI-first compatibility branch defers the optional notifier
server and its idle starter so Shell/touch bring-up is not held behind global
notification plug-ins.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PREVIOUS_MARKER = "HTCLEO_EIKSRVUI_CONSTRUCT_DURABLE_LOG_V1"
MARKER = "HTCLEO_EIKSRVUI_INITIALIZE_DURABLE_LOG_V1"
OPTIONAL_C32_FAIL_OPEN_MARKER = "HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN_V1"
NOTIFIER_SERVER_FAIL_OPEN_MARKER = "HTCLEO_EIKSRVUI_NOTIFIER_SERVER_UI_FAIL_OPEN_V1"
STAGES = tuple(
    [f"E7C{x:X}" for x in range(16)]
    + [f"E7D{x:X}" for x in range(16)]
    + ["E7E0", "E7E1", "E7E2"]
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "previous logger": source.count(PREVIOUS_MARKER) == 1,
        "initialize marker": source.count(MARKER) == 1,
        "outer entry": source.count(
            "HtcleoEikSrvUiLog(0x0000E775u, KErrNone, 0u)"
        ) == 1,
        "outer return": source.count(
            "HtcleoEikSrvUiLog(0x0000E776u, KErrNone, 0u)"
        ) == 1,
        "initialize function": source.count(
            "CEikServAppUiBase::InitializeL(TEikServCtrlFactories& aCtrlFactories)"
        ) == 1,
        "watcher call": source.count("CreateWatcherThreadL();") == 1,
        "view server call": source.count(
            "CVwsSessionWrapper::StartViewServer(*iAppStarter)"
        ) == 1,
        "C32 policy": (
            source.count("StartC32();") == 1
            or (
                source.count(OPTIONAL_C32_FAIL_OPEN_MARKER) == 1
                and source.count("StartC32();") == 0
            )
        ),
        "PDD call": source.count("User::LoadPhysicalDevice(COMMS_PDD_NAME)") == 1,
        "LDD call": source.count("User::LoadLogicalDevice(COMMS_LDD_NAME)") == 1,
        "notifier-server UI-first marker": (
            source.count(NOTIFIER_SERVER_FAIL_OPEN_MARKER) == 1
        ),
        "blocking notifier construction retired": source.count(
            "iNotifyServer = CEikServNotifyServer::NewL(aCtrlFactories.iAlert);"
        ) == 0,
        "notifier idle starter retired": source.count(
            "iEikServExtra->iNotifierServerStarter = CIdle::NewL("
        ) == 0,
        "notifier idle callback retired": source.count(
            "iEikServExtra->iNotifierServerStarter->Start("
        ) == 0,
        "explicit null notifier state": source.count(
            "iNotifyServer = NULL;"
        ) == 1,
        "notifier bypass detail": source.count("0x4E465953u") == 3,
    }
    for stage in STAGES:
        checks[f"stage {stage}"] = (
            source.count(f"HtcleoEikSrvUiLog(0x0000{stage}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvui InitializeL trace verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()
    source_path = (
        args.epocroot
        / "sf/mw/classicui/uifw/EikStd/srvuisrc/EIKSRVUI.CPP"
    )
    source = source_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = replace_once(
            source,
            r"""EXPORT_C void CEikServAppUiBase::InitializeL(TEikServCtrlFactories& aCtrlFactories)
    {
    RWindowGroup& rootWin = iCoeEnv->RootWin();

    CleanupStack::PushL(TCleanupItem(&ReleaseFactories,&aCtrlFactories));
    RFs& fsSession = iCoeEnv->FsSession();
    _LIT(KAppDirName, "C:\\System\\Apps\\");
    fsSession.MkDirAll(KAppDirName); // !! prevent app arch crash

    // Initialize some system settings.
    SetSystemTime();
    rootWin.EnableOnEvents(EEventControlAlways);
""",
            r"""EXPORT_C void CEikServAppUiBase::InitializeL(TEikServCtrlFactories& aCtrlFactories)
    {
    // HTCLEO_EIKSRVUI_INITIALIZE_DURABLE_LOG_V1
    HtcleoEikSrvUiLog(0x0000E7C0u, KErrNone, 0u);
    RWindowGroup& rootWin = iCoeEnv->RootWin();

    CleanupStack::PushL(TCleanupItem(&ReleaseFactories,&aCtrlFactories));
    RFs& fsSession = iCoeEnv->FsSession();
    HtcleoEikSrvUiLog(0x0000E7C1u, KErrNone, 0u);
    _LIT(KAppDirName, "C:\\System\\Apps\\");
    const TInt htcleoAppDirResult = fsSession.MkDirAll(KAppDirName);
    HtcleoEikSrvUiLog(0x0000E7C2u, htcleoAppDirResult, 0u);

    // Initialize some system settings.
    HtcleoEikSrvUiLog(0x0000E7C3u, KErrNone, 0u);
    SetSystemTime();
    HtcleoEikSrvUiLog(0x0000E7C4u, KErrNone, 0u);
    rootWin.EnableOnEvents(EEventControlAlways);
    HtcleoEikSrvUiLog(0x0000E7C5u, KErrNone, 0u);
""",
            "InitializeL entry, app dir and system time",
        )
        source = replace_once(
            source,
            """    TRAP_IGNORE(
        CEikPasswordModeCategory* pcategory = CEikPasswordModeCategory::NewLC(fsSession);
""",
            """    HtcleoEikSrvUiLog(0x0000E7C6u, KErrNone, (TUint32)mode);
    TRAPD(htcleoPasswordModeResult,
        CEikPasswordModeCategory* pcategory = CEikPasswordModeCategory::NewLC(fsSession);
""",
            "password trap entry",
        )
        source = replace_once(
            source,
            """            CleanupStack::PopAndDestroy(); // pcategory
            }
        );

    // Create separate thread for OOD watchers.
    CreateWatcherThreadL();

    // Start View Server.
    iAppStarter = CEikServAppStarter::NewL();
    User::LeaveIfError(CVwsSessionWrapper::StartViewServer(*iAppStarter));
    iVwsSession = CVwsSessionWrapper::NewL();
""",
            """            CleanupStack::PopAndDestroy(); // pcategory
            }
        );
    HtcleoEikSrvUiLog(0x0000E7C7u, htcleoPasswordModeResult,
        (TUint32)mode);

    // Create separate thread for OOD watchers.
    HtcleoEikSrvUiLog(0x0000E7C8u, KErrNone, 0u);
    CreateWatcherThreadL();
    HtcleoEikSrvUiLog(0x0000E7C9u, KErrNone, 0u);

    // Start View Server.
    HtcleoEikSrvUiLog(0x0000E7CAu, KErrNone, 0u);
    iAppStarter = CEikServAppStarter::NewL();
    HtcleoEikSrvUiLog(0x0000E7CBu, KErrNone, iAppStarter ? 1u : 0u);
    const TInt htcleoViewStartResult =
        CVwsSessionWrapper::StartViewServer(*iAppStarter);
    HtcleoEikSrvUiLog(0x0000E7CCu, htcleoViewStartResult, 0u);
    User::LeaveIfError(htcleoViewStartResult);
    HtcleoEikSrvUiLog(0x0000E7CDu, KErrNone, 0u);
    iVwsSession = CVwsSessionWrapper::NewL();
    HtcleoEikSrvUiLog(0x0000E7CEu, KErrNone, iVwsSession ? 1u : 0u);
""",
            "password return, watcher and view server",
        )
        source = replace_once(
            source,
            """    TResourceReader reader;
    iEikonEnv->CreateResourceReaderLC(reader, R_EIK_SYSTEM_DEFAULT_VIEW_ID);
    TVwsViewId viewId;
    viewId.iAppUid.iUid = reader.ReadInt32();
    viewId.iViewUid.iUid = reader.ReadInt32();
    CleanupStack::PopAndDestroy(); // reader
    iVwsSession->SetSystemDefaultView(viewId);

    TInt serverEventTimeOutDuration = EikResourceUtils::ReadTInt32L(    
        R_EIK_SYSTEM_VIEW_SERVER_EVENT_TIME_OUT, iEikonEnv);
        
    iVwsSession->SetServerEventTimeOut( TTimeIntervalMicroSeconds32(serverEventTimeOutDuration) );
    
    TInt clientRequestTimeOutDuration = EikResourceUtils::ReadTInt32L(
        R_EIK_SYSTEM_VIEW_SERVER_CLIENT_REQUEST_TIME_OUT, iEikonEnv);
        
    iVwsSession->SetClientRequestTimeOut( TTimeIntervalMicroSeconds32(clientRequestTimeOutDuration) );

    iVwsSession->EnableServerBlankScreen(EFalse);
""",
            """    HtcleoEikSrvUiLog(0x0000E7CFu, KErrNone, 0u);
    TResourceReader reader;
    iEikonEnv->CreateResourceReaderLC(reader, R_EIK_SYSTEM_DEFAULT_VIEW_ID);
    TVwsViewId viewId;
    viewId.iAppUid.iUid = reader.ReadInt32();
    viewId.iViewUid.iUid = reader.ReadInt32();
    CleanupStack::PopAndDestroy(); // reader
    HtcleoEikSrvUiLog(0x0000E7D0u, KErrNone,
        (TUint32)viewId.iAppUid.iUid);
    iVwsSession->SetSystemDefaultView(viewId);
    HtcleoEikSrvUiLog(0x0000E7D1u, KErrNone,
        (TUint32)viewId.iViewUid.iUid);

    TInt serverEventTimeOutDuration = EikResourceUtils::ReadTInt32L(    
        R_EIK_SYSTEM_VIEW_SERVER_EVENT_TIME_OUT, iEikonEnv);
    HtcleoEikSrvUiLog(0x0000E7D2u, KErrNone,
        (TUint32)serverEventTimeOutDuration);
        
    iVwsSession->SetServerEventTimeOut( TTimeIntervalMicroSeconds32(serverEventTimeOutDuration) );
    HtcleoEikSrvUiLog(0x0000E7D3u, KErrNone, 0u);
    
    TInt clientRequestTimeOutDuration = EikResourceUtils::ReadTInt32L(
        R_EIK_SYSTEM_VIEW_SERVER_CLIENT_REQUEST_TIME_OUT, iEikonEnv);
    HtcleoEikSrvUiLog(0x0000E7D4u, KErrNone,
        (TUint32)clientRequestTimeOutDuration);
        
    iVwsSession->SetClientRequestTimeOut( TTimeIntervalMicroSeconds32(clientRequestTimeOutDuration) );
    HtcleoEikSrvUiLog(0x0000E7D5u, KErrNone, 0u);

    iVwsSession->EnableServerBlankScreen(EFalse);
    HtcleoEikSrvUiLog(0x0000E7D6u, KErrNone, 0u);
""",
            "view defaults and timeouts",
        )
        source = replace_once(
            source,
            """    // Start Comms
    TInt err = StartC32();
    if (err != KErrNone && err != KErrAlreadyExists)
        {
        User::Leave(err);
        }
    
    err = User::LoadPhysicalDevice(COMMS_PDD_NAME);
    if (err != KErrNone && err != KErrAlreadyExists && err != KErrNotFound)
        {
        User::Leave(err);
        }
        
    err = User::LoadLogicalDevice(COMMS_LDD_NAME);
    if (err != KErrNone && err != KErrAlreadyExists && err != KErrNotFound)
        {
        User::Leave(err);
        }
""",
            """    // Start Comms
    HtcleoEikSrvUiLog(0x0000E7D7u, KErrNone, 0u);
    TInt err = StartC32();
    HtcleoEikSrvUiLog(0x0000E7D8u, err, 0u);
    if (err != KErrNone && err != KErrAlreadyExists)
        {
        User::Leave(err);
        }
    
    err = User::LoadPhysicalDevice(COMMS_PDD_NAME);
    HtcleoEikSrvUiLog(0x0000E7D9u, err, 0u);
    if (err != KErrNone && err != KErrAlreadyExists && err != KErrNotFound)
        {
        User::Leave(err);
        }
        
    err = User::LoadLogicalDevice(COMMS_LDD_NAME);
    HtcleoEikSrvUiLog(0x0000E7DAu, err, 0u);
    if (err != KErrNone && err != KErrAlreadyExists && err != KErrNotFound)
        {
        User::Leave(err);
        }
""",
            "communications",
        )
        source = replace_once(
            source,
            """    // Start notifier server last as these may have plug-ins that rely on the other servers 
    // started here being up and running.
    iNotifyServer = CEikServNotifyServer::NewL(aCtrlFactories.iAlert);

    CleanupStack::Pop(); // aCtrlFactories

    iEikServExtra->iNotifierServerStarter = CIdle::NewL(CActive::EPriorityLow);
    iEikServExtra->iNotifierServerStarter->Start(TCallBack(StartNotifierServerCallBackL, this));

    rootWin.EnableGroupListChangeEvents();

    // Create undertaker active object.
    iUndertaker = CEikUndertaker::NewL(*this);

    // Create an active object to restart servers. 
    iEikServExtra->iServerRestarter = CPeriodic::NewL(CActive::EPriorityStandard);
    }
""",
            """    // Start notifier server last as these may have plug-ins that rely on the other servers 
    // started here being up and running.
    HtcleoEikSrvUiLog(0x0000E7DBu, KErrNone, 0u);
    iNotifyServer = CEikServNotifyServer::NewL(aCtrlFactories.iAlert);
    HtcleoEikSrvUiLog(0x0000E7DCu, KErrNone, iNotifyServer ? 1u : 0u);

    CleanupStack::Pop(); // aCtrlFactories
    HtcleoEikSrvUiLog(0x0000E7DDu, KErrNone, 0u);

    iEikServExtra->iNotifierServerStarter = CIdle::NewL(CActive::EPriorityLow);
    HtcleoEikSrvUiLog(0x0000E7DEu, KErrNone,
        iEikServExtra->iNotifierServerStarter ? 1u : 0u);
    iEikServExtra->iNotifierServerStarter->Start(TCallBack(StartNotifierServerCallBackL, this));
    HtcleoEikSrvUiLog(0x0000E7DFu, KErrNone, 0u);

    rootWin.EnableGroupListChangeEvents();
    HtcleoEikSrvUiLog(0x0000E7E0u, KErrNone, 0u);

    // Create undertaker active object.
    iUndertaker = CEikUndertaker::NewL(*this);
    HtcleoEikSrvUiLog(0x0000E7E1u, KErrNone, iUndertaker ? 1u : 0u);

    // Create an active object to restart servers. 
    iEikServExtra->iServerRestarter = CPeriodic::NewL(CActive::EPriorityStandard);
    HtcleoEikSrvUiLog(0x0000E7E2u, KErrNone,
        iEikServExtra->iServerRestarter ? 1u : 0u);
    }
""",
            "notifier and active objects",
        )

    if NOTIFIER_SERVER_FAIL_OPEN_MARKER not in source:
        source = replace_once(
            source,
            "    HtcleoEikSrvUiLog(0x0000E7DBu, KErrNone, 0u);\n"
            "    iNotifyServer = CEikServNotifyServer::NewL(aCtrlFactories.iAlert);\n"
            "    HtcleoEikSrvUiLog(0x0000E7DCu, KErrNone, iNotifyServer ? 1u : 0u);\n\n"
            "    CleanupStack::Pop(); // aCtrlFactories\n"
            "    HtcleoEikSrvUiLog(0x0000E7DDu, KErrNone, 0u);\n\n"
            "    iEikServExtra->iNotifierServerStarter = CIdle::NewL(CActive::EPriorityLow);\n"
            "    HtcleoEikSrvUiLog(0x0000E7DEu, KErrNone,\n"
            "        iEikServExtra->iNotifierServerStarter ? 1u : 0u);\n"
            "    iEikServExtra->iNotifierServerStarter->Start(TCallBack(StartNotifierServerCallBackL, this));\n"
            "    HtcleoEikSrvUiLog(0x0000E7DFu, KErrNone, 0u);\n",
            "    HtcleoEikSrvUiLog(0x0000E7DBu, KErrNone, 0u);\n"
            "    // HTCLEO_EIKSRVUI_NOTIFIER_SERVER_UI_FAIL_OPEN_V1\n"
            "    // Global notes/notifier plug-ins are secondary to Shell and touch\n"
            "    // bring-up. Keep the owned fields explicitly null and defer both\n"
            "    // construction and the idle StartL callback for later repair.\n"
            "    iNotifyServer = NULL;\n"
            "    HtcleoEikSrvUiLog(0x0000E7DCu, KErrNotSupported, 0x4E465953u);\n\n"
            "    CleanupStack::Pop(); // aCtrlFactories\n"
            "    HtcleoEikSrvUiLog(0x0000E7DDu, KErrNone, 0u);\n\n"
            "    iEikServExtra->iNotifierServerStarter = NULL;\n"
            "    HtcleoEikSrvUiLog(0x0000E7DEu, KErrNotSupported, 0x4E465953u);\n"
            "    HtcleoEikSrvUiLog(0x0000E7DFu, KErrNotSupported, 0x4E465953u);\n",
            "EikSrv notifier server UI-first bypass",
        )

    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVUI_INITIALIZE_DURABLE_LOG=installed "
        "stages=E7C0-E7E2 notifier-server=ui-first-deferred"
    )


if __name__ == "__main__":
    main()
