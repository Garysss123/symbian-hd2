#!/usr/bin/env python3
"""Extend the proven one-shot ECom reconnect to the HomeScreen process."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_SERVER_RETRY_V1"
PREREQUISITE = "HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY_V1"
FUNCTION_START = "TAny* REComSession::ResolveAndCreateImplL(TInt aServiceId,"
FUNCTION_END = "\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);"


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("HomeScreen ECom retry requires the MatrixMenu retry")
    start = text.find(FUNCTION_START)
    end = text.find(FUNCTION_END, start)
    if start < 0 or end < 0:
        raise SystemExit("HomeScreen ECom retry function boundary missing")
    end += len(FUNCTION_END)
    block = text[start:end]
    anchor = (
        "\tconst TBool htcleoMatrixMenu =\n"
        "\t\t(RProcess().SecureId().iId == 0x101F4CD2u);\n"
    )
    replacement = anchor + (
        "\t// HTCLEO_ECOM_HOMESCREEN_SERVER_RETRY_V1\n"
        "\tconst TBool htcleoHomeScreen =\n"
        "\t\t(RProcess().SecureId().iId == 0x102750F0u);\n"
        "\tconst TBool htcleoUiShell =\n"
        "\t\thtcleoMatrixMenu || htcleoHomeScreen;\n"
    )
    if block.count(anchor) != 1:
        raise SystemExit("HomeScreen ECom retry scope anchor mismatch")
    block = block.replace(anchor, replacement, 1)
    if block.count("if(htcleoMatrixMenu)") != 2:
        raise SystemExit("HomeScreen ECom retry trace guards mismatch")
    block = block.replace("if(htcleoMatrixMenu)", "if(htcleoUiShell)")
    condition = (
        "if(htcleoMatrixMenu && "
        "htcleoSendResult == KErrServerTerminated)"
    )
    if block.count(condition) != 1:
        raise SystemExit("HomeScreen ECom retry failure guard mismatch")
    block = block.replace(
        condition,
        "if(htcleoUiShell && htcleoSendResult == KErrServerTerminated)",
        1,
    )
    return text[:start] + block + text[end:]


def verify(text: str) -> None:
    start = text.find(FUNCTION_START)
    end = text.find(FUNCTION_END, start) + len(FUNCTION_END)
    block = text[start:end]
    checks = {
        "marker": text.count(MARKER) == 1,
        "HomeScreen SID": block.count("0x102750F0u") == 1,
        "combined narrow scope": block.count("htcleoUiShell") == 4,
        "one reconnect": (
            block.count(
                "htcleoUiShell && htcleoSendResult == KErrServerTerminated"
            ) == 1
            and block.count("ReallyClose();") == 1
            and block.count("TRAPD(htcleoReconnectResult, ConstructL())") == 1
            and block.count("htcleoSendResult = SendReceive(aServiceId") == 2
        ),
        "stock failure retained": block.count(
            "User::LeaveIfError(htcleoSendResult)"
        ) == 1,
        "no delay or normalization": (
            "User::After" not in block
            and "htcleoSendResult = KErrNone" not in block
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen ECom retry verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing ECom source: {path}")
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_ECOM_HOMESCREEN_SERVER_RETRY="
        "sid-102750f0-shared-one-reconnect-no-normalization"
    )


if __name__ == "__main__":
    main()
