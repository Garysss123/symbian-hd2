#!/usr/bin/env python3
"""Connect MatrixMenu to the AknCap AppServer under its registered name.

Iteration 508 proves that AknCap publishes ready=1 and that MatrixMenu wakes,
but all 64 lookups of the hard-coded differentiator/name return KErrNotFound.
The application UID and service UID are stable; only the registered server
differentiator can vary on this port.  After the ready event, enumerate the
single ``*_10207218_AppServer`` namespace and connect using the kernel-returned
name.  The service UID still authenticates that the candidate is AknCap.

This is MatrixMenu-only, timer-free, bounded, and retains the old fixed-name
retry as a fail-closed fallback.  It changes neither server construction nor
the ready handshake.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_DISCOVER_REGISTERED_SERVER_V1"

OLD = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA21Au, KErrNone, 0u);
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
                    TInt htcleoEikCoreTraceValue = -1;
                    (void)RProperty::Get(
                        KHtcleoAknReadyCategory,
                        KHtcleoEikCoreTraceKey,
                        htcleoEikCoreTraceValue);
                    HtcleoAknUiConnectMenuLog(0x4D4DA21Du, err,
                        (TUint32)htcleoEikCoreTraceValue);
                    }
                }
            while (htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit &&
                (err == KErrNotFound || err == KErrServerTerminated));
'''

NEW = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA21Au, KErrNone, 0u);
            // HTCLEO_AKNUI_CONNECT_DISCOVER_REGISTERED_SERVER_V1
            // Iteration 508 proves ready=1 but the reference fixed-name
            // lookup remains KErrNotFound.  The service is live under a
            // different differentiator on this port.  Ask the kernel for the
            // registered name with the immutable AknCap application UID, then
            // let the existing service-UID handshake validate the candidate.
            if (htcleoAknUiCallerSid == 0x101f4cd2u &&
                htcleoReuseInflightChild)
                {
                _LIT(KHtcleoAknCapServerPattern,
                    "*_10207218_AppServer");
                TFindServer htcleoAknCapServerFind(
                    KHtcleoAknCapServerPattern);
                TFullName htcleoAknCapRegisteredName;
                TInt htcleoAknCapFindResult = KErrNone;
                TInt htcleoAknCapCandidateCount = 0;
                TInt htcleoAknCapCandidateConnect = KErrNotFound;
                while (htcleoAknCapCandidateCount < 16 &&
                    (htcleoAknCapFindResult =
                        htcleoAknCapServerFind.Next(
                            htcleoAknCapRegisteredName)) == KErrNone &&
                    (err == KErrNotFound ||
                        err == KErrServerTerminated))
                    {
                    ++htcleoAknCapCandidateCount;
                    HtcleoAknUiConnectMenuLog(0x4D4DA228u,
                        htcleoAknCapFindResult,
                        (TUint32)htcleoAknCapRegisteredName.Length());
                    TRAP(htcleoAknCapCandidateConnect,
                        ConnectExistingByNameL(
                            htcleoAknCapRegisteredName));
                    HtcleoAknUiConnectMenuLog(0x4D4DA229u,
                        htcleoAknCapCandidateConnect,
                        (TUint32)htcleoAknCapCandidateCount);
                    if (htcleoAknCapCandidateConnect == KErrNone)
                        {
                        err = KErrNone;
                        }
                    }
                HtcleoAknUiConnectMenuLog(0x4D4DA22Au, err,
                    ((TUint32)htcleoAknCapCandidateCount << 16) |
                    ((TUint32)htcleoAknCapFindResult & 0x0000ffffu));
                }
            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_BOUNDED_RETRY_V3
            // Iteration 499 proves one immediate retry is earlier than AknCap
            // registration.  Retain the old fixed-name path as a bounded
            // fallback if no registered AknCap candidate connected.
            const TInt htcleoAknUiRetryLimit =
                (htcleoAknUiCallerSid == 0x101f4cd2u) ? 64 : 1;
            TInt htcleoAknUiRetryAttempt = 0;
            if (err != KErrNone)
                {
                do
                    {
                    TRAP(err,ConnectExistingByNameL(serverName));
                    ++htcleoAknUiRetryAttempt;
                    if (htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit &&
                        (err == KErrNotFound || err == KErrServerTerminated))
                        {
                        TInt htcleoEikCoreTraceValue = -1;
                        (void)RProperty::Get(
                            KHtcleoAknReadyCategory,
                            KHtcleoEikCoreTraceKey,
                            htcleoEikCoreTraceValue);
                        HtcleoAknUiConnectMenuLog(0x4D4DA21Du, err,
                            (TUint32)htcleoEikCoreTraceValue);
                        }
                    }
                while (htcleoAknUiRetryAttempt < htcleoAknUiRetryLimit &&
                    (err == KErrNotFound || err == KErrServerTerminated));
                }
'''


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "AknCap UID pattern": source.count(
            '"*_10207218_AppServer"'
        ) == 1,
        "bounded discovery": source.count(
            "htcleoAknCapCandidateCount < 16"
        ) == 1,
        "kernel server enumeration": source.count(
            "htcleoAknCapServerFind.Next("
        ) == 1,
        "candidate service connect": source.count(
            "ConnectExistingByNameL(\n"
            "                            htcleoAknCapRegisteredName)"
        ) == 1,
        "fallback fixed-name connect": source.count(
            "TRAP(err,ConnectExistingByNameL(serverName));"
        ) == 1,
        "fallback only on failure": source.count(
            "if (err != KErrNone)"
        ) == 1,
        "discovery stages": all(
            source.count(f"0x{stage:08X}u") == 1
            for stage in range(0x4D4DA228, 0x4D4DA22B)
        ),
        "ready wait retained": source.count(
            "HTCLEO_AKNUI_CONNECT_READY_PROPERTY_WAIT_V1"
        ) == 1,
        "bounded retry retained": (
            source.count("htcleoAknUiRetryLimit") == 3
            and source.count("0x4D4DA21Du") == 1
            and source.count("0x4D4DA21Eu") == 1
        ),
        "no timer or display": (
            "User::After" not in NEW
            and "RTimer" not in NEW
            and "HalFunction" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknUi registered-server discovery verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/clientsrc/"
          "AknCapServerClient.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                "registered-server discovery anchor: expected one, "
                f"found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_REGISTERED_SERVER="
        "uid-pattern-discovery bounded=16 fallback=fixed-name"
    )


if __name__ == "__main__":
    main()
