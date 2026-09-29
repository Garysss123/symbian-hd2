#!/usr/bin/env python3
"""Trace the initial HN metadata evaluation pipeline on HTC Leo.

Iteration 532 proves suite loading, observer registration, filter construction
and mode setup all succeed; CHnMdModel::EvaluateL alone leaves with
KErrServerTerminated.  Add MatrixMenu-only close-only MDLOG checkpoints through
the model, suite and query-result collector layers.  Behavior is unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MODEL_MARKER = "HTCLEO_HNMETADATA_EVALUATION_DURABLE_LOG_V1"
SUITE_MARKER = "HTCLEO_HNMDSUITE_EVALUATION_DURABLE_LOG_V1"
QUERY_MARKER = "HTCLEO_HNQUERY_EVALUATION_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER_TEMPLATE = r'''
#include <f32file.h>

// __MARKER__
static void __FUNCTION__(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101F4CD2u)
        {
        return;
        }
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }
    _LIT(KHtcleoMdEvalDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMdEvalPath, "C:\\Symbian3\\MDLOG.TXT");
    r = fs.MkDirAll(KHtcleoMdEvalDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }
    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMdEvalPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMdEvalPath, EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((64 * 64) - 64))
        {
        _LIT8(KHtcleoMdEvalPrefix, "HTCLEO_MD ");
        TBuf8<96> record;
        record.Append(KHtcleoMdEvalPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        file.Write(record);
        }
    file.Close();
    fs.Close();
    }
'''


def logger(marker: str, function: str) -> str:
    return LOGGER_TEMPLATE.replace("__MARKER__", marker).replace(
        "__FUNCTION__", function
    )


def install_model(source: str) -> str:
    return replace_once(
        source,
        """EXPORT_C void CHnMdModel::EvaluateL( CHnFilter& aFilter )
    {
    for ( TInt i = iLoadedSuites.Count() - 1; i >= 0; i-- )
        {
        iLoadedSuites[i]->MarkEvaluationL( aFilter, *iCmnPtrs.iContainer->GetSuiteModel(i) );
        if( i == iLoadedSuites.Count() - 1 && !iIgnoreEvaluations )
            {
            iLoadedSuites[i]->EvaluateL( *iCmnPtrs.iContainer->GetSuiteModel(i) );
            }
        }
    }
""",
        """EXPORT_C void CHnMdModel::EvaluateL( CHnFilter& aFilter )
    {
    // HTCLEO_HNMETADATA_EVALUATION_DURABLE_LOG_V1
    HtcleoMdLog(0x4D440200u, KErrNone,
        (TUint32)iLoadedSuites.Count());
    for ( TInt i = iLoadedSuites.Count() - 1; i >= 0; i-- )
        {
        HtcleoMdLog(0x4D440201u, KErrNone, (TUint32)i);
        CHnSuiteModel* htcleoSuiteModel =
            iCmnPtrs.iContainer->GetSuiteModel(i);
        HtcleoMdLog(0x4D440202u, KErrNone,
            htcleoSuiteModel ? 1u : 0u);
        HtcleoMdLog(0x4D440203u, KErrNone, (TUint32)i);
        iLoadedSuites[i]->MarkEvaluationL( aFilter, *htcleoSuiteModel );
        HtcleoMdLog(0x4D440204u, KErrNone, (TUint32)i);
        HtcleoMdLog(0x4D440205u, KErrNone,
            iIgnoreEvaluations ? 1u : 0u);
        if( i == iLoadedSuites.Count() - 1 && !iIgnoreEvaluations )
            {
            HtcleoMdLog(0x4D440206u, KErrNone, (TUint32)i);
            iLoadedSuites[i]->EvaluateL( *htcleoSuiteModel );
            HtcleoMdLog(0x4D440207u, KErrNone, (TUint32)i);
            }
        HtcleoMdLog(0x4D440208u, KErrNone, (TUint32)i);
        }
    HtcleoMdLog(0x4D440209u, KErrNone, 0u);
    }
""",
        "metadata EvaluateL",
    )


def install_suite(source: str) -> str:
    source = replace_once(
        source,
        "#include <mmf/common/mmfcontrollerpluginresolver.h>\n",
        "#include <mmf/common/mmfcontrollerpluginresolver.h>\n"
        + logger(SUITE_MARKER, "HtcleoMdSuiteLog"),
        "suite logger",
    )
    source = replace_once(
        source,
        """TInt CHnMdSuite::EvaluateL( CHnSuiteModel & aSuiteModel )
    {
    MMPERF(("CHnMdSuite::EvaluateL - START"));
    aSuiteModel.GetItemsOrder()->DefineModelItemCountL( iItems.Count() );
    if( iEvaluationNeeded )
        {
        EvaluateSuiteItselfL( aSuiteModel );
        MMPERF(("CHnMdSuite::EvaluateL - suite evaluated"));
        iEvaluationNeeded = EFalse;
        }
    for( TInt i( 0 ); i < iItems.Count(); i++ )
    \t{
    \tCHnMdItem * item = iItems[i];
    \titem->SetAlternativeTemplateL( GetAlternativeWidgetNumber() );
    \titem->EvaluateItemL( aSuiteModel, GetSuiteParameters(), i );
    \t}
    
    MMPERF(("CHnMdSuite::EvaluateL - items evaluated - DONE"));
    return KErrNone;
    }
""",
        """TInt CHnMdSuite::EvaluateL( CHnSuiteModel & aSuiteModel )
    {
    HtcleoMdSuiteLog(0x4D440300u, KErrNone,
        (TUint32)iItems.Count());
    MMPERF(("CHnMdSuite::EvaluateL - START"));
    HtcleoMdSuiteLog(0x4D440301u, KErrNone, 0u);
    aSuiteModel.GetItemsOrder()->DefineModelItemCountL( iItems.Count() );
    HtcleoMdSuiteLog(0x4D440302u, KErrNone,
        (TUint32)iItems.Count());
    HtcleoMdSuiteLog(0x4D440303u, KErrNone,
        iEvaluationNeeded ? 1u : 0u);
    if( iEvaluationNeeded )
        {
        HtcleoMdSuiteLog(0x4D440304u, KErrNone, 0u);
        EvaluateSuiteItselfL( aSuiteModel );
        HtcleoMdSuiteLog(0x4D440305u, KErrNone, 0u);
        MMPERF(("CHnMdSuite::EvaluateL - suite evaluated"));
        iEvaluationNeeded = EFalse;
        HtcleoMdSuiteLog(0x4D440306u, KErrNone, 0u);
        }
    for( TInt i( 0 ); i < iItems.Count(); i++ )
    \t{
    \tCHnMdItem * item = iItems[i];
        HtcleoMdSuiteLog(0x4D440310u, KErrNone, (TUint32)i);
    \titem->SetAlternativeTemplateL( GetAlternativeWidgetNumber() );
        HtcleoMdSuiteLog(0x4D440311u, KErrNone, (TUint32)i);
        HtcleoMdSuiteLog(0x4D440312u, KErrNone, (TUint32)i);
    \titem->EvaluateItemL( aSuiteModel, GetSuiteParameters(), i );
        HtcleoMdSuiteLog(0x4D440313u, KErrNone, (TUint32)i);
    \t}
    
    MMPERF(("CHnMdSuite::EvaluateL - items evaluated - DONE"));
    HtcleoMdSuiteLog(0x4D440320u, KErrNone, 0u);
    return KErrNone;
    }
""",
        "suite EvaluateL",
    )
    source = replace_once(
        source,
        """void CHnMdSuite::EvaluateSuiteItselfL( CHnSuiteModel & aSuiteModel )
    {
    
    DEBUG(("_MM_: CHnMdSuite::EvaluateSuiteItselfL IN"));
    iSuiteModel = &aSuiteModel;
    //delete old query collector and create new one
    //currently running evaluations will be cancelled
    delete iQc;
    iQc = NULL;
    iQc = CHnQueryResultCollector::NewL( *iQueries, GetSuiteParameters() );
    iQc->StartAsynchL( this );
    }
""",
        """void CHnMdSuite::EvaluateSuiteItselfL( CHnSuiteModel & aSuiteModel )
    {
    HtcleoMdSuiteLog(0x4D440330u, KErrNone, 0u);
    DEBUG(("_MM_: CHnMdSuite::EvaluateSuiteItselfL IN"));
    iSuiteModel = &aSuiteModel;
    HtcleoMdSuiteLog(0x4D440331u, KErrNone,
        iSuiteModel ? 1u : 0u);
    //delete old query collector and create new one
    //currently running evaluations will be cancelled
    HtcleoMdSuiteLog(0x4D440332u, KErrNone, iQc ? 1u : 0u);
    delete iQc;
    iQc = NULL;
    HtcleoMdSuiteLog(0x4D440333u, KErrNone, 0u);
    HtcleoMdSuiteLog(0x4D440334u, KErrNone, 0u);
    iQc = CHnQueryResultCollector::NewL( *iQueries, GetSuiteParameters() );
    HtcleoMdSuiteLog(0x4D440335u, KErrNone, iQc ? 1u : 0u);
    HtcleoMdSuiteLog(0x4D440336u, KErrNone, 0u);
    iQc->StartAsynchL( this );
    HtcleoMdSuiteLog(0x4D440337u, KErrNone, 0u);
    }
""",
        "suite EvaluateSuiteItselfL",
    )
    return source


def install_query(source: str) -> str:
    source = replace_once(
        source,
        "#include <liwservicehandler.h>\n",
        "#include <liwservicehandler.h>\n"
        + logger(QUERY_MARKER, "HtcleoMdQueryLog"),
        "query logger",
    )
    source = replace_once(
        source,
        """CHnQueryResultCollector* CHnQueryResultCollector::NewL(
\t\tconst CHnMdQueries& aQueries , const CLiwGenericParamList& aParams )
\t{
\tCHnQueryResultCollector* self = NewLC( aQueries , aParams );
\tCleanupStack::Pop( self );
\treturn self;
\t}
""",
        """CHnQueryResultCollector* CHnQueryResultCollector::NewL(
\t\tconst CHnMdQueries& aQueries , const CLiwGenericParamList& aParams )
\t{
        HtcleoMdQueryLog(0x4D440400u, KErrNone, 0u);
\tCHnQueryResultCollector* self = NewLC( aQueries , aParams );
        HtcleoMdQueryLog(0x4D440401u, KErrNone, self ? 1u : 0u);
\tCleanupStack::Pop( self );
        HtcleoMdQueryLog(0x4D440402u, KErrNone, 0u);
\treturn self;
\t}
""",
        "collector NewL",
    )
    source = replace_once(
        source,
        """CHnQueryResultCollector* CHnQueryResultCollector::NewLC(
\t\tconst CHnMdQueries& aQueries , const CLiwGenericParamList& aParams )
\t{
\tCHnQueryResultCollector* self =
\tnew ( ELeave ) CHnQueryResultCollector( aQueries , aParams );
\tCleanupStack::PushL( self );
\tself->ConstructL();
\treturn self;
\t}
""",
        """CHnQueryResultCollector* CHnQueryResultCollector::NewLC(
\t\tconst CHnMdQueries& aQueries , const CLiwGenericParamList& aParams )
\t{
        HtcleoMdQueryLog(0x4D440410u, KErrNone, 0u);
\tCHnQueryResultCollector* self =
\tnew ( ELeave ) CHnQueryResultCollector( aQueries , aParams );
        HtcleoMdQueryLog(0x4D440411u, KErrNone, self ? 1u : 0u);
\tCleanupStack::PushL( self );
        HtcleoMdQueryLog(0x4D440412u, KErrNone, 0u);
        HtcleoMdQueryLog(0x4D440413u, KErrNone, 0u);
\tself->ConstructL();
        HtcleoMdQueryLog(0x4D440414u, KErrNone, 0u);
\treturn self;
\t}
""",
        "collector NewLC",
    )
    source = replace_once(
        source,
        """void CHnQueryResultCollector::ConstructL()
\t{
\tiResults = CLiwGenericParamList::NewL();
\tiCurrentQueryResults = CLiwGenericParamList::NewL();
\tCActiveScheduler::Add( this );
\t}
""",
        """void CHnQueryResultCollector::ConstructL()
\t{
        HtcleoMdQueryLog(0x4D440420u, KErrNone, 0u);
\tiResults = CLiwGenericParamList::NewL();
        HtcleoMdQueryLog(0x4D440421u, KErrNone, iResults ? 1u : 0u);
\tiCurrentQueryResults = CLiwGenericParamList::NewL();
        HtcleoMdQueryLog(0x4D440422u, KErrNone,
            iCurrentQueryResults ? 1u : 0u);
\tCActiveScheduler::Add( this );
        HtcleoMdQueryLog(0x4D440423u, KErrNone, 0u);
\t}
""",
        "collector ConstructL",
    )
    source = replace_once(
        source,
        """void CHnQueryResultCollector::StartAsynchL(
        MHnQueryResultCollectorNotification* aNotification )
    {
    __ASSERT_DEBUG( aNotification , User::Panic( KMatrixPanic , 0) );
    iNotification = aNotification;
    ResetL();
    if( iQueryIterator < iQueries.Count())
        {
        ExecQueryAsynchL();
        }
    else
        {
        iNotification->ResultsCollectedL( iResults );
        }
    }
""",
        """void CHnQueryResultCollector::StartAsynchL(
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
    }
""",
        "collector StartAsynchL",
    )
    source = replace_once(
        source,
        """void CHnQueryResultCollector::ExecQueryAsynchL()
    {
    __ASSERT_DEBUG( iQueryIterator < iQueries.Count() ,
                    User::Panic( KMatrixPanic , 0) );
    //cancel any running evaulations
    Cancel();
    ExecQueryL( iQueries.Query( iQueryIterator ) );
    SetActive();
    }
""",
        """void CHnQueryResultCollector::ExecQueryAsynchL()
    {
    HtcleoMdQueryLog(0x4D440440u, KErrNone,
        (TUint32)iQueryIterator);
    __ASSERT_DEBUG( iQueryIterator < iQueries.Count() ,
                    User::Panic( KMatrixPanic , 0) );
    //cancel any running evaulations
    Cancel();
    HtcleoMdQueryLog(0x4D440441u, KErrNone,
        (TUint32)iQueryIterator);
    HtcleoMdQueryLog(0x4D440442u, KErrNone,
        (TUint32)iQueryIterator);
    ExecQueryL( iQueries.Query( iQueryIterator ) );
    HtcleoMdQueryLog(0x4D440443u, KErrNone,
        (TUint32)iQueryIterator);
    SetActive();
    HtcleoMdQueryLog(0x4D440444u, KErrNone,
        (TUint32)iQueryIterator);
    }
""",
        "collector ExecQueryAsynchL",
    )
    source = replace_once(
        source,
        """void CHnQueryResultCollector::ExecQueryL( CHnMdQuery& aQuery )
    {
    CLiwGenericParamList* constructor
        = aQuery.GetService().EvaluateConstructorL( iParams );
    CleanupStack::PushL( constructor );
    CLiwGenericParamList* command
        = aQuery.GetService().EvaluateCommandL( iParams );
    CleanupStack::PushL( command );

    delete iSh;
    iSh = NULL;
    iSh = CHnServiceHandler::NewL(
            aQuery.GetService().GetServiceName(),
            aQuery.GetService().GetInterfaceName(),
            aQuery.GetService().GetCommand().GetCommandName(),
            aQuery.GetService().GetCommand().GetCommandMode(),
            constructor,
            command );

    CleanupStack::Pop( command );
    CleanupStack::Pop( constructor );

    iSh->ExecuteL( *iCurrentQueryResults, iStatus );
    }
""",
        """void CHnQueryResultCollector::ExecQueryL( CHnMdQuery& aQuery )
    {
    HtcleoMdQueryLog(0x4D440450u, KErrNone, 0u);
    HtcleoMdQueryLog(0x4D440451u, KErrNone, 0u);
    CLiwGenericParamList* constructor
        = aQuery.GetService().EvaluateConstructorL( iParams );
    HtcleoMdQueryLog(0x4D440452u, KErrNone,
        constructor ? 1u : 0u);
    CleanupStack::PushL( constructor );
    HtcleoMdQueryLog(0x4D440453u, KErrNone, 0u);
    CLiwGenericParamList* command
        = aQuery.GetService().EvaluateCommandL( iParams );
    HtcleoMdQueryLog(0x4D440454u, KErrNone, command ? 1u : 0u);
    CleanupStack::PushL( command );

    HtcleoMdQueryLog(0x4D440455u, KErrNone, iSh ? 1u : 0u);
    delete iSh;
    iSh = NULL;
    HtcleoMdQueryLog(0x4D440456u, KErrNone, 0u);
    iSh = CHnServiceHandler::NewL(
            aQuery.GetService().GetServiceName(),
            aQuery.GetService().GetInterfaceName(),
            aQuery.GetService().GetCommand().GetCommandName(),
            aQuery.GetService().GetCommand().GetCommandMode(),
            constructor,
            command );
    HtcleoMdQueryLog(0x4D440457u, KErrNone, iSh ? 1u : 0u);

    CleanupStack::Pop( command );
    CleanupStack::Pop( constructor );
    HtcleoMdQueryLog(0x4D440458u, KErrNone, 0u);

    HtcleoMdQueryLog(0x4D440459u, KErrNone, 0u);
    iSh->ExecuteL( *iCurrentQueryResults, iStatus );
    HtcleoMdQueryLog(0x4D44045Au, KErrNone, 0u);
    }
""",
        "collector ExecQueryL",
    )
    return source


def verify(model: str, suite: str, query: str) -> None:
    commit_requery = "HTCLEO_MCS_HN_COMMIT_REQUERY_V1" in query
    synchronous_getlist = "HTCLEO_HN_GETLIST_SYNCHRONOUS_V1" in query
    queued_sync_completion = "HTCLEO_HN_SYNC_COMPLETION_QUEUED_RUNL_V1" in query
    model_stages = range(0x4D440200, 0x4D44020A)
    suite_stages = [
        *range(0x4D440300, 0x4D440307),
        *range(0x4D440310, 0x4D440314),
        0x4D440320,
        *range(0x4D440330, 0x4D440338),
    ]
    query_stages = [
        *range(0x4D440400, 0x4D440403),
        *range(0x4D440410, 0x4D440415),
        *range(0x4D440420, 0x4D440424),
        *range(0x4D440430, 0x4D440436),
        *range(0x4D440440, 0x4D440445),
        *range(0x4D440450, 0x4D44045B),
    ]
    missing = []
    for source, stages in (
        (model, model_stages),
        (suite, suite_stages),
        (query, query_stages),
    ):
        missing.extend(
            f"0x{stage:08X}u"
            for stage in stages
            if source.count(f"0x{stage:08X}u") != 1
        )
    checks = {
        "model marker": model.count(MODEL_MARKER) == 1,
        "suite marker": suite.count(SUITE_MARKER) == 1,
        "query marker": query.count(QUERY_MARKER) == 1,
        "suite path": suite.count(r"C:\\Symbian3\\MDLOG.TXT") == 1,
        "query path": query.count(r"C:\\Symbian3\\MDLOG.TXT") == 1,
        "MatrixMenu SID gates": (
            suite.count("0x101F4CD2u") == 1
            and query.count("0x101F4CD2u") == (
                5 if queued_sync_completion else (
                    4 if synchronous_getlist else (3 if commit_requery else 1)
                )
            )
        ),
        "close-only": (
            suite.count("file.Write(record);") == 1
            and query.count("file.Write(record);") == 1
            and "file.Flush" not in suite
            and "file.Flush" not in query
        ),
        "core calls retained": (
            model.count("iLoadedSuites[i]->EvaluateL( *htcleoSuiteModel );") == 1
            and suite.count("iQc->StartAsynchL( this );") == 1
            and query.count("iSh = CHnServiceHandler::NewL(") == 1
            and query.count("iSh->ExecuteL( *iCurrentQueryResults, iStatus );") == 1
        ),
        "no timer display or normalization": all(
            token not in suite + query
            for token in ("User::After", "HalFunction", "KErrServerTerminated = KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if missing:
        failed.append("missing/duplicate stages=" + ",".join(missing))
    if failed:
        raise SystemExit("HN metadata evaluation trace failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel"
    )
    model_path = component / "src/hnmdmodel.cpp"
    suite_path = component / "src/hnmdsuite.cpp"
    query_path = component / "src/hnqueryresultcollector.cpp"
    if not all(path.is_file() for path in (model_path, suite_path, query_path)):
        raise SystemExit("missing HN metadata evaluation sources")
    model = model_path.read_text(encoding="latin-1")
    suite = suite_path.read_text(encoding="latin-1")
    query = query_path.read_text(encoding="latin-1")
    if MODEL_MARKER not in model:
        model = install_model(model)
    if SUITE_MARKER not in suite:
        suite = install_suite(suite)
    if QUERY_MARKER not in query:
        query = install_query(query)
    verify(model, suite, query)
    model_path.write_text(model, encoding="latin-1")
    suite_path.write_text(suite, encoding="latin-1")
    query_path.write_text(query, encoding="latin-1")
    print(
        "HTCLEO_HNMETADATA_EVALUATION_LOG=installed "
        "stages=4D440200-4D44045A behavior=unchanged"
    )


if __name__ == "__main__":
    main()
