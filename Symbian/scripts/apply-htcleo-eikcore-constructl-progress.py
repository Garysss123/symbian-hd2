#!/usr/bin/env python3
"""Trace CEikonEnv::ConstructL without changing its control flow.

The existing eikcore helper sends AknCapServer stages through one fail-open
property write and MatrixMenu stages through its SID-gated durable MENULOG
writer. This transform only adds returning boundaries around stock calls.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_AKNCAP_CONSTRUCTL_TRACE_V2"
HELPER = "HtcleoEikCorePreFactoryTrace"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "EXPORT_C void CEikonEnv::ConstructL(TBool aInitialFocusState, TInt aWindowGroupID)\n"
        "\t{\n"
        "\t// iEikEnvExtra might have been created",
        "EXPORT_C void CEikonEnv::ConstructL(TBool aInitialFocusState, TInt aWindowGroupID)\n"
        "\t{\n"
        "\t// HTCLEO_EIKCORE_AKNCAP_CONSTRUCTL_TRACE_V2\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE400u, aInitialFocusState);\n"
        "\t// iEikEnvExtra might have been created",
        "ConstructL entry",
    )
    source = replace_once(
        source,
        "\tif(!iEikEnvExtra)\n"
        "\t\tiEikEnvExtra = CEikEnvExtra::NewL(*this);\n"
        "\t\n"
        "\tLafEnv::HandleExtensionEventL(*this, LafEnv::ELafEnvPreCoeEnvConstructL );\n"
        "\tCCoeEnv::ConstructL(aInitialFocusState, iEikEnvExtra->iDefaultScreenNumber, aWindowGroupID); // Added May 04 - support for Multiple screens.\n"
        "\tRApaLsSession::SetFsSessionL(FsSession());\n"
        "\tLafEnv::HandleExtensionEventL(*this, LafEnv::ELafEnvPostCoeEnvConstructL );\n"
        "\tconst TBool isEiksrv = IsEiksrvThread();",
        "\tif(!iEikEnvExtra)\n"
        "\t\t{\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE401u, KErrNone);\n"
        "\t\tiEikEnvExtra = CEikEnvExtra::NewL(*this);\n"
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE402u, iEikEnvExtra->iDefaultScreenNumber);\n"
        "\t\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE403u, KErrNone);\n"
        "\tLafEnv::HandleExtensionEventL(*this, LafEnv::ELafEnvPreCoeEnvConstructL );\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE404u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE405u, iEikEnvExtra->iDefaultScreenNumber);\n"
        "\tCCoeEnv::ConstructL(aInitialFocusState, iEikEnvExtra->iDefaultScreenNumber, aWindowGroupID); // Added May 04 - support for Multiple screens.\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE406u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE407u, KErrNone);\n"
        "\tRApaLsSession::SetFsSessionL(FsSession());\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE408u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE409u, KErrNone);\n"
        "\tLafEnv::HandleExtensionEventL(*this, LafEnv::ELafEnvPostCoeEnvConstructL );\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE40Au, KErrNone);\n"
        "\tconst TBool isEiksrv = IsEiksrvThread();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE40Bu, isEiksrv);",
        "early ConstructL calls",
    )
    source = replace_once(
        source,
        "\tif(!isEiksrv)\n"
        "\t\tUser::SetPriorityControl(ETrue);\n"
        "\t\n"
        "\tif (isEiksrv)",
        "\tif(!isEiksrv)\n"
        "\t\tUser::SetPriorityControl(ETrue);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE40Cu, isEiksrv);\n"
        "\t\n"
        "\tif (isEiksrv)",
        "priority branch",
    )
    source = replace_once(
        source,
        "\t\t}\n"
        "\t\n"
        "\tInitColorSchemeL();\n"
        "\tLoadParserListL();\n"
        "\tiLafEnv = new(ELeave) CEikLafEnv();\n"
        "\tiEditableControlStandardHeight = LafEnv::EditableControlStandardHeight(*iLafEnv);\n"
        "\tInitSystemBitmapsL();\n"
        "\tiWgName = CApaWindowGroupName::NewL(iWsSession);\n"
        "\tReadResourceL(iNudgeChars,R_EIK_TBUF_NUDGE_CHARS);\n"
        "\tiVirtualCursor.SetCursorStateL(TEikVirtualCursor::EOff, *this);\n"
        "\tLoadLibrariesL();",
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE40Du, isEiksrv ? (TInt)iEikEnvExtra->iAppLanguage : KErrNotFound);\n"
        "\t\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE40Eu, KErrNone);\n"
        "\tInitColorSchemeL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE40Fu, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE410u, KErrNone);\n"
        "\tLoadParserListL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE411u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE412u, KErrNone);\n"
        "\tiLafEnv = new(ELeave) CEikLafEnv();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE413u, iLafEnv ? KErrNone : KErrNoMemory);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE414u, KErrNone);\n"
        "\tiEditableControlStandardHeight = LafEnv::EditableControlStandardHeight(*iLafEnv);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE415u, iEditableControlStandardHeight);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE416u, KErrNone);\n"
        "\tInitSystemBitmapsL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE417u, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE418u, KErrNone);\n"
        "\tiWgName = CApaWindowGroupName::NewL(iWsSession);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE419u, iWgName ? KErrNone : KErrNoMemory);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE41Au, KErrNone);\n"
        "\tReadResourceL(iNudgeChars,R_EIK_TBUF_NUDGE_CHARS);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE41Bu, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE41Cu, KErrNone);\n"
        "\tiVirtualCursor.SetCursorStateL(TEikVirtualCursor::EOff, *this);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE41Du, KErrNone);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE41Eu, KErrNone);\n"
        "\tLoadLibrariesL();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE41Fu, KErrNone);",
        "middle ConstructL calls",
    )
    source = replace_once(
        source,
        "\tiLogicalBorderProxy = new(ELeave) CEikLogicalBorderProxy();\n"
        "\tGulTls::SetLogicalBorder(iLogicalBorderProxy);\n"
        "\t\n"
        "\tiOOMErrorText = AllocReadResourceL(iSystemResourceFileOffset+1-KErrNoMemory);\n"
        "\tInitInfoMsgL(); // CEikonEnv::HandleError relies on this being the last thing to be constructed (it uses it to test whether it has been fully constructed or not, and thus whether the infra-structure is in place so that it can actually handle the error)\t\n"
        "\t}",
        "\tHtcleoEikCorePreFactoryTrace(0xE420u, KErrNone);\n"
        "\tiLogicalBorderProxy = new(ELeave) CEikLogicalBorderProxy();\n"
        "\tGulTls::SetLogicalBorder(iLogicalBorderProxy);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE421u, iLogicalBorderProxy ? KErrNone : KErrNoMemory);\n"
        "\t\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE422u, KErrNone);\n"
        "\tiOOMErrorText = AllocReadResourceL(iSystemResourceFileOffset+1-KErrNoMemory);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE423u, iOOMErrorText ? KErrNone : KErrNoMemory);\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE424u, KErrNone);\n"
        "\tInitInfoMsgL(); // CEikonEnv::HandleError relies on this being the last thing to be constructed (it uses it to test whether it has been fully constructed or not, and thus whether the infra-structure is in place so that it can actually handle the error)\t\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE425u, KErrNone);\n"
        "\t}",
        "ConstructL tail",
    )
    return source


def verify(source: str) -> None:
    stages = range(0xE400, 0xE426)
    frame_correlation = (
        "HTCLEO_EIKCORE_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1" in source
    )
    checks = {
        "marker": source.count(MARKER) == 1,
        "existing helper": source.count(
            "static void HtcleoEikCorePreFactoryTrace("
        ) == 1,
        "existing MatrixMenu durable helper": (
            source.count(
                "HTCLEO_EIKCORE_MATRIXMENU_PREFACTORY_DURABLE_LOG_V2"
            ) == 1
            and source.count("sid == KHtcleoAknCapTraceCategory.iUid") == 1
            and source.count("sid == KHtcleoMatrixMenuSid") == 1
        ),
        "all ConstructL stages": all(
            source.count(f"0x{stage:04X}u") == 1 for stage in stages
        ),
        "exact overload": source.count(
            "EXPORT_C void CEikonEnv::ConstructL("
            "TBool aInitialFocusState, TInt aWindowGroupID)"
        ) == 1,
        "single property write": source.count("(void)RProperty::Set(") == (
            2 if frame_correlation else 1
        ),
        "no AknCap durable IO": "AKNCAP.TXT" not in source,
        "no injected delay": "User::After" not in source,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print("HTCLEO_EIKCORE_CONSTRUCTL_TRACE=installed stages=E400-E425")


if __name__ == "__main__":
    main()
