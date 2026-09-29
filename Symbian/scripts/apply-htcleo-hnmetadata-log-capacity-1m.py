#!/usr/bin/env python3
"""Raise all MatrixMenu HN metadata logs to a one-megabyte ceiling.

Hardware 660r1 filled MDLOG exactly at the old 16 KiB ceiling after stage
049C, hiding the remainder of the callback that later panicked with
KERN-EXEC 0 (EBadHandle). This changes only diagnostic append ceilings.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNMETADATA_LOG_CAPACITY_1M_V1"
FILES = (
    "hnmdmodel.cpp",
    "hnmdsuite.cpp",
    "hnqueryresultcollector.cpp",
    "hnmdnotifyrequests.cpp",
)
OLD = "    if (r == KErrNone && position <= ((256 * 64) - 64))\n"
NEW = (
    f"    // {MARKER}\n"
    "    if (r == KErrNone && position <= ((16384 * 64) - 64))\n"
)


def install(text: str, label: str) -> str:
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(f"{label}: expected one 16K ceiling, found {count}")
        text = text.replace(OLD, NEW, 1)
    checks = {
        "marker": text.count(MARKER) == 1,
        "1M ceiling": text.count(
            "position <= ((16384 * 64) - 64)"
        ) == 1,
        "old ceiling retired": OLD not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(f"{label}: " + ", ".join(failed))
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_dir = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src"
    )
    paths = [source_dir / name for name in FILES]
    if not all(path.is_file() for path in paths):
        raise SystemExit("missing HN metadata logger source")
    updated = {
        path: install(path.read_text(encoding="latin-1"), path.name)
        for path in paths
    }
    for path, text in updated.items():
        path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_HNMETADATA_LOG_CAPACITY="
        "1048576-bytes-four-loggers-trace-only"
    )


if __name__ == "__main__":
    main()
