#!/usr/bin/env python3
"""Publish the exact MenuContent output-list count for bounded HN recovery."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_GETLIST_SERVER_COUNT_PROPERTY_V1"
INCLUDE_ANCHOR = "#include <s32mem.h>\n"
INCLUDE_PATCHED = "#include <s32mem.h>\n#include <e32property.h>\n"
LIST_TAIL = "\t\t\t\tignoredAttributes );"
LIST_TAIL_PATCHED = r'''                ignoredAttributes );

    // HTCLEO_MCS_GETLIST_SERVER_COUNT_PROPERTY_V1
    // outputList is the real server-created GetList result.  MatrixMenu owns
    // this always-pass property; HN still rejects values outside 1..30.
    const TUid htcleoCountCategory = { 0x101F4CD2 };
    const TUint htcleoCountKey = 0x7F4D4302u;
    RProperty::Set(htcleoCountCategory, htcleoCountKey,
        outputList->Count());'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if "#include <e32property.h>" not in text:
        if text.count(INCLUDE_ANCHOR) != 1:
            raise SystemExit("MCS server count: include anchor missing")
        text = text.replace(INCLUDE_ANCHOR, INCLUDE_PATCHED, 1)
    if text.count(LIST_TAIL) != 1:
        raise SystemExit(
            f"MCS server count: list anchor count={text.count(LIST_TAIL)}"
        )
    return text.replace(LIST_TAIL, LIST_TAIL_PATCHED, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "property include": text.count("#include <e32property.h>") == 1,
        "MatrixMenu category": text.count("0x101F4CD2") == 1,
        "count key": text.count("0x7F4D4302u") == 1,
        "real output count": text.count("outputList->Count()") == 1,
        "single set": text.count("RProperty::Set(") == 1,
        "real list retained": (
            text.count("outputListCreator->CreateLC(") == 1
            and text.count("TLiwVariant lvList( outputList );") == 1
            and text.count("TLiwGenericParam lgpList( KReturnValue, lvList );") == 1
        ),
        "no wait or fabricated items": all(
            token not in text for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS server count property verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/mcsgetlisthandler.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MCS GetList handler: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MCS_GETLIST_SERVER_COUNT="
        "real-output-list-property-7f4d4302-hn-bounded-30"
    )


if __name__ == "__main__":
    main()
