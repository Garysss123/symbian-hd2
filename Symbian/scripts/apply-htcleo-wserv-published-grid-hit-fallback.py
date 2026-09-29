#!/usr/bin/env python3
"""Route root-only pointer hits to the real published MatrixMenu grid window."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_PUBLISHED_GRID_HIT_FALLBACK_V1"

INCLUDE_ANCHOR = "#include <e32std.h>\n"
INCLUDE_NEW = INCLUDE_ANCHOR + "#include <e32property.h>\n"

INSERT_ANCHOR = r'''	if (aOutPos!=NULL)
'''

FALLBACK = r'''	/* HTCLEO_WSERV_PUBLISHED_GRID_HIT_FALLBACK_V1
	 * MatrixMenu publishes its real RWindow handle after WServ construction.
	 * If both stock BaseArea and the real-tree AbsRect fallback still return
	 * the root, resolve that existing handle from the actual window tree.
	 */
	if (winItIsIn==this && aGrabWin==NULL)
		{
		TInt htcleoGridHandle=0;
		const TInt htcleoPropertyResult=RProperty::Get(
			TUid::Uid(0x101F4CD2), 0x7F4D5701u, htcleoGridHandle);
		MWsWindow *htcleoPublishedWindow=NULL;
		if (htcleoPropertyResult==KErrNone && htcleoGridHandle!=0)
			htcleoPublishedWindow=FindChildByHandle(
				static_cast<TUint32>(htcleoGridHandle));
		CWsWindow *htcleoPublishedGrid=htcleoPublishedWindow ?
			static_cast<CWsWindow *>(htcleoPublishedWindow) : NULL;
		if (gHtcleoPublishedGridFallbackTraceCount < 16)
			{
			HtcleoWsLog(0x00000468u, htcleoPropertyResult,
				static_cast<TUint32>(htcleoGridHandle));
			HtcleoWsLog(0x00000469u,
				htcleoPublishedGrid ?
					static_cast<TInt>(htcleoPublishedGrid->ClientHandle()) : 0,
				(static_cast<TUint32>(aInPos.iX & 0xffff) << 16) |
				static_cast<TUint32>(aInPos.iY & 0xffff));
			++gHtcleoPublishedGridFallbackTraceCount;
			}
		if (htcleoPublishedGrid && htcleoPublishedGrid->IsVisible())
			{
			winItIsIn=htcleoPublishedGrid;
			aOriginalWinItIsIn=htcleoPublishedGrid;
			}
		}
	if (aOutPos!=NULL)
'''

DECL_ANCHOR = "static TInt gHtcleoAbsRectPointerFallbackTraceCount = 0;\n"
DECL_NEW = (
    DECL_ANCHOR
    + "static TInt gHtcleoPublishedGridFallbackTraceCount = 0;\n"
)

WALKER_OLD = (
    "\tTWalkWindowTreeFindByHandle(TUint32 aHandle) : iHandle(aHandle) { }\n"
)
WALKER_NEW = (
    "\tTWalkWindowTreeFindByHandle(TUint32 aHandle) : "
    "iHandle(aHandle), iFound(NULL) { }\n"
)


def install(rootwin: str, walker: str) -> tuple[str, str]:
    if MARKER in rootwin:
        return rootwin, walker
    if "HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK_V1" not in rootwin:
        raise SystemExit("published-grid fallback requires AbsRect fallback first")
    if "#include <e32property.h>" not in rootwin:
        if rootwin.count(INCLUDE_ANCHOR) != 1:
            raise SystemExit("published-grid property include anchor mismatch")
        rootwin = rootwin.replace(INCLUDE_ANCHOR, INCLUDE_NEW, 1)
    if rootwin.count(DECL_ANCHOR) != 1:
        raise SystemExit("published-grid trace declaration anchor mismatch")
    if rootwin.count(INSERT_ANCHOR) != 1:
        raise SystemExit("published-grid insertion anchor mismatch")
    if walker.count(WALKER_OLD) == 1:
        walker = walker.replace(WALKER_OLD, WALKER_NEW, 1)
    elif walker.count(WALKER_NEW) != 1:
        raise SystemExit("window-tree handle walker initializer mismatch")
    rootwin = rootwin.replace(DECL_ANCHOR, DECL_NEW, 1)
    rootwin = rootwin.replace(INSERT_ANCHOR, FALLBACK, 1)
    return rootwin, walker


def verify(rootwin: str, walker: str) -> None:
    checks = {
        "marker": rootwin.count(MARKER) == 1,
        "property contract": (
            rootwin.count("TUid::Uid(0x101F4CD2)") == 1
            and rootwin.count("0x7F4D5701u") == 1
        ),
        "real tree lookup": rootwin.count("FindChildByHandle(") == 1,
        "safe walker": walker.count(WALKER_NEW) == 1,
        "visible real target": (
            rootwin.count("htcleoPublishedGrid->IsVisible()") == 1
            and rootwin.count("winItIsIn=htcleoPublishedGrid") == 1
            and rootwin.count("aOriginalWinItIsIn=htcleoPublishedGrid") == 1
        ),
        "root no-grab only": rootwin.count("winItIsIn==this && aGrabWin==NULL") == 2,
        "bounded stages": (
            (
                rootwin.count("gHtcleoPublishedGridFallbackTraceCount < 16") == 1
                or rootwin.count(
                    "gHtcleoPublishedGridFallbackTraceCount < 8"
                ) == 1
            )
            and rootwin.count("0x00000468u") == 1
            and rootwin.count("0x00000469u") == 1
        ),
        "no fabricated handle": "00A58400" not in FALLBACK,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("published-grid hit fallback verification failed: "
                         + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    server = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    rootwin_path = server / "ROOTWIN.CPP"
    walker_path = server / "openwfc/walkwindowtree.h"
    rootwin = rootwin_path.read_text(encoding="utf-8")
    walker = walker_path.read_text(encoding="utf-8")
    rootwin, walker = install(rootwin, walker)
    verify(rootwin, walker)
    rootwin_path.write_text(rootwin, encoding="utf-8")
    walker_path.write_text(walker, encoding="utf-8")
    print(
        "HTCLEO_WSERV_PUBLISHED_GRID_HIT_FALLBACK="
        "root-only-real-property-handle-tree-lookup-0468-0469"
    )


if __name__ == "__main__":
    main()
