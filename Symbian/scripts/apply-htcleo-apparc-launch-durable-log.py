#!/usr/bin/env python3
"""Install a fail-open caller-side AppArc/AknCapServer launch trace.

Iteration 431 proves the Gate-11 display stack is intact but produces no
APALOG.TXT.  The UI command list later receives KErrServerTerminated while
WaitForApparcInit is pending.  This transform records the existing synchronous
APSEXE Create/Rendezvous and AknCapServer StartApp path without changing any
return value, wait, retry, or error policy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_APPARC_LAUNCH_DURABLE_LOG_V1"
EXIT_MARKER = "HTCLEO_APPARC_LAUNCH_EXIT_CATEGORY_LOG_V2"
TARGET_EXIT_MARKER = "HTCLEO_AKNCAP_THREAD_EXIT_CATEGORY_LOG_V3"
MACRO = "__HTCLEO_APPARC_LAUNCH_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_APPARC_LAUNCH_DURABLE_LOG__
#include <f32file.h>

// HTCLEO_APPARC_LAUNCH_DURABLE_LOG_V1
static void HtcleoApaLaunchLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoApaStartLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoApaStartLogPath, "C:\\Symbian3\\APASTART.TXT");
	r = fs.MkDirAll(KHtcleoApaStartLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoApaStartLogPath, EFileWrite | EFileShareAny);
	if(r == KErrNotFound || r == KErrPathNotFound)
		{
		r = file.Replace(fs, KHtcleoApaStartLogPath,
			EFileWrite | EFileShareAny);
		}
	else if(r == KErrNone)
		{
		r = file.Seek(ESeekEnd, position);
		}
	if(r == KErrNone && position >= (256 * 67))
		{
		file.Close();
		fs.Close();
		return;
		}

	if(r == KErrNone)
		{
		_LIT8(KHtcleoApaStartPrefix, "HTCLEO_APASTART ");
		TBuf8<96> record;
		record.Append(KHtcleoApaStartPrefix);
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
		if(r == KErrNone)
			{
			r = file.Flush();
			}
		file.Close();
		}

	fs.Close();
	}
#else
inline void HtcleoApaLaunchLog(TUint32, TInt, TUint32) {}
#endif

'''


def verify(source: str, mmp: str) -> None:
    property_ready = (
        "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1" in source
    )
    property_poll = "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2" in source
    property_fire = "HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3" in source
    expected_log_helpers = (
        2
        if "HTCLEO_AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG_V1" in source
        else 1
    )
    stages = (
        tuple(range(0xA000, 0xA007))
        + tuple(range(0xB000, 0xB006))
        + tuple(range(0xA200, 0xA206))
    )
    checks = {
        "single marker": source.count(MARKER) == 1,
        "single exit-category marker": source.count(EXIT_MARKER) == 1,
        "single target-exit marker": source.count(TARGET_EXIT_MARKER) == 1,
        "single log path": source.count("C:\\\\Symbian3\\\\APASTART.TXT") == 1,
        "all checkpoints": all(f"0x{stage:08X}u" in source for stage in stages),
        "one write per durable helper": (
            source.count("file.Write(record)") == expected_log_helpers
        ),
        "one flush per durable helper": (
            source.count("file.Flush()") == expected_log_helpers
        ),
        "bounded log": source.count("position >= (256 * 67)") == 1,
        "exact target thread captured across readiness wait": (
            (
                source.count("htcleoAknThread.Open(dummy)") == 1
                or (
                    property_ready
                    and source.count(
                        "htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread)"
                    ) == 1
                )
            )
            and source.count("htcleoAknThread.ExitCategory()") == 1
            and source.count("HtcleoPackApaExitCategory") == 5
            and source.count("server.ExitCategory()") == 0
            and (
                (
                    not property_ready
                    and source.index("htcleoAknThread.Open(dummy)")
                    < source.index(
                        "User::WaitForRequest(requestStatusForRendezvous)"
                    )
                )
                or (
                    property_ready and not property_poll
                    and source.index(
                        "htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread)"
                    )
                    < source.index(
                        "User::WaitForRequest(htcleoAknReadyStatus, "
                        "htcleoAknDeathStatus)"
                    )
                )
                or (
                    property_fire
                    and source.index(
                        "htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread)"
                    )
                    < source.index("htcleoAknProcess.Resume();")
                )
                or (
                    property_poll
                    and not property_fire
                    and source.index(
                        "htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread)"
                    )
                    < source.index("for(; htcleoAknPollCount")
                )
            )
            and source.index("htcleoAknThread.ExitCategory()")
            < source.rindex("htcleoAknThread.Close()")
        ),
        "raw APSEXE result retained": source.count(
            "const TInt htcleoApaStartResult = AknStartupApaServerProcess();"
        ) == 1,
        "APSEXE result still ignored": source.count(
            "HtcleoApaLaunchLog(0x0000A001u, htcleoApaStartResult, 0u);"
        ) == 1 and "LeaveIfError(htcleoApaStartResult)" not in source,
        "readiness successor owns all added waits": (
            source.count("User::WaitForRequest(") == 2
            if not property_ready
            else (
                (
                    "WaitForRequest(htcleoAknReadyStatus" not in source
                    and source.count(
                        "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
                    ) == 2
                    and (
                        "User::After(10000)" not in source
                        if property_fire
                        else "User::After(10000)" in source
                    )
                )
                if property_poll
                else (
                    source.count(
                        "User::WaitForRequest(htcleoAknReadyStatus, "
                        "htcleoAknDeathStatus)"
                    ) == 1
                    and "requestStatusForRendezvous" not in source
                )
            )
        ),
        "original retry delay unchanged": source.count("User::After(500000)") == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "efsrv": mmp.count("LIBRARY         efsrv.lib") == 1,
        "case-correct AknNotify import": mmp.count(
            "LIBRARY         AknNotify.lib"
        ) == 1 and "LIBRARY         aknnotify.lib" not in mmp,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AppArc launch durable log verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    component = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer"
    )
    source_path = component / "clientsrc/AknCapServerClient.cpp"
    mmp_path = component / "group/AknCapServerClient.mmp"
    if not source_path.is_file() or not mmp_path.is_file():
        raise SystemExit("missing AknCapServerClient source/MMP")

    source = source_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")

    if MARKER not in source:
        source = replace_once(
            source,
            '#include "akndiscreetpopupdata.h"\n',
            '#include "akndiscreetpopupdata.h"\n' + LOGGER,
            "logger insertion",
        )
        source = replace_once(
            source,
            "EXPORT_C void RAknUiServer::StartAknCapserverL()\n"
            "    {\n"
            "    AknStartupApaServerProcess();\n"
            "    \n"
            "    RApaLsSession apa;\n"
            "    User::LeaveIfError(apa.Connect());\n",
            "EXPORT_C void RAknUiServer::StartAknCapserverL()\n"
            "    {\n"
            "    HtcleoApaLaunchLog(0x0000A000u, KErrNone, 0u);\n"
            "    const TInt htcleoApaStartResult = AknStartupApaServerProcess();\n"
            "    HtcleoApaLaunchLog(0x0000A001u, htcleoApaStartResult, 0u);\n"
            "    \n"
            "    RApaLsSession apa;\n"
            "    const TInt htcleoApaConnectResult = apa.Connect();\n"
            "    HtcleoApaLaunchLog(0x0000A002u, htcleoApaConnectResult, 0u);\n"
            "    User::LeaveIfError(htcleoApaConnectResult);\n",
            "StartAknCapserver entry and AppArc result",
        )
        source = replace_once(
            source,
            "    cmdLine->SetCommandL(EApaCommandBackground);\n"
            "    TThreadId dummy;\n",
            "    cmdLine->SetCommandL(EApaCommandBackground);\n"
            "    HtcleoApaLaunchLog(0x0000A003u, KErrNone, "
            "(TUint32)KUikonUidPluginInterfaceNotifiers);\n"
            "    TThreadId dummy;\n",
            "AknCap command line complete",
        )
        source = replace_once(
            source,
            "    User::LeaveIfError(apa.StartApp(*cmdLine, dummy, "
            "&requestStatusForRendezvous));\n"
            "    User::WaitForRequest(requestStatusForRendezvous);\n"
            "    User::LeaveIfError(requestStatusForRendezvous.Int());\n"
            "    CleanupStack::PopAndDestroy(2, &apa);   // cmdLine and apa    \n",
            "    const TInt htcleoStartAppResult = apa.StartApp(*cmdLine, dummy, "
            "&requestStatusForRendezvous);\n"
            "    HtcleoApaLaunchLog(0x0000A004u, htcleoStartAppResult, 0u);\n"
            "    User::LeaveIfError(htcleoStartAppResult);\n"
            "    User::WaitForRequest(requestStatusForRendezvous);\n"
            "    const TInt htcleoAknRendezvousResult = "
            "requestStatusForRendezvous.Int();\n"
            "    HtcleoApaLaunchLog(0x0000A005u, "
            "htcleoAknRendezvousResult, (TUint32)dummy.Id());\n"
            "    User::LeaveIfError(htcleoAknRendezvousResult);\n"
            "    HtcleoApaLaunchLog(0x0000A006u, KErrNone, 0u);\n"
            "    CleanupStack::PopAndDestroy(2, &apa);   // cmdLine and apa    \n",
            "AknCap StartApp and rendezvous",
        )
        source = replace_once(
            source,
            "EXPORT_C TInt AknStartupApaServerProcess()\n"
            "    {\n"
            "    _LIT(KNameApaImage,\"APSEXE\");\n",
            "EXPORT_C TInt AknStartupApaServerProcess()\n"
            "    {\n"
            "    HtcleoApaLaunchLog(0x0000B000u, KErrNone, 0u);\n"
            "    _LIT(KNameApaImage,\"APSEXE\");\n",
            "APSEXE launch entry",
        )
        source = replace_once(
            source,
            "    TInt r = server.Create(KNameApaImage, KApaCommandLine, uidType);\n"
            "    \n"
            "    if (r != KErrNone)\n",
            "    TInt r = server.Create(KNameApaImage, KApaCommandLine, uidType);\n"
            "    HtcleoApaLaunchLog(0x0000B001u, r, 0u);\n"
            "    \n"
            "    if (r != KErrNone)\n",
            "APSEXE Create result",
        )
        source = replace_once(
            source,
            "    TRequestStatus stat;\n"
            "    server.Rendezvous(stat);\n"
            "    if (stat != KRequestPending)\n",
            "    TRequestStatus stat;\n"
            "    server.Rendezvous(stat);\n"
            "    HtcleoApaLaunchLog(0x0000B002u, stat.Int(), 0u);\n"
            "    if (stat != KRequestPending)\n",
            "APSEXE Rendezvous registration",
        )
        source = replace_once(
            source,
            "        {\n"
            "        server.Kill(0);     // abort startup\n"
            "        }\n"
            "    else\n"
            "        {\n"
            "        server.Resume();    // logon OK - start the server\n"
            "        }\n"
            "    User::WaitForRequest(stat); // wait for start or death\n"
            "    server.Close();\n"
            "    return stat.Int();\n",
            "        {\n"
            "        HtcleoApaLaunchLog(0x0000B003u, stat.Int(), 0u);\n"
            "        server.Kill(0);     // abort startup\n"
            "        }\n"
            "    else\n"
            "        {\n"
            "        HtcleoApaLaunchLog(0x0000B003u, stat.Int(), 1u);\n"
            "        server.Resume();    // logon OK - start the server\n"
            "        }\n"
            "    User::WaitForRequest(stat); // wait for start or death\n"
            "    const TInt htcleoApaRendezvousResult = stat.Int();\n"
            "    const TUint32 htcleoApaExitDetail = "
            "((TUint32)server.ExitType() << 16) | "
            "((TUint32)server.ExitReason() & 0x0000FFFFu);\n"
            "    HtcleoApaLaunchLog(0x0000B004u, "
            "htcleoApaRendezvousResult, htcleoApaExitDetail);\n"
            "    server.Close();\n"
            "    HtcleoApaLaunchLog(0x0000B005u, "
            "htcleoApaRendezvousResult, 0u);\n"
            "    return htcleoApaRendezvousResult;\n",
            "APSEXE rendezvous completion",
        )

    if EXIT_MARKER not in source:
        source = replace_once(
            source,
            '''\tfs.Close();
\t}
#else
inline void HtcleoApaLaunchLog(TUint32, TInt, TUint32) {}
#endif
''',
            '''\tfs.Close();
\t}

// HTCLEO_APPARC_LAUNCH_EXIT_CATEGORY_LOG_V2
static TUint32 HtcleoPackApaExitCategory(
    const TDesC& aCategory, TInt aOffset)
\t{
\tTUint32 packed = 0;
\tfor(TInt i = 0; i < 4; ++i)
\t\t{
\t\tconst TInt index = aOffset + i;
\t\tif(index >= aCategory.Length())
\t\t\t{
\t\t\tbreak;
\t\t\t}
\t\tpacked |= ((TUint32)aCategory[index] & 0x000000FFu) << (i * 8);
\t\t}
\treturn packed;
\t}
#else
inline void HtcleoApaLaunchLog(TUint32, TInt, TUint32) {}
#endif
''',
            "exit category packer",
        )

        source = replace_once(
            source,
            '''    const TUint32 htcleoApaExitDetail = ((TUint32)server.ExitType() << 16) | ((TUint32)server.ExitReason() & 0x0000FFFFu);
    HtcleoApaLaunchLog(0x0000B004u, htcleoApaRendezvousResult, htcleoApaExitDetail);
    server.Close();
''',
            '''    const TUint32 htcleoApaExitDetail = ((TUint32)server.ExitType() << 16) | ((TUint32)server.ExitReason() & 0x0000FFFFu);
    HtcleoApaLaunchLog(0x0000B004u, htcleoApaRendezvousResult, htcleoApaExitDetail);
    const TExitCategoryName htcleoApaExitCategory = server.ExitCategory();
    HtcleoApaLaunchLog(0x0000B100u, server.ExitReason(),
        (TUint32)htcleoApaExitCategory.Length());
    HtcleoApaLaunchLog(0x0000B101u, (TInt)server.ExitType(),
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 0));
    HtcleoApaLaunchLog(0x0000B102u, KErrNone,
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 4));
    HtcleoApaLaunchLog(0x0000B103u, KErrNone,
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 8));
    HtcleoApaLaunchLog(0x0000B104u, KErrNone,
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 12));
    server.Close();
''',
            "APSEXE panic category before process close",
        )

    if TARGET_EXIT_MARKER not in source:
        source = replace_once(
            source,
            '''    const TInt htcleoStartAppResult = apa.StartApp(*cmdLine, dummy, &requestStatusForRendezvous);
    HtcleoApaLaunchLog(0x0000A004u, htcleoStartAppResult, 0u);
    User::LeaveIfError(htcleoStartAppResult);
    User::WaitForRequest(requestStatusForRendezvous);
    const TInt htcleoAknRendezvousResult = requestStatusForRendezvous.Int();
    HtcleoApaLaunchLog(0x0000A005u, htcleoAknRendezvousResult, (TUint32)dummy.Id());
    User::LeaveIfError(htcleoAknRendezvousResult);
''',
            '''    const TInt htcleoStartAppResult = apa.StartApp(*cmdLine, dummy, &requestStatusForRendezvous);
    HtcleoApaLaunchLog(0x0000A004u, htcleoStartAppResult, 0u);
    User::LeaveIfError(htcleoStartAppResult);

    // HTCLEO_AKNCAP_THREAD_EXIT_CATEGORY_LOG_V3
    RThread htcleoAknThread;
    const TInt htcleoAknThreadOpenResult = htcleoAknThread.Open(dummy);
    HtcleoApaLaunchLog(0x0000A200u, htcleoAknThreadOpenResult,
        (TUint32)dummy.Id());
    User::WaitForRequest(requestStatusForRendezvous);
    const TInt htcleoAknRendezvousResult = requestStatusForRendezvous.Int();
    HtcleoApaLaunchLog(0x0000A005u, htcleoAknRendezvousResult, (TUint32)dummy.Id());
    if(htcleoAknThreadOpenResult == KErrNone)
        {
        const TExitCategoryName htcleoAknExitCategory =
            htcleoAknThread.ExitCategory();
        HtcleoApaLaunchLog(0x0000A201u, htcleoAknThread.ExitReason(),
            (TUint32)htcleoAknExitCategory.Length());
        HtcleoApaLaunchLog(0x0000A202u, (TInt)htcleoAknThread.ExitType(),
            HtcleoPackApaExitCategory(htcleoAknExitCategory, 0));
        HtcleoApaLaunchLog(0x0000A203u, KErrNone,
            HtcleoPackApaExitCategory(htcleoAknExitCategory, 4));
        HtcleoApaLaunchLog(0x0000A204u, KErrNone,
            HtcleoPackApaExitCategory(htcleoAknExitCategory, 8));
        HtcleoApaLaunchLog(0x0000A205u, KErrNone,
            HtcleoPackApaExitCategory(htcleoAknExitCategory, 12));
        }
    htcleoAknThread.Close();
    User::LeaveIfError(htcleoAknRendezvousResult);
''',
            "AknCap target thread exit category",
        )

        # V2 queried APSEXE immediately after its successful rendezvous, where
        # ExitType is necessarily EExitPending.  Remove those non-frontier
        # records while retaining the shared descriptor packer for the exact
        # AknCap main-thread handle captured above.
        source = replace_once(
            source,
            '''    const TExitCategoryName htcleoApaExitCategory = server.ExitCategory();
    HtcleoApaLaunchLog(0x0000B100u, server.ExitReason(),
        (TUint32)htcleoApaExitCategory.Length());
    HtcleoApaLaunchLog(0x0000B101u, (TInt)server.ExitType(),
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 0));
    HtcleoApaLaunchLog(0x0000B102u, KErrNone,
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 4));
    HtcleoApaLaunchLog(0x0000B103u, KErrNone,
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 8));
    HtcleoApaLaunchLog(0x0000B104u, KErrNone,
        HtcleoPackApaExitCategory(htcleoApaExitCategory, 12));
''',
            '',
            "retire APSEXE-pending category records",
        )

    # V1 was first drafted with KUikonUidPluginInterfaceNotifiers treated as a
    # TUid, while this S60 header exposes it as an integer constant.  Keep the
    # transform idempotent across an already-installed draft source tree.
    source = source.replace(
        "(TUint32)KUikonUidPluginInterfaceNotifiers.iUid",
        "(TUint32)KUikonUidPluginInterfaceNotifiers",
    )

    if f"MACRO          {MACRO}" not in mmp:
        mmp = replace_once(
            mmp,
            "LIBRARY         ws32.lib\n",
            "LIBRARY         ws32.lib\n"
            "LIBRARY         efsrv.lib\n"
            f"MACRO          {MACRO}\n",
            "MMP logger dependencies",
        )

    # The PDK ships AknNotify.dso with mixed case while the stock MMP names
    # aknnotify.lib.  Linux SBS is case-sensitive, so retain the required
    # import with the on-disk spelling.
    mmp = mmp.replace(
        "LIBRARY         aknnotify.lib\n",
        "LIBRARY         AknNotify.lib\n",
    )
    mmp = mmp.replace(
        "// HTCLEO: unused AknNotify import removed for case-sensitive GCCE build\n",
        "LIBRARY         AknNotify.lib\n",
    )

    verify(source, mmp)
    source_path.write_text(source, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print(
        "HTCLEO_APPARC_LAUNCH_LOG=installed "
        "stages=A000-A006+A200-A205+B000-B005"
    )


if __name__ == "__main__":
    main()
