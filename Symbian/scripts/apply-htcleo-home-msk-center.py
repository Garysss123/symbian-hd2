#!/usr/bin/env python3
"""Center Home page indicator and keep its legacy Xn hit test aligned."""

from __future__ import annotations
import argparse
from pathlib import Path

CBA_MARKER = "HTCLEO_HOME_MSK_CENTER_V1"
XNA_MARKER = "HTCLEO_HOME_MSK_HIT_COORDINATE_V1"
DEFER_MARKER = "HTCLEO_HOME_MENU_AFTER_POINTER_DISPATCH_V1"
MENU_HELPER = r'''
// HTCLEO_HOME_MENU_EXISTING_TASK_V1
static TInt HtcleoHomeShowMatrixL(RWsSession& aWs)
    {
    HtcleoXnGeometryLog(0x48581755u, KErrNone, 0x101f4cd2u);
    // HTCLEO_HOME_MENU_HEAP_ARRAY_V1
    // CArrayFixBase relies on CBase::operator new zero-initializing iCount
    // and iBase. A stack instance leaves those members uninitialized.
    CArrayFixFlat<TInt>* groups = new(ELeave) CArrayFixFlat<TInt>(8);
    CleanupStack::PushL(groups);
    HtcleoXnGeometryLog(0x48581759u, KErrNone, (TUint32)groups->Count());
    TInt result = aWs.WindowGroupList(groups);
    HtcleoXnGeometryLog(0x4858175Au, result, (TUint32)groups->Count());
    if (result != KErrNone)
        {
        CleanupStack::PopAndDestroy(groups);
        return result;
        }
    for (TInt i = 0; i < groups->Count(); ++i)
        {
        const TInt group = (*groups)[i];
        TThreadId tid;
        if (aWs.GetWindowGroupClientThreadId(group, tid) != KErrNone)
            continue;
        RThread thread;
        if (thread.Open(tid) != KErrNone)
            continue;
        RProcess owner;
        result = thread.Process(owner);
        thread.Close();
        if (result != KErrNone)
            continue;
        const TBool matrix = owner.SecureId().iId == 0x101f4cd2u &&
            owner.ExitType() == EExitPending;
        owner.Close();
        if (!matrix)
            continue;
        HtcleoXnGeometryLog(0x48581756u, group, 0x101f4cd2u);
        // HTCLEO_HOME_MENU_PRIORITY_SAFE_ORDINAL_V2
        // 729 proved this real WServ operation immediately puts Matrix in
        // front, but Home lost foreground process priority before the sync
        // reply could run. 730's replacement message cannot be dispatched
        // while Matrix is busy. Freeze Home at its current foreground level
        // for this one stock shell handoff, then restore normal WServ priority
        // control after the real ordinal call returns.
        aWs.ComputeMode(RWsSession::EPriorityControlDisabled);
        const TInt ordinalResult = aWs.SetWindowGroupOrdinalPosition(group, 0);
        aWs.ComputeMode(RWsSession::EPriorityControlComputeOff);
        // Restore default priority control before any file-backed evidence.
        HtcleoXnGeometryLog(0x4858175Bu, ordinalResult, (TUint32)group);
        HtcleoXnGeometryLog(0x4858175Cu, KErrNone, (TUint32)group);
        CleanupStack::PopAndDestroy(groups);
        return ordinalResult;
        }
    CleanupStack::PopAndDestroy(groups);
    return KErrNotFound;
    }

'''


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Home MSK anchor mismatch: {old[:96]!r}")
    return text.replace(old, new, 1)


def patch_cba(text: str) -> str:
    if CBA_MARKER in text:
        return text
    anchor = "                TRect rect( qgn_graf_sk_msk.Rect() );"
    text = once(text, anchor, anchor + r'''
                // HTCLEO_HOME_MSK_CENTER_V1
                // qHD CDL supplies a fixed center; use the actual CBA width.
                // Keep indicator size, y and pressed-state offset unchanged.
                if (RProcess().SecureId().iId == 0x102750f0u &&
                    Size().iWidth == 480 && !isLandscape)
                    rect.Move((Size().iWidth - rect.Width()) / 2 - rect.iTl.iX, 0);
''')
    start = text.index("TRect CEikCba::ButtonRectByPosition(")
    end = text.index("\nvoid CEikCba::", start)
    section = text[start:end]
    section = once(section, "                rect = buttonMSKRect;",
        r'''                rect = buttonMSKRect;
                // Keep the native CBA hit rectangle under the centered image.
                if (RProcess().SecureId().iId == 0x102750f0u &&
                    containerRect.Width() == 480 && !rect.IsEmpty() &&
                    (AknLayoutFlags() & EAknLayoutCbaInControlPane))
                    rect.Move(containerRect.iTl.iX +
                        (containerRect.Width() - rect.Width()) / 2 - rect.iTl.iX, 0);''')
    return text[:start] + section + text[end:]


DISPATCH = r'''                    // HTCLEO_HOME_MSK_HIT_COORDINATE_V1
                    TPointerEvent htcleoMenuEvent(*aEvent.Pointer());
                    const TBool htcleoHome =
                        RProcess().SecureId().iId == 0x102750f0u;
                    if (htcleoHome)
                        {
                        // Xn menu DLL still computes g7 in qHD coordinates.
                        // Translate only the real centered MSK hit back to
                        // that existing hit test; other points stay untouched.
                        const TRect area(cba->PositionRelativeToScreen(), cba->Size());
                        TBool htcleoCenterHit = EFalse;
                        if (area.Width() == 480 && area.Height() <= 160)
                            {
                            TAknLayoutRect legacyLayout;
                            legacyLayout.LayoutRect(area,
                                AknLayoutScalable_Avkon::control_pane_g7(0).LayoutLine());
                            const TRect legacy(legacyLayout.Rect());
                            if (!legacy.IsEmpty())
                                {
                                const TInt delta = area.iTl.iX +
                                    (area.Width() - legacy.Width()) / 2 - legacy.iTl.iX;
                                TRect centered(legacy);
                                centered.Move(delta, 0);
                                if (centered.Contains(htcleoMenuEvent.iParentPosition))
                                    {
                                    htcleoCenterHit = ETrue;
                                    htcleoMenuEvent.iParentPosition.iX -= delta;
                                    }
                                }
                            TAknLayoutRect rightLayout;
                            rightLayout.LayoutRect(area,
                                AknLayoutScalable_Avkon::control_pane_g8(0).LayoutLine());
                            // Normal Home RSK is now Menu. Preserve popup Back
                            // and editing Done by leaving those modes stock.
                            if (!htcleoCenterHit && !iUiEngine.IsMenuDisplaying() &&
                                !iUiEngine.IsEditMode() &&
                                rightLayout.Rect().Contains(aEvent.Pointer()->iParentPosition))
                                {
                                if (htcleoMenuEvent.iType != TPointerEvent::EDrag)
                                    HtcleoXnGeometryLog(0x48581753u,
                                        htcleoMenuEvent.iType, 0x4d454e55u);
                                if (htcleoMenuEvent.iType == TPointerEvent::EButton1Down)
                                    iHtcleoMenuDown = ETrue;
                                else if (htcleoMenuEvent.iType == TPointerEvent::EButton1Up)
                                    {
                                    const TBool activate = iHtcleoMenuDown;
                                    iHtcleoMenuDown = EFalse;
                                    if (activate)
                                        {
                                        TInt taskResult = KErrNone;
                                        TRAPD(taskLeave, taskResult =
                                            HtcleoHomeShowMatrixL(iCoeEnv->WsSession()));
                                        HtcleoXnGeometryLog(0x48581758u,
                                            taskLeave == KErrNone ? taskResult : taskLeave, 0u);
                                        }
                                    }
                                return;
                                }
                            }
                        if (htcleoMenuEvent.iType == TPointerEvent::EButton1Up)
                            iHtcleoMenuDown = EFalse;
                        if (htcleoMenuEvent.iType != TPointerEvent::EDrag)
                            {
                            HtcleoXnGeometryLog(0x48581750u,
                                htcleoMenuEvent.iType,
                                ((TUint32)(aEvent.Pointer()->iParentPosition.iX & 0xffff) << 16) |
                                (TUint32)(aEvent.Pointer()->iParentPosition.iY & 0xffff));
                            HtcleoXnGeometryLog(0x48581751u,
                                htcleoMenuEvent.iType,
                                ((TUint32)(htcleoMenuEvent.iParentPosition.iX & 0xffff) << 16) |
                                (TUint32)(htcleoMenuEvent.iParentPosition.iY & 0xffff));
                            }
                        }
                    TRAPD(htcleoMenuResult,
                        adapter->HandlePointerEventL(htcleoMenuEvent));
                    if (htcleoHome && htcleoMenuEvent.iType != TPointerEvent::EDrag)
                        HtcleoXnGeometryLog(0x48581752u,
                            htcleoMenuResult, (TUint32)htcleoMenuEvent.iType);
'''


def patch_dispatcher(text: str) -> str:
    if XNA_MARKER in text:
        if ("HTCLEO_HOME_MENU_HEAP_ARRAY_V1" not in text or
                "HTCLEO_HOME_MENU_PRIORITY_SAFE_ORDINAL_V2" not in text):
            start = text.index("// HTCLEO_HOME_MENU_EXISTING_TASK_V1")
            end = text.index("\n    }\n", start) + len("\n    }\n")
            text = text[:start] + MENU_HELPER.strip() + "\n" + text[end:]
        return patch_deferred_dispatch(text)
    text = once(text, "#include <AknUtils.h>\n",
        "#include <AknUtils.h>\n#include <aknlayoutscalable_avkon.cdl.h>\n"
        "extern void HtcleoXnGeometryLog(TUint32, TInt, TUint32);\n")
    text = once(text, "const TInt KOneView = 1;\n", "const TInt KOneView = 1;\n" + MENU_HELPER)
    text = once(text, "    : iUiEngine( aUiEngine )\n",
                "    : iUiEngine( aUiEngine ), iHtcleoMenuDown(EFalse)\n")
    text = once(text,
        "                    TRAP_IGNORE( \n"
        "                        adapter->HandlePointerEventL( *aEvent.Pointer() ) );",
        DISPATCH.rstrip())
    text = once(text,
        "    TKeyResponse resp( EKeyWasNotConsumed );",
        '''    // HTCLEO_HOME_CALL_REPLACED_BY_MENU_V1
    if (RProcess().SecureId().iId == 0x102750f0u &&
        aKeyEvent.iScanCode == EStdKeyDevice1 &&
        !iUiEngine.IsMenuDisplaying() && !iUiEngine.IsEditMode())
        {
        if (aType == EEventKey)
            {
            TInt taskResult = KErrNone;
            TRAPD(taskLeave, taskResult = HtcleoHomeShowMatrixL(iCoeEnv->WsSession()));
            HtcleoXnGeometryLog(0x48581754u,
                taskLeave == KErrNone ? taskResult : taskLeave, 0x4d454e55u);
            }
        return EKeyWasConsumed;
        }
    TKeyResponse resp( EKeyWasNotConsumed );''')
    # Both initial menu binding and normal refresh can reinstall the softkeys.
    old = "        menuAdapter->SetContainerL( *iCbaContainer );"
    if text.count(old) != 2:
        raise SystemExit("Home CBA binding anchors changed")
    text = text.replace(old, old + '''
        if (RProcess().SecureId().iId == 0x102750f0u &&
            !iUiEngine.IsMenuDisplaying() && !iUiEngine.IsEditMode())
            {
            // The real CBA keeps the label and visual press feedback; command
            // zero prevents a second Back/Call action after our pointer route.
            _LIT(KHtcleoMenuLabel, "Menu");
            iCbaContainer->SetCommandL(
                CEikButtonGroupContainer::ERightSoftkeyPosition, 0, KHtcleoMenuLabel);
            iCbaContainer->DimCommandByPosition(
                CEikButtonGroupContainer::ERightSoftkeyPosition, EFalse);
            }
''')
    return patch_deferred_dispatch(text)


DEFERRED_CALLBACK = r'''
// HTCLEO_HOME_MENU_AFTER_POINTER_DISPATCH_V1
TInt CXnKeyEventDispatcher::HtcleoQueueMenu()
    {
    if (!iHtcleoMenuCallback)
        return KErrNotReady;
    if (!iHtcleoMenuCallback->IsActive())
        {
        // MonitorWsMessage precedes the real CBA HandlePointerEventL. Only
        // enqueue here: the release, grab and pressed-state redraw must run
        // while Home still owns the foreground. No timer or synthetic input.
        HtcleoXnGeometryLog(0x4858175Du, KErrNone, 0x51554555u);
        iHtcleoMenuCallback->CallBack();
        }
    return KErrNone;
    }

TInt CXnKeyEventDispatcher::HtcleoMenuCallback(TAny* aSelf)
    {
    CXnKeyEventDispatcher* self = static_cast<CXnKeyEventDispatcher*>(aSelf);
    // The normal event handler must return before this scheduler callback.
    HtcleoXnGeometryLog(0x4858175Eu, KErrNone, 0x41465452u);
    TInt taskResult = KErrNone;
    TRAPD(taskLeave, taskResult =
        HtcleoHomeShowMatrixL(self->iCoeEnv->WsSession()));
    HtcleoXnGeometryLog(0x48581758u,
        taskLeave == KErrNone ? taskResult : taskLeave, 0u);
    return KErrNone;
    }

'''


def patch_deferred_dispatch(text: str) -> str:
    if DEFER_MARKER in text:
        return text
    text = once(text,
        "    : iUiEngine( aUiEngine ), iHtcleoMenuDown(EFalse)\n",
        "    : iUiEngine( aUiEngine ), iHtcleoMenuDown(EFalse),\n"
        "      iHtcleoMenuCallback(NULL)\n")
    text = once(text,
        "CXnKeyEventDispatcher::~CXnKeyEventDispatcher()\n    {\n",
        "CXnKeyEventDispatcher::~CXnKeyEventDispatcher()\n    {\n"
        "    if (iHtcleoMenuCallback)\n"
        "        iHtcleoMenuCallback->Cancel();\n"
        "    delete iHtcleoMenuCallback;\n"
        "    iHtcleoMenuCallback = NULL;\n")
    text = once(text,
        "void CXnKeyEventDispatcher::ConstructL()\n    {\n",
        "void CXnKeyEventDispatcher::ConstructL()\n    {\n"
        "    if (RProcess().SecureId().iId == 0x102750f0u)\n"
        "        iHtcleoMenuCallback = new(ELeave) CAsyncCallBack(\n"
        "            TCallBack(HtcleoMenuCallback, this), CActive::EPriorityStandard);\n")
    text = once(text,
        "                                        TInt taskResult = KErrNone;\n"
        "                                        TRAPD(taskLeave, taskResult =\n"
        "                                            HtcleoHomeShowMatrixL(iCoeEnv->WsSession()));\n"
        "                                        HtcleoXnGeometryLog(0x48581758u,\n"
        "                                            taskLeave == KErrNone ? taskResult : taskLeave, 0u);",
        "                                        (void)HtcleoQueueMenu();")
    text = once(text,
        "            TInt taskResult = KErrNone;\n"
        "            TRAPD(taskLeave, taskResult = HtcleoHomeShowMatrixL(iCoeEnv->WsSession()));\n"
        "            HtcleoXnGeometryLog(0x48581754u,\n"
        "                taskLeave == KErrNone ? taskResult : taskLeave, 0x4d454e55u);",
        "            const TInt queueResult = HtcleoQueueMenu();\n"
        "            HtcleoXnGeometryLog(0x48581754u, queueResult, 0x4d454e55u);")
    return once(text,
        "void CXnKeyEventDispatcher::MonitorWsMessage( const TWsEvent& aEvent )",
        DEFERRED_CALLBACK +
        "void CXnKeyEventDispatcher::MonitorWsMessage( const TWsEvent& aEvent )")


def patch_header(text: str) -> str:
    if "TBool iHtcleoMenuDown;" not in text:
        text = once(text, "    TPointerEvent iPointerEvent;",
                    "    TPointerEvent iPointerEvent;\n    TBool iHtcleoMenuDown;")
    if "CAsyncCallBack* iHtcleoMenuCallback;" not in text:
        text = once(text, "    TBool iHtcleoMenuDown;",
                    "    TBool iHtcleoMenuDown;\n"
                    "    CAsyncCallBack* iHtcleoMenuCallback; // owned\n"
                    "    TInt HtcleoQueueMenu();\n"
                    "    static TInt HtcleoMenuCallback(TAny* aSelf);")
    return text


def verify(cba: str, dispatcher: str, header: str) -> None:
    if cba.count(CBA_MARKER) != 1 or dispatcher.count(XNA_MARKER) != 1:
        raise SystemExit("Home MSK markers failed")
    if cba.count("rect.Move((Size().iWidth - rect.Width()) / 2 - rect.iTl.iX, 0);") != 1:
        raise SystemExit("Home MSK visual center check failed")
    if dispatcher.count("centered.Contains(htcleoMenuEvent.iParentPosition)") != 1:
        raise SystemExit("Home MSK hit translation check failed")
    for stage in range(0x1750, 0x175D):
        if stage == 0x1757:
            continue  # Removed inline focus query; WS heartbeat owns evidence.
        if dispatcher.count(f"0x4858{stage:04X}u") != 1:
            raise SystemExit("Home CBA event boundary check failed")
    if any(x in DISPATCH for x in ("SetWindowGroupOrdinalPosition", "ActivateView", "CreateWindow", "User::After")):
        raise SystemExit("unexpected CBA behavior change")
    if dispatcher.count("HTCLEO_HOME_CALL_REPLACED_BY_MENU_V1") != 1:
        raise SystemExit("Home Menu replacement marker missing")
    if "owner.SecureId().iId == 0x101f4cd2u" not in dispatcher:
        raise SystemExit("Matrix task owner check missing")
    if header.count("TBool iHtcleoMenuDown;") != 1:
        raise SystemExit("Menu press state missing")
    if "CArrayFixFlat<TInt> groups(" in dispatcher:
        raise SystemExit("CBase-derived arrays must not be constructed on the stack")
    if dispatcher.count("new(ELeave) CArrayFixFlat<TInt>(8)") != 1:
        raise SystemExit("Menu array must use zero-filled CBase heap allocation")
    if dispatcher.count("CleanupStack::PopAndDestroy(groups);") != 3:
        raise SystemExit("Menu array cleanup paths changed")
    helper = dispatcher[dispatcher.index("static TInt HtcleoHomeShowMatrixL("):
                        dispatcher.index("\n    }\n", dispatcher.index("static TInt HtcleoHomeShowMatrixL("))]
    if any(call in helper for call in
           ("aWs.Finish()", "aWs.GetFocusWindowGroup()", "SendMessageToWindowGroup", "BringToForeground")):
        raise SystemExit("Home Menu must use the proven ordinal path without rendering waits")
    if ("HTCLEO_HOME_MENU_PRIORITY_SAFE_ORDINAL_V2" not in helper or
            helper.count("SetWindowGroupOrdinalPosition(group, 0)") != 1 or
            helper.count("ComputeMode(RWsSession::EPriorityControlDisabled)") != 1 or
            helper.count("ComputeMode(RWsSession::EPriorityControlComputeOff)") != 1):
        raise SystemExit("priority-safe real ordinal handoff missing")
    if not (helper.index("EPriorityControlDisabled") <
            helper.index("SetWindowGroupOrdinalPosition(group, 0)") <
            helper.index("EPriorityControlComputeOff") <
            helper.index("HtcleoXnGeometryLog(0x4858175Bu")):
        raise SystemExit("Home priority freeze/ordinal/restore order changed")
    if dispatcher.count(DEFER_MARKER) != 1:
        raise SystemExit("Home Menu deferred-dispatch marker missing")
    monitor_start = dispatcher.index("void CXnKeyEventDispatcher::MonitorWsMessage(")
    monitor_end = dispatcher.index("const TPointerEvent& CXnKeyEventDispatcher::PointerEvent()", monitor_start)
    monitor = dispatcher[monitor_start:monitor_end]
    if ("HtcleoHomeShowMatrixL(" in monitor or
            "SetWindowGroupOrdinalPosition" in monitor or
            "(void)HtcleoQueueMenu();" not in monitor):
        raise SystemExit("Home monitor must queue instead of changing foreground inline")
    if (dispatcher.count("HtcleoHomeShowMatrixL(") != 2 or
            dispatcher.count("iHtcleoMenuCallback->CallBack();") != 1 or
            dispatcher.count("iHtcleoMenuCallback->Cancel();") != 1 or
            dispatcher.count("delete iHtcleoMenuCallback;") != 1 or
            dispatcher.count("if (!iHtcleoMenuCallback->IsActive())") != 1 or
            dispatcher.count("new(ELeave) CAsyncCallBack(") != 1 or
            header.count("CAsyncCallBack* iHtcleoMenuCallback;") != 1):
        raise SystemExit("Home callback ownership or single-flight contract changed")
    for stage in ("0x4858175Du", "0x4858175Eu"):
        if dispatcher.count(stage) != 1:
            raise SystemExit("Home queue/callback evidence missing")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    cba_path = args.root / "sf/mw/classicui/uifw/EikStd/coctlsrc/eikcba.cpp"
    dispatcher_path = args.root / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src/xnkeyeventdispatcher.cpp"
    header_path = dispatcher_path.parent.parent / "inc/xnkeyeventdispatcher.h"
    cba = patch_cba(cba_path.read_text(encoding="latin-1"))
    dispatcher = patch_dispatcher(dispatcher_path.read_text(encoding="utf-8"))
    header = patch_header(header_path.read_text(encoding="utf-8"))
    verify(cba, dispatcher, header)
    cba_path.write_text(cba, encoding="latin-1")
    dispatcher_path.write_text(dispatcher, encoding="utf-8")
    header_path.write_text(header, encoding="utf-8")
    print("HTCLEO_HOME_MSK_CENTER=physical480-center-image-and-hit-normal-home-menu-rsk")
    print("HTCLEO_HOME_MENU_ARRAY=heap-cbase-zero-init-cleanupstack-no-stack-array")
    print("HTCLEO_HOME_MENU_HANDOFF=priority-freeze-real-ordinal-restore-no-render-wait-175b-175c")
    print("HTCLEO_HOME_MENU_DISPATCH=owned-async-after-cba-event-no-inline-ordinal-175d-175e")


if __name__ == "__main__":
    main()
