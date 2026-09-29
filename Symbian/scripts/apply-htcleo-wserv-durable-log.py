#!/usr/bin/env python3
"""Install a fail-open HTCLEO Window Server startup trace.

The trace starts only after CLE has launched ``ewsrv.exe``.  The Window Server
main thread is the sole writer.  Each completed checkpoint appends and flushes
one fixed ASCII record to ``C:\\Symbian3\\WSLOG.TXT``; logging errors are
ignored and never change Window Server control flow.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_DURABLE_LOG_V1"
CAPACITY_MARKER = "HTCLEO_WSERV_LOG_CAPACITY_512_V1"
MACRO = "__HTCLEO_WSERV_DURABLE_LOG__"
COMPAT_WRAPPER = """#ifndef HTCLEO_CASE_COMPAT_WSGRAPHICDRAWERINTERFACE_H
#define HTCLEO_CASE_COMPAT_WSGRAPHICDRAWERINTERFACE_H
#include <graphics/wsgraphicdrawerinterface.h>
#endif
"""
COMPAT_CONSTANTS = """#ifndef HTCLEO_CASE_COMPAT_WINDOWSERVERCONSTANTS_H
#define HTCLEO_CASE_COMPAT_WINDOWSERVERCONSTANTS_H
#include <Graphics/windowserverconstants.h>
#endif
"""


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(cpp: str, mmp: str, wrapper: str, constants: str, wstypes: str) -> None:
    expected_stages = (
        "0x00000001u", "0x00000002u", "0x00000003u", "0x00000004u",
        "0x00000010u", "0x00000011u", "0x00000012u", "0x00000013u",
        "0x00000014u", "0x00000015u", "0x00000016u", "0x00000017u",
        "0x00000018u", "0x00000019u", "0x0000001Au", "0x0000001Bu",
        "0x0000001Cu", "0x0000001Du", "0x0000001Eu", "0x0000001Fu",
        "0x00000020u", "0x00000021u", "0x00000022u", "0x00000023u",
        "0x00000030u", "0x00000031u", "0xE0000001u",
    )
    checks = {
        "marker": cpp.count(MARKER) == 1,
        "target macro": mmp.count(f"MACRO             {MACRO}") == 1,
        "case-compat wrapper": wrapper == COMPAT_WRAPPER,
        "case-compat constants": constants == COMPAT_CONSTANTS,
        "GCCE dependent-base fix": "TRegion::iAllocedRects" not in wstypes
        and "TRegion::iCount" not in wstypes,
        "external logger declaration and definition": cpp.count("\nvoid HtcleoWsLog(") == 2
        and cpp.count("static void HtcleoWsLog(") == 0,
        "one writer path": cpp.count("C:\\\\Symbian3\\\\WSLOG.TXT") == 1,
        "record prefix": cpp.count("HTCLEO_WS ") == 1,
        "sync write": cpp.count("file.Write(record)") == 1,
        "durable flush": cpp.count("file.Flush()") == 1,
        "512-record capacity marker": cpp.count(CAPACITY_MARKER) == 1,
        "record capacity": (
            cpp.count("gHtcleoWsLogSequence >= 512") == 1
            or ("HTCLEO_WSERV_LOG_RING_1M_V1" in cpp
                and "KCapacity = 1048576" in cpp)
        )
        and "gHtcleoWsLogSequence >= 256" not in cpp
        and "gHtcleoWsLogSequence >= 96" not in cpp,
        "no UI-thread wait": "User::After" not in cpp or (
            "HTCLEO_WSERV_NONBLOCKING_LOG_V1" in cpp
            and cpp.count("User::After") == 1
            and "User::After(100000);" in cpp[
                cpp.index("static TInt HtcleoWsLogWorker"):
                cpp.index("void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n\t{")]
        ),
        "all checkpoints": all(cpp.count(stage) == 1 for stage in expected_stages),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("durable Window Server log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    component = args.root / "sf/os/graphics/windowing/windowserver"
    cpp_path = component / "nga/SERVER/openwfc/WSTOP.CPP"
    mmp_path = component / "group/openwfc/WServ_nga.MMP"
    wrapper_path = component / "inc/Graphics/WSGRAPHICDRAWERINTERFACE.H"
    constants_path = component / "inc/graphics/windowserverconstants.h"
    wstypes_path = component / "nga/SERVER/wstypes.h"
    for path in (cpp_path, mmp_path, wstypes_path):
        if not path.is_file():
            raise SystemExit(f"missing Window Server source: {path}")

    cpp = cpp_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")
    wstypes = wstypes_path.read_text(encoding="utf-8")
    wstypes = wstypes.replace("TRegion::iCount", "this->iCount")
    wstypes = wstypes.replace("TRegion::iAllocedRects", "this->iAllocedRects")
    wstypes_path.write_text(wstypes, encoding="utf-8")
    if MARKER in cpp:
        # V2 exposes the same single writer to the plugin-manager translation
        # unit.  Normalise an already-installed V1 tree before verification.
        cpp = cpp.replace("static void HtcleoWsLog(", "void HtcleoWsLog(")
        if "HTCLEO_WSERV_LOG_CAPACITY_256_V1" in cpp:
            cpp = cpp.replace(
                "HTCLEO_WSERV_LOG_CAPACITY_256_V1", CAPACITY_MARKER, 1
            )
            cpp = replace_once(
                cpp,
                "\tif(gHtcleoWsLogSequence >= 256)\n",
                "\tif(gHtcleoWsLogSequence >= 512)\n",
                "installed logger capacity 256-to-512 upgrade",
            )
        elif CAPACITY_MARKER not in cpp:
            cpp = replace_once(
                cpp,
                "\tif(gHtcleoWsLogSequence >= 96)\n",
                f"\t// {CAPACITY_MARKER}\n"
                "\tif(gHtcleoWsLogSequence >= 512)\n",
                "installed logger capacity upgrade",
            )
        cpp_path.write_text(cpp, encoding="utf-8")
        compat_prefix = "USERINCLUDE       /path/to/hd2-legacy-lab/"
        if compat_prefix in mmp:
            mmp = "\n".join(
                line for line in mmp.splitlines()
                if not line.startswith(compat_prefix)
            ) + "\n"
            mmp_path.write_text(mmp, encoding="utf-8")
        if wrapper_path.exists() and wrapper_path.read_text(encoding="utf-8") != COMPAT_WRAPPER:
            raise SystemExit(f"unexpected case-compat wrapper content: {wrapper_path}")
        wrapper_path.write_text(COMPAT_WRAPPER, encoding="utf-8")
        constants_path.parent.mkdir(parents=True, exist_ok=True)
        if constants_path.exists() and constants_path.read_text(encoding="utf-8") != COMPAT_CONSTANTS:
            raise SystemExit(f"unexpected case-compat constants content: {constants_path}")
        constants_path.write_text(COMPAT_CONSTANTS, encoding="utf-8")
        verify(
            cpp, mmp, wrapper_path.read_text(encoding="utf-8"),
            constants_path.read_text(encoding="utf-8"), wstypes,
        )
        print("HTCLEO_WSERV_DURABLE_LOG=installed checkpoints=27 capacity=512 path=C:\\Symbian3\\WSLOG.TXT")
        return

    cpp = replace_once(
        cpp,
        '#include "wstop.h"\n',
        '#include "wstop.h"\n\n'
        f'#ifdef {MACRO}\n'
        '#include <f32file.h>\n'
        '#endif\n',
        "f32 include",
    )

    logger = r'''
#ifdef __HTCLEO_WSERV_DURABLE_LOG__
// HTCLEO_WSERV_DURABLE_LOG_V1
// Best-effort startup evidence.  The Window Server main thread is sole writer.
static TInt gHtcleoWsLogSequence = 0;
static TBool gHtcleoWsLogStarted = EFalse;

void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                         __attribute__((noinline));

void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	// HTCLEO_WSERV_LOG_CAPACITY_512_V1
	if(gHtcleoWsLogSequence >= 512)
		{
		return;
		}

	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoWsLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoWsLogPath, "C:\\Symbian3\\WSLOG.TXT");
	r = fs.MkDirAll(KHtcleoWsLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	if(!gHtcleoWsLogStarted)
		{
		r = file.Replace(fs, KHtcleoWsLogPath, EFileWrite | EFileShareAny);
		}
	else
		{
		r = file.Open(fs, KHtcleoWsLogPath, EFileWrite | EFileShareAny);
		if(r == KErrNone)
			{
			r = file.Seek(ESeekEnd, position);
			}
		}

	if(r == KErrNone)
		{
		_LIT8(KHtcleoWsPrefix, "HTCLEO_WS ");
		TBuf8<64> record;
		record.Append(KHtcleoWsPrefix);
		record.AppendNumFixedWidth((TUint)gHtcleoWsLogSequence, EHex, 2);
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
			r = file.Flush();
			}
		file.Close();
		}

	fs.Close();
	if(r == KErrNone)
		{
		gHtcleoWsLogStarted = ETrue;
		++gHtcleoWsLogSequence;
		}
	}
#else
static inline void HtcleoWsLog(TUint32, TInt, TUint32) {}
#endif

'''
    cpp = replace_once(
        cpp,
        "typedef CDebugLogBase *(*CreateDebugLog)(TBool aIsFirst, TDesC &aParams);\n",
        "typedef CDebugLogBase *(*CreateDebugLog)(TBool aIsFirst, TDesC &aParams);\n" + logger,
        "logger insertion",
    )

    cpp = replace_once(
        cpp,
        "\tUserSvr::WsRegisterThread();\n",
        "\tUserSvr::WsRegisterThread();\n\tHtcleoWsLog(0x00000001u, KErrNone, 0u);\n",
        "E32Main entry",
    )
    cpp = replace_once(
        cpp,
        "\telse\n\t\t{\n\t\treturn err;\n\t\t}\n\n\tCTrapCleanup* CleanUpStack=CTrapCleanup::New();",
        "\telse\n\t\t{\n\t\treturn err;\n\t\t}\n"
        "\tHtcleoWsLog(0x00000002u, err, 0u);\n\n"
        "\tCTrapCleanup* CleanUpStack=CTrapCleanup::New();",
        "thread rename return",
    )
    cpp = replace_once(
        cpp,
        "\tTRAP(err, WsIniFile = CIniFile::NewL());\n\tif (err!=KErrNone)",
        "\tTRAP(err, WsIniFile = CIniFile::NewL());\n"
        "\tHtcleoWsLog(0x00000003u, err, (TUint32)(WsIniFile != NULL));\n"
        "\tif (err!=KErrNone)",
        "INI return",
    )
    cpp = replace_once(
        cpp,
        "\t\tstartCount=User::Heap().Count();\n\t\tTRAP(err,CWsTop::RunServerL());\n\t\tif (err!=KErrNone)",
        "\t\tstartCount=User::Heap().Count();\n"
        "\t\tHtcleoWsLog(0x00000004u, KErrNone, (TUint32)startCount);\n"
        "\t\tTRAP(err,CWsTop::RunServerL());\n"
        "\t\tHtcleoWsLog(0xE0000001u, err, 0u);\n"
        "\t\tif (err!=KErrNone)",
        "RunServer trap",
    )

    cpp = replace_once(
        cpp,
        "void CWsTop::InitStaticsL()\n\t{\n\tiShuttingDown=EFalse;",
        "void CWsTop::InitStaticsL()\n\t{\n"
        "\tHtcleoWsLog(0x00000010u, KErrNone, 0u);\n"
        "\tiShuttingDown=EFalse;",
        "InitStatics entry",
    )
    cpp = replace_once(
        cpp,
        "\tiIgnoreSwitchOffEvent = WsIniFile->FindVar(KWSERVIniFileVarSwitchOffEvent);\t\n\n\tiPluginManager",
        "\tiIgnoreSwitchOffEvent = WsIniFile->FindVar(KWSERVIniFileVarSwitchOffEvent);\t\n"
        "\tHtcleoWsLog(0x00000011u, KErrNone, (TUint32)startShell);\n\n"
        "\tiPluginManager",
        "scheduler and INI complete",
    )
    cpp = replace_once(
        cpp,
        "\tiPluginManager = CWsPluginManager::NewL(); // need to be constructed before iServer!\n\tiServer=CWindowServer::NewL();",
        "\tiPluginManager = CWsPluginManager::NewL(); // need to be constructed before iServer!\n"
        "\tHtcleoWsLog(0x00000012u, KErrNone, (TUint32)(iPluginManager != NULL));\n"
        "\tiServer=CWindowServer::NewL();",
        "plugin manager return",
    )
    cpp = replace_once(
        cpp,
        "\tiServer=CWindowServer::NewL();\n\tCClick::InitStaticsL();",
        "\tiServer=CWindowServer::NewL();\n"
        "\tHtcleoWsLog(0x00000013u, KErrNone, (TUint32)(iServer != NULL));\n"
        "\tCClick::InitStaticsL();",
        "server return",
    )
    cpp = replace_once(
        cpp,
        "\tUser::LeaveIfError(FbsStartup());\n\tUser::LeaveIfError(RFbsSession::Connect());\n\tUser::LeaveIfError(iTimer.CreateLocal());",
        "\tTInt htcleoResult = FbsStartup();\n"
        "\tHtcleoWsLog(0x00000014u, htcleoResult, 0u);\n"
        "\tUser::LeaveIfError(htcleoResult);\n"
        "\thtcleoResult = RFbsSession::Connect();\n"
        "\tHtcleoWsLog(0x00000015u, htcleoResult, 0u);\n"
        "\tUser::LeaveIfError(htcleoResult);\n"
        "\thtcleoResult = iTimer.CreateLocal();\n"
        "\tHtcleoWsLog(0x00000016u, htcleoResult, 0u);\n"
        "\tUser::LeaveIfError(htcleoResult);",
        "FBS and timer returns",
    )
    cpp = replace_once(
        cpp,
        "\tTWindowServerEvent::InitStaticsL();\n\tCWsClient::InitStaticsL();\n\t//-------------------------------------------\n\tUser::LeaveIfError(  HAL::Get( HAL::EDisplayNumberOfScreens, iNumberOfScreens ) ) ;",
        "\tTWindowServerEvent::InitStaticsL();\n"
        "\tCWsClient::InitStaticsL();\n"
        "\tHtcleoWsLog(0x00000017u, KErrNone, 0u);\n"
        "\t//-------------------------------------------\n"
        "\thtcleoResult = HAL::Get(HAL::EDisplayNumberOfScreens, iNumberOfScreens);\n"
        "\tHtcleoWsLog(0x00000018u, htcleoResult, (TUint32)iNumberOfScreens);\n"
        "\tUser::LeaveIfError(htcleoResult);",
        "event statics and HAL return",
    )
    cpp = replace_once(
        cpp,
        "\tiScreens = new (ELeave) CArrayPtrFlat<CScreen>( iNumberOfScreens ) ;  //\n\t// now construct screens",
        "\tiScreens = new (ELeave) CArrayPtrFlat<CScreen>( iNumberOfScreens ) ;  //\n"
        "\tHtcleoWsLog(0x00000019u, KErrNone, (TUint32)iNumberOfScreens);\n"
        "\t// now construct screens",
        "screen array return",
    )
    cpp = replace_once(
        cpp,
        "\t\tInitScreenL( ii ) ;\n\t\t}\n\t//---------------------------------------------",
        "\t\tInitScreenL( ii ) ;\n\t\t}\n"
        "\tHtcleoWsLog(0x0000001Au, KErrNone, (TUint32)iNumberOfScreens);\n"
        "\t//---------------------------------------------",
        "all screens return",
    )
    cpp = replace_once(
        cpp,
        "\tiCurrentFocusScreen = (*iScreens)[0] ;\n\tiServer->StartL();\n\n\tCWsFontCache",
        "\tiCurrentFocusScreen = (*iScreens)[0] ;\n"
        "\tiServer->StartL();\n"
        "\tHtcleoWsLog(0x0000001Bu, KErrNone, 0u);\n\n"
        "\tCWsFontCache",
        "server StartL return",
    )
    cpp = replace_once(
        cpp,
        "\tCWsSpriteBase::InitStaticsL();\n\tCEventQueue::InitStaticsL();\n\n//",
        "\tCWsSpriteBase::InitStaticsL();\n"
        "\tCEventQueue::InitStaticsL();\n"
        "\tHtcleoWsLog(0x0000001Cu, KErrNone, 0u);\n\n//",
        "graphics statics return",
    )
    cpp = replace_once(
        cpp,
        "\tCWsAnimDll::InitStaticsL();\n//\n\tTInt bootMode=0;",
        "\tCWsAnimDll::InitStaticsL();\n"
        "\tHtcleoWsLog(0x0000001Du, KErrNone, 0u);\n"
        "//\n\tTInt bootMode=0;",
        "animation statics return",
    )
    cpp = replace_once(
        cpp,
        "\tTWsPointer::InitStaticsL();\n\tiShellStarter=new (ELeave) CShellStarter;",
        "\tTWsPointer::InitStaticsL();\n"
        "\tHtcleoWsLog(0x0000001Eu, KErrNone, 0u);\n"
        "\tiShellStarter=new (ELeave) CShellStarter;",
        "window and pointer statics return",
    )
    cpp = replace_once(
        cpp,
        "\tiShellStarter=new (ELeave) CShellStarter;\n\tiShellStarter->ConstructL();\n\t_LIT(KPreProcess",
        "\tiShellStarter=new (ELeave) CShellStarter;\n"
        "\tiShellStarter->ConstructL();\n"
        "\tHtcleoWsLog(0x0000001Fu, KErrNone, 0u);\n"
        "\t_LIT(KPreProcess",
        "shell starter return",
    )
    cpp = replace_once(
        cpp,
        "\tRProcess::Rendezvous(KErrNone);\n\t// Start the shell",
        "\tHtcleoWsLog(0x00000030u, KErrNone, 0u);\n"
        "\tRProcess::Rendezvous(KErrNone);\n"
        "\tHtcleoWsLog(0x00000031u, KErrNone, 0u);\n"
        "\t// Start the shell",
        "rendezvous",
    )

    cpp = replace_once(
        cpp,
        "void CWsTop::InitScreenL( TInt aScreenNumber)  // static\n\t{\n\t// create a new screen",
        "void CWsTop::InitScreenL( TInt aScreenNumber)  // static\n\t{\n"
        "\tHtcleoWsLog(0x00000020u, KErrNone, (TUint32)aScreenNumber);\n"
        "\t// create a new screen",
        "InitScreen entry",
    )
    cpp = replace_once(
        cpp,
        "\t\tdigitiserArea = TRect(-machineInfo.iOffsetToDisplayInPixels,machineInfo.iXYInputSizeInPixels);\n\t\t}\n\tscreen->ConstructL",
        "\t\tdigitiserArea = TRect(-machineInfo.iOffsetToDisplayInPixels,machineInfo.iXYInputSizeInPixels);\n"
        "\t\tHtcleoWsLog(0x00000021u, KErrNone, (TUint32)aScreenNumber);\n"
        "\t\t}\n"
        "\tscreen->ConstructL",
        "machine info return",
    )
    cpp = replace_once(
        cpp,
        "\tscreen->ConstructL(digitiserArea, aScreenNumber);\n\tiScreens->AppendL( screen ) ;",
        "\tscreen->ConstructL(digitiserArea, aScreenNumber);\n"
        "\tHtcleoWsLog(0x00000022u, KErrNone, (TUint32)aScreenNumber);\n"
        "\tiScreens->AppendL( screen ) ;",
        "screen ConstructL return",
    )
    cpp = replace_once(
        cpp,
        "\tiScreens->AppendL( screen ) ; \n\tCleanupStack::Pop( screen ) ;",
        "\tiScreens->AppendL( screen ) ; \n"
        "\tHtcleoWsLog(0x00000023u, KErrNone, (TUint32)aScreenNumber);\n"
        "\tCleanupStack::Pop( screen ) ;",
        "screen append return",
    )

    mmp = replace_once(
        mmp,
        "MACRO             SYMBIAN_GRAPHICS_GCE\n",
        "MACRO             SYMBIAN_GRAPHICS_GCE\n"
        f"MACRO             {MACRO}\n",
        "target macro",
    )

    wrapper_path.write_text(COMPAT_WRAPPER, encoding="utf-8")
    constants_path.parent.mkdir(parents=True, exist_ok=True)
    constants_path.write_text(COMPAT_CONSTANTS, encoding="utf-8")
    verify(
        cpp, mmp, wrapper_path.read_text(encoding="utf-8"),
        constants_path.read_text(encoding="utf-8"), wstypes,
    )
    cpp_path.write_text(cpp, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print("HTCLEO_WSERV_DURABLE_LOG=installed checkpoints=27 capacity=512 path=C:\\Symbian3\\WSLOG.TXT")


if __name__ == "__main__":
    main()
