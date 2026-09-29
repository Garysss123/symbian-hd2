#!/usr/bin/env python3
"""Cover the three source-proven nonvisual Xn action node types.

Iteration 708 did not enter the singular ``action`` predicate.  The real
persistent theme sources order these nodes as ``actions``, ``action``,
``trigger``, ``event``; Xn handles trigger as a built-in general node, while
actions/action/event all reach the optional rendering-factory list.  Extend the
same bounded recovery to exactly those three nonvisual resolver types without
masking any visual factory query.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY_V1"
PREREQUISITE = "HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1"

OLD = r'''	// HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1
	const TBool htcleoHomeScreenActionFactoryList =
		(RProcess().SecureId().iId == 0x102750F0u &&
		 aInterfaceUid.iUid == 0x20019592u &&
		 aResolutionParameters.DataType().Compare(_L8("action")) == 0);
	const TBool htcleoUiShellList =
		htcleoMatrixMenuList || htcleoHomeScreenExternalList ||
		htcleoHomeScreenActionFactoryList;
'''

NEW = r'''	// HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1
	// HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY_V1
	const TDesC8& htcleoHomeScreenResolverType =
		aResolutionParameters.DataType();
	const TBool htcleoHomeScreenNonvisualFactoryList =
		(RProcess().SecureId().iId == 0x102750F0u &&
		 aInterfaceUid.iUid == 0x20019592u &&
		 (htcleoHomeScreenResolverType.Compare(_L8("actions")) == 0 ||
		  htcleoHomeScreenResolverType.Compare(_L8("action")) == 0 ||
		  htcleoHomeScreenResolverType.Compare(_L8("event")) == 0));
	const TBool htcleoUiShellList =
		htcleoMatrixMenuList || htcleoHomeScreenExternalList ||
		htcleoHomeScreenNonvisualFactoryList;
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("nonvisual retry requires singular action retry")
    if text.count(OLD) != 1:
        raise SystemExit("nonvisual retry scope anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    menubar_extended = (
        "HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1" in text
    )
    rendering_extended = (
        "HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY_V1" in text
    )
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "single descriptor": text.count(
            "const TDesC8& htcleoHomeScreenResolverType"
        ) == 1,
        "exact nonvisual types": all(
            text.count(f'htcleoHomeScreenResolverType.Compare(_L8("{name}")) == 0')
            == 1
            for name in ("actions", "action", "event")
        ),
        "exact interface": text.count(
            "aInterfaceUid.iUid == 0x20019592u"
        ) == (2 if menubar_extended else 1),
        "shared recovery": (
            (
                text.count("htcleoHomeScreenNonvisualFactoryList;") == 1
                if rendering_extended
                else text.count("htcleoHomeScreenNonvisualFactoryList ||") == 1
                if menubar_extended
                else text.count("htcleoHomeScreenNonvisualFactoryList;") == 1
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
        "visual types exposed": all(
            token not in NEW for token in ('_L8("text")', '_L8("image")', '_L8("view")')
        ),
        "no timer": "User::After" not in NEW,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom HomeScreen nonvisual-list retry verification failed: "
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
        "HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY="
        "sid-102750f0-interface-20019592-types-actions-action-event"
    )


if __name__ == "__main__":
    main()
