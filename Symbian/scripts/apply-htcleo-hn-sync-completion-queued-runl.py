#!/usr/bin/env python3
"""Requeue a MatrixMenu query completed before CActive::SetActive()."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1"
SYNC_MARKER = "HTCLEO_HN_GETLIST_SYNCHRONOUS_V1"
SAFE_TAIL_MARKER = "HTCLEO_HN_SYNC_DIRECT_SAFE_TAIL_V1"


ANCHOR = r'''    ExecQueryL( iQueries.Query( iQueryIterator ) );
    HtcleoMdQueryLog(0x4D440443u, KErrNone,
        (TUint32)iQueryIterator);
    SetActive();
    HtcleoMdQueryLog(0x4D440444u, KErrNone,
        (TUint32)iQueryIterator);'''


PATCHED = r'''    ExecQueryL( iQueries.Query( iQueryIterator ) );
    HtcleoMdQueryLog(0x4D440443u, KErrNone,
        (TUint32)iQueryIterator);
    // HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1
    // Synchronous GetList can complete iStatus before this caller arms its
    // CActive.  Requeue that result only after SetActive so RunL executes at
    // the normal scheduler boundary and cannot reenter the current EvaluateL.
    if (RProcess().SecureId().iId == 0x101F4CD2u
            && iStatus != KRequestPending)
        {
        const TInt htcleoCompletedResult = iStatus.Int();
        iStatus = KRequestPending;
        SetActive();
        TRequestStatus* htcleoQueuedStatus = &iStatus;
        User::RequestComplete(htcleoQueuedStatus, htcleoCompletedResult);
        HtcleoMdQueryLog(0x4D440466u, htcleoCompletedResult,
            (TUint32)iQueryIterator);
        return;
        }
    SetActive();
    HtcleoMdQueryLog(0x4D440444u, KErrNone,
        (TUint32)iQueryIterator);'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(text: str) -> None:
    if SAFE_TAIL_MARKER in text:
        safe_checks = {
            "lineage marker": text.count(MARKER) == 1,
            "safe-tail markers": text.count(SAFE_TAIL_MARKER) == 3,
            "direct completed result": (
                text.count("iStatus != KRequestPending") == 1
                and text.count("RunL();") == 1
                and "User::RequestComplete(htcleoQueuedStatus" not in text
            ),
            "stage": text.count("0x4D440466u") == 1,
        }
        failed = [name for name, ok in safe_checks.items() if not ok]
        if failed:
            raise SystemExit(
                "superseding HN safe-tail verification failed: " + ", ".join(failed)
            )
        return
    checks = {
        "marker": text.count(MARKER) == 1,
        "synchronous GetList retained": text.count(SYNC_MARKER) == 1,
        "completed-before-active guard": (
            text.count("iStatus != KRequestPending") == 1
            and text.count("iStatus = KRequestPending;") == 1
            and text.count("User::RequestComplete(htcleoQueuedStatus") == 1
            and text.count("RunL();") == 0
        ),
        "active before requeue": (
            text.index("SetActive();", text.index(MARKER))
            < text.index("User::RequestComplete(htcleoQueuedStatus")
        ),
        "stage": text.count("0x4D440466u") == 1,
        "bounded retry retained": (
            text.count("iHtcleoReadyRetryIssued = ETrue") == 1
            and text.count("ExecQueryAsynchL();") == 3
        ),
        "no timer fake or inline reentry": all(
            token not in text
            for token in ("RTimer", "User::After", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HN queued RunL verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src/hnqueryresultcollector.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing HN query source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        text = replace_once(text, ANCHOR, PATCHED, "pre-SetActive completion")
    verify(text)
    path.write_text(text, encoding="latin-1")
    if SAFE_TAIL_MARKER in text:
        print("HTCLEO_HN_SYNC_COMPLETION=superseded-by-direct-safe-tail")
    else:
        print(
            "HTCLEO_HN_SYNC_COMPLETION="
            "pre-setactive-requeue-466-pending-stock"
        )


if __name__ == "__main__":
    main()
