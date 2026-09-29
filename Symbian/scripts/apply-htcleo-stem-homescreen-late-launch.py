#!/usr/bin/env python3
"""Move ailaunch from Critical Apps to the later Non-critical SSM state."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1"
MARKER = "HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1"
POST_WAIT_MARKER = "HTCLEO_STEM_HOMESCREEN_POST_MATRIXMENU_WAIT_V1"


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
        """\t\tr_cmd_menu,\t// TomP - moved from the Security command list
        // HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1
        // Restore the stock Active Idle supervisor beside MatrixMenu.  Both
        // processes retain deferred rendezvous and the following MultipleWait.
        r_cmd_idle,
        // prio 0xFFE6
        r_cmd_multiwaitforever""",
        """\t\tr_cmd_menu,\t// TomP - moved from the Security command list
        // HTCLEO_STEM_HOMESCREEN_AILAUNCH_V1
        // HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1
        // Active Idle moved to Non-critical: MatrixMenu/AknCap and ECom must
        // complete the critical phase before controller 0x2001952C is queried.
        // prio 0xFFE6
        r_cmd_multiwaitforever""",
        "critical command removal",
    )
    idle_start = text.find(
        "// ---------------------------------------------------------------------------\n"
        "// r_cmd_idle\n"
    )
    menu_start = text.find(
        "// ---------------------------------------------------------------------------\n"
        "// r_cmd_menu\n",
        idle_start + 1,
    )
    if idle_start < 0 or menu_start < 0:
        raise SystemExit("critical ailaunch resource boundary missing")
    text = text[:idle_start] + text[menu_start:]
    monitor = """// Stock monitoring contract used by the restored ailaunch supervisor.
RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore
    {
    restart_mode = 0;
    retries = 32767;
    }
"""
    text = replace_once(text, monitor, "", "critical monitor removal")
    return text


def install_noncritical(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        """        r_cmd_psstate,          // prio 0xFFF0  
        // prio 0xFFC7
        r_cmd_startupready      // Last command, prio 0x0000""",
        """        r_cmd_psstate,          // prio 0xFFF0
        // HTCLEO_STEM_HOMESCREEN_LATE_AILAUNCH_V1
        r_cmd_idle,             // prio 0xFFE7
        r_cmd_idlewait,         // prio 0xFFE6
        r_cmd_startupready      // Last command, prio 0x0000""",
        "noncritical command insertion",
    )
    resource = r'''// ---------------------------------------------------------------------------
// r_cmd_idle -- after Critical Apps/MatrixMenu/AknCap/ECom readiness
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
// r_cmd_idlewait
// ---------------------------------------------------------------------------
//
RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait
    {
    priority = 0xFFE6;
    }

'''
    text = replace_once(
        text,
        "// ---------------------------------------------------------------------------\n"
        "// r_cmd_psstate\n",
        resource
        + "// ---------------------------------------------------------------------------\n"
        + "// r_cmd_psstate\n",
        "noncritical resources",
    )
    monitor = """
// Monitor ailaunch itself.  Its child homescreen restart loop is separately
// bounded by HTCLEO_HOMESCREEN_BOUNDED_RESTART_V1.
RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore
    {
    restart_mode = 0;
    retries = 32767;
    }

"""
    text = replace_once(
        text,
        "// ===========================================================================\n"
        "// Conditional blocks in alphabetical order\n",
        monitor
        + "// ===========================================================================\n"
        + "// Conditional blocks in alphabetical order\n",
        "noncritical monitor",
    )
    return text


def verify(critical: str, noncritical: str) -> None:
    if POST_WAIT_MARKER in critical or POST_WAIT_MARKER in noncritical:
        commands = critical.find("commands =")
        wait = critical.find("r_cmd_multiwaitforever,", commands)
        idle = critical.find("r_cmd_idle,", commands)
        idlewait = critical.find("r_cmd_idlewait", commands)
        checks = {
            "critical markers": (
                critical.count(OLD_MARKER) == 1
                and critical.count(MARKER) == 1
                and critical.count(POST_WAIT_MARKER) == 1
            ),
            "critical post-wait order": 0 <= commands < wait < idle < idlewait,
            "critical late launch": (
                critical.count(
                    "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
                ) == 1
                and critical.count(
                    r'name = "z:\\sys\\bin\\ailaunch.exe";'
                ) == 1
                and critical.count(
                    "RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait"
                ) == 1
            ),
            "noncritical retired": (
                noncritical.count(MARKER) == 1
                and noncritical.count(POST_WAIT_MARKER) == 1
                and "r_cmd_idle," not in noncritical
                and "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
                not in noncritical
                and r'name = "z:\\sys\\bin\\ailaunch.exe";'
                not in noncritical
            ),
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            raise SystemExit(
                "post-wait HomeScreen launch verification failed: "
                + "; ".join(failed)
            )
        return
    checks = {
        "critical markers": (
            critical.count(OLD_MARKER) == 1
            and critical.count(MARKER) == 1
        ),
        "critical has no ailaunch": (
            "r_cmd_idle," not in critical
            and "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle" not in critical
            and r'name = "z:\\sys\\bin\\ailaunch.exe";' not in critical
        ),
        "MatrixMenu critical retained": critical.count(
            r'name = "z:\\sys\\bin\\matrixmenu.exe";'
        ) == 1,
        "critical wait retained": critical.count("r_cmd_multiwaitforever") == 3,
        "noncritical marker": noncritical.count(MARKER) == 1,
        "single late launch": (
            noncritical.count("r_cmd_idle,") == 1
            and noncritical.count(
                "RESOURCE SSM_START_PROCESS_INFO r_cmd_idle"
            ) == 1
            and noncritical.count(
                r'name = "z:\\sys\\bin\\ailaunch.exe";'
            ) == 1
        ),
        "late wait": (
            noncritical.count("r_cmd_idlewait,") == 1
            and noncritical.count(
                "RESOURCE SSM_MULTIPLE_WAIT r_cmd_idlewait"
            ) == 1
        ),
        "startup ready remains last": (
            noncritical.find("r_cmd_idle,")
            < noncritical.find("r_cmd_idlewait,")
            < noncritical.find("r_cmd_startupready")
        ),
        "single monitor": noncritical.count(
            "RESOURCE SSM_MONITOR_INFO r_mon_max_restarts_ignore"
        ) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "late HomeScreen launch verification failed: " + "; ".join(failed)
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
        "noncritical-after-matrixmenu-akncap-ecom-deferred-wait"
    )


if __name__ == "__main__":
    main()
