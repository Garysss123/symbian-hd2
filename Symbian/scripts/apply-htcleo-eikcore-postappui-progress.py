#!/usr/bin/env python3
"""Trace the MatrixMenu post-AppUi Eikon tail without changing behavior.

Iteration 539 proves that MatrixMenu's own CMmAppUi::ConstructL body, the real
MenuContent GetList path, and HN initialization all return.  The next unknown
is therefore the stock CEikonEnv tail between CEikDocument::PrepareToEditL()
and SetAppReady(), followed by the asynchronous startup-view activation.

The existing SID-gated HtcleoEikCorePreFactoryTrace helper writes durable
MENULOG records for MatrixMenu and a property for AknCap.  This transform only
adds returning boundaries around the existing calls; it adds no wait, retry,
error normalization, display operation, or control-flow change.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_POSTAPPUI_TRACE_V1"
ACTIVATOR_MARKER = "HTCLEO_EIKCORE_STARTUP_VIEW_ACTIVATOR_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "\tHtcleoEikCorePreFactoryTrace(0xE311u, serverDifferentiator);\n"
        "\t// Create the document object using the application factory\n"
        "\tCEikDocument& doc = *static_cast<CEikDocument*>(iProcess->AddNewDocumentL(aApplicationFactory));\n"
        "\tiProcess->SetMainDocument(&doc);\n"
        "\tUpdateTaskNameL();\n",
        "\t// HTCLEO_EIKCORE_POSTAPPUI_TRACE_V1\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE311u, serverDifferentiator);\n"
        "\t// Create the document object using the application factory\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE320u, KErrNone);\n"
        "\tCEikDocument& doc = *static_cast<CEikDocument*>(iProcess->AddNewDocumentL(aApplicationFactory));\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE321u, KErrNone);\n"
        "\tiProcess->SetMainDocument(&doc);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE322u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE323u, KErrNone);\n"
        "\tUpdateTaskNameL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE324u, KErrNone);\n",
        "document factory tail",
    )
    source = replace_once(
        source,
        "\t\tiEikEnvExtra->iAppServer->ConstructUniqueL(serverDifferentiator, app->AppDllUid());\n"
        "\t\t}\n\n"
        "\t// Prepare the document for editing, this includes creating the AppUi object\n"
        "\tdoc.PrepareToEditL(); // creates AppUi\n"
        "\tCEikAppUi& appUi = *EikAppUi();\n",
        "\t\tiEikEnvExtra->iAppServer->ConstructUniqueL(serverDifferentiator, app->AppDllUid());\n"
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE325u, serverDifferentiator);\n\n"
        "\t// Prepare the document for editing, this includes creating the AppUi object\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE326u, KErrNone);\n"
        "\tdoc.PrepareToEditL(); // creates AppUi\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE327u, KErrNone);\n"
        "\tCEikAppUi& appUi = *EikAppUi();\n",
        "PrepareToEdit boundary",
    )
    source = replace_once(
        source,
        "\tconst TBool runAppWithoutViews = (command==EApaCommandRunWithoutViews || command==EApaCommandBackgroundAndWithoutViews);\n"
        "\tif (!runAppWithoutViews)\n"
        "\t\tappUi.CheckInitializeViewsL(appUi.Application()->AppDllUid());\n\n"
        "\t// If the application is starting in the foreground, create a high-priority async view activator, \n"
        "\t// as the ViewSrv won't activate the top view automatically\n"
        "\tif (startAppInForeground && command!=EApaCommandViewActivate )\n"
        "\t\tiEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);\n\t\n"
        "\t// Get the file name associated with the document, and set it on the process CApaProcess object\n"
        "\tconst TBool doOpen = appUi.ProcessCommandParametersL(const_cast<CApaCommandLine&>(aCommandLine));\n",
        "\tconst TBool runAppWithoutViews = (command==EApaCommandRunWithoutViews || command==EApaCommandBackgroundAndWithoutViews);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE328u, runAppWithoutViews);\n"
        "\tif (!runAppWithoutViews)\n"
        "\t\t{\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE329u, KErrNone);\n"
        "\t\tappUi.CheckInitializeViewsL(appUi.Application()->AppDllUid());\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE32Au, KErrNone);\n"
        "\t\t}\n\n"
        "\t// If the application is starting in the foreground, create a high-priority async view activator, \n"
        "\t// as the ViewSrv won't activate the top view automatically\n"
        "\tconst TBool htcleoNeedsViewActivator =\n"
        "\t\t(startAppInForeground && command!=EApaCommandViewActivate);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE32Bu, htcleoNeedsViewActivator);\n"
        "\tif (htcleoNeedsViewActivator)\n"
        "\t\t{\n"
        "\t\tiEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);\n"
        "\t\t}\n\t\n"
        "\t// Get the file name associated with the document, and set it on the process CApaProcess object\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE32Du, KErrNone);\n"
        "\tconst TBool doOpen = appUi.ProcessCommandParametersL(const_cast<CApaCommandLine&>(aCommandLine));\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE32Eu, doOpen);\n",
        "views and command parameters",
    )
    source = replace_once(
        source,
        "\tTUnlimitedFileName* const modifiedDocumentName = TUnlimitedFileName::NewLC(aCommandLine.DocumentName());\n"
        "\tiProcess->SetMainDocFileNameL(*modifiedDocumentName);\n"
        "\tUpdateTaskNameL();\n"
        "\t\n\t\n"
        "\tTBool openByFileName = (modifiedDocumentName->Length());\n",
        "\tTUnlimitedFileName* const modifiedDocumentName = TUnlimitedFileName::NewLC(aCommandLine.DocumentName());\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE32Fu, modifiedDocumentName->Length());\n"
        "\tiProcess->SetMainDocFileNameL(*modifiedDocumentName);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE330u, KErrNone);\n"
        "\tUpdateTaskNameL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE331u, KErrNone);\n"
        "\t\n\t\n"
        "\tTBool openByFileName = (modifiedDocumentName->Length());\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE332u, openByFileName);\n",
        "document name tail",
    )
    source = replace_once(
        source,
        "\taCommandLine.GetFileByHandleL(file);\n"
        "\tTBool receivedFileHandle=EFalse;\n"
        "\tif (file.SubSessionHandle() != KNullHandle)\n",
        "\taCommandLine.GetFileByHandleL(file);\n"
        "\tTBool receivedFileHandle=EFalse;\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE333u, file.SubSessionHandle());\n"
        "\tif (file.SubSessionHandle() != KNullHandle)\n",
        "file handle boundary",
    )
    source = replace_once(
        source,
        "\tCleanupStack::PopAndDestroy(&file);\n"
        "\tif (openByFileName)\n"
        "\t\t{\n"
        "\t\tTRAP(err, docStore = doc.OpenFileL(doOpen, *modifiedDocumentName, FsSession()));\n"
        "\t\t}\n\t\t\n"
        "\tif (err==KErrCorrupt || err==KErrEof)\n",
        "\tCleanupStack::PopAndDestroy(&file);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE334u, err);\n"
        "\tif (openByFileName)\n"
        "\t\t{\n"
        "\t\tTRAP(err, docStore = doc.OpenFileL(doOpen, *modifiedDocumentName, FsSession()));\n"
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE335u, err);\n"
        "\t\t\n"
        "\tif (err==KErrCorrupt || err==KErrEof)\n",
        "open document boundary",
    )
    source = replace_once(
        source,
        "\tUser::LeaveIfError(err);\n"
        "\tif (docStore)\n"
        "\t    {\n"
        "\t    doc.SetEditStoreWithoutAppUiNotificationL(docStore);\n"
        "\t    iProcess->SetMainStore(docStore); // takes ownership of docStore\n"
        "\t    }\n"
        "   \tCleanupStack::Pop(&docStore);\n"
        "   \t\n"
        "\tif ((modifiedDocumentName->Length()>0) || receivedFileHandle)\n"
        "\t\tappUi.HandleModelChangeL();\n\n"
        "    CleanupStack::PopAndDestroy(modifiedDocumentName);\n\n"
        "    // If not, the app will Rendezvous at its convenience.\n"
        "    if( AppUi()->FrameworkCallsRendezvous() )\n"
        "\t\tRProcess::Rendezvous(KErrNone);\n"
        "    \t\n"
        " \tSetAppReady();\n"
        "\t}",
        "\tHtcleoEikCorePreFactoryTrace(0xE336u, err);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE337u, err);\n"
        "\tUser::LeaveIfError(err);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE338u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE339u, docStore ? 1 : 0);\n"
        "\tif (docStore)\n"
        "\t    {\n"
        "\t    doc.SetEditStoreWithoutAppUiNotificationL(docStore);\n"
        "\t    iProcess->SetMainStore(docStore); // takes ownership of docStore\n"
        "\t    }\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE33Au, KErrNone);\n"
        "   \tCleanupStack::Pop(&docStore);\n"
        "   \t\n"
        "\tconst TBool htcleoHasModelChange =\n"
        "\t\t((modifiedDocumentName->Length()>0) || receivedFileHandle);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE33Bu, htcleoHasModelChange);\n"
        "\tif (htcleoHasModelChange)\n"
        "\t\tappUi.HandleModelChangeL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE33Cu, KErrNone);\n\n"
        "    CleanupStack::PopAndDestroy(modifiedDocumentName);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE33Du, KErrNone);\n\n"
        "    // If not, the app will Rendezvous at its convenience.\n"
        "\tconst TBool htcleoFrameworkRendezvous =\n"
        "\t\tAppUi()->FrameworkCallsRendezvous();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE33Eu, htcleoFrameworkRendezvous);\n"
        "    if( htcleoFrameworkRendezvous )\n"
        "\t\tRProcess::Rendezvous(KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE33Fu, KErrNone);\n"
        "    \t\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE340u, KErrNone);\n"
        " \tSetAppReady();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE341u, KErrNone);\n"
        "\t}",
        "final framework tail",
    )
    source = replace_once(
        source,
        "void CEikStartUpViewActivator::RunL()\n"
        "\t{\n"
        "\tRWsSession& ws = iEnv.WsSession();\n"
        "\tconst TInt numWgs = ws.NumWindowGroups(0);\n"
        "\tCArrayFixFlat<TInt>* windowList = new(ELeave) CArrayFixFlat<TInt>(numWgs);\n"
        "\tCleanupStack::PushL(windowList);\n"
        "\tws.WindowGroupList(0, windowList);\n"
        "\tconst TInt wgId = iEnv.RootWin().Identifier();\n"
        "\tif ((ws.GetFocusWindowGroup() == wgId || (windowList->Count() > 0 && windowList->At(0) == wgId))  \n"
        "\t\t&& (iEnv.IsSchedulerRunning()))\n"
        "\t\t{\n"
        "\t\tiAppUi.ActivateTopViewL();\t\n"
        "\t\t}\n"
        "\tCleanupStack::PopAndDestroy(windowList); \t\n"
        "\tdelete this;\n"
        "\t}",
        "void CEikStartUpViewActivator::RunL()\n"
        "\t{\n"
        "\t// HTCLEO_EIKCORE_STARTUP_VIEW_ACTIVATOR_TRACE_V1\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE350u, KErrNone);\n"
        "\tRWsSession& ws = iEnv.WsSession();\n"
        "\tconst TInt numWgs = ws.NumWindowGroups(0);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE351u, numWgs);\n"
        "\tCArrayFixFlat<TInt>* windowList = new(ELeave) CArrayFixFlat<TInt>(numWgs);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE352u, windowList ? KErrNone : KErrNoMemory);\n"
        "\tCleanupStack::PushL(windowList);\n"
        "\tws.WindowGroupList(0, windowList);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE353u, windowList->Count());\n"
        "\tconst TInt wgId = iEnv.RootWin().Identifier();\n"
        "\tconst TBool htcleoActivateTopView =\n"
        "\t\t(ws.GetFocusWindowGroup() == wgId ||\n"
        "\t\t(windowList->Count() > 0 && windowList->At(0) == wgId)) &&\n"
        "\t\tiEnv.IsSchedulerRunning();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE354u, htcleoActivateTopView);\n"
        "\tif (htcleoActivateTopView)\n"
        "\t\t{\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE355u, KErrNone);\n"
        "\t\tiAppUi.ActivateTopViewL();\t\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE356u, KErrNone);\n"
        "\t\t}\n"
        "\tCleanupStack::PopAndDestroy(windowList); \t\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE357u, KErrNone);\n"
        "\tdelete this;\n"
        "\t}",
        "startup view activator",
    )
    return source


def verify(source: str) -> None:
    synchronous_stages = range(0xE320, 0xE342)
    asynchronous_stages = range(0xE350, 0xE358)
    checks = {
        "post-AppUi marker": source.count(MARKER) == 1,
        "view activator marker": source.count(ACTIVATOR_MARKER) == 1,
        "existing durable helper": (
            source.count("HTCLEO_EIKCORE_MATRIXMENU_PREFACTORY_DURABLE_LOG_V2")
            == 1
            and source.count("static void HtcleoEikCorePreFactoryTrace(") == 1
        ),
        "all synchronous stages": all(
            source.count(f"0x{stage:04X}u") == 1
            for stage in synchronous_stages
        ),
        "all asynchronous stages": all(
            source.count(f"0x{stage:04X}u") == 1
            for stage in asynchronous_stages
        ),
        "stock PrepareToEdit retained": source.count("doc.PrepareToEditL();") == 1,
        "stock view initialization retained": (
            source.count("appUi.CheckInitializeViewsL(") == 1
        ),
        "stock command processing retained": (
            source.count("appUi.ProcessCommandParametersL(") == 1
        ),
        "stock activation retained": source.count("iAppUi.ActivateTopViewL();") == 1,
        "stock readiness retained": source.count("SetAppReady();") == 1,
        "no injected wait or display": (
            "User::After" not in source[source.index(MARKER):source.index(MARKER) + 8000]
            and "HalFunction" not in source[source.index(MARKER):source.index(MARKER) + 8000]
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_POSTAPPUI_TRACE=installed "
        "sync=E320-E341 async=E350-E357 behavior=unchanged"
    )


if __name__ == "__main__":
    main()
