#!/usr/bin/env python3
"""Trace CHnEngine initial suite loading for MatrixMenu on HTC Leo.

Iteration 531 completes CHnEngine construction but CMmAppUi::InitializeL leaves
with KErrServerTerminated.  Add close-only HNLOG checkpoints around the HN
InitializeL interface and every synchronous step in HandleNewSuiteLoadedEventL.
All return, Leave, evaluation and error-note behavior remains unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNENGINE_INITIALIZE_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        """EXPORT_C TInt CHnEngine::InitializeL( CLiwGenericParamList& aParam )
    {
    DEBUG(("_MM_:CMatrixMenuAppUi::InitializeL IN"));
    User::LeaveIfError( HandleNewSuiteLoadedEventL( aParam ) );
    DEBUG(("_MM_:CMatrixMenuAppUi::InitializeL OUT"));
    // This is an interface method so some value has to be returned.
    return KErrNone;
    }
""",
        """EXPORT_C TInt CHnEngine::InitializeL( CLiwGenericParamList& aParam )
    {
    // HTCLEO_HNENGINE_INITIALIZE_DURABLE_LOG_V1
    HtcleoHnLog(0x484E0200u, KErrNone, 0u);
    DEBUG(("_MM_:CMatrixMenuAppUi::InitializeL IN"));
    const TInt htcleoInitializeResult = HandleNewSuiteLoadedEventL( aParam );
    HtcleoHnLog(0x484E0201u, htcleoInitializeResult, 0u);
    User::LeaveIfError( htcleoInitializeResult );
    DEBUG(("_MM_:CMatrixMenuAppUi::InitializeL OUT"));
    HtcleoHnLog(0x484E0202u, KErrNone, 0u);
    // This is an interface method so some value has to be returned.
    return KErrNone;
    }
""",
        "HN InitializeL body",
    )
    source = replace_once(
        source,
        """TInt CHnEngine::HandleNewSuiteLoadedEventL(
        CLiwGenericParamList& aParams )
    {
    DEBUG(("_MM_:CHnEngine::HandleNewSuiteLoadedEventL IN"));
    TInt err( KErrNone );
    const TLiwGenericParam* param =
        aParams.FindFirst( err, KNewSuiteParamNameEn );
    if( err != KErrNotFound )
        {
        TPtrC genre;
        param->Value().Get( genre );
        DEBUG16(("_MM_:\\tSuite genre name: %S",&genre));
        // load and evaluate the suite
        if( genre.Compare( KFolderSuite) )
            {
            //only folder suite is supported
            User::Leave( KErrNotSupported );
            }
        err = iMetaDataModel->LoadSuiteL( genre, &aParams );
        if ( !err )
            {
            GetLastSuiteModelL()->RegisterSuiteObserverL( &iControllerInterface, EPriorityNull );
            CHnFilter* filter = CHnFilter::NewLC();
            filter->SetSuiteNameL( genre );
            filter->SetEvaluateSuiteL( ETrue );
            if ( iEditMode )
                {
                iMetaDataModel->SetModeL( EMdModeEdit );
                }
            else
                {
                iMetaDataModel->SetModeL( EMdModeNormal );
                }

            TRAP( err, iMetaDataModel->EvaluateL( *filter ) );

            CleanupStack::PopAndDestroy( filter );
            if ( err )
                {
                iMetaDataModel->DeleteLastSuite();
                iSuiteContainer->PopSuiteModelL( genre );
                }
            }
        else
            {
            // show error note to User
            HBufC* message( NULL );
            switch ( err )
                {
                case KErrPathNotFound :
                    {
                    message = KDebugNoteDirNotFound().AllocL();
                    }
                    break;
                case KErrNotFound :
                    {
                    message = KDebugNoteFileNotFound().AllocL();
                    }
                    break;
                default :
                    {
                    message = HBufC::NewL( KDebugNoteOtherError().Length() +
                                            KMaxLength );
                    message->Des().AppendFormat( KDebugNoteOtherError, err );
                    }
                    break;
                }
            iEEnv->AlertWin( *message );
            delete message;
            }
        }
    DEBUG(("_MM_:\\tReturned error code: %d",err));
    DEBUG(("_MM_:CHnEngine::HandleNewSuiteLoadedEventL OUT"));

    return err;
    }
""",
        """TInt CHnEngine::HandleNewSuiteLoadedEventL(
        CLiwGenericParamList& aParams )
    {
    HtcleoHnLog(0x484E0210u, KErrNone, 0u);
    DEBUG(("_MM_:CHnEngine::HandleNewSuiteLoadedEventL IN"));
    TInt err( KErrNone );
    const TLiwGenericParam* param =
        aParams.FindFirst( err, KNewSuiteParamNameEn );
    HtcleoHnLog(0x484E0211u, err, param ? 1u : 0u);
    if( err != KErrNotFound )
        {
        TPtrC genre;
        param->Value().Get( genre );
        HtcleoHnLog(0x484E0212u, KErrNone, (TUint32)genre.Length());
        DEBUG16(("_MM_:\\tSuite genre name: %S",&genre));
        // load and evaluate the suite
        if( genre.Compare( KFolderSuite) )
            {
            //only folder suite is supported
            User::Leave( KErrNotSupported );
            }
        HtcleoHnLog(0x484E0213u, KErrNone, 0u);
        HtcleoHnLog(0x484E0214u, KErrNone, 0u);
        err = iMetaDataModel->LoadSuiteL( genre, &aParams );
        HtcleoHnLog(0x484E0215u, err, 0u);
        if ( !err )
            {
            HtcleoHnLog(0x484E0216u, KErrNone, 0u);
            GetLastSuiteModelL()->RegisterSuiteObserverL( &iControllerInterface, EPriorityNull );
            HtcleoHnLog(0x484E0217u, KErrNone, 0u);
            CHnFilter* filter = CHnFilter::NewLC();
            HtcleoHnLog(0x484E0218u, KErrNone, filter ? 1u : 0u);
            filter->SetSuiteNameL( genre );
            filter->SetEvaluateSuiteL( ETrue );
            HtcleoHnLog(0x484E0219u, KErrNone, 0u);
            HtcleoHnLog(0x484E021Au, KErrNone, iEditMode ? 1u : 0u);
            if ( iEditMode )
                {
                iMetaDataModel->SetModeL( EMdModeEdit );
                }
            else
                {
                iMetaDataModel->SetModeL( EMdModeNormal );
                }
            HtcleoHnLog(0x484E021Bu, KErrNone, 0u);

            HtcleoHnLog(0x484E021Cu, KErrNone, 0u);
            TRAP( err, iMetaDataModel->EvaluateL( *filter ) );
            HtcleoHnLog(0x484E021Du, err, 0u);

            CleanupStack::PopAndDestroy( filter );
            if ( err )
                {
                iMetaDataModel->DeleteLastSuite();
                iSuiteContainer->PopSuiteModelL( genre );
                }
            HtcleoHnLog(0x484E021Eu, err, 0u);
            }
        else
            {
            HtcleoHnLog(0x484E0220u, err, 0u);
            // show error note to User
            HBufC* message( NULL );
            switch ( err )
                {
                case KErrPathNotFound :
                    {
                    message = KDebugNoteDirNotFound().AllocL();
                    }
                    break;
                case KErrNotFound :
                    {
                    message = KDebugNoteFileNotFound().AllocL();
                    }
                    break;
                default :
                    {
                    message = HBufC::NewL( KDebugNoteOtherError().Length() +
                                            KMaxLength );
                    message->Des().AppendFormat( KDebugNoteOtherError, err );
                    }
                    break;
                }
            HtcleoHnLog(0x484E0221u, err, message ? 1u : 0u);
            HtcleoHnLog(0x484E0222u, err, 0u);
            iEEnv->AlertWin( *message );
            HtcleoHnLog(0x484E0223u, err, 0u);
            delete message;
            HtcleoHnLog(0x484E0224u, err, 0u);
            }
        }
    DEBUG(("_MM_:\\tReturned error code: %d",err));
    DEBUG(("_MM_:CHnEngine::HandleNewSuiteLoadedEventL OUT"));

    HtcleoHnLog(0x484E0225u, err, 0u);
    return err;
    }
""",
        "HN new-suite body",
    )
    return source


def verify(source: str) -> None:
    expected = [
        *range(0x484E0200, 0x484E0203),
        *range(0x484E0210, 0x484E021F),
        *range(0x484E0220, 0x484E0226),
    ]
    missing = [
        f"0x{stage:08X}u"
        for stage in expected
        if source.count(f"0x{stage:08X}u") != 1
    ]
    checks = {
        "single marker": source.count(MARKER) == 1,
        "logger retained": source.count("static void HtcleoHnLog(") == 1,
        "load retained": source.count(
            "err = iMetaDataModel->LoadSuiteL( genre, &aParams );"
        ) == 1,
        "evaluate trap retained": source.count(
            "TRAP( err, iMetaDataModel->EvaluateL( *filter ) );"
        ) == 1,
        "return error retained": source.count("return err;") >= 1,
        "no timer display or normalization": (
            "User::After" not in source[source.index(MARKER) - 300 : source.index(MARKER) + 8000]
            and "HalFunction" not in source[source.index(MARKER) - 300 : source.index(MARKER) + 8000]
            and "KErrServerTerminated = KErrNone" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if missing:
        failed.append("missing/duplicate stages=" + ",".join(missing))
    if failed:
        raise SystemExit("HN initialize trace verification failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnengine/src/hnengine.cpp"
    )
    if not source_path.is_file():
        raise SystemExit("missing HN engine source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_HNENGINE_INITIALIZE_LOG=installed "
        "stages=484E0200-484E0225 behavior=unchanged"
    )


if __name__ == "__main__":
    main()
