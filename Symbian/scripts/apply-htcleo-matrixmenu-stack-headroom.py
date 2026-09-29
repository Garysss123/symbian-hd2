#!/usr/bin/env python3
"""Give the HTCLEO MatrixMenu shell enough stack for GCCE-built Avkon.

The source-built eikcoctl AknLayoutRect() requires a 0x15d4-byte frame before
its first statement.  The stock MatrixMenu MMP does not declare a stack size,
so the platform default is insufficient in the deep status-pane call chain.
Set only MatrixMenu's process stack to 64 KiB; heap limits and behavior remain
unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_GCCE_STACK_HEADROOM_V1"
STACK_SIZE = "0x10000"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(mmp: str) -> str:
    return replace_once(
        mmp,
        "epocheapsize  1800000 4500000\n\n"
        "TARGET          matrixmenu.exe",
        "epocheapsize  1800000 4500000\n"
        f"// {MARKER}\n"
        f"EPOCSTACKSIZE   {STACK_SIZE}\n\n"
        "TARGET          matrixmenu.exe",
        "MatrixMenu stack-size anchor",
    )


def verify(mmp: str) -> None:
    checks = {
        "marker": mmp.count(MARKER) == 1,
        "stack size": mmp.count(f"EPOCSTACKSIZE   {STACK_SIZE}") == 1,
        "heap unchanged": mmp.count("epocheapsize  1800000 4500000") == 1,
        "target unchanged": mmp.count("TARGET          matrixmenu.exe") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu stack headroom verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/group/matrixmenu.mmp"
    )
    mmp = path.read_text(encoding="latin-1")
    if MARKER not in mmp:
        mmp = install(mmp)
    verify(mmp)
    if mmp != path.read_text(encoding="latin-1"):
        path.write_text(mmp, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_STACK_HEADROOM=installed "
        "stack=0x10000 heap=unchanged scope=matrixmenu"
    )


if __name__ == "__main__":
    main()
