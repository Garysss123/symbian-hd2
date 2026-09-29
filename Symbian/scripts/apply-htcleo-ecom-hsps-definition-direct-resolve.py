#!/usr/bin/env python3
"""Resolve the single HSPS definition-engine provider without default resolver."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HSPS_DEFINITION_DIRECT_RESOLVE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_session(text: str) -> str:
    if MARKER in text:
        return text
    return replace_once(
        text,
        "\tconst TBool htcleoHomeCreate =\n"
        "\t\t(aMessage.Function() == EGetImplementationCreationMethod &&\n"
        "\t\t uids[KInterfaceUidIndex].iUid == 0x2001952Cu);",
        "\t// HTCLEO_ECOM_HSPS_DEFINITION_DIRECT_RESOLVE_V1\n"
        "\tconst TBool htcleoHspsDefinitionResolve =\n"
        "\t\t((aMessage.Function() == EGetResolvedCreationMethod ||\n"
        "\t\t  aMessage.Function() == EGetCustomResolvedCreationMethod) &&\n"
        "\t\t uids[KInterfaceUidIndex].iUid == 0x200159C7u);\n"
        "\tconst TBool htcleoHomeCreate =\n"
        "\t\t(aMessage.Function() == EGetImplementationCreationMethod &&\n"
        "\t\t uids[KInterfaceUidIndex].iUid == 0x2001952Cu) ||\n"
        "\t\thtcleoHspsDefinitionResolve;",
        "resolved request arm",
    )


def patch_server(text: str) -> str:
    if MARKER in text:
        return text
    return replace_once(
        text,
        "void CEComServer::GetResolvedDllInfoL(  const TUid aInterfaceUid,\n"
        "\t\t\t\t\t\t\t\t\t\tconst TEComResolverParams& aAdditionalParameters,\n"
        "\t\t\t\t\t\t\t\t\t\tconst TUid aResolverUid,\n"
        "\t\t\t\t\t\t\t\t\t\tconst RExtendedInterfacesArray& aExtendedInterfaces,\n"
        "\t\t\t\t\t\t\t\t\t\tTEntry& aDllInfo,\n"
        "\t\t\t\t\t\t\t\t\t\tTUid& aDtor_Key,\n"
        "\t\t\t\t\t\t\t\t\t\tconst TClientRequest& aClientRequest)\n"
        "\t{\n"
        "\tCResolver* resolver = NULL;",
        "void CEComServer::GetResolvedDllInfoL(  const TUid aInterfaceUid,\n"
        "\t\t\t\t\t\t\t\t\t\tconst TEComResolverParams& aAdditionalParameters,\n"
        "\t\t\t\t\t\t\t\t\t\tconst TUid aResolverUid,\n"
        "\t\t\t\t\t\t\t\t\t\tconst RExtendedInterfacesArray& aExtendedInterfaces,\n"
        "\t\t\t\t\t\t\t\t\t\tTEntry& aDllInfo,\n"
        "\t\t\t\t\t\t\t\t\t\tTUid& aDtor_Key,\n"
        "\t\t\t\t\t\t\t\t\t\tconst TClientRequest& aClientRequest)\n"
        "\t{\n"
        "\t// HTCLEO_ECOM_HSPS_DEFINITION_DIRECT_RESOLVE_V1\n"
        "\tconst TDesC8& htcleoDataType = aAdditionalParameters.DataType();\n"
        "\tconst TBool htcleoHspsDefinition =\n"
        "\t\t(aInterfaceUid.iUid == 0x200159C7u &&\n"
        "\t\t aResolverUid == KDefaultResolverUid &&\n"
        "\t\t htcleoDataType.CompareF(_L8(\"hspsdefinitionengine\")) == 0);\n"
        "\tif(aInterfaceUid.iUid == 0x200159C7u)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomServerLog(0x0000F540u, KErrNone,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t\tHtcleoEcomServerLog(0x0000F541u, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\t\tHtcleoEcomServerLog(0x0000F542u,\n"
        "\t\t\thtcleoHspsDefinition ? KErrNone : KErrNotFound,\n"
        "\t\t\t(TUint32)htcleoDataType.Length());\n"
        "\t\t}\n"
        "\tif(htcleoHspsDefinition)\n"
        "\t\t{\n"
        "\t\tconst TUid htcleoImplementationUid = {0x200159C8};\n"
        "\t\taDtor_Key = htcleoImplementationUid;\n"
        "\t\tCImplementationInformation* htcleoImplInfo = NULL;\n"
        "\t\tHtcleoEcomServerLog(0x0000F543u, KErrNone,\n"
        "\t\t\t(TUint32)htcleoImplementationUid.iUid);\n"
        "\t\tconst TInt htcleoResult =\n"
        "\t\t\tiRegistryData->GetImplementationDllInfoForClientL(\n"
        "\t\t\t\taClientRequest, htcleoImplementationUid,\n"
        "\t\t\t\taInterfaceUid, aDllInfo, htcleoImplInfo, ETrue);\n"
        "\t\tHtcleoEcomServerLog(0x0000F544u, htcleoResult,\n"
        "\t\t\t(TUint32)htcleoImplInfo);\n"
        "\t\tUser::LeaveIfError(htcleoResult);\n"
        "\t\tHtcleoEcomServerLog(0x0000F545u, KErrNone,\n"
        "\t\t\t(TUint32)aDllInfo.iName.Length());\n"
        "\t\treturn;\n"
        "\t\t}\n"
        "\tif(aInterfaceUid.iUid == 0x200159C7u)\n"
        "\t\tHtcleoEcomServerLog(0x0000F546u, KErrNone, 0u);\n"
        "\tCResolver* resolver = NULL;",
        "exact HSPS resolver",
    )


def verify(session: str, server: str) -> None:
    joined = session + server
    checks = {
        "marker coverage": joined.count(MARKER) == 2,
        "interface and implementation": (
            joined.count("0x200159C7u") >= 3
            and server.count("0x200159C8") == 1
            and server.count('hspsdefinitionengine') == 1
        ),
        "resolved arm": (
            session.count("htcleoHspsDefinitionResolve") >= 2
            and session.count("EGetResolvedCreationMethod") >= 2
        ),
        "stages": all(
            server.count(f"0x0000F{stage:03X}u") == 1
            for stage in range(0x540, 0x547)
        ),
        "real registry and security": (
            server.count("GetImplementationDllInfoForClientL(") >= 2
            and server.count("htcleoImplInfo, ETrue") == 1
            and server.count("User::LeaveIfError(htcleoResult)") == 1
        ),
        "stock resolver retained": (
            server.count("CRegistryResolveTransaction::NewL") >= 1
            and server.count("IdentifyImplementationL") >= 1
        ),
        "no fake result or delay": all(
            token not in joined
            for token in ("htcleoResult = KErrNone", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HSPS definition direct-resolve verification failed: " +
            ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    session_path = frame / "EComServerSession.cpp"
    server_path = frame / "EComServer.cpp"
    session = session_path.read_text(encoding="utf-8")
    server = server_path.read_text(encoding="utf-8")
    session = patch_session(session)
    server = patch_server(server)
    verify(session, server)
    session_path.write_text(session, encoding="utf-8")
    server_path.write_text(server, encoding="utf-8")
    print(
        "HTCLEO_ECOM_HSPS_DEFINITION_RESOLVE="
        "interface200159c7-to-real-impl200159c8-security-checked"
    )


if __name__ == "__main__":
    main()
