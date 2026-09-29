#!/usr/bin/env python3
"""Publish post-E100 AknCap stages through the existing boot-local property.

Iteration 505 proves that retiring synchronous AKNCAP.TXT writes after E100 is
safe, but its MENULOG remains byte-identical to 504 because a no-op logger no
longer exposes progress inside CAknCapAppServerAppUi::ConstructL.  Reuse the
already-defined 0x10207218/0x7f044301 EikCore trace property: every retired
logger call publishes ``stage << 16 | result`` and returns without filesystem
I/O.  The existing MatrixMenu A21D sampler makes the breadcrumb durable.

This is diagnostic-only.  It introduces no waits, retries, display writes or
changes to AknCap construction and ready/rendezvous control flow.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_POSTCRITICAL_PROPERTY_BREADCRUMB_V1"
PRE_RETIREMENT_MARKER = "HTCLEO_AKNCAPSERVER_E100_PRE_RETIREMENT_V1"


def install(source: str) -> str:
    include_anchor = "#include <f32file.h>\n"
    include_replacement = "#include <f32file.h>\n#include <e32property.h>\n"
    if source.count(include_anchor) != 1:
        raise SystemExit(
            "AKNCAP f32file include: expected one, found "
            f"{source.count(include_anchor)}"
        )
    source = source.replace(include_anchor, include_replacement, 1)

    old_guard = """    if (gHtcleoAknCapFileLogRetired)
        {
        return;
        }
"""
    new_guard = f"""    if (gHtcleoAknCapFileLogRetired)
        {{
        // {MARKER}
        const TUint32 htcleoBreadcrumb =
            ((aStage & 0xffffu) << 16) |
            ((TUint32)aResult & 0xffffu);
        (void)RProperty::Set(
            TUid::Uid(0x10207218), 0x7f044301u,
            (TInt)htcleoBreadcrumb);
        return;
        }}
"""
    if source.count(old_guard) != 1:
        raise SystemExit(
            "postcritical no-op guard: expected one, found "
            f"{source.count(old_guard)}"
        )
    return source.replace(old_guard, new_guard, 1)


def verify(source: str) -> None:
    expected_retirement_assignments = (
        2 if PRE_RETIREMENT_MARKER in source else 1
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        "property include available before logger": source.count(
            "#include <f32file.h>\n#include <e32property.h>\n"
        )
        == 1,
        "single retired guard": source.count(
            "if (gHtcleoAknCapFileLogRetired)"
        )
        == 1,
        "single property write": source.count(
            "(void)RProperty::Set(\n"
            "            TUid::Uid(0x10207218), 0x7f044301u,"
        )
        == 1,
        "stage/result packing": source.count(
            "((aStage & 0xffffu) << 16) |"
        )
        == 1
        and source.count("((TUint32)aResult & 0xffffu);") == 1,
        "file retirement retained": source.count(
            "gHtcleoAknCapFileLogRetired = ETrue;"
        )
        == expected_retirement_assignments,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "postcritical property breadcrumb verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src/AknCapServerEntry.cpp"
    )
    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAPSERVER_POSTCRITICAL_PROPERTY_BREADCRUMB=installed "
        "key=10207218:7f044301 packing=stage16-result16 fat-io=none"
    )


if __name__ == "__main__":
    main()
