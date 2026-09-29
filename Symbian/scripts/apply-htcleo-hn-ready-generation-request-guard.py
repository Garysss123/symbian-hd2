#!/usr/bin/env python3
"""Wait for MCS readiness only after HN sent a real notify request."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HN_READY_GENERATION_REQUEST_GUARD_V1"
READY_MARKER = "HTCLEO_MCS_HN_READY_GENERATION_V1"
SUPERSEDED_MARKER = "HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1"


LOOP_ANCHOR = r'''    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        for (int i=0; i<Count(); i++)'''


LOOP_PATCHED = r'''    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        TBool htcleoNotifySent = EFalse;
        for (int i=0; i<Count(); i++)'''


SUCCESS_ANCHOR = r'''            User::LeaveIfError(htcleoNotifyError);
            HtcleoMdNotifyLog(0x4D440504u, KErrNone, (TUint32)i);'''


SUCCESS_PATCHED = r'''            User::LeaveIfError(htcleoNotifyError);
            htcleoNotifySent = ETrue;
            HtcleoMdNotifyLog(0x4D440504u, KErrNone, (TUint32)i);'''


WAIT_ANCHOR = r'''        // invoked reentrantly from this notification stack.
        const TUid htcleoReadyCategory = { 0x200113DB };'''


WAIT_PATCHED = r'''        // invoked reentrantly from this notification stack.
        // HTCLEO_HN_READY_GENERATION_REQUEST_GUARD_V1
        // Count can be zero here, and every attempted request can also have
        // been deferred after KErrServerTerminated.  In either case no LIW
        // provider was started, so waiting for its property would deadlock
        // before CHnQueryResultCollector can issue the real model query.
        if (!htcleoNotifySent)
            {
            HtcleoMdNotifyLog(0x4D440511u, KErrNone, (TUint32)Count());
            return;
            }
        const TUid htcleoReadyCategory = { 0x200113DB };'''


LEGACY_DUPLICATE_505 = r'''            HtcleoMdNotifyLog(0x4D440511u, KErrNone, (TUint32)Count());
            HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
            return;'''


UNIQUE_511 = r'''            HtcleoMdNotifyLog(0x4D440511u, KErrNone, (TUint32)Count());
            return;'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    text = replace_once(text, LOOP_ANCHOR, LOOP_PATCHED, "notify success flag")
    text = replace_once(text, SUCCESS_ANCHOR, SUCCESS_PATCHED, "notify success set")
    return replace_once(text, WAIT_ANCHOR, WAIT_PATCHED, "readiness request guard")


def verify(text: str) -> None:
    if SUPERSEDED_MARKER in text:
        superseded_checks = {
            "ready lineage retained": text.count(READY_MARKER) == 1,
            "request guard retained": (
                text.count(MARKER) == 1
                and text.count("if (!htcleoNotifySent)") == 1
                and text.count("0x4D440511u") == 1
            ),
            "property wait supersedes timer": (
                text.count("htcleoReadyProperty.Subscribe(htcleoReadyStatus)") == 1
                and text.count("User::WaitForRequest(htcleoReadyStatus)") == 1
                and "RTimer htcleoReadyTimer" not in text
            ),
        }
        failed = [name for name, ok in superseded_checks.items() if not ok]
        if failed:
            raise SystemExit(
                "superseding HN request-guard verification failed: "
                + ", ".join(failed)
            )
        return
    checks = {
        "ready generation retained": text.count(READY_MARKER) == 1,
        "request guard marker": text.count(MARKER) == 1,
        "success flag": (
            text.count("TBool htcleoNotifySent = EFalse;") == 1
            and text.count("htcleoNotifySent = ETrue;") == 1
            and text.count("if (!htcleoNotifySent)") == 1
        ),
        "skip stage": text.count("0x4D440511u") == 1,
        "legacy stage remains unique": text.count("0x4D440505u") == 1,
        "bounded wait retained": (
            text.count("htcleoReadyAttempts < 120") == 1
            and text.count("User::WaitForRequest(htcleoDelayStatus)") == 1
        ),
        "real query retained": (
            "HtcleoInitialRefreshL" not in text
            and "AppendL( htcleo" not in text
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HN request-guard verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src/hnmdnotifyrequests.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing HN notify source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER in text and LEGACY_DUPLICATE_505 in text:
        text = replace_once(
            text,
            LEGACY_DUPLICATE_505,
            UNIQUE_511,
            "remove duplicate legacy 505",
        )
    if MARKER not in text:
        text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_HN_READY_REQUEST_GUARD=no-success-skip-511-success-generation-wait")


if __name__ == "__main__":
    main()
