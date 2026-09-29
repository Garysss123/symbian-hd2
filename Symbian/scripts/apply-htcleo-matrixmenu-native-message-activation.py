#!/usr/bin/env python3
"""Activate Matrix through its existing APA message path and owned WG handle."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MATRIXMENU_NATIVE_MESSAGE_ACTIVATION_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Matrix native activation anchor mismatch: {old[:90]!r}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if MARKER in text:
        return text
    start = text.index("void CMmAppUi::ProcessMessageL( TUid /*aUid*/, const TDesC8& aParams )")
    end = text.index("MCoeMessageObserver::TMessageResponse CMmAppUi::HandleMessageL(", start)
    section = text[start:end]
    section = once(section, "    MMPERF((\"APA Message Recieved\"));", '''    MMPERF(("APA Message Recieved"));
    // HTCLEO_MATRIXMENU_NATIVE_MESSAGE_ACTIVATION_V1
    HtcleoMenuLog(0x4D4D1450u, KErrNone, (TUint32)aParams.Length());''')
    section = once(section, "            CleanupForExitL( EExitKeyApplication );", '''            HtcleoMenuLog(0x4D4D1451u, KErrNone, 0u);
            CleanupForExitL( EExitKeyApplication );
            HtcleoMenuLog(0x4D4D1452u, KErrNone, 0u);''')
    section = once(section, '''            User::LeaveIfError( iCoeEnv->WsSession().SetWindowGroupOrdinalPosition(
            CEikonEnv::Static()->RootWin().Identifier(), 0 ) );''', '''            // Operate on our owned handle, not an arbitrary window-group ID
            // through RWsSession::SetWindowGroupOrdinalPosition/WriteReply.
            HtcleoMenuLog(0x4D4D1453u, KErrNone,
                (TUint32)CEikonEnv::Static()->RootWin().Identifier());
            CEikonEnv::Static()->RootWin().SetOrdinalPosition(0);
            HtcleoMenuLog(0x4D4D1454u, KErrNone, 0u);
            iCoeEnv->WsSession().Flush();
            HtcleoMenuLog(0x4D4D1455u, KErrNone, 0u);''')
    section = once(section, "            iAppkeyHandler->StartL();", '''            iAppkeyHandler->StartL();
            HtcleoMenuLog(0x4D4D1456u, KErrNone, 0u);''')
    section = once(section, '    MMPERF(("APA Message Processed"));', '''    HtcleoMenuLog(0x4D4D145Fu, KErrNone, (TUint32)aParams.Length());
    MMPERF(("APA Message Processed"));''')
    return text[:start] + section + text[end:]


def verify(text: str) -> None:
    start = text.index("void CMmAppUi::ProcessMessageL(")
    end = text.index("MCoeMessageObserver::TMessageResponse CMmAppUi::HandleMessageL(", start)
    section = text[start:end]
    if section.count(MARKER) != 1:
        raise SystemExit("Matrix native activation marker missing")
    for stage in list(range(0x1450, 0x1457)) + [0x145F]:
        if text.count(f"0x4D4D{stage:04X}u") != 1:
            raise SystemExit("Matrix native activation trace boundary missing/duplicated")
    if "WsSession().SetWindowGroupOrdinalPosition(" in section:
        raise SystemExit("synchronous arbitrary-WG activation remains")
    for call in ("CleanupForExitL( EExitKeyApplication );", "RootWin().SetOrdinalPosition(0);",
                 "WsSession().Flush();", "iAppkeyHandler->StartL();", "HandleMessageL( aParams );"):
        if section.count(call) != 1:
            raise SystemExit(f"native activation flow changed: {call}")
    if not (section.index("CleanupForExitL(") < section.index("RootWin().SetOrdinalPosition(0)")
            < section.index("WsSession().Flush()") < section.index("iAppkeyHandler->StartL()")):
        raise SystemExit("stock cleanup/activation/appkey order changed")
    if any(call in section for call in (".Finish()", "User::After", "CreateWindow", "ActivateViewL")):
        raise SystemExit("unexpected wait/view/probe in native activation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    text = patch(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print("HTCLEO_MATRIX_NATIVE_ACTIVATION=stock-apa-empty-message-owned-wg-buffered-ordinal-1450-145f")


if __name__ == "__main__":
    main()
