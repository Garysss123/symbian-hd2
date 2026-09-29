#!/usr/bin/env python3
"""Reuse the fixed HTCLEO panel in MatrixMenu's Post-Coe layout pass.

After the C529 SetSgcParams frontier, ApplyLayoutChangeL returns to the
Post-Coe path and otherwise performs another synchronous WServ size query.
The device has one hardware-proven 480x800 panel, so extend the existing
EikSrv fixed-panel branch only to MatrixMenu and retain stock behaviour for
all other processes.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_MATRIXMENU_POSTCOE_FIXED_SCREEN_V1"

OLD = r'''        const TBool htcleoPostCoeFixedScreen =
            RProcess().SecureId().iId == 0x10003A4A;
'''

NEW = r'''        // HTCLEO_AKNAPPUI_MATRIXMENU_POSTCOE_FIXED_SCREEN_V1
        const TUint32 htcleoPostCoeSid = RProcess().SecureId().iId;
        const TBool htcleoPostCoeFixedScreen =
            htcleoPostCoeSid == 0x10003A4Au ||
            htcleoPostCoeSid == 0x101F4CD2u;
'''


def verify(source: str) -> None:
    homescreen_postcoe_trace = (
        "HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE_V1" in source
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        "matrixmenu target": source.count(
            "htcleoPostCoeSid == 0x101F4CD2u;"
        ) == 1,
        "eiksrv target retained": source.count(
            "htcleoPostCoeSid == 0x10003A4Au ||"
        ) == 1,
        "old eiksrv-only decision absent": OLD not in source,
        "single fixed-panel decision": source.count(
            "const TBool htcleoPostCoeFixedScreen ="
        ) == 1,
        "hardware size retained": source.count("TSize(480, 800)") >= 2,
        "stock query retained": source.count(
            "iCoeEnv->ScreenDevice()->SizeInPixels();"
        ) >= 1,
        "postcoe stages retained": all(
            source.count(f"0x0000B5{stage}u")
            == (2 if homescreen_postcoe_trace and stage == "30" else 1)
            for stage in ("30", "31", "32", "33", "34", "35")
        ),
        "no timer display handle or success fabrication": all(
            token not in NEW
            for token in (
                "User::After", "RTimer", "HalFunction", "SetHandle",
                "KErrNone",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu Post-Coe fixed-screen verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root / "sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing Avkon input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu Post-Coe fixed-screen anchor: expected one, "
                f"found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNAPPUI_MATRIXMENU_POSTCOE_SCREEN="
        "fixed-480x800-b533-b534"
    )


if __name__ == "__main__":
    main()
