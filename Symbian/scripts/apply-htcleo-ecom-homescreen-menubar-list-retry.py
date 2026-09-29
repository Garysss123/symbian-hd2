#!/usr/bin/env python3
"""Retry the first real HomeScreen visual factory without masking failure.

Hardware 712 crosses the finite non-layout metadata set, then the stock QHD
View.xml order reaches ``menubar``.  Its real xn3menufactory registration and
DLL are present in ROM, but the resolved-list IPC returns
KErrServerTerminated.  Reuse the existing one-reconnect path for only this
SID/interface/type tuple.  Unlike metadata nodes, a second failure remains
fatal so no visual control is fabricated or silently omitted.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1"
PREREQUISITE = "HTCLEO_ECOM_HOMESCREEN_NONVISUAL_LIST_RETRY_V1"

OLD_SCOPE = '''\tconst TBool htcleoUiShellList =
\t\thtcleoMatrixMenuList || htcleoHomeScreenExternalList ||
\t\thtcleoHomeScreenNonvisualFactoryList;
'''

NEW_SCOPE = '''\t// HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1
\tconst TBool htcleoHomeScreenMenubarFactoryList =
\t\t(RProcess().SecureId().iId == 0x102750F0u &&
\t\t aInterfaceUid.iUid == 0x20019592u &&
\t\t htcleoHomeScreenResolverType.Compare(_L8("menubar")) == 0);
\tconst TBool htcleoUiShellList =
\t\thtcleoMatrixMenuList || htcleoHomeScreenExternalList ||
\t\thtcleoHomeScreenNonvisualFactoryList ||
\t\thtcleoHomeScreenMenubarFactoryList;
\tconst TBool htcleoUiShellListFailOpen =
\t\t!htcleoHomeScreenMenubarFactoryList && htcleoUiShellList;
'''

OLD_NORMALIZE = '''\tif(htcleoUiShellList && error == KErrServerTerminated)
\t\t{
\t\t// ListImplementationsL already defines no implementation as a valid
'''

NEW_NORMALIZE = '''\tif(htcleoUiShellListFailOpen && error == KErrServerTerminated)
\t\t{
\t\t// ListImplementationsL already defines no implementation as a valid
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("menubar retry requires nonvisual-list recovery")
    if text.count(OLD_SCOPE) != 1:
        raise SystemExit("HomeScreen menubar retry scope anchor mismatch")
    if text.count(OLD_NORMALIZE) != 1:
        raise SystemExit("HomeScreen menubar normalization anchor mismatch")
    text = text.replace(OLD_SCOPE, NEW_SCOPE, 1)
    return text.replace(OLD_NORMALIZE, NEW_NORMALIZE, 1)


def verify(text: str) -> None:
    rendering_extended = (
        "HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY_V1" in text
    )
    if rendering_extended:
        exact_factory_scope = (
            text.count("const TBool htcleoHomeScreenRenderingFactoryList") == 1
            and text.count(
                'htcleoHomeScreenResolverType.Compare(_L8("menubar")) == 0'
            ) == 0
        )
        visual_failure_retained = (
            text.count("htcleoHomeScreenNonvisualFactoryList;") == 1
            and "!htcleoHomeScreenMenubarFactoryList" not in text
        )
    else:
        exact_factory_scope = (
            text.count("const TBool htcleoHomeScreenMenubarFactoryList") == 1
            and text.count(
                'htcleoHomeScreenResolverType.Compare(_L8("menubar")) == 0'
            ) == 1
        )
        visual_failure_retained = text.count(
            "!htcleoHomeScreenMenubarFactoryList && htcleoUiShellList"
        ) == 1
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "exact menubar tuple": (
            exact_factory_scope
            and text.count("aInterfaceUid.iUid == 0x20019592u") == 2
            and text.count("RProcess().SecureId().iId == 0x102750F0u") == 4
        ),
        "one reconnect path": (
            text.count("if(htcleoUiShellList && error == KErrServerTerminated)")
            == 1
            and text.count("TRAPD(htcleoListReconnectResult, ConstructL())") == 1
        ),
        "visual failure retained": (
            text.count(
                "if(htcleoUiShellListFailOpen && "
                "error == KErrServerTerminated)"
            ) == 1
            and visual_failure_retained
            and text.count("error = KEComErrNoInterfaceIdentified;") == 1
        ),
        "other visual types excluded": all(
            token not in NEW_SCOPE
            for token in ('_L8("text")', '_L8("image")', '_L8("view")')
        ),
        "no timing or display": all(
            token not in NEW_SCOPE + NEW_NORMALIZE
            for token in ("User::After", "RTimer", "HalFunction")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom HomeScreen menubar retry verification failed: "
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
        "HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY="
        "sid-102750f0-interface-20019592-type-menubar-one-reconnect-failclosed"
    )


if __name__ == "__main__":
    main()
