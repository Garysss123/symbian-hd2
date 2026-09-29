#!/usr/bin/env python3
"""Replace the failed MCS generation timer with a real P&S ready signal."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1"
GENERATION_MARKER = "HTCLEO_MCS_HN_READY_GENERATION_V1"
REQUEST_GUARD_MARKER = "HTCLEO_HN_READY_GENERATION_REQUEST_GUARD_V1"
COMMIT_REQUERY_MARKER = "HTCLEO_MCS_HN_COMMIT_REQUERY_V1"


MCS_START = "        // HTCLEO_MCS_HN_READY_GENERATION_V1\n"
MCS_END = r'''        HtcleoMcsLog(0x4D43016Cu, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
'''


MCS_REPLACEMENT = r'''        // HTCLEO_MCS_HN_READY_GENERATION_V1
        // The PID-generation/timer policy is superseded by the following
        // real app-count signal.  MenuContent runs as SID 0x200113DD, while
        // 0x200113DB is only the DLL UID and cannot own a server property.
        // HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        const TInt htcleoReadyResult = RProperty::Set(
            htcleoReadyCategory, htcleoReadyKey, htcleoAppCount);
        HtcleoMcsLog(0x4D43016Cu, htcleoReadyResult,
            (TUint32)htcleoAppCount);
'''


HN_SETUP_ANCHOR = r'''        TBool htcleoNotifySent = EFalse;
        for (int i=0; i<Count(); i++)'''


HN_SETUP_REPLACEMENT = r'''        // HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1
        // Define the property in MatrixMenu's own SID category before a LIW
        // request can start MenuContent.  Always-pass policies permit the
        // real 0x200113DD server to publish its completed app count.
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        const TSecurityPolicy htcleoReadyPolicy(
            TSecurityPolicy::EAlwaysPass);
        TInt htcleoReadySetup = RProperty::Define(
            htcleoReadyKey, RProperty::EInt,
            htcleoReadyPolicy, htcleoReadyPolicy);
        if (htcleoReadySetup == KErrAlreadyExists)
            {
            htcleoReadySetup = KErrNone;
            }
        HtcleoMdNotifyLog(0x4D440512u, htcleoReadySetup,
            (TUint32)Count());
        TBool htcleoNotifySent = EFalse;
        for (int i=0; i<Count(); i++)'''


HN_START = "        // HTCLEO_MCS_HN_READY_GENERATION_V1\n"
HN_END = r'''        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;
'''


HN_REPLACEMENT = r'''        // HTCLEO_MCS_HN_READY_GENERATION_V1
        // The generation-two RTimer wait is superseded on HTCLEO.
        // HTCLEO_HN_READY_GENERATION_REQUEST_GUARD_V1
        if (!htcleoNotifySent)
            {
            HtcleoMdNotifyLog(0x4D440511u, KErrNone, (TUint32)Count());
            return;
            }
        // HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1
        // RequestNotifyL has now started the real provider.  If its first
        // 12-app scan is not already complete, subscribe once and let the
        // server's property Set wake this thread.  No timer or fake refresh.
        TInt htcleoReadyValue = 0;
        TInt htcleoReadyResult = RProperty::Get(
            htcleoReadyCategory, htcleoReadyKey, htcleoReadyValue);
        HtcleoMdNotifyLog(0x4D44050Eu, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        if (htcleoReadyResult == KErrNone && htcleoReadyValue == 0)
            {
            RProperty htcleoReadyProperty;
            htcleoReadyResult = htcleoReadyProperty.Attach(
                htcleoReadyCategory, htcleoReadyKey);
            if (htcleoReadyResult == KErrNone)
                {
                TRequestStatus htcleoReadyStatus;
                htcleoReadyProperty.Subscribe(htcleoReadyStatus);
                htcleoReadyResult = htcleoReadyProperty.Get(htcleoReadyValue);
                const TBool htcleoWaitForReady =
                    htcleoReadyResult == KErrNone && htcleoReadyValue == 0;
                if (!htcleoWaitForReady)
                    {
                    htcleoReadyProperty.Cancel();
                    }
                User::WaitForRequest(htcleoReadyStatus);
                if (htcleoWaitForReady)
                    {
                    htcleoReadyResult = htcleoReadyStatus.Int();
                    if (htcleoReadyResult == KErrNone)
                        {
                        htcleoReadyResult =
                            htcleoReadyProperty.Get(htcleoReadyValue);
                        }
                    }
                htcleoReadyProperty.Close();
                }
            }
        HtcleoMdNotifyLog(0x4D44050Fu, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        HtcleoMdNotifyLog(0x4D440510u, KErrNone, (TUint32)Count());
        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;
'''


def replace_block(text: str, start: str, end: str, replacement: str, label: str) -> str:
    start_count = text.count(start)
    end_count = text.count(end)
    if start_count != 1 or end_count != 1:
        raise SystemExit(
            f"{label}: expected one block, starts={start_count} ends={end_count}"
        )
    first = text.index(start)
    last = text.index(end, first) + len(end)
    return text[:first] + replacement + text[last:]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(mcs: str, hn: str) -> tuple[str, str]:
    mcs = replace_block(mcs, MCS_START, MCS_END, MCS_REPLACEMENT, "MCS signal")
    hn = replace_once(hn, HN_SETUP_ANCHOR, HN_SETUP_REPLACEMENT, "HN setup")
    hn = replace_block(hn, HN_START, HN_END, HN_REPLACEMENT, "HN wait")
    return mcs, hn


def verify(mcs: str, hn: str) -> None:
    if COMMIT_REQUERY_MARKER in mcs:
        commit_checks = {
            "layer markers": (
                mcs.count(MARKER) == 1
                and hn.count(MARKER) == 2
                and mcs.count(COMMIT_REQUERY_MARKER) == 1
            ),
            "scanner signal deferred": (
                mcs.count("0x4D43016Cu, KErrNotReady") == 1
                and "RProperty::Set(\n            htcleoReadyCategory" not in mcs
            ),
            "MatrixMenu property retained": (
                hn.count("TSecurityPolicy::EAlwaysPass") == 1
                and hn.count("htcleoReadyProperty.Subscribe(htcleoReadyStatus)") == 1
            ),
        }
        failed = [name for name, ok in commit_checks.items() if not ok]
        if failed:
            raise SystemExit(
                "commit-requery property verification failed: " + ", ".join(failed)
            )
        return
    checks = {
        "layer markers": (
            mcs.count(GENERATION_MARKER) == 1
            and hn.count(GENERATION_MARKER) == 1
            and hn.count(REQUEST_GUARD_MARKER) == 1
            and mcs.count(MARKER) == 1
            and hn.count(MARKER) == 2
        ),
        "MatrixMenu-owned property": (
            mcs.count("0x101F4CD2") == 1
            and hn.count("0x101F4CD2") >= 2
            and mcs.count("0x7F4D4301u") == 1
            and hn.count("0x7F4D4301u") == 1
        ),
        "always-pass setup": (
            hn.count("TSecurityPolicy::EAlwaysPass") == 1
            and hn.count("RProperty::Define(\n            htcleoReadyKey") == 1
        ),
        "real app-count publisher": (
            mcs.count("RProperty::Set(\n            htcleoReadyCategory") == 1
            and mcs.count("(TUint32)htcleoAppCount") >= 2
            and "htcleoGeneration" not in mcs
        ),
        "single property wait": (
            hn.count("htcleoReadyProperty.Subscribe(htcleoReadyStatus)") == 1
            and hn.count("User::WaitForRequest(htcleoReadyStatus)") == 1
            and hn.count("htcleoReadyProperty.Cancel()") == 1
            and "RTimer htcleoReadyTimer" not in hn
            and "htcleoReadyAttempts" not in hn
        ),
        "HN stages": all(
            hn.count(f"0x4D440{stage:03X}u") == 1
            for stage in (0x50E, 0x50F, 0x510, 0x511, 0x512)
        ),
        "no synthetic data": (
            "AppendL( htcleo" not in mcs
            and "AppendL( htcleo" not in hn
            and "HtcleoInitialRefreshL" not in hn
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MCS/HN property-subscribe verification failed: " + ", ".join(failed))


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
            raise SystemExit(f"missing property-subscribe source: {path}")
    mcs = mcs_path.read_text(encoding="latin-1")
    hn = hn_path.read_text(encoding="latin-1")
    if MARKER not in mcs or MARKER not in hn:
        mcs, hn = install(mcs, hn)
    verify(mcs, hn)
    mcs_path.write_text(mcs, encoding="latin-1")
    hn_path.write_text(hn, encoding="latin-1")
    if COMMIT_REQUERY_MARKER in mcs:
        print(
            "HTCLEO_MCS_HN_READY_SIGNAL="
            "matrixmenu-owned-alwayspass-commit-generation-query-retry-no-timer"
        )
    else:
        print(
            "HTCLEO_MCS_HN_READY_SIGNAL="
            "matrixmenu-owned-alwayspass-appcount-subscribe-no-timer"
        )


if __name__ == "__main__":
    main()
