#!/usr/bin/env python3
"""Publish deterministic local startup metadata for non-cellular HTCLEO.

The reference UI-services command list asks the miscellaneous adaptation for
the global startup mode and hidden-reset state.  On HTCLEO there is no Symbian
phone/baseband adaptation to complete that asynchronous request.  Replace only
the active command-list membership with local P&S writes for the supported
normal startup path.  Keep the original custom-command resource definition in
the source tree for ABI and historical clarity.
"""

from pathlib import Path
import sys


MARKER = "HTCLEO_LOCAL_NORMAL_STARTUP_MODE"
ACTIVE_ENTRY = "        r_cmd_startupmode,\n"
LOCAL_ENTRIES = (
    f"        // {MARKER}: fixed non-cellular normal startup metadata.\n"
    "        r_cmd_htcleo_startupmode,\n"
    "        r_cmd_htcleo_startupreason,\n"
)
ORIGINAL_SECTION = """// ---------------------------------------------------------------------------
// r_cmd_startupmode
// ---------------------------------------------------------------------------
//
RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_startupmode
"""
LOCAL_RESOURCES = """// ---------------------------------------------------------------------------
// r_cmd_htcleo_startupmode / r_cmd_htcleo_startupreason
// HTCLEO is a non-cellular product and always follows the normal boot path.
// ---------------------------------------------------------------------------
//
RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupmode
    {
    priority = 0xFFE8;
    severity = ECmdCriticalSeverity;
    category = 0x101F8766; // KPSUidStartup
    key      = 0x00000042; // KPSGlobalStartupMode
    value    = 100;        // EStartupModeNormal
    }

RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupreason
    {
    priority = 0xFFE7;
    severity = ECmdCriticalSeverity;
    category = 0x101F8766; // KPSUidStartup
    key      = 0x00000045; // KPSStartupReason
    value    = 100;        // ENormalStartup
    }

"""


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} <full-epoc-root>")

    root = Path(sys.argv[1]).resolve()
    path = root / "sf/incubator/stemkit/startup/stem_uiservicescmdlist.rss"
    text = path.read_text(encoding="utf-8")

    entry_count = text.count(ACTIVE_ENTRY)
    marker_count = text.count(MARKER)
    local_mode_count = text.count(
        "RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupmode"
    )
    local_reason_count = text.count(
        "RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupreason"
    )
    exact_local_resources_count = text.count(LOCAL_RESOURCES)
    original_definition_count = text.count(
        "RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_startupmode"
    )

    if (
        entry_count == 1
        and marker_count == 0
        and local_mode_count == 0
        and local_reason_count == 0
        and exact_local_resources_count == 0
        and text.count(ORIGINAL_SECTION) == 1
    ):
        text = text.replace(ACTIVE_ENTRY, LOCAL_ENTRIES, 1)
        text = text.replace(ORIGINAL_SECTION, LOCAL_RESOURCES + ORIGINAL_SECTION, 1)
        path.write_text(text, encoding="utf-8")
        state = "applied"
    elif (
        entry_count == 0
        and marker_count == 1
        and local_mode_count == 1
        and local_reason_count == 1
        and exact_local_resources_count == 1
    ):
        state = "installed"
    else:
        raise RuntimeError(
            "unexpected startup-mode transform state: "
            f"entry={entry_count} marker={marker_count} "
            f"mode={local_mode_count} reason={local_reason_count} "
            f"exact={exact_local_resources_count}"
        )

    verified = path.read_text(encoding="utf-8")
    if verified.count(ACTIVE_ENTRY) != 0 or verified.count(MARKER) != 1:
        raise RuntimeError("active adaptation-backed startup-mode command remains")
    if verified.count("        r_cmd_htcleo_startupmode,\n") != 1:
        raise RuntimeError("local startup-mode command membership is not singular")
    if verified.count("        r_cmd_htcleo_startupreason,\n") != 1:
        raise RuntimeError("local startup-reason command membership is not singular")
    if verified.count(
        "RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupmode"
    ) != 1:
        raise RuntimeError("local startup-mode resource is not singular")
    if verified.count(
        "RESOURCE SSM_SET_PUBLISH_AND_SUBSCRIBE r_cmd_htcleo_startupreason"
    ) != 1:
        raise RuntimeError("local startup-reason resource is not singular")
    if verified.count(LOCAL_RESOURCES) != 1:
        raise RuntimeError("local startup metadata values, priority or severity drifted")
    if original_definition_count != 1 or verified.count(
        "RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_startupmode"
    ) != 1:
        raise RuntimeError("original startup-mode resource definition changed")

    print(f"HTCLEO_LOCAL_NORMAL_STARTUP_MODE={state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
