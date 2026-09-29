#!/usr/bin/env python3
"""Avoid invalid AknSrv fade IPC during UI-first status-pane bring-up.

Iteration 521 proves combined pane/control/count are valid and stops between
B705 and B706 at IsFaded().  On the HTCLEO MatrixMenu fail-open AknSrv path the
session handle is zero, so querying server fade state cannot succeed.  Hardware
687 proves HomeScreen reaches the identical IsFaded() boundary.  Treat only
MatrixMenu/HomeScreen with an invalid session as not faded; every valid session
and every other SID retains stock IsFaded() behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_FADE_FAILCLOSED_V1"
HOME_MARKER = "HTCLEO_EIKCOCTL_HOMESCREEN_FADE_FAILCLOSED_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    return replace_once(
        source,
        "        TBool isFaded( IsFaded() );\n"
        "        HtcleoStatusPaneLog(0x0000B706u, KErrNone,",
        "        // " + MARKER + "\n"
        "        TBool isFaded( EFalse );\n"
        "        RAknUiServer* htcleoAknSrv = CAknSgcClient::AknSrv();\n"
        "        if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n"
        "             ( !htcleoAknSrv || htcleoAknSrv->Handle() == 0 ) )\n"
        "            {\n"
        "            HtcleoStatusPaneLog(0x0000B70Eu, KErrNotSupported,\n"
        "                0x46414445u); // FADE\n"
        "            }\n"
        "        else\n"
        "            {\n"
        "            isFaded = IsFaded();\n"
        "            }\n"
        "        HtcleoStatusPaneLog(0x0000B70Fu, KErrNone,\n"
        "            (TUint32)isFaded);\n"
        "        HtcleoStatusPaneLog(0x0000B706u, KErrNone,",
        "MatrixMenu invalid AknSrv fade guard",
    )


def install_homescreen_scope(source: str) -> str:
    return replace_once(
        source,
        "        if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n"
        "             ( !htcleoAknSrv || htcleoAknSrv->Handle() == 0 ) )",
        "        // " + HOME_MARKER + "\n"
        "        const TUint32 htcleoFadeSid = RProcess().SecureId().iId;\n"
        "        const TBool htcleoFadeUiFirst =\n"
        "            ( htcleoFadeSid == 0x101F4CD2u ||\n"
        "              htcleoFadeSid == 0x102750F0u );\n"
        "        if ( htcleoFadeUiFirst &&\n"
        "             ( !htcleoAknSrv || htcleoAknSrv->Handle() == 0 ) )",
        "HomeScreen invalid AknSrv fade guard",
    )


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "HomeScreen marker": source.count(HOME_MARKER) == 1,
        "narrow UI-first SIDs": (
            source.count("htcleoFadeSid == 0x101F4CD2u") == 1
            and source.count("htcleoFadeSid == 0x102750F0u") == 1
            and source.count("const TBool htcleoFadeUiFirst") == 1
        ),
        "handle guard": source.count("htcleoAknSrv->Handle() == 0") == 1,
        "stock fade retained": source.count("isFaded = IsFaded();") == 1,
        "false default": source.count("TBool isFaded( EFalse );") == 1,
        "policy stage": source.count("0x0000B70Eu") == 1,
        "return stage": source.count("0x0000B70Fu") == 1,
        "combined flow retained": source.count(
            "subPane->SetParentWindowL( NULL,"
        )
        == 1,
        "no timer": "User::After" not in MARKER,
        "no display": "HalFunction" not in MARKER,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu fade fail-closed verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    path = args.root / "sf/mw/classicui/uifw/EikStd/coctlsrc/eikspane.cpp"
    source = path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    if HOME_MARKER not in source:
        source = install_homescreen_scope(source)
    verify(source)
    if source != path.read_text(encoding="latin-1"):
        path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCOCTL_MATRIXMENU_FADE_FAILCLOSED=installed "
        "condition=matrixmenu-or-homescreen-and-aknsrv-handle-zero "
        "result=not-faded valid-session=stock"
    )


if __name__ == "__main__":
    main()
