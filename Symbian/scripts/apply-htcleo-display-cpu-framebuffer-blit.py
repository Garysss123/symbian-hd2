#!/usr/bin/env python3
"""Add an HTC Leo CPU RGB565 display fallback to the WServ display stage.

The full MatrixMenu draw chain completes, but the stock OpenWFC/SurfaceUpdate
path neither posts visible pixels nor completes the first frame on QSD8250.
Map the already rendered UI target, convert/copy it into the display driver's
legacy framebuffer, switch scanout through the standard WServ display HAL,
and complete the render status synchronously.  Other builds retain the stock
path.
"""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_MARKER = "HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_V1"
MMP_MARKER = "HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_BUILD_V1"
FRAME_LOOP_MARKER = "HTCLEO_DISPLAY_CPU_FRAME_LOOP_V1"


INCLUDE_ANCHOR = "#include <bitdev.h>\n"
INCLUDES = r'''#include <bitdev.h>
#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
#include <e32event_private.h>
#include <e32svr.h>
#include <u32hal.h>
#include <graphics/sgutils.h>
#endif
'''


LOGGER_ANCHOR = r'''#ifdef __HTCLEO_DISPLAY_DURABLE_LOG__
void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoDsprLog(TUint32, TInt, TUint32) {}
#endif
'''


HELPER = r'''#ifdef __HTCLEO_DISPLAY_DURABLE_LOG__
void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoDsprLog(TUint32, TInt, TUint32) {}
#endif

#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
// HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_V1
static TInt HtcleoCpuFramebufferBlit(CRenderTarget& aTarget, TInt aScreenNumber)
    {
    const TSize size = aTarget.SizeInPixels();
    const TUidPixelFormat sourceFormat = aTarget.PixelFormat();
    HtcleoDsprLog(0x00001900u, aScreenNumber, (TUint32)sourceFormat);
    HtcleoDsprLog(0x00001901u, KErrNone,
        ((TUint32)(size.iWidth & 0xFFFF) << 16)
        | (TUint32)(size.iHeight & 0xFFFF));
    if (aScreenNumber != 0 || size != TSize(480, 800))
        {
        return KErrNotSupported;
        }

    TAny* sourceAddress = NULL;
    TInt sourceStride = 0;
    TInt result = aTarget.MapReadWrite(sourceAddress, sourceStride);
    HtcleoDsprLog(0x00001902u, result, (TUint32)sourceStride);
    if (result != KErrNone)
        {
        return result;
        }

    TPckgBuf<TScreenInfoV01> screenInfoPackage;
    UserSvr::ScreenInfo(screenInfoPackage);
    const TScreenInfoV01& screenInfo = screenInfoPackage();
    HtcleoDsprLog(0x00001903u,
        screenInfo.iScreenAddressValid ? KErrNone : KErrNotReady,
        screenInfo.iScreenAddress ? 1u : 0u);

    if (!sourceAddress || sourceStride <= 0
            || !screenInfo.iScreenAddressValid
            || !screenInfo.iScreenAddress
            || screenInfo.iScreenSize != TSize(480, 800))
        {
        result = KErrNotReady;
        }
    else
        {
        const TRect fullScreen(TPoint(0, 0), size);
        result = SgUtils::TransferPixels(
            screenInfo.iScreenAddress,
            480 * 2,
            EUidPixelFormatRGB_565,
            sourceAddress,
            sourceStride,
            sourceFormat,
            fullScreen);
        }
    HtcleoDsprLog(0x00001904u, result, 480u * 800u * 2u);

    const TInt unmapResult = aTarget.Unmap();
    HtcleoDsprLog(0x00001905u, unmapResult, 0u);
    if (result == KErrNone && unmapResult != KErrNone)
        {
        result = unmapResult;
        }

    if (result == KErrNone)
        {
        result = UserSvr::HalFunction(
            EHalGroupDisplay | (aScreenNumber << 16),
            EDisplayHalWsSwitchOnScreen,
            NULL,
            NULL);
        HtcleoDsprLog(0x00001906u, result, 0u);
        HtcleoDsprLog(0x00001907u, result,
            result == KErrNone ? 1u : 0u);
        }
    HtcleoDsprLog(0x00001908u, result, 0u);
    return result;
    }
#endif
'''


BEGIN_ANCHOR = r'''void CDisplayRenderStage::Begin(const TRegion* aRegion)
	{
	STD_ASSERT_DEBUG(!aRegion || !aRegion->CheckError(), EPluginPanicRegionError);
	iUpdateRegion = aRegion;
	iOpenWfcWrapper->Begin(aRegion);
	}'''


BEGIN_REPLACEMENT = r'''void CDisplayRenderStage::Begin(const TRegion* aRegion)
	{
	STD_ASSERT_DEBUG(!aRegion || !aRegion->CheckError(), EPluginPanicRegionError);
	iUpdateRegion = aRegion;
#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
	// HTCLEO_DISPLAY_CPU_FRAME_LOOP_V1
	HtcleoDsprLog(0x00001910u, KErrNone,
		aRegion && !aRegion->IsEmpty() ? 1u : 0u);
#else
	iOpenWfcWrapper->Begin(aRegion);
#endif
	}'''


END_ANCHOR = r'''void CDisplayRenderStage::End(TRequestStatus* aFinished)
	{
#if 0'''


END_REPLACEMENT = r'''void CDisplayRenderStage::End(TRequestStatus* aFinished)
	{
#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
	const TBool htcleoUpdatePending =
		iUpdateRegion && !iUpdateRegion->IsEmpty();
	const TInt htcleoCpuBlitResult = htcleoUpdatePending
		? HtcleoCpuFramebufferBlit(*iRenderTarget, ScreenNumber())
		: KErrNone;
	HtcleoDsprLog(0x00001909u, htcleoCpuBlitResult,
		htcleoUpdatePending ? 1u : 0u);
	if (aFinished)
		{
		*aFinished = KRequestPending;
		User::RequestComplete(aFinished, KErrNone);
		}
	HtcleoDsprLog(0x00001911u, KErrNone,
		aFinished ? 1u : 0u);
	iOpenWfcWrapper->End();
	iUpdateRegion = NULL;
	DEBUGOSB
	return;
#endif
#if 0'''


OLD_CPU_END = r'''#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
	const TInt htcleoCpuBlitResult =
		HtcleoCpuFramebufferBlit(*iRenderTarget, ScreenNumber());
	HtcleoDsprLog(0x00001909u, htcleoCpuBlitResult,
		iUpdateRegion && !iUpdateRegion->IsEmpty() ? 1u : 0u);
	if (aFinished)
		{
		*aFinished = KRequestPending;
		User::RequestComplete(aFinished, KErrNone);
		}
	iOpenWfcWrapper->End();
	iUpdateRegion = NULL;'''


NEW_CPU_END = r'''#ifdef __HTCLEO_CPU_FRAMEBUFFER_BLIT__
	const TBool htcleoUpdatePending =
		iUpdateRegion && !iUpdateRegion->IsEmpty();
	const TInt htcleoCpuBlitResult = htcleoUpdatePending
		? HtcleoCpuFramebufferBlit(*iRenderTarget, ScreenNumber())
		: KErrNone;
	HtcleoDsprLog(0x00001909u, htcleoCpuBlitResult,
		htcleoUpdatePending ? 1u : 0u);
	if (aFinished)
		{
		*aFinished = KRequestPending;
		User::RequestComplete(aFinished, KErrNone);
		}
	HtcleoDsprLog(0x00001911u, KErrNone,
		aFinished ? 1u : 0u);
	iOpenWfcWrapper->End();
	iUpdateRegion = NULL;'''


CPU_END_RESET_ANCHOR = r'''	HtcleoDsprLog(0x00001911u, KErrNone,
		aFinished ? 1u : 0u);
	iUpdateRegion = NULL;
	DEBUGOSB
	return;
#endif'''


CPU_END_RESET_REPLACEMENT = r'''	HtcleoDsprLog(0x00001911u, KErrNone,
		aFinished ? 1u : 0u);
	iOpenWfcWrapper->End();
	iUpdateRegion = NULL;
	DEBUGOSB
	return;
#endif'''


MMP_ANCHOR = "macro __HTCLEO_DISPLAY_DURABLE_LOG__\n"
MMP_REPLACEMENT = r'''macro __HTCLEO_DISPLAY_DURABLE_LOG__
// HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT_BUILD_V1
macro __HTCLEO_CPU_FRAMEBUFFER_BLIT__
'''


OLD_DISPLAY_POST = r'''    if (result == KErrNone)
        {
        RDisplayChannel displayChannel;
        result = displayChannel.Open(aScreenNumber);
        HtcleoDsprLog(0x00001906u, result, 0u);
        if (result == KErrNone)
            {
            RDisplayChannel::TPostCount postCount = 0;
            result = displayChannel.PostLegacyBuffer(NULL, postCount);
            HtcleoDsprLog(0x00001907u, result, (TUint32)postCount);
            displayChannel.Close();
            }
        }'''


NEW_DISPLAY_POST = r'''    if (result == KErrNone)
        {
        result = UserSvr::HalFunction(
            EHalGroupDisplay | (aScreenNumber << 16),
            EDisplayHalWsSwitchOnScreen,
            NULL,
            NULL);
        HtcleoDsprLog(0x00001906u, result, 0u);
        HtcleoDsprLog(0x00001907u, result,
            result == KErrNone ? 1u : 0u);
        }'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str, mmp: str) -> tuple[str, str]:
    if SOURCE_MARKER not in source:
        source = replace_once(source, INCLUDE_ANCHOR, INCLUDES, "includes")
        source = replace_once(source, LOGGER_ANCHOR, HELPER, "helper")
        source = replace_once(source, BEGIN_ANCHOR, BEGIN_REPLACEMENT, "Begin")
        source = replace_once(source, END_ANCHOR, END_REPLACEMENT, "End")
    elif "#include <sgutils.h>" in source:
        source = replace_once(
            source,
            "#include <sgutils.h>",
            "#include <graphics/sgutils.h>",
            "exported sgutils include",
        )
    if FRAME_LOOP_MARKER not in source:
        source = replace_once(
            source,
            BEGIN_ANCHOR,
            BEGIN_REPLACEMENT,
            "CPU-only frame Begin",
        )
        source = replace_once(
            source,
            OLD_CPU_END,
            NEW_CPU_END,
            "CPU-only frame End",
        )
    if FRAME_LOOP_MARKER in source and source.count(
        "iOpenWfcWrapper->End();"
    ) == 1:
        source = replace_once(
            source,
            CPU_END_RESET_ANCHOR,
            CPU_END_RESET_REPLACEMENT,
            "CPU-only frame wrapper state reset",
        )
    if "RDisplayChannel displayChannel;" in source:
        source = replace_once(
            source,
            "#include <dispchannel.h>",
            "#include <u32hal.h>",
            "display HAL include",
        )
        source = replace_once(
            source,
            OLD_DISPLAY_POST,
            NEW_DISPLAY_POST,
            "WServ screen switch",
        )
    if MMP_MARKER not in mmp:
        mmp = replace_once(mmp, MMP_ANCHOR, MMP_REPLACEMENT, "mmp macro")
    return source, mmp


def verify(source: str, mmp: str) -> None:
    stages = range(0x1900, 0x190A)
    region_aware = "HTCLEO_DISPLAY_REGION_AWARE_BLIT_V1" in source
    scaled_blank_guard = any(
        marker in source
        for marker in (
            "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V2",
            "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V3",
        )
    )
    checks = {
        "single source marker": source.count(SOURCE_MARKER) == 1,
        "single build marker": mmp.count(MMP_MARKER) == 1,
        "single frame-loop marker": source.count(FRAME_LOOP_MARKER) == 1,
        "single macro": mmp.count("macro __HTCLEO_CPU_FRAMEBUFFER_BLIT__") == 1,
        "required headers": all(
            source.count(header) == 1
            for header in (
                "#include <e32event_private.h>",
                "#include <e32svr.h>",
                "#include <u32hal.h>",
                "#include <graphics/sgutils.h>",
            )
        ),
        "screen contract": (
            source.count("TSize(480, 800)")
            == (3 if scaled_blank_guard else 2)
            and source.count("EUidPixelFormatRGB_565")
            == (2 if region_aware else 1)
            and source.count("480 * 2")
            == (3 if region_aware else 1)
        ),
        "mapped transfer": (
            source.count("aTarget.MapReadWrite") == 1
            and source.count("SgUtils::TransferPixels")
            == (2 if region_aware else 1)
            and source.count("aTarget.Unmap()") == 1
        ),
        "legal framebuffer api": (
            source.count("UserSvr::ScreenInfo") == 1
            and source.count("UserSvr::HalFunction") == 1
            and source.count("EDisplayHalWsSwitchOnScreen") == 1
            and "RDisplayChannel displayChannel" not in source
            and "displayChannel.Open" not in source
            and "displayChannel.PostLegacyBuffer" not in source
        ),
        "status completion": (
            END_REPLACEMENT.count(
                "User::RequestComplete(aFinished, KErrNone)"
            ) == 1
            and END_REPLACEMENT.count("iOpenWfcWrapper->End();") == 1
            and source.count("iOpenWfcWrapper->End();") == 2
            and source.count("iOpenWfcWrapper->Begin(aRegion);") == 1
            and source.count("0x00001910u") == 1
            and source.count("0x00001911u") == 1
        ),
        "all stages": all(
            source.count(f"0x{stage:08X}u") == 1 for stage in stages
        ),
        "no raw hardware address": all(
            token not in source.lower()
            for token in ("0xc6400000", "0x03839000", "0xc6300000")
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
    source_path = component / "src/displayrenderstage.cpp"
    mmp_path = component / "group/stdplugin.mmp"
    source = source_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")
    source, mmp = install(source, mmp)
    verify(source, mmp)
    source_path.write_text(source, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print(
        "HTCLEO_DISPLAY_CPU_FRAMEBUFFER_BLIT="
        "cpu-frame-loop-rgb565-map-transfer-screeninfo-"
        "wsswitchon-1910-1911-1900-1909"
    )


if __name__ == "__main__":
    main()
