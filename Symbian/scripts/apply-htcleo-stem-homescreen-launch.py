#!/usr/bin/env python3
"""Restore the stock ailaunch supervisor to the active STEM command list."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1"
LATE_MARKER = "HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1"
POST_WAIT_MARKER = "HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        """\t\tr_cmd_menu,\t// TomP - moved from the Security command list
        // prio 0xFFE6""",
        """\t\tr_cmd_menu,\t// TomP - moved from the Security command list
        // HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1
        // Restore the stock Active Idle supervisor beside MatrixMenu.  Both
        // processes retain deferred rendezvous and the following MultipleWait.
        r_cmd_idle,
        // prio 0xFFE6""",
        "critical command sequence",
    )
    text = replace_once(
        text,
        r"""// ---------------------------------------------------------------------------
// r_cmd_menu
// ---------------------------------------------------------------------------
//
RESOURCE SSM_START_APP_INFO r_cmd_menu""",
        r"""// ---------------------------------------------------------------------------
// r_cmd_idle
// ---------------------------------------------------------------------------
//
RESOURCE SSM_START_PROCESS_INFO r_cmd_idle
    {
    priority = 0xFFE7;
    name = "z:\\sys\\bin\\ailaunch.exe";
    execution_behaviour = ESsmDeferredWaitForSignal;
    monitor_info = r_mon_max_restarts_ignore;
    }

// ---------------------------------------------------------------------------
// r_cmd_menu
// ---------------------------------------------------------------------------
//
RESOURCE SSM_START_APP_INFO r_cmd_menu""",
        "ailaunch process resource",
    )
    text = replace_once(
        text,
        """// monitoring.rss contains resource definitions, so it may not be included
// before entry point.
// #include \"stem_monitoring.rss\"""",
        """// Stock monitoring contract used by the restored ailaunch supervisor.
RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore
    {
    restart_mode = 0;
    retries = 32767;
    }""",
        "monitor resource",
    )
    return text


def verify(text: str) -> None:
    if POST_WAIT_MARKER in text:
        commands = text.find("commands =")
        wait = text.find("r_cmd_multiwaitforever,", commands)
        idle = text.find("r_cmd_idle,", commands)
        idlewait = text.find("r_cmd_idlewait", commands)
        checks = {
            "markers": (
                text.count(MARKER) == 1
                and text.count(LATE_MARKER) == 1
                and text.count(POST_WAIT_MARKER) == 1
            ),
            "post-MatrixMenu order": 0 <= commands < wait < idle < idlewait,
            "single process resource": text.count(
                "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
            ) == 1,
            "real supervisor": text.count(
                r'name = "z:\\sys\\bin\\ailaunch.exe";'
            ) == 1,
            "separate wait": text.count(
                "RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait"
            ) == 1,
            "MatrixMenu retained": text.count(
                r'name = "z:\\sys\\bin\\matrixmenu.exe";'
            ) == 1,
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            raise SystemExit(
                "post-wait STEM HomeScreen launch verification failed: "
                + "; ".join(failed)
            )
        return
    if LATE_MARKER in text:
        checks = {
            "original marker retained": text.count(MARKER) == 1,
            "late marker": text.count(LATE_MARKER) == 1,
            "critical command retired": "r_cmd_idle," not in text,
            "critical resource retired": (
                "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle" not in text
                and r'name = "z:\\sys\\bin\\ailaunch.exe";' not in text
            ),
            "MatrixMenu retained": text.count(
                r'name = "z:\\sys\\bin\\matrixmenu.exe";'
            ) == 1,
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            raise SystemExit(
                "late STEM HomeScreen launch verification failed: "
                + "; ".join(failed)
            )
        return
    checks = {
        "marker": text.count(MARKER) == 1,
        "single command": text.count("r_cmd_idle,") == 1,
        "single process resource": text.count(
            "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
        ) == 1,
        "real supervisor": text.count(
            r'name = "z:\\sys\\bin\\ailaunch.exe";'
        ) == 1,
        "deferred rendezvous": text.count(
            "execution_behaviour = ESsmDeferredWaitForSignal;"
        ) == 2,
        "stock monitor": (
            text.count("monitor_info = r_mon_max_restarts_ignore;") == 1
            and text.count("RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore") == 1
            and text.count("retries = 32767;") == 1
        ),
        "matrix menu retained": text.count(
            r'name = "z:\\sys\\bin\\matrixmenu.exe";'
        ) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("STEM HomeScreen launch repair failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/incubator/stemkit/startup/stem_criticalappscmdlist.rss"
    if not path.is_file():
        raise SystemExit(f"missing STEM critical command list: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_STEM_HOMESCREEN_LAUNCH="
        "stock-ailaunch-deferred-monitor-32767"
    )


if __name__ == "__main__":
    main()
