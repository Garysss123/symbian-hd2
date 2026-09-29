#!/usr/bin/env python3
"""Trace MenuContent server/process/engine reuse after first AppArc completion."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_SERVER_CONTEXT_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


SERVER_INCLUDE = '#include "menusrveng.h"\n'
SERVER_INCLUDE_PATCHED = r'''#include "menusrveng.h"

// HTCLEO_MCS_SERVER_CONTEXT_TRACE_V1
void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);

static TUint32 HtcleoMcsProcessId()
    {
    return (TUint32)RProcess().Id().Id();
    }

static TUint32 HtcleoMcsThreadId()
    {
    return (TUint32)RThread().Id().Id();
    }

static TUint32 HtcleoMcsContentHash(const TDesC& aName)
    {
    TUint32 hash = 2166136261u;
    for (TInt i = 0; i < aName.Length(); ++i)
        {
        hash ^= (TUint32)aName[i];
        hash *= 16777619u;
        }
    return hash;
    }
'''


RUN_SERVER = r'''EXPORT_C TInt RunMenuServer()
    {
    __UHEAP_MARK;
    CTrapCleanup* trapCleanup = NULL;
    CActiveScheduler* activeScheduler = NULL;
    CMenuSrv* server = NULL;

    TInt err = User::RenameThread( KMenuSrvName );
    if ( !err )
        {
        // Create a trap cleanup, make and install an active scheduler.
        err = KErrNoMemory;
        trapCleanup = CTrapCleanup::New();
        if ( trapCleanup )
            {
            activeScheduler = new CActiveScheduler();
            if ( activeScheduler )
                {
                CActiveScheduler::Install( activeScheduler );
                err = CreateServer( server );   // Not pushed (no leaving).
                if ( !err )
                    {
                    err = server->Start( KMenuSrvName );
                    }
                }
            else
            	{
            	err = KErrNoMemory;
            	}
            }
        }
    // Let the caller know how it went.
    RProcess::Rendezvous( err );
    if ( !err )
        {
        CActiveScheduler::Start(); // Start off. Exit timer will stop it.
        }
    CActiveScheduler::Install( NULL );
    delete activeScheduler;
    delete server;
    delete trapCleanup;
    __UHEAP_MARKEND;
    return err;
    }'''


RUN_SERVER_PATCHED = r'''EXPORT_C TInt RunMenuServer()
    {
    __UHEAP_MARK;
    CTrapCleanup* trapCleanup = NULL;
    CActiveScheduler* activeScheduler = NULL;
    CMenuSrv* server = NULL;

    HtcleoMcsLog(0x4D430142u, KErrNone, HtcleoMcsProcessId());
    HtcleoMcsLog(0x4D43014Fu, KErrNone, HtcleoMcsThreadId());
    TInt err = User::RenameThread( KMenuSrvName );
    if ( !err )
        {
        // Create a trap cleanup, make and install an active scheduler.
        err = KErrNoMemory;
        trapCleanup = CTrapCleanup::New();
        if ( trapCleanup )
            {
            activeScheduler = new CActiveScheduler();
            if ( activeScheduler )
                {
                CActiveScheduler::Install( activeScheduler );
                err = CreateServer( server );   // Not pushed (no leaving).
                HtcleoMcsLog(0x4D430143u, err, HtcleoMcsProcessId());
                if ( !err )
                    {
                    err = server->Start( KMenuSrvName );
                    HtcleoMcsLog(0x4D430144u, err, HtcleoMcsProcessId());
                    }
                }
            else
            	{
            	err = KErrNoMemory;
            	}
            }
        }
    // Let the caller know how it went.
    RProcess::Rendezvous( err );
    if ( !err )
        {
        HtcleoMcsLog(0x4D430145u, KErrNone, HtcleoMcsProcessId());
        CActiveScheduler::Start(); // Start off. Exit timer will stop it.
        HtcleoMcsLog(0x4D430146u, KErrNone, HtcleoMcsProcessId());
        }
    CActiveScheduler::Install( NULL );
    delete activeScheduler;
    delete server;
    delete trapCleanup;
    __UHEAP_MARKEND;
    return err;
    }'''


GET_ENGINE = r'''CMenuSrvEng* CMenuSrv::GetEngineL( const TDesC& aName )
    {
    CMenuSrvEng* eng = NULL;
    for ( TInt i = 0; i < iEngines->Count(); i++ )
        {
        eng = (CMenuSrvEng*)(*iEngines)[i];
        if ( eng->ContentName() == aName )
            {
            return eng;
            }
        }
    eng = CMenuSrvEng::NewL( *this, aName );
    CleanupClosePushL( *eng );
    iEngines->AddL( eng );
    CleanupStack::Pop( eng );
    return eng;
    }'''


GET_ENGINE_PATCHED = r'''CMenuSrvEng* CMenuSrv::GetEngineL( const TDesC& aName )
    {
    const TUint32 htcleoNameHash = HtcleoMcsContentHash(aName);
    HtcleoMcsLog(0x4D430147u, aName.Length(), htcleoNameHash);
    HtcleoMcsLog(0x4D430148u, iEngines->Count(), HtcleoMcsProcessId());
    CMenuSrvEng* eng = NULL;
    for ( TInt i = 0; i < iEngines->Count(); i++ )
        {
        eng = (CMenuSrvEng*)(*iEngines)[i];
        if ( eng->ContentName() == aName )
            {
            HtcleoMcsLog(0x4D430149u, i, htcleoNameHash);
            return eng;
            }
        }
    HtcleoMcsLog(0x4D43014Au, KErrNotFound, htcleoNameHash);
    eng = CMenuSrvEng::NewL( *this, aName );
    CleanupClosePushL( *eng );
    iEngines->AddL( eng );
    HtcleoMcsLog(0x4D43014Bu, iEngines->Count(), HtcleoMcsProcessId());
    CleanupStack::Pop( eng );
    return eng;
    }'''


ENGINE_DESTRUCTOR = r'''CMenuSrvEng::~CMenuSrvEng()
    {
    __ASSERT_DEBUG( !iSessions.Count(), User::Invariant() );'''


ENGINE_DESTRUCTOR_PATCHED = r'''CMenuSrvEng::~CMenuSrvEng()
    {
    HtcleoMcsLog(0x4D43014Du, KErrNone, (TUint32)iSessions.Count());
    __ASSERT_DEBUG( !iSessions.Count(), User::Invariant() );'''


ENGINE_ERROR = r'''void CMenuSrvEng::EngineError( TInt aErr )
    {
    // Unrecoverable engine error.'''


ENGINE_ERROR_PATCHED = r'''void CMenuSrvEng::EngineError( TInt aErr )
    {
    HtcleoMcsLog(0x4D43014Cu, aErr, (TUint32)iSessions.Count());
    // Unrecoverable engine error.'''


ENGINE_ERROR_TAIL = r'''    iContentName.Close();
    iTimedClose->Cancel();
    iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );
    }'''


ENGINE_ERROR_TAIL_PATCHED = r'''    iContentName.Close();
    iTimedClose->Cancel();
    iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );
    HtcleoMcsLog(0x4D430150u, aErr, 0u);
    }'''


CLOSE_CALLBACK = r'''LOCAL_C TInt CloseSrvEng( TAny* aSrvEng )
    {
    CMenuSrvEng* srvEng = (CMenuSrvEng*)aSrvEng;'''


CLOSE_CALLBACK_PATCHED = r'''LOCAL_C TInt CloseSrvEng( TAny* aSrvEng )
    {
    CMenuSrvEng* srvEng = (CMenuSrvEng*)aSrvEng;
    HtcleoMcsLog(0x4D43014Eu, KErrNone,
        srvEng ? (TUint32)srvEng->AccessCount() : 0u);'''


def install(server: str, engine: str) -> tuple[str, str]:
    server = replace_once(
        server, SERVER_INCLUDE, SERVER_INCLUDE_PATCHED, "server trace helpers"
    )
    server = replace_once(server, RUN_SERVER, RUN_SERVER_PATCHED, "server lifecycle")
    server = replace_once(server, GET_ENGINE, GET_ENGINE_PATCHED, "engine lookup")
    engine = replace_once(
        engine, ENGINE_DESTRUCTOR, ENGINE_DESTRUCTOR_PATCHED, "engine destructor"
    )
    engine = replace_once(engine, ENGINE_ERROR, ENGINE_ERROR_PATCHED, "engine error")
    engine = replace_once(
        engine,
        ENGINE_ERROR_TAIL,
        ENGINE_ERROR_TAIL_PATCHED,
        "engine error cleanup",
    )
    engine = replace_once(
        engine, CLOSE_CALLBACK, CLOSE_CALLBACK_PATCHED, "timed close callback"
    )
    return server, engine


def verify(server: str, engine: str) -> None:
    combined = server + engine
    checks = {
        "marker": server.count(MARKER) == 1,
        "shared logger": (
            server.count("void HtcleoMcsLog(") == 1
            and engine.count("void HtcleoMcsLog(") == 1
        ),
        "stages": all(
            combined.count(f"0x4D430{stage:03X}u") == (
                2 if stage in (0x144, 0x145) and
                "HTCLEO_MCS_STARTUP_NO_FILE_IO_V1" in engine else 1)
            for stage in range(0x142, 0x151)
        ),
        "pid": server.count("HtcleoMcsProcessId()") == 8,
        "thread id": server.count("HtcleoMcsThreadId()") == 2,
        "full hash": server.count("HtcleoMcsContentHash") == 2,
        "real server retained": server.count("CActiveScheduler::Start();") == 1,
        "real lookup retained": server.count("eng->ContentName() == aName") == 1,
        "fatal path retained": engine.count("iContentName.Close();") == 2,
        "no wait/display": (
            "User::After" not in server
            and "HalFunction" not in server
            and "HalFunction" not in engine
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MCS server context trace failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    server_path = component / "srvsrc/menusrv.cpp"
    engine_path = component / "srvsrc/menusrveng.cpp"
    if not server_path.is_file() or not engine_path.is_file():
        raise SystemExit("missing MenuContent server sources")
    server = server_path.read_text(encoding="latin-1")
    engine = engine_path.read_text(encoding="latin-1")
    if MARKER not in server:
        server, engine = install(server, engine)
    verify(server, engine)
    server_path.write_text(server, encoding="latin-1")
    engine_path.write_text(engine, encoding="latin-1")
    print("HTCLEO_MCS_SERVER_CONTEXT_TRACE=142-150-process-thread-lookup-error-dtor")


if __name__ == "__main__":
    main()
