#!/usr/bin/env python3
"""Keep an already-visible MatrixMenu frame across redundant focus gain."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V1"
MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2"
NEXT_MARKER = "HTCLEO_MATRIXMENU_FOCUS_CHROME_ACTIVATION_V3"
REARM_MARKER = "HTCLEO_MATRIXMENU_FOCUS_TOUCH_REARM_V4"

ANCHOR = r'''    TEventCode type = static_cast< TEventCode >( aEvent.Type() );

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
'''

REPLACEMENT = r'''    TEventCode type = static_cast< TEventCode >( aEvent.Type() );

    // HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2
    // The first runtime focus event arrives after this application is already
    // visible and foreground.  Entering the Avkon transition path at that
    // point submits an empty frame before returning to MatrixMenu.  Preserve
    // the live non-transition UI path for this one redundant state only.
    if ( type == EEventFocusGained && htcleoRuntimeState == 0x0Fu )
        {
        // 735 reaches this with model/container/visibility/foreground already
        // set. The full handler then blocks in its redundant DrawNow before
        // touch or the return CBA can dispatch. Its container focus flag is
        // only for marquee animation; the real WServ focus is already ours.
        // Commit the AppUi state with no redraw, pane refresh, animation or
        // file-backed trace in this event-critical path.
        iHasFocus = ETrue;
        return;
        }

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
'''


def install(text: str) -> str:
    if NEXT_MARKER in text or REARM_MARKER in text:
        return text
    if MARKER in text:
        return text
    if OLD_MARKER in text:
        start = text.index("    // " + OLD_MARKER)
        end = text.index("\n\n    if ( ( type == EEventFocusLost", start)
        old = text[start:end]
        new = REPLACEMENT[REPLACEMENT.index("    // " + MARKER):
                          REPLACEMENT.index("\n\n    if ( ( type == EEventFocusLost")]
        return text[:start] + new + text[end:]
    count = text.count(ANCHOR)
    if count != 1:
        raise SystemExit(f"focus fast path: expected one anchor, found {count}")
    return text.replace(ANCHOR, REPLACEMENT, 1)


def verify(text: str) -> None:
    if NEXT_MARKER in text or REARM_MARKER in text:
        successor = NEXT_MARKER if NEXT_MARKER in text else REARM_MARKER
        if text.count(successor) != 1 or MARKER in text or OLD_MARKER in text:
            raise SystemExit("unexpected V3 successor installation")
        return
    checks = {
        "marker": text.count(MARKER) == 1,
        "strict redundant state": (
            text.count("type == EEventFocusGained && htcleoRuntimeState == 0x0Fu")
            == 1
        ),
        "state-only focus commit": text.count("iHasFocus = ETrue;") >= 2,
        "stock base retained": text.count(
            "CAknAppUi::HandleWsEventL( aEvent, aDestination );"
        ) == 1,
        "no blocking or redraw in fast path": all(token not in REPLACEMENT for token in (
            "HtcleoMenuLog(", "HandleFocusGainedL()", "->DrawNow()",
            "WsSession().Finish", "RefreshUiPanesL(", "->SetHasFocusL(",
            "User::After(", "RTimer")),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu redundant-focus verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH="
        "visible-foreground-0f-appui-focus-state-only-no-redraw-no-filelog"
    )


if __name__ == "__main__":
    main()
