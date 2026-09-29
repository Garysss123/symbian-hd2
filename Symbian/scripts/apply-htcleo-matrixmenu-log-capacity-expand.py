#!/usr/bin/env python3
"""Expand MatrixMenu's own MENULOG writer beyond the 585 startup frontier."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_LOG_CAPACITY_64K_V1"
MARKER_1M = "HTCLEO_MATRIXMENU_LOG_CAPACITY_1M_V1"
OLD = "    if (r == KErrNone && position <= ((256 * 64) - 64))\n"
NEW = r'''    // HTCLEO_MATRIXMENU_LOG_CAPACITY_64K_V1
    if (r == KErrNone && position <= ((1024 * 64) - 64))
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/htcleomenulog.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu logger source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER_1M in text:
        if text.count("position <= ((16384 * 64) - 64)") != 1:
            raise SystemExit("MatrixMenu 1 MiB capacity marker/bound mismatch")
        print("HTCLEO_MATRIXMENU_LOG_CAPACITY=1048576-bytes-own-writer")
        return
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise SystemExit(
                "MatrixMenu log capacity: expected one 16K bound, "
                f"found {text.count(OLD)}"
            )
        text = text.replace(OLD, NEW, 1)
    checks = {
        "marker": text.count(MARKER) == 1,
        "64K bound": text.count("position <= ((1024 * 64) - 64)") == 1,
        "old bound gone": "position <= ((256 * 64) - 64)" not in text,
        "same path": text.count(r"C:\\Symbian3\\MENULOG.TXT") == 1,
        "same prefix": text.count('"HTCLEO_MENU "') == 1,
        "no delay": "User::After" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu log capacity verification failed: " + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_MATRIXMENU_LOG_CAPACITY=65536-bytes-own-writer")


if __name__ == "__main__":
    main()
