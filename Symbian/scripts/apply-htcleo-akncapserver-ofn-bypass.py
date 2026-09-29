#!/usr/bin/env python3
"""Skip Nokia optical-finger-navigation startup on HTC Leo.

HTC HD2 has no OFN device.  Calling ``InitiateOFNStatus`` can enter the
Nokia-specific FeatureManager/CenRep/HAL path before AknCapServer publishes its
ready state.  Keep the stock helper in the source, but do not invoke it in the
HTCLEO AknCapServer build.  E102 remains the durable post-boundary record and
uses an OFN tag so hardware logs prove that this exact policy ran.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_OFN_BYPASS_V1"
OFN_TAG = "0x4F464E00u"


def install(source: str) -> str:
    old = (
        "    InitiateOFNStatus();\n"
        "    HtcleoAknCapLog(0x0000E102u, KErrNone, 0u);"
    )
    new = (
        f"    // {MARKER}\n"
        "    // HTC Leo has no optical finger navigation hardware.\n"
        f"    HtcleoAknCapLog(0x0000E102u, KErrNone, {OFN_TAG});"
    )
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"OFN call anchor: expected one, found {count}")
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "OFN call removed": source.count("    InitiateOFNStatus();") == 0,
        "stock helper retained": source.count(
            "void CAknCapAppServerAppUi::InitiateOFNStatus()"
        )
        == 1,
        "tagged E102": source.count(
            f"HtcleoAknCapLog(0x0000E102u, KErrNone, {OFN_TAG});"
        )
        == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("OFN bypass verification failed: " + ", ".join(failed))


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
        "HTCLEO_AKNCAPSERVER_OFN_BYPASS=installed "
        "policy=no-optical-navigation e102-detail=4F464E00"
    )


if __name__ == "__main__":
    main()
