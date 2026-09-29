#!/usr/bin/env python3
"""Trace the Post-Coe Avkon layout path and reuse HTCLEO's fixed panel size.

Iteration 478 proves that CCoeAppUi::ConstructL() returns (EIKBASE B60A) but
the virtual KEikPostCoeAppUiConstructL callback does not return (no B60B).
Iteration 479 then reaches C51C but not C51D, isolating the next block to
CAknAppUiBase::IsForeground(), whose ThreadIsForeground() implementation does
two synchronous Window Server focus queries.  Iteration 480 proves that
EikSrv-only foreground deferral returns through C51D and reaches C529, but the
synchronous SetSgcParams() IPC never reaches C52A.  This transform adds dense
EikSrv-only AKNBASE checkpoints, reuses the proven 480x800 panel, defers only
those two EikSrv startup calls, and preserves the stock queries, SetSgcParams
IPC and leave policy for every other Avkon process.
"""

from __future__ import annotations

import argparse
from pathlib import Path


POSTCOE_MARKER = "HTCLEO_AKNAPPUI_POSTCOE_LAYOUT_DURABLE_LOG_V1"
FIXED_SIZE_MARKER = "HTCLEO_AKNAPPUI_POSTCOE_FIXED_SCREEN_SIZE_COMPAT_V1"
SGC_MARKER = "HTCLEO_AKNSGC_HANDLECHANGE_DURABLE_LOG_V1"
FOREGROUND_MARKER = "HTCLEO_AKNSGC_EIKSRV_FOREGROUND_QUERY_COMPAT_V1"
SGC_PARAMS_MARKER = "HTCLEO_AKNSGC_EIKSRV_SETSGCPARAMS_COMPAT_V1"
MATRIXMENU_POSTCOE_FIXED_MARKER = (
    "HTCLEO_AKNAPPUI_MATRIXMENU_POSTCOE_FIXED_SCREEN_V1"
)
LOGGER = "HtcleoAknAppUiBaseLog"
MACRO = "__HTCLEO_AKNAPPUI_BASECONSTRUCT_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_section(
    text: str, start: str, end: str, replacement: str, label: str
) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(
            f"{label}: expected unique bounds, found "
            f"start={text.count(start)} end={text.count(end)}"
        )
    begin = text.index(start)
    finish = text.index(end, begin)
    return text[:begin] + replacement + text[finish:]


POSTCOE_BLOCK = r'''    else if ( aType == KEikPostCoeAppUiConstructL  )
        {
        // HTCLEO_AKNAPPUI_POSTCOE_LAYOUT_DURABLE_LOG_V1
        HtcleoAknAppUiBaseLog(0x0000B530u, KErrNone, (TUint32)aType);
        HtcleoAknAppUiBaseLog(0x0000B531u, KErrNone, 0u);
        ApplyLayoutChangeL(EFalse);
        HtcleoAknAppUiBaseLog(0x0000B532u, KErrNone, 0u);

        // HTCLEO_AKNAPPUI_POSTCOE_FIXED_SCREEN_SIZE_COMPAT_V1
        const TBool htcleoPostCoeFixedScreen =
            RProcess().SecureId().iId == 0x10003A4A;
        HtcleoAknAppUiBaseLog(0x0000B533u,
            htcleoPostCoeFixedScreen ? KErrNotSupported : KErrNone,
            0x46495832u);
        if (htcleoPostCoeFixedScreen)
            {
            iAppUiBaseExtension->iApplicationRect = TSize(480, 800);
            }
        else
            {
            iAppUiBaseExtension->iApplicationRect =
                iCoeEnv->ScreenDevice()->SizeInPixels();
            }
        HtcleoAknAppUiBaseLog(0x0000B534u,
            iAppUiBaseExtension->iApplicationRect.Width(),
            (TUint32)iAppUiBaseExtension->iApplicationRect.Height());
        HtcleoAknAppUiBaseLog(0x0000B535u, KErrNone, 0u);
        }
'''


APPLY_LAYOUT = r'''EXPORT_C void CAknAppUiBase::ApplyLayoutChangeL(TBool aReportChange)
    {
    HtcleoAknAppUiBaseLog(0x0000B540u, KErrNone, aReportChange);
    HtcleoAknAppUiBaseLog(0x0000B541u, KErrNone, 0u);
    CAknSgcClient::HandleChangeL();
    HtcleoAknAppUiBaseLog(0x0000B542u, KErrNone, 0u);

    HtcleoAknAppUiBaseLog(0x0000B543u, KErrNone, 0u);
    const TBool htcleoLayoutLoaded = iAvkonEnv->LoadAknLayoutL();
    HtcleoAknAppUiBaseLog(0x0000B544u, KErrNone, htcleoLayoutLoaded);
    if (htcleoLayoutLoaded)
        {
        if(aReportChange)
            {
            HtcleoAknAppUiBaseLog(0x0000B545u, KErrNone, 0u);
            ReportResourceChangedToAppL(KEikDynamicLayoutVariantSwitch);
            HtcleoAknAppUiBaseLog(0x0000B546u, KErrNone, 0u);
            }
        }
    HtcleoAknAppUiBaseLog(0x0000B547u, KErrNone, 0u);
    }

'''


SGC_DECLARATION = r'''

#ifdef __HTCLEO_AKNAPPUI_BASECONSTRUCT_LOG__
// HTCLEO_AKNSGC_HANDLECHANGE_DURABLE_LOG_V1
extern void HtcleoAknAppUiBaseLog(
    TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
inline void HtcleoAknAppUiBaseLog(TUint32, TInt, TUint32) {}
#endif
'''


SGC_FUNCTIONS = r'''EXPORT_C void CAknSgcClient::HandleChangeL()
	{
	HtcleoAknAppUiBaseLog(0x0000C500u, KErrNone, 0u);
	CAknSgcClient* self = Static();
	HtcleoAknAppUiBaseLog(0x0000C501u, KErrNone, self != NULL);
	if (self)
		{
		HtcleoAknAppUiBaseLog(0x0000C502u, KErrNone, 0u);
		self->DoHandleChangeL();
		HtcleoAknAppUiBaseLog(0x0000C503u, KErrNone, 0u);
		}
	HtcleoAknAppUiBaseLog(0x0000C504u, KErrNone, 0u);
	}

void CAknSgcClient::DoHandleChangeL()
	{
	HtcleoAknAppUiBaseLog(0x0000C510u, KErrNone, 0u);
	const TBool htcleoInAknSrv = iFlags[EInAknSrv];
	HtcleoAknAppUiBaseLog(0x0000C511u,
		htcleoInAknSrv ? KErrNotSupported : KErrNone, htcleoInAknSrv);
	if (htcleoInAknSrv)
		{
		return;
		}

	CAknAppUi* topAppUi = iAvkonAppUi;
	HtcleoAknAppUiBaseLog(0x0000C512u, KErrNone, topAppUi != NULL);

	HtcleoAknAppUiBaseLog(0x0000C513u,
		topAppUi ? KErrNone : KErrNotFound, topAppUi != NULL);
	if (!topAppUi)
		{
		return;
		}

	const TBool htcleoAlreadyHandlingChange = iFlags[EHandlingChange];
	HtcleoAknAppUiBaseLog(0x0000C514u,
		htcleoAlreadyHandlingChange ? KErrInUse : KErrNone,
		htcleoAlreadyHandlingChange);
	if (htcleoAlreadyHandlingChange)
		{
		return;
		}
	iFlags.Set(EHandlingChange);
	CleanupStack::PushL(TCleanupItem(ClearHandlingChangeFlag, this));
	HtcleoAknAppUiBaseLog(0x0000C515u, KErrNone, 0u);

	TInt spLayout = 0;
	TInt spFlags = 0;
	TBitFlags appFlags;
	TInt screenMode = KAknScreenModeUnset;
	HtcleoAknAppUiBaseLog(0x0000C516u, KErrNone, 0u);
	SetLegacyOrientationAndScreenModeAppUiFlags(appFlags, screenMode, topAppUi);
	HtcleoAknAppUiBaseLog(0x0000C517u, screenMode, 0u);
	HtcleoAknAppUiBaseLog(0x0000C518u, KErrNone, 0u);
	appFlags.Assign(EFullScreen, topAppUi->IsFullScreenApp());
	HtcleoAknAppUiBaseLog(0x0000C519u, KErrNone, appFlags[EFullScreen]);
	HtcleoAknAppUiBaseLog(0x0000C51Au, KErrNone, 0u);
	TBool partialFg = topAppUi->IsPartialForeground();
	HtcleoAknAppUiBaseLog(0x0000C51Bu, KErrNone, partialFg);
	// HTCLEO_AKNSGC_EIKSRV_FOREGROUND_QUERY_COMPAT_V1
	const TBool htcleoDeferForegroundQuery =
		RProcess().SecureId().iId == 0x10003A4A;
	HtcleoAknAppUiBaseLog(0x0000C51Cu,
		htcleoDeferForegroundQuery ? KErrNotSupported : KErrNone,
		0x46475244u);
	TBool foreground = EFalse;
	if (!htcleoDeferForegroundQuery)
		{
		foreground = topAppUi->IsForeground();
		}
	HtcleoAknAppUiBaseLog(0x0000C51Du, KErrNone, foreground);
	HtcleoAknAppUiBaseLog(0x0000C51Eu, KErrNone, partialFg);
	HtcleoAknAppUiBaseLog(0x0000C51Fu, KErrNone, foreground);

	// Loop over app UIs from most embedded to base app.
	for (CAknAppUiBase* appUi = static_cast<CAknAppUiBase*>(topAppUi);
		appUi;
		appUi = static_cast<CAknAppUiBase*>(appUi->ContainerAppUi()))
		{
		HtcleoAknAppUiBaseLog(0x0000C520u, KErrNone, appUi != NULL);
		HtcleoAknAppUiBaseLog(0x0000C521u, KErrNone, 0u);
		CEikStatusPane* sp = StatusPane(appUi);
		HtcleoAknAppUiBaseLog(0x0000C522u, KErrNone, sp != NULL);
		if (sp && !spLayout)
			{
			HtcleoAknAppUiBaseLog(0x0000C523u, KErrNone, 0u);
			spLayout = sp->CurrentLayoutResId();
			HtcleoAknAppUiBaseLog(0x0000C524u, spLayout, 0u);
			spFlags = sp->Flags();
			HtcleoAknAppUiBaseLog(0x0000C525u, spFlags, 0u);
			}

		if (appUi != topAppUi)
			{
			HtcleoAknAppUiBaseLog(0x0000C526u, KErrNone, 0u);
			SetLegacyOrientationAndScreenModeAppUiFlags(
				appFlags, screenMode, appUi);

			partialFg = (foreground || partialFg) && !appFlags[EFullScreen];
			foreground = EFalse;
			appFlags.Assign(
				EFullScreen, appFlags[EFullScreen] || appUi->IsFullScreenApp());

			SetAppUiForegroundL(appUi, foreground);
			SetAppUiPartialFgL(appUi, partialFg);
			HtcleoAknAppUiBaseLog(0x0000C527u, KErrNone, screenMode);
			}
		}

	const TBool htcleoSgcParamsChanged =
		spLayout != iSpLayout ||
		!(appFlags == iAppFlags) ||
		spFlags != iSpFlags ||
		screenMode != iAppScreenMode;
	HtcleoAknAppUiBaseLog(
		0x0000C528u, KErrNone, htcleoSgcParamsChanged);
	if (htcleoSgcParamsChanged)
		{
		iSpLayout = spLayout;
		iSpFlags = spFlags;
		iAppFlags = appFlags;
		iAppScreenMode = screenMode;
		HtcleoAknAppUiBaseLog(0x0000C529u, KErrNone, screenMode);
		// HTCLEO_AKNSGC_EIKSRV_SETSGCPARAMS_COMPAT_V1
		const TBool htcleoDeferSgcParams =
			RProcess().SecureId().iId == 0x10003A4A;
		TInt htcleoSgcSetResult = KErrNotSupported;
		if (!htcleoDeferSgcParams)
			{
			htcleoSgcSetResult = iAknSrv.SetSgcParams(
				iEikonEnv->RootWin().Identifier(), appFlags,
				spLayout, spFlags, screenMode);
			}
		HtcleoAknAppUiBaseLog(
			0x0000C52Au, htcleoSgcSetResult,
			htcleoDeferSgcParams ? 0x53474350u : (TUint32)spLayout);
		if (!htcleoDeferSgcParams)
			{
			User::LeaveIfError(htcleoSgcSetResult);
			}
		}

	HtcleoAknAppUiBaseLog(0x0000C52Bu, KErrNone, 0u);
	CleanupStack::PopAndDestroy();
	HtcleoAknAppUiBaseLog(0x0000C52Cu, KErrNone, 0u);
	}

'''


def install(aknappui: str, aknsgcc: str) -> tuple[str, str]:
    aknappui = replace_once(
        aknappui,
        "static void HtcleoAknAppUiBaseLog(",
        "void HtcleoAknAppUiBaseLog(",
        "cross-object durable logger linkage",
    )
    aknappui = replace_section(
        aknappui,
        "    else if ( aType == KEikPostCoeAppUiConstructL  )\n",
        "    else if ( aType == KAknShutOrHideApp )\n",
        POSTCOE_BLOCK,
        "Post-Coe callback",
    )
    aknappui = replace_section(
        aknappui,
        "EXPORT_C void CAknAppUiBase::ApplyLayoutChangeL(TBool aReportChange)\n",
        "TBool CAknAppUiBase::HasFullOrPartialForeground() const\n",
        APPLY_LAYOUT,
        "ApplyLayoutChangeL",
    )

    aknsgcc = replace_once(
        aknsgcc,
        '#include "AknPanic.h"\n',
        '#include "AknPanic.h"\n' + SGC_DECLARATION,
        "SGC logger declaration",
    )
    aknsgcc = replace_section(
        aknsgcc,
        "EXPORT_C void CAknSgcClient::HandleChangeL()\n",
        "CAknSgcClient::CAknSgcClient()\n",
        SGC_FUNCTIONS,
        "SGC HandleChange functions",
    )
    return aknappui, aknsgcc


def install_foreground_compat(aknsgcc: str) -> str:
    old = r'''	HtcleoAknAppUiBaseLog(0x0000C51Cu, KErrNone, 0u);
	TBool foreground = topAppUi->IsForeground();
	HtcleoAknAppUiBaseLog(0x0000C51Du, KErrNone, foreground);
'''
    new = r'''	// HTCLEO_AKNSGC_EIKSRV_FOREGROUND_QUERY_COMPAT_V1
	const TBool htcleoDeferForegroundQuery =
		RProcess().SecureId().iId == 0x10003A4A;
	HtcleoAknAppUiBaseLog(0x0000C51Cu,
		htcleoDeferForegroundQuery ? KErrNotSupported : KErrNone,
		0x46475244u);
	TBool foreground = EFalse;
	if (!htcleoDeferForegroundQuery)
		{
		foreground = topAppUi->IsForeground();
		}
	HtcleoAknAppUiBaseLog(0x0000C51Du, KErrNone, foreground);
'''
    return replace_once(
        aknsgcc,
        old,
        new,
        "EikSrv startup foreground-query compatibility",
    )


def install_sgc_params_compat(aknsgcc: str) -> str:
    old = r'''		HtcleoAknAppUiBaseLog(0x0000C529u, KErrNone, screenMode);
		const TInt htcleoSgcSetResult = iAknSrv.SetSgcParams(
			iEikonEnv->RootWin().Identifier(), appFlags,
			spLayout, spFlags, screenMode);
		HtcleoAknAppUiBaseLog(
			0x0000C52Au, htcleoSgcSetResult, (TUint32)spLayout);
		User::LeaveIfError(htcleoSgcSetResult);
'''
    new = r'''		HtcleoAknAppUiBaseLog(0x0000C529u, KErrNone, screenMode);
		// HTCLEO_AKNSGC_EIKSRV_SETSGCPARAMS_COMPAT_V1
		const TBool htcleoDeferSgcParams =
			RProcess().SecureId().iId == 0x10003A4A;
		TInt htcleoSgcSetResult = KErrNotSupported;
		if (!htcleoDeferSgcParams)
			{
			htcleoSgcSetResult = iAknSrv.SetSgcParams(
				iEikonEnv->RootWin().Identifier(), appFlags,
				spLayout, spFlags, screenMode);
			}
		HtcleoAknAppUiBaseLog(
			0x0000C52Au, htcleoSgcSetResult,
			htcleoDeferSgcParams ? 0x53474350u : (TUint32)spLayout);
		if (!htcleoDeferSgcParams)
			{
			User::LeaveIfError(htcleoSgcSetResult);
			}
'''
    return replace_once(
        aknsgcc,
        old,
        new,
        "EikSrv startup SetSgcParams compatibility",
    )


def verify(aknappui: str, aknsgcc: str, mmp: str) -> None:
    app_stages = list(range(0xB530, 0xB536)) + list(range(0xB540, 0xB548))
    sgc_stages = list(range(0xC500, 0xC505)) + list(range(0xC510, 0xC52D))
    matrixmenu_postcoe_fixed = MATRIXMENU_POSTCOE_FIXED_MARKER in aknappui
    homescreen_postcoe_trace = (
        "HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE_V1" in aknappui
    )
    checks = {
        "Post-Coe marker": aknappui.count(POSTCOE_MARKER) == 1,
        "fixed-screen marker": aknappui.count(FIXED_SIZE_MARKER) == 1,
        "SGC marker": aknsgcc.count(SGC_MARKER) == 1,
        "foreground-query compatibility marker": (
            aknsgcc.count(FOREGROUND_MARKER) == 1
        ),
        "SetSgcParams compatibility marker": (
            aknsgcc.count(SGC_PARAMS_MARKER) == 1
        ),
        "cross-object logger definition": aknappui.count(
            "void HtcleoAknAppUiBaseLog("
        ) == 2
        and "static void HtcleoAknAppUiBaseLog(" not in aknappui,
        "cross-object logger declaration": aknsgcc.count(
            "extern void HtcleoAknAppUiBaseLog("
        ) == 1,
        "all Post-Coe stages": all(
            aknappui.count(f"0x0000{stage:04X}u")
            == (
                2
                if homescreen_postcoe_trace
                and stage in (0xB530, 0xB547)
                else 1
            )
            for stage in app_stages
        ),
        "all SGC stages": all(
            aknsgcc.count(f"0x0000{stage:04X}u") == 1
            for stage in sgc_stages
        ),
        "EikSrv-only fixed panel": aknappui.count(
            "const TBool htcleoPostCoeFixedScreen ="
        ) == 1
        and aknappui.count("0x46495832u") == 1
        and aknappui.count("TSize(480, 800)") == 2,
        "non-EikSrv stock query retained": (
            (
                aknappui.count(
                    "iCoeEnv->ScreenDevice()->SizeInPixels();"
                ) >= 1
                if matrixmenu_postcoe_fixed
                else POSTCOE_BLOCK in aknappui
                and POSTCOE_BLOCK.count(
                    "iCoeEnv->ScreenDevice()->SizeInPixels();"
                ) == 1
            )
        ),
        "stock SGC calls retained": aknappui.count(
            "CAknSgcClient::HandleChangeL();"
        ) >= 4
        and aknsgcc.count("iAknSrv.SetSgcParams(") == 1,
        "stock layout load retained": aknappui.count(
            "iAvkonEnv->LoadAknLayoutL();"
        ) == 1,
        "EikSrv-only foreground-query deferral": (
            aknsgcc.count(
                "const TBool htcleoDeferForegroundQuery ="
            ) == 1
            and aknsgcc.count("0x46475244u") == 1
            and aknsgcc.count("foreground = topAppUi->IsForeground();") == 1
        ),
        "EikSrv-only SetSgcParams deferral": (
            aknsgcc.count("const TBool htcleoDeferSgcParams =") == 1
            and aknsgcc.count("if (!htcleoDeferSgcParams)") == 2
            and aknsgcc.count("0x53474350u") == 1
            and aknsgcc.count("iAknSrv.SetSgcParams(") == 1
            and aknsgcc.count(
                "User::LeaveIfError(htcleoSgcSetResult);"
            ) == 1
        ),
        "macro retained": mmp.count(f"MACRO          {MACRO}") == 1,
        "no wait or display probe": all(
            token not in (POSTCOE_BLOCK + APPLY_LAYOUT + SGC_FUNCTIONS)
            for token in ("User::After", "User::WaitForRequest", "HalFunction", "e7f000f0")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Akn Post-Coe layout durable-log verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()

    avkon = args.epocroot / "sf/mw/classicui/uifw/AvKon"
    aknappui_path = avkon / "src/AknAppUi.cpp"
    aknsgcc_path = avkon / "src/aknsgcc.cpp"
    mmp_path = args.epocroot / "sf/incubator/stemkit/breakdeps/avkon.mmp"

    aknappui = aknappui_path.read_text(encoding="latin-1")
    aknsgcc = aknsgcc_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    if POSTCOE_MARKER not in aknappui or SGC_MARKER not in aknsgcc:
        if POSTCOE_MARKER in aknappui or SGC_MARKER in aknsgcc:
            raise SystemExit("partial Akn Post-Coe transform state")
        aknappui, aknsgcc = install(aknappui, aknsgcc)

    if FOREGROUND_MARKER not in aknsgcc:
        aknsgcc = install_foreground_compat(aknsgcc)

    if SGC_PARAMS_MARKER not in aknsgcc:
        aknsgcc = install_sgc_params_compat(aknsgcc)

    verify(aknappui, aknsgcc, mmp)
    for path, transformed in (
        (aknappui_path, aknappui),
        (aknsgcc_path, aknsgcc),
    ):
        original = path.read_text(encoding="latin-1")
        if transformed != original:
            path.write_text(transformed, encoding="latin-1")

    print(
        "HTCLEO_AKNAPPUI_POSTCOE_LAYOUT_DURABLE_LOG=installed "
        "stages=B530-B547,C500-C52C "
        "screen-size=eiksrv-fixed-480x800-ui-first "
        "foreground=eiksrv-deferred-false-ui-first "
        "sgc-params=eiksrv-deferred-ui-first"
    )


if __name__ == "__main__":
    main()
