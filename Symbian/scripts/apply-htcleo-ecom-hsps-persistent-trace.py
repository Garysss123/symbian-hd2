#!/usr/bin/env python3
"""Persist HSPS definition-engine ECom tracing across ECom server restarts."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_header(text: str) -> str:
    if MARKER in text:
        return text
    return replace_once(
        text,
        "void HtcleoEcomServerLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n",
        "void HtcleoEcomServerLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n"
        "// HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1\n"
        "void HtcleoEcomHspsArm();\n"
        "void HtcleoEcomHspsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n",
        "enabled declarations",
    ).replace(
        "static inline void HtcleoEcomServerLog(TUint32, TInt, TUint32) {}\n",
        "static inline void HtcleoEcomServerLog(TUint32, TInt, TUint32) {}\n"
        "static inline void HtcleoEcomHspsArm() {}\n"
        "static inline void HtcleoEcomHspsLog(TUint32, TInt, TUint32) {}\n",
        1,
    )


def patch_logger(text: str) -> str:
    if MARKER in text:
        return text
    block = r'''

// HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1
static TBool gHtcleoEcomHspsArmed = EFalse;

void HtcleoEcomHspsArm()
	{
	if(gHtcleoEcomHspsArmed)
		return;
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		return;
	_LIT(KDir, "C:\\Symbian3\\");
	_LIT(KPath, "C:\\Symbian3\\HSPSECOM.TXT");
	r = fs.MkDirAll(KDir);
	if(r == KErrNone || r == KErrAlreadyExists)
		{
		RFile file;
		r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
		if(r == KErrNotFound || r == KErrPathNotFound)
			r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
		file.Close();
		}
	fs.Close();
	if(r == KErrNone)
		gHtcleoEcomHspsArmed = ETrue;
	}

void HtcleoEcomHspsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	if(!gHtcleoEcomHspsArmed)
		return;
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		return;
	_LIT(KDir, "C:\\Symbian3\\");
	_LIT(KPath, "C:\\Symbian3\\HSPSECOM.TXT");
	(void)fs.MkDirAll(KDir);
	RFile file;
	r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
	if(r == KErrNotFound || r == KErrPathNotFound)
		r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
	TInt position = 0;
	if(r == KErrNone)
		r = file.Seek(ESeekEnd, position);
	if(r == KErrNone && position <= (1048576 - 128))
		{
		_LIT8(KPrefix, "HTCLEO_HECO ");
		TBuf8<128> record;
		record.Append(KPrefix);
		record.AppendNumFixedWidth((TUint32)position, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
		record.Append('\n');
		r = file.Write(record);
		if(r == KErrNone)
			(void)file.Flush();
		}
	file.Close();
	fs.Close();
	}
'''
    return replace_once(text, "#endif\n", block + "\n#endif\n", "logger tail")


def patch_session(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\tconst TBool htcleoHomeCreate =\n"
        "\t\t(aMessage.Function() == EGetImplementationCreationMethod &&\n"
        "\t\t uids[KInterfaceUidIndex].iUid == 0x2001952Cu) ||\n"
        "\t\thtcleoHspsDefinitionResolve;\n"
        "\tif(htcleoHomeCreate)",
        "\tconst TBool htcleoHomeCreate =\n"
        "\t\t(aMessage.Function() == EGetImplementationCreationMethod &&\n"
        "\t\t uids[KInterfaceUidIndex].iUid == 0x2001952Cu) ||\n"
        "\t\thtcleoHspsDefinitionResolve;\n"
        "\t// HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomHspsArm();\n"
        "\t\tHtcleoEcomHspsLog(0x0000F600u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\t\tHtcleoEcomHspsLog(0x0000F601u, KErrNone,\n"
        "\t\t\t(TUint32)uids[KInterfaceUidIndex].iUid);\n"
        "\t\t}\n"
        "\tif(htcleoHomeCreate)",
        "session HSPS arm",
    )
    return replace_once(
        text,
        "\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);\n"
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F504u,",
        "\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);\n"
        "\tif(htcleoHspsDefinitionResolve)\n"
        "\t\tHtcleoEcomHspsLog(0x0000F602u, matchStr.Length(),\n"
        "\t\t\t(TUint32)extendedInterfaces.Count());\n"
        "\tif(htcleoHomeCreate)\n"
        "\t\tHtcleoEcomServerLog(0x0000F504u,",
        "session request payload",
    )


def patch_server(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\tif(aInterfaceUid.iUid == 0x200159C7u)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomServerLog(0x0000F540u, KErrNone,",
        "\t// HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1\n"
        "\tif(aInterfaceUid.iUid == 0x200159C7u)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomHspsLog(0x0000F610u, KErrNone,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F611u, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F612u,\n"
        "\t\t\thtcleoHspsDefinition ? KErrNone : KErrNotFound,\n"
        "\t\t\t(TUint32)htcleoDataType.Length());\n"
        "\t\tHtcleoEcomServerLog(0x0000F540u, KErrNone,",
        "server request trace",
    )
    text = replace_once(
        text,
        "\t\tHtcleoEcomServerLog(0x0000F543u, KErrNone,\n"
        "\t\t\t(TUint32)htcleoImplementationUid.iUid);\n"
        "\t\tconst TInt htcleoResult =",
        "\t\tHtcleoEcomServerLog(0x0000F543u, KErrNone,\n"
        "\t\t\t(TUint32)htcleoImplementationUid.iUid);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F613u, KErrNone,\n"
        "\t\t\t(TUint32)htcleoImplementationUid.iUid);\n"
        "\t\tconst TInt htcleoResult =",
        "server registry entry",
    )
    text = replace_once(
        text,
        "\t\tHtcleoEcomServerLog(0x0000F544u, htcleoResult,\n"
        "\t\t\t(TUint32)htcleoImplInfo);\n"
        "\t\tUser::LeaveIfError(htcleoResult);\n"
        "\t\tHtcleoEcomServerLog(0x0000F545u, KErrNone,",
        "\t\tHtcleoEcomServerLog(0x0000F544u, htcleoResult,\n"
        "\t\t\t(TUint32)htcleoImplInfo);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F614u, htcleoResult,\n"
        "\t\t\t(TUint32)htcleoImplInfo);\n"
        "\t\tUser::LeaveIfError(htcleoResult);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F615u, KErrNone,\n"
        "\t\t\t(TUint32)aDllInfo.iName.Length());\n"
        "\t\tHtcleoEcomServerLog(0x0000F545u, KErrNone,",
        "server registry result",
    )
    return replace_once(
        text,
        "\tif(aInterfaceUid.iUid == 0x200159C7u)\n"
        "\t\tHtcleoEcomServerLog(0x0000F546u, KErrNone, 0u);",
        "\tif(aInterfaceUid.iUid == 0x200159C7u)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomHspsLog(0x0000F616u, KErrNone, 0u);\n"
        "\t\tHtcleoEcomServerLog(0x0000F546u, KErrNone, 0u);\n"
        "\t\t}",
        "server stock fallback",
    )


def patch_registry(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\t// HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1\n"
        "\tHtcleoEcomServerLog(0x0000F530u, KErrNone,",
        "\t// HTCLEO_ECOM_HOMESCREEN_SERVER_CREATE_TRACE_V1\n"
        "\t// HTCLEO_ECOM_HSPS_PERSISTENT_TRACE_V1\n"
        "\tconst TBool htcleoHspsImpl = (aImplUid.iUid == 0x200159C8u);\n"
        "\tif(htcleoHspsImpl)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomHspsLog(0x0000F620u, KErrNone,\n"
        "\t\t\t(TUint32)aImplUid.iUid);\n"
        "\t\tHtcleoEcomHspsLog(0x0000F621u,\n"
        "\t\t\taSecurityCheckNeeded ? 1 : 0,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t\t}\n"
        "\tHtcleoEcomServerLog(0x0000F530u, KErrNone,",
        "registry entry",
    )
    text = replace_once(
        text,
        "\t\t\tres = FindImplementation(aImplUid, aInterfaceUid, implData);\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F533u, res,",
        "\t\t\tres = FindImplementation(aImplUid, aInterfaceUid, implData);\n"
        "\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\tHtcleoEcomHspsLog(0x0000F622u, res,\n"
        "\t\t\t\t\tres == KErrNone ? (TUint32)implData : 0u);\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F533u, res,",
        "registry find result",
    )
    text = replace_once(
        text,
        "\t\t\tCDllData* dll = implData->iParent->iParent;\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F534u, KErrNone, (TUint32)dll);",
        "\t\t\tCDllData* dll = implData->iParent->iParent;\n"
        "\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\tHtcleoEcomHspsLog(0x0000F623u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)dll);\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F534u, KErrNone, (TUint32)dll);",
        "registry DLL",
    )
    text = replace_once(
        text,
        "\t\t\tHtcleoEcomServerLog(0x0000F535u, KErrNone, 0u);\n"
        "\t\t\tsecurityPassed = dll->ProcessSecurityCheckL();\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F536u,",
        "\t\t\tHtcleoEcomServerLog(0x0000F535u, KErrNone, 0u);\n"
        "\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\tHtcleoEcomHspsLog(0x0000F624u, KErrNone, 0u);\n"
        "\t\t\tsecurityPassed = dll->ProcessSecurityCheckL();\n"
        "\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\tHtcleoEcomHspsLog(0x0000F625u,\n"
        "\t\t\t\t\tsecurityPassed ? KErrNone : KErrPermissionDenied,\n"
        "\t\t\t\t\t(TUint32)securityPassed);\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F536u,",
        "registry security",
    )
    text = replace_once(
        text,
        "\t\t\t\tconst TBool htcleoCapability =\n"
        "\t\t\t\t\taClientRequest.CheckCapability(\n"
        "\t\t\t\t\t\tdll->iCapSet, *(implData->iImplInfo));\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F538u,",
        "\t\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\t\tHtcleoEcomHspsLog(0x0000F626u, KErrNone, 0u);\n"
        "\t\t\t\tconst TBool htcleoCapability =\n"
        "\t\t\t\t\taClientRequest.CheckCapability(\n"
        "\t\t\t\t\t\tdll->iCapSet, *(implData->iImplInfo));\n"
        "\t\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\t\tHtcleoEcomHspsLog(0x0000F627u,\n"
        "\t\t\t\t\t\thtcleoCapability ? KErrNone : KErrPermissionDenied,\n"
        "\t\t\t\t\t\t(TUint32)htcleoCapability);\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F538u,",
        "registry capability",
    )
    return replace_once(
        text,
        "\t\t\t\tHtcleoEcomServerLog(0x0000F539u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)aEntry.iName.Length());",
        "\t\t\t\tHtcleoEcomServerLog(0x0000F539u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)aEntry.iName.Length());\n"
        "\t\t\t\tif(htcleoHspsImpl)\n"
        "\t\t\t\t\tHtcleoEcomHspsLog(0x0000F628u, KErrNone,\n"
        "\t\t\t\t\t\t(TUint32)aEntry.iName.Length());",
        "registry populated entry",
    )


def verify(header: str, logger: str, session: str, server: str,
           registry: str) -> None:
    joined = header + logger + session + server + registry
    checks = {
        "marker coverage": joined.count(MARKER) == 5,
        "path and capacity": (
            logger.count(r"C:\\Symbian3\\HSPSECOM.TXT") == 2
            and logger.count("1048576 - 128") == 1
        ),
        "append across restart": (
            logger.count("file.Open(fs, KPath") == 2
            and logger.count("file.Replace(fs, KPath") == 2
            and "file.Seek(ESeekEnd, position)" in logger
        ),
        "flush before crash": "file.Flush()" in logger,
        "session stages": all(
            session.count(f"0x0000F{stage:03X}u") == 1
            for stage in range(0x600, 0x603)
        ),
        "server stages": all(
            server.count(f"0x0000F{stage:03X}u") == 1
            for stage in range(0x610, 0x617)
        ),
        "registry stages": all(
            registry.count(f"0x0000F{stage:03X}u") == 1
            for stage in range(0x620, 0x629)
        ),
        "no behavior change": all(
            token not in joined
            for token in ("User::After", "RTimer", "htcleoResult = KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS persistent ECom trace verification failed: " +
                         ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    paths = {
        "header": frame / "HtcleoEcomServerLog.h",
        "logger": frame / "HtcleoEcomServerLog.cpp",
        "session": frame / "EComServerSession.cpp",
        "server": frame / "EComServer.cpp",
        "registry": frame / "RegistryData.cpp",
    }
    values = {name: path.read_text(encoding="utf-8")
              for name, path in paths.items()}
    values["header"] = patch_header(values["header"])
    values["logger"] = patch_logger(values["logger"])
    values["session"] = patch_session(values["session"])
    values["server"] = patch_server(values["server"])
    values["registry"] = patch_registry(values["registry"])
    verify(**values)
    for name, path in paths.items():
        path.write_text(values[name], encoding="utf-8")
    print(
        "HTCLEO_ECOM_HSPS_PERSISTENT_TRACE="
        "HSPSECOM-1m-f600-f628-append-across-server-restart"
    )


if __name__ == "__main__":
    main()
