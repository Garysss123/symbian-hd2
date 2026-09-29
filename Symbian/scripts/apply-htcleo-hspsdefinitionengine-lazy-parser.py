#!/usr/bin/env python3
"""Defer the nested XML ECom parser until after the outer plugin factory."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPS_DEFINITION_ENGINE_LAZY_PARSER_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "ChspsDefinitionEngine::ChspsDefinitionEngine()\n"
        "    {\n"
        "    }",
        "ChspsDefinitionEngine::ChspsDefinitionEngine()\n"
        "    : ihspsXMLHandler( NULL )\n"
        "    {\n"
        "    }",
        "constructor state",
    )
    text = replace_once(
        text,
        "void ChspsDefinitionEngine::ConstructL()\n"
        "    {\n"
        "    ihspsXMLHandler = ChspsXMLHandler::NewL();\n"
        "    }",
        "void ChspsDefinitionEngine::ConstructL()\n"
        "    {\n"
        "    // HTCLEO_HSPS_DEFINITION_ENGINE_LAZY_PARSER_V1\n"
        "    // CParser::NewL uses ECom.  Construct it after this outer ECom\n"
        "    // plugin factory has returned, avoiding nested LoadManager state.\n"
        "    }",
        "factory deferral",
    )
    return replace_once(
        text,
        "    errCode.iDefEngError = KErrNone;\n"
        "    errCode.iSubComponentError = KErrNone;\n"
        "    \n"
        "    TRAPD( err,ihspsXMLHandler->ParseXmlDocL( aFsSession, aXMLFileName, dom ) );",
        "    errCode.iDefEngError = KErrNone;\n"
        "    errCode.iSubComponentError = KErrNone;\n"
        "\n"
        "    if ( !ihspsXMLHandler )\n"
        "        {\n"
        "        TRAPD( parserInitError,\n"
        "            ihspsXMLHandler = ChspsXMLHandler::NewL() );\n"
        "        if ( parserInitError != KErrNone )\n"
        "            {\n"
        "            errCode.iDefEngError = KErrXmlParsing;\n"
        "            errCode.iSubComponentError = parserInitError;\n"
        "            return errCode;\n"
        "            }\n"
        "        }\n"
        "    \n"
        "    TRAPD( err,ihspsXMLHandler->ParseXmlDocL( aFsSession, aXMLFileName, dom ) );",
        "lazy parser construction",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "null initialized": text.count(": ihspsXMLHandler( NULL )") == 1,
        "factory no nested parser": (
            text.count("ihspsXMLHandler = ChspsXMLHandler::NewL()")
            == (
                1
                if "HTCLEO_HSPS_LIBXML2_ROM_CLOSURE_V1" in text
                else (
                    2
                    if "HTCLEO_HSPS_DEFINITION_ECOM_RECOVERY_TRACE_V1" in text
                    else 1
                )
            )
            and text.index("ihspsXMLHandler = ChspsXMLHandler::NewL()")
            > text.index("ChspsDefinitionEngine::CreateDOM(")
        ),
        "lazy error preserved": (
            text.count("TRAPD( parserInitError,") == 1
            and text.count("errCode.iSubComponentError = parserInitError") == 1
            and text.count("errCode.iDefEngError = KErrXmlParsing") == 2
        ),
        "real parse retained": text.count("ihspsXMLHandler->ParseXmlDocL") == 1,
        "no delay or fabricated parser": all(
            token not in text for token in ("User::After", "RTimer", "reinterpret_cast<ChspsXMLHandler")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS lazy-parser verification failed: " + ", ".join(failed))


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
        "HTCLEO_HSPS_DEFINITION_ENGINE_PARSER="
        "lazy-after-outer-ecom-factory-real-parser-retained"
    )


if __name__ == "__main__":
    main()
