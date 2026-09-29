#!/usr/bin/env python3
"""Accept empty factories for the two QHD menu grouping metadata nodes."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XN_MENU_GROUP_METADATA_FAILOPEN_V1"
PREREQUISITE = "HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1"

OLD = '''          aName == KContentSourceNodeName ||
          aName == KMenuExtensionNodeName));
    // HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1
'''

NEW = '''          aName == KContentSourceNodeName ||
          aName == KMenuExtensionNodeName ||
          aName.Compare(_L8("menuitemgrouping")) == 0 ||
          aName.Compare(_L8("menuitemgroup")) == 0));
    // HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1
    // HTCLEO_XN_MENU_GROUP_METADATA_FAILOPEN_V1
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("menu-group fail-open requires metadata factory guard")
    if text.count(OLD) != 1:
        raise SystemExit("menu-group metadata predicate anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "two exact groups": (
            text.count('aName.Compare(_L8("menuitemgrouping")) == 0') == 1
            and text.count('aName.Compare(_L8("menuitemgroup")) == 0') == 1
        ),
        "same boundary": (
            text.count("RProcess().SecureId().iId == 0x102750f0u") == 2
            and text.count("interfaceUid.iUid == 0x20019592u") == 1
            and text.count("htcleoFactoryListError == KErrServerTerminated") == 1
        ),
        "same empty result": (
            text.count("factories->Container().Reset();") == 1
            and text.count("htcleoFactoryListError = KErrNone;") == 1
        ),
        "visual types excluded": all(
            token not in NEW
            for token in (
                '_L8("menubar")',
                '_L8("view")',
                '_L8("widget")',
                '_L8("text")',
                '_L8("image")',
            )
        ),
        "no timing or display": all(
            token not in NEW for token in ("User::After", "RTimer", "HalFunction")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Xn menu-group metadata fail-open verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/app/homescreen/idlehomescreen/xmluirendering/"
        "uiengine/src/xnodtparser.cpp"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_XN_MENU_GROUP_FACTORY_FAILOPEN="
        "homescreen-20019592-menuitemgrouping-menuitemgroup-serverterminated-empty"
    )


if __name__ == "__main__":
    main()
