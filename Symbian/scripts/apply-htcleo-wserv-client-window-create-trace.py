#!/usr/bin/env python3
"""Trace the real Window Server client-window creation path on HTC Leo.

Iteration 549 proves the ROM-declared grid presentation is ready and enters the
real CMmGridContainer constructor, whose final record is immediately before
CCoeControl::CreateWindowL().  Iteration 554 then proves that an exact-handle
filter records no server request even after the SID assumption is removed.
Arm on the published property instead: the first WServ request after the
property exists records the property read result, published pointer, actual
owner SID and actual client handle, then follows that actual request through
the existing window-construction stages.  Behavior and error policy are
unchanged; the existing bounded WSLOG writer remains the sole logger.
"""

from __future__ import annotations

import argparse
from pathlib import Path


CLIENT_MARKER = "HTCLEO_WSERV_CLIENT_WINDOW_CREATE_TRACE_V1"
WINDOW_MARKER = "HTCLEO_WSERV_CLIENT_WINDOW_CONSTRUCT_TRACE_V1"
MACRO = "__HTCLEO_WSERV_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


DECLARATION = r'''
#ifdef __HTCLEO_WSERV_DURABLE_LOG__
#include <e32property.h>
extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
// HTCLEO_WSERV_ARMED_REQUEST_TRACE_V2
static inline void HtcleoMatrixMenuWsLog(
        const CWsClient* aClient,
        TUint32 aClientHandle,
        TUint32 aStage,
        TInt aResult,
        TUint32 aDetail)
    {
    TInt htcleoGridHandle = 0;
    const TInt htcleoHandleResult = RProperty::Get(
        TUid::Uid(0x101F4CD2), 0x7F4D5701u, htcleoGridHandle);
    static TBool htcleoOwnerLogged = EFalse;
    static TUint32 htcleoArmedClientHandle = 0u;
    if (aClient
            && !htcleoOwnerLogged
            && htcleoHandleResult != KErrNotFound)
        {
        HtcleoWsLog(0x00000430u,
            htcleoHandleResult,
            (TUint32)htcleoGridHandle);
        HtcleoWsLog(0x00000431u,
            (TInt)aClient->SecureId().iId,
            aClientHandle);
        HtcleoWsLog(0x00000432u,
            (aClientHandle == (TUint32)htcleoGridHandle) ? 1 : 0,
            aStage);
        if (htcleoHandleResult == KErrNone
                && htcleoGridHandle != 0)
            {
            htcleoArmedClientHandle = aClientHandle;
            }
        htcleoOwnerLogged = ETrue;
        }
    if (aClient
            && htcleoArmedClientHandle != 0u
            && aClientHandle == htcleoArmedClientHandle)
        {
        HtcleoWsLog(aStage, aResult, aDetail);
        }
    }
#else
static inline void HtcleoMatrixMenuWsLog(
        const CWsClient*, TUint32, TUint32, TInt, TUint32) {}
#endif
'''

OLD_DECLARATION = r'''
#ifdef __HTCLEO_WSERV_DURABLE_LOG__
extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#endif
'''


OLD_CLIENT = r'''void CWsClient::CreateNewWindowL(const TWsClCmdCreateWindow &aCmd)
	{
	CWsWindowBase* parent;
	HandleToWindow(aCmd.parent,&parent);
	CWsClientWindow* win = NULL;
	TBool deviceIsInvalid = EFalse;
	CScreen* screen = parent->Screen();
	if (parent->WinType()==EWinTypeGroup)
		{
		__ASSERT_DEBUG(!((CWsWindowGroup*)parent)->ScreenDeviceDeleted(),PPanic(EWservPanicGroupWinScreenDeviceDeleted));
		win=new(ELeave) CWsTopClientWindow(this, screen);
		deviceIsInvalid=!((CWsWindowGroup*)parent)->ScreenDeviceValid();
		}
	else
		win=new(ELeave) CWsClientWindow(this, screen);

	CleanupStack::PushL(win);
	win->ConstructL(aCmd,parent,deviceIsInvalid);
	CleanupStack::Pop(win);
	}'''


NEW_CLIENT = r'''void CWsClient::CreateNewWindowL(const TWsClCmdCreateWindow &aCmd)
	{
	// HTCLEO_WSERV_CLIENT_WINDOW_CREATE_TRACE_V1
	HtcleoWsLog(0x00000400u, KErrNone, aCmd.parent);
	CWsWindowBase* parent;
	HandleToWindow(aCmd.parent,&parent);
	HtcleoWsLog(0x00000401u, KErrNone,
		parent ? (TUint32)parent->WinType() : 0xFFFFFFFFu);
	CWsClientWindow* win = NULL;
	TBool deviceIsInvalid = EFalse;
	CScreen* screen = parent->Screen();
	HtcleoWsLog(0x00000402u, KErrNone, screen ? 1u : 0u);
	HtcleoWsLog(0x00000403u, KErrNone,
		parent->WinType()==EWinTypeGroup ? 1u : 0u);
	if (parent->WinType()==EWinTypeGroup)
		{
		__ASSERT_DEBUG(!((CWsWindowGroup*)parent)->ScreenDeviceDeleted(),PPanic(EWservPanicGroupWinScreenDeviceDeleted));
		win=new(ELeave) CWsTopClientWindow(this, screen);
		deviceIsInvalid=!((CWsWindowGroup*)parent)->ScreenDeviceValid();
		}
	else
		{
		win=new(ELeave) CWsClientWindow(this, screen);
		}
	HtcleoWsLog(0x00000404u, KErrNone, win ? 1u : 0u);

	CleanupStack::PushL(win);
	HtcleoWsLog(0x00000405u, KErrNone,
		deviceIsInvalid ? 1u : 0u);
	win->ConstructL(aCmd,parent,deviceIsInvalid);
	HtcleoWsLog(0x00000406u, KErrNone, 1u);
	CleanupStack::Pop(win);
	HtcleoWsLog(0x00000407u, KErrNone, 1u);
	}'''


OLD_WINDOW = r'''void CWsClientWindow::ConstructL(const TWsClCmdCreateWindow &aCmd, CWsWindowBase *aParent, TBool aScreenDeviceIsInvalid)
	{
	CWsWindow::Construct();
	NewObjL();
	if (aCmd.clientHandle==NULL)
		OwnerPanic(EWservPanicNullHandle);
#if defined(_DEBUG)
	if (IsClientHandleInUse(aCmd.clientHandle))
		OwnerPanic(EWservPanicDuplicateHandle);
#endif
	iPointerFilter=EPointerFilterEnterExit|EPointerFilterMove|EPointerFilterDrag;
	iClientHandle=aCmd.clientHandle;
	CWsWindow* inherit=static_cast<CWsWindow *>(aParent);
	if (aParent->WinType()==EWinTypeGroup)
		inherit=RootWindow();
	SetPointerCursor(aParent->PointerCursor());
	iAbs=inherit->Abs();
	iOrigin=aParent->Origin();
	iRel.iBr.iX=inherit->Rel().iBr.iX-inherit->Rel().iTl.iX;
	iRel.iBr.iY=inherit->Rel().iBr.iY-inherit->Rel().iTl.iY;
	switch(aCmd.type)
		{
		case EWinRedraw:
			iRedraw=new(ELeave) CWsRedrawMsgWindow(this);
			break;
		case EWinBackedUp:
			iRedraw=new(ELeave) CWsBackedUpWindow(this, aCmd.displayMode);
			iAbs.iBr=iAbs.iTl;
			iRel.iBr=iRel.iTl;
			break;
		case EWinBlank:
			iRedraw=new(ELeave) CWsBlankWindow(this);
			break;
		default:
			OwnerPanic(EWservPanicRedrawType);
		}
	ResetHiddenFlag();
	SetCornerTypeL(EWindowCornerSquare,0,NULL,EFalse);
	CWsWindowBase::ConstructL(aParent);
	if (aScreenDeviceIsInvalid)
		{
		iFlags|=EFlagScreenDeviceInvalid;
		ResetHiddenFlag();
		}
	iRedraw->ConstructL();
	}'''


NEW_WINDOW = r'''void CWsClientWindow::ConstructL(const TWsClCmdCreateWindow &aCmd, CWsWindowBase *aParent, TBool aScreenDeviceIsInvalid)
	{
	// HTCLEO_WSERV_CLIENT_WINDOW_CONSTRUCT_TRACE_V1
	HtcleoWsLog(0x00000410u, KErrNone, aCmd.clientHandle);
	CWsWindow::Construct();
	HtcleoWsLog(0x00000411u, KErrNone, 0u);
	NewObjL();
	HtcleoWsLog(0x00000412u, KErrNone, 0u);
	if (aCmd.clientHandle==NULL)
		OwnerPanic(EWservPanicNullHandle);
#if defined(_DEBUG)
	if (IsClientHandleInUse(aCmd.clientHandle))
		OwnerPanic(EWservPanicDuplicateHandle);
#endif
	iPointerFilter=EPointerFilterEnterExit|EPointerFilterMove|EPointerFilterDrag;
	iClientHandle=aCmd.clientHandle;
	HtcleoWsLog(0x00000413u, KErrNone, iClientHandle);
	CWsWindow* inherit=static_cast<CWsWindow *>(aParent);
	if (aParent->WinType()==EWinTypeGroup)
		inherit=RootWindow();
	SetPointerCursor(aParent->PointerCursor());
	iAbs=inherit->Abs();
	iOrigin=aParent->Origin();
	iRel.iBr.iX=inherit->Rel().iBr.iX-inherit->Rel().iTl.iX;
	iRel.iBr.iY=inherit->Rel().iBr.iY-inherit->Rel().iTl.iY;
	HtcleoWsLog(0x00000414u, KErrNone,
		((TUint32)(iRel.iBr.iX & 0xFFFF) << 16)
			| (TUint32)(iRel.iBr.iY & 0xFFFF));
	HtcleoWsLog(0x00000415u, KErrNone, (TUint32)aCmd.type);
	switch(aCmd.type)
		{
		case EWinRedraw:
			iRedraw=new(ELeave) CWsRedrawMsgWindow(this);
			break;
		case EWinBackedUp:
			iRedraw=new(ELeave) CWsBackedUpWindow(this, aCmd.displayMode);
			iAbs.iBr=iAbs.iTl;
			iRel.iBr=iRel.iTl;
			break;
		case EWinBlank:
			iRedraw=new(ELeave) CWsBlankWindow(this);
			break;
		default:
			OwnerPanic(EWservPanicRedrawType);
		}
	HtcleoWsLog(0x00000416u, KErrNone, iRedraw ? 1u : 0u);
	ResetHiddenFlag();
	HtcleoWsLog(0x00000417u, KErrNone, 0u);
	HtcleoWsLog(0x00000418u, KErrNone, 0u);
	SetCornerTypeL(EWindowCornerSquare,0,NULL,EFalse);
	HtcleoWsLog(0x00000419u, KErrNone, 0u);
	HtcleoWsLog(0x0000041Au, KErrNone, 0u);
	CWsWindowBase::ConstructL(aParent);
	HtcleoWsLog(0x0000041Bu, KErrNone, 0u);
	if (aScreenDeviceIsInvalid)
		{
		iFlags|=EFlagScreenDeviceInvalid;
		ResetHiddenFlag();
		}
	HtcleoWsLog(0x0000041Cu, KErrNone,
		aScreenDeviceIsInvalid ? 1u : 0u);
	iRedraw->ConstructL();
	HtcleoWsLog(0x0000041Du, KErrNone, 0u);
	}'''


OLD_TOP = r'''void CWsTopClientWindow::ConstructL(const TWsClCmdCreateWindow &cmd, CWsWindowBase *aParent, TBool aScreenDeviceIsInvalid)
	{
	iFlags|=EFlagIsTopClientWindow;
	CWsClientWindow::ConstructL(cmd, aParent, aScreenDeviceIsInvalid);
	}'''


NEW_TOP = r'''void CWsTopClientWindow::ConstructL(const TWsClCmdCreateWindow &cmd, CWsWindowBase *aParent, TBool aScreenDeviceIsInvalid)
	{
	HtcleoWsLog(0x00000420u, KErrNone, 0u);
	iFlags|=EFlagIsTopClientWindow;
	CWsClientWindow::ConstructL(cmd, aParent, aScreenDeviceIsInvalid);
	HtcleoWsLog(0x00000421u, KErrNone, 0u);
	}'''


def install(client: str, window: str) -> tuple[str, str]:
    client = replace_once(
        client,
        '#include "windowelementset.h"\n',
        '#include "windowelementset.h"\n' + DECLARATION,
        "client logger declaration",
    )
    client_trace = NEW_CLIENT.replace(
        "\tHtcleoWsLog(",
        "\tHtcleoMatrixMenuWsLog(this, aCmd.clientHandle, ",
    )
    client = replace_once(client, OLD_CLIENT, client_trace, "client create window")
    window = replace_once(
        window,
        '#include "windowelementset.h"\n',
        '#include "windowelementset.h"\n' + DECLARATION,
        "window logger declaration",
    )
    window_trace = NEW_WINDOW.replace(
        "\tHtcleoWsLog(",
        "\tHtcleoMatrixMenuWsLog(WsOwner(), aCmd.clientHandle, ",
    )
    top_trace = NEW_TOP.replace(
        "\tHtcleoWsLog(",
        "\tHtcleoMatrixMenuWsLog(WsOwner(), cmd.clientHandle, ",
    )
    window = replace_once(window, OLD_WINDOW, window_trace, "window construct")
    window = replace_once(window, OLD_TOP, top_trace, "top window construct")
    return client, window


def verify(client: str, window: str) -> None:
    combined = client + window
    expected = [
        *range(0x00000400, 0x00000408),
        *range(0x00000410, 0x0000041E),
        0x00000420,
        0x00000421,
    ]
    checks = {
        "client marker": client.count(CLIENT_MARKER) == 1,
        "window marker": window.count(WINDOW_MARKER) == 1,
        "two declarations": combined.count(
            "extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);"
        ) == 2,
        "property-armed request filter": (
            combined.count("aClient->SecureId().iId") == 2
            and combined.count("0x7F4D5701u") >= 2
            and combined.count("0x00000430u") == 2
            and combined.count("0x00000431u") == 2
            and combined.count("0x00000432u") == 2
            and combined.count("HTCLEO_WSERV_ARMED_REQUEST_TRACE_V2") == 2
            and combined.count("htcleoHandleResult != KErrNotFound") == 2
            and combined.count("htcleoArmedClientHandle = aClientHandle") == 2
            and client.count(
                "HtcleoMatrixMenuWsLog(this, aCmd.clientHandle,"
            ) == 8
            and window.count(
                "HtcleoMatrixMenuWsLog(WsOwner(), aCmd.clientHandle,"
            ) == 14 + (
                1
                if "HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE_V1" in window
                else 0
            )
            and window.count(
                "HtcleoMatrixMenuWsLog(WsOwner(), cmd.clientHandle,"
            ) == 2
            and combined.count("\tHtcleoWsLog(")
            == (
                1
                if (
                    "HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V1"
                    in combined
                    or "HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V2"
                    in combined
                )
                else 0
            ) + (
                1
                if "HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1" in combined
                else 0
            ) + (
                2
                if "HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY_V1" in combined
                else 0
            ) + (
                1
                if "HTCLEO_WSERV_HOME_EXIT_ATTRIBUTION_V1" in combined
                else 0
            ) + (
                4
                if "HTCLEO_WSERV_SHELL_HANDOFF_TRACE_V1" in combined
                else 0
            )
        ),
        "all stages": all(
            combined.count(f"0x{stage:08X}u") == 1 for stage in expected
        ),
        "stock calls retained": (
            window.count("SetCornerTypeL(EWindowCornerSquare,0,NULL,EFalse);") == 1
            and window.count("CWsWindowBase::ConstructL(aParent);") == 1
            and window.count("iRedraw->ConstructL();") == 1
            and client.count("win->ConstructL(aCmd,parent,deviceIsInvalid);") == 1
        ),
        "behavior unchanged": (
            "TRAP" not in NEW_CLIENT
            and "TRAP" not in NEW_WINDOW
            and "User::After" not in NEW_CLIENT
            and "User::After" not in NEW_WINDOW
            and "KErrNotSupported" not in NEW_CLIENT
            and "KErrNotSupported" not in NEW_WINDOW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/os/graphics/windowing/windowserver"
    client_path = component / "nga/SERVER/openwfc/CLIENT.CPP"
    window_path = component / "nga/SERVER/openwfc/cliwin.cpp"
    client = client_path.read_text(encoding="utf-8")
    window = window_path.read_text(encoding="utf-8")
    if CLIENT_MARKER not in client and WINDOW_MARKER not in window:
        client, window = install(client, window)
    else:
        if "HTCLEO_WSERV_ARMED_REQUEST_TRACE_V2" not in client:
            client_decl_start = client.index(
                "#ifdef __HTCLEO_WSERV_DURABLE_LOG__\n"
            )
            client_decl_end = client.index(
                "#endif\n", client_decl_start
            ) + len("#endif\n")
            client = replace_once(
                client,
                client[client_decl_start:client_decl_end],
                DECLARATION,
                "installed client property-armed declaration",
            )
        if "HTCLEO_WSERV_ARMED_REQUEST_TRACE_V2" not in window:
            window_decl_start = window.index(
                "#ifdef __HTCLEO_WSERV_DURABLE_LOG__\n"
            )
            window_decl_end = window.index(
                "#endif\n", window_decl_start
            ) + len("#endif\n")
            window = replace_once(
                window,
                window[window_decl_start:window_decl_end],
                DECLARATION,
                "installed window property-armed declaration",
            )
    verify(client, window)
    client_path.write_text(client, encoding="utf-8")
    window_path.write_text(window, encoding="utf-8")
    print(
        "HTCLEO_WSERV_CLIENT_WINDOW_CREATE_TRACE="
        "property-armed-request-0430-0432-0400-0421-behavior-unchanged"
    )


if __name__ == "__main__":
    main()
