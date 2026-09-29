#!/usr/bin/env python3
"""Retire the proven per-pointer FAT trace fan-out, not pointer processing.

745r1 produced six HAB, three HEB and one HCOE record per delivered Home
pointer event, including drags. Keep focus, CBA/edge traces and heartbeats.
Home changes three diagnostic predicates. Matrix throttles its pointer entry
and keeps only grid edges. No event handler, scheduling or window call changes.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

MARKER = "HTCLEO_HOME_POINTER_FILE_TRACE_RETIRED_V1"
AKN_OLD = """    const TBool htcleoHomeFocusTrace =
        (RProcess().SecureId().iId == 0x102750f0u);"""
AKN_NEW = """    // HTCLEO_HOME_POINTER_FILE_TRACE_RETIRED_V1
    // Pointer dispatch still runs below; only its per-event file trace stops.
    // Native focus and real CBA command/edge diagnostics remain available.
    const TBool htcleoHomeFocusTrace =
        (RProcess().SecureId().iId == 0x102750f0u) &&
        aEvent.Type() != EEventPointer;"""
EIK_OLD = """\tconst TBool htcleoHomeWsTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u);"""
EIK_NEW = """\t// HTCLEO_HOME_POINTER_FILE_TRACE_RETIRED_V1
\t// Do not open/write/close HSXML three times for every queued drag.
\tconst TBool htcleoHomeWsTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u) &&
\t\taEvent.Type() != EEventPointer;"""
CONE_OLD = """\t\tif (htcleoConeStage == 0x050Fu || htcleoConeStage == 0x0207u)"""
CONE_NEW = """\t\t// HTCLEO_HOME_POINTER_FILE_TRACE_RETIRED_V1
\t\t// 0207 carries event.Type(), not an error code. Keep other event ends.
\t\tif (htcleoConeStage == 0x050Fu ||
\t\t\t(htcleoConeStage == 0x0207u && aResult != EEventPointer))"""

MATRIX_MARKER = "HTCLEO_MATRIX_POINTER_FILE_TRACE_THROTTLED_V1"
MATRIX_GATE = """    // HTCLEO_MATRIX_POINTER_FILE_TRACE_THROTTLED_V1
    // Keep frame-stage publication ABOVE this gate, even for omitted records.
    // One pointer-entry record per5s is enough to establish app-side input.
    // These stage arguments are event types/counters, not error results.
    if (aStage == 0x4D4D1200u && aResult == EEventPointer)
        {
        static TBool loggedPointer = EFalse;
        static TUint32 lastPointerTick = 0;
        const TUint32 now = User::NTickCount();
        if (loggedPointer && now - lastPointerTick < 5000u)
            return;
        loggedPointer = ETrue;
        lastPointerTick = now;
        }
    if ((aStage == 0x4D4D1201u && aResult == EEventPointer) ||
        (aStage == 0x4D4D1290u && aResult == KErrNone))
        return;
"""
GRID_MARKER = "HTCLEO_MMW_POINTER_FILE_TRACE_EDGES_V1"
GRID_GATE = """    // HTCLEO_MMW_POINTER_FILE_TRACE_EDGES_V1
    // Keep genuine grid down/up coordinates; suppress continuous move/drag
    // and the redundant successful per-packet HAL-counter tail.
    if (aStage == 0x4D570180u &&
        aResult != TPointerEvent::EButton1Down &&
        aResult != TPointerEvent::EButton1Up)
        return;
    if (aStage == 0x4D570181u && aResult >= 0)
        return;
"""


def patch_file_gate(text: str, marker: str, gate: str, frame_state: bool) -> str:
    if marker in text:
        if text.count(gate) != 1 or text.count(marker) != 1:
            raise SystemExit("file-gate installation mismatch")
        return text
    before = text
    include = "#include <f32file.h>"
    if text.count(include) != 1 or "#include <w32std.h>" in text:
        raise SystemExit("unexpected shell logger includes")
    text = text.replace(include, include + "\n#include <w32std.h>", 1)
    if text.count("    RFs fs;") != 1:
        raise SystemExit("ambiguous shell file-writer entry")
    text = text.replace("    RFs fs;", gate + "    RFs fs;", 1)
    if frame_state and not (text.index("RProperty::Set(") < text.index(marker) < text.index("    RFs fs;")):
        raise SystemExit("Matrix display breadcrumb must execute before log throttle")
    restored = text.replace(gate, "", 1).replace("\n#include <w32std.h>", "", 1)
    if restored != before:
        raise SystemExit("unexpected non-logging delta")
    return text


def replace(text: str, old: str, new: str) -> str:
    if MARKER in text:
        if text.count(MARKER) != 1 or text.count(new) != 1:
            raise SystemExit("unexpected installed pointer-log retirement")
        return text
    if text.count(old) != 1:
        raise SystemExit(f"pointer-log predicate anchor missing/duplicated: {old!r}")
    changed = text.replace(old, new, 1)
    if changed.replace(new, old, 1) != text:
        raise SystemExit("non-diagnostic source delta detected")
    return changed


def verify_flag(text: str, flag: str, writer: str) -> None:
    # The guarded booleans MUST NOT control any real UI action/compatibility fix.
    uses = text.count(flag)
    calls = re.findall(r"if \(" + flag + r"\)\s+(\w+)\(", text)
    if len(calls) != uses - 1 or not calls or any(c != writer for c in calls):
        raise SystemExit(f"{flag} is not exclusively a diagnostic-call gate")


def transform(root: Path, write: bool) -> None:
    base = root / "sf/mw/classicui"
    specs = (
        (base / "uifw/AvKon/src/AknAppUi.cpp", AKN_OLD, AKN_NEW),
        (base / "commonuisupport/uikon/coresrc/EIKAPPUI.CPP", EIK_OLD, EIK_NEW),
        (base / "lafagnosticuifoundation/cone/src/COEMAIN.CPP", CONE_OLD, CONE_NEW),
    )
    contents = []
    for path, old, new in specs:
        before = path.read_text(encoding="latin-1")
        after = replace(before, old, new)
        if replace(after, old, new) != after:
            raise SystemExit("pointer-log retirement is not idempotent")
        # Even on an already transformed source, only the reviewed predicate
        # differs from the pre-retirement form; retain all logger call sites.
        if after.replace(new, old, 1).replace(old, new, 1) != after:
            raise SystemExit("predicate roundtrip mismatch")
        contents.append(after)
    verify_flag(contents[0], "htcleoHomeFocusTrace", "HtcleoAknAppUiBaseLog")
    verify_flag(contents[1], "htcleoHomeWsTrace", "HtcleoEikAppUiBaseLog")
    if any("1048576" not in source for source in contents):
        raise SystemExit("preserve existing 1MiB capacities")
    for source, required in zip(contents, (
        ("CAknAppUiBase::HandleWsEventL(aEvent, aDestination);", "UpdateKeyBlockMode();"),
        ("CCoeAppUi::HandleWsEventL(aEvent, aDestination);", "EikBubbleHelp::Cancel();"),
        ("iAppUi->HandleWsEventL(event,window);", "HtcleoHomeConeLog(aStage, aResult, aDetail);"),
    )):
        if any(call not in source for call in required):
            raise SystemExit("real event/focus dispatch or retained logger missing")
    matrix_base = root / "sf/app/homescreen/menufw/menufwui"
    logger_specs = (
        (matrix_base / "matrixmenu/src/htcleomenulog.cpp", MATRIX_MARKER, MATRIX_GATE, True),
        (matrix_base / "mmwidgets/src/htcleommwlog.cpp", GRID_MARKER, GRID_GATE, False),
    )
    logger_contents = []
    for path, marker, gate, frame_state in logger_specs:
        after = patch_file_gate(path.read_text(encoding="latin-1"), marker, gate, frame_state)
        if patch_file_gate(after, marker, gate, frame_state) != after:
            raise SystemExit("file throttle is not idempotent")
        if "16384 * 64" not in after:
            raise SystemExit("preserve1MiB shell log capacity")
        logger_contents.append(after)
    if write:
        for (path, _, _), after in zip(specs, contents):
            path.write_text(after, encoding="latin-1")
        for (path, _, _, _), after in zip(logger_specs, logger_contents):
            path.write_text(after, encoding="latin-1")
    print("HTCLEO_SHELL_POINTER_LOG_POLICY=home-no-per-pointer-files-matrix-5s-entry-grid-edges-heartbeats-commands-focus-retained")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    transform(args.root, not args.check_only)


if __name__ == "__main__":
    main()
