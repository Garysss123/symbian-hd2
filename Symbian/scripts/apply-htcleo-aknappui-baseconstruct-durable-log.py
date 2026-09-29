#!/usr/bin/env python3
"""Add exact durable tracing around and inside CAknAppUiBase::BaseConstructL.

Iteration 473 reaches the EikSrvUi E7A2 checkpoint but never reaches E7A3.
The outer TRAP/re-leave records a synchronous leave without changing the
caller's failure policy.  Iteration 481 returns from the complete Post-Coe/SGC
path and reaches B51A, but not B51B, isolating the next block to the optional
Avkon transition-effects notification.  Iteration 482 contains the new B51B
code and was byte-for-byte deployed, yet reproduces the exact 481 log ending
at B51A.  Since the next compiled path calls the B51B logger without first
calling TransitionEvent, the block is inside the tail of the B51A logger or
the next B51B logger operation.  Removing the redundant per-record Flush lets
iteration 483 durably record B51B, hardware-proving the transition bypass but
also showing that dense per-checkpoint file-server traffic is now perturbing
the frontier.  Later iterations therefore suppress already-proven AKNBASE
stages and retain only B51C-B520, the unproven BaseConstruct tail.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_BASECONSTRUCT_DURABLE_LOG_V1"
SCREEN_CHANGE_COMPAT_MARKER = "HTCLEO_AKNAPPUI_SCREEN_CHANGE_UI_FIRST_COMPAT_V1"
SCREEN_SIZE_COMPAT_MARKER = "HTCLEO_AKNAPPUI_FIXED_SCREEN_SIZE_UI_FIRST_COMPAT_V1"
TACTILE_FEEDBACK_COMPAT_MARKER = "HTCLEO_AKNAPPUI_TACTILE_FEEDBACK_UI_FIRST_COMPAT_V1"
TRANSITION_EFFECTS_COMPAT_MARKER = "HTCLEO_AKNAPPUI_EIKSRV_TRANSITION_EFFECTS_COMPAT_V1"
LOG_CLOSE_ONLY_MARKER = "HTCLEO_AKNAPPUI_LOG_CLOSE_ONLY_V1"
LOG_FRONTIER_ONLY_MARKER = "HTCLEO_AKNAPPUI_LOG_FRONTIER_B51C_B520_V1"
MATRIXMENU_UI_FIRST_MARKER = "HTCLEO_AKNAPPUI_MATRIXMENU_UI_FIRST_COMPAT_V1"
OUTER_MARKER = "HTCLEO_EIKSRVUI_BASECONSTRUCT_RESULT_LOG_V1"
MACRO = "__HTCLEO_AKNAPPUI_BASECONSTRUCT_LOG__"
TEMPLATE_ALIAS_MARKER = "HTCLEO_AVKON_GCCE_C1_ALIAS_V1"
GENERIC_DEFFILE = "DEFFILE /sf/mw/classicui/uifw/AvKon/~/AVKON.def"
PREVIOUS_LINUX_DEFFILE = "DEFFILE /sf/mw/classicui/uifw/AvKon/EABI/AVKONU.DEF"
EPOCROOT_RELATIVE_DEFFILE = "DEFFILE /sf/mw/classicui/uifw/AvKon/EABI/AVKON.DEF"
LINUX_GCCE_DEFFILE = "DEFFILE /root/symbian3-full/sf/mw/classicui/uifw/AvKon/EABI/AVKON.DEF"
GCCE_LIBRARY_CASE_FIXES = {
    "LIBRARY         aknnotify.lib": "LIBRARY         AknNotify.lib",
    "LIBRARY         FindUtil.lib": "LIBRARY         findutil.lib",
    "LIBRARY         servicehandler.lib": "LIBRARY         ServiceHandler.lib",
    "LIBRARY         numbergrouping.lib": "LIBRARY         NumberGrouping.lib",
}

TEMPLATE_C1_ALIASES = r'''

#if defined(__GCCE__)
// HTCLEO_AVKON_GCCE_C1_ALIAS_V1
// GCCE 4.4 folds the complete-object constructor into the base-object
// constructor for these three template instantiations.  The released frozen
// Avkon ABI nevertheless names both symbols, so publish exact same-address
// C1 aliases without introducing another implementation.
asm(
    ".global _ZN23AknListBoxLinesTemplateI17CAknColumnListBoxEC1Ei\n"
    ".type _ZN23AknListBoxLinesTemplateI17CAknColumnListBoxEC1Ei, %function\n"
    ".set _ZN23AknListBoxLinesTemplateI17CAknColumnListBoxEC1Ei, _ZN23AknListBoxLinesTemplateI17CAknColumnListBoxEC2Ei\n"
    ".global _ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxEC1Ei\n"
    ".type _ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxEC1Ei, %function\n"
    ".set _ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxEC1Ei, _ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxEC2Ei\n"
    ".global _ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxEC1Ei\n"
    ".type _ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxEC1Ei, %function\n"
    ".set _ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxEC1Ei, _ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxEC2Ei\n"
    );
#endif
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''

#ifdef __HTCLEO_AKNAPPUI_BASECONSTRUCT_LOG__
#include <f32file.h>

// HTCLEO_AKNAPPUI_BASECONSTRUCT_DURABLE_LOG_V1
static void HtcleoAknAppUiBaseLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // Keep this shared Avkon DLL silent for every process except EikSrv.
    if (RProcess().SecureId().iId != 0x10003A4A)
        {
        return;
        }

    // HTCLEO_AKNAPPUI_LOG_FRONTIER_B51C_B520_V1
    // Iteration 483 hardware-proved every earlier checkpoint through B51B.
    // Keep only the five still-unproven BaseConstruct tail records so the
    // diagnostic file traffic does not become the boot blocker itself.
    if (aStage < 0x0000B51Cu || aStage > 0x0000B520u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoAknBaseLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoAknBaseLogPath, "C:\\Symbian3\\AKNBASE.TXT");
    r = fs.MkDirAll(KHtcleoAknBaseLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoAknBaseLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoAknBaseLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position < (128 * 64))
        {
        _LIT8(KHtcleoAknBasePrefix, "HTCLEO_AKNBASE ");
        TBuf8<96> record;
        record.Append(KHtcleoAknBasePrefix);
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
        // HTCLEO_AKNAPPUI_LOG_CLOSE_ONLY_V1
        // Avoid a second synchronous file-server transaction at every
        // checkpoint. RFile/RFs Close below release the completed write;
        // hardware tests wait before power removal.
        }
    file.Close();
    fs.Close();
    }
#else
inline void HtcleoAknAppUiBaseLog(TUint32, TInt, TUint32) {}
#endif
'''


def install_aknappui(source: str) -> str:
    source = replace_once(
        source,
        "#include <aknpointereventmodifier.h>\n"
        "#include <aknitemactionmenuregister.h>\n",
        "#include <aknpointereventmodifier.h>\n"
        "#include <aknitemactionmenuregister.h>\n" + HELPER,
        "durable logger",
    )
    source = replace_once(
        source,
        "EXPORT_C void CAknAppUiBase::BaseConstructL( TInt aAppUiFlags )\n"
        "    {\n",
        "EXPORT_C void CAknAppUiBase::BaseConstructL( TInt aAppUiFlags )\n"
        "    {\n"
        "    HtcleoAknAppUiBaseLog(0x0000B500u, KErrNone, "
        "(TUint32)aAppUiFlags);\n",
        "BaseConstructL entry",
    )
    source = replace_once(
        source,
        "        SetAppUiAndLeaveIfErrorL( err );\n"
        "        }\n\n"
        "    // enable receipt of changes to screen state\n"
        "    iEikonEnv->RootWin().EnableScreenChangeEvents();\n\n"
        "    iAppUiBaseExtension->iApplicationRect = iCoeEnv->ScreenDevice()->SizeInPixels();\n",
        "        SetAppUiAndLeaveIfErrorL( err );\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B501u, KErrNone, "
        "iAppUiBaseExtension != NULL);\n\n"
        "    // enable receipt of changes to screen state\n"
        "    HtcleoAknAppUiBaseLog(0x0000B502u, KErrNone, 0u);\n"
        "    iEikonEnv->RootWin().EnableScreenChangeEvents();\n"
        "    HtcleoAknAppUiBaseLog(0x0000B503u, KErrNone, 0u);\n\n"
        "    HtcleoAknAppUiBaseLog(0x0000B504u, KErrNone, 0u);\n"
        "    iAppUiBaseExtension->iApplicationRect = iCoeEnv->ScreenDevice()->SizeInPixels();\n"
        "    HtcleoAknAppUiBaseLog(0x0000B505u,\n"
        "        iAppUiBaseExtension->iApplicationRect.Width(),\n"
        "        (TUint32)iAppUiBaseExtension->iApplicationRect.Height());\n",
        "extension screen setup",
    )
    source = replace_once(
        source,
        "    if (!iAppUiBaseExtension->iFeedbackAdaptation )\n"
        "        {\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation = CTouchFeedbackAdaptation::NewL();\n"
        "        }\n",
        "    HtcleoAknAppUiBaseLog(0x0000B506u, KErrNone,\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation != NULL);\n"
        "    if (!iAppUiBaseExtension->iFeedbackAdaptation )\n"
        "        {\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation = CTouchFeedbackAdaptation::NewL();\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B507u, KErrNone,\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation != NULL);\n",
        "touch feedback adaptation",
    )
    source = replace_once(
        source,
        "    CRepository* repository = NULL;\n"
        "    TRAPD(ret, repository = CRepository::NewL(KCRUidAvkon));\n"
        "    if (ret == KErrNone)\n"
        "        {\n"
        "        ret = repository->Get(KAknDefaultAppOrientation, iAppUiBaseExtension->iDefaultRotation);\n"
        "        ret = repository->Get(KAknMiddleSoftkeyEnabled, iAppUiBaseExtension->iMSKEnabled);\n"
        "        }\n",
        "    CRepository* repository = NULL;\n"
        "    HtcleoAknAppUiBaseLog(0x0000B508u, KErrNone, 0u);\n"
        "    TRAPD(ret, repository = CRepository::NewL(KCRUidAvkon));\n"
        "    HtcleoAknAppUiBaseLog(0x0000B509u, ret, repository != NULL);\n"
        "    if (ret == KErrNone)\n"
        "        {\n"
        "        ret = repository->Get(KAknDefaultAppOrientation, iAppUiBaseExtension->iDefaultRotation);\n"
        "        HtcleoAknAppUiBaseLog(0x0000B50Au, ret,\n"
        "            (TUint32)iAppUiBaseExtension->iDefaultRotation);\n"
        "        ret = repository->Get(KAknMiddleSoftkeyEnabled, iAppUiBaseExtension->iMSKEnabled);\n"
        "        HtcleoAknAppUiBaseLog(0x0000B50Bu, ret,\n"
        "            (TUint32)iAppUiBaseExtension->iMSKEnabled);\n"
        "        }\n",
        "Avkon central repository",
    )
    source = replace_once(
        source,
        "    CRepository* defaultOrientationCr = NULL;\n"
        "    TRAPD( err, defaultOrientationCr = CRepository::NewL( KCRUidDefaultAppOrientation ) );\n",
        "    CRepository* defaultOrientationCr = NULL;\n"
        "    HtcleoAknAppUiBaseLog(0x0000B50Cu, KErrNone, 0u);\n"
        "    TRAPD( err, defaultOrientationCr = CRepository::NewL( KCRUidDefaultAppOrientation ) );\n"
        "    HtcleoAknAppUiBaseLog(0x0000B50Du, err, defaultOrientationCr != NULL);\n",
        "default orientation repository",
    )
    source = replace_once(
        source,
        "        }\n\n"
        "    iAknFlags.Assign(EOrientationSpecified, orientationFlags&EAppOrientationSpecifiedFlag);\n",
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B50Eu, err, (TUint32)orientationFlags);\n\n"
        "    iAknFlags.Assign(EOrientationSpecified, orientationFlags&EAppOrientationSpecifiedFlag);\n",
        "orientation completion",
    )
    source = replace_once(
        source,
        "        }\n\n"
        "    AknItemActionMenuRegister::SetConstructingMenuBarOwnerL( this );\n",
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B50Fu, KErrNone,\n"
        "        iAknFlags[ETouchCompatible]);\n\n"
        "    HtcleoAknAppUiBaseLog(0x0000B510u, KErrNone, 0u);\n"
        "    AknItemActionMenuRegister::SetConstructingMenuBarOwnerL( this );\n"
        "    HtcleoAknAppUiBaseLog(0x0000B511u, KErrNone, 0u);\n",
        "touch flags and menu owner",
    )
    source = replace_once(
        source,
        "    if (CAknCompaIf::IsNeeded(aAppUiFlags, repository))\n"
        "        {\n",
        "    HtcleoAknAppUiBaseLog(0x0000B512u, KErrNone, repository != NULL);\n"
        "    const TBool htcleoCompaNeeded =\n"
        "        CAknCompaIf::IsNeeded(aAppUiFlags, repository);\n"
        "    HtcleoAknAppUiBaseLog(0x0000B513u, KErrNone, htcleoCompaNeeded);\n"
        "    if (htcleoCompaNeeded)\n"
        "        {\n",
        "compatibility decision",
    )
    source = replace_once(
        source,
        "        TBool isConsoleApp;\n"
        "        TRAPD(compaModeErr,\n",
        "        TBool isConsoleApp;\n"
        "        HtcleoAknAppUiBaseLog(0x0000B514u, KErrNone, 0u);\n"
        "        TRAPD(compaModeErr,\n",
        "compatibility setup entry",
    )
    source = replace_once(
        source,
        "                    *iCoeEnv, *repository));\n"
        "        delete repository; repository = NULL;\n"
        "        // Ensure that CCoeEnv takes ownership before leaving\n"
        "        SetAppUiAndLeaveIfErrorL(compaModeErr);\n",
        "                    *iCoeEnv, *repository));\n"
        "        HtcleoAknAppUiBaseLog(0x0000B515u, compaModeErr,\n"
        "            (TUint32)compaScreenMode);\n"
        "        delete repository; repository = NULL;\n"
        "        // Ensure that CCoeEnv takes ownership before leaving\n"
        "        SetAppUiAndLeaveIfErrorL(compaModeErr);\n"
        "        HtcleoAknAppUiBaseLog(0x0000B516u, KErrNone,\n"
        "            (TUint32)compaScreenMode);\n",
        "compatibility setup result",
    )
    source = replace_once(
        source,
        "        }\n"
        "    delete repository; repository = NULL;\n\n"
        "    CEikAppUi::BaseConstructL( aAppUiFlags );\n",
        "        }\n"
        "    delete repository; repository = NULL;\n"
        "    HtcleoAknAppUiBaseLog(0x0000B517u, KErrNone,\n"
        "        (TUint32)compaScreenMode);\n\n"
        "    HtcleoAknAppUiBaseLog(0x0000B518u, KErrNone,\n"
        "        (TUint32)aAppUiFlags);\n"
        "    CEikAppUi::BaseConstructL( aAppUiFlags );\n"
        "    HtcleoAknAppUiBaseLog(0x0000B519u, KErrNone, 0u);\n",
        "CEikAppUi base construct",
    )
    source = replace_once(
        source,
        "        AddToStackL( iAppUiBaseExtension->iDiallerLauncher, -100, \n"
        "                     ECoeStackFlagRefusesFocus );\n"
        "        }\n\n"
        "    iAvkonEnv->TransitionEvent(KAknTransitionEventFlags); //look at fullsceen flags\n",
        "        AddToStackL( iAppUiBaseExtension->iDiallerLauncher, -100, \n"
        "                     ECoeStackFlagRefusesFocus );\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Au, KErrNone,\n"
        "        iAppUiBaseExtension->iDiallerLauncher != NULL);\n\n"
        "    iAvkonEnv->TransitionEvent(KAknTransitionEventFlags); //look at fullsceen flags\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Bu, KErrNone, 0u);\n",
        "dialler and transition",
    )
    source = replace_once(
        source,
        "    iEventMonitor = CAknWsEventMonitor::NewL();\n"
        "    \n"
        "    if(!(aAppUiFlags & EAknExplicitStartupEffectCompletion)) //does start idle time\n"
        "        iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);//normal case\n",
        "    HtcleoAknAppUiBaseLog(0x0000B51Cu, KErrNone, 0u);\n"
        "    iEventMonitor = CAknWsEventMonitor::NewL();\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Du, KErrNone,\n"
        "        iEventMonitor != NULL);\n"
        "    \n"
        "    if(!(aAppUiFlags & EAknExplicitStartupEffectCompletion)) //does start idle time\n"
        "        iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);//normal case\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Eu, KErrNone, 0u);\n",
        "event monitor and startup transition",
    )
    source = replace_once(
        source,
        "    // Touch compatibility mode\n"
        "    if (iAppUiBaseExtension->iCompaIf)\n",
        "    // Touch compatibility mode\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Fu, KErrNone,\n"
        "        iAppUiBaseExtension->iCompaIf != NULL);\n"
        "    if (iAppUiBaseExtension->iCompaIf)\n",
        "final compatibility entry",
    )
    source = replace_once(
        source,
        "        TRAP_IGNORE( iAppUiBaseExtension->iPointerEventModifier = CAknPointerEventModifier::NewL() )\n"
        "        }\n"
        "    }\n\n"
        "EXPORT_C TBool CAknAppUiBase::IsFaded() const\n",
        "        TRAP_IGNORE( iAppUiBaseExtension->iPointerEventModifier = CAknPointerEventModifier::NewL() )\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B520u, KErrNone, 0u);\n"
        "    }\n\n"
        "EXPORT_C TBool CAknAppUiBase::IsFaded() const\n",
        "BaseConstructL exit",
    )
    return source


def install_screen_change_compat(source: str) -> str:
    """Avoid the blocking screen-flip subscription only in EikSrv.

    HTC HD2 has one fixed panel and no cover/flip screen topology.  The stock
    call's return value is ignored, but its WriteReply() flush never returns on
    hardware.  Keep the exact stock call for every other Avkon process and
    preserve the rest of BaseConstructL unchanged.
    """
    return replace_once(
        source,
        "    HtcleoAknAppUiBaseLog(0x0000B502u, KErrNone, 0u);\n"
        "    iEikonEnv->RootWin().EnableScreenChangeEvents();\n"
        "    HtcleoAknAppUiBaseLog(0x0000B503u, KErrNone, 0u);\n",
        "    HtcleoAknAppUiBaseLog(0x0000B502u, KErrNone, 0u);\n"
        "    // HTCLEO_AKNAPPUI_SCREEN_CHANGE_UI_FIRST_COMPAT_V1\n"
        "    TInt htcleoScreenChangeResult = KErrNotSupported;\n"
        "    if (!(RProcess().SecureId().iId == 0x10003A4A))\n"
        "        {\n"
        "        htcleoScreenChangeResult =\n"
        "            iEikonEnv->RootWin().EnableScreenChangeEvents();\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B503u,\n"
        "        htcleoScreenChangeResult, 0x5343524Eu);\n",
        "EikSrv fixed-screen screen-change compatibility",
    )


def install_screen_size_compat(source: str) -> str:
    """Use the hardware-proven fixed panel size only in EikSrv.

    CWsScreenDevice::SizeInPixels() always performs a synchronous WriteReplyP
    to WServ.  Iteration 475 proves that request does not return at this exact
    startup point even though the earlier WServ/OpenWFC/NVG chain already
    established the HD2's fixed 480x800 RGB565 panel.  Keep the stock query for
    every other Avkon process and preserve all later BaseConstructL work.
    """
    return replace_once(
        source,
        "    HtcleoAknAppUiBaseLog(0x0000B504u, KErrNone, 0u);\n"
        "    iAppUiBaseExtension->iApplicationRect = iCoeEnv->ScreenDevice()->SizeInPixels();\n"
        "    HtcleoAknAppUiBaseLog(0x0000B505u,\n"
        "        iAppUiBaseExtension->iApplicationRect.Width(),\n"
        "        (TUint32)iAppUiBaseExtension->iApplicationRect.Height());\n",
        "    // HTCLEO_AKNAPPUI_FIXED_SCREEN_SIZE_UI_FIRST_COMPAT_V1\n"
        "    const TBool htcleoUseFixedScreenSize =\n"
        "        RProcess().SecureId().iId == 0x10003A4A;\n"
        "    HtcleoAknAppUiBaseLog(0x0000B504u, KErrNone,\n"
        "        htcleoUseFixedScreenSize ? 0x53495A45u : 0u);\n"
        "    if (htcleoUseFixedScreenSize)\n"
        "        {\n"
        "        iAppUiBaseExtension->iApplicationRect = TSize(480, 800);\n"
        "        }\n"
        "    else\n"
        "        {\n"
        "        iAppUiBaseExtension->iApplicationRect =\n"
        "            iCoeEnv->ScreenDevice()->SizeInPixels();\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B505u,\n"
        "        iAppUiBaseExtension->iApplicationRect.Width(),\n"
        "        (TUint32)iAppUiBaseExtension->iApplicationRect.Height());\n",
        "EikSrv fixed-panel screen-size compatibility",
    )


def install_tactile_feedback_compat(source: str) -> str:
    """Defer tactile-feedback startup only in EikSrv.

    Iteration 476 reaches B506 but not B507, bracketing the synchronous block
    inside CTouchFeedbackAdaptation::NewL().  Tactile/haptic feedback is not
    touch input and is not required for EikSrv to publish the UI.  Preserve the
    stock construction for every other Avkon process and make the one later
    compatibility-mode notification tolerate the intentionally absent object.
    """
    source = replace_once(
        source,
        "    HtcleoAknAppUiBaseLog(0x0000B506u, KErrNone,\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation != NULL);\n"
        "    if (!iAppUiBaseExtension->iFeedbackAdaptation )\n"
        "        {\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation = CTouchFeedbackAdaptation::NewL();\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B507u, KErrNone,\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation != NULL);\n",
        "    // HTCLEO_AKNAPPUI_TACTILE_FEEDBACK_UI_FIRST_COMPAT_V1\n"
        "    const TBool htcleoDeferTactileFeedback = htcleoUseFixedScreenSize;\n"
        "    HtcleoAknAppUiBaseLog(0x0000B506u,\n"
        "        htcleoDeferTactileFeedback ? KErrNotSupported : KErrNone,\n"
        "        0x48415054u);\n"
        "    if (!htcleoDeferTactileFeedback &&\n"
        "        !iAppUiBaseExtension->iFeedbackAdaptation )\n"
        "        {\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation = CTouchFeedbackAdaptation::NewL();\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B507u, KErrNone,\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation != NULL);\n",
        "EikSrv tactile-feedback deferral",
    )
    return replace_once(
        source,
        "        // Tactile feedback needs to be informed about layout change, because\n"
        "        // otherwise it won't get correct information about pen support\n"
        "        // (Tactile Feedback was instantiated earlier in this function, when\n"
        "        // pen was still enabled).\n"
        "        iAppUiBaseExtension->iFeedbackAdaptation->LayoutChanged();\n",
        "        // Tactile feedback needs to be informed about layout change, because\n"
        "        // otherwise it won't get correct information about pen support.\n"
        "        // EikSrv may intentionally defer this optional adaptation on HTCLEO.\n"
        "        if (iAppUiBaseExtension->iFeedbackAdaptation)\n"
        "            {\n"
        "            iAppUiBaseExtension->iFeedbackAdaptation->LayoutChanged();\n"
        "            }\n",
        "nullable compatibility-mode tactile notification",
    )


def install_transition_effects_compat(source: str) -> str:
    """Defer optional startup transition effects only in EikSrv.

    Iteration 481 reaches B51A but not B51B.  The only enclosed call dispatches
    KAknTransitionEventFlags into CTransitionManager::CheckFlags(), which may
    synchronously enter GfxTransEffect.  These animations are not required for
    UI construction, touch input or application operation.  Keep both stock
    transition calls for every non-EikSrv Avkon process.
    """
    source = replace_once(
        source,
        "    iAvkonEnv->TransitionEvent(KAknTransitionEventFlags); //look at fullsceen flags\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Bu, KErrNone, 0u);\n",
        "    // HTCLEO_AKNAPPUI_EIKSRV_TRANSITION_EFFECTS_COMPAT_V1\n"
        "    const TBool htcleoDeferTransitionEffects =\n"
        "        htcleoUseFixedScreenSize;\n"
        "    if (!htcleoDeferTransitionEffects)\n"
        "        {\n"
        "        iAvkonEnv->TransitionEvent(KAknTransitionEventFlags); //look at fullsceen flags\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Bu,\n"
        "        htcleoDeferTransitionEffects ? KErrNotSupported : KErrNone,\n"
        "        0x54524E46u);\n",
        "EikSrv transition-flags compatibility",
    )
    return replace_once(
        source,
        "    if(!(aAppUiFlags & EAknExplicitStartupEffectCompletion)) //does start idle time\n"
        "        iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);//normal case\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Eu, KErrNone, 0u);\n",
        "    if (!(aAppUiFlags & EAknExplicitStartupEffectCompletion) &&\n"
        "        !htcleoDeferTransitionEffects) //does start idle time\n"
        "        {\n"
        "        iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);//normal case\n"
        "        }\n"
        "    HtcleoAknAppUiBaseLog(0x0000B51Eu,\n"
        "        htcleoDeferTransitionEffects ? KErrNotSupported : KErrNone,\n"
        "        0x54524E53u);\n",
        "EikSrv startup-complete transition compatibility",
    )


def install_log_close_only(source: str) -> str:
    """Remove the per-record Flush implicated at the B51A/B51B boundary.

    Keep the exact Write and the existing RFile/RFs Close sequence.  This
    removes only the redundant second synchronous file-server transaction;
    the hardware test protocol already waits before power removal.
    """
    return replace_once(
        source,
        "        r = file.Write(record);\n"
        "        if (r == KErrNone)\n"
        "            {\n"
        "            file.Flush();\n"
        "            }\n",
        "        r = file.Write(record);\n"
        "        // HTCLEO_AKNAPPUI_LOG_CLOSE_ONLY_V1\n"
        "        // Avoid a second synchronous file-server transaction at every\n"
        "        // checkpoint. RFile/RFs Close below release the completed write;\n"
        "        // hardware tests wait before power removal.\n",
        "AKNBASE close-only logger compatibility",
    )


def install_log_frontier_only(source: str) -> str:
    """Retire hardware-proven AKNBASE stages and retain only B51C-B520.

    Iteration 483 writes B51B successfully but does not reach the immediately
    following B51C logger.  Suppressing the 66 proven records removes their
    repeated file-server transactions without changing any Avkon control flow,
    transition policy, error result, or the five unproven tail checkpoints.
    """
    return replace_once(
        source,
        "    if (RProcess().SecureId().iId != 0x10003A4A)\n"
        "        {\n"
        "        return;\n"
        "        }\n\n"
        "    RFs fs;\n",
        "    if (RProcess().SecureId().iId != 0x10003A4A)\n"
        "        {\n"
        "        return;\n"
        "        }\n\n"
        "    // HTCLEO_AKNAPPUI_LOG_FRONTIER_B51C_B520_V1\n"
        "    // Iteration 483 hardware-proved every earlier checkpoint through B51B.\n"
        "    // Keep only the five still-unproven BaseConstruct tail records so the\n"
        "    // diagnostic file traffic does not become the boot blocker itself.\n"
        "    if (aStage < 0x0000B51Cu || aStage > 0x0000B520u)\n"
        "        {\n"
        "        return;\n"
        "        }\n\n"
        "    RFs fs;\n",
        "AKNBASE B51C-B520 frontier-only logger",
    )


def install_outer(source: str) -> str:
    return replace_once(
        source,
        "    HtcleoEikSrvUiLog(0x0000E7A2u, KErrNone, 0u);\n"
        "    CAknAppUiBase::BaseConstructL(ENonStandardResourceFile|ENoScreenFurniture|\n"
        "        EAknEnableMSK|EAknSingleClickCompatible);\n"
        "    HtcleoEikSrvUiLog(0x0000E7A3u, KErrNone, 0u);\n",
        "    // HTCLEO_EIKSRVUI_BASECONSTRUCT_RESULT_LOG_V1\n"
        "    HtcleoEikSrvUiLog(0x0000E7A2u, KErrNone, 0u);\n"
        "    TInt htcleoBaseConstructResult = KErrNone;\n"
        "    TRAP(htcleoBaseConstructResult,\n"
        "        CAknAppUiBase::BaseConstructL(\n"
        "            ENonStandardResourceFile|ENoScreenFurniture|\n"
        "            EAknEnableMSK|EAknSingleClickCompatible));\n"
        "    HtcleoEikSrvUiLog(0x0000E7A3u, htcleoBaseConstructResult,\n"
        "        0x42415345u);\n"
        "    User::LeaveIfError(htcleoBaseConstructResult);\n",
        "EikSrvUi BaseConstructL result wrapper",
    )


def verify(aknappui: str, aknlists: str, eiksrvui: str, mmp: str) -> None:
    stages = range(0xB500, 0xB521)
    matrixmenu_ui_first = MATRIXMENU_UI_FIRST_MARKER in aknappui
    homescreen_trace = (
        "HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1" in aknappui
    )
    checks = {
        "internal marker": aknappui.count(MARKER) == 1,
        "screen-change compatibility marker": (
            aknappui.count(SCREEN_CHANGE_COMPAT_MARKER) == 1
        ),
        "screen-size compatibility marker": (
            aknappui.count(SCREEN_SIZE_COMPAT_MARKER) == 1
        ),
        "tactile-feedback compatibility marker": (
            aknappui.count(TACTILE_FEEDBACK_COMPAT_MARKER) == 1
        ),
        "transition-effects compatibility marker": (
            aknappui.count(TRANSITION_EFFECTS_COMPAT_MARKER) == 1
        ),
        "close-only logger marker": (
            aknappui.count(LOG_CLOSE_ONLY_MARKER) == 1
        ),
        "frontier-only logger marker": (
            aknappui.count(LOG_FRONTIER_ONLY_MARKER) == 1
        ),
        "outer marker": eiksrvui.count(OUTER_MARKER) == 1,
        "exact diagnostic SID gate": (
            aknappui.count(
                "if (!htcleoLogEikSrv && !htcleoLogMatrixMenu &&"
            ) == 1
            and aknappui.count("!htcleoLogHomeScreen") == 1
            if homescreen_trace
            else (
                aknappui.count(
                    "if (!htcleoLogEikSrv && !htcleoLogMatrixMenu)"
                ) == 1
                if matrixmenu_ui_first
                else aknappui.count(
                    "RProcess().SecureId().iId != 0x10003A4A"
                ) == 1
            )
        ),
        "durable path": (
            aknappui.count("AKNBASE.TXT") == 1
            and (
                aknappui.count("HSXML.TXT") == 1
                if homescreen_trace
                else True
            )
        ),
        "single write without explicit Flush": (
            aknappui.count("r = file.Write(record);") == 1
            and aknappui.count("file.Flush();") == 0
        ),
        "exact unproven tail filter": (
            aknappui.count(
                "(aStage < 0x0000B51Cu || aStage > 0x0000B520u))"
            ) == 1
            if matrixmenu_ui_first
            else aknappui.count(
                "if (aStage < 0x0000B51Cu || aStage > 0x0000B520u)"
            ) == 1
        ),
        "all internal stages": all(
            aknappui.count(f"0x0000{stage:04X}u")
            == (
                2 if homescreen_trace and stage == 0xB500
                else 3 if homescreen_trace and stage == 0xB520
                else 2 if stage == 0xB51C
                else 2 if not homescreen_trace and stage == 0xB520
                else 1
            )
            for stage in stages
        ),
        "fixed-screen branch": (
            aknappui.count("if (!htcleoUiFirstFixedPanel)") == 1
            if matrixmenu_ui_first
            else aknappui.count(
                "if (!(RProcess().SecureId().iId == 0x10003A4A))"
            ) == 1
        ),
        "non-EikSrv stock call retained": aknappui.count(
            "iEikonEnv->RootWin().EnableScreenChangeEvents();"
        ) == 1,
        "screen-change compatibility result": aknappui.count(
            "htcleoScreenChangeResult, 0x5343524Eu"
        ) == 1,
        "fixed screen-size decision": (
            aknappui.count("htcleoUiFirstFixedPanel;") == 1
            if matrixmenu_ui_first
            else aknappui.count(
                "RProcess().SecureId().iId == 0x10003A4A;"
            ) == 2
        ),
        "non-EikSrv stock size query retained": aknappui.count(
            "        iAppUiBaseExtension->iApplicationRect =\n"
            "            iCoeEnv->ScreenDevice()->SizeInPixels();"
        ) == 1,
        "hardware-proven fixed panel size": aknappui.count(
            "iAppUiBaseExtension->iApplicationRect = TSize(480, 800);"
        ) == 2,
        "screen-size compatibility detail": aknappui.count(
            "htcleoUseFixedScreenSize ? 0x53495A45u : 0u"
        ) == 1,
        "EikSrv-only tactile deferral": aknappui.count(
            "const TBool htcleoDeferTactileFeedback = htcleoUseFixedScreenSize;"
        ) == 1,
        "non-EikSrv tactile construction retained": aknappui.count(
            "CTouchFeedbackAdaptation::NewL();"
        ) == 1,
        "tactile compatibility detail": aknappui.count("0x48415054u") == 1,
        "nullable compatibility-mode tactile notification": aknappui.count(
            "if (iAppUiBaseExtension->iFeedbackAdaptation)\n"
            "            {\n"
            "            iAppUiBaseExtension->iFeedbackAdaptation->LayoutChanged();"
        ) == 1,
        "EikSrv-only transition-effects deferral": (
            aknappui.count(
                "const TBool htcleoDeferTransitionEffects ="
            ) == 1
            and aknappui.count("if (!htcleoDeferTransitionEffects)") == 1
            and aknappui.count("0x54524E46u") == 1
            and aknappui.count("0x54524E53u") == 1
        ),
        "non-EikSrv stock transition calls retained": (
            aknappui.count(
                "iAvkonEnv->TransitionEvent(KAknTransitionEventFlags);"
            ) == 1
            and aknappui.count(
                "iAvkonEnv->TransitionEvent(AknTransEffect::EAppStartComplete);"
            ) == 1
        ),
        "outer trap": eiksrvui.count("TRAP(htcleoBaseConstructResult,") == 1,
        "outer result detail": eiksrvui.count("0x42415345u") == 1,
        "outer re-leave": eiksrvui.count(
            "User::LeaveIfError(htcleoBaseConstructResult);"
        ) == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "obsolete ignored MMP option absent": "OPTION GCCE -fpermissive" not in mmp,
        "case-exact Linux GCCE def": mmp.count(LINUX_GCCE_DEFFILE) == 1,
        "no generic case-folded def": GENERIC_DEFFILE not in mmp,
        "case-exact Linux GCCE libraries": all(
            mmp.count(correct) == 1 and wrong not in mmp
            for wrong, correct in GCCE_LIBRARY_CASE_FIXES.items()
        ),
        "three exact GCCE constructor aliases": (
            aknlists.count(TEMPLATE_ALIAS_MARKER) == 1
            and aknlists.count(".global _ZN23AknListBoxLinesTemplate") == 3
            and aknlists.count("EC1Ei, _ZN23AknListBoxLinesTemplate") == 3
        ),
        "no delay": "User::After" not in HELPER,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknAppUi BaseConstruct durable-log verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()

    avkon = args.epocroot / "sf/mw/classicui/uifw/AvKon"
    aknappui_path = avkon / "src/AknAppUi.cpp"
    aknlists_path = avkon / "src/aknlists.cpp"
    # The active STEM recipe maps stem_avkon.dll to sys\\bin\\avkon.dll.
    # Its breakdeps MMP, not the ordinary avkon.mmp, is therefore authoritative.
    mmp_path = args.epocroot / "sf/incubator/stemkit/breakdeps/avkon.mmp"
    inactive_mmp_path = avkon / "group/avkon.mmp"
    eiksrvui_path = (
        args.epocroot
        / "sf/mw/classicui/uifw/EikStd/srvuisrc/EIKSRVUI.CPP"
    )

    aknappui = aknappui_path.read_text(encoding="latin-1")
    aknlists = aknlists_path.read_text(encoding="latin-1")
    eiksrvui = eiksrvui_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    inactive_mmp = inactive_mmp_path.read_text(encoding="latin-1")

    if MARKER not in aknappui:
        aknappui = install_aknappui(aknappui)
    if SCREEN_CHANGE_COMPAT_MARKER not in aknappui:
        aknappui = install_screen_change_compat(aknappui)
    if SCREEN_SIZE_COMPAT_MARKER not in aknappui:
        aknappui = install_screen_size_compat(aknappui)
    if TACTILE_FEEDBACK_COMPAT_MARKER not in aknappui:
        aknappui = install_tactile_feedback_compat(aknappui)
    if TRANSITION_EFFECTS_COMPAT_MARKER not in aknappui:
        aknappui = install_transition_effects_compat(aknappui)
    if LOG_CLOSE_ONLY_MARKER not in aknappui:
        aknappui = install_log_close_only(aknappui)
    if LOG_FRONTIER_ONLY_MARKER not in aknappui:
        aknappui = install_log_frontier_only(aknappui)
    if TEMPLATE_ALIAS_MARKER not in aknlists:
        aknlists += TEMPLATE_C1_ALIASES
    if OUTER_MARKER not in eiksrvui:
        eiksrvui = install_outer(eiksrvui)
    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"
    # SBSv2 ignores OPTION GCCE. The isolated avkon_permissive Raptor variant
    # supplies -fpermissive without weakening any other target.
    mmp = mmp.replace("\nOPTION GCCE -fpermissive\n", "\n")
    if GENERIC_DEFFILE in mmp:
        mmp = mmp.replace(GENERIC_DEFFILE, LINUX_GCCE_DEFFILE, 1)
    if PREVIOUS_LINUX_DEFFILE in mmp:
        mmp = mmp.replace(PREVIOUS_LINUX_DEFFILE, LINUX_GCCE_DEFFILE, 1)
    if EPOCROOT_RELATIVE_DEFFILE in mmp:
        mmp = mmp.replace(EPOCROOT_RELATIVE_DEFFILE, LINUX_GCCE_DEFFILE, 1)
    # The original MMP was authored for a case-insensitive Windows host.  Use
    # the exact spellings of the PDK's existing import DSOs on Linux; this is a
    # host-build compatibility correction and does not replace runtime DLLs.
    for wrong, correct in GCCE_LIBRARY_CASE_FIXES.items():
        if wrong in mmp:
            mmp = mmp.replace(wrong, correct, 1)

    # Raptor appends the Unicode suffix and looks for AVKONu.DEF. The PDK ships
    # the same frozen DEF only as AVKONU.DEF; provide a byte-identical
    # case-correct alias for Linux without changing the ordinal contract.
    frozen_def_path = avkon / "EABI/AVKONU.DEF"
    frozen_def_alias_path = avkon / "EABI/AVKONu.DEF"
    frozen_def = frozen_def_path.read_bytes()
    if not frozen_def_alias_path.is_file() or frozen_def_alias_path.read_bytes() != frozen_def:
        frozen_def_alias_path.write_bytes(frozen_def)
    inactive_mmp = inactive_mmp.replace(f"\nMACRO          {MACRO}\n", "\n")

    verify(aknappui, aknlists, eiksrvui, mmp)
    # Preserve mtimes for byte-identical inputs so SBS can genuinely reuse the
    # large Avkon object cache on later immutable incremental iterations.
    for path, original, transformed in (
        (aknappui_path, aknappui_path.read_text(encoding="latin-1"), aknappui),
        (aknlists_path, aknlists_path.read_text(encoding="latin-1"), aknlists),
        (eiksrvui_path, eiksrvui_path.read_text(encoding="latin-1"), eiksrvui),
        (mmp_path, mmp_path.read_text(encoding="latin-1"), mmp),
        (
            inactive_mmp_path,
            inactive_mmp_path.read_text(encoding="latin-1"),
            inactive_mmp,
        ),
    ):
        if transformed != original:
            path.write_text(transformed, encoding="latin-1")
    if frozen_def_alias_path.read_bytes() != frozen_def:
        raise SystemExit("Avkon frozen DEF Linux alias mismatch")
    print(
        "HTCLEO_AKNAPPUI_BASECONSTRUCT_DURABLE_LOG=installed "
        "stages=B500-B520 outer=E7A3-result-releave "
        "screen-change=eiksrv-fixed-screen-ui-first "
        "screen-size=eiksrv-fixed-480x800-ui-first "
        "tactile-feedback=eiksrv-deferred-ui-first "
        "transition-effects=eiksrv-deferred-ui-first "
        "log-flush=close-only log-scope=frontier-b51c-b520"
    )


if __name__ == "__main__":
    main()
