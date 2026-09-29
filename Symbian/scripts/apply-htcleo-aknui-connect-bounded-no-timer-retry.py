#!/usr/bin/env python3
"""Add a bounded, cooperative, timer-free AknUi connection retry.

Iteration 499 proves that removing the broken 500 ms timer is necessary, but
its single immediate retry runs before AknCap finishes registration.  For the
exact MatrixMenu SID, retry the existing ConnectExistingByNameL call at most
64 times.  One durable MENULOG record after each retryable failure supplies
file-server IPC as a cooperative scheduling point, matching the hardware-used
EikSrv single-child retry pattern.  Other SIDs keep one stock retry.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_MATRIXMENU_BOUNDED_RETRY_V3"

OLD = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA21Au, KErrNone, 0u);
            TRAP(err,ConnectExistingByNameL(serverName));
            HtcleoAknUiConnectMenuLog(0x4D4DA21Bu, err,
                (TUint32)Handle());
'''

NEW = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA21Au, KErrNone, 0u);
            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_BOUNDED_RETRY_V3
            // Iteration 499 proves one immediate retry is earlier than AknCap
            // registration.  Reuse the existing session lookup with a hard
            // bound; each failed-attempt record performs file-server IPC and
            // gives the child a cooperative scheduling opportunity.
            const TInt htcleoAknUiRetryLimit =
                (htcleoAknUiCallerSid == 0x101f4cd2u) ? 64 : 1;
            TInt htcleoAknUiRetryAttempt = 0;
            do
                {
                TRAP(err,ConnectExistingByNameL(serverName));
                ++htcleoAknUiRetryAttempt;
                if (htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit &&
                    (err == KErrNotFound || err == KErrServerTerminated))
                    {
                    HtcleoAknUiConnectMenuLog(0x4D4DA21Du, err,
                        (TUint32)htcleoAknUiRetryAttempt);
                    }
                }
            while (htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit &&
                (err == KErrNotFound || err == KErrServerTerminated));
            HtcleoAknUiConnectMenuLog(0x4D4DA21Eu, err,
                (TUint32)htcleoAknUiRetryAttempt);
            HtcleoAknUiConnectMenuLog(0x4D4DA21Bu, err,
                (TUint32)Handle());
'''


def verify(source: str) -> None:
    original_limit = source.count(
        "(htcleoAknUiCallerSid == 0x101f4cd2u) ? 64 : 1"
    ) == 1
    downstream_single_attempt = (
        source.count("HTCLEO_AKNUI_CONNECT_MATRIXMENU_SINGLE_ATTEMPT_V1")
        == 1
        and source.count("const TInt htcleoAknUiRetryLimit = 1;") == 1
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        # Iteration 523 intentionally overrides the old 64-attempt value after
        # all legacy transforms have run.  Accept that documented downstream
        # marker on later incremental builds while retaining every loop guard.
        "matrixmenu limit": original_limit or downstream_single_attempt,
        "single existing lookup": source.count(
            "TRAP(err,ConnectExistingByNameL(serverName));"
        ) == 1,
        "bounded loop": (
            source.count("htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit")
            == 2
        ),
        "retryable errors": (
            source.count(
                "err == KErrNotFound || err == KErrServerTerminated"
            ) == 2
        ),
        "cooperative failure record": source.count("0x4D4DA21Du") == 1,
        "final attempt record": source.count("0x4D4DA21Eu") == 1,
        "single stock delay": source.count("User::After(500000);") == 1,
        "no new timer or display": (
            "User::After" not in NEW
            and "RTimer" not in NEW
            and "HalFunction" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknUi bounded no-timer retry verification failed: "
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
            raise SystemExit("AknUi direct retry anchor is not unique")
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_MATRIXMENU_BOUNDED_RETRY=installed "
        "attempts=64 cooperative-log=A21D final=A21E timer=none"
    )


if __name__ == "__main__":
    main()
