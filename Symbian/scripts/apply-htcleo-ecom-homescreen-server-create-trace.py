#!/usr/bin/env python3
"""Trace HomeScreen implementation 0x2001952C inside ecomserver.exe."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1"
IMPL_UID = "0x2001952Cu"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_session(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        """\tServiceL(msg);
\tif(htcleoTrace)
\t\tHtcleoEcomServerLog(0x0000F322u, KErrNone, 0u);""",
        """\tServiceL(msg);
\tHtcleoEcomServerLog(0x0000F50Fu, KErrNone,
\t\t(TUint32)aMessage.Function());
\tif(htcleoTrace)
\t\tHtcleoEcomServerLog(0x0000F322u, KErrNone, 0u);""",
        "outer ServiceL return",
    )
    text = replace_once(
        text,
        """\tcase EGetCustomResolvedCreationMethod:
RECORD_CLIENT_REQUEST_START_TIMER_RESULT(EEComCreateRequestType, Server().GetCurrentStartupState());
\t\tDoGetResolvedImplementationL(aMessage);
RECORD_CLIENT_REQUEST_END_TIMER_RESULT;""",
        """\tcase EGetCustomResolvedCreationMethod:
RECORD_CLIENT_REQUEST_START_TIMER_RESULT(EEComCreateRequestType, Server().GetCurrentStartupState());
\t\tHtcleoEcomServerLog(0x0000F510u, KErrNone,
\t\t\t(TUint32)aMessage.Function());
\t\tDoGetResolvedImplementationL(aMessage);
\t\tHtcleoEcomServerLog(0x0000F511u, KErrNone,
\t\t\t(TUint32)aMessage.Function());
RECORD_CLIENT_REQUEST_END_TIMER_RESULT;""",
        "create dispatch",
    )
    text = replace_once(
        text,
        """void CEComServerSession::DoGetResolvedImplementationL(const TClientRequest& aMessage)
\t{
\t// Unpack the client supplied parameters""",
        """void CEComServerSession::DoGetResolvedImplementationL(const TClientRequest& aMessage)
\t{
\t// HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1
\t// Unpack the client supplied parameters""",
        "DoGet marker",
    )
    text = replace_once(
        text,
        """\taMessage.ReadL(KIPCParameterUids, uidsPkg);

\t// Now rebuild the TEComResolverParams""",
        """\taMessage.ReadL(KIPCParameterUids, uidsPkg);
\tconst TBool htcleoHomeCreate =
\t\t(aMessage.Function() == EGetImplementationCreationMethod &&
\t\t uids[KInterfaceUidIndex].iUid == 0x2001952Cu);
\tif(htcleoHomeCreate)
\t\t{
\t\tHtcleoEcomServerArm();
\t\tHtcleoEcomServerLog(0x0000F500u, KErrNone,
\t\t\t(TUint32)aMessage.Function());
\t\tHtcleoEcomServerLog(0x0000F501u, KErrNone,
\t\t\t(TUint32)uids[KInterfaceUidIndex].iUid);
\t\tHtcleoEcomServerLog(0x0000F502u, KErrNone,
\t\t\t(TUint32)uids[KResolverUidIndex].iUid);
\t\t}

\t// Now rebuild the TEComResolverParams""",
        "HomeScreen request arm",
    )
    text = replace_once(
        text,
        """\tCleanupClosePushL(extendedInterfaces);
\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);
    if(matchStr.Length()>0)""",
        """\tCleanupClosePushL(extendedInterfaces);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F503u, KErrNone, 0u);
\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F504u,
\t\t\tmatchStr.Length(), (TUint32)extendedInterfaces.Count());
    if(matchStr.Length()>0)""",
        "request unpack",
    )
    text = replace_once(
        text,
        """\tTUid dtorIdKey(KNullUid);
\tTEntry loadInfo;
\t
\tswitch(aMessage.Function())""",
        """\tTUid dtorIdKey(KNullUid);
\tTEntry loadInfo;
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F505u, KErrNone, 0u);
\t
\tswitch(aMessage.Function())""",
        "resolver switch",
    )
    text = replace_once(
        text,
        "\t\tcase EGetImplementationCreationMethod:\n",
        "\t\tcase EGetImplementationCreationMethod:\n"
        "\t\t\tif(htcleoHomeCreate)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F506u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)uids[KInterfaceUidIndex].iUid);\n",
        "direct implementation lookup entry",
    )
    text = replace_once(
        text,
        "\t\t\tbreak;\n\t\tcase EGetResolvedCreationMethod:\n",
        "\t\t\tif(htcleoHomeCreate)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F507u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)loadInfo.iName.Length());\n"
        "\t\t\tbreak;\n\t\tcase EGetResolvedCreationMethod:\n",
        "direct implementation lookup return",
    )
    text = replace_once(
        text,
        """\tCleanupStack::PopAndDestroy(&extendedInterfaces);
\tCleanupStack::PopAndDestroy(&matchStr);
\t
// ??? Compile time assert""",
        """\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F508u, KErrNone,
\t\t\t(TUint32)dtorIdKey.iUid);
\tCleanupStack::PopAndDestroy(&extendedInterfaces);
\tCleanupStack::PopAndDestroy(&matchStr);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F509u, KErrNone,
\t\t\t(TUint32)loadInfo.iName.Length());
\t
// ??? Compile time assert""",
        "lookup cleanup",
    )
    text = replace_once(
        text,
        """\tTPckg<TEntry> result(loadInfo);
\t
\taMessage.WriteL(KIPCReturnParameterCreationMethodPtr, result);
\t// Next the destruction identification uid""",
        """\tTPckg<TEntry> result(loadInfo);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F50Au, KErrNone,
\t\t\t(TUint32)result.Length());
\t
\taMessage.WriteL(KIPCReturnParameterCreationMethodPtr, result);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F50Bu, KErrNone,
\t\t\t(TUint32)loadInfo.iName.Length());
\t// Next the destruction identification uid""",
        "creation-method reply",
    )
    text = replace_once(
        text,
        """\tTPckg<TUidType> dtorIdKeyPkg(type);
\t
\taMessage.WriteL(KIPCReturnParameterUidsPtr, dtorIdKeyPkg);
\t}""",
        """\tTPckg<TUidType> dtorIdKeyPkg(type);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F50Cu, KErrNone,
\t\t\t(TUint32)dtorIdKey.iUid);
\t
\taMessage.WriteL(KIPCReturnParameterUidsPtr, dtorIdKeyPkg);
\tif(htcleoHomeCreate)
\t\tHtcleoEcomServerLog(0x0000F50Du, KErrNone,
\t\t\t(TUint32)dtorIdKey.iUid);
\t}""",
        "destruction-key reply",
    )
    return text


def patch_server(text: str) -> str:
    if MARKER in text:
        return text
    old = """void CEComServer::GetResolvedDllInfoL(\tconst TUid aImplementationUid,
\t\t\t\t\t\t\t\t\t\tTEntry& aDllInfo,
\t\t\t\t\t\t\t\t\t\tTUid& aDtor_Key,
\t\t\t\t\t\t\t\t\t\tconst TClientRequest& aClientRequest)
\t{
\t// No resolution to do create directly.
\taDtor_Key = aImplementationUid;
\tCImplementationInformation* implInfo = NULL;
\tTUid dummyUid={0x00000000};
\t//We need to do the security check for the case that implementationUid is known.
\t//if implementationUid is unknown, the security check will be done in ListImplementationsL.
\tUser::LeaveIfError(iRegistryData->GetImplementationDllInfoForClientL(
\t\taClientRequest, aImplementationUid, dummyUid, aDllInfo, implInfo, ETrue));
\t}"""
    new = """void CEComServer::GetResolvedDllInfoL(\tconst TUid aImplementationUid,
\t\t\t\t\t\t\t\t\t\tTEntry& aDllInfo,
\t\t\t\t\t\t\t\t\t\tTUid& aDtor_Key,
\t\t\t\t\t\t\t\t\t\tconst TClientRequest& aClientRequest)
\t{
\t// HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1
\tHtcleoEcomServerLog(0x0000F520u, KErrNone,
\t\t(TUint32)aImplementationUid.iUid);
\t// No resolution to do create directly.
\taDtor_Key = aImplementationUid;
\tHtcleoEcomServerLog(0x0000F521u, KErrNone,
\t\t(TUint32)aDtor_Key.iUid);
\tCImplementationInformation* implInfo = NULL;
\tTUid dummyUid={0x00000000};
\t//We need to do the security check for the case that implementationUid is known.
\t//if implementationUid is unknown, the security check will be done in ListImplementationsL.
\tHtcleoEcomServerLog(0x0000F522u, KErrNone, 0u);
\tconst TInt htcleoRegistryResult =
\t\tiRegistryData->GetImplementationDllInfoForClientL(
\t\t\taClientRequest, aImplementationUid, dummyUid,
\t\t\taDllInfo, implInfo, ETrue);
\tHtcleoEcomServerLog(0x0000F523u, htcleoRegistryResult,
\t\t(TUint32)implInfo);
\tUser::LeaveIfError(htcleoRegistryResult);
\tHtcleoEcomServerLog(0x0000F524u, KErrNone,
\t\t(TUint32)aDllInfo.iName.Length());
\t}"""
    return replace_once(text, old, new, "server direct lookup")


def patch_registry(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        """\t{
\taImplInfo = NULL;
\tTInt res = KErrNotFound;
\tCImplementationData* implData;""",
        """\t{
\t// HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1
\tHtcleoEcomServerLog(0x0000F530u, KErrNone,
\t\t(TUint32)aImplUid.iUid);
\tHtcleoEcomServerLog(0x0000F531u,
\t\taSecurityCheckNeeded ? 1 : 0,
\t\t(TUint32)aInterfaceUid.iUid);
\taImplInfo = NULL;
\tTInt res = KErrNotFound;
\tCImplementationData* implData;""",
        "registry entry",
    )
    text = replace_once(
        text,
        """\t\t\tres = FindImplementation(aImplUid, aInterfaceUid, implData);
\t\t\tif (KErrNone != res)
\t\t\t\t{
\t\t\t\treturn res;
\t\t\t\t}
\t\t\tCDllData* dll = implData->iParent->iParent;
\t\t\t// security check is deferred to here.
\t\t\tsecurityPassed = dll->ProcessSecurityCheckL();""",
        """\t\t\tHtcleoEcomServerLog(0x0000F532u, KErrNone,
\t\t\t\t(TUint32)aImplUid.iUid);
\t\t\tres = FindImplementation(aImplUid, aInterfaceUid, implData);
\t\t\tHtcleoEcomServerLog(0x0000F533u, res,
\t\t\t\tres == KErrNone ? (TUint32)implData : 0u);
\t\t\tif (KErrNone != res)
\t\t\t\t{
\t\t\t\treturn res;
\t\t\t\t}
\t\t\tCDllData* dll = implData->iParent->iParent;
\t\t\tHtcleoEcomServerLog(0x0000F534u, KErrNone, (TUint32)dll);
\t\t\t// security check is deferred to here.
\t\t\tHtcleoEcomServerLog(0x0000F535u, KErrNone, 0u);
\t\t\tsecurityPassed = dll->ProcessSecurityCheckL();
\t\t\tHtcleoEcomServerLog(0x0000F536u,
\t\t\t\tsecurityPassed ? KErrNone : KErrPermissionDenied,
\t\t\t\t(TUint32)securityPassed);""",
        "registry security lookup",
    )
    text = replace_once(
        text,
        """\t\t\t\tif (!aClientRequest.CheckCapability(dll->iCapSet, *(implData->iImplInfo)))
\t\t\t\t\t{
\t\t\t\t\treturn KErrPermissionDenied;
\t\t\t\t\t}
\t\t\t\tdll->PopulateAnEntry(aEntry);
\t\t\t\taImplInfo = implData->iImplInfo;""",
        """\t\t\t\tHtcleoEcomServerLog(0x0000F537u, KErrNone, 0u);
\t\t\t\tconst TBool htcleoCapability =
\t\t\t\t\taClientRequest.CheckCapability(
\t\t\t\t\t\tdll->iCapSet, *(implData->iImplInfo));
\t\t\t\tHtcleoEcomServerLog(0x0000F538u,
\t\t\t\t\thtcleoCapability ? KErrNone : KErrPermissionDenied,
\t\t\t\t\t(TUint32)htcleoCapability);
\t\t\t\tif (!htcleoCapability)
\t\t\t\t\t{
\t\t\t\t\treturn KErrPermissionDenied;
\t\t\t\t\t}
\t\t\t\tdll->PopulateAnEntry(aEntry);
\t\t\t\taImplInfo = implData->iImplInfo;
\t\t\t\tHtcleoEcomServerLog(0x0000F539u, KErrNone,
\t\t\t\t\t(TUint32)aEntry.iName.Length());""",
        "registry capability and entry",
    )
    return text


def verify(session: str, server: str, registry: str) -> None:
    joined = session + server + registry
    checks = {
        "marker coverage": joined.count(MARKER) == 3,
        "implementation UID": joined.count(IMPL_UID) >= 1,
        "request arm": session.count("HtcleoEcomServerArm();") >= 1,
        "session stages": all(
            f"0x0000F{stage:03X}u" in session
            for stage in list(range(0x500, 0x510)) + [0x510, 0x511]
            if stage not in (0x50E,)
        ),
        "server stages": all(
            f"0x0000F{stage:03X}u" in server
            for stage in range(0x520, 0x525)
        ),
        "registry stages": all(
            f"0x0000F{stage:03X}u" in registry
            for stage in range(0x530, 0x53A)
        ),
        "real lookup retained": (
            "GetImplementationDllInfoForClientL" in server
            and "FindImplementation(aImplUid, aInterfaceUid, implData)" in registry
            and "ProcessSecurityCheckL()" in registry
        ),
        "no retry or normalization": all(
            token not in joined
            for token in ("User::After", "htcleoRegistryResult = KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen ECom server trace verification failed: "
            + "; ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    paths = {
        "session": frame / "EComServerSession.cpp",
        "server": frame / "EComServer.cpp",
        "registry": frame / "RegistryData.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing ECom server source: {path}")
    session = patch_session(paths["session"].read_text(encoding="utf-8"))
    server = patch_server(paths["server"].read_text(encoding="utf-8"))
    registry = patch_registry(paths["registry"].read_text(encoding="utf-8"))
    verify(session, server, registry)
    paths["session"].write_text(session, encoding="utf-8")
    paths["server"].write_text(server, encoding="utf-8")
    paths["registry"].write_text(registry, encoding="utf-8")
    print(
        "HTCLEO_ECOM_HOMESCREEN_SERVER_TRACE="
        "service6-impl2001952c-session-server-registry-f500-f539"
    )


if __name__ == "__main__":
    main()
