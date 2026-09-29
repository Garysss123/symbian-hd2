#!/usr/bin/env python3
"""Defer the non-returning SGC parameter IPC for HomeScreen on HTCLEO.

Iteration 684 proves every HomeScreen child reaches C529 and stops inside the
following iAknSrv.SetSgcParams call.  EikSrv and MatrixMenu already use the
same fixed-single-panel KErrNotSupported path on HTC Leo.  Extend that proven
path only to HomeScreen SID 0x102750F0; retain the real IPC and leave policy for
all other processes.  No success value or AknSrv handle is fabricated.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS_DEFER_V1"

OLD = '''\t\tconst TBool htcleoDeferSgcParams =
\t\t\thtcleoSgcProcessSid == 0x10003A4Au ||
\t\t\thtcleoSgcProcessSid == 0x101F4CD2u;
'''

NEW = '''\t\t// HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS_DEFER_V1
\t\tconst TBool htcleoDeferSgcParams =
\t\t\thtcleoSgcProcessSid == 0x10003A4Au ||
\t\t\thtcleoSgcProcessSid == 0x101F4CD2u ||
\t\t\thtcleoSgcProcessSid == 0x102750F0u;
'''


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "three exact SIDs": (
            source.count("htcleoSgcProcessSid == 0x10003A4Au ||") == 1
            and source.count("htcleoSgcProcessSid == 0x101F4CD2u ||") == 1
            and source.count("htcleoSgcProcessSid == 0x102750F0u;") == 1
        ),
        "single decision": source.count(
            "const TBool htcleoDeferSgcParams ="
        ) == 1,
        "real IPC retained": source.count("iAknSrv.SetSgcParams(") == 1,
        "real leave policy retained": source.count(
            "User::LeaveIfError(htcleoSgcSetResult);"
        ) == 1,
        "explicit unsupported path": source.count(
            "TInt htcleoSgcSetResult = KErrNotSupported;"
        ) == 1,
        "C529-C52C retained": all(
            source.count(f"0x0000{stage:04X}u") >= 1
            for stage in range(0xC529, 0xC52D)
        ),
        "no timer display handle or fake success": all(
            token not in NEW
            for token in (
                "User::After",
                "RTimer",
                "HalFunction",
                "SetHandle",
                "KErrNone",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = args.root / "sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        if source.count(OLD) != 1:
            raise SystemExit(
                "HomeScreen SetSgcParams anchor: expected one, "
                f"found {source.count(OLD)}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNSGC_HOMESCREEN_SETSGCPARAMS="
        "fixed-panel-deferred-keerrnotsupported-C529-C52C"
    )


if __name__ == "__main__":
    main()
