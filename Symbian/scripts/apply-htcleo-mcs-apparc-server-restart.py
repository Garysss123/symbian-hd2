#!/usr/bin/env python3
"""Restart the real AppArc server when replacement MenuContent finds it gone."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_APPARC_SERVER_RESTART_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER_ANCHOR = r'''#include "mcssathandler.h"

// ================= MEMBER FUNCTIONS ======================='''


HELPER_PATCHED = r'''#include "mcssathandler.h"

// HTCLEO_MCS_APPARC_SERVER_RESTART_V1
// RApaLsSession::Connect() only calls CreateSession and never starts APSEXE.
// Reuse Symbian's stock server-launch rendezvous pattern from RMenu so an
// abruptly lost AppArc process can be recovered without fake application data.
_LIT( KHtcleoApaServerExe, "apsexe.exe" );

LOCAL_C TInt HtcleoStartApaServer()
    {
    RProcess server;
    TInt err = server.Create(KHtcleoApaServerExe, KNullDesC, EOwnerThread);
    HtcleoMcsLog(0x4D430168u, err, 0u);
    if (err == KErrNone)
        {
        TRequestStatus status;
        server.Rendezvous(status);
        HtcleoMcsLog(0x4D430169u, status.Int(), 0u);
        if (status != KRequestPending)
            {
            server.Kill(0);
            }
        else
            {
            server.Resume();
            }
        User::WaitForRequest(status);
        err = (server.ExitType() == EExitPanic)
            ? KErrGeneral : status.Int();
        HtcleoMcsLog(0x4D43016Au, err,
            (TUint32)server.ExitType());
        server.Close();
        }
    return err;
    }

// ================= MEMBER FUNCTIONS ======================='''


RECONNECT = r'''    if (!iApaLsSession.Handle())
        {
        htcleoApaReconnectResult = iApaLsSession.Connect();
        }
    HtcleoMcsLog(0x4D43012Bu, htcleoApaReconnectResult,
        iApaLsSession.Handle() ? 1u : 0u);
    if (htcleoApaReconnectResult != KErrNone
            || !iApaLsSession.Handle())
        {'''


RECONNECT_WITH_RESTART = r'''    if (!iApaLsSession.Handle())
        {
        htcleoApaReconnectResult = iApaLsSession.Connect();
        }
    if (htcleoApaReconnectResult == KErrNotFound
            || htcleoApaReconnectResult == KErrServerTerminated)
        {
        // HTCLEO_MCS_APPARC_SERVER_RESTART_V1
        iApaLsSession.Close();
        const TInt htcleoApaStartResult = HtcleoStartApaServer();
        if (htcleoApaStartResult == KErrNone
                || htcleoApaStartResult == KErrAlreadyExists)
            {
            htcleoApaReconnectResult = iApaLsSession.Connect();
            }
        else
            {
            htcleoApaReconnectResult = htcleoApaStartResult;
            }
        HtcleoMcsLog(0x4D43016Bu, htcleoApaReconnectResult,
            iApaLsSession.Handle() ? 1u : 0u);
        }
    HtcleoMcsLog(0x4D43012Bu, htcleoApaReconnectResult,
        iApaLsSession.Handle() ? 1u : 0u);
    if (htcleoApaReconnectResult != KErrNone
            || !iApaLsSession.Handle())
        {'''


def install(source: str) -> str:
    source = replace_once(source, HELPER_ANCHOR, HELPER_PATCHED, "AppArc launcher")
    source = replace_once(
        source, RECONNECT, RECONNECT_WITH_RESTART, "AppArc reconnect restart"
    )
    return source


def verify(source: str) -> None:
    checks = {
        "markers": source.count(MARKER) == 2,
        "real executable": source.count('_LIT( KHtcleoApaServerExe, "apsexe.exe" )')
        == 1,
        "stock launch pattern": (
            source.count("server.Create(KHtcleoApaServerExe, KNullDesC, EOwnerThread)")
            == 1
            and source.count("server.Rendezvous(status)") == 1
            and source.count("server.Resume()") == 1
            and source.count("User::WaitForRequest(status)") == 1
            and source.count("server.ExitType() == EExitPanic") == 1
        ),
        "narrow restart": (
            source.count("htcleoApaReconnectResult == KErrNotFound") == 1
            and source.count("htcleoApaReconnectResult == KErrServerTerminated") == 1
            and source.count("htcleoApaStartResult == KErrAlreadyExists") == 1
        ),
        "stages": all(
            source.count(f"0x4D430{stage:03X}u") == 1
            for stage in range(0x168, 0x16C)
        ),
        "real enumeration retained": (
            source.count("iApaLsSession.GetAllApps( 0 )") == 1
            and source.count("iApaLsSession.GetNextApp( appInfo )") == 1
            and source.count("return htcleoApaReconnectResult != KErrNone") == 1
        ),
        "no display or fake data": (
            "HalFunction" not in source
            and "AppendL( htcleo" not in source
            and "User::After" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS AppArc server restart verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/menusrvengutils.cpp"
    )
    if not source_path.is_file():
        raise SystemExit("missing MenuContent engine utils source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print("HTCLEO_MCS_APPARC_SERVER_RESTART=168-16B-apsexe-rendezvous")


if __name__ == "__main__":
    main()
