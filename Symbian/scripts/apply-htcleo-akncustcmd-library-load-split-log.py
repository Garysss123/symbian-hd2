#!/usr/bin/env python3
"""Split the exact Akn custom-command RLibrary load into durable stages.

Iteration 434 proved that EFILE completed the exact akncustcmds.dll request,
all recursive imports, RLdrReq cleanup and client message completion, while
the stock RLibrary::Load caller still did not reach its post-call checkpoint.
For that already filename/ordinal-gated command only, reproduce the stock
RLibrary::Load order so loader IPC return can be distinguished from
RLibrary::Init/process attach.  All other custom-command loads retain their
original single RLibrary::Load call.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKN_CUSTOM_COMMAND_LIBRARY_LOAD_SPLIT_V1"
INIT_TRACE_MARKER = "HTCLEO_AKN_CUSTOM_COMMAND_LIBRARY_INIT_ENTRYPOINT_LOG_V1"
MACRO = "__HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG__"
STAGES = tuple(f"0x0000C10{index:X}u" for index in range(9))

INCLUDE_ANCHOR = "#include <s32file.h>\n"
PRIVATE_INCLUDES = f"""\
#include <s32file.h>
#ifdef {MACRO}
#include <e32ldr_private.h>
#include <e32const_private.h>
#endif
"""

OLD_BLOCK = """\
\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C012u, KErrNone, 0u);
\t\terr = iLibrary.Load(iInfo->FileName());
\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C013u, err, (TUint32)iLibrary.Handle());
"""

NEW_BLOCK = f"""\
\t\tconst TBool htcleoAknLoadTrace = HtcleoIsAknStartCommand(iInfo);
\t\tif(htcleoAknLoadTrace) HtcleoCustomCmdLog(0x0000C012u, KErrNone, 0u);
#ifdef {MACRO}
\t\tif(htcleoAknLoadTrace)
\t\t\t{{
\t\t\t// {MARKER}
\t\t\tTInt htcleoHandle = 0;
\t\t\tHtcleoCustomCmdLog(0x0000C100u, KErrNone,
\t\t\t\t(TUint32)iInfo->FileName().Length());
\t\t\tRLoader htcleoLoader;
\t\t\tTInt htcleoLoaderResult = htcleoLoader.Connect();
\t\t\tHtcleoCustomCmdLog(0x0000C101u, htcleoLoaderResult,
\t\t\t\t(TUint32)htcleoHandle);
\t\t\tif(htcleoLoaderResult == KErrNone)
\t\t\t\t{{
\t\t\t\tHtcleoCustomCmdLog(0x0000C102u, KErrNone,
\t\t\t\t\t(TUint32)KModuleVersionWild);
\t\t\t\thtcleoLoaderResult = htcleoLoader.LoadLibrary(htcleoHandle,
\t\t\t\t\tiInfo->FileName(), KNullDesC, TUidType(),
\t\t\t\t\tKModuleVersionWild);
\t\t\t\tHtcleoCustomCmdLog(0x0000C103u, htcleoLoaderResult,
\t\t\t\t\t(TUint32)htcleoHandle);
\t\t\t\tiLibrary.SetHandle(htcleoHandle);
\t\t\t\tHtcleoCustomCmdLog(0x0000C104u, htcleoLoaderResult,
\t\t\t\t\t(TUint32)iLibrary.Handle());
\t\t\t\thtcleoLoader.Close();
\t\t\t\tHtcleoCustomCmdLog(0x0000C105u, htcleoLoaderResult,
\t\t\t\t\t(TUint32)iLibrary.Handle());
\t\t\t\terr = htcleoLoaderResult;
\t\t\t\tif(err == KErrNone)
\t\t\t\t\t{{
\t\t\t\t\tHtcleoCustomCmdLog(0x0000C106u, KErrNone,
\t\t\t\t\t\t(TUint32)iLibrary.Handle());
\t\t\t\t\terr = iLibrary.Init();
\t\t\t\t\tHtcleoCustomCmdLog(0x0000C107u, err,
\t\t\t\t\t\t(TUint32)iLibrary.Handle());
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\telse
\t\t\t\t{{
\t\t\t\terr = htcleoLoaderResult;
\t\t\t\t}}
\t\t\tHtcleoCustomCmdLog(0x0000C108u, err,
\t\t\t\t(TUint32)iLibrary.Handle());
\t\t\t}}
\t\telse
\t\t\t{{
\t\t\terr = iLibrary.Load(iInfo->FileName());
\t\t\t}}
#else
\t\terr = iLibrary.Load(iInfo->FileName());
#endif
\t\tif(htcleoAknLoadTrace) HtcleoCustomCmdLog(0x0000C013u, err, (TUint32)iLibrary.Handle());
"""


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    checks = {
        "marker": text.count(MARKER) == 1,
        "private loader include": text.count("#include <e32ldr_private.h>") == 1,
        "private constants include": text.count("#include <e32const_private.h>") == 1,
        "nine split stages": all(text.count(stage) == 1 for stage in STAGES),
        "exact loader call": text.count(
            "htcleoLoader.LoadLibrary(htcleoHandle,"
        ) == 1,
        "exact init path": (
            text.count("err = iLibrary.Init();") == 0
            and text.count("err = HtcleoAknLibraryInit(iLibrary,") == 1
        ) if INIT_TRACE_MARKER in text else text.count("err = iLibrary.Init();") == 1,
        "stock non-Akn path": text.count(
            "err = iLibrary.Load(iInfo->FileName());"
        ) == 2,
        "existing caller boundaries":
            text.count("0x0000C012u") == 1
            and text.count("0x0000C013u") == 1,
        "no delay and only traced watcher waits":
            "User::After" not in text
            and (
                text.count("User::WaitForRequest(") == 2
                if INIT_TRACE_MARKER in text
                else "User::WaitForRequest" not in text
            ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Akn custom-command load-split verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    path = (
        args.root
        / "sf/os/devicesrv/sysstatemgmt/systemstatemgr/cmd"
        / "src/cmdcustomcommand.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing custom-command source: {path}")

    text = path.read_text(encoding="utf-8").replace("\r", "")
    if MARKER in text:
        verify(path)
        print("HTCLEO_AKN_CUSTOM_COMMAND_LOAD_SPLIT=installed stages=C100-C108")
        return

    if text.count("HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG_V1") != 1:
        raise SystemExit("custom-command durable logger must be installed first")
    if text.count(INCLUDE_ANCHOR) != 1:
        raise SystemExit("private include anchor is not unique")
    if text.count(OLD_BLOCK) != 1:
        raise SystemExit(
            f"load-split body anchor expected once, found {text.count(OLD_BLOCK)}"
        )

    text = text.replace(INCLUDE_ANCHOR, PRIVATE_INCLUDES, 1)
    text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    verify(path)
    print("HTCLEO_AKN_CUSTOM_COMMAND_LOAD_SPLIT=installed stages=C100-C108")


if __name__ == "__main__":
    main()
