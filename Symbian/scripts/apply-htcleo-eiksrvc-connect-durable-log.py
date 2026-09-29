#!/usr/bin/env python3
"""Install an AknCap-gated durable trace in REikAppUiSession::Connect.

Iteration 462 proves eiksrvs.exe completes process rendezvous and reaches its
active-scheduler boundary while AknCapServer remains inside
REikAppUiSession::Connect().  This trace separates Close, CreateSession,
StartServerL/rendezvous, retry, and session-data construction without changing
their retry, wait, leave, panic, or scheduling semantics.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1"
MACRO = "__HTCLEO_EIKSRVC_CONNECT_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_EIKSRVC_CONNECT_LOG__
#include <f32file.h>

// HTCLEO_EIKSRVC_CONNECT_DURABLE_LOG_V1
static void HtcleoEikConnLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // This DLL is shared by many UI clients.  Keep the trace exact to the
    // AknCapServer process whose outer E108/E109 bracket owns this frontier.
    if (RProcess().SecureId().iId != 0x10207218u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikConnLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikConnLogPath, "C:\\Symbian3\\EIKCONN.TXT");
    r = fs.MkDirAll(KHtcleoEikConnLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoEikConnLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoEikConnLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position < (512 * 64))
        {
        _LIT8(KHtcleoEikConnPrefix, "HTCLEO_EIKCONN ");
        TBuf8<96> record;
        record.Append(KHtcleoEikConnPrefix);
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
#else
inline void HtcleoEikConnLog(TUint32, TInt, TUint32) {}
#endif

'''


CONNECT_OLD = r'''EXPORT_C TInt REikAppUiSession::Connect()
	{
	Close();
	TInt err=KErrNone;
	TInt retry=KNumConnectRetries;
	FOREVER
		{
		err=CreateSession(EIKAPPUI_SERVER_NAME,Version());
		if ((--retry>0) && ((err==KErrNotFound) || (err==KErrServerTerminated)))
			{
			TRAP(err,StartServerL());
			if ((err!=KErrNone) && (err!=KErrAlreadyExists))
				{
				break;
				}
			}
		else
			{
			break;
			}
		}
	if (err==KErrNone)
		{
		
		TRAP(err,
				iExtension=new(ELeave) CExtension;
				iExtension->iDataStorage=CCoeDataStorage::NewL());
		}
	if (err!=KErrNone)
		{
		Close();
		}
	return err;
	}
'''


CONNECT_NEW = r'''EXPORT_C TInt REikAppUiSession::Connect()
	{
	HtcleoEikConnLog(0x0000E900u, KErrNone, (TUint32)KNumConnectRetries);
	Close();
	HtcleoEikConnLog(0x0000E901u, KErrNone, 0u);
	TInt err=KErrNone;
	TInt retry=KNumConnectRetries;
	FOREVER
		{
		HtcleoEikConnLog(0x0000E902u, KErrNone, (TUint32)retry);
		err=CreateSession(EIKAPPUI_SERVER_NAME,Version());
		HtcleoEikConnLog(0x0000E903u, err, (TUint32)retry);
		if ((--retry>0) && ((err==KErrNotFound) || (err==KErrServerTerminated)))
			{
			HtcleoEikConnLog(0x0000E904u, err, (TUint32)retry);
			HtcleoEikConnLog(0x0000E905u, KErrNone, (TUint32)retry);
			TRAP(err,StartServerL());
			HtcleoEikConnLog(0x0000E906u, err, (TUint32)retry);
			if ((err!=KErrNone) && (err!=KErrAlreadyExists))
				{
				HtcleoEikConnLog(0x0000E907u, err, (TUint32)retry);
				break;
				}
			HtcleoEikConnLog(0x0000E908u, err, (TUint32)retry);
			}
		else
			{
			HtcleoEikConnLog(0x0000E909u, err, (TUint32)retry);
			break;
			}
		}
	if (err==KErrNone)
		{
		HtcleoEikConnLog(0x0000E90Au, KErrNone, 0u);
		TRAP(err,
				iExtension=new(ELeave) CExtension;
				iExtension->iDataStorage=CCoeDataStorage::NewL());
		HtcleoEikConnLog(0x0000E90Bu, err,
			(iExtension ? 1u : 0u));
		}
	if (err!=KErrNone)
		{
		HtcleoEikConnLog(0x0000E90Cu, err, 0u);
		Close();
		HtcleoEikConnLog(0x0000E90Du, err, 0u);
		}
	HtcleoEikConnLog(0x0000E90Eu, err, 0u);
	return err;
	}
'''


START_OLD = r'''void REikAppUiSession::StartServerL()
	{
	const TUidType serverUid(KNullUid,KNullUid,KServerUid3);

	RProcess server;
	User::LeaveIfError(server.Create(KEikSrvName,KNullDesC,serverUid));
	TRequestStatus stat;
	server.Rendezvous(stat);
	if (stat!=KRequestPending)
		server.Kill(0);         // abort startup
	else
		server.Resume();        // logon OK - start the server
	User::WaitForRequest(stat);             // wait for start or death
	// we can't use the 'exit reason' if the server panicked as this
	// is the panic 'reason' and may be '0' which cannot be distinguished
	// from KErrNone
	TInt r=(server.ExitType()==EExitPanic) ? KErrGeneral : stat.Int();
	server.Close();
	User::LeaveIfError(r);
	}
'''


START_NEW = r'''void REikAppUiSession::StartServerL()
	{
	HtcleoEikConnLog(0x0000E910u, KErrNone, 0u);
	const TUidType serverUid(KNullUid,KNullUid,KServerUid3);

	RProcess server;
	HtcleoEikConnLog(0x0000E911u, KErrNone, 0u);
	const TInt htcleoCreateResult =
		server.Create(KEikSrvName,KNullDesC,serverUid);
	HtcleoEikConnLog(0x0000E912u, htcleoCreateResult, 0u);
	User::LeaveIfError(htcleoCreateResult);
	TRequestStatus stat;
	HtcleoEikConnLog(0x0000E913u, KErrNone, 0u);
	server.Rendezvous(stat);
	HtcleoEikConnLog(0x0000E914u, stat.Int(), 0u);
	if (stat!=KRequestPending)
		{
		HtcleoEikConnLog(0x0000E915u, stat.Int(), 0u);
		server.Kill(0);         // abort startup
		}
	else
		{
		HtcleoEikConnLog(0x0000E916u, stat.Int(), 0u);
		server.Resume();        // logon OK - start the server
		}
	HtcleoEikConnLog(0x0000E917u, KErrNone, 0u);
	User::WaitForRequest(stat);             // wait for start or death
	HtcleoEikConnLog(0x0000E918u, stat.Int(), 0u);
	// we can't use the 'exit reason' if the server panicked as this
	// is the panic 'reason' and may be '0' which cannot be distinguished
	// from KErrNone
	const TExitType htcleoExitType = server.ExitType();
	TInt r=(htcleoExitType==EExitPanic) ? KErrGeneral : stat.Int();
	HtcleoEikConnLog(0x0000E919u, r, (TUint32)htcleoExitType);
	HtcleoEikConnLog(0x0000E91Au, KErrNone, 0u);
	server.Close();
	HtcleoEikConnLog(0x0000E91Bu, r, 0u);
	User::LeaveIfError(r);
	HtcleoEikConnLog(0x0000E91Cu, KErrNone, 0u);
	}
'''


def verify(source: str, mmp: str) -> None:
    stages = [*(range(0xE900, 0xE90F)), *(range(0xE910, 0xE91D))]
    rendezvous_compat = "HTCLEO_EIKSRVC_RENDEZVOUS_TIMEOUT_COMPAT_V1" in source
    checks = {
        "marker": source.count(MARKER) == 1,
        "log path": source.count("C:\\\\Symbian3\\\\EIKCONN.TXT") == 1,
        "AknCap SID gate": source.count("0x10207218u") == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "efsrv": mmp.lower().count("library  efsrv.lib") == 1,
        "CreateSession preserved": source.count(
            "CreateSession(EIKAPPUI_SERVER_NAME,Version())"
        ) == 1,
        # The downstream QSD8250 compatibility transform has two guarded
        # direct-wait fallbacks.  Before that transform, the stock single wait
        # must remain exact.
        "wait preserved": source.count("User::WaitForRequest(stat)")
        == (2 if rendezvous_compat else 1),
        "retry preserved": source.count("TInt retry=KNumConnectRetries") == 1,
        "no delay": "User::After" not in source[source.index(MARKER) :],
    }
    for stage in stages:
        checks[f"stage {stage:04X}"] = (
            source.count(f"HtcleoEikConnLog(0x0000{stage:04X}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()

    component = args.epocroot / "sf/mw/classicui/commonuisupport/uikon"
    source_path = component / "srvsrc/EIKSRVC.CPP"
    mmp_path = component / "group/EIKSRVC.MMP"
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = replace_once(
            source,
            '#include "eiksrvsconsts.h"\n',
            '#include "eiksrvsconsts.h"\n' + LOGGER,
            "logger insertion",
        )
        source = replace_once(source, CONNECT_OLD, CONNECT_NEW, "Connect")
        source = replace_once(source, START_OLD, START_NEW, "StartServerL")

    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(source, mmp)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    print("HTCLEO_EIKSRVC_CONNECT_LOG=installed stages=E900-E90E,E910-E91C")


if __name__ == "__main__":
    main()
