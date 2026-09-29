#!/usr/bin/env python3
"""Reuse an in-flight AknCap child and expose its eikcore frontier.

Iteration 500 proves one boot launches two AknCap children: the SSM launch and
the later MatrixMenu fallback.  Both stop inside ConstructAppFromCommandLineL
at E208 while all 64 client retries return KErrNotFound.  The first launcher
defines a persistent, boot-local readiness property before resuming its child.
For MatrixMenu only, reuse that proven in-flight launch instead of creating a
second child.  During the existing bounded retries, sample the already-present
eikcore trace property and carry its deepest E3xx/E4xx value in A21D.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_REUSE_INFLIGHT_CHILD_TRACE_V4"
READY_WAIT_MARKER = "HTCLEO_AKNUI_CONNECT_READY_PROPERTY_WAIT_V1"
DISCOVERY_MARKER = "HTCLEO_AKNUI_CONNECT_DISCOVER_REGISTERED_SERVER_V1"

CONSTANT_OLD = r'''const TUint KHtcleoAknReadyKey = 0x7f044302u;
'''

CONSTANT_NEW = r'''const TUint KHtcleoAknReadyKey = 0x7f044302u;
const TUint KHtcleoEikCoreTraceKey = 0x7f044301u;
'''

LAUNCH_OLD = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA216u, err, 0u);
            TRAP_IGNORE(StartAknCapserverL());
            HtcleoAknUiConnectMenuLog(0x4D4DA217u, KErrNone, 0u);
            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2
            // Iteration 498 proves this pure-RnD timer never returns on
            // HTCLEO.  The fallback launcher has already returned; preserve
            // the stock delay for every other SID and run the existing retry
            // directly for MatrixMenu.
            const TUint32 htcleoAknUiCallerSid =
                RProcess().SecureId().iId;
            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone,
                0x4E4F544Du); // "NOTM"
'''

LAUNCH_NEW = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA216u, err, 0u);
            // HTCLEO_AKNUI_CONNECT_REUSE_INFLIGHT_CHILD_TRACE_V4
            // The SSM launcher defines this boot-local property before Resume.
            // If it exists, MatrixMenu must reuse that in-flight child instead
            // of creating the duplicate proven by iteration 500.
            const TUint32 htcleoAknUiCallerSid =
                RProcess().SecureId().iId;
            TInt htcleoAknReadyValue = -1;
            const TInt htcleoAknReadyRead = RProperty::Get(
                KHtcleoAknReadyCategory, KHtcleoAknReadyKey,
                htcleoAknReadyValue);
            const TBool htcleoReuseInflightChild =
                (htcleoAknUiCallerSid == 0x101f4cd2u &&
                htcleoAknReadyRead == KErrNone);
            HtcleoAknUiConnectMenuLog(0x4D4DA21Fu,
                htcleoAknReadyRead, (TUint32)htcleoAknReadyValue);
            HtcleoAknUiConnectMenuLog(0x4D4DA220u, KErrNone,
                htcleoReuseInflightChild ? 1u : 0u);
            if (!htcleoReuseInflightChild)
                {
                TRAP_IGNORE(StartAknCapserverL());
                }
            HtcleoAknUiConnectMenuLog(0x4D4DA217u, KErrNone,
                htcleoReuseInflightChild ? 1u : 0u);
            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2
            // Iteration 498 proves this pure-RnD timer never returns on
            // HTCLEO.  Preserve the stock delay for every other SID and run
            // the existing bounded retry directly for MatrixMenu.
            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone,
                0x4E4F544Du); // "NOTM"
'''

RETRY_LOG_OLD = r'''                    HtcleoAknUiConnectMenuLog(0x4D4DA21Du, err,
                        (TUint32)htcleoAknUiRetryAttempt);
'''

RETRY_LOG_NEW = r'''                    TInt htcleoEikCoreTraceValue = -1;
                    (void)RProperty::Get(
                        KHtcleoAknReadyCategory,
                        KHtcleoEikCoreTraceKey,
                        htcleoEikCoreTraceValue);
                    HtcleoAknUiConnectMenuLog(0x4D4DA21Du, err,
                        (TUint32)htcleoEikCoreTraceValue);
'''

FINAL_OLD = r'''            HtcleoAknUiConnectMenuLog(0x4D4DA21Eu, err,
                (TUint32)htcleoAknUiRetryAttempt);
'''

FINAL_NEW = r'''            TInt htcleoEikCoreFinalTraceValue = -1;
            const TInt htcleoEikCoreFinalTraceRead = RProperty::Get(
                KHtcleoAknReadyCategory,
                KHtcleoEikCoreTraceKey,
                htcleoEikCoreFinalTraceValue);
            HtcleoAknUiConnectMenuLog(0x4D4DA221u,
                htcleoEikCoreFinalTraceRead,
                (TUint32)htcleoEikCoreFinalTraceValue);
            HtcleoAknUiConnectMenuLog(0x4D4DA21Eu, err,
                (TUint32)htcleoAknUiRetryAttempt);
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    ready_wait = READY_WAIT_MARKER in source
    discovery = DISCOVERY_MARKER in source
    checks = {
        "single marker": source.count(MARKER) == 1,
        "trace key": source.count(
            "KHtcleoEikCoreTraceKey = 0x7f044301u"
        ) == 1,
        "ready property read": source.count(
            "const TInt htcleoAknReadyRead = RProperty::Get("
        ) == 1,
        "matrixmenu-only reuse": source.count(
            "htcleoAknUiCallerSid == 0x101f4cd2u &&"
        ) == (3 if discovery else 2 if ready_wait else 1),
        "existing launch retained": source.count(
            "TRAP_IGNORE(StartAknCapserverL());"
        ) == 1,
        "launch guarded": source.count(
            "if (!htcleoReuseInflightChild)"
        ) == 1,
        "decision stages": all(
            source.count(f"0x{stage:08X}u") == 1
            for stage in (0x4D4DA21F, 0x4D4DA220, 0x4D4DA221)
        ),
        "retry samples trace": source.count(
            "HtcleoAknUiConnectMenuLog(0x4D4DA21Du, err,"
        ) == 1 and source.count(
            "(TUint32)htcleoEikCoreTraceValue);"
        ) == 1,
        "final trace sample": source.count(
            "const TInt htcleoEikCoreFinalTraceRead = RProperty::Get("
        ) == 1,
        "bounded retry retained": (
            source.count("htcleoAknUiRetryLimit") == 3
            and source.count(
                "TRAP(err,ConnectExistingByNameL(serverName));"
            ) == 1
        ),
        "stock other-SID delay retained": source.count(
            "User::After(500000);"
        ) == 1,
        "no new wait timer or display": (
            "WaitForRequest" not in LAUNCH_NEW + RETRY_LOG_NEW + FINAL_NEW
            and "RTimer" not in LAUNCH_NEW + RETRY_LOG_NEW + FINAL_NEW
            and "User::After" not in LAUNCH_NEW + RETRY_LOG_NEW + FINAL_NEW
            and "HalFunction" not in LAUNCH_NEW + RETRY_LOG_NEW + FINAL_NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknUi in-flight child reuse verification failed: "
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
        source = replace_once(
            source, CONSTANT_OLD, CONSTANT_NEW, "eikcore trace key"
        )
        source = replace_once(
            source, LAUNCH_OLD, LAUNCH_NEW, "in-flight launch decision"
        )
        source = replace_once(
            source, RETRY_LOG_OLD, RETRY_LOG_NEW, "retry trace sample"
        )
        source = replace_once(
            source, FINAL_OLD, FINAL_NEW, "final trace sample"
        )
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_REUSE_INFLIGHT_CHILD=installed "
        "ready=A21F decision=A220 retry-trace=A21D final-trace=A221"
    )


if __name__ == "__main__":
    main()
