#!/usr/bin/env python3
"""Install fail-open HTCLEO NVG render-stage startup logging.

The NVG ECom plug-in runs inside EWSRV.  It is the sole writer of
``C:\\Symbian3\\NVGLOG.TXT`` and records completed loader/factory/render-stage
boundaries without changing the selected render-stage chain.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


OLD_MARKER = "HTCLEO_NVG_DURABLE_LOG_V1"
MARKER = "HTCLEO_NVG_DURABLE_LOG_V2"
MACRO = "__HTCLEO_NVG_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def durable_logger() -> str:
    return r'''
#ifdef __HTCLEO_NVG_DURABLE_LOG__
// HTCLEO_NVG_DURABLE_LOG_V2
void HtcleoNvgLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                         __attribute__((noinline));

void HtcleoNvgLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoNvgLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoNvgLogPath, "C:\\Symbian3\\NVGLOG.TXT");
	r = fs.MkDirAll(KHtcleoNvgLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoNvgLogPath, EFileWrite | EFileShareAny);
	if(r == KErrNotFound || r == KErrPathNotFound)
		{
		r = file.Replace(fs, KHtcleoNvgLogPath, EFileWrite | EFileShareAny);
		}
	else if(r == KErrNone)
		{
		r = file.Seek(ESeekEnd, position);
		}

	// Every record below is exactly 42 bytes.  Deriving the sequence from the
	// append offset avoids writable DLL globals, which E32Image rejects.
	if(r == KErrNone && position < (64 * 42))
		{
		_LIT8(KHtcleoNvgPrefix, "HTCLEO_NVG ");
		TBuf8<64> record;
		record.Append(KHtcleoNvgPrefix);
		record.AppendNumFixedWidth((TUint)(position / 42), EHex, 2);
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
		}

	file.Close();
	fs.Close();
	}
#else
void HtcleoNvgLog(TUint32, TInt, TUint32) {}
#endif

'''


def verify(plugin: str, factory: str, stage: str, mmp: str) -> None:
    expected = (
        "0x00000001u", "0x00000002u",
        "0x00000010u", "0x00000011u",
        "0x00000020u", "0x00000021u",
        "0xE0000020u", "0x00000030u", "0x00000031u",
        "0x00000040u", "0x00000041u", "0x00000042u", "0x00000043u",
        "0x00000050u", "0x00000051u", "0x00000052u", "0x00000053u",
        "0x00000054u", "0x00000055u", "0x00000056u", "0x00000057u",
        "0x00000058u",
    )
    combined = plugin + factory + stage
    checks = {
        "marker": plugin.count(MARKER) == 1,
        "macro": mmp.count(f"MACRO\t\t{MACRO}") == 1,
        "efsrv": mmp.count("LIBRARY\tefsrv.lib") == 1,
        "one writer path": combined.count("C:\\\\Symbian3\\\\NVGLOG.TXT") == 1,
        "record prefix": combined.count("HTCLEO_NVG ") == 1,
        "logger definition": plugin.count("void HtcleoNvgLog(") == 3,
        "logger declarations": factory.count("void HtcleoNvgLog(") == 2
        and stage.count("void HtcleoNvgLog(") == 2,
        "write and flush": plugin.count("file.Write(record)") == 1
        and plugin.count("file.Flush()") == 1,
        "no writable globals": "gHtcleoNvgLog" not in plugin,
        "all stages": all(combined.count(value) == 1 for value in expected),
        "no delay": "User::After" not in combined,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("NVG durable-log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    component = args.root / "sf/mw/uiresources/uigraphics/NVGRenderStage"
    plugin_path = component / "src/nvgrenderstageplugin.cpp"
    factory_path = component / "src/nvgrenderstagefactory.cpp"
    stage_path = component / "src/nvgrenderstage.cpp"
    mmp_path = component / "group/nvgrenderstage.mmp"
    for path in (plugin_path, factory_path, stage_path, mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing NVGRenderStage source: {path}")

    plugin = plugin_path.read_text(encoding="utf-8")
    factory = factory_path.read_text(encoding="utf-8")
    stage = stage_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")

    logger = durable_logger()
    if OLD_MARKER in plugin:
        plugin, count = re.subn(
            rf'#ifdef {re.escape(MACRO)}\n// {OLD_MARKER}.*?#endif\n\n',
            lambda _match: logger,
            plugin,
            count=1,
            flags=re.DOTALL,
        )
        if count != 1:
            raise SystemExit(f"legacy logger upgrade: expected one block, found {count}")
        verify(plugin, factory, stage, mmp)
        plugin_path.write_text(plugin, encoding="utf-8")
        print("HTCLEO_NVG_DURABLE_LOG=upgraded-v2 checkpoints=22 path=C:\\Symbian3\\NVGLOG.TXT")
        return

    if MARKER in plugin:
        verify(plugin, factory, stage, mmp)
        print("HTCLEO_NVG_DURABLE_LOG=installed checkpoints=22 path=C:\\Symbian3\\NVGLOG.TXT")
        return

    plugin = replace_once(
        plugin,
        '#include <ecom/implementationproxy.h>\n',
        '#include <ecom/implementationproxy.h>\n'
        f'#ifdef {MACRO}\n#include <f32file.h>\n#endif\n',
        "logger include",
    )

    plugin = replace_once(
        plugin,
        '#include "nvgrenderstagefactory.h"\n\n',
        '#include "nvgrenderstagefactory.h"\n' + logger,
        "logger body",
    )
    plugin = replace_once(
        plugin,
        '\t{\n\tRDebug::Printf("nvgrenderstage - ImplementationGroupProxy called\\n");\n'
        '\taTableCount = (sizeof(KImplementationTable) / sizeof(TImplementationProxy));\n'
        '\treturn KImplementationTable;\n\t}\n',
        '\t{\n\tHtcleoNvgLog(0x00000001u, KErrNone, 0u);\n'
        '\tRDebug::Printf("nvgrenderstage - ImplementationGroupProxy called\\n");\n'
        '\taTableCount = (sizeof(KImplementationTable) / sizeof(TImplementationProxy));\n'
        '\tHtcleoNvgLog(0x00000002u, KErrNone, (TUint32)aTableCount);\n'
        '\treturn KImplementationTable;\n\t}\n',
        "implementation proxy stages",
    )

    declaration = f'''\n#ifdef {MACRO}\nvoid HtcleoNvgLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n#else\nstatic inline void HtcleoNvgLog(TUint32, TInt, TUint32) {{}}\n#endif\n'''
    factory = replace_once(
        factory,
        '#include "nvgrenderstagepanic.h"\n',
        '#include "nvgrenderstagepanic.h"\n' + declaration,
        "factory logger declaration",
    )
    factory = replace_once(
        factory,
        'CNvgRenderStageFactory* CNvgRenderStageFactory::CreateL()\n\t{\n'
        '\treturn new(ELeave) CNvgRenderStageFactory;\n\t}\n',
        'CNvgRenderStageFactory* CNvgRenderStageFactory::CreateL()\n\t{\n'
        '\tHtcleoNvgLog(0x00000010u, KErrNone, 0u);\n'
        '\tCNvgRenderStageFactory* factory = new(ELeave) CNvgRenderStageFactory;\n'
        '\tHtcleoNvgLog(0x00000011u, KErrNone, (TUint32)(factory != NULL));\n'
        '\treturn factory;\n\t}\n',
        "factory allocation",
    )
    factory = replace_once(
        factory,
        '\t{\n\tBaseConstructL(aEnv);\n\t}\n',
        '\t{\n\tHtcleoNvgLog(0x00000020u, KErrNone, 0u);\n'
        '\tBaseConstructL(aEnv);\n'
        '\tHtcleoNvgLog(0x00000021u, KErrNone, 0u);\n\t}\n',
        "factory construction",
    )
    factory = replace_once(
        factory,
        '\t{\t\n\tPanic(EExtendedBitmapRenderStageMustNotBeFinal);\n',
        '\t{\t\n\tHtcleoNvgLog(0xE0000020u, KErrNotSupported, 0u);\n'
        '\tPanic(EExtendedBitmapRenderStageMustNotBeFinal);\n',
        "invalid final-stage path",
    )
    factory = replace_once(
        factory,
        '\t{\n\tCNvgRenderStage* stage = CNvgRenderStage::NewL(&Env(), aScreen, aScreenRedraw, aNextStage);\n'
        '\treturn stage;\n\t}\n',
        '\t{\n\tHtcleoNvgLog(0x00000030u, KErrNone, (TUint32)(aNextStage != NULL));\n'
        '\tCNvgRenderStage* stage = CNvgRenderStage::NewL(&Env(), aScreen, aScreenRedraw, aNextStage);\n'
        '\tHtcleoNvgLog(0x00000031u, KErrNone, (TUint32)(stage != NULL));\n'
        '\treturn stage;\n\t}\n',
        "render-stage factory path",
    )

    stage = replace_once(
        stage,
        '#include <AknIconUtils.h>\n',
        '#include <AknIconUtils.h>\n' + declaration,
        "stage logger declaration",
    )
    stage = replace_once(
        stage,
        '\t{\n\tCNvgRenderStage* stage = new(ELeave) CNvgRenderStage();\n'
        '\tCleanupStack::PushL(stage);\n\tstage->ConstructL(aNextStage);\n'
        '\tCleanupStack::Pop(stage);\n\treturn stage;\n\t}\n',
        '\t{\n\tHtcleoNvgLog(0x00000040u, KErrNone, (TUint32)(aNextStage != NULL));\n'
        '\tCNvgRenderStage* stage = new(ELeave) CNvgRenderStage();\n'
        '\tHtcleoNvgLog(0x00000041u, KErrNone, (TUint32)(stage != NULL));\n'
        '\tCleanupStack::PushL(stage);\n\tstage->ConstructL(aNextStage);\n'
        '\tHtcleoNvgLog(0x00000042u, KErrNone, 0u);\n'
        '\tCleanupStack::Pop(stage);\n'
        '\tHtcleoNvgLog(0x00000043u, KErrNone, (TUint32)(stage != NULL));\n'
        '\treturn stage;\n\t}\n',
        "render-stage NewL path",
    )
    stage = replace_once(
        stage,
        '\t{\n\tiBrushPattern = new(ELeave) CFbsBitmap;\n'
        '\tiInternalBrushPattern = new(ELeave) CFbsBitmap;\n'
        '\tiGraphicsInterface = new(ELeave) CVGIGraphicsInterface;\n'
        '  iNvgEngine = CNvgEngine::NewL();\n'
        '  iNvgEngine->SetVGImageBinder(iGraphicsInterface);\n\t\n'
        '\tBaseConstructL();\t\n\tSetNext(aNextStage);\n\t}\n',
        '\t{\n\tHtcleoNvgLog(0x00000050u, KErrNone, 0u);\n'
        '\tiBrushPattern = new(ELeave) CFbsBitmap;\n'
        '\tHtcleoNvgLog(0x00000051u, KErrNone, 1u);\n'
        '\tiInternalBrushPattern = new(ELeave) CFbsBitmap;\n'
        '\tHtcleoNvgLog(0x00000052u, KErrNone, 1u);\n'
        '\tiGraphicsInterface = new(ELeave) CVGIGraphicsInterface;\n'
        '\tHtcleoNvgLog(0x00000053u, KErrNone, 1u);\n'
        '  iNvgEngine = CNvgEngine::NewL();\n'
        '\tHtcleoNvgLog(0x00000054u, KErrNone, (TUint32)(iNvgEngine != NULL));\n'
        '  iNvgEngine->SetVGImageBinder(iGraphicsInterface);\n'
        '\tHtcleoNvgLog(0x00000055u, KErrNone, 0u);\n\t\n'
        '\tBaseConstructL();\t\n'
        '\tHtcleoNvgLog(0x00000056u, KErrNone, 0u);\n'
        '\tSetNext(aNextStage);\n'
        '\tHtcleoNvgLog(0x00000057u, KErrNone, (TUint32)(aNextStage != NULL));\n'
        '\tHtcleoNvgLog(0x00000058u, KErrNone, 0u);\n\t}\n',
        "render-stage construction path",
    )

    mmp = replace_once(
        mmp,
        'MACRO\t\tSYMBIAN_GRAPHICS_GCE\n',
        'MACRO\t\tSYMBIAN_GRAPHICS_GCE\n'
        f'MACRO\t\t{MACRO}\n',
        "target macro",
    )
    mmp = replace_once(
        mmp,
        'LIBRARY\teuser.lib\n',
        'LIBRARY\teuser.lib\nLIBRARY\tefsrv.lib\n',
        "file-server import",
    )

    verify(plugin, factory, stage, mmp)
    plugin_path.write_text(plugin, encoding="utf-8")
    factory_path.write_text(factory, encoding="utf-8")
    stage_path.write_text(stage, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print("HTCLEO_NVG_DURABLE_LOG=installed checkpoints=22 path=C:\\Symbian3\\NVGLOG.TXT")


if __name__ == "__main__":
    main()
