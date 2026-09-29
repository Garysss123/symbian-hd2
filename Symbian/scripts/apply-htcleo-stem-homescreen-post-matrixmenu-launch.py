#!/usr/bin/env python3
"""Start HomeScreen after MatrixMenu's critical MultipleWait completes."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1"
LATE_MARKER = "HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1"
MARKER = "HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_critical(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        """        // HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1
        // Active Idle moved to Non-critical: MatrixMenu/AknCap and ECom must
        // complete the critical phase before controller 0x2001952C is queried.
        // prio 0xFFE6
        r_cmd_multiwaitforever""",
        """        // HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1
        // HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1
        // First wait for MatrixMenu/AknCap/ECom; only then start Active Idle.
        // prio 0xFFE6
        r_cmd_multiwaitforever,
        r_cmd_idle,             // prio 0xFFE5
        r_cmd_idlewait          // prio 0xFFE4""",
        "post-MatrixMenu command order",
    )
    resources = r'''// ---------------------------------------------------------------------------
// r_cmd_idle -- reachable only after MatrixMenu's MultipleWait returns
// ---------------------------------------------------------------------------
//
RESOURCE SSM_START_PROCESS_INFO r_cmd_idle
    {
    priority = 0xFFE5;
    name = "z:\\sys\\bin\\ailaunch.exe";
    execution_behaviour = ESsmDeferredWaitForSignal;
    monitor_info = r_mon_max_restarts_ignore;
    }

// ---------------------------------------------------------------------------
// r_cmd_idlewait
// ---------------------------------------------------------------------------
//
RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait
    {
    priority = 0xFFE4;
    }

'''
    text = replace_once(
        text,
        "// ---------------------------------------------------------------------------\n"
        "// r_cmd_psstate\n",
        resources
        + "// ---------------------------------------------------------------------------\n"
        + "// r_cmd_psstate\n",
        "post-MatrixMenu resources",
    )
    monitor = """
// Monitor ailaunch itself; its homescreen child loop remains bounded.
RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore
    {
    restart_mode = 0;
    retries = 32767;
    }

"""
    text = replace_once(
        text,
        "// ===========================================================================\n"
        "// DLL data items in alphabetical order\n",
        monitor
        + "// ===========================================================================\n"
        + "// DLL data items in alphabetical order\n",
        "critical monitor",
    )
    return text


def install_noncritical(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        """        // HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1
        r_cmd_idle,             // prio 0xFFE7
        r_cmd_idlewait,         // prio 0xFFE6
        r_cmd_startupready      // Last command, prio 0x0000""",
        """        // HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1
        // HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1
        // This state is not reached on the current STEM route; launch moved
        // behind the reachable Critical Apps MatrixMenu wait.
        r_cmd_startupready      // Last command, prio 0x0000""",
        "noncritical command retirement",
    )
    start = text.find(
        "// ---------------------------------------------------------------------------\n"
        "// r_cmd_idle -- after Critical Apps/MatrixMenu/AknCap/ECom readiness\n"
    )
    end = text.find(
        "// ---------------------------------------------------------------------------\n"
        "// r_cmd_psstate\n",
        start + 1,
    )
    if start < 0 or end < 0:
        raise SystemExit("noncritical ailaunch resource boundary missing")
    text = text[:start] + text[end:]
    monitor = """
// Monitor ailaunch itself.  Its child homescreen restart loop is separately
// bounded by HTCLEO_HOMESCREEN_BOUNDED_RESTART_V1.
RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore
    {
    restart_mode = 0;
    retries = 32767;
    }

"""
    text = replace_once(text, monitor, "\n", "noncritical monitor removal")
    return text


def verify(critical: str, noncritical: str) -> None:
    commands = critical.find("commands =")
    wait = critical.find("r_cmd_multiwaitforever,", commands)
    idle = critical.find("r_cmd_idle,", commands)
    idlewait = critical.find("r_cmd_idlewait", commands)
    checks = {
        "critical markers": (
            critical.count(OLD_MARKER) == 1
            and critical.count(LATE_MARKER) == 1
            and critical.count(MARKER) == 1
        ),
        "reachable order": 0 <= commands < wait < idle < idlewait,
        "critical launch": (
            critical.count("r_cmd_idle,") == 1
            and critical.count(
                "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
            ) == 1
            and critical.count(
                r'name = "z:\\sys\\bin\\ailaunch.exe";'
            ) == 1
            and critical.count(
                "RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait"
            ) == 1
        ),
        "critical monitor": critical.count(
            "RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore"
        ) == 1,
        "noncritical markers": (
            noncritical.count(LATE_MARKER) == 1
            and noncritical.count(MARKER) == 1
        ),
        "noncritical retired": (
            "r_cmd_idle," not in noncritical
            and "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
            not in noncritical
            and r'name = "z:\\sys\\bin\\ailaunch.exe";'
            not in noncritical
            and "RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore"
            not in noncritical
        ),
        "startup ready retained": noncritical.count("r_cmd_startupready") == 3,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "post-MatrixMenu HomeScreen launch verification failed: "
            + "; ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    startup = args.root / "sf/incubator/stemkit/startup"
    critical_path = startup / "stem_criticalappscmdlist.rss"
    noncritical_path = startup / "stem_noncriticalcmdlist.rss"
    if not critical_path.is_file() or not noncritical_path.is_file():
        raise SystemExit("STEM command-list sources missing")
    critical = install_critical(critical_path.read_text(encoding="latin-1"))
    noncritical = install_noncritical(
        noncritical_path.read_text(encoding="latin-1")
    )
    verify(critical, noncritical)
    critical_path.write_text(critical, encoding="latin-1")
    noncritical_path.write_text(noncritical, encoding="latin-1")
    print(
        "HTCLEO_STEM_HOMESCREEN_LAUNCH_ORDER="
        "critical-post-matrixmenu-wait-deferred-wait"
    )


if __name__ == "__main__":
    main()
