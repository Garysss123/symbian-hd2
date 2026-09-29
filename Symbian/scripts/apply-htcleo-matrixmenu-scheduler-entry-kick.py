#!/usr/bin/env python3
"""Retire the legacy unowned scheduler-entry signal after panic46 evidence.

The old workaround completed a stack TRequestStatus with no matching CActive.
740/741 now reach real callbacks and heartbeat, then panic EReqStrayEvent.
Keep stage1013 for existing display correlation, but let genuine requests wake
the scheduler. Tested historical packages retain their original transformer.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_SCHEDULER_ENTRY_KICK_V1"
RETIRED_MARKER = "HTCLEO_MATRIXMENU_SCHEDULER_ENTRY_KICK_RETIRED_V1"
PREREQUISITE = "HTCLEO_MATRIXMENU_EIKSTART_DURABLE_LOG_V2"


OLD = r'''    if (!error)
        {
        HtcleoMenuLog(0x4D4D100Bu, KErrNone, 0u);
        env->Execute();
        HtcleoMenuLog(0x4D4D100Cu, KErrNone, 0u);
        }'''


NEW = r'''    if (!error)
        {
        HtcleoMenuLog(0x4D4D100Bu, KErrNone, 0u);
        // HTCLEO_MATRIXMENU_SCHEDULER_ENTRY_KICK_V1
        // Do not log after RequestComplete and before Execute: synchronous
        // file IPC could consume the exact signal being preserved here.
        HtcleoMenuLog(0x4D4D1013u, KErrNone, 1u);
        TRequestStatus htcleoSchedulerEntryKick = KRequestPending;
        TRequestStatus* htcleoSchedulerEntryKickPtr =
            &htcleoSchedulerEntryKick;
        User::RequestComplete(htcleoSchedulerEntryKickPtr, KErrNone);
        env->Execute();
        HtcleoMenuLog(0x4D4D100Cu, KErrNone, 0u);
        }'''


RETIRED = r'''    if (!error)
        {
        HtcleoMenuLog(0x4D4D100Bu, KErrNone, 0u);
        // HTCLEO_MATRIXMENU_SCHEDULER_ENTRY_KICK_RETIRED_V1
        // No synthetic signal: a stack status has no owning CActive. Real
        // event/timer requests now drive Execute; surplus credits panic46.
        // Preserve this stage for the established display guard only.
        HtcleoMenuLog(0x4D4D1013u, KErrNone, 0u);
        env->Execute();
        HtcleoMenuLog(0x4D4D100Cu, KErrNone, 0u);
        }'''


def install(source: str) -> str:
    if RETIRED_MARKER in source:
        return source
    anchor = NEW if MARKER in source else OLD
    count = source.count(anchor)
    if count != 1:
        raise SystemExit(f"Execute entry anchor: expected one, found {count}")
    return source.replace(anchor, RETIRED, 1)


def verify(source: str) -> None:
    marker_index = source.index(RETIRED_MARKER)
    execute_index = source.index("env->Execute();", marker_index)
    between = source[marker_index:execute_index]
    checks = {
        "local EikStart prerequisite": source.count(PREREQUISITE) == 1,
        "retirement marker": source.count(RETIRED_MARKER) == 1 and MARKER not in source,
        "single stage": source.count("0x4D4D1013u") == 1,
        "no unowned request": "htcleoSchedulerEntryKick" not in source,
        "no synthetic wake": "User::RequestComplete" not in between
            and "RequestSignal" not in between and "TRequestStatus" not in between,
        "retired stage detail": "HtcleoMenuLog(0x4D4D1013u, KErrNone, 0u);" in source,
        "stock Execute retained": source.count("env->Execute();") == 1,
        "stock post-Execute stage retained": source.count("0x4D4D100Cu") == 1,
        "no wait timer or direct dispatch": (
            "User::After" not in RETIRED
            and "RTimer" not in RETIRED
            and "WaitFor" not in RETIRED
            and "RunIfReady" not in RETIRED
            and "RunL(" not in RETIRED
            and "ActivateTopViewL" not in RETIRED
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmgui.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_SCHEDULER_ENTRY_KICK="
        "retired-unowned-signal stage=1013-detail0 stock-scheduler-and-view"
    )


if __name__ == "__main__":
    main()
