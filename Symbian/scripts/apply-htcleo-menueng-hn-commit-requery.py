#!/usr/bin/env python3
"""Publish committed MenuEng generations and retry one empty HN query."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_HN_COMMIT_REQUERY_V1"
READY_MARKER = "HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1"


SCANNER_START = "        // HTCLEO_MCS_HN_READY_GENERATION_V1\n"
SCANNER_END = r'''        HtcleoMcsLog(0x4D43016Cu, htcleoReadyResult,
            (TUint32)htcleoAppCount);
'''


SCANNER_REPLACEMENT = r'''        // HTCLEO_MCS_HN_READY_GENERATION_V1
        // HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1
        // HTCLEO_MCS_HN_COMMIT_REQUERY_V1
        // A scanner count is process-local and precedes MenuEng's real DOM
        // commit.  Keep the count as evidence but let stage 0532 publish only
        // after CompleteCurrentOperation has flushed real notifications.
        HtcleoMcsLog(0x4D43016Cu, KErrNotReady,
            (TUint32)htcleoAppCount);
'''


MENUENG_INCLUDE = "#include <sysutil.h>\n"
MENUENG_INCLUDE_PATCHED = "#include <sysutil.h>\n#include <e32property.h>\n"


MENUENG_COMMIT = r'''        CompleteCurrentOperation( KErrNone );
        HtcleoMenuEngLog(0x4D450531u, KErrNone,
            (TUint32)iOperations.Count());'''


MENUENG_COMMIT_PATCHED = r'''        CompleteCurrentOperation( KErrNone );
        HtcleoMenuEngLog(0x4D450531u, KErrNone,
            (TUint32)iOperations.Count());
        // HTCLEO_MCS_HN_COMMIT_REQUERY_V1
        // Every process owns a private RAM tree.  Publish a monotonically
        // increasing generation only after this process has committed its
        // real mutation and flushed the associated notifications.
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        TInt htcleoCommitGeneration = 0;
        TInt htcleoCommitResult = RProperty::Get(
            htcleoReadyCategory, htcleoReadyKey,
            htcleoCommitGeneration);
        if (htcleoCommitResult == KErrNone)
            {
            ++htcleoCommitGeneration;
            htcleoCommitResult = RProperty::Set(
                htcleoReadyCategory, htcleoReadyKey,
                htcleoCommitGeneration);
            }
        HtcleoMenuEngLog(0x4D450532u, htcleoCommitResult,
            (TUint32)htcleoCommitGeneration);'''


QUERY_INCLUDE = "#include <liwservicehandler.h>\n"
QUERY_INCLUDE_PATCHED = r'''#include <liwservicehandler.h>
#include <e32property.h>
'''


QUERY_GLOBAL_INCLUDE = '#include "hnmdservicecommand.h"\n'
QUERY_GLOBAL_INCLUDE_PATCHED = r'''#include "hnmdservicecommand.h"
#include "hnglobals.h"
'''


QUERY_CONSTRUCTOR = r'''CHnQueryResultCollector::CHnQueryResultCollector(
		const CHnMdQueries& aQueries ,
		const CLiwGenericParamList& aParams) : CActive ( EPriorityStandard ),
                                        	   iQueries( aQueries ),
                                        	   iParams( aParams )
	{
	}'''


QUERY_CONSTRUCTOR_PATCHED = r'''CHnQueryResultCollector::CHnQueryResultCollector(
		const CHnMdQueries& aQueries ,
		const CLiwGenericParamList& aParams) : CActive ( EPriorityStandard ),
                                        	   iQueries( aQueries ),
                                        	   iParams( aParams ),
                                           iHtcleoReadyRetryIssued( EFalse ),
                                           iHtcleoReadyGeneration( 0 )
	{
	}'''


QUERY_EXECUTE = r'''    HtcleoMdQueryLog(0x4D440459u, KErrNone, 0u);
    iSh->ExecuteL( *iCurrentQueryResults, iStatus );
    HtcleoMdQueryLog(0x4D44045Au, KErrNone, 0u);'''


QUERY_EXECUTE_PATCHED = r'''    HtcleoMdQueryLog(0x4D440459u, KErrNone, 0u);
    // HTCLEO_MCS_HN_COMMIT_REQUERY_V1
    if (RProcess().SecureId().iId == 0x101F4CD2u
            && !iHtcleoReadyRetryIssued)
        {
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        const TInt htcleoReadyRead = RProperty::Get(
            htcleoReadyCategory, htcleoReadyKey,
            iHtcleoReadyGeneration);
        HtcleoMdQueryLog(0x4D440464u, htcleoReadyRead,
            (TUint32)iHtcleoReadyGeneration);
        }
    iSh->ExecuteL( *iCurrentQueryResults, iStatus );
    HtcleoMdQueryLog(0x4D44045Au, KErrNone, 0u);'''


QUERY_RUNL = r'''void CHnQueryResultCollector::RunL()
    {
    if ( !iStatus.Int() )
        {
        HandleQueryResultsL();
        }

    if( NextQuery() )
        {
        ExecQueryAsynchL();
        }
    else
        {
        iNotification->ResultsCollectedL( iResults );
        }
    }'''


QUERY_RUNL_PATCHED = r'''void CHnQueryResultCollector::RunL()
    {
    // HTCLEO_MCS_HN_COMMIT_REQUERY_V1
    TInt htcleoReturnedItems = KErrNotFound;
    if (iStatus.Int() == KErrNone)
        {
        TInt htcleoReturnPosition = 0;
        const TLiwGenericParam* htcleoReturn =
            iCurrentQueryResults->FindFirst(
                htcleoReturnPosition, KReturnValue8());
        if (htcleoReturnPosition != KErrNotFound && htcleoReturn)
            {
            const CLiwList* htcleoReturnList =
                htcleoReturn->Value().AsList();
            if (htcleoReturnList)
                {
                htcleoReturnedItems = htcleoReturnList->Count();
                }
            }
        }
    HtcleoMdQueryLog(0x4D440460u, iStatus.Int(),
        (TUint32)htcleoReturnedItems);

    const TInt htcleoQueryStatus = iStatus.Int();
    const TBool htcleoRetryableStatus =
        htcleoQueryStatus == KErrServerTerminated
        || htcleoQueryStatus == KErrDisconnected
        || htcleoQueryStatus == KErrNotFound;
    if (RProcess().SecureId().iId == 0x101F4CD2u
            && !iHtcleoReadyRetryIssued
            && (htcleoReturnedItems == 0 || htcleoRetryableStatus))
        {
        iHtcleoReadyRetryIssued = ETrue;
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        TInt htcleoCurrentGeneration = 0;
        TInt htcleoReadyResult = RProperty::Get(
            htcleoReadyCategory, htcleoReadyKey,
            htcleoCurrentGeneration);
        HtcleoMdQueryLog(0x4D440461u, htcleoReadyResult,
            (TUint32)htcleoCurrentGeneration);
        if (htcleoReadyResult == KErrNone
                && htcleoCurrentGeneration <= iHtcleoReadyGeneration)
            {
            RProperty htcleoReadyProperty;
            htcleoReadyResult = htcleoReadyProperty.Attach(
                htcleoReadyCategory, htcleoReadyKey);
            if (htcleoReadyResult == KErrNone)
                {
                TRequestStatus htcleoReadyStatus;
                htcleoReadyProperty.Subscribe(htcleoReadyStatus);
                htcleoReadyResult =
                    htcleoReadyProperty.Get(htcleoCurrentGeneration);
                const TBool htcleoWaitForCommit =
                    htcleoReadyResult == KErrNone
                    && htcleoCurrentGeneration <= iHtcleoReadyGeneration;
                if (!htcleoWaitForCommit)
                    {
                    htcleoReadyProperty.Cancel();
                    }
                User::WaitForRequest(htcleoReadyStatus);
                if (htcleoWaitForCommit)
                    {
                    htcleoReadyResult = htcleoReadyStatus.Int();
                    if (htcleoReadyResult == KErrNone)
                        {
                        htcleoReadyResult = htcleoReadyProperty.Get(
                            htcleoCurrentGeneration);
                        }
                    }
                htcleoReadyProperty.Close();
                }
            }
        HtcleoMdQueryLog(0x4D440462u, htcleoReadyResult,
            (TUint32)htcleoCurrentGeneration);
        iCurrentQueryResults->Reset();
        ExecQueryAsynchL();
        HtcleoMdQueryLog(0x4D440463u, KErrNone,
            (TUint32)iQueryIterator);
        return;
        }

    if ( !htcleoQueryStatus )
        {
        HandleQueryResultsL();
        }

    if( NextQuery() )
        {
        ExecQueryAsynchL();
        }
    else
        {
        iNotification->ResultsCollectedL( iResults );
        }
    }'''


QUERY_HEADER_TAIL = r'''    CHnServiceHandler* iSh;
	
	};'''


QUERY_HEADER_TAIL_PATCHED = r'''    CHnServiceHandler* iSh;

    // HTCLEO_MCS_HN_COMMIT_REQUERY_V1
    TBool iHtcleoReadyRetryIssued;
    TInt iHtcleoReadyGeneration;
	
	};'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_block(text: str, start: str, end: str, replacement: str, label: str) -> str:
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(
            f"{label}: expected one block, starts={text.count(start)} ends={text.count(end)}"
        )
    first = text.index(start)
    last = text.index(end, first) + len(end)
    return text[:first] + replacement + text[last:]


def install(
    scanner: str, menueng: str, query: str, query_header: str
) -> tuple[str, str, str, str]:
    scanner = replace_block(
        scanner, SCANNER_START, SCANNER_END, SCANNER_REPLACEMENT,
        "defer scanner signal"
    )
    if "#include <e32property.h>" not in menueng:
        menueng = replace_once(
            menueng, MENUENG_INCLUDE, MENUENG_INCLUDE_PATCHED,
            "MenuEng property include"
        )
    menueng = replace_once(
        menueng, MENUENG_COMMIT, MENUENG_COMMIT_PATCHED,
        "MenuEng committed generation"
    )
    if "#include <e32property.h>" not in query:
        query = replace_once(
            query, QUERY_INCLUDE, QUERY_INCLUDE_PATCHED,
            "query property include"
        )
    query = replace_once(
        query, QUERY_GLOBAL_INCLUDE, QUERY_GLOBAL_INCLUDE_PATCHED,
        "query globals include"
    )
    query = replace_once(
        query, QUERY_CONSTRUCTOR, QUERY_CONSTRUCTOR_PATCHED,
        "query retry initialization"
    )
    query = replace_once(
        query, QUERY_EXECUTE, QUERY_EXECUTE_PATCHED,
        "query generation baseline"
    )
    query = replace_once(
        query, QUERY_RUNL, QUERY_RUNL_PATCHED,
        "query one-shot retry"
    )
    query_header = replace_once(
        query_header, QUERY_HEADER_TAIL, QUERY_HEADER_TAIL_PATCHED,
        "query retry fields"
    )
    return scanner, menueng, query, query_header


def verify(scanner: str, menueng: str, query: str, query_header: str) -> None:
    checks = {
        "markers": (
            scanner.count(MARKER) == 1
            and menueng.count(MARKER) == 1
            and query.count(MARKER) == 2
            and query_header.count(MARKER) == 1
            and scanner.count(READY_MARKER) == 1
        ),
        "scanner signal deferred": (
            scanner.count("0x4D43016Cu, KErrNotReady") == 1
            and "RProperty::Set(\n            htcleoReadyCategory" not in scanner
        ),
        "committed generation": (
            menueng.count("0x4D450532u") == 1
            and menueng.count("++htcleoCommitGeneration") == 1
            and menueng.count("RProperty::Set(\n                htcleoReadyCategory") == 1
        ),
        "result-list inspection": (
            query.count("KReturnValue8()") == 1
            and query.count("htcleoReturnList->Count()") == 1
        ),
        "one retry": (
            query.count("iHtcleoReadyRetryIssued = ETrue") == 1
            and query.count("!iHtcleoReadyRetryIssued") == 2
            and query.count("ExecQueryAsynchL();") == 3
            and query_header.count("TBool iHtcleoReadyRetryIssued;") == 1
            and query_header.count("TInt iHtcleoReadyGeneration;") == 1
        ),
        "commit wait without timer": (
            query.count("htcleoReadyProperty.Subscribe(htcleoReadyStatus)") == 1
            and query.count("User::WaitForRequest(htcleoReadyStatus)") == 1
            and "RTimer" not in query
            and "User::After" not in query
        ),
        "query stages": all(
            query.count(f"0x4D440{stage:03X}u") == 1
            for stage in range(0x460, 0x465)
        ),
        "no synthetic item": (
            "AppendL( htcleo" not in scanner
            and "AppendL( htcleo" not in menueng
            and "AppendL( htcleo" not in query
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MenuEng/HN commit-requery verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    scanner_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/menusrvappscanner.cpp"
    )
    menueng_path = (
        args.root / "sf/mw/homescreensrv/menucontentsrv/engsrc/menueng.cpp"
    )
    query_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src/hnqueryresultcollector.cpp"
    )
    query_header_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/inc/hnqueryresultcollector.h"
    )
    for path in (scanner_path, menueng_path, query_path, query_header_path):
        if not path.is_file():
            raise SystemExit(f"missing commit-requery source: {path}")
    scanner = scanner_path.read_text(encoding="latin-1")
    menueng = menueng_path.read_text(encoding="latin-1")
    query = query_path.read_text(encoding="latin-1")
    query_header = query_header_path.read_text(encoding="latin-1")
    if MARKER not in scanner:
        scanner, menueng, query, query_header = install(
            scanner, menueng, query, query_header
        )
    verify(scanner, menueng, query, query_header)
    scanner_path.write_text(scanner, encoding="latin-1")
    menueng_path.write_text(menueng, encoding="latin-1")
    query_path.write_text(query, encoding="latin-1")
    query_header_path.write_text(query_header, encoding="latin-1")
    print(
        "HTCLEO_MCS_HN_COMMIT_REQUERY="
        "menueng-532-empty-or-transient-once-460-464-no-timer"
    )


if __name__ == "__main__":
    main()
