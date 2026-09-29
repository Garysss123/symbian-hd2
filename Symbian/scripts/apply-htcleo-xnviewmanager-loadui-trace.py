#!/usr/bin/env python3
"""Trace the real HomeScreen LoadUi root/view composition path."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XN_LOADUI_TRACE_V1"


LOGGER = r'''

#include <e32base.h>
#include <f32file.h>

// HTCLEO_XN_LOADUI_TRACE_V1
static void HtcleoXnLoadUiLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x102750f0u)
        return;
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;
    _LIT(KDir, "C:\\Symbian3\\");
    _LIT(KPath, "C:\\Symbian3\\HSXML.TXT");
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
        _LIT8(KPrefix, "HTCLEO_HLD  ");
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


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def add_logger(text: str, anchor: str, label: str) -> str:
    if MARKER in text:
        include_anchor = "\n// HTCLEO_XN_LOADUI_TRACE_V1\n"
        include_block = (
            "\n#include <e32base.h>\n"
            "#include <f32file.h>\n\n"
            "// HTCLEO_XN_LOADUI_TRACE_V1\n"
        )
        if include_block not in text:
            text = replace_once(
                text, include_anchor, include_block, label + " includes"
            )
        return text
    return replace_once(text, anchor, anchor + LOGGER, label)


def install_manager(text: str) -> str:
    text = add_logger(text, '#include <startupdomainpskeys.h>\n', "manager logger")
    if "0x48581500u" in text:
        return text
    text = replace_once(
        text,
        "void CXnViewManager::LoadUiL()\n"
        "    {\n"
        "    iUiEngine->DisableRenderUiLC();",
        "void CXnViewManager::LoadUiL()\n"
        "    {\n"
        "    HtcleoXnLoadUiLog(0x48581500u, KErrNone,\n"
        "        (TUint32)iApplicationUid.iUid);\n"
        "    iUiEngine->DisableRenderUiLC();\n"
        "    HtcleoXnLoadUiLog(0x48581501u, KErrNone, 0u);",
        "LoadUi entry",
    )
    text = replace_once(
        text,
        "    // Load application root configuration\n"
        "    iRootData = CXnRootData::NewL( *this, iApplicationUid );",
        "    // Load application root configuration\n"
        "    HtcleoXnLoadUiLog(0x48581502u, KErrNone, 0u);\n"
        "    iRootData = CXnRootData::NewL( *this, iApplicationUid );\n"
        "    HtcleoXnLoadUiLog(0x48581503u, KErrNone,\n"
        "        (TUint32)iRootData);",
        "root allocation",
    )
    text = replace_once(
        text,
        "    // Load root configuration and initial view.\n"
        "    TInt err = iRootData->Load();",
        "    // Load root configuration and initial view.\n"
        "    HtcleoXnLoadUiLog(0x48581504u, KErrNone, 0u);\n"
        "    TInt err = iRootData->Load();\n"
        "    HtcleoXnLoadUiLog(0x48581505u, err,\n"
        "        (TUint32)iRootData->PluginData().Count());",
        "root load",
    )
    text = replace_once(
        text,
        "    if( err == EXnInvalidConfiguration )\n"
        "        {\n"
        "        // Configuration loading failed totally\n"
        "        Panic( EXnInvalidConfiguration );",
        "    if( err == EXnInvalidConfiguration )\n"
        "        {\n"
        "        // Configuration loading failed totally\n"
        "        HtcleoXnLoadUiLog(0x48581506u, err, 0u);\n"
        "        Panic( EXnInvalidConfiguration );",
        "invalid configuration",
    )
    text = replace_once(
        text,
        "    if( iRootData->PluginData().Count() == 1 )\n"
        "        {        \n"
        "        HandleErrorNotes( err );\n"
        "        }",
        "    if( iRootData->PluginData().Count() == 1 )\n"
        "        {\n"
        "        HtcleoXnLoadUiLog(0x48581507u, err, 0u);\n"
        "        HandleErrorNotes( err );\n"
        "        HtcleoXnLoadUiLog(0x48581508u, err, 0u);\n"
        "        }",
        "error note",
    )
    text = replace_once(
        text,
        "    CleanupStack::PopAndDestroy(); // DisableRenderUiLC();\n"
        "    \n"
        "    // Load initial view publishers    \n"
        "    ActiveViewData().SetActive( ETrue );",
        "    HtcleoXnLoadUiLog(0x48581509u, KErrNone, 0u);\n"
        "    CleanupStack::PopAndDestroy(); // DisableRenderUiLC();\n"
        "    HtcleoXnLoadUiLog(0x4858150Au, KErrNone, 0u);\n"
        "    \n"
        "    // Load initial view publishers\n"
        "    HtcleoXnLoadUiLog(0x4858150Bu, KErrNone, 0u);\n"
        "    ActiveViewData().SetActive( ETrue );\n"
        "    HtcleoXnLoadUiLog(0x4858150Cu, KErrNone, 0u);",
        "LoadUi completion",
    )
    return text


def install_root(text: str) -> str:
    text = add_logger(text, '#include "xnviewmanager.h"\n', "root logger")
    if "0x48581510u" in text:
        return text
    text = replace_once(
        text,
        "void CXnRootData::ConstructL()\n"
        "    {   \n"
        "    CXnPluginData::ConstructL();",
        "void CXnRootData::ConstructL()\n"
        "    {\n"
        "    HtcleoXnLoadUiLog(0x48581510u, KErrNone,\n"
        "        (TUint32)iApplicationUid.iUid);\n"
        "    CXnPluginData::ConstructL();\n"
        "    HtcleoXnLoadUiLog(0x48581511u, KErrNone, 0u);",
        "root ConstructL entry",
    )
    text = replace_once(
        text,
        "    iEcomHandler = CXnEcomHandler::NewL();\n"
        "    \n"
        "    iParser = CXnODTParser::NewL( iManager, *iEcomHandler );   \n"
        "    \n"
        "    iLoadTimer = CPeriodic::NewL( CActive::EPriorityLow );           \n"
        "    iDestroyTimer = CPeriodic::NewL( CActive::EPriorityLow );",
        "    iEcomHandler = CXnEcomHandler::NewL();\n"
        "    HtcleoXnLoadUiLog(0x48581512u, KErrNone,\n"
        "        (TUint32)iEcomHandler);\n"
        "    \n"
        "    iParser = CXnODTParser::NewL( iManager, *iEcomHandler );\n"
        "    HtcleoXnLoadUiLog(0x48581513u, KErrNone, (TUint32)iParser);\n"
        "    \n"
        "    iLoadTimer = CPeriodic::NewL( CActive::EPriorityLow );\n"
        "    HtcleoXnLoadUiLog(0x48581514u, KErrNone,\n"
        "        (TUint32)iLoadTimer);\n"
        "    iDestroyTimer = CPeriodic::NewL( CActive::EPriorityLow );\n"
        "    HtcleoXnLoadUiLog(0x48581515u, KErrNone,\n"
        "        (TUint32)iDestroyTimer);",
        "root construction",
    )
    text = replace_once(
        text,
        "TInt CXnRootData::Load()\n"
        "    { \n"
        "    if ( Occupied() )",
        "TInt CXnRootData::Load()\n"
        "    {\n"
        "    HtcleoXnLoadUiLog(0x48581520u, KErrNone,\n"
        "        (TUint32)Occupied());\n"
        "    if ( Occupied() )",
        "root Load entry",
    )
    text = replace_once(
        text,
        "    // Load application root configuration\n"
        "    TRAP( err, iODT = iManager.Composer().ComposeRootL( *this ) );",
        "    // Load application root configuration\n"
        "    HtcleoXnLoadUiLog(0x48581521u, KErrNone, 0u);\n"
        "    TRAP( err, iODT = iManager.Composer().ComposeRootL( *this ) );\n"
        "    HtcleoXnLoadUiLog(0x48581522u, err, (TUint32)iODT);",
        "compose root",
    )
    text = replace_once(
        text,
        "        // Can't recover\n"
        "        return EXnInvalidConfiguration;",
        "        // Can't recover\n"
        "        HtcleoXnLoadUiLog(0x48581523u, EXnInvalidConfiguration, 0u);\n"
        "        return EXnInvalidConfiguration;",
        "null root",
    )
    text = replace_once(
        text,
        "        TRAP( err, iManager.Parser().LoadRootL( *this, iApplicationUid ) );",
        "        HtcleoXnLoadUiLog(0x48581524u, KErrNone,\n"
        "            (TUint32)iPluginsData.Count());\n"
        "        TRAP( err, iManager.Parser().LoadRootL( *this, iApplicationUid ) );\n"
        "        HtcleoXnLoadUiLog(0x48581525u, err,\n"
        "            (TUint32)iPluginsData.Count());",
        "load root nodes",
    )
    text = replace_once(
        text,
        "            if ( plugin->Initial() )\n"
        "                {\n"
        "                err = plugin->Load();",
        "            HtcleoXnLoadUiLog(0x48581526u, i,\n"
        "                (TUint32)plugin->Initial());\n"
        "            if ( plugin->Initial() )\n"
        "                {\n"
        "                HtcleoXnLoadUiLog(0x48581527u, KErrNone,\n"
        "                    (TUint32)i);\n"
        "                err = plugin->Load();\n"
        "                HtcleoXnLoadUiLog(0x48581528u, err,\n"
        "                    (TUint32)plugin->Occupied());",
        "initial view load",
    )
    text = replace_once(
        text,
        "                    // Rest of the views will be loaded asynchronously by the RunLoadL()\n"
        "                    return err;",
        "                    // Rest of the views will be loaded asynchronously by the RunLoadL()\n"
        "                    HtcleoXnLoadUiLog(0x48581529u, err,\n"
        "                        (TUint32)i);\n"
        "                    return err;",
        "initial view return",
    )
    text = replace_once(
        text,
        "        // Initial view loading failed, fallback to load any of the views\n"
        "        while( iPluginsData.Count() )",
        "        // Initial view loading failed, fallback to load any of the views\n"
        "        HtcleoXnLoadUiLog(0x4858152Au, err,\n"
        "            (TUint32)iPluginsData.Count());\n"
        "        while( iPluginsData.Count() )",
        "fallback entry",
    )
    text = replace_once(
        text,
        "            // Ignore error\n"
        "            plugin->Load();\n"
        "                            \n"
        "            if ( plugin->Occupied() )",
        "            // Ignore error\n"
        "            HtcleoXnLoadUiLog(0x4858152Bu, KErrNone,\n"
        "                (TUint32)iPluginsData.Count());\n"
        "            TInt htcleoFallbackError = plugin->Load();\n"
        "            HtcleoXnLoadUiLog(0x4858152Cu, htcleoFallbackError,\n"
        "                (TUint32)plugin->Occupied());\n"
        "                            \n"
        "            if ( plugin->Occupied() )",
        "fallback load",
    )
    return replace_once(
        text,
        "                // Return error because of fallback condition\n"
        "                return KXnErrViewPluginFailure;",
        "                // Return error because of fallback condition\n"
        "                HtcleoXnLoadUiLog(0x4858152Du,\n"
        "                    KXnErrViewPluginFailure, 0u);\n"
        "                return KXnErrViewPluginFailure;",
        "fallback return",
    )


def install_composer(text: str) -> str:
    text = add_logger(text, '#include <s32file.h>\n', "composer logger")
    if "0x48581530u" in text:
        return text
    text = replace_once(
        text,
        "CXnODT* CXnComposer::ComposeRootL( CXnRootData& aRootData )\n"
        "    {\n"
        "    // Not owned",
        "CXnODT* CXnComposer::ComposeRootL( CXnRootData& aRootData )\n"
        "    {\n"
        "    HtcleoXnLoadUiLog(0x48581530u, KErrNone, 0u);\n"
        "    // Not owned",
        "composer entry",
    )
    text = replace_once(
        text,
        "    // Get application configuration\n"
        "    CHspsConfiguration* configuration( iWrapper.GetAppConfigurationL() );",
        "    // Get application configuration\n"
        "    HtcleoXnLoadUiLog(0x48581531u, KErrNone, 0u);\n"
        "    CHspsConfiguration* configuration( iWrapper.GetAppConfigurationL() );\n"
        "    HtcleoXnLoadUiLog(0x48581532u, KErrNone,\n"
        "        (TUint32)configuration);",
        "get app configuration",
    )
    text = replace_once(
        text,
        "    const TDesC8& state( configuration->PluginInfo().ConfigurationState() );\n"
        "    \n"
        "    aRootData.SetConfigurationIdL( configuration->ConfId() );",
        "    const TDesC8& state( configuration->PluginInfo().ConfigurationState() );\n"
        "    HtcleoXnLoadUiLog(0x48581533u,\n"
        "        configuration->Resources().Count(), (TUint32)state.Length());\n"
        "    \n"
        "    aRootData.SetConfigurationIdL( configuration->ConfId() );",
        "configuration state",
    )
    text = replace_once(
        text,
        "    aRootData.SetConfigurationIdL( configuration->ConfId() );",
        "    aRootData.SetConfigurationIdL( configuration->ConfId() );\n"
        "    HtcleoXnLoadUiLog(0x48581534u, KErrNone,\n"
        "        (TUint32)configuration->ConfId().Length());",
        "configuration id",
    )
    text = replace_once(
        text,
        "    // Get application configuration odt resource\n"
        "    CXnODT* odt = CXnODT::NewL();",
        "    // Get application configuration odt resource\n"
        "    HtcleoXnLoadUiLog(0x48581535u, KErrNone, 0u);\n"
        "    CXnODT* odt = CXnODT::NewL();\n"
        "    HtcleoXnLoadUiLog(0x48581536u, KErrNone, (TUint32)odt);",
        "ODT allocation",
    )
    text = replace_once(
        text,
        "    const CObjectMap* resourceObject = FindObject( \n"
        "            configuration->Resources(), KTagXuikon() );",
        "    const CObjectMap* resourceObject = FindObject(\n"
        "            configuration->Resources(), KTagXuikon() );\n"
        "    HtcleoXnLoadUiLog(0x48581537u, KErrNone,\n"
        "        (TUint32)resourceObject);",
        "root resource",
    )
    text = replace_once(
        text,
        "    CXnDomNode* root( GetOdtL( *resourceObject, aRootData ) );",
        "    HtcleoXnLoadUiLog(0x48581538u, KErrNone, 0u);\n"
        "    CXnDomNode* root( GetOdtL( *resourceObject, aRootData ) );\n"
        "    HtcleoXnLoadUiLog(0x48581539u, KErrNone, (TUint32)root);",
        "root ODT",
    )
    text = replace_once(
        text,
        "    CXnDomNode* views( FindNodeByName( root, KViews ) );",
        "    CXnDomNode* views( FindNodeByName( root, KViews ) );\n"
        "    HtcleoXnLoadUiLog(0x4858153Au, KErrNone, (TUint32)views);",
        "views node",
    )
    text = replace_once(
        text,
        "    RPointerArray< CPluginMap >& plugins( configuration->PluginMaps() );\n"
        "\n"
        "    if ( ( plugins.Count() == 0 ) || ( aRootData.MaxPages() <= 0 ) )",
        "    RPointerArray< CPluginMap >& plugins( configuration->PluginMaps() );\n"
        "    HtcleoXnLoadUiLog(0x4858153Bu, plugins.Count(),\n"
        "        (TUint32)aRootData.MaxPages());\n"
        "\n"
        "    if ( ( plugins.Count() == 0 ) || ( aRootData.MaxPages() <= 0 ) )",
        "view map count",
    )
    text = replace_once(
        text,
        "        CPluginMap* plugin( plugins[i] );\n"
        "        \n"
        "        CXnViewData* view = CXnViewData::NewLC( aRootData );",
        "        CPluginMap* plugin( plugins[i] );\n"
        "        HtcleoXnLoadUiLog(0x4858153Cu, i,\n"
        "            (TUint32)plugin);\n"
        "        \n"
        "        CXnViewData* view = CXnViewData::NewLC( aRootData );\n"
        "        HtcleoXnLoadUiLog(0x4858153Du, i, (TUint32)view);",
        "view allocation",
    )
    return replace_once(
        text,
        "    // Ownership is granted to the caller\n"
        "    return odt;",
        "    // Ownership is granted to the caller\n"
        "    HtcleoXnLoadUiLog(0x4858153Eu, index, (TUint32)odt);\n"
        "    return odt;",
        "composer return",
    )


def install_parser(text: str) -> str:
    text = add_logger(text, '#include <aisystemuids.hrh>\n', "ODT parser logger")
    if "0x48581550u" in text:
        return text
    text = replace_once(
        text,
        "void CXnODTParser::LoadRootL( CXnRootData& aRootData, TUid /*aAppUid*/ )        \n"
        "    {    \n"
        "    CXnDomNode* root( aRootData.Owner() );",
        "void CXnODTParser::LoadRootL( CXnRootData& aRootData, TUid /*aAppUid*/ )\n"
        "    {\n"
        "    CXnDomNode* root( aRootData.Owner() );\n"
        "    HtcleoXnLoadUiLog(0x48581550u, KErrNone, (TUint32)root);",
        "LoadRoot entry",
    )
    text = replace_once(
        text,
        "    // Build root\n"
        "    CXnNode* node( BuildRootNodeL( iUiEngine ) );",
        "    // Build root\n"
        "    HtcleoXnLoadUiLog(0x48581551u, KErrNone, 0u);\n"
        "    CXnNode* node( BuildRootNodeL( iUiEngine ) );\n"
        "    HtcleoXnLoadUiLog(0x48581552u, KErrNone, (TUint32)node);",
        "build root node",
    )
    text = replace_once(
        text,
        "    CreateNodesL( root, *sp, aRootData );\n\n"
        "    // root doesn't have any controls   \n"
        "    \n"
        "    aRootData.SetOccupied();",
        "    HtcleoXnLoadUiLog(0x48581553u, KErrNone, 0u);\n"
        "    CreateNodesL( root, *sp, aRootData );\n"
        "    HtcleoXnLoadUiLog(0x48581554u, KErrNone, 0u);\n\n"
        "    // root doesn't have any controls\n"
        "    \n"
        "    aRootData.SetOccupied();\n"
        "    HtcleoXnLoadUiLog(0x48581555u, KErrNone, 1u);",
        "create root nodes",
    )
    return text


def install_view(text: str) -> str:
    text = add_logger(text, '#include <babitflags.h>\n', "view logger")
    if "0x48581560u" in text:
        return text
    text = replace_once(
        text,
        "TInt CXnViewData::Load()\n"
        "    {\n"
        "    TInt err( KErrNone );",
        "TInt CXnViewData::Load()\n"
        "    {\n"
        "    TInt err( KErrNone );\n"
        "    HtcleoXnLoadUiLog(0x48581560u, KErrNone,\n"
        "        (TUint32)Occupied());",
        "view Load entry",
    )
    text = replace_once(
        text,
        "        TRAP( err, err = iManager.Composer().ComposeViewL( *this ) );\n"
        "    \n"
        "        if ( err == KErrNone )",
        "        HtcleoXnLoadUiLog(0x48581561u, KErrNone, 0u);\n"
        "        TRAP( err, err = iManager.Composer().ComposeViewL( *this ) );\n"
        "        HtcleoXnLoadUiLog(0x48581562u, err,\n"
        "            (TUint32)iPluginsData.Count());\n"
        "    \n"
        "        if ( err == KErrNone )",
        "compose view",
    )
    text = replace_once(
        text,
        "            TRAP( err, iManager.Parser().LoadViewL( *this ) );",
        "            HtcleoXnLoadUiLog(0x48581563u, KErrNone, 0u);\n"
        "            TRAP( err, iManager.Parser().LoadViewL( *this ) );\n"
        "            HtcleoXnLoadUiLog(0x48581564u, err,\n"
        "                (TUint32)iPluginsData.Count());",
        "load view nodes",
    )
    text = replace_once(
        text,
        "                    TInt err2( iPluginsData[i]->Load() );",
        "                    HtcleoXnLoadUiLog(0x48581565u, i, 0u);\n"
        "                    TInt err2( iPluginsData[i]->Load() );\n"
        "                    HtcleoXnLoadUiLog(0x48581566u, err2,\n"
        "                        (TUint32)i);",
        "widget load",
    )
    return replace_once(
        text,
        "    iLoadError = err;\n"
        "                \n"
        "    return iLoadError;",
        "    iLoadError = err;\n"
        "    HtcleoXnLoadUiLog(0x48581567u, iLoadError,\n"
        "        (TUint32)Occupied());\n"
        "                \n"
        "    return iLoadError;",
        "view Load return",
    )


def verify(path: Path, text: str, stages: range) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "path": text.count(r"C:\\Symbian3\\HSXML.TXT") == 1,
        "capacity": text.count("1048576 - 128") == 1,
        "stages": all(text.count(f"0x485815{stage:02X}u") == 1 for stage in stages),
        "no behavior shim": all(
            token not in text for token in ("User::After", "RTimer", "KErrNone; // HTCLEO")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(f"{path.name} LoadUi trace verification failed: {', '.join(failed)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    src = (
        args.root
        / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src"
    )
    jobs = (
        ("xnviewmanager.cpp", install_manager, range(0x00, 0x0D)),
        ("xnrootdata.cpp", install_root,
         tuple(range(0x10, 0x16)) + tuple(range(0x20, 0x2E))),
        ("xncomposer.cpp", install_composer, range(0x30, 0x3F)),
        ("xnodtparser.cpp", install_parser, range(0x50, 0x56)),
        ("xnviewdata.cpp", install_view, range(0x60, 0x68)),
    )
    for name, installer, stages in jobs:
        path = src / name
        text = installer(path.read_text(encoding="utf-8"))
        verify(path, text, stages)
        path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_XNVIEWMANAGER_LOADUI_TRACE="
        "HSXML-1m-48581500-0c-10-15-20-2d-30-3e-50-55-60-67"
    )


if __name__ == "__main__":
    main()
