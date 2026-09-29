#!/usr/bin/env python3
"""Discard an already-stale Matrix FocusLost without repainting or waiting."""
from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "HTCLEO_MATRIXMENU_STALE_FOCUS_NO_REDRAW_V1"
OLD = '''            if (iCurrentContainer)
                {
                iCurrentContainer->MakeVisible(ETrue);
                iCurrentContainer->DrawNow();
                }
            const TInt htcleoFocusFinish = htcleoFocusWs.Finish();
            HtcleoMenuLog(0x4D4D120Au, htcleoFocusFinish,
                (TUint32)htcleoFocusWs.GetFocusWindowGroup());'''
NEW = '''            // HTCLEO_MATRIXMENU_STALE_FOCUS_NO_REDRAW_V1
            // Current WServ focus already equals this live root. The queued
            // FocusLost is obsolete: preserve the existing state and return.
            // Repainting and waiting for Finish here needlessly couples event
            // dispatch to rendering. 120A now reports SKIP, not a Finish result.
            HtcleoMenuLog(0x4D4D120Au, KErrNotSupported, 0x534B4950u);'''


def stale_branch(text: str) -> str:
    start = text.index("        if (htcleoFocusWg == htcleoRootWg)")
    end = text.index("\n    if ( ( type == EEventFocusLost", start)
    return text[start:end]


def patch(text: str) -> str:
    if MARKER in text:
        verify(text)
        return text
    if text.count(OLD) != 1 or OLD not in stale_branch(text):
        raise SystemExit("stale FocusLost repaint anchor missing or outside guard")
    changed = text.replace(OLD, NEW, 1)
    if changed.replace(NEW, OLD, 1) != text:
        raise SystemExit("unexpected edit outside stale FocusLost branch")
    verify(changed)
    return changed


def restore(text: str) -> str:
    """Undo only the 759 experiment; preserve every other source change."""
    if MARKER not in text:
        if text.count(OLD) != 1 or OLD not in stale_branch(text):
            raise SystemExit("758 stale-focus restoration anchor mismatch")
        return text
    verify(text)
    restored = text.replace(NEW, OLD, 1)
    if MARKER in restored or patch(restored) != text:
        raise SystemExit("759 reversal changed anything outside its exact block")
    return restored


def verify(text: str) -> None:
    branch = stale_branch(text)
    if text.count(MARKER) != 1 or branch.count(NEW) != 1:
        raise SystemExit("stale FocusLost no-redraw marker mismatch")
    if any(token in branch for token in (
        "->DrawNow(", "->MakeVisible(", ".Finish(", ".Flush(",
        "SetOrdinalPosition(", "GetFocusWindowGroup(", "User::After(",
        "HalFunction(", "RequestComplete(", "TRAP_IGNORE",
    )):
        raise SystemExit("stale FocusLost still mutates UI, waits, or re-arms input")
    if "0x4D4D120Bu" not in branch or "return;" not in branch:
        raise SystemExit("stale FocusLost state evidence/return missing")
    for required in (
        "type == EEventFocusLost && htcleoRuntimeState == 0x0Fu",
        "htcleoFocusWs.GetFocusWindowGroup();",
        "CAknAppUi::HandleWsEventL( aEvent, aDestination );",
        "HandleFocusLostL();", "HandleFocusGainedL();",
        "SetOwningWindowGroup(task.WgId());",
    ):
        if required not in text:
            raise SystemExit("genuine focus or existing Home return path changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--restore", action="store_true",
                        help="retire the rejected 759 experiment and restore 758")
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    original = path.read_text(encoding="latin-1")
    transform = restore if args.restore else patch
    changed = transform(original)
    if transform(changed) != changed:
        raise SystemExit("stale FocusLost transform not idempotent")
    if not args.check and changed != original:
        path.write_text(changed, encoding="latin-1")
    if args.restore:
        print("HTCLEO_MATRIX_STALE_FOCUS=759-frozen-758-original-redraw-finish-restored")
    else:
        print("HTCLEO_MATRIX_STALE_FOCUS=own-root-stale-lost-no-redraw-no-finish-120a-skip-120b")


if __name__ == "__main__":
    main()
