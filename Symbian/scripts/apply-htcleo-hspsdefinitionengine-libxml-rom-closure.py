#!/usr/bin/env python3
"""Retire unsafe FinalClose retry once the real libxml SAX plugin is in ROM."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPS_LIBXML2_ROM_CLOSURE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    return replace_once(
        text,
        "        if ( parserInitError == KErrServerTerminated )\n"
        "            {\n"
        "            REComSession::FinalClose();\n"
        "            HtcleoHspsDefinitionLog(0x485814E3u, parserInitError, 0u);\n"
        "            TRAP(parserInitError,\n"
        "                ihspsXMLHandler = ChspsXMLHandler::NewL() );\n"
        "            HtcleoHspsDefinitionLog(0x485814E4u, parserInitError,\n"
        "                (TUint32)ihspsXMLHandler);\n"
        "            }",
        "        // HTCLEO_HSPS_LIBXML2_ROM_CLOSURE_V1\n"
        "        // The stock libxml2 SAX DLL/resource/SPI now exist in ROM.\n"
        "        // Do not FinalClose the ECom session of this live plugin.\n"
        "        if ( parserInitError == KErrServerTerminated )\n"
        "            {\n"
        "            HtcleoHspsDefinitionLog(0x485814E3u, parserInitError, 0u);\n"
        "            }\n"
        "        HtcleoHspsDefinitionLog(0x485814E4u, parserInitError,\n"
        "            (TUint32)ihspsXMLHandler);",
        "unsafe ECom retry",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "single parser construction": (
            text.count("ihspsXMLHandler = ChspsXMLHandler::NewL()") == 1
        ),
        "no FinalClose": text.count("REComSession::FinalClose();") == 0,
        "real parse retained": text.count("ihspsXMLHandler->ParseXmlDocL") == 1,
        "structured failure retained": (
            text.count("errCode.iSubComponentError = parserInitError") == 1
        ),
        "trace retained": all(
            text.count(f"0x485814{stage:02X}u") == 1
            for stage in range(0xE0, 0xEC)
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS libxml ROM closure verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/homescreenpluginsrv/hspsdefinitionengine"
        / "hspsdefinitionengine/src/hspsdefinitionengine.cpp"
    )
    text = install(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_HSPS_LIBXML2_ROM_CLOSURE="
        "stock-dll-resource-spi-impl-101f9783-no-finalclose"
    )


if __name__ == "__main__":
    main()
