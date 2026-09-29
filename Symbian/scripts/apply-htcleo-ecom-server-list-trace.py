#!/usr/bin/env python3
"""Install a dedicated durable trace around the FeatMgr ECom server list IPC.

The trace is diagnostic-only.  It does not change resolver selection, retries,
message completion, leave handling, timing policy, or display state.  Records
are written by ecomserver.exe to C:\\Symbian3\\ECOMSRV.TXT.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_SERVER_FEATMGR_LIST_TRACE_V1"
LOGGER_MARKER = "HTCLEO_ECOM_SERVER_DURABLE_LOG_V1"
CAPACITY_MARKER = "HTCLEO_ECOM_SERVER_LOG_CAPACITY_16384_V2"
EXACT_ARM_MARKER = "HTCLEO_ECOM_SERVER_EXACT_REQUEST_ARM_V2"
REGISTRY_LIST_MARKER = "HTCLEO_ECOM_SERVER_REGISTRY_LIST_TRACE_V3"
MACRO = "__HTCLEO_ECOM_SERVER_DURABLE_LOG__"
INTERFACE_UID = "0x10205057u"
RESOLVER_UID = "0x10009D92u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def add_after(text: str, anchor: str, addition: str, label: str) -> str:
    return replace_once(text, anchor, anchor + addition, label)


HEADER = r'''#ifndef HTCLEO_ECOM_SERVER_DURABLE_LOG_H
#define HTCLEO_ECOM_SERVER_DURABLE_LOG_H

#include <e32std.h>

#ifdef __HTCLEO_ECOM_SERVER_DURABLE_LOG__
void HtcleoEcomServerArm();
void HtcleoEcomServerDisarm();
void HtcleoEcomServerLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoEcomServerArm() {}
static inline void HtcleoEcomServerDisarm() {}
static inline void HtcleoEcomServerLog(TUint32, TInt, TUint32) {}
#endif

#endif
'''


LOGGER = r'''// HTCLEO_ECOM_SERVER_DURABLE_LOG_V1
#include "HtcleoEcomServerLog.h"

#ifdef __HTCLEO_ECOM_SERVER_DURABLE_LOG__
#include <f32file.h>

// HTCLEO_ECOM_SERVER_EXACT_REQUEST_ARM_V2
static TBool gHtcleoEcomServerArmed = EFalse;

void HtcleoEcomServerArm()
	{
	if(gHtcleoEcomServerArmed)
		return;

	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		return;
	_LIT(KHtcleoEcomServerArmDir, "C:\\Symbian3\\");
	_LIT(KHtcleoEcomServerArmPath, "C:\\Symbian3\\ECOMSRV.TXT");
	r = fs.MkDirAll(KHtcleoEcomServerArmDir);
	if(r == KErrNone || r == KErrAlreadyExists)
		{
		RFile file;
		r = file.Replace(fs, KHtcleoEcomServerArmPath,
			EFileWrite | EFileShareAny);
		file.Close();
		}
	fs.Close();
	if(r == KErrNone)
		gHtcleoEcomServerArmed = ETrue;
	}

void HtcleoEcomServerDisarm()
	{
	gHtcleoEcomServerArmed = EFalse;
	}

void HtcleoEcomServerLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                               __attribute__((noinline));

void HtcleoEcomServerLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	if(!gHtcleoEcomServerArmed)
		return;

	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		return;

	_LIT(KHtcleoEcomServerLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoEcomServerLogPath, "C:\\Symbian3\\ECOMSRV.TXT");
	r = fs.MkDirAll(KHtcleoEcomServerLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoEcomServerLogPath, EFileWrite | EFileShareAny);
	if(r == KErrNotFound || r == KErrPathNotFound)
		r = file.Replace(fs, KHtcleoEcomServerLogPath,
			EFileWrite | EFileShareAny);
	else if(r == KErrNone)
		r = file.Seek(ESeekEnd, position);

	// Each record is 45 bytes.  The offset supplies a sequence number without
	// writable process globals.
	// HTCLEO_ECOM_SERVER_LOG_CAPACITY_16384_V2
	if(r == KErrNone && position < (16384 * 45))
		{
		_LIT8(KHtcleoEcomServerPrefix, "HTCLEO_ESRV ");
		TBuf8<64> record;
		record.Append(KHtcleoEcomServerPrefix);
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
			(void)file.Flush();
		}

	file.Close();
	fs.Close();
	}
#endif
'''


def patch_start(text: str) -> str:
    text = add_after(
        text,
        '#include "EComServer.h"\n',
        '#include "HtcleoEcomServerLog.h"\n\n// ' + MARKER + '\n',
        "server-start include",
    )
    text = replace_once(
        text,
        "\t{\n\t// naming the server thread after the server helps to debug panics\n"
        "    User::LeaveIfError(User::RenameThread(KEComServerName));",
        "\t{\n\tHtcleoEcomServerLog(0x0000F300u, KErrNone, 0u);\n"
        "\t// naming the server thread after the server helps to debug panics\n"
        "    TInt htcleoRenameResult = User::RenameThread(KEComServerName);\n"
        "\tHtcleoEcomServerLog(0x0000F301u, htcleoRenameResult, 0u);\n"
        "\tUser::LeaveIfError(htcleoRenameResult);",
        "RunServerL entry",
    )
    text = add_after(
        text,
        "\tCActiveScheduler* scheduler=new(ELeave) CActiveScheduler;\n",
        "\tHtcleoEcomServerLog(0x0000F302u, KErrNone, (TUint32)scheduler);\n",
        "scheduler allocation",
    )
    text = add_after(
        text,
        "\tCActiveScheduler::Install(scheduler);\n",
        "\tHtcleoEcomServerLog(0x0000F303u, KErrNone, 0u);\n",
        "scheduler install",
    )
    text = add_after(
        text,
        "\tCEComServer::NewLC();\n",
        "\tHtcleoEcomServerLog(0x0000F304u, KErrNone, 0u);\n",
        "server NewLC",
    )
    text = replace_once(
        text,
        "\tRProcess::Rendezvous(KErrNone);\n",
        "\tHtcleoEcomServerLog(0x0000F305u, KErrNone, 0u);\n"
        "\tRProcess::Rendezvous(KErrNone);\n"
        "\tHtcleoEcomServerLog(0x0000F306u, KErrNone, 0u);\n",
        "server rendezvous",
    )
    text = replace_once(
        text,
        "\tCActiveScheduler::Start();\n",
        "\tHtcleoEcomServerLog(0x0000F307u, KErrNone, 0u);\n"
        "\tCActiveScheduler::Start();\n"
        "\tHtcleoEcomServerLog(0x0000F308u, KErrNone, 0u);\n",
        "scheduler start",
    )
    text = add_after(
        text,
        "\tCleanupStack::PopAndDestroy(2, scheduler);\n",
        "\tHtcleoEcomServerLog(0x0000F309u, KErrNone, 0u);\n",
        "RunServerL cleanup",
    )
    text = replace_once(
        text,
        "TInt ServerStart()\n\t{\n\tCTrapCleanup* cleanup=CTrapCleanup::New();",
        "TInt ServerStart()\n\t{\n"
        "\tHtcleoEcomServerLog(0x0000F30Au, KErrNone, 0u);\n"
        "\tCTrapCleanup* cleanup=CTrapCleanup::New();\n"
        "\tHtcleoEcomServerLog(0x0000F30Bu, KErrNone, (TUint32)cleanup);",
        "ServerStart entry",
    )
    text = add_after(
        text,
        "\t\tTRAP(err,RunServerL());\n",
        "\t\tHtcleoEcomServerLog(0x0000F30Cu, err, 0u);\n",
        "ServerStart trap",
    )
    text = add_after(
        text,
        "\t\tdelete cleanup;\n",
        "\t\tHtcleoEcomServerLog(0x0000F30Du, KErrNone, 0u);\n",
        "ServerStart cleanup",
    )
    text = replace_once(
        text,
        "\treturn err;\t\n\t}",
        "\tHtcleoEcomServerLog(0x0000F30Eu, err, 0u);\n"
        "\treturn err;\t\n\t}",
        "ServerStart return",
    )
    text = replace_once(
        text,
        "\t{\n\t__UHEAP_MARK;\n\t__ECOM_TRACE(\"ECOM: Server started, initialisation begun\");",
        "\t{\n\t__UHEAP_MARK;\n"
        "\tHtcleoEcomServerLog(0x0000F30Fu, KErrNone, 0u);\n"
        "\t__ECOM_TRACE(\"ECOM: Server started, initialisation begun\");",
        "E32Main entry",
    )
    text = add_after(
        text,
        "\tTInt err = ServerStart();\n",
        "\tHtcleoEcomServerLog(0x0000F310u, err, 0u);\n",
        "E32Main ServerStart",
    )
    text = replace_once(
        text,
        "\t__UHEAP_MARKEND;\n\treturn err;",
        "\t__UHEAP_MARKEND;\n"
        "\tHtcleoEcomServerLog(0x0000F311u, err, 0u);\n"
        "\treturn err;",
        "E32Main return",
    )
    return text


def patch_session(text: str) -> str:
    text = add_after(
        text,
        '#include "EComDebug.h"\n',
        '#include "HtcleoEcomServerLog.h"\n',
        "server-session include",
    )
    old_wrapper = '''void CEComServerSession::ServiceL(const RMessage2& aMessage)
{
	const TClientRequest msg(aMessage);
	ServiceL(msg);
}'''
    new_wrapper = '''void CEComServerSession::ServiceL(const RMessage2& aMessage)
{
	const TBool htcleoTrace =
		(aMessage.Function() == EListCustomResolvedImplementations);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F320u, KErrNone,
			(TUint32)aMessage.Function());
	const TClientRequest msg(aMessage);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F321u, KErrNone, 0u);
	ServiceL(msg);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F322u, KErrNone, 0u);
}'''
    text = replace_once(text, old_wrapper, new_wrapper, "ServiceL wrapper")
    text = replace_once(
        text,
        "\t{\n\tTInt completionCode = KErrNone;\n\tTBool asyncRequest = EFalse;\n\n\tswitch (aMessage.Function())",
        "\t{\n\tconst TBool htcleoTrace =\n"
        "\t\t(aMessage.Function() == EListCustomResolvedImplementations);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F323u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\tTInt completionCode = KErrNone;\n\tTBool asyncRequest = EFalse;\n\n"
        "\tswitch (aMessage.Function())",
        "ServiceL internal entry",
    )
    text = replace_once(
        text,
        "\tcase EListCustomResolvedImplementations:\n\t\tif(Server().RegistryIndexValid())\n\t\t\t{",
        "\tcase EListCustomResolvedImplementations:\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F324u, KErrNone,\n"
        "\t\t\t\t(TUint32)Server().RegistryIndexValid());\n"
        "\t\tif(Server().RegistryIndexValid())\n\t\t\t{",
        "list registry state",
    )
    text = replace_once(
        text,
        "RECORD_CLIENT_REQUEST_START_TIMER_RESULT(EEComListRequestType, Server().GetCurrentStartupState());\n"
        "\t\t\tDoListImplementationsL(aMessage);\n"
        "RECORD_CLIENT_REQUEST_END_TIMER_RESULT;",
        "RECORD_CLIENT_REQUEST_START_TIMER_RESULT(EEComListRequestType, Server().GetCurrentStartupState());\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F325u, KErrNone, 0u);\n"
        "\t\t\tDoListImplementationsL(aMessage);\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F326u, KErrNone, 0u);\n"
        "RECORD_CLIENT_REQUEST_END_TIMER_RESULT;",
        "list dispatch",
    )
    text = replace_once(
        text,
        "\tif (!asyncRequest)\n\t\taMessage.Complete(completionCode);",
        "\tif (!asyncRequest)\n\t\t{\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F327u, completionCode, 0u);\n"
        "\t\taMessage.Complete(completionCode);\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F328u, completionCode, 0u);\n"
        "\t\t}",
        "message completion",
    )

    text = replace_once(
        text,
        "\t{\n\t\n\t//now get the matchString and extendedInterfaces",
        "\t{\n\tconst TBool htcleoTrace =\n"
        "\t\t(aMessage.Function() == EListCustomResolvedImplementations);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F370u, KErrNone, 0u);\n\t\n"
        "\t//now get the matchString and extendedInterfaces",
        "unpack entry",
    )
    text = add_after(
        text,
        "\tTInt sizeOfMatchStrExtInfBuf = aMessage.GetDesLength(KIPCParameterMatchStrExtInf);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F371u, sizeOfMatchStrExtInfBuf, 0u);\n",
        "unpack descriptor length",
    )
    text = add_after(
        text,
        "\tmatchStrExtInfBuf.CreateMaxL(sizeOfMatchStrExtInfBuf);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F372u, KErrNone,\n"
        "\t\t\t(TUint32)matchStrExtInfBuf.MaxLength());\n",
        "unpack buffer create",
    )
    text = add_after(
        text,
        "\taMessage.ReadL(KIPCParameterMatchStrExtInf,matchStrExtInfBuf);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F373u, KErrNone,\n"
        "\t\t\t(TUint32)matchStrExtInfBuf.Length());\n",
        "unpack buffer read",
    )
    text = add_after(
        text,
        "\treadStream.Open(matchStrExtInfBuf);\n",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F374u, KErrNone, 0u);\n",
        "unpack stream open",
    )
    text = add_after(
        text,
        "\tTInt lenOfMatchStr = readStream.ReadInt32L();\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F375u, KErrNone,\n"
        "\t\t\t(TUint32)lenOfMatchStr);\n",
        "unpack match length",
    )
    text = add_after(
        text,
        "\taMatchStr.CreateMaxL(lenOfMatchStr);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F376u, KErrNone,\n"
        "\t\t\t(TUint32)aMatchStr.MaxLength());\n",
        "unpack match create",
    )
    text = replace_once(
        text,
        "\t\treadStream.ReadL(aMatchStr,lenOfMatchStr);\t\t\n\t\t}",
        "\t\treadStream.ReadL(aMatchStr,lenOfMatchStr);\t\t\n\t\t}\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F377u, KErrNone,\n"
        "\t\t\t(TUint32)aMatchStr.Length());",
        "unpack match read",
    )
    text = add_after(
        text,
        "\tTInt numOfExtendedInterfaces = readStream.ReadInt32L();\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F378u, KErrNone,\n"
        "\t\t\t(TUint32)numOfExtendedInterfaces);\n",
        "unpack extended count",
    )
    text = replace_once(
        text,
        "\t\taExtendedInterfaces.AppendL(TUid::Uid(readStream.ReadInt32L()));\n",
        "\t\tTUid htcleoExtendedUid = TUid::Uid(readStream.ReadInt32L());\n"
        "\t\taExtendedInterfaces.AppendL(htcleoExtendedUid);\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F379u, i,\n"
        "\t\t\t\t(TUint32)htcleoExtendedUid.iUid);\n",
        "unpack extended loop",
    )
    text = add_after(
        text,
        "\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf); \n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F37Au, KErrNone,\n"
        "\t\t\t(TUint32)aExtendedInterfaces.Count());\n",
        "unpack return",
    )

    text = replace_once(
        text,
        "void CEComServerSession::DoListImplementationsL(const TClientRequest& aMessage)\n"
        "\t{\n\t// Unpack the client supplied parameters",
        "void CEComServerSession::DoListImplementationsL(const TClientRequest& aMessage)\n"
        "\t{\n\tconst TBool htcleoTrace =\n"
        "\t\t(aMessage.Function() == EListCustomResolvedImplementations);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F340u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.Function());\n"
        "\t// Unpack the client supplied parameters",
        "DoList entry",
    )
    text = add_after(
        text,
        "\tTPckg<TUidType> uidsPkg(uids);\t\n",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F341u, KErrNone, 0u);\n",
        "DoList UID pre-read",
    )
    text = add_after(
        text,
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F341u, KErrNone, 0u);\n"
        "\taMessage.ReadL(KIPCParameterUids, uidsPkg);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F342u, KErrNone,\n"
        "\t\t\t(TUint32)uids[KInterfaceUidIndex].iUid);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F343u, KErrNone,\n"
        "\t\t\t(TUint32)uids[KResolverUidIndex].iUid);\n",
        "DoList UID read",
    )
    text = add_after(
        text,
        "  \tTPckg<TListImplParam> listParamPkg(listParam);\n",
        "  \tif(htcleoTrace)\n  \t\tHtcleoEcomServerLog(0x0000F344u, KErrNone, 0u);\n",
        "DoList list-param pre-read",
    )
    text = add_after(
        text,
        "  \taMessage.ReadL(2,listParamPkg);\n",
        "  \tif(htcleoTrace)\n"
        "  \t\tHtcleoEcomServerLog(0x0000F345u, KErrNone,\n"
        "  \t\t\t(TUint32)listParam.iBufferSize);\n"
        "  \tif(htcleoTrace)\n"
        "  \t\tHtcleoEcomServerLog(0x0000F346u,\n"
        "  \t\t\t(TInt)listParam.iCapabilityCheck,\n"
        "  \t\t\t(TUint32)listParam.iMatchType);\n",
        "DoList list-param read",
    )
    text = replace_once(
        text,
        "\tRBuf8 matchStr;\n\tRExtendedInterfacesArray extendedInterfaces;\n"
        "\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);",
        "\tRBuf8 matchStr;\n\tRExtendedInterfacesArray extendedInterfaces;\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F347u, KErrNone, 0u);\n"
        "\tUnpackMatchStrAndExtendedInterfacesFromClientL(aMessage,extendedInterfaces,matchStr);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F348u, KErrNone,\n"
        "\t\t\t(TUint32)matchStr.Length());\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F349u, KErrNone,\n"
        "\t\t\t(TUint32)extendedInterfaces.Count());",
        "DoList unpack",
    )
    text = add_after(
        text,
        "\tiListContext = aMessage.Function();\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F34Au, KErrNone,\n"
        "\t\t\t(TUint32)iListContext);\n",
        "DoList context",
    )
    text = replace_once(
        text,
        "\t\tcase EListCustomResolvedImplementations:\n"
        "\t\t\tif(uids[KResolverUidIndex] == KNullUid)",
        "\t\tcase EListCustomResolvedImplementations:\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F34Bu, KErrNone,\n"
        "\t\t\t\t\t(TUint32)uids[KResolverUidIndex].iUid);\n"
        "\t\t\tif(uids[KResolverUidIndex] == KNullUid)",
        "DoList custom pre-call",
    )
    text = add_after(
        text,
        "\t\t\tiList = Server().ListImplementationsL( uids[KInterfaceUidIndex], resolverParameters, uids[KResolverUidIndex], extendedInterfaces, aMessage);\n",
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F34Cu, KErrNone,\n"
        "\t\t\t\t\t(TUint32)iList);\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F34Du, KErrNone,\n"
        "\t\t\t\t\t(TUint32)(iList ? iList->Count() : 0));\n",
        "DoList custom return",
    )
    text = replace_once(
        text,
        "\t//Now cleanup the extended interface\n"
        "\tCleanupStack::PopAndDestroy(&extendedInterfaces);\n"
        "\tCleanupStack::PopAndDestroy(&matchStr);",
        "\t//Now cleanup the extended interface\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F34Eu, KErrNone, 0u);\n"
        "\tCleanupStack::PopAndDestroy(&extendedInterfaces);\n"
        "\tCleanupStack::PopAndDestroy(&matchStr);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F34Fu, KErrNone, 0u);",
        "DoList cleanup params",
    )
    text = add_after(
        text,
        "\tTInt bufferSizeRequired=0;\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F350u, KErrNone, (TUint32)iList);\n",
        "DoList packaging entry",
    )
    text = replace_once(
        text,
        "\tif(iList)\n\t\t{\n\t\tif(iList->Count()>0)",
        "\tif(iList)\n\t\t{\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F351u, KErrNone,\n"
        "\t\t\t\t(TUint32)iList->Count());\n"
        "\t\tif(iList->Count()>0)",
        "DoList list count",
    )
    text = add_after(
        text,
        "\t\t\tCBufFlat* memoryStore = CBufFlat::NewL(KDefaultStoreSize);\n",
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F352u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)memoryStore);\n",
        "DoList memory store",
    )
    text = add_after(
        text,
        "\t\t\twriteStream.Open(*iMemoryStore);\n",
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F353u, KErrNone, 0u);\n",
        "DoList stream open",
    )
    text = add_after(
        text,
        "\t\t\twriteStream.WriteInt32L(entryCount);\n",
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F354u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)entryCount);\n",
        "DoList write count",
    )
    text = replace_once(
        text,
        "\t\t\tfor(TInt i = 0; i < entryCount; ++i)\n"
        "\t\t\t\t(*iList)[i]->ExternalizeL(ETrue,writeStream);",
        "\t\t\tfor(TInt i = 0; i < entryCount; ++i)\n"
        "\t\t\t\t{\n"
        "\t\t\t\tif(htcleoTrace)\n"
        "\t\t\t\t\tHtcleoEcomServerLog(0x0000F355u, i,\n"
        "\t\t\t\t\t\t(TUint32)(*iList)[i]);\n"
        "\t\t\t\t(*iList)[i]->ExternalizeL(ETrue,writeStream);\n"
        "\t\t\t\tif(htcleoTrace)\n"
        "\t\t\t\t\tHtcleoEcomServerLog(0x0000F356u, i, 0u);\n"
        "\t\t\t\t}",
        "DoList externalize loop",
    )
    text = replace_once(
        text,
        "\t\t\twriteStream.CommitL();\n\n\t\t\t// Set to actual size",
        "\t\t\twriteStream.CommitL();\n"
        "\t\t\tif(htcleoTrace)\n\t\t\t\tHtcleoEcomServerLog(0x0000F357u, KErrNone, 0u);\n\n"
        "\t\t\t// Set to actual size",
        "DoList commit",
    )
    text = add_after(
        text,
        "\t\t\tbufferSizeRequired=iMemoryStore->Size();\n",
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F358u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)bufferSizeRequired);\n",
        "DoList size",
    )
    text = add_after(
        text,
        "\t\t\tCleanupInternalList();\t\n",
        "\t\t\tif(htcleoTrace)\n\t\t\t\tHtcleoEcomServerLog(0x0000F359u, KErrNone, 0u);\n",
        "DoList cleanup list",
    )
    text = replace_once(
        text,
        "\t//if nothing is returned we should still indicate this to the client side\n"
        "\tif (bufferSizeRequired==0)",
        "\t//if nothing is returned we should still indicate this to the client side\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F35Au, KErrNone,\n"
        "\t\t\t(TUint32)bufferSizeRequired);\n"
        "\tif (bufferSizeRequired==0)",
        "DoList post packaging",
    )
    text = replace_once(
        text,
        "\t\tlistParam.iBufferSize=0;\n  \t\taMessage.WriteL(2,listParamPkg);\n\t\treturn;",
        "\t\tlistParam.iBufferSize=0;\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F35Bu, KErrNone, 0u);\n"
        "  \t\taMessage.WriteL(2,listParamPkg);\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F35Cu, KErrNone, 0u);\n"
        "\t\treturn;",
        "DoList empty return",
    )
    text = replace_once(
        text,
        "\tif (listParam.iBufferSize >= bufferSizeRequired)\n\t\t{",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F35Du,\n"
        "\t\t\t(TInt)listParam.iBufferSize, (TUint32)bufferSizeRequired);\n"
        "\tif (listParam.iBufferSize >= bufferSizeRequired)\n\t\t{",
        "DoList size compare",
    )
    text = replace_once(
        text,
        "\t\t\tlistParam.iBufferSize=bufferSizeRequired;\n  \t\t\taMessage.WriteL(2,listParamPkg);\n"
        "\t\t\tTPtr8 data=iMemoryStore->Ptr(0);\n\t\t\taMessage.WriteL(3,data);\n"
        "\t\t\tdelete iMemoryStore;\n\t\t\tiMemoryStore=NULL;",
        "\t\t\tlistParam.iBufferSize=bufferSizeRequired;\n"
        "\t\t\tif(htcleoTrace)\n\t\t\t\tHtcleoEcomServerLog(0x0000F35Eu, KErrNone, 0u);\n"
        "  \t\t\taMessage.WriteL(2,listParamPkg);\n"
        "\t\t\tif(htcleoTrace)\n\t\t\t\tHtcleoEcomServerLog(0x0000F35Fu, KErrNone, 0u);\n"
        "\t\t\tTPtr8 data=iMemoryStore->Ptr(0);\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F360u, KErrNone,\n"
        "\t\t\t\t\t(TUint32)data.Length());\n"
        "\t\t\taMessage.WriteL(3,data);\n"
        "\t\t\tif(htcleoTrace)\n\t\t\t\tHtcleoEcomServerLog(0x0000F361u, KErrNone, 0u);\n"
        "\t\t\tdelete iMemoryStore;\n\t\t\tiMemoryStore=NULL;\n"
        "\t\t\tif(htcleoTrace)\n\t\t\t\tHtcleoEcomServerLog(0x0000F362u, KErrNone, 0u);",
        "DoList fitting response",
    )
    text = replace_once(
        text,
        "\telse\n\t\t{\n\t\t//write back the bufferSize\n"
        "\t\tlistParam.iBufferSize=bufferSizeRequired;\n  \t\taMessage.WriteL(2,listParamPkg);\n"
        "\t\tUser::Leave(KErrOverflow);",
        "\telse\n\t\t{\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F363u, KErrOverflow,\n"
        "\t\t\t\t(TUint32)bufferSizeRequired);\n"
        "\t\t//write back the bufferSize\n"
        "\t\tlistParam.iBufferSize=bufferSizeRequired;\n"
        "  \t\taMessage.WriteL(2,listParamPkg);\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F364u, KErrNone,\n"
        "\t\t\t\t(TUint32)bufferSizeRequired);\n"
        "\t\tUser::Leave(KErrOverflow);",
        "DoList overflow response",
    )
    return text


def patch_server(text: str) -> str:
    text = add_after(
        text,
        '#include "EComPatchDataConstantv2.h"\n',
        '#include "HtcleoEcomServerLog.h"\n',
        "server include",
    )
    text = replace_once(
        text,
        "\t{\n\tif (aError == KErrBadDescriptor)",
        "\t{\n"
        "\tHtcleoEcomServerLog(0x0000F329u, aError,\n"
        "\t\t(TUint32)Message().Function());\n"
        "\tif (aError == KErrBadDescriptor)",
        "RunError entry",
    )
    text = add_after(
        text,
        "\t\tMessage().Complete(aError);\n\t\t}\n",
        "\tHtcleoEcomServerLog(0x0000F32Au, aError, 0u);\n",
        "RunError complete",
    )
    text = add_after(
        text,
        "\tReStart();\n",
        "\tHtcleoEcomServerLog(0x0000F32Bu, aError, 0u);\n",
        "RunError restart",
    )

    anchor = '''RImplInfoArray* CEComServer::ListImplementationsL(TUid aInterfaceUid, 
											   const TEComResolverParams& aAdditionalParameters, 
											   TUid aResolverUid,
											   const RExtendedInterfacesArray& aExtendedInterfaces,
											   const TClientRequest& aMessage
											   ) 
	{
	RImplInfoArray* result = NULL;'''
    replacement = anchor[:-len("\tRImplInfoArray* result = NULL;")] + '''	const TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F380u, KErrNone,
			(TUint32)aInterfaceUid.iUid);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F381u, KErrNone,
			(TUint32)aResolverUid.iUid);
	RImplInfoArray* result = NULL;'''
    text = replace_once(text, anchor, replacement, "server custom list entry")
    text = add_after(
        text,
        "\tTBool capability= ETrue;\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F382u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.IsNull());\n",
        "server custom message state",
    )
    # This read sequence occurs first in the custom-resolver overload.
    text = replace_once(
        text,
        "\t\tTListImplParam listParam;\n  \t\tTPckg<TListImplParam> listParamPkg(listParam);\n  \t\taMessage.ReadL(2,listParamPkg);\n  \t\tcapability=listParam.iCapabilityCheck;",
        "\t\tTListImplParam listParam;\n"
        "  \t\tTPckg<TListImplParam> listParamPkg(listParam);\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F383u, KErrNone, 0u);\n"
        "  \t\taMessage.ReadL(2,listParamPkg);\n"
        "  \t\tcapability=listParam.iCapabilityCheck;\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F384u,\n"
        "\t\t\t\t(TInt)capability, (TUint32)listParam.iBufferSize);",
        "server custom list-param read",
    )
    text = replace_once(
        text,
        "  \t\n  \t\n\tCRegistryResolveTransaction* registryResolveTransaction = CRegistryResolveTransaction::NewL(*iRegistryData,",
        "  \t\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F385u, KErrNone, 0u);\n"
        "\tCRegistryResolveTransaction* registryResolveTransaction = CRegistryResolveTransaction::NewL(*iRegistryData,",
        "server custom transaction pre-new",
    )
    text = add_after(
        text,
        "\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\taMessage,capability);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F386u, KErrNone,\n"
        "\t\t\t(TUint32)registryResolveTransaction);\n",
        "server custom transaction new",
    )
    # The long formatting of the call above can vary; remaining anchors are local.
    text = add_after(
        text,
        "\tCleanupStack::PushL(registryResolveTransaction);\n",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F387u, KErrNone, 0u);\n",
        "server custom transaction push",
    )
    text = replace_once(
        text,
        "\t//create resolver\n\tresolver = CreateResolverLC(aResolverUid,registryResolveTransaction);\n"
        "\tresult = ListImplementationsL(aInterfaceUid, aAdditionalParameters, resolver);",
        "\t//create resolver\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F388u, KErrNone, 0u);\n"
        "\tresolver = CreateResolverLC(aResolverUid,registryResolveTransaction);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F389u, KErrNone, (TUint32)resolver);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F38Au, KErrNone, 0u);\n"
        "\tresult = ListImplementationsL(aInterfaceUid, aAdditionalParameters, resolver);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F38Bu, KErrNone, (TUint32)result);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F38Cu, KErrNone,\n"
        "\t\t\t(TUint32)(result ? result->Count() : 0));",
        "server custom resolver and list",
    )
    text = replace_once(
        text,
        "\tCleanupStack::PopAndDestroy(resolver);\n"
        "\tCleanupStack::PopAndDestroy(registryResolveTransaction);",
        "\tCleanupStack::PopAndDestroy(resolver);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F38Du, KErrNone, 0u);\n"
        "\tCleanupStack::PopAndDestroy(registryResolveTransaction);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F38Eu, KErrNone, 0u);",
        "server custom cleanup",
    )
    text = replace_once(
        text,
        "\t\tiResolverLibrary.Close();\n\t\t}\n\treturn result;",
        "\t\tiResolverLibrary.Close();\n\t\t}\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F38Fu, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F390u, KErrNone,\n"
        "\t\t\t(TUint32)result);\n"
        "\treturn result;",
        "server custom return",
    )

    text = replace_once(
        text,
        "\t{\n\tCResolver* resolver = NULL;\n\tif(aResolverUid == KDefaultResolverUid)",
        "\t{\n\tconst TBool htcleoTrace = (aResolverUid == KRomOnlyResolverUid);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F391u, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\tCResolver* resolver = NULL;\n\tif(aResolverUid == KDefaultResolverUid)",
        "CreateResolver entry",
    )
    text = replace_once(
        text,
        "\t\tresolver = static_cast<CResolver*>(CRomOnlyResolver::NewL(*aRegistryResolveTransaction));\n"
        "\t\tCleanupStack::PushL(resolver);",
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F392u, KErrNone, 0u);\n"
        "\t\tresolver = static_cast<CResolver*>(CRomOnlyResolver::NewL(*aRegistryResolveTransaction));\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F393u, KErrNone,\n"
        "\t\t\t\t(TUint32)resolver);\n"
        "\t\tCleanupStack::PushL(resolver);\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F394u, KErrNone, 0u);",
        "CreateResolver ROM-only",
    )
    text = replace_once(
        text,
        "\treturn resolver;\n\t}\n\n/**\nCreates custom resolver object",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F395u, KErrNone, (TUint32)resolver);\n"
        "\treturn resolver;\n\t}\n\n/**\nCreates custom resolver object",
        "CreateResolver return",
    )

    text = replace_once(
        text,
        "\t{\n\tif(!aResolver)\n\t\tUser::Leave(KEComErrNoResolver);\n"
        "\t// Use the client provided resolver to build up the list.\n"
        "\tRImplInfoArray* infoArray = aResolver->ListAllL(aInterfaceUid, aAdditionalParameters);\n"
        "\treturn infoArray;",
        "\t{\n\tconst TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F396u, KErrNone, (TUint32)aResolver);\n"
        "\tif(!aResolver)\n\t\tUser::Leave(KEComErrNoResolver);\n"
        "\t// Use the client provided resolver to build up the list.\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F397u, KErrNone, 0u);\n"
        "\tRImplInfoArray* infoArray = aResolver->ListAllL(aInterfaceUid, aAdditionalParameters);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F398u, KErrNone, (TUint32)infoArray);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F399u, KErrNone,\n"
        "\t\t\t(TUint32)(infoArray ? infoArray->Count() : 0));\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F39Au, KErrNone, 0u);\n"
        "\treturn infoArray;",
        "server private list helper",
    )
    return text


def patch_server_v2(text: str) -> str:
    """Patch EComServer.cpp using function-bounded regions.

    The stock file contains several overloads with deliberately identical local
    variable names, so whole-file anchors are unsafe here.
    """
    text = add_after(
        text,
        '#include "EComPatchDataConstantv2.h"\n',
        '#include "HtcleoEcomServerLog.h"\n',
        "server include",
    )

    run_start = text.index("TInt CEComServer::RunError(TInt aError)")
    run_end = text.index("/**\nCreates resolver object", run_start)
    run = text[run_start:run_end]
    run = replace_once(
        run,
        "\t{\n\tif (aError == KErrBadDescriptor)",
        "\t{\n"
        "\tHtcleoEcomServerLog(0x0000F329u, aError,\n"
        "\t\t(TUint32)Message().Function());\n"
        "\tif (aError == KErrBadDescriptor)",
        "RunError entry",
    )
    run = add_after(
        run,
        "\t\tMessage().Complete(aError);\n\t\t}\n",
        "\tHtcleoEcomServerLog(0x0000F32Au, aError, 0u);\n",
        "RunError complete",
    )
    run = add_after(
        run,
        "\tReStart();\n",
        "\tHtcleoEcomServerLog(0x0000F32Bu, aError, 0u);\n",
        "RunError restart",
    )
    text = text[:run_start] + run + text[run_end:]

    first_list = text.index("RImplInfoArray* CEComServer::ListImplementationsL")
    second_list = text.index(
        "RImplInfoArray* CEComServer::ListImplementationsL", first_list + 1
    )
    region = text[first_list:second_list]
    region = replace_once(
        region,
        "\t{\n\tRImplInfoArray* result = NULL;",
        "\t{\n\tconst TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F380u, KErrNone,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F381u, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\tRImplInfoArray* result = NULL;",
        "server custom list entry",
    )
    region = add_after(
        region,
        "\tTBool capability= ETrue;\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F382u, KErrNone,\n"
        "\t\t\t(TUint32)aMessage.IsNull());\n",
        "server custom message state",
    )
    region = replace_once(
        region,
        "\t\tTListImplParam listParam;\n  \t\tTPckg<TListImplParam> listParamPkg(listParam);\n"
        "  \t\taMessage.ReadL(2,listParamPkg);\n  \t\tcapability=listParam.iCapabilityCheck;",
        "\t\tTListImplParam listParam;\n"
        "  \t\tTPckg<TListImplParam> listParamPkg(listParam);\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F383u, KErrNone, 0u);\n"
        "  \t\taMessage.ReadL(2,listParamPkg);\n"
        "  \t\tcapability=listParam.iCapabilityCheck;\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F384u,\n"
        "\t\t\t\t(TInt)capability, (TUint32)listParam.iBufferSize);",
        "server custom list-param read",
    )
    region = replace_once(
        region,
        "\tCRegistryResolveTransaction* registryResolveTransaction = CRegistryResolveTransaction::NewL(*iRegistryData,",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F385u, KErrNone, 0u);\n"
        "\tCRegistryResolveTransaction* registryResolveTransaction = CRegistryResolveTransaction::NewL(*iRegistryData,",
        "server custom transaction pre-new",
    )
    region = add_after(
        region,
        "aMessage,capability);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F386u, KErrNone,\n"
        "\t\t\t(TUint32)registryResolveTransaction);\n",
        "server custom transaction new",
    )
    region = add_after(
        region,
        "\tCleanupStack::PushL(registryResolveTransaction);\n",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F387u, KErrNone, 0u);\n",
        "server custom transaction push",
    )
    region = replace_once(
        region,
        "\t//create resolver\n\tresolver = CreateResolverLC(aResolverUid,registryResolveTransaction);\n"
        "\tresult = ListImplementationsL(aInterfaceUid, aAdditionalParameters, resolver);",
        "\t//create resolver\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F388u, KErrNone, 0u);\n"
        "\tresolver = CreateResolverLC(aResolverUid,registryResolveTransaction);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F389u, KErrNone, (TUint32)resolver);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F38Au, KErrNone, 0u);\n"
        "\tresult = ListImplementationsL(aInterfaceUid, aAdditionalParameters, resolver);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F38Bu, KErrNone, (TUint32)result);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F38Cu, KErrNone,\n"
        "\t\t\t(TUint32)(result ? result->Count() : 0));",
        "server custom resolver and list",
    )
    region = replace_once(
        region,
        "\tCleanupStack::PopAndDestroy(resolver);\n"
        "\tCleanupStack::PopAndDestroy(registryResolveTransaction);",
        "\tCleanupStack::PopAndDestroy(resolver);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F38Du, KErrNone, 0u);\n"
        "\tCleanupStack::PopAndDestroy(registryResolveTransaction);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F38Eu, KErrNone, 0u);",
        "server custom cleanup",
    )
    region = replace_once(
        region,
        "\treturn result;\n\t}\n\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F38Fu, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F390u, KErrNone, (TUint32)result);\n"
        "\treturn result;\n\t}\n\n",
        "server custom return",
    )
    text = text[:first_list] + region + text[second_list:]

    create_start = text.index("CResolver* CEComServer::CreateResolverLC")
    create_end = text.index("/**\nCreates custom resolver object", create_start)
    region = text[create_start:create_end]
    region = replace_once(
        region,
        "\t{\n\tCResolver* resolver = NULL;",
        "\t{\n\tconst TBool htcleoTrace = (aResolverUid == KRomOnlyResolverUid);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F391u, KErrNone,\n"
        "\t\t\t(TUint32)aResolverUid.iUid);\n"
        "\tCResolver* resolver = NULL;",
        "CreateResolver entry",
    )
    region = replace_once(
        region,
        "\t\tresolver = static_cast<CResolver*>(CRomOnlyResolver::NewL(*aRegistryResolveTransaction));\n"
        "\t\tCleanupStack::PushL(resolver);",
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F392u, KErrNone, 0u);\n"
        "\t\tresolver = static_cast<CResolver*>(CRomOnlyResolver::NewL(*aRegistryResolveTransaction));\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F393u, KErrNone, (TUint32)resolver);\n"
        "\t\tCleanupStack::PushL(resolver);\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F394u, KErrNone, 0u);",
        "CreateResolver ROM-only",
    )
    region = replace_once(
        region,
        "\treturn resolver;\n\t}",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F395u, KErrNone, (TUint32)resolver);\n"
        "\treturn resolver;\n\t}",
        "CreateResolver return",
    )
    text = text[:create_start] + region + text[create_end:]

    helper_comment = text.index("// The private helper")
    helper_start = text.index(
        "RImplInfoArray* CEComServer::ListImplementationsL", helper_comment
    )
    helper_end = text.index(
        "RImplInfoArray* CEComServer::ListImplementationsL", helper_start + 1
    )
    region = text[helper_start:helper_end]
    region = replace_once(
        region,
        "\t{\n\tif(!aResolver)",
        "\t{\n\tconst TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F396u, KErrNone, (TUint32)aResolver);\n"
        "\tif(!aResolver)",
        "private list helper entry",
    )
    region = replace_once(
        region,
        "\t// Use the client provided resolver to build up the list.\n"
        "\tRImplInfoArray* infoArray = aResolver->ListAllL(aInterfaceUid, aAdditionalParameters);\n"
        "\treturn infoArray;",
        "\t// Use the client provided resolver to build up the list.\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F397u, KErrNone, 0u);\n"
        "\tRImplInfoArray* infoArray = aResolver->ListAllL(aInterfaceUid, aAdditionalParameters);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F398u, KErrNone, (TUint32)infoArray);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F399u, KErrNone,\n"
        "\t\t\t(TUint32)(infoArray ? infoArray->Count() : 0));\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F39Au, KErrNone, 0u);\n"
        "\treturn infoArray;",
        "private list helper return",
    )
    text = text[:helper_start] + region + text[helper_end:]
    return text


def patch_rom_only(text: str) -> str:
    text = add_after(
        text,
        '#include "RomOnlyResolver.h"\n',
        '#include "HtcleoEcomServerLog.h"\n',
        "rom-only include",
    )
    text = replace_once(
        text,
        "\t{\n\treturn new(ELeave) CRomOnlyResolver(aRegistry);\n\t}",
        "\t{\n\tHtcleoEcomServerLog(0x0000F3A0u, KErrNone, 0u);\n"
        "\tCRomOnlyResolver* resolver = new(ELeave) CRomOnlyResolver(aRegistry);\n"
        "\tHtcleoEcomServerLog(0x0000F3A1u, KErrNone, (TUint32)resolver);\n"
        "\treturn resolver;\n\t}",
        "rom-only NewL",
    )
    text = replace_once(
        text,
        "\t{\n\t// Use the base class version to get the list of matches\n"
        "\tRImplInfoArray* retList = CDefaultResolver::ListAllL(aInterfaceUid, aAdditionalParameters);",
        "\t{\n\tconst TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3A2u, KErrNone,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t// Use the base class version to get the list of matches\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F3A3u, KErrNone, 0u);\n"
        "\tRImplInfoArray* retList = CDefaultResolver::ListAllL(aInterfaceUid, aAdditionalParameters);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3A4u, KErrNone, (TUint32)retList);",
        "rom-only list entry",
    )
    text = add_after(
        text,
        "\tconst TInt count = retList->Count();\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3A5u, KErrNone, (TUint32)count);\n",
        "rom-only list count",
    )
    text = replace_once(
        text,
        "\tfor(TInt index = count-1; index >=0; --index)\n"
        "\t\tif(!(*retList)[index]->RomBased())\n\t\t\tretList->Remove(index);",
        "\tfor(TInt index = count-1; index >=0; --index)\n"
        "\t\t{\n\t\tconst TBool romBased = (*retList)[index]->RomBased();\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3A6u, index,\n"
        "\t\t\t\t(TUint32)romBased);\n"
        "\t\tif(!romBased)\n\t\t\t{\n\t\t\tretList->Remove(index);\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F3A7u, index, 0u);\n"
        "\t\t\t}\n\t\t}",
        "rom-only filter loop",
    )
    text = replace_once(
        text,
        "\treturn retList;\n\t}",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3A8u, KErrNone,\n"
        "\t\t\t(TUint32)retList->Count());\n"
        "\treturn retList;\n\t}",
        "rom-only list return",
    )
    return text


def patch_default(text: str) -> str:
    text = add_after(
        text,
        '#include "DefaultResolver.h"\n',
        '#include "HtcleoEcomServerLog.h"\n',
        "default-resolver include",
    )
    text = replace_once(
        text,
        "\t{\n\t// Use the member var to create the array so that we get proper cleanup behaviour\n"
        "\tRImplInfoArray* retList = new (ELeave) RImplInfoArray;",
        "\t{\n\tconst TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3B0u, KErrNone,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t// Use the member var to create the array so that we get proper cleanup behaviour\n"
        "\tRImplInfoArray* retList = new (ELeave) RImplInfoArray;\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3B1u, KErrNone, (TUint32)retList);",
        "default list entry",
    )
    text = add_after(
        text,
        "\tCleanupStack::PushL(TCleanupItem(CloseAndDeleteRArray,retList));\n",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F3B2u, KErrNone, 0u);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F3B3u, KErrNone, 0u);\n",
        "default list push",
    )
    text = add_after(
        text,
        "\tRImplInfoArray& fullList = iRegistry.ListImplementationsL(aInterfaceUid);\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3B4u, KErrNone, (TUint32)&fullList);\n",
        "default registry return",
    )
    text = add_after(
        text,
        "\tconst TInt numImps = fullList.Count();\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3B5u, KErrNone, (TUint32)numImps);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3B6u, (TInt)useWildcards,\n"
        "\t\t\t(TUint32)matchType.Length());\n",
        "default list metadata",
    )
    text = replace_once(
        text,
        "\tfor(TInt index = 0; index < numImps; ++index)\n\t\t{\t\n"
        "\t\tif(Match(fullList[index]->DataType(), matchType, useWildcards))\n"
        "\t\t\t{\n\t\t\tUser::LeaveIfError(retList->Append(fullList[index]));\n\t\t\t}",
        "\tfor(TInt index = 0; index < numImps; ++index)\n\t\t{\t\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3B7u, index,\n"
        "\t\t\t\t(TUint32)fullList[index]);\n"
        "\t\tconst TDesC8& htcleoDataType = fullList[index]->DataType();\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3B8u, index,\n"
        "\t\t\t\t(TUint32)htcleoDataType.Length());\n"
        "\t\tconst TBool htcleoMatch = Match(htcleoDataType, matchType, useWildcards);\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3B9u, index,\n"
        "\t\t\t\t(TUint32)htcleoMatch);\n"
        "\t\tif(htcleoMatch)\n"
        "\t\t\t{\n"
        "\t\t\tTInt htcleoAppendResult = retList->Append(fullList[index]);\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F3BAu, htcleoAppendResult,\n"
        "\t\t\t\t\t(TUint32)retList->Count());\n"
        "\t\t\tUser::LeaveIfError(htcleoAppendResult);\n\t\t\t}",
        "default list loop",
    )
    text = replace_once(
        text,
        "\tCleanupStack::Pop();\n\treturn retList;\n\t}\n\nTBool CDefaultResolver::Match",
        "\tCleanupStack::Pop();\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3BBu, KErrNone,\n"
        "\t\t\t(TUint32)retList->Count());\n"
        "\treturn retList;\n\t}\n\nTBool CDefaultResolver::Match",
        "default list return",
    )
    return text


def patch_transaction(text: str) -> str:
    text = add_after(
        text,
        '#include "EComMessageIds.h"\n',
        '#include "HtcleoEcomServerLog.h"\n',
        "transaction include",
    )
    text = replace_once(
        text,
        "\t{\n\tCRegistryResolveTransaction* self=new(ELeave) CRegistryResolveTransaction(aRegistryData,aExtendedInterfaces,aClientRequest,aCapability);\n"
        "\treturn self;",
        "\t{\n"
        "\tHtcleoEcomServerLog(0x0000F3C0u, (TInt)aCapability,\n"
        "\t\t(TUint32)aExtendedInterfaces.Count());\n"
        "\tCRegistryResolveTransaction* self=new(ELeave) CRegistryResolveTransaction(aRegistryData,aExtendedInterfaces,aClientRequest,aCapability);\n"
        "\tHtcleoEcomServerLog(0x0000F3C1u, KErrNone, (TUint32)self);\n"
        "\treturn self;",
        "transaction NewL",
    )
    text = replace_once(
        text,
        "\t{\n\t__ASSERT_DEBUG(iExtendedInterfaces!=NULL, User::Invariant());",
        "\t{\n\tconst TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3C2u, KErrNone,\n"
        "\t\t\t(TUint32)aInterfaceUid.iUid);\n"
        "\t__ASSERT_DEBUG(iExtendedInterfaces!=NULL, User::Invariant());",
        "transaction list entry",
    )
    text = add_after(
        text,
        "\tiImplementationInfo.Reset();\n",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F3C3u, KErrNone, 0u);\n",
        "transaction reset",
    )
    text = replace_once(
        text,
        "\tCleanupClosePushL(implDataList);\n\tiRegistryData.ListImplementationsL(aInterfaceUid,implDataList);",
        "\tCleanupClosePushL(implDataList);\n"
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F3C4u, KErrNone, 0u);\n"
        "\tiRegistryData.ListImplementationsL(aInterfaceUid,implDataList);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3C5u, KErrNone,\n"
        "\t\t\t(TUint32)implDataList.Count());",
        "transaction registry list",
    )
    text = add_after(
        text,
        "\t\tCRegistryData::CImplementationData *currentImplementation = implDataList[j];\n",
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3C6u, j,\n"
        "\t\t\t\t(TUint32)currentImplementation);\n",
        "transaction impl data",
    )
    text = add_after(
        text,
        "\t\tCImplementationInformation* implInfo = currentImplementation->iImplInfo;\n",
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3C7u, j, (TUint32)implInfo);\n",
        "transaction impl info",
    )
    text = add_after(
        text,
        "\t\tCRegistryData::CDllData *dll = currentImplementation->iParent->iParent;\n",
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3C8u, j, (TUint32)dll);\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3C9u, j, (TUint32)iCapability);\n",
        "transaction dll data",
    )
    text = replace_once(
        text,
        "\t\t\tif(iClientRequest->CheckCapability(dll->iCapSet,*(implInfo)))\n"
        "\t\t\t\t{\n\t\t\t\tListImplementationsL(implInfo,dll);\t\t\t\n\t\t\t\t}",
        "\t\t\tTBool htcleoCapability =\n"
        "\t\t\t\tiClientRequest->CheckCapability(dll->iCapSet,*(implInfo));\n"
        "\t\t\tif(htcleoTrace)\n"
        "\t\t\t\tHtcleoEcomServerLog(0x0000F3CAu, j,\n"
        "\t\t\t\t\t(TUint32)htcleoCapability);\n"
        "\t\t\tif(htcleoCapability)\n"
        "\t\t\t\t{\n\t\t\t\tListImplementationsL(implInfo,dll);\t\t\t\n"
        "\t\t\t\tif(htcleoTrace)\n"
        "\t\t\t\t\tHtcleoEcomServerLog(0x0000F3CBu, j,\n"
        "\t\t\t\t\t\t(TUint32)iImplementationInfo.Count());\n"
        "\t\t\t\t}",
        "transaction capability check",
    )
    text = replace_once(
        text,
        "\tCleanupStack::PopAndDestroy(&implDataList);\t\n\treturn iImplementationInfo;",
        "\tif(htcleoTrace)\n\t\tHtcleoEcomServerLog(0x0000F3CCu, KErrNone, 0u);\n"
        "\tCleanupStack::PopAndDestroy(&implDataList);\t\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3CDu, KErrNone,\n"
        "\t\t\t(TUint32)iImplementationInfo.Count());\n"
        "\treturn iImplementationInfo;",
        "transaction return",
    )
    text = replace_once(
        text,
        "\t{\n\tTBool passExtendedInterfaceCheck = ETrue;",
        "\t{\n\tconst TBool htcleoTrace = (iExtendedInterfaces != NULL);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3D0u, KErrNone, (TUint32)aImplInfo);\n"
        "\tTBool passExtendedInterfaceCheck = ETrue;",
        "transaction helper entry",
    )
    text = add_after(
        text,
        "\tRExtendedInterfacesArray* extendedInterfacesOfThisImp = aImplInfo->GetExtendedInterfaceList();\n",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3D1u, KErrNone,\n"
        "\t\t\t(TUint32)extendedInterfacesOfThisImp);\n"
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3D2u,\n"
        "\t\t\tiExtendedInterfaces->Count(),\n"
        "\t\t\t(TUint32)(extendedInterfacesOfThisImp ?\n"
        "\t\t\t\textendedInterfacesOfThisImp->Count() : 0));\n",
        "transaction helper interfaces",
    )
    text = replace_once(
        text,
        "\tif (passExtendedInterfaceCheck)\n\t\t{\n\t\taImplInfo->SetVendorId(aDll->iVid);\n"
        "\t\t// Append the capability check passed found implementation\n"
        "\t\tUser::LeaveIfError(iImplementationInfo.Append(aImplInfo));\t",
        "\tif(htcleoTrace)\n"
        "\t\tHtcleoEcomServerLog(0x0000F3D3u, KErrNone,\n"
        "\t\t\t(TUint32)passExtendedInterfaceCheck);\n"
        "\tif (passExtendedInterfaceCheck)\n\t\t{\n"
        "\t\tif(htcleoTrace)\n\t\t\tHtcleoEcomServerLog(0x0000F3D4u, KErrNone, 0u);\n"
        "\t\taImplInfo->SetVendorId(aDll->iVid);\n"
        "\t\t// Append the capability check passed found implementation\n"
        "\t\tTInt htcleoAppendResult = iImplementationInfo.Append(aImplInfo);\n"
        "\t\tif(htcleoTrace)\n"
        "\t\t\tHtcleoEcomServerLog(0x0000F3D5u, htcleoAppendResult,\n"
        "\t\t\t\t(TUint32)iImplementationInfo.Count());\n"
        "\t\tUser::LeaveIfError(htcleoAppendResult);\t",
        "transaction helper append",
    )
    return text


def patch_exact_request_arm_session(text: str) -> str:
    text = replace_once(
        text,
        "void CEComServerSession::ServiceL(const RMessage2& aMessage)\n"
        "{\n\tconst TBool htcleoTrace =\n",
        "void CEComServerSession::ServiceL(const RMessage2& aMessage)\n"
        "{\n\t// " + EXACT_ARM_MARKER + "\n"
        "\t// A previous leave must remain armed through CEComServer::RunError();\n"
        "\t// the next service request closes that scope before any new trace.\n"
        "\tHtcleoEcomServerDisarm();\n"
        "\tconst TBool htcleoTrace =\n",
        "service request disarm",
    )
    old = '''void CEComServerSession::DoListImplementationsL(const TClientRequest& aMessage)
	{
	const TBool htcleoTrace =
		(aMessage.Function() == EListCustomResolvedImplementations);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F340u, KErrNone,
			(TUint32)aMessage.Function());
	// Unpack the client supplied parameters
	// Firstly get the uids
	TUidType uids;
	TPckg<TUidType> uidsPkg(uids);	
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F341u, KErrNone, 0u);
	aMessage.ReadL(KIPCParameterUids, uidsPkg);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F342u, KErrNone,
			(TUint32)uids[KInterfaceUidIndex].iUid);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F343u, KErrNone,
			(TUint32)uids[KResolverUidIndex].iUid);
'''
    new = '''void CEComServerSession::DoListImplementationsL(const TClientRequest& aMessage)
	{
	// Unpack the client supplied parameters before arming the durable writer.
	// This prevents startup and unrelated custom-resolver traffic from consuming
	// the fixed record budget before the FeatMgr request arrives.
	TUidType uids;
	TPckg<TUidType> uidsPkg(uids);	
	aMessage.ReadL(KIPCParameterUids, uidsPkg);
	const TBool htcleoTrace =
		(aMessage.Function() == EListCustomResolvedImplementations &&
		 uids[KInterfaceUidIndex].iUid == 0x10205057u &&
		 uids[KResolverUidIndex].iUid == 0x10009D92u);
	if(htcleoTrace)
		{
		HtcleoEcomServerArm();
		HtcleoEcomServerLog(0x0000F340u, KErrNone,
			(TUint32)aMessage.Function());
		HtcleoEcomServerLog(0x0000F341u, KErrNone, 0u);
		HtcleoEcomServerLog(0x0000F342u, KErrNone,
			(TUint32)uids[KInterfaceUidIndex].iUid);
		HtcleoEcomServerLog(0x0000F343u, KErrNone,
			(TUint32)uids[KResolverUidIndex].iUid);
		}
'''
    return replace_once(text, old, new, "exact request arm")


def patch_exact_request_arm_server(text: str) -> str:
    old = '''	const TBool htcleoTrace = (aInterfaceUid.iUid == 0x10205057u);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F380u, KErrNone,'''
    new = '''	const TBool htcleoTrace =
		(aInterfaceUid.iUid == 0x10205057u &&
		 aResolverUid.iUid == 0x10009D92u);
	if(htcleoTrace)
		HtcleoEcomServerLog(0x0000F380u, KErrNone,'''
    return replace_once(text, old, new, "server exact interface and resolver gate")


def patch_registry_data(text: str) -> str:
    text = add_after(
        text,
        '#include "RegistryData.h"\n',
        '#include "HtcleoEcomServerLog.h"\n\n// ' + REGISTRY_LIST_MARKER + '\n',
        "registry data trace include",
    )
    start = text.index(
        "void CRegistryData::ListImplementationsL(TUid aInterfaceUid,\n"
        "\t\t\t\t\t\t\t\t\t\t RImplDataArray& aImplementationData) const\n"
    )
    end_anchor = (
        "\n\t}\n\n/**\n"
        "Enables or disables the specified interface implementation within the registry."
    )
    end = text.index(end_anchor, start) + len("\n\t}")
    original = text[start:end]
    required = (
        "if(iCurrentlyDiscovering)",
        "index = IndexedFind(aInterfaceUid);",
        "TImplContainerArray& implementationList = iInterfaceImplIndex[index].iImpData;",
        "securityPassed = dll->ProcessSecurityCheckL();",
        "User::LeaveIfError(aImplementationData.Append(currentImplementation));",
    )
    if not all(anchor in original for anchor in required):
        raise SystemExit("registry list trace: stock control-flow anchor mismatch")
    replacement = r'''void CRegistryData::ListImplementationsL(TUid aInterfaceUid,
										 RImplDataArray& aImplementationData) const
	{
	HtcleoEcomServerLog(0x0000F3E0u, KErrNone,
		(TUint32)aInterfaceUid.iUid);
	HtcleoEcomServerLog(0x0000F3E1u, KErrNone, (TUint32)this);
	// Read the discovery flag between two records so a bad registry object is
	// distinguishable from the normal unavailable-list leave.
	const TBool htcleoCurrentlyDiscovering = iCurrentlyDiscovering;
	HtcleoEcomServerLog(0x0000F3E2u, KErrNone,
		(TUint32)htcleoCurrentlyDiscovering);
	if(htcleoCurrentlyDiscovering)
		{
		HtcleoEcomServerLog(0x0000F3E3u,
			KEComErrListCurrentlyUnavailable, 0u);
		User::Leave(KEComErrListCurrentlyUnavailable);
		}
	HtcleoEcomServerLog(0x0000F3E4u, KErrNone, 0u);

	TBool securityPassed = EFalse;
	HtcleoEcomServerLog(0x0000F3E5u, KErrNone,
		(TUint32)securityPassed);
	TInt index = 0;
	HtcleoEcomServerLog(0x0000F3E6u, index, 0u);
	while (!securityPassed)
		{
		HtcleoEcomServerLog(0x0000F3E7u, (TInt)securityPassed,
			(TUint32)index);
		HtcleoEcomServerLog(0x0000F3E8u, KErrNone,
			(TUint32)aImplementationData.Count());
		aImplementationData.Reset();
		HtcleoEcomServerLog(0x0000F3E9u, KErrNone,
			(TUint32)aImplementationData.Count());
		HtcleoEcomServerLog(0x0000F3EAu, KErrNone,
			(TUint32)aInterfaceUid.iUid);
		index = IndexedFind(aInterfaceUid);
		HtcleoEcomServerLog(0x0000F3EBu, index, 0u);
		if(index == KErrNotFound)
			{
			HtcleoEcomServerLog(0x0000F3ECu,
				KEComErrNoInterfaceIdentified, 0u);
			User::Leave(KEComErrNoInterfaceIdentified);
			}
		HtcleoEcomServerLog(0x0000F3EDu, index, 0u);
		User::LeaveIfError(index);
		HtcleoEcomServerLog(0x0000F3EEu, index, 0u);

		HtcleoEcomServerLog(0x0000F3EFu, index, 0u);
		TImplContainerArray& implementationList = iInterfaceImplIndex[index].iImpData;
		HtcleoEcomServerLog(0x0000F3F0u, KErrNone,
			(TUint32)implementationList.Count());
		for (TInt j = 0; j < implementationList.Count(); j++)
			{
			HtcleoEcomServerLog(0x0000F3F1u, j,
				(TUint32)implementationList.Count());
			HtcleoEcomServerLog(0x0000F3F2u, j, 0u);
			CImplementationData* currentImplementation = implementationList[j].iCurrentImpl;
			HtcleoEcomServerLog(0x0000F3F3u, j,
				(TUint32)currentImplementation);
			HtcleoEcomServerLog(0x0000F3F4u, j,
				(TUint32)currentImplementation);
			CDllData* dll = currentImplementation->iParent->iParent;
			HtcleoEcomServerLog(0x0000F3F5u, j, (TUint32)dll);

			HtcleoEcomServerLog(0x0000F3F6u, j, (TUint32)dll);
			securityPassed = dll->ProcessSecurityCheckL();
			HtcleoEcomServerLog(0x0000F3F7u,
				(TInt)securityPassed, (TUint32)dll);
			if(!securityPassed)
				{
				HtcleoEcomServerLog(0x0000F3F8u, j, (TUint32)dll);
				DeleteDllL(dll);
				HtcleoEcomServerLog(0x0000F3F9u, j, (TUint32)dll);
				delete dll;
				dll = NULL;
				HtcleoEcomServerLog(0x0000F3FAu, j, 0u);
				break;
				}
			else
				{
				HtcleoEcomServerLog(0x0000F3FBu, j,
					(TUint32)currentImplementation);
				TInt htcleoAppendResult =
					aImplementationData.Append(currentImplementation);
				HtcleoEcomServerLog(0x0000F3FCu, htcleoAppendResult,
					(TUint32)aImplementationData.Count());
				User::LeaveIfError(htcleoAppendResult);
				HtcleoEcomServerLog(0x0000F3FDu, j,
					(TUint32)aImplementationData.Count());
				}
			HtcleoEcomServerLog(0x0000F3FEu,
				(TInt)securityPassed, (TUint32)aImplementationData.Count());
			}
		HtcleoEcomServerLog(0x0000F3FFu,
			(TInt)securityPassed, (TUint32)aImplementationData.Count());
		}
	HtcleoEcomServerLog(0x0000F400u,
		(TInt)securityPassed, (TUint32)aImplementationData.Count());
	}'''
    return text[:start] + replacement + text[end:]


def verify(root: Path) -> None:
    frame = root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    mmp = root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/MMPFiles/EComServer.mmp"
    paths = {
        "start": frame / "EComServerStart.cpp",
        "session": frame / "EComServerSession.cpp",
        "server": frame / "EComServer.cpp",
        "rom": frame / "RomOnlyResolver.cpp",
        "default": frame / "DefaultResolver.cpp",
        "transaction": frame / "RegistryResolveTransaction.cpp",
        "registry": frame / "RegistryData.cpp",
        "logger": frame / "HtcleoEcomServerLog.cpp",
        "header": frame / "HtcleoEcomServerLog.h",
        "mmp": mmp,
    }
    texts = {name: path.read_text(encoding="latin-1") for name, path in paths.items()}
    source_text = "".join(
        texts[name] for name in (
            "start", "session", "server", "rom", "default", "transaction", "registry"
        )
    )
    stages = [
        *range(0xF300, 0xF312), *range(0xF320, 0xF32C),
        *range(0xF340, 0xF365), *range(0xF370, 0xF37B),
        *range(0xF380, 0xF39B), *range(0xF3A0, 0xF3A9),
        *range(0xF3B0, 0xF3BC), *range(0xF3C0, 0xF3CE),
        *range(0xF3D0, 0xF3D6), *range(0xF3E0, 0xF400), 0xF400,
    ]
    checks = {
        "marker": source_text.count(MARKER) == 1,
        "logger marker": texts["logger"].count(LOGGER_MARKER) == 1,
        "path": texts["logger"].count("C:\\\\Symbian3\\\\ECOMSRV.TXT") == 2,
        "macro": texts["mmp"].count(f"MACRO {MACRO}") == 1,
        "logger source": texts["mmp"].count("SOURCE\t\tHtcleoEcomServerLog.cpp") == 1,
        "all stages": all(source_text.count(f"0x0000{stage:04X}u") >= 1 for stage in stages),
        "interface gates": source_text.count(INTERFACE_UID) >= 4,
        "no delay": "User::After" not in texts["logger"],
        "no display": "HalFunction" not in source_text + texts["logger"],
        "large capacity marker": texts["logger"].count(CAPACITY_MARKER) == 1,
        "fixed capacity": "position < (16384 * 45)" in texts["logger"]
        and "position < (256 * 43)" not in texts["logger"],
        "four-digit sequence": texts["logger"].count(
            "position / 45), EHex, 4"
        ) == 1,
        "exact arm marker": texts["session"].count(EXACT_ARM_MARKER) == 1,
        "logger arm marker": texts["logger"].count(EXACT_ARM_MARKER) == 1,
        "exact resolver": source_text.count(RESOLVER_UID) >= 2,
        "arm truncates": "HtcleoEcomServerArmPath" in texts["logger"]
        and "file.Replace" in texts["logger"],
        "unarmed suppressed": "if(!gHtcleoEcomServerArmed)" in texts["logger"],
        "writer flush": "file.Write(record)" in texts["logger"] and "file.Flush()" in texts["logger"],
        "registry marker": texts["registry"].count(REGISTRY_LIST_MARKER) == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("ECom server trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    frame = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame"
    mmp_path = args.root / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/MMPFiles/EComServer.mmp"
    files = {
        "start": frame / "EComServerStart.cpp",
        "session": frame / "EComServerSession.cpp",
        "server": frame / "EComServer.cpp",
        "rom": frame / "RomOnlyResolver.cpp",
        "default": frame / "DefaultResolver.cpp",
        "transaction": frame / "RegistryResolveTransaction.cpp",
        "registry": frame / "RegistryData.cpp",
    }
    for path in (*files.values(), mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing ECom server source: {path}")

    logger_path = frame / "HtcleoEcomServerLog.cpp"
    header_path = frame / "HtcleoEcomServerLog.h"
    if (not logger_path.is_file()
            or LOGGER_MARKER not in logger_path.read_text(encoding="latin-1")
            or EXACT_ARM_MARKER not in logger_path.read_text(encoding="latin-1")):
        header_path.write_text(HEADER, encoding="latin-1")
        logger_path.write_text(LOGGER, encoding="latin-1")
    logger_text = logger_path.read_text(encoding="latin-1")
    if CAPACITY_MARKER not in logger_text:
        logger_text = replace_once(
            logger_text,
            "\tif(r == KErrNone && position < (256 * 43))\n",
            f"\t// {CAPACITY_MARKER}\n"
            "\tif(r == KErrNone && position < (16384 * 45))\n",
            "installed server logger capacity upgrade",
        )
        logger_text = replace_once(
            logger_text,
            "position / 43), EHex, 2",
            "position / 45), EHex, 4",
            "installed server logger sequence width upgrade",
        )
        logger_text = replace_once(
            logger_text,
            "Each record is 43 bytes.",
            "Each record is 45 bytes.",
            "installed server logger record-size comment upgrade",
        )
        logger_path.write_text(logger_text, encoding="latin-1")

    mutations = {
        "start": (patch_start, "0x0000F300u"),
        "session": (patch_session, "0x0000F320u"),
        "server": (patch_server_v2, "0x0000F329u"),
        "rom": (patch_rom_only, "0x0000F3A0u"),
        "default": (patch_default, "0x0000F3B0u"),
        "transaction": (patch_transaction, "0x0000F3C0u"),
        "registry": (patch_registry_data, "0x0000F3E0u"),
    }
    for name, (mutate, installed_stage) in mutations.items():
        path = files[name]
        text = path.read_text(encoding="latin-1")
        if installed_stage not in text:
            path.write_text(mutate(text), encoding="latin-1")

    session_text = files["session"].read_text(encoding="latin-1")
    if EXACT_ARM_MARKER not in session_text:
        files["session"].write_text(
            patch_exact_request_arm_session(session_text), encoding="latin-1"
        )
    server_text = files["server"].read_text(encoding="latin-1")
    exact_server_gate = (
        "aInterfaceUid.iUid == 0x10205057u &&\n"
        "\t\t aResolverUid.iUid == 0x10009D92u"
    )
    if exact_server_gate not in server_text:
        files["server"].write_text(
            patch_exact_request_arm_server(server_text), encoding="latin-1"
        )

    mmp = mmp_path.read_text(encoding="latin-1")
    if f"MACRO {MACRO}" not in mmp:
        mmp = add_after(
            mmp,
            "CAPABILITY ProtServ\n",
            f"MACRO {MACRO}\n",
            "server MMP macro",
        )
        mmp = add_after(
            mmp,
            "SOURCE\t\tEComServerStart.cpp\n",
            "SOURCE\t\tHtcleoEcomServerLog.cpp\n",
            "server MMP logger source",
        )
        mmp_path.write_text(mmp, encoding="latin-1")

    verify(args.root)
    print(
        "HTCLEO_ECOM_SERVER_FEATMGR_LIST_TRACE=installed "
        "path=C:\\Symbian3\\ECOMSRV.TXT stages=F300-F400 "
        "exact_request_arm=1 interface=10205057 resolver=10009D92"
    )


if __name__ == "__main__":
    main()
