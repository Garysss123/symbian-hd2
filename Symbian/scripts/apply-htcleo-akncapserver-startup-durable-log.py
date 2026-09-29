#!/usr/bin/env python3
"""Install a fail-open AknCapServer process/startup durable trace.

Iteration 441 proves that ConstructAppFromCommandLineL returns
KErrServerTerminated before NewApplication (E010). This transform retains the
application/document/AppUi lifecycle trace and mirrors the release
EikStart::RunApplication control flow locally inside the isolated AknCap
executable. E200-E211 bracket every exported pre-factory returning boundary;
E212 reads the protected CCoeEnv constructor result through an empty local
derived class and confirms the process TLS identity. It does not replace the
process-wide eikcore.dll or change startup policy, return values, waits or
retries.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_STARTUP_DURABLE_LOG_V1"
EIKSTART_MARKER = "HTCLEO_AKNCAPSERVER_EIKSTART_DURABLE_LOG_V2"
EIKSTART_EXPORT_MARKER = "HTCLEO_AKNCAPSERVER_EIKSTART_EXPORTED_ONLY_V3"
EIKSTART_CONSTRUCTOR_MARKER = "HTCLEO_AKNCAPSERVER_CONSTRUCTOR_ERROR_V4"
MACRO = "__HTCLEO_AKNCAPSERVER_STARTUP_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_AKNCAPSERVER_STARTUP_LOG__
#include <f32file.h>

// HTCLEO_AKNCAPSERVER_STARTUP_DURABLE_LOG_V1
static void HtcleoAknCapLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoAknCapLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoAknCapLogPath, "C:\\Symbian3\\AKNCAP.TXT");
    r = fs.MkDirAll(KHtcleoAknCapLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoAknCapLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoAknCapLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position >= (512 * 65))
        {
        file.Close();
        fs.Close();
        return;
        }

    if (r == KErrNone)
        {
        _LIT8(KHtcleoAknCapPrefix, "HTCLEO_AKNCAP ");
        TBuf8<96> record;
        record.Append(KHtcleoAknCapPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        r = file.Write(record);
        if (r == KErrNone)
            {
            r = file.Flush();
            }
        file.Close();
        }
    fs.Close();
    }
#else
inline void HtcleoAknCapLog(TUint32, TInt, TUint32) {}
#endif

'''


EIKSTART_INCLUDES = r'''#include <basched.h>
#include <eikenv.h>
#include <eikdebug.h>
#include <eikpanic.h>
#include <uiklafgt/eikcore.rsg>
'''


EIKSTART_WRAPPER = r'''
#ifdef __HTCLEO_AKNCAPSERVER_STARTUP_LOG__
// HTCLEO_AKNCAPSERVER_EIKSTART_DURABLE_LOG_V2
// This is the UREL EikStart::RunApplication flow, scoped to akncapserver.exe.
// HTCLEO_AKNCAPSERVER_CONSTRUCTOR_ERROR_V4
class CHtcleoAknCapEikonEnv : public CEikonEnv
    {
public:
    TInt HtcleoConstructorError() const
        {
        return CoeEnvConstructorError();
        }
    };

static TInt HtcleoRunAknCapApplication(
    TApaApplicationFactory aApplicationFactory)
    {
    HtcleoAknCapLog(0x0000E200u, KErrNone, 0u);
    CApaCommandLine* commandLine = NULL;
    TBool disableShutdownChecks = EFalse;
    TInt error = CApaCommandLine::GetCommandLineFromProcessEnvironment(
        commandLine);
    HtcleoAknCapLog(0x0000E201u, error, commandLine ? 1u : 0u);
    if (error)
        {
        goto done;
        }

    User::__DbgMarkStart(RHeap::EUser);
    HtcleoAknCapLog(0x0000E202u, KErrNone, 0u);

    {
    TFileName executableFileName = RProcess().FileName();
    HtcleoAknCapLog(0x0000E203u, KErrNone,
        (TUint32)executableFileName.Length());
    error = User::RenameThread(TParsePtrC(executableFileName).Name());
    HtcleoAknCapLog(0x0000E204u, error, 0u);
    if (error)
        {
        goto done;
        }
    }

    {
    HtcleoAknCapLog(0x0000E205u, KErrNone, 0u);
    CHtcleoAknCapEikonEnv* env = new CHtcleoAknCapEikonEnv;
    HtcleoAknCapLog(0x0000E206u,
        env ? KErrNone : KErrNoMemory, env ? 1u : 0u);
    if (!env)
        {
        error = KErrNoMemory;
        }
    else
        {
        const TInt constructorError = env->HtcleoConstructorError();
        HtcleoAknCapLog(0x0000E212u, constructorError,
            CEikonEnv::Static() == env ? 1u : 0u);
        // HTCLEO_AKNCAPSERVER_EIKSTART_EXPORTED_ONLY_V3
        // ConstructAppFromCommandLineL begins with the same constructor-error
        // preflight as EikStart, then leaves before mutation on failure.  Using
        // it directly avoids importing a private/protected eikcore symbol.
        HtcleoAknCapLog(0x0000E207u, KErrNone, 1u);
        HtcleoAknCapLog(0x0000E208u, KErrNone, 0u);
        TRAP(error,
            env->ConstructAppFromCommandLineL(
                aApplicationFactory, *commandLine));
        HtcleoAknCapLog(0x0000E209u, error, 0u);
        }

    delete commandLine;
    commandLine = NULL;
    HtcleoAknCapLog(0x0000E20Au, error, 0u);

    if (!error)
        {
        HtcleoAknCapLog(0x0000E20Bu, KErrNone, 0u);
        env->Execute();
        HtcleoAknCapLog(0x0000E20Cu, KErrNone, 0u);
        }
    else if (env)
        {
        const TInt unhandledError = error;
        if (error == KLeaveWithoutAlert || error == KLeaveExit)
            {
            error = KErrNone;
            }
        else
            {
            TRAP_IGNORE(env->HandleError(error));
            }
        HtcleoAknCapLog(0x0000E20Du, unhandledError,
            (TUint32)error);
        }

    if (env != NULL)
        {
        disableShutdownChecks = env->DisableShutdownChecks();
        HtcleoAknCapLog(0x0000E20Eu, KErrNone,
            disableShutdownChecks ? 1u : 0u);
        env->DestroyEnvironment();
        HtcleoAknCapLog(0x0000E20Fu, KErrNone, 0u);
        }

    if (!error)
        {
        env = NULL;
        }
    }

done:
    delete commandLine;
    HtcleoAknCapLog(0x0000E210u, error,
        disableShutdownChecks ? 1u : 0u);
    if (!disableShutdownChecks)
        {
        User::__DbgMarkEnd(RHeap::EUser, 0);
        }
    HtcleoAknCapLog(0x0000E211u, error,
        disableShutdownChecks ? 1u : 0u);
    return error;
    }
#else
static TInt HtcleoRunAknCapApplication(
    TApaApplicationFactory aApplicationFactory)
    {
    return EikStart::RunApplication(aApplicationFactory);
    }
#endif
'''


def verify(
    source: str,
    mmp: str,
    widget_header: str,
    compatibility_headers: dict[str, str],
) -> None:
    stages = (
        tuple(range(0xE000, 0xE002))
        + tuple(range(0xE010, 0xE012))
        + tuple(range(0xE020, 0xE024))
        + tuple(range(0xE030, 0xE032))
        + tuple(range(0xE040, 0xE043))
        + tuple(range(0xE100, 0xE125))
        + tuple(range(0xE200, 0xE212))
        + (0xE212,)
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        "single EikStart marker": source.count(EIKSTART_MARKER) == 1,
        "single constructor-error marker": (
            source.count(EIKSTART_CONSTRUCTOR_MARKER) == 1
        ),
        "exported-only EikStart path": (
            source.count(EIKSTART_EXPORT_MARKER) == 1
            and "env->ConstructorError()" not in source
            and "env->CoeEnvConstructorError()" not in source
        ),
        "isolated constructor error access": (
            source.count("class CHtcleoAknCapEikonEnv : public CEikonEnv") == 1
            and source.count("return CoeEnvConstructorError();") == 1
            and source.count("env->HtcleoConstructorError()") == 1
            and source.count("CEikonEnv::Static() == env") == 1
        ),
        "single log path": source.count("C:\\\\Symbian3\\\\AKNCAP.TXT") == 1,
        "all stages": all(f"0x{stage:08X}u" in source for stage in stages),
        "single write": source.count("file.Write(record)") == 1,
        "single flush": source.count("file.Flush()") == 1,
        "bounded log": source.count("position >= (512 * 65)") == 1,
        "isolated EikStart wrapper": (
            source.count("HtcleoRunAknCapApplication(NewApplication)") == 1
            and source.count("env->ConstructAppFromCommandLineL(") == 1
            and source.count("env->Execute()") == 1
        ),
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "existing efsrv retained": mmp.count("LIBRARY         efsrv.lib") == 1,
        "widget include case fixed": (
            "#include <widgetregistrydata.h>" in widget_header
            and "#include <WidgetRegistryData.h>" not in widget_header
            and "#include <widgetpropertyvalue.h>" in widget_header
            and "#include <WidgetPropertyValue.h>" not in widget_header
        ),
        "GCCE declaration qualifications fixed": all(
            old not in compatibility_headers[name]
            and new in compatibility_headers[name]
            for name, old, new in (
                (
                    "alfvisual.h",
                    "CAlfVisual::SetEffectL",
                    "void SetEffectL",
                ),
                (
                    "alfvisual.h",
                    "CAlfVisual::SetGroupEffectL",
                    "void SetGroupEffectL",
                ),
                (
                    "AknEikSgcs.h",
                    "CEikSgcServer::RestoreThreadPriorities",
                    "TInt RestoreThreadPriorities",
                ),
                (
                    "AknKeyFilter.h",
                    "CAknServKeyFilter::HwKeyToKeyBoardType",
                    "TInt HwKeyToKeyBoardType",
                ),
                (
                    "eikedwin.h",
                    "CEikEdwin::AknEditorFlags",
                    "TInt AknEditorFlags",
                ),
                (
                    "AknBidiTextUtils.h",
                    "AknBidiTextUtils::MeasureTextBoundsWidth",
                    "TInt MeasureTextBoundsWidth",
                ),
            )
        ),
        "no waits": "User::After" not in source and "WaitForRequest" not in source,
        "no display probe": (
            "EHalGroupPlatformSpecific1, 2" not in source
            and "c6400000" not in source.lower()
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("AknCapServer startup log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    component = args.root / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer"
    source_path = component / "src/AknCapServerEntry.cpp"
    mmp_path = component / "group/AknCapServer.mmp"
    widget_header_path = args.root / "epoc32/include/platform/mw/widgetregistryclient.h"
    compatibility_header_paths = {
        "alfvisual.h": args.root / "epoc32/include/platform/mw/alf/alfvisual.h",
        "AknEikSgcs.h": component / "inc/AknEikSgcs.h",
        "AknKeyFilter.h": component / "inc/AknKeyFilter.h",
        "eikedwin.h": args.root / "epoc32/include/mw/eikedwin.h",
        "AknBidiTextUtils.h": args.root / "epoc32/include/mw/AknBidiTextUtils.h",
    }
    for path in (
        source_path,
        mmp_path,
        widget_header_path,
        *compatibility_header_paths.values(),
    ):
        if not path.is_file():
            raise SystemExit(f"missing AknCapServer input: {path}")

    source = source_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")
    widget_header = widget_header_path.read_text(encoding="utf-8")
    compatibility_headers = {
        # Some public PDK headers retain Windows-1252 punctuation.  Latin-1
        # preserves every original byte while the declarations we patch are
        # ASCII, so this remains a byte-stable mechanical compatibility fix.
        name: path.read_text(encoding="latin-1")
        for name, path in compatibility_header_paths.items()
    }

    widget_header = widget_header.replace(
        "#include <WidgetRegistryData.h>", "#include <widgetregistrydata.h>"
    )
    widget_header = widget_header.replace(
        "#include <WidgetPropertyValue.h>", "#include <widgetpropertyvalue.h>"
    )

    qualification_fixes = {
        "alfvisual.h": (
            (
                "IMPORT_C void CAlfVisual::SetEffectL(",
                "IMPORT_C void SetEffectL(",
            ),
            (
                "IMPORT_C void CAlfVisual::SetGroupEffectL(",
                "IMPORT_C void SetGroupEffectL(",
            ),
        ),
        "AknEikSgcs.h": (
            (
                "static TInt CEikSgcServer::RestoreThreadPriorities(",
                "static TInt RestoreThreadPriorities(",
            ),
        ),
        "AknKeyFilter.h": (
            (
                "TInt CAknServKeyFilter::HwKeyToKeyBoardType(",
                "TInt HwKeyToKeyBoardType(",
            ),
        ),
        "eikedwin.h": (
            (
                "IMPORT_C TInt CEikEdwin::AknEditorFlags(",
                "IMPORT_C TInt AknEditorFlags(",
            ),
        ),
        "AknBidiTextUtils.h": (
            (
                "IMPORT_C static TInt AknBidiTextUtils::MeasureTextBoundsWidth(",
                "IMPORT_C static TInt MeasureTextBoundsWidth(",
            ),
        ),
    }
    for name, replacements in qualification_fixes.items():
        for old, new in replacements:
            compatibility_headers[name] = compatibility_headers[name].replace(old, new)

    if MARKER not in source:
        source = replace_once(
            source,
            '#include <eikstart.h>\n',
            '#include <eikstart.h>\n' + LOGGER,
            "logger insertion",
        )

        source = replace_once(
            source,
            '''CAknCapServerApplication::CAknCapServerApplication()
    {
    }
''',
            '''CAknCapServerApplication::CAknCapServerApplication()
    {
    }
''',
            "constructor anchor",
        )

        source = replace_once(
            source,
            '''void CAknCapServerApplication::NewAppServerL(CApaAppServer*& aAppServer)
    {
    CAknCapServer* server = new (ELeave) CAknCapServer();
    
    CleanupStack::PushL(server);
    server->CreateDynamicSoftNoteEventManagerL();
    CleanupStack::Pop(server);    
    
    server->SetPriority(EActivePriorityIpcEventsHigh);
    aAppServer=&*server;
    iCapServer = server;
    }
''',
            '''void CAknCapServerApplication::NewAppServerL(CApaAppServer*& aAppServer)
    {
    HtcleoAknCapLog(0x0000E020u, KErrNone, 0u);
    CAknCapServer* server = new (ELeave) CAknCapServer();
    HtcleoAknCapLog(0x0000E021u, KErrNone, server ? 1u : 0u);
    
    CleanupStack::PushL(server);
    server->CreateDynamicSoftNoteEventManagerL();
    HtcleoAknCapLog(0x0000E022u, KErrNone, 0u);
    CleanupStack::Pop(server);    
    
    server->SetPriority(EActivePriorityIpcEventsHigh);
    aAppServer=&*server;
    iCapServer = server;
    HtcleoAknCapLog(0x0000E023u, KErrNone, 1u);
    }
''',
            "NewAppServerL",
        )

        source = replace_once(
            source,
            '''CApaDocument* CAknCapServerApplication::CreateDocumentL()
    {
    return new (ELeave) CAknCapAppServerDocument(*this);
    }
''',
            '''CApaDocument* CAknCapServerApplication::CreateDocumentL()
    {
    HtcleoAknCapLog(0x0000E030u, KErrNone, 0u);
    CAknCapAppServerDocument* document =
        new (ELeave) CAknCapAppServerDocument(*this);
    HtcleoAknCapLog(0x0000E031u, KErrNone, document ? 1u : 0u);
    return document;
    }
''',
            "CreateDocumentL",
        )

        source = replace_once(
            source,
            '''CEikAppUi* CAknCapAppServerDocument::CreateAppUiL()
    {
    CAknCapServerApplication* app = static_cast<CAknCapServerApplication*>(iApp);
    CAknCapServer* server = app->CapServer();
    CAknCapAppServerAppUi* ret = new (ELeave) CAknCapAppServerAppUi( server );
    return ret;
    }
''',
            '''CEikAppUi* CAknCapAppServerDocument::CreateAppUiL()
    {
    HtcleoAknCapLog(0x0000E040u, KErrNone, 0u);
    CAknCapServerApplication* app = static_cast<CAknCapServerApplication*>(iApp);
    CAknCapServer* server = app->CapServer();
    HtcleoAknCapLog(0x0000E041u, KErrNone, server ? 1u : 0u);
    CAknCapAppServerAppUi* ret = new (ELeave) CAknCapAppServerAppUi( server );
    HtcleoAknCapLog(0x0000E042u, KErrNone, ret ? 1u : 0u);
    return ret;
    }
''',
            "CreateAppUiL",
        )

        source = replace_once(
            source,
            '''void CAknCapAppServerAppUi::ConstructL()
    {
    User::SetCritical(User::ESystemCritical);

    InitiateOFNStatus();
    
    iEikonEnv->SetSystem( ETrue );
''',
            '''void CAknCapAppServerAppUi::ConstructL()
    {
    HtcleoAknCapLog(0x0000E100u, KErrNone, 0u);
    User::SetCritical(User::ESystemCritical);
    HtcleoAknCapLog(0x0000E101u, KErrNone, 0u);

    InitiateOFNStatus();
    HtcleoAknCapLog(0x0000E102u, KErrNone, 0u);
    
    iEikonEnv->SetSystem( ETrue );
    HtcleoAknCapLog(0x0000E103u, KErrNone, 0u);
''',
            "ConstructL entry",
        )

        source = replace_once(
            source,
            '''        iEikonEnv->InstallFepL(TUid::Uid(0x101FD65A));
        }
    
    // define and set the PS key listing installed languages
    PublishInstalledLanguagesL();
''',
            '''        iEikonEnv->InstallFepL(TUid::Uid(0x101FD65A));
        }
    HtcleoAknCapLog(0x0000E104u, KErrNone,
        (TUint32)iEikonEnv->FepUid().iUid);
    
    // define and set the PS key listing installed languages
    PublishInstalledLanguagesL();
    HtcleoAknCapLog(0x0000E105u, KErrNone, 0u);
''',
            "FEP and languages",
        )

        source = replace_once(
            source,
            '''        value = 0;
        }
    CRepository* repository = CRepository::NewL(KCRUidAknFep);
''',
            '''        value = 0;
        }
    HtcleoAknCapLog(0x0000E106u, KErrNone, (TUint32)value);
    CRepository* repository = CRepository::NewL(KCRUidAknFep);
    HtcleoAknCapLog(0x0000E107u, KErrNone, repository ? 1u : 0u);
''',
            "feature and repository",
        )

        source = replace_once(
            source,
            '''    delete repository;
    repository = NULL;
    
    // kick eikon server in (in case it is not running yet)
    TInt error = iEikSrv.Connect();
    __ASSERT_ALWAYS(error == KErrNone, User::Invariant());
    
    // base call
    CAknNotifierAppServerAppUi::ConstructL();
''',
            '''    delete repository;
    repository = NULL;
    HtcleoAknCapLog(0x0000E108u, KErrNone, (TUint32)value);
    
    // kick eikon server in (in case it is not running yet)
    TInt error = iEikSrv.Connect();
    HtcleoAknCapLog(0x0000E109u, error, 0u);
    __ASSERT_ALWAYS(error == KErrNone, User::Invariant());
    
    // base call
    CAknNotifierAppServerAppUi::ConstructL();
    HtcleoAknCapLog(0x0000E10Au, KErrNone, 0u);
''',
            "repository and EikSrv",
        )

        source = replace_once(
            source,
            '''    iBackdropWindowGroup=RWindowGroup(wsSession);
    User::LeaveIfError(iBackdropWindowGroup.Construct((TUint32)&iBackdropWindowGroup, EFalse));
    iBackdropWindowGroup.AutoForeground(EFalse);
''',
            '''    iBackdropWindowGroup=RWindowGroup(wsSession);
    const TInt htcleoBackdropResult =
        iBackdropWindowGroup.Construct((TUint32)&iBackdropWindowGroup, EFalse);
    HtcleoAknCapLog(0x0000E10Bu, htcleoBackdropResult, 0u);
    User::LeaveIfError(htcleoBackdropResult);
    iBackdropWindowGroup.AutoForeground(EFalse);
''',
            "backdrop construct",
        )

        source = replace_once(
            source,
            '''    CApaWindowGroupName* apaName = 
        CApaWindowGroupName::NewLC(wsSession, (TUint32)&iBackdropWindowGroup);
        
    apaName->SetHidden(ETrue);
''',
            '''    CApaWindowGroupName* apaName = 
        CApaWindowGroupName::NewLC(wsSession, (TUint32)&iBackdropWindowGroup);
    HtcleoAknCapLog(0x0000E10Cu, KErrNone, apaName ? 1u : 0u);
        
    apaName->SetHidden(ETrue);
''',
            "window group name",
        )

        source = replace_once(
            source,
            '''    apaName->SetCaptionL(EIKON_SERVER_BACKDROP_WINDOW_GROUP_NAME);
    User::LeaveIfError(apaName->SetWindowGroupName(iBackdropWindowGroup));
    CleanupStack::PopAndDestroy(); //apaName
''',
            '''    apaName->SetCaptionL(EIKON_SERVER_BACKDROP_WINDOW_GROUP_NAME);
    const TInt htcleoWindowNameResult =
        apaName->SetWindowGroupName(iBackdropWindowGroup);
    HtcleoAknCapLog(0x0000E10Du, htcleoWindowNameResult, 0u);
    User::LeaveIfError(htcleoWindowNameResult);
    CleanupStack::PopAndDestroy(); //apaName
    HtcleoAknCapLog(0x0000E10Eu, KErrNone, 0u);
''',
            "window group publish",
        )

        source = replace_once(
            source,
            '''    wsSession.SetKeyboardRepeatRate(KAknKeyboardRepeatInitialDelay, KAknStandardKeyboardRepeatRate); 
 
    // Disable some of wserv hotkeys if not in RnD mode.
''',
            '''    wsSession.SetKeyboardRepeatRate(KAknKeyboardRepeatInitialDelay, KAknStandardKeyboardRepeatRate); 
    HtcleoAknCapLog(0x0000E10Fu, KErrNone, 0u);
 
    // Disable some of wserv hotkeys if not in RnD mode.
''',
            "WServ settings",
        )

        source = replace_once(
            source,
            '''        User::LeaveIfError(wsSession.ClearHotKeys(EHotKeyOff));       
        }

    // Create statuspane & SGcs
''',
            '''        User::LeaveIfError(wsSession.ClearHotKeys(EHotKeyOff));       
        }
    HtcleoAknCapLog(0x0000E110u, KErrNone, 0u);

    // Create statuspane & SGcs
''',
            "hotkeys",
        )

        source = replace_once(
            source,
            '''            iEikonEnv->StatusPaneCoreResId());
        }

    iSgcs = CEikSgcServer::NewL();
''',
            '''            iEikonEnv->StatusPaneCoreResId());
        }
    HtcleoAknCapLog(0x0000E111u, KErrNone, iStatusPane ? 1u : 0u);

    iSgcs = CEikSgcServer::NewL();
    HtcleoAknCapLog(0x0000E112u, KErrNone, iSgcs ? 1u : 0u);
''',
            "status pane and SGC",
        )

        source = replace_once(
            source,
            '''    iSgcs->HandleWindowGroupParamChangeL(rootWin.Identifier(), EFalse, 0, 0, KAknScreenModeUnset);

    // create a high priority key filter
''',
            '''    iSgcs->HandleWindowGroupParamChangeL(rootWin.Identifier(), EFalse, 0, 0, KAknScreenModeUnset);
    HtcleoAknCapLog(0x0000E113u, KErrNone, 0u);

    // create a high priority key filter
''',
            "SGC initial event",
        )

        source = replace_once(
            source,
            '''    iKeyCaptureControl=new(ELeave) CAknServKeyFilter();
    iKeyCaptureControl->ConstructL(*this);

    TFileName fileName(KEikSrvUIResFileName);
''',
            '''    iKeyCaptureControl=new(ELeave) CAknServKeyFilter();
    iKeyCaptureControl->ConstructL(*this);
    HtcleoAknCapLog(0x0000E114u, KErrNone, iKeyCaptureControl ? 1u : 0u);

    TFileName fileName(KEikSrvUIResFileName);
''',
            "key filter",
        )

        source = replace_once(
            source,
            '''    BaflUtils::NearestLanguageFile(iEikonEnv->FsSession(),fileName);
    iResourceFileOffset=iCoeEnv->AddResourceFileL(fileName);
    
    // MMC unlocker
    iMMCUnlock = CAknMMCPasswordRequester::NewL();
''',
            '''    BaflUtils::NearestLanguageFile(iEikonEnv->FsSession(),fileName);
    iResourceFileOffset=iCoeEnv->AddResourceFileL(fileName);
    HtcleoAknCapLog(0x0000E115u, KErrNone, (TUint32)iResourceFileOffset);
    
    // MMC unlocker
    iMMCUnlock = CAknMMCPasswordRequester::NewL();
    HtcleoAknCapLog(0x0000E116u, KErrNone, iMMCUnlock ? 1u : 0u);
''',
            "resource and MMC",
        )

        source = replace_once(
            source,
            '''#endif

    // Start OOM watcher thread when scheduler is running
''',
            '''#endif
    HtcleoAknCapLog(0x0000E117u, KErrNone, 0u);

    // Start OOM watcher thread when scheduler is running
''',
            "priority",
        )

        source = replace_once(
            source,
            '''    iIdler = CIdle::NewL(CActive::EPriorityIdle);
    iIdler->Start(TCallBack(StartOOM, this));
    SetAliasKeyCodeResolverL(this);       
''',
            '''    iIdler = CIdle::NewL(CActive::EPriorityIdle);
    iIdler->Start(TCallBack(StartOOM, this));
    SetAliasKeyCodeResolverL(this);       
    HtcleoAknCapLog(0x0000E118u, KErrNone, iIdler ? 1u : 0u);
''',
            "idler and alias resolver",
        )

        source = replace_once(
            source,
            '''    TInt err = RProperty::Define(
        KPSUidAvkonInternal, 
        KAknIdleAppWindowGroupId, 
        RProperty::EInt, 
        KPassReadPolicy,  // None
        KWriteDDPolicy);  // WriteDeviceData
        
    if (err != KErrAlreadyExists)
''',
            '''    TInt err = RProperty::Define(
        KPSUidAvkonInternal, 
        KAknIdleAppWindowGroupId, 
        RProperty::EInt, 
        KPassReadPolicy,  // None
        KWriteDDPolicy);  // WriteDeviceData
    HtcleoAknCapLog(0x0000E119u, err, 0u);
        
    if (err != KErrAlreadyExists)
''',
            "idle property",
        )

        source = replace_once(
            source,
            '''    KAknMenuOptionNoTaskSwapper, 
    RProperty::EInt); 
               
    if ( err != KErrNone && err != KErrAlreadyExists )
''',
            '''    KAknMenuOptionNoTaskSwapper, 
    RProperty::EInt); 
    HtcleoAknCapLog(0x0000E11Au, err, 0u);
               
    if ( err != KErrNone && err != KErrAlreadyExists )
''',
            "task swapper property",
        )

        source = replace_once(
            source,
            '''    User::LeaveIfError(iGlobalNotesAllowedProperty.Attach(
        KPSUidUikon, 
        KUikGlobalNotesAllowed));        

    iGlobalNotesAllowedSubscriber = new (ELeave) CPropertySubscriber(
''',
            '''    const TInt htcleoGlobalNotesAttach =
        iGlobalNotesAllowedProperty.Attach(KPSUidUikon, KUikGlobalNotesAllowed);
    HtcleoAknCapLog(0x0000E11Bu, htcleoGlobalNotesAttach, 0u);
    User::LeaveIfError(htcleoGlobalNotesAttach);        

    iGlobalNotesAllowedSubscriber = new (ELeave) CPropertySubscriber(
''',
            "global notes attach",
        )

        source = replace_once(
            source,
            '''    iGlobalNotesAllowedSubscriber->Subscribe();
    
    // Start listening "telephony idle uid" property.
''',
            '''    iGlobalNotesAllowedSubscriber->Subscribe();
    HtcleoAknCapLog(0x0000E11Cu, KErrNone,
        iGlobalNotesAllowedSubscriber ? 1u : 0u);
    
    // Start listening "telephony idle uid" property.
''',
            "global notes subscriber",
        )

        source = replace_once(
            source,
            '''    User::LeaveIfError(iTelephonyIdleUidProperty.Attach(
        KPSUidAiInformation, 
        KActiveIdleUid));

    iTelephonyIdleUidSubscriber = new (ELeave) CPropertySubscriber(
''',
            '''    const TInt htcleoIdleUidAttach =
        iTelephonyIdleUidProperty.Attach(KPSUidAiInformation, KActiveIdleUid);
    HtcleoAknCapLog(0x0000E11Du, htcleoIdleUidAttach, 0u);
    User::LeaveIfError(htcleoIdleUidAttach);

    iTelephonyIdleUidSubscriber = new (ELeave) CPropertySubscriber(
''',
            "telephony idle attach",
        )

        source = replace_once(
            source,
            '''    iTelephonyIdleUidSubscriber->Subscribe();    
#ifdef RD_INTELLIGENT_TEXT_INPUT
''',
            '''    iTelephonyIdleUidSubscriber->Subscribe();    
    HtcleoAknCapLog(0x0000E11Eu, KErrNone,
        iTelephonyIdleUidSubscriber ? 1u : 0u);
#ifdef RD_INTELLIGENT_TEXT_INPUT
''',
            "telephony idle subscriber",
        )

        source = replace_once(
            source,
            '''#endif

    // Create capserver discreetpopuphandler     
''',
            '''#endif
    HtcleoAknCapLog(0x0000E11Fu, KErrNone, 0u);

    // Create capserver discreetpopuphandler     
''',
            "Pti block",
        )

        source = replace_once(
            source,
            '''    // Create capserver discreetpopuphandler     
    CAknCapServerDiscreetPopupHandler::CreateDiscreetPopupHandlerL();     
	
    LoadAlternateFsPlugin();
''',
            '''    // Create capserver discreetpopuphandler     
    CAknCapServerDiscreetPopupHandler::CreateDiscreetPopupHandlerL();     
    HtcleoAknCapLog(0x0000E120u, KErrNone, 0u);
	
    LoadAlternateFsPlugin();
    HtcleoAknCapLog(0x0000E121u, KErrNone, iAlternateFS ? 1u : 0u);
''',
            "popup and alternate FSW",
        )

        source = replace_once(
            source,
            '''        iFSControl= new (ELeave) CAknFastSwapWindowControl(*this);
        iFSControl->ConstructL();
        }
	ProcessInitFlipStatus();
    }
''',
            '''        iFSControl= new (ELeave) CAknFastSwapWindowControl(*this);
        iFSControl->ConstructL();
        }
    HtcleoAknCapLog(0x0000E122u, KErrNone, iFSControl ? 1u : 0u);
	ProcessInitFlipStatus();
    HtcleoAknCapLog(0x0000E123u, KErrNone, 0u);
    HtcleoAknCapLog(0x0000E124u, KErrNone, 0u);
    }
''',
            "ConstructL tail",
        )

        source = replace_once(
            source,
            '''LOCAL_C CApaApplication* NewApplication()
    {
    return new CAknCapServerApplication();
    }   
    
GLDEF_C TInt E32Main()
    {
    return EikStart::RunApplication(NewApplication);
    }
''',
            '''LOCAL_C CApaApplication* NewApplication()
    {
    HtcleoAknCapLog(0x0000E010u, KErrNone, 0u);
    CAknCapServerApplication* application = new CAknCapServerApplication();
    HtcleoAknCapLog(0x0000E011u, KErrNone, application ? 1u : 0u);
    return application;
    }   
    
GLDEF_C TInt E32Main()
    {
    HtcleoAknCapLog(0x0000E000u, KErrNone, 0u);
    const TInt result = EikStart::RunApplication(NewApplication);
    HtcleoAknCapLog(0x0000E001u, result, 0u);
    return result;
    }
''',
            "E32Main and factory",
        )

    if EIKSTART_MARKER not in source:
        source = replace_once(
            source,
            "#include <eikstart.h>\n",
            "#include <eikstart.h>\n" + EIKSTART_INCLUDES,
            "isolated EikStart includes",
        )
        source = replace_once(
            source,
            "GLDEF_C TInt E32Main()\n",
            EIKSTART_WRAPPER + "\nGLDEF_C TInt E32Main()\n",
            "isolated EikStart wrapper",
        )
        source = replace_once(
            source,
            "const TInt result = EikStart::RunApplication(NewApplication);",
            "const TInt result = HtcleoRunAknCapApplication(NewApplication);",
            "isolated EikStart call",
        )

    # Early V2 drafts called a private/protected constructor-error accessor.
    # The exported ConstructAppFromCommandLineL starts with the exact same
    # preflight and leaves before mutation, so normalize installed drafts to an
    # exported-only path without changing the resulting error.
    if EIKSTART_EXPORT_MARKER not in source:
        old_constructor_block = '''        const TInt constructorError = env->CoeEnvConstructorError();
        HtcleoAknCapLog(0x0000E207u, constructorError, 0u);
        if (constructorError != KErrNone)
            {
            error = constructorError;
            }
        else
            {
            HtcleoAknCapLog(0x0000E208u, KErrNone, 0u);
            TRAP(error,
                env->ConstructAppFromCommandLineL(
                    aApplicationFactory, *commandLine));
            HtcleoAknCapLog(0x0000E209u, error, 0u);
            }
'''
        exported_constructor_block = '''        // HTCLEO_AKNCAPSERVER_EIKSTART_EXPORTED_ONLY_V3
        // ConstructAppFromCommandLineL begins with the same constructor-error
        // preflight as EikStart, then leaves before mutation on failure.  Using
        // it directly avoids importing a private/protected eikcore symbol.
        HtcleoAknCapLog(0x0000E207u, KErrNone, 1u);
        HtcleoAknCapLog(0x0000E208u, KErrNone, 0u);
        TRAP(error,
            env->ConstructAppFromCommandLineL(
                aApplicationFactory, *commandLine));
        HtcleoAknCapLog(0x0000E209u, error, 0u);
'''
        source = replace_once(
            source,
            old_constructor_block,
            exported_constructor_block,
            "exported-only constructor preflight",
        )

    if EIKSTART_CONSTRUCTOR_MARKER not in source:
        source = replace_once(
            source,
            '''// This is the UREL EikStart::RunApplication flow, scoped to akncapserver.exe.
static TInt HtcleoRunAknCapApplication(
''',
            '''// This is the UREL EikStart::RunApplication flow, scoped to akncapserver.exe.
// HTCLEO_AKNCAPSERVER_CONSTRUCTOR_ERROR_V4
class CHtcleoAknCapEikonEnv : public CEikonEnv
    {
public:
    TInt HtcleoConstructorError() const
        {
        return CoeEnvConstructorError();
        }
    };

static TInt HtcleoRunAknCapApplication(
''',
            "isolated constructor-error accessor",
        )
        source = replace_once(
            source,
            "CEikonEnv* env = new CEikonEnv;",
            "CHtcleoAknCapEikonEnv* env = new CHtcleoAknCapEikonEnv;",
            "isolated constructor-error environment",
        )
        source = replace_once(
            source,
            '''    else
        {
        // HTCLEO_AKNCAPSERVER_EIKSTART_EXPORTED_ONLY_V3
''',
            '''    else
        {
        const TInt constructorError = env->HtcleoConstructorError();
        HtcleoAknCapLog(0x0000E212u, constructorError,
            CEikonEnv::Static() == env ? 1u : 0u);
        // HTCLEO_AKNCAPSERVER_EIKSTART_EXPORTED_ONLY_V3
''',
            "constructor-error durable record",
        )

    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(source, mmp, widget_header, compatibility_headers)
    source_path.write_text(source, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    widget_header_path.write_text(widget_header, encoding="utf-8")
    for name, path in compatibility_header_paths.items():
        path.write_text(compatibility_headers[name], encoding="latin-1")
    print("HTCLEO_AKNCAPSERVER_STARTUP_LOG=installed stages=E000-E212")


if __name__ == "__main__":
    main()
