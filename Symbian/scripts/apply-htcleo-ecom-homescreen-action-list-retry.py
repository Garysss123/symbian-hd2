#!/usr/bin/env python3
"""Recover the HomeScreen rendering-factory query for nonvisual action nodes.

Iteration 707 proves the external-rendering list fallback returns naturally,
then CXnODTParser enters CreateFactoryControlL for the same ``action`` node and
the rendering-factory interface 0x20019592 returns KErrServerTerminated.  Add
only that exact SID/interface/resolver tuple to the already bounded reconnect;
do not hide failures for visual text/image/view factories.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1"
PREREQUISITE = "HTCLEO_ECOM_HOMESCREEN_LIST_RETRY_V1"

OLD = r'''	const TBool htcleoHomeScreenExternalList =
		(RProcess().SecureId().iId == 0x102750F0u &&
		 aInterfaceUid.iUid == 0x200286DFu);
	const TBool htcleoUiShellList =
		htcleoMatrixMenuList || htcleoHomeScreenExternalList;
'''

NEW = r'''	const TBool htcleoHomeScreenExternalList =
		(RProcess().SecureId().iId == 0x102750F0u &&
		 aInterfaceUid.iUid == 0x200286DFu);
	// HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1
	const TBool htcleoHomeScreenActionFactoryList =
		(RProcess().SecureId().iId == 0x102750F0u &&
		 aInterfaceUid.iUid == 0x20019592u &&
		 aResolutionParameters.DataType().Compare(_L8("action")) == 0);
	const TBool htcleoUiShellList =
		htcleoMatrixMenuList || htcleoHomeScreenExternalList ||
		htcleoHomeScreenActionFactoryList;
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("HomeScreen action retry requires external-list retry")
    if text.count(OLD) != 1:
        raise SystemExit("HomeScreen action retry scope anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    nonvisual_extended = (
        "HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY_V1" in text
    )
    menubar_extended = (
        "HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1" in text
    )
    rendering_extended = (
        "HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY_V1" in text
    )
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "exact SID": text.count(
            "RProcess().SecureId().iId == 0x102750F0u"
        ) == (4 if menubar_extended else 3),
        "factory interface": text.count(
            "aInterfaceUid.iUid == 0x20019592u"
        ) == (2 if menubar_extended else 1),
        "action retained": text.count(
            'htcleoHomeScreenResolverType.Compare(_L8("action")) == 0'
            if nonvisual_extended
            else 'aResolutionParameters.DataType().Compare(_L8("action")) == 0'
        ) == 1,
        "shared recovery": (
            (
                text.count("htcleoHomeScreenNonvisualFactoryList;") == 1
                if rendering_extended
                else text.count("htcleoHomeScreenNonvisualFactoryList ||") == 1
                if menubar_extended
                else text.count(
                    "htcleoHomeScreenNonvisualFactoryList;"
                    if nonvisual_extended
                    else "htcleoHomeScreenActionFactoryList;"
                ) == 1
            )
            and text.count(
                "if(htcleoUiShellList && error == KErrServerTerminated)"
            ) == (1 if menubar_extended else 2)
            and (
                not menubar_extended
                or text.count(
                    "if(htcleoUiShellListFailOpen && "
                    "error == KErrServerTerminated)"
                ) == 1
            )
            and text.count("TRAPD(htcleoListReconnectResult, ConstructL())") == 1
        ),
        "no visual factory masking": all(
            token not in NEW for token in ('_L8("text")', '_L8("image")', '_L8("view")')
        ),
        "no delay": "User::After" not in NEW,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom HomeScreen action-list retry verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY="
        "sid-102750f0-interface-20019592-type-action-one-reconnect-then-empty"
    )


if __name__ == "__main__":
    main()
