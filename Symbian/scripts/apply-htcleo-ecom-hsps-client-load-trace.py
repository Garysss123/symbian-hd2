#!/usr/bin/env python3
"""Trace HSPS ECom client DLL loading and factory creation."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def patch_header(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "void HtcleoEcomLog(TUint32 aStage, TInt aResult, TUint32 aDetail);",
        "void HtcleoEcomLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n"
        "// HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1\n"
        "void HtcleoEcomHspsClientArm();\n"
        "void HtcleoEcomHspsClientLog(TUint32 aStage, TInt aResult, TUint32 aDetail);",
        "enabled declarations",
    )
    return replace_once(
        text,
        "static inline void HtcleoEcomLog(TUint32, TInt, TUint32) {}",
        "static inline void HtcleoEcomLog(TUint32, TInt, TUint32) {}\n"
        "static inline void HtcleoEcomHspsClientArm() {}\n"
        "static inline void HtcleoEcomHspsClientLog(TUint32, TInt, TUint32) {}",
        "disabled declarations",
    )


def patch_logger(text: str) -> str:
    if MARKER in text:
        # Repair the initial transform draft if it was applied before the C++
        # path escaping check was added.  A correct installed tree is unchanged.
        text = text.replace(
            r'''_LIT(KDir, "C:\Symbian3\");''',
            r'''_LIT(KDir, "C:\\Symbian3\\");''',
        )
        text = text.replace(
            r'''_LIT(KPath, "C:\Symbian3\HSPSECOM.TXT");''',
            r'''_LIT(KPath, "C:\\Symbian3\\HSPSECOM.TXT");''',
        )
        new_arm = r'''void HtcleoEcomHspsClientArm()
	{
	// Calls are UID-gated at their source sites.  ECom DLLs cannot contain
	// writable global state, and the logger creates the file on first write.
	}'''
        state_marker = "static TBool gHtcleoEcomHspsClientArmed = EFalse;"
        if state_marker in text:
            start = text.index(state_marker)
            end = text.index("\n\nvoid HtcleoEcomHspsClientLog", start)
            text = text[:start] + new_arm + text[end:]
        text = text.replace(
            "\tif(!gHtcleoEcomHspsClientArmed)\n\t\treturn;\n",
            "",
            1,
        )
        return text
    block = r'''

// HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1
void HtcleoEcomHspsClientArm()
	{
	// Calls are UID-gated at their source sites.  ECom DLLs cannot contain
	// writable global state, and the logger creates the file on first write.
	}

void HtcleoEcomHspsClientLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
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
		_LIT8(KPrefix, "HTCLEO_HCLI ");
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
    return replace_once(text, "\n#endif\n", block + "\n#endif\n", "logger tail")


def patch_session(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\tconst TBool htcleoNvg = (aInterfaceUid.iUid == 0x1028653B);\n"
        "\t// HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY_V1",
        "\tconst TBool htcleoNvg = (aInterfaceUid.iUid == 0x1028653B);\n"
        "\t// HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1\n"
        "\tconst TBool htcleoHspsClient =\n"
        "\t\t(aInterfaceUid.iUid == 0x200159C7u);\n"
        "\tif(htcleoHspsClient)\n"
        "\t\t{\n"
        "\t\tHtcleoEcomHspsClientArm();\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C700u, aServiceId,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t\t}\n"
        "\t// HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY_V1",
        "session arm",
    )
    text = replace_once(
        text,
        "    TInt htcleoSendResult = SendReceive(aServiceId,\n"
        "        TIpcArgs(&uids,&matchStrExtInfBuf,matchType,&dllPkg));",
        "    if(htcleoHspsClient)\n"
        "        HtcleoEcomHspsClientLog(0x0000C701u, KErrNone,\n"
        "            (TUint32)matchStrExtInfBuf.Length());\n"
        "    TInt htcleoSendResult = SendReceive(aServiceId,\n"
        "        TIpcArgs(&uids,&matchStrExtInfBuf,matchType,&dllPkg));\n"
        "    if(htcleoHspsClient)\n"
        "        HtcleoEcomHspsClientLog(0x0000C702u, htcleoSendResult,\n"
        "            (TUint32)dllInfo.iName.Length());",
        "server response",
    )
    text = replace_once(
        text,
        "    User::LeaveIfError(htcleoSendResult);\n"
        "\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);",
        "    User::LeaveIfError(htcleoSendResult);\n"
        "\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C703u, KErrNone,\n"
        "\t\t\t(TUint32)uidStore[KDtorKeyUidIndex].iUid);",
        "response cleanup",
    )
    text = replace_once(
        text,
        "\tCGlobalData* globalData = CGlobalData::Instance();\n"
        "\tif(htcleoNvg)",
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C704u, KErrNone,\n"
        "\t\t\t(TUint32)dllInfo.iType[1].iUid);\n"
        "\tCGlobalData* globalData = CGlobalData::Instance();\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C705u,\n"
        "\t\t\tglobalData ? KErrNone : KErrNotReady,\n"
        "\t\t\t(TUint32)globalData);\n"
        "\tif(htcleoNvg)",
        "global data",
    )
    text = replace_once(
        text,
        "\tTAny* object=(TAny*)globalData->LoadManager().ImplementationObjectL(uidStore[KDtorKeyUidIndex],",
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C706u, KErrNone,\n"
        "\t\t\t(TUint32)uidStore[KDtorKeyUidIndex].iUid);\n"
        "\tTAny* object=(TAny*)globalData->LoadManager().ImplementationObjectL(uidStore[KDtorKeyUidIndex],",
        "load manager entry",
    )
    return replace_once(
        text,
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000030Cu, KErrNone, (TUint32)(object != NULL));\n"
        "\treturn object;",
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000030Cu, KErrNone, (TUint32)(object != NULL));\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C707u, KErrNone,\n"
        "\t\t\t(TUint32)(object != NULL));\n"
        "\treturn object;",
        "load manager return",
    )


def patch_load_manager(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);\n"
        "\tif(htcleoNvg) HtcleoEcomLog(0x00000401u,",
        "\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);\n"
        "\t// HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1\n"
        "\tconst TBool htcleoHspsClient =\n"
        "\t\t(aUniqueImplementationUid.iUid == 0x200159C8u);\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C710u, KErrNone,\n"
        "\t\t\t(TUint32)aEntry.iName.Length());\n"
        "\tif(htcleoNvg) HtcleoEcomLog(0x00000401u,",
        "load manager arm",
    )
    text = replace_once(
        text,
        "\tGetUnloadPolicy(aUniqueImplementationUid,aEntry,policy);\n"
        "\tif(htcleoNvg)",
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C711u, KErrNone,\n"
        "\t\t\t(TUint32)aEntry.iType[1].iUid);\n"
        "\tGetUnloadPolicy(aUniqueImplementationUid,aEntry,policy);\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C712u, KErrNone,\n"
        "\t\t\t(TUint32)(policy != NULL));\n"
        "\tif(htcleoNvg)",
        "policy lookup",
    )
    text = replace_once(
        text,
        "\t\tpolicy = CUnloadPolicy::NewLC(aEntry);\n"
        "\t\tif(htcleoNvg)",
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C713u, KErrNone, 0u);\n"
        "\t\tpolicy = CUnloadPolicy::NewLC(aEntry);\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C714u, KErrNone,\n"
        "\t\t\t\t(TUint32)policy);\n"
        "\t\tif(htcleoNvg)",
        "new policy",
    )
    text = replace_once(
        text,
        "\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();\n"
        "\t\tif(htcleoNvg) HtcleoEcomLog(0x00000407u,",
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C715u, KErrNone, 0u);\n"
        "\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C716u, KErrNone,\n"
        "\t\t\t\t(TUint32)libFunctionProxy);\n"
        "\t\tif(htcleoNvg) HtcleoEcomLog(0x00000407u,",
        "new policy load",
    )
    text = replace_once(
        text,
        "\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();\n"
        "\t\tif(htcleoNvg) HtcleoEcomLog(0x0000040Au,",
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C71Cu, KErrNone, 0u);\n"
        "\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C71Du, KErrNone,\n"
        "\t\t\t\t(TUint32)libFunctionProxy);\n"
        "\t\tif(htcleoNvg) HtcleoEcomLog(0x0000040Au,",
        "existing policy load",
    )
    text = replace_once(
        text,
        "\tif (aEntry[1] == KUidInterfaceImplementationCollection)\n"
        "\t\t{",
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C717u, KErrNone,\n"
        "\t\t\t(TUint32)aEntry[1].iUid);\n"
        "\tif (aEntry[1] == KUidInterfaceImplementationCollection)\n"
        "\t\t{\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C718u, KErrNone, 1u);",
        "plugin type",
    )
    text = replace_once(
        text,
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000040Du, err, (TUint32)(object != NULL));\n"
        "\t\n\tif (err != KErrNone)",
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000040Du, err, (TUint32)(object != NULL));\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C719u, err,\n"
        "\t\t\t(TUint32)(object != NULL));\n"
        "\t\n\tif (err != KErrNone)",
        "factory result",
    )
    text = replace_once(
        text,
        "\t\tCleanup(policy);\n"
        "\t\tUser::Leave(err);",
        "\t\tCleanup(policy);\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C71Au, err, 0u);\n"
        "\t\tUser::Leave(err);",
        "factory leave",
    )
    return replace_once(
        text,
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000040Eu, KErrNone, (TUint32)aInstanceKey.iUid);\n"
        "\t\t\t\n\treturn object;",
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000040Eu, KErrNone, (TUint32)aInstanceKey.iUid);\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C71Bu, KErrNone,\n"
        "\t\t\t(TUint32)aInstanceKey.iUid);\n"
        "\t\t\t\n\treturn object;",
        "load manager success",
    )


def patch_implementation1(text: str) -> str:
    # This operates on the same LoadManager.cpp text after patch_load_manager.
    old = "\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);\n\tif(htcleoNvg) HtcleoEcomLog(0x00000601u,"
    if old not in text:
        if text.count("0x0000C730u") == 1:
            return text
        raise SystemExit("implementation1: anchor missing")
    new = (
        "\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);\n"
        "\tconst TBool htcleoHspsClientImpl1 =\n"
        "\t\t(aUniqueImplementationUid.iUid == 0x200159C8u);\n"
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C730u, KErrNone,\n"
        "\t\t\t(TUint32)aLibFunctionProxy);\n"
        "\tif(htcleoNvg) HtcleoEcomLog(0x00000601u,"
    )
    text = text.replace(old, new, 1)
    text = replace_once(
        text,
        "\tTAny* newLPointer = GetNewLPointerAndProxyTableRowL<TImplementationProxy,TInstantiationL>(aUniqueImplementationUid,implementationProxyRow,proxy);",
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C731u, KErrNone, 0u);\n"
        "\tTAny* newLPointer = GetNewLPointerAndProxyTableRowL<TImplementationProxy,TInstantiationL>(aUniqueImplementationUid,implementationProxyRow,proxy);\n"
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C732u, KErrNone,\n"
        "\t\t\t(TUint32)newLPointer);",
        "proxy row",
    )
    text = replace_once(
        text,
        "\tCInstanceInfoSimple* instanceInfoSimple = CInstanceInfoSimple::NewL(aPolicy,implementationProxyRow);",
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C733u, KErrNone, 0u);\n"
        "\tCInstanceInfoSimple* instanceInfoSimple = CInstanceInfoSimple::NewL(aPolicy,implementationProxyRow);\n"
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C734u, KErrNone,\n"
        "\t\t\t(TUint32)instanceInfoSimple);",
        "instance info",
    )
    text = replace_once(
        text,
        "\tiInstanceInfoList.InsertInAddressOrderL(instanceInfoSimple);",
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C735u, KErrNone,\n"
        "\t\t\t(TUint32)iInstanceInfoList.Count());\n"
        "\tiInstanceInfoList.InsertInAddressOrderL(instanceInfoSimple);\n"
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C736u, KErrNone,\n"
        "\t\t\t(TUint32)iInstanceInfoList.Count());",
        "instance list",
    )
    return replace_once(
        text,
        "\tobject = ImplementationObjectL(aCreationParameters, \n"
        "\t aCreationParamsFlag,newLPointer);\n"
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000060Au,",
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C737u, KErrNone,\n"
        "\t\t\t(TUint32)aCreationParamsFlag);\n"
        "\tobject = ImplementationObjectL(aCreationParameters, \n"
        "\t aCreationParamsFlag,newLPointer);\n"
        "\tif(htcleoHspsClientImpl1)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C738u, KErrNone,\n"
        "\t\t\t(TUint32)object);\n"
        "\tif(htcleoNvg) HtcleoEcomLog(0x0000060Au,",
        "object factory",
    )


def patch_unload_policy(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "\t_LIT(KHtcleoNvgDllName, \"nvgrenderstage.dll\");\n"
        "\tconst TBool htcleoNvg = (htcleoLibraryPath.FindF(KHtcleoNvgDllName) != KErrNotFound);",
        "\t_LIT(KHtcleoNvgDllName, \"nvgrenderstage.dll\");\n"
        "\tconst TBool htcleoNvg = (htcleoLibraryPath.FindF(KHtcleoNvgDllName) != KErrNotFound);\n"
        "\t// HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1\n"
        "\t_LIT(KHtcleoHspsDllName, \"hspsdefinitionengine.dll\");\n"
        "\tconst TBool htcleoHspsClient =\n"
        "\t\t(htcleoLibraryPath.FindF(KHtcleoHspsDllName) != KErrNotFound);\n"
        "\tif(htcleoHspsClient)\n"
        "\t\tHtcleoEcomHspsClientLog(0x0000C720u, KErrNone,\n"
        "\t\t\t(TUint32)iReferencesInUseCount);",
        "HSPS library identity",
    )
    text = replace_once(
        text,
        "\t\tIncreaseReference();\n"
        "\t\tTLibraryFunction htcleoExistingProxy = iLibrary.Lookup(KImplementationGroupProxy);",
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C721u, KErrNone,\n"
        "\t\t\t\t(TUint32)iReferencesInUseCount);\n"
        "\t\tIncreaseReference();\n"
        "\t\tTLibraryFunction htcleoExistingProxy = iLibrary.Lookup(KImplementationGroupProxy);\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C722u, KErrNone,\n"
        "\t\t\t\t(TUint32)htcleoExistingProxy);",
        "existing proxy",
    )
    text = replace_once(
        text,
        "\t\tTInt htcleoLoadResult = KErrNone;\n"
        "\t\tif(htcleoNvg)",
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\t{\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C723u, KErrNone,\n"
        "\t\t\t\t(TUint32)libraryPath.Length());\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C724u, KErrNone,\n"
        "\t\t\t\t(TUint32)iDllEntry->GetThirdUid().iUid);\n"
        "\t\t\t}\n"
        "\t\tTInt htcleoLoadResult = KErrNone;\n"
        "\t\tif(htcleoNvg)",
        "load preamble",
    )
    text = replace_once(
        text,
        "\t\t\thtcleoLoadResult = iLibrary.Load(libraryPath,\n"
        "\t\t\t\tTUidType(KDynamicLibraryUid,iDllEntry->GetSecondUid(),iDllEntry->GetThirdUid()));\n"
        "\t\t\t}\n"
        "\t\tif(htcleoNvg)",
        "\t\t\tif(htcleoHspsClient)\n"
        "\t\t\t\tHtcleoEcomHspsClientLog(0x0000C725u, KErrNone, 0u);\n"
        "\t\t\thtcleoLoadResult = iLibrary.Load(libraryPath,\n"
        "\t\t\t\tTUidType(KDynamicLibraryUid,iDllEntry->GetSecondUid(),iDllEntry->GetThirdUid()));\n"
        "\t\t\tif(htcleoHspsClient)\n"
        "\t\t\t\tHtcleoEcomHspsClientLog(0x0000C726u, htcleoLoadResult,\n"
        "\t\t\t\t\t(TUint32)iLibrary.Handle());\n"
        "\t\t\t}\n"
        "\t\tif(htcleoNvg)",
        "library load",
    )
    text = replace_once(
        text,
        "\t\tUser::LeaveIfError(htcleoLoadResult);\n"
        "\t\tif(htcleoNvg)",
        "\t\tUser::LeaveIfError(htcleoLoadResult);\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C727u, KErrNone,\n"
        "\t\t\t\t(TUint32)iLibrary.Handle());\n"
        "\t\tif(htcleoNvg)",
        "post load",
    )
    return replace_once(
        text,
        "\t\tTLibraryFunction htcleoProxy = iLibrary.Lookup(KImplementationGroupProxy);\n"
        "\t\tif(htcleoNvg)",
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C728u, KErrNone,\n"
        "\t\t\t\t(TUint32)iReferencesInUseCount);\n"
        "\t\tTLibraryFunction htcleoProxy = iLibrary.Lookup(KImplementationGroupProxy);\n"
        "\t\tif(htcleoHspsClient)\n"
        "\t\t\tHtcleoEcomHspsClientLog(0x0000C729u,\n"
        "\t\t\t\thtcleoProxy ? KErrNone : KErrNotFound,\n"
        "\t\t\t\t(TUint32)htcleoProxy);\n"
        "\t\tif(htcleoNvg)",
        "proxy lookup",
    )


def verify(header: str, logger: str, session: str, load: str, unload: str) -> None:
    joined = header + logger + session + load + unload
    stages = (
        list(range(0x700, 0x708))
        + list(range(0x710, 0x71E))
        + list(range(0x720, 0x72A))
        + list(range(0x730, 0x739))
    )
    checks = {
        "marker coverage": joined.count(MARKER) == 5,
        "path and capacity": (
            logger.count(r"C:\\Symbian3\\HSPSECOM.TXT") == 1
            and logger.count("1048576 - 128") == 1
        ),
        "append and flush": (
            "file.Seek(ESeekEnd, position)" in logger
            and "file.Flush()" in logger
        ),
        "all stages": all(
            joined.count(f"0x0000C{stage:03X}u") == 1 for stage in stages
        ),
        "real server IPC": session.count("SendReceive(aServiceId,") >= 2,
        "real library load": unload.count("iLibrary.Load(libraryPath,") == 1,
        "real proxy and factory": (
            unload.count("iLibrary.Lookup(KImplementationGroupProxy)") == 2
            and load.count("ImplementationObjectL(aCreationParameters,") >= 2
        ),
        "no writable globals": "gHtcleo" not in joined,
        "no normalization or delay": all(
            token not in joined
            for token in ("User::After", "htcleoLoadResult = KErrNone; //", "KErrServerTerminated = KErrNone")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HSPS client-load trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    paths = {
        "header": frame / "HtcleoEcomLog.h",
        "logger": frame / "HtcleoEcomLog.cpp",
        "session": frame / "EComSession.cpp",
        "load": frame / "LoadManager.cpp",
        "unload": frame / "UnloadPolicy.cpp",
    }
    values = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    values["header"] = patch_header(values["header"])
    values["logger"] = patch_logger(values["logger"])
    values["session"] = patch_session(values["session"])
    values["load"] = patch_load_manager(values["load"])
    values["load"] = patch_implementation1(values["load"])
    values["unload"] = patch_unload_policy(values["unload"])
    verify(**values)
    for name, path in paths.items():
        path.write_text(values[name], encoding="utf-8")
    print(
        "HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE="
        "HSPSECOM-hcli-c700-c707-c710-c71d-c720-c729-c730-c738"
    )


if __name__ == "__main__":
    main()
