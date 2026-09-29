#!/usr/bin/env python3
"""Expand MDLOG capacity after iteration 533 fills the original 4 KiB file.

The evaluation control flow is unchanged.  Only the close-only append ceiling in
the three MatrixMenu-gated metadata loggers grows from 4096 to 16384 bytes.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKERS = {
    "hnmdmodel.cpp": "HTCLEO_HNMETADATA_LOG_CAPACITY_16K_V1",
    "hnmdsuite.cpp": "HTCLEO_HNMDSUITE_LOG_CAPACITY_16K_V1",
    "hnqueryresultcollector.cpp": "HTCLEO_HNQUERY_LOG_CAPACITY_16K_V1",
}


def expand(source: str, marker: str, label: str) -> str:
    if "HTCLEO_HNMETADATA_LOG_CAPACITY_1M_V1" in source:
        if source.count(marker) != 1:
            raise SystemExit(f"{label}: retained 16K marker mismatch")
        if source.count("position <= ((16384 * 64) - 64)") != 1:
            raise SystemExit(f"{label}: installed 1M ceiling mismatch")
        if "position <= ((64 * 64) - 64)" in source:
            raise SystemExit(f"{label}: stale 4K ceiling remains")
        return source
    if marker not in source:
        old = "    if (r == KErrNone && position <= ((64 * 64) - 64))\n"
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"{label}: expected one 4K ceiling, found {count}")
        source = source.replace(
            old,
            f"    // {marker}\n"
            "    if (r == KErrNone && position <= ((256 * 64) - 64))\n",
            1,
        )
    if source.count(marker) != 1:
        raise SystemExit(f"{label}: capacity marker mismatch")
    if source.count("position <= ((256 * 64) - 64)") != 1:
        raise SystemExit(f"{label}: 16K ceiling mismatch")
    if "position <= ((64 * 64) - 64)" in source:
        raise SystemExit(f"{label}: stale 4K ceiling remains")
    return source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_dir = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src"
    )
    paths = {name: source_dir / name for name in MARKERS}
    if not all(path.is_file() for path in paths.values()):
        raise SystemExit("missing HN metadata logger sources")
    updated = {}
    for name, path in paths.items():
        source = path.read_text(encoding="latin-1")
        updated[path] = expand(source, MARKERS[name], name)
    for path, source in updated.items():
        path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_HNMETADATA_LOG_CAPACITY=expanded "
        "from=4096 to=16384 behavior=unchanged"
    )


if __name__ == "__main__":
    main()
