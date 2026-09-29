#!/usr/bin/env python3
"""Bound the proven WServ RunL event trace so later delivery logs survive."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_RUNL_TRACE_BOUND_V1"

OLD = r'''void CRawEventReceiver::RunL()
	{
//__PROFILE_START(11);
	HtcleoWsLog(0x0000045Eu, iStatus.Int(),
		static_cast<TUint32>(iEventBuf.Event().Type()));
'''

NEW = r'''void CRawEventReceiver::RunL()
	{
//__PROFILE_START(11);
	// HTCLEO_WSERV_RUNL_TRACE_BOUND_V1
	static TInt htcleoRunLTraceCount = 0;
	if (htcleoRunLTraceCount < 32)
		{
		HtcleoWsLog(0x0000045Eu, iStatus.Int(),
			static_cast<TUint32>(iEventBuf.Event().Type()));
		++htcleoRunLTraceCount;
		}
'''


def install(source: str) -> str:
    if MARKER in source:
        return source
    if source.count(OLD) != 1:
        raise SystemExit("WServ RunL trace-bound anchor mismatch")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "bound": source.count("htcleoRunLTraceCount < 32") == 1,
        "stage": source.count("0x0000045Eu") == 1,
        "real status and type": (
            source.count("iStatus.Int()") >= 2
            and source.count("iEventBuf.Event().Type()") >= 1
        ),
        "stock request retained": (
            source.count("UserSvr::RequestEvent(iEventBuf,iStatus);") == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("WServ RunL trace-bound verification failed: "
                         + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/EVENT.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print("HTCLEO_WSERV_RUNL_TRACE_BOUND=first32-real-events-045e")


if __name__ == "__main__":
    main()
