#!/usr/bin/env python3
"""Raise MatrixMenu's durable log ceiling to one MiB."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_MATRIXMENU_LOG_CAPACITY_64K_V1"
MARKER = "HTCLEO_MATRIXMENU_LOG_CAPACITY_1M_V1"
OLD_BOUND = "position <= ((1024 * 64) - 64)"
NEW_BOUND = "position <= ((16384 * 64) - 64)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/htcleomenulog.cpp"
    )
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        if text.count(OLD_MARKER) != 1 or text.count(OLD_BOUND) != 1:
            raise SystemExit("MatrixMenu 1 MiB capacity prerequisite mismatch")
        text = text.replace(OLD_MARKER, MARKER, 1)
        text = text.replace(OLD_BOUND, NEW_BOUND, 1)
    checks = {
        "marker": text.count(MARKER) == 1,
        "one MiB bound": text.count(NEW_BOUND) == 1,
        "old capacity retired": OLD_MARKER not in text and OLD_BOUND not in text,
        "same path": text.count(r"C:\\Symbian3\\MENULOG.TXT") == 1,
        "same record": text.count('TBuf8<96> record;') == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MatrixMenu 1 MiB capacity failed: " + "; ".join(failed))
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_MATRIXMENU_LOG_CAPACITY=1048576-bytes-own-writer")


if __name__ == "__main__":
    main()
