#!/usr/bin/env python3
"""Persist the HomeScreen child panic category before bounded restart."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HOMESCREEN_EXIT_CATEGORY_TRACE_V1"
RESTART_MARKER = "HTCLEO_HOMESCREEN_BOUNDED_RESTART_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    if text.count(RESTART_MARKER) != 1:
        raise SystemExit("bounded restart prerequisite is missing or duplicated")

    text = replace_once(
        text,
        f"// {RESTART_MARKER}\n",
        f"// {RESTART_MARKER}\n// {MARKER}\n",
        "exit-category marker",
    )
    text = replace_once(
        text,
        """void CHsLaunch::ProcessEnded( const TExitType& aExitType,
                              const TInt aExitReason,
                              const TExitCategoryName& /*aExitCategory*/ )
    {
    HtcleoHomeLog(0x484F0240u, aExitReason, (TUint32)aExitType);
""",
        """void CHsLaunch::ProcessEnded( const TExitType& aExitType,
                              const TInt aExitReason,
                              const TExitCategoryName& aExitCategory )
    {
    HtcleoHomeLog(0x484F0240u, aExitReason, (TUint32)aExitType);
    const TInt htcleoCategoryLength =
        aExitCategory.Length() < 16 ? aExitCategory.Length() : 16;
    HtcleoHomeLog(0x484F0246u, htcleoCategoryLength, 0u);
    for ( TInt i = 0; i < htcleoCategoryLength; i += 2 )
        {
        TUint32 pair = (TUint32)aExitCategory[i];
        if ( i + 1 < htcleoCategoryLength )
            {
            pair |= ((TUint32)aExitCategory[i + 1]) << 16;
            }
        HtcleoHomeLog(0x484F0247u + (TUint32)(i >> 1), i, pair);
        }
""",
        "exit-category records",
    )
    return text


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "restart prerequisite": text.count(RESTART_MARKER) == 1,
        "named category": text.count(
            "const TExitCategoryName& aExitCategory"
        ) == 1,
        "bounded category": text.count("aExitCategory.Length() < 16") == 1,
        "category header": text.count("0x484F0246u") == 1,
        "category pairs": text.count("0x484F0247u +") == 1,
        "category indexing": text.count("aExitCategory[i + 1]") == 1,
        "restart trace retained": text.count("0x484F0243u") == 1,
        "restart fuse retained": text.count("0x484F0244u") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "homescreen exit-category trace audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/idlefw/hslaunch/src/hslaunch.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing HomeScreen launcher source: {path}")
    text = patch(path.read_text(encoding="latin-1"))
    path.write_text(text, encoding="latin-1")
    verify(text)
    print(
        "HTCLEO_HOMESCREEN_EXIT_CATEGORY_TRACE="
        "HSLOG-1m-0240-0246-024e-utf16-pairs"
    )


if __name__ == "__main__":
    main()
