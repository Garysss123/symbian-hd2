#!/usr/bin/env python3
"""Bind MatrixMenu's owning window group to the resolved Home task."""
from __future__ import annotations

import argparse
from pathlib import Path


PREDECESSOR = "HTCLEO_MATRIXMENU_HOME_OWNING_WINDOW_SWITCH_V2"
MARKER = "HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3"

OLD = '''        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
        // HTCLEO_MATRIXMENU_HOME_OWNING_WINDOW_SWITCH_V2
        // WServ defines this value specifically as: bring forward the window
        // that would own focus if this group died. The Home task was resolved
        // above; use Matrix's real root group and a buffered command so the
        // background-priority caller never waits for a synchronous reply.
        iCoeEnv->RootWin().SetOrdinalPosition(
            KOrdinalPositionSwitchToOwningWindow);
        iCoeEnv->WsSession().Flush();
        HtcleoMenuLog(0x4D4D1443u, KErrNone,
            (TUint32)task.WgId());'''

NEW = '''        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
        // HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3
        // 757 proved that switch-to-owner is non-blocking but leaves focus on
        // Matrix because this root group had no Home owner relationship. Bind
        // the already-resolved live Home group first. Both public WServ calls
        // are buffered and the single Flush preserves their order.
        HtcleoMenuLog(0x4D4D144Au, KErrNone,
            (TUint32)task.WgId());
        iCoeEnv->RootWin().SetOwningWindowGroup(task.WgId());
        HtcleoMenuLog(0x4D4D144Bu, KErrNone,
            (TUint32)task.WgId());
        iCoeEnv->RootWin().SetOrdinalPosition(
            KOrdinalPositionSwitchToOwningWindow);
        iCoeEnv->WsSession().Flush();
        HtcleoMenuLog(0x4D4D1443u, KErrNone,
            (TUint32)task.WgId());'''


def patch(text: str) -> str:
    if MARKER in text:
        verify(text)
        return text
    if text.count(PREDECESSOR) != 1:
        raise SystemExit("Matrix owning-window predecessor missing")
    if text.count(OLD) != 1:
        raise SystemExit("Matrix owning-window block missing or duplicated")
    text = text.replace(OLD, NEW, 1)
    verify(text)
    return text


def verify(text: str) -> None:
    if text.count(MARKER) != 1 or PREDECESSOR in text:
        raise SystemExit("Matrix Home-owner binding marker mismatch")
    start = text.index("void CMmAppUi::OpenAppL(")
    end = text.index("void CMmAppUi::InitializeL", start)
    body = text[start:end]
    required = (
        "task.Exists()",
        "task.WgId()",
        "0x4D4D1442u",
        "0x4D4D144Au",
        "iCoeEnv->RootWin().SetOwningWindowGroup(task.WgId());",
        "0x4D4D144Bu",
        "KOrdinalPositionSwitchToOwningWindow",
        "iCoeEnv->RootWin().SetOrdinalPosition(",
        "iCoeEnv->WsSession().Flush();",
        "0x4D4D1443u",
        "lsSession.StartApp( *cmdLine )",
    )
    if any(token not in body for token in required):
        raise SystemExit("Matrix Home-owner binding lost required behavior")
    ordered = (
        "0x4D4D1442u",
        "0x4D4D144Au",
        "SetOwningWindowGroup(task.WgId())",
        "0x4D4D144Bu",
        "KOrdinalPositionSwitchToOwningWindow",
        "WsSession().Flush();",
        "0x4D4D1443u",
    )
    positions = [body.index(token) for token in ordered]
    if positions != sorted(positions):
        raise SystemExit("Matrix Home-owner command order changed")
    for forbidden in (
        "SetWindowGroupOrdinalPosition(task.WgId(), 0)",
        "CAknSgcClient::MoveApp( task.WgId()",
        "ComputeMode(RWsSession::EPriorityControlDisabled)",
        "User::LeaveIfError(htcleoHomeOrdinal)",
        "Finish()",
        "User::After",
        "RTimer",
        "WaitForRequest",
        "SendMessageToWindowGroup",
        "RThread",
        "RProcess::Create",
    ):
        if forbidden in body:
            raise SystemExit("Matrix Home-owner handoff added a blocking/fabricated path")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    text = patch(path.read_text(encoding="latin-1"))
    if patch(text) != text:
        raise SystemExit("Matrix Home-owner binding is not idempotent")
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIX_HOME_HANDOFF="
        "bind-real-home-owner-buffered-switch-root-flush-144a-144b-1443"
    )


if __name__ == "__main__":
    main()
