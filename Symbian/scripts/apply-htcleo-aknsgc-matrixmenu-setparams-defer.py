#!/usr/bin/env python3
"""Defer the blocking SetSgcParams IPC only for MatrixMenu on HTCLEO.

Iteration 513 reaches C529 but never C52A inside CAknSgcClient::HandleChangeL.
The same synchronous SetSgcParams request already had to be deferred for
EikSrv.  Extend that explicit KErrNotSupported UI-first path to MatrixMenu;
keep the stock IPC and leave policy for every other process.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNSGC_MATRIXMENU_SETSGCPARAMS_DEFER_V1"

OLD = r'''		const TBool htcleoDeferSgcParams =
			RProcess().SecureId().iId == 0x10003A4A;
'''

NEW = r'''		// HTCLEO_AKNSGC_MATRIXMENU_SETSGCPARAMS_DEFER_V1
		const TUint32 htcleoSgcProcessSid = RProcess().SecureId().iId;
		const TBool htcleoDeferSgcParams =
			htcleoSgcProcessSid == 0x10003A4Au ||
			htcleoSgcProcessSid == 0x101F4CD2u;
'''


def verify(source: str) -> None:
    homescreen_defer = (
        "HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS_DEFER_V1" in source
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        "matrixmenu target": source.count(
            "htcleoSgcProcessSid == 0x101F4CD2u ||"
        ) == 1
        if homescreen_defer
        else source.count("htcleoSgcProcessSid == 0x101F4CD2u;") == 1,
        "homescreen target": source.count(
            "htcleoSgcProcessSid == 0x102750F0u;"
        ) == 1
        if homescreen_defer
        else True,
        "eiksrv target retained": source.count(
            "htcleoSgcProcessSid == 0x10003A4Au ||"
        ) == 1,
        "old eiksrv-only decision absent": OLD not in source,
        "single decision": source.count(
            "const TBool htcleoDeferSgcParams ="
        ) == 1,
        "stock IPC retained": source.count("iAknSrv.SetSgcParams(") == 1,
        "real stock error policy retained": source.count(
            "User::LeaveIfError(htcleoSgcSetResult);"
        ) == 1,
        "explicit unsupported result retained": source.count(
            "TInt htcleoSgcSetResult = KErrNotSupported;"
        ) == 1,
        "bounded stages retained": (
            source.count("0x0000C529u") == 1
            and source.count("0x0000C52Au") == 1
            and source.count("0x0000C52Bu") == 1
            and source.count("0x0000C52Cu") == 1
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
            "MatrixMenu SetSgcParams deferral verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root / "sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing Avkon SGC input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu SetSgcParams anchor: expected one, "
                f"found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNSGC_MATRIXMENU_SETSGCPARAMS="
        "deferred-keerrnotsupported-c529-c52a"
    )


if __name__ == "__main__":
    main()
