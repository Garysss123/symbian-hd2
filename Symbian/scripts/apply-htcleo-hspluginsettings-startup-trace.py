#!/usr/bin/env python3
"""Trace HomeScreen settings initialization without changing LIW behavior."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPLUGINSETTINGS_STARTUP_TRACE_V1"
MACRO = "__HTCLEO_HSPLUGINSETTINGS_TRACE__"
EFSRV_LIBRARY = "LIBRARY         efsrv.lib"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''

#ifdef __HTCLEO_HSPLUGINSETTINGS_TRACE__
#include <f32file.h>

// HTCLEO_HSPLUGINSETTINGS_STARTUP_TRACE_V1
static void HtcleoHsPluginSettingsLog(TUint32 aStage, TInt aResult,
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
        _LIT8(KPrefix, "HTCLEO_HPS  ");
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
#else
inline void HtcleoHsPluginSettingsLog(TUint32, TInt, TUint32) {}
#endif

'''


def install(source: str) -> str:
    source = replace_once(
        source,
        '#include <mhomescreensettingsobserver.h>\n',
        '#include <mhomescreensettingsobserver.h>\n' + HELPER,
        "logger helper",
    )
    source = replace_once(
        source,
        "EXPORT_C void CHomescreenSettings::InitializeL( const TDesC8& aAppUid )\n"
        "    {\n"
        "    CTlsEntry* entry = static_cast<CTlsEntry*>( Dll::Tls() );",
        "EXPORT_C void CHomescreenSettings::InitializeL( const TDesC8& aAppUid )\n"
        "    {\n"
        "    HtcleoHsPluginSettingsLog(0x48581200u, KErrNone,\n"
        "        (TUint32)aAppUid.Length());\n"
        "    CTlsEntry* entry = static_cast<CTlsEntry*>( Dll::Tls() );\n"
        "    HtcleoHsPluginSettingsLog(0x48581201u, KErrNone,\n"
        "        (TUint32)entry);",
        "Initialize entry/TLS",
    )
    source = replace_once(
        source,
        "        entry = new (ELeave) CTlsEntry();\n"
        "        entry->iInstance = NULL;\n"
        "        entry->iRefCount = 1;\n"
        "        \n"
        "        CleanupStack::PushL( entry );\n"
        "        entry->iInstance = CHomescreenSettings::NewL( aAppUid );\n"
        "        CleanupStack::Pop( entry );                                \n"
        "        \n"
        "        Dll::SetTls( entry );",
        "        HtcleoHsPluginSettingsLog(0x48581202u, KErrNone, 0u);\n"
        "        entry = new (ELeave) CTlsEntry();\n"
        "        HtcleoHsPluginSettingsLog(0x48581203u, KErrNone,\n"
        "            (TUint32)entry);\n"
        "        entry->iInstance = NULL;\n"
        "        entry->iRefCount = 1;\n"
        "        \n"
        "        CleanupStack::PushL( entry );\n"
        "        HtcleoHsPluginSettingsLog(0x48581204u, KErrNone, 0u);\n"
        "        entry->iInstance = CHomescreenSettings::NewL( aAppUid );\n"
        "        HtcleoHsPluginSettingsLog(0x48581205u, KErrNone,\n"
        "            (TUint32)entry->iInstance);\n"
        "        CleanupStack::Pop( entry );                                \n"
        "        \n"
        "        HtcleoHsPluginSettingsLog(0x48581206u, KErrNone,\n"
        "            (TUint32)entry);\n"
        "        Dll::SetTls( entry );\n"
        "        HtcleoHsPluginSettingsLog(0x48581207u, KErrNone,\n"
        "            (TUint32)Dll::Tls());",
        "new TLS entry",
    )
    source = replace_once(
        source,
        "    else\n"
        "        {\n"
        "        entry->iRefCount++;\n"
        "        }\n"
        "    }\n\n"
        "// ---------------------------------------------------------------------------\n"
        "// ---------------------------------------------------------------------------\n"
        "//\n"
        "EXPORT_C void CHomescreenSettings::UnInitialize()",
        "    else\n"
        "        {\n"
        "        HtcleoHsPluginSettingsLog(0x48581208u, KErrNone,\n"
        "            (TUint32)entry->iRefCount);\n"
        "        entry->iRefCount++;\n"
        "        HtcleoHsPluginSettingsLog(0x48581209u, KErrNone,\n"
        "            (TUint32)entry->iRefCount);\n"
        "        }\n"
        "    HtcleoHsPluginSettingsLog(0x4858120Au, KErrNone,\n"
        "        (TUint32)entry);\n"
        "    }\n\n"
        "// ---------------------------------------------------------------------------\n"
        "// ---------------------------------------------------------------------------\n"
        "//\n"
        "EXPORT_C void CHomescreenSettings::UnInitialize()",
        "Initialize exit",
    )
    source = replace_once(
        source,
        "CHomescreenSettings* CHomescreenSettings::NewL(\n"
        "    const TDesC8& aAppUid )\n"
        "    {\n"
        "    CHomescreenSettings* self = CHomescreenSettings::NewLC( aAppUid );\n"
        "    CleanupStack::Pop( self );\n"
        "    return self;",
        "CHomescreenSettings* CHomescreenSettings::NewL(\n"
        "    const TDesC8& aAppUid )\n"
        "    {\n"
        "    HtcleoHsPluginSettingsLog(0x48581210u, KErrNone, 0u);\n"
        "    CHomescreenSettings* self = CHomescreenSettings::NewLC( aAppUid );\n"
        "    HtcleoHsPluginSettingsLog(0x48581211u, KErrNone,\n"
        "        (TUint32)self);\n"
        "    CleanupStack::Pop( self );\n"
        "    HtcleoHsPluginSettingsLog(0x48581212u, KErrNone,\n"
        "        (TUint32)self);\n"
        "    return self;",
        "NewL",
    )
    source = replace_once(
        source,
        "CHomescreenSettings* CHomescreenSettings::NewLC(\n"
        "    const TDesC8& aAppUid )\n"
        "    {    \n"
        "    CHomescreenSettings* self = new( ELeave ) CHomescreenSettings();\n"
        "    CleanupStack::PushL( self );\n"
        "    self->ConstructL( aAppUid );   \n"
        "    \n"
        "    return self;",
        "CHomescreenSettings* CHomescreenSettings::NewLC(\n"
        "    const TDesC8& aAppUid )\n"
        "    {    \n"
        "    HtcleoHsPluginSettingsLog(0x48581213u, KErrNone, 0u);\n"
        "    CHomescreenSettings* self = new( ELeave ) CHomescreenSettings();\n"
        "    HtcleoHsPluginSettingsLog(0x48581214u, KErrNone,\n"
        "        (TUint32)self);\n"
        "    CleanupStack::PushL( self );\n"
        "    HtcleoHsPluginSettingsLog(0x48581215u, KErrNone, 0u);\n"
        "    self->ConstructL( aAppUid );   \n"
        "    HtcleoHsPluginSettingsLog(0x48581216u, KErrNone,\n"
        "        (TUint32)self);\n"
        "    \n"
        "    HtcleoHsPluginSettingsLog(0x48581217u, KErrNone,\n"
        "        (TUint32)self);\n"
        "    return self;",
        "NewLC",
    )
    source = replace_once(
        source,
        "void CHomescreenSettings::ConstructL( const TDesC8& aAppUid )\n"
        "    {\n"
        "    // Attach to HSPS:\n"
        "    iServiceHandler = CLiwServiceHandler::NewL();",
        "void CHomescreenSettings::ConstructL( const TDesC8& aAppUid )\n"
        "    {\n"
        "    HtcleoHsPluginSettingsLog(0x48581220u, KErrNone,\n"
        "        (TUint32)aAppUid.Length());\n"
        "    // Attach to HSPS:\n"
        "    HtcleoHsPluginSettingsLog(0x48581221u, KErrNone, 0u);\n"
        "    iServiceHandler = CLiwServiceHandler::NewL();\n"
        "    HtcleoHsPluginSettingsLog(0x48581222u, KErrNone,\n"
        "        (TUint32)iServiceHandler);",
        "service handler",
    )
    source = replace_once(
        source,
        "    iHspsService = CLiwCriteriaItem::NewL( 1, KHSPSConfigurationIf, KHSPS );\n"
        "    iHspsService->SetServiceClass( TUid::Uid( KLiwClassBase ) );",
        "    HtcleoHsPluginSettingsLog(0x48581223u, KErrNone, 0u);\n"
        "    iHspsService = CLiwCriteriaItem::NewL( 1, KHSPSConfigurationIf, KHSPS );\n"
        "    HtcleoHsPluginSettingsLog(0x48581224u, KErrNone,\n"
        "        (TUint32)iHspsService);\n"
        "    iHspsService->SetServiceClass( TUid::Uid( KLiwClassBase ) );\n"
        "    HtcleoHsPluginSettingsLog(0x48581225u, KErrNone,\n"
        "        (TUint32)KLiwClassBase);",
        "criteria item",
    )
    source = replace_once(
        source,
        "    RCriteriaArray interestList;\n"
        "    interestList.AppendL( iHspsService );\n"
        "    iServiceHandler->AttachL( interestList );\n"
        "    interestList.Reset();",
        "    RCriteriaArray interestList;\n"
        "    HtcleoHsPluginSettingsLog(0x48581226u, KErrNone, 0u);\n"
        "    interestList.AppendL( iHspsService );\n"
        "    HtcleoHsPluginSettingsLog(0x48581227u, KErrNone,\n"
        "        (TUint32)interestList.Count());\n"
        "    HtcleoHsPluginSettingsLog(0x48581228u, KErrNone, 0u);\n"
        "    iServiceHandler->AttachL( interestList );\n"
        "    HtcleoHsPluginSettingsLog(0x48581229u, KErrNone, 0u);\n"
        "    interestList.Reset();\n"
        "    HtcleoHsPluginSettingsLog(0x4858122Au, KErrNone, 0u);",
        "LIW attach",
    )
    source = replace_once(
        source,
        "    HtcleoHsPluginSettingsLog(0x4858122Au, KErrNone, 0u);\n    \n"
        "    CLiwGenericParamList& inParamList = iServiceHandler->InParamListL();\n"
        "    CLiwGenericParamList& outParamList = iServiceHandler->OutParamListL();",
        "    HtcleoHsPluginSettingsLog(0x4858122Au, KErrNone, 0u);\n    \n"
        "    HtcleoHsPluginSettingsLog(0x4858122Bu, KErrNone, 0u);\n"
        "    CLiwGenericParamList& inParamList = iServiceHandler->InParamListL();\n"
        "    HtcleoHsPluginSettingsLog(0x4858122Cu, KErrNone,\n"
        "        (TUint32)&inParamList);\n"
        "    HtcleoHsPluginSettingsLog(0x4858122Du, KErrNone, 0u);\n"
        "    CLiwGenericParamList& outParamList = iServiceHandler->OutParamListL();\n"
        "    HtcleoHsPluginSettingsLog(0x4858122Eu, KErrNone,\n"
        "        (TUint32)&outParamList);",
        "parameter lists",
    )
    source = replace_once(
        source,
        "    TLiwGenericParam appUid;\n"
        "    TLiwVariant uidVar;\n"
        "    uidVar.Set( aAppUid );\n"
        "    appUid.SetNameAndValueL( KHspsAppUid, uidVar );\n"
        "    appUid.PushL();\n"
        "    inParamList.AppendL( appUid );\n"
        "    CleanupStack::Pop();\n"
        "    appUid.Reset();",
        "    HtcleoHsPluginSettingsLog(0x48581230u, KErrNone, 0u);\n"
        "    TLiwGenericParam appUid;\n"
        "    TLiwVariant uidVar;\n"
        "    uidVar.Set( aAppUid );\n"
        "    appUid.SetNameAndValueL( KHspsAppUid, uidVar );\n"
        "    HtcleoHsPluginSettingsLog(0x48581231u, KErrNone,\n"
        "        (TUint32)aAppUid.Length());\n"
        "    appUid.PushL();\n"
        "    HtcleoHsPluginSettingsLog(0x48581232u, KErrNone, 0u);\n"
        "    inParamList.AppendL( appUid );\n"
        "    HtcleoHsPluginSettingsLog(0x48581233u, KErrNone,\n"
        "        (TUint32)inParamList.Count());\n"
        "    CleanupStack::Pop();\n"
        "    appUid.Reset();\n"
        "    HtcleoHsPluginSettingsLog(0x48581234u, KErrNone, 0u);",
        "application UID parameter",
    )
    source = replace_once(
        source,
        "    iServiceHandler->ExecuteServiceCmdL( *iHspsService,inParamList,outParamList );\n"
        "    inParamList.Reset();\n"
        "    TInt pos = 0;\n"
        "    outParamList.FindFirst( pos, KHSPSConfigurationIf );",
        "    HtcleoHsPluginSettingsLog(0x48581235u, KErrNone, 0u);\n"
        "    iServiceHandler->ExecuteServiceCmdL( *iHspsService,inParamList,outParamList );\n"
        "    HtcleoHsPluginSettingsLog(0x48581236u, KErrNone,\n"
        "        (TUint32)outParamList.Count());\n"
        "    inParamList.Reset();\n"
        "    HtcleoHsPluginSettingsLog(0x48581237u, KErrNone, 0u);\n"
        "    TInt pos = 0;\n"
        "    HtcleoHsPluginSettingsLog(0x48581238u, KErrNone, 0u);\n"
        "    outParamList.FindFirst( pos, KHSPSConfigurationIf );\n"
        "    HtcleoHsPluginSettingsLog(0x48581239u, pos,\n"
        "        (TUint32)outParamList.Count());",
        "configuration service command",
    )
    source = replace_once(
        source,
        "        iHspsInterface = outParamList[ pos ].Value().AsInterface();    \n"
        "        outParamList.Reset();        \n"
        "        }\n"
        "    else\n"
        "        {\n"
        "        outParamList.Reset();       \n"
        "        User::Leave( KErrNotFound );",
        "        iHspsInterface = outParamList[ pos ].Value().AsInterface();    \n"
        "        HtcleoHsPluginSettingsLog(0x4858123Au, KErrNone,\n"
        "            (TUint32)iHspsInterface);\n"
        "        outParamList.Reset();        \n"
        "        }\n"
        "    else\n"
        "        {\n"
        "        outParamList.Reset();       \n"
        "        HtcleoHsPluginSettingsLog(0x4858123Bu, KErrNotFound, 0u);\n"
        "        User::Leave( KErrNotFound );",
        "configuration interface result",
    )
    source = replace_once(
        source,
        "    iHspsInterface->ExecuteCmdL( KRequestNotification,\n"
        "                                 inParamList,\n"
        "                                 outParamList,\n"
        "                                 KLiwOptASyncronous,\n"
        "                                 this );\n"
        "    \n"
        "    const TLiwGenericParam* outParam( NULL );",
        "    HtcleoHsPluginSettingsLog(0x4858123Cu, KErrNone,\n"
        "        (TUint32)iHspsInterface);\n"
        "    iHspsInterface->ExecuteCmdL( KRequestNotification,\n"
        "                                 inParamList,\n"
        "                                 outParamList,\n"
        "                                 KLiwOptASyncronous,\n"
        "                                 this );\n"
        "    HtcleoHsPluginSettingsLog(0x4858123Du, KErrNone,\n"
        "        (TUint32)outParamList.Count());\n"
        "    \n"
        "    const TLiwGenericParam* outParam( NULL );",
        "notification request",
    )
    source = replace_once(
        source,
        "    outParam = outParamList.FindFirst( pos, _L8(\"status\") );\n"
        "           \n"
        "    if( outParam )",
        "    outParam = outParamList.FindFirst( pos, _L8(\"status\") );\n"
        "    HtcleoHsPluginSettingsLog(0x4858123Eu, KErrNone,\n"
        "        (TUint32)outParam);\n"
        "           \n"
        "    if( outParam )",
        "notification status",
    )
    source = replace_once(
        source,
        "        }\n"
        "    }\n\n"
        "// ---------------------------------------------------------------------------\n"
        "// ---------------------------------------------------------------------------\n"
        "//\n"
        "CHomescreenSettings* CHomescreenSettings::NewL(",
        "        }\n"
        "    HtcleoHsPluginSettingsLog(0x4858123Fu, KErrNone,\n"
        "        (TUint32)iTransactionId);\n"
        "    }\n\n"
        "// ---------------------------------------------------------------------------\n"
        "// ---------------------------------------------------------------------------\n"
        "//\n"
        "CHomescreenSettings* CHomescreenSettings::NewL(",
        "ConstructL exit",
    )
    return source


def verify(source: str, mmp: str) -> None:
    stages = [
        *range(0x00, 0x0B),
        *range(0x10, 0x18),
        *range(0x20, 0x2F),
        *range(0x30, 0x40),
    ]
    checks = {
        "marker": source.count(MARKER) == 1,
        "SID/path/capacity/prefix": (
            source.count("RProcess().SecureId().iId != 0x102750f0u") == 1
            and source.count(r"C:\\Symbian3\\HSXML.TXT") == 1
            and source.count("1048576 - 128") == 1
            and source.count('"HTCLEO_HPS  "') == 1
        ),
        "stages": all(
            source.count(f"0x485812{stage:02X}u") == 1 for stage in stages
        ),
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "logger filesystem library": mmp.count(EFSRV_LIBRARY) == 1,
        "LIW behavior retained": all(
            source.count(call) >= 1
            for call in (
                "CLiwServiceHandler::NewL();",
                "CLiwCriteriaItem::NewL( 1, KHSPSConfigurationIf, KHSPS );",
                "iServiceHandler->AttachL( interestList );",
                "iServiceHandler->ExecuteServiceCmdL(",
                "iHspsInterface->ExecuteCmdL( KRequestNotification,",
                "User::Leave( KErrNotFound );",
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
        raise SystemExit("HS plugin settings trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = (
        args.root
        / "sf/mw/homescreensrv/homescreenpluginsrv/homescreen_settings_api"
    )
    source_path = component / "src/hspluginsettings.cpp"
    mmp_path = component / "group/hspluginsettings.mmp"
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"
    if EFSRV_LIBRARY not in mmp:
        mmp += f"{EFSRV_LIBRARY}\n"
    verify(source, mmp)
    if source != source_path.read_text(encoding="latin-1"):
        source_path.write_text(source, encoding="latin-1")
    if mmp != mmp_path.read_text(encoding="latin-1"):
        mmp_path.write_text(mmp, encoding="latin-1")
    print(
        "HTCLEO_HSPLUGINSETTINGS_STARTUP_TRACE="
        "HSXML-1m-48581200-4858123F-behavior-neutral"
    )


if __name__ == "__main__":
    main()
