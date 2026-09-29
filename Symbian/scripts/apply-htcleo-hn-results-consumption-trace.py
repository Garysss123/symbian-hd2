#!/usr/bin/env python3
"""Trace real HN query consumption and CHnMdItem model publication."""

from __future__ import annotations

import argparse
from pathlib import Path


QUERY_MARKER = "HTCLEO_HN_QUERY_CONSUMPTION_TRACE_V1"
ITEM_MARKER_V1 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V1"
ITEM_MARKER_V2 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V2"
ITEM_MARKER_V3 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V3"
ITEM_MARKER_V4 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V4"
ITEM_MARKER_V5 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V5"
ITEM_MARKER_V6 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V6"
ITEM_MARKER_V7 = "HTCLEO_HN_ITEM_RESULTS_TRACE_V7"
ITEM_MARKER = "HTCLEO_HN_ITEM_RESULTS_TRACE_V8"


QUERY_OLD = r'''    if ( !htcleoQueryStatus )
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


QUERY_NEW = r'''    // HTCLEO_HN_QUERY_CONSUMPTION_TRACE_V1
    if ( !htcleoQueryStatus )
        {
        HtcleoMdQueryLog(0x4D440467u, KErrNone,
            (TUint32)iCurrentQueryResults->Count());
        HandleQueryResultsL();
        HtcleoMdQueryLog(0x4D440468u, KErrNone,
            (TUint32)iResults->Count());
        }

    HtcleoMdQueryLog(0x4D440469u, KErrNone,
        (TUint32)iQueryIterator);
    const TBool htcleoHasNextQuery = NextQuery();
    HtcleoMdQueryLog(0x4D44046Au, KErrNone,
        ((TUint32)(htcleoHasNextQuery ? 1 : 0) << 16)
        | ((TUint32)iQueryIterator & 0xFFFFu));
    if( htcleoHasNextQuery )
        {
        ExecQueryAsynchL();
        }
    else
        {
        HtcleoMdQueryLog(0x4D44046Bu, KErrNone,
            (TUint32)iResults->Count());
        iNotification->ResultsCollectedL( iResults );
        HtcleoMdQueryLog(0x4D44046Cu, KErrNone, 0u);
        }
    }'''


ITEM_DECL_ANCHOR = "using namespace LIW;\n"
ITEM_DECL = r'''using namespace LIW;

// HTCLEO_HN_ITEM_RESULTS_TRACE_V8
void HtcleoMdNotifyLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
'''


ITEM_FUNCTION = r'''void CHnMdItem::ResultsCollectedL( CLiwGenericParamList* aResults )
    {
    // HTCLEO_HN_ITEM_RESULTS_TRACE_V8
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        const TUint htcleoCountSetupKey = 0x7F4D4302u;
        const TSecurityPolicy htcleoCountSetupPolicy(
            TSecurityPolicy::EAlwaysPass);
        TInt htcleoCountSetupResult = RProperty::Define(
            htcleoCountSetupKey, RProperty::EInt,
            htcleoCountSetupPolicy, htcleoCountSetupPolicy);
        if ( htcleoCountSetupResult == KErrAlreadyExists )
            {
            htcleoCountSetupResult = KErrNone;
            }
        HtcleoMdNotifyLog(0x4D44049Bu, htcleoCountSetupResult, 0u);
        const TUint htcleoIconSetupKey = 0x7F4D4303u;
        TInt htcleoIconSetupResult = RProperty::Define(
            htcleoIconSetupKey, RProperty::EInt,
            htcleoCountSetupPolicy, htcleoCountSetupPolicy);
        if ( htcleoIconSetupResult == KErrAlreadyExists )
            {
            htcleoIconSetupResult = KErrNone;
            }
        HtcleoMdNotifyLog(0x4D44049Cu, htcleoIconSetupResult, 0u);
        }
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        TInt htcleoReadyValue = 0;
        const TInt htcleoReadyResult = RProperty::Get(
            htcleoReadyCategory, htcleoReadyKey, htcleoReadyValue);
        HtcleoMdNotifyLog(0x4D44049Au, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        const TUint htcleoIconErrorKey = 0x7F4D4303u;
        TInt htcleoIconErrorValue = KErrNotFound;
        const TInt htcleoIconErrorResult = RProperty::Get(
            htcleoReadyCategory, htcleoIconErrorKey,
            htcleoIconErrorValue);
        HtcleoMdNotifyLog(0x4D44049Du, htcleoIconErrorResult,
            (TUint32)htcleoIconErrorValue);
        if ( htcleoReadyResult != KErrNone || htcleoReadyValue == 0 )
            {
            return;
            }
        }
    HtcleoMdNotifyLog(0x4D440470u, KErrNone,
        aResults ? (TUint32)aResults->Count() : 0xFFFFFFFFu);
    iQueriesResultsList->AppendL( *aResults );
    HtcleoMdNotifyLog(0x4D440471u, KErrNone,
        (TUint32)iQueriesResultsList->Count());

    RArray< TInt > ids;
    CleanupClosePushL( ids );
    HtcleoMdNotifyLog(0x4D440472u, KErrNone,
        (TUint32)iItemPosition);
    iSuiteModel->GetItemsOrder()->GetIdsForL( iItemPosition, ids );
    HtcleoMdNotifyLog(0x4D440473u, KErrNone, (TUint32)ids.Count());
    TInt startCount = ids.Count();
    TInt visibleItemsBeforeEvaluation = iSuiteModel->GetItemsOrder()->Count();
    HtcleoMdNotifyLog(0x4D440474u, KErrNone,
        (TUint32)visibleItemsBeforeEvaluation);
    TInt id( 0 );

    TBool result = ETrue;
    TInt itemCounter = 0;

    HtcleoMdNotifyLog(0x4D440475u, KErrNone, 0u);
    TInt maxCount( GetItemsMaxCountL() );
    HtcleoMdNotifyLog(0x4D440476u, KErrNone, (TUint32)maxCount);
    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         maxCount == KErrNotFound && aResults && aResults->Count() > 0 )
        {
        const TUid htcleoCountCategory = { 0x101F4CD2 };
        const TUint htcleoCountKey = 0x7F4D4302u;
        TInt htcleoRealCount = KErrNotFound;
        const TInt htcleoCountResult = RProperty::Get(
            htcleoCountCategory, htcleoCountKey, htcleoRealCount);
        HtcleoMdNotifyLog(0x4D440477u, htcleoCountResult,
            (TUint32)htcleoRealCount);
        if ( htcleoCountResult == KErrNone &&
             htcleoRealCount > 0 && htcleoRealCount <= 30 )
            {
            maxCount = htcleoRealCount;
            }
        }

    for ( TInt i(0); result; i++, itemCounter++)
        {
        HtcleoMdNotifyLog(0x4D440480u, KErrNone,
            (((TUint32)i & 0xFFFFu) << 16)
            | ((TUint32)itemCounter & 0xFFFFu));
        result = ( maxCount != KErrUnknown ) ? i < maxCount && result : result;

        if ( !result )
            {
            HtcleoMdNotifyLog(0x4D440481u, KErrNone, (TUint32)i);
            continue;
            }

        id = (ids.Count() > 0 && i < ids.Count()) ? ids[itemCounter]
                : KErrNotFound;
        HtcleoMdNotifyLog(0x4D440482u, KErrNone, (TUint32)id);

        TInt htcleoMutationResult = KErrNone;
        if( id == KErrNotFound )
            {
            id = iCmnPtrs->iIdGenerator->GetNextId();
            HtcleoMdNotifyLog(0x4D440483u, KErrNone, (TUint32)id);
            TInt err = AddItemL( *iSuiteModel, id, *iQueriesResultsList,
                    iItemPosition, itemCounter );
            htcleoMutationResult = err;
            if ( KErrAlreadyExists == err )
                {
                // update empty item which is identified by "-1"
                TInt err = UpdateItemL( *iSuiteModel,
                    iSuiteModel->IdByIndex(-1), *iQueriesResultsList, i );
                htcleoMutationResult = err;
                result = ( KErrNone == err ) ? ETrue : EFalse;
                }
            else if ( KErrNone != err )
                {
                result = EFalse;
                }
            }
        else
            {
            TInt err = UpdateItemL( *iSuiteModel, id,
                *iQueriesResultsList, i );
            htcleoMutationResult = err;
            result = ( KErrNone == err ) ? ETrue : EFalse;
            }
        HtcleoMdNotifyLog(0x4D440484u, htcleoMutationResult,
            (TUint32)id);

        HtcleoMdNotifyLog(0x4D440485u, KErrNone, (TUint32)i);
        const TBool htcleoValid = IsValidL( *iQueriesResultsList, i );
        HtcleoMdNotifyLog(0x4D440486u, KErrNone,
            htcleoValid ? 1u : 0u);
        if ( !htcleoValid )
            {
            HtcleoMdNotifyLog(0x4D440487u, KErrNone, (TUint32)id);
            RemoveItemL( *iSuiteModel, id );
            itemCounter--;
            continue;
            }
        }

    HtcleoMdNotifyLog(0x4D440490u, KErrNone,
        (((TUint32)startCount & 0xFFFFu) << 16)
        | ((TUint32)itemCounter & 0xFFFFu));
    for( TInt it(startCount - 1); it >= itemCounter -1 && it >= 0; it-- )
        {
        HtcleoMdNotifyLog(0x4D440491u, KErrNone, (TUint32)ids[it]);
        RemoveItemL( *iSuiteModel, ids[it] );
        HtcleoMdNotifyLog(0x4D440492u, KErrNone, (TUint32)it);
        }

    CleanupStack::PopAndDestroy( &ids );
    HtcleoMdNotifyLog(0x4D440493u, KErrNone,
        (TUint32)visibleItemsBeforeEvaluation);
    iSuiteModel->RefreshMulModelL( visibleItemsBeforeEvaluation );
    HtcleoMdNotifyLog(0x4D440494u, KErrNone, 0u);
    TBool observersNotified =
        iSuiteModel->ItemEvaluationFinishedL( iItemPosition );
    HtcleoMdNotifyLog(0x4D440495u, KErrNone,
        observersNotified ? 1u : 0u);
    const TInt htcleoVisibleItemsAfterEvaluation =
        iSuiteModel->GetItemsOrder()->Count();
    HtcleoMdNotifyLog(0x4D440499u,
        observersNotified && htcleoVisibleItemsAfterEvaluation == 0
            ? KErrNotFound : KErrNone,
        (TUint32)htcleoVisibleItemsAfterEvaluation);
    if ( observersNotified && htcleoVisibleItemsAfterEvaluation > 0 )
        {
        HtcleoMdNotifyLog(0x4D440496u, KErrNone, 0u);
        iCmnPtrs->iModel->SuiteModelReadyToShowL( iSuiteModel );
        HtcleoMdNotifyLog(0x4D440497u, KErrNone, 0u);
        }

    HtcleoMdNotifyLog(0x4D440498u, KErrNone, 0u);
    DEBUG(("_MM_: CHnMdItem::ResultsCollectedL OUT"));
    }'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_query(text: str) -> str:
    if QUERY_MARKER in text:
        return text
    return replace_once(text, QUERY_OLD, QUERY_NEW, "query consumption tail")


def install_item(text: str) -> str:
    if ITEM_MARKER_V1 in text and ITEM_MARKER_V2 not in text:
        text = text.replace(ITEM_MARKER_V1, ITEM_MARKER_V2)
        old = r'''    if ( observersNotified )
        {
        HtcleoMdNotifyLog(0x4D440496u, KErrNone, 0u);
        iCmnPtrs->iModel->SuiteModelReadyToShowL( iSuiteModel );
        HtcleoMdNotifyLog(0x4D440497u, KErrNone, 0u);
        }'''
        new = r'''    const TInt htcleoVisibleItemsAfterEvaluation =
        iSuiteModel->GetItemsOrder()->Count();
    HtcleoMdNotifyLog(0x4D440499u,
        observersNotified && htcleoVisibleItemsAfterEvaluation == 0
            ? KErrNotFound : KErrNone,
        (TUint32)htcleoVisibleItemsAfterEvaluation);
    if ( observersNotified && htcleoVisibleItemsAfterEvaluation > 0 )
        {
        HtcleoMdNotifyLog(0x4D440496u, KErrNone, 0u);
        iCmnPtrs->iModel->SuiteModelReadyToShowL( iSuiteModel );
        HtcleoMdNotifyLog(0x4D440497u, KErrNone, 0u);
        }'''
        text = replace_once(text, old, new, "empty suite publication guard")
    if ITEM_MARKER_V2 in text and ITEM_MARKER_V3 not in text:
        text = text.replace(ITEM_MARKER_V2, ITEM_MARKER_V3)
        if "#include <e32property.h>" not in text:
            text = replace_once(
                text,
                "#include <liwservicehandler.h>\n",
                "#include <liwservicehandler.h>\n#include <e32property.h>\n",
                "property include",
            )
        old_entry = r'''    // HTCLEO_HN_ITEM_RESULTS_TRACE_V3
    HtcleoMdNotifyLog(0x4D440470u, KErrNone,'''
        new_entry = r'''    // HTCLEO_HN_ITEM_RESULTS_TRACE_V3
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        const TUid htcleoGridHandleCategory = { 0x101F4CD2 };
        const TUint htcleoGridHandleKey = 0x7F4D5701u;
        TInt htcleoGridHandle = 0;
        const TInt htcleoGridHandleResult = RProperty::Get(
            htcleoGridHandleCategory, htcleoGridHandleKey,
            htcleoGridHandle);
        HtcleoMdNotifyLog(0x4D44049Au, htcleoGridHandleResult,
            (TUint32)htcleoGridHandle);
        if ( htcleoGridHandleResult != KErrNone || htcleoGridHandle == 0 )
            {
            return;
            }
        }
    HtcleoMdNotifyLog(0x4D440470u, KErrNone,'''
        text = replace_once(text, old_entry, new_entry, "pre-grid result guard")
    if ITEM_MARKER_V3 in text and ITEM_MARKER_V4 not in text:
        text = text.replace(ITEM_MARKER_V3, ITEM_MARKER_V4)
        old_gate = r'''    // HTCLEO_HN_ITEM_RESULTS_TRACE_V4
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        const TUid htcleoGridHandleCategory = { 0x101F4CD2 };
        const TUint htcleoGridHandleKey = 0x7F4D5701u;
        TInt htcleoGridHandle = 0;
        const TInt htcleoGridHandleResult = RProperty::Get(
            htcleoGridHandleCategory, htcleoGridHandleKey,
            htcleoGridHandle);
        HtcleoMdNotifyLog(0x4D44049Au, htcleoGridHandleResult,
            (TUint32)htcleoGridHandle);
        if ( htcleoGridHandleResult != KErrNone || htcleoGridHandle == 0 )
            {
            return;
            }
        }'''
        new_gate = r'''    // HTCLEO_HN_ITEM_RESULTS_TRACE_V4
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        const TUid htcleoReadyCategory = { 0x101F4CD2 };
        const TUint htcleoReadyKey = 0x7F4D4301u;
        TInt htcleoReadyValue = 0;
        const TInt htcleoReadyResult = RProperty::Get(
            htcleoReadyCategory, htcleoReadyKey, htcleoReadyValue);
        HtcleoMdNotifyLog(0x4D44049Au, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        if ( htcleoReadyResult != KErrNone || htcleoReadyValue == 0 )
            {
            return;
            }
        }'''
        text = replace_once(text, old_gate, new_gate, "AppArc-ready result gate")
    if ITEM_MARKER_V4 in text and ITEM_MARKER_V5 not in text:
        text = text.replace(ITEM_MARKER_V4, ITEM_MARKER_V5)
        old_count = r'''    TInt maxCount( GetItemsMaxCountL() );
    HtcleoMdNotifyLog(0x4D440476u, KErrNone, (TUint32)maxCount);'''
        new_count = r'''    TInt maxCount( GetItemsMaxCountL() );
    HtcleoMdNotifyLog(0x4D440476u, KErrNone, (TUint32)maxCount);
    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         maxCount == KErrNotFound && aResults && aResults->Count() > 0 )
        {
        HtcleoMdNotifyLog(0x4D440477u, KErrNone,
            (TUint32)aResults->Count());
        maxCount = KErrUnknown;
        }'''
        text = replace_once(
            text, old_count, new_count, "missing count fail-open"
        )
    if ITEM_MARKER_V5 in text and ITEM_MARKER_V6 not in text:
        text = text.replace(ITEM_MARKER_V5, ITEM_MARKER_V6)
        old_fallback = r'''    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         maxCount == KErrNotFound && aResults && aResults->Count() > 0 )
        {
        HtcleoMdNotifyLog(0x4D440477u, KErrNone,
            (TUint32)aResults->Count());
        maxCount = KErrUnknown;
        }'''
        new_fallback = r'''    if ( RProcess().SecureId().iId == 0x101F4CD2u &&
         maxCount == KErrNotFound && aResults && aResults->Count() > 0 )
        {
        const TUid htcleoCountCategory = { 0x101F4CD2 };
        const TUint htcleoCountKey = 0x7F4D4302u;
        TInt htcleoRealCount = KErrNotFound;
        const TInt htcleoCountResult = RProperty::Get(
            htcleoCountCategory, htcleoCountKey, htcleoRealCount);
        HtcleoMdNotifyLog(0x4D440477u, htcleoCountResult,
            (TUint32)htcleoRealCount);
        if ( htcleoCountResult == KErrNone &&
             htcleoRealCount > 0 && htcleoRealCount <= 30 )
            {
            maxCount = htcleoRealCount;
            }
        }'''
        text = replace_once(
            text, old_fallback, new_fallback, "bounded real count fallback"
        )
    if ITEM_MARKER_V6 in text and ITEM_MARKER_V7 not in text:
        text = text.replace(ITEM_MARKER_V6, ITEM_MARKER_V7)
        old_entry = r'''    // HTCLEO_HN_ITEM_RESULTS_TRACE_V7
    if ( RProcess().SecureId().iId == 0x101F4CD2u )'''
        new_entry = r'''    // HTCLEO_HN_ITEM_RESULTS_TRACE_V7
    if ( RProcess().SecureId().iId == 0x101F4CD2u )
        {
        const TUint htcleoCountSetupKey = 0x7F4D4302u;
        const TSecurityPolicy htcleoCountSetupPolicy(
            TSecurityPolicy::EAlwaysPass);
        TInt htcleoCountSetupResult = RProperty::Define(
            htcleoCountSetupKey, RProperty::EInt,
            htcleoCountSetupPolicy, htcleoCountSetupPolicy);
        if ( htcleoCountSetupResult == KErrAlreadyExists )
            {
            htcleoCountSetupResult = KErrNone;
            }
        HtcleoMdNotifyLog(0x4D44049Bu, htcleoCountSetupResult, 0u);
        }
    if ( RProcess().SecureId().iId == 0x101F4CD2u )'''
        text = replace_once(
            text, old_entry, new_entry, "real count property setup"
        )
    if ITEM_MARKER_V7 in text and ITEM_MARKER not in text:
        text = text.replace(ITEM_MARKER_V7, ITEM_MARKER)
        count_log = r'''        HtcleoMdNotifyLog(0x4D44049Bu, htcleoCountSetupResult, 0u);'''
        count_and_icon_log = r'''        HtcleoMdNotifyLog(0x4D44049Bu, htcleoCountSetupResult, 0u);
        const TUint htcleoIconSetupKey = 0x7F4D4303u;
        TInt htcleoIconSetupResult = RProperty::Define(
            htcleoIconSetupKey, RProperty::EInt,
            htcleoCountSetupPolicy, htcleoCountSetupPolicy);
        if ( htcleoIconSetupResult == KErrAlreadyExists )
            {
            htcleoIconSetupResult = KErrNone;
            }
        HtcleoMdNotifyLog(0x4D44049Cu, htcleoIconSetupResult, 0u);'''
        text = replace_once(
            text, count_log, count_and_icon_log, "icon error property setup"
        )
        ready_log = r'''        HtcleoMdNotifyLog(0x4D44049Au, htcleoReadyResult,
            (TUint32)htcleoReadyValue);'''
        ready_and_icon_log = r'''        HtcleoMdNotifyLog(0x4D44049Au, htcleoReadyResult,
            (TUint32)htcleoReadyValue);
        const TUint htcleoIconErrorKey = 0x7F4D4303u;
        TInt htcleoIconErrorValue = KErrNotFound;
        const TInt htcleoIconErrorResult = RProperty::Get(
            htcleoReadyCategory, htcleoIconErrorKey,
            htcleoIconErrorValue);
        HtcleoMdNotifyLog(0x4D44049Du, htcleoIconErrorResult,
            (TUint32)htcleoIconErrorValue);'''
        text = replace_once(
            text, ready_log, ready_and_icon_log, "icon error property read"
        )
    if ITEM_MARKER in text and "htcleoRealCount <= 64" in text:
        text = replace_once(
            text,
            "htcleoRealCount <= 64",
            "htcleoRealCount <= 30",
            "real count safety ceiling",
        )
    if ITEM_MARKER in text:
        return text
    if "#include <e32property.h>" not in text:
        text = replace_once(
            text,
            "#include <liwservicehandler.h>\n",
            "#include <liwservicehandler.h>\n#include <e32property.h>\n",
            "property include",
        )
    text = replace_once(text, ITEM_DECL_ANCHOR, ITEM_DECL, "item logger declaration")
    start = text.find(
        "void CHnMdItem::ResultsCollectedL( CLiwGenericParamList* aResults )"
    )
    end = text.find("\n// End of file", start)
    if start < 0 or end < 0:
        raise SystemExit("item ResultsCollectedL function boundary not found")
    return text[:start] + ITEM_FUNCTION + "\n" + text[end:]


def verify(query: str, item: str) -> None:
    checks = {
        "query marker": query.count(QUERY_MARKER) == 1,
        "query stages": all(
            query.count(f"0x4D440{stage:03X}u") == 1
            for stage in range(0x467, 0x46D)
        ),
        "one notification": query.count(
            "iNotification->ResultsCollectedL( iResults );"
        ) == 2,
        "item marker": item.count(ITEM_MARKER) == 2,
        "item declaration": item.count(
            "void HtcleoMdNotifyLog(TUint32 aStage, TInt aResult, TUint32 aDetail);"
        ) == 1,
        "item stages": all(
            item.count(f"0x4D440{stage:03X}u") == 1
            for stage in (
                0x470, 0x471, 0x472, 0x473, 0x474, 0x475, 0x476, 0x477,
                0x480, 0x481, 0x482, 0x483, 0x484, 0x485, 0x486,
                0x487, 0x490, 0x491, 0x492, 0x493, 0x494, 0x495,
                0x496, 0x497, 0x498, 0x499, 0x49A, 0x49B, 0x49C, 0x49D,
            )
        ),
        "old item markers absent": (
            ITEM_MARKER_V1 not in item
            and ITEM_MARKER_V2 not in item
            and ITEM_MARKER_V3 not in item
            and ITEM_MARKER_V4 not in item
            and ITEM_MARKER_V5 not in item
            and ITEM_MARKER_V6 not in item
            and ITEM_MARKER_V7 not in item
        ),
        "AppArc-ready result guard": (
            item.count("#include <e32property.h>") == 1
            and item.count("RProcess().SecureId().iId == 0x101F4CD2u") == 3
            and item.count("0x7F4D4301u") == 1
            and item.count("0x4D44049Au") == 1
            and item.count("htcleoReadyResult != KErrNone") == 1
            and item.count("htcleoReadyValue == 0") == 1
        ),
        "bounded real count fallback": (
            item.count("maxCount == KErrNotFound") == 1
            and item.count("aResults && aResults->Count() > 0") == 1
            and item.count("0x7F4D4302u") == 2
            and item.count("htcleoRealCount > 0") == 1
            and item.count("htcleoRealCount <= 30") == 1
            and item.count("maxCount = htcleoRealCount") == 1
            and item.count("maxCount = KErrUnknown") == 0
            and item.count("0x4D440477u") == 1
        ),
        "real count property setup": (
            item.count("htcleoCountSetupKey = 0x7F4D4302u") == 1
            and item.count("TSecurityPolicy::EAlwaysPass") == 1
            and item.count("htcleoCountSetupResult = RProperty::Define(") == 1
            and item.count("0x4D44049Bu") == 1
        ),
        "icon error property trace": (
            item.count("htcleoIconSetupKey = 0x7F4D4303u") == 1
            and item.count("htcleoIconErrorKey = 0x7F4D4303u") == 1
            and item.count("0x4D44049Cu") == 1
            and item.count("0x4D44049Du") == 1
        ),
        "empty suite publication guarded": (
            item.count("htcleoVisibleItemsAfterEvaluation") == 4
            and item.count(
                "observersNotified && htcleoVisibleItemsAfterEvaluation > 0"
            ) == 1
            and item.count(
                "observersNotified && htcleoVisibleItemsAfterEvaluation == 0"
            ) == 1
        ),
        "behavior retained": all(
            token in item
            for token in (
                "AddItemL( *iSuiteModel",
                "UpdateItemL( *iSuiteModel",
                "IsValidL( *iQueriesResultsList, i )",
                "RefreshMulModelL( visibleItemsBeforeEvaluation )",
                "ItemEvaluationFinishedL( iItemPosition )",
                "SuiteModelReadyToShowL( iSuiteModel )",
            )
        ),
        "no fake or wait": all(
            token not in query + item
            for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HN results consumption trace verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src"
    )
    query_path = base / "hnqueryresultcollector.cpp"
    item_path = base / "hnmditem.cpp"
    if not query_path.is_file() or not item_path.is_file():
        raise SystemExit("missing HN query/item source")
    query = install_query(query_path.read_text(encoding="latin-1"))
    item = install_item(item_path.read_text(encoding="latin-1"))
    verify(query, item)
    query_path.write_text(query, encoding="latin-1")
    item_path.write_text(item, encoding="latin-1")
    print(
        "HTCLEO_HN_RESULTS_CONSUMPTION_TRACE="
        "query-467-46c-item-470-49a-apparc-ready-gated-"
        "bounded-real-count-empty-suite-suppressed"
    )


if __name__ == "__main__":
    main()
