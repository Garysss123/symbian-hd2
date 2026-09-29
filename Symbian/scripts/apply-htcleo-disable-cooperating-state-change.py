#!/usr/bin/env python3
"""Remove phone/baseband cooperative state-change commands from STEM lists.

HTCLEO is brought up as a non-telephony handheld.  The reference STEM lists
begin four local startup/shutdown states by waiting for customcmds.dll ordinal
8 to notify a separate cooperating system.  HTCLEO has no supported Symbian
cooperating-system adaptation, so that acknowledgement can remain pending
forever and block otherwise-local startup.  Keep the resource definitions for
ABI/history clarity, but remove their command-list membership.
"""

from pathlib import Path
import sys


MARKER = "HTCLEO_NO_COOPERATING_SYSTEM_STATE_CHANGE"
ENTRY = (
    "        r_cmd_sastate,          // This needs to be the first command "
    "in state, prio 0xFFF2\n"
)
REPLACEMENT = (
    f"        // {MARKER}: no supported phone/baseband cooperating system.\n"
)
FILES = (
    "stem_uiservicescmdlist.rss",
    "stem_criticalappscmdlist.rss",
    "stem_noncriticalcmdlist.rss",
    "stem_shutdowncmdlists.rss",
)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} <full-epoc-root>")

    root = Path(sys.argv[1]).resolve()
    startup = root / "sf/incubator/stemkit/startup"
    states = []
    for name in FILES:
        path = startup / name
        text = path.read_text(encoding="utf-8")
        entry_count = text.count(ENTRY)
        marker_count = text.count(MARKER)
        definition_count = text.count("RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_sastate")

        if entry_count == 1 and marker_count == 0:
            text = text.replace(ENTRY, REPLACEMENT, 1)
            path.write_text(text, encoding="utf-8")
            state = "applied"
        elif entry_count == 0 and marker_count == 1:
            state = "installed"
        else:
            raise RuntimeError(
                f"unexpected {name} state: entry={entry_count} marker={marker_count}"
            )

        verified = path.read_text(encoding="utf-8")
        if verified.count(ENTRY) != 0 or verified.count(MARKER) != 1:
            raise RuntimeError(f"failed to disable cooperative state change in {name}")
        if definition_count != 1 or verified.count(
            "RESOURCE SSM_START_CUSTOM_COMMAND r_cmd_sastate"
        ) != 1:
            raise RuntimeError(f"unexpected r_cmd_sastate definition count in {name}")
        states.append(f"{name}={state}")

    print("HTCLEO_COOPERATING_STATE_CHANGE=" + ",".join(states))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
