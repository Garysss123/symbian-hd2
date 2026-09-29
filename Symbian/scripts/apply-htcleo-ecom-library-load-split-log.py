#!/usr/bin/env python3
"""Split the exact NVG ECom RLibrary load into attributable durable stages.

The stock RLibrary::Load implementation is reproduced only for the already
UID/name-gated nvgrenderstage.dll request.  Non-NVG requests retain the stock
single-call path.  This distinguishes loader IPC return from DLL Init/attach
without changing loader policy, retrying, delaying, or adding display output.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_LIBRARY_LOAD_SPLIT_V2"
OLD_MARKER = "HTCLEO_ECOM_LIBRARY_LOAD_SPLIT_V1"
STAGES = tuple(f"0x0000080{index:X}u" for index in range(1, 10))
OLD_STAGES = tuple(f"0x0000060{index:X}u" for index in range(1, 10))


OLD_BLOCK = r'''		if(htcleoNvg) HtcleoEcomLog(0x00000505u, KErrNone, (TUint32)iDllEntry->GetThirdUid().iUid);
		TInt htcleoLoadResult = iLibrary.Load(libraryPath, TUidType(KDynamicLibraryUid,iDllEntry->GetSecondUid(),iDllEntry->GetThirdUid()));
		if(htcleoNvg) HtcleoEcomLog(0x00000506u, htcleoLoadResult, (TUint32)iLibrary.Handle());'''


NEW_BLOCK = r'''		if(htcleoNvg) HtcleoEcomLog(0x00000505u, KErrNone, (TUint32)iDllEntry->GetThirdUid().iUid);
		TInt htcleoLoadResult = KErrNone;
		if(htcleoNvg)
			{
			// HTCLEO_ECOM_LIBRARY_LOAD_SPLIT_V2
			TInt htcleoHandle = 0;
			HtcleoEcomLog(0x00000801u, KErrNone, (TUint32)libraryPath.Length());
			RLoader htcleoLoader;
			TInt htcleoLoaderResult = htcleoLoader.Connect();
			HtcleoEcomLog(0x00000802u, htcleoLoaderResult, (TUint32)htcleoHandle);
			if(htcleoLoaderResult == KErrNone)
				{
				const TUidType htcleoType(KDynamicLibraryUid,
					iDllEntry->GetSecondUid(), iDllEntry->GetThirdUid());
				HtcleoEcomLog(0x00000803u, KErrNone,
					(TUint32)iDllEntry->GetThirdUid().iUid);
				htcleoLoaderResult = htcleoLoader.LoadLibrary(htcleoHandle,
					libraryPath, KNullDesC, htcleoType, KModuleVersionWild);
				HtcleoEcomLog(0x00000804u, htcleoLoaderResult,
					(TUint32)htcleoHandle);
				iLibrary.SetHandle(htcleoHandle);
				HtcleoEcomLog(0x00000805u, htcleoLoaderResult,
					(TUint32)iLibrary.Handle());
				htcleoLoader.Close();
				HtcleoEcomLog(0x00000806u, htcleoLoaderResult,
					(TUint32)iLibrary.Handle());
				htcleoLoadResult = htcleoLoaderResult;
				if(htcleoLoadResult == KErrNone)
					{
					HtcleoEcomLog(0x00000807u, KErrNone,
						(TUint32)iLibrary.Handle());
					htcleoLoadResult = iLibrary.Init();
					HtcleoEcomLog(0x00000808u, htcleoLoadResult,
						(TUint32)iLibrary.Handle());
					}
				}
			else
				{
				htcleoLoadResult = htcleoLoaderResult;
				}
			HtcleoEcomLog(0x00000809u, htcleoLoadResult,
				(TUint32)iLibrary.Handle());
			}
		else
			{
			htcleoLoadResult = iLibrary.Load(libraryPath,
				TUidType(KDynamicLibraryUid,iDllEntry->GetSecondUid(),iDllEntry->GetThirdUid()));
			}
		if(htcleoNvg) HtcleoEcomLog(0x00000506u, htcleoLoadResult, (TUint32)iLibrary.Handle());'''


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    checks = {
        "marker": text.count(MARKER) == 1,
        "loader private include": text.count("#include <e32ldr_private.h>") == 1,
        "constant private include": text.count("#include <e32const_private.h>") == 1,
        "nine split stages": all(text.count(stage) == 1 for stage in STAGES),
        "explicit loader call": text.count("htcleoLoader.LoadLibrary(htcleoHandle,") == 1,
        "explicit init call": (
            text.count("htcleoLoadResult = iLibrary.Init();") == 1
            or (
                text.count("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V1") == 1
                and text.count(
                    "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary);"
                ) == 1
            )
            or (
                text.count("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V2") == 1
                and text.count(
                    "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
                    "\t\t\t\t\t\thtcleoAttachTrace);"
                ) == 1
            )
            or (
                text.count("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V3") == 1
                and text.count(
                    "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
                    "\t\t\t\t\t\thtcleoAttachTrace);"
                ) == 1
            )
            or (
                text.count("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V4") == 1
                and text.count(
                    "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
                    "\t\t\t\t\t\thtcleoAttachTrace);"
                ) == 1
            )
            or (
                text.count("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V5") == 1
                and text.count(
                    "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
                    "\t\t\t\t\t\thtcleoAttachTrace);"
                ) == 1
            )
            or (
                text.count("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V6") == 1
                and text.count(
                    "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
                    "\t\t\t\t\t\thtcleoAttachTrace);"
                ) == 1
            )
        ),
        "stock non-NVG path": text.count("htcleoLoadResult = iLibrary.Load(libraryPath,") == 1,
        "no delay": "User::After" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("ECom load-split verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    path = (
        args.root
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/UnloadPolicy.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing ECom source: {path}")

    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        verify(path)
        print("HTCLEO_ECOM_LIBRARY_LOAD_SPLIT=installed stages=0801-0809")
        return

    if OLD_MARKER in text:
        start = text.index(OLD_MARKER)
        begin = text.rfind("\t\tTInt htcleoLoadResult = KErrNone;", 0, start)
        end = text.index(
            "\t\tif(htcleoNvg) HtcleoEcomLog(0x00000506u", start
        )
        if begin < 0 or end <= begin:
            raise SystemExit("cannot isolate installed V1 ECom load-split block")
        block = text[begin:end].replace(OLD_MARKER, MARKER, 1)
        for old_stage, new_stage in zip(OLD_STAGES, STAGES):
            if block.count(old_stage) != 1:
                raise SystemExit(f"installed V1 stage is not unique: {old_stage}")
            block = block.replace(old_stage, new_stage, 1)
        text = text[:begin] + block + text[end:]
        path.write_text(text, encoding="utf-8")
        verify(path)
        print("HTCLEO_ECOM_LIBRARY_LOAD_SPLIT=installed stages=0801-0809")
        return

    include_anchor = '#include "HtcleoEcomLog.h"\n'
    if text.count(include_anchor) != 1:
        raise SystemExit("ECom load-split include anchor is not unique")
    if text.count(OLD_BLOCK) != 1:
        raise SystemExit(
            f"ECom load-split body anchor expected once, found {text.count(OLD_BLOCK)}"
        )

    text = text.replace(
        include_anchor,
        include_anchor + "#include <e32ldr_private.h>\n#include <e32const_private.h>\n",
        1,
    )
    text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
    path.write_text(text, encoding="utf-8")
    verify(path)
    print("HTCLEO_ECOM_LIBRARY_LOAD_SPLIT=installed stages=0801-0809")


if __name__ == "__main__":
    main()
