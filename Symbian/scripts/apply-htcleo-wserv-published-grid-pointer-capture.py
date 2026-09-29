#!/usr/bin/env python3
"""Capture the real published grid object when its WServ tree link is missing."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE_V1"

CLI_INCLUDE_ANCHOR = "#include <graphics/wselement.h>\n"
CLI_INCLUDE_NEW = CLI_INCLUDE_ANCHOR + "#include <e32property.h>\n"

CLI_DECL_ANCHOR = "TBool CWsClientWindow::iAbsoluteFading = EFalse;\n"
CLI_DECL_NEW = (
    "// HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE_V1\n"
    "CWsClientWindow* gHtcleoPublishedGridWindow = NULL;\n"
    + CLI_DECL_ANCHOR
)

CLI_CAPTURE_ANCHOR = r'''	iClientHandle=aCmd.clientHandle;
	HtcleoMatrixMenuWsLog(WsOwner(), aCmd.clientHandle, 0x00000413u, KErrNone, iClientHandle);
'''

CLI_CAPTURE_NEW = r'''	iClientHandle=aCmd.clientHandle;
	HtcleoMatrixMenuWsLog(WsOwner(), aCmd.clientHandle, 0x00000413u, KErrNone, iClientHandle);
	TInt htcleoPublishedHandle=0;
	if (WsOwner()->SecureId().iId==0x101F4CD2u &&
			RProperty::Get(TUid::Uid(0x101F4CD2), 0x7F4D5701u,
				htcleoPublishedHandle)==KErrNone &&
			htcleoPublishedHandle==static_cast<TInt>(iClientHandle))
		{
		gHtcleoPublishedGridWindow=this;
		HtcleoMatrixMenuWsLog(WsOwner(), aCmd.clientHandle,
			0x0000046Au, KErrNone,
			static_cast<TUint32>(reinterpret_cast<TUint>(this)));
		}
'''

CLI_DTOR_ANCHOR = r'''CWsClientWindow::~CWsClientWindow()
	{
'''

CLI_DTOR_NEW = r'''CWsClientWindow::~CWsClientWindow()
	{
	if (gHtcleoPublishedGridWindow==this)
		gHtcleoPublishedGridWindow=NULL;
'''

ROOT_DECL_ANCHOR = (
    "static TInt gHtcleoPublishedGridFallbackTraceCount = 0;\n"
)
ROOT_DECL_NEW = (
    ROOT_DECL_ANCHOR
    + "extern CWsClientWindow* gHtcleoPublishedGridWindow;\n"
)

ROOT_LOOKUP_OLD = r'''		CWsWindow *htcleoPublishedGrid=htcleoPublishedWindow ?
			static_cast<CWsWindow *>(htcleoPublishedWindow) : NULL;
'''

ROOT_LOOKUP_NEW = r'''		CWsWindow *htcleoTreeGrid=htcleoPublishedWindow ?
			static_cast<CWsWindow *>(htcleoPublishedWindow) : NULL;
		CWsClientWindow *htcleoCapturedGrid=gHtcleoPublishedGridWindow;
		CWsWindow *htcleoPublishedGrid=htcleoTreeGrid;
		if (!htcleoPublishedGrid && htcleoCapturedGrid &&
				htcleoCapturedGrid->ClientHandle()==
					static_cast<TUint32>(htcleoGridHandle))
			htcleoPublishedGrid=htcleoCapturedGrid;
'''

ROOT_LOG_ANCHOR = r'''			HtcleoWsLog(0x00000469u,
				htcleoPublishedGrid ?
					static_cast<TInt>(htcleoPublishedGrid->ClientHandle()) : 0,
				(static_cast<TUint32>(aInPos.iX & 0xffff) << 16) |
				static_cast<TUint32>(aInPos.iY & 0xffff));
'''

ROOT_LOG_NEW = ROOT_LOG_ANCHOR + r'''			HtcleoWsLog(0x0000046Bu,
				htcleoTreeGrid ? 1 : (htcleoPublishedGrid ? 2 : 0),
				htcleoPublishedGrid ?
					static_cast<TUint32>(htcleoPublishedGrid->ClientHandle()) : 0u);
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def install(cliwin: str, rootwin: str) -> tuple[str, str]:
    if MARKER in cliwin:
        return cliwin, rootwin
    if "#include <e32property.h>" not in cliwin.split("#ifdef", 1)[0]:
        cliwin = replace_once(
            cliwin, CLI_INCLUDE_ANCHOR, CLI_INCLUDE_NEW,
            "client unconditional property include",
        )
    cliwin = replace_once(cliwin, CLI_DECL_ANCHOR, CLI_DECL_NEW,
                          "client captured pointer declaration")
    cliwin = replace_once(cliwin, CLI_CAPTURE_ANCHOR, CLI_CAPTURE_NEW,
                          "client published handle capture")
    cliwin = replace_once(cliwin, CLI_DTOR_ANCHOR, CLI_DTOR_NEW,
                          "client captured pointer teardown")
    rootwin = replace_once(rootwin, ROOT_DECL_ANCHOR, ROOT_DECL_NEW,
                           "root captured pointer declaration")
    rootwin = replace_once(rootwin, ROOT_LOOKUP_OLD, ROOT_LOOKUP_NEW,
                           "root tree-to-captured lookup")
    rootwin = replace_once(rootwin, ROOT_LOG_ANCHOR, ROOT_LOG_NEW,
                           "root lookup source trace")
    rootwin = replace_once(
        rootwin,
        "gHtcleoPublishedGridFallbackTraceCount < 16",
        "gHtcleoPublishedGridFallbackTraceCount < 8",
        "root published trace bound",
    )
    return cliwin, rootwin


def verify(cliwin: str, rootwin: str) -> None:
    checks = {
        "marker": cliwin.count(MARKER) == 1,
        "single captured pointer": (
            cliwin.count("CWsClientWindow* gHtcleoPublishedGridWindow") == 1
            and rootwin.count("extern CWsClientWindow* gHtcleoPublishedGridWindow") == 1
        ),
        "real capture identity": (
            cliwin.count("WsOwner()->SecureId().iId==0x101F4CD2u") == 1
            and cliwin.count("htcleoPublishedHandle==static_cast<TInt>(iClientHandle)") == 1
            and cliwin.count("gHtcleoPublishedGridWindow=this") == 1
        ),
        "lifetime clear": (
            cliwin.count("gHtcleoPublishedGridWindow = NULL") == 1
            and cliwin.count("gHtcleoPublishedGridWindow=NULL") == 1
        ),
        "root handle match": (
            rootwin.count("htcleoCapturedGrid->ClientHandle()==") == 1
            and rootwin.count("htcleoPublishedGrid=htcleoCapturedGrid") == 1
        ),
        "visibility retained": (
            rootwin.count("htcleoPublishedGrid->IsVisible()") == 1
        ),
        "bounded source trace": (
            rootwin.count("gHtcleoPublishedGridFallbackTraceCount < 8") == 1
            and rootwin.count("0x0000046Bu") == 1
            and cliwin.count("0x0000046Au") == 1
        ),
        "no hard-coded object": "00A58400" not in CLI_CAPTURE_NEW + ROOT_LOOKUP_NEW,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("published-grid pointer capture verification failed: "
                         + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    server = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    cliwin_path = server / "openwfc/cliwin.cpp"
    rootwin_path = server / "ROOTWIN.CPP"
    cliwin = cliwin_path.read_text(encoding="utf-8")
    rootwin = rootwin_path.read_text(encoding="utf-8")
    cliwin, rootwin = install(cliwin, rootwin)
    verify(cliwin, rootwin)
    cliwin_path.write_text(cliwin, encoding="utf-8")
    rootwin_path.write_text(rootwin, encoding="utf-8")
    print(
        "HTCLEO_WSERV_PUBLISHED_GRID_POINTER_CAPTURE="
        "real-construct-pointer-handle-match-visible-lifetime-cleared-046a-046b"
    )


if __name__ == "__main__":
    main()
