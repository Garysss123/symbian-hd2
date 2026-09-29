#!/usr/bin/env python3
"""Foreground MatrixMenu without queuing an incompatible Avkon view event.

TApaTask::BringToForeground() both changes the window-group ordinal position
and sends EApaSystemEventBroughtToForeground.  HTCLEO currently presents its
real MatrixMenu container without an Avkon view, so the delayed system event
enters ActivateTopViewL after the UI is live.  Use the same real WServ window
group ordering without generating that redundant view-activation event.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_FOREGROUND_ORDINAL_NO_SYSTEM_EVENT_V1"
STARTUP_MARKER = "HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1"
QUARANTINE_MARKER = "HTCLEO_MATRIXMENU_FOCUS_QUARANTINE_V1"
RESTORE_MARKER = "HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1"
STATE_ONLY_MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    if (STARTUP_MARKER not in text or
            (QUARANTINE_MARKER not in text and STATE_ONLY_MARKER not in text)):
        raise SystemExit("foreground ordinal fix prerequisites are missing")

    if QUARANTINE_MARKER in text:
        text = replace_once(
            text,
        "    // HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1\n",
        "    // HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1\n"
        f"    // {MARKER}\n",
        "foreground marker",
    )
    text = replace_once(
        text,
        """    HideApplicationFromFSW(EFalse);
    isHiddenFromFS = EFalse;
    htcleoTask.BringToForeground();

    StatusPane()->MakeVisible(ETrue);""",
        """    HideApplicationFromFSW(EFalse);
    isHiddenFromFS = EFalse;
    // TApaTask::BringToForeground would also queue EEventUser with
    // EApaSystemEventBroughtToForeground.  This UI-first shell has a real
    // container but no Avkon view to activate, so keep only the real window
    // group ordering operation.
    const TInt htcleoOrdinalResult =
        htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0);
    HtcleoMenuLog(0x4D4D0355u, htcleoOrdinalResult,
        (TUint32)htcleoRootWg);

    StatusPane()->MakeVisible(ETrue);""",
        "startup BringToForeground",
    )
    text = replace_once(
        text,
        """        if (htcleoMenuTaskExists && htcleoFocusBefore != htcleoRootWg)
            {
            htcleoMenuTask.BringToForeground();
            }
""",
        """        if (htcleoMenuTaskExists && htcleoFocusBefore != htcleoRootWg)
            {
            const TInt htcleoFocusOrdinalResult =
                htcleoFocusWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0);
            HtcleoMenuLog(0x4D4D120Au, htcleoFocusOrdinalResult,
                (TUint32)htcleoRootWg);
            }
""",
            "focus-quarantine BringToForeground",
        )
    fast_marker = ("V2" if STATE_ONLY_MARKER in text else "V1")
    text = replace_once(
        text,
        """    TEventCode type = static_cast< TEventCode >( aEvent.Type() );

    // HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_''' + fast_marker + '''""",
        """    TEventCode type = static_cast< TEventCode >( aEvent.Type() );
    if ( type == EEventUser )
        {
        const TInt htcleoSystemEvent =
            *(reinterpret_cast<const TInt*>(aEvent.EventData()));
        HtcleoMenuLog(0x4D4D1291u, htcleoSystemEvent,
            (TUint32)aEvent.Handle());
        }

    // HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_''' + fast_marker + '''""",
        "EEventUser payload trace",
    )
    return text


def verify(text: str) -> None:
    checks = {
        "markers": (
            text.count(MARKER) == 1
            and text.count(STARTUP_MARKER) == 1
            and (
                text.count(QUARANTINE_MARKER) == 1
                or text.count(RESTORE_MARKER) == 1
                or text.count(STATE_ONLY_MARKER) == 1
            )
        ),
        "startup ordinal only": (
            text.count("htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)")
            == 1
            and "htcleoTask.BringToForeground();" not in text
        ),
        "quarantine ordinal only": (
            (
                (
                    text.count(QUARANTINE_MARKER) == 1
                    and text.count(
                        "htcleoFocusWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)"
                    ) == 1
                )
                or (
                    text.count(RESTORE_MARKER) == 1
                    and text.count(
                        "htcleoFocusWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)"
                    ) == 0
                )
                or (
                    text.count(STATE_ONLY_MARKER) == 1
                    and text.count(
                        "htcleoFocusWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)"
                    ) == 0
                )
            )
            and "htcleoMenuTask.BringToForeground();" not in text
        ),
        "stock foreground path retained": text.count("me.BringToForeground();") == 1,
        "diagnostic stages": (
            text.count("0x4D4D0355u") == 1
            and text.count("0x4D4D120Au") ==
                (0 if STATE_ONLY_MARKER in text and RESTORE_MARKER not in text else 1)
            and text.count("0x4D4D1291u") == 1
        ),
        "system-event payload": (
            text.count("type == EEventUser") == 1
            and text.count("aEvent.EventData()") == 1
        ),
        "no delay or fabricated UI": all(
            token not in text[text.index(MARKER) : text.index(MARKER) + 900]
            for token in ("User::After", "RTimer", "CreateWindowL", "SetPixel")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu ordinal-only foreground verification failed: "
            + "; ".join(failed)
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
        "HTCLEO_MATRIXMENU_FOREGROUND_POLICY="
        "real-wg-ordinal-no-brought-to-foreground-system-event-0355-120a-1291"
    )


if __name__ == "__main__":
    main()
