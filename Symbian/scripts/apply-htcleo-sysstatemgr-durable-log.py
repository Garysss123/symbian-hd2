#!/usr/bin/env python3
"""Install the HTCLEO durable SSM startup trace in the full PDK tree.

The trace is deliberately downstream of the hardware-proven iteration-403 FAT
frontier.  sysstatemgr is the only writer.  Each completed checkpoint appends
one fixed-format ASCII line to C:\\Symbian3\\SSMLOG.TXT and flushes it.  Logging
is best-effort and never changes SSM control flow or propagates an error.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_SSM_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(main: str, server: str, engine: str) -> None:
    checks = {
        "marker": main.count(MARKER) == 1,
        "logger definition": main.count("void HtcleoSsmLog(") == 1,
        "main stage 01": main.count("HtcleoSsmLog(0x00000001u") == 1,
        "main stage 02": main.count("HtcleoSsmLog(0x00000002u") == 1,
        "main stage 06": main.count("HtcleoSsmLog(0x00000006u") == 1,
        "main stage 07": main.count("HtcleoSsmLog(0x00000007u") == 1,
        "server declaration": server.count("void HtcleoSsmLog(") == 1,
        "server stage 03": server.count("HtcleoSsmLog(0x00000003u") == 1,
        "server stage 04": server.count("HtcleoSsmLog(0x00000004u") == 1,
        "server stage 05": server.count("HtcleoSsmLog(0x00000005u") == 1,
        "engine declaration": engine.count("void HtcleoSsmLog(") == 1,
        "RunL record": engine.count("0x10000000u | (TUint32)iNextAction") == 1,
        "command submitted record": engine.count("HtcleoSsmLog(0x20000005u") == 1,
        "RunError record": engine.count("0xE0000000u | (TUint32)iNextAction") == 1,
        "no User::After": "User::After" not in main + server + engine,
        "one writer path": (main + server + engine).count("C:\\\\Symbian3\\\\SSMLOG.TXT") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("durable SSM log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT, e.g. /root/symbian3-full")
    args = parser.parse_args()

    source = args.root / "sf/os/devicesrv/sysstatemgmt/systemstatemgr/ssm/src"
    main_path = source / "main.cpp"
    server_path = source / "ssmserver.cpp"
    engine_path = source / "ssmstatetransitionengine.cpp"
    for path in (main_path, server_path, engine_path):
        if not path.is_file():
            raise SystemExit(f"missing source: {path}")

    texts = {path: path.read_text(encoding="utf-8") for path in (main_path, server_path, engine_path)}
    joined = "\n".join(texts.values())
    if MARKER in joined:
        verify(texts[main_path], texts[server_path], texts[engine_path])
        print("HTCLEO_SSM_DURABLE_LOG=installed checkpoints=fixed-01-07+runl+submit+fatal")
        return

    main_text = texts[main_path]
    main_text = replace_once(
        main_text,
        "#include <e32std.h>\n",
        "#include <e32std.h>\n#include <f32file.h>\n",
        "main f32 include",
    )

    logger = r'''
// HTCLEO_SSM_DURABLE_LOG_V1
// Best-effort, append-only startup evidence.  sysstatemgr is the sole writer.
static TInt gHtcleoSsmLogSequence = 0;
static TBool gHtcleoSsmLogStarted = EFalse;

void HtcleoSsmLog(TUint32 aStage, TUint32 aState, TInt aResult)
	{
	if(gHtcleoSsmLogSequence >= 96)
		{
		return;
		}

	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoSsmLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoSsmLogPath, "C:\\Symbian3\\SSMLOG.TXT");
	r = fs.MkDirAll(KHtcleoSsmLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	if(!gHtcleoSsmLogStarted)
		{
		r = file.Replace(fs, KHtcleoSsmLogPath, EFileWrite | EFileShareAny);
		}
	else
		{
		r = file.Open(fs, KHtcleoSsmLogPath, EFileWrite | EFileShareAny);
		if(r == KErrNone)
			{
			r = file.Seek(ESeekEnd, position);
			}
		}

	if(r == KErrNone)
		{
		_LIT8(KHtcleoSsmPrefix, "HTCLEO_SSM ");
		TBuf8<64> record;
		record.Append(KHtcleoSsmPrefix);
		record.AppendNumFixedWidth((TUint)gHtcleoSsmLogSequence, EHex, 2);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aState, EHex, 8);
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
		gHtcleoSsmLogStarted = ETrue;
		++gHtcleoSsmLogSequence;
		}
	}

'''
    main_text = replace_once(main_text, "static void MainL()\n", logger + "static void MainL()\n", "logger insertion")
    main_text = replace_once(
        main_text,
        "static void MainL()\n\t{\n",
        "static void MainL()\n\t{\n\tHtcleoSsmLog(0x00000001u, 0u, KErrNone);\n",
        "MainL entry",
    )
    main_text = replace_once(
        main_text,
        "\t\tPanicNow(KPanicSysStateMgr, EAddDomainHierarchyError);\n\t\t}\n\t\n\tCSsmServer* server",
        "\t\tPanicNow(KPanicSysStateMgr, EAddDomainHierarchyError);\n\t\t}\n\tHtcleoSsmLog(0x00000002u, 0u, err);\n\t\n\tCSsmServer* server",
        "domain hierarchy result",
    )
    main_text = replace_once(
        main_text,
        "\tCSsmServer* server = CSsmServer::NewLC(ESsmStartup);\n",
        "\tCSsmServer* server = CSsmServer::NewLC(ESsmStartup);\n\tHtcleoSsmLog(0x00000006u, 0u, KErrNone);\n",
        "server return",
    )
    main_text = replace_once(
        main_text,
        "\tRProcess::Rendezvous(KErrNone);\n",
        "\tRProcess::Rendezvous(KErrNone);\n\tHtcleoSsmLog(0x00000007u, 0u, KErrNone);\n",
        "rendezvous return",
    )

    server_text = texts[server_path]
    server_text = replace_once(
        server_text,
        '#include "ssmdebug.h"\n',
        '#include "ssmdebug.h"\n\nvoid HtcleoSsmLog(TUint32 aStage, TUint32 aState, TInt aResult);\n',
        "server logger declaration",
    )
    server_text = replace_once(
        server_text,
        "\tstateResolver->GetStatePolicyL(initalState);\n",
        "\tstateResolver->GetStatePolicyL(initalState);\n"
        "\tconst TUint32 htcleoInitialState = ((TUint32)initalState.MainState() << 16) | initalState.SubState();\n"
        "\tHtcleoSsmLog(0x00000003u, htcleoInitialState, KErrNone);\n",
        "initial policy loaded",
    )
    server_text = replace_once(
        server_text,
        "\tiStateTransitionEngine = CSsmStateTransitionEngine::NewL(stateResolver, stateCleSession);\n",
        "\tiStateTransitionEngine = CSsmStateTransitionEngine::NewL(stateResolver, stateCleSession);\n"
        "\tHtcleoSsmLog(0x00000004u, htcleoInitialState, KErrNone);\n",
        "engine created",
    )
    server_text = replace_once(
        server_text,
        "\tiStateTransitionEngine->SubmitL(doStartup);\n",
        "\tiStateTransitionEngine->SubmitL(doStartup);\n"
        "\tHtcleoSsmLog(0x00000005u, htcleoInitialState, KErrNone);\n",
        "startup submitted",
    )

    engine_text = texts[engine_path]
    engine_text = replace_once(
        engine_text,
        '#include "ssmcommandlistutils.h"\n',
        '#include "ssmcommandlistutils.h"\n\nvoid HtcleoSsmLog(TUint32 aStage, TUint32 aState, TInt aResult);\n',
        "engine logger declaration",
    )
    engine_text = replace_once(
        engine_text,
        "void CSsmStateTransitionEngine::RunL()\n\t{\n",
        "void CSsmStateTransitionEngine::RunL()\n\t{\n"
        "\tconst TUint32 htcleoState = ((TUint32)iTargetSystemState.MainState() << 16) | iTargetSystemState.SubState();\n"
        "\tHtcleoSsmLog(0x10000000u | (TUint32)iNextAction, htcleoState, iStatus.Int());\n",
        "RunL record",
    )
    engine_text = replace_once(
        engine_text,
        "TInt CSsmStateTransitionEngine::RunError(TInt aError)\n\t{\n",
        "TInt CSsmStateTransitionEngine::RunError(TInt aError)\n\t{\n"
        "\tconst TUint32 htcleoState = ((TUint32)iTargetSystemState.MainState() << 16) | iTargetSystemState.SubState();\n"
        "\tHtcleoSsmLog(0xE0000000u | (TUint32)iNextAction, htcleoState, aError);\n",
        "RunError record",
    )
    engine_text = replace_once(
        engine_text,
        "\t\tiCleSession.ExecuteCommandList(*iCommandList, iStatus, iSeverity);\n\t\tSetActive();\n",
        "\t\tiCleSession.ExecuteCommandList(*iCommandList, iStatus, iSeverity);\n"
        "\t\tSetActive();\n"
        "\t\tconst TUint32 htcleoState = ((TUint32)iTargetSystemState.MainState() << 16) | iTargetSystemState.SubState();\n"
        "\t\tHtcleoSsmLog(0x20000005u, htcleoState, KErrNone);\n",
        "command list submitted",
    )

    verify(main_text, server_text, engine_text)
    main_path.write_text(main_text, encoding="utf-8")
    server_path.write_text(server_text, encoding="utf-8")
    engine_path.write_text(engine_text, encoding="utf-8")
    print("HTCLEO_SSM_DURABLE_LOG=installed checkpoints=fixed-01-07+runl+submit+fatal")


if __name__ == "__main__":
    main()
