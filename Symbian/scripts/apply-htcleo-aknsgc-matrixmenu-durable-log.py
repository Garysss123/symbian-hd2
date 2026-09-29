#!/usr/bin/env python3
"""Add MatrixMenu-only durable tracing to CAknSgcClient construction.

Iteration 496 reaches CAknSgcClient::CreateL but does not return.  This trace
brackets CreateL, BaseConstructL and ConstructL, retaining every stock call,
leave and branch.  Only MatrixMenu SID 0x101f4cd2 writes MENULOG.TXT.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNSGC_MATRIXMENU_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
// HTCLEO_AKNSGC_MATRIXMENU_DURABLE_LOG_V1
static void HtcleoAknSgcMenuLog(
    TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101f4cd2u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }
    _LIT(KHtcleoAknSgcMenuDir, "C:\\Symbian3\\");
    _LIT(KHtcleoAknSgcMenuPath, "C:\\Symbian3\\MENULOG.TXT");
    r = fs.MkDirAll(KHtcleoAknSgcMenuDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoAknSgcMenuPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoAknSgcMenuPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoAknSgcMenuPrefix, "HTCLEO_MENU ");
        TBuf8<96> record;
        record.Append(KHtcleoAknSgcMenuPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            }
        }
    file.Close();
    fs.Close();
    }

'''


CREATE_STOCK = r'''EXPORT_C void CAknSgcClient::CreateL()
	{
	CAknSgcClient* self=CAknSgcClient::Static();
	if (!self)
		{
		RThread thread;
		if (thread.Name() == _L("akncapserver"))
			self = new(ELeave) CAknSgcClientServerInst();  // CCoeEnv takes ownership immediately
		else
			self = new(ELeave) CAknSgcClient(); // CCoeEnv takes ownership immediately
		self->ConstructL();
		}
	}
'''


CREATE_TRACED = r'''EXPORT_C void CAknSgcClient::CreateL()
	{
	HtcleoAknSgcMenuLog(0x4D4DA100u, KErrNone, 0u);
	CAknSgcClient* self=CAknSgcClient::Static();
	HtcleoAknSgcMenuLog(0x4D4DA101u, KErrNone, self ? 1u : 0u);
	if (!self)
		{
		RThread thread;
		const TBool serverInstance =
			thread.Name() == _L("akncapserver");
		HtcleoAknSgcMenuLog(0x4D4DA102u, KErrNone,
			serverInstance ? 1u : 0u);
		HtcleoAknSgcMenuLog(0x4D4DA103u, KErrNone, 0u);
		if (serverInstance)
			self = new(ELeave) CAknSgcClientServerInst();  // CCoeEnv takes ownership immediately
		else
			self = new(ELeave) CAknSgcClient(); // CCoeEnv takes ownership immediately
		HtcleoAknSgcMenuLog(0x4D4DA104u, KErrNone, self ? 1u : 0u);
		HtcleoAknSgcMenuLog(0x4D4DA105u, KErrNone, 0u);
		self->ConstructL();
		HtcleoAknSgcMenuLog(0x4D4DA106u, KErrNone, 0u);
		}
	HtcleoAknSgcMenuLog(0x4D4DA107u, KErrNone, self ? 1u : 0u);
	}
'''


BASE_STOCK = r'''void CAknSgcClient::BaseConstructL()
	{
	RProcess process;
	if( process.SecureId() == KPeninputServerUid )
	    {
	    iFlags.Set(ENeverRelinquish);
	    }
	
	iDrawSync = CAknDrawSynchronizer::NewL();
	iLayoutConfig = new(ELeave) CAknLayoutConfig;
	}
'''


BASE_TRACED = r'''void CAknSgcClient::BaseConstructL()
	{
	HtcleoAknSgcMenuLog(0x4D4DA110u, KErrNone, 0u);
	RProcess process;
	const TBool penInputServer = process.SecureId() == KPeninputServerUid;
	HtcleoAknSgcMenuLog(0x4D4DA111u, KErrNone,
		penInputServer ? 1u : 0u);
	if (penInputServer)
	    {
	    iFlags.Set(ENeverRelinquish);
	    }
	
	HtcleoAknSgcMenuLog(0x4D4DA112u, KErrNone, 0u);
	iDrawSync = CAknDrawSynchronizer::NewL();
	HtcleoAknSgcMenuLog(0x4D4DA113u, KErrNone,
		iDrawSync ? 1u : 0u);
	HtcleoAknSgcMenuLog(0x4D4DA114u, KErrNone, 0u);
	iLayoutConfig = new(ELeave) CAknLayoutConfig;
	HtcleoAknSgcMenuLog(0x4D4DA115u, KErrNone,
		iLayoutConfig ? 1u : 0u);
	}
'''


CONSTRUCT_STOCK = r'''void CAknSgcClient::ConstructL()
	{
	BaseConstructL();
	
	User::LeaveIfError(iAknSrv.Connect());
	iSpRedrawCoord = new(ELeave) TSgcClientStatusPaneRedrawCoordinator(iAknSrv);
	SetImpl(new(ELeave) CAknSgcClientImpl(iAknSrv));

    if(iAvkonEnv->HasBlank())
        StartupBlankL();

	HBufC8* packedBuf;
	if (iAknSrv.Handle())
		{
		packedBuf = iAknSrv.GetPackedConfigL();
		}
	else
		{	// eiksrv will end up here
		packedBuf = iLayoutConfig->CreatePackedBufL();
		}
	iLayoutConfig->ConstructL(packedBuf);
	}
'''


CONSTRUCT_TRACED = r'''void CAknSgcClient::ConstructL()
	{
	HtcleoAknSgcMenuLog(0x4D4DA120u, KErrNone, 0u);
	HtcleoAknSgcMenuLog(0x4D4DA121u, KErrNone, 0u);
	BaseConstructL();
	HtcleoAknSgcMenuLog(0x4D4DA122u, KErrNone, 0u);
	
	HtcleoAknSgcMenuLog(0x4D4DA123u, KErrNone, 0u);
	const TInt aknServerError = iAknSrv.Connect();
	HtcleoAknSgcMenuLog(0x4D4DA124u, aknServerError, 0u);
	User::LeaveIfError(aknServerError);
	HtcleoAknSgcMenuLog(0x4D4DA125u, KErrNone, 0u);
	iSpRedrawCoord = new(ELeave) TSgcClientStatusPaneRedrawCoordinator(iAknSrv);
	HtcleoAknSgcMenuLog(0x4D4DA126u, KErrNone,
		iSpRedrawCoord ? 1u : 0u);
	HtcleoAknSgcMenuLog(0x4D4DA127u, KErrNone, 0u);
	SetImpl(new(ELeave) CAknSgcClientImpl(iAknSrv));
	HtcleoAknSgcMenuLog(0x4D4DA128u, KErrNone, 0u);

    const TBool hasBlank = iAvkonEnv->HasBlank();
	HtcleoAknSgcMenuLog(0x4D4DA129u, KErrNone, hasBlank ? 1u : 0u);
    if(hasBlank)
        {
		HtcleoAknSgcMenuLog(0x4D4DA12Au, KErrNone, 0u);
        StartupBlankL();
		HtcleoAknSgcMenuLog(0x4D4DA12Bu, KErrNone, 0u);
		}

	HBufC8* packedBuf;
	const TInt aknServerHandle = iAknSrv.Handle();
	HtcleoAknSgcMenuLog(0x4D4DA12Cu, KErrNone,
		(TUint32)aknServerHandle);
	if (aknServerHandle)
		{
		HtcleoAknSgcMenuLog(0x4D4DA12Du, KErrNone, 0u);
		packedBuf = iAknSrv.GetPackedConfigL();
		HtcleoAknSgcMenuLog(0x4D4DA12Eu, KErrNone,
			packedBuf ? 1u : 0u);
		}
	else
		{	// eiksrv will end up here
		HtcleoAknSgcMenuLog(0x4D4DA12Fu, KErrNone, 0u);
		packedBuf = iLayoutConfig->CreatePackedBufL();
		HtcleoAknSgcMenuLog(0x4D4DA130u, KErrNone,
			packedBuf ? 1u : 0u);
		}
	HtcleoAknSgcMenuLog(0x4D4DA131u, KErrNone, 0u);
	iLayoutConfig->ConstructL(packedBuf);
	HtcleoAknSgcMenuLog(0x4D4DA132u, KErrNone, 0u);
	}
'''


def install(source: str) -> str:
    source = replace_once(
        source,
        '#include "AknPanic.h"\n',
        '#include "AknPanic.h"\n#include <f32file.h>\n',
        "filesystem include",
    )
    source = replace_once(
        source,
        "#define KLegacyScreenSize",
        HELPER + "#define KLegacyScreenSize",
        "durable helper",
    )
    source = replace_once(source, CREATE_STOCK, CREATE_TRACED, "CreateL")
    source = replace_once(source, BASE_STOCK, BASE_TRACED, "BaseConstructL")
    return replace_once(
        source, CONSTRUCT_STOCK, CONSTRUCT_TRACED, "ConstructL"
    )


def verify(source: str) -> None:
    stages = (
        *range(0x4D4DA100, 0x4D4DA108),
        *range(0x4D4DA110, 0x4D4DA116),
        *range(0x4D4DA120, 0x4D4DA133),
    )
    checks = {
        "marker": source.count(MARKER) == 1,
        "exact SID gate": (
            source.count(
                "htcleoSid != 0x101f4cd2u && !htcleoHome"
            ) == 1
            if "HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN_V1"
            in source
            else source.count(
                "RProcess().SecureId().iId != 0x101f4cd2u"
            ) == 1
        ),
        "durable path": source.count(r"C:\\Symbian3\\MENULOG.TXT") == 1,
        "all stages": all(
            source.count(f"0x{stage:08X}u") == 1 for stage in stages
        ),
        "single write and flush": (
            source.count("file.Write(record)") == 1
            and source.count("file.Flush()") == 1
        ),
        "stock server connect semantics": (
            source.count("const TInt aknServerError = iAknSrv.Connect();") == 1
            and source.count("User::LeaveIfError(aknServerError);") == 1
        ),
        "stock construction calls": all(
            source.count(call) == 1
            for call in (
                "CAknDrawSynchronizer::NewL();",
                "SetImpl(new(ELeave) CAknSgcClientImpl(iAknSrv));",
                "StartupBlankL();",
                "iAknSrv.GetPackedConfigL();",
                "iLayoutConfig->ConstructL(packedBuf);",
            )
        ) and source.count("iLayoutConfig->CreatePackedBufL();") == 2,
        "no delay or display": (
            "User::After" not in HELPER and "HalFunction" not in HELPER
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("AknSgc trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNSGC_MATRIXMENU_DURABLE_LOG=installed "
        "stages=4D4DA100-A107,A110-A115,A120-A132"
    )


if __name__ == "__main__":
    main()
