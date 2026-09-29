#!/usr/bin/env python3
"""Install a fail-open durable trace in the real STEM EiksrvUi implementation.

Iteration 456 proves eiksrv.dll loads the ROM's EiksrvUi image, resolves its
factory, creates the application-UI object, and reaches the call to
CEikServAppUi::ConstructL.  The ROM recipe maps stem_eiksrvui.dll to
sys\\bin\\eiksrvui.dll, so this transform instruments that shared source while
enabling it only in the STEM break-dependency MMP.  It changes no leave,
startup, retry, scheduler, server, sound, skin, or display policy.  Iteration
484 hardware-proves all earlier EikSrvUi stages through E7DB, after 109
per-record file transactions.  Later builds retain only the unproven
Initialize/Construct tail and remove the redundant explicit Flush so logging
cannot become the boot blocker itself.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKSRVUI_CONSTRUCT_DURABLE_LOG_V1"
SKIN_RESULT_MARKER = "HTCLEO_EIKSRVUI_SKIN_RESULT_RELEAVE_V2"
LOG_CLOSE_ONLY_MARKER = "HTCLEO_EIKSRVUI_LOG_CLOSE_ONLY_V1"
LOG_FRONTIER_ONLY_MARKER = "HTCLEO_EIKSRVUI_LOG_FRONTIER_TAIL_V1"
OPTIONAL_UI_TAIL_BYPASS_MARKER = "HTCLEO_EIKSRVUI_OPTIONAL_UI_TAIL_BYPASS_V1"
MACRO = "__HTCLEO_EIKSRVUI_CONSTRUCT_LOG__"
STAGES = (
    "E760", "E761", "E762", "E763", "E764", "E765", "E766", "E767",
    "E768", "E769", "E76A", "E76B", "E76C", "E76D", "E76E", "E76F",
    "E770", "E771", "E772", "E773", "E774", "E775", "E776", "E777",
    "E778", "E779", "E77A", "E77B", "E77C", "E77D", "E77E", "E77F",
    "E790", "E791", "E792", "E793", "E794", "E795", "E796", "E797",
    "E798", "E799", "E79A", "E79B",
    "E7A0", "E7A1", "E7A2", "E7A3", "E7A4", "E7A5", "E7A6", "E7A7",
    "E7A8", "E7A9", "E7AA", "E7AB", "E7AC", "E7AD", "E7AE", "E7AF",
    "E7B0",
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_EIKSRVUI_CONSTRUCT_LOG__
#include <f32file.h>

// HTCLEO_EIKSRVUI_CONSTRUCT_DURABLE_LOG_V1
static void HtcleoEikSrvUiLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // HTCLEO_EIKSRVUI_LOG_FRONTIER_TAIL_V1
    // Iteration 484 hardware-proved all earlier stages through E7DB. Retain
    // only the unproven Initialize tail and the derived Construct tail.
    if (!((aStage >= 0x0000E7DCu && aStage <= 0x0000E7E2u) ||
          (aStage >= 0x0000E776u && aStage <= 0x0000E79Bu)))
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikSrvUiLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikSrvUiLogPath, "C:\\Symbian3\\EIKSRV.TXT");
    r = fs.MkDirAll(KHtcleoEikSrvUiLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoEikSrvUiLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoEikSrvUiLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position < (128 * 64))
        {
        _LIT8(KHtcleoEikSrvUiPrefix, "HTCLEO_EIKSRV ");
        TBuf8<96> record;
        record.Append(KHtcleoEikSrvUiPrefix);
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
        // HTCLEO_EIKSRVUI_LOG_CLOSE_ONLY_V1
        // RFile/RFs Close below release the completed write. Hardware tests
        // wait before power removal, so avoid a second synchronous request at
        // every checkpoint.
        }
    file.Close();
    fs.Close();
    }
#else
inline void HtcleoEikSrvUiLog(TUint32, TInt, TUint32) {}
#endif

'''


def verify(source: str, mmp: str, frozen_def: Path, linux_def_alias: Path) -> None:
    arm_def_base = frozen_def.with_name("EIKSVUI.DEF").as_posix()
    checks = {
        "marker": source.count(MARKER) == 1,
        "skin result marker": source.count(SKIN_RESULT_MARKER) == 1,
        "skin result trap": source.count(
            "TRAP(htcleoSkinInitResult, AknsUtils::InitSkinSupportL())"
        ) == 1,
        "skin result re-leave": source.count(
            "User::LeaveIfError(htcleoSkinInitResult)"
        ) == 1,
        "close-only logger marker": source.count(LOG_CLOSE_ONLY_MARKER) == 1,
        "frontier-only logger marker": source.count(LOG_FRONTIER_ONLY_MARKER) == 1,
        "single write without explicit Flush": (
            source.count("r = file.Write(record);") == 1
            and source.count("file.Flush();") == 0
        ),
        "exact Initialize/Construct tail filter": source.count(
            "aStage >= 0x0000E7DCu && aStage <= 0x0000E7E2u"
        ) == 1 and source.count(
            "aStage >= 0x0000E776u && aStage <= 0x0000E79Bu"
        ) == 1,
        "optional UI tail bypass marker": (
            source.count(OPTIONAL_UI_TAIL_BYPASS_MARKER) == 1
        ),
        "external-key startup work retired": source.count(
            "TRAP_IGNORE(EnsureExternalKeyHandlerAppStreamExistsL());"
        ) == 0,
        "initial keysound launch retired": source.count(
            "const TInt htcleoKeySoundResult ="
        ) == 0,
        "initial keysound animation retired": source.count(
            "iAknAnimDll = new(ELeave)RAnimDll(wsSession);"
        ) == 0,
        "initial default keysound replacement retired": source.count(
            "ReplaceKeySoundsL(0x100053D0);"
        ) == 1,
        "initial bitmap cursor load retired": source.count(
            "LoadBitmapCursorsL();"
        ) == 1,
        "external-key bypass detail": source.count("0x4558544Bu") == 2,
        "keysound bypass detail": source.count("0x4B534E44u") == 10,
        "cursor bypass detail": source.count("0x43555253u") == 2,
        "log path": source.count("C:\\\\Symbian3\\\\EIKSRV.TXT") == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "linux EikStd path": "/sf/mw/classicui/uifw/EikStd/" in mmp,
        "no lowercase eikstd path": "/sf/mw/classicui/uifw/eikstd/" not in mmp,
        "no mixed-case Eikstd path": "/sf/mw/classicui/uifw/Eikstd/" not in mmp,
        "AknNotify import case": mmp.count("LIBRARY         AknNotify.lib") == 1,
        "AknNotifyPlugin import case": (
            mmp.count("LIBRARY         AknNotifyPlugin.lib") == 1
        ),
        "classicui exported private include": (
            mmp.count("USERINCLUDE     /sf/mw/classicui/inc") == 1
        ),
        "ARM frozen def base": (
            mmp.count(f"DEFFILE         {arm_def_base}") == 1
        ),
        "no suffixed ARM def in MMP": "EIKSVUIU.DEF" not in mmp,
        "Linux ARM def alias": (
            frozen_def.is_file()
            and linux_def_alias.is_file()
            and frozen_def.read_bytes() == linux_def_alias.read_bytes()
        ),
        "derived construct": source.count("void CEikServAppUi::ConstructL()") == 1,
        "base construct": source.count("CEikServAppUiBase::ConstructL()") >= 2,
    }
    for stage in STAGES:
        checks[f"stage {stage}"] = (
            source.count(f"HtcleoEikSrvUiLog(0x0000{stage}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()

    source_path = (
        args.epocroot
        / "sf/mw/classicui/uifw/EikStd/srvuisrc/EIKSRVUI.CPP"
    )
    mmp_path = args.epocroot / "sf/incubator/stemkit/breakdeps/EIKSRVUI.MMP"
    frozen_def = (
        args.epocroot
        / "sf/mw/classicui/uifw/EikStd/EABI/EIKSVUIU.DEF"
    )
    linux_def_alias = (
        args.epocroot
        / "sf/mw/classicui/uifw/EikStd/EABI/EIKSVUIu.DEF"
    )
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = replace_once(
            source,
            '#include "AknEikSrv.pan"\n',
            '#include "AknEikSrv.pan"\n' + LOGGER,
            "logger insertion",
        )

        source = replace_once(
            source,
            """EXPORT_C void CEikServAppUiBase::ConstructL() 
    {
    RWindowGroup& groupWin = iCoeEnv->RootWin();
""",
            """EXPORT_C void CEikServAppUiBase::ConstructL() 
    {
    HtcleoEikSrvUiLog(0x0000E7A0u, KErrNone, 0u);
    RWindowGroup& groupWin = iCoeEnv->RootWin();
""",
            "base entry",
        )
        source = replace_once(
            source,
            """    iEikonEnv->FsSession().SetNotifyUser(EFalse);

    // Must call BaseConstructL to get Avkon classes called.
""",
            """    iEikonEnv->FsSession().SetNotifyUser(EFalse);
    HtcleoEikSrvUiLog(0x0000E7A1u, KErrNone, 0u);

    // Must call BaseConstructL to get Avkon classes called.
""",
            "base environment",
        )
        source = replace_once(
            source,
            """    CAknAppUiBase::BaseConstructL(ENonStandardResourceFile|ENoScreenFurniture|
        EAknEnableMSK|EAknSingleClickCompatible);
""",
            """    HtcleoEikSrvUiLog(0x0000E7A2u, KErrNone, 0u);
    CAknAppUiBase::BaseConstructL(ENonStandardResourceFile|ENoScreenFurniture|
        EAknEnableMSK|EAknSingleClickCompatible);
    HtcleoEikSrvUiLog(0x0000E7A3u, KErrNone, 0u);
""",
            "base avkon construct",
        )
        source = replace_once(
            source,
            """    wsSession.ComputeMode(RWsSession::EPriorityControlDisabled);
    iCoeEnv->RootWin().EnableScreenChangeEvents();
    RThread thread;
""",
            """    wsSession.ComputeMode(RWsSession::EPriorityControlDisabled);
    iCoeEnv->RootWin().EnableScreenChangeEvents();
    HtcleoEikSrvUiLog(0x0000E7A4u, KErrNone, 0u);
    RThread thread;
""",
            "base window settings",
        )
        source = replace_once(
            source,
            """#else
    thread.SetPriority(EPriorityAbsoluteForeground);
#endif

    // Create a window group for the password and alarm screens.
""",
            """#else
    thread.SetPriority(EPriorityAbsoluteForeground);
#endif
    HtcleoEikSrvUiLog(0x0000E7A5u, KErrNone, 0u);

    // Create a window group for the password and alarm screens.
""",
            "base priority",
        )
        source = replace_once(
            source,
            """    iAlertGroupWin = RWindowGroup(wsSession);
    
    // EFalse disables key events - they will be enabled again as soon as the ordinal position is 
    // set such that iAlertGroupWin is not the foreground window-group.
    User::LeaveIfError(iAlertGroupWin.Construct((TUint32)this, EFalse)); 
""",
            """    iAlertGroupWin = RWindowGroup(wsSession);
    HtcleoEikSrvUiLog(0x0000E7A6u, KErrNone, 0u);
    
    // EFalse disables key events - they will be enabled again as soon as the ordinal position is 
    // set such that iAlertGroupWin is not the foreground window-group.
    const TInt htcleoAlertGroupResult =
        iAlertGroupWin.Construct((TUint32)this, EFalse);
    HtcleoEikSrvUiLog(0x0000E7A7u, htcleoAlertGroupResult, 0u);
    User::LeaveIfError(htcleoAlertGroupResult); 
""",
            "base alert window construct",
        )
        source = replace_once(
            source,
            """    // Enable key events, now that iAlertGroupWin is not in the foreground.
    iAlertGroupWin.EnableReceiptOfFocus(ETrue); 

    iEikServExtra = new(ELeave) CEikServExtra();
    
    TInt numCursors = LafServAppUiBase::NumberOfCursorsInSystemCursorList();
    if(numCursors != 0 && LafServAppUiBase::ClaimPointerCursorListIfNeeded(*iEikonEnv) == KErrNone)
        {
        iEikServExtra->iPointerCursors = new(ELeave) CArrayPtrFlat<RWsPointerCursor>(4);
""",
            """    // Enable key events, now that iAlertGroupWin is not in the foreground.
    iAlertGroupWin.EnableReceiptOfFocus(ETrue); 
    HtcleoEikSrvUiLog(0x0000E7A8u, KErrNone, 0u);

    iEikServExtra = new(ELeave) CEikServExtra();
    HtcleoEikSrvUiLog(0x0000E7A9u, KErrNone, iEikServExtra ? 1u : 0u);
    
    TInt numCursors = LafServAppUiBase::NumberOfCursorsInSystemCursorList();
    HtcleoEikSrvUiLog(0x0000E7AAu, numCursors, 0u);
    TInt htcleoClaimResult = KErrNotFound;
    if (numCursors != 0)
        {
        htcleoClaimResult =
            LafServAppUiBase::ClaimPointerCursorListIfNeeded(*iEikonEnv);
        }
    HtcleoEikSrvUiLog(0x0000E7ABu, htcleoClaimResult, (TUint32)numCursors);
    if(numCursors != 0 && htcleoClaimResult == KErrNone)
        {
        iEikServExtra->iPointerCursors = new(ELeave) CArrayPtrFlat<RWsPointerCursor>(4);
        HtcleoEikSrvUiLog(0x0000E7ACu, KErrNone,
            iEikServExtra->iPointerCursors ? 1u : 0u);
""",
            "base cursor setup",
        )
        source = replace_once(
            source,
            """        for(TInt ii = 0; ii < numCursors; ii++)
            {
            RWsPointerCursor* cursor = LafServAppUiBase::ConstructPointerCursorL(ii, member, 
                *iEikonEnv);
                
            CleanupStack::PushL(TCleanupItem(PointerCleanup, cursor));
            iEikServExtra->iPointerCursors->AppendL(cursor);
            CleanupStack::Pop(); // cursor - handle & ptr
            }
        }
    }

EXPORT_C void CEikServAppUiBase::InitializeL(TEikServCtrlFactories& aCtrlFactories)
""",
            """        for(TInt ii = 0; ii < numCursors; ii++)
            {
            HtcleoEikSrvUiLog(0x0000E7ADu, KErrNone, (TUint32)ii);
            RWsPointerCursor* cursor = LafServAppUiBase::ConstructPointerCursorL(ii, member, 
                *iEikonEnv);
            HtcleoEikSrvUiLog(0x0000E7AEu, KErrNone, cursor ? 1u : 0u);
                
            CleanupStack::PushL(TCleanupItem(PointerCleanup, cursor));
            iEikServExtra->iPointerCursors->AppendL(cursor);
            HtcleoEikSrvUiLog(0x0000E7AFu, KErrNone, (TUint32)ii);
            CleanupStack::Pop(); // cursor - handle & ptr
            }
        }
    HtcleoEikSrvUiLog(0x0000E7B0u, KErrNone, 0u);
    }

EXPORT_C void CEikServAppUiBase::InitializeL(TEikServCtrlFactories& aCtrlFactories)
""",
            "base cursor loop and return",
        )

        source = replace_once(
            source,
            """void CEikServAppUi::ConstructL()
    {
    // Create stub to allow device boot up with old notifier controller dependencies.
    iNotifierDialogController = CNotifierDialogController::NewL(0);
""",
            """void CEikServAppUi::ConstructL()
    {
    HtcleoEikSrvUiLog(0x0000E760u, KErrNone, 0u);
    // Create stub to allow device boot up with old notifier controller dependencies.
    HtcleoEikSrvUiLog(0x0000E761u, KErrNone, 0u);
    iNotifierDialogController = CNotifierDialogController::NewL(0);
    HtcleoEikSrvUiLog(0x0000E762u, KErrNone,
        iNotifierDialogController ? 1u : 0u);
""",
            "derived entry and notifier",
        )
        source = replace_once(
            source,
            """    AknsUtils::InitSkinSupportL();
#ifdef _DEBUG
""",
            """    HtcleoEikSrvUiLog(0x0000E763u, KErrNone, 0u);
    AknsUtils::InitSkinSupportL();
    HtcleoEikSrvUiLog(0x0000E764u, KErrNone, 0u);
#ifdef _DEBUG
""",
            "skin support",
        )
        source = replace_once(
            source,
            """    CEikServAppUiBase::ConstructL();
#ifdef _DEBUG
""",
            """    HtcleoEikSrvUiLog(0x0000E765u, KErrNone, 0u);
    CEikServAppUiBase::ConstructL();
    HtcleoEikSrvUiLog(0x0000E766u, KErrNone, 0u);
#ifdef _DEBUG
""",
            "base call",
        )
        source = replace_once(
            source,
            """    AknsUtils::SetAvkonSkinEnabledL( ETrue );
#ifdef _DEBUG
    RDebug::Print(_L("CEikServAppUi::ConstructL(), CEikServAppUiBase::ConstructL() succeed"));
#endif

    AknsUtils::SetAvkonSkinEnabledL( ETrue );
""",
            """    HtcleoEikSrvUiLog(0x0000E767u, KErrNone, 0u);
    AknsUtils::SetAvkonSkinEnabledL( ETrue );
    HtcleoEikSrvUiLog(0x0000E768u, KErrNone, 0u);
#ifdef _DEBUG
    RDebug::Print(_L("CEikServAppUi::ConstructL(), CEikServAppUiBase::ConstructL() succeed"));
#endif

    HtcleoEikSrvUiLog(0x0000E769u, KErrNone, 0u);
    AknsUtils::SetAvkonSkinEnabledL( ETrue );
    HtcleoEikSrvUiLog(0x0000E76Au, KErrNone, 0u);
""",
            "skin enable calls",
        )
        source = replace_once(
            source,
            """    TFileName fileName(KResFileName);
    BaflUtils::NearestLanguageFile(iEikonEnv->FsSession(), fileName);
    iResourceFileOffset = iCoeEnv->AddResourceFileL(fileName);

    // Create notifier controller before Notfier server is started.
    iNotifierController = CAknNotifierController::NewL();
""",
            """    TFileName fileName(KResFileName);
    HtcleoEikSrvUiLog(0x0000E76Bu, KErrNone, 0u);
    BaflUtils::NearestLanguageFile(iEikonEnv->FsSession(), fileName);
    HtcleoEikSrvUiLog(0x0000E76Cu, KErrNone, 0u);
    HtcleoEikSrvUiLog(0x0000E76Du, KErrNone, 0u);
    iResourceFileOffset = iCoeEnv->AddResourceFileL(fileName);
    HtcleoEikSrvUiLog(0x0000E76Eu, iResourceFileOffset, 0u);

    // Create notifier controller before Notfier server is started.
    HtcleoEikSrvUiLog(0x0000E76Fu, KErrNone, 0u);
    iNotifierController = CAknNotifierController::NewL();
    HtcleoEikSrvUiLog(0x0000E770u, KErrNone,
        iNotifierController ? 1u : 0u);
""",
            "resource and notifier controller",
        )
        source = replace_once(
            source,
            """    CEikServNotifyAlert* alert=new(ELeave) CEikServNotifyAlert;
    CleanupStack::PushL(alert);
    alert->ConstructL();
""",
            """    HtcleoEikSrvUiLog(0x0000E771u, KErrNone, 0u);
    CEikServNotifyAlert* alert=new(ELeave) CEikServNotifyAlert;
    HtcleoEikSrvUiLog(0x0000E772u, KErrNone, alert ? 1u : 0u);
    CleanupStack::PushL(alert);
    HtcleoEikSrvUiLog(0x0000E773u, KErrNone, 0u);
    alert->ConstructL();
    HtcleoEikSrvUiLog(0x0000E774u, KErrNone, 0u);
""",
            "alert construct",
        )
        source = replace_once(
            source,
            """    CEikServAppUiBase::InitializeL(fctry);

#ifdef _DEBUG
""",
            """    HtcleoEikSrvUiLog(0x0000E775u, KErrNone, 0u);
    CEikServAppUiBase::InitializeL(fctry);
    HtcleoEikSrvUiLog(0x0000E776u, KErrNone, 0u);

#ifdef _DEBUG
""",
            "base initialize",
        )
        source = replace_once(
            source,
            """    // Initialize some system settings.
    TRAP_IGNORE(EnsureExternalKeyHandlerAppStreamExistsL());
""",
            """    // Initialize some system settings.
    HtcleoEikSrvUiLog(0x0000E777u, KErrNone, 0u);
    TRAP_IGNORE(EnsureExternalKeyHandlerAppStreamExistsL());
    HtcleoEikSrvUiLog(0x0000E778u, KErrNone, 0u);
""",
            "external key stream",
        )
        source = replace_once(
            source,
            """    // Create high priority windows for app bar and side bar.
    iOffScreenGroupWin = RWindowGroup(wsSession);
    User::LeaveIfError(iOffScreenGroupWin.Construct((TUint32)&iOffScreenGroupWin, 
        EFalse)); // EFalse disables key events
    iOffScreenGroupWin.SetOrdinalPosition(0,ECoeWinPriorityHigh);
""",
            """    // Create high priority windows for app bar and side bar.
    iOffScreenGroupWin = RWindowGroup(wsSession);
    HtcleoEikSrvUiLog(0x0000E779u, KErrNone, 0u);
    const TInt htcleoOffScreenResult =
        iOffScreenGroupWin.Construct((TUint32)&iOffScreenGroupWin, EFalse);
    HtcleoEikSrvUiLog(0x0000E77Au, htcleoOffScreenResult, 0u);
    User::LeaveIfError(htcleoOffScreenResult); // EFalse disables key events
    iOffScreenGroupWin.SetOrdinalPosition(0,ECoeWinPriorityHigh);
    HtcleoEikSrvUiLog(0x0000E77Bu, KErrNone, 0u);
""",
            "offscreen window",
        )
        source = replace_once(
            source,
            """    // Launch the Avkon KeySound Server
    User::LeaveIfError(CEikKeySoundServer::LaunchServer(iKeySoundThreadId));
    
    // Start the Avkon Anim Dll - required for keysounds
    iAknAnimDll = new(ELeave)RAnimDll(wsSession);
    iAknAnimDll->Load(KAnimDllFileName);
    iAknAnimKeySound = new(ELeave)RAknAnimKeySound(*iAknAnimDll);
    iAknAnimKeySound->ConstructL(&iOffScreenGroupWin);
""",
            """    // Launch the Avkon KeySound Server
    HtcleoEikSrvUiLog(0x0000E77Cu, KErrNone, 0u);
    const TInt htcleoKeySoundResult =
        CEikKeySoundServer::LaunchServer(iKeySoundThreadId);
    HtcleoEikSrvUiLog(0x0000E77Du, htcleoKeySoundResult, 0u);
    User::LeaveIfError(htcleoKeySoundResult);
    
    // Start the Avkon Anim Dll - required for keysounds
    HtcleoEikSrvUiLog(0x0000E77Eu, KErrNone, 0u);
    iAknAnimDll = new(ELeave)RAnimDll(wsSession);
    HtcleoEikSrvUiLog(0x0000E77Fu, KErrNone, iAknAnimDll ? 1u : 0u);
    const TInt htcleoAnimLoadResult = iAknAnimDll->Load(KAnimDllFileName);
    HtcleoEikSrvUiLog(0x0000E790u, htcleoAnimLoadResult, 0u);
    iAknAnimKeySound = new(ELeave)RAknAnimKeySound(*iAknAnimDll);
    HtcleoEikSrvUiLog(0x0000E791u, KErrNone, iAknAnimKeySound ? 1u : 0u);
    HtcleoEikSrvUiLog(0x0000E792u, KErrNone, 0u);
    iAknAnimKeySound->ConstructL(&iOffScreenGroupWin);
    HtcleoEikSrvUiLog(0x0000E793u, KErrNone, 0u);
""",
            "keysound and animation",
        )
        source = replace_once(
            source,
            """    // Create default keysounds - pass in UID.
    ReplaceKeySoundsL(0x100053D0);
""",
            """    // Create default keysounds - pass in UID.
    HtcleoEikSrvUiLog(0x0000E794u, KErrNone, 0u);
    ReplaceKeySoundsL(0x100053D0);
    HtcleoEikSrvUiLog(0x0000E795u, KErrNone, 0u);
""",
            "replace keysounds",
        )
        source = replace_once(
            source,
            """    TInt bufSize = 6400;
    ws.SetMaxBufferSizeL(bufSize);

    // Load bitmap cursors.
    LoadBitmapCursorsL();

    STATIC_CAST(CEikServEnv*,CEikonEnv::Static())->SetEikServAppUiSessionFactory( this );
""",
            """    TInt bufSize = 6400;
    HtcleoEikSrvUiLog(0x0000E796u, KErrNone, (TUint32)bufSize);
    ws.SetMaxBufferSizeL(bufSize);
    HtcleoEikSrvUiLog(0x0000E797u, KErrNone, 0u);

    // Load bitmap cursors.
    HtcleoEikSrvUiLog(0x0000E798u, KErrNone, 0u);
    LoadBitmapCursorsL();
    HtcleoEikSrvUiLog(0x0000E799u, KErrNone, 0u);

    STATIC_CAST(CEikServEnv*,CEikonEnv::Static())->SetEikServAppUiSessionFactory( this );
    HtcleoEikSrvUiLog(0x0000E79Au, KErrNone, 0u);
""",
            "buffer cursors and factory",
        )
        source = replace_once(
            source,
            """#ifdef _DEBUG
    RDebug::Print(_L("CEikServAppUi::ConstructL(), over and out"));
#endif
    }


void CEikServAppUi::RestartKeySoundThreadL()
""",
            """#ifdef _DEBUG
    RDebug::Print(_L("CEikServAppUi::ConstructL(), over and out"));
#endif
    HtcleoEikSrvUiLog(0x0000E79Bu, KErrNone, 0u);
    }


void CEikServAppUi::RestartKeySoundThreadL()
""",
            "derived return",
        )

        if not mmp.endswith("\n"):
            mmp += "\n"
        mmp += f"\nMACRO          {MACRO}\n"

    # Iteration 457 reaches E763 and leaves inside InitSkinSupportL before
    # E764.  Trap only long enough to durably record the original result, then
    # immediately re-leave with that same value.  This preserves the direct
    # leaving call's success/failure semantics and does not make skins
    # optional.
    if SKIN_RESULT_MARKER not in source:
        source = replace_once(
            source,
            """    HtcleoEikSrvUiLog(0x0000E763u, KErrNone, 0u);
    AknsUtils::InitSkinSupportL();
    HtcleoEikSrvUiLog(0x0000E764u, KErrNone, 0u);
""",
            f"""    // {SKIN_RESULT_MARKER}
    HtcleoEikSrvUiLog(0x0000E763u, KErrNone,
        AknsUtils::SkinInstance() ? 1u : 0u);
    TInt htcleoSkinInitResult = KErrNone;
    TRAP(htcleoSkinInitResult, AknsUtils::InitSkinSupportL());
    HtcleoEikSrvUiLog(0x0000E764u, htcleoSkinInitResult,
        AknsUtils::SkinInstance() ? 1u : 0u);
    User::LeaveIfError(htcleoSkinInitResult);
""",
            "skin result trap and semantic re-leave",
        )

    if LOG_CLOSE_ONLY_MARKER not in source:
        source = replace_once(
            source,
            "        r = file.Write(record);\n"
            "        if (r == KErrNone)\n"
            "            {\n"
            "            file.Flush();\n"
            "            }\n",
            "        r = file.Write(record);\n"
            "        // HTCLEO_EIKSRVUI_LOG_CLOSE_ONLY_V1\n"
            "        // RFile/RFs Close below release the completed write. Hardware tests\n"
            "        // wait before power removal, so avoid a second synchronous request at\n"
            "        // every checkpoint.\n",
            "EikSrvUi close-only logger",
        )

    if LOG_FRONTIER_ONLY_MARKER not in source:
        source = replace_once(
            source,
            "static void HtcleoEikSrvUiLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n"
            "    {\n"
            "    RFs fs;\n",
            "static void HtcleoEikSrvUiLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n"
            "    {\n"
            "    // HTCLEO_EIKSRVUI_LOG_FRONTIER_TAIL_V1\n"
            "    // Iteration 484 hardware-proved all earlier stages through E7DB. Retain\n"
            "    // only the unproven Initialize tail and the derived Construct tail.\n"
            "    if (!((aStage >= 0x0000E7DCu && aStage <= 0x0000E7E2u) ||\n"
            "          (aStage >= 0x0000E776u && aStage <= 0x0000E79Bu)))\n"
            "        {\n"
            "        return;\n"
            "        }\n\n"
            "    RFs fs;\n",
            "EikSrvUi unproven-tail logger filter",
        )

    if OPTIONAL_UI_TAIL_BYPASS_MARKER not in source:
        source = replace_once(
            source,
            "    // Initialize some system settings.\n"
            "    HtcleoEikSrvUiLog(0x0000E777u, KErrNone, 0u);\n"
            "    TRAP_IGNORE(EnsureExternalKeyHandlerAppStreamExistsL());\n"
            "    HtcleoEikSrvUiLog(0x0000E778u, KErrNone, 0u);\n",
            "    // Initialize some system settings.\n"
            "    // HTCLEO_EIKSRVUI_OPTIONAL_UI_TAIL_BYPASS_V1\n"
            "    // External-key settings are not required for the HD2 touchscreen.\n"
            "    HtcleoEikSrvUiLog(0x0000E777u, KErrNotSupported, 0x4558544Bu);\n"
            "    HtcleoEikSrvUiLog(0x0000E778u, KErrNotSupported, 0x4558544Bu);\n",
            "EikSrvUi external-key UI-first bypass",
        )
        source = replace_once(
            source,
            "    // Launch the Avkon KeySound Server\n"
            "    HtcleoEikSrvUiLog(0x0000E77Cu, KErrNone, 0u);\n"
            "    const TInt htcleoKeySoundResult =\n"
            "        CEikKeySoundServer::LaunchServer(iKeySoundThreadId);\n"
            "    HtcleoEikSrvUiLog(0x0000E77Du, htcleoKeySoundResult, 0u);\n"
            "    User::LeaveIfError(htcleoKeySoundResult);\n"
            "    \n"
            "    // Start the Avkon Anim Dll - required for keysounds\n"
            "    HtcleoEikSrvUiLog(0x0000E77Eu, KErrNone, 0u);\n"
            "    iAknAnimDll = new(ELeave)RAnimDll(wsSession);\n"
            "    HtcleoEikSrvUiLog(0x0000E77Fu, KErrNone, iAknAnimDll ? 1u : 0u);\n"
            "    const TInt htcleoAnimLoadResult = iAknAnimDll->Load(KAnimDllFileName);\n"
            "    HtcleoEikSrvUiLog(0x0000E790u, htcleoAnimLoadResult, 0u);\n"
            "    iAknAnimKeySound = new(ELeave)RAknAnimKeySound(*iAknAnimDll);\n"
            "    HtcleoEikSrvUiLog(0x0000E791u, KErrNone, iAknAnimKeySound ? 1u : 0u);\n"
            "    HtcleoEikSrvUiLog(0x0000E792u, KErrNone, 0u);\n"
            "    iAknAnimKeySound->ConstructL(&iOffScreenGroupWin);\n"
            "    HtcleoEikSrvUiLog(0x0000E793u, KErrNone, 0u);\n",
            "    // Launch the Avkon KeySound Server\n"
            "    // Sound and key-click animation are secondary to Shell/touch bring-up.\n"
            "    HtcleoEikSrvUiLog(0x0000E77Cu, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E77Du, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E77Eu, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E77Fu, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E790u, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E791u, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E792u, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E793u, KErrNotSupported, 0x4B534E44u);\n",
            "EikSrvUi keysound/animation UI-first bypass",
        )
        source = replace_once(
            source,
            "    // Create default keysounds - pass in UID.\n"
            "    HtcleoEikSrvUiLog(0x0000E794u, KErrNone, 0u);\n"
            "    ReplaceKeySoundsL(0x100053D0);\n"
            "    HtcleoEikSrvUiLog(0x0000E795u, KErrNone, 0u);\n",
            "    // Create default keysounds - deferred with the sound server.\n"
            "    HtcleoEikSrvUiLog(0x0000E794u, KErrNotSupported, 0x4B534E44u);\n"
            "    HtcleoEikSrvUiLog(0x0000E795u, KErrNotSupported, 0x4B534E44u);\n",
            "EikSrvUi default keysound UI-first bypass",
        )
        source = replace_once(
            source,
            "    // Load bitmap cursors.\n"
            "    HtcleoEikSrvUiLog(0x0000E798u, KErrNone, 0u);\n"
            "    LoadBitmapCursorsL();\n"
            "    HtcleoEikSrvUiLog(0x0000E799u, KErrNone, 0u);\n",
            "    // Bitmap mouse cursors are not required for HD2 touch input.\n"
            "    HtcleoEikSrvUiLog(0x0000E798u, KErrNotSupported, 0x43555253u);\n"
            "    HtcleoEikSrvUiLog(0x0000E799u, KErrNotSupported, 0x43555253u);\n",
            "EikSrvUi bitmap cursor UI-first bypass",
        )

    # The original STEM MMP was authored for a case-insensitive Windows host.
    # Normalize only path/import spelling so the identical target can be
    # rebuilt on the Linux SBS host; this has no runtime-policy effect.
    mmp = mmp.replace(
        "/sf/mw/classicui/uifw/eikstd/",
        "/sf/mw/classicui/uifw/EikStd/",
    )
    mmp = mmp.replace(
        "/sf/mw/classicui/uifw/Eikstd/",
        "/sf/mw/classicui/uifw/EikStd/",
    )
    mmp = mmp.replace(
        "LIBRARY         aknnotify.lib",
        "LIBRARY         AknNotify.lib",
    )
    mmp = mmp.replace(
        "LIBRARY         aknnotifyplugin.lib",
        "LIBRARY         AknNotifyPlugin.lib",
    )
    if "USERINCLUDE     /sf/mw/classicui/inc" not in mmp:
        mmp = replace_once(
            mmp,
            "USERINCLUDE     /sf/mw/classicui/uifw/EikStd/srvuisrc\n",
            "USERINCLUDE     /sf/mw/classicui/uifw/EikStd/srvuisrc\n"
            "USERINCLUDE     /sf/mw/classicui/inc\n",
            "Linux private-header include",
        )
    # Raptor appends the urel suffix itself.  Preserve an unsuffixed MMP entry
    # and provide the exact lower-case-u filename it requests on the
    # case-sensitive Linux host.  For DEFFILE, unlike SOURCE/USERINCLUDE,
    # Raptor tests a leading /sf path against the host root instead of
    # EPOCROOT.  Use the transform's resolved EPOCROOT path explicitly.  The
    # alias is byte-identical to the original frozen 64-ordinal DEF; it does
    # not create or reorder exports.
    arm_def_base = frozen_def.with_name("EIKSVUI.DEF").as_posix()
    for old_def in (
        "DEFFILE         /sf/mw/classicui/uifw/EikStd/eabi/EIKSVUI.DEF",
        "DEFFILE         /sf/mw/classicui/uifw/EikStd/EABI/EIKSVUIU.DEF",
        "DEFFILE         /sf/mw/classicui/uifw/EikStd/EABI/EIKSVUI.DEF",
    ):
        mmp = mmp.replace(
            old_def,
            f"DEFFILE         {arm_def_base}",
        )
    if not frozen_def.is_file():
        raise SystemExit(f"missing frozen DEF: {frozen_def}")
    frozen_def_bytes = frozen_def.read_bytes()
    if linux_def_alias.exists() and linux_def_alias.read_bytes() != frozen_def_bytes:
        raise SystemExit(f"conflicting Linux DEF alias: {linux_def_alias}")
    linux_def_alias.write_bytes(frozen_def_bytes)

    verify(source, mmp, frozen_def, linux_def_alias)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    print(
        "HTCLEO_EIKSRVUI_CONSTRUCT_LOG=installed stages=E760-E7B0 "
        "skin-result=releave log-flush=close-only "
        "log-scope=e7dc-e7e2,e776-e79b optional-tail=ui-first-deferred"
    )


if __name__ == "__main__":
    main()
