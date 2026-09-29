#!/usr/bin/env python3
"""Map HTC Leo WVGA to the shipped qHD HSPS family and trace ROM bootstrap."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPSTHEMESERVER_HD2_FAMILY_COMPAT_V1"
INSTALL_MARKER = "HTCLEO_HSPS_INSTALLATION_CONSTRUCT_TRACE_V1"
MACRO = "__HTCLEO_HSPS_HD2_FAMILY_COMPAT__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''

#ifdef __HTCLEO_HSPS_HD2_FAMILY_COMPAT__
// HTCLEO_HSPSTHEMESERVER_HD2_FAMILY_COMPAT_V1
static void HtcleoHspsServerLog(TUint32 aStage, TInt aResult,
                                TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;
    _LIT(KDir, "C:\\Symbian3\\");
    _LIT(KPath, "C:\\Symbian3\\HSPSSRV.TXT");
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
        _LIT8(KPrefix, "HTCLEO_HSS  ");
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
inline void HtcleoHspsServerLog(TUint32, TInt, TUint32) {}
#endif

'''


def install_server(source: str) -> str:
    source = replace_once(
        source,
        '#include "hspsfamily.h"\n',
        '#include "hspsfamily.h"\n' + LOGGER,
        "server logger",
    )
    source = replace_once(
        source,
        "void ChspsThemeServer::ConstructL()\n"
        "    {\n"
        "    User::LeaveIfError( iFsSession.Connect() );",
        "void ChspsThemeServer::ConstructL()\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x48581300u, KErrNone, 0u);\n"
        "    TInt htcleoFsError = iFsSession.Connect();\n"
        "    HtcleoHspsServerLog(0x48581301u, htcleoFsError, 0u);\n"
        "    User::LeaveIfError( htcleoFsError );",
        "server filesystem",
    )
    source = replace_once(
        source,
        "    // These might leave if configurations are invalid\n"
        "    TRAP_IGNORE( InitializeHeadersL() );",
        "    // These might leave if configurations are invalid.  Preserve the\n"
        "    // stock fail-open policy while exposing its hidden result.\n"
        "    HtcleoHspsServerLog(0x4858130Bu, KErrNone,\n"
        "        (TUint32)iHeaderListCache->Count());\n"
        "    TRAPD(htcleoHeadersError, InitializeHeadersL());\n"
        "    HtcleoHspsServerLog(0x4858130Cu, htcleoHeadersError,\n"
        "        (TUint32)iHeaderListCache->Count());",
        "header initialization result",
    )
    source = replace_once(
        source,
        "void ChspsThemeServer::InitializeHeadersL()\n"
        "    {        \n"
        "    // Auto-localize ODTs in the Definition Repository when the device language has changed\n"
        "    HandleLanguageChangeL();            \n"
        "   \n"
        "    // Reinstall plug-ins/handle FOTA updates\n"
        "    HandleRomInstallationsL();",
        "void ChspsThemeServer::InitializeHeadersL()\n"
        "    {        \n"
        "    HtcleoHspsServerLog(0x48581310u, KErrNone,\n"
        "        (TUint32)iHeaderListCache->Count());\n"
        "    // Auto-localize ODTs in the Definition Repository when the device language has changed\n"
        "    TRAPD(htcleoLanguageError, HandleLanguageChangeL());\n"
        "    HtcleoHspsServerLog(0x48581311u, htcleoLanguageError,\n"
        "        (TUint32)iDeviceLanguage);\n"
        "    User::LeaveIfError(htcleoLanguageError);\n"
        "   \n"
        "    // Reinstall plug-ins/handle FOTA updates\n"
        "    HtcleoHspsServerLog(0x48581312u, KErrNone,\n"
        "        (TUint32)iHeaderListCache->Count());\n"
        "    TRAPD(htcleoRomError, HandleRomInstallationsL());\n"
        "    HtcleoHspsServerLog(0x48581313u, htcleoRomError,\n"
        "        (TUint32)iHeaderListCache->Count());\n"
        "    User::LeaveIfError(htcleoRomError);",
        "initialization phases",
    )
    source = replace_once(
        source,
        "void ChspsThemeServer::HandleRomInstallationsL()\n"
        "    {    \n",
        "void ChspsThemeServer::HandleRomInstallationsL()\n"
        "    {    \n"
        "    HtcleoHspsServerLog(0x48581330u, KErrNone,\n"
        "        (TUint32)iHeaderListCache->Count());\n",
        "ROM install entry",
    )
    source = replace_once(
        source,
        "    if ( res.Count() == 0 )\n"
        "        {",
        "    HtcleoHspsServerLog(0x48581331u, KErrNone,\n"
        "        (TUint32)res.Count());\n"
        "    if ( res.Count() == 0 )\n"
        "        {",
        "PostRFS key count",
    )
    source = replace_once(
        source,
        "    TInt errorCode = iCentralRepository->Get( key, fwVersion );\n"
        "    if( ( errorCode == KErrNone ) &&",
        "    TInt errorCode = iCentralRepository->Get( key, fwVersion );\n"
        "    HtcleoHspsServerLog(0x48581332u, errorCode,\n"
        "        (TUint32)fwVersion.Length());\n"
        "    if( ( errorCode == KErrNone ) &&",
        "PostRFS key value",
    )
    source = replace_once(
        source,
        "        // Install widgets from install and import directories (eMMC, UDA ROM)\n"
        "        InstallWidgetsL( ETrue );",
        "        // Install widgets from install and import directories (eMMC, UDA ROM)\n"
        "        HtcleoHspsServerLog(0x48581333u, KErrNone, 1u);\n"
        "        InstallWidgetsL( ETrue );\n"
        "        HtcleoHspsServerLog(0x48581334u, KErrNone,\n"
        "            (TUint32)iHeaderListCache->Count());",
        "first ROM install",
    )
    source = replace_once(
        source,
        "#if defined(WINSCW) || defined(__WINS__)\n"
        "    // Activate client specific root configurations from active display resolution",
        "#ifdef __HTCLEO_HSPS_HD2_FAMILY_COMPAT__\n"
        "    // A previous boot with an unsupported WVGA family can record the firmware\n"
        "    // version even though every manifest was rejected.  Retry only while the\n"
        "    // real Active Idle root configuration is absent.\n"
        "    TBool htcleoHomeRootPresent = EFalse;\n"
        "    for (TInt htcleoIndex = 0;\n"
        "         htcleoIndex < iHeaderListCache->Count(); ++htcleoIndex)\n"
        "        {\n"
        "        ChspsODT* htcleoHeader = iHeaderListCache->At(htcleoIndex);\n"
        "        if (htcleoHeader && htcleoHeader->RootUid() ==\n"
        "            (TInt)KAppId_hspsAI &&\n"
        "            htcleoHeader->ConfigurationType() ==\n"
        "            EhspsAppConfiguration)\n"
        "            {\n"
        "            htcleoHomeRootPresent = ETrue;\n"
        "            break;\n"
        "            }\n"
        "        }\n"
        "    HtcleoHspsServerLog(0x48581335u,\n"
        "        htcleoHomeRootPresent ? KErrNone : KErrNotFound,\n"
        "        (TUint32)iHeaderListCache->Count());\n"
        "    if (!htcleoHomeRootPresent)\n"
        "        {\n"
        "        InstallWidgetsL(ETrue);\n"
        "        for (TInt htcleoIndex = 0;\n"
        "             htcleoIndex < iHeaderListCache->Count(); ++htcleoIndex)\n"
        "            {\n"
        "            ChspsODT* htcleoHeader = iHeaderListCache->At(htcleoIndex);\n"
        "            if (htcleoHeader && htcleoHeader->RootUid() ==\n"
        "                (TInt)KAppId_hspsAI &&\n"
        "                htcleoHeader->ConfigurationType() ==\n"
        "                EhspsAppConfiguration)\n"
        "                {\n"
        "                htcleoHomeRootPresent = ETrue;\n"
        "                break;\n"
        "                }\n"
        "            }\n"
        "        HtcleoHspsServerLog(0x48581336u,\n"
        "            htcleoHomeRootPresent ? KErrNone : KErrNotFound,\n"
        "            (TUint32)iHeaderListCache->Count());\n"
        "        User::LeaveIfError(htcleoHomeRootPresent ? KErrNone :\n"
        "            KErrNotFound);\n"
        "        }\n"
        "#endif\n"
        "\n"
        "#if defined(WINSCW) || defined(__WINS__)\n"
        "    // Activate client specific root configurations from active display resolution",
        "missing-root retry",
    )
    source = replace_once(
        source,
        "void ChspsThemeServer::InstallWidgetsL(\n"
        "        const TBool aInstallUdaEmmc )\n"
        "    {    \n",
        "void ChspsThemeServer::InstallWidgetsL(\n"
        "        const TBool aInstallUdaEmmc )\n"
        "    {    \n"
        "    HtcleoHspsServerLog(0x48581340u, KErrNone,\n"
        "        (TUint32)aInstallUdaEmmc);\n",
        "InstallWidgets entry",
    )
    source = replace_once(
        source,
        "\tiRomInstaller->InstallL();\n"
        "\t\t\t\n"
        "\tdelete iRomInstaller;",
        "\tiRomInstaller->InstallL();\n"
        "    HtcleoHspsServerLog(0x48581341u, KErrNone,\n"
        "        (TUint32)iHeaderListCache->Count());\n"
        "\t\t\t\n"
        "\tdelete iRomInstaller;",
        "InstallWidgets result",
    )
    return source


def install_family(source: str) -> str:
    source = replace_once(
        source,
        '#include <featmgr.h>\n',
        '#include <featmgr.h>\n#include <f32file.h>\n' + LOGGER,
        "family logger",
    )
    source = replace_once(
        source,
        "        case 640:\n"
        "            {\n"
        "            if( resolution.iWidth == 360 )\n"
        "                {\n"
        "                aFamily.Append( KFamilyQhd );\n"
        "                }\n"
        "            else if( resolution.iWidth == 480 )\n"
        "                {\n"
        "                aFamily.Append( KFamilyVga );\n"
        "                }            \n"
        "            }\n"
        "            break;\n"
        "        \n"
        "        default:",
        "        case 640:\n"
        "            {\n"
        "            if( resolution.iWidth == 360 )\n"
        "                {\n"
        "                aFamily.Append( KFamilyQhd );\n"
        "                }\n"
        "            else if( resolution.iWidth == 480 )\n"
        "                {\n"
        "                aFamily.Append( KFamilyVga );\n"
        "                }            \n"
        "            }\n"
        "            break;\n"
        "#ifdef __HTCLEO_HSPS_HD2_FAMILY_COMPAT__\n"
        "        case 800:\n"
        "            {\n"
        "            // HTC Leo is physically 480x800, while the shipped S60\n"
        "            // HomeScreen assets use the 360x640 qhd_tch family and\n"
        "            // are scaled by the proven display compatibility path.\n"
        "            if (resolution.iWidth == 480)\n"
        "                {\n"
        "                aFamily.Append(KFamilyQhd);\n"
        "                }\n"
        "            }\n"
        "            break;\n"
        "#endif\n"
        "        \n"
        "        default:",
        "WVGA family mapping",
    )
    source = replace_once(
        source,
        "    if( aFamily.Length() > 0 )\n"
        "        {                     \n"
        "        aFamily.Append( KTch );\n"
        "        }\n"
        "    }",
        "    HtcleoHspsServerLog(0x485813F0u, KErrNone,\n"
        "        ((TUint32)(resolution.iWidth & 0xffff) << 16) |\n"
        "        (TUint32)(resolution.iHeight & 0xffff));\n"
        "    if( aFamily.Length() > 0 )\n"
        "        {                     \n"
        "        aFamily.Append( KTch );\n"
        "        }\n"
        "    HtcleoHspsServerLog(0x485813F1u,\n"
        "        aFamily.Length() ? KErrNone : KErrNotSupported,\n"
        "        (TUint32)GetFamilyType(aFamily));\n"
        "    }",
        "family result trace",
    )
    return source


def install_rom_installer(source: str) -> str:
    source = replace_once(
        source,
        '#include "hspsserverutil.h"\n',
        '#include "hspsserverutil.h"\n' + LOGGER,
        "ROM installer logger",
    )
    source = replace_once(
        source,
        "void ChspsRomInstaller::InstallL()\n"
        "    {\n"
        "    RPointerArray<HBufC> fileArray;",
        "void ChspsRomInstaller::InstallL()\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x48581350u, KErrNone,\n"
        "        (TUint32)iInstallUdaEmmc);\n"
        "    RPointerArray<HBufC> fileArray;",
        "ROM installer entry",
    )
    source = replace_once(
        source,
        "    FindInstallFilesL( fileArray );\n"
        "      \n"
        "    // Find manifest files from the \"imports\" directories\n"
        "    FindImportFilesL( fileArray );",
        "    FindInstallFilesL( fileArray );\n"
        "    HtcleoHspsServerLog(0x48581351u, KErrNone,\n"
        "        (TUint32)fileArray.Count());\n"
        "      \n"
        "    // Find manifest files from the \"imports\" directories\n"
        "    FindImportFilesL( fileArray );\n"
        "    HtcleoHspsServerLog(0x48581352u, KErrNone,\n"
        "        (TUint32)fileArray.Count());",
        "manifest counts",
    )
    source = replace_once(
        source,
        "        ThspsServiceCompletedMessage ret = EhspsInstallThemeFailed;\n"
        "        TRAP_IGNORE( ret = InstallThemeL( namePtr  ) );\n"
        "        if ( ret != EhspsInstallThemeSuccess )",
        "        ThspsServiceCompletedMessage ret = EhspsInstallThemeFailed;\n"
        "        HtcleoHspsServerLog(0x48581353u, KErrNone,\n"
        "            ((TUint32)index << 16) | (TUint32)namePtr.Length());\n"
        "        TRAPD(htcleoInstallError, ret = InstallThemeL( namePtr  ));\n"
        "        HtcleoHspsServerLog(0x48581354u, htcleoInstallError,\n"
        "            ((TUint32)index << 16) | ((TUint32)ret & 0xffffu));\n"
        "        if ( ret != EhspsInstallThemeSuccess )",
        "per-manifest result",
    )
    source = replace_once(
        source,
        "    if ( fileArray.Count() == 0 )\n"
        "        {",
        "    HtcleoHspsServerLog(0x48581355u, KErrNone,\n"
        "        (TUint32)fileArray.Count());\n"
        "    if ( fileArray.Count() == 0 )\n"
        "        {",
        "manifest loop result",
    )
    source = replace_once(
        source,
        "    iRet = iInstallationHandler->hspsInstallTheme( aFileName, iHeaderData );    \n"
        "    if ( iRet == EhspsInstallThemeSuccess && !IsActive() )",
        "    iRet = iInstallationHandler->hspsInstallTheme( aFileName, iHeaderData );    \n"
        "    HtcleoHspsServerLog(0x48581356u, (TInt)iRet,\n"
        "        (TUint32)aFileName.Length());\n"
        "    if ( iRet == EhspsInstallThemeSuccess && !IsActive() )",
        "initial install result",
    )
    source = replace_once(
        source,
        "        // Wait until the installation phases have been executed (async->sync) \n"
        "        CActiveScheduler::Start();\n"
        "        }\n"
        "    \n"
        "    return iRet;",
        "        // Wait until the installation phases have been executed (async->sync) \n"
        "        HtcleoHspsServerLog(0x48581357u, KErrNone, 0u);\n"
        "        CActiveScheduler::Start();\n"
        "        HtcleoHspsServerLog(0x48581358u, (TInt)iRet, 0u);\n"
        "        }\n"
        "    \n"
        "    return iRet;",
        "async install phases",
    )
    source = replace_once(
        source,
        "TInt ChspsRomInstaller::RunError( TInt /*aError*/ )\n"
        "    {\n"
        "    iRet = EhspsInstallThemeFailed;",
        "TInt ChspsRomInstaller::RunError( TInt aError )\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x4858135Au, aError, 0u);\n"
        "    iRet = EhspsInstallThemeFailed;",
        "RunError trace",
    )
    source = replace_once(
        source,
        "void ChspsRomInstaller::RunL()\n"
        "    {\n"
        "    iRet = (ThspsServiceCompletedMessage)iStatus.Int();",
        "void ChspsRomInstaller::RunL()\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x48581359u, iStatus.Int(),\n"
        "        (TUint32)iRet);\n"
        "    iRet = (ThspsServiceCompletedMessage)iStatus.Int();",
        "RunL trace",
    )
    return source


def install_installation_handler(source: str) -> str:
    install_logger = LOGGER.replace(MARKER, INSTALL_MARKER)
    source = replace_once(
        source,
        "#include <centralrepository.h>\n",
        "#include <centralrepository.h>\n"
        "#include <ecom/ecom.h>\n"
        "#include <f32file.h>\n" + install_logger,
        "installation-handler logger",
    )
    source = replace_once(
        source,
        "ChspsInstallationHandler* ChspsInstallationHandler::NewL( ChspsThemeServer& aThemeServer )\n"
        "    {\n"
        "    ChspsInstallationHandler* h = ChspsInstallationHandler::NewLC( aThemeServer );\n"
        "    CleanupStack::Pop( h );\n"
        "    return ( h );",
        "ChspsInstallationHandler* ChspsInstallationHandler::NewL( ChspsThemeServer& aThemeServer )\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x48581360u, KErrNone, 0u);\n"
        "    ChspsInstallationHandler* h = ChspsInstallationHandler::NewLC( aThemeServer );\n"
        "    HtcleoHspsServerLog(0x48581361u, KErrNone, (TUint32)h);\n"
        "    CleanupStack::Pop( h );\n"
        "    return ( h );",
        "installation NewL",
    )
    source = replace_once(
        source,
        "ChspsInstallationHandler* ChspsInstallationHandler::NewLC( ChspsThemeServer& aThemeServer )\n"
        "    {\n"
        "    ChspsInstallationHandler* h = new (ELeave) ChspsInstallationHandler( aThemeServer );\n"
        "    CleanupStack::PushL( h );\n"
        "    h->ConstructL();\n"
        "    return ( h );",
        "ChspsInstallationHandler* ChspsInstallationHandler::NewLC( ChspsThemeServer& aThemeServer )\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x48581362u, KErrNone, 0u);\n"
        "    ChspsInstallationHandler* h = new (ELeave) ChspsInstallationHandler( aThemeServer );\n"
        "    HtcleoHspsServerLog(0x48581363u, KErrNone, (TUint32)h);\n"
        "    CleanupStack::PushL( h );\n"
        "    HtcleoHspsServerLog(0x48581364u, KErrNone, 0u);\n"
        "    h->ConstructL();\n"
        "    HtcleoHspsServerLog(0x48581365u, KErrNone, (TUint32)h);\n"
        "    return ( h );",
        "installation NewLC",
    )
    source = replace_once(
        source,
        "void ChspsInstallationHandler::ConstructL()\n"
        "    {\n"
        "    User::LeaveIfError( iFsSession.Connect() );\n"
        "\n"
        "    _LIT8(KMimeType, \"text/xml\");\n"
        "    MContentHandler* contentHandler = this;\n"
        "    iXmlParser = Xml::CParser::NewL( KMimeType, *contentHandler );\n"
        "    \n"
        "     iDefEngine = ChspsDefinitionEngineInterface::NewL(KhspsDefinitionEngine);\n"
        "         \n"
        "    iOdt = ChspsODT::NewL();",
        "void ChspsInstallationHandler::ConstructL()\n"
        "    {\n"
        "    HtcleoHspsServerLog(0x48581370u, KErrNone, 0u);\n"
        "    TInt htcleoFsError = iFsSession.Connect();\n"
        "    HtcleoHspsServerLog(0x48581371u, htcleoFsError, 0u);\n"
        "    User::LeaveIfError( htcleoFsError );\n"
        "\n"
        "    _LIT8(KMimeType, \"text/xml\");\n"
        "    MContentHandler* contentHandler = this;\n"
        "    HtcleoHspsServerLog(0x48581372u, KErrNone, 0u);\n"
        "    TRAPD(htcleoParserError,\n"
        "        iXmlParser = Xml::CParser::NewL(KMimeType, *contentHandler));\n"
        "    HtcleoHspsServerLog(0x48581373u, htcleoParserError,\n"
        "        (TUint32)iXmlParser);\n"
        "    if (htcleoParserError == KErrServerTerminated)\n"
        "        {\n"
        "        REComSession::FinalClose();\n"
        "        HtcleoHspsServerLog(0x48581374u, htcleoParserError, 0u);\n"
        "        TRAP(htcleoParserError,\n"
        "            iXmlParser = Xml::CParser::NewL(KMimeType, *contentHandler));\n"
        "        HtcleoHspsServerLog(0x48581375u, htcleoParserError,\n"
        "            (TUint32)iXmlParser);\n"
        "        }\n"
        "    User::LeaveIfError(htcleoParserError);\n"
        "    \n"
        "    HtcleoHspsServerLog(0x48581376u, KErrNone, 0u);\n"
        "    TRAPD(htcleoEngineError,\n"
        "        iDefEngine = ChspsDefinitionEngineInterface::NewL(\n"
        "            KhspsDefinitionEngine));\n"
        "    HtcleoHspsServerLog(0x48581377u, htcleoEngineError,\n"
        "        (TUint32)iDefEngine);\n"
        "    if (htcleoEngineError == KErrServerTerminated)\n"
        "        {\n"
        "        REComSession::FinalClose();\n"
        "        HtcleoHspsServerLog(0x48581378u, htcleoEngineError, 0u);\n"
        "        TRAP(htcleoEngineError,\n"
        "            iDefEngine = ChspsDefinitionEngineInterface::NewL(\n"
        "                KhspsDefinitionEngine));\n"
        "        HtcleoHspsServerLog(0x48581379u, htcleoEngineError,\n"
        "            (TUint32)iDefEngine);\n"
        "        }\n"
        "    User::LeaveIfError(htcleoEngineError);\n"
        "         \n"
        "    HtcleoHspsServerLog(0x4858137Au, KErrNone, 0u);\n"
        "    iOdt = ChspsODT::NewL();\n"
        "    HtcleoHspsServerLog(0x4858137Bu, KErrNone, (TUint32)iOdt);",
        "installation ConstructL ECom stages",
    )
    source = replace_once(
        source,
        "    iResult = ChspsResult::NewL();\n"
        "    iXmlFile = KNullDesC().AllocL();\n"
        "    \n"
        "    iMultiInstanceFound = EFalse;    \n"
        "    }",
        "    iResult = ChspsResult::NewL();\n"
        "    HtcleoHspsServerLog(0x4858137Cu, KErrNone, (TUint32)iResult);\n"
        "    iXmlFile = KNullDesC().AllocL();\n"
        "    HtcleoHspsServerLog(0x4858137Du, KErrNone, (TUint32)iXmlFile);\n"
        "    \n"
        "    iMultiInstanceFound = EFalse;    \n"
        "    HtcleoHspsServerLog(0x4858137Eu, KErrNone, 0u);\n"
        "    }",
        "installation ConstructL tail",
    )
    return source


def verify(server: str, family: str, installer: str, installation: str,
           mmp: str) -> None:
    combined = server + family + installer + installation
    stages = [
        0x00, 0x01, 0x0B, 0x0C, 0x10, 0x11, 0x12, 0x13,
        0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x40, 0x41,
        0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58,
        0x59, 0x5A, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65,
        0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77,
        0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0xF0, 0xF1,
    ]
    checks = {
        "markers": (
            combined.count(MARKER) == 3
            and installation.count(INSTALL_MARKER) == 1
        ),
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "log path/capacity": (
            combined.count(r"C:\\Symbian3\\HSPSSRV.TXT") == 4
            and combined.count("1048576 - 128") == 4
            and combined.count('"HTCLEO_HSS  "') == 4
        ),
        "stages": all(combined.count(f"0x485813{stage:02X}u") == 1
                      for stage in stages),
        "WVGA maps to shipped qHD": (
            family.count("case 800:") == 1
            and family.count("resolution.iWidth == 480") >= 2
            and family.count("aFamily.Append(KFamilyQhd);") == 1
        ),
        "missing root retry": (
            server.count("htcleoHomeRootPresent") >= 6
            and server.count("InstallWidgetsL(ETrue);") == 1
            and server.count("KAppId_hspsAI") >= 3
        ),
        "stock install retained": (
            server.count("InstallWidgetsL( ETrue );") >= 1
            and installer.count("ret = InstallThemeL( namePtr  )") == 1
            and installer.count("CActiveScheduler::Start();") == 1
        ),
        "bounded ECom recovery": (
            installation.count("REComSession::FinalClose();") == 3
            and installation.count("== KErrServerTerminated") == 2
            and installation.count("Xml::CParser::NewL") == 2
            and installation.count(
                "ChspsDefinitionEngineInterface::NewL") == 3
        ),
        "single behavior macro": combined.count("case 800:") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS HTC Leo transform verification failed: " +
                         ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/homescreenpluginsrv/hspsmanager"
    server_path = component / "src/hspsthemeserver.cpp"
    family_path = component / "src/hspsfamily.cpp"
    installer_path = component / "src/hspsrominstaller.cpp"
    installation_path = component / "src/hspsinstallationhandler.cpp"
    mmp_path = component / "group/hspsthemeserver.mmp"

    server = server_path.read_text(encoding="latin-1")
    family = family_path.read_text(encoding="latin-1")
    installer = installer_path.read_text(encoding="latin-1")
    installation = installation_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    if MARKER not in server:
        server = install_server(server)
    if MARKER not in family:
        family = install_family(family)
    if MARKER not in installer:
        installer = install_rom_installer(installer)
    if INSTALL_MARKER not in installation:
        installation = install_installation_handler(installation)
    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(server, family, installer, installation, mmp)
    server_path.write_text(server, encoding="latin-1")
    family_path.write_text(family, encoding="latin-1")
    installer_path.write_text(installer, encoding="latin-1")
    installation_path.write_text(installation, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    print(
        "HTCLEO_HSPSTHEMESERVER_FAMILY_COMPAT="
        "480x800-to-qhd_tch-missing-root-retry"
    )
    print(
        "HTCLEO_HSPSTHEMESERVER_TRACE="
        "HSPSSRV-1m-48581300-485813F1"
    )
    print(
        "HTCLEO_HSPS_INSTALLER_ECOM_RECOVERY="
        "xml-parser-and-definition-engine-serverterminated-retry-once"
    )


if __name__ == "__main__":
    main()
