#!/usr/bin/env python3
"""Use real visible-window AbsRect hit testing only when stock WServ returns root."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK_V1"

DECL_ANCHOR = '#include "EVENT.H"\n'
DECLARATION = DECL_ANCHOR + r'''

extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
static TInt gHtcleoAbsRectPointerFallbackTraceCount = 0;
'''

INSERT_ANCHOR = r'''	if (aOutPos!=NULL)
'''

FALLBACK = r'''	/* HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK_V1
	 * The CPU-render compatibility path can leave BaseArea empty even though
	 * a real client window is visible and has a valid 480x800 AbsRect.  Keep
	 * stock region/capture hit testing first; only when it returns the root,
	 * repeat the same top-to-child walk using the real absolute rectangles.
	 */
	if (winItIsIn==this && aGrabWin==NULL)
		{
		const CWsWindow *htcleoFallback=this;
		const CWsWindowGroup *htcleoGroup;
		for (htcleoGroup=(aForceInGroup ? aForceInGroup : Child());
				htcleoGroup!=NULL; htcleoGroup=htcleoGroup->NextSibling())
			{
			CWsClientWindow *htcleoWin=htcleoGroup->Child();
			while (htcleoWin!=NULL)
				{
				if (htcleoWin->IsVisible() &&
						htcleoWin->AbsRect().Contains(aInPos))
					{
					htcleoFallback=htcleoWin;
					htcleoWin=htcleoWin->Child();
					}
				else
					htcleoWin=htcleoWin->NextSibling();
				}
			if (htcleoFallback!=this || aForceInGroup!=NULL)
				break;
			}
		if (htcleoFallback!=this)
			{
			winItIsIn=htcleoFallback;
			aOriginalWinItIsIn=htcleoFallback;
			if (gHtcleoAbsRectPointerFallbackTraceCount < 16)
				{
				HtcleoWsLog(0x00000466u,
					static_cast<TInt>(htcleoFallback->ClientHandle()),
					(static_cast<TUint32>(aInPos.iX & 0xffff) << 16) |
					static_cast<TUint32>(aInPos.iY & 0xffff));
				const TRect htcleoRect=htcleoFallback->AbsRect();
				HtcleoWsLog(0x00000467u, KErrNone,
					(static_cast<TUint32>(htcleoRect.Width() & 0xffff) << 16) |
					static_cast<TUint32>(htcleoRect.Height() & 0xffff));
				++gHtcleoAbsRectPointerFallbackTraceCount;
				}
			}
		}
	if (aOutPos!=NULL)
'''


def install(source: str) -> str:
    if MARKER in source:
        return source
    if source.count(DECL_ANCHOR) != 1:
        raise SystemExit("WServ root-window fallback declaration anchor mismatch")
    if source.count(INSERT_ANCHOR) != 1:
        raise SystemExit("WServ root-window fallback insertion anchor mismatch")
    source = source.replace(DECL_ANCHOR, DECLARATION, 1)
    source = source.replace(INSERT_ANCHOR, FALLBACK, 1)
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "stock BaseArea retained": source.count("baseArea->Contains(aInPos)") == 2,
        "root-only fallback": source.count("winItIsIn==this && aGrabWin==NULL") >= 1,
        "visible real tree": (
            source.count("htcleoWin->IsVisible()") == 1
            and source.count("htcleoWin->AbsRect().Contains(aInPos)") == 1
        ),
        "real selected window": (
            source.count("winItIsIn=htcleoFallback") == 1
            and source.count("aOriginalWinItIsIn=htcleoFallback") == 1
        ),
        "bounded stages": (
            source.count("gHtcleoAbsRectPointerFallbackTraceCount < 16") == 1
            and source.count("0x00000466u") == 1
            and source.count("0x00000467u") == 1
        ),
        "no hard-coded target": "00A58400" not in FALLBACK,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("WServ AbsRect pointer fallback verification failed: "
                         + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/os/graphics/windowing/windowserver/nga/SERVER/ROOTWIN.CPP"
    )
    source = source_path.read_text(encoding="utf-8")
    source = install(source)
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_WSERV_ABSRECT_POINTER_HIT_FALLBACK="
        "stock-basearea-root-only-visible-tree-absrect-0466-0467"
    )


if __name__ == "__main__":
    main()
