#!/usr/bin/env python3
"""Trace the HSPS ECom response/IPC tail without changing its result."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HSPS_RESPONSE_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_session(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_once(
        text,
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F504u,\n"
        "\t\t\tmatchStr.Length(), (TUint32)extendedInterfaces.Count());\n"
        "    if(matchStr.Length()>0)",
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F504u,\n"
        "\t\t\tmatchStr.Length(), (TUint32)extendedInterfaces.Count());\n"
        "\t// HTCLEO_ECOM_HSPS_RESPONSE_TRACE_V1\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F603u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "    if(matchStr.Length()>0)",
        "request payload tail",
    )
    text = replace_once(
        text,
        "\t\tdefault:\n"
        "\t\t\tbreak;\n"
        "\t\t}\n"
        "\tif(htcleoHomeCreate)",
        "\t\tdefault:\n"
        "\t\t\tbreak;\n"
        "\t\t}\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F604u, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tif(htcleoHomeCreate)",
        "server return",
    )
    text = replace_once(
        text,
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F508u, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tCleanupStack::PopAndDestroy(&extendedInterfaces);",
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F508u, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F605u, KErrNone,\n"
        "\t\t\t(TUint32)extendedInterfaces.Count());\n"
        "\tCleanupStack::PopAndDestroy(&extendedInterfaces);",
        "pre-cleanup",
    )
    text = replace_once(
        text,
        "\tCleanupStack::PopAndDestroy(&extendedInterfaces);\n"
        "\tCleanupStack::PopAndDestroy(&matchStr);\n"
        "\tif(htcleoHomeCreate)",
        "\tCleanupStack::PopAndDestroy(&extendedInterfaces);\n"
        "\tCleanupStack::PopAndDestroy(&matchStr);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F606u, KErrNone,\n"
        "\t\t\t(TUint32)loadInfo.iName.Length());\n"
        "\tif(htcleoHomeCreate)",
        "post-cleanup",
    )
    text = replace_once(
        text,
        "\t// Then re-package the results for return\n"
        "\t// Firstly the Interface Implementation creation method pointer\n"
        "\tTPckg<TEntry> result(loadInfo);",
        "\t// Then re-package the results for return\n"
        "\t// Firstly the Interface Implementation creation method pointer\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F607u, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tTPckg<TEntry> result(loadInfo);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F608u, KErrNone,\n"
        "\t\t\t(TUint32)result.Length());",
        "result package",
    )
    text = replace_once(
        text,
        "\t\n\taMessage.WriteL(KIPCReturnParameterCreationMethodPtr, result);\n"
        "\tif(htcleoHomeCreate)",
        "\t\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F609u, KErrNone,\n"
        "\t\t\t(TUint32)KIPCReturnParameterCreationMethodPtr);\n"
        "\taMessage.WriteL(KIPCReturnParameterCreationMethodPtr, result);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F60Au, KErrNone,\n"
        "\t\t\t(TUint32)loadInfo.iName.Length());\n"
        "\tif(htcleoHomeCreate)",
        "creation-method write",
    )
    text = replace_once(
        text,
        "\tTUidType type(KNullUid,dtorIdKey,KNullUid);\n"
        "\tTPckg<TUidType> dtorIdKeyPkg(type);",
        "\tTUidType type(KNullUid,dtorIdKey,KNullUid);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F60Bu, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tTPckg<TUidType> dtorIdKeyPkg(type);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F60Cu, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKeyPkg.Length());",
        "destructor package",
    )
    text = replace_once(
        text,
        "\t\n\taMessage.WriteL(KIPCReturnParameterUidsPtr, dtorIdKeyPkg);\n"
        "\tif(htcleoHomeCreate)",
        "\t\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F60Du, KErrNone,\n"
        "\t\t\t(TUint32)KIPCReturnParameterUidsPtr);\n"
        "\taMessage.WriteL(KIPCReturnParameterUidsPtr, dtorIdKeyPkg);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F60Eu, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tif(htcleoHomeCreate)",
        "destructor-key write",
    )
    text = replace_once(
        text,
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F50Du, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\t}\n",
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F50Du, KErrNone,\n"
        "\t\t\t(TUint32)dtorIdKey.iUid);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F60Fu, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\t}\n",
        "function return",
    )
    text = replace_once(
        text,
        "\t\tDoGetResolvedImplementationL(aMessage);\n"
        "\t\tHtcleoEcomServerLog(0x0000F511u, KErrNone,",
        "\t\tDoGetResolvedImplementationL(aMessage);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F631u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\t\tHtcleoEcomServerLog(0x0000F511u, KErrNone,",
        "inner service return",
    )
    text = replace_once(
        text,
        "\t\taMessage.Complete(completionCode);\n"
        "\t\tif(htcleoTrace)",
        "\t\tHtcleoEcomHspsLog(0x0000F632u, completionCode,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\t\taMessage.Complete(completionCode);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F633u, completionCode,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\t\tif(htcleoTrace)",
        "message completion",
    )
    return replace_once(
        text,
        "\tServiceL(msg);\n"
        "\tHtcleoEcomServerLog(0x0000F50Fu, KErrNone,",
        "\tServiceL(msg);\n"
        "\tHtcleoEcomHspsLog(0x0000F634u, KErrNone,\n"
        "\t\t(TUint32)aMessage.Function());\n"
        "\tHtcleoEcomServerLog(0x0000F50Fu, KErrNone,",
        "outer service return",
    )


def patch_server(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\t\tHtcleoEcomServerLog(0x0000F545u, KErrNone,\n"
        "\t\t\t(TUint32)aDllInfo.iName.Length());\n"
        "\t\treturn;",
        "\t\tHtcleoEcomServerLog(0x0000F545u, KErrNone,\n"
        "\t\t\t(TUint32)aDllInfo.iName.Length());\n"
        "\t\t// HTCLEO_ECOM_HSPS_RESPONSE_TRACE_V1\n"
        "\t\tHtcleoEcomHspsLog(0x0000F617u, KErrNone,\n"
        "\t\t\t(TUint32)aDllInfo.iName.Length());\n"
        "\t\treturn;",
        "direct return",
    )
    text = replace_once(
        text,
        "\t{\n"
        "\tHtcleoEcomServerLog(0x0000F329u, aError,",
        "\t{\n"
        "\tHtcleoEcomHspsLog(0x0000F640u, aError,\n"
        "\t\t(TUint32)Message().Function());\n"
        "\tHtcleoEcomServerLog(0x0000F329u, aError,",
        "runerror entry",
    )
    text = replace_once(
        text,
        "\t\tMessage().Complete(aError);\n"
        "\t\t}\n"
        "\tHtcleoEcomServerLog(0x0000F32Au, aError, 0u);",
        "\t\tMessage().Complete(aError);\n"
        "\t\t}\n"
        "\tHtcleoEcomHspsLog(0x0000F641u, aError,\n"
        "\t\t(TUint32)Message().Function());\n"
        "\tHtcleoEcomServerLog(0x0000F32Au, aError, 0u);",
        "runerror completion",
    )
    return replace_once(
        text,
        "\tReStart();\n"
        "\tHtcleoEcomServerLog(0x0000F32Bu, aError, 0u);",
        "\tReStart();\n"
        "\tHtcleoEcomHspsLog(0x0000F642u, aError, 0u);\n"
        "\tHtcleoEcomServerLog(0x0000F32Bu, aError, 0u);",
        "runerror restart",
    )


def verify(session: str, server: str) -> None:
    joined = session + server
    expected = list(range(0x603, 0x610)) + [
        0x617, 0x631, 0x632, 0x633, 0x634, 0x640, 0x641, 0x642
    ]
    checks = {
        "marker coverage": joined.count(MARKER) == 2,
        "all stages exactly once": all(
            joined.count(f"0x0000F{stage:03X}u") == 1 for stage in expected
        ),
        "real IPC retained": (
            session.count("aMessage.WriteL(KIPCReturnParameterCreationMethodPtr, result)") == 1
            and session.count("aMessage.WriteL(KIPCReturnParameterUidsPtr, dtorIdKeyPkg)") == 1
            and session.count("aMessage.Complete(completionCode)") == 1
        ),
        "real error path retained": (
            server.count("Message().Complete(aError)") == 1
            and server.count("ReStart()") == 1
        ),
        "no behavior change": all(
            token not in joined
            for token in ("User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS response trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    session_path = frame / "EComServerSession.cpp"
    server_path = frame / "EComServer.cpp"
    session = patch_session(session_path.read_text(encoding="utf-8"))
    server = patch_server(server_path.read_text(encoding="utf-8"))
    verify(session, server)
    session_path.write_text(session, encoding="utf-8")
    server_path.write_text(server, encoding="utf-8")
    print(
        "HTCLEO_ECOM_HSPS_RESPONSE_TRACE="
        "HSPSECOM-f603-f60f-f617-f631-f634-f640-f642"
    )


if __name__ == "__main__":
    main()
