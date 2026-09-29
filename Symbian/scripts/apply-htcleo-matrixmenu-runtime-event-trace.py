#!/usr/bin/env python3
"""Trace MatrixMenu runtime WS focus/foreground events after first frame."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_RUNTIME_EVENT_TRACE_V1"


OLD = r'''void CMmAppUi::HandleWsEventL( const TWsEvent& aEvent,
                               CCoeControl* aDestination )
    {
    DEBUG(("_Mm_:CMmAppUi::HandleWsEventL %d - IN", aEvent.Type()));

    if ( aEvent.Type() == KAknUidValueEndKeyCloseEvent )
        {
        // return when the red key was pressed
        MMPERF(("End key pressed"));
        DEBUG(("_Mm_:CMmAppUi::HandleWsEventL - End key"));
        ExitMatrix( EExitToIdle );
        return;
        }

    TEventCode type = static_cast< TEventCode >( aEvent.Type() );

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
        && iCurrentContainer )
        {
        iCurrentContainer->CacheWidgetPosition();
        }

    // base's HandleWsEventL needs to be called before foreground handling,
    // otherwise the screen saver will be turned off
    CAknAppUi::HandleWsEventL( aEvent, aDestination );

    // refreshes toolbar when pen down event was invoked
    if ( type == EEventPointer )
        {
        if ( iCurrentSuiteModel )
            {
            RefreshToolbarL();
            }
        }
    else if ( type == EEventFocusGained )
        {
        HandleFocusGainedL();
        }
    else if ( type == EEventFocusLost )
        {
        HandleFocusLostL();
        }
    else if ( type == KAknFullOrPartialForegroundGained )
        {
        HandleFullOrPartialForegroundGainedL();
        }
    else if( type == KAknFullOrPartialForegroundLost )
        {
        HandleFullOrPartialForegroundLostL();
        }
    }'''


NEW = r'''void CMmAppUi::HandleWsEventL( const TWsEvent& aEvent,
                               CCoeControl* aDestination )
    {
    // HTCLEO_MATRIXMENU_RUNTIME_EVENT_TRACE_V1
    const TUint32 htcleoRuntimeState =
        (iCurrentContainer ? 0x01u : 0u)
        | (iCurrentSuiteModel ? 0x02u : 0u)
        | ((iCurrentContainer && iCurrentContainer->IsVisible()) ? 0x04u : 0u)
        | (IsForeground() ? 0x08u : 0u)
        | (isHiddenFromFS ? 0x10u : 0u);
    HtcleoMenuLog(0x4D4D1200u, aEvent.Type(), htcleoRuntimeState);
    DEBUG(("_Mm_:CMmAppUi::HandleWsEventL %d - IN", aEvent.Type()));

    if ( aEvent.Type() == KAknUidValueEndKeyCloseEvent )
        {
        HtcleoMenuLog(0x4D4D1202u, KErrNone, htcleoRuntimeState);
        // return when the red key was pressed
        MMPERF(("End key pressed"));
        DEBUG(("_Mm_:CMmAppUi::HandleWsEventL - End key"));
        ExitMatrix( EExitToIdle );
        return;
        }

    TEventCode type = static_cast< TEventCode >( aEvent.Type() );

    if ( ( type == EEventFocusLost || type == KAknFullOrPartialForegroundLost )
        && iCurrentContainer )
        {
        iCurrentContainer->CacheWidgetPosition();
        }

    // base's HandleWsEventL needs to be called before foreground handling,
    // otherwise the screen saver will be turned off
    CAknAppUi::HandleWsEventL( aEvent, aDestination );
    HtcleoMenuLog(0x4D4D1201u, type, htcleoRuntimeState);

    // refreshes toolbar when pen down event was invoked
    if ( type == EEventPointer )
        {
        if ( iCurrentSuiteModel )
            {
            RefreshToolbarL();
            }
        }
    else if ( type == EEventFocusGained )
        {
        HtcleoMenuLog(0x4D4D1210u, type, htcleoRuntimeState);
        HandleFocusGainedL();
        HtcleoMenuLog(0x4D4D1211u, KErrNone, htcleoRuntimeState);
        }
    else if ( type == EEventFocusLost )
        {
        HtcleoMenuLog(0x4D4D1220u, type, htcleoRuntimeState);
        HandleFocusLostL();
        HtcleoMenuLog(0x4D4D1221u, KErrNone, htcleoRuntimeState);
        }
    else if ( type == KAknFullOrPartialForegroundGained )
        {
        HtcleoMenuLog(0x4D4D1230u, type, htcleoRuntimeState);
        HandleFullOrPartialForegroundGainedL();
        HtcleoMenuLog(0x4D4D1231u, KErrNone, htcleoRuntimeState);
        }
    else if( type == KAknFullOrPartialForegroundLost )
        {
        HtcleoMenuLog(0x4D4D1240u, type, htcleoRuntimeState);
        HandleFullOrPartialForegroundLostL();
        HtcleoMenuLog(0x4D4D1241u, KErrNone, htcleoRuntimeState);
        }
    HtcleoMenuLog(0x4D4D1290u, KErrNone,
        (iCurrentContainer && iCurrentContainer->IsVisible()) ? 1u : 0u);
    }'''


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
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise SystemExit(
                "MatrixMenu runtime events: expected one handler, "
                f"found {text.count(OLD)}"
            )
        text = text.replace(OLD, NEW, 1)
    stages = (
        0x1200, 0x1201, 0x1202, 0x1210, 0x1211,
        0x1220, 0x1221, 0x1230, 0x1231, 0x1240, 0x1241, 0x1290,
    )
    checks = {
        "marker": text.count(MARKER) == 1,
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1 for stage in stages
        ),
        "base retained": text.count(
            "CAknAppUi::HandleWsEventL( aEvent, aDestination );"
        ) == 1,
        "handlers retained": all(
            text.count(f"{name}();") >= 1
            for name in (
                "HandleFocusGainedL",
                "HandleFocusLostL",
                "HandleFullOrPartialForegroundGainedL",
                "HandleFullOrPartialForegroundLostL",
            )
        ),
        "no behavior bypass": all(
            token not in NEW
            for token in ("TRAP_IGNORE", "User::After", "RTimer", "return KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu runtime-event verification failed: " + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_RUNTIME_EVENT_TRACE="
        "ws-1200-1202-focus-1210-1221-foreground-1230-1241-exit-1290"
    )


if __name__ == "__main__":
    main()
