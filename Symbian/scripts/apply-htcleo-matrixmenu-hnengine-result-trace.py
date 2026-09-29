#!/usr/bin/env python3
"""Record and re-leave MatrixMenu's CHnEngine constructor result.

Iteration 527 passes the deferred dummy placeholder at 0309/030A but does not
reach 030B after CHnEngine::NewL().  HN is the real menu model/navigation
engine and cannot be bypassed.  Trap only its constructor, record the exact
Leave result and pointer state at 030B, then re-leave failures unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_HNENGINE_RESULT_TRACE_V1"
OLD = """    iHNInterface = CHnEngine::NewL( *this );
    HtcleoMenuLog(0x4D4D030Bu, KErrNone, iHNInterface ? 1u : 0u);
"""
NEW = """    // HTCLEO_MATRIXMENU_HNENGINE_RESULT_TRACE_V1
    TInt htcleoHnEngineResult = KErrNone;
    TRAP(htcleoHnEngineResult, iHNInterface = CHnEngine::NewL( *this ));
    HtcleoMenuLog(0x4D4D030Bu, htcleoHnEngineResult,
        iHNInterface ? 1u : 0u);
    User::LeaveIfError(htcleoHnEngineResult);
"""


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "old untrapped constructor retired": OLD not in source,
        "startup HN constructor retained": source.count(
            "TRAP(htcleoHnEngineResult, iHNInterface = CHnEngine::NewL( *this ));"
        ) == 1,
        "honest result record": source.count(
            "HtcleoMenuLog(0x4D4D030Bu, htcleoHnEngineResult,"
        ) == 1,
        "failure re-left": source.count(
            "User::LeaveIfError(htcleoHnEngineResult);"
        ) == 1,
        "later HN constructor retained": source.count(
            "iHNInterface = CHnEngine::NewL( *this );"
        ) >= 1,
        "next real template retained": source.count(
            "iTemplateLibrary = CMmTemplateLibrary::NewL();"
        ) >= 1,
        "no timer display or normalization": (
            "User::After" not in NEW
            and "HalFunction" not in NEW
            and "htcleoHnEngineResult = KErrNone" not in NEW.split("TRAP", 1)[1]
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu HN-engine trace verification failed: "
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
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                f"MatrixMenu HN-engine anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_HNENGINE_TRACE=installed "
        "stage=030B policy=trap-log-releave"
    )


if __name__ == "__main__":
    main()
