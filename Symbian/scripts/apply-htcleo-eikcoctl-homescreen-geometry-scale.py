#!/usr/bin/env python3
"""Apply MatrixMenu's proven 360x640-to-480x800 chrome contract to HomeScreen.

This deliberately does not set HomeScreen's ApplicationRect to 480x800.  It
extends the already hardware-proven final ClientRect, StatusPane and CBA
screen-space mappings, including the real CBA redraw that keeps the softkey
pane above CPU-composited content.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE_V1"
CLIENT_PREREQUISITE = "HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V2"
STATUS_PREREQUISITE = "HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_SCALE_V1"
CBA_PREREQUISITES = (
    "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V2",
    "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_BOUNDING_SCALE_V1",
    "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_SIZE_SCALE_V1",
)
WRAPPER_PREREQUISITE = "HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V3"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_client(text: str) -> str:
    if text.count(CLIENT_PREREQUISITE) != 1:
        raise SystemExit("MatrixMenu client-rect prerequisite is missing")
    return replace_once(
        text,
        "    // HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V2\n"
        "    // Keep the stock Laf reductions, then map the resulting Nokia 360x640\n"
        "    // logical rectangle onto the physical HTC Leo 480x800 panel.\n"
        "    if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n",
        "    // HTCLEO_EIKCOCTL_MATRIXMENU_CLIENTRECT_SCALE_V2\n"
        f"    // {MARKER}\n"
        "    // Keep the stock Laf reductions, then map the resulting Nokia 360x640\n"
        "    // logical rectangle onto the physical HTC Leo 480x800 panel.\n"
        "    const TUint32 htcleoGeometrySid = RProcess().SecureId().iId;\n"
        "    if ( ( htcleoGeometrySid == 0x101F4CD2u ||\n"
        "           htcleoGeometrySid == 0x102750F0u ) &&\n",
        "client-rect SID scope",
    )


def install_status(text: str) -> str:
    if text.count(STATUS_PREREQUISITE) != 1:
        raise SystemExit("MatrixMenu status-pane prerequisite is missing")
    return replace_once(
        text,
        "            // HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_SCALE_V1\n"
        "            TRect htcleoPaneRect( aNode->Rect() );\n"
        "            if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n",
        "            // HTCLEO_EIKCOCTL_MATRIXMENU_STATUSPANE_SCALE_V1\n"
        f"            // {MARKER}\n"
        "            TRect htcleoPaneRect( aNode->Rect() );\n"
        "            const TUint32 htcleoPaneSid = RProcess().SecureId().iId;\n"
        "            if ( ( htcleoPaneSid == 0x101F4CD2u ||\n"
        "                   htcleoPaneSid == 0x102750F0u ) &&\n",
        "status-pane SID scope",
    )


def install_cba(text: str) -> str:
    for prerequisite in CBA_PREREQUISITES:
        if text.count(prerequisite) != 1:
            raise SystemExit(f"CBA prerequisite is missing: {prerequisite}")
    text = replace_once(
        text,
        "        // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V2\n"
        "        // The CPU fallback has no z-composition.  If the full MatrixMenu grid\n"
        "        // was drawn after this real CBA, force the existing inner control to\n"
        "        // take its normal DrawNow path even though it is already visible.\n"
        "        const TBool htcleoMatrixMenuCba =\n"
        "            RProcess().SecureId().iId == 0x101F4CD2u;\n",
        "        // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_INNER_REDRAW_V2\n"
        f"        // {MARKER}\n"
        "        // The CPU fallback has no z-composition.  Keep the existing real CBA\n"
        "        // above either scaled shell without inventing controls or pixels.\n"
        "        const TUint32 htcleoCbaSid = RProcess().SecureId().iId;\n"
        "        const TBool htcleoMatrixMenuCba =\n"
        "            htcleoCbaSid == 0x101F4CD2u ||\n"
        "            htcleoCbaSid == 0x102750F0u;\n",
        "inner CBA redraw SID scope",
    )
    old_guard = "        if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n"
    new_bounding_guard = (
        "        const TUint32 htcleoCbaBoundingSid =\n"
        "            RProcess().SecureId().iId;\n"
        "        if ( ( htcleoCbaBoundingSid == 0x101F4CD2u ||\n"
        "               htcleoCbaBoundingSid == 0x102750F0u ) &&\n"
    )
    text = replace_once(
        text, old_guard, new_bounding_guard, "CBA bounding SID scope"
    )
    new_size_guard = (
        "    const TUint32 htcleoCbaSizeSid = RProcess().SecureId().iId;\n"
        "    if ( ( htcleoCbaSizeSid == 0x101F4CD2u ||\n"
        "           htcleoCbaSizeSid == 0x102750F0u ) &&\n"
    )
    text = replace_once(
        text,
        "    if ( RProcess().SecureId().iId == 0x101F4CD2u &&\n",
        new_size_guard,
        "CBA size SID scope",
    )
    return text


def install_wrapper(text: str) -> str:
    if text.count(WRAPPER_PREREQUISITE) != 1:
        raise SystemExit("MatrixMenu CBA wrapper prerequisite is missing")
    return replace_once(
        text,
        "    // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V3\n"
        "    if ( aVisible &&\n"
        "         RProcess().SecureId().iId == 0x101F4CD2u )\n",
        "    // HTCLEO_EIKCOCTL_MATRIXMENU_CBA_WRAPPER_REDRAW_V3\n"
        f"    // {MARKER}\n"
        "    const TUint32 htcleoCbaWrapperSid = RProcess().SecureId().iId;\n"
        "    if ( aVisible &&\n"
        "         ( htcleoCbaWrapperSid == 0x101F4CD2u ||\n"
        "           htcleoCbaWrapperSid == 0x102750F0u ) )\n",
        "CBA wrapper SID scope",
    )


def verify(client: str, status: str, cba: str, wrapper: str) -> None:
    checks = {
        "markers": all(
            source.count(MARKER) == 1
            for source in (client, status, cba, wrapper)
        ),
        "client SIDs": (
            client.count("htcleoGeometrySid == 0x101F4CD2u") == 1
            and client.count("htcleoGeometrySid == 0x102750F0u") == 1
        ),
        "status SIDs": (
            status.count("htcleoPaneSid == 0x101F4CD2u") == 1
            and status.count("htcleoPaneSid == 0x102750F0u") == 1
        ),
        "CBA SIDs": (
            cba.count("== 0x101F4CD2u") >= 3
            and cba.count("== 0x102750F0u") == 3
        ),
        "wrapper SIDs": (
            wrapper.count("htcleoCbaWrapperSid == 0x101F4CD2u") == 1
            and wrapper.count("htcleoCbaWrapperSid == 0x102750F0u") == 1
        ),
        "scale constants retained": (
            client.count("* 480") == 2
            and client.count("* 800") == 2
            and status.count("* 480") >= 2
            and status.count("* 800") >= 2
            and cba.count("* 480") >= 4
            and cba.count("* 800") >= 4
        ),
        "real CBA redraw retained": (
            wrapper.count("htcleoRealButtonGroup->DrawDeferred();") == 1
            and wrapper.count(
                "htcleoRealButtonGroup->DrawNow(htcleoRedrawRect);"
            ) == 1
        ),
        "no ApplicationRect override": (
            "iApplicationRect" not in client + status + cba + wrapper
            and "TSize(480, 800)" not in client + status + cba + wrapper
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen geometry-scale audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/classicui/uifw/EikStd/coctlsrc"
    client_path = base / "EIKCOLIB.CPP"
    status_path = base / "eikspane.cpp"
    cba_path = base / "eikcba.cpp"
    wrapper_path = base / "EIKBTGPC.CPP"
    for path in (client_path, status_path, cba_path, wrapper_path):
        if not path.is_file():
            raise SystemExit(f"missing EikStd source: {path}")
    client = client_path.read_text(encoding="latin-1")
    status = status_path.read_text(encoding="latin-1")
    cba = cba_path.read_text(encoding="latin-1")
    wrapper = wrapper_path.read_text(encoding="latin-1")
    if MARKER not in client:
        client = install_client(client)
    if MARKER not in status:
        status = install_status(status)
    if MARKER not in cba:
        cba = install_cba(cba)
    if MARKER not in wrapper:
        wrapper = install_wrapper(wrapper)
    verify(client, status, cba, wrapper)
    client_path.write_text(client, encoding="latin-1")
    status_path.write_text(status, encoding="latin-1")
    cba_path.write_text(cba, encoding="latin-1")
    wrapper_path.write_text(wrapper, encoding="latin-1")
    print(
        "HTCLEO_EIKCOCTL_HOMESCREEN_GEOMETRY_SCALE="
        "matrix-contract-client-status-cba-360x640-to-480x800"
    )


if __name__ == "__main__":
    main()
