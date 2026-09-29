#!/usr/bin/env python3
"""Install a fail-open, per-command CLE startup trace in the full PDK tree.

The logger is deliberately downstream of the hardware-proven iteration-403
FAT path.  The CLE server thread is its sole writer.  Every record is flushed
to C:\\Symbian3\\CLELOG.TXT before execution advances, so the last complete
record distinguishes a synchronous Execute() stall, an outstanding async
command, a timer wait, and a completed command-list boundary.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_CLE_DURABLE_LOG_V1"
MACRO = "__HTCLEO_CLE_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(cpp: str, header: str, mmp: str) -> None:
    checks = {
        "marker": cpp.count(MARKER) == 1,
        "target macro": mmp.count(f"MACRO           {MACRO}") == 1,
        "logger declaration and definition": cpp.count("static void HtcleoCleLog(") == 2,
        "logger body": cpp.count("TUint32 aCount, TUint32 aType, TInt aResult)\n\t{") == 1,
        "writer path": cpp.count("C:\\\\Symbian3\\\\CLELOG.TXT") == 1,
        "list start": cpp.count("KHtcleoCleListStart") == 2,
        "command complete": cpp.count("KHtcleoCleCommandComplete") == 2,
        "dispatch enter": cpp.count("KHtcleoCleDispatchEnter") == 3,
        "dispatch return": cpp.count("KHtcleoCleDispatchReturn") == 3,
        "delay start": cpp.count("KHtcleoCleDelayStart") == 2,
        "delay complete": cpp.count("KHtcleoCleDelayComplete") == 2,
        "list complete": cpp.count("KHtcleoCleListComplete") == 3,
        "run error": cpp.count("KHtcleoCleRunError") == 2,
        "request kind member": header.count("iHtcleoRequestKind") == 1,
        "list id member": header.count("iHtcleoListId") == 1,
        "header guard": header.count(f"#ifdef {MACRO}") == 1,
        "no sleep": "User::After" not in cpp,
        "sync write": cpp.count("file.Write(record)") == 1,
        "durable flush": cpp.count("file.Flush()") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("durable CLE log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    cle = args.root / "sf/os/devicesrv/sysstatemgmt/systemstatemgr/cle"
    cpp_path = cle / "src/cmdlistexecutor.cpp"
    header_path = cle / "inc/cmdlistexecutor.h"
    mmp_path = cle / "group/clesrv.mmp"
    for path in (cpp_path, header_path, mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing CLE source: {path}")

    cpp = cpp_path.read_text(encoding="utf-8")
    header = header_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")
    if MARKER in cpp:
        verify(cpp, header, mmp)
        print("HTCLEO_CLE_DURABLE_LOG=installed events=list+command+delay+fatal")
        return

    cpp = replace_once(
        cpp,
        '#include "cmdlistexecutor.h"\n',
        '#include "cmdlistexecutor.h"\n\n'
        '#ifdef __HTCLEO_CLE_DURABLE_LOG__\n'
        '#include <ssm/ssmcommand.h>\n'
        '#include <f32file.h>\n'
        '#endif\n',
        "CLE includes",
    )

    logger = r'''
#ifdef __HTCLEO_CLE_DURABLE_LOG__
// HTCLEO_CLE_DURABLE_LOG_V1
// Best-effort command-list evidence.  The CLE server thread is the sole writer.
static TInt gHtcleoCleLogSequence = 0;
static TUint32 gHtcleoCleNextListId = 0;
static TBool gHtcleoCleLogStarted = EFalse;

static const TUint32 KHtcleoCleListStart = 0x00000001u;
static const TUint32 KHtcleoCleCommandComplete = 0x00000002u;
static const TUint32 KHtcleoCleDispatchEnter = 0x00000003u;
static const TUint32 KHtcleoCleDispatchReturn = 0x00000004u;
static const TUint32 KHtcleoCleDelayStart = 0x00000005u;
static const TUint32 KHtcleoCleDelayComplete = 0x00000006u;
static const TUint32 KHtcleoCleListComplete = 0x00000008u;
static const TUint32 KHtcleoCleRunError = 0xE0000001u;

static void HtcleoCleLog(TUint32 aList, TUint32 aEvent, TUint32 aIndex,
                         TUint32 aCount, TUint32 aType, TInt aResult)
                         __attribute__((noinline));

static void HtcleoCleLog(TUint32 aList, TUint32 aEvent, TUint32 aIndex,
                         TUint32 aCount, TUint32 aType, TInt aResult)
	{
	if(gHtcleoCleLogSequence >= 512)
		{
		return;
		}

	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoCleLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoCleLogPath, "C:\\Symbian3\\CLELOG.TXT");
	r = fs.MkDirAll(KHtcleoCleLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	if(!gHtcleoCleLogStarted)
		{
		r = file.Replace(fs, KHtcleoCleLogPath, EFileWrite | EFileShareAny);
		}
	else
		{
		r = file.Open(fs, KHtcleoCleLogPath, EFileWrite | EFileShareAny);
		if(r == KErrNone)
			{
			r = file.Seek(ESeekEnd, position);
			}
		}

	if(r == KErrNone)
		{
		_LIT8(KHtcleoClePrefix, "HTCLEO_CLE ");
		TBuf8<96> record;
		record.Append(KHtcleoClePrefix);
		record.AppendNumFixedWidth((TUint)gHtcleoCleLogSequence, EHex, 4);
		record.Append(' ');
		record.AppendNumFixedWidth(aList, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aEvent, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aIndex, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aCount, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aType, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
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
		gHtcleoCleLogStarted = ETrue;
		++gHtcleoCleLogSequence;
		}
	}
#endif

'''
    cpp = replace_once(cpp, "/**\n Initiate command processing.", logger + "/**\n Initiate command processing.", "logger insertion")

    cpp = replace_once(
        cpp,
        "\tiCommandIndex = 0;\n\t\n\tSetActive();\n",
        "\tiCommandIndex = 0;\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\tiHtcleoRequestKind = 0;\n"
        "\tiHtcleoListId = ++gHtcleoCleNextListId;\n"
        "\tif(iHtcleoListId == 0)\n"
        "\t\t{\n"
        "\t\tiHtcleoListId = ++gHtcleoCleNextListId;\n"
        "\t\t}\n"
        "\tHtcleoCleLog(iHtcleoListId, KHtcleoCleListStart, 0xFFFFFFFFu,\n"
        "\t\t(TUint32)iCommandCount, 0xFFFFFFFFu, iSessionIndex);\n"
        "#endif\n"
        "\t\n\tSetActive();\n",
        "StartL list record",
    )

    cpp = replace_once(
        cpp,
        "void CSsmCmdListExecutor::RunL()\n\t{\n",
        "void CSsmCmdListExecutor::RunL()\n\t{\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\tif(iHtcleoRequestKind == 1 && iCommandIndex > 0)\n"
        "\t\t{\n"
        "\t\tconst TInt htcleoCompletedIndex = iCommandIndex - 1;\n"
        "\t\tconst MSsmCommand* htcleoCompleted = (*iCommandList)[htcleoCompletedIndex];\n"
        "\t\tconst TUint32 htcleoCompletedType = htcleoCompleted ?\n"
        "\t\t\t(TUint32)htcleoCompleted->Type() : 0xFFFFFFFFu;\n"
        "\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleCommandComplete,\n"
        "\t\t\t(TUint32)htcleoCompletedIndex, (TUint32)iCommandCount,\n"
        "\t\t\thtcleoCompletedType, iStatus.Int());\n"
        "\t\t}\n"
        "\telse if(iHtcleoRequestKind == 2)\n"
        "\t\t{\n"
        "\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleDelayComplete,\n"
        "\t\t\t(TUint32)iCommandIndex, (TUint32)iCommandCount,\n"
        "\t\t\t0xFFFFFFFFu, iStatus.Int());\n"
        "\t\t}\n"
        "\tiHtcleoRequestKind = 0;\n"
        "#endif\n",
        "RunL completion record",
    )

    cpp = replace_once(
        cpp,
        "\t\tfor (; iCommandIndex < iCommandCount; iCommandIndex++)\n"
        "\t\t\t{\n"
        "\t\t\tiCommandList->ExecuteCancel(iCommandIndex);\n"
        "\t\t\t}\n"
        "\t\tiObserver.ListExecutionComplete( iStatus.Int(), iSessionIndex, iCommandList->Severity(iCommandIndex-1) );\n",
        "\t\tfor (; iCommandIndex < iCommandCount; iCommandIndex++)\n"
        "\t\t\t{\n"
        "\t\t\tiCommandList->ExecuteCancel(iCommandIndex);\n"
        "\t\t\t}\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleListComplete,\n"
        "\t\t\t(TUint32)iCommandIndex, (TUint32)iCommandCount,\n"
        "\t\t\t0xFFFFFFFFu, iStatus.Int());\n"
        "#endif\n"
        "\t\tiObserver.ListExecutionComplete( iStatus.Int(), iSessionIndex, iCommandList->Severity(iCommandIndex-1) );\n",
        "error list completion",
    )
    cpp = replace_once(
        cpp,
        "\t\t// The last command must have completed.\n"
        "\t\tiRunning = EFalse;\n"
        "\t\tiObserver.ListExecutionComplete( iStatus.Int(), iSessionIndex, iCommandList->Severity(iCommandIndex-1) );\n",
        "\t\t// The last command must have completed.\n"
        "\t\tiRunning = EFalse;\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleListComplete,\n"
        "\t\t\t(TUint32)iCommandIndex, (TUint32)iCommandCount,\n"
        "\t\t\t0xFFFFFFFFu, iStatus.Int());\n"
        "#endif\n"
        "\t\tiObserver.ListExecutionComplete( iStatus.Int(), iSessionIndex, iCommandList->Severity(iCommandIndex-1) );\n",
        "success list completion",
    )

    cpp = replace_once(
        cpp,
        "\t\t\tiDoDelayToggle = EFalse;\n\t\t\tiTimer.After( iStatus, iInterCmdDelay * KMilliToMicro );\n",
        "\t\t\tiDoDelayToggle = EFalse;\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\t\tiHtcleoRequestKind = 2;\n"
        "\t\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleDelayStart,\n"
        "\t\t\t\t(TUint32)iCommandIndex, (TUint32)iCommandCount,\n"
        "\t\t\t\t0xFFFFFFFFu, iInterCmdDelay);\n"
        "#endif\n"
        "\t\t\tiTimer.After( iStatus, iInterCmdDelay * KMilliToMicro );\n",
        "timer record",
    )

    execute_with_delay = "\t\t\tiCommandList->Execute( iCommandIndex++, iStatus );\n\t\t\t\n\t\t\tSetActive();\n"
    execute_with_delay_new = (
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\t\tconst TInt htcleoCommandIndex = iCommandIndex;\n"
        "\t\t\tconst MSsmCommand* htcleoCommand = (*iCommandList)[htcleoCommandIndex];\n"
        "\t\t\tconst TUint32 htcleoType = htcleoCommand ? (TUint32)htcleoCommand->Type() : 0xFFFFFFFFu;\n"
        "\t\t\tconst TInt htcleoAttrs = htcleoCommand ?\n"
        "\t\t\t\t(((TInt)htcleoCommand->Severity() << 16) | ((TInt)htcleoCommand->ExecutionBehaviour() & 0xFFFF)) : -1;\n"
        "\t\t\tiHtcleoRequestKind = 1;\n"
        "\t\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleDispatchEnter,\n"
        "\t\t\t\t(TUint32)htcleoCommandIndex, (TUint32)iCommandCount, htcleoType, htcleoAttrs);\n"
        "#endif\n"
        "\t\t\tiCommandList->Execute( iCommandIndex++, iStatus );\n\t\t\t\n\t\t\tSetActive();\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleDispatchReturn,\n"
        "\t\t\t\t(TUint32)htcleoCommandIndex, (TUint32)iCommandCount, htcleoType, iStatus.Int());\n"
        "#endif\n"
    )
    cpp = replace_once(cpp, execute_with_delay, execute_with_delay_new, "delayed command records")

    execute_no_delay = "\t\tiCommandList->Execute( iCommandIndex++, iStatus );\n\t\t\n\t\tSetActive();\t\t\n"
    execute_no_delay_new = (
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\tconst TInt htcleoCommandIndex = iCommandIndex;\n"
        "\t\tconst MSsmCommand* htcleoCommand = (*iCommandList)[htcleoCommandIndex];\n"
        "\t\tconst TUint32 htcleoType = htcleoCommand ? (TUint32)htcleoCommand->Type() : 0xFFFFFFFFu;\n"
        "\t\tconst TInt htcleoAttrs = htcleoCommand ?\n"
        "\t\t\t(((TInt)htcleoCommand->Severity() << 16) | ((TInt)htcleoCommand->ExecutionBehaviour() & 0xFFFF)) : -1;\n"
        "\t\tiHtcleoRequestKind = 1;\n"
        "\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleDispatchEnter,\n"
        "\t\t\t(TUint32)htcleoCommandIndex, (TUint32)iCommandCount, htcleoType, htcleoAttrs);\n"
        "#endif\n"
        "\t\tiCommandList->Execute( iCommandIndex++, iStatus );\n\t\t\n\t\tSetActive();\t\t\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\t\tHtcleoCleLog(iHtcleoListId, KHtcleoCleDispatchReturn,\n"
        "\t\t\t(TUint32)htcleoCommandIndex, (TUint32)iCommandCount, htcleoType, iStatus.Int());\n"
        "#endif\n"
    )
    cpp = replace_once(cpp, execute_no_delay, execute_no_delay_new, "non-delayed command records")

    cpp = replace_once(
        cpp,
        "TInt CSsmCmdListExecutor::RunError( TInt aError )\n\t{\t\n\tiRunning = EFalse;\n",
        "TInt CSsmCmdListExecutor::RunError( TInt aError )\n\t{\t\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\tHtcleoCleLog(iHtcleoListId, KHtcleoCleRunError,\n"
        "\t\t(TUint32)iCommandIndex, (TUint32)iCommandCount,\n"
        "\t\t0xFFFFFFFFu, aError);\n"
        "#endif\n"
        "\tiRunning = EFalse;\n",
        "RunError record",
    )

    header = replace_once(
        header,
        "\tTInt iInterCmdDelay;\n\t\n",
        "\tTInt iInterCmdDelay;\n"
        "#ifdef __HTCLEO_CLE_DURABLE_LOG__\n"
        "\tTUint32 iHtcleoListId;\n"
        "\tTInt iHtcleoRequestKind; // 0=self/none, 1=command, 2=delay\n"
        "#endif\n\t\n",
        "executor trace state",
    )

    mmp = replace_once(
        mmp,
        "targetpath      /sys/bin\n",
        "targetpath      /sys/bin\n\nMACRO           __HTCLEO_CLE_DURABLE_LOG__\n",
        "CLE target macro",
    )

    verify(cpp, header, mmp)
    cpp_path.write_text(cpp, encoding="utf-8")
    header_path.write_text(header, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print("HTCLEO_CLE_DURABLE_LOG=installed events=list+command+delay+fatal")


if __name__ == "__main__":
    main()
