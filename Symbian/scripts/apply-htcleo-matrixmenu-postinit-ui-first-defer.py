#!/usr/bin/env python3
"""Defer optional post-initialize MatrixMenu services on HTC Leo.

The first visible shell does not require Menu Framework ECom extensions or the
MatrixMenu-owned dynamic skin notification session.  Defer both after initial HN
evaluation, retain AppKey/P&S/core UI, and make every extension use NULL-safe.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_POSTINIT_UI_FIRST_DEFER_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        """    iMmExtManager = CMMExtensionManager::NewL( *this );
    HtcleoMenuLog(0x4D4D030Fu, KErrNone, iMmExtManager ? 1u : 0u);

    iScreenOn = ETrue;
    iSkinChangeNeeded = EFalse;
    iSkinChangeInProgress = EFalse;
    iHasFocus = ETrue;

    iSkinSrvSession.Connect(this);
    HtcleoMenuLog(0x4D4D0310u, KErrNone, 0u);
""",
        """    // HTCLEO_MATRIXMENU_POSTINIT_UI_FIRST_DEFER_V1
    // ECom menu extensions and dynamic skin-change notifications are optional
    // for the first visible shell.  Preserve members and report the defer.
    iMmExtManager = NULL;
    HtcleoMenuLog(0x4D4D030Fu, KErrNotSupported, 0x4558544Eu);

    iScreenOn = ETrue;
    iSkinChangeNeeded = EFalse;
    iSkinChangeInProgress = EFalse;
    iHasFocus = ETrue;

    HtcleoMenuLog(0x4D4D0310u, KErrNotSupported, 0x534B494Eu);
""",
        "startup optional services",
    )
    source = replace_once(
        source,
        """    iMmExtManager = CMMExtensionManager::NewL( *this );

    iScreenOn = ETrue;
""",
        """    // Keep optional extensions deferred across reset as well.
    iMmExtManager = NULL;

    iScreenOn = ETrue;
""",
        "reset extension manager",
    )
    source = replace_once(
        source,
        """    iCurrentContainer->SetExDialogOpened( ETrue );
    return iMmExtManager->ExecuteActionL( aUid, aCommand, aEventParamList);
""",
        """    iCurrentContainer->SetExDialogOpened( ETrue );
    if ( !iMmExtManager )
        {
        iCurrentContainer->SetExDialogOpened( EFalse );
        return KErrNotSupported;
        }
    return iMmExtManager->ExecuteActionL( aUid, aCommand, aEventParamList);
""",
        "extension action guard",
    )
    source = replace_once(
        source,
        """    // closing all dialogs opened in ui extensions before exit
    iMmExtManager->ExecuteActionL( TUid::Null(), KCommandDeleteDialog, NULL );
""",
        """    // closing all dialogs opened in ui extensions before exit
    if ( iMmExtManager )
        {
        iMmExtManager->ExecuteActionL(
            TUid::Null(), KCommandDeleteDialog, NULL );
        }
""",
        "extension cleanup guard",
    )
    return source


def verify(source: str) -> None:
    late_haze = "HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION_V1" in source
    checks = {
        "single marker": source.count(MARKER) == 1,
        "startup extension defer": source.count(
            "HtcleoMenuLog(0x4D4D030Fu, KErrNotSupported, 0x4558544Eu);"
        ) == 1,
        "skin session policy": (
            (
                source.count(
                    "HtcleoMenuLog(0x4D4D0310u, KErrNotSupported, "
                    "0x534B494Eu);"
                ) == 1
                and "iSkinSrvSession.Connect(this);" not in source
            )
            if not late_haze
            else (
                source.count("iSkinSrvSession.Connect(this)") == 1
                and source.count("SetAllDefinitionSets(htcleoHazePid)") == 1
            )
        ),
        "manager constructors retired": "CMMExtensionManager::NewL(" not in source,
        "manager null assignments": source.count("iMmExtManager = NULL;") >= 3,
        "extension action guard": source.count("if ( !iMmExtManager )") == 1,
        "existing message guard retained": source.count("if( iMmExtManager )") == 1,
        "cleanup guard": source.count("if ( iMmExtManager )") == 1,
        "AppKey retained": source.count("iAppkeyHandler = CMmAppkeyHandler::NewL();") == 1,
        "P&S retained": source.count(
            "RProperty::Define( KMMenuPSCat, KMMenuLastViewKey, RProperty::EText );"
        ) == 1,
        "no timer display or fake success": (
            "User::After" not in source[source.index(MARKER) - 300 : source.index(MARKER) + 1200]
            and "HalFunction" not in source[source.index(MARKER) - 300 : source.index(MARKER) + 1200]
            and "0x4558544Eu);" in source
            and "0x534B494Eu);" in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MatrixMenu post-init defer failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not source_path.is_file():
        raise SystemExit("missing MatrixMenu AppUi source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    if "HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION_V1" in source:
        print(
            "HTCLEO_MATRIXMENU_POSTINIT=extensions-deferred "
            "skin=late-haze-0310-0360-0362"
        )
    else:
        print(
            "HTCLEO_MATRIXMENU_POSTINIT=deferred "
            "extensions=030F-4558544E skin=0310-534B494E"
        )


if __name__ == "__main__":
    main()
