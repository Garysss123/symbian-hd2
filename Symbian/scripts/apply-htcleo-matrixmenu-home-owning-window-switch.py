#!/usr/bin/env python3
"""Use WServ's buffered owning-window switch for Matrix-to-Home handoff."""
from __future__ import annotations

import argparse
from pathlib import Path


PREDECESSOR = "HTCLEO_MATRIXMENU_HOME_PRIORITY_SAFE_ORDINAL_V1"
MARKER = "HTCLEO_MATRIXMENU_HOME_OWNING_WINDOW_SWITCH_V2"
NEXT_MARKER = "HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3"

OLD = '''        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
        // HTCLEO_MATRIXMENU_HOME_PRIORITY_SAFE_ORDINAL_V1
        // 736 proves MoveApp changes WServ focus to the real Home group9 but
        // never returns after Matrix loses foreground process priority. Use
        // the same priority-safe real ordinal contract that 735 proved in the
        // opposite direction. Restore default priority control before logging.
        RWsSession& htcleoHomeWs = iCoeEnv->WsSession();
        htcleoHomeWs.ComputeMode(RWsSession::EPriorityControlDisabled);
        const TInt htcleoHomeOrdinal =
            htcleoHomeWs.SetWindowGroupOrdinalPosition(task.WgId(), 0);
        htcleoHomeWs.ComputeMode(RWsSession::EPriorityControlComputeOff);
        HtcleoMenuLog(0x4D4D1443u, htcleoHomeOrdinal,
            (TUint32)task.WgId());
        User::LeaveIfError(htcleoHomeOrdinal);'''

NEW = '''        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
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


def patch(text: str) -> str:
    if NEXT_MARKER in text:
        if text.count(NEXT_MARKER) != 1 or MARKER in text or PREDECESSOR in text:
            raise SystemExit("Matrix Home-owner successor marker mismatch")
        return text
    if MARKER in text:
        verify(text)
        return text
    if text.count(PREDECESSOR) != 1:
        raise SystemExit("Matrix synchronous ordinal predecessor missing")
    if text.count(OLD) != 1:
        raise SystemExit("Matrix synchronous ordinal block missing or duplicated")
    text = text.replace(OLD, NEW, 1)
    verify(text)
    return text


def verify(text: str) -> None:
    if text.count(MARKER) != 1 or PREDECESSOR in text:
        raise SystemExit("Matrix owning-window switch marker mismatch")
    start = text.index("void CMmAppUi::OpenAppL(")
    end = text.index("void CMmAppUi::InitializeL", start)
    body = text[start:end]
    for token in (
        "task.Exists()", "task.WgId()", "0x4D4D1442u",
        "KOrdinalPositionSwitchToOwningWindow",
        "iCoeEnv->RootWin().SetOrdinalPosition(",
        "iCoeEnv->WsSession().Flush();", "0x4D4D1443u",
        "lsSession.StartApp( *cmdLine )",
    ):
        if token not in body:
            raise SystemExit("Matrix owning-window handoff lost required behavior")
    if not (
        body.index("0x4D4D1442u")
        < body.index("KOrdinalPositionSwitchToOwningWindow")
        < body.index("WsSession().Flush();")
        < body.index("0x4D4D1443u")
    ):
        raise SystemExit("Matrix owning-window switch order changed")
    for forbidden in (
        "SetWindowGroupOrdinalPosition(task.WgId(), 0)",
        "CAknSgcClient::MoveApp( task.WgId()",
        "ComputeMode(RWsSession::EPriorityControlDisabled)",
        "User::LeaveIfError(htcleoHomeOrdinal)",
        "Finish()", "User::After", "RTimer", "WaitForRequest",
        "SendMessageToWindowGroup", "RThread", "RProcess::Create",
    ):
        if forbidden in body:
            raise SystemExit("Matrix owning-window handoff remains synchronous or fabricated")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    text = patch(path.read_text(encoding="latin-1"))
    if patch(text) != text:
        raise SystemExit("Matrix owning-window handoff is not idempotent")
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIX_HOME_HANDOFF="
        "buffered-owning-window-switch-root-flush-1442-1443"
    )


if __name__ == "__main__":
    main()
