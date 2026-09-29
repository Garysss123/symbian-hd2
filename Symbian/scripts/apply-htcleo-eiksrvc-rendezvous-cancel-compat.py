#!/usr/bin/env python3
"""Replace the non-working RTimer rendezvous bound with synchronous cancel."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER_V1 = "HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1"
MARKER_TIMER = "HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT_V1"
MARKER_CANCEL = "HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT_V1"
MARKER_READY = "HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT_V1"


CANCEL_BLOCK = r'''
	// HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT_V1
	// The HTCLEO NTimer/DFC path is not operational, as iteration 464 proved:
	// both rendezvous and RTimer statuses remained pending after CreateLocal
	// succeeded.  EKA2 RendezvousCancel synchronously completes an outstanding
	// request (the platform test suite observes KErrNone in the status despite
	// the API comment saying KErrCancel).  Cancel only the lost notification,
	// preserve the already-resumed child, and let Connect's stock CreateSession
	// retry determine whether !EikAppUiServer is registered.
	HtcleoEikConnLog(0x0000E930u, stat.Int(),
		(TUint32)server.ExitType());
	const TInt htcleoCancelResult = server.RendezvousCancel(stat);
	HtcleoEikConnLog(0x0000E931u, htcleoCancelResult,
		(TUint32)stat.Int());
	if (htcleoCancelResult == KErrNone)
		{
		HtcleoEikConnLog(0x0000E932u, stat.Int(),
			(TUint32)server.ExitType());
		server.Close();
		HtcleoEikConnLog(0x0000E933u, KErrNone, 0u);
		return;
		}
	if (stat == KRequestPending)
		{
		// Contract-violation fallback: do not leave a kernel-owned request
		// status on this stack.  This is the sole retained stock wait.
		HtcleoEikConnLog(0x0000E934u, htcleoCancelResult,
			(TUint32)stat.Int());
		User::WaitForRequest(stat);
		HtcleoEikConnLog(0x0000E935u, stat.Int(),
			(TUint32)server.ExitType());
		}
	HtcleoEikConnLog(0x0000E936u, htcleoCancelResult,
		(TUint32)stat.Int());
'''


def verify(source: str) -> None:
    checks = {
        "v1 logger": source.count(MARKER_V1) == 1,
        "timer retired": MARKER_TIMER not in source,
        "cancel marker": source.count(MARKER_CANCEL) == 1,
        "no RTimer": "RTimer htcleoRendezvousTimer" not in source,
        "no dual wait": "WaitForRequest(stat, htcleoTimeoutStatus)" not in source,
        "cancel": source.count("server.RendezvousCancel(stat)") == 1,
        "contract fallback wait": source.count("User::WaitForRequest(stat);") == 1,
        "stock rendezvous": source.count("server.Rendezvous(stat)") == 1,
        "stock resume": source.count("server.Resume()") == 1,
        "stock create": source.count(
            "server.Create(KEikSrvName,KNullDesC,serverUid)"
        )
        == 1,
        "no User::After": "User::After" not in source[source.index(MARKER_V1) :],
    }
    for stage in range(0xE930, 0xE937):
        checks[f"stage {stage:04X}"] = (
            source.count(f"HtcleoEikConnLog(0x0000{stage:04X}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvc rendezvous-cancel verification failed: " + ", ".join(failed)
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
    if MARKER_READY in source:
        if source.count(MARKER_V1) != 1 or source.count(MARKER_READY) != 1:
            raise SystemExit("eiksrvc downstream ready-wait compat is malformed")
        print("HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT=retired-by-ready-wait")
        return
    if MARKER_CANCEL not in source:
        if source.count(MARKER_TIMER) != 1:
            raise SystemExit("expected exactly one iteration-464 timer block")
        start_anchor = "\t// " + MARKER_TIMER + "\n"
        end_anchor = "\tHtcleoEikConnLog(0x0000E918u, stat.Int(), 0u);\n"
        if source.count(start_anchor) != 1 or source.count(end_anchor) != 1:
            raise SystemExit("eiksrvc timer replacement anchors are not unique")
        start = source.index(start_anchor)
        end = source.index(end_anchor, start)
        source = source[:start] + CANCEL_BLOCK + source[end:]
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT=installed "
        "stages=E930-E936 timer=retired child=preserved stock-retry=1"
    )


if __name__ == "__main__":
    main()
