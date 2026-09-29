#!/usr/bin/env python3
"""Defer the blocking Eikon system-task attribute during UI bring-up.

Iteration 472 proves that RootWin, WsSession and SetAutoForwarding return, then
stops inside CEikonEnv::SetSystem(ETrue). SetSystem only marks the window group
as protected from ordinary Task End and synchronously republishes its name; it
does not construct the UI, touch path or application framework. Keep the later
explicit Eikon server name setup and record a reversible UI-first deferral.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PREVIOUS_MARKER = "HTCLEO_EIKSRVUI_CONSTRUCT_ENTRY_SPLIT_LOG_V1"
MARKER = "HTCLEO_EIKSRVUI_SYSTEM_ATTRIBUTE_UI_FAIL_OPEN_V1"
DETAIL = "0x53595301u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "entry split retained": source.count(PREVIOUS_MARKER) == 1,
        "system attribute marker": source.count(MARKER) == 1,
        "blocking call retired": source.count(
            "iEikonEnv->SetSystem(ETrue);"
        ) == 0,
        "explicit skip record": source.count(
            f"HtcleoEikSrvUiLog(0x0000E7F3u, KErrNotSupported, {DETAIL});"
        ) == 1,
        "SetNotifyUser retained": source.count(
            "iEikonEnv->FsSession().SetNotifyUser(EFalse);"
        ) >= 1,
        "E7F4 retained": source.count(
            "HtcleoEikSrvUiLog(0x0000E7F4u, KErrNone, 0u);"
        ) == 1,
        "later Eikon server name retained": source.count(
            "groupWin.SetName(__EIKON_SERVER_NAME);"
        ) == 1,
        "NULL alert policy retained": source.count(
            "HTCLEO_EIKSRVUI_NOTIFY_ALERT_UI_FAIL_OPEN_V1"
        ) == 1,
        "C32 policy retained": source.count(
            "HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN_V1"
        ) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvui system-attribute UI fail-open verification failed: "
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
            """    iEikonEnv->SetSystem(ETrue);
    HtcleoEikSrvUiLog(0x0000E7F3u, KErrNone, 0u);
""",
            """    // HTCLEO_EIKSRVUI_SYSTEM_ATTRIBUTE_UI_FAIL_OPEN_V1
    // CEikonEnv::SetSystem only protects this server from ordinary Task End
    // and republishes window-group metadata. Defer that synchronous update
    // until the QSD8K UI path is stable; the explicit server name remains.
    HtcleoEikSrvUiLog(0x0000E7F3u, KErrNotSupported, 0x53595301u);
""",
            "EikSrvUi SetSystem call",
        )

    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVUI_SYSTEM_ATTRIBUTE_UI_FAIL_OPEN=installed "
        "stage=E7F3 raw=KErrNotSupported detail=53595301 "
        "policy=defer-task-end-protection-only"
    )


if __name__ == "__main__":
    main()
