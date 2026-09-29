#!/usr/bin/env python3
"""Restore real focus handoff and attribute its destination task.

Hardware 660 proved that the startup EEventFocusLost is stale: WServ still
reports MatrixMenu's own root window group as focused. Ignore only that
contradictory event. A real focus change remains on the stock Avkon path and
is attributed by window group, application UID, thread ID and process ID.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1"
PREVIOUS_MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V1"
STATE_ONLY_MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2"
QUARANTINE_MARKER = "HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1"

ANCHOR = r'''        return;
        }

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
'''

REPLACEMENT = r'''        return;
        }

    // HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1
    // 660 showed focus-WG == MatrixMenu root-WG for the startup FocusLost.
    // Preserve only that stale event. A different real focus group retains
    // the stock Avkon transition below after its identity is recorded.
    if ( type == EEventFocusLost && htcleoRuntimeState == 0x0Fu )
        {
        RWsSession& htcleoFocusWs = iCoeEnv->WsSession();
        const TInt htcleoRootWg =
            CEikonEnv::Static()->RootWin().Identifier();
        const TInt htcleoFocusWg =
            htcleoFocusWs.GetFocusWindowGroup();
        HtcleoMenuLog(0x4D4D1206u, htcleoFocusWg,
            (TUint32)htcleoRootWg);

        TUid htcleoFocusUid = KNullUid;
        CApaWindowGroupName* htcleoFocusName = NULL;
        TRAPD(htcleoNameError,
            htcleoFocusName = CApaWindowGroupName::NewL(
                htcleoFocusWs, htcleoFocusWg));
        if (htcleoNameError == KErrNone && htcleoFocusName)
            {
            htcleoFocusUid = htcleoFocusName->AppUid();
            }
        delete htcleoFocusName;
        HtcleoMenuLog(0x4D4D1207u, htcleoNameError,
            (TUint32)htcleoFocusUid.iUid);

        TThreadId htcleoFocusTid;
        const TInt htcleoThreadError =
            htcleoFocusWs.GetWindowGroupClientThreadId(
                htcleoFocusWg, htcleoFocusTid);
        HtcleoMenuLog(0x4D4D1208u, htcleoThreadError,
            htcleoThreadError == KErrNone
                ? (TUint32)htcleoFocusTid.Id() : 0u);

        TInt htcleoProcessError = htcleoThreadError;
        TUint32 htcleoFocusPid = 0u;
        if (htcleoThreadError == KErrNone)
            {
            RThread htcleoFocusThread;
            htcleoProcessError = htcleoFocusThread.Open(htcleoFocusTid);
            if (htcleoProcessError == KErrNone)
                {
                RProcess htcleoFocusProcess;
                htcleoProcessError = htcleoFocusThread.Process(
                    htcleoFocusProcess);
                if (htcleoProcessError == KErrNone)
                    {
                    htcleoFocusPid =
                        (TUint32)htcleoFocusProcess.Id().Id();
                    htcleoFocusProcess.Close();
                    }
                htcleoFocusThread.Close();
                }
            }
        HtcleoMenuLog(0x4D4D1209u, htcleoProcessError,
            htcleoFocusPid);

        if (htcleoFocusWg == htcleoRootWg)
            {
            if (iCurrentContainer)
                {
                iCurrentContainer->MakeVisible(ETrue);
                iCurrentContainer->DrawNow();
                }
            const TInt htcleoFocusFinish = htcleoFocusWs.Finish();
            HtcleoMenuLog(0x4D4D120Au, htcleoFocusFinish,
                (TUint32)htcleoFocusWs.GetFocusWindowGroup());
            const TUint32 htcleoPreservedState =
                ((StatusPane() && StatusPane()->IsVisible()) ? 0x01u : 0u)
                | ((Cba() && Cba()->IsVisible()) ? 0x02u : 0u)
                | ((iCurrentContainer && iCurrentContainer->IsVisible())
                    ? 0x04u : 0u);
            HtcleoMenuLog(0x4D4D120Bu, KErrNone,
                htcleoPreservedState);
            return;
            }
        }

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREVIOUS_MARKER not in text and STATE_ONLY_MARKER not in text:
        raise SystemExit("focus attribution requires the 659 focus-gain path")
    if QUARANTINE_MARKER in text:
        state = (
            "    static TBool htcleoFocusQuarantine = EFalse;\n"
            "    static TUint32 htcleoFocusQuarantineCount = 0u;\n"
        )
        if text.count(state) != 1:
            raise SystemExit("focus attribution: quarantine state mismatch")
        text = text.replace(state, "", 1)
        arm = "        htcleoFocusQuarantine = ETrue;\n"
        if text.count(arm) != 1:
            raise SystemExit("focus attribution: quarantine arm mismatch")
        text = text.replace(arm, "", 1)
        block_start = text.find(
            "    // HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1\n"
        )
        block_end = text.find(
            "    if ( ( type == EEventFocusLost || "
            "type == KAknFullOrPartialForegroundLost )\n",
            block_start,
        )
        if block_start < 0 or block_end < 0:
            raise SystemExit("focus attribution: quarantine block mismatch")
        text = text[:block_start] + text[block_end:]
    count = text.count(ANCHOR)
    if count != 1:
        raise SystemExit(
            f"focus attribution: expected one insertion anchor, found {count}"
        )
    return text.replace(ANCHOR, REPLACEMENT, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "strict stale guard": text.count(
            "if (htcleoFocusWg == htcleoRootWg)"
        ) == 1,
        "real uid": text.count("htcleoFocusName->AppUid()") == 1,
        "real tid": text.count("GetWindowGroupClientThreadId(") == 1,
        "real pid": text.count("htcleoFocusProcess.Id().Id()") == 1,
        "stock base retained": text.count(
            "CAknAppUi::HandleWsEventL( aEvent, aDestination );"
        ) == 1,
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in range(0x1206, 0x120C)
        ),
        "no quarantine": "HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1" not in text,
        "no timer or fabrication": all(
            token not in REPLACEMENT
            for token in (
                "User::After", "RTimer", "CPeriodic", "AddEvent",
                "RWindow", "SetPixel", "BringToForeground",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu focus-attribution verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu AppUi source: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION="
        "stale-own-wg-guard-real-wg-uid-tid-pid-stock-handoff-1206-120b"
    )


if __name__ == "__main__":
    main()
