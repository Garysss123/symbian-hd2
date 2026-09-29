#!/usr/bin/env python3
"""Add 1 MiB startup and heartbeat logging to the stock HomeScreen chain."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HOMESCREEN_DURABLE_LOG_V1"
ECOM_MARKER = "HTCLEO_HOMESCREEN_ECOM_STATUS_GUARD_V1"

LOGGER_H = r'''#ifndef HTCLEO_HOME_LOG_H
#define HTCLEO_HOME_LOG_H

#include <e32std.h>

void HtcleoHomeLog(TUint32 aStage, TInt aResult, TUint32 aDetail);

#endif
'''

LOGGER_CPP = r'''// HTCLEO_HOMESCREEN_DURABLE_LOG_V1
#include "htcleohomelog.h"
#include <e32base.h>
#include <f32file.h>

void HtcleoHomeLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;
    _LIT(KDir, "C:\\Symbian3\\");
    _LIT(KPath, "C:\\Symbian3\\HSLOG.TXT");
    (void)fs.MkDirAll(KDir);
    RFile file;
    r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound)
        r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
    TInt position = 0;
    if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);
    if (r == KErrNone && position <= (1048576 - 128))
        {
        TBuf8<128> record;
        _LIT8(KPrefix, "HTCLEO_HOME ");
        record.Append(KPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)r, EHex, 8);
        record.Append('\n');
        (void)file.Write(record);
        }
    file.Close();
    fs.Close();
    }
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def add_logger_to_mmp(text: str, common_anchor: str) -> str:
    if "SOURCE          htcleohomelog.cpp" in text:
        return text
    return replace_once(
        text,
        common_anchor,
        common_anchor + "SOURCE          htcleohomelog.cpp\n",
        "logger MMP source",
    )


def add_efsrv_to_mmp(text: str) -> str:
    if "LIBRARY         efsrv.lib" in text:
        return text
    return replace_once(
        text,
        "LIBRARY         euser.lib",
        "LIBRARY         euser.lib\nLIBRARY         efsrv.lib",
        "logger efsrv library",
    )


def install_main(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "debug.h"\n',
        '#include "debug.h"\n#include "htcleohomelog.h"\n',
        "main logger include",
    )
    text = replace_once(
        text,
        """GLDEF_C TInt E32Main()
    {
    __TICK("FW: Entry point");""",
        """GLDEF_C TInt E32Main()
    {
    // HTCLEO_HOMESCREEN_DURABLE_LOG_V1
    HtcleoHomeLog(0x484F0000u, KErrNone, 0u);
    __TICK("FW: Entry point");""",
        "HomeScreen E32Main entry",
    )
    text = replace_once(
        text,
        """    CTrapCleanup* cleanupStack = CTrapCleanup::New();
    if (!cleanupStack)""",
        """    CTrapCleanup* cleanupStack = CTrapCleanup::New();
    HtcleoHomeLog(0x484F0001u,
        cleanupStack ? KErrNone : KErrNoMemory,
        (TUint32)cleanupStack);
    if (!cleanupStack)""",
        "cleanup stack",
    )
    text = replace_once(
        text,
        """    TInt aiFwResult = KErrNone;
    TRAP( aiFwResult, """,
        """    TInt aiFwResult = KErrNone;
    HtcleoHomeLog(0x484F0002u, KErrNone, 0u);
    TRAP( aiFwResult, """,
        "framework trap entry",
    )
    text = replace_once(
        text,
        """        );

    // Clean up before exit""",
        """        );
    HtcleoHomeLog(0x484F0003u, aiFwResult, 0u);

    // Clean up before exit""",
        "framework trap exit",
    )
    text = replace_once(
        text,
        """    __PRINT_IF_ERROR(aiFwResult, "FW: Framework exit with error %d");
    return aiFwResult;""",
        """    __PRINT_IF_ERROR(aiFwResult, "FW: Framework exit with error %d");
    HtcleoHomeLog(0x484F0004u, aiFwResult, 0u);
    return aiFwResult;""",
        "HomeScreen E32Main exit",
    )
    return text


def install_aifw(text: str) -> str:
    if MARKER in text or "0x484F0100u" in text:
        return text
    text = replace_once(
        text,
        '#include "debug.h"\n',
        '#include "debug.h"\n#include "htcleohomelog.h"\n',
        "aifw logger include",
    )
    text = replace_once(
        text,
        """// Constants


// ======== MEMBER FUNCTIONS ========""",
        """// Constants

static TInt HtcleoHomeHeartbeat(TAny*)
    {
    HtcleoHomeLog(0x484F01FFu, KErrNone, 0x414C4956u); // ALIV
    return ETrue;
    }

// ======== MEMBER FUNCTIONS ========""",
        "heartbeat callback",
    )
    text = replace_once(
        text,
        """void CAiFw::ConstructL()
    {
    __PRINTS( "*** CAiFw::ConstructL" );""",
        """void CAiFw::ConstructL()
    {
    HtcleoHomeLog(0x484F0100u, KErrNone, 0u);
    __PRINTS( "*** CAiFw::ConstructL" );""",
        "framework ConstructL entry",
    )
    text = replace_once(
        text,
        """    iRepository = CRepository::NewL( TUid::Uid( KCRUidActiveIdleLV ) );
#endif
        
    TInt value( 0 );
    
    iRepository->Get( KAiMainUIController, value );""",
        """    iRepository = CRepository::NewL( TUid::Uid( KCRUidActiveIdleLV ) );
#endif
    HtcleoHomeLog(0x484F0101u, KErrNone, (TUint32)iRepository);
        
    TInt value( 0 );
    const TInt htcleoControllerKeyResult =
        iRepository->Get( KAiMainUIController, value );
    HtcleoHomeLog(0x484F0102u, htcleoControllerKeyResult,
        (TUint32)value);""",
        "controller CenRep",
    )
    text = replace_once(
        text,
        """    iUiControllerManager = CAiUiControllerManager::NewL( this );
    
    iFactory = CAiPluginFactory::NewL( *iUiControllerManager );
    
    iStateManager = CAiStateManager::NewL( *iFactory );
               
    iStateProvider = CAiStateProvider::NewL( *iStateManager );
    
    iEventHandler = CAiEventHandler::NewL( *iFactory );""",
        """    iUiControllerManager = CAiUiControllerManager::NewL( this );
    HtcleoHomeLog(0x484F0103u, KErrNone, (TUint32)iUiControllerManager);
    
    iFactory = CAiPluginFactory::NewL( *iUiControllerManager );
    HtcleoHomeLog(0x484F0104u, KErrNone, (TUint32)iFactory);
    
    iStateManager = CAiStateManager::NewL( *iFactory );
    HtcleoHomeLog(0x484F0105u, KErrNone, (TUint32)iStateManager);
               
    iStateProvider = CAiStateProvider::NewL( *iStateManager );
    HtcleoHomeLog(0x484F0106u, KErrNone, (TUint32)iStateProvider);
    
    iEventHandler = CAiEventHandler::NewL( *iFactory );
    HtcleoHomeLog(0x484F0107u, KErrNone, (TUint32)iEventHandler);""",
        "framework members",
    )
    text = replace_once(
        text,
        """CAiFw::~CAiFw()
    {        
    if ( iNotifyHandler )""",
        """CAiFw::~CAiFw()
    {
    HtcleoHomeLog(0x484F0108u, KErrNone, 0u);
    if ( iHtcleoHeartbeat )
        {
        iHtcleoHeartbeat->Cancel();
        delete iHtcleoHeartbeat;
        iHtcleoHeartbeat = NULL;
        }
    if ( iNotifyHandler )""",
        "framework destructor",
    )
    text = replace_once(
        text,
        """EXPORT_C void CAiFw::RunL()
    {
    __TICK( "CAiFw::RunL" );""",
        """EXPORT_C void CAiFw::RunL()
    {
    HtcleoHomeLog(0x484F0110u, KErrNone, 0u);
    __TICK( "CAiFw::RunL" );""",
        "RunL entry",
    )
    text = replace_once(
        text,
        """    registry->RegisterL();
    CleanupStack::PopAndDestroy( registry );""",
        """    registry->RegisterL();
    HtcleoHomeLog(0x484F0111u, KErrNone, 0x102750F0u);
    CleanupStack::PopAndDestroy( registry );""",
        "idle property registration",
    )
    text = replace_once(
        text,
        """    iUiControllerManager->RunApplicationL();
    
    __PRINTS( "*** CAiFw::RunL - done" );""",
        """    HtcleoHomeLog(0x484F0112u, KErrNone, 0u);
    iUiControllerManager->RunApplicationL();
    HtcleoHomeLog(0x484F0113u, KErrNone, 0u);
    
    __PRINTS( "*** CAiFw::RunL - done" );""",
        "controller application loop",
    )
    text = replace_once(
        text,
        """void CAiFw::AppEnvReadyL()
    {
    __TICK( "CAiFw::AppEnvReadyL" );""",
        """void CAiFw::AppEnvReadyL()
    {
    HtcleoHomeLog(0x484F0120u, KErrNone, 0u);
    __TICK( "CAiFw::AppEnvReadyL" );""",
        "AppEnvReady entry",
    )
    text = replace_once(
        text,
        """    CCoeEnv& env( iUiControllerManager->CoeEnv() );

    // Create WS pluign manager
    iWsPluginManager = CAiWsPluginManager::NewL( env );""",
        """    CCoeEnv& env( iUiControllerManager->CoeEnv() );
    HtcleoHomeLog(0x484F0121u, KErrNone, (TUint32)&env);

    // Create WS pluign manager
    iWsPluginManager = CAiWsPluginManager::NewL( env );
    HtcleoHomeLog(0x484F0122u, KErrNone, (TUint32)iWsPluginManager);""",
        "WS plugin manager",
    )
    text = replace_once(
        text,
        """    iStateProvider->StartL( env );
               
    // CenRep notifier""",
        """    iStateProvider->StartL( env );
    HtcleoHomeLog(0x484F0123u, KErrNone, 0u);

    if ( !iHtcleoHeartbeat )
        {
        iHtcleoHeartbeat = CPeriodic::NewL( CActive::EPriorityIdle );
        iHtcleoHeartbeat->Start( 5000000, 5000000,
            TCallBack( HtcleoHomeHeartbeat, this ) );
        HtcleoHomeLog(0x484F0124u, KErrNone,
            (TUint32)iHtcleoHeartbeat);
        }
               
    // CenRep notifier""",
        "heartbeat start",
    )
    text = replace_once(
        text,
        """    iNotifyHandlerESS->StartListeningL();
    
    __PRINTS( "*** CAiFw::AppEnvReadyL - done" );""",
        """    iNotifyHandlerESS->StartListeningL();
    HtcleoHomeLog(0x484F0125u, KErrNone, 0u);
    
    __PRINTS( "*** CAiFw::AppEnvReadyL - done" );""",
        "AppEnvReady exit",
    )
    return text


def install_aifw_header(text: str) -> str:
    if "iHtcleoHeartbeat" in text:
        return text
    return replace_once(
        text,
        """    TBool iLibrariesLoaded;
    
    RLibrary iLibrary1;""",
        """    TBool iLibrariesLoaded;

    // HTCLEO_HOMESCREEN_DURABLE_LOG_V1: 5-second process heartbeat.
    CPeriodic* iHtcleoHeartbeat;
    
    RLibrary iLibrary1;""",
        "heartbeat member",
    )


def install_ecom_observer(text: str) -> str:
    if ECOM_MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "aiecomobserver.h"\n',
        '#include "aiecomobserver.h"\n#include "htcleohomelog.h"\n',
        "ECom observer logger include",
    )
    return replace_once(
        text,
        """void CAiEcomObserver::RunL()
\t{   
    // Store completion status
    TInt status( iStatus.Int() );

    // Continue request
    StartObserving();

    // Notify observers
    if ( status == KErrNone )
        {
        NotifyObservers();
        }    
\t}""",
        """void CAiEcomObserver::RunL()
\t{
    // HTCLEO_HOMESCREEN_ECOM_STATUS_GUARD_V1
    const TInt status( iStatus.Int() );
    HtcleoHomeLog(0x484F0130u, status, 0u);
    if ( status != KErrNone )
        {
        // A terminated session is not a registry change.  Retire this failed
        // subscription instead of immediately reusing its stale handle.
        return;
        }
    StartObserving();
    NotifyObservers();
    HtcleoHomeLog(0x484F0131u, KErrNone, 0u);
\t}""",
        "HomeScreen ECom status guard",
    )


def install_idle_register(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include <activeidle2domainpskeys.h>\n',
        '#include <activeidle2domainpskeys.h>\n#include "htcleohomelog.h"\n',
        "idle register logger include",
    )
    text = replace_once(
        text,
        """void CAiIdleAppRegisterImpl::RegisterL()
    {
    // Give own uid for phone.
    TInt setPSResult = SetIdleAppPS();""",
        """void CAiIdleAppRegisterImpl::RegisterL()
    {
    // HTCLEO_HOMESCREEN_DURABLE_LOG_V1
    HtcleoHomeLog(0x484F0140u, KErrNone, 0x102750F0u);
    // Give own uid for phone.
    TInt setPSResult = SetIdleAppPS();
    HtcleoHomeLog(0x484F0141u, setPSResult, 0x102750F0u);""",
        "idle register entry",
    )
    text = replace_once(
        text,
        """        const TInt err = DefineIdleAppPS();
        if( err == KErrNone || err == KErrAlreadyExists )
            {
            // Try setting again
            setPSResult = SetIdleAppPS();
            }""",
        """        const TInt err = DefineIdleAppPS();
        HtcleoHomeLog(0x484F0142u, err, KActiveIdleUid);
        if( err == KErrNone || err == KErrAlreadyExists )
            {
            // Try setting again
            setPSResult = SetIdleAppPS();
            HtcleoHomeLog(0x484F0143u, setPSResult, 0x102750F0u);
            }""",
        "idle property define",
    )
    text = replace_once(
        text,
        """    SetIdleSendNumKeysToPhonePS();
    }""",
        """    SetIdleSendNumKeysToPhonePS();
    HtcleoHomeLog(0x484F0144u, setPSResult, 0x102750F0u);
    }""",
        "idle register exit",
    )
    return text


def install_hslaunch(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "hslaunch.h"\n',
        '#include "hslaunch.h"\n#include "htcleohomelog.h"\n',
        "hslaunch logger include",
    )
    text = replace_once(
        text,
        """void RunAppL()
    {
    // Construct active scheduler.""",
        """void RunAppL()
    {
    HtcleoHomeLog(0x484F0200u, KErrNone, 0u);
    // Construct active scheduler.""",
        "hslaunch RunApp entry",
    )
    text = replace_once(
        text,
        """    RProcess::Rendezvous(KErrNone);
    
    // Start active scheduler.""",
        """    RProcess::Rendezvous(KErrNone);
    HtcleoHomeLog(0x484F0201u, KErrNone, 0u);
    
    // Start active scheduler.""",
        "hslaunch rendezvous",
    )
    text = replace_once(
        text,
        """TInt E32Main()
    {            
    TInt error = KErrNone;""",
        """TInt E32Main()
    {
    // HTCLEO_HOMESCREEN_DURABLE_LOG_V1
    HtcleoHomeLog(0x484F0210u, KErrNone, 0u);
    TInt error = KErrNone;""",
        "hslaunch E32Main entry",
    )
    text = replace_once(
        text,
        """    __UHEAP_MARKEND;
    
    return error;""",
        """    __UHEAP_MARKEND;
    HtcleoHomeLog(0x484F0211u, error, 0u);
    
    return error;""",
        "hslaunch E32Main exit",
    )
    text = replace_once(
        text,
        """void CHsLaunch::ConstructL()
    {
    iShutdownMonitor = CHsShutdownMonitor::NewL( *this );""",
        """void CHsLaunch::ConstructL()
    {
    HtcleoHomeLog(0x484F0220u, KErrNone, 0u);
    iShutdownMonitor = CHsShutdownMonitor::NewL( *this );""",
        "hslaunch ConstructL",
    )
    text = replace_once(
        text,
        """void CHsLaunch::RunL()
    {    
    // Create app or connect to existing.""",
        """void CHsLaunch::RunL()
    {
    HtcleoHomeLog(0x484F0230u, iStatus.Int(), 0u);
    // Create app or connect to existing.""",
        "hslaunch RunL entry",
    )
    text = replace_once(
        text,
        """    TInt processError = process.Create( KHsExeName, KNullDesC );
    if( processError == KErrAlreadyExists )""",
        """    TInt processError = process.Create( KHsExeName, KNullDesC );
    HtcleoHomeLog(0x484F0231u, processError,
        (TUint32)process.Handle());
    if( processError == KErrAlreadyExists )""",
        "homescreen process create",
    )
    text = replace_once(
        text,
        """        TRAP( monitorError, InitProcessMonitorL( process.Id() ) );
        }""",
        """        TRAP( monitorError, InitProcessMonitorL( process.Id() ) );
        HtcleoHomeLog(0x484F0232u, monitorError,
            (TUint32)process.Id().Id());
        }""",
        "homescreen process monitor",
    )
    text = replace_once(
        text,
        """        process.Resume();""",
        """        process.Resume();
        HtcleoHomeLog(0x484F0233u, KErrNone,
            (TUint32)process.Id().Id());""",
        "homescreen process resume",
    )
    text = replace_once(
        text,
        """    process.Close();""",
        """    process.Close();
    HtcleoHomeLog(0x484F0234u, processError,
        (TUint32)processExisted);""",
        "homescreen process close",
    )
    return text


def verify(paths: dict[str, Path]) -> None:
    joined = "\n".join(path.read_text(encoding="latin-1") for path in paths.values())
    checks = {
        "marker coverage": joined.count(MARKER) >= 4,
        "ECom guard": joined.count(ECOM_MARKER) == 1,
        "logger capacity": "1048576 - 128" in paths["logger_cpp"].read_text(encoding="latin-1"),
        "heartbeat": (
            joined.count("0x484F01FFu") == 1
            and joined.count("5000000, 5000000") == 1
        ),
        "main stages": all(f"0x484F{stage:04X}u" in joined for stage in range(0x0000, 0x0005)),
        "idle UID stages": all(f"0x484F{stage:04X}u" in joined for stage in range(0x0140, 0x0145)),
        "launcher stages": all(
            f"0x484F{stage:04X}u" in joined
            for stage in (0x0200, 0x0201, 0x0210, 0x0211, 0x0220,
                          0x0230, 0x0231, 0x0232, 0x0233, 0x0234)
        ),
        "no fabricated UI": all(token not in joined for token in ("SetPixel", "CreateWindowL")),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HomeScreen durable log verification failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/idlefw"
    paths = {
        "logger_h": component / "inc/common/htcleohomelog.h",
        "logger_cpp": component / "src/common/htcleohomelog.cpp",
        "main": component / "src/framework/main.cpp",
        "aifw": component / "src/framework/aifw.cpp",
        "aifw_h": component / "inc/framework/aifw.h",
        "ecom": component / "src/framework/aiecomobserver.cpp",
        "idle": component / "src/idleint/aiidleappregister.cpp",
        "launch": component / "hslaunch/src/hslaunch.cpp",
        "homescreen_mmp": component / "group/homescreen.mmp",
        "aifw_mmp": component / "group/aifw.mmp",
        "idle_mmp": component / "group/aiidleint.mmp",
        "launch_mmp": component / "hslaunch/group/hslaunch.mmp",
    }
    for key, path in paths.items():
        if key not in ("logger_h", "logger_cpp") and not path.is_file():
            raise SystemExit(f"missing HomeScreen source: {path}")

    paths["logger_h"].write_text(LOGGER_H, encoding="latin-1")
    paths["logger_cpp"].write_text(LOGGER_CPP, encoding="latin-1")
    paths["main"].write_text(install_main(paths["main"].read_text(encoding="latin-1")), encoding="latin-1")
    paths["aifw"].write_text(install_aifw(paths["aifw"].read_text(encoding="latin-1")), encoding="latin-1")
    paths["aifw_h"].write_text(install_aifw_header(paths["aifw_h"].read_text(encoding="latin-1")), encoding="latin-1")
    paths["ecom"].write_text(install_ecom_observer(paths["ecom"].read_text(encoding="latin-1")), encoding="latin-1")
    paths["idle"].write_text(install_idle_register(paths["idle"].read_text(encoding="latin-1")), encoding="latin-1")
    paths["launch"].write_text(install_hslaunch(paths["launch"].read_text(encoding="latin-1")), encoding="latin-1")

    for key in ("aifw_mmp", "idle_mmp"):
        text = paths[key].read_text(encoding="latin-1")
        text = add_logger_to_mmp(text, "SOURCE          aifwpanic.cpp\n")
        text = add_efsrv_to_mmp(text)
        paths[key].write_text(text, encoding="latin-1")
    homescreen_mmp = paths["homescreen_mmp"].read_text(encoding="latin-1")
    if "SOURCE          htcleohomelog.cpp" not in homescreen_mmp:
        homescreen_mmp = replace_once(
            homescreen_mmp,
            "SOURCE          main.cpp\n",
            "SOURCE          main.cpp\n\n"
            "SOURCEPATH      ../src/common\n"
            "SOURCE          htcleohomelog.cpp\n",
            "homescreen logger source",
        )
    if "SOURCE          htcleohomelog.cpp\n\nSOURCEPATH      ../src/framework\n" not in homescreen_mmp:
        homescreen_mmp = replace_once(
            homescreen_mmp,
            "SOURCE          htcleohomelog.cpp\n\nSTART RESOURCE",
            "SOURCE          htcleohomelog.cpp\n\n"
            "SOURCEPATH      ../src/framework\n\nSTART RESOURCE",
            "homescreen resource sourcepath",
        )
    homescreen_mmp = add_efsrv_to_mmp(homescreen_mmp)
    paths["homescreen_mmp"].write_text(homescreen_mmp, encoding="latin-1")
    launch_mmp = paths["launch_mmp"].read_text(encoding="latin-1")
    if "SOURCE\t\t\thtcleohomelog.cpp" not in launch_mmp:
        launch_mmp = replace_once(
            launch_mmp,
            "SOURCE\t\t\thsshutdownmonitor.cpp\n",
            "SOURCE\t\t\thsshutdownmonitor.cpp\n\n"
            "SOURCEPATH\t\t../../src/common\n"
            "SOURCE\t\t\thtcleohomelog.cpp\n",
            "hslaunch logger source",
        )
        launch_mmp = replace_once(
            launch_mmp,
            "USERINCLUDE\t\t../inc\n",
            "USERINCLUDE\t\t../inc\nUSERINCLUDE\t\t../../inc/common\n",
            "hslaunch logger include",
        )
        launch_mmp = replace_once(
            launch_mmp,
            "LIBRARY\t\t\tbafl.lib   // descriptors\n",
            "LIBRARY\t\t\tbafl.lib   // descriptors\n"
            "LIBRARY\t\t\tefsrv.lib  // durable HSLOG\n",
            "hslaunch logger library",
        )
        paths["launch_mmp"].write_text(launch_mmp, encoding="latin-1")

    verify(paths)
    print(
        "HTCLEO_HOMESCREEN_DURABLE_LOG="
        "HSLOG-1m-startup-ecom-idleuid-launch-heartbeat-5s"
    )


if __name__ == "__main__":
    main()
