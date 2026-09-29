#!/usr/bin/env python3
"""Temporarily pin MatrixMenu focus to validate real touch delivery.

Iteration 659 proved that its focus-gained fast path returns, then the first
EEventFocusLost enters the Avkon base handler, never returns, and commits a
blank frame.  This deliberately temporary Gate-15 diagnostic skips that
FocusLost path and brings the existing real MatrixMenu task back to the
foreground.  It creates no fake window, event, item, pixel, or timer.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1"
PREVIOUS_MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V1"
STATE_ONLY_MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2"
RESTORE_MARKER = "HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1"
ORDINAL_ONLY_MARKER = "HTCLEO_MATRIXMENU_FOREGROUND_ORDINAL_NO_SYSTEM_EVENT_V1"

MARKER_ANCHOR = r'''    // HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V1
'''

ARM_ANCHOR = r'''        HtcleoMenuLog(0x4D4D1205u, KErrNone,
            iCurrentContainer ? 1u : 0u);
        return;
'''

LOST_ANCHOR = r'''        return;
        }

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
'''

LOST_REPLACEMENT = r'''        return;
        }

    // HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1
    // Temporary validation mode requested for Gate 15: keep the existing real
    // MatrixMenu task focused so pointer delivery can be tested independently
    // of the broken startup focus handoff.  Remove in the next iteration after
    // MatrixMenu survival/touch is established.
    if ( type == EEventFocusLost &&
         htcleoFocusQuarantine &&
         htcleoRuntimeState == 0x0Fu )
        {
        RWsSession& htcleoFocusWs = iCoeEnv->WsSession();
        const TInt htcleoRootWg =
            CEikonEnv::Static()->RootWin().Identifier();
        const TInt htcleoFocusBefore =
            htcleoFocusWs.GetFocusWindowGroup();
        HtcleoMenuLog(0x4D4D1206u, htcleoFocusBefore,
            (TUint32)htcleoRootWg);

        TApaTask htcleoMenuTask(htcleoFocusWs);
        htcleoMenuTask.SetWgId(htcleoRootWg);
        const TBool htcleoMenuTaskExists = htcleoMenuTask.Exists();
        HtcleoMenuLog(0x4D4D1207u,
            htcleoMenuTaskExists ? KErrNone : KErrNotFound,
            htcleoFocusQuarantineCount);
        if (htcleoMenuTaskExists && htcleoFocusBefore != htcleoRootWg)
            {
            htcleoMenuTask.BringToForeground();
            }

        if (iCurrentContainer)
            {
            iCurrentContainer->MakeVisible(ETrue);
            iCurrentContainer->DrawNow();
            }
        const TInt htcleoFocusFinish = htcleoFocusWs.Finish();
        ++htcleoFocusQuarantineCount;
        HtcleoMenuLog(0x4D4D1208u, htcleoFocusFinish,
            (TUint32)htcleoFocusWs.GetFocusWindowGroup());
        const TUint32 htcleoPreservedState =
            ((StatusPane() && StatusPane()->IsVisible()) ? 0x01u : 0u)
            | ((Cba() && Cba()->IsVisible()) ? 0x02u : 0u)
            | ((iCurrentContainer && iCurrentContainer->IsVisible())
                ? 0x04u : 0u);
        HtcleoMenuLog(0x4D4D1209u, KErrNone, htcleoPreservedState);
        return;
        }

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    # Once Gate 14-15 has passed, focus restoration is the permanent successor
    # to this diagnostic.  Keep repeated full-ROM builds idempotent and never
    # resurrect the retired quarantine from an already-restored source tree.
    if RESTORE_MARKER in text or STATE_ONLY_MARKER in text:
        return text
    if MARKER in text:
        return text
    if PREVIOUS_MARKER not in text:
        raise SystemExit("focus quarantine requires the 659 focus-gain path")
    text = replace_once(
        text,
        MARKER_ANCHOR,
        MARKER_ANCHOR
        + "    static TBool htcleoFocusQuarantine = EFalse;\n"
        + "    static TUint32 htcleoFocusQuarantineCount = 0u;\n",
        "quarantine state",
    )
    text = replace_once(
        text,
        ARM_ANCHOR,
        ARM_ANCHOR.replace(
            "        return;\n",
            "        htcleoFocusQuarantine = ETrue;\n"
            "        return;\n",
        ),
        "arm after focus gain",
    )
    return replace_once(
        text, LOST_ANCHOR, LOST_REPLACEMENT, "focus-lost insertion"
    )


def verify(text: str) -> None:
    ordinal_only = ORDINAL_ONLY_MARKER in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "quarantine flag": text.count("htcleoFocusQuarantine") == 6,
        "quarantine counter": text.count("htcleoFocusQuarantineCount") == 3,
        "strict event and state": (
            "type == EEventFocusLost &&\n"
            "         htcleoFocusQuarantine &&\n"
            "         htcleoRuntimeState == 0x0Fu" in text
        ),
        "real root task": text.count("htcleoMenuTask.SetWgId(htcleoRootWg)") == 1,
        "real foreground call": (
            (
                not ordinal_only
                and text.count("htcleoMenuTask.BringToForeground()") == 1
            )
            or (
                ordinal_only
                and "htcleoMenuTask.BringToForeground()" not in text
                and text.count(
                    "htcleoFocusWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)"
                ) == 1
            )
        ),
        "stock transition retained": text.count(
            "CAknAppUi::HandleWsEventL( aEvent, aDestination );"
        ) == 1,
        "focus restore retired": RESTORE_MARKER not in text,
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in (0x1206, 0x1207, 0x1208, 0x1209)
        ),
        "no timer or fabrication": all(
            token not in LOST_REPLACEMENT
            for token in (
                "User::After", "RTimer", "CPeriodic", "AddEvent",
                "RWindow", "SetPixel", "fake",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu focus-quarantine verification failed: "
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
    if RESTORE_MARKER in text or STATE_ONLY_MARKER in text:
        if MARKER in text:
            raise SystemExit("focus quarantine coexists with permanent successor")
        print("HTCLEO_MATRIXMENU_FOCUS_QUARANTINE=retired-after-gate15")
        return
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_FOCUS_QUARANTINE="
        "temporary-pin-real-root-task-preserve-ui-finish-1206-1209"
    )


if __name__ == "__main__":
    main()
