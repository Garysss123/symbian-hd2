#!/usr/bin/env python3
"""Trace the FeatMgr-specific ECom list request without changing policy."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_FEATMGR_LIST_TRACE_V1"
FEATMGR_SID = "0x10205054u"
FEATMGR_INTERFACE = "0x10205057u"
STAGES = (
    *range(0xF200, 0xF208),
    *range(0xF210, 0xF219),
    *range(0xF220, 0xF226),
    *range(0xF230, 0xF238),
    *range(0xF240, 0xF24E),
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def mutate_region(
    text: str, start_marker: str, end_marker: str, mutate, label: str
) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    region = text[start:end]
    changed = mutate(region)
    if changed == region:
        raise SystemExit(f"{label}: region did not change")
    return text[:start] + changed + text[end:]


START_SERVER = r'''static TInt StartServer()
	{
	const TBool htcleoFeatMgrTrace =
		(RProcess().SecureId().iId == 0x10205054u);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F200u, KErrNone, 0u);
	const TUidType serverUid(KNullUid,KNullUid,KEComServerUid3);

	// EPOC is easy, we just create a new server process. Simultaneous launching
	// of two such processes should be detected when the second one attempts to
	// create the server object, failing with KErrAlreadyExists.
	RProcess server;
	TInt error = server.Create(KEComServerImg,KNullDesC,serverUid);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F201u, error, (TUint32)server.Handle());
	if (error != KErrNone)
		{
		if(htcleoFeatMgrTrace)
			HtcleoEcomLog(0x0000F202u, error, 0u);
		return error;
		}

	TRequestStatus stat;
	server.Rendezvous(stat);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F203u, stat.Int(), 0u);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F204u, KErrNone,
			(TUint32)(stat != KRequestPending));
	if (stat!=KRequestPending)
		server.Kill(0);		// abort startup
	else
		server.Resume();	// logon OK - start the server
	User::WaitForRequest(stat);		// wait for start or death
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F205u, stat.Int(), 0u);
	// we can't use the 'exit reason' if the server panicked as this
	// is the panic 'reason' and may be '0' which cannot be distinguished
	// from KErrNone
	const TExitType exitType = server.ExitType();
	const TInt exitReason = server.ExitReason();
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F206u, exitReason, (TUint32)exitType);
	error=(exitType==EExitPanic) ? KErrGeneral : stat.Int();
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F207u, error, 0u);
	server.Close();
	return error;
	}'''


OPEN_L = r'''EXPORT_C REComSession& REComSession::OpenL()
	{
	const TBool htcleoFeatMgrTrace =
		(RProcess().SecureId().iId == 0x10205054u);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F220u, KErrNone, 0u);
	//CGlobalData::NewL() will create just one CGlobalData instance.
	//Every next CGlobalData::NewL() call will return a pointer to the already created
	//CGlobalData instance.
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F221u, KErrNone, 0u);
	CGlobalData* globalData = CGlobalData::NewL();
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F222u, KErrNone, (TUint32)globalData);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F223u, KErrNone, 0u);
	globalData->IncRefCnt();
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F224u, KErrNone, 0u);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F225u, KErrNone, (TUint32)globalData);
	return globalData->EComSession();
	}'''


CONSTRUCT_L = r'''void REComSession::ConstructL()
	{
	const TBool htcleoFeatMgrTrace =
		(RProcess().SecureId().iId == 0x10205054u);
	if(htcleoFeatMgrTrace)
		HtcleoEcomLog(0x0000F210u, KErrNone, 0u);
	// Now connect to the ECom server
	TInt retry=KMaxStartAttempts;
	for (;;)
		{
		if(htcleoFeatMgrTrace)
			HtcleoEcomLog(0x0000F211u, KErrNone, (TUint32)retry);
		// create session with unlimited message slots due to notification API being asynchronous
		TInt error = CreateSession(KEComServerName,TVersion(KEComServerMajorVN,KEComServerMinorVN,KEComServerBuildVN),-1);
		if(htcleoFeatMgrTrace)
			HtcleoEcomLog(0x0000F212u, error, (TUint32)retry);
		if(error == KErrNone)
			{
			if(htcleoFeatMgrTrace)
				HtcleoEcomLog(0x0000F213u, KErrNone, (TUint32)retry);
			return;	// Success
			}
		else if (error != KErrNotFound && error != KErrServerTerminated)
			{
			if(htcleoFeatMgrTrace)
				HtcleoEcomLog(0x0000F214u, error, (TUint32)retry);
			User::Leave(error);
			}
		if (--retry==0)
			{
			if(htcleoFeatMgrTrace)
				HtcleoEcomLog(0x0000F215u, error, 0u);
			User::Leave(error);
			}
		if(htcleoFeatMgrTrace)
			HtcleoEcomLog(0x0000F216u, KErrNone, (TUint32)retry);
		error = StartServer();
		if(htcleoFeatMgrTrace)
			HtcleoEcomLog(0x0000F217u, error, (TUint32)retry);
		if (error != KErrNone && error != KErrAlreadyExists)
			{
			if(htcleoFeatMgrTrace)
				HtcleoEcomLog(0x0000F218u, error, (TUint32)retry);
			User::Leave(error);
			}
		}
	}'''


def mutate_outer(region: str) -> str:
    region = replace_once(
        region,
        "\t{\n\tif( aInterfaceUid.iUid == 0 ||\n",
        "\t{\n\tconst TBool htcleoFeatMgrTrace =\n"
        "\t\t(aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F230u, KErrNone, "
        "(TUint32)aResolverUid.iUid);\n"
        "\tif( aInterfaceUid.iUid == 0 ||\n",
        "LI6 entry",
    )
    region = replace_once(
        region,
        "\t\tUser::Leave(KErrArgument);\n\n\t// call FinalClose()",
        "\t\tUser::Leave(KErrArgument);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F231u, KErrNone, 0u);\n\n"
        "\t// call FinalClose()",
        "LI6 validation",
    )
    region = replace_once(
        region,
        "\tCleanupStack::PushL(TCleanupItem(CleanupFinalClose, NULL));\n\n"
        "\t// Open a local instance",
        "\tCleanupStack::PushL(TCleanupItem(CleanupFinalClose, NULL));\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F232u, KErrNone, 0u);\n\n"
        "\t// Open a local instance",
        "LI6 cleanup push",
    )
    region = replace_once(
        region,
        "\tREComSession& ecomSession = REComSession::OpenLC();",
        "\tREComSession& ecomSession = REComSession::OpenLC();\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F233u, KErrNone, 0u);",
        "LI6 OpenLC",
    )
    region = replace_once(
        region,
        "\tecomSession.ListImplementationsL(EListCustomResolvedImplementations,",
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F234u, KErrNone, "
        "(TUint32)EListCustomResolvedImplementations);\n"
        "\tecomSession.ListImplementationsL(EListCustomResolvedImplementations,",
        "LI6 inner call entry",
    )
    region = replace_once(
        region,
        "\t\t\t\t\t\t aImplInfoArray);\n\n"
        "\tCleanupStack::PopAndDestroy(&ecomSession);",
        "\t\t\t\t\t\t aImplInfoArray);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F235u, KErrNone, "
        "(TUint32)aImplInfoArray.Count());\n\n"
        "\tCleanupStack::PopAndDestroy(&ecomSession);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F236u, KErrNone, 0u);",
        "LI6 inner return",
    )
    region = replace_once(
        region,
        "\tCleanupStack::Pop(); // CleanupFinalClose\n\t}\n",
        "\tCleanupStack::Pop(); // CleanupFinalClose\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F237u, KErrNone, "
        "(TUint32)aImplInfoArray.Count());\n"
        "\t}\n",
        "LI6 return",
    )
    return region


def mutate_internal(region: str) -> str:
    region = replace_once(
        region,
        "\t{\n\t// Ensure the array we have been given is empty",
        "\t{\n\tconst TBool htcleoFeatMgrTrace =\n"
        "\t\t(aInterfaceUid.iUid == 0x10205057u);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F240u, KErrNone, "
        "(TUint32)aServiceId);\n"
        "\t// Ensure the array we have been given is empty",
        "internal entry",
    )
    region = replace_once(
        region,
        "\taImplInfoArray.ResetAndDestroy();\n\n",
        "\taImplInfoArray.ResetAndDestroy();\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F241u, KErrNone, 0u);\n\n",
        "internal reset",
    )
    region = replace_once(
        region,
        "\tTPckg<TUidType> uids(uidtype);\n",
        "\tTPckg<TUidType> uids(uidtype);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F242u, KErrNone, "
        "(TUint32)aResolverUid.iUid);\n",
        "internal UID package",
    )
    region = replace_once(
        region,
        "\tPackMatchStrAndExtendedInterfacesL(aResolutionParameters,aExtendedInterfaces,matchStrExtInfBuf);\n"
        "\tmatchStrExtInfBuf.CleanupClosePushL();",
        "\tPackMatchStrAndExtendedInterfacesL(aResolutionParameters,aExtendedInterfaces,matchStrExtInfBuf);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F243u, KErrNone, "
        "(TUint32)matchStrExtInfBuf.Length());\n"
        "\tmatchStrExtInfBuf.CleanupClosePushL();",
        "internal match pack",
    )
    region = replace_once(
        region,
        "\tbuf.CreateMaxL(bufferSize);\t\n\tbuf.CleanupClosePushL();",
        "\tbuf.CreateMaxL(bufferSize);\t\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F244u, KErrNone, "
        "(TUint32)bufferSize);\n"
        "\tbuf.CleanupClosePushL();",
        "internal output buffer",
    )
    region = replace_once(
        region,
        "\tTInt error= SendReceive(aServiceId,aArgs);",
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F245u, KErrNone, "
        "(TUint32)aServiceId);\n"
        "\tTInt error= SendReceive(aServiceId,aArgs);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F246u, error, "
        "(TUint32)listParam.iBufferSize);",
        "internal SendReceive",
    )
    region = replace_once(
        region,
        "\tif (error == KErrOverflow)\n\t\t{",
        "\tif (error == KErrOverflow)\n"
        "\t\t{\n"
        "\t\tif(htcleoFeatMgrTrace)\n"
        "\t\t\tHtcleoEcomLog(0x0000F247u, error, "
        "(TUint32)listParam.iBufferSize);",
        "internal overflow",
    )
    region = replace_once(
        region,
        "\t\t\tUser::LeaveIfError(SendReceive(ECollectImplementationsList,args));\n"
        "\t\t\terror=KErrNone;",
        "\t\t\tTInt collectError = SendReceive(ECollectImplementationsList,args);\n"
        "\t\t\tif(htcleoFeatMgrTrace)\n"
        "\t\t\t\tHtcleoEcomLog(0x0000F248u, collectError, "
        "(TUint32)listParam.iBufferSize);\n"
        "\t\t\tUser::LeaveIfError(collectError);\n"
        "\t\t\terror=KErrNone;",
        "internal collect",
    )
    region = replace_once(
        region,
        "\tif (error==KErrNone)\n\t\t{\t",
        "\tif (error==KErrNone)\n"
        "\t\t{\t\n"
        "\t\tif(htcleoFeatMgrTrace)\n"
        "\t\t\tHtcleoEcomLog(0x0000F249u, KErrNone, "
        "(TUint32)listParam.iBufferSize);",
        "internal success",
    )
    region = replace_once(
        region,
        "\t\t\tTInt entryCount = readStream.ReadInt32L();",
        "\t\t\tTInt entryCount = readStream.ReadInt32L();\n"
        "\t\t\tif(htcleoFeatMgrTrace)\n"
        "\t\t\t\tHtcleoEcomLog(0x0000F24Au, KErrNone, "
        "(TUint32)entryCount);",
        "internal entry count",
    )
    region = replace_once(
        region,
        "\t\t\tCleanupStack::PopAndDestroy(&readStream);\n"
        "\t\t\t__ECOM_TRACE1",
        "\t\t\tCleanupStack::PopAndDestroy(&readStream);\n"
        "\t\t\tif(htcleoFeatMgrTrace)\n"
        "\t\t\t\tHtcleoEcomLog(0x0000F24Bu, KErrNone, "
        "(TUint32)aImplInfoArray.Count());\n"
        "\t\t\t__ECOM_TRACE1",
        "internal decode complete",
    )
    region = replace_once(
        region,
        "\t\t__ECOM_TRACE1(\"ECOM: Request error %d\", error);\n"
        "\t\tUser::Leave(error);",
        "\t\t__ECOM_TRACE1(\"ECOM: Request error %d\", error);\n"
        "\t\tif(htcleoFeatMgrTrace)\n"
        "\t\t\tHtcleoEcomLog(0x0000F24Cu, error, "
        "(TUint32)listParam.iBufferSize);\n"
        "\t\tUser::Leave(error);",
        "internal error",
    )
    region = replace_once(
        region,
        "\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);\n\t}",
        "\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);\n"
        "\tif(htcleoFeatMgrTrace)\n"
        "\t\tHtcleoEcomLog(0x0000F24Du, KErrNone, "
        "(TUint32)aImplInfoArray.Count());\n"
        "\t}",
        "internal return",
    )
    return region


def verify(path: Path) -> None:
    text = path.read_text(encoding="latin-1")
    checks = {
        "marker": text.count(MARKER) == 1,
        "all stages": all(
            text.count(f"HtcleoEcomLog(0x0000{stage:04X}u") == 1
            for stage in STAGES
        ),
        "FeatMgr SID filters": text.count(FEATMGR_SID) == 3,
        "FeatMgr interface filters": text.count(FEATMGR_INTERFACE) == 2,
        "single stock wait": text.count("User::WaitForRequest(stat);") == 1,
        "single collect request": text.count(
            "SendReceive(ECollectImplementationsList,args)"
        ) == 1,
        "no delay": "User::After" not in text,
        "no display": "HalFunction" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("FeatMgr ECom trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        text = replace_once(
            text,
            '#include "HtcleoEcomLog.h"\n',
            '#include "HtcleoEcomLog.h"\n\n// ' + MARKER + "\n",
            "marker include",
        )
        text = mutate_region(
            text,
            "static TInt StartServer()\n",
            "EXPORT_C REComSession::REComSession()",
            lambda _region: START_SERVER + "\n\n",
            "StartServer",
        )
        text = mutate_region(
            text,
            "EXPORT_C REComSession& REComSession::OpenL()\n",
            "/**\nThis method returns a reference to the singleton client/server session object",
            lambda _region: OPEN_L + "\n\n",
            "OpenL",
        )
        text = mutate_region(
            text,
            "void REComSession::ConstructL()\n",
            "/**\nCloses the open handle on the ECOM framework.",
            lambda _region: CONSTRUCT_L + "\n\n",
            "ConstructL",
        )
        text = mutate_region(
            text,
            "//ListImplementationsL - LI6",
            "//ListImplementationsL - LI7",
            mutate_outer,
            "FeatMgr public list overload",
        )
        text = mutate_region(
            text,
            "void REComSession::ListImplementationsL(\n            TInt aServiceId,",
            "/**\nProvides the instantiation method",
            mutate_internal,
            "internal list IPC",
        )
        path.write_text(text, encoding="latin-1")
    verify(path)
    print(
        "HTCLEO_ECOM_FEATMGR_LIST_TRACE=installed "
        "sid=10205054 interface=10205057 stages=F200-F24D"
    )


if __name__ == "__main__":
    main()
