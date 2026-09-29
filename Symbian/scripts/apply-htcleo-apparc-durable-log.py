#!/usr/bin/env python3
"""Install a fail-open AppArc startup and list-population trace.

Iteration 430 proves that the UI command list reaches WaitForApparcInit.  This
transform traces the already-running APSEXE process without framebuffer output,
waits, retries, or changed error handling.  APSERV and APLIST append fixed ASCII
records to C:\\Symbian3\\APALOG.TXT and flush every completed checkpoint.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_APPARC_DURABLE_LOG_V1"
MACRO = "__HTCLEO_APPARC_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_count(text: str, old: str, new: str, expected: int, label: str) -> str:
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} anchors, found {count}")
    return text.replace(old, new)


SERVER_HEADER = r'''#ifndef HTCLEO_APPARC_LOG_H
#define HTCLEO_APPARC_LOG_H

#include <e32std.h>

#ifdef __HTCLEO_APPARC_DURABLE_LOG__
void HtcleoApaServerLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
inline void HtcleoApaServerLog(TUint32, TInt, TUint32) {}
#endif

#endif
'''


LIST_HEADER = r'''#ifndef HTCLEO_APPLIST_LOG_H
#define HTCLEO_APPLIST_LOG_H

#include <e32std.h>

#ifdef __HTCLEO_APPARC_DURABLE_LOG__
void HtcleoApaListLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
inline void HtcleoApaListLog(TUint32, TInt, TUint32) {}
#endif

#endif
'''


def logger_cpp(header: str, function: str, source_tag: str, marker: str) -> str:
    return rf'''#include "{header}"

#ifdef __HTCLEO_APPARC_DURABLE_LOG__
#include <f32file.h>

// {MARKER} {marker}
void {function}(TUint32 aStage, TInt aResult, TUint32 aDetail)
                         __attribute__((noinline));

void {function}(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{{
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{{
		return;
		}}

	_LIT(KHtcleoApaLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoApaLogPath, "C:\\Symbian3\\APALOG.TXT");
	r = fs.MkDirAll(KHtcleoApaLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{{
		fs.Close();
		return;
		}}

	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoApaLogPath, EFileWrite | EFileShareAny);
	if(r == KErrNotFound || r == KErrPathNotFound)
		{{
		r = file.Replace(fs, KHtcleoApaLogPath, EFileWrite | EFileShareAny);
		}}
	else if(r == KErrNone)
		{{
		r = file.Seek(ESeekEnd, position);
		}}
	if(r == KErrNone && position >= 131072)
		{{
		file.Close();
		fs.Close();
		return;
		}}

	if(r == KErrNone)
		{{
		_LIT8(KHtcleoApaPrefix, "HTCLEO_APA {source_tag} ");
		TBuf8<96> record;
		record.Append(KHtcleoApaPrefix);
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
			{{
			r = file.Flush();
			}}
		file.Close();
		}}

	fs.Close();
	}}
#endif
'''


def verify(paths: dict[str, Path]) -> None:
    texts = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    checks = {
        "server logger marker": texts["server_logger"].count(MARKER) == 1,
        "list logger marker": texts["list_logger"].count(MARKER) == 1,
        "single path per logger": texts["server_logger"].count("C:\\\\Symbian3\\\\APALOG.TXT") == 1
        and texts["list_logger"].count("C:\\\\Symbian3\\\\APALOG.TXT") == 1,
        "write and flush": all(
            text.count("file.Write(record)") == 1 and text.count("file.Flush()") == 1
            for text in (texts["server_logger"], texts["list_logger"])
        ),
        "no waits": all(
            "User::After" not in text and "WaitForRequest" not in text
            for text in (texts["server_logger"], texts["list_logger"])
        ),
        "no writable logger globals": all(
            "gHtcleoApaLogSequence" not in text and
            "static TUint32" not in text
            for text in (texts["server_logger"], texts["list_logger"])
        ),
        "bounded by file length": all(
            "position >= 131072" in text
            for text in (texts["server_logger"], texts["list_logger"])
        ),
        "no writable scan global": "gHtcleoApaScanStep" not in texts["aplist"],
        "server macro": texts["apserv_mmp"].count(f"MACRO          {MACRO}") == 1,
        "list macro": texts["aplist_mmp"].count(f"MACRO          {MACRO}") == 1,
        "server source": texts["apserv_mmp"].count("source          htcleoapalog.cpp") == 1,
        "list source": texts["aplist_mmp"].count("source          htcleoapplistlog.cpp") == 1,
        "server includes": all(
            text.count('#include "htcleoapalog.h"') == 1
            for text in (texts["apsstart"], texts["apsserv"], texts["apsses"])
        ),
        "list include": texts["aplist"].count('#include "htcleoapplistlog.h"') == 1,
        "server checkpoints": all(
            f"0x{stage:08X}u" in texts[unit]
            for unit, stages in {
                "apsstart": (0x100, 0x101, 0x102, 0x103, 0x104, 0x105, 0x1E0),
                "apsserv": (0x200, 0x201, 0x202, 0x203, 0x204, 0x205,
                            0x206, 0x207, 0x208, 0x209, 0x20A, 0x400, 0x401),
                "apsses": (0x300, 0x301, 0x302, 0x410, 0x411),
            }.items()
            for stage in stages
        ),
        "list checkpoints": all(
            f"0x{stage:08X}u" in texts["aplist"]
            for stage in (0x1000, 0x1001, 0x1002, 0x1003, 0x1004,
                          0x1100, 0x1101, 0x1102, 0x1110, 0x1111, 0x1112,
                          0x1200, 0x1201, 0x1202, 0x1203, 0x1204, 0x1205,
                          0x1300, 0x1301, 0x1302, 0x1310, 0x1311)
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("AppArc durable log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    base = args.root / "sf/mw/appsupport/appfw/apparchitecture"
    paths = {
        "apsstart": base / "apserv/APSSTART.CPP",
        "apsserv": base / "apserv/APSSERV.CPP",
        "apsses": base / "apserv/APSSES.CPP",
        "aplist": base / "aplist/aplapplist.cpp",
        "apserv_mmp": base / "group/APSERV.MMP",
        "aplist_mmp": base / "group/APLIST.MMP",
        "server_header": base / "apserv/htcleoapalog.h",
        "server_logger": base / "apserv/htcleoapalog.cpp",
        "list_header": base / "aplist/htcleoapplistlog.h",
        "list_logger": base / "aplist/htcleoapplistlog.cpp",
    }
    for name in ("apsstart", "apsserv", "apsses", "aplist", "apserv_mmp", "aplist_mmp"):
        if not paths[name].is_file():
            raise SystemExit(f"missing AppArc source: {paths[name]}")

    paths["server_header"].write_text(SERVER_HEADER, encoding="utf-8")
    paths["server_logger"].write_text(
        logger_cpp("htcleoapalog.h", "HtcleoApaServerLog", "S", "APSERV"),
        encoding="utf-8",
    )
    paths["list_header"].write_text(LIST_HEADER, encoding="utf-8")
    paths["list_logger"].write_text(
        logger_cpp("htcleoapplistlog.h", "HtcleoApaListLog", "L", "APLIST"),
        encoding="utf-8",
    )

    apsstart = paths["apsstart"].read_text(encoding="utf-8")
    if MARKER not in apsstart:
        apsstart = replace_once(
            apsstart,
            '#include <eikdll.h>\n',
            '#include <eikdll.h>\n#include "htcleoapalog.h"\n\n'
            f'// {MARKER}\n',
            "APSSTART include",
        )
        apsstart = replace_once(
            apsstart,
            "static void RunServerL()\n//\n// Perform all server initialisation, in particular creation of the\n// scheduler and server and then run the scheduler\n//\n\t{\n",
            "static void RunServerL()\n//\n// Perform all server initialisation, in particular creation of the\n// scheduler and server and then run the scheduler\n//\n\t{\n"
            "\tHtcleoApaServerLog(0x00000100u, KErrNone, 0u);\n",
            "RunServerL entry",
        )
        apsstart = replace_once(
            apsstart,
            "\tCSvActiveScheduler::NewLC();\n",
            "\tCSvActiveScheduler::NewLC();\n"
            "\tHtcleoApaServerLog(0x00000101u, KErrNone, 0u);\n",
            "scheduler return",
        )
        apsstart = replace_once(
            apsstart,
            "\tUser::LeaveIfError(RFbsSession::Connect());\n",
            "\tconst TInt htcleoFbsResult = RFbsSession::Connect();\n"
            "\tHtcleoApaServerLog(0x00000102u, htcleoFbsResult, 0u);\n"
            "\tUser::LeaveIfError(htcleoFbsResult);\n",
            "FBS connect",
        )
        apsstart = replace_once(
            apsstart,
            "\tCApaAppArcServer* appArcServer = CApaAppArcServer::NewL();\n",
            "\tHtcleoApaServerLog(0x00000103u, KErrNone, 0u);\n"
            "\tCApaAppArcServer* appArcServer = CApaAppArcServer::NewL();\n"
            "\tHtcleoApaServerLog(0x00000104u, KErrNone, (TUint32)appArcServer);\n",
            "server factory",
        )
        apsstart = replace_once(
            apsstart,
            "\tRProcess::Rendezvous(KErrNone);\n",
            "\tRProcess::Rendezvous(KErrNone);\n"
            "\tHtcleoApaServerLog(0x00000105u, KErrNone, 0u);\n",
            "rendezvous return",
        )
        apsstart = replace_once(
            apsstart,
            "\t\t\tTRAP(r,RunServerL());\n",
            "\t\t\tTRAP(r,RunServerL());\n"
            "\t\t\tHtcleoApaServerLog(0x000001E0u, r, 0u);\n",
            "RunServer trap",
        )
        paths["apsstart"].write_text(apsstart, encoding="utf-8")

    apsserv = paths["apsserv"].read_text(encoding="utf-8")
    if MARKER not in apsserv:
        apsserv = replace_once(
            apsserv,
            '#include "apgnotif.h"\n',
            '#include "apgnotif.h"\n#include "htcleoapalog.h"\n\n'
            f'// {MARKER}\n',
            "APSSERV include",
        )
        apsserv = replace_once(
            apsserv,
            "void CApaAppArcServer::ConstructL()\n\t{\n\tStartL(KAppListServerName);\n\tUser::LeaveIfError(Dll::SetTls(this));\n\tUser::LeaveIfError(iFs.Connect());\n",
            "void CApaAppArcServer::ConstructL()\n\t{\n"
            "\tHtcleoApaServerLog(0x00000200u, KErrNone, 0u);\n"
            "\tStartL(KAppListServerName);\n"
            "\tHtcleoApaServerLog(0x00000201u, KErrNone, 0u);\n"
            "\tconst TInt htcleoTlsResult = Dll::SetTls(this);\n"
            "\tHtcleoApaServerLog(0x00000202u, htcleoTlsResult, 0u);\n"
            "\tUser::LeaveIfError(htcleoTlsResult);\n"
            "\tconst TInt htcleoFsResult = iFs.Connect();\n"
            "\tHtcleoApaServerLog(0x00000203u, htcleoFsResult, 0u);\n"
            "\tUser::LeaveIfError(htcleoFsResult);\n",
            "ConstructL entry",
        )
        apsserv = replace_once(
            apsserv,
            "\tconst TInt cmdLineLen = User::CommandLineLength();\n",
            "\tconst TInt cmdLineLen = User::CommandLineLength();\n"
            "\tHtcleoApaServerLog(0x00000204u, KErrNone, (TUint32)cmdLineLen);\n",
            "command line length",
        )
        apsserv = replace_count(
            apsserv,
            "\t\t\tUser::LeaveIfError(iWsSession.Connect());\n",
            "\t\t\tconst TInt htcleoWsResult = iWsSession.Connect();\n"
            "\t\t\tHtcleoApaServerLog(0x00000205u, htcleoWsResult, 0u);\n"
            "\t\t\tUser::LeaveIfError(htcleoWsResult);\n",
            1,
            "command-line WS connect",
        )
        apsserv = replace_count(
            apsserv,
            "\t\t\tiRuleBasedPlugIns = CApaScanningRuleBasedPlugIns::NewL();\n",
            "\t\t\tiRuleBasedPlugIns = CApaScanningRuleBasedPlugIns::NewL();\n"
            "\t\t\tHtcleoApaServerLog(0x00000206u, KErrNone, (TUint32)iRuleBasedPlugIns);\n",
            1,
            "command-line rule plugins",
        )
        apsserv = replace_once(
            apsserv,
            "\t\t// and rule based plugins are enabled\n"
            "\t\tUser::LeaveIfError(iWsSession.Connect());\n"
            "\t\tiRuleBasedPlugIns = CApaScanningRuleBasedPlugIns::NewL();\n",
            "\t\t// and rule based plugins are enabled\n"
            "\t\tconst TInt htcleoWsResult = iWsSession.Connect();\n"
            "\t\tHtcleoApaServerLog(0x00000205u, htcleoWsResult, 0u);\n"
            "\t\tUser::LeaveIfError(htcleoWsResult);\n"
            "\t\tiRuleBasedPlugIns = CApaScanningRuleBasedPlugIns::NewL();\n"
            "\t\tHtcleoApaServerLog(0x00000206u, KErrNone, (TUint32)iRuleBasedPlugIns);\n",
            "default WS/rule plugins",
        )
        apsserv = replace_once(
            apsserv,
            "\tiAppList=CApaAppList::NewL(iFs, iLoadMbmIconsOnDemand, idlePeriodicDelay); // takes ownership of scanner\n",
            "\tiAppList=CApaAppList::NewL(iFs, iLoadMbmIconsOnDemand, idlePeriodicDelay); // takes ownership of scanner\n"
            "\tHtcleoApaServerLog(0x00000207u, KErrNone, (TUint32)iAppList);\n",
            "app list factory",
        )
        apsserv = replace_once(
            apsserv,
            "\tTRAP_IGNORE(iAppList->InitListL(this));\n",
            "\tHtcleoApaServerLog(0x00000208u, KErrNone, 0u);\n"
            "\tTRAPD(htcleoInitListResult, iAppList->InitListL(this));\n"
            "\tHtcleoApaServerLog(0x00000209u, htcleoInitListResult, 0u);\n",
            "InitList trap",
        )
        apsserv = replace_once(
            apsserv,
            "\tiAppInstallationMonitor->Start();\n\t}\n",
            "\tiAppInstallationMonitor->Start();\n"
            "\tHtcleoApaServerLog(0x0000020Au, KErrNone, (TUint32)iAppList->Count());\n"
            "\t}\n",
            "ConstructL return",
        )
        apsserv = replace_once(
            apsserv,
            "void CApaAppArcServer::InitialListPopulationComplete()\n\t{\n",
            "void CApaAppArcServer::InitialListPopulationComplete()\n\t{\n"
            "\tHtcleoApaServerLog(0x00000400u, KErrNone, (TUint32)iAppList->Count());\n",
            "population complete entry",
        )
        apsserv = replace_once(
            apsserv,
            "\twhile (ses!=NULL)\n\t\t{\n\t\tses->NotifyClientForCompletionOfListPopulation();\t\n\t\tses=static_cast<CApaAppArcServSession*>(&(*iSessionIter++));\n\t\t}\n\t}\n",
            "\twhile (ses!=NULL)\n\t\t{\n\t\tses->NotifyClientForCompletionOfListPopulation();\t\n\t\tses=static_cast<CApaAppArcServSession*>(&(*iSessionIter++));\n\t\t}\n"
            "\tHtcleoApaServerLog(0x00000401u, KErrNone, (TUint32)iAppList->Count());\n"
            "\t}\n",
            "population complete notify",
        )
        paths["apsserv"].write_text(apsserv, encoding="utf-8")

    apsses = paths["apsses"].read_text(encoding="utf-8")
    if MARKER not in apsses:
        apsses = replace_once(
            apsses,
            '#include "apsecutils.h"\n',
            '#include "apsecutils.h"\n#include "htcleoapalog.h"\n\n'
            f'// {MARKER}\n',
            "APSSES include",
        )
        apsses = replace_once(
            apsses,
            "void CApaAppListServSession::RegisterListPopulationCompleteObserver(const RMessage2& aMessage)\n\t{\n",
            "void CApaAppListServSession::RegisterListPopulationCompleteObserver(const RMessage2& aMessage)\n\t{\n"
            "\tHtcleoApaServerLog(0x00000300u, KErrNone,\n"
            "\t\t(TUint32)iAppList.IsFirstScanComplete());\n",
            "observer entry",
        )
        apsses = replace_once(
            apsses,
            "\t\tif(iAppList.IsFirstScanComplete())\n\t\t\taMessage.Complete(KErrNone);\n\t\telse\n\t\t\tiCompletionOfListPopulationObserverMsg=aMessage;\n",
            "\t\tif(iAppList.IsFirstScanComplete())\n"
            "\t\t\t{\n"
            "\t\t\taMessage.Complete(KErrNone);\n"
            "\t\t\tHtcleoApaServerLog(0x00000301u, KErrNone, 1u);\n"
            "\t\t\t}\n"
            "\t\telse\n"
            "\t\t\t{\n"
            "\t\t\tiCompletionOfListPopulationObserverMsg=aMessage;\n"
            "\t\t\tHtcleoApaServerLog(0x00000302u, KRequestPending, 0u);\n"
            "\t\t\t}\n",
            "observer branch",
        )
        apsses = replace_once(
            apsses,
            "void CApaAppListServSession::NotifyClientForCompletionOfListPopulation()\n\t{\n\tif (!iCompletionOfListPopulationObserverMsg.IsNull())\n\t\tiCompletionOfListPopulationObserverMsg.Complete(KErrNone);\n\t}",
            "void CApaAppListServSession::NotifyClientForCompletionOfListPopulation()\n\t{\n"
            "\tHtcleoApaServerLog(0x00000410u, KErrNone,\n"
            "\t\t(TUint32)!iCompletionOfListPopulationObserverMsg.IsNull());\n"
            "\tif (!iCompletionOfListPopulationObserverMsg.IsNull())\n"
            "\t\tiCompletionOfListPopulationObserverMsg.Complete(KErrNone);\n"
            "\tHtcleoApaServerLog(0x00000411u, KErrNone, 0u);\n"
            "\t}",
            "observer completion",
        )
        paths["apsses"].write_text(apsses, encoding="utf-8")

    aplist = paths["aplist"].read_text(encoding="utf-8")
    if MARKER in aplist and "gHtcleoApaScanStep" in aplist:
        # V1 initially used writable DLL data for a cosmetic scan counter.
        # Symbian DLLs reject that at elf2e32, and the counter is unnecessary:
        # the record already carries TickCount and the append offset.  Migrate
        # an already-installed tree without disturbing any checkpoint anchor.
        if aplist.count("gHtcleoApaScanStep") != 5:
            raise SystemExit("APLIST scan-counter migration count mismatch")
        aplist = aplist.replace("static TUint32 gHtcleoApaScanStep = 0;\n\n", "", 1)
        aplist = aplist.replace("++gHtcleoApaScanStep", "User::TickCount()", 1)
        aplist = aplist.replace("gHtcleoApaScanStep", "User::TickCount()")
        paths["aplist"].write_text(aplist, encoding="utf-8")
    if MARKER not in aplist:
        aplist = replace_once(
            aplist,
            '#endif\n\n\n// Delays in the pseudo idle object that builds the application list\n',
            '#endif\n#include "htcleoapplistlog.h"\n\n'
            f'// {MARKER}\n\n'
            '// Delays in the pseudo idle object that builds the application list\n',
            "APLIST include",
        )
        aplist = replace_once(
            aplist,
            "EXPORT_C void CApaAppList::InitListL(MApaAppListObserver* aObserver)\n/** It Restores the data present in the AppsList.bin file and updates the applist. ",
            "EXPORT_C void CApaAppList::InitListL(MApaAppListObserver* aObserver)\n/** It Restores the data present in the AppsList.bin file and updates the applist. ",
            "InitList declaration guard",
        )
        aplist = replace_once(
            aplist,
            "\t{\n\tDeleteAppsListBackUpAndTempFiles();\n\tTInt ret = KErrGeneral;\n#ifndef __WINS__ // on the emulator, don't read app list from file, as doing so means apps\n",
            "\t{\n"
            "\tHtcleoApaListLog(0x00001000u, KErrNone, 0u);\n"
            "\tDeleteAppsListBackUpAndTempFiles();\n"
            "\tTInt ret = KErrGeneral;\n#ifndef __WINS__ // on the emulator, don't read app list from file, as doing so means apps\n",
            "InitList entry",
        )
        aplist = replace_once(
            aplist,
            "\tTRAP(ret, RestoreL());\n#endif\n\tif (ret != KErrNone)\n",
            "\tTRAP(ret, RestoreL());\n#endif\n"
            "\tHtcleoApaListLog(0x00001001u, ret, 0u);\n"
            "\tif (ret != KErrNone)\n",
            "restore result",
        )
        aplist = replace_once(
            aplist,
            "\t\tiFs.Delete(iAppsListCacheFileName);\n\t\tStartIdleUpdateL(aObserver);\n",
            "\t\tiFs.Delete(iAppsListCacheFileName);\n"
            "\t\tHtcleoApaListLog(0x00001002u, ret, 0u);\n"
            "\t\tStartIdleUpdateL(aObserver);\n"
            "\t\tHtcleoApaListLog(0x00001003u, KErrNone, 0u);\n",
            "fallback scan",
        )
        aplist = replace_once(
            aplist,
            "\telse\n\t\t{\n\t\tiObserver = aObserver;\n",
            "\telse\n\t\t{\n"
            "\t\tHtcleoApaListLog(0x00001004u, KErrNone, 1u);\n"
            "\t\tiObserver = aObserver;\n",
            "restore branch",
        )
        aplist = replace_once(
            aplist,
            "EXPORT_C void CApaAppList::StartIdleUpdateL()\n",
            "EXPORT_C void CApaAppList::StartIdleUpdateL()\n",
            "StartIdle declaration guard",
        )
        aplist = replace_once(
            aplist,
            "list is stored. */\n\t{\n"
            "\t// find the default icons (.mbm file) for applications, wrt current locale\n",
            "list is stored. */\n\t{\n"
            "\tHtcleoApaListLog(0x00001100u, KErrNone,\n"
            "\t\t(TUint32)IsFirstScanComplete());\n"
            "\t// find the default icons (.mbm file) for applications, wrt current locale\n",
            "StartIdle entry",
        )
        aplist = replace_once(
            aplist,
            "\tiAppRegFinder->FindAllAppsL(CApaAppRegFinder::EScanAllDrives);\n",
            "\tiAppRegFinder->FindAllAppsL(CApaAppRegFinder::EScanAllDrives);\n"
            "\tHtcleoApaListLog(0x00001101u, KErrNone, 0u);\n",
            "FindAllApps return",
        )
        aplist = replace_once(
            aplist,
            "\tiAppIdler->Start(KIdleStartDelay, IsFirstScanComplete()? 0 : iIdlePeriodicDelay, TCallBack(IdleUpdateCallbackL, this));\n",
            "\tconst TInt htcleoIdleDelay = IsFirstScanComplete()? 0 : iIdlePeriodicDelay;\n"
            "\tiAppIdler->Start(KIdleStartDelay, htcleoIdleDelay, TCallBack(IdleUpdateCallbackL, this));\n"
            "\tHtcleoApaListLog(0x00001102u, KErrNone, (TUint32)htcleoIdleDelay);\n",
            "idler start",
        )
        aplist = replace_once(
            aplist,
            "\t{\n\tiObserver=aObserver;\n\n\t// Rename Appslist.bin file to AppsList_Backup.bin",
            "\t{\n"
            "\tHtcleoApaListLog(0x00001110u, KErrNone, 0u);\n"
            "\tiObserver=aObserver;\n\n\t// Rename Appslist.bin file to AppsList_Backup.bin",
            "observer StartIdle entry",
        )
        aplist = replace_once(
            aplist,
            "\tTInt replaceError = iFs.Replace(iAppsListCacheFileName, iAppsListCacheBackUpFileName);\n",
            "\tTInt replaceError = iFs.Replace(iAppsListCacheFileName, iAppsListCacheBackUpFileName);\n"
            "\tHtcleoApaListLog(0x00001111u, replaceError, 0u);\n",
            "cache replace result",
        )
        aplist = replace_once(
            aplist,
            "\tStartIdleUpdateL();\n\t}\n\nvoid CApaAppList::CreateDefaultAppIconFileNameL()",
            "\tStartIdleUpdateL();\n"
            "\tHtcleoApaListLog(0x00001112u, KErrNone, 0u);\n"
            "\t}\n\nvoid CApaAppList::CreateDefaultAppIconFileNameL()",
            "observer StartIdle return",
        )
        aplist = replace_once(
            aplist,
            "TInt CApaAppList::IdleUpdateL()\n// returns ETrue if there is more scanning to be done.\n\t{\n\tTBool more=EFalse;\n\tTApaAppEntry currentApp = TApaAppEntry();\n\tTRAPD(err, more = iAppRegFinder->NextL(currentApp, *iForcedRegistrations));\n",
            "TInt CApaAppList::IdleUpdateL()\n// returns ETrue if there is more scanning to be done.\n\t{\n"
            "\tconst TUint32 htcleoScanStep = User::TickCount();\n"
            "\tHtcleoApaListLog(0x00001200u, KErrNone, htcleoScanStep);\n"
            "\tTBool more=EFalse;\n"
            "\tTApaAppEntry currentApp = TApaAppEntry();\n"
            "\tTRAPD(err, more = iAppRegFinder->NextL(currentApp, *iForcedRegistrations));\n"
            "\tHtcleoApaListLog(0x00001201u, err, more ?\n"
            "\t\t(TUint32)currentApp.iUidType[2].iUid : 0u);\n",
            "IdleUpdate NextL",
        )
        aplist = replace_once(
            aplist,
            "\t\tTRAPD(err,UpdateNextAppL(currentApp,hasChanged));\n\t\tif (err!=KErrNone)\n",
            "\t\tTRAPD(err,UpdateNextAppL(currentApp,hasChanged));\n"
            "\t\tHtcleoApaListLog(0x00001202u, err,\n"
            "\t\t\t(TUint32)currentApp.iUidType[2].iUid);\n"
            "\t\tif (err!=KErrNone)\n",
            "IdleUpdate app",
        )
        aplist = replace_once(
            aplist,
            "\telse\n\t\t{\n\t\tSetNotFound(iAppData,hasChanged);\n\t\tPurgeL();\n\t\t}\n\n\tif (hasChanged)\n",
            "\telse\n\t\t{\n"
            "\t\tHtcleoApaListLog(0x00001203u, KErrNone, htcleoScanStep);\n"
            "\t\tSetNotFound(iAppData,hasChanged);\n"
            "\t\tPurgeL();\n"
            "\t\tHtcleoApaListLog(0x00001204u, KErrNone, htcleoScanStep);\n"
            "\t\t}\n\n\tif (hasChanged)\n",
            "IdleUpdate purge",
        )
        aplist = replace_once(
            aplist,
            "\tif (hasChanged)\n\t\tiFlags |= EAppListHasChanged;\n\n\treturn more;\n",
            "\tif (hasChanged)\n\t\tiFlags |= EAppListHasChanged;\n\n"
            "\tHtcleoApaListLog(0x00001205u, KErrNone,\n"
            "\t\t(htcleoScanStep << 1) | (more ? 1u : 0u));\n"
            "\treturn more;\n",
            "IdleUpdate return",
        )
        aplist = replace_once(
            aplist,
            "void CApaAppList::InitiateStoringOfAppList()\n\t{\n\tScanComplete();\t\n\tNotifyObserver();\n",
            "void CApaAppList::InitiateStoringOfAppList()\n\t{\n"
            "\tHtcleoApaListLog(0x00001300u, KErrNone, User::TickCount());\n"
            "\tScanComplete();\t\n"
            "\tHtcleoApaListLog(0x00001301u, KErrNone, User::TickCount());\n"
            "\tNotifyObserver();\n"
            "\tHtcleoApaListLog(0x00001302u, KErrNone, User::TickCount());\n",
            "storing handoff",
        )
        aplist = replace_once(
            aplist,
            "void CApaAppList::ScanComplete()\n\t{\n\tif (!(iFlags & EFirstScanComplete) && iObserver)\n\t\tiObserver->InitialListPopulationComplete();\n",
            "void CApaAppList::ScanComplete()\n\t{\n"
            "\tHtcleoApaListLog(0x00001310u, KErrNone, (TUint32)iFlags);\n"
            "\tif (!(iFlags & EFirstScanComplete) && iObserver)\n"
            "\t\tiObserver->InitialListPopulationComplete();\n"
            "\tHtcleoApaListLog(0x00001311u, KErrNone, (TUint32)iFlags);\n",
            "ScanComplete observer",
        )
        paths["aplist"].write_text(aplist, encoding="utf-8")

    for mmp_name, source_line in (
        ("apserv_mmp", "source          htcleoapalog.cpp\n"),
        ("aplist_mmp", "source          htcleoapplistlog.cpp\n"),
    ):
        mmp = paths[mmp_name].read_text(encoding="utf-8")
        if source_line not in mmp:
            mmp = replace_once(mmp, "SMPSAFE\n", source_line + f"MACRO          {MACRO}\n\nSMPSAFE\n", f"{mmp_name} source/macro")
            paths[mmp_name].write_text(mmp, encoding="utf-8")

    verify(paths)
    print("HTCLEO_APPARC_DURABLE_LOG=installed path=C:\\Symbian3\\APALOG.TXT")


if __name__ == "__main__":
    main()
