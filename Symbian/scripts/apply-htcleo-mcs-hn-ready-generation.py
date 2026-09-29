#!/usr/bin/env python3
"""Gate HN's first real query on two successful MenuContent process scans."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_HN_READY_GENERATION_V1"
SUPERSEDED_MARKER = "HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1"
COMMIT_REQUERY_MARKER = "HTCLEO_MCS_HN_COMMIT_REQUERY_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


MCS_INCLUDE = "#include <mcsmenuutils.h>\n"
MCS_INCLUDE_PATCHED = r'''#include <mcsmenuutils.h>
#include <e32property.h>
'''


MCS_SUCCESS = r'''    if (aErr == KErrNone && htcleoAppCount > 0)
        {
        iHtcleoApaRetryCount = 0;
        }
    HtcleoMcsLog(0x4D430167u, htcleoRetryReason,
        (TUint32)htcleoAppCount);'''


MCS_SUCCESS_PATCHED = r'''    if (aErr == KErrNone && htcleoAppCount > 0)
        {
        iHtcleoApaRetryCount = 0;
        // HTCLEO_MCS_HN_READY_GENERATION_V1
        // Count successful scanner processes, not operations.  The first
        // process publishes generation one and the recovered replacement
        // process publishes generation two with its PID in the low word.
        const TUid htcleoReadyCategory = { 0x200113DB };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        TInt htcleoReadyResult = RProperty::Define(
            htcleoReadyCategory, htcleoReadyKey, RProperty::EInt);
        if (htcleoReadyResult == KErrAlreadyExists)
            {
            htcleoReadyResult = KErrNone;
            }
        TInt htcleoReadyValue = 0;
        if (htcleoReadyResult == KErrNone)
            {
            const TInt htcleoReadyRead = RProperty::Get(
                htcleoReadyCategory, htcleoReadyKey, htcleoReadyValue);
            if (htcleoReadyRead != KErrNone)
                {
                htcleoReadyValue = 0;
                }
            const TUint32 htcleoPid =
                (TUint32)RProcess().Id().Id() & 0xFFFFu;
            TUint32 htcleoGeneration =
                ((TUint32)htcleoReadyValue >> 16) & 0x7FFFu;
            if (((TUint32)htcleoReadyValue & 0xFFFFu) != htcleoPid)
                {
                ++htcleoGeneration;
                }
            htcleoReadyValue = (TInt)((htcleoGeneration << 16) | htcleoPid);
            htcleoReadyResult = RProperty::Set(
                htcleoReadyCategory, htcleoReadyKey, htcleoReadyValue);
            }
        HtcleoMcsLog(0x4D43016Cu, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        }
    HtcleoMcsLog(0x4D430167u, htcleoRetryReason,
        (TUint32)htcleoAppCount);'''


HN_INCLUDE = r'''#include <e32base.h>

#include <f32file.h>'''


HN_INCLUDE_PATCHED = r'''#include <e32base.h>
#include <e32property.h>

#include <f32file.h>'''


HN_SENT = r'''        iSent = ETrue;
        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;'''


HN_SENT_PATCHED = r'''        iSent = ETrue;
        // HTCLEO_MCS_HN_READY_GENERATION_V1
        // The CAsyncCallBack never dispatches on this hardware.  Wait before
        // returning to CHnMdItem's original first query, so that query itself
        // reads the recovered real 12-App MCS model and no reevaluation is
        // invoked reentrantly from this notification stack.
        const TUid htcleoReadyCategory = { 0x200113DB };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        TInt htcleoReadyValue = 0;
        TInt htcleoReadyResult = KErrNotReady;
        TInt htcleoReadyAttempts = 0;
        RTimer htcleoReadyTimer;
        const TInt htcleoTimerResult = htcleoReadyTimer.CreateLocal();
        HtcleoMdNotifyLog(0x4D44050Eu, htcleoTimerResult, 0u);
        if (htcleoTimerResult == KErrNone)
            {
            for (htcleoReadyAttempts = 0;
                    htcleoReadyAttempts < 120; ++htcleoReadyAttempts)
                {
                htcleoReadyResult = RProperty::Get(
                    htcleoReadyCategory, htcleoReadyKey, htcleoReadyValue);
                if (htcleoReadyResult == KErrNone
                        && (((TUint32)htcleoReadyValue >> 16) & 0x7FFFu) >= 2u)
                    {
                    break;
                    }
                TRequestStatus htcleoDelayStatus;
                htcleoReadyTimer.After(htcleoDelayStatus, 25000);
                User::WaitForRequest(htcleoDelayStatus);
                }
            htcleoReadyTimer.Close();
            if (htcleoReadyResult == KErrNone
                    && (((TUint32)htcleoReadyValue >> 16) & 0x7FFFu) < 2u)
                {
                htcleoReadyResult = KErrTimedOut;
                }
            }
        else
            {
            htcleoReadyResult = htcleoTimerResult;
            }
        HtcleoMdNotifyLog(0x4D44050Fu, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        HtcleoMdNotifyLog(0x4D440510u, KErrNone,
            (TUint32)htcleoReadyAttempts);
        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;'''


def install(mcs: str, hn: str) -> tuple[str, str]:
    if "#include <e32property.h>" not in mcs:
        mcs = replace_once(
            mcs, MCS_INCLUDE, MCS_INCLUDE_PATCHED, "MCS property include"
        )
    mcs = replace_once(mcs, MCS_SUCCESS, MCS_SUCCESS_PATCHED, "MCS ready publish")
    hn = replace_once(hn, HN_INCLUDE, HN_INCLUDE_PATCHED, "HN property include")
    hn = replace_once(hn, HN_SENT, HN_SENT_PATCHED, "HN first-query gate")
    return mcs, hn


def verify(mcs: str, hn: str) -> None:
    if COMMIT_REQUERY_MARKER in mcs:
        commit_checks = {
            "commit marker": mcs.count(COMMIT_REQUERY_MARKER) == 1,
            "lineage markers": mcs.count(MARKER) == 1 and hn.count(MARKER) == 1,
            "scanner signal deferred": (
                mcs.count("0x4D43016Cu, KErrNotReady") == 1
                and "RProperty::Set(\n            htcleoReadyCategory" not in mcs
            ),
            "HN property subscription retained": (
                hn.count("htcleoReadyProperty.Subscribe(htcleoReadyStatus)") == 1
                and hn.count("User::WaitForRequest(htcleoReadyStatus)") == 1
            ),
        }
        failed = [name for name, ok in commit_checks.items() if not ok]
        if failed:
            raise SystemExit(
                "commit-requery MCS/HN ready verification failed: "
                + ", ".join(failed)
            )
        return
    if SUPERSEDED_MARKER in mcs or SUPERSEDED_MARKER in hn:
        superseded_checks = {
            "superseding markers": (
                mcs.count(SUPERSEDED_MARKER) == 1
                and hn.count(SUPERSEDED_MARKER) == 2
            ),
            "lineage markers": mcs.count(MARKER) == 1 and hn.count(MARKER) == 1,
            "app-count signal": (
                mcs.count("RProperty::Set(\n            htcleoReadyCategory") == 1
                and "htcleoGeneration" not in mcs
            ),
            "property subscription": (
                hn.count("htcleoReadyProperty.Subscribe(htcleoReadyStatus)") == 1
                and hn.count("User::WaitForRequest(htcleoReadyStatus)") == 1
                and "RTimer htcleoReadyTimer" not in hn
            ),
        }
        failed = [name for name, ok in superseded_checks.items() if not ok]
        if failed:
            raise SystemExit(
                "superseding MCS/HN ready verification failed: " + ", ".join(failed)
            )
        return
    checks = {
        "markers": mcs.count(MARKER) == 1 and hn.count(MARKER) == 1,
        "property includes": (
            mcs.count("#include <e32property.h>") >= 1
            and hn.count("#include <e32property.h>") == 1
        ),
        "shared identity": (
            mcs.count("0x200113DB") == 1
            and hn.count("0x200113DB") == 1
            and mcs.count("0x7F4D4301u") == 1
            and hn.count("0x7F4D4301u") == 1
        ),
        "process generation": (
            mcs.count("RProcess().Id().Id()") == 1
            and mcs.count("htcleoGeneration << 16") == 1
            and mcs.count("0x4D43016Cu") == 1
        ),
        "bounded synchronous wait": (
            hn.count("htcleoReadyAttempts < 120") == 1
            and hn.count("htcleoReadyTimer.After(htcleoDelayStatus, 25000)") == 1
            and hn.count("User::WaitForRequest(htcleoDelayStatus)") == 1
            and "User::After" not in hn
        ),
        "HN stages": all(
            hn.count(f"0x4D440{stage:03X}u") == 1
            for stage in range(0x50E, 0x511)
        ),
        "real first query retained": (
            hn.count("iSent = ETrue;") == 2
            and mcs.count("iSrvEngUtils.GetAppItemsL().Count()") >= 1
            and "AppendL( htcleo" not in mcs
            and "AppendL( htcleo" not in hn
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS/HN ready generation verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    mcs_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/menusrvappscanner.cpp"
    )
    hn_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src/hnmdnotifyrequests.cpp"
    )
    for path in (mcs_path, hn_path):
        if not path.is_file():
            raise SystemExit(f"missing ready-generation source: {path}")
    mcs = mcs_path.read_text(encoding="latin-1")
    hn = hn_path.read_text(encoding="latin-1")
    if MARKER not in mcs:
        mcs, hn = install(mcs, hn)
    verify(mcs, hn)
    mcs_path.write_text(mcs, encoding="latin-1")
    hn_path.write_text(hn, encoding="latin-1")
    if COMMIT_REQUERY_MARKER in mcs:
        print("HTCLEO_MCS_HN_READY_GENERATION=menueng-commit-532")
    elif SUPERSEDED_MARKER in mcs:
        print("HTCLEO_MCS_HN_READY_GENERATION=retired-by-property-subscribe")
    else:
        print("HTCLEO_MCS_HN_READY_GENERATION=16C-50E-510-two-process-real-query")


if __name__ == "__main__":
    main()
