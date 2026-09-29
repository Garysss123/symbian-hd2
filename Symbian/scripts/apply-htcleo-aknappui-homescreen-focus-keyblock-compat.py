#!/usr/bin/env python3
"""Trace HomeScreen focus gain and avoid key-block IPC on a null AknSrv."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_KEYBLOCK_COMPAT_V1"
APPUI_PREREQUISITE = "HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1"
SGC_PREREQUISITE = "HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_appui(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    if text.count(APPUI_PREREQUISITE) != 1:
        raise SystemExit("AknAppUi HomeScreen logger prerequisite is missing")

    text = replace_once(
        text,
        f"// {APPUI_PREREQUISITE}\n",
        f"// {APPUI_PREREQUISITE}\n// {MARKER}\n",
        "AknAppUi marker",
    )
    text = replace_once(
        text,
        """EXPORT_C void CAknAppUi::HandleWsEventL(const TWsEvent& aEvent,CCoeControl* aDestination)
    {
    iAvkonEnv->TransitionEvent(KAknTransitionEventAvkon); 
""",
        """EXPORT_C void CAknAppUi::HandleWsEventL(const TWsEvent& aEvent,CCoeControl* aDestination)
    {
    const TBool htcleoHomeFocusTrace =
        (RProcess().SecureId().iId == 0x102750f0u);
    if (htcleoHomeFocusTrace)
        HtcleoAknAppUiBaseLog(0x0000C560u, aEvent.Type(),
            (TUint32)aDestination);
    if (htcleoHomeFocusTrace)
        HtcleoAknAppUiBaseLog(0x0000C561u, KErrNone,
            (TUint32)iAvkonEnv);
    iAvkonEnv->TransitionEvent(KAknTransitionEventAvkon);
    if (htcleoHomeFocusTrace)
        HtcleoAknAppUiBaseLog(0x0000C562u, KErrNone,
            (TUint32)iAvkonEnv);
""",
        "AknAppUi entry and first transition",
    )
    text = replace_once(
        text,
        """    if (EventMonitor() && EventMonitor()->IsEnabled())
        {
        EventMonitor()->HandleWsEventL(aEvent,aDestination);
        }
    
    TInt eventType = aEvent.Type();
""",
        """    if (htcleoHomeFocusTrace)
        HtcleoAknAppUiBaseLog(0x0000C563u, KErrNone,
            (TUint32)EventMonitor());
    if (EventMonitor() && EventMonitor()->IsEnabled())
        {
        if (htcleoHomeFocusTrace)
            HtcleoAknAppUiBaseLog(0x0000C564u, KErrNone, 0u);
        EventMonitor()->HandleWsEventL(aEvent,aDestination);
        if (htcleoHomeFocusTrace)
            HtcleoAknAppUiBaseLog(0x0000C565u, KErrNone, 0u);
        }
    
    TInt eventType = aEvent.Type();
""",
        "AknAppUi event monitor",
    )
    text = replace_once(
        text,
        """    if (!iDumpNextControl)
        {
        CAknAppUiBase::HandleWsEventL(aEvent, aDestination);    
        }
    switch (eventType)
""",
        """    if (htcleoHomeFocusTrace)
        HtcleoAknAppUiBaseLog(0x0000C566u, KErrNone,
            iDumpNextControl ? 1u : 0u);
    if (!iDumpNextControl)
        {
        CAknAppUiBase::HandleWsEventL(aEvent, aDestination);
        }
    if (htcleoHomeFocusTrace)
        HtcleoAknAppUiBaseLog(0x0000C567u, KErrNone, 0u);
    switch (eventType)
""",
        "AknAppUi base handler",
    )
    text = replace_once(
        text,
        """        case EEventFocusGained:
            UpdateKeyBlockMode();
            GfxTransEffect::Enable();
            iAvkonEnv->TransitionEvent(AknTransEffect::EApplicationActivate);
            if (iExtension)
""",
        """        case EEventFocusGained:
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C568u, KErrNone, 0u);
            UpdateKeyBlockMode();
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C569u, KErrNone, 0u);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Au, KErrNone, 0u);
            GfxTransEffect::Enable();
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Bu, KErrNone, 0u);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Cu, KErrNone,
                    (TUint32)iAvkonEnv);
            iAvkonEnv->TransitionEvent(AknTransEffect::EApplicationActivate);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Du, KErrNone,
                    (TUint32)iAvkonEnv);
            if (iExtension)
""",
        "AknAppUi focus branch",
    )
    text = replace_once(
        text,
        """#endif                         
                }
            break;
        case EEventFocusLost:
""",
        """#endif                         
                }
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Eu, KErrNone, 0u);
            break;
        case EEventFocusLost:
""",
        "AknAppUi focus return",
    )
    return text


def patch_sgc(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    if text.count(SGC_PREREQUISITE) != 1:
        raise SystemExit("AknSgc HomeScreen fail-open prerequisite is missing")

    text = replace_once(
        text,
        f"// {SGC_PREREQUISITE}\n",
        f"// {SGC_PREREQUISITE}\n// {MARKER}\n",
        "AknSgc marker",
    )
    text = replace_once(
        text,
        """void CAknSgcClient::DoSetKeyBlockMode(TAknKeySoundOpcode aMode)
    {
	if (iFlags[EInAknSrv])
		{
        TRawEvent event;
        TAknKeySoundOpcode opcode = EEnableKeyBlock; // default
	    if (aMode == ENoKeyBlock)
		    {
		    opcode = EDisableKeyBlock;
		    }
	    event.Set((TRawEvent::TType)opcode);
        iEikonEnv->WsSession().SimulateRawEvent(event);		
		}
	else
		{
		iAknSrv.SetKeyblockMode(aMode);
		}
    }
""",
        """void CAknSgcClient::DoSetKeyBlockMode(TAknKeySoundOpcode aMode)
    {
    const TBool htcleoHomeKeyBlock =
        (RProcess().SecureId().iId == 0x102750f0u);
    const TInt htcleoAknSrvHandle = iAknSrv.Handle();
    if (htcleoHomeKeyBlock)
        HtcleoAknAppUiBaseLog(0x0000C570u, aMode,
            iFlags[EInAknSrv] ? 1u : 0u);
    if (htcleoHomeKeyBlock)
        HtcleoAknAppUiBaseLog(0x0000C571u, htcleoAknSrvHandle, 0u);
	if (iFlags[EInAknSrv])
		{
        TRawEvent event;
        TAknKeySoundOpcode opcode = EEnableKeyBlock; // default
	    if (aMode == ENoKeyBlock)
		    {
		    opcode = EDisableKeyBlock;
		    }
	    event.Set((TRawEvent::TType)opcode);
        if (htcleoHomeKeyBlock)
            HtcleoAknAppUiBaseLog(0x0000C572u, KErrNone, opcode);
        iEikonEnv->WsSession().SimulateRawEvent(event);
        if (htcleoHomeKeyBlock)
            HtcleoAknAppUiBaseLog(0x0000C573u, KErrNone, opcode);
		}
	else if (htcleoHomeKeyBlock && htcleoAknSrvHandle == 0)
		{
        // HTC Leo has no live AknCapServer session here.  A focus-gained
        // key-block IPC on handle zero causes KERN-EXEC 0; there is no server
        // on which this optional mode could take effect.
        HtcleoAknAppUiBaseLog(0x0000C574u, KErrNotReady, aMode);
		}
	else
		{
        if (htcleoHomeKeyBlock)
            HtcleoAknAppUiBaseLog(0x0000C575u, KErrNone,
                htcleoAknSrvHandle);
		iAknSrv.SetKeyblockMode(aMode);
        if (htcleoHomeKeyBlock)
            HtcleoAknAppUiBaseLog(0x0000C576u, KErrNone,
                htcleoAknSrvHandle);
		}
    }
""",
        "HomeScreen key-block handle guard",
    )
    return text


def verify(appui: str, sgc: str) -> None:
    joined = appui + sgc
    keyblock = sgc[
        sgc.index("void CAknSgcClient::DoSetKeyBlockMode") :
        sgc.index("void CAknSgcClient::DoSetKeyboardRepeatRate")
    ]
    checks = {
        "markers": appui.count(MARKER) == 1 and sgc.count(MARKER) == 1,
        "HomeScreen gates": (
            appui.count("const TBool htcleoHomeFocusTrace") == 1
            and sgc.count("const TBool htcleoHomeKeyBlock") == 1
        ),
        "focus stages": all(
            appui.count(
                f"HtcleoAknAppUiBaseLog(0x0000C{stage:03X}u"
            ) == 1
            for stage in range(0x560, 0x56F)
        ),
        "key-block stages": all(
            sgc.count(f"0x0000C{stage:03X}u") == 1
            for stage in range(0x570, 0x577)
        ),
        "base handler retained": appui.count(
            "CAknAppUiBase::HandleWsEventL(aEvent, aDestination);"
        ) == 1,
        "focus actions retained": (
            appui.count("UpdateKeyBlockMode();") >= 2
            and appui.count("GfxTransEffect::Enable();") == 1
            and appui.count(
                "iAvkonEnv->TransitionEvent(AknTransEffect::EApplicationActivate);"
            ) == 1
        ),
        "zero-handle guard": sgc.count(
            "htcleoHomeKeyBlock && htcleoAknSrvHandle == 0"
        ) == 1,
        "real IPC retained": sgc.count("iAknSrv.SetKeyblockMode(aMode);") == 1,
        "no fabricated handle": all(
            token not in keyblock
            for token in ("SetHandle", "CreateSession", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen focus/key-block compatibility audit failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/classicui/uifw/AvKon/src"
    appui_path = base / "AknAppUi.cpp"
    sgc_path = base / "aknsgcc.cpp"
    for path in (appui_path, sgc_path):
        if not path.is_file():
            raise SystemExit(f"missing Avkon source: {path}")
    appui = patch_appui(appui_path.read_text(encoding="latin-1"))
    sgc = patch_sgc(sgc_path.read_text(encoding="latin-1"))
    appui_path.write_text(appui, encoding="latin-1")
    sgc_path.write_text(sgc, encoding="latin-1")
    verify(appui, sgc)
    print(
        "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_KEYBLOCK="
        "HSXML-C560-C576-handle0-skip"
    )


if __name__ == "__main__":
    main()
