#!/usr/bin/env python3
"""Defer MatrixMenu's redundant initial usual-status-pane layout switch.

Iteration 523 completed BaseConstructL, FeatureManager initialisation,
transition setup and RefreshUiPanesL, then stopped inside the explicit
SwitchLayoutL(R_AVKON_STATUS_PANE_LAYOUT_USUAL) call before stage 0307.  The
status pane and title/CBA controls are already constructed and refreshed.
Defer only this one startup reset so MatrixMenu can continue constructing its
shell; later runtime status-pane layout operations remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_INITIAL_STATUSLAYOUT_DEFER_V1"
OLD = """    Cba()->MakeVisible( EFalse );
    StatusPane()->SwitchLayoutL( R_AVKON_STATUS_PANE_LAYOUT_USUAL );
    HtcleoMenuLog(0x4D4D0307u, KErrNone, 0u);
"""
NEW = """    Cba()->MakeVisible( EFalse );
    // HTCLEO_MATRIXMENU_INITIAL_STATUSLAYOUT_DEFER_V1
    // BaseConstructL and RefreshUiPanesL already produced a usable status
    // pane.  Defer only this duplicate startup reset; runtime switches stay.
    HtcleoMenuLog(0x4D4D0307u, KErrNotSupported, 0x53504C59u);
"""


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "startup switch retired": OLD not in source,
        # One later runtime call intentionally remains in mmappui.cpp.  Only
        # the ConstructL startup call anchored by OLD is removed.
        "runtime usual-layout calls retained": source.count(
            "StatusPane()->SwitchLayoutL( R_AVKON_STATUS_PANE_LAYOUT_USUAL );"
        ) == 1,
        "honest defer record": source.count(
            "HtcleoMenuLog(0x4D4D0307u, KErrNotSupported, 0x53504C59u);"
        ) == 1,
        "next constructor retained": source.count(
            "iDummyTemplateLib = CMmTemplateLibrary::NewL();"
        ) == 1,
        "no timer display or fake success": (
            "User::After" not in NEW
            and "HalFunction" not in NEW
            and "KErrNone" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu initial status-layout defer verification failed: "
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
                f"MatrixMenu startup layout anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_INITIAL_STATUSLAYOUT=deferred "
        "stage=0307 detail=53504C59 runtime-layout-switches=retained"
    )


if __name__ == "__main__":
    main()
