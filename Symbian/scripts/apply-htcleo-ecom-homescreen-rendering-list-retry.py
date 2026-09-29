#!/usr/bin/env python3
"""Generalize the proven menubar reconnect to HomeScreen rendering lists.

Hardware 713 proves an exact menubar resolved-list request succeeds after one
ECom reconnect.  Apply that recovery to every HomeScreen request for the same
rendering-factory interface so later real text/image/view factories do not each
require a separate iteration.  Empty-list normalization stays limited to the
older MatrixMenu/external/nonvisual scopes; every visual failure remains fatal.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY_V1"
PREREQUISITE = "HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1"

OLD = '''\t// HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1
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

NEW = '''\t// HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1
\t// HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY_V1
\tconst TBool htcleoHomeScreenRenderingFactoryList =
\t\t(RProcess().SecureId().iId == 0x102750F0u &&
\t\t aInterfaceUid.iUid == 0x20019592u);
\tconst TBool htcleoUiShellList =
\t\thtcleoMatrixMenuList || htcleoHomeScreenExternalList ||
\t\thtcleoHomeScreenRenderingFactoryList;
\tconst TBool htcleoUiShellListFailOpen =
\t\thtcleoMatrixMenuList || htcleoHomeScreenExternalList ||
\t\thtcleoHomeScreenNonvisualFactoryList;
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("rendering retry requires proven menubar retry")
    if text.count(OLD) != 1:
        raise SystemExit("HomeScreen rendering retry scope anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "all rendering tuple": (
            text.count("const TBool htcleoHomeScreenRenderingFactoryList") == 1
            and text.count("aInterfaceUid.iUid == 0x20019592u") == 2
            and text.count("RProcess().SecureId().iId == 0x102750F0u") == 4
        ),
        "one reconnect": (
            text.count("if(htcleoUiShellList && error == KErrServerTerminated)")
            == 1
            and text.count("TRAPD(htcleoListReconnectResult, ConstructL())") == 1
        ),
        "visual failure retained": (
            text.count(
                "if(htcleoUiShellListFailOpen && "
                "error == KErrServerTerminated)"
            ) == 1
            and text.count(
                "htcleoMatrixMenuList || htcleoHomeScreenExternalList ||\n"
                "\t\thtcleoHomeScreenNonvisualFactoryList;"
            ) == 1
            and "!htcleoHomeScreenMenubarFactoryList" not in text
        ),
        "no type fabrication": all(
            token not in NEW
            for token in ('_L8("text")', '_L8("image")', '_L8("view")')
        ),
        "no timing or display": all(
            token not in NEW for token in ("User::After", "RTimer", "HalFunction")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom HomeScreen rendering retry verification failed: "
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
        "HTCLEO_ECOM_HOMESCREEN_RENDERING_LIST_RETRY="
        "sid-102750f0-interface-20019592-all-types-one-reconnect-visual-failclosed"
    )


if __name__ == "__main__":
    main()
