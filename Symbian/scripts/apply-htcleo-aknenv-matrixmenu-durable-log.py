#!/usr/bin/env python3
"""Add a MatrixMenu-only durable trace to CAknEnv::ConstructL.

Iteration 495 reaches the post-Cone LafEnv hook and does not return from
CAknEnv::ConstructL.  This transform brackets every stock initialization call
in that function.  It preserves all calls, leaves and results; only the exact
MatrixMenu SID appends bounded, fail-open records to MENULOG.TXT.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNENV_MATRIXMENU_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
// HTCLEO_AKNENV_MATRIXMENU_DURABLE_LOG_V1
static void HtcleoAknEnvMenuLog(
    TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101f4cd2u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoAknEnvMenuDir, "C:\\Symbian3\\");
    _LIT(KHtcleoAknEnvMenuPath, "C:\\Symbian3\\MENULOG.TXT");
    r = fs.MkDirAll(KHtcleoAknEnvMenuDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoAknEnvMenuPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoAknEnvMenuPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoAknEnvMenuPrefix, "HTCLEO_MENU ");
        TBuf8<96> record;
        record.Append(KHtcleoAknEnvMenuPrefix);
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
        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            }
        }
    file.Close();
    fs.Close();
    }

'''


STOCK_CONSTRUCT = r'''EXPORT_C void CAknEnv::ConstructL()
    {
    TName threadName=RThread().Name();
    TBool isEiksrvThread=(threadName.CompareC(EIKAPPUI_SERVER_THREAD_NAME)==KErrNone);

    User::LeaveIfError( RAknIconSrvClient::Connect() );

    iCdlEngRef = CdlEngine::CreateCdlEngineL();

    iSettingCache = CAknSettingCache::NewL();
    
    //if KFeatureIdUiTransitionEffects is not supported, CTransitionManager::NewL returns NULL
	iTransitionManager = CTransitionManager::NewL( *iCoeEnv );

    iStateArray = new(ELeave) CArrayPtrFlat<MAknIntermediateState>(1);
    CAknSgcClient::CreateL();   // owned by CCoeStatic system
    TAknPopupFader::CreateStaticL();    // owned by CCoeStatic system

    iRunInfoArray = new( ELeave )
        TBidirectionalState::TRunInfo[KInitialRunInfoArraySize];

    iRunInfoArrayLength = KInitialRunInfoArraySize;

    SetLayoutRequirementsL();
    LoadAknLayoutL();
    AssertLayoutLoaded();
    iLayout = &AknLayout::CustomisationInstance();

    // Set the current feature language
    if (FeatureManager::FeatureSupported(KFeatureIdJapanese))
        {
        iFeatureLanguage = KFeatureIdJapanese;
        }

    }
'''


TRACED_CONSTRUCT = r'''EXPORT_C void CAknEnv::ConstructL()
    {
    TName threadName=RThread().Name();
    TBool isEiksrvThread=(threadName.CompareC(EIKAPPUI_SERVER_THREAD_NAME)==KErrNone);
    HtcleoAknEnvMenuLog(0x4D4DA000u, KErrNone,
        isEiksrvThread ? 1u : 0u);

    HtcleoAknEnvMenuLog(0x4D4DA001u, KErrNone, 0u);
    const TInt iconServerError = RAknIconSrvClient::Connect();
    HtcleoAknEnvMenuLog(0x4D4DA002u, iconServerError, 0u);
    User::LeaveIfError(iconServerError);

    HtcleoAknEnvMenuLog(0x4D4DA003u, KErrNone, 0u);
    iCdlEngRef = CdlEngine::CreateCdlEngineL();
    HtcleoAknEnvMenuLog(0x4D4DA004u, KErrNone,
        iCdlEngRef ? 1u : 0u);

    HtcleoAknEnvMenuLog(0x4D4DA005u, KErrNone, 0u);
    iSettingCache = CAknSettingCache::NewL();
    HtcleoAknEnvMenuLog(0x4D4DA006u, KErrNone,
        iSettingCache ? 1u : 0u);
    
    //if KFeatureIdUiTransitionEffects is not supported, CTransitionManager::NewL returns NULL
    HtcleoAknEnvMenuLog(0x4D4DA007u, KErrNone, 0u);
	iTransitionManager = CTransitionManager::NewL( *iCoeEnv );
    HtcleoAknEnvMenuLog(0x4D4DA008u, KErrNone,
        iTransitionManager ? 1u : 0u);

    HtcleoAknEnvMenuLog(0x4D4DA009u, KErrNone, 0u);
    iStateArray = new(ELeave) CArrayPtrFlat<MAknIntermediateState>(1);
    HtcleoAknEnvMenuLog(0x4D4DA00Au, KErrNone,
        iStateArray ? 1u : 0u);
    HtcleoAknEnvMenuLog(0x4D4DA00Bu, KErrNone, 0u);
    CAknSgcClient::CreateL();   // owned by CCoeStatic system
    HtcleoAknEnvMenuLog(0x4D4DA00Cu, KErrNone, 0u);
    HtcleoAknEnvMenuLog(0x4D4DA00Du, KErrNone, 0u);
    TAknPopupFader::CreateStaticL();    // owned by CCoeStatic system
    HtcleoAknEnvMenuLog(0x4D4DA00Eu, KErrNone, 0u);

    HtcleoAknEnvMenuLog(0x4D4DA00Fu, KErrNone, 0u);
    iRunInfoArray = new( ELeave )
        TBidirectionalState::TRunInfo[KInitialRunInfoArraySize];
    HtcleoAknEnvMenuLog(0x4D4DA010u, KErrNone,
        iRunInfoArray ? 1u : 0u);

    iRunInfoArrayLength = KInitialRunInfoArraySize;
    HtcleoAknEnvMenuLog(0x4D4DA011u, KErrNone,
        (TUint32)iRunInfoArrayLength);

    HtcleoAknEnvMenuLog(0x4D4DA012u, KErrNone, 0u);
    SetLayoutRequirementsL();
    HtcleoAknEnvMenuLog(0x4D4DA013u, KErrNone, 0u);
    HtcleoAknEnvMenuLog(0x4D4DA014u, KErrNone, 0u);
    LoadAknLayoutL();
    HtcleoAknEnvMenuLog(0x4D4DA015u, KErrNone, 0u);
    HtcleoAknEnvMenuLog(0x4D4DA016u, KErrNone, 0u);
    AssertLayoutLoaded();
    HtcleoAknEnvMenuLog(0x4D4DA017u, KErrNone, 0u);
    HtcleoAknEnvMenuLog(0x4D4DA018u, KErrNone, 0u);
    iLayout = &AknLayout::CustomisationInstance();
    HtcleoAknEnvMenuLog(0x4D4DA019u, KErrNone,
        iLayout ? 1u : 0u);

    // Set the current feature language
    if (FeatureManager::FeatureSupported(KFeatureIdJapanese))
        {
        iFeatureLanguage = KFeatureIdJapanese;
        }
    HtcleoAknEnvMenuLog(0x4D4DA01Au, KErrNone,
        (TUint32)iFeatureLanguage);

    }
'''


def install(source: str) -> str:
    source = replace_once(
        source,
        "#include <e32property.h>\n",
        "#include <e32property.h>\n#include <f32file.h>\n",
        "filesystem include",
    )
    source = replace_once(
        source,
        "#define APPLY_CONE_FONT_EXTRA_LARGE_FACTOR",
        HELPER + "#define APPLY_CONE_FONT_EXTRA_LARGE_FACTOR",
        "durable helper",
    )
    return replace_once(
        source,
        STOCK_CONSTRUCT,
        TRACED_CONSTRUCT,
        "CAknEnv ConstructL",
    )


def verify(source: str) -> None:
    stages = range(0x4D4DA000, 0x4D4DA01B)
    checks = {
        "marker": source.count(MARKER) == 1,
        "exact SID gate": (
            source.count(
                "htcleoSid != 0x101f4cd2u && !htcleoHome"
            ) == 1
            if "HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT_V1"
            in source
            else source.count(
                "RProcess().SecureId().iId != 0x101f4cd2u"
            ) == 1
        ),
        "durable path": source.count(r"C:\\Symbian3\\MENULOG.TXT") == 1,
        "all stages": all(
            source.count(f"0x{stage:08X}u") == 1 for stage in stages
        ),
        "single write": source.count("file.Write(record)") == 1,
        "single flush": source.count("file.Flush()") == 1,
        "stock icon connect": source.count(
            "const TInt iconServerError = RAknIconSrvClient::Connect();"
        ) == 1,
        "stock icon error": source.count(
            "User::LeaveIfError(iconServerError);"
        ) == 1,
        "stock layout calls": (
            source.count("SetLayoutRequirementsL();") == (
                2 if "HTCLEO_AKNENV_MATRIXMENU_CDL_RECONNECT_V1" in source
                else 1
            )
            and source.count("LoadAknLayoutL()") >= (
                2 if "HTCLEO_AKNENV_MATRIXMENU_CDL_RECONNECT_V1" in source
                else 1
            )
            and source.count("AssertLayoutLoaded();") == 1
            and source.count(
                "iLayout = &AknLayout::CustomisationInstance();"
            ) == 1
        ),
        "no delay or display": (
            "User::After" not in HELPER and "HalFunction" not in HELPER
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("AknEnv trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AvKon/src/aknenv.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNENV_MATRIXMENU_DURABLE_LOG=installed "
        "stages=4D4DA000-4D4DA01A"
    )


if __name__ == "__main__":
    main()
