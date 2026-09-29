#!/usr/bin/env python3
"""Keep replacement MenuContent scanner alive without optional bootstrap data."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_SCANNER_OPTIONAL_CONSTRUCT_FAILOPEN_V1"
POINTER_INIT_MARKER = "HTCLEO_MCS_SCANNER_POINTER_INIT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


CONSTRUCT_DEPS = r'''    iMmcHistory = new (ELeave) CMenuSrvMmcHistory();
    iMmcHistory->LoadL( iFs, KMenuMmcHistoryFname() );
    // The notifier has its own session to apparc, instead of taking
    // it as argument... :(
    iNotifier = CApaAppListNotifier::NewL( this, CActive::EPriorityStandard );

   	iCenRepSession = CRepository::NewL( KCRUidMenu );'''


CONSTRUCT_DEPS_PATCHED = r'''    // HTCLEO_MCS_SCANNER_OPTIONAL_CONSTRUCT_FAILOPEN_V1
    // MMC history, the long-lived AppArc notifier and hide-list CenRep are
    // optional for the real initial AppArc enumeration.  A replacement MCS
    // process currently sees KErrNotFound in this constructor; keep the core
    // scan alive while retaining narrow failures for all other errors.
    iMmcHistory = new (ELeave) CMenuSrvMmcHistory();
    TRAPD(htcleoHistoryResult,
        iMmcHistory->LoadL( iFs, KMenuMmcHistoryFname() ));
    HtcleoMcsLog(0x4D430160u, htcleoHistoryResult, 0u);
    if (htcleoHistoryResult != KErrNone
            && htcleoHistoryResult != KErrNotFound
            && htcleoHistoryResult != KErrPathNotFound)
        {
        User::Leave(htcleoHistoryResult);
        }

    iNotifier = NULL;
    TRAPD(htcleoNotifierResult,
        iNotifier = CApaAppListNotifier::NewL(
            this, CActive::EPriorityStandard ));
    HtcleoMcsLog(0x4D430161u, htcleoNotifierResult,
        iNotifier ? 1u : 0u);
    if (htcleoNotifierResult != KErrNone
            && htcleoNotifierResult != KErrNotFound
            && htcleoNotifierResult != KErrServerTerminated)
        {
        User::Leave(htcleoNotifierResult);
        }

    iCenRepSession = NULL;
    TRAPD(htcleoCenRepResult,
        iCenRepSession = CRepository::NewL( KCRUidMenu ));
    HtcleoMcsLog(0x4D430162u, htcleoCenRepResult,
        iCenRepSession ? 1u : 0u);
    if (htcleoCenRepResult != KErrNone
            && htcleoCenRepResult != KErrNotFound
            && htcleoCenRepResult != KErrPathNotFound
            && htcleoCenRepResult != KErrServerTerminated)
        {
        User::Leave(htcleoCenRepResult);
        }
    HtcleoMcsLog(0x4D430163u, KErrNone,
        (iMmcHistory ? 1u : 0u)
            | (iNotifier ? 2u : 0u)
            | (iCenRepSession ? 4u : 0u));'''


GET_CR = r'''void CMenuSrvAppScanner::GetCrItemsL( RPointerArray<CMenuSrvAppAttributes>& aArray )
    {
 	TBuf<KCenRepBufferSize> buf;
	iCenRepSession->Get( KMenuHideCPApplication, buf );
	ParseUidsL( buf, aArray );// parses UIDs from buf and appends them to array
	iCenRepSession->Get( KMenuHideApplication, buf );
	ParseUidsL( buf, aArray );// parses UIDs from buf and appends them to array
    }'''


GET_CR_PATCHED = r'''void CMenuSrvAppScanner::GetCrItemsL( RPointerArray<CMenuSrvAppAttributes>& aArray )
    {
    if (!iCenRepSession)
        {
        HtcleoMcsLog(0x4D430164u, KErrNotSupported, 0u);
        return;
        }
 	TBuf<KCenRepBufferSize> buf;
	iCenRepSession->Get( KMenuHideCPApplication, buf );
	ParseUidsL( buf, aArray );// parses UIDs from buf and appends them to array
	iCenRepSession->Get( KMenuHideApplication, buf );
	ParseUidsL( buf, aArray );// parses UIDs from buf and appends them to array
    }'''


CONSTRUCTOR = r'''CMenuSrvAppScanner::CMenuSrvAppScanner(
        CMenuEng& aEng, CMenuSrvEngUtils& aSrvEngUtils )
: CActive( CActive::EPriorityStandard ), iEng( aEng ),
  iSrvEngUtils( aSrvEngUtils )
    {
    CActiveScheduler::Add( this );
    }'''


CONSTRUCTOR_PATCHED = r'''CMenuSrvAppScanner::CMenuSrvAppScanner(
        CMenuEng& aEng, CMenuSrvEngUtils& aSrvEngUtils )
: CActive( CActive::EPriorityStandard ), iEng( aEng ),
  iSrvEngUtils( aSrvEngUtils ),
  iNotifier( NULL ), iMmcHistory( NULL ), iCenRepSession( NULL )
    {
    // HTCLEO_MCS_SCANNER_POINTER_INIT_V1
    CActiveScheduler::Add( this );
    }'''


def install(source: str) -> str:
    source = replace_once(
        source, CONSTRUCT_DEPS, CONSTRUCT_DEPS_PATCHED, "optional scanner deps"
    )
    source = replace_once(source, GET_CR, GET_CR_PATCHED, "CenRep null guard")
    return source


def install_pointer_init(source: str) -> str:
    if POINTER_INIT_MARKER not in source:
        source = replace_once(
            source, CONSTRUCTOR, CONSTRUCTOR_PATCHED, "scanner pointer initialization"
        )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "pointer marker": source.count(POINTER_INIT_MARKER) == 1,
        "explicit pointers": (
            source.count("iNotifier( NULL )") == 1
            and source.count("iMmcHistory( NULL )") == 1
            and source.count("iCenRepSession( NULL )") == 1
        ),
        "stages": all(
            source.count(f"0x4D430{stage:03X}u") == 1
            for stage in range(0x160, 0x165)
        ),
        "real scan retained": (
            source.count("ScheduleScan();") >= 1
            and source.count("iEng.QueueOperationL( *this );") == 1
        ),
        "history object retained": source.count(
            "iMmcHistory = new (ELeave) CMenuSrvMmcHistory();"
        ) == 1,
        "narrow optional errors": (
            source.count("htcleoHistoryResult != KErrNotFound") == 1
            and source.count("htcleoNotifierResult != KErrNotFound") == 1
            and source.count("htcleoCenRepResult != KErrNotFound") == 1
            and source.count("htcleoNotifierResult != KErrServerTerminated") == 1
            and source.count("htcleoCenRepResult != KErrServerTerminated") == 1
        ),
        "CenRep guard": source.count("if (!iCenRepSession)") == 1,
        "no wait or display": (
            "User::After" not in source and "HalFunction" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS scanner optional construct fail-open failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/menusrvappscanner.cpp"
    )
    if not source_path.is_file():
        raise SystemExit("missing MenuContent scanner source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    source = install_pointer_init(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print("HTCLEO_MCS_SCANNER_OPTIONAL_CONSTRUCT=160-164-narrow-failopen")


if __name__ == "__main__":
    main()
