#!/usr/bin/env python3
"""Keep MatrixMenu GetList on LIW's callback interface for provider sync-pump."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HN_GETLIST_PROVIDER_SYNC_PUMP_MODE_V1"
LEGACY_MARKER = "HTCLEO_HN_GETLIST_SYNCHRONOUS_V1"


OLD = r'''        htcleoQueryMode = EServiceModeSynchronous;'''


NEW = r'''        // HTCLEO_HN_GETLIST_PROVIDER_SYNC_PUMP_MODE_V1
        // MenuContent's LIW interface requires a non-null callback even when
        // its real server IPC is completed synchronously.  Keep the callback
        // contract; mcsservice performs the MatrixMenu-only synchronous pump.
        htcleoQueryMode = EServiceModeAsynchronous;'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if text.count(OLD) != 1:
        raise SystemExit(
            "GetList provider mode: expected one synchronous assignment, "
            f"found {text.count(OLD)}"
        )
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "legacy transform retained": text.count(LEGACY_MARKER) == 1,
        "provider mode marker": text.count(MARKER) == 1,
        "callback mode": (
            text.count("htcleoQueryMode = EServiceModeAsynchronous;") == 1
            and "htcleoQueryMode = EServiceModeSynchronous;" not in text
        ),
        "GetList scope": text.count("KCmdGetList8()) == 0") == 1,
        "same provider": text.count("iSh = CHnServiceHandler::NewL(") == 1,
        "no fake or wait": all(
            token not in text
            for token in ("AppendL( htcleo", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HN GetList provider sync-pump mode verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src/hnqueryresultcollector.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing HN query source: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_HN_GETLIST_EXECUTION="
        "matrixmenu-async-liw-provider-sync-pump-465"
    )


if __name__ == "__main__":
    main()
