#!/usr/bin/env python3
"""Expose the native Type2A diagnostic HAL and trace real grid pointer input.

Iteration 613 restored the existing epointer.dll as an auto-extension while
keeping every 612 executable byte-identical.  Hardware retained UI/CBA but
showed no visible touch response and no MatrixMenu WS-event records.  Query the
read-only touch diagnostic HAL once when the real widget container constructs,
then snapshot it again from the already-existing background draw path and log
every real CMmGrid pointer entry/return.  This fabricates no input, selection,
timer, window or pixel.
"""

from __future__ import annotations

import argparse
from pathlib import Path


CONTAINER_MARKER = "HTCLEO_MMWIDGETS_TYPE2A_DIAGNOSTIC_V1"
GRID_MARKER = "HTCLEO_MMWIDGETS_GRID_POINTER_TRACE_V1"
REDRAW_MARKER = "HTCLEO_MMWIDGETS_TYPE2A_REDRAW_SNAPSHOT_V1"

CONTAINER_OLD = r'''    iLongTapDetector->EnableLongTapAnimation( ETrue );
    HtcleoMmwLog(0x4D570116u, KErrNone, 0u);
    }'''

CONTAINER_NEW = r'''    iLongTapDetector->EnableLongTapAnimation( ETrue );
    HtcleoMmwLog(0x4D570116u, KErrNone, 0u);

    // HTCLEO_MMWIDGETS_TYPE2A_DIAGNOSTIC_V1
    // Read-only snapshot of the native epointer extension after the real
    // file-backed MatrixMenu logger is available.
    HtcleoMmwLog(0x4D570172u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 0, 0, 0), 0u);
    HtcleoMmwLog(0x4D570173u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 1, 0, 0), 0u);
    HtcleoMmwLog(0x4D570174u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 2, 0, 0), 0u);
    HtcleoMmwLog(0x4D570175u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 3, 0, 0), 0u);
    HtcleoMmwLog(0x4D570176u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 4, 0, 0), 0u);
    HtcleoMmwLog(0x4D570177u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 5, 0, 0), 0u);
    }'''

GRID_OLD = r'''void CMmGrid::HandlePointerEventL(const TPointerEvent& aPointerEvent)
    {
//    if ( aPointerEvent.iType == TPointerEvent::EButton1Down &&'''

GRID_NEW = r'''void CMmGrid::HandlePointerEventL(const TPointerEvent& aPointerEvent)
    {
    // HTCLEO_MMWIDGETS_GRID_POINTER_TRACE_V1
    HtcleoMmwLog(0x4D570180u, aPointerEvent.iType,
        (static_cast<TUint32>(aPointerEvent.iPosition.iX & 0xffff) << 16) |
        static_cast<TUint32>(aPointerEvent.iPosition.iY & 0xffff));
//    if ( aPointerEvent.iType == TPointerEvent::EButton1Down &&'''

GRID_TAIL_OLD = r'''    else
        {
        HandlePointerEventInNormalModeL( aPointerEvent );
        }
    }'''

GRID_TAIL_NEW = r'''    else
        {
        HandlePointerEventInNormalModeL( aPointerEvent );
        }
    HtcleoMmwLog(0x4D570181u,
        UserSvr::HalFunction(EHalGroupPlatformSpecific2, 4, 0, 0),
        static_cast<TUint32>(CurrentItemIndex()));
    }'''

REDRAW_OLD = r'''        HtcleoMmwLog(0x4D570171u, htcleoCpuHazeResult, 0x52A2A500u);
#ifdef RD_UI_TRANSITION_EFFECTS_LIST'''

REDRAW_NEW = r'''        HtcleoMmwLog(0x4D570171u, htcleoCpuHazeResult, 0x52A2A500u);

        // HTCLEO_MMWIDGETS_TYPE2A_REDRAW_SNAPSHOT_V1
        // Reuse this real redraw boundary to observe the already-armed native
        // polling timer.  No timer, input event or redraw is introduced here.
        const TInt htcleoTouchStage =
            UserSvr::HalFunction(EHalGroupPlatformSpecific2, 0, 0, 0);
        const TInt htcleoTouchResult =
            UserSvr::HalFunction(EHalGroupPlatformSpecific2, 1, 0, 0);
        const TInt htcleoTouchDetail =
            UserSvr::HalFunction(EHalGroupPlatformSpecific2, 2, 0, 0);
        const TInt htcleoTouchSamples =
            UserSvr::HalFunction(EHalGroupPlatformSpecific2, 3, 0, 0);
        const TInt htcleoTouchEvents =
            UserSvr::HalFunction(EHalGroupPlatformSpecific2, 4, 0, 0);
        const TInt htcleoTouchLastXY =
            UserSvr::HalFunction(EHalGroupPlatformSpecific2, 5, 0, 0);
        HtcleoMmwLog(0x4D570178u, htcleoTouchStage, htcleoTouchResult);
        HtcleoMmwLog(0x4D570179u, htcleoTouchSamples, htcleoTouchEvents);
        HtcleoMmwLog(0x4D57017Au, htcleoTouchDetail, htcleoTouchLastXY);
#ifdef RD_UI_TRANSITION_EFFECTS_LIST'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/app/homescreen/menufw/menufwui/mmwidgets/src"
    container = base / "mmwidgetcontainer.cpp"
    grid = base / "mmgrid.cpp"
    redraw = base / "mmlistboxitemdrawer.cpp"
    if not container.is_file() or not grid.is_file() or not redraw.is_file():
        raise SystemExit("missing MMWidgets touch diagnostic source")

    container_text = container.read_text(encoding="latin-1")
    if "#include <u32hal.h>" not in container_text:
        anchor = "#include <e32math.h>\n"
        if container_text.count(anchor) != 1:
            raise SystemExit("MMWidgets touch diagnostic HAL group include mismatch")
        container_text = container_text.replace(
            anchor, anchor + "#include <u32hal.h>\n", 1
        )
    if "#include <e32svr.h>" not in container_text:
        anchor = "#include <e32math.h>\n"
        if container_text.count(anchor) != 1:
            raise SystemExit("MMWidgets touch diagnostic include anchor mismatch")
        container_text = container_text.replace(
            anchor, anchor + "#include <e32svr.h>\n", 1
        )
    if CONTAINER_MARKER not in container_text:
        if container_text.count(CONTAINER_OLD) != 1:
            raise SystemExit("MMWidgets touch diagnostic construct anchor mismatch")
        container_text = container_text.replace(
            CONTAINER_OLD, CONTAINER_NEW, 1
        )

    grid_text = grid.read_text(encoding="latin-1")
    if "#include <u32hal.h>" not in grid_text:
        anchor = "#include <AknsDrawUtils.h>\n"
        if grid_text.count(anchor) != 1:
            raise SystemExit("MMWidgets pointer trace HAL group include mismatch")
        grid_text = grid_text.replace(
            anchor, anchor + "#include <u32hal.h>\n", 1
        )
    if "#include <e32svr.h>" not in grid_text:
        anchor = "#include <AknsDrawUtils.h>\n"
        if grid_text.count(anchor) != 1:
            raise SystemExit("MMWidgets pointer trace HAL include mismatch")
        grid_text = grid_text.replace(
            anchor, anchor + "#include <e32svr.h>\n", 1
        )
    if '#include "htcleommwlog.h"' not in grid_text:
        anchor = '#include "mmgrid.h"\n'
        if grid_text.count(anchor) != 1:
            raise SystemExit("MMWidgets pointer trace logger include mismatch")
        grid_text = grid_text.replace(
            anchor, anchor + '#include "htcleommwlog.h"\n', 1
        )
    if GRID_MARKER not in grid_text:
        if grid_text.count(GRID_OLD) != 1:
            raise SystemExit("MMWidgets pointer trace entry anchor mismatch")
        if grid_text.count(GRID_TAIL_OLD) != 1:
            raise SystemExit("MMWidgets pointer trace tail anchor mismatch")
        grid_text = grid_text.replace(GRID_OLD, GRID_NEW, 1)
        grid_text = grid_text.replace(GRID_TAIL_OLD, GRID_TAIL_NEW, 1)

    redraw_text = redraw.read_text(encoding="latin-1")
    if "#include <u32hal.h>" not in redraw_text:
        anchor = "#include <e32math.h>\n"
        if redraw_text.count(anchor) != 1:
            raise SystemExit("MMWidgets redraw diagnostic HAL include mismatch")
        redraw_text = redraw_text.replace(
            anchor, anchor + "#include <u32hal.h>\n", 1
        )
    if "#include <e32svr.h>" not in redraw_text:
        anchor = "#include <e32math.h>\n"
        if redraw_text.count(anchor) != 1:
            raise SystemExit("MMWidgets redraw diagnostic include mismatch")
        redraw_text = redraw_text.replace(
            anchor, anchor + "#include <e32svr.h>\n", 1
        )
    if REDRAW_MARKER not in redraw_text:
        if redraw_text.count(REDRAW_OLD) != 1:
            raise SystemExit("MMWidgets redraw diagnostic anchor mismatch")
        redraw_text = redraw_text.replace(REDRAW_OLD, REDRAW_NEW, 1)

    container_checks = {
        "container marker": container_text.count(CONTAINER_MARKER) == 1,
        "container stages": all(
            container_text.count(f"0x4D570{stage:03X}u") == 1
            for stage in range(0x172, 0x178)
        ),
        "six HAL reads": container_text.count(
            "UserSvr::HalFunction(EHalGroupPlatformSpecific2,"
        ) == 6,
    }
    grid_checks = {
        "grid marker": grid_text.count(GRID_MARKER) == 1,
        "grid stages": all(
            grid_text.count(f"0x4D570{stage:03X}u") == 1
            for stage in (0x180, 0x181)
        ),
        "stock paths": (
            grid_text.count("HandlePointerEventInEditModeL( aPointerEvent );")
            >= 1
            and grid_text.count(
                "HandlePointerEventInNormalModeL( aPointerEvent );"
            ) == 1
        ),
        "no fabricated input or timing": all(
            token not in GRID_NEW + GRID_TAIL_NEW
            for token in (
                "Kern::AddEvent", "event.Set", "SetHighlightL", "User::After",
                "RTimer", "CPeriodic", "DrawNow", "MakeVisible",
            )
        ),
    }
    redraw_checks = {
        "redraw marker": redraw_text.count(REDRAW_MARKER) == 1,
        "redraw stages": all(
            redraw_text.count(f"0x4D570{stage:03X}u") == 1
            for stage in (0x178, 0x179, 0x17A)
        ),
        "six redraw HAL reads": redraw_text.count(
            "UserSvr::HalFunction(EHalGroupPlatformSpecific2,"
        ) == 6,
        "no fabricated redraw input or timing": all(
            token not in REDRAW_NEW
            for token in (
                "Kern::AddEvent", "event.Set", "User::After", "RTimer",
                "CPeriodic", "DrawNow", "MakeVisible",
            )
        ),
    }
    failed = [
        name
        for name, ok in {
            **container_checks, **grid_checks, **redraw_checks
        }.items()
        if not ok
    ]
    if failed:
        raise SystemExit(
            "MMWidgets touch diagnostic verification failed: "
            + ", ".join(failed)
        )

    container.write_text(container_text, encoding="latin-1")
    grid.write_text(grid_text, encoding="latin-1")
    redraw.write_text(redraw_text, encoding="latin-1")
    print(
        "HTCLEO_MMWIDGETS_TOUCH_DIAGNOSTIC="
        "hal-172-17a-existing-redraw-snapshots-grid-pointer-180-181-readonly"
    )


if __name__ == "__main__":
    main()
