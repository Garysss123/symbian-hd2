#!/usr/bin/env python3
"""Allow the existing HomeScreen logger to emit focus/key-block stages."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V1"
UPGRADE_MARKER = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V2"
PREREQUISITE = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_KEYBLOCK_COMPAT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if text.count(PREREQUISITE) != 1:
        raise SystemExit("HomeScreen focus/key-block prerequisite is missing")
    if text.count(UPGRADE_MARKER) == 1:
        return text
    if text.count(MARKER) == 1:
        text = replace_once(
            text,
            "    // HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V1\n",
            "    // HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V1\n"
            "    // HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V2\n",
            "focus route upgrade marker",
        )
        return replace_once(
            text,
            "aStage >= 0x0000C560u && aStage <= 0x0000C576u",
            "aStage >= 0x0000C560u && aStage <= 0x0000C59Fu",
            "focus route upper bound",
        )
    return replace_once(
        text,
        """    const TBool htcleoHomeSgcStage =
        aStage >= 0x0000C500u && aStage <= 0x0000C52Cu;
    if (htcleoLogHomeScreen &&
        !htcleoHomeBaseStage && !htcleoHomePostCoeStage &&
        !htcleoHomeSgcStage)
""",
        """    const TBool htcleoHomeSgcStage =
        aStage >= 0x0000C500u && aStage <= 0x0000C52Cu;
    // HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V1
    // HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V2
    const TBool htcleoHomeFocusStage =
        aStage >= 0x0000C560u && aStage <= 0x0000C59Fu;
    if (htcleoLogHomeScreen &&
        !htcleoHomeBaseStage && !htcleoHomePostCoeStage &&
        !htcleoHomeSgcStage && !htcleoHomeFocusStage)
""",
        "HomeScreen focus-stage logger route",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "upgrade marker": text.count(UPGRADE_MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "focus range start": text.count("aStage >= 0x0000C560u") == 1,
        "focus range end": text.count("aStage <= 0x0000C59Fu") == 1,
        "route predicate": text.count("!htcleoHomeFocusStage") == 1,
        "old ranges retained": (
            text.count("aStage >= 0x0000B500u") == 1
            and text.count("aStage >= 0x0000B530u") == 1
            and text.count("aStage >= 0x0000C500u") == 1
        ),
        "one MiB retained": text.count("1048576 - 128") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen focus log-route audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing AknAppUi source: {path}")
    text = patch(path.read_text(encoding="latin-1"))
    path.write_text(text, encoding="latin-1")
    verify(text)
    print(
        "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE="
        "HSXML-C560-C59F-enabled-existing-1m"
    )


if __name__ == "__main__":
    main()
