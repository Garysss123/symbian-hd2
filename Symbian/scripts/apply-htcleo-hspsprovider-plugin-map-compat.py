#!/usr/bin/env python3
"""Use the schema-owned HSPS plug-in list and trace its LIW handoff."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPSPROVIDER_PLUGIN_MAP_COMPAT_V1"


LOGGER = r'''

// HTCLEO_HSPSPROVIDER_PLUGIN_MAP_COMPAT_V1
static void HtcleoHspsProviderLog(TUint32 aStage, TInt aResult,
                                  TUint32 aDetail)
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
        _LIT8(KPrefix, "HTCLEO_HPRV ");
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


REPLACEMENT = r'''TInt CHspsLiwUtilities::AppendPluginsFlatL( ChspsDomNode& aConfigurationNode,
                         CLiwDefaultMap& aMap )
    {
    TInt err = KErrNone;
    CLiwDefaultList* list = CLiwDefaultList::NewL();
    CleanupStack::PushL( list );

    // The expanded application ODT contains nested configuration/control/
    // plugins trees.  Select the list owned directly by this configuration
    // instead of accepting the first same-named node from a depth walk.
    ChspsDomNode* controlNode = static_cast<ChspsDomNode*>(
        aConfigurationNode.ChildNodes().FindByName( KControlElement ) );
    HtcleoHspsProviderLog(0x48581610u,
        controlNode ? KErrNone : KErrNotFound,
        (TUint32)aConfigurationNode.ChildNodes().Length());

    ChspsDomNode* pluginsNode = NULL;
    if ( controlNode )
        {
        pluginsNode = static_cast<ChspsDomNode*>(
            controlNode->ChildNodes().FindByName( KPluginsElement ) );
        }
    HtcleoHspsProviderLog(0x48581611u,
        pluginsNode ? KErrNone : KErrNotFound,
        controlNode ? (TUint32)controlNode->ChildNodes().Length() : 0u);

    TInt length = 0;
    if ( pluginsNode )
        {
        ChspsDomList& children = pluginsNode->ChildNodes();
        length = children.Length();
        HtcleoHspsProviderLog(0x48581612u, KErrNone, (TUint32)length);
        for ( TInt i = 0; i < length; i++ )
            {
            ChspsDomNode* plugin =
                static_cast<ChspsDomNode*>( children.Item( i ) );
            HtcleoHspsProviderLog(0x48581613u, i,
                plugin ? (TUint32)plugin->AttributeList().Length() : 0u);
            if ( !plugin )
                {
                continue;
                }
            CLiwDefaultMap* map = CLiwDefaultMap::NewL();
            CleanupStack::PushL( map );

            TInt pluginMapItems = (
                CHspsLiwUtilities::EPluginMapId +
                CHspsLiwUtilities::EPluginMapUid +
                CHspsLiwUtilities::EPluginMapActivationState +
                CHspsLiwUtilities::EPluginMapLocked );
            BuildPluginMapL( *plugin, *map, pluginMapItems );

            TLiwVariant mapVariant;
            mapVariant.Set( map );
            list->AppendL( mapVariant );

            CleanupStack::Pop( map );
            map->DecRef();
            }
        }
    else
        {
        HtcleoHspsProviderLog(0x48581612u, KErrNotFound, 0u);
        }

    HtcleoHspsProviderLog(0x48581614u, list->Count(),
        (TUint32)length);
    TLiwVariant listVariant;
    listVariant.Set( list );
    aMap.InsertL( KHspsLiwPlugins, listVariant );
    HtcleoHspsProviderLog(0x48581615u, KErrNone,
        (TUint32)list->Count());

    CleanupStack::Pop( list );
    list->DecRef();
    return err;
    }
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install_source(text: str) -> str:
    if MARKER not in text:
        text = replace_once(
            text,
            "#include <s32mem.h>\n",
            "#include <s32mem.h>\n#include <f32file.h>\n",
            "file-server include",
        )
        text = replace_once(
            text,
            '_LIT8( KMaxChildDefault, "6" );\n',
            '_LIT8( KMaxChildDefault, "6" );\n' + LOGGER,
            "provider logger",
        )

        start = text.index("TInt CHspsLiwUtilities::AppendPluginsFlatL(")
        end_marker = (
            "// -----------------------------------------------------------------------------\n"
            "// Builds and appends settings to a map."
        )
        end = text.index(end_marker, start)
        text = text[:start] + REPLACEMENT + "\n" + text[end:]
    return text


def install_mmp(text: str) -> str:
    if "LIBRARY         efsrv.lib" not in text:
        text = replace_once(
            text,
            "LIBRARY         euser.lib\n",
            "LIBRARY         euser.lib\nLIBRARY         efsrv.lib\n",
            "file-server import",
        )
    return text


def verify(source: str, mmp: str) -> None:
    stages = range(0x10, 0x16)
    checks = {
        "marker": source.count(MARKER) == 1,
        "stages": all(
            source.count(f"0x485816{stage:02X}u")
            == (2 if stage == 0x12 else 1)
            for stage in stages
        ),
        "direct control": source.count("aConfigurationNode.ChildNodes().FindByName( KControlElement )") == 1,
        "direct plugins": source.count("controlNode->ChildNodes().FindByName( KPluginsElement )") == 1,
        "old depth iterator removed": "ChspsDomDepthIterator::NewL( \n\t\t\t\t\t\t\t\t\t\t\t\t\t\t   aConfigurationNode )" not in source,
        "real map retained": source.count("BuildPluginMapL( *plugin, *map, pluginMapItems )") >= 2,
        "real liw insert retained": source.count("aMap.InsertL( KHspsLiwPlugins, listVariant )") == 1,
        "capacity": source.count("1048576 - 128") == 1,
        "log path": source.count(r"C:\\Symbian3\\HSXML.TXT") == 1,
        "efsrv": mmp.count("LIBRARY         efsrv.lib") == 1,
        "no delay": all(token not in source for token in ("User::After", "RTimer", "HalFunction")),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        stage_counts = ",".join(
            f"{stage:02X}:{source.count(f'0x485816{stage:02X}u')}"
            for stage in stages
        )
        raise SystemExit(
            "HSPS provider plugin-map verification failed: "
            + ", ".join(failed)
            + f"; stage_counts={stage_counts}; "
            + "real_map_count="
            + str(source.count("BuildPluginMapL( *plugin, *map, pluginMapItems )"))
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / (
        "sf/mw/homescreensrv/homescreensrv_plat/"
        "sapi_homescreenplugin"
    )
    source_path = component / "src/hspsliwutilities.cpp"
    mmp_path = component / "group/hspsprovider.mmp"
    source = install_source(source_path.read_text(encoding="utf-8"))
    mmp = install_mmp(mmp_path.read_text(encoding="utf-8"))
    verify(source, mmp)
    source_path.write_text(source, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print(
        "HTCLEO_HSPSPROVIDER_PLUGIN_MAP_COMPAT="
        "schema-direct-root-list-real-liw-maps"
    )


if __name__ == "__main__":
    main()
