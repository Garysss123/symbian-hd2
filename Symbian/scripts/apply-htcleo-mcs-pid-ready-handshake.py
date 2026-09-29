#!/usr/bin/env python3
"""Use child-specific MCS readiness for Matrix without a rendezvous request."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MCS_PID_READY_HANDSHAKE_V1"

HEADER = '''#ifndef HTCLEO_MCS_READY_H
#define HTCLEO_MCS_READY_H
#include <e32property.h>
// HTCLEO_MCS_PID_READY_HANDSHAKE_V1
const TUid KHtcleoMcsReadyCategory = {0x101F4CD2};
inline TInt HtcleoMcsReadyKey(TUint64 aPid, TUint& aKey)
    {
    // A separate key for each exact supported PID avoids late old-child writes.
    if (!aPid || aPid > 0x00FFFFFFu)
        return KErrOverflow;
    aKey = 0x7E000000u | (TUint)aPid;
    return KErrNone;
    }
inline void HtcleoMcsPublishReady(TInt aStage)
    {
    TUint key = 0;
    if (HtcleoMcsReadyKey(RProcess().Id().Id(), key) == KErrNone)
        (void)RProperty::Set(KHtcleoMcsReadyCategory, key, aStage);
    }
#endif
'''

HELPER = '''// HTCLEO_MCS_PID_READY_HANDSHAKE_V1
// HTCLEO_MCS_READY_RESOURCE_SAFE_DIAGNOSTICS_V1
LOCAL_C void HtcleoMcsReadyTrace(TInt aCreate, TUint32 aPid, TInt aPrepare,
        TUint aKey, TInt aResult, TInt aReady, TInt aPolls)
    {
    // Called only after process handles/property cleanup; never hold a
    // suspended child while opening a diagnostic file.
    HtcleoMcsLog(0x4D430194u, aCreate, aPid);
    HtcleoMcsLog(0x4D430195u, aPrepare, aKey);
    HtcleoMcsLog(0x4D430196u, aResult, (TUint32)aReady);
    HtcleoMcsLog(0x4D430197u, aResult, (TUint32)aPolls);
    }

LOCAL_C TInt HtcleoStartMcsReadyProcess()
    {
    RProcess server;
    TInt result = server.Create(KMenuSrvExe, KNullDesC, EOwnerThread);
    const TUint32 pid = result == KErrNone ? (TUint32)server.Id().Id() : 0u;
    if (result != KErrNone)
        {
        server.Close();
        HtcleoMcsReadyTrace(result, pid, result, 0u, result, 0, 0);
        return result;
        }

    TUint key = 0;
    TBool propertyDefined = EFalse;
    result = HtcleoMcsReadyKey(server.Id().Id(), key);
    if (result == KErrNone)
        {
        _LIT_SECURITY_POLICY_PASS(KReadyRead);
        _LIT_SECURITY_POLICY_PASS(KReadyWrite);
        result = RProperty::Define(KHtcleoMcsReadyCategory, key,
            RProperty::EInt, KReadyRead, KReadyWrite);
        if (result == KErrAlreadyExists)
            result = KErrNone;
        propertyDefined = result == KErrNone;
        }
    if (result == KErrNone)
        result = RProperty::Set(KHtcleoMcsReadyCategory, key, 0);
    if (result != KErrNone)
        {
        // Only our newly-created, still-suspended child is aborted here.
        server.Kill(result);
        server.Close();
        if (propertyDefined)
            (void)RProperty::Delete(KHtcleoMcsReadyCategory, key);
        HtcleoMcsReadyTrace(KErrNone, pid, result, key, result, 0, 0);
        return result;
        }

    // No Rendezvous/Subscribe/Logon request owns a stack status in this path.
    // Timer-backed yields are used only with the repaired bring-up timer;
    // 500 is an attempt bound, not a hard real-time guarantee if a kernel API stalls.
    server.Resume();
    const TInt KReadyAttempts = 500;
    TInt ready = 0;
    TInt polls = 0;
    result = KErrTimedOut;
    for (; polls < KReadyAttempts; ++polls)
        {
        const TInt read = RProperty::Get(KHtcleoMcsReadyCategory, key, ready);
        if (read != KErrNone)
            {
            result = read;
            break;
            }
        if (server.ExitType() != EExitPending)
            {
            result = server.ExitType() == EExitPanic ? KErrGeneral : server.ExitReason();
            if (result >= KErrNone)
                result = KErrDied;
            break;
            }
        if (ready == 2)
            {
            result = KErrNone;
            break;
            }
        if (ready < 0 || ready > 2)
            {
            result = ready < 0 ? ready : KErrCorrupt;
            break;
            }
        User::After(10000);
        }
    (void)RProperty::Delete(KHtcleoMcsReadyCategory, key);
    // A resumed server may already have other clients. Do not kill it on timeout.
    server.Close();
    HtcleoMcsReadyTrace(KErrNone, pid, KErrNone, key, result, ready, polls);
    return result;
    }

'''


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"MCS readiness anchor mismatch: {old[:90]!r}")
    return text.replace(old, new, 1)


def patch_client(text: str) -> str:
    if MARKER in text:
        if "HTCLEO_MCS_READY_RESOURCE_SAFE_DIAGNOSTICS_V1" not in text:
            start = text.index("// " + MARKER)
            end = text.index("LOCAL_C TInt StartServer()", start)
            text = text[:start] + HELPER + text[end:]
        return text
    text = once(text, '#include <e32debug.h>\n', '#include <e32debug.h>\n#include "htcleomcsready.h"\n')
    return once(text, "LOCAL_C TInt StartServer()\n    {", HELPER + '''LOCAL_C TInt StartServer()
    {
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        return HtcleoStartMcsReadyProcess();''')


def patch_server(text: str) -> str:
    if "HtcleoMcsPublishReady(2);" in text:
        return text
    text = once(text, '#include "menusrveng.h"\n', '#include "menusrveng.h"\n#include "htcleomcsready.h"\n')
    text = once(text, "    RProcess::Rendezvous( err );", '''    // Child-owned key: 1 proves Start returned success, 2 crosses Rendezvous.
    HtcleoMcsPublishReady(err == KErrNone ? 1 : err);
    RProcess::Rendezvous( err );''')
    return once(text, '''        HtcleoMcsLog(0x4D430145u, KErrNone, HtcleoMcsProcessId());
        CActiveScheduler::Start();''', '''        HtcleoMcsLog(0x4D430145u, KErrNone, HtcleoMcsProcessId());
        HtcleoMcsPublishReady(2);
        CActiveScheduler::Start();''')


def patch_engine(text: str) -> str:
    if "aStage > 0x4D430197u" in text:
        return text
    return once(text, "aStage > 0x4D430193u", "aStage > 0x4D430197u")


def verify(client: str, server: str, engine: str, header: str) -> None:
    if client.count(MARKER) != 1 or header != HEADER:
        raise SystemExit("MCS readiness identity/header mismatch")
    if client.count("HTCLEO_MCS_READY_RESOURCE_SAFE_DIAGNOSTICS_V1") != 1:
        raise SystemExit("resource-safe readiness diagnostics missing")
    helper = client[client.index("LOCAL_C TInt HtcleoStartMcsReadyProcess()"):
                    client.index("LOCAL_C TInt StartServer()")]
    if any(call in helper for call in (".Rendezvous(", ".Subscribe(", ".Logon(", "WaitForRequest(", "TRequestStatus ")):
        raise SystemExit("no pending async stack request or unbounded request wait in Matrix startup")
    if not (helper.index("RProperty::Set(") < helper.index("server.Resume();") < helper.index("polls < KReadyAttempts")):
        raise SystemExit("child property must be reset before Resume and bounded polling")
    if "KReadyAttempts = 500" not in helper or helper.count("User::After(10000);") != 1:
        raise SystemExit("bounded cooperative readiness poll changed")
    if helper.index("server.ExitType() != EExitPending") > helper.index("if (ready == 2)"):
        raise SystemExit("ready must not accept an exited child")
    if helper.rfind("server.Kill(") > helper.index("server.Resume();"):
        raise SystemExit("never kill resumed server on timeout")
    if "RProperty::Delete(KHtcleoMcsReadyCategory, key);" not in helper:
        raise SystemExit("child-specific readiness property cleanup missing")
    if "HtcleoMcsLog(" in helper:
        raise SystemExit("do not log while owning the startup process handle")
    if helper.count("server.Close();\n") != 3 or helper.count("HtcleoMcsReadyTrace(") != 3:
        raise SystemExit("each exit must release the process before diagnostic logging")
    if "propertyDefined" not in helper or "if (result >= KErrNone)" not in helper:
        raise SystemExit("property cleanup and nonnegative child-exit normalization required")
    if client.count("CreateSession( KMenuSrvName, version )") != 2:
        raise SystemExit("real session connection must remain the final criterion")
    for stage in range(0x194, 0x198):
        if client.count(f"0x4D430{stage:03X}u") != 1:
            raise SystemExit("readiness boundary record missing/duplicated")
    if "aStage > 0x4D430197u" not in engine:
        raise SystemExit("readiness records not enabled for Matrix client")
    start = server.index("err = server->Start( KMenuSrvName );")
    if not (start < server.index("HtcleoMcsPublishReady(err == KErrNone ? 1 : err);")
            < server.index("RProcess::Rendezvous( err );")
            < server.index("HtcleoMcsPublishReady(2);") < server.index("CActiveScheduler::Start();")):
        raise SystemExit("child registration/rendezvous/scheduler proof order changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/homescreensrv/menucontentsrv"
    client_path = base / "src/menu.cpp"
    server_path = base / "srvsrc/menusrv.cpp"
    engine_path = base / "srvsrc/menusrveng.cpp"
    client = patch_client(client_path.read_text(encoding="latin-1"))
    server = patch_server(server_path.read_text(encoding="latin-1"))
    engine = patch_engine(engine_path.read_text(encoding="latin-1"))
    verify(client, server, engine, HEADER)
    client_path.write_text(client, encoding="latin-1")
    server_path.write_text(server, encoding="latin-1")
    engine_path.write_text(engine, encoding="latin-1")
    (base / "inc/htcleomcsready.h").write_text(HEADER, encoding="latin-1")
    print("HTCLEO_MCS_READY_HANDSHAKE=matrix-per-pid-property-500x10ms-no-rendezvous-request-real-createsession")


if __name__ == "__main__":
    main()
