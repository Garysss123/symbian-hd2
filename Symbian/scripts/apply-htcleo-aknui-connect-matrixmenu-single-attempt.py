#!/usr/bin/env python3
"""Retire MatrixMenu's proven-unproductive 64-attempt AknSrv retry loop.

Iteration 522 completed the combined-pane visibility block, then entered a
second AknUi connection.  Hardware logs show that the first connection had
already exhausted all 64 fixed-name attempts with KErrNotFound and that the
second call was still writing the same A21D failure after 26 attempts when the
one-minute observation ended.  Keep one real discovery/fixed-name connection
attempt on every Connect() call so a later live server can still be used, but
do not repeat the same failure 64 times in one call.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_MATRIXMENU_SINGLE_ATTEMPT_V1"
OLD = """            const TInt htcleoAknUiRetryLimit =
                (htcleoAknUiCallerSid == 0x101f4cd2u) ? 64 : 1;
"""
NEW = """            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_SINGLE_ATTEMPT_V1
            // Keep one real attempt per Connect() call.  If AknCap becomes
            // available later, a subsequent call can still connect normally.
            const TInt htcleoAknUiRetryLimit = 1;
"""


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "old 64-attempt policy retired": OLD not in source,
        "single-attempt limit": source.count(
            "const TInt htcleoAknUiRetryLimit = 1;"
        ) == 1,
        "real fixed-name attempt retained": source.count(
            "TRAP(err,ConnectExistingByNameL(serverName));"
        ) == 1,
        "bounded loop retained": source.count(
            "htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit"
        ) == 2,
        "retry classification retained": source.count(
            "err == KErrNotFound || err == KErrServerTerminated"
        ) == 2,
        "final result retained": source.count("0x4D4DA21Eu") == 1,
        "no timer or fake success": (
            "User::After" not in NEW
            and "RTimer" not in NEW
            and "err = KErrNone" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu single-attempt verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/clientsrc/"
        "AknCapServerClient.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing AknCap client input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                f"MatrixMenu 64-attempt anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_MATRIXMENU_SINGLE_ATTEMPT=installed "
        "attempts-per-call=1 discovery-and-fixed-name=retained timer=none"
    )


if __name__ == "__main__":
    main()
