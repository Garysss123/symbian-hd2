#!/usr/bin/env python3
"""Disable the cosmetic startup splash for the HTCLEO product profile.

The reference UI-services command list launches splashscreen.exe before the
real Avkon startup command. That process is cosmetic and depends on the early
Window Server/Icon Server path; on HTCLEO its fire-and-forget StartProcess
request remains pending and blocks the command list. Keep the executable and
resource definition byte-present for ABI/history and remove only active list
membership. The real UI framework remains required and unchanged.
"""

from pathlib import Path
import sys


MARKER = "HTCLEO_NO_STARTUP_SPLASHSCREEN"
ACTIVE_ENTRY = "        r_cmd_splash,\n"
REPLACEMENT = (
    f"        // {MARKER}: cosmetic pre-UI process is not part of the HTCLEO "
    "product profile.\n"
)
RESOURCE_DEFINITION = "RESOURCE SSM_START_PROCESS_INFO r_cmd_splash"
EXECUTABLE = '    name = "Z:\\\\sys\\\\bin\\\\splashscreen.exe";'


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} <full-epoc-root>")

    root = Path(sys.argv[1]).resolve()
    path = root / "sf/incubator/stemkit/startup/stem_uiservicescmdlist.rss"
    text = path.read_text(encoding="utf-8")

    entry_count = text.count(ACTIVE_ENTRY)
    marker_count = text.count(MARKER)
    definition_count = text.count(RESOURCE_DEFINITION)
    executable_count = text.count(EXECUTABLE)

    if (
        entry_count == 1
        and marker_count == 0
        and definition_count == 1
        and executable_count == 1
    ):
        text = text.replace(ACTIVE_ENTRY, REPLACEMENT, 1)
        path.write_text(text, encoding="utf-8")
        state = "applied"
    elif (
        entry_count == 0
        and marker_count == 1
        and definition_count == 1
        and executable_count == 1
    ):
        state = "installed"
    else:
        raise RuntimeError(
            "unexpected splashscreen transform state: "
            f"entry={entry_count} marker={marker_count} "
            f"definition={definition_count} executable={executable_count}"
        )

    verified = path.read_text(encoding="utf-8")
    if verified.count(ACTIVE_ENTRY) != 0 or verified.count(MARKER) != 1:
        raise RuntimeError("active splashscreen command remains or marker drifted")
    if verified.count(RESOURCE_DEFINITION) != 1:
        raise RuntimeError("splashscreen resource definition changed")
    if verified.count(EXECUTABLE) != 1:
        raise RuntimeError("splashscreen executable definition changed")

    print(f"HTCLEO_STARTUP_SPLASHSCREEN={state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
