#!/usr/bin/env python3
"""Return transient AppArc status to the scanner before scheduling its retry."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_APPARC_RETURNED_RETRY_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


UTILS_DECL = "    void ReloadApaItemsL();"
UTILS_DECL_RETURNED = r'''    // HTCLEO_MCS_APPARC_RETURNED_RETRY_V2
    TInt ReloadApaItemsL();'''


UTILS_SIGNATURE = "void CMenuSrvEngUtils::ReloadApaItemsL()"
UTILS_SIGNATURE_RETURNED = r'''// HTCLEO_MCS_APPARC_RETURNED_RETRY_V2
TInt CMenuSrvEngUtils::ReloadApaItemsL()'''


UTILS_TRANSIENT_LEAVE = r'''        // HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1
        // Do not let an unavailable replacement AppArc session masquerade as
        // a successful empty scan.  The engine reports this transient result
        // to CMenuSrvAppScanner, which owns the bounded asynchronous retry.
        User::Leave(htcleoApaReconnectResult != KErrNone
            ? htcleoApaReconnectResult : KErrNotReady);'''


UTILS_TRANSIENT_RETURN = r'''        // HTCLEO_MCS_APPARC_BOUNDED_RETRY_V1
        // HTCLEO_MCS_APPARC_RETURNED_RETRY_V2
        // Return the transient result without leaving through CMenuEng.  The
        // scanner will stop before mutating missing flags and will schedule
        // its own bounded asynchronous retry from normal completion.
        return htcleoApaReconnectResult != KErrNone
            ? htcleoApaReconnectResult : KErrNotReady;'''


UTILS_SUCCESS_TAIL = r'''    HtcleoMcsLog(0x4D43012Cu, KErrNone,
        (TUint32)iAppAttributes.Count());
    }'''


UTILS_SUCCESS_TAIL_RETURNED = r'''    HtcleoMcsLog(0x4D43012Cu, KErrNone,
        (TUint32)iAppAttributes.Count());
    return KErrNone;
    }'''


SCANNER_CONSTRUCTOR = r'''  iNotifier( NULL ), iMmcHistory( NULL ), iCenRepSession( NULL ),
  iHtcleoApaRetryCount( 0 )'''


SCANNER_CONSTRUCTOR_RETURNED = r'''  iNotifier( NULL ), iMmcHistory( NULL ), iCenRepSession( NULL ),
  iHtcleoApaRetryCount( 0 ), iHtcleoApaReloadResult( KErrNone )'''


SCANNER_RELOAD_CALL = "    iSrvEngUtils.ReloadApaItemsL();"
SCANNER_RELOAD_RETURNED = r'''    iHtcleoApaReloadResult = KErrNotReady;
    iHtcleoApaReloadResult = iSrvEngUtils.ReloadApaItemsL();
    if (iHtcleoApaReloadResult != KErrNone)
        {
        // Do not interpret a failed AppArc connection as an empty system and
        // do not mark the ROM menu entries missing.
        CleanupStack::PopAndDestroy( &mcsItems );
        return;
        }'''


SCANNER_OPERATION = r'''    UpdateApplicationItemsL();
    HtcleoMcsLog(0x4D430129u, KErrNone,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    UpdateApplicationWithHideIfInstalledItemsL();
    UpdateLinkItemsL();
    iOpStatus = EFalse;
    HtcleoMcsLog(0x4D43012Au, KErrNone, 0u);'''


SCANNER_OPERATION_RETURNED = r'''    UpdateApplicationItemsL();
    HtcleoMcsLog(0x4D430129u, iHtcleoApaReloadResult,
        (TUint32)iSrvEngUtils.GetAppItemsL().Count());
    if (iHtcleoApaReloadResult == KErrNone)
        {
        UpdateApplicationWithHideIfInstalledItemsL();
        UpdateLinkItemsL();
        }
    iOpStatus = EFalse;
    HtcleoMcsLog(0x4D43012Au, iHtcleoApaReloadResult, 0u);'''


COMPLETED_PREFIX = r'''    const TInt htcleoAppCount = iSrvEngUtils.GetAppItemsL().Count();
    HtcleoMcsLog(0x4D43012Fu, aErr, (TUint32)htcleoAppCount);

    TInt htcleoRetryReason = aErr;
    if (htcleoRetryReason == KErrNone && htcleoAppCount == 0)
        {
        htcleoRetryReason = KErrNotReady;
        }'''


COMPLETED_PREFIX_RETURNED = r'''    const TInt htcleoAppCount = iSrvEngUtils.GetAppItemsL().Count();
    TInt htcleoRetryReason = aErr;
    if (htcleoRetryReason == KErrNone
            && iHtcleoApaReloadResult != KErrNone)
        {
        htcleoRetryReason = iHtcleoApaReloadResult;
        }
    else if (htcleoRetryReason == KErrNone && htcleoAppCount == 0)
        {
        htcleoRetryReason = KErrNotReady;
        }
    HtcleoMcsLog(0x4D43012Fu, htcleoRetryReason,
        (TUint32)htcleoAppCount);'''


HEADER_FIELDS = r'''    RTimer iHtcleoApaRetryTimer;
    TInt iHtcleoApaRetryCount;'''


HEADER_FIELDS_RETURNED = r'''    RTimer iHtcleoApaRetryTimer;
    TInt iHtcleoApaRetryCount;

    // HTCLEO_MCS_APPARC_RETURNED_RETRY_V2
    TInt iHtcleoApaReloadResult;'''


def install(
    utils: str, utils_header: str, scanner: str, scanner_header: str
) -> tuple[str, str, str, str]:
    utils_header = replace_once(
        utils_header, UTILS_DECL, UTILS_DECL_RETURNED, "ReloadApaItems declaration"
    )
    utils = replace_once(
        utils, UTILS_SIGNATURE, UTILS_SIGNATURE_RETURNED, "ReloadApaItems signature"
    )
    utils = replace_once(
        utils, UTILS_TRANSIENT_LEAVE, UTILS_TRANSIENT_RETURN, "transient return"
    )
    utils = replace_once(
        utils, UTILS_SUCCESS_TAIL, UTILS_SUCCESS_TAIL_RETURNED, "success return"
    )
    scanner = replace_once(
        scanner,
        SCANNER_CONSTRUCTOR,
        SCANNER_CONSTRUCTOR_RETURNED,
        "scanner reload result initialization",
    )
    scanner = replace_once(
        scanner, SCANNER_RELOAD_CALL, SCANNER_RELOAD_RETURNED, "scanner reload result"
    )
    scanner = replace_once(
        scanner,
        SCANNER_OPERATION,
        SCANNER_OPERATION_RETURNED,
        "scanner operation result",
    )
    scanner = replace_once(
        scanner,
        COMPLETED_PREFIX,
        COMPLETED_PREFIX_RETURNED,
        "normal completion retry result",
    )
    scanner_header = replace_once(
        scanner_header,
        HEADER_FIELDS,
        HEADER_FIELDS_RETURNED,
        "scanner reload result field",
    )
    return utils, utils_header, scanner, scanner_header


def verify(utils: str, utils_header: str, scanner: str, scanner_header: str) -> None:
    checks = {
        "markers": (
            utils.count(MARKER) == 2
            and utils_header.count(MARKER) == 1
            and scanner_header.count(MARKER) == 1
        ),
        "returned API": (
            utils_header.count("TInt ReloadApaItemsL();") == 1
            and utils.count("TInt CMenuSrvEngUtils::ReloadApaItemsL()") == 1
            and utils.count("return htcleoApaReconnectResult != KErrNone") == 1
            and utils.count("return KErrNone;") >= 1
            and "User::Leave(htcleoApaReconnectResult" not in utils
        ),
        "stop before mutation": (
            scanner.count("iHtcleoApaReloadResult = iSrvEngUtils.ReloadApaItemsL();")
            == 1
            and scanner.count("CleanupStack::PopAndDestroy( &mcsItems );") >= 2
            and scanner.count("if (iHtcleoApaReloadResult == KErrNone)") == 1
        ),
        "normal completion scheduling": (
            scanner.count("htcleoRetryReason = iHtcleoApaReloadResult;") == 1
            and scanner.count("iHtcleoApaRetryTimer.After") == 1
            and scanner.count("KHtcleoApaRetryLimit = 12") == 1
        ),
        "state": (
            scanner_header.count("TInt iHtcleoApaReloadResult;") == 1
            and scanner.count("iHtcleoApaReloadResult( KErrNone )") == 1
        ),
        "real enumeration retained": (
            utils.count("iApaLsSession.GetAllApps( 0 )") == 1
            and utils.count("iApaLsSession.GetNextApp( appInfo )") == 1
            and scanner.count("UpdateApplicationItemL(") >= 2
        ),
        "no blocking or fake item": (
            "User::After" not in scanner
            and "CActiveSchedulerWait" not in scanner
            and "AppendL( htcleo" not in scanner
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS returned AppArc retry verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    utils_path = component / "srvsrc/menusrvengutils.cpp"
    utils_header_path = component / "srvinc/menusrvengutils.h"
    scanner_path = component / "srvsrc/menusrvappscanner.cpp"
    scanner_header_path = component / "srvinc/menusrvappscanner.h"
    paths = (utils_path, utils_header_path, scanner_path, scanner_header_path)
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"missing MenuContent source: {path}")

    utils = utils_path.read_text(encoding="latin-1")
    utils_header = utils_header_path.read_text(encoding="latin-1")
    scanner = scanner_path.read_text(encoding="latin-1")
    scanner_header = scanner_header_path.read_text(encoding="latin-1")
    if MARKER not in utils:
        utils, utils_header, scanner, scanner_header = install(
            utils, utils_header, scanner, scanner_header
        )
    verify(utils, utils_header, scanner, scanner_header)
    utils_path.write_text(utils, encoding="latin-1")
    utils_header_path.write_text(utils_header, encoding="latin-1")
    scanner_path.write_text(scanner, encoding="latin-1")
    scanner_header_path.write_text(scanner_header, encoding="latin-1")
    print("HTCLEO_MCS_APPARC_RETURNED_RETRY=return-status-before-mutation")


if __name__ == "__main__":
    main()
