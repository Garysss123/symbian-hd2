#!/usr/bin/env python3
"""Trace the core CHnEngine constructor for MatrixMenu on HTC Leo.

Iteration 528 traps CHnEngine::NewL() but never records its return, proving an
internal block.  Add MatrixMenu-only close-only HNLOG checkpoints around NewL,
NewLC and the three ConstructL dependencies: suite model container, metadata
model and HWRM light.  All calls and Leave behavior remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNENGINE_DURABLE_LOG_V1"
BUILD_MARKER = "HTCLEO_HNENGINE_BUILD_CLOSURE_V1"
IMPORT_MARKER = "HTCLEO_HNENGINE_PRESENTATION_IMPORT_CLOSURE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
#include <f32file.h>

// HTCLEO_HNENGINE_DURABLE_LOG_V1
static void HtcleoHnLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
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
    _LIT(KHtcleoHnLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoHnLogPath, "C:\\Symbian3\\HNLOG.TXT");
    r = fs.MkDirAll(KHtcleoHnLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }
    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoHnLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoHnLogPath, EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((64 * 64) - 64))
        {
        _LIT8(KHtcleoHnPrefix, "HTCLEO_HN ");
        TBuf8<96> record;
        record.Append(KHtcleoHnPrefix);
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


def install(source: str) -> str:
    source = replace_once(
        source,
        "#include <AknUtils.h>\n",
        "#include <AknUtils.h>\n" + HELPER,
        "HN logger helper",
    )
    source = replace_once(
        source,
        """void CHnEngine::ConstructL()
    {
    iEEnv = CEikonEnv::Static();
    iSuiteContainer = CHnSuiteModelContainer::NewL( *this , iControllerInterface );
    iMetaDataModel = CHnMdModel::NewL( this, iSuiteContainer );
    iLight = CHWRMLight::NewL(this);
    }
""",
        """void CHnEngine::ConstructL()
    {
    HtcleoHnLog(0x484E0120u, KErrNone, 0u);
    iEEnv = CEikonEnv::Static();
    HtcleoHnLog(0x484E0121u, KErrNone, iEEnv ? 1u : 0u);
    HtcleoHnLog(0x484E0122u, KErrNone, 0u);
    iSuiteContainer = CHnSuiteModelContainer::NewL( *this , iControllerInterface );
    HtcleoHnLog(0x484E0123u, KErrNone,
        iSuiteContainer ? 1u : 0u);
    HtcleoHnLog(0x484E0124u, KErrNone, 0u);
    iMetaDataModel = CHnMdModel::NewL( this, iSuiteContainer );
    HtcleoHnLog(0x484E0125u, KErrNone,
        iMetaDataModel ? 1u : 0u);
    HtcleoHnLog(0x484E0126u, KErrNone, 0u);
    iLight = CHWRMLight::NewL(this);
    HtcleoHnLog(0x484E0127u, KErrNone, iLight ? 1u : 0u);
    HtcleoHnLog(0x484E0128u, KErrNone, 0u);
    }
""",
        "HN ConstructL body",
    )
    source = replace_once(
        source,
        """    {
    CHnEngine* self = CHnEngine::NewLC( aController );
    CleanupStack::Pop( self );
    return self;
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
EXPORT_C CHnEngine* CHnEngine::NewLC""",
        """    {
    HtcleoHnLog(0x484E0100u, KErrNone, 0u);
    CHnEngine* self = CHnEngine::NewLC( aController );
    HtcleoHnLog(0x484E0101u, KErrNone, self ? 1u : 0u);
    CleanupStack::Pop( self );
    HtcleoHnLog(0x484E0102u, KErrNone, 0u);
    return self;
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
EXPORT_C CHnEngine* CHnEngine::NewLC""",
        "HN NewL boundary",
    )
    source = replace_once(
        source,
        """    {
    CHnEngine* self = new( ELeave ) CHnEngine( aController );
    CleanupStack::PushL( self );
    self->ConstructL();
    return self;
    }
""",
        """    {
    HtcleoHnLog(0x484E0110u, KErrNone, 0u);
    CHnEngine* self = new( ELeave ) CHnEngine( aController );
    HtcleoHnLog(0x484E0111u, KErrNone, self ? 1u : 0u);
    CleanupStack::PushL( self );
    HtcleoHnLog(0x484E0112u, KErrNone, 0u);
    HtcleoHnLog(0x484E0113u, KErrNone, 0u);
    self->ConstructL();
    HtcleoHnLog(0x484E0114u, KErrNone, 0u);
    return self;
    }
""",
        "HN NewLC boundary",
    )
    return source


def verify(source: str, mmp: str, presentation_header: str) -> None:
    expected = [
        *range(0x484E0100, 0x484E0103),
        *range(0x484E0110, 0x484E0115),
        *range(0x484E0120, 0x484E0129),
    ]
    missing = [
        f"0x{stage:08X}u"
        for stage in expected
        if source.count(f"0x{stage:08X}u") != 1
    ]
    checks = {
        "single marker": source.count(MARKER) == 1,
        "durable path": source.count(r"C:\\Symbian3\\HNLOG.TXT") == 1,
        "MatrixMenu SID gate": source.count("0x101F4CD2u") == 1,
        "close-only": source.count("file.Write(record);") == 1 and "file.Flush" not in source,
        "build closure": (
            mmp.count(BUILD_MARKER) == 1
            and mmp.count("../../hnmetadatamodel/inc") == 1
            and mmp.count("../../hnpresentationmodel/inc") == 1
            and mmp.count("../../hnutilities/inc") == 1
        ),
        "presentation import closure": (
            presentation_header.count(IMPORT_MARKER) == 1
            and presentation_header.count(
                "IMPORT_C CHnSuiteModel* GetLastSuiteModel();"
            ) == 1
            and presentation_header.count(
                "IMPORT_C CHnSuiteModel* GetParentSuiteModel();"
            ) == 1
            and presentation_header.count(
                "IMPORT_C CHnSuiteModel* GetSuiteModel( TInt aPosition );"
            ) == 1
        ),
        "calls retained": (
            source.count("CHnSuiteModelContainer::NewL( *this , iControllerInterface )") >= 2
            and source.count("CHnMdModel::NewL( this, iSuiteContainer )") >= 2
            and source.count("CHWRMLight::NewL(this)") == 1
        ),
        "no timer display or normalization": (
            "User::After" not in HELPER
            and "HalFunction" not in HELPER
            and "KErrNotSupported" not in HELPER
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if missing:
        failed.append("missing/duplicate stages=" + ",".join(missing))
    if failed:
        raise SystemExit("HN engine trace verification failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnengine"
    )
    source_path = component / "src/hnengine.cpp"
    mmp_path = component / "group/hnengine.mmp"
    presentation_header_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnpresentationmodel/inc/hnsuitemodelcontainer.h"
    )
    if (
        not source_path.is_file()
        or not mmp_path.is_file()
        or not presentation_header_path.is_file()
    ):
        raise SystemExit("missing HN engine source or MMP")
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    presentation_header = presentation_header_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    if BUILD_MARKER not in mmp:
        mmp = replace_once(
            mmp,
            "USERINCLUDE     ../inc\n",
            "USERINCLUDE     ../inc\n"
            "// HTCLEO_HNENGINE_BUILD_CLOSURE_V1\n"
            "USERINCLUDE     ../../hnmetadatamodel/inc\n"
            "USERINCLUDE     ../../hnpresentationmodel/inc\n"
            "USERINCLUDE     ../../hnutilities/inc\n",
            "HN include closure",
        )
    if IMPORT_MARKER not in presentation_header:
        presentation_header = replace_once(
            presentation_header,
            "    CHnSuiteModel* GetLastSuiteModel();\n",
            "    // HTCLEO_HNENGINE_PRESENTATION_IMPORT_CLOSURE_V1\n"
            "    IMPORT_C CHnSuiteModel* GetLastSuiteModel();\n",
            "last suite import",
        )
        presentation_header = replace_once(
            presentation_header,
            "    CHnSuiteModel* GetParentSuiteModel();\n",
            "    IMPORT_C CHnSuiteModel* GetParentSuiteModel();\n",
            "parent suite import",
        )
        presentation_header = replace_once(
            presentation_header,
            "    CHnSuiteModel* GetSuiteModel( TInt aPosition );\n",
            "    IMPORT_C CHnSuiteModel* GetSuiteModel( TInt aPosition );\n",
            "position suite import",
        )
    verify(source, mmp, presentation_header)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    presentation_header_path.write_text(presentation_header, encoding="latin-1")
    print(
        "HTCLEO_HNENGINE_DURABLE_LOG=installed "
        "path=C:\\Symbian3\\HNLOG.TXT stages=484E0100-484E0128"
    )


if __name__ == "__main__":
    main()
