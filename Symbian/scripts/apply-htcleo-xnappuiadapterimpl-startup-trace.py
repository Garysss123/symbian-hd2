#!/usr/bin/env python3
"""Trace HomeScreen CXnAppUiAdapterImpl::ConstructL without changing flow."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XNAPPUIADAPTERIMPL_STARTUP_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''

// HTCLEO_XNAPPUIADAPTERIMPL_STARTUP_TRACE_V1
static void HtcleoXnAdapterImplLog(TUint32 aStage, TInt aResult,
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
        _LIT8(KPrefix, "HTCLEO_HXI  ");
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


def install(source: str) -> str:
    source = replace_once(
        source,
        '#include "debug.h"\n',
        '#include "debug.h"\n#include <f32file.h>\n' + HELPER,
        "logger helper",
    )
    source = replace_once(
        source,
        "void CXnAppUiAdapterImpl::ConstructL()\n"
        "    {       \n"
        '    __PRINTS( "*** CXnAppUiAdapterImpl::ConstructL" );',
        "void CXnAppUiAdapterImpl::ConstructL()\n"
        "    {       \n"
        "    HtcleoXnAdapterImplLog(0x48581100u, KErrNone, (TUint32)this);\n"
        '    __PRINTS( "*** CXnAppUiAdapterImpl::ConstructL" );',
        "ConstructL entry",
    )
    source = replace_once(
        source,
        "    uid.Format( KUint, iApplicationUid.iUid );    \n"
        "    \n"
        "    HSPluginSettingsIf::CHomescreenSettings::InitializeL( uid );",
        "    uid.Format( KUint, iApplicationUid.iUid );    \n"
        "    HtcleoXnAdapterImplLog(0x48581101u, KErrNone,\n"
        "        (TUint32)iApplicationUid.iUid);\n"
        "    \n"
        "    HtcleoXnAdapterImplLog(0x48581102u, KErrNone, 0u);\n"
        "    HSPluginSettingsIf::CHomescreenSettings::InitializeL( uid );\n"
        "    HtcleoXnAdapterImplLog(0x48581103u, KErrNone, 0u);",
        "HomeScreen settings initialization",
    )
    source = replace_once(
        source,
        "    resFile.Append( KResourceFile );\n"
        "    BaflUtils::NearestLanguageFile( CCoeEnv::Static()->FsSession(),\n"
        "            resFile );      \n"
        "    \n"
        "    iResourceOffset = CCoeEnv::Static()->AddResourceFileL( resFile );",
        "    resFile.Append( KResourceFile );\n"
        "    HtcleoXnAdapterImplLog(0x48581104u, KErrNone,\n"
        "        (TUint32)resFile.Length());\n"
        "    HtcleoXnAdapterImplLog(0x48581105u, KErrNone, 0u);\n"
        "    BaflUtils::NearestLanguageFile( CCoeEnv::Static()->FsSession(),\n"
        "            resFile );      \n"
        "    HtcleoXnAdapterImplLog(0x48581106u, KErrNone,\n"
        "        (TUint32)resFile.Length());\n"
        "    \n"
        "    HtcleoXnAdapterImplLog(0x48581107u, KErrNone, 0u);\n"
        "    iResourceOffset = CCoeEnv::Static()->AddResourceFileL( resFile );\n"
        "    HtcleoXnAdapterImplLog(0x48581108u, KErrNone,\n"
        "        (TUint32)iResourceOffset);",
        "resource file setup",
    )
    source = replace_once(
        source,
        "    iContentControlFactory = CHsContentControlFactory::NewL( iAdapter );    \n"
        "    \n"
        "    iUiStateListener = CXnUiStateListener::NewL( iAdapter );\n"
        "            \n"
        "    iViewManager = CXnViewManager::NewL( iAdapter );\n"
        "    \n"
        "    iUiEngine = CXnUiEngine::NewL( iAdapter );",
        "    HtcleoXnAdapterImplLog(0x48581109u, KErrNone, 0u);\n"
        "    iContentControlFactory = CHsContentControlFactory::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x4858110Au, KErrNone,\n"
        "        (TUint32)iContentControlFactory);\n"
        "    \n"
        "    HtcleoXnAdapterImplLog(0x4858110Bu, KErrNone, 0u);\n"
        "    iUiStateListener = CXnUiStateListener::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x4858110Cu, KErrNone,\n"
        "        (TUint32)iUiStateListener);\n"
        "            \n"
        "    HtcleoXnAdapterImplLog(0x4858110Du, KErrNone, 0u);\n"
        "    iViewManager = CXnViewManager::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x4858110Eu, KErrNone,\n"
        "        (TUint32)iViewManager);\n"
        "    \n"
        "    HtcleoXnAdapterImplLog(0x4858110Fu, KErrNone, 0u);\n"
        "    iUiEngine = CXnUiEngine::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x48581110u, KErrNone,\n"
        "        (TUint32)iUiEngine);",
        "core object construction",
    )
    source = replace_once(
        source,
        "    iViewManager->SetUiEngine( *iUiEngine );\n"
        "    \n"
        "    // iViewAdapter is owned by CAknViewAppUi\n"
        "    iViewAdapter = CXnViewAdapter::NewL( iAdapter );\n"
        "       \n"
        "    iViewManager->LoadUiL();",
        "    HtcleoXnAdapterImplLog(0x48581111u, KErrNone, 0u);\n"
        "    iViewManager->SetUiEngine( *iUiEngine );\n"
        "    HtcleoXnAdapterImplLog(0x48581112u, KErrNone, 0u);\n"
        "    \n"
        "    // iViewAdapter is owned by CAknViewAppUi\n"
        "    HtcleoXnAdapterImplLog(0x48581113u, KErrNone, 0u);\n"
        "    iViewAdapter = CXnViewAdapter::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x48581114u, KErrNone,\n"
        "        (TUint32)iViewAdapter);\n"
        "       \n"
        "    HtcleoXnAdapterImplLog(0x48581115u, KErrNone, 0u);\n"
        "    iViewManager->LoadUiL();\n"
        "    HtcleoXnAdapterImplLog(0x48581116u, KErrNone, 0u);",
        "engine/view setup",
    )
    source = replace_once(
        source,
        "    iCcProviderClient = CHsCcProviderClient::NewL( iViewManager->Editor() );\n"
        "    \n"
        "    CXnWallpaperView* wallpaper = CXnWallpaperView::NewL( *iUiEngine );\n"
        "    CleanupStack::PushL( wallpaper );\n"
        "    \n"
        "    // wallpaper view is owned by CAknViewAppUi\n"
        "    iAdapter.AddViewL( wallpaper );\n"
        "    CleanupStack::Pop( wallpaper );",
        "    HtcleoXnAdapterImplLog(0x48581117u, KErrNone, 0u);\n"
        "    iCcProviderClient = CHsCcProviderClient::NewL( iViewManager->Editor() );\n"
        "    HtcleoXnAdapterImplLog(0x48581118u, KErrNone,\n"
        "        (TUint32)iCcProviderClient);\n"
        "    \n"
        "    HtcleoXnAdapterImplLog(0x48581119u, KErrNone, 0u);\n"
        "    CXnWallpaperView* wallpaper = CXnWallpaperView::NewL( *iUiEngine );\n"
        "    HtcleoXnAdapterImplLog(0x4858111Au, KErrNone,\n"
        "        (TUint32)wallpaper);\n"
        "    CleanupStack::PushL( wallpaper );\n"
        "    \n"
        "    // wallpaper view is owned by CAknViewAppUi\n"
        "    HtcleoXnAdapterImplLog(0x4858111Bu, KErrNone, 0u);\n"
        "    iAdapter.AddViewL( wallpaper );\n"
        "    HtcleoXnAdapterImplLog(0x4858111Cu, KErrNone, 0u);\n"
        "    CleanupStack::Pop( wallpaper );\n"
        "    HtcleoXnAdapterImplLog(0x4858111Du, KErrNone, 0u);",
        "content/wallpaper setup",
    )
    source = replace_once(
        source,
        "    iEffectManager = CXnEffectManager::NewL( iAdapter );   \n"
        "    \n"
        "    iBackupRestoreObserver = CXnPropertySubscriber::NewL( \n"
        "            KUidSystemCategory, conn::KUidBackupRestoreKey, *this );\n"
        "\n"
        "    iActivator = CXnItemActivator::NewL( iAdapter );\n"
        "    \n"
        '    __TIME_ENDMARK( "CXnAppUiAdapterImpl::ConstructL, done", time );',
        "    HtcleoXnAdapterImplLog(0x4858111Eu, KErrNone, 0u);\n"
        "    iEffectManager = CXnEffectManager::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x4858111Fu, KErrNone,\n"
        "        (TUint32)iEffectManager);\n"
        "    \n"
        "    HtcleoXnAdapterImplLog(0x48581120u, KErrNone, 0u);\n"
        "    iBackupRestoreObserver = CXnPropertySubscriber::NewL( \n"
        "            KUidSystemCategory, conn::KUidBackupRestoreKey, *this );\n"
        "    HtcleoXnAdapterImplLog(0x48581121u, KErrNone,\n"
        "        (TUint32)iBackupRestoreObserver);\n"
        "\n"
        "    HtcleoXnAdapterImplLog(0x48581122u, KErrNone, 0u);\n"
        "    iActivator = CXnItemActivator::NewL( iAdapter );\n"
        "    HtcleoXnAdapterImplLog(0x48581123u, KErrNone,\n"
        "        (TUint32)iActivator);\n"
        "    HtcleoXnAdapterImplLog(0x48581124u, KErrNone, 0u);\n"
        "    \n"
        '    __TIME_ENDMARK( "CXnAppUiAdapterImpl::ConstructL, done", time );',
        "tail object construction",
    )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "SID/path/capacity/prefix": (
            source.count("RProcess().SecureId().iId != 0x102750f0u") == 1
            and source.count(r"C:\\Symbian3\\HSXML.TXT") == 1
            and source.count("1048576 - 128") == 1
            and source.count('"HTCLEO_HXI  "') == 1
        ),
        "all stages": all(
            source.count(f"0x485811{stage:02X}u") == 1
            for stage in range(0x25)
        ),
        "stock calls retained": all(
            source.count(call) >= 1
            for call in (
                "HSPluginSettingsIf::CHomescreenSettings::InitializeL( uid );",
                "BaflUtils::NearestLanguageFile( CCoeEnv::Static()->FsSession(),",
                "iResourceOffset = CCoeEnv::Static()->AddResourceFileL( resFile );",
                "iContentControlFactory = CHsContentControlFactory::NewL( iAdapter );",
                "iUiStateListener = CXnUiStateListener::NewL( iAdapter );",
                "iViewManager = CXnViewManager::NewL( iAdapter );",
                "iUiEngine = CXnUiEngine::NewL( iAdapter );",
                "iViewManager->SetUiEngine( *iUiEngine );",
                "iViewAdapter = CXnViewAdapter::NewL( iAdapter );",
                "iViewManager->LoadUiL();",
                "iCcProviderClient = CHsCcProviderClient::NewL( iViewManager->Editor() );",
                "CXnWallpaperView* wallpaper = CXnWallpaperView::NewL( *iUiEngine );",
                "iAdapter.AddViewL( wallpaper );",
                "iEffectManager = CXnEffectManager::NewL( iAdapter );",
                "iBackupRestoreObserver = CXnPropertySubscriber::NewL(",
                "iActivator = CXnItemActivator::NewL( iAdapter );",
            )
        ),
        "single writer": source.count("file.Write(record)") == 1,
        "no behavior change": all(
            token not in HELPER
            for token in ("User::After", "RTimer", "HalFunction", "TRAP")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Xn adapter impl trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src/xnappuiadapterimpl.cpp"
    )
    source = path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    if source != path.read_text(encoding="latin-1"):
        path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_XNAPPUIADAPTERIMPL_STARTUP_TRACE="
        "HSXML-1m-48581100-48581124-behavior-neutral"
    )


if __name__ == "__main__":
    main()
