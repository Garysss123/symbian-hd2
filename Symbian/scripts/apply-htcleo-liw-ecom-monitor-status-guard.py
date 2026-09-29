#!/usr/bin/env python3
"""Keep LIW from treating an ECom session failure as a registry change."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_LIW_ECOM_MONITOR_STATUS_GUARD_V1"

OLD = r'''void CLiwEcomMonitor::RunL()
    {
    iSynchronizeCallBack.CallBack();
    StartMonitoring();
    }'''

NEW = r'''void CLiwEcomMonitor::RunL()
    {
    // HTCLEO_LIW_ECOM_MONITOR_STATUS_GUARD_V1
    // A terminated ECom session completes every outstanding notification with
    // KErrServerTerminated.  That is not a registry-change notification.  In
    // particular, running SynchronizeDbL from this error completion can tear
    // down live LIW providers while MatrixMenu is dispatching its first frame.
    // Retire this failed subscription; normal successful notifications retain
    // their stock synchronize-and-rearm behavior.  A later process start opens
    // a fresh monitor, while normal ECom calls keep their existing reconnect
    // policy.
    if (iStatus.Int() != KErrNone)
        {
        return;
        }
    iSynchronizeCallBack.CallBack();
    StartMonitoring();
    }'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"LIW ECom monitor RunL anchor: expected one, found {count}")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "single status guard": text.count("if (iStatus.Int() != KErrNone)") == 1,
        "error completion retires": text.count("return;") >= 1,
        "successful callback retained": text.count(
            "iSynchronizeCallBack.CallBack();"
        ) == 1,
        "successful rearm retained": text.count("StartMonitoring();") == 2,
        "real ECom notify retained": text.count(
            "iEcomSession.NotifyOnChange(iStatus);"
        ) == 1,
        "cancel retained": text.count(
            "iEcomSession.CancelNotifyOnChange(iStatus);"
        ) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("LIW ECom monitor guard failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/serviceapifw/languageinterworkingfw/servicehandler/src/"
        "liwecommonitor.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing LIW ECom monitor source: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_LIW_ECOM_MONITOR_POLICY="
        "negative-notify-retire-success-sync-rearm"
    )


if __name__ == "__main__":
    main()
