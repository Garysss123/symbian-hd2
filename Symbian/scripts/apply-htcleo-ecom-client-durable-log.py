#!/usr/bin/env python3
"""Install UID-attributed durable logging in the ECom client DLL.

The logger is active only for NVGRenderStage implementation UID 0x1028653B
(or its resolved DLL name inside CUnloadPolicy).  It uses no writable DLL
globals: every completed boundary appends and flushes one fixed record to
``C:\\Symbian3\\ECOMLOG.TXT`` and all logging failures are ignored.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_CLIENT_DURABLE_LOG_V1"
CAPACITY_MARKER = "HTCLEO_ECOM_LOG_CAPACITY_16384_V2"
OLD_CAPACITY_MARKER = "HTCLEO_ECOM_LOG_CAPACITY_256_V1"
MACRO = "__HTCLEO_ECOM_CLIENT_DURABLE_LOG__"
NVG_UID = "0x1028653B"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, start: str, new: str, label: str,
                     after: str = "") -> str:
    """Replace one simple Symbian C++ function ending in a tab-indented brace."""
    search_from = 0
    if after:
        marker_count = text.count(after)
        if marker_count != 1:
            raise SystemExit(
                f"{label}: expected one section marker, found {marker_count}"
            )
        search_from = text.index(after) + len(after)
    begin = text.find(start, search_from)
    if begin < 0:
        raise SystemExit(f"{label}: function start not found")
    if text.find(start, begin + len(start)) >= 0 and not after:
        raise SystemExit(f"{label}: function start is not unique")
    end = text.find("\n\t}\n", begin)
    if end < 0:
        raise SystemExit(f"{label}: function end not found")
    return text[:begin] + new + text[end + len("\n\t}\n"):]


def replace_region(text: str, start: str, end: str, new: str,
                   label: str) -> str:
    if text.count(start) != 1:
        raise SystemExit(
            f"{label}: expected one region start, found {text.count(start)}"
        )
    begin = text.index(start)
    finish = text.find(end, begin + len(start))
    if finish < 0:
        raise SystemExit(f"{label}: region end not found")
    finish += len(end)
    return text[:begin] + new + text[finish:]


HEADER = r'''#ifndef HTCLEO_ECOM_DURABLE_LOG_H
#define HTCLEO_ECOM_DURABLE_LOG_H

#include <e32std.h>

#ifdef __HTCLEO_ECOM_CLIENT_DURABLE_LOG__
void HtcleoEcomLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoEcomLog(TUint32, TInt, TUint32) {}
#endif

#endif
'''


LOGGER = r'''// HTCLEO_ECOM_CLIENT_DURABLE_LOG_V1
#include "HtcleoEcomLog.h"

#ifdef __HTCLEO_ECOM_CLIENT_DURABLE_LOG__
#include <f32file.h>

void HtcleoEcomLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                         __attribute__((noinline));

void HtcleoEcomLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoEcomLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoEcomLogPath, "C:\\Symbian3\\ECOMLOG.TXT");
	r = fs.MkDirAll(KHtcleoEcomLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoEcomLogPath, EFileWrite | EFileShareAny);
	if(r == KErrNotFound || r == KErrPathNotFound)
		{
		r = file.Replace(fs, KHtcleoEcomLogPath, EFileWrite | EFileShareAny);
		}
	else if(r == KErrNone)
		{
		r = file.Seek(ESeekEnd, position);
		}

	// Every record is exactly 45 bytes.  Derive sequence from the file offset
	// so the E32 DLL contains no writable static data.
	// HTCLEO_ECOM_LOG_CAPACITY_16384_V2
	if(r == KErrNone && position < (16384 * 45))
		{
		_LIT8(KHtcleoEcomPrefix, "HTCLEO_ECOM ");
		TBuf8<64> record;
		record.Append(KHtcleoEcomPrefix);
		record.AppendNumFixedWidth((TUint)(position / 45), EHex, 4);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(_L8("\r\n"));
		r = file.Write(record);
		if(r == KErrNone)
			{
			(void)file.Flush();
			}
		}

	file.Close();
	fs.Close();
	}
#endif
'''


def verify(root: Path) -> None:
    frame = root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    session = (frame / "EComSession.cpp").read_text(encoding="utf-8")
    load = (frame / "LoadManager.cpp").read_text(encoding="utf-8")
    unload = (frame / "UnloadPolicy.cpp").read_text(encoding="utf-8")
    inline = (frame / "loadmanager.inl").read_text(encoding="utf-8")
    logger = (frame / "HtcleoEcomLog.cpp").read_text(encoding="utf-8")
    header = (frame / "HtcleoEcomLog.h").read_text(encoding="utf-8")
    mmp = (root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/MMPFiles/ECom.mmp").read_text(encoding="utf-8")
    combined = session + load + unload + inline
    hsps_client_extension = (
        "HTCLEO_ECOM_HSPS_CLIENT_LOAD_TRACE_V1" in logger
    )
    expected_writer_count = 2 if hsps_client_extension else 1
    stages = (
        range(0x0101, 0x0109), range(0x0201, 0x0206),
        range(0x0301, 0x030D), range(0x0401, 0x040F),
        range(0x0501, 0x050A), range(0x0601, 0x060B),
        range(0x0701, 0x0707),
    )
    expected = [f"0x{stage:08X}u" for group in stages for stage in group]
    checks = {
        "marker": logger.count(MARKER) == 1,
        "macro": mmp.count(f"MACRO {MACRO}") == 1,
        "logger source": mmp.count("SOURCE\t\tHtcleoEcomLog.cpp") == 1,
        "headers": all(text.count('#include "HtcleoEcomLog.h"') == 1
                       for text in (session, load, unload, inline)),
        "one path": logger.count("C:\\\\Symbian3\\\\ECOMLOG.TXT") == 1,
        "fixed prefix": logger.count("HTCLEO_ECOM ") == 1,
        "write flush": (
            logger.count("file.Write(record)") == expected_writer_count
            and logger.count("file.Flush()") == expected_writer_count
        ),
        "16384-record capacity marker": logger.count(CAPACITY_MARKER) == 1,
        "16384-record capacity": logger.count("position < (16384 * 45)") == 1
        and "position < (256 * 43)" not in logger,
        "four-digit sequence": logger.count(
            "position / 45), EHex, 4"
        ) == 1,
        "no writable globals": "gHtcleo" not in logger + combined,
        "all stages": all(combined.count(stage) == 1 for stage in expected),
        "exact uid gates": combined.count(NVG_UID) >= 6,
        "no delays": "User::After" not in logger,
        "efsrv": "efsrv.lib" in mmp,
        "header guard": "HTCLEO_ECOM_DURABLE_LOG_H" in header,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("ECom durable-log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    mmp_path = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/MMPFiles/ECom.mmp"
    session_path = frame / "EComSession.cpp"
    load_path = frame / "LoadManager.cpp"
    unload_path = frame / "UnloadPolicy.cpp"
    inline_path = frame / "loadmanager.inl"
    header_path = frame / "HtcleoEcomLog.h"
    logger_path = frame / "HtcleoEcomLog.cpp"
    for path in (session_path, load_path, unload_path, inline_path, mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing ECom source: {path}")

    if logger_path.is_file() and MARKER in logger_path.read_text(encoding="utf-8"):
        logger = logger_path.read_text(encoding="utf-8")
        if CAPACITY_MARKER not in logger:
            logger = replace_once(
                logger,
                f"\t// {OLD_CAPACITY_MARKER}\n"
                "\tif(r == KErrNone && position < (256 * 43))\n",
                f"\t// {CAPACITY_MARKER}\n"
                "\tif(r == KErrNone && position < (16384 * 45))\n",
                "installed logger capacity upgrade",
            )
            logger = replace_once(
                logger,
                "position / 43), EHex, 2",
                "position / 45), EHex, 4",
                "installed logger sequence width upgrade",
            )
            logger = replace_once(
                logger,
                "Every record is exactly 43 bytes.",
                "Every record is exactly 45 bytes.",
                "installed logger record-size comment upgrade",
            )
            logger_path.write_text(logger, encoding="utf-8")
        verify(args.root)
        print("HTCLEO_ECOM_CLIENT_DURABLE_LOG=installed checkpoints=64 capacity=16384 bytes=737280 path=C:\\Symbian3\\ECOMLOG.TXT")
        return

    session = session_path.read_text(encoding="utf-8")
    load = load_path.read_text(encoding="utf-8")
    unload = unload_path.read_text(encoding="utf-8")
    inline = inline_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")

    session = replace_once(session, '#include "EComUidCodes.h"\n',
                           '#include "EComUidCodes.h"\n#include "HtcleoEcomLog.h"\n',
                           "session logger include")
    load = replace_once(load, '#include "EComInternalErrorCodes.h"\n',
                        '#include "EComInternalErrorCodes.h"\n#include "HtcleoEcomLog.h"\n',
                        "load logger include")
    unload = replace_once(unload, '#include "EComUidCodes.h"\n',
                          '#include "EComUidCodes.h"\n#include "HtcleoEcomLog.h"\n',
                          "unload logger include")
    inline = replace_once(inline, '*/\n', '*/\n#include "HtcleoEcomLog.h"\n',
                          "inline logger include")

    old = '''EXPORT_C TAny* REComSession::CreateImplementationL(TUid aImplementationUid, 
\t\t\t\t\t\t\t\t\t\t\tTUid& aInstanceKey)
\t{
\tTUid tempInstanceKey = aInstanceKey = KNullUid;
\tTBool instParamsFlag = EFalse;

\tif( aImplementationUid.iUid == 0 ) 
\t\tUser::Leave(KErrArgument);
\t
\t// call FinalClose() in the event of a leave
\tCleanupStack::PushL(TCleanupItem(CleanupFinalClose, NULL));

\t// Open a local instance for the
\t// interface creation, because this is a static
\t// method and we may be not created yet.
\tREComSession& ecomSession = REComSession::OpenLC();\t// NOTE: This will connect to ECom
\t\t\t\t\t\t\t\t\t\t\t\t// using the global instance which is returned.
\t// Use the default resolver in the overloaded method.
\tTAny* result = ecomSession.ResolveAndCreateImplL(aImplementationUid, tempInstanceKey, NULL, instParamsFlag);
\t
\tCleanupStack::Pop(&ecomSession);
\tCleanupStack::Pop(); // CleanupFinalClose

\taInstanceKey = tempInstanceKey;
\t
\treturn result;
\t}'''
    new = '''EXPORT_C TAny* REComSession::CreateImplementationL(TUid aImplementationUid, 
\t\t\t\t\t\t\t\t\t\t\tTUid& aInstanceKey)
\t{
\tconst TBool htcleoNvg = (aImplementationUid.iUid == 0x1028653B);
\tif(htcleoNvg) HtcleoEcomLog(0x00000101u, KErrNone, (TUint32)aImplementationUid.iUid);
\tTUid tempInstanceKey = aInstanceKey = KNullUid;
\tTBool instParamsFlag = EFalse;

\tif( aImplementationUid.iUid == 0 ) 
\t\tUser::Leave(KErrArgument);
\tif(htcleoNvg) HtcleoEcomLog(0x00000102u, KErrNone, 0u);
\t
\t// call FinalClose() in the event of a leave
\tCleanupStack::PushL(TCleanupItem(CleanupFinalClose, NULL));
\tif(htcleoNvg) HtcleoEcomLog(0x00000103u, KErrNone, 0u);

\t// Open a local instance for the
\t// interface creation, because this is a static
\t// method and we may be not created yet.
\tREComSession& ecomSession = REComSession::OpenLC();\t// NOTE: This will connect to ECom
\t\t\t\t\t\t\t\t\t\t\t\t// using the global instance which is returned.
\tif(htcleoNvg) HtcleoEcomLog(0x00000104u, KErrNone, 0u);
\t// Use the default resolver in the overloaded method.
\tif(htcleoNvg) HtcleoEcomLog(0x00000105u, KErrNone, 0u);
\tTAny* result = ecomSession.ResolveAndCreateImplL(aImplementationUid, tempInstanceKey, NULL, instParamsFlag);
\tif(htcleoNvg) HtcleoEcomLog(0x00000106u, KErrNone, (TUint32)tempInstanceKey.iUid);
\t
\tCleanupStack::Pop(&ecomSession);
\tCleanupStack::Pop(); // CleanupFinalClose
\tif(htcleoNvg) HtcleoEcomLog(0x00000107u, KErrNone, 0u);

\taInstanceKey = tempInstanceKey;
\tif(htcleoNvg) HtcleoEcomLog(0x00000108u, KErrNone, (TUint32)(result != NULL));
\t
\treturn result;
\t}'''
    session = replace_function(
        session,
        "EXPORT_C TAny* REComSession::CreateImplementationL(TUid aImplementationUid, ",
        new,
        "CI1 implementation path",
        "\n//CreateImplementationL - CI1\n",
    )

    old = '''TAny* REComSession::ResolveAndCreateImplL(TUid aImplementationUid, 
\t\t\t\t\t\t\t\t\t\t\t   TUid& aInstanceKey,
\t\t\t\t\t\t\t\t\t\t\t   TAny* aCreationParameters, TBool aCreationParamsFlag)
\t{
\tTEComResolverParams resolutionParameters;
\tRExtendedInterfacesArray extendedInterfaces;
\tCleanupClosePushL(extendedInterfaces);
\tTAny* object = ResolveAndCreateImplL(EGetImplementationCreationMethod,
\t\t\t\t\t\t\t\t\t\t  aImplementationUid, 
\t\t\t\t\t\t\t\t\t\t  extendedInterfaces,
\t\t\t\t\t\t\t\t\t\t  resolutionParameters, 
\t\t\t\t\t\t\t\t\t\t  KNullUid, 
\t\t\t\t\t\t\t\t\t\t  aInstanceKey,
\t\t\t\t\t\t\t\t\t\t  aCreationParameters, aCreationParamsFlag);
\tCleanupStack::PopAndDestroy(&extendedInterfaces);\t\t\t\t\t\t\t\t\t  
\treturn object;\t\t\t\t\t\t\t\t\t  
\t}'''
    new = '''TAny* REComSession::ResolveAndCreateImplL(TUid aImplementationUid, 
\t\t\t\t\t\t\t\t\t\t\t   TUid& aInstanceKey,
\t\t\t\t\t\t\t\t\t\t\t   TAny* aCreationParameters, TBool aCreationParamsFlag)
\t{
\tconst TBool htcleoNvg = (aImplementationUid.iUid == 0x1028653B);
\tif(htcleoNvg) HtcleoEcomLog(0x00000201u, KErrNone, 0u);
\tTEComResolverParams resolutionParameters;
\tRExtendedInterfacesArray extendedInterfaces;
\tCleanupClosePushL(extendedInterfaces);
\tif(htcleoNvg) HtcleoEcomLog(0x00000202u, KErrNone, 0u);
\tif(htcleoNvg) HtcleoEcomLog(0x00000203u, KErrNone, (TUint32)EGetImplementationCreationMethod);
\tTAny* object = ResolveAndCreateImplL(EGetImplementationCreationMethod,
\t\t\t\t\t\t\t\t\t\t  aImplementationUid, 
\t\t\t\t\t\t\t\t\t\t  extendedInterfaces,
\t\t\t\t\t\t\t\t\t\t  resolutionParameters, 
\t\t\t\t\t\t\t\t\t\t  KNullUid, 
\t\t\t\t\t\t\t\t\t\t  aInstanceKey,
\t\t\t\t\t\t\t\t\t\t  aCreationParameters, aCreationParamsFlag);
\tif(htcleoNvg) HtcleoEcomLog(0x00000204u, KErrNone, (TUint32)(object != NULL));
\tCleanupStack::PopAndDestroy(&extendedInterfaces);
\tif(htcleoNvg) HtcleoEcomLog(0x00000205u, KErrNone, (TUint32)aInstanceKey.iUid);
\treturn object;
\t}'''
    session = replace_function(
        session,
        "TAny* REComSession::ResolveAndCreateImplL(TUid aImplementationUid, ",
        new,
        "outer resolve path",
    )

    session = replace_once(
        session,
        '''\t{
\t// Package the parameters
\t// 1st argument. Use the UidType because it will hold our 3 possible UIDs ''',
        '''\t{
\tconst TBool htcleoNvg = (aInterfaceUid.iUid == 0x1028653B);
\tif(htcleoNvg) HtcleoEcomLog(0x00000301u, KErrNone, (TUint32)aServiceId);
\t// Package the parameters
\t// 1st argument. Use the UidType because it will hold our 3 possible UIDs ''',
        "deep resolve entry",
    )
    session = replace_once(
        session,
        '''\tTUidType uidStore(aInterfaceUid, aInstanceKey, aResolverUid);
\tTPckg<TUidType> uids(uidStore);''',
        '''\tTUidType uidStore(aInterfaceUid, aInstanceKey, aResolverUid);
\tTPckg<TUidType> uids(uidStore);
\tif(htcleoNvg) HtcleoEcomLog(0x00000302u, KErrNone, (TUint32)aInterfaceUid.iUid);''',
        "deep UID package",
    )
    session = replace_once(
        session,
        '''\tRBuf8 matchStrExtInfBuf;
\tPackMatchStrAndExtendedInterfacesL(aResolutionParameters,aExtendedInterfaces,matchStrExtInfBuf);
\tmatchStrExtInfBuf.CleanupClosePushL();\t''',
        '''\tRBuf8 matchStrExtInfBuf;
\tif(htcleoNvg) HtcleoEcomLog(0x00000303u, KErrNone, (TUint32)aExtendedInterfaces.Count());
\tPackMatchStrAndExtendedInterfacesL(aResolutionParameters,aExtendedInterfaces,matchStrExtInfBuf);
\tif(htcleoNvg) HtcleoEcomLog(0x00000304u, KErrNone, (TUint32)matchStrExtInfBuf.Length());
\tmatchStrExtInfBuf.CleanupClosePushL();
\tif(htcleoNvg) HtcleoEcomLog(0x00000305u, KErrNone, 0u);\t''',
        "deep match pack",
    )
    session = replace_region(
        session,
        '''\tTEntry dllInfo;
\tTPckg<TEntry> dllPkg(dllInfo);''',
        '''\treturn object;''',
        '''\tTEntry dllInfo;
\tTPckg<TEntry> dllPkg(dllInfo);
\tif(htcleoNvg) HtcleoEcomLog(0x00000306u, KErrNone, (TUint32)matchType);

// And call the server
\tif(htcleoNvg) HtcleoEcomLog(0x00000307u, KErrNone, (TUint32)aServiceId);
\tTInt htcleoSendResult = SendReceive(aServiceId, TIpcArgs(&uids,&matchStrExtInfBuf,matchType,&dllPkg));
\tif(htcleoNvg) HtcleoEcomLog(0x00000308u, htcleoSendResult, (TUint32)dllInfo.iName.Length());
\tUser::LeaveIfError(htcleoSendResult);
\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);
\tif(htcleoNvg) HtcleoEcomLog(0x00000309u, KErrNone, (TUint32)uidStore[KDtorKeyUidIndex].iUid);
// delegate to LoadManager to instantiate the object
\tCGlobalData* globalData = CGlobalData::Instance();
\tif(htcleoNvg) HtcleoEcomLog(0x0000030Au, KErrNone, (TUint32)(globalData != NULL));
\tif(htcleoNvg) HtcleoEcomLog(0x0000030Bu, KErrNone, (TUint32)dllInfo.iType[1].iUid);
\tTAny* object=(TAny*)globalData->LoadManager().ImplementationObjectL(uidStore[KDtorKeyUidIndex], 
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tdllInfo,
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\taCreationParameters,
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\taCreationParamsFlag,
\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\taInstanceKey);
\tif(htcleoNvg) HtcleoEcomLog(0x0000030Cu, KErrNone, (TUint32)(object != NULL));
\treturn object;''',
        "deep send and load manager",
    )

    load = replace_once(
        load,
        '''\t{
\t//if the implementation Uid here is Null or the entry returned by the ecomserver
\t//contains nothing, we should leave with KErrNotFound''',
        '''\t{
\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);
\tif(htcleoNvg) HtcleoEcomLog(0x00000401u, KErrNone, (TUint32)aEntry.iName.Length());
\t//if the implementation Uid here is Null or the entry returned by the ecomserver
\t//contains nothing, we should leave with KErrNotFound''',
        "load manager entry",
    )
    load = replace_once(
        load,
        '''\t\tUser::Leave(KErrNotFound);
\t\t}

\tTAny* object = NULL;''',
        '''\t\tUser::Leave(KErrNotFound);
\t\t}
\tif(htcleoNvg) HtcleoEcomLog(0x00000402u, KErrNone, (TUint32)aEntry.iType[1].iUid);

\tTAny* object = NULL;''',
        "load manager validation",
    )
    load = replace_once(
        load,
        '''\tGetUnloadPolicy(aUniqueImplementationUid,aEntry,policy);
\tif (policy == NULL)
\t\t{
\t\t// No policy found, so create a new CUnloadPolicy and load DLL.
\t\tpolicy = CUnloadPolicy::NewLC(aEntry);
\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();
\t\tif (libFunctionProxy==NULL)
\t\t\t{
\t\t\tUser::Leave(KErrNotFound);
\t\t\t}
\t\tiAllUnloadPolicies.AppendL(policy);
\t\tCleanupStack::Pop(policy);\t// owned by iAllUnloadPolicies
\t\t}
\telse
\t\t{
\t\t// Found a policy. Load Dll if not already loaded.
\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();
\t\tif (libFunctionProxy==NULL)
\t\t\t{
\t\t\tUser::Leave(KErrNotFound);
\t\t\t}
\t\t}''',
        '''\tGetUnloadPolicy(aUniqueImplementationUid,aEntry,policy);
\tif(htcleoNvg) HtcleoEcomLog(0x00000403u, KErrNone, (TUint32)(policy != NULL));
\tif (policy == NULL)
\t\t{
\t\t// No policy found, so create a new CUnloadPolicy and load DLL.
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000404u, KErrNone, 0u);
\t\tpolicy = CUnloadPolicy::NewLC(aEntry);
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000405u, KErrNone, (TUint32)(policy != NULL));
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000406u, KErrNone, 0u);
\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000407u, KErrNone, (TUint32)(libFunctionProxy != NULL));
\t\tif (libFunctionProxy==NULL)
\t\t\t{
\t\t\tUser::Leave(KErrNotFound);
\t\t\t}
\t\tiAllUnloadPolicies.AppendL(policy);
\t\tCleanupStack::Pop(policy);\t// owned by iAllUnloadPolicies
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000408u, KErrNone, (TUint32)iAllUnloadPolicies.Count());
\t\t}
\telse
\t\t{
\t\t// Found a policy. Load Dll if not already loaded.
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000409u, KErrNone, 0u);
\t\tlibFunctionProxy = policy->LoadDllAndReturnProxyL();
\t\tif(htcleoNvg) HtcleoEcomLog(0x0000040Au, KErrNone, (TUint32)(libFunctionProxy != NULL));
\t\tif (libFunctionProxy==NULL)
\t\t\t{
\t\t\tUser::Leave(KErrNotFound);
\t\t\t}
\t\t}
\tif(htcleoNvg) HtcleoEcomLog(0x0000040Bu, KErrNone, (TUint32)(libFunctionProxy != NULL));''',
        "policy and DLL load",
    )
    load = replace_once(
        load,
        '''\tif (aEntry[1] == KUidInterfaceImplementationCollection)
\t\t{''',
        '''\tif(htcleoNvg) HtcleoEcomLog(0x0000040Cu, KErrNone, (TUint32)aEntry[1].iUid);
\tif (aEntry[1] == KUidInterfaceImplementationCollection)
\t\t{''',
        "implementation dispatch",
    )
    load = replace_once(
        load,
        '''\telse
\t\t{
\t\terr = KErrNotSupported;
\t\t}
\t
\tif (err != KErrNone)''',
        '''\telse
\t\t{
\t\terr = KErrNotSupported;
\t\t}
\tif(htcleoNvg) HtcleoEcomLog(0x0000040Du, err, (TUint32)(object != NULL));
\t
\tif (err != KErrNone)''',
        "implementation result",
    )
    load = replace_once(
        load,
        '''\t__ECOM_TRACE2("ECOM: Implementation created (%03d) %x", ++iDebugInstantiationCounter, aUniqueImplementationUid.iUid);
\t\t\t
\treturn object;''',
        '''\t__ECOM_TRACE2("ECOM: Implementation created (%03d) %x", ++iDebugInstantiationCounter, aUniqueImplementationUid.iUid);
\tif(htcleoNvg) HtcleoEcomLog(0x0000040Eu, KErrNone, (TUint32)aInstanceKey.iUid);
\t\t\t
\treturn object;''',
        "load manager return",
    )

    unload = replace_once(
        unload,
        '''\t{
\t// Function at ordinal 1 is InstantiationMethodL()
\tconst TInt KImplementationGroupProxy = 1;''',
        '''\t{
\tconst TDesC& htcleoLibraryPath = iDllEntry->GetName();
\t_LIT(KHtcleoNvgDllName, "nvgrenderstage.dll");
\tconst TBool htcleoNvg = (htcleoLibraryPath.FindF(KHtcleoNvgDllName) != KErrNotFound);
\tif(htcleoNvg) HtcleoEcomLog(0x00000501u, KErrNone, (TUint32)iReferencesInUseCount);
\t// Function at ordinal 1 is InstantiationMethodL()
\tconst TInt KImplementationGroupProxy = 1;''',
        "unload policy entry",
    )
    unload = replace_once(
        unload,
        '''\tif(iReferencesInUseCount > 0)
\t\t{
\t\tIncreaseReference();
\t\treturn iLibrary.Lookup(KImplementationGroupProxy);
\t\t}
\tconst TDesC& libraryPath = iDllEntry->GetName();
\tif(libraryPath.Length())
\t\t{
\t\t// Load up the specified library and its default method
\t\t// Dynamically load DLL\t
\t\tUser::LeaveIfError(iLibrary.Load(libraryPath, TUidType(KDynamicLibraryUid,iDllEntry->GetSecondUid(),iDllEntry->GetThirdUid())));
\t\t// Add to the reference count now to keep the
\t\t// library loaded for the instantiation call.
\t\t// IF the client fails before instantiating an implementation
\t\t// we can rely upon CEcomServerSession to correctly call
\t\t// for an implementations reference to be removed.
\t\tIncreaseReference();
\t\treturn iLibrary.Lookup(KImplementationGroupProxy);
\t\t}
\treturn NULL;''',
        '''\tif(iReferencesInUseCount > 0)
\t\t{
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000502u, KErrNone, (TUint32)iReferencesInUseCount);
\t\tIncreaseReference();
\t\tTLibraryFunction htcleoExistingProxy = iLibrary.Lookup(KImplementationGroupProxy);
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000503u, KErrNone, (TUint32)(htcleoExistingProxy != NULL));
\t\treturn htcleoExistingProxy;
\t\t}
\tconst TDesC& libraryPath = htcleoLibraryPath;
\tif(htcleoNvg) HtcleoEcomLog(0x00000504u, KErrNone, (TUint32)libraryPath.Length());
\tif(libraryPath.Length())
\t\t{
\t\t// Load up the specified library and its default method
\t\t// Dynamically load DLL
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000505u, KErrNone, (TUint32)iDllEntry->GetThirdUid().iUid);
\t\tTInt htcleoLoadResult = iLibrary.Load(libraryPath, TUidType(KDynamicLibraryUid,iDllEntry->GetSecondUid(),iDllEntry->GetThirdUid()));
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000506u, htcleoLoadResult, (TUint32)iLibrary.Handle());
\t\tUser::LeaveIfError(htcleoLoadResult);
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000507u, KErrNone, 0u);
\t\t// Add to the reference count now to keep the
\t\t// library loaded for the instantiation call.
\t\t// IF the client fails before instantiating an implementation
\t\t// we can rely upon CEcomServerSession to correctly call
\t\t// for an implementations reference to be removed.
\t\tIncreaseReference();
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000508u, KErrNone, (TUint32)iReferencesInUseCount);
\t\tTLibraryFunction htcleoProxy = iLibrary.Lookup(KImplementationGroupProxy);
\t\tif(htcleoNvg) HtcleoEcomLog(0x00000509u, KErrNone, (TUint32)(htcleoProxy != NULL));
\t\treturn htcleoProxy;
\t\t}
\treturn NULL;''',
        "unload policy load and lookup",
    )

    load = replace_once(
        load,
        '''\t{
\tTAny* object = NULL; // Instantiation object
\tTInstantiationL proxy = reinterpret_cast<TInstantiationL>(aLibFunctionProxy);''',
        '''\t{
\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);
\tif(htcleoNvg) HtcleoEcomLog(0x00000601u, KErrNone, (TUint32)(aLibFunctionProxy != NULL));
\tTAny* object = NULL; // Instantiation object
\tTInstantiationL proxy = reinterpret_cast<TInstantiationL>(aLibFunctionProxy);''',
        "implementation1 entry",
    )
    load = replace_once(
        load,
        '''\tTImplementationProxy* implementationProxyRow = NULL;
\tTAny* newLPointer = GetNewLPointerAndProxyTableRowL<TImplementationProxy,TInstantiationL>(aUniqueImplementationUid,implementationProxyRow,proxy);
\t// Now create an instance info object''',
        '''\tTImplementationProxy* implementationProxyRow = NULL;
\tif(htcleoNvg) HtcleoEcomLog(0x00000602u, KErrNone, 0u);
\tTAny* newLPointer = GetNewLPointerAndProxyTableRowL<TImplementationProxy,TInstantiationL>(aUniqueImplementationUid,implementationProxyRow,proxy);
\tif(htcleoNvg) HtcleoEcomLog(0x00000603u, KErrNone, (TUint32)(newLPointer != NULL));
\t// Now create an instance info object''',
        "implementation1 proxy table",
    )
    load = replace_once(
        load,
        '''\tCInstanceInfoSimple* instanceInfoSimple = CInstanceInfoSimple::NewL(aPolicy,implementationProxyRow);
\tCleanupStack::PushL(instanceInfoSimple);''',
        '''\tif(htcleoNvg) HtcleoEcomLog(0x00000604u, KErrNone, 0u);
\tCInstanceInfoSimple* instanceInfoSimple = CInstanceInfoSimple::NewL(aPolicy,implementationProxyRow);
\tif(htcleoNvg) HtcleoEcomLog(0x00000605u, KErrNone, (TUint32)(instanceInfoSimple != NULL));
\tCleanupStack::PushL(instanceInfoSimple);
\tif(htcleoNvg) HtcleoEcomLog(0x00000606u, KErrNone, 0u);''',
        "implementation1 instance info",
    )
    load = replace_once(
        load,
        '''\taInstanceKey.iUid = reinterpret_cast<TInt32>(instanceInfoSimple);

\t// Add item to instance info list. This list will contain all of the instance objects.
\tiInstanceInfoList.InsertInAddressOrderL(instanceInfoSimple);''',
        '''\taInstanceKey.iUid = reinterpret_cast<TInt32>(instanceInfoSimple);
\tif(htcleoNvg) HtcleoEcomLog(0x00000607u, KErrNone, (TUint32)aInstanceKey.iUid);

\t// Add item to instance info list. This list will contain all of the instance objects.
\tiInstanceInfoList.InsertInAddressOrderL(instanceInfoSimple);
\tif(htcleoNvg) HtcleoEcomLog(0x00000608u, KErrNone, (TUint32)iInstanceInfoList.Count());''',
        "implementation1 instance insertion",
    )
    load = replace_once(
        load,
        '''\tobject = ImplementationObjectL(aCreationParameters, 
\t aCreationParamsFlag,newLPointer);

\tCleanupStack::Pop(instanceInfoSimple);

\treturn object;''',
        '''\tif(htcleoNvg) HtcleoEcomLog(0x00000609u, KErrNone, (TUint32)aCreationParamsFlag);
\tobject = ImplementationObjectL(aCreationParameters, 
\t aCreationParamsFlag,newLPointer);
\tif(htcleoNvg) HtcleoEcomLog(0x0000060Au, KErrNone, (TUint32)(object != NULL));

\tCleanupStack::Pop(instanceInfoSimple);

\treturn object;''',
        "implementation1 constructor call",
    )

    inline = replace_once(
        inline,
        '''\t{
\tTInt count = 0;
\t
\t// Get the implementation table entry. Note that count gets updated after this call.
\tTImpProxy* implementationTable = aProxy(count);''',
        '''\t{
\tconst TBool htcleoNvg = (aUniqueImplementationUid.iUid == 0x1028653B);
\tif(htcleoNvg) HtcleoEcomLog(0x00000701u, KErrNone, 0u);
\tTInt count = 0;
\t
\t// Get the implementation table entry. Note that count gets updated after this call.
\tif(htcleoNvg) HtcleoEcomLog(0x00000702u, KErrNone, 0u);
\tTImpProxy* implementationTable = aProxy(count);
\tif(htcleoNvg) HtcleoEcomLog(0x00000703u, KErrNone, (TUint32)count);''',
        "proxy call",
    )
    inline = replace_once(
        inline,
        '''\tif (implementationTable==0)
\t\t{
\t\tUser::Leave(KErrNotFound);
\t\t}
\tTAny* newLpointer=NULL;''',
        '''\tif (implementationTable==0)
\t\t{
\t\tUser::Leave(KErrNotFound);
\t\t}
\tif(htcleoNvg) HtcleoEcomLog(0x00000704u, KErrNone, (TUint32)(implementationTable != NULL));
\tTAny* newLpointer=NULL;''',
        "proxy table validation",
    )
    inline = replace_once(
        inline,
        '''\t\tif(aUniqueImplementationUid == implementationTable[i].iImplementationUid)
\t\t\t{
\t\t\tnewLpointer = (TAny*)implementationTable[i].iNewLFuncPtr;
\t\t\taImplementationTableEntry = &implementationTable[i];
\t\t\tbreak;
\t\t\t}''',
        '''\t\tif(aUniqueImplementationUid == implementationTable[i].iImplementationUid)
\t\t\t{
\t\t\tnewLpointer = (TAny*)implementationTable[i].iNewLFuncPtr;
\t\t\taImplementationTableEntry = &implementationTable[i];
\t\t\tif(htcleoNvg) HtcleoEcomLog(0x00000705u, KErrNone, (TUint32)i);
\t\t\tbreak;
\t\t\t}''',
        "proxy row match",
    )
    inline = replace_once(
        inline,
        '''\tif(!newLpointer)
\t\t{
\t\tUser::Leave(KErrNotFound);
\t\t}

\treturn newLpointer;''',
        '''\tif(!newLpointer)
\t\t{
\t\tUser::Leave(KErrNotFound);
\t\t}
\tif(htcleoNvg) HtcleoEcomLog(0x00000706u, KErrNone, (TUint32)(newLpointer != NULL));

\treturn newLpointer;''',
        "proxy row return",
    )

    mmp = replace_once(mmp, 'MACRO ECOM_CLIENT\n',
                       f'MACRO ECOM_CLIENT\nMACRO {MACRO}\n',
                       "ECom logger macro")
    mmp = replace_once(mmp, 'SOURCE\t\tEComEntry.cpp TlsData.cpp\n',
                       'SOURCE\t\tEComEntry.cpp TlsData.cpp\nSOURCE\t\tHtcleoEcomLog.cpp\n',
                       "ECom logger source")

    header_path.write_text(HEADER, encoding="utf-8")
    logger_path.write_text(LOGGER, encoding="utf-8")
    session_path.write_text(session, encoding="utf-8")
    load_path.write_text(load, encoding="utf-8")
    unload_path.write_text(unload, encoding="utf-8")
    inline_path.write_text(inline, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    verify(args.root)
    print("HTCLEO_ECOM_CLIENT_DURABLE_LOG=installed checkpoints=64 capacity=16384 bytes=737280 path=C:\\Symbian3\\ECOMLOG.TXT")


if __name__ == "__main__":
    main()
