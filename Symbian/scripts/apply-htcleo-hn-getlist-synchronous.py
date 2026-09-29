#!/usr/bin/env python3
"""Use the existing synchronous LIW mode for MatrixMenu's GetList query."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HN_GETLIST_SYNCHRONOUS_V1"
COMMIT_MARKER = "HTCLEO_MCS_HN_COMMIT_REQUERY_V1"
PROVIDER_PUMP_MARKER = "HTCLEO_HN_GETLIST_PROVIDER_SYNC_PUMP_MODE_V1"


HANDLER = r'''    iSh = CHnServiceHandler::NewL(
            aQuery.GetService().GetServiceName(),
            aQuery.GetService().GetInterfaceName(),
            aQuery.GetService().GetCommand().GetCommandName(),
            aQuery.GetService().GetCommand().GetCommandMode(),
            constructor,
            command );'''


HANDLER_PATCHED = r'''    // HTCLEO_HN_GETLIST_SYNCHRONOUS_V1
    // LIW asynchronous completion callbacks do not dispatch on this port.
    // CHnServiceHandler already provides a stock synchronous ExecuteCmdL
    // branch with the same provider, parameters and output list.  Select it
    // only for MatrixMenu's real GetList query; subscriptions stay async.
    TServiceMode htcleoQueryMode =
        aQuery.GetService().GetCommand().GetCommandMode();
    if (RProcess().SecureId().iId == 0x101F4CD2u
            && aQuery.GetService().GetCommand().GetCommandName().Compare(
                KCmdGetList8()) == 0)
        {
        htcleoQueryMode = EServiceModeSynchronous;
        }
    HtcleoMdQueryLog(0x4D440465u, KErrNone,
        (TUint32)htcleoQueryMode);
    iSh = CHnServiceHandler::NewL(
            aQuery.GetService().GetServiceName(),
            aQuery.GetService().GetInterfaceName(),
            aQuery.GetService().GetCommand().GetCommandName(),
            htcleoQueryMode,
            constructor,
            command );'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(text: str) -> None:
    provider_pump = PROVIDER_PUMP_MARKER in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "commit retry retained": text.count(COMMIT_MARKER) == 2,
        "GetList-only mode": (
            text.count("KCmdGetList8()) == 0") == 1
            and (
                text.count("htcleoQueryMode = EServiceModeSynchronous;") == 1
                or (
                    provider_pump
                    and text.count(
                        "htcleoQueryMode = EServiceModeAsynchronous;"
                    )
                    == 1
                )
            )
            and text.count("aQuery.GetService().GetCommand().GetCommandMode();") == 1
        ),
        "same handler retained": (
            text.count("iSh = CHnServiceHandler::NewL(") == 1
            and text.count("iSh->ExecuteL( *iCurrentQueryResults, iStatus );") == 1
        ),
        "stage": text.count("0x4D440465u") == 1,
        "no timer fake or direct refresh": all(
            token not in text
            for token in ("RTimer", "User::After", "AppendL( htcleo", "HtcleoInitialRefreshL")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HN synchronous GetList verification failed: " + ", ".join(failed))


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
    if MARKER not in text:
        text = replace_once(text, HANDLER, HANDLER_PATCHED, "GetList handler mode")
    verify(text)
    path.write_text(text, encoding="latin-1")
    if PROVIDER_PUMP_MARKER in text:
        print(
            "HTCLEO_HN_GETLIST_EXECUTION="
            "superseded-by-provider-sync-pump-mode"
        )
    else:
        print(
            "HTCLEO_HN_GETLIST_EXECUTION="
            "matrixmenu-only-synchronous-same-provider-465"
        )


if __name__ == "__main__":
    main()
