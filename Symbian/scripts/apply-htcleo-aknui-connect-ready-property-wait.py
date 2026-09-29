#!/usr/bin/env python3
"""Replace the broken 500 ms delay with an AknCap-ready P&S wait.

Iteration 498 shows that blocking MatrixMenu gives the rest of the UI stack
scheduling space (green then white), but User::After(500000) never returns on
HTCLEO.  Iteration 499 shows that deleting the wait entirely makes MatrixMenu
retry and exit too early (green only).  The SSM launcher already defines a
persistent ready property and AknCap sets it to one after construction.  For
MatrixMenu reusing that child, subscribe and wait for the actual property
change, then retain the existing bounded connection retry.  No RTimer or
NTimer-backed delay is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_READY_PROPERTY_WAIT_V1"
DISCOVERY_MARKER = "HTCLEO_AKNUI_CONNECT_DISCOVER_REGISTERED_SERVER_V1"

OLD = r'''            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2
            // Iteration 498 proves this pure-RnD timer never returns on
            // HTCLEO.  Preserve the stock delay for every other SID and run
            // the existing bounded retry directly for MatrixMenu.
            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone,
                0x4E4F544Du); // "NOTM"
            if (htcleoAknUiCallerSid != 0x101f4cd2u)
                {
                User::After(500000);
                }
            HtcleoAknUiConnectMenuLog(0x4D4DA219u, KErrNone, 0u);
'''

NEW = r'''            // HTCLEO_AKNUI_CONNECT_MATRIXMENU_NO_TIMER_RETRY_V2
            // HTCLEO_AKNUI_CONNECT_READY_PROPERTY_WAIT_V1
            // Preserve 498's scheduling wait, but wake on the real AknCap
            // readiness event instead of the non-ticking 500 ms NTimer.
            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone,
                0x50535754u); // "PSWT"
            if (htcleoAknUiCallerSid == 0x101f4cd2u &&
                htcleoReuseInflightChild)
                {
                RProperty htcleoMatrixReadyProperty;
                TInt htcleoMatrixReadyResult =
                    htcleoMatrixReadyProperty.Attach(
                        KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
                HtcleoAknUiConnectMenuLog(0x4D4DA222u,
                    htcleoMatrixReadyResult, 0u);
                if (htcleoMatrixReadyResult == KErrNone)
                    {
                    TRequestStatus htcleoMatrixReadyStatus;
                    htcleoMatrixReadyProperty.Subscribe(
                        htcleoMatrixReadyStatus);
                    TInt htcleoMatrixReadyValue = 0;
                    htcleoMatrixReadyResult =
                        htcleoMatrixReadyProperty.Get(
                            htcleoMatrixReadyValue);
                    HtcleoAknUiConnectMenuLog(0x4D4DA223u,
                        htcleoMatrixReadyResult,
                        (TUint32)htcleoMatrixReadyValue);
                    if (htcleoMatrixReadyResult == KErrNone &&
                        htcleoMatrixReadyValue != 1)
                        {
                        HtcleoAknUiConnectMenuLog(0x4D4DA224u,
                            htcleoMatrixReadyStatus.Int(),
                            (TUint32)htcleoMatrixReadyValue);
                        User::WaitForRequest(htcleoMatrixReadyStatus);
                        HtcleoAknUiConnectMenuLog(0x4D4DA225u,
                            htcleoMatrixReadyStatus.Int(), 0u);
                        htcleoMatrixReadyResult =
                            htcleoMatrixReadyProperty.Get(
                                htcleoMatrixReadyValue);
                        }
                    else
                        {
                        htcleoMatrixReadyProperty.Cancel();
                        User::WaitForRequest(htcleoMatrixReadyStatus);
                        }
                    HtcleoAknUiConnectMenuLog(0x4D4DA226u,
                        htcleoMatrixReadyResult,
                        (TUint32)htcleoMatrixReadyValue);
                    htcleoMatrixReadyProperty.Close();
                    }
                HtcleoAknUiConnectMenuLog(0x4D4DA227u,
                    htcleoMatrixReadyResult,
                    htcleoMatrixReadyResult == KErrNone ? 1u : 0u);
                }
            else if (htcleoAknUiCallerSid != 0x101f4cd2u)
                {
                User::After(500000);
                }
            HtcleoAknUiConnectMenuLog(0x4D4DA219u, KErrNone, 0u);
'''


def verify(source: str) -> None:
    discovery = DISCOVERY_MARKER in source
    checks = {
        "single marker": source.count(MARKER) == 1,
        "ready property attach": source.count(
            "htcleoMatrixReadyProperty.Attach("
        )
        == 1,
        "subscribe before wait": (
            source.count("htcleoMatrixReadyProperty.Subscribe(") == 1
            and source.count(
                "User::WaitForRequest(htcleoMatrixReadyStatus);"
            )
            == 2
            and source.index("htcleoMatrixReadyProperty.Subscribe(")
            < source.index("User::WaitForRequest(htcleoMatrixReadyStatus);")
        ),
        "lost-wakeup recheck": source.count(
            "htcleoMatrixReadyProperty.Get("
        )
        == 2,
        "MatrixMenu existing child only": source.count(
            "htcleoAknUiCallerSid == 0x101f4cd2u &&"
        ) == (3 if discovery else 2)
        and source.count(
            "if (htcleoAknUiCallerSid == 0x101f4cd2u &&\n"
            "                htcleoReuseInflightChild)"
        )
        == (2 if discovery else 1),
        "stock other-SID delay retained": source.count(
            "User::After(500000);"
        )
        == 1,
        "no new timer": "RTimer" not in NEW,
        "wait stages": all(
            source.count(f"0x{stage:08X}u") == 1
            for stage in range(0x4D4DA222, 0x4D4DA228)
        ),
        "bounded retry retained": (
            source.count("htcleoAknUiRetryLimit") == 3
            and source.count(
                "TRAP(err,ConnectExistingByNameL(serverName));"
            )
            == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknUi ready-property wait verification failed: "
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
                f"ready-property wait anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_READY_WAIT=property-subscribe "
        "matrixmenu=inflight-child timer=none bounded-retry=retained"
    )


if __name__ == "__main__":
    main()
