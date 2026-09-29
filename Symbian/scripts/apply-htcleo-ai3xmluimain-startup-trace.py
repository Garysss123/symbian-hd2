#!/usr/bin/env python3
"""Add a behavior-neutral durable startup trace to ai3xmluimain.dll."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AI3XMLUIMAIN_STARTUP_TRACE_V1"
LOGGER_MARKER = "HTCLEO_AI3XMLUIMAIN_DURABLE_LOG_V1"
MXML_FORWARD_MARKER = "HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HEADER = r'''#ifndef HTCLEO_AI3XML_LOG_H
#define HTCLEO_AI3XML_LOG_H

#include <e32std.h>

void HtcleoAi3XmlLog(TUint32 aStage, TInt aResult, TUint32 aDetail);

#endif
'''


MXML_FORWARD_HEADER = r'''#ifndef HTCLEO_MXMLATTRIBUTES_FORWARD_H
#define HTCLEO_MXMLATTRIBUTES_FORWARD_H

// HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_V1
// The public SVG listener ABI uses this type only by reference.  The PDK
// omitted its private XML-parser header, so an incomplete declaration is the
// exact compile-time contract needed by ai3xmluimain; no layout is invented.
class MXMLAttributes;

#endif
'''


LOGGER = r'''// HTCLEO_AI3XMLUIMAIN_DURABLE_LOG_V1
#include "htcleoai3xmllog.h"
#include <e32base.h>
#include <f32file.h>

void HtcleoAi3XmlLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                            __attribute__((noinline));

void HtcleoAi3XmlLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
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
    // One MiB ceiling; no writable DLL-global counter is used.
    if (r == KErrNone && position <= (1048576 - 128))
        {
        TBuf8<128> record;
        _LIT8(KPrefix, "HTCLEO_HXML ");
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


def patch_controller(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "xmluicontroller.h"\n',
        '#include "xmluicontroller.h"\n#include "htcleoai3xmllog.h"\n\n'
        f'// {MARKER}\n',
        "controller logger include",
    )
    text = replace_once(
        text,
        '''void CXmlUiController::NotifyAppEnvReadyL()
    {    
    iCPSpublisher = CContentPublisher::NewL( *this );
    
    iExitTimer = CPeriodic::NewL( CActive::EPriorityStandard );    

    if( iFwEventHandler )
        {
        iFwEventHandler->AppEnvReadyL();        
        }          
    }''',
        '''void CXmlUiController::NotifyAppEnvReadyL()
    {
    HtcleoAi3XmlLog(0x48580200u, KErrNone, 0u);
    iCPSpublisher = CContentPublisher::NewL( *this );
    HtcleoAi3XmlLog(0x48580201u, KErrNone, (TUint32)iCPSpublisher);
    
    iExitTimer = CPeriodic::NewL( CActive::EPriorityStandard );
    HtcleoAi3XmlLog(0x48580202u, KErrNone, (TUint32)iExitTimer);

    HtcleoAi3XmlLog(0x48580203u, KErrNone,
        (TUint32)(iFwEventHandler != NULL));
    if( iFwEventHandler )
        {
        HtcleoAi3XmlLog(0x48580204u, KErrNone, 0u);
        iFwEventHandler->AppEnvReadyL();
        HtcleoAi3XmlLog(0x48580205u, KErrNone, 0u);
        }
    HtcleoAi3XmlLog(0x48580206u, KErrNone, 0u);
    }''',
        "NotifyAppEnvReadyL trace",
    )
    text = replace_once(
        text,
        '''void CXmlUiController::RunApplicationL()
    {
    __PRINTS( "*** CXmlUiController::RunApplicationL" );
    
    iRunningAsMain = ETrue;
                                                    
    User::LeaveIfError( 
        EikStart::RunApplication( &CXmlUiController::NewApplication ) );       
    }''',
        '''void CXmlUiController::RunApplicationL()
    {
    HtcleoAi3XmlLog(0x48580100u, KErrNone, 0u);
    __PRINTS( "*** CXmlUiController::RunApplicationL" );
    
    iRunningAsMain = ETrue;
    HtcleoAi3XmlLog(0x48580101u, KErrNone, 1u);

    HtcleoAi3XmlLog(0x48580102u, KErrNone, 0u);
    const TInt htcleoRunResult =
        EikStart::RunApplication( &CXmlUiController::NewApplication );
    HtcleoAi3XmlLog(0x48580103u, htcleoRunResult, 0u);
    User::LeaveIfError( htcleoRunResult );
    HtcleoAi3XmlLog(0x48580104u, KErrNone, 0u);
    }''',
        "RunApplicationL trace",
    )
    text = replace_once(
        text,
        '''CApaApplication* CXmlUiController::NewApplication()
    {
    __TICK( "CXmlUiController::NewApplication" );
    __TIME_MARK( time );
    
    CXmlUiController* self = static_cast< CXmlUiController* >( Dll::Tls() );
    
    __ASSERT_ALWAYS( self, Panic( ECriticalPointerNull ) );
    
    CApplication* app = CApplication::New( *self );    
    
    __TIME_ENDMARK( "CXmlUiController::NewApplication, done", time );
    
    return app;
    }''',
        '''CApaApplication* CXmlUiController::NewApplication()
    {
    HtcleoAi3XmlLog(0x48580110u, KErrNone, 0u);
    __TICK( "CXmlUiController::NewApplication" );
    __TIME_MARK( time );
    
    CXmlUiController* self = static_cast< CXmlUiController* >( Dll::Tls() );
    HtcleoAi3XmlLog(0x48580111u, KErrNone, (TUint32)self);
    
    __ASSERT_ALWAYS( self, Panic( ECriticalPointerNull ) );
    
    CApplication* app = CApplication::New( *self );
    HtcleoAi3XmlLog(0x48580112u, KErrNone, (TUint32)app);
    
    __TIME_ENDMARK( "CXmlUiController::NewApplication, done", time );
    
    return app;
    }''',
        "NewApplication trace",
    )
    return text


def patch_application(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "application.h"\n',
        '#include "application.h"\n#include "htcleoai3xmllog.h"\n\n'
        f'// {MARKER}\n',
        "application logger include",
    )
    text = replace_once(
        text,
        '''CApplication* CApplication::New(CXmlUiController& aUiCtl)
    {
    CApplication* self = NULL;''',
        '''CApplication* CApplication::New(CXmlUiController& aUiCtl)
    {
    HtcleoAi3XmlLog(0x48580120u, KErrNone, (TUint32)&aUiCtl);
    CApplication* self = NULL;''',
        "application New entry",
    )
    text = replace_once(
        text,
        '''    __HEAP("XML UI: Create Application");

    return self;''',
        '''    __HEAP("XML UI: Create Application");
    HtcleoAi3XmlLog(0x48580121u, KErrNone, (TUint32)self);

    return self;''',
        "application New return",
    )
    text = replace_once(
        text,
        '''CApaDocument* CApplication::CreateDocumentL()
    {
    return CDocument::NewL(*this, iUiCtl);
    }''',
        '''CApaDocument* CApplication::CreateDocumentL()
    {
    HtcleoAi3XmlLog(0x48580130u, KErrNone, (TUint32)this);
    CApaDocument* document = CDocument::NewL(*this, iUiCtl);
    HtcleoAi3XmlLog(0x48580131u, KErrNone, (TUint32)document);
    return document;
    }''',
        "CreateDocument trace",
    )
    text = replace_once(
        text,
        '''TFileName CApplication::ResourceFileName() const
    {
    
    TFileName resFile;''',
        '''TFileName CApplication::ResourceFileName() const
    {
    HtcleoAi3XmlLog(0x48580140u, KErrNone, (TUint32)this);
    
    TFileName resFile;''',
        "resource name entry",
    )
    text = replace_once(
        text,
        '''    resFile.Append( KDC_APP_RESOURCE_DIR );
    resFile.Append( KAiXmlUiResourceFile );
    BaflUtils::NearestLanguageFile( CCoeEnv::Static()->FsSession(), resFile );
    
    return resFile;''',
        '''    resFile.Append( KDC_APP_RESOURCE_DIR );
    resFile.Append( KAiXmlUiResourceFile );
    HtcleoAi3XmlLog(0x48580141u, KErrNone, (TUint32)resFile.Length());
    CCoeEnv* env = CCoeEnv::Static();
    HtcleoAi3XmlLog(0x48580142u, KErrNone, (TUint32)env);
    BaflUtils::NearestLanguageFile( env->FsSession(), resFile );
    HtcleoAi3XmlLog(0x48580143u, KErrNone, (TUint32)resFile.Length());
    
    return resFile;''',
        "resource name resolution trace",
    )
    return text


def patch_document(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "document.h"\n',
        '#include "document.h"\n#include "htcleoai3xmllog.h"\n\n'
        f'// {MARKER}\n',
        "document logger include",
    )
    text = replace_once(
        text,
        '''CDocument* CDocument::NewL(CEikApplication &aApp, CXmlUiController& aUiCtl)
    {
    CDocument* self = NULL;''',
        '''CDocument* CDocument::NewL(CEikApplication &aApp, CXmlUiController& aUiCtl)
    {
    HtcleoAi3XmlLog(0x48580150u, KErrNone, (TUint32)&aApp);
    CDocument* self = NULL;''',
        "document NewL entry",
    )
    text = replace_once(
        text,
        '''\t__HEAP("XML UI: Create Document");

    return self;''',
        '''\t__HEAP("XML UI: Create Document");
    HtcleoAi3XmlLog(0x48580151u, KErrNone, (TUint32)self);

    return self;''',
        "document NewL return",
    )
    text = replace_once(
        text,
        '''CEikAppUi* CDocument::CreateAppUiL()
    {
    return CAppUi::NewL(iUiCtl);
    }''',
        '''CEikAppUi* CDocument::CreateAppUiL()
    {
    HtcleoAi3XmlLog(0x48580160u, KErrNone, (TUint32)this);
    CEikAppUi* appUi = CAppUi::NewL(iUiCtl);
    HtcleoAi3XmlLog(0x48580161u, KErrNone, (TUint32)appUi);
    return appUi;
    }''',
        "CreateAppUi trace",
    )
    return text


def patch_appui(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "appui.h"\n',
        '#include "appui.h"\n#include "htcleoai3xmllog.h"\n\n'
        f'// {MARKER}\n',
        "appui logger include",
    )
    text = replace_once(
        text,
        '''void CAppUi::ConstructL()
    {
    __TICK( "CAppUi::ConstructL" );''',
        '''void CAppUi::ConstructL()
    {
    HtcleoAi3XmlLog(0x48580180u, KErrNone, (TUint32)this);
    __TICK( "CAppUi::ConstructL" );''',
        "appui Construct entry",
    )
    text = replace_once(
        text,
        '''    iUiCtl.SetAppUi( *this );
    
    iCoeEnv->DisableExitChecks( ETrue );
       
    TRAPD( err, DoConstructL() );''',
        '''    iUiCtl.SetAppUi( *this );
    HtcleoAi3XmlLog(0x48580181u, KErrNone, (TUint32)iCoeEnv);
    
    iCoeEnv->DisableExitChecks( ETrue );
    HtcleoAi3XmlLog(0x48580182u, KErrNone, 1u);

    HtcleoAi3XmlLog(0x48580183u, KErrNone, 0u);
    TRAPD( err, DoConstructL() );
    HtcleoAi3XmlLog(0x48580184u, err, 0u);''',
        "appui DoConstruct trap",
    )
    text = replace_once(
        text,
        '''        // HandleUiShutdown must be called here 
        // to free all control environment dependent framework objects
        iUiCtl.FwEventHandler()->HandleUiShutdown( iUiCtl );    
        }
    
    User::LeaveIfError( err );
    
    __TICK( "CAppUi::ConstructL - done" );''',
        '''        // HandleUiShutdown must be called here 
        // to free all control environment dependent framework objects
        HtcleoAi3XmlLog(0x48580185u, err,
            (TUint32)iUiCtl.FwEventHandler());
        iUiCtl.FwEventHandler()->HandleUiShutdown( iUiCtl );
        HtcleoAi3XmlLog(0x48580186u, err, 0u);
        }
    
    User::LeaveIfError( err );
    HtcleoAi3XmlLog(0x48580187u, KErrNone, 0u);
    
    __TICK( "CAppUi::ConstructL - done" );''',
        "appui Construct result",
    )
    text = replace_once(
        text,
        '''void CAppUi::DoConstructL()
    {
    iUiCtl.NotifyAppEnvReadyL();''',
        '''void CAppUi::DoConstructL()
    {
    HtcleoAi3XmlLog(0x48580190u, KErrNone, 0u);
    HtcleoAi3XmlLog(0x48580191u, KErrNone, 0u);
    iUiCtl.NotifyAppEnvReadyL();
    HtcleoAi3XmlLog(0x48580192u, KErrNone, 0u);''',
        "DoConstruct framework ready",
    )
    text = replace_once(
        text,
        '''    RProperty::Set( KPSUidAiInformation,
      KActiveIdleForwardNumericKeysToPhone, EPSAiForwardNumericKeysToPhone );''',
        '''    const TInt htcleoForwardKeyResult = RProperty::Set(
      KPSUidAiInformation, KActiveIdleForwardNumericKeysToPhone,
      EPSAiForwardNumericKeysToPhone );
    HtcleoAi3XmlLog(0x48580193u, htcleoForwardKeyResult, 0u);''',
        "forward-key property trace",
    )
    text = replace_once(
        text,
        '''    __TIME("XML UI: CXnAppUiAdapter::ConstructL",
        CXnAppUiAdapter::ConstructL() );       
      
    CAknAppUiBase::SetKeyEventFlags''',
        '''    HtcleoAi3XmlLog(0x48580194u, KErrNone, 0u);
    __TIME("XML UI: CXnAppUiAdapter::ConstructL",
        CXnAppUiAdapter::ConstructL() );
    HtcleoAi3XmlLog(0x48580195u, KErrNone, 0u);
      
    CAknAppUiBase::SetKeyEventFlags''',
        "Xn adapter trace",
    )
    text = replace_once(
        text,
        '''                                     CAknAppUiBase::EDisableSendKeyLong );
    
    iEditModeTitle = StringLoader::LoadL( R_QTN_HS_TITLE_EDITMODE );
    
    // Register for XML UI view activation & deactivation
    AddViewActivationObserverL( this );''',
        '''                                     CAknAppUiBase::EDisableSendKeyLong );
    HtcleoAi3XmlLog(0x48580196u, KErrNone, 0u);
    
    HtcleoAi3XmlLog(0x48580197u, KErrNone, R_QTN_HS_TITLE_EDITMODE);
    iEditModeTitle = StringLoader::LoadL( R_QTN_HS_TITLE_EDITMODE );
    HtcleoAi3XmlLog(0x48580198u, KErrNone, (TUint32)iEditModeTitle);
    
    // Register for XML UI view activation & deactivation
    HtcleoAi3XmlLog(0x48580199u, KErrNone, 0u);
    AddViewActivationObserverL( this );
    HtcleoAi3XmlLog(0x4858019Au, KErrNone, 0u);''',
        "title and observer trace",
    )
    text = replace_once(
        text,
        '''    __TIME("XML UI: Construct Content Renderer",
        iContentRenderer = CContentRenderer::NewL( *this );
    )
    __HEAP("XML UI: Construct Content Renderer");

    TXnUiEngineAppIf* uiEngine( UiEngineL() );''',
        '''    HtcleoAi3XmlLog(0x4858019Bu, KErrNone, 0u);
    __TIME("XML UI: Construct Content Renderer",
        iContentRenderer = CContentRenderer::NewL( *this );
    )
    __HEAP("XML UI: Construct Content Renderer");
    HtcleoAi3XmlLog(0x4858019Cu, KErrNone, (TUint32)iContentRenderer);

    TXnUiEngineAppIf* uiEngine( UiEngineL() );
    HtcleoAi3XmlLog(0x4858019Du, KErrNone, (TUint32)uiEngine);''',
        "renderer and engine trace",
    )
    text = replace_once(
        text,
        '''    iUiCtl.SetObserver( *iContentRenderer );
    
    iContentRenderer->SetEventHandler( *iUiCtl.FwEventHandler() );
           
    iEventHandler = iUiCtl.CreateXuikonEventHandlerL( *iContentRenderer );''',
        '''    iUiCtl.SetObserver( *iContentRenderer );
    HtcleoAi3XmlLog(0x4858019Eu, KErrNone, 0u);
    
    iContentRenderer->SetEventHandler( *iUiCtl.FwEventHandler() );
    HtcleoAi3XmlLog(0x4858019Fu, KErrNone,
        (TUint32)iUiCtl.FwEventHandler());
           
    iEventHandler = iUiCtl.CreateXuikonEventHandlerL( *iContentRenderer );
    HtcleoAi3XmlLog(0x485801A0u, KErrNone, (TUint32)iEventHandler);''',
        "handler trace",
    )
    text = replace_once(
        text,
        '''    iHelper = COnlineOfflineHelper::NewL( iUiCtl );
    
    iIdleIntegration = CAiUiIdleIntegration::NewL
        ( *iEikonEnv, keySoundConfig, iUiCtl.FwEventHandler() );
               
    __TICK( "CAppUi::ConstructL - done" );''',
        '''    HtcleoAi3XmlLog(0x485801A1u, KErrNone, 0u);
    iHelper = COnlineOfflineHelper::NewL( iUiCtl );
    HtcleoAi3XmlLog(0x485801A2u, KErrNone, (TUint32)iHelper);
    
    HtcleoAi3XmlLog(0x485801A3u, KErrNone, (TUint32)iEikonEnv);
    iIdleIntegration = CAiUiIdleIntegration::NewL
        ( *iEikonEnv, keySoundConfig, iUiCtl.FwEventHandler() );
    HtcleoAi3XmlLog(0x485801A4u, KErrNone, (TUint32)iIdleIntegration);
               
    __TICK( "CAppUi::ConstructL - done" );''',
        "helper and integration trace",
    )
    text = replace_once(
        text,
        '''CAppUi* CAppUi::NewL( CXmlUiController& aUiCtl )
    {
    CAppUi* self = new ( ELeave ) CAppUi( aUiCtl, KUidXmlUiApp );

    // ConstructL is called by the UI framework

    return self;
    }''',
        '''CAppUi* CAppUi::NewL( CXmlUiController& aUiCtl )
    {
    HtcleoAi3XmlLog(0x48580170u, KErrNone, (TUint32)&aUiCtl);
    CAppUi* self = new ( ELeave ) CAppUi( aUiCtl, KUidXmlUiApp );
    HtcleoAi3XmlLog(0x48580171u, KErrNone, (TUint32)self);

    // ConstructL is called by the UI framework

    return self;
    }''',
        "appui NewL trace",
    )
    return text


def verify(root: Path) -> None:
    component = root / "sf/app/homescreen/idlehomescreen/xmluicontroller"
    paths = {
        "controller": component / "src/xmluicontroller.cpp",
        "application": component / "src/application.cpp",
        "document": component / "src/document.cpp",
        "appui": component / "src/appui.cpp",
        "logger": component / "src/htcleoai3xmllog.cpp",
        "header": component / "inc/htcleoai3xmllog.h",
        "mxml": component / "inc/MXMLAttributes.h",
        "mmp": component / "group/aixmluimain.mmp",
    }
    texts = {name: path.read_text(encoding="latin-1") for name, path in paths.items()}
    source = "".join(texts[name] for name in ("controller", "application", "document", "appui"))
    stages = (
        list(range(0x0100, 0x0105))
        + list(range(0x0110, 0x0113))
        + list(range(0x0120, 0x0122))
        + list(range(0x0130, 0x0132))
        + list(range(0x0140, 0x0144))
        + list(range(0x0150, 0x0152))
        + list(range(0x0160, 0x0162))
        + list(range(0x0170, 0x0172))
        + list(range(0x0180, 0x0188))
        + list(range(0x0190, 0x01A5))
        + list(range(0x0200, 0x0207))
    )
    checks = {
        "source markers": all(texts[name].count(MARKER) == 1 for name in ("controller", "application", "document", "appui")),
        "logger marker": texts["logger"].count(LOGGER_MARKER) == 1,
        "MXML forward declaration": texts["mxml"].count(MXML_FORWARD_MARKER) == 1
        and texts["mxml"].count("class MXMLAttributes;") == 1,
        "one MiB": texts["logger"].count("1048576 - 128") == 1,
        "path": texts["logger"].count("C:\\\\Symbian3\\\\HSXML.TXT") == 1,
        "no writable globals": "static " not in texts["logger"],
        "all stages": all(source.count(f"0x4858{stage:04X}u") == 1 for stage in stages),
        "EikStart once": source.count("EikStart::RunApplication") == 1,
        "result preserved": source.count("User::LeaveIfError( htcleoRunResult )") == 1,
        "logger source": texts["mmp"].count("SOURCE          htcleoai3xmllog.cpp") == 1,
        "efsrv": "efsrv.lib" in texts["mmp"],
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("ai3xmluimain trace audit failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/app/homescreen/idlehomescreen/xmluicontroller"
    paths = {
        "controller": component / "src/xmluicontroller.cpp",
        "application": component / "src/application.cpp",
        "document": component / "src/document.cpp",
        "appui": component / "src/appui.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing XML controller source: {path}")
    mutations = {
        "controller": patch_controller,
        "application": patch_application,
        "document": patch_document,
        "appui": patch_appui,
    }
    for name, path in paths.items():
        text = path.read_text(encoding="latin-1")
        path.write_text(mutations[name](text), encoding="latin-1")
    (component / "inc/htcleoai3xmllog.h").write_text(HEADER, encoding="latin-1")
    (component / "inc/MXMLAttributes.h").write_text(
        MXML_FORWARD_HEADER, encoding="latin-1"
    )
    (component / "src/htcleoai3xmllog.cpp").write_text(LOGGER, encoding="latin-1")
    mmp_path = component / "group/aixmluimain.mmp"
    mmp = mmp_path.read_text(encoding="latin-1")
    if "SOURCE          htcleoai3xmllog.cpp" not in mmp:
        mmp = replace_once(
            mmp,
            "SOURCE          xmluicontroller.cpp\n",
            "SOURCE          xmluicontroller.cpp\n"
            "SOURCE          htcleoai3xmllog.cpp\n",
            "logger MMP source",
        )
        mmp_path.write_text(mmp, encoding="latin-1")
    verify(args.root)
    print("HTCLEO_AI3XMLUIMAIN_STARTUP_TRACE=installed stages=48580100-48580206 log=HSXML.TXT capacity=1048576")


if __name__ == "__main__":
    main()
