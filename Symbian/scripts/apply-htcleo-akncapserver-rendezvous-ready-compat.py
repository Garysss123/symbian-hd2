#!/usr/bin/env python3
"""Guarantee AknCap process readiness rendezvous after UI construction.

Iteration 486 proves that AknCap completes ConstructAppFromCommandLineL and
enters the permanent CEikonEnv scheduler, while the AppArc starter remains on
its process-rendezvous request.  The request is registered before the child is
resumed, and RProcess::Rendezvous(TInt) completes every outstanding request.
Calling it here is therefore an idempotent HTCLEO compatibility repair: it
completes a missed framework signal, while a framework signal that already
completed simply leaves no request to complete.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_RENDEZVOUS_READY_COMPAT_V1"
ANCHOR = """    if (!error)
        {
        HtcleoAknCapLog(0x0000E20Bu, KErrNone, 0u);
        env->Execute();
        HtcleoAknCapLog(0x0000E20Cu, KErrNone, 0u);
        }
"""
REPLACEMENT = """    if (!error)
        {
        // HTCLEO_AKNCAPSERVER_RENDEZVOUS_READY_COMPAT_V1
        // ConstructAppFromCommandLineL has completed every application,
        // document, AppUi and SetAppReady boundary.  Explicitly complete the
        // process readiness request before entering the permanent scheduler.
        HtcleoAknCapLog(0x0000E215u, KRequestPending, 0u);
        RProcess::Rendezvous(KErrNone);
        HtcleoAknCapLog(0x0000E216u, KErrNone, 0u);
        HtcleoAknCapLog(0x0000E20Bu, KErrNone, 0u);
        env->Execute();
        HtcleoAknCapLog(0x0000E20Cu, KErrNone, 0u);
        }
"""


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "single explicit rendezvous": (
            source.count("RProcess::Rendezvous(KErrNone);") == 1
        ),
        "pre-signal record": source.count(
            "HtcleoAknCapLog(0x0000E215u, KRequestPending, 0u);"
        )
        == 1,
        "post-signal record": source.count(
            "HtcleoAknCapLog(0x0000E216u, KErrNone, 0u);"
        )
        == 1,
        "signal before scheduler": (
            source.index("RProcess::Rendezvous(KErrNone);")
            < source.index("env->Execute();")
        ),
        "no startup timer or wait": (
            "User::After" not in source
            and "User::WaitForRequest" not in source
        ),
        "no display probe": (
            "EHalGroupPlatformSpecific1, 2" not in source
            and "c6400000" not in source.lower()
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknCap rendezvous-ready verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src/AknCapServerEntry.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing AknCapServer input: {source_path}")

    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        count = source.count(ANCHOR)
        if count != 1:
            raise SystemExit(
                f"AknCap rendezvous-ready anchor: expected one, found {count}"
            )
        source = source.replace(ANCHOR, REPLACEMENT, 1)

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print("HTCLEO_AKNCAPSERVER_RENDEZVOUS_READY_COMPAT=installed stages=E215-E216")


if __name__ == "__main__":
    main()
