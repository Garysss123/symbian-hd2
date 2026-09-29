#!/usr/bin/env python3
"""Route HTC Leo WServ flicker-buffer frames directly to the CPU scanout.

The display-stage fallback can expose the legacy RGB565 framebuffer, but its
first invocation is ClearDisplay() and therefore contains only a white frame.
On HTC Leo, copy the completed CFbRenderStage target directly and complete the
upstream WServ scheduler request without entering the unavailable OpenWFC
handoff.  Other platforms retain the stock render-stage chain.
"""

from __future__ import annotations

import argparse
from pathlib import Path


EXPORT_MARKER = "HTCLEO_FLICKER_CPU_FRAMEBUFFER_EXPORT_V1"
SOURCE_MARKER = "HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT_V1"
STATE_MARKER = "HTCLEO_FLICKER_CPU_FRAMEBUFFER_STATE_V1"


DISPLAY_EXPORT_ANCHOR = (
    "static TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, "
    "TInt aScreenNumber)"
)
DISPLAY_EXPORT_REPLACEMENT = (
    "// HTCLEO_FLICKER_CPU_FRAMEBUFFER_EXPORT_V1\n"
    "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, "
    "TInt aScreenNumber)"
)


LOGGER_ANCHOR = r'''#ifdef __HTCLEO_DISPLAY_DURABLE_LOG__
void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoDsprLog(TUint32, TInt, TUint32) {}
#endif
'''


LOGGER_REPLACEMENT = r'''#ifdef __HTCLEO_DISPLAY_DURABLE_LOG__
void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoDsprLog(TUint32, TInt, TUint32) {}
#endif

#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, TInt aScreenNumber);
#endif
'''


END_ANCHOR = r'''void CFbRenderStage::End(TRequestStatus* aFinished)
	{
	STD_ASSERT_DEBUG(!iRequestPending || !aFinished, EPluginPanicMultipleUpdateRequests);'''


END_REPLACEMENT = r'''void CFbRenderStage::End(TRequestStatus* aFinished)
	{
#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
	// HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT_V1
	// HTCLEO_FLICKER_CPU_FRAMEBUFFER_STATE_V1
	iRequestPending = ETrue;
	iUpstreamRequestStatus = aFinished;
	if (iUpstreamRequestStatus)
		{
		*iUpstreamRequestStatus = KRequestPending;
		}
	const TBool htcleoUpdatePending =
		iUpdateRegion && !iUpdateRegion->IsEmpty()
		&& !iUpdateRegion->CheckError();
	HtcleoDsprLog(0x00001920u, KErrNone,
		(aFinished ? 1u : 0u) | (htcleoUpdatePending ? 2u : 0u));
	const TInt htcleoCpuBlitResult = htcleoUpdatePending
		? HtcleoCpuFramebufferBlit(
			*iRenderTarget, iNextScreenDevice->ScreenNumber())
		: KErrNone;
	HtcleoDsprLog(0x00001921u, htcleoCpuBlitResult,
		htcleoUpdatePending ? 1u : 0u);
	if (iUpstreamRequestStatus
		&& *iUpstreamRequestStatus == KRequestPending)
		{
		User::RequestComplete(iUpstreamRequestStatus, KErrNone);
		}
	iRequestPending = EFalse;
	iUpstreamRequestStatus = NULL;
	DEBUGOSB
	return;
#endif
	STD_ASSERT_DEBUG(!iRequestPending || !aFinished, EPluginPanicMultipleUpdateRequests);'''


OLD_END_REPLACEMENT = r'''void CFbRenderStage::End(TRequestStatus* aFinished)
	{
#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
	// HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT_V1
	const TBool htcleoUpdatePending =
		iUpdateRegion && !iUpdateRegion->IsEmpty()
		&& !iUpdateRegion->CheckError();
	HtcleoDsprLog(0x00001920u, KErrNone,
		(aFinished ? 1u : 0u) | (htcleoUpdatePending ? 2u : 0u));
	const TInt htcleoCpuBlitResult = htcleoUpdatePending
		? HtcleoCpuFramebufferBlit(
			*iRenderTarget, iNextScreenDevice->ScreenNumber())
		: KErrNone;
	HtcleoDsprLog(0x00001921u, htcleoCpuBlitResult,
		htcleoUpdatePending ? 1u : 0u);
	if (aFinished)
		{
		*aFinished = KRequestPending;
		User::RequestComplete(aFinished, KErrNone);
		}
	iRequestPending = EFalse;
	iUpstreamRequestStatus = NULL;
	DEBUGOSB
	return;
#endif
	STD_ASSERT_DEBUG(!iRequestPending || !aFinished, EPluginPanicMultipleUpdateRequests);'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(display: str, flicker: str) -> tuple[str, str]:
    if EXPORT_MARKER not in display:
        display = replace_once(
            display,
            DISPLAY_EXPORT_ANCHOR,
            DISPLAY_EXPORT_REPLACEMENT,
            "display CPU helper export",
        )
    if SOURCE_MARKER not in flicker:
        flicker = replace_once(
            flicker,
            LOGGER_ANCHOR,
            LOGGER_REPLACEMENT,
            "flicker CPU helper declaration",
        )
        flicker = replace_once(
            flicker,
            END_ANCHOR,
            END_REPLACEMENT,
            "flicker CPU End",
        )
    elif STATE_MARKER not in flicker:
        flicker = replace_once(
            flicker,
            OLD_END_REPLACEMENT,
            END_REPLACEMENT,
            "flicker CPU upstream state",
        )
    return display, flicker


def verify(display: str, flicker: str, mmp: str) -> None:
    checks = {
        "display fallback prerequisite": (
            display.count("HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_V1") == 1
            and mmp.count("macro __HTCLEO_CPU_FRAMEBUFFER_BLIT__") == 1
        ),
        "single helper export": (
            display.count(EXPORT_MARKER) == 1
            and display.count(
                "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget"
            ) == 1
            and "static TInt HtcleoCpuFramebufferBlit" not in display
        ),
        "single flicker route": (
            flicker.count(SOURCE_MARKER) == 1
            and flicker.count(STATE_MARKER) == 1
            and flicker.count(
                "TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget"
            ) == 1
            and flicker.count("0x00001920u") == 1
            and flicker.count("0x00001921u") == 1
        ),
        "real flicker target and upstream completion": (
            END_REPLACEMENT.count("*iRenderTarget") == 1
            and END_REPLACEMENT.count("iNextScreenDevice->ScreenNumber()") == 1
            and END_REPLACEMENT.count(
                "User::RequestComplete(iUpstreamRequestStatus, KErrNone)"
            ) == 1
            and END_REPLACEMENT.count("Next()->End") == 0
        ),
        "state reset": (
            END_REPLACEMENT.count("iRequestPending = ETrue") == 1
            and END_REPLACEMENT.count("iRequestPending = EFalse") == 1
            and END_REPLACEMENT.count(
                "iUpstreamRequestStatus = aFinished"
            ) == 1
            and END_REPLACEMENT.count("iUpstreamRequestStatus = NULL") == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/os/graphics/windowing/windowserverplugins/openwfc"
    display_path = component / "src/displayrenderstage.cpp"
    flicker_path = component / "src/fbrenderstage.cpp"
    mmp_path = component / "group/stdplugin.mmp"
    display = display_path.read_text(encoding="utf-8")
    flicker = flicker_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")
    display, flicker = install(display, flicker)
    verify(display, flicker, mmp)
    display_path.write_text(display, encoding="utf-8")
    flicker_path.write_text(flicker, encoding="utf-8")
    print(
        "HTCLEO_FLICKER_CPU_FRAMEBUFFER_BLIT="
        "wserv-flicker-target-direct-rgb565-1920-1921"
    )


if __name__ == "__main__":
    main()
