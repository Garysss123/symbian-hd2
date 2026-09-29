#!/usr/bin/env python3
"""Return MatrixMenu to an existing Home task without losing the sync caller."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MATRIXMENU_HOME_PRIORITY_SAFE_ORDINAL_V1"
NEXT_MARKERS = (
    "HTCLEO_MATRIXMENU_HOME_OWNING_WINDOW_SWITCH_V2",
    "HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3",
)

OLD = '''        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
        CAknSgcClient::MoveApp( task.WgId(), ESgcMoveAppToForeground );
        HtcleoMenuLog(0x4D4D1443u, KErrNone, (TUint32)task.WgId());'''

NEW = '''        HtcleoMenuLog(0x4D4D1442u, KErrNone, (TUint32)task.WgId());
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


def patch(text: str) -> str:
    if MARKER in text or any(marker in text for marker in NEXT_MARKERS):
        return text
    if text.count(OLD) != 1:
        raise SystemExit("Matrix Home ordinal anchor missing or duplicated")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    successors = [marker for marker in NEXT_MARKERS if marker in text]
    if successors:
        if len(successors) != 1 or text.count(successors[0]) != 1 or MARKER in text:
            raise SystemExit("Matrix owning-window successor marker mismatch")
        return
    if text.count(MARKER) != 1:
        raise SystemExit("Matrix Home ordinal marker missing")
    start = text.index("void CMmAppUi::OpenAppL(")
    end = text.index("\n    }\n", start) + len("\n    }\n")
    section = text[start:end]
    if "CAknSgcClient::MoveApp( task.WgId()" in section:
        raise SystemExit("blocking SGC MoveApp remains in existing Home path")
    required = (
        "task.Exists()", "task.WgId()",
        "ComputeMode(RWsSession::EPriorityControlDisabled)",
        "SetWindowGroupOrdinalPosition(task.WgId(), 0)",
        "ComputeMode(RWsSession::EPriorityControlComputeOff)",
        "HtcleoMenuLog(0x4D4D1443u, htcleoHomeOrdinal",
        "User::LeaveIfError(htcleoHomeOrdinal)",
        "lsSession.StartApp( *cmdLine )",
    )
    if any(token not in section for token in required):
        raise SystemExit("real existing/new Home task behavior changed")
    if not (section.index("EPriorityControlDisabled") <
            section.index("SetWindowGroupOrdinalPosition(task.WgId(), 0)") <
            section.index("EPriorityControlComputeOff") <
            section.index("0x4D4D1443u")):
        raise SystemExit("Matrix priority freeze/ordinal/restore/log order changed")
    if any(token in NEW for token in
           ("SendMessageToWindowGroup", "Finish()", "GetFocusWindowGroup",
            "BringToForeground", "User::After", "RTimer", "CreateWindow")):
        raise SystemExit("unexpected wait/message/UI fabrication in Home handoff")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    text = patch(path.read_text(encoding="latin-1"))
    verify(text)
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_MATRIX_HOME_HANDOFF=priority-freeze-real-ordinal-restore-1442-1443")


if __name__ == "__main__":
    main()
