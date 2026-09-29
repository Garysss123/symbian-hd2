#!/usr/bin/env python3
"""Restore EikSrv's real rendezvous wait after hardware proved readiness.

Iteration 485 proves that the single EikSrv child completes construction and
calls RProcess::Rendezvous(KErrNone).  The older HTCLEO workaround cancelled
that request immediately, so the AknCap client could exhaust all CreateSession
polls before the server reached ExecuteD.  Keep the existing AknCap-only retry
policy as a fallback, but wait for the proven rendezvous notification first.
"""

from pathlib import Path
import sys


MARKER = "HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT_V1"

OLD = r'''	// HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT_V1
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

NEW = r'''	// HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT_V1
	// Iteration 485 hardware-proved that this single child reaches
	// RProcess::Rendezvous(KErrNone).  Wait for that real readiness signal
	// instead of cancelling it and racing 64 unpaced CreateSession attempts.
	HtcleoEikConnLog(0x0000E950u, stat.Int(),
		(TUint32)server.ExitType());
	User::WaitForRequest(stat);
	HtcleoEikConnLog(0x0000E951u, stat.Int(),
		(TUint32)server.ExitType());
'''


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-htcleo-eiksrvc-rendezvous-ready-wait.py EPOCROOT")

    root = Path(sys.argv[1])
    source_path = root / "sf/mw/classicui/commonuisupport/uikon/srvsrc/EIKSRVC.CPP"
    source = source_path.read_text(encoding="latin-1")

    if MARKER not in source:
        if source.count(OLD) != 1:
            raise SystemExit("expected exactly one rendezvous-cancel compatibility block")
        source = source.replace(OLD, NEW, 1)
        source_path.write_text(source, encoding="latin-1", newline="")

    checks = {
        "ready-wait marker": source.count(MARKER) == 1,
        "pre-wait stage": source.count("HtcleoEikConnLog(0x0000E950u") == 1,
        "post-wait stage": source.count("HtcleoEikConnLog(0x0000E951u") == 1,
        "single wait": source.count("User::WaitForRequest(stat);") == 1,
        "cancel removed": "server.RendezvousCancel(stat)" not in source,
        "cancel marker removed": "HTCLEO_EIKSRVC_RENDEZVOUS_CANCEL_COMPAT_V1" not in source,
        "timer remains absent": "htcleoRendezvousTimer" not in source,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))

    print("HTCLEO_EIKSRVC_RENDEZVOUS_READY_WAIT=installed stages=E950-E951")


if __name__ == "__main__":
    main()
