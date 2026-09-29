#!/usr/bin/env python3
"""Repair an empty Active Idle root from its real ROM configuration once."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_V1"


HELPER = r'''

// HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL_V1
static TBool gHtcleoRootRepairAttempted = EFalse;

static TInt HtcleoHspsRootPluginCount(ChspsODT& aOdt)
    {
    ChspsDomNode* root = aOdt.DomDocument().RootNode();
    if (!root)
        return KErrNotFound;
    ChspsDomNode* configuration = hspsServerUtil::FindNodeByTagL(
        KConfigurationElement, *root);
    if (!configuration)
        return KErrNotFound;
    ChspsDomNode* control = static_cast<ChspsDomNode*>(
        configuration->ChildNodes().FindByName(KControlElement));
    if (!control)
        return KErrNotFound;
    ChspsDomNode* plugins = static_cast<ChspsDomNode*>(
        control->ChildNodes().FindByName(KPluginsElement));
    if (!plugins)
        return KErrNotFound;
    return plugins->ChildNodes().Length();
    }
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if '#include "hspsdomdocument.h"\n' not in text:
        text = replace_once(
            text,
            '#include "hspsconfiguration.h"\n',
            '#include "hspsconfiguration.h"\n'
            '#include "hspsdomdocument.h"\n',
            "DOM document include",
        )
    if MARKER not in text:
        text = replace_once(
            text,
            '#include "hspsdomdocument.h"\n',
            '#include "hspsdomdocument.h"\n'
            '#include "hspsdomnode.h"\n'
            '#include "hspsdomlist.h"\n',
            "DOM includes",
        )
        text = replace_once(
            text,
            "#ifdef _hsps_PERFORMANCE_TEST_\n"
            '#include "hspstimemon.h"\n'
            "#endif //_hsps_PERFORMANCE_TEST_\n",
            HELPER
            + "\n#ifdef _hsps_PERFORMANCE_TEST_\n"
            + '#include "hspstimemon.h"\n'
            + "#endif //_hsps_PERFORMANCE_TEST_\n",
            "self-heal helper",
        )

    if MARKER in text and "0x48581370u" in text:
        for old, new in zip(range(0x70, 0x75), range(0xE0, 0xE5)):
            text = text.replace(
                f"0x485813{old:02X}u", f"0x485813{new:02X}u", 1
            )

    if "0x485813E0u" not in text:
        old = '''    // Get a complete ODT instance from the definition repository
    if ( iDefinitionRepository->GetOdtL( aRetrievedODT ) )    
        {        
#ifdef HSPS_LOG_ACTIVE        
        iLogBus->LogText( _L( "ChspsThemeServer::GetConfigurationL(): - theme cannot be accessed." ) );
#endif                
        return KErrAccessDenied;
        }    
    
    return KErrNone;
'''
        new = '''    // Get a complete ODT instance from the definition repository
    TInt repositoryError = iDefinitionRepository->GetOdtL( aRetrievedODT );
    if ( repositoryError )
        {
#ifdef HSPS_LOG_ACTIVE
        iLogBus->LogText( _L( "ChspsThemeServer::GetConfigurationL(): - theme cannot be accessed." ) );
#endif
        return KErrAccessDenied;
        }

#ifdef __HTCLEO_HSPS_HD2_FAMILY_COMPAT__
    TInt htcleoRootPluginCount = HtcleoHspsRootPluginCount(aRetrievedODT);
    HtcleoHspsServerLog(0x485813E0u, htcleoRootPluginCount,
        (TUint32)aRetrievedODT.ThemeUid());
    if (aRetrievedODT.RootUid() == (TInt)KAppId_hspsAI &&
        aRetrievedODT.ThemeUid() == 0x2001F482 &&
        aRetrievedODT.ConfigurationType() == EhspsAppConfiguration &&
        htcleoRootPluginCount == 0)
        {
        const TBool repositoryLocked = iDefinitionRepository->Locked();
        HtcleoHspsServerLog(0x485813E1u, (TInt)repositoryLocked,
            (TUint32)aRetrievedODT.RootUid());
        if (!repositoryLocked && !gHtcleoRootRepairAttempted)
            {
            gHtcleoRootRepairAttempted = ETrue;
            TRAPD(reinstallError,
                ReinstallConfL(aRetrievedODT.RootUid(),
                    aRetrievedODT.ThemeUid()));
            HtcleoHspsServerLog(0x485813E2u, reinstallError,
                (TUint32)aRetrievedODT.ThemeUid());
            if (reinstallError == KErrNone)
                {
                repositoryError = iDefinitionRepository->GetOdtL(
                    aRetrievedODT);
                htcleoRootPluginCount =
                    HtcleoHspsRootPluginCount(aRetrievedODT);
                HtcleoHspsServerLog(0x485813E3u, repositoryError,
                    (TUint32)htcleoRootPluginCount);
                }
            }
        }
    HtcleoHspsServerLog(0x485813E4u, htcleoRootPluginCount,
        (TUint32)gHtcleoRootRepairAttempted);
#endif

    return KErrNone;
'''
        text = replace_once(text, old, new, "GetConfiguration self-heal")
    return text


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "DOM document include": text.count('#include "hspsdomdocument.h"') == 1,
        "exact root": text.count("0x2001F482") == 1,
        "exact app": text.count("KAppId_hspsAI") >= 2,
        "one-shot": text.count("gHtcleoRootRepairAttempted = ETrue") == 1,
        "real reinstall": text.count("ReinstallConfL(aRetrievedODT.RootUid()") == 1,
        "real reload": text.count("iDefinitionRepository->GetOdtL(\n                    aRetrievedODT)") == 1,
        "locked guard": text.count("!repositoryLocked && !gHtcleoRootRepairAttempted") == 1,
        "stages": all(text.count(f"0x485813{stage:02X}u") == 1 for stage in range(0xE0, 0xE5)),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS active-root self-heal verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/mw/homescreensrv/homescreenpluginsrv/hspsmanager/"
        "src/hspsthemeserver.cpp"
    )
    text = install(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_HSPS_ACTIVE_ROOT_SELF_HEAL="
        "ai3-2001f482-empty-reinstall-once-real-rom"
    )


if __name__ == "__main__":
    main()
