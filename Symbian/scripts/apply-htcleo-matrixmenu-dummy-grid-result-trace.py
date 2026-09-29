#!/usr/bin/env python3
"""Record and re-leave MatrixMenu's dummy-grid construction result.

Iteration 524 reached 0308 after creating the dummy template library but did
not reach 0309 after CMmWidgetContainer::NewGridContainerL().  The dummy grid
is dereferenced throughout MatrixMenu, so a null bypass is not safe.  Trap only
this constructor, record its exact Leave code in the existing 0309 stage, then
re-leave unchanged on failure.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_DUMMY_GRID_RESULT_TRACE_V1"
DOWNSTREAM_MARKER = "HTCLEO_MATRIXMENU_DUMMY_CONTAINER_UI_FIRST_BYPASS_V1"
OLD = """    iDummyContainer = CMmWidgetContainer::NewGridContainerL( ClientRect(),
            this, iDummyTemplateLib );
    HtcleoMenuLog(0x4D4D0309u, KErrNone, iDummyContainer ? 1u : 0u);
"""
NEW = """    // HTCLEO_MATRIXMENU_DUMMY_GRID_RESULT_TRACE_V1
    TInt htcleoDummyGridResult = KErrNone;
    TRAP(htcleoDummyGridResult,
        iDummyContainer = CMmWidgetContainer::NewGridContainerL(
            ClientRect(), this, iDummyTemplateLib ));
    HtcleoMenuLog(0x4D4D0309u, htcleoDummyGridResult,
        iDummyContainer ? 1u : 0u);
    User::LeaveIfError(htcleoDummyGridResult);
"""


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "old untrapped call retired": OLD not in source,
        "single constructor call": source.count(
            "iDummyContainer = CMmWidgetContainer::NewGridContainerL("
        ) == 1,
        "single trap result": source.count(
            "TRAP(htcleoDummyGridResult,"
        ) == 1,
        "honest result record": source.count(
            "HtcleoMenuLog(0x4D4D0309u, htcleoDummyGridResult,"
        ) == 1,
        "failure re-left": source.count(
            "User::LeaveIfError(htcleoDummyGridResult);"
        ) == 1,
        "following setup retained": source.count(
            "iDummyContainer->SetEmptyTextL( KNullDesC );"
        ) == 1,
        "no timer display or normalization": (
            "User::After" not in NEW
            and "HalFunction" not in NEW
            and "htcleoDummyGridResult = KErrNone" not in NEW.split("TRAP", 1)[1]
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu dummy-grid trace verification failed: "
            + ", ".join(failed)
        )


def verify_downstream(source: str) -> None:
    checks = {
        "single downstream marker": source.count(DOWNSTREAM_MARKER) == 1,
        "trace retired": MARKER not in source and "htcleoDummyGridResult" not in source,
        "old call retired": OLD not in source,
        "honest downstream record": source.count(
            "HtcleoMenuLog(0x4D4D0309u, KErrNotSupported, 0x44554D59u);"
        ) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu downstream dummy-grid verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing MatrixMenu app-ui input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if DOWNSTREAM_MARKER in source:
        verify_downstream(source)
        print(
            "HTCLEO_MATRIXMENU_DUMMY_GRID_TRACE=retired "
            "downstream=dummy-container-ui-first-bypass"
        )
        return
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                f"MatrixMenu dummy-grid anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_DUMMY_GRID_TRACE=installed "
        "stage=0309 policy=trap-log-releave"
    )


if __name__ == "__main__":
    main()
