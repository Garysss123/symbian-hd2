#!/usr/bin/env python3
"""Extend Xn factory fail-open to the complete nonvisual metadata set.

Hardware 711 crosses actionshandler and stops at the first widgetmenuitem.
Cross-checking ConstructNodeL's explicit non-layout list against all rendering
factory default_data values leaves a finite metadata-only set.  Preserve the
stock empty-factory behavior for exactly that set; real visual types remain
fail-closed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1"
PREREQUISITE = "HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN_V1"

OLD = r'''         (aName.Compare(_L8("actions")) == 0 ||
          aName.Compare(_L8("action")) == 0 ||
          aName.Compare(_L8("event")) == 0));
'''

NEW = r'''         (aName == KActionsHandlerNodeName ||
          aName == KActionsNodeName ||
          aName == KActionNodeName ||
          aName == KEventNodeName ||
          aName == KDynMenuItemNodeName ||
          aName == KWidgetMenuItemNodeName ||
          aName == KDescNodeName ||
          aName == KTextZoomNodeName ||
          aName == KConfigurationNodeName ||
          aName == KSettingsConfigurationNodeName ||
          aName == KContentSourceNodeName ||
          aName == KMenuExtensionNodeName));
    // HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1
'''


METADATA_NAMES = (
    "KActionsHandlerNodeName",
    "KActionsNodeName",
    "KActionNodeName",
    "KEventNodeName",
    "KDynMenuItemNodeName",
    "KWidgetMenuItemNodeName",
    "KDescNodeName",
    "KTextZoomNodeName",
    "KConfigurationNodeName",
    "KSettingsConfigurationNodeName",
    "KContentSourceNodeName",
    "KMenuExtensionNodeName",
)


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("metadata fail-open requires nonvisual caller guard")
    if text.count(OLD) != 1:
        raise SystemExit("metadata factory predicate anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "metadata set": all(NEW.count(f"aName == {name}") == 1 for name in METADATA_NAMES),
        "real visual types excluded": all(
            name not in NEW
            for name in (
                "KWidgetNodeName",
                "KTextNodeName",
                "KImageNodeName",
                "KViewNodeName",
                "KClockNodeName",
                "KMenuBarNodeName",
                "KNewstickerNodeName",
                "KSliderNodeName",
                "KTextEditorNodeName",
            )
        ),
        "same narrow boundary": (
            text.count("RProcess().SecureId().iId == 0x102750f0u") == 2
            and text.count("interfaceUid.iUid == 0x20019592u") == 1
            and text.count("htcleoFactoryListError == KErrServerTerminated") == 1
        ),
        "same empty-list result": (
            text.count("factories->Container().Reset();") == 1
            and text.count("htcleoFactoryListError = KErrNone;") == 1
            and text.count("User::LeaveIfError(htcleoFactoryListError)") == 1
        ),
        "no timing or display": all(
            token not in NEW for token in ("User::After", "RTimer", "HalFunction")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Xn metadata factory fail-open verification failed: "
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
        "HTCLEO_XN_METADATA_FACTORY_FAILOPEN="
        "homescreen-20019592-explicit-nonlayout-metadata-set"
    )


if __name__ == "__main__":
    main()
