#!/usr/bin/env python3
"""Keep one EikSrv child while AknCap polls for server registration.

Iteration 465 proved that synchronous RendezvousCancel releases the client,
but the stock four restart attempts run faster than EikSrv can finish its
heavily instrumented construction.  The attempts also create competing server
children.  For AknCap only, retain one accepted child start and use bounded
CreateSession retries.  The existing durable logger supplies cooperative file
server IPC between attempts; no timer, delay, display probe, or policy bypass
is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER_LOG = "HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1"
MARKER_CANCEL = "HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT_V1"
MARKER_READY = "HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT_V1"
MARKER_RETRY = "HTCLEO_EIKSRVC_SINGLE_CHILD_READY_RETRY_V1"


TARGET_OLD = r'''#ifdef __HTCLEO_EIKSRVC_CONNECT_LOG__
#include <f32file.h>

// HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1
static void HtcleoEikConnLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
'''


TARGET_NEW = r'''// HTCLEO_EIKSRVC_SINGLE_CHILD_READY_RETRY_V1
static TBool HtcleoEikConnTarget()
    {
#ifdef __HTCLEO_EIKSRVC_CONNECT_LOG__
    return RProcess().SecureId().iId == 0x10207218u;
#else
    return EFalse;
#endif
    }

#ifdef __HTCLEO_EIKSRVC_CONNECT_LOG__
#include <f32file.h>

// HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1
static void HtcleoEikConnLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
'''


LOGGER_GATE_OLD = r'''    if (RProcess().SecureId().iId != 0x10207218u)
        {
        return;
        }
'''


LOGGER_GATE_NEW = r'''    if (!HtcleoEikConnTarget())
        {
        return;
        }
'''


RETRY_INIT_OLD = r'''	TInt err=KErrNone;
	TInt retry=KNumConnectRetries;
	FOREVER
'''


RETRY_INIT_NEW = r'''	TInt err=KErrNone;
	TInt retry=KNumConnectRetries;
	const TBool htcleoSingleChildRetry=HtcleoEikConnTarget();
	TBool htcleoServerStartIssued=EFalse;
	if (htcleoSingleChildRetry)
		{
		retry=64;
		HtcleoEikConnLog(0x0000E940u, KErrNone, (TUint32)retry);
		}
	FOREVER
'''


START_BRANCH_OLD = r'''			HtcleoEikConnLog(0x0000E904u, err, (TUint32)retry);
			HtcleoEikConnLog(0x0000E905u, KErrNone, (TUint32)retry);
			TRAP(err,StartServerL());
			HtcleoEikConnLog(0x0000E906u, err, (TUint32)retry);
			if ((err!=KErrNone) && (err!=KErrAlreadyExists))
				{
				HtcleoEikConnLog(0x0000E907u, err, (TUint32)retry);
				break;
				}
			HtcleoEikConnLog(0x0000E908u, err, (TUint32)retry);
'''


START_BRANCH_NEW = r'''			HtcleoEikConnLog(0x0000E904u, err, (TUint32)retry);
			if (htcleoSingleChildRetry && htcleoServerStartIssued)
				{
				HtcleoEikConnLog(0x0000E941u, err, (TUint32)retry);
				continue;
				}
			HtcleoEikConnLog(0x0000E905u, KErrNone, (TUint32)retry);
			TRAP(err,StartServerL());
			HtcleoEikConnLog(0x0000E906u, err, (TUint32)retry);
			if ((err!=KErrNone) && (err!=KErrAlreadyExists))
				{
				HtcleoEikConnLog(0x0000E907u, err, (TUint32)retry);
				break;
				}
			HtcleoEikConnLog(0x0000E908u, err, (TUint32)retry);
			if (htcleoSingleChildRetry)
				{
				htcleoServerStartIssued=ETrue;
				HtcleoEikConnLog(0x0000E942u, err, (TUint32)retry);
				}
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "durable logger": source.count(MARKER_LOG) == 1,
        "rendezvous policy": (
            source.count(MARKER_CANCEL) == 1 and MARKER_READY not in source
        ) or (
            source.count(MARKER_READY) == 1 and MARKER_CANCEL not in source
        ),
        "single-child marker": source.count(MARKER_RETRY) == 1,
        "target helper": source.count("HtcleoEikConnTarget()") == 3,
        "single SID literal": source.count("0x10207218u") == 1,
        "stock retry declaration": source.count("TInt retry=KNumConnectRetries;") == 1,
        "bounded target retry": source.count("retry=64;") == 1,
        "start issued flag": source.count("htcleoServerStartIssued=ETrue;") == 1,
        "skip repeated child": source.count(
            "htcleoSingleChildRetry && htcleoServerStartIssued"
        )
        == 1,
        "one CreateSession": source.count(
            "CreateSession(EIKAPPUI_SERVER_NAME,Version())"
        )
        == 1,
        "one StartServerL call": source.count("TRAP(err,StartServerL())") == 1,
        "one process create": source.count(
            "server.Create(KEikSrvName,KNullDesC,serverUid)"
        )
        == 1,
        "timer retired": "RTimer htcleoRendezvousTimer" not in source,
        "no delay": "User::After" not in source[source.index(MARKER_LOG) :],
    }
    for stage in range(0xE940, 0xE943):
        checks[f"stage {stage:04X}"] = (
            source.count(f"HtcleoEikConnLog(0x0000{stage:04X}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvc single-child retry verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()
    source_path = (
        args.epocroot
        / "sf/mw/classicui/commonuisupport/uikon/srvsrc/EIKSRVC.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER_RETRY not in source:
        source = replace_once(source, TARGET_OLD, TARGET_NEW, "target helper")
        source = replace_once(
            source, LOGGER_GATE_OLD, LOGGER_GATE_NEW, "logger target gate"
        )
        source = replace_once(source, RETRY_INIT_OLD, RETRY_INIT_NEW, "retry init")
        source = replace_once(
            source, START_BRANCH_OLD, START_BRANCH_NEW, "server-start branch"
        )
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVC_SINGLE_CHILD_READY_RETRY=installed "
        "attempts=64 stages=E940-E942 child-starts=1 timer=none"
    )


if __name__ == "__main__":
    main()
