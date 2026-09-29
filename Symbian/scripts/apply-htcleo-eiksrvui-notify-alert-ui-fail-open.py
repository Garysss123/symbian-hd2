#!/usr/bin/env python3
"""Suppress the blocking EikSrv notification alert for UI-first bring-up.

Iteration 470 reaches E773 but not E774, which brackets
CEikServNotifyAlert::ConstructL().  The notifier server already treats a NULL
MEikServNotifyAlert as supported and simply makes DisplayNotifier a no-op.
Skip only this optional alert factory while retaining the notifier server,
alarm factory, base InitializeL path, and the iteration-470 C32 policy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


PREVIOUS_MARKER = "HTCLEO_EIKSRVUI_C32_UI_FAIL_OPEN_V1"
MARKER = "HTCLEO_EIKSRVUI_NOTIFY_ALERT_UI_FAIL_OPEN_V1"
DETAIL = "0xA17F0001u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "C32 fail-open retained": source.count(PREVIOUS_MARKER) == 1,
        "notify alert marker": source.count(MARKER) == 1,
        "blocking constructor retired": source.count("alert->ConstructL();") == 0,
        "alert allocation retired": source.count(
            "CEikServNotifyAlert* alert=new(ELeave) CEikServNotifyAlert;"
        )
        == 0,
        "NULL alert factory": source.count(
            "CEikServNotifyAlert* alert = NULL;"
        )
        == 1,
        "skip result": source.count(
            f"HtcleoEikSrvUiLog(0x0000E774u, KErrNotSupported, {DETAIL});"
        )
        == 1,
        "factory retained": source.count("fctry.iAlert = alert;") == 1,
        "alarm factory retained": source.count("fctry.iAlarmAlert = this;") == 1,
        "base InitializeL retained": source.count(
            "CEikServAppUiBase::InitializeL(fctry);"
        )
        == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "eiksrvui notify-alert UI fail-open verification failed: "
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
            """    HtcleoEikSrvUiLog(0x0000E771u, KErrNone, 0u);
    CEikServNotifyAlert* alert=new(ELeave) CEikServNotifyAlert;
    HtcleoEikSrvUiLog(0x0000E772u, KErrNone, alert ? 1u : 0u);
    CleanupStack::PushL(alert);
    HtcleoEikSrvUiLog(0x0000E773u, KErrNone, 0u);
    alert->ConstructL();
    HtcleoEikSrvUiLog(0x0000E774u, KErrNone, 0u);
    TEikServCtrlFactories fctry;
    fctry.iAlert = alert;
    fctry.iAlarmAlert = this;
    CleanupStack::Pop();
""",
            """    HtcleoEikSrvUiLog(0x0000E771u, KErrNone, 0u);
    // HTCLEO_EIKSRVUI_NOTIFY_ALERT_UI_FAIL_OPEN_V1
    // CEikServNotifyServer explicitly supports a NULL alert factory.  Keep
    // the server and alarm factory, but do not synchronously construct the
    // optional sleeping notification dialog on the UI bring-up path.
    CEikServNotifyAlert* alert = NULL;
    HtcleoEikSrvUiLog(0x0000E772u, KErrNotSupported, 0xA17F0001u);
    HtcleoEikSrvUiLog(0x0000E773u, KErrNone, 0u);
    HtcleoEikSrvUiLog(0x0000E774u, KErrNotSupported, 0xA17F0001u);
    TEikServCtrlFactories fctry;
    fctry.iAlert = alert;
    fctry.iAlarmAlert = this;
""",
            "EikSrv notification alert construction",
        )

    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVUI_NOTIFY_ALERT_UI_FAIL_OPEN=installed "
        "stage=E774 raw=KErrNotSupported detail=A17F0001 "
        "policy=null-alert-factory-notifier-server-retained"
    )


if __name__ == "__main__":
    main()
