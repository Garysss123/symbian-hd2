#!/usr/bin/env python3
"""Keep one durable record per repeated EikSrv readiness poll.

Iteration 466 proved the single-child policy and reached a fully constructed
EikSrv, but four write/flush records per failed CreateSession made only 27 of
64 attempts complete during the one-minute hardware run.  Preserve the first
attempt's dense trace and E941 as the cooperative-yield/result record, while
retiring E902/E903/E904 only on repeated single-child readiness polls.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER_PREVIOUS = "HTCLEO_EIKSRVC_SINGLE_CHILD_READY_RETRY_V1"
MARKER = "HTCLEO_EIKSRVC_COMPACT_READY_POLL_LOG_V1"


OLD = r'''	FOREVER
		{
		HtcleoEikConnLog(0x0000E902u, KErrNone, (TUint32)retry);
		err=CreateSession(EIKAPPUI_SERVER_NAME,Version());
		HtcleoEikConnLog(0x0000E903u, err, (TUint32)retry);
		if ((--retry>0) && ((err==KErrNotFound) || (err==KErrServerTerminated)))
			{
			HtcleoEikConnLog(0x0000E904u, err, (TUint32)retry);
			if (htcleoSingleChildRetry && htcleoServerStartIssued)
				{
				HtcleoEikConnLog(0x0000E941u, err, (TUint32)retry);
				continue;
				}
'''


NEW = r'''	FOREVER
		{
		// HTCLEO_EIKSRVC_COMPACT_READY_POLL_LOG_V1
		const TBool htcleoReadinessPoll=
			htcleoSingleChildRetry && htcleoServerStartIssued;
		if (!htcleoReadinessPoll)
			{
			HtcleoEikConnLog(0x0000E902u, KErrNone, (TUint32)retry);
			}
		err=CreateSession(EIKAPPUI_SERVER_NAME,Version());
		if (!htcleoReadinessPoll)
			{
			HtcleoEikConnLog(0x0000E903u, err, (TUint32)retry);
			}
		if ((--retry>0) && ((err==KErrNotFound) || (err==KErrServerTerminated)))
			{
			if (htcleoReadinessPoll)
				{
				HtcleoEikConnLog(0x0000E941u, err, (TUint32)retry);
				continue;
				}
			HtcleoEikConnLog(0x0000E904u, err, (TUint32)retry);
'''


def verify(source: str) -> None:
    checks = {
        "previous policy": source.count(MARKER_PREVIOUS) == 1,
        "compact marker": source.count(MARKER) == 1,
        "readiness selector": source.count("const TBool htcleoReadinessPoll=") == 1,
        "selector expression": source.count(
            "htcleoSingleChildRetry && htcleoServerStartIssued;"
        ) == 1,
        "two dense-log gates": source.count("if (!htcleoReadinessPoll)") == 2,
        "one compact poll gate": source.count("if (htcleoReadinessPoll)") == 1,
        "one E902": source.count("HtcleoEikConnLog(0x0000E902u") == 1,
        "one E903": source.count("HtcleoEikConnLog(0x0000E903u") == 1,
        "one E904": source.count("HtcleoEikConnLog(0x0000E904u") == 1,
        "one E941": source.count("HtcleoEikConnLog(0x0000E941u") == 1,
        "one CreateSession": source.count(
            "CreateSession(EIKAPPUI_SERVER_NAME,Version())"
        ) == 1,
        "bounded retry": source.count("retry=64;") == 1,
        "single child start": source.count("htcleoServerStartIssued=ETrue;") == 1,
        "timer retired": "RTimer htcleoRendezvousTimer" not in source,
        "no delay": "User::After" not in source,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvc compact readiness-log verification failed: "
            + ", ".join(failed)
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
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                f"compact readiness-loop anchor: expected exactly one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVC_COMPACT_READY_POLL_LOG=installed "
        "dense-first=E902-E904 repeated=E941 flushes-per-failed-poll=1"
    )


if __name__ == "__main__":
    main()
