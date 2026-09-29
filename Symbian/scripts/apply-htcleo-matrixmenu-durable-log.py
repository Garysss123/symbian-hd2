#!/usr/bin/env python3
"""Install a bounded durable MatrixMenu lifecycle trace.

Iteration 492 completes AppArc startup and the UI-services command list, then
stops in the critical-apps list at the MultipleWait following the deferred
matrixmenu.exe StartApp command.  Iteration 493 proves MatrixMenu E32Main but
does not reach its application factory.  In addition to the existing lifecycle
records, this transform therefore expands the release EikStart flow locally in
matrixmenu.exe and records each returning pre-factory boundary.  It changes no
wait, rendezvous, display, input, error, or application policy and does not
replace the shared eikcore.dll.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_DURABLE_LOG_V1"
EIKSTART_MARKER = "HTCLEO_MATRIXMENU_EIKSTART_DURABLE_LOG_V2"
HN_INCLUDE_BLOCK = r'''USERINCLUDE     ../../../hierarchynavigator/hnengine/inc
USERINCLUDE     ../../../hierarchynavigator/hnmetadatamodel/inc
USERINCLUDE     ../../../hierarchynavigator/hnpresentationmodel/inc
USERINCLUDE     ../../../hierarchynavigator/hnutilities/inc
'''

EIKSTART_INCLUDES = r'''#include <f32file.h>
#include <bautils.h>
#include <basched.h>
#include <eikenv.h>
#include <eikdebug.h>
#include <eikpanic.h>
#include <uiklafgt/eikcore.rsg>
'''

EIKSTART_WRAPPER = r'''
// HTCLEO_MATRIXMENU_EIKSTART_DURABLE_LOG_V2
// Release EikStart::RunApplication flow, scoped to matrixmenu.exe only.
class CHtcleoMatrixMenuEikonEnv : public CEikonEnv
    {
public:
    TInt HtcleoConstructorError() const
        {
        return CoeEnvConstructorError();
        }
    };

static TInt HtcleoRunMatrixMenuApplication(
    TApaApplicationFactory aApplicationFactory)
    {
    HtcleoMenuLog(0x4D4D1000u, KErrNone, 0u);
    CApaCommandLine* commandLine = NULL;
    TBool disableShutdownChecks = EFalse;
    TInt error = CApaCommandLine::GetCommandLineFromProcessEnvironment(
        commandLine);
    HtcleoMenuLog(0x4D4D1001u, error, commandLine ? 1u : 0u);
    if (error)
        {
        goto done;
        }

    User::__DbgMarkStart(RHeap::EUser);
    HtcleoMenuLog(0x4D4D1002u, KErrNone, 0u);

    {
    TFileName executableFileName = RProcess().FileName();
    HtcleoMenuLog(0x4D4D1003u, KErrNone,
        (TUint32)executableFileName.Length());
    error = User::RenameThread(TParsePtrC(executableFileName).Name());
    HtcleoMenuLog(0x4D4D1004u, error, 0u);
    if (error)
        {
        goto done;
        }
    }

    {
    HtcleoMenuLog(0x4D4D1005u, KErrNone, 0u);
    CHtcleoMatrixMenuEikonEnv* env = new CHtcleoMatrixMenuEikonEnv;
    HtcleoMenuLog(0x4D4D1006u,
        env ? KErrNone : KErrNoMemory, env ? 1u : 0u);
    if (!env)
        {
        error = KErrNoMemory;
        }
    else
        {
        const TInt constructorError = env->HtcleoConstructorError();
        HtcleoMenuLog(0x4D4D1012u, constructorError,
            CEikonEnv::Static() == env ? 1u : 0u);
        HtcleoMenuLog(0x4D4D1007u, KErrNone, 1u);
        HtcleoMenuLog(0x4D4D1008u, KErrNone, 0u);
        TRAP(error,
            env->ConstructAppFromCommandLineL(
                aApplicationFactory, *commandLine));
        HtcleoMenuLog(0x4D4D1009u, error, 0u);
        }

    delete commandLine;
    commandLine = NULL;
    HtcleoMenuLog(0x4D4D100Au, error, 0u);

    if (!error)
        {
        HtcleoMenuLog(0x4D4D100Bu, KErrNone, 0u);
        env->Execute();
        HtcleoMenuLog(0x4D4D100Cu, KErrNone, 0u);
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
        HtcleoMenuLog(0x4D4D100Du, unhandledError,
            (TUint32)error);
        }

    if (env != NULL)
        {
        disableShutdownChecks = env->DisableShutdownChecks();
        HtcleoMenuLog(0x4D4D100Eu, KErrNone,
            disableShutdownChecks ? 1u : 0u);
        env->DestroyEnvironment();
        HtcleoMenuLog(0x4D4D100Fu, KErrNone, 0u);
        }

    if (!error)
        {
        env = NULL;
        }
    }

done:
    delete commandLine;
    HtcleoMenuLog(0x4D4D1010u, error,
        disableShutdownChecks ? 1u : 0u);
    if (!disableShutdownChecks)
        {
        User::__DbgMarkEnd(RHeap::EUser, 0);
        }
    HtcleoMenuLog(0x4D4D1011u, error,
        disableShutdownChecks ? 1u : 0u);
    return error;
    }
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HEADER = r'''#ifndef HTCLEO_MENU_LOG_H
#define HTCLEO_MENU_LOG_H

#include <e32std.h>

void HtcleoMenuLog(TUint32 aStage, TInt aResult, TUint32 aDetail);

#endif
'''


LOGGER = r'''#include "htcleomenulog.h"

#include <e32base.h>
#include <f32file.h>

// HTCLEO_MATRIXMENU_DURABLE_LOG_V1
void HtcleoMenuLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoMenuLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMenuLogPath, "C:\\Symbian3\\MENULOG.TXT");
    r = fs.MkDirAll(KHtcleoMenuLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMenuLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMenuLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoMenuPrefix, "HTCLEO_MENU ");
        TBuf8<96> record;
        record.Append(KHtcleoMenuPrefix);
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
            file.Flush();
            }
        }
    file.Close();
    fs.Close();
    }
'''


def install(component: Path) -> None:
    src = component / "src"
    inc = component / "inc"
    group = component / "group"
    logger_header = inc / "htcleomenulog.h"
    logger_source = src / "htcleomenulog.cpp"
    mmgui_path = src / "mmgui.cpp"
    app_path = src / "mmapplication.cpp"
    document_path = src / "mmdocument.cpp"
    appui_path = src / "mmappui.cpp"
    mmp_path = group / "matrixmenu.mmp"

    mmgui = mmgui_path.read_text(encoding="latin-1")
    app = app_path.read_text(encoding="latin-1")
    document = document_path.read_text(encoding="latin-1")
    appui = appui_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    already = logger_source.exists() and MARKER in logger_source.read_text(
        encoding="latin-1"
    )
    if not already:
        mmgui = replace_once(
            mmgui,
            '#include "mmapplication.h"\n',
            '#include "mmapplication.h"\n#include "htcleomenulog.h"\n',
            "mmgui logger include",
        )
        mmgui = replace_once(
            mmgui,
            '''LOCAL_C CApaApplication* NewApplication()
\t{
\treturn new CMmApplication;
\t}
''',
            '''LOCAL_C CApaApplication* NewApplication()
\t{
    HtcleoMenuLog(0x4D4D0001u, KErrNone, 0u);
    CApaApplication* application = new CMmApplication;
    HtcleoMenuLog(0x4D4D0002u,
        application ? KErrNone : KErrNoMemory, application ? 1u : 0u);
\treturn application;
\t}
''',
            "NewApplication trace",
        )
        mmgui = replace_once(
            mmgui,
            '''GLDEF_C TInt E32Main()
\t{
\treturn EikStart::RunApplication( NewApplication );
\t}
''',
            '''GLDEF_C TInt E32Main()
\t{
    HtcleoMenuLog(0x4D4D0000u, KErrNone, 0u);
    const TInt result = EikStart::RunApplication( NewApplication );
    HtcleoMenuLog(0x4D4D0003u, result, 0u);
\treturn result;
\t}
''',
            "E32Main trace",
        )

        app = replace_once(
            app,
            '#include "mmguiconstants.h"\n',
            '#include "mmguiconstants.h"\n#include "htcleomenulog.h"\n',
            "application logger include",
        )
        app = replace_once(
            app,
            '''CApaDocument* CMmApplication::CreateDocumentL()
\t{
\t// Create a Matrix Menu document, and return a pointer to it
\treturn ( static_cast<CApaDocument*>
\t\t\t\t\t( CMmDocument::NewL( *this ) ) );
\t}
''',
            '''CApaDocument* CMmApplication::CreateDocumentL()
\t{
    HtcleoMenuLog(0x4D4D0100u, KErrNone, 0u);
\t// Create a Matrix Menu document, and return a pointer to it
    CApaDocument* document = static_cast<CApaDocument*>(
        CMmDocument::NewL(*this));
    HtcleoMenuLog(0x4D4D0101u, KErrNone, document ? 1u : 0u);
\treturn document;
\t}
''',
            "CreateDocumentL trace",
        )

        document = replace_once(
            document,
            '#include <apgwgnam.h>\n',
            '#include <apgwgnam.h>\n#include "htcleomenulog.h"\n',
            "document logger include",
        )
        document = replace_once(
            document,
            '''CMmDocument* CMmDocument::NewL( CEikApplication& aApp )
\t{
\tCMmDocument* self = NewLC( aApp );
\tCleanupStack::Pop( self );
\treturn self;
\t}
''',
            '''CMmDocument* CMmDocument::NewL( CEikApplication& aApp )
\t{
    HtcleoMenuLog(0x4D4D0200u, KErrNone, 0u);
\tCMmDocument* self = NewLC( aApp );
\tCleanupStack::Pop( self );
    HtcleoMenuLog(0x4D4D0201u, KErrNone, self ? 1u : 0u);
\treturn self;
\t}
''',
            "document NewL trace",
        )
        document = replace_once(
            document,
            '''CMmDocument* CMmDocument::NewLC( CEikApplication& aApp )
\t{
\tCMmDocument* self =
\t\tnew ( ELeave ) CMmDocument( aApp );

\tCleanupStack::PushL( self );
\tself->ConstructL();
\treturn self;
\t}
''',
            '''CMmDocument* CMmDocument::NewLC( CEikApplication& aApp )
\t{
    HtcleoMenuLog(0x4D4D0210u, KErrNone, 0u);
\tCMmDocument* self =
\t\tnew ( ELeave ) CMmDocument( aApp );
    HtcleoMenuLog(0x4D4D0211u, KErrNone, self ? 1u : 0u);

\tCleanupStack::PushL( self );
\tself->ConstructL();
    HtcleoMenuLog(0x4D4D0212u, KErrNone, 0u);
\treturn self;
\t}
''',
            "document NewLC trace",
        )
        document = replace_once(
            document,
            '''CEikAppUi* CMmDocument::CreateAppUiL()
\t{
\t// Create the application user interface, and return a pointer to it
\t// the framework takes ownership of this object
\treturn ( static_cast <CEikAppUi*> ( new ( ELeave ) CMmAppUi ) );
\t}
''',
            '''CEikAppUi* CMmDocument::CreateAppUiL()
\t{
    HtcleoMenuLog(0x4D4D0220u, KErrNone, 0u);
\t// Create the application user interface, and return a pointer to it
\t// the framework takes ownership of this object
    CEikAppUi* appUi = static_cast<CEikAppUi*>(new (ELeave) CMmAppUi);
    HtcleoMenuLog(0x4D4D0221u, KErrNone, appUi ? 1u : 0u);
\treturn appUi;
\t}
''',
            "CreateAppUiL trace",
        )

        appui = replace_once(
            appui,
            '#include "mmappkeyhandler.h"\n',
            '#include "mmappkeyhandler.h"\n#include "htcleomenulog.h"\n',
            "appui logger include",
        )
        start = appui.index("void CMmAppUi::ConstructL()")
        end = appui.index("TBool CMmAppUi::IsRootdisplayedL()", start)
        construct = appui[start:end]
        anchors = (
            ("    {\n", "    {\n    HtcleoMenuLog(0x4D4D0300u, KErrNone, 0u);\n"),
            ("    iEikonEnv->SetSystem( ETrue );\n", "    iEikonEnv->SetSystem( ETrue );\n    HtcleoMenuLog(0x4D4D0301u, KErrNone, 0u);\n"),
            ("    BaseConstructL( appUiFlags );\n", "    HtcleoMenuLog(0x4D4D0302u, KErrNone, (TUint32)appUiFlags);\n    BaseConstructL( appUiFlags );\n    HtcleoMenuLog(0x4D4D0303u, KErrNone, 0u);\n"),
            ("    FeatureManager::InitializeLibL();\n", "    FeatureManager::InitializeLibL();\n    HtcleoMenuLog(0x4D4D0304u, KErrNone, 0u);\n"),
            ("    StartLayoutSwitchFullScreen( AknTransEffect::EApplicationStart );\n", "    StartLayoutSwitchFullScreen( AknTransEffect::EApplicationStart );\n    HtcleoMenuLog(0x4D4D0305u, KErrNone, 0u);\n"),
            ("    RefreshUiPanesL( ETrue );\n", "    RefreshUiPanesL( ETrue );\n    HtcleoMenuLog(0x4D4D0306u, KErrNone, 0u);\n"),
            ("    StatusPane()->SwitchLayoutL( R_AVKON_STATUS_PANE_LAYOUT_USUAL );\n", "    StatusPane()->SwitchLayoutL( R_AVKON_STATUS_PANE_LAYOUT_USUAL );\n    HtcleoMenuLog(0x4D4D0307u, KErrNone, 0u);\n"),
            ("    iDummyTemplateLib = CMmTemplateLibrary::NewL();\n", "    iDummyTemplateLib = CMmTemplateLibrary::NewL();\n    HtcleoMenuLog(0x4D4D0308u, KErrNone, iDummyTemplateLib ? 1u : 0u);\n"),
            ("            this, iDummyTemplateLib );\n", "            this, iDummyTemplateLib );\n    HtcleoMenuLog(0x4D4D0309u, KErrNone, iDummyContainer ? 1u : 0u);\n"),
            ("            ECoeStackFlagRefusesFocus | ECoeStackFlagRefusesAllKeys );\n", "            ECoeStackFlagRefusesFocus | ECoeStackFlagRefusesAllKeys );\n    HtcleoMenuLog(0x4D4D030Au, KErrNone, 0u);\n"),
            ("    iHNInterface = CHnEngine::NewL( *this );\n", "    iHNInterface = CHnEngine::NewL( *this );\n    HtcleoMenuLog(0x4D4D030Bu, KErrNone, iHNInterface ? 1u : 0u);\n"),
            ("    iTemplateLibrary = CMmTemplateLibrary::NewL();\n", "    iTemplateLibrary = CMmTemplateLibrary::NewL();\n    HtcleoMenuLog(0x4D4D030Cu, KErrNone, iTemplateLibrary ? 1u : 0u);\n"),
            ("    InitializeL();\n", "    HtcleoMenuLog(0x4D4D030Du, KErrNone, 0u);\n    InitializeL();\n    HtcleoMenuLog(0x4D4D030Eu, KErrNone, 0u);\n"),
            ("    iMmExtManager = CMMExtensionManager::NewL( *this );\n", "    iMmExtManager = CMMExtensionManager::NewL( *this );\n    HtcleoMenuLog(0x4D4D030Fu, KErrNone, iMmExtManager ? 1u : 0u);\n"),
            ("    iSkinSrvSession.Connect(this);\n", "    iSkinSrvSession.Connect(this);\n    HtcleoMenuLog(0x4D4D0310u, KErrNone, 0u);\n"),
            ("    iAppkeyHandler = CMmAppkeyHandler::NewL();\n", "    iAppkeyHandler = CMmAppkeyHandler::NewL();\n    HtcleoMenuLog(0x4D4D0311u, KErrNone, iAppkeyHandler ? 1u : 0u);\n"),
            ("    RProperty::Define( KMMenuPSCat, KMMenuLastViewKey, RProperty::EText );\n", "    RProperty::Define( KMMenuPSCat, KMMenuLastViewKey, RProperty::EText );\n    HtcleoMenuLog(0x4D4D0312u, KErrNone, 0u);\n"),
        )
        for old, new in anchors:
            construct = replace_once(construct, old, new, f"ConstructL anchor {old.strip()}")
        appui = appui[:start] + construct + appui[end:]

        if "SOURCE          htcleomenulog.cpp" not in mmp:
            mmp = replace_once(
                mmp,
                "SOURCE          mmgui.cpp\n",
                "SOURCE          mmgui.cpp\nSOURCE          htcleomenulog.cpp\n",
                "logger source in mmp",
            )
        if "LIBRARY           efsrv.lib" not in mmp:
            mmp = replace_once(
                mmp,
                "LIBRARY           euser.lib\n",
                "LIBRARY           euser.lib\nLIBRARY           efsrv.lib\n",
                "efsrv library in mmp",
            )

        if HN_INCLUDE_BLOCK not in mmp:
            mmp = replace_once(
                mmp,
                "USERINCLUDE     ../loc\n",
                "USERINCLUDE     ../loc\n" + HN_INCLUDE_BLOCK,
                "hierarchy navigator include closure",
            )

        logger_header.write_text(HEADER, encoding="latin-1")
        logger_source.write_text(LOGGER, encoding="latin-1")
        mmgui_path.write_text(mmgui, encoding="latin-1")
        app_path.write_text(app, encoding="latin-1")
        document_path.write_text(document, encoding="latin-1")
        appui_path.write_text(appui, encoding="latin-1")
        mmp_path.write_text(mmp, encoding="latin-1")

    # A first isolated build can expose missing transitive exports after the
    # lifecycle transform was already installed. Keep this repair idempotent
    # so a fail-closed rebuild can resume from the exact same source policy.
    if HN_INCLUDE_BLOCK not in mmp:
        mmp = replace_once(
            mmp,
            "USERINCLUDE     ../loc\n",
            "USERINCLUDE     ../loc\n" + HN_INCLUDE_BLOCK,
            "hierarchy navigator include closure resume",
        )
        mmp_path.write_text(mmp, encoding="latin-1")

    # Iteration 493 reaches E32Main but not NewApplication.  Keep all existing
    # lifecycle instrumentation and replace only the single EikStart call with
    # a source-equivalent, MatrixMenu-local release flow so every pre-factory
    # returning boundary can be recorded without touching shared eikcore.dll.
    mmgui = mmgui_path.read_text(encoding="latin-1")
    if EIKSTART_MARKER not in mmgui:
        mmgui = replace_once(
            mmgui,
            "#include <eikstart.h>\n",
            "#include <eikstart.h>\n" + EIKSTART_INCLUDES,
            "local EikStart includes",
        )
        mmgui = replace_once(
            mmgui,
            "LOCAL_C CApaApplication* NewApplication()\n",
            EIKSTART_WRAPPER + "\nLOCAL_C CApaApplication* NewApplication()\n",
            "local EikStart wrapper",
        )
        mmgui = replace_once(
            mmgui,
            "const TInt result = EikStart::RunApplication( NewApplication );",
            "const TInt result = HtcleoRunMatrixMenuApplication(NewApplication);",
            "local EikStart call",
        )
        mmgui_path.write_text(mmgui, encoding="latin-1")

    sources = "\n".join(
        path.read_text(encoding="latin-1")
        for path in (logger_source, mmgui_path, app_path, document_path, appui_path)
    )
    expected = (
        0x4D4D0000, 0x4D4D0001, 0x4D4D0002, 0x4D4D0003,
        0x4D4D0100, 0x4D4D0101,
        0x4D4D0200, 0x4D4D0201, 0x4D4D0210, 0x4D4D0211,
        0x4D4D0212, 0x4D4D0220, 0x4D4D0221,
        *range(0x4D4D0300, 0x4D4D0313),
        *range(0x4D4D1000, 0x4D4D1013),
    )
    checks = {
        "marker": sources.count(MARKER) == 1,
        "local EikStart marker": sources.count(EIKSTART_MARKER) == 1,
        "durable path": sources.count(r"C:\\Symbian3\\MENULOG.TXT") == 1,
        "all stages": all(sources.count(f"0x{stage:08X}u") == 1 for stage in expected),
        "local release EikStart": (
            sources.count("HtcleoRunMatrixMenuApplication(NewApplication)") == 1
            and sources.count("env->ConstructAppFromCommandLineL(") == 1
            and sources.count("env->Execute();") == 1
            and "EikStart::RunApplication( NewApplication )" not in sources
        ),
        "stock BaseConstructL": sources.count("BaseConstructL( appUiFlags );") == 1,
        "stock InitializeL": sources.count("    InitializeL();") >= 1,
        "logger source": mmp.count("SOURCE          htcleomenulog.cpp") == 1,
        "efsrv library": mmp.count("LIBRARY           efsrv.lib") == 1,
        "hierarchy navigator include closure": mmp.count(HN_INCLUDE_BLOCK) == 1,
        "no delay": "User::After" not in logger_source.read_text(encoding="latin-1"),
        "no display probe or unscoped HAL": (
            "HalFunction" not in sources
            or (
                sources.count("HTCLEO_MATRIXMENU_FOCUS_TOUCH_REARM_V4") == 1
                and sources.count("UserSvr::HalFunction(") == 6
                and sources.count("EHalGroupPlatformSpecific2, 10") == 1
                and sources.count("EHalGroupPlatformSpecific2, 11") == 3
                and sources.count("EHalGroupPlatformSpecific2, 12") == 1
                and sources.count("EHalGroupPlatformSpecific2, 13") == 1
                and "HalFunction(EHalGroupDisplay" not in sources
                and "HalFunction(EHalGroupScreen" not in sources
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MatrixMenu trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu"
    )
    install(component)
    print(
        "HTCLEO_MATRIXMENU_DURABLE_LOG=installed "
        "stages=4D4D0000-4D4D0312,4D4D1000-4D4D1012"
    )


if __name__ == "__main__":
    main()
