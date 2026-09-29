#!/usr/bin/env python3
"""Synchronously consume GetList without post-callback collector access."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HN_SYNC_DIRECT_SAFE_TAIL_V1"
QUEUED_MARKER = "HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1"
SIGNAL_MARKER = "HTCLEO_HN_SYNC_OWNED_SIGNAL_CONSUME_V1"


START_OLD = r'''void CHnQueryResultCollector::StartAsynchL(
        MHnQueryResultCollectorNotification* aNotification )
    {
    HtcleoMdQueryLog(0x4D440430u, KErrNone,
        (TUint32)iQueries.Count());
    __ASSERT_DEBUG( aNotification , User::Panic( KMatrixPanic , 0) );
    iNotification = aNotification;
    ResetL();
    HtcleoMdQueryLog(0x4D440431u, KErrNone,
        (TUint32)iQueryIterator);
    HtcleoMdQueryLog(0x4D440435u, KErrNone, 0u);
    if( iQueryIterator < iQueries.Count())
        {
        HtcleoMdQueryLog(0x4D440432u, KErrNone,
            (TUint32)iQueryIterator);
        ExecQueryAsynchL();
        HtcleoMdQueryLog(0x4D440433u, KErrNone,
            (TUint32)iQueryIterator);
        }
    else
        {
        HtcleoMdQueryLog(0x4D440434u, KErrNone, 0u);
        iNotification->ResultsCollectedL( iResults );
        }
    HtcleoMdQueryLog(0x4D440435u, KErrNone, 0u);
    }'''


START_NEW = r'''void CHnQueryResultCollector::StartAsynchL(
        MHnQueryResultCollectorNotification* aNotification )
    {
    HtcleoMdQueryLog(0x4D440430u, KErrNone,
        (TUint32)iQueries.Count());
    __ASSERT_DEBUG( aNotification , User::Panic( KMatrixPanic , 0) );
    iNotification = aNotification;
    ResetL();
    HtcleoMdQueryLog(0x4D440431u, KErrNone,
        (TUint32)iQueryIterator);
    if( iQueryIterator < iQueries.Count())
        {
        // HTCLEO_HN_SYNC_DIRECT_SAFE_TAIL_V1
        // Log every caller-side stage before a synchronous completion can
        // notify model observers.  Nothing in this frame touches the
        // collector after ExecQueryAsynchL returns.
        HtcleoMdQueryLog(0x4D440432u, KErrNone,
            (TUint32)iQueryIterator);
        HtcleoMdQueryLog(0x4D440433u, KErrNone,
            (TUint32)iQueryIterator);
        ExecQueryAsynchL();
        return;
        }
    else
        {
        HtcleoMdQueryLog(0x4D440434u, KErrNone, 0u);
        iNotification->ResultsCollectedL( iResults );
        }
    }'''


LEGACY_QUERY_435 = r'''        HtcleoMdQueryLog(0x4D440433u, KErrNone,
            (TUint32)iQueryIterator);
        HtcleoMdQueryLog(0x4D440435u, KErrNone, 0u);
        ExecQueryAsynchL();'''


UNIQUE_QUERY_TAIL = r'''        HtcleoMdQueryLog(0x4D440433u, KErrNone,
            (TUint32)iQueryIterator);
        ExecQueryAsynchL();'''


LEGACY_FINAL_435 = r'''        iNotification->ResultsCollectedL( iResults );
        }
    HtcleoMdQueryLog(0x4D440435u, KErrNone, 0u);
    }'''


UNIQUE_FINAL_TAIL = r'''        iNotification->ResultsCollectedL( iResults );
        }
    }'''


PRE_BRANCH_ANCHOR = r'''    HtcleoMdQueryLog(0x4D440431u, KErrNone,
        (TUint32)iQueryIterator);
    if( iQueryIterator < iQueries.Count())'''


PRE_BRANCH_WITH_435 = r'''    HtcleoMdQueryLog(0x4D440431u, KErrNone,
        (TUint32)iQueryIterator);
    HtcleoMdQueryLog(0x4D440435u, KErrNone, 0u);
    if( iQueryIterator < iQueries.Count())'''


RETRY_OLD = r'''        iCurrentQueryResults->Reset();
        ExecQueryAsynchL();
        HtcleoMdQueryLog(0x4D440463u, KErrNone,
            (TUint32)iQueryIterator);
        return;'''


RETRY_NEW = r'''        iCurrentQueryResults->Reset();
        // HTCLEO_HN_SYNC_DIRECT_SAFE_TAIL_V1
        // The recursive synchronous completion may notify observers, so emit
        // the final retry breadcrumb before entering it and do no work after.
        HtcleoMdQueryLog(0x4D440463u, KErrNone,
            (TUint32)iQueryIterator);
        ExecQueryAsynchL();
        return;'''


QUEUED_OLD = r'''    // HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1
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
        }'''


DIRECT_NEW = r'''    // HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1
    // HTCLEO_HN_SYNC_DIRECT_SAFE_TAIL_V1
    // This early boot scheduler does not dispatch even a correctly requeued
    // completion.  Consume only an already-completed MatrixMenu request here;
    // the caller and retry frames have no collector access after this call.
    if (RProcess().SecureId().iId == 0x101F4CD2u
            && iStatus != KRequestPending)
        {
        HtcleoMdQueryLog(0x4D440466u, iStatus.Int(),
            (TUint32)iQueryIterator);
        RunL();
        return;
        }'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    text = replace_once(text, START_OLD, START_NEW, "StartAsynch safe tail")
    text = replace_once(text, RETRY_OLD, RETRY_NEW, "retry safe tail")
    return replace_once(text, QUEUED_OLD, DIRECT_NEW, "direct completed result")


def consume_completed_signal(text: str) -> str:
    if SIGNAL_MARKER in text:
        return text
    return replace_once(text,
        "        HtcleoMdQueryLog(0x4D440466u, iStatus.Int(),\n"
        "            (TUint32)iQueryIterator);\n"
        "        RunL();",
        "        HtcleoMdQueryLog(0x4D440466u, iStatus.Int(),\n"
        "            (TUint32)iQueryIterator);\n"
        "        // HTCLEO_HN_SYNC_OWNED_SIGNAL_CONSUME_V1\n"
        "        // ExecuteL's callback completed this request with\n"
        "        // User::RequestComplete. Direct RunL consumes the result but\n"
        "        // not its thread semaphore credit. Retire exactly that one\n"
        "        // completed request before running the existing safe tail;\n"
        "        // pending requests still use the normal SetActive path.\n"
        "        User::WaitForRequest(iStatus);\n"
        "        RunL();",
        "consume the completed request's signal before direct dispatch")


def verify(text: str) -> None:
    checks = {
        "markers": text.count(MARKER) == 3 and text.count(QUEUED_MARKER) == 1,
        "direct completed result": (
            text.count("iStatus != KRequestPending") == 1
            and text.count("RunL();") == 1
            and "User::RequestComplete(htcleoQueuedStatus" not in text
        ),
        "owned completion signal": (
            text.count(SIGNAL_MARKER) == 1
            and text.count("User::WaitForRequest(iStatus);") == 1
            and "User::WaitForRequest(iStatus);\n        RunL();\n        return;" in text
            and text.index("iStatus != KRequestPending")
                < text.index(SIGNAL_MARKER)
                < text.index("User::WaitForRequest(iStatus);")
        ),
        "safe caller tail": (
            text.count("ExecQueryAsynchL();\n        return;") == 2
            and text.count("0x4D440435u") == 1
            and text.index("0x4D440435u") < text.index(MARKER)
            and text.index(MARKER)
            < text.index("ExecQueryAsynchL();", text.index(MARKER))
        ),
        "retry remains bounded": (
            text.count("iHtcleoReadyRetryIssued = ETrue") == 1
            and text.count("ExecQueryAsynchL();") == 3
        ),
        "stages retained": all(
            text.count(f"0x4D440{stage:03X}u") == 1
            for stage in range(0x460, 0x467)
        ),
        "no timer fake": all(
            token not in text for token in ("RTimer", "User::After", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HN synchronous safe-tail verification failed: " + ", ".join(failed))


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
    if MARKER in text and text.count("0x4D440435u") == 2:
        text = replace_once(text, LEGACY_QUERY_435, UNIQUE_QUERY_TAIL,
            "remove query-path duplicate 435")
        text = replace_once(text, LEGACY_FINAL_435, UNIQUE_FINAL_TAIL,
            "remove final duplicate 435")
        text = replace_once(text, PRE_BRANCH_ANCHOR, PRE_BRANCH_WITH_435,
            "move 435 before completion")
    if MARKER not in text:
        text = install(text)
    text = consume_completed_signal(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_HN_SYNC_RESULT="
        "direct-runl-safe-caller-and-retry-tail-460-466"
    )
    print("HTCLEO_HN_SYNC_COMPLETION_SIGNAL=owned-completed-status-wait-before-direct-runl")


if __name__ == "__main__":
    main()
