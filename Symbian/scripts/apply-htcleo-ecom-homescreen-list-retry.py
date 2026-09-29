#!/usr/bin/env python3
"""Extend the proven ECom list reconnect to HomeScreen external controls.

Iteration 706 reached CXnODTParser::CreateExternalControlL() for the first
``action`` node in two independent HomeScreen processes.  Both calls left with
KErrServerTerminated while listing interface 0x200286DF.  Reuse the existing
MatrixMenu one-shot reconnect/empty-list fallback, but only for HomeScreen and
that exact optional external-rendering interface.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_LIST_RETRY_V1"
PREREQUISITE = "HTCLEO_ECOM_MATRIXMENU_LIST_RETRY_V1"

SCOPE_OLD = r'''	const TBool htcleoMatrixMenuList =
		(RProcess().SecureId().iId == 0x101F4CD2u);
	const TBool htcleoFeatMgrTrace =
'''

SCOPE_NEW = r'''	const TBool htcleoMatrixMenuList =
		(RProcess().SecureId().iId == 0x101F4CD2u);
	// HTCLEO_ECOM_HOMESCREEN_LIST_RETRY_V1
	const TBool htcleoHomeScreenExternalList =
		(RProcess().SecureId().iId == 0x102750F0u &&
		 aInterfaceUid.iUid == 0x200286DFu);
	const TBool htcleoUiShellList =
		htcleoMatrixMenuList || htcleoHomeScreenExternalList;
	const TBool htcleoFeatMgrTrace =
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("HomeScreen list retry requires MatrixMenu list retry")
    if text.count(SCOPE_OLD) != 1:
        raise SystemExit("HomeScreen list retry scope anchor mismatch")
    text = text.replace(SCOPE_OLD, SCOPE_NEW, 1)
    if text.count("if(htcleoMatrixMenuList)") != 2:
        raise SystemExit("HomeScreen list retry trace predicate count mismatch")
    if text.count(
        "if(htcleoMatrixMenuList && error == KErrServerTerminated)"
    ) != 2:
        raise SystemExit("HomeScreen list retry recovery predicate count mismatch")
    text = text.replace("if(htcleoMatrixMenuList)", "if(htcleoUiShellList)")
    text = text.replace(
        "if(htcleoMatrixMenuList && error == KErrServerTerminated)",
        "if(htcleoUiShellList && error == KErrServerTerminated)",
    )
    text = text.replace(
        "MatrixMenu can therefore retain its normal\n"
        "\t\t// non-effect/non-plugin fallback without terminating the UI process.",
        "MatrixMenu and the exact HomeScreen external-control list can therefore\n"
        "\t\t// retain their normal non-effect/non-plugin fallback without terminating UI.",
        1,
    )
    return text


def verify(text: str) -> None:
    action_factory_extended = (
        "HTCLEO_ECOM_HOMESCREEN_ACTION_LIST_RETRY_V1" in text
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
        "HomeScreen SID": text.count(
            "RProcess().SecureId().iId == 0x102750F0u"
        ) == (4 if menubar_extended else 3 if action_factory_extended else 2),
        "exact external interface": text.count(
            "aInterfaceUid.iUid == 0x200286DFu"
        ) == 1,
        "shared predicate": (
            text.count("htcleoMatrixMenuList || htcleoHomeScreenExternalList")
            == (2 if rendering_extended else 1)
            and text.count("if(htcleoUiShellList)") == 2
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
        ),
        "one bounded reconnect": (
            text.count("TRAPD(htcleoListReconnectResult, ConstructL())") == 1
            and text.count("error = SendReceive(aServiceId,aArgs)") == 1
        ),
        "natural empty-list fallback": (
            text.count("error = KEComErrNoInterfaceIdentified") == 1
            and text.count("0x0000031Au") == 1
        ),
        "no delay": "User::After" not in SCOPE_NEW,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom HomeScreen list retry verification failed: " + ", ".join(failed)
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
        "HTCLEO_ECOM_HOMESCREEN_LIST_RETRY="
        "sid-102750f0-interface-200286df-one-reconnect-then-empty"
    )


if __name__ == "__main__":
    main()
