#!/usr/bin/env python3
"""Attribute HomeScreen main-controller creation without changing semantics."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HOMESCREEN_CONTROLLER_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        '#include "debug.h"\n',
        '#include "debug.h"\n#include "htcleohomelog.h"\n',
        "logger include",
    )
    text = replace_once(
        text,
        """void CAiUiControllerManager::LoadMainControllerL( CRepository& aRepository )    
    {
    TInt value( 0 );
    
    // Main UI Controller must be configured correctly
    User::LeaveIfError( aRepository.Get( KAiMainUIController, value ) );
    
    CAiUiController* controller = CAiUiController::NewL( TUid::Uid( value ) );
    
    iCreatedUICList.Append( value );
    CleanupStack::PushL( controller );
    
    iMainUiController = controller->MainInterface();""",
        """void CAiUiControllerManager::LoadMainControllerL( CRepository& aRepository )    
    {
    // HTCLEO_HOMESCREEN_CONTROLLER_TRACE_V1
    TInt value( 0 );
    
    // Main UI Controller must be configured correctly
    const TInt htcleoRepositoryResult =
        aRepository.Get( KAiMainUIController, value );
    HtcleoHomeLog(0x484F0130u, htcleoRepositoryResult, (TUint32)value);
    User::LeaveIfError( htcleoRepositoryResult );
    
    CAiUiController* controller = NULL;
    TRAPD(htcleoControllerResult,
        controller = CAiUiController::NewL( TUid::Uid( value ) ));
    HtcleoHomeLog(0x484F0131u, htcleoControllerResult,
        (TUint32)value);
    User::LeaveIfError( htcleoControllerResult );
    HtcleoHomeLog(0x484F0132u, KErrNone, (TUint32)controller);
    
    iCreatedUICList.Append( value );
    CleanupStack::PushL( controller );
    
    iMainUiController = controller->MainInterface();
    HtcleoHomeLog(0x484F0133u,
        iMainUiController ? KErrNone : KErrNotFound,
        (TUint32)iMainUiController);""",
        "main controller creation",
    )
    text = replace_once(
        text,
        """    iUiControllerArray.AppendL( controller );
    CleanupStack::Pop( controller );    
    }""",
        """    iUiControllerArray.AppendL( controller );
    CleanupStack::Pop( controller );
    HtcleoHomeLog(0x484F0134u, KErrNone,
        (TUint32)iUiControllerArray.Count());
    }""",
        "main controller append",
    )
    text = replace_once(
        text,
        """    TRAP_IGNORE( LoadSecondaryControllersL( repository ) );
                           
    for ( TInt i = 0; i < iUiControllerArray.Count(); i++ )
        {
        iUiControllerArray[i]->SetEventHandler( *aAiFw );
        }
        
    __TIME_ENDMARK("FW: Create UI Ctrls", t);""",
        """    TRAP_IGNORE( LoadSecondaryControllersL( repository ) );
    HtcleoHomeLog(0x484F0135u, KErrNone,
        (TUint32)iUiControllerArray.Count());
                           
    for ( TInt i = 0; i < iUiControllerArray.Count(); i++ )
        {
        HtcleoHomeLog(0x484F0136u, KErrNone, (TUint32)i);
        iUiControllerArray[i]->SetEventHandler( *aAiFw );
        }
    HtcleoHomeLog(0x484F0137u, KErrNone,
        (TUint32)iUiControllerArray.Count());
        
    __TIME_ENDMARK("FW: Create UI Ctrls", t);""",
        "controller event handlers",
    )
    return text


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "stages": all(
            text.count(f"0x484F{stage:04X}u") == 1
            for stage in range(0x0130, 0x0138)
        ),
        "real controller": text.count(
            "controller = CAiUiController::NewL( TUid::Uid( value ) )"
        ) == 1,
        "failure preserved": text.count(
            "User::LeaveIfError( htcleoControllerResult )"
        ) == 1,
        "main interface retained": text.count(
            "iMainUiController = controller->MainInterface();"
        ) == 1,
        "no fabricated UI or delay": all(
            token not in text[text.index(MARKER) : text.index(MARKER) + 1800]
            for token in ("User::After", "CreateWindowL", "SetPixel")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen controller trace verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/idlefw/src/framework/aiuicontrollermanager.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing controller manager source: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_HOMESCREEN_CONTROLLER_TRACE="
        "cenrep-ecom-maininterface-array-handlers-0130-0137"
    )


if __name__ == "__main__":
    main()
