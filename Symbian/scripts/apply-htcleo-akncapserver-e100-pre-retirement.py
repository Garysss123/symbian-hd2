#!/usr/bin/env python3
"""Pre-arm AknCap FAT-log retirement before the proven E100 flush blocker.

Iteration 506 leaves a durable E100 record but never changes the already
defined stage property from E311.  The V1 retirement flag is assigned only
after Write, Flush, file Close and RFs Close return, so the record proves the
write reached media but does not prove the logger returned or retirement was
armed.  Set the existing flag immediately before the E100 logger call.  E100
and every later call then use the property-only path without FAT I/O.

This changes diagnostic transport only.  User::SetCritical, application
construction, readiness, rendezvous and MatrixMenu retry policy are retained.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_E100_PRE_RETIREMENT_V1"
CRITICALITY_MARKER = "HTCLEO_AKNCAPSERVER_CRITICALITY_BYPASS_V1"


def install(source: str) -> str:
    old = """void CAknCapAppServerAppUi::ConstructL()
    {
    HtcleoAknCapLog(0x0000E100u, KErrNone, 0x4E4F494Fu);
    User::SetCritical(User::ESystemCritical);
"""
    new = f"""void CAknCapAppServerAppUi::ConstructL()
    {{
    // {MARKER}
    // The prior E100 record can be durable while its Flush never returns.
    // Arm the existing property-only path before entering that logger call.
    gHtcleoAknCapFileLogRetired = ETrue;
    HtcleoAknCapLog(0x0000E100u, KErrNone, 0x4E4F494Fu);
    User::SetCritical(User::ESystemCritical);
"""
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"E100 pre-retirement anchor: expected one, found {count}"
        )
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    expected_setcritical_calls = 0 if CRITICALITY_MARKER in source else 1
    checks = {
        "single marker": source.count(MARKER) == 1,
        "single pre-arm": source.count(
            "gHtcleoAknCapFileLogRetired = ETrue;"
        )
        == 2,
        "pre-arm immediately before E100": source.count(
            "gHtcleoAknCapFileLogRetired = ETrue;\n"
            "    HtcleoAknCapLog(0x0000E100u, KErrNone, 0x4E4F494Fu);"
        )
        == 1,
        "property breadcrumb retained": source.count(
            "HTCLEO_AKNCAPSERVER_POSTCRITICAL_PROPERTY_BREADCRUMB_V1"
        )
        == 1,
        "criticality layering consistent": source.count(
            "User::SetCritical(User::ESystemCritical);"
        )
        == expected_setcritical_calls,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "E100 pre-retirement verification failed: " + ", ".join(failed)
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
        "HTCLEO_AKNCAPSERVER_E100_RETIREMENT=prearmed "
        "transport=property-only fat-io=none setcritical=retained"
    )


if __name__ == "__main__":
    main()
