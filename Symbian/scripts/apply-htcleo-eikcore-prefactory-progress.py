#!/usr/bin/env python3
"""Instrument the exact Eikon pre-factory path without changing control flow.

The existing AknCapServer SID continues to update its private integer property.
For the MatrixMenu SID only, the same E300-E311 and E400-E425 boundaries append
fail-open records to MENULOG.TXT.  No other process performs file I/O, and the
shared DLL does not wait, retry, suppress an error, or alter any branch.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE_V1"
MENU_MARKER = "HTCLEO_EIKCORE_MATRIXMENU_PREFACTORY_DURABLE_LOG_V2"
OFFSET_MARKER = "HTCLEO_GCCE_UNLIMITED_FILENAME_OFFSET_V1"
MACRO = "__HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LEGACY_HELPER = r'''
#ifdef __HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE__
// HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE_V1
const TUid KHtcleoAknCapTraceCategory = {0x10207218};
const TUint KHtcleoEikCoreTraceKey = 0x7f044301u;

static void HtcleoEikCorePreFactoryTrace(TUint32 aStage, TInt aResult)
    {
    if (RProcess().SecureId().iId != KHtcleoAknCapTraceCategory.iUid)
        {
        return;
        }
    const TUint32 value = ((aStage & 0xffffu) << 16) |
        ((TUint32)aResult & 0xffffu);
    (void)RProperty::Set(
        KHtcleoAknCapTraceCategory,
        KHtcleoEikCoreTraceKey,
        (TInt)value);
    }
#else
inline void HtcleoEikCorePreFactoryTrace(TUint32, TInt) {}
#endif

'''


HELPER = r'''
#ifdef __HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE__
// HTCLEO_EIKCORE_AKNCAP_PREFACTORY_TRACE_V1
// HTCLEO_EIKCORE_MATRIXMENU_PREFACTORY_DURABLE_LOG_V2
const TUid KHtcleoAknCapTraceCategory = {0x10207218};
const TUint KHtcleoEikCoreTraceKey = 0x7f044301u;
const TUint32 KHtcleoMatrixMenuSid = 0x101f4cd2u;

static void HtcleoEikCoreMatrixMenuTrace(TUint32 aStage, TInt aResult)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikCoreMenuDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikCoreMenuPath, "C:\\Symbian3\\MENULOG.TXT");
    r = fs.MkDirAll(KHtcleoEikCoreMenuDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoEikCoreMenuPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoEikCoreMenuPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoEikCoreMenuPrefix, "HTCLEO_MENU ");
        TBuf8<96> record;
        record.Append(KHtcleoEikCoreMenuPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(
            0x4D4D0000u | (aStage & 0xffffu), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(0u, EHex, 8);
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

static void HtcleoEikCorePreFactoryTrace(TUint32 aStage, TInt aResult)
    {
    const TUint32 sid = RProcess().SecureId().iId;
    if (sid == KHtcleoAknCapTraceCategory.iUid)
        {
        const TUint32 value = ((aStage & 0xffffu) << 16) |
            ((TUint32)aResult & 0xffffu);
        (void)RProperty::Set(
            KHtcleoAknCapTraceCategory,
            KHtcleoEikCoreTraceKey,
            (TInt)value);
        }
    else if (sid == KHtcleoMatrixMenuSid)
        {
        HtcleoEikCoreMatrixMenuTrace(aStage, aResult);
        }
    }
#else
inline void HtcleoEikCorePreFactoryTrace(TUint32, TInt) {}
#endif

'''


def install(source: str) -> str:
    source = replace_once(
        source,
        "#include <e32hal.h>\n",
        "#include <e32hal.h>\n#include <e32property.h>\n",
        "property include",
    )
    source = replace_once(
        source,
        "GLDEF_C void Panic(TEikPanic aPanic)\n",
        HELPER + "GLDEF_C void Panic(TEikPanic aPanic)\n",
        "trace helper",
    )
    source = replace_once(
        source,
        "\tUser::LeaveIfError(coeEnvConstructionError);\n\n\t// Construct iEikEnvExtra here",
        "\tUser::LeaveIfError(coeEnvConstructionError);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE300u, coeEnvConstructionError);\n\n"
        "\t// Construct iEikEnvExtra here",
        "constructor checkpoint",
    )
    source = replace_once(
        source,
        "\tif (!iEikEnvExtra)\n\t\tiEikEnvExtra = CEikEnvExtra::NewL(*this);\n\t\n\tTApaCommand command = aCommandLine.Command();",
        "\tif (!iEikEnvExtra)\n"
        "\t\t{\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE301u, KErrNone);\n"
        "\t\tiEikEnvExtra = CEikEnvExtra::NewL(*this);\n"
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE302u, KErrNone);\n"
        "\t\n\tTApaCommand command = aCommandLine.Command();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE303u, (TInt)command);",
        "environment-extra checkpoints",
    )
    source = replace_once(
        source,
        "\tCleanupClosePushL(apparcServer);\n\tTInt err = apparcServer.Connect();\n\t\n\t// Store application language",
        "\tCleanupClosePushL(apparcServer);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE304u, KErrNone);\n"
        "\tTInt err = apparcServer.Connect();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE305u, err);\n"
        "\t\n\t// Store application language",
        "AppArc connect checkpoints",
    )
    source = replace_once(
        source,
        "\tStoreAppLanguageL(apparcServer);\n\t\n\t// Set default screen",
        "\tHtcleoEikCorePreFactoryTrace(0xE306u, err);\n"
        "\tStoreAppLanguageL(apparcServer);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE307u, KErrNone);\n"
        "\t\n\t// Set default screen",
        "language checkpoints",
    )
    source = replace_once(
        source,
        "\t// Set default screen\n\tif (aCommandLine.IsDefaultScreenSet())",
        "\t// Set default screen\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE308u, err);\n"
        "\tif (aCommandLine.IsDefaultScreenSet())",
        "screen pre-checkpoint",
    )
    source = replace_once(
        source,
        "\t\tif (err)\n\t\t\tiEikEnvExtra->iDefaultScreenNumber = 0;\n\t\t}\n\t// Close AppArc server session",
        "\t\tif (err)\n\t\t\tiEikEnvExtra->iDefaultScreenNumber = 0;\n"
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE309u, err);\n"
        "\t// Close AppArc server session",
        "screen post-checkpoint",
    )
    source = replace_once(
        source,
        "\tCleanupStack::PopAndDestroy(&apparcServer);\n\t\n\t// Construct application environment",
        "\tCleanupStack::PopAndDestroy(&apparcServer);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE30Au, KErrNone);\n"
        "\t\n\t// Construct application environment",
        "AppArc close checkpoint",
    )
    source = replace_once(
        source,
        "\tconst TBool startAppInForeground = (command!=EApaCommandBackground && command!=EApaCommandBackgroundAndWithoutViews);\n\tConstructL(startAppInForeground, aCommandLine.ParentWindowGroupID());\n\t\t\n\t// Init instrumentation",
        "\tconst TBool startAppInForeground = (command!=EApaCommandBackground && command!=EApaCommandBackgroundAndWithoutViews);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE30Bu, startAppInForeground);\n"
        "\tConstructL(startAppInForeground, aCommandLine.ParentWindowGroupID());\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE30Cu, KErrNone);\n"
        "\t\t\n\t// Init instrumentation",
        "ConstructL checkpoints",
    )
    source = replace_once(
        source,
        "\tSetAppStartupInstrumentationEventIdBaseL(aCommandLine.AppStartupInstrumentationEventIdBase());",
        "\tHtcleoEikCorePreFactoryTrace(0xE30Du, KErrNone);\n"
        "\tSetAppStartupInstrumentationEventIdBaseL(aCommandLine.AppStartupInstrumentationEventIdBase());\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE30Eu, KErrNone);",
        "instrumentation checkpoints",
    )
    source = replace_once(
        source,
        "\tiProcess = CEikProcess::NewL(iFsSession, aCommandLine.ParentProcessId());",
        "\tHtcleoEikCorePreFactoryTrace(0xE30Fu, KErrNone);\n"
        "\tiProcess = CEikProcess::NewL(iFsSession, aCommandLine.ParentProcessId());\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE310u, iProcess ? KErrNone : KErrNoMemory);",
        "process checkpoints",
    )
    source = replace_once(
        source,
        "\t// Create the document object using the application factory\n\tCEikDocument& doc =",
        "\tHtcleoEikCorePreFactoryTrace(0xE311u, serverDifferentiator);\n"
        "\t// Create the document object using the application factory\n"
        "\tCEikDocument& doc =",
        "factory boundary",
    )
    return source


def verify(source: str, mmp: str, compatibility_source: str) -> None:
    stages = range(0xE300, 0xE312)
    frame_correlation = (
        "HTCLEO_EIKCORE_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1" in source
    )
    checks = {
        "marker": source.count(MARKER) == 1,
        "MatrixMenu durable marker": source.count(MENU_MARKER) == 1,
        "GCCE runtime offset compatibility": (
            compatibility_source.count(OFFSET_MARKER) == 1
            and "iBuf[maxLength]" not in compatibility_source
            and compatibility_source.count(
                "_FOFF(TUnlimitedFileName, iBuf) + "
                "maxLength * sizeof(TUint16)"
            ) == 1
        ),
        "property include": source.count("#include <e32property.h>") == 1,
        "required SID gates": (
            source.count("RProcess().SecureId().iId") >= 1
            and source.count(
                "sid == KHtcleoAknCapTraceCategory.iUid"
            ) == 1
            and source.count("sid == KHtcleoMatrixMenuSid") == 1
            and source.count(
                "KHtcleoMatrixMenuSid = 0x101f4cd2u"
            ) == 1
        ),
        "exact key": source.count("KHtcleoEikCoreTraceKey = 0x7f044301u") == 1,
        "all stages": all(
            source.count(f"0x{stage:04X}u") == 1 for stage in stages
        ),
        "single property write": source.count("(void)RProperty::Set(") == (
            2 if frame_correlation else 1
        ),
        "MatrixMenu durable writer": (
            source.count("C:\\\\Symbian3\\\\MENULOG.TXT") == 1
            and source.count("HtcleoEikCoreMatrixMenuTrace(") == 2
            and source.count(
                "0x4D4D0000u | (aStage & 0xffffu)"
            ) == 1
            and source.count("file.Write(record)") == (
                2
                if "HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE_V1"
                in source
                else 1
            )
            and source.count("file.Flush()") == 1
        ),
        "stock exported function": source.count(
            "EXPORT_C void CEikonEnv::ConstructAppFromCommandLineL("
        ) == 1,
        "stock factory call": source.count(
            "iProcess->AddNewDocumentL(aApplicationFactory)"
        ) == 1,
        "no AknCap durable IO": "AKNCAP.TXT" not in source,
        "no injected delay or display": (
            "User::After" not in HELPER and "HalFunction" not in HELPER
        ),
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/classicui/commonuisupport/uikon"
    source_path = component / "coresrc/EIKENV.CPP"
    compatibility_source_path = component / "coresrc/eikprivate.cpp"
    mmp_path = component / "group/EIKCORE.MMP"
    source = source_path.read_text(encoding="latin-1")
    compatibility_source = compatibility_source_path.read_text(
        encoding="latin-1"
    )
    mmp = mmp_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = install(source)
    elif MENU_MARKER not in source:
        source = replace_once(
            source,
            LEGACY_HELPER,
            HELPER,
            "MatrixMenu durable trace helper upgrade",
        )
    if OFFSET_MARKER not in compatibility_source:
        compatibility_source = replace_once(
            compatibility_source,
            "\tTUnlimitedFileName* const fakeFileName = STATIC_CAST(TUnlimitedFileName*, User::AllocLC(_FOFF(TUnlimitedFileName, iBuf[maxLength])));",
            "\t// HTCLEO_GCCE_UNLIMITED_FILENAME_OFFSET_V1\n"
            "\tconst TInt allocationSize = _FOFF(TUnlimitedFileName, iBuf) + "
            "maxLength * sizeof(TUint16);\n"
            "\tTUnlimitedFileName* const fakeFileName = STATIC_CAST("
            "TUnlimitedFileName*, User::AllocLC(allocationSize));",
            "GCCE runtime member offset",
        )
    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(source, mmp, compatibility_source)
    source_path.write_text(source, encoding="latin-1")
    compatibility_source_path.write_text(
        compatibility_source, encoding="latin-1"
    )
    mmp_path.write_text(mmp, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_PREFACTORY_TRACE=installed stages=E300-E311 "
        "matrixmenu=MENULOG-4D4DE300-E311-and-4D4DE400-E425"
    )


if __name__ == "__main__":
    main()
