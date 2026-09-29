#!/usr/bin/env python3
"""Split the EikSrvUi ConstructL entry bracket without changing behavior.

Iteration 471 wrote E7A0 but not E7A1 even though iteration 470 had crossed
the same code. Add durable checkpoints after each existing expression in that
narrow bracket so a retry can distinguish a transient boot from a real
RootWin/WsSession/EikonEnv/SetNotifyUser frontier.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PREVIOUS_MARKER = "HTCLEO_EIKSRVUI_NOTIFY_ALERT_UI_FAIL_OPEN_V1"
MARKER = "HTCLEO_EIKSRVUI_CONSTRUCT_ENTRY_SPLIT_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "notify-alert policy retained": source.count(PREVIOUS_MARKER) == 1,
        "entry split marker": source.count(MARKER) == 1,
        "E7A0 entry retained": source.count(
            "HtcleoEikSrvUiLog(0x0000E7A0u, KErrNone, 0u);"
        ) == 1,
        "E7A1 return retained": source.count(
            "HtcleoEikSrvUiLog(0x0000E7A1u, KErrNone, 0u);"
        ) == 1,
        "RootWin return checkpoint": source.count(
            "HtcleoEikSrvUiLog(0x0000E7F0u, KErrNone, 0u);"
        ) == 1,
        "WsSession return checkpoint": source.count(
            "HtcleoEikSrvUiLog(0x0000E7F1u, KErrNone, 0u);"
        ) == 1,
        "SetAutoForwarding return checkpoint": source.count(
            "HtcleoEikSrvUiLog(0x0000E7F2u, KErrNone, 0u);"
        ) == 1,
        "SetSystem boundary checkpoint": (
            source.count(
                "HtcleoEikSrvUiLog(0x0000E7F3u, KErrNone, 0u);"
            )
            + source.count(
                "HtcleoEikSrvUiLog(0x0000E7F3u, KErrNotSupported, "
                "0x53595301u);"
            )
        ) == 1,
        "SetNotifyUser return checkpoint": source.count(
            "HtcleoEikSrvUiLog(0x0000E7F4u, KErrNone, 0u);"
        ) == 1,
        "RootWin call retained": source.count(
            "RWindowGroup& groupWin = iCoeEnv->RootWin();"
        ) >= 1,
        "WsSession call retained": source.count(
            "RWsSession& wsSession = iCoeEnv->WsSession();"
        ) >= 1,
        "SetAutoForwarding retained": source.count(
            "iEikonEnv->SetAutoForwarding(ETrue);"
        ) >= 1,
        "SetSystem boundary retained or explicitly deferred": (
            source.count("iEikonEnv->SetSystem(ETrue);") >= 1
            or source.count(
                "HTCLEO_EIKSRVUI_SYSTEM_ATTRIBUTE_UI_FAIL_OPEN_V1"
            ) == 1
        ),
        "SetNotifyUser retained": source.count(
            "iEikonEnv->FsSession().SetNotifyUser(EFalse);"
        ) >= 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvui ConstructL entry split-log verification failed: "
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
            """    HtcleoEikSrvUiLog(0x0000E7A0u, KErrNone, 0u);
    RWindowGroup& groupWin = iCoeEnv->RootWin();
    RWsSession& wsSession = iCoeEnv->WsSession();
    iEikonEnv->SetAutoForwarding(ETrue);
    iEikonEnv->SetSystem(ETrue);
    iEikonEnv->FsSession().SetNotifyUser(EFalse);
    HtcleoEikSrvUiLog(0x0000E7A1u, KErrNone, 0u);
""",
            """    // HTCLEO_EIKSRVUI_CONSTRUCT_ENTRY_SPLIT_LOG_V1
    HtcleoEikSrvUiLog(0x0000E7A0u, KErrNone, 0u);
    RWindowGroup& groupWin = iCoeEnv->RootWin();
    HtcleoEikSrvUiLog(0x0000E7F0u, KErrNone, 0u);
    RWsSession& wsSession = iCoeEnv->WsSession();
    HtcleoEikSrvUiLog(0x0000E7F1u, KErrNone, 0u);
    iEikonEnv->SetAutoForwarding(ETrue);
    HtcleoEikSrvUiLog(0x0000E7F2u, KErrNone, 0u);
    iEikonEnv->SetSystem(ETrue);
    HtcleoEikSrvUiLog(0x0000E7F3u, KErrNone, 0u);
    iEikonEnv->FsSession().SetNotifyUser(EFalse);
    HtcleoEikSrvUiLog(0x0000E7F4u, KErrNone, 0u);
    HtcleoEikSrvUiLog(0x0000E7A1u, KErrNone, 0u);
""",
            "EikSrvUi ConstructL E7A0-E7A1 entry bracket",
        )

    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVUI_CONSTRUCT_ENTRY_SPLIT_LOG=installed "
        "stages=E7A0,E7F0-E7F4,E7A1 behavior=unchanged"
    )


if __name__ == "__main__":
    main()
