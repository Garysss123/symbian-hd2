#!/usr/bin/env python3
"""Skip the proven-broken AknUi retry timer for MatrixMenu only.

Hardware iteration 498 reaches the fallback launch, returns from
StartAknCapserverL(), and stops at the stock pure-RnD User::After(500000).
Iteration 490 already proved timer-backed User::After does not return on this
port.  Preserve the stock delay for every other SID, but let the exact
MatrixMenu process proceed directly to the existing connection retry.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2"
READY_WAIT_MARKER = "HTCLEO_AKNUI_CONNECT_READY_PROPERTY_WAIT_V1"

OLD = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone, 500000u);
            User::After(500000); // No problem to wait synchronously as pure RnD support.
            HtcleoAknUiConnectMenuLog(0x4D4DA219u, KErrNone, 0u);
'''

NEW = r'''            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2
            // Iteration 498 proves this pure-RnD timer never returns on
            // HTCLEO.  The fallback launcher has already returned; preserve
            // the stock delay for every other SID and run the existing retry
            // directly for MatrixMenu.
            const TUint32 htcleoAknUiCallerSid =
                RProcess().SecureId().iId;
            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone,
                0x4E4F544Du); // "NOTM"
            if (htcleoAknUiCallerSid != 0x101f4cd2u)
                {
                User::After(500000);
                }
            HtcleoAknUiConnectMenuLog(0x4D4DA219u, KErrNone, 0u);
'''


def verify(source: str) -> None:
    ready_wait = READY_WAIT_MARKER in source
    checks = {
        "single marker": source.count(MARKER) == 1,
        "matrixmenu SID": source.count(
            "htcleoAknUiCallerSid != 0x101f4cd2u"
        ) == 1,
        "single stock delay retained": source.count(
            "User::After(500000);"
        ) == 1,
        "no-timer detail": (
            source.count("0x50535754u") == 1
            and source.count("0x4E4F544Du") == 0
            if ready_wait
            else source.count("0x4E4F544Du") == 1
        ),
        "existing fallback launch": source.count(
            "TRAP_IGNORE(StartAknCapserverL());"
        ) == 1,
        "existing retry": source.count(
            "TRAP(err,ConnectExistingByNameL(serverName));"
        ) == 1,
        "boundary stages": (
            source.count("0x4D4DA218u") == 1
            and source.count("0x4D4DA219u") == 1
        ),
        "no loop or display": (
            "for(" not in NEW
            and "while(" not in NEW
            and "HalFunction" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknUi MatrixMenu no-timer retry verification failed: "
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
        if source.count(OLD) != 1:
            raise SystemExit("AknUi retry timer anchor is not unique")
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_MATRIXMENU_RETRY=installed "
        "policy=direct-no-timer other-sids=stock stages=A218-A21C"
    )


if __name__ == "__main__":
    main()
