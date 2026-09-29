#!/usr/bin/env python3
"""Trace the real HSPS ROM InstallSkeleton path after lazy parser recovery."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HSPS_INSTALL_SKELETON_TRACE_V1"
HANDOFF_MARKER = "HTCLEO_HSPS_INSTALL_HANDOFF_TRACE_V1"
ROM_MARKER = "HTCLEO_HSPS_ROMINSTALLER_HANDOFF_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_once(
        text,
        "       // Defaults\n"
        "       ThspsServiceCompletedMessage ret = EhspsInstallPhaseSuccess;",
        "       // HTCLEO_HSPS_INSTALL_SKELETON_TRACE_V1\n"
        "       HtcleoHspsServerLog(0x485813A0u, KErrNone,\n"
        "           (TUint32)iInstallationPhase);\n"
        "       // Defaults\n"
        "       ThspsServiceCompletedMessage ret = EhspsInstallPhaseSuccess;",
        "phase entry",
    )
    text = replace_once(
        text,
        "                TRAP( errorCode, CleanupL( *iOdt ) );",
        "                HtcleoHspsServerLog(0x485813A1u, KErrNone,\n"
        "                    (TUint32)iInstallationPhase);\n"
        "                TRAP( errorCode, CleanupL( *iOdt ) );\n"
        "                HtcleoHspsServerLog(0x485813A2u, errorCode,\n"
        "                    (TUint32)iInstallationPhase);",
        "cleanup phase",
    )
    text = replace_once(
        text,
        "               TRAP( errorCode, InstallSkeletonL( ret ) );",
        "               HtcleoHspsServerLog(0x485813A3u, KErrNone,\n"
        "                   (TUint32)iInstallationPhase);\n"
        "               TRAP( errorCode, InstallSkeletonL( ret ) );\n"
        "               HtcleoHspsServerLog(0x485813A4u, errorCode,\n"
        "                   ((TUint32)iInstallationPhase << 16) |\n"
        "                   ((TUint32)ret & 0xffffu));",
        "skeleton phase",
    )
    text = replace_once(
        text,
        "       if ( iHeaderData )\n",
        "       HtcleoHspsServerLog(0x485813A5u, (TInt)ret,\n"
        "           (TUint32)iInstallationPhase);\n"
        "       if ( iHeaderData )\n",
        "phase result",
    )

    text = replace_once(
        text,
        "    iOdt->SetOdtLanguage( ELangNone );\n",
        "    HtcleoHspsServerLog(0x485813C0u, KErrNone, 0u);\n"
        "    iOdt->SetOdtLanguage( ELangNone );\n"
        "    HtcleoHspsServerLog(0x485813C1u, KErrNone, 0u);\n",
        "skeleton language",
    )
    text = replace_once(
        text,
        "    // Parse DOM\n"
        "    ParseDocumentL( *iOdt );",
        "    // Parse DOM\n"
        "    HtcleoHspsServerLog(0x485813C2u, KErrNone, 0u);\n"
        "    ParseDocumentL( *iOdt );\n"
        "    HtcleoHspsServerLog(0x485813C3u, KErrNone,\n"
        "        (TUint32)iOdt->DomDocument().DomNodeCount());",
        "parse document",
    )
    text = replace_once(
        text,
        "    SetODTAsResourceL( *iOdt );",
        "    SetODTAsResourceL( *iOdt );\n"
        "    HtcleoHspsServerLog(0x485813C4u, KErrNone,\n"
        "        (TUint32)iOdt->ResourceCount());",
        "odt resource",
    )
    text = replace_once(
        text,
        "    User::LeaveIfError( iDefinitionRepository.SetResourceListL( *iOdt, *iResourceList ) );",
        "    TInt htcleoResourceListError =\n"
        "        iDefinitionRepository.SetResourceListL( *iOdt, *iResourceList );\n"
        "    HtcleoHspsServerLog(0x485813C5u, htcleoResourceListError,\n"
        "        (TUint32)iResourceList->Count());\n"
        "    User::LeaveIfError( htcleoResourceListError );",
        "resource list",
    )
    text = replace_once(
        text,
        "    hspsServerUtil::GenerateConfigurationAttributesL( *iOdt );",
        "    hspsServerUtil::GenerateConfigurationAttributesL( *iOdt );\n"
        "    HtcleoHspsServerLog(0x485813C6u, KErrNone, 0u);",
        "configuration attributes",
    )
    text = replace_once(
        text,
        "    if ( iTrustedInstallation )\n",
        "    HtcleoHspsServerLog(0x485813C7u, KErrNone,\n"
        "        (TUint32)iTrustedInstallation);\n"
        "    if ( iTrustedInstallation )\n",
        "max-child boundary",
    )
    text = replace_once(
        text,
        "    iOdt->SetOdtLanguage( ELangTest );",
        "    HtcleoHspsServerLog(0x485813C8u, KErrNone, 0u);\n"
        "    iOdt->SetOdtLanguage( ELangTest );",
        "confirmed-state boundary",
    )
    text = replace_once(
        text,
        "    hspsServerUtil::GenerateObjectAttributesL( *iOdt );",
        "    hspsServerUtil::GenerateObjectAttributesL( *iOdt );\n"
        "    HtcleoHspsServerLog(0x485813C9u, KErrNone,\n"
        "        (TUint32)iOdt->ResourceCount());",
        "object attributes",
    )
    text = replace_once(
        text,
        "    iThemeServer.LocalizeL(\n"
        "        *iDefEngine,\n"
        "        *iOdt );",
        "    HtcleoHspsServerLog(0x485813CAu, KErrNone, 0u);\n"
        "    iThemeServer.LocalizeL(\n"
        "        *iDefEngine,\n"
        "        *iOdt );\n"
        "    HtcleoHspsServerLog(0x485813CBu, KErrNone, 0u);",
        "localization",
    )
    text = replace_once(
        text,
        "    iDefinitionRepository.SetOdtL( *iOdt );  \n",
        "    HtcleoHspsServerLog(0x485813CCu, KErrNone, 0u);\n"
        "    iDefinitionRepository.SetOdtL( *iOdt );\n"
        "    HtcleoHspsServerLog(0x485813CDu, KErrNone, 0u);\n",
        "repository ODT",
    )

    text = replace_once(
        text,
        "    ChspsDefinitionEngineInterface::TError t_error;  \n",
        "    ChspsDefinitionEngineInterface::TError t_error;\n"
        "    HtcleoHspsServerLog(0x485813D0u, KErrNone,\n"
        "        (TUint32)aOdt.ThemeUid());\n",
        "parse entry",
    )
    text = replace_once(
        text,
        "    t_error = iDefEngine->CreateDOM( iFsSession, *iXmlFile, aOdt );\n"
        "          \n"
        "    deferror = t_error.iDefEngError + t_error.iSubComponentError;",
        "    HtcleoHspsServerLog(0x485813D1u, KErrNone,\n"
        "        iXmlFile ? (TUint32)iXmlFile->Length() : 0u);\n"
        "    t_error = iDefEngine->CreateDOM( iFsSession, *iXmlFile, aOdt );\n"
        "    HtcleoHspsServerLog(0x485813D2u, t_error.iDefEngError,\n"
        "        (TUint32)t_error.iSubComponentError);\n"
        "          \n"
        "    deferror = t_error.iDefEngError + t_error.iSubComponentError;",
        "definition-engine call",
    )
    text = replace_once(
        text,
        "        TInt domNodeCount = domDocument.DomNodeCount();",
        "        TInt domNodeCount = domDocument.DomNodeCount();\n"
        "        HtcleoHspsServerLog(0x485813D3u, KErrNone,\n"
        "            (TUint32)domNodeCount);",
        "DOM success",
    )
    text = replace_once(
        text,
        "        errorCode = KErrCorrupt;\n"
        "        iResult->iXuikonError = errorCode;",
        "        errorCode = KErrCorrupt;\n"
        "        HtcleoHspsServerLog(0x485813D4u, errorCode,\n"
        "            ((TUint32)(TUint16)t_error.iDefEngError << 16) |\n"
        "            (TUint32)(TUint16)t_error.iSubComponentError);\n"
        "        iResult->iXuikonError = errorCode;",
        "DOM error",
    )
    return text


def install_handoff(text: str) -> str:
    if HANDOFF_MARKER in text:
        text = text.replace(
            "    HtcleoHspsServerLog(0x485813B6u, KErrNone,\n"
            "        (TUint32)iRequestStatus->Int());",
            "    HtcleoHspsServerLog(0x485813B6u,\n"
            "        iRequestStatus ? iRequestStatus->Int() : KErrNone,\n"
            "        (TUint32)(iRequestStatus != NULL));",
            1,
        )
        return text
    text = replace_once(
        text,
        "void ChspsInstallationHandler::hspsInstallNextPhaseL( \n"
        "        TDes8& aHeaderData, \n"
        "        TRequestStatus& aRequestStatus )\n"
        "    {\n"
        "    ThspsServiceCompletedMessage ret = EhspsServiceNotSupported;",
        "void ChspsInstallationHandler::hspsInstallNextPhaseL( \n"
        "        TDes8& aHeaderData, \n"
        "        TRequestStatus& aRequestStatus )\n"
        "    {\n"
        "    // HTCLEO_HSPS_INSTALL_HANDOFF_TRACE_V1\n"
        "    HtcleoHspsServerLog(0x485813B0u, KErrNone,\n"
        "        (TUint32)iInstallationPhase);\n"
        "    ThspsServiceCompletedMessage ret = EhspsServiceNotSupported;",
        "async wrapper entry",
    )
    text = replace_once(
        text,
        "    iInstallationMode = EAsynchronousObject;\n"
        "    iRequestStatus = &aRequestStatus;\n"
        "    *iRequestStatus = KRequestPending;",
        "    iInstallationMode = EAsynchronousObject;\n"
        "    HtcleoHspsServerLog(0x485813B1u, KErrNone,\n"
        "        (TUint32)iInstallationMode);\n"
        "    iRequestStatus = &aRequestStatus;\n"
        "    *iRequestStatus = KRequestPending;\n"
        "    HtcleoHspsServerLog(0x485813B2u, iRequestStatus->Int(),\n"
        "        (TUint32)iInstallationPhase);",
        "async wrapper status",
    )
    text = replace_once(
        text,
        "    ret = hspsInstallNextPhaseL( aHeaderData );\n"
        "    CompleteRequestL( ret );",
        "    HtcleoHspsServerLog(0x485813B3u, KErrNone,\n"
        "        (TUint32)iInstallationPhase);\n"
        "    ret = hspsInstallNextPhaseL( aHeaderData );\n"
        "    HtcleoHspsServerLog(0x485813B4u, (TInt)ret,\n"
        "        (TUint32)iInstallationPhase);\n"
        "    HtcleoHspsServerLog(0x485813B5u, KErrNone,\n"
        "        (TUint32)iRequestStatus->Int());\n"
        "    CompleteRequestL( ret );\n"
        "    HtcleoHspsServerLog(0x485813B6u,\n"
        "        iRequestStatus ? iRequestStatus->Int() : KErrNone,\n"
        "        (TUint32)(iRequestStatus != NULL));",
        "async wrapper completion",
    )
    return text


def install_rom(text: str) -> str:
    if ROM_MARKER in text:
        return text
    text = replace_once(
        text,
        "    HtcleoHspsServerLog(0x48581359u, iStatus.Int(),\n"
        "        (TUint32)iRet);\n"
        "    iRet = (ThspsServiceCompletedMessage)iStatus.Int();",
        "    HtcleoHspsServerLog(0x48581359u, iStatus.Int(),\n"
        "        (TUint32)iRet);\n"
        "    // HTCLEO_HSPS_ROMINSTALLER_HANDOFF_TRACE_V1\n"
        "    HtcleoHspsServerLog(0x4858135Bu, iStatus.Int(),\n"
        "        (TUint32)iRet);\n"
        "    iRet = (ThspsServiceCompletedMessage)iStatus.Int();\n"
        "    HtcleoHspsServerLog(0x4858135Cu, (TInt)iRet,\n"
        "        (TUint32)IsActive());",
        "RunL status handoff",
    )
    text = replace_once(
        text,
        "        case EhspsInstallPhaseSuccess:\n"
        "        \t{\n"
        "        \t// Execute next phase of the installation\n"
        "            if ( !IsActive() )\n"
        "                {                \n"
        "                SetActive();\n"
        "                iInstallationHandler->hspsInstallNextPhaseL( iHeaderData, iStatus  );\n"
        "                }",
        "        case EhspsInstallPhaseSuccess:\n"
        "        \t{\n"
        "        \t// Execute next phase of the installation\n"
        "            HtcleoHspsServerLog(0x4858135Du, (TInt)iRet,\n"
        "                (TUint32)IsActive());\n"
        "            if ( !IsActive() )\n"
        "                {\n"
        "                HtcleoHspsServerLog(0x4858135Eu, iStatus.Int(),\n"
        "                    (TUint32)iRet);\n"
        "                SetActive();\n"
        "                HtcleoHspsServerLog(0x4858135Fu, iStatus.Int(),\n"
        "                    (TUint32)IsActive());\n"
        "                HtcleoHspsServerLog(0x48581390u, KErrNone,\n"
        "                    (TUint32)iRet);\n"
        "                iInstallationHandler->hspsInstallNextPhaseL( iHeaderData, iStatus );\n"
        "                HtcleoHspsServerLog(0x48581391u, iStatus.Int(),\n"
        "                    (TUint32)iRet);\n"
        "                }",
        "RunL phase-success handoff",
    )
    return text


def verify(text: str) -> None:
    stages = [
        0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5,
        0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7,
        0xC8, 0xC9, 0xCA, 0xCB, 0xCC, 0xCD,
        0xD0, 0xD1, 0xD2, 0xD3, 0xD4,
    ]
    checks = {
        "marker": text.count(MARKER) == 1,
        "stages": all(text.count(f"0x485813{stage:02X}u") == 1 for stage in stages),
        "real operations retained": all(
            text.count(token) >= 1
            for token in (
                "ParseDocumentL( *iOdt )",
                "SetODTAsResourceL( *iOdt )",
                "SetResourceListL( *iOdt, *iResourceList )",
                "GenerateConfigurationAttributesL( *iOdt )",
                "GenerateObjectAttributesL( *iOdt )",
                "iThemeServer.LocalizeL(",
                "iDefinitionRepository.SetOdtL( *iOdt )",
                "iDefEngine->CreateDOM( iFsSession, *iXmlFile, aOdt )",
            )
        ),
        "no bypass": all(
            token not in text
            for token in ("User::After", "RTimer", "EhspsInstallThemeSuccess; // HTCLEO")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS skeleton trace verification failed: " + ", ".join(failed))


def verify_handoff(text: str) -> None:
    stages = list(range(0xB0, 0xB7))
    checks = {
        "marker": text.count(HANDOFF_MARKER) == 1,
        "stages": all(text.count(f"0x485813{stage:02X}u") == 1 for stage in stages),
        "real call retained": text.count("ret = hspsInstallNextPhaseL( aHeaderData );") == 1,
        "real completion retained": text.count("CompleteRequestL( ret );") >= 1,
        "post-complete pointer guarded": (
            text.count("iRequestStatus ? iRequestStatus->Int() : KErrNone") == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS handoff trace verification failed: " + ", ".join(failed))


def verify_rom(text: str) -> None:
    stages = (0x5B, 0x5C, 0x5D, 0x5E, 0x5F, 0x90, 0x91)
    checks = {
        "marker": text.count(ROM_MARKER) == 1,
        "stages": all(text.count(f"0x485813{stage:02X}u") == 1 for stage in stages),
        "real SetActive retained": text.count("SetActive();") >= 1,
        "real phase call retained": (
            text.count("iInstallationHandler->hspsInstallNextPhaseL( iHeaderData, iStatus") >= 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS ROM handoff trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/homescreenpluginsrv/hspsmanager"
        / "src/hspsinstallationhandler.cpp"
    )
    text = install(path.read_text(encoding="utf-8"))
    text = install_handoff(text)
    verify(text)
    verify_handoff(text)
    path.write_text(text, encoding="utf-8")
    rom_path = (
        args.root
        / "sf/mw/homescreensrv/homescreenpluginsrv/hspsmanager"
        / "src/hspsrominstaller.cpp"
    )
    rom_text = install_rom(rom_path.read_text(encoding="utf-8"))
    verify_rom(rom_text)
    rom_path.write_text(rom_text, encoding="utf-8")
    print(
        "HTCLEO_HSPS_INSTALL_SKELETON_TRACE="
        "HSPSSRV-1m-4858135b-5f-90-91-b0-b6-a0-a5-c0-cd-d0-d4-behavior-neutral"
    )
    print(
        "HTCLEO_HSPS_POSTCOMPLETE_POINTER="
        "guarded-null-after-user-requestcomplete"
    )


if __name__ == "__main__":
    main()
