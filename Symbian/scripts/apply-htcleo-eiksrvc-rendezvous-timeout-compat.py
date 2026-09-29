#!/usr/bin/env python3
"""Add the HTCLEO lost-rendezvous compatibility path to eiksrvc.dll."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER_V1 = "HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1"
MARKER_V2 = "HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT_V1"
MARKER_V3 = "HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT_V1"
MARKER_READY = "HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT_V1"


OLD_WAIT = r'''
	HtcleoEikConnLog(0x0000E917u, KErrNone, 0u);
	User::WaitForRequest(stat);             // wait for start or death
	HtcleoEikConnLog(0x0000E918u, stat.Int(), 0u);
'''


NEW_WAIT = r'''
	HtcleoEikConnLog(0x0000E917u, KErrNone, 0u);
	// HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT_V1
	// Some QSD8250 boots reach the server-side Rendezvous call while the
	// client request remains pending forever.  Bound only that notification
	// wait.  On timeout cancel the request, preserve the child process, return
	// success from StartServerL, and let Connect's stock CreateSession retry
	// determine whether the server is actually ready.
	TBool htcleoRendezvousTimedOut = EFalse;
	RTimer htcleoRendezvousTimer;
	const TInt htcleoTimerResult = htcleoRendezvousTimer.CreateLocal();
	HtcleoEikConnLog(0x0000E920u, htcleoTimerResult, 10000000u);
	if (htcleoTimerResult == KErrNone)
		{
		TRequestStatus htcleoTimeoutStatus;
		htcleoRendezvousTimer.After(htcleoTimeoutStatus,
			TTimeIntervalMicroSeconds32(10000000));
		HtcleoEikConnLog(0x0000E921u, stat.Int(),
			(TUint32)htcleoTimeoutStatus.Int());
		User::WaitForRequest(stat, htcleoTimeoutStatus);
		HtcleoEikConnLog(0x0000E922u, stat.Int(),
			(TUint32)htcleoTimeoutStatus.Int());
		if (stat == KRequestPending)
			{
			htcleoRendezvousTimedOut = ETrue;
			HtcleoEikConnLog(0x0000E923u, KErrTimedOut,
				(TUint32)server.ExitType());
			const TInt htcleoCancelResult = server.RendezvousCancel(stat);
			HtcleoEikConnLog(0x0000E924u, htcleoCancelResult,
				(TUint32)stat.Int());
			if (htcleoCancelResult != KErrNone || stat == KRequestPending)
				{
				HtcleoEikConnLog(0x0000E929u, htcleoCancelResult,
					(TUint32)stat.Int());
				User::WaitForRequest(stat);
				htcleoRendezvousTimedOut = EFalse;
				}
			}
		else
			{
			htcleoRendezvousTimer.Cancel();
			User::WaitForRequest(htcleoTimeoutStatus);
			HtcleoEikConnLog(0x0000E925u, stat.Int(),
				(TUint32)htcleoTimeoutStatus.Int());
			}
		htcleoRendezvousTimer.Close();
		}
	else
		{
		HtcleoEikConnLog(0x0000E926u, htcleoTimerResult, 0u);
		User::WaitForRequest(stat);             // preserve stock fallback
		}
	if (htcleoRendezvousTimedOut)
		{
		HtcleoEikConnLog(0x0000E927u, KErrTimedOut,
			(TUint32)server.ExitType());
		server.Close();
		HtcleoEikConnLog(0x0000E928u, KErrNone, 0u);
		return;
		}
	HtcleoEikConnLog(0x0000E918u, stat.Int(), 0u);
'''


def verify(source: str) -> None:
    checks = {
        "v1 logger": source.count(MARKER_V1) == 1,
        "v2 marker": source.count(MARKER_V2) == 1,
        "dual wait": source.count(
            "User::WaitForRequest(stat, htcleoTimeoutStatus);"
        )
        == 1,
        "timer cancel wait": source.count(
            "User::WaitForRequest(htcleoTimeoutStatus);"
        )
        == 1,
        "cancel": source.count("server.RendezvousCancel(stat)") == 1,
        "ten second timer": source.count("TTimeIntervalMicroSeconds32(10000000)")
        == 1,
        "stock rendezvous": source.count("server.Rendezvous(stat)") == 1,
        "stock resume": source.count("server.Resume()") == 1,
        "stock create": source.count("server.Create(KEikSrvName,KNullDesC,serverUid)")
        == 1,
    }
    for stage in range(0xE920, 0xE92A):
        checks[f"stage {stage:04X}"] = (
            source.count(f"HtcleoEikConnLog(0x0000{stage:04X}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("eiksrvc rendezvous compat verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()
    source_path = (
        args.epocroot
        / "sf/mw/classicui/commonuisupport/uikon/srvsrc/EIKSRVC.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER_READY in source:
        if source.count(MARKER_V1) != 1 or source.count(MARKER_READY) != 1:
            raise SystemExit("eiksrvc downstream ready-wait compat is malformed")
        print("HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT=retired-by-ready-wait")
        return
    if MARKER_V3 in source:
        if source.count(MARKER_V1) != 1 or source.count(MARKER_V3) != 1:
            raise SystemExit("eiksrvc downstream cancel compat is malformed")
        print("HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT=retired-by-cancel-compat")
        return
    if MARKER_V2 not in source:
        if source.count(OLD_WAIT) != 1:
            raise SystemExit(
                f"eiksrvc rendezvous wait: expected one anchor, found {source.count(OLD_WAIT)}"
            )
        source = source.replace(OLD_WAIT, NEW_WAIT, 1)
    elif "User::WaitForRequest(htcleoTimeoutStatus);" not in source:
        # Allow a failed/repeated local build to tighten the already-installed
        # V1 compatibility block without requiring an unsafe source-tree reset.
        cancel_anchor = "\t\t\thtcleoRendezvousTimer.Cancel();\n"
        if source.count(cancel_anchor) != 1:
            raise SystemExit(
                "eiksrvc rendezvous timer-cancel anchor is not unique"
            )
        source = source.replace(
            cancel_anchor,
            cancel_anchor + "\t\t\tUser::WaitForRequest(htcleoTimeoutStatus);\n",
            1,
        )
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print("HTCLEO_EIKSRVC_RENDEZVOUS_COMPAT=installed timeout-us=10000000 stages=E920-E929")


if __name__ == "__main__":
    main()
