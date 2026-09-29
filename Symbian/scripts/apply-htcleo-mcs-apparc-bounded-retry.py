#!/usr/bin/env python3
"""Retry the replacement MenuContent AppArc scan without accepting an empty tree."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


RELOAD_EMPTY_SUCCESS = r'''    if (htcleoApaReconnectResult != KErrNone
            || !iApaLsSession.Handle())
        {
        return;
        }
    TApaAppInfo appInfo;'''


RELOAD_TRANSIENT_LEAVE = r'''    if (htcleoApaReconnectResult != KErrNone
            || !iApaLsSession.Handle())
        {
        // HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1
        // Do not let an unavailable replacement AppArc session masquerade as
        // a successful empty scan.  The engine reports this transient result
        // to CMenuSrvAppScanner, which owns the bounded asynchronous retry.
        User::Leave(htcleoApaReconnectResult != KErrNone
            ? htcleoApaReconnectResult : KErrNotReady);
        }
    TApaAppInfo appInfo;'''


SCANNER_CONSTANTS_ANCHOR = r'''_LIT( KMenuMmcHistoryFname, "mmchistory" );

// ==================== LOCAL FUNCTIONS ===================='''


SCANNER_CONSTANTS_PATCHED = r'''_LIT( KMenuMmcHistoryFname, "mmchistory" );

// HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1
// Yield through the active scheduler between attempts.  This is deliberately
// bounded and does not block MatrixMenu or synthesize application entries.
const TInt KHtcleoApaRetryLimit = 12;
const TInt KHtcleoApaRetryDelayUs = 250000;

// ==================== LOCAL FUNCTIONS ===================='''


CONSTRUCTOR = r'''CMenuSrvAppScanner::CMenuSrvAppScanner(
        CMenuEng& aEng, CMenuSrvEngUtils& aSrvEngUtils )
: CActive( CActive::EPriorityStandard ), iEng( aEng ),
  iSrvEngUtils( aSrvEngUtils ),
  iNotifier( NULL ), iMmcHistory( NULL ), iCenRepSession( NULL )
    {
    // HTCLEO_MCS_SCANNER_POINTER_INIT_V1
    CActiveScheduler::Add( this );
    }'''


CONSTRUCTOR_PATCHED = r'''CMenuSrvAppScanner::CMenuSrvAppScanner(
        CMenuEng& aEng, CMenuSrvEngUtils& aSrvEngUtils )
: CActive( CActive::EPriorityStandard ), iEng( aEng ),
  iSrvEngUtils( aSrvEngUtils ),
  iNotifier( NULL ), iMmcHistory( NULL ), iCenRepSession( NULL ),
  iHtcleoApaRetryCount( 0 )
    {
    // HTCLEO_MCS_SCANNER_POINTER_INIT_V1
    CActiveScheduler::Add( this );
    }'''


DESTRUCTOR_TAIL = r'''  	delete iCenRepSession;
  	delete iFreeSpaceObserver;

    }'''


DESTRUCTOR_TAIL_PATCHED = r'''  	delete iCenRepSession;
  	delete iFreeSpaceObserver;
    iHtcleoApaRetryTimer.Close();

    }'''


RUNL = r'''void CMenuSrvAppScanner::RunL()
    {
    User::LeaveIfError( iStatus.Int() ); // Handle errors in RunL.
    // AppArc app scan complete, we have the app list.'''


RUNL_PATCHED = r'''void CMenuSrvAppScanner::RunL()
    {
    HtcleoMcsLog(0x4D430165u, iStatus.Int(),
        (TUint32)iHtcleoApaRetryCount);
    User::LeaveIfError( iStatus.Int() ); // Handle errors in RunL.
    // AppArc app scan complete, we have the app list.'''


DOCANCEL = r'''void CMenuSrvAppScanner::DoCancel()
    {
    }'''


DOCANCEL_PATCHED = r'''void CMenuSrvAppScanner::DoCancel()
    {
    if (iHtcleoApaRetryTimer.Handle())
        {
        iHtcleoApaRetryTimer.Cancel();
        }
    }'''


COMPLETED = r'''void CMenuSrvAppScanner::CompletedMenuEngOperation( TInt aErr )
    {
    iOpStatus = EFalse;
    HtcleoMcsLog(0x4D43012Fu, aErr, 0u);
    }'''


COMPLETED_PATCHED = r'''void CMenuSrvAppScanner::CompletedMenuEngOperation( TInt aErr )
    {
    iOpStatus = EFalse;
    const TInt htcleoAppCount = iSrvEngUtils.GetAppItemsL().Count();
    HtcleoMcsLog(0x4D43012Fu, aErr, (TUint32)htcleoAppCount);

    TInt htcleoRetryReason = aErr;
    if (htcleoRetryReason == KErrNone && htcleoAppCount == 0)
        {
        htcleoRetryReason = KErrNotReady;
        }

    if ((htcleoRetryReason == KErrNotFound
            || htcleoRetryReason == KErrServerTerminated
            || htcleoRetryReason == KErrNotReady)
            && iHtcleoApaRetryCount < KHtcleoApaRetryLimit
            && !IsActive())
        {
        TInt htcleoTimerResult = KErrNone;
        if (!iHtcleoApaRetryTimer.Handle())
            {
            htcleoTimerResult = iHtcleoApaRetryTimer.CreateLocal();
            }
        if (htcleoTimerResult == KErrNone)
            {
            ++iHtcleoApaRetryCount;
            iOpStatus = ETrue;
            iStatus = KRequestPending;
            SetActive();
            iHtcleoApaRetryTimer.After(iStatus, KHtcleoApaRetryDelayUs);
            }
        HtcleoMcsLog(0x4D430166u, htcleoTimerResult,
            (TUint32)iHtcleoApaRetryCount);
        if (htcleoTimerResult != KErrNone)
            {
            iOpStatus = EFalse;
            }
        return;
        }

    if (aErr == KErrNone && htcleoAppCount > 0)
        {
        iHtcleoApaRetryCount = 0;
        }
    HtcleoMcsLog(0x4D430167u, htcleoRetryReason,
        (TUint32)htcleoAppCount);
    }'''


HEADER_FIELDS = r'''    TBool iOpStatus;
    };'''


HEADER_FIELDS_PATCHED = r'''    TBool iOpStatus;

    // HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1
    RTimer iHtcleoApaRetryTimer;
    TInt iHtcleoApaRetryCount;
    };'''


def install(utils: str, scanner: str, header: str) -> tuple[str, str, str]:
    utils = replace_once(
        utils, RELOAD_EMPTY_SUCCESS, RELOAD_TRANSIENT_LEAVE, "AppArc empty success"
    )
    scanner = replace_once(
        scanner,
        SCANNER_CONSTANTS_ANCHOR,
        SCANNER_CONSTANTS_PATCHED,
        "retry constants",
    )
    scanner = replace_once(scanner, CONSTRUCTOR, CONSTRUCTOR_PATCHED, "constructor")
    scanner = replace_once(
        scanner, DESTRUCTOR_TAIL, DESTRUCTOR_TAIL_PATCHED, "destructor timer"
    )
    scanner = replace_once(scanner, RUNL, RUNL_PATCHED, "RunL retry trace")
    scanner = replace_once(scanner, DOCANCEL, DOCANCEL_PATCHED, "timer cancellation")
    scanner = replace_once(
        scanner, COMPLETED, COMPLETED_PATCHED, "bounded retry completion"
    )
    header = replace_once(header, HEADER_FIELDS, HEADER_FIELDS_PATCHED, "retry fields")
    return utils, scanner, header


def verify(utils: str, scanner: str, header: str) -> None:
    checks = {
        "markers": utils.count(MARKER) == 1
        and scanner.count(MARKER) == 1
        and header.count(MARKER) == 1,
        "transient propagation": (
            (
                utils.count("? htcleoApaReconnectResult : KErrNotReady") == 1
                or (
                    utils.count("HTCLEO_MCS_APPARC_RETURNED_RETRY_V2") == 2
                    and utils.count(
                        "return htcleoApaReconnectResult != KErrNone"
                    )
                    == 1
                )
            )
            and utils.count("0x4D43012Bu") == 1
            and utils.count("0x4D43012Cu") == 1
        ),
        "bounded timer": (
            scanner.count("KHtcleoApaRetryLimit = 12") == 1
            and scanner.count("KHtcleoApaRetryDelayUs = 250000") == 1
            and scanner.count("iHtcleoApaRetryTimer.After") == 1
            and scanner.count("iHtcleoApaRetryTimer.Cancel") == 1
            and scanner.count("iHtcleoApaRetryTimer.Close") == 1
        ),
        "retry state": (
            header.count("RTimer iHtcleoApaRetryTimer;") == 1
            and header.count("TInt iHtcleoApaRetryCount;") == 1
            and scanner.count("iHtcleoApaRetryCount( 0 )") == 1
        ),
        "stages": all(
            scanner.count(f"0x4D430{stage:03X}u") == 1
            for stage in range(0x165, 0x168)
        ),
        "real AppArc retained": (
            utils.count("iApaLsSession.Connect()")
            == (
                3
                if "HTCLEO_MCS_APPARC_SERVER_RESTART_V1" in utils
                else 2
            )
            and utils.count("iApaLsSession.GetAllApps( 0 )") == 1
            and scanner.count("iEng.QueueOperationL( *this );") == 1
        ),
        "no fake data or blocking delay": (
            "User::After" not in scanner
            and "HalFunction" not in scanner
            and "AppendL( htcleo" not in scanner
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS bounded AppArc retry verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    utils_path = component / "srvsrc/menusrvengutils.cpp"
    scanner_path = component / "srvsrc/menusrvappscanner.cpp"
    header_path = component / "srvinc/menusrvappscanner.h"
    for path in (utils_path, scanner_path, header_path):
        if not path.is_file():
            raise SystemExit(f"missing MenuContent source: {path}")

    utils = utils_path.read_text(encoding="latin-1")
    scanner = scanner_path.read_text(encoding="latin-1")
    header = header_path.read_text(encoding="latin-1")
    if MARKER not in utils:
        utils, scanner, header = install(utils, scanner, header)
    verify(utils, scanner, header)
    utils_path.write_text(utils, encoding="latin-1")
    scanner_path.write_text(scanner, encoding="latin-1")
    header_path.write_text(header, encoding="latin-1")
    print("HTCLEO_MCS_APPARC_BOUNDED_RETRY=165-167-12x250ms-real-scan")


if __name__ == "__main__":
    main()
