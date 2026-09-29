#!/usr/bin/env python3
"""Defer the synchronous EikSrv StartC32 call for UI-first bring-up.

Iteration 469 proves the C32 caller reaches its property wait while the
configurator reaches the post-rendezvous trace boundary.  The two consecutive
post-rendezvous file records also prove the durable trace itself is intrusive
at that boundary, so it is not valid evidence for changing C32 internals.

For HTCLEO UI bring-up, skip only EikSrv's synchronous StartC32 invocation,
record the skip at the existing E7D8 checkpoint, then normalize the local
result so the unchanged PDD/LDD and remaining InitializeL path can continue.
The traced c32root.dll/c32start.exe pair stays in the ROM for later repair.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PREVIOUS_MARKER = "HTCLEO_EIKSRVUI_INITIALIZE_DURABLE_LOG_V1"
MARKER = "HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "initialize trace": source.count(PREVIOUS_MARKER) == 1,
        "fail-open marker": source.count(MARKER) == 1,
        "stock synchronous call retired": source.count("StartC32();") == 0,
        "explicit skip result": source.count(
            "TInt err = KErrNotSupported;"
        ) == 1,
        "skip evidence": source.count(
            "HtcleoEikSrvUiLog(0x0000E7D8u, err, 0xC32F0001u);"
        ) == 1,
        "local result normalization": source.count("err = KErrNone;") == 1,
        "PDD preserved": source.count(
            "User::LoadPhysicalDevice(COMMS_PDD_NAME)"
        ) == 1,
        "LDD preserved": source.count(
            "User::LoadLogicalDevice(COMMS_LDD_NAME)"
        ) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvui C32 UI fail-open verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()
    source_path = (
        args.epocroot
        / "sf/mw/classicui/uifw/EikStd/srvuisrc/EIKSRVUI.CPP"
    )
    source = source_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = replace_once(
            source,
            """    // Start Comms
    HtcleoEikSrvUiLog(0x0000E7D7u, KErrNone, 0u);
    TInt err = StartC32();
    HtcleoEikSrvUiLog(0x0000E7D8u, err, 0u);
    if (err != KErrNone && err != KErrAlreadyExists)
""",
            """    // Start Comms
    // HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN_V1
    // C32 remains present and traced in ROM, but its synchronous bootstrap is
    // deferred so UI/touch bring-up is not held behind the comms stack.
    HtcleoEikSrvUiLog(0x0000E7D7u, KErrNone, 0u);
    TInt err = KErrNotSupported;
    HtcleoEikSrvUiLog(0x0000E7D8u, err, 0xC32F0001u);
    err = KErrNone;
    if (err != KErrNone && err != KErrAlreadyExists)
""",
            "EikSrv StartC32 call",
        )

    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN=installed "
        "stage=E7D8 raw=KErrNotSupported detail=C32F0001 "
        "policy=skip-eiksrvui-startc32-only"
    )


if __name__ == "__main__":
    main()
