#!/usr/bin/env python3
"""Trace the first real HomeScreen view node/control construction failure."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XN_ODT_VIEW_LOAD_TRACE_V1"


HELPER = r'''
// HTCLEO_XN_ODT_VIEW_LOAD_TRACE_V1
static TUint32 HtcleoXnNodeTag(const TDesC8& aName)
    {
    TUint32 tag = 0;
    const TInt count = Min(aName.Length(), 4);
    for (TInt i = 0; i < count; ++i)
        {
        tag = (tag << 8) | (TUint8)aName[i];
        }
    return tag;
    }

'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER not in text:
        text = replace_once(
            text,
            "template<class T>\nstatic void CleanupResetAndDestroy( TAny* aObj )",
            HELPER + "template<class T>\nstatic void CleanupResetAndDestroy( TAny* aObj )",
            "tag helper",
        )

    if "0x48581570u" not in text:
        text = replace_once(
            text,
            "static CXnNode* ConstructNodeFromPluginL(\n"
            "    CXnEcomHandler& aEcomHandler,\n"
            "    CXnDomNode& aSource )\n"
            "    {\n"
            "    CXnNode* returnValue = NULL;\n"
            "    const TDesC8& name = aSource.Name();",
            "static CXnNode* ConstructNodeFromPluginL(\n"
            "    CXnEcomHandler& aEcomHandler,\n"
            "    CXnDomNode& aSource )\n"
            "    {\n"
            "    CXnNode* returnValue = NULL;\n"
            "    const TDesC8& name = aSource.Name();\n"
            "    HtcleoXnLoadUiLog(0x48581570u, KErrNone,\n"
            "        HtcleoXnNodeTag(name));",
            "plugin node entry",
        )
        text = replace_once(
            text,
            "    TUid interfaceUid = { AI3_RENDERING_PLUGIN_ECOM_FACTORY_UID };\n"
            "    aEcomHandler.PluginsL( interfaceUid, name, *componentFactories );\n"
            "    TInt count = componentFactories->Container().Count();",
            "    TUid interfaceUid = { AI3_RENDERING_PLUGIN_ECOM_FACTORY_UID };\n"
            "    HtcleoXnLoadUiLog(0x48581571u, KErrNone,\n"
            "        (TUint32)interfaceUid.iUid);\n"
            "    aEcomHandler.PluginsL( interfaceUid, name, *componentFactories );\n"
            "    TInt count = componentFactories->Container().Count();\n"
            "    HtcleoXnLoadUiLog(0x48581572u, count,\n"
            "        HtcleoXnNodeTag(name));",
            "render factory discovery",
        )
        text = replace_once(
            text,
            "        MXnComponentFactory* factory = static_cast< MXnComponentFactory* >(\n"
            "            componentFactories->Container()[i] );\n"
            "        componentNodeImplNeeded = factory->DoesNodeNeedComponentImplL( name );",
            "        MXnComponentFactory* factory = static_cast< MXnComponentFactory* >(\n"
            "            componentFactories->Container()[i] );\n"
            "        HtcleoXnLoadUiLog(0x48581573u, i, (TUint32)factory);\n"
            "        componentNodeImplNeeded = factory->DoesNodeNeedComponentImplL( name );\n"
            "        HtcleoXnLoadUiLog(0x48581574u,\n"
            "            (TInt)componentNodeImplNeeded, HtcleoXnNodeTag(name));",
            "factory predicate",
        )
        text = replace_once(
            text,
            "    CleanupStack::PopAndDestroy( componentFactories );\n"
            "    if ( componentNodeImplNeeded )",
            "    CleanupStack::PopAndDestroy( componentFactories );\n"
            "    HtcleoXnLoadUiLog(0x48581575u,\n"
            "        (TInt)componentNodeImplNeeded, HtcleoXnNodeTag(name));\n"
            "    if ( componentNodeImplNeeded )",
            "factory decision",
        )
        text = replace_once(
            text,
            "    return returnValue;\n"
            "    }\n\n"
            "// -----------------------------------------------------------------------------\n"
            "// ConstructKnownBuiltinNodeL",
            "    HtcleoXnLoadUiLog(0x48581576u, KErrNone,\n"
            "        (TUint32)returnValue);\n"
            "    return returnValue;\n"
            "    }\n\n"
            "// -----------------------------------------------------------------------------\n"
            "// ConstructKnownBuiltinNodeL",
            "plugin node return",
        )

    if "0x48581580u" not in text:
        text = replace_once(
            text,
            "    const TDesC8& name( aSource.Name() );",
            "    const TDesC8& name( aSource.Name() );\n"
            "    HtcleoXnLoadUiLog(0x48581580u,\n"
            "        aSource.ChildNodes().Length(), HtcleoXnNodeTag(name));",
            "construct node entry",
        )
        text = replace_once(
            text,
            "    CXnNode* node( ConstructKnownBuiltinNodeL( aSource ) ); \n\n"
            "    if ( !node )",
            "    CXnNode* node( ConstructKnownBuiltinNodeL( aSource ) );\n"
            "    HtcleoXnLoadUiLog(0x48581581u, KErrNone, (TUint32)node);\n\n"
            "    if ( !node )",
            "builtin node result",
        )
        text = replace_once(
            text,
            "        node = ConstructNodeFromPluginL( iEcomHandler, aSource );\n"
            "        \n"
            "        if ( !node )",
            "        HtcleoXnLoadUiLog(0x48581582u, KErrNone,\n"
            "            HtcleoXnNodeTag(name));\n"
            "        node = ConstructNodeFromPluginL( iEcomHandler, aSource );\n"
            "        HtcleoXnLoadUiLog(0x48581583u, KErrNone, (TUint32)node);\n"
            "        \n"
            "        if ( !node )",
            "plugin node result",
        )
        text = replace_once(
            text,
            "            node = ConstructGeneralNodeL( aSource );\n"
            "            \n"
            "            if ( !node )",
            "            node = ConstructGeneralNodeL( aSource );\n"
            "            HtcleoXnLoadUiLog(0x48581584u, KErrNone,\n"
            "                (TUint32)node);\n"
            "            \n"
            "            if ( !node )",
            "general node result",
        )
        text = replace_once(
            text,
            "    CXnNode* parent( FindAncestorWhoActAsParent( aSource ) );\n\n"
            "    if( !parent )",
            "    CXnNode* parent( FindAncestorWhoActAsParent( aSource ) );\n"
            "    HtcleoXnLoadUiLog(0x48581585u, KErrNone, (TUint32)parent);\n\n"
            "    if( !parent )",
            "layout parent result",
        )
        text = replace_once(
            text,
            "    parent->AddChildL( node );\n\n"
            "    if ( !parent->IsLayoutCapable() )",
            "    parent->AddChildL( node );\n"
            "    HtcleoXnLoadUiLog(0x48581586u, KErrNone, (TUint32)node);\n\n"
            "    if ( !parent->IsLayoutCapable() )",
            "add layout child",
        )
        text = replace_once(
            text,
            "    CopyPropertiesFromDomNodeToNodeL( *node, aSource, aSp );\n"
            "           \n"
            "    if ( name == KTriggerNodeName )",
            "    CopyPropertiesFromDomNodeToNodeL( *node, aSource, aSp );\n"
            "    HtcleoXnLoadUiLog(0x48581587u, KErrNone,\n"
            "        HtcleoXnNodeTag(name));\n"
            "           \n"
            "    if ( name == KTriggerNodeName )",
            "property copy",
        )
        text = replace_once(
            text,
            "        aPluginData.SetInitialFocusNodeL( node );\n"
            "        }\n"
            "    }\n\n"
            "// -----------------------------------------------------------------------------\n"
            "// CXnODTParser::CreateControlsL()",
            "        aPluginData.SetInitialFocusNodeL( node );\n"
            "        }\n"
            "    HtcleoXnLoadUiLog(0x48581588u, KErrNone,\n"
            "        HtcleoXnNodeTag(name));\n"
            "    }\n\n"
            "// -----------------------------------------------------------------------------\n"
            "// CXnODTParser::CreateControlsL()",
            "construct node return",
        )

    if "0x48581590u" not in text:
        text = replace_once(
            text,
            "void CXnODTParser::LoadViewL( CXnViewData& aViewData )\n"
            "    {    \n"
            "    // <view> element\n"
            "    CXnDomNode* view( aViewData.Node() );",
            "void CXnODTParser::LoadViewL( CXnViewData& aViewData )\n"
            "    {\n"
            "    HtcleoXnLoadUiLog(0x48581590u, KErrNone,\n"
            "        (TUint32)aViewData.Occupied());\n"
            "    // <view> element\n"
            "    CXnDomNode* view( aViewData.Node() );",
            "load view entry",
        )
        text = replace_once(
            text,
            "    // from <view> element\n"
            "    CreateNodesL( view, *sp, aViewData );       \n"
            "    CreateControlsL( view, aViewData );",
            "    // from <view> element\n"
            "    HtcleoXnLoadUiLog(0x48581591u, KErrNone,\n"
            "        view ? HtcleoXnNodeTag(view->Name()) : 0u);\n"
            "    CreateNodesL( view, *sp, aViewData );\n"
            "    HtcleoXnLoadUiLog(0x48581592u, KErrNone, 0u);\n"
            "    HtcleoXnLoadUiLog(0x48581593u, KErrNone, 0u);\n"
            "    CreateControlsL( view, aViewData );\n"
            "    HtcleoXnLoadUiLog(0x48581594u, KErrNone, 0u);",
            "view node and control phases",
        )
        text = replace_once(
            text,
            "    // By default make controls invisible\n"
            "    CXnControlAdapter* adapter( view->LayoutNode()->Control() );",
            "    // By default make controls invisible\n"
            "    HtcleoXnLoadUiLog(0x48581595u, KErrNone,\n"
            "        (TUint32)view->LayoutNode());\n"
            "    CXnControlAdapter* adapter( view->LayoutNode()->Control() );\n"
            "    HtcleoXnLoadUiLog(0x48581596u, KErrNone,\n"
            "        (TUint32)adapter);",
            "view control adapter",
        )
        text = replace_once(
            text,
            "        adapter->MakeVisible( EFalse );\n"
            "        }    \n"
            "        \n"
            "    aViewData.SetOccupied();",
            "        adapter->MakeVisible( EFalse );\n"
            "        HtcleoXnLoadUiLog(0x48581597u, KErrNone, 0u);\n"
            "        }\n"
            "        \n"
            "    aViewData.SetOccupied();\n"
            "    HtcleoXnLoadUiLog(0x48581598u, KErrNone, 1u);",
            "view occupied",
        )

    if "0x485815A0u" not in text:
        text = replace_once(
            text,
            "    if( !aNode )\n"
            "        {\n"
            "        return;\n"
            "        }\n"
            "    \n"
            "    CXnComponentNodeImpl* impl( aNode->ComponentNodeImpl() );",
            "    if( !aNode )\n"
            "        {\n"
            "        return;\n"
            "        }\n"
            "    HtcleoXnLoadUiLog(0x485815A0u, KErrNone,\n"
            "        HtcleoXnNodeTag(aNode->Type()->Type()));\n"
            "    \n"
            "    CXnComponentNodeImpl* impl( aNode->ComponentNodeImpl() );",
            "construct control entry",
        )
        text = replace_once(
            text,
            "    const TDesC8& name( aNode->Type()->Type() );\n\n"
            "    if ( needsCreation )",
            "    const TDesC8& name( aNode->Type()->Type() );\n"
            "    HtcleoXnLoadUiLog(0x485815A1u, (TInt)needsCreation,\n"
            "        HtcleoXnNodeTag(name));\n\n"
            "    if ( needsCreation )",
            "control creation decision",
        )
        text = replace_once(
            text,
            "        // Try if builtin control can be created\n"
            "        if ( !CreateBuiltInControlL( *aNode, name ) )\n"
            "            {\n"
            "            // Not builtin, invoke factory chain\n"
            "            CreateFactoryControlL( *aNode, name );\n"
            "            }\n\n"
            "        // Fill plugin data\n"
            "        aPluginData.SetControlL( aNode );",
            "        // Try if builtin control can be created\n"
            "        HtcleoXnLoadUiLog(0x485815A2u, KErrNone,\n"
            "            HtcleoXnNodeTag(name));\n"
            "        TBool htcleoBuiltIn = CreateBuiltInControlL( *aNode, name );\n"
            "        HtcleoXnLoadUiLog(0x485815A3u, (TInt)htcleoBuiltIn,\n"
            "            HtcleoXnNodeTag(name));\n"
            "        if ( !htcleoBuiltIn )\n"
            "            {\n"
            "            // Not builtin, invoke factory chain\n"
            "            HtcleoXnLoadUiLog(0x485815A4u, KErrNone,\n"
            "                HtcleoXnNodeTag(name));\n"
            "            CreateFactoryControlL( *aNode, name );\n"
            "            HtcleoXnLoadUiLog(0x485815A5u, KErrNone,\n"
            "                HtcleoXnNodeTag(name));\n"
            "            }\n\n"
            "        // Fill plugin data\n"
            "        aPluginData.SetControlL( aNode );\n"
            "        HtcleoXnLoadUiLog(0x485815A6u, KErrNone,\n"
            "            HtcleoXnNodeTag(name));",
            "control factory boundary",
        )
        text = replace_once(
            text,
            "        aPluginData.SetContentSourceNodeL( aNode );\n"
            "        }\n"
            "    }\n\n"
            "// -----------------------------------------------------------------------------\n"
            "// CXnODTParser::CreateExternalControlL()",
            "        aPluginData.SetContentSourceNodeL( aNode );\n"
            "        }\n"
            "    HtcleoXnLoadUiLog(0x485815A7u, KErrNone,\n"
            "        HtcleoXnNodeTag(name));\n"
            "    }\n\n"
            "// -----------------------------------------------------------------------------\n"
            "// CXnODTParser::CreateExternalControlL()",
            "construct control return",
        )
    return text


def verify(text: str) -> None:
    stages = list(range(0x70, 0x77)) + list(range(0x80, 0x89))
    stages += list(range(0x90, 0x99)) + list(range(0xA0, 0xA8))
    checks = {
        "marker": text.count(MARKER) == 1,
        "tag helper": text.count("static TUint32 HtcleoXnNodeTag") == 1,
        "stages": all(text.count(f"0x485815{stage:02X}u") == 1 for stage in stages),
        "real compose path": text.count("CreateNodesL( view, *sp, aViewData )") == 1,
        "real controls path": text.count("CreateControlsL( view, aViewData )") == 1,
        "real discovery": text.count("aEcomHandler.PluginsL( interfaceUid, name, *componentFactories )") == 1,
        "real factory": text.count("CreateFactoryControlL( *aNode, name )") == 1,
        "no delay or normalization": all(
            token not in text for token in ("User::After", "RTimer", "KErrServerTerminated )\n        err = KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Xn ODT view trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/app/homescreen/idlehomescreen/xmluirendering/"
        "uiengine/src/xnodtparser.cpp"
    )
    text = install(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_XN_ODT_VIEW_LOAD_TRACE="
        "HSXML-1570-15A7-node-ecom-control-boundaries"
    )


if __name__ == "__main__":
    main()
