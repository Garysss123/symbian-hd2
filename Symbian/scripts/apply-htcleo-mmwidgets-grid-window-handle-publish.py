#!/usr/bin/env python3
"""Publish the exact real MatrixMenu grid control handle for WServ tracing.

MatrixMenu creates many windows, so even SID-scoped WServ tracing can fill the
bounded log.  Immediately before the already-traced real grid CreateWindowL(),
publish that control's client handle through a MatrixMenu-owned integer
property.  Logging/property errors remain diagnostic only and do not alter the
real window call or its error behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MMWIDGETS_GRID_WINDOW_HANDLE_PUBLISH_V1"


OLD = r'''    HtcleoMmwLog(0x4D570143u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570144u, KErrNone, 0u);
    CreateWindowL(); // Creates window.'''


NEW = r'''    HtcleoMmwLog(0x4D570143u, KErrNone, 0u);
    // HTCLEO_MMWIDGETS_GRID_WINDOW_HANDLE_PUBLISH_V1
    const TUid htcleoGridHandleCategory = { 0x101F4CD2 };
    const TUint htcleoGridHandleKey = 0x7F4D5701u;
    TInt htcleoGridHandleResult = RProperty::Define(
        htcleoGridHandleCategory,
        htcleoGridHandleKey,
        RProperty::EInt);
    if (htcleoGridHandleResult == KErrAlreadyExists)
        {
        htcleoGridHandleResult = KErrNone;
        }
    if (htcleoGridHandleResult == KErrNone)
        {
        htcleoGridHandleResult = RProperty::Set(
            htcleoGridHandleCategory,
            htcleoGridHandleKey,
            (TInt)this);
        }
    HtcleoMmwLog(0x4D570144u, htcleoGridHandleResult, (TUint32)this);
    CreateWindowL(); // Creates window.'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"grid window anchor: expected one, found {count}")
    source = source.replace(
        '#include "hnglobals.h"\n',
        '#include "hnglobals.h"\n#include <e32property.h>\n',
        1,
    )
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "property include": source.count("#include <e32property.h>") == 1,
        "exact category": source.count("0x101F4CD2") == 1,
        "exact key": source.count("0x7F4D5701u") == 1,
        "pointer publish": source.count("(TInt)this") == 1,
        "pointer log": source.count(
            "HtcleoMmwLog(0x4D570144u, htcleoGridHandleResult, (TUint32)this);"
        ) == 1,
        "real window retained": source.count(
            "CreateWindowL(); // Creates window."
        ) == 1,
        "diagnostic fail open": (
            "User::LeaveIfError(htcleoGridHandleResult)" not in source
            and "TRAP" not in NEW
            and "User::After" not in NEW
            and "HalFunction" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/mmwidgets/src/mmgridcontainer.cpp"
    )
    source = path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MMWIDGETS_GRID_WINDOW_HANDLE="
        "property-101f4cd2-7f4d5701-stage-0144"
    )


if __name__ == "__main__":
    main()
