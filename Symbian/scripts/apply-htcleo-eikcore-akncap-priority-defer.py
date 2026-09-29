#!/usr/bin/env python3
"""Keep AknCap runnable until its startup-ready handshake completes.

Iteration 502 proved that the single AknCap child reaches the stock
``RThread().SetProcessPriority(EPriorityBackground)`` call but never returns
while MatrixMenu performs its bounded no-timer readiness polling.  Preserve
the stock priority change for every other SID and defer it only for AknCap.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_AKNCAP_PRIORITY_DEFER_V1"
AKNCAP_SID = "0x10207218u"


def install(source: str) -> str:
    old = (
        "\t\t\tHtcleoEikCorePreFactoryTrace(0xE31Bu, KErrNone);\n"
        "\t\t\tRThread().SetProcessPriority(EPriorityBackground);\n"
        "\t\t\tHtcleoEikCorePreFactoryTrace(0xE31Cu, KErrNone);"
    )
    new = (
        "\t\t\tHtcleoEikCorePreFactoryTrace(0xE31Bu, KErrNone);\n"
        f"\t\t\t// {MARKER}\n"
        "\t\t\tconst TBool htcleoDeferBackgroundPriority = "
        f"(RProcess().SecureId().iId == {AKNCAP_SID});\n"
        "\t\t\tif (!htcleoDeferBackgroundPriority)\n"
        "\t\t\t\tRThread().SetProcessPriority(EPriorityBackground);\n"
        "\t\t\tHtcleoEikCorePreFactoryTrace(0xE31Cu, "
        "htcleoDeferBackgroundPriority);"
    )
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"priority anchor: expected one, found {count}")
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "AknCap SID": source.count(
            f"RProcess().SecureId().iId == {AKNCAP_SID}"
        )
        >= 1,
        "defer flag": source.count("htcleoDeferBackgroundPriority") == 3,
        "stock priority retained": source.count(
            "RThread().SetProcessPriority(EPriorityBackground)"
        )
        >= 1,
        "E31B retained": source.count(
            "HtcleoEikCorePreFactoryTrace(0xE31Bu"
        )
        == 1,
        "E31C retained": source.count(
            "HtcleoEikCorePreFactoryTrace(0xE31Cu"
        )
        == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_AKNCAP_PRIORITY_DEFER=installed "
        "sid=10207218 stock-other-sids"
    )


if __name__ == "__main__":
    main()
