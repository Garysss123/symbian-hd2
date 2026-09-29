#!/usr/bin/env python3
"""Skip AknCap thread system-critical policy for the HTC Leo UI profile.

User::SetCritical(ESystemCritical) changes only kernel failure policy: if the
thread dies, the failure is treated as system-fatal.  It does not provide UI,
touch, FEP, storage or Wi-Fi functionality.  The HTC Leo port keeps failures
observable and recoverable while the UI stack is brought up.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_CRITICALITY_BYPASS_V1"


def install(source: str) -> str:
    old = "    User::SetCritical(User::ESystemCritical);\n"
    new = f"""    // {MARKER}
    // UI-first HTC Leo policy: an AknCap failure must remain observable,
    // not turn the entire bring-up into a system-fatal thread event.
"""
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"AknCap SetCritical anchor: expected one, found {count}"
        )
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "critical call removed": source.count(
            "User::SetCritical(User::ESystemCritical);"
        )
        == 0,
        "E100 retained": source.count(
            "HtcleoAknCapLog(0x0000E100u, KErrNone, 0x4E4F494Fu);"
        )
        == 1,
        "E101 retained": source.count(
            "HtcleoAknCapLog(0x0000E101u, KErrNone, 0u);"
        )
        == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknCap criticality bypass verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src/AknCapServerEntry.cpp"
    )
    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAPSERVER_CRITICALITY=ui-first "
        "thread-system-critical=skipped functionality=unchanged"
    )


if __name__ == "__main__":
    main()
