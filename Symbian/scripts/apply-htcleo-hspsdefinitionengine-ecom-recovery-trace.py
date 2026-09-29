#!/usr/bin/env python3
"""Recover and trace HSPS definition-engine XML parser ECom construction."""

from __future__ import annotations

import argparse
from pathlib import Path


ENGINE_MARKER = "HTCLEO_HSPS_DEFINITION_ECOM_RECOVERY_TRACE_V1"
XML_MARKER = "HTCLEO_HSPS_XML_HANDLER_TRACE_V1"


LOGGER = r'''

// HTCLEO_HSPS_DEFINITION_ECOM_RECOVERY_TRACE_V1
static void HtcleoHspsDefinitionLog(TUint32 aStage, TInt aResult,
                                    TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;
    _LIT(KDir, "C:\\Symbian3\\");
    _LIT(KPath, "C:\\Symbian3\\HSDEF.TXT");
    (void)fs.MkDirAll(KDir);
    RFile file;
    r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
    TInt position = 0;
    if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);
    if (r == KErrNone && position <= (1048576 - 128))
        {
        _LIT8(KPrefix, "HTCLEO_HDEF ");
        TBuf8<128> record;
        record.Append(KPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
        record.Append('\n');
        (void)file.Write(record);
        }
    file.Close();
    fs.Close();
    }

'''


XML_LOGGER = LOGGER.replace(ENGINE_MARKER, XML_MARKER)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install_engine(text: str) -> str:
    if ENGINE_MARKER in text:
        return text
    text = replace_once(
        text,
        '#include    <f32file.h>\n',
        '#include    <f32file.h>\n#include    <ecom/ecom.h>\n' + LOGGER,
        "engine logger include",
    )
    text = replace_once(
        text,
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
        "    HtcleoHspsDefinitionLog(0x485814E0u, KErrNone,\n"
        "        (TUint32)ahspsOdt.ThemeUid());\n"
        "    if ( !ihspsXMLHandler )\n"
        "        {\n"
        "        HtcleoHspsDefinitionLog(0x485814E1u, KErrNone,\n"
        "            (TUint32)aXMLFileName.Length());\n"
        "        TRAPD( parserInitError,\n"
        "            ihspsXMLHandler = ChspsXMLHandler::NewL() );\n"
        "        HtcleoHspsDefinitionLog(0x485814E2u, parserInitError,\n"
        "            (TUint32)ihspsXMLHandler);\n"
        "        if ( parserInitError == KErrServerTerminated )\n"
        "            {\n"
        "            REComSession::FinalClose();\n"
        "            HtcleoHspsDefinitionLog(0x485814E3u, parserInitError, 0u);\n"
        "            TRAP(parserInitError,\n"
        "                ihspsXMLHandler = ChspsXMLHandler::NewL() );\n"
        "            HtcleoHspsDefinitionLog(0x485814E4u, parserInitError,\n"
        "                (TUint32)ihspsXMLHandler);\n"
        "            }\n"
        "        if ( parserInitError != KErrNone )\n"
        "            {\n"
        "            errCode.iDefEngError = KErrXmlParsing;\n"
        "            errCode.iSubComponentError = parserInitError;\n"
        "            HtcleoHspsDefinitionLog(0x485814E5u, parserInitError,\n"
        "                (TUint32)errCode.iDefEngError);\n"
        "            return errCode;\n"
        "            }\n"
        "        }\n"
        "\n"
        "    HtcleoHspsDefinitionLog(0x485814E6u, KErrNone,\n"
        "        (TUint32)aXMLFileName.Length());\n"
        "    TRAPD( err,ihspsXMLHandler->ParseXmlDocL( aFsSession, aXMLFileName, dom ) );\n"
        "    HtcleoHspsDefinitionLog(0x485814E7u, err,\n"
        "        (TUint32)dom.DomNodeCount());",
        "parser construction and parse",
    )
    text = replace_once(
        text,
        "        errCode.iDefEngError = KErrXmlParsing;\n"
        "        errCode.iSubComponentError = err;\n"
        "        return errCode;\n"
        "        }\n"
        "        \n"
        "    TRAP( err, BuildRefNodesL( dom ) );",
        "        errCode.iDefEngError = KErrXmlParsing;\n"
        "        errCode.iSubComponentError = err;\n"
        "        HtcleoHspsDefinitionLog(0x485814E8u, err,\n"
        "            (TUint32)errCode.iDefEngError);\n"
        "        return errCode;\n"
        "        }\n"
        "\n"
        "    HtcleoHspsDefinitionLog(0x485814E9u, KErrNone,\n"
        "        (TUint32)dom.DomNodeCount());\n"
        "    TRAP( err, BuildRefNodesL( dom ) );\n"
        "    HtcleoHspsDefinitionLog(0x485814EAu, err,\n"
        "        (TUint32)dom.DomNodeCount());",
        "ref-node trace",
    )
    return replace_once(
        text,
        "    return errCode;\n\n"
        "    }\n\n"
        "// -----------------------------------------------------------------------------\n"
        "// ChspsDefinitionEngine::ApplyLanguageL",
        "    HtcleoHspsDefinitionLog(0x485814EBu, KErrNone,\n"
        "        (TUint32)dom.DomNodeCount());\n"
        "    return errCode;\n\n"
        "    }\n\n"
        "// -----------------------------------------------------------------------------\n"
        "// ChspsDefinitionEngine::ApplyLanguageL",
        "CreateDOM success",
    )


def install_xml(text: str) -> str:
    if XML_MARKER in text:
        return text
    text = replace_once(
        text,
        '#include    <parserfeature.h>\n',
        '#include    <parserfeature.h>\n#include    <f32file.h>\n' + XML_LOGGER,
        "XML logger include",
    )
    text = replace_once(
        text,
        "void ChspsXMLHandler::ConstructL()\n"
        "    {\n"
        "    MContentHandler* contentHandler = this;",
        "void ChspsXMLHandler::ConstructL()\n"
        "    {\n"
        "    HtcleoHspsDefinitionLog(0x485814F0u, KErrNone, 0u);\n"
        "    MContentHandler* contentHandler = this;",
        "XML construct entry",
    )
    text = replace_once(
        text,
        "    CMatchData* matchData = CMatchData::NewL();\n"
        "    CleanupStack::PushL(matchData);\n"
        "    matchData->SetMimeTypeL(KXmlMimeType);\n"
        "    matchData->SetVariantL(KVariant);\n\n"
        "    iXmlParser = Xml::CParser::NewL( *matchData, *contentHandler );\n"
        "    iXmlParser->EnableFeature( EReplaceIntEntityFromExtSubsetByRef );\n"
        "    iNodeStack = new (ELeave)RPointerArray<ChspsDomNode>;\n"
        "    CleanupStack::PopAndDestroy(matchData);",
        "    CMatchData* matchData = CMatchData::NewL();\n"
        "    HtcleoHspsDefinitionLog(0x485814F1u, KErrNone,\n"
        "        (TUint32)matchData);\n"
        "    CleanupStack::PushL(matchData);\n"
        "    matchData->SetMimeTypeL(KXmlMimeType);\n"
        "    HtcleoHspsDefinitionLog(0x485814F2u, KErrNone,\n"
        "        (TUint32)KXmlMimeType().Length());\n"
        "    matchData->SetVariantL(KVariant);\n"
        "    HtcleoHspsDefinitionLog(0x485814F3u, KErrNone,\n"
        "        (TUint32)KVariant().Length());\n\n"
        "    HtcleoHspsDefinitionLog(0x485814F4u, KErrNone, 0u);\n"
        "    iXmlParser = Xml::CParser::NewL( *matchData, *contentHandler );\n"
        "    HtcleoHspsDefinitionLog(0x485814F5u, KErrNone,\n"
        "        (TUint32)iXmlParser);\n"
        "    TInt htcleoFeatureResult =\n"
        "        iXmlParser->EnableFeature( EReplaceIntEntityFromExtSubsetByRef );\n"
        "    HtcleoHspsDefinitionLog(0x485814F6u, htcleoFeatureResult, 0u);\n"
        "    iNodeStack = new (ELeave)RPointerArray<ChspsDomNode>;\n"
        "    HtcleoHspsDefinitionLog(0x485814F7u, KErrNone,\n"
        "        (TUint32)iNodeStack);\n"
        "    CleanupStack::PopAndDestroy(matchData);",
        "XML parser construction",
    )
    return replace_once(
        text,
        "    iError = KErrNone;\n"
        "    iDomDocument = &aDomDocument;\n"
        "    Xml::ParseL(*iXmlParser, aFsSession, aFileName );\n"
        "    User::LeaveIfError( iError );",
        "    HtcleoHspsDefinitionLog(0x485814F8u, KErrNone,\n"
        "        (TUint32)aFileName.Length());\n"
        "    iError = KErrNone;\n"
        "    iDomDocument = &aDomDocument;\n"
        "    HtcleoHspsDefinitionLog(0x485814F9u, KErrNone,\n"
        "        (TUint32)iXmlParser);\n"
        "    Xml::ParseL(*iXmlParser, aFsSession, aFileName );\n"
        "    HtcleoHspsDefinitionLog(0x485814FAu, iError,\n"
        "        (TUint32)aDomDocument.DomNodeCount());\n"
        "    User::LeaveIfError( iError );\n"
        "    HtcleoHspsDefinitionLog(0x485814FBu, KErrNone,\n"
        "        (TUint32)aDomDocument.DomNodeCount());",
        "XML parse trace",
    )


def verify_engine(text: str) -> None:
    stages = range(0xE0, 0xEC)
    closed_by_rom = "HTCLEO_HSPS_LIBXML2_ROM_CLOSURE_V1" in text
    checks = {
        "marker": text.count(ENGINE_MARKER) == 1,
        "stages": all(text.count(f"0x485814{stage:02X}u") == 1 for stage in stages),
        "one bounded retry": (
            text.count("parserInitError == KErrServerTerminated") == 1
            and text.count("REComSession::FinalClose();") == (0 if closed_by_rom else 1)
            and text.count("ihspsXMLHandler = ChspsXMLHandler::NewL()")
            == (1 if closed_by_rom else 2)
        ),
        "real parse": text.count("ihspsXMLHandler->ParseXmlDocL") == 1,
        "real refs": text.count("BuildRefNodesL( dom )") == 1,
        "capacity": text.count("1048576 - 128") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS definition recovery verification failed: " + ", ".join(failed))


def verify_xml(text: str) -> None:
    stages = range(0xF0, 0xFC)
    checks = {
        "marker": text.count(XML_MARKER) == 1,
        "stages": all(text.count(f"0x485814{stage:02X}u") == 1 for stage in stages),
        "real parser": text.count("iXmlParser = Xml::CParser::NewL") == 1,
        "real parse": text.count("Xml::ParseL(*iXmlParser, aFsSession, aFileName )") == 1,
        "capacity": text.count("1048576 - 128") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS XML trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = (
        args.root
        / "sf/mw/homescreensrv/homescreenpluginsrv/hspsdefinitionengine"
        / "hspsdefinitionengine/src"
    )
    engine_path = base / "hspsdefinitionengine.cpp"
    engine = install_engine(engine_path.read_text(encoding="utf-8"))
    verify_engine(engine)
    engine_path.write_text(engine, encoding="utf-8")
    xml_path = base / "hspsxmlhandler.cpp"
    xml = install_xml(xml_path.read_text(encoding="utf-8"))
    verify_xml(xml)
    xml_path.write_text(xml, encoding="utf-8")
    print(
        "HTCLEO_HSPS_DEFINITION_ENGINE_ECOM_RECOVERY="
        "parser-newl-serverterminated-finalclose-retry-once"
    )
    print(
        "HTCLEO_HSPS_DEFINITION_ENGINE_TRACE="
        "HSDEF-1m-485814e0-eb-f0-fb"
    )


if __name__ == "__main__":
    main()
