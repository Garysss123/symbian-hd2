#!/usr/bin/env python3
"""Trace CHnMdModel construction for MatrixMenu on HTC Leo.

Iteration 529 reaches the call to CHnMdModel::NewL() but never returns.  Add
MatrixMenu-only, close-only checkpoints around allocation/member construction,
ConstructL, localization, XML provider, bitmap cache, TLS publication and both
Central Repository observers.  Calls and Leave behavior remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNMETADATAMODEL_DURABLE_LOG_V1"
BUILD_MARKER = "HTCLEO_HNMETADATAMODEL_BUILD_CLOSURE_V1"
ABI_MARKER = "HTCLEO_HNMETADATAMODEL_FROZEN_ABI_CLOSURE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
#include <f32file.h>

// HTCLEO_HNMETADATAMODEL_DURABLE_LOG_V1
static void HtcleoMdLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
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
    _LIT(KHtcleoMdLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMdLogPath, "C:\\Symbian3\\MDLOG.TXT");
    r = fs.MkDirAll(KHtcleoMdLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }
    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMdLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMdLogPath, EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((64 * 64) - 64))
        {
        _LIT8(KHtcleoMdPrefix, "HTCLEO_MD ");
        TBuf8<96> record;
        record.Append(KHtcleoMdPrefix);
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
        '#include <AvkonInternalCRKeys.h>\n',
        '#include <AvkonInternalCRKeys.h>\n' + HELPER,
        "metadata logger helper",
    )
    source = replace_once(
        source,
        """void CHnMdModel::ConstructL( MHnMdModelEventObserver *aModelObserver,
        CHnSuiteModelContainer * aSuiteModelContainer )
    {
    MMPERF(("CHnMetaDataModel::ConstructL - START"));
    MMPERF(("CHnMetaDataModel::ConstructL - query handler ready"));
    iLocalization = CHnMdLocalization::NewL();
    MMPERF(("CHnMetaDataModel::ConstructL - localization ready"));
    iXmlModelProvider = CHnXmlModelProvider::NewL();
    MMPERF(("CHnMetaDataModel::ConstructL - bitmap and mask ids cache ready"));
    iBitmapIdCache = CHnBitmapIdCache::NewL();
    MMPERF(("CHnMetaDataModel::ConstructL - model privider ready"));

    iCmnPtrs.iLocalization = iLocalization;
    iCmnPtrs.iIdGenerator = &iIdGenerator;
    iCmnPtrs.iModel = this;
    iCmnPtrs.iXmlModelProvider = iXmlModelProvider;
    iCmnPtrs.iContainer = aSuiteModelContainer;
    iCmnPtrs.iModelEventObserver = aModelObserver;
    iCmnPtrs.iBitmapIdCache = iBitmapIdCache;

    THnMdCommonPointers::SetStatic(&iCmnPtrs);

    iMode = EMdModeNormal;
    iRepositoryWidgetTypeObserver = CHnRepositoryWidgetTypeObserver::NewL( &iCmnPtrs, KMatrixRepositoryUid );
    iRepositoryShowFolderObserver = CHnRepositoryShowFolderObserver::NewL( &iCmnPtrs, KCRUidMenu, KMenuShowFolder );
    MMPERF(("CHnMetaDataModel::ConstructL - rep. observer ready"));
    }
""",
        """void CHnMdModel::ConstructL( MHnMdModelEventObserver *aModelObserver,
        CHnSuiteModelContainer * aSuiteModelContainer )
    {
    HtcleoMdLog(0x4D440120u, KErrNone, 0u);
    MMPERF(("CHnMetaDataModel::ConstructL - START"));
    MMPERF(("CHnMetaDataModel::ConstructL - query handler ready"));
    HtcleoMdLog(0x4D440121u, KErrNone, 0u);
    iLocalization = CHnMdLocalization::NewL();
    HtcleoMdLog(0x4D440122u, KErrNone, iLocalization ? 1u : 0u);
    MMPERF(("CHnMetaDataModel::ConstructL - localization ready"));
    HtcleoMdLog(0x4D440123u, KErrNone, 0u);
    iXmlModelProvider = CHnXmlModelProvider::NewL();
    HtcleoMdLog(0x4D440124u, KErrNone, iXmlModelProvider ? 1u : 0u);
    MMPERF(("CHnMetaDataModel::ConstructL - bitmap and mask ids cache ready"));
    HtcleoMdLog(0x4D440125u, KErrNone, 0u);
    iBitmapIdCache = CHnBitmapIdCache::NewL();
    HtcleoMdLog(0x4D440126u, KErrNone, iBitmapIdCache ? 1u : 0u);
    MMPERF(("CHnMetaDataModel::ConstructL - model privider ready"));

    HtcleoMdLog(0x4D440127u, KErrNone, 0u);
    iCmnPtrs.iLocalization = iLocalization;
    iCmnPtrs.iIdGenerator = &iIdGenerator;
    iCmnPtrs.iModel = this;
    iCmnPtrs.iXmlModelProvider = iXmlModelProvider;
    iCmnPtrs.iContainer = aSuiteModelContainer;
    iCmnPtrs.iModelEventObserver = aModelObserver;
    iCmnPtrs.iBitmapIdCache = iBitmapIdCache;

    THnMdCommonPointers::SetStatic(&iCmnPtrs);
    HtcleoMdLog(0x4D440128u, KErrNone, 0u);

    iMode = EMdModeNormal;
    HtcleoMdLog(0x4D440129u, KErrNone, 0u);
    iRepositoryWidgetTypeObserver = CHnRepositoryWidgetTypeObserver::NewL( &iCmnPtrs, KMatrixRepositoryUid );
    HtcleoMdLog(0x4D44012Au, KErrNone,
        iRepositoryWidgetTypeObserver ? 1u : 0u);
    HtcleoMdLog(0x4D44012Bu, KErrNone, 0u);
    iRepositoryShowFolderObserver = CHnRepositoryShowFolderObserver::NewL( &iCmnPtrs, KCRUidMenu, KMenuShowFolder );
    HtcleoMdLog(0x4D44012Cu, KErrNone,
        iRepositoryShowFolderObserver ? 1u : 0u);
    MMPERF(("CHnMetaDataModel::ConstructL - rep. observer ready"));
    HtcleoMdLog(0x4D44012Du, KErrNone, 0u);
    }
""",
        "metadata ConstructL body",
    )
    source = replace_once(
        source,
        """    {
    CHnMdModel* self = CHnMdModel::NewLC( aModelObserver,
            aSuiteModelContainer );
    CleanupStack::Pop( self );
    return self;
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
EXPORT_C CHnMdModel* CHnMdModel::NewLC""",
        """    {
    HtcleoMdLog(0x4D440100u, KErrNone, 0u);
    CHnMdModel* self = CHnMdModel::NewLC( aModelObserver,
            aSuiteModelContainer );
    HtcleoMdLog(0x4D440101u, KErrNone, self ? 1u : 0u);
    CleanupStack::Pop( self );
    HtcleoMdLog(0x4D440102u, KErrNone, 0u);
    return self;
    }

// ---------------------------------------------------------------------------
//
// ---------------------------------------------------------------------------
//
EXPORT_C CHnMdModel* CHnMdModel::NewLC""",
        "metadata NewL boundary",
    )
    source = replace_once(
        source,
        """    {
    CHnMdModel* self = new( ELeave ) CHnMdModel();
    CleanupStack::PushL( self );
    self->ConstructL( aModelObserver, aSuiteModelContainer );
    return self;
    }
""",
        """    {
    HtcleoMdLog(0x4D440110u, KErrNone, 0u);
    CHnMdModel* self = new( ELeave ) CHnMdModel();
    HtcleoMdLog(0x4D440112u, KErrNone, self ? 1u : 0u);
    CleanupStack::PushL( self );
    HtcleoMdLog(0x4D440113u, KErrNone, 0u);
    HtcleoMdLog(0x4D440114u, KErrNone, 0u);
    self->ConstructL( aModelObserver, aSuiteModelContainer );
    HtcleoMdLog(0x4D440115u, KErrNone, 0u);
    return self;
    }
""",
        "metadata NewLC boundary",
    )
    source = replace_once(
        source,
        """CHnMdModel::CHnMdModel()
    {
    }
""",
        """CHnMdModel::CHnMdModel()
    {
    HtcleoMdLog(0x4D440111u, KErrNone, 0u);
    }
""",
        "metadata constructor body",
    )
    return source


def verify(source: str, mmp: str, event_header: str) -> None:
    expected = [
        *range(0x4D440100, 0x4D440103),
        *range(0x4D440110, 0x4D440116),
        *range(0x4D440120, 0x4D44012E),
    ]
    missing = [
        f"0x{stage:08X}u"
        for stage in expected
        if source.count(f"0x{stage:08X}u") != 1
    ]
    checks = {
        "single marker": source.count(MARKER) == 1,
        "durable path": source.count(r"C:\\Symbian3\\MDLOG.TXT") == 1,
        "MatrixMenu SID gate": source.count("0x101F4CD2u") == 1,
        "close-only": source.count("file.Write(record);") == 1 and "file.Flush" not in source,
        "build closure": (
            mmp.count(BUILD_MARKER) == 1
            and mmp.count("../../hnpresentationmodel/inc") == 1
            and mmp.count("../../hnutilities/inc") == 1
        ),
        "frozen ABI closure": (
            event_header.count(ABI_MARKER) == 1
            and event_header.count("    TInt Id() const;") == 1
            and "IMPORT_C TInt Id() const;" not in event_header
        ),
        "calls retained": (
            source.count("CHnMdLocalization::NewL()") == 1
            and source.count("CHnXmlModelProvider::NewL()") == 1
            and source.count("CHnBitmapIdCache::NewL()") == 1
            and source.count("CHnRepositoryWidgetTypeObserver::NewL(") == 1
            and (
                source.count("CHnRepositoryShowFolderObserver::NewL(") == 1
                or source.count(
                    "HTCLEO_HNMETADATA_SHOWFOLDER_UI_FIRST_DEFER_V1"
                ) == 1
            )
            and source.count("THnMdCommonPointers::SetStatic(&iCmnPtrs);") == 1
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
        raise SystemExit("HN metadata trace verification failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/src/hnmdmodel.cpp"
    )
    mmp_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/group/hnmetadatamodel.mmp"
    )
    event_header_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/inc/hnmdevent.h"
    )
    if (
        not source_path.is_file()
        or not mmp_path.is_file()
        or not event_header_path.is_file()
    ):
        raise SystemExit("missing HN metadata model source, MMP or event header")
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    event_header = event_header_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    if BUILD_MARKER not in mmp:
        mmp = replace_once(
            mmp,
            "USERINCLUDE     ../inc\n",
            "USERINCLUDE     ../inc\n"
            "// HTCLEO_HNMETADATAMODEL_BUILD_CLOSURE_V1\n"
            "USERINCLUDE     ../../hnpresentationmodel/inc\n"
            "USERINCLUDE     ../../hnutilities/inc\n",
            "metadata include closure",
        )
    if ABI_MARKER not in event_header:
        event_header = replace_once(
            event_header,
            "    IMPORT_C TInt Id() const;\n",
            "    // HTCLEO_HNMETADATAMODEL_FROZEN_ABI_CLOSURE_V1\n"
            "    TInt Id() const;\n",
            "metadata event frozen ABI closure",
        )
    verify(source, mmp, event_header)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    event_header_path.write_text(event_header, encoding="latin-1")
    print(
        "HTCLEO_HNMETADATAMODEL_DURABLE_LOG=installed "
        "path=C:\\Symbian3\\MDLOG.TXT stages=4D440100-4D44012D"
    )


if __name__ == "__main__":
    main()
