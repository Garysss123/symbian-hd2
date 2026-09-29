#!/usr/bin/env python3
"""Trace the exact Akn custom-command RLibrary::Init sequence durably.

Iteration 435 proved that RLoader::LoadLibrary returned successfully, the
library handle was published and the loader session closed, then stopped at
the boundary immediately before RLibrary::Init.  For that already
filename/ordinal-gated command only, reproduce stock ARM RLibrary::InitL and
reuse the proven kernel LibraryAttach notify/flush/ack protocol.  All other
custom-command loads retain their stock path.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import runpy


MARKER = "HTCLEO_AKN_CUSTOM_COMMAND_LIBRARY_INIT_ENTRYPOINT_LOG_V1"
MACRO = "__HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG__"
HELPER_ANCHOR = "static TBool HtcleoIsAknStartCommand"
TRACE_DECL_ANCHOR = "\t\t\tTInt htcleoHandle = 0;\n"
CALL_ANCHOR = "\t\t\t\t\terr = iLibrary.Init();"
STOP_ANCHOR = "\t\t\tHtcleoCustomCmdLog(0x0000C108u, err,\n"


def make_helper() -> str:
    """Retarget the already hardware-proven ECom V6 helper exactly once."""

    ecom_transform = Path(__file__).with_name(
        "apply-htcleo-ecom-library-init-entrypoint-log.py"
    )
    if not ecom_transform.is_file():
        raise SystemExit(f"missing proven ECom helper source: {ecom_transform}")
    helper = runpy.run_path(str(ecom_transform))["HELPER"]
    replacements = [
        ("HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V6", MARKER),
        ("HtcleoNvg", "HtcleoAkn"),
        ("KHtcleoAttach", "KHtcleoAknAttach"),
        ("HtcleoEcomLog", "HtcleoCustomCmdLog"),
        ("ECOMLOG", "CUSTLOG"),
    ]
    replacements.extend(
        (f"0x0000090{index:X}u", f"0x0000C20{index:X}u")
        for index in range(1, 10)
    )
    replacements.extend(
        [
            ("0x00000910u", "0x0000C210u"),
            ("0x00000911u", "0x0000C211u"),
            ("0x00000a00u", "0x0000CA00u"),
            ("0x00000a01u", "0x0000CA01u"),
            ("0x00000a02u", "0x0000CA02u"),
            ("0x00000a03u", "0x0000CA03u"),
            ("0x00000a05u", "0x0000CA05u"),
            ("0x00000a10u + step", "0x0000CA10u + step"),
            ("0x0000b000u", "0x0000CB00u"),
            ("0x0000b006u", "0x0000CB06u"),
            ("0x0000b100u + (TUint32)phase", "0x0000CB10u + (TUint32)phase"),
            ("0x0000b200u + (TUint32)phase", "0x0000CB20u + (TUint32)phase"),
        ]
    )
    for old, new in replacements:
        if old not in helper:
            raise SystemExit(f"proven helper retarget anchor missing: {old}")
        helper = helper.replace(old, new)
    return f"#ifdef {MACRO}\n{helper}#endif\n\n"


HELPER = make_helper()


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    fixed_init_stages = tuple(f"0x0000C20{index:X}u" for index in range(1, 10))
    checks = {
        "marker": text.count(MARKER) == 1,
        "panic include": text.count("#include <e32panic.h>") == 1,
        "exec enum include": text.count("#include <exec_enum.h>") == 1,
        "module reason include": text.count("#include <u32std.h>") == 1,
        "fixed init stages": all(text.count(stage) == 1 for stage in fixed_init_stages),
        "entrypoint stages": text.count("0x0000C210u") == 1
        and text.count("0x0000C211u") == 1,
        "attach exec": text.count("HtcleoAknLibraryAttachExec") == 4,
        "attached exec": text.count("HtcleoAknLibraryAttachedExec") == 3,
        "thumb entry ARM SWI veneers": text.count('asm("bx pc")') == 2
        and text.count('asm("nop")') == 2
        and text.count('asm(".code 32")') == 2
        and text.count('asm(".code 16")') == 2,
        "exact init helper call": text.count(
            "err = HtcleoAknLibraryInit(iLibrary,\n"
            "\t\t\t\t\t\thtcleoAttachTrace);"
        ) == 1,
        "watcher start": text.count("HtcleoAknAttachTraceStart(") == 2,
        "watcher stop": text.count("HtcleoAknAttachTraceStop(") == 4,
        "watcher thread": text.count("HtcleoAknAttachWatchThread") == 2,
        "watcher create": text.count("iThread.Create(") == 1,
        "watcher low priority": text.count(
            "iThread.SetPriority(EPriorityMuchLess)"
        ) == 1,
        "watcher rendezvous": text.count("RThread::Rendezvous(KErrNone)") == 1,
        "kernel notify semaphore": text.count("iKernelNotify.CreateLocal(0)") == 1
        and text.count("iKernelNotify.Wait()") == 1
        and text.count("iKernelNotify.Signal()") == 1
        and text.count("iKernelNotify.Handle()") == 1,
        "kernel ack semaphore": text.count("iKernelAck.CreateLocal(0)") == 1
        and text.count("iKernelAck.Signal()") == 1
        and text.count("iKernelAck.Handle()") == 1,
        "watcher fixed stages": all(
            text.count(f"0x0000CA0{stage}u") == (2 if stage == 3 else 1)
            for stage in range(5)
        ),
        "watcher anomaly": text.count("0x0000CA05u") == 2,
        "watcher dynamic stage": text.count("0x0000CA10u + step") == 1,
        "bootstrap constants": text.count("0x42000100u") == 1
        and text.count("0xa0b60000u") == 1,
        "bootstrap fixed stages": text.count("0x0000CB00u") == 1
        and text.count("0x0000CB06u") == 1,
        "bootstrap dynamic stages": text.count(
            "0x0000CB10u + (TUint32)phase"
        ) == 1
        and text.count("0x0000CB20u + (TUint32)phase") == 1
        and text.count("phase <= 6") == 1,
        "six bootstrap attach calls": text.count("HtcleoAknAttachBootstrap(") == 2,
        "exact trace flag": text.count("0x40000000u") == 1,
        "exact trace magic": text.count("0x484c3432u") == 1,
        "259-word buffer": text.count(
            "sizeof(TLinAddr) * (KMaxLibraryEntryPoints + 3)"
        ) == 1,
        "stock init only non-ARM fallback": text.count("return aLibrary.Init();") == 1,
        "direct stock init removed": text.count("err = iLibrary.Init();") == 0,
        "trace starts before loader": text.index("HtcleoAknAttachTraceStart(", text.index("void CCmdCustomCommand::PrepareCustomCmdL"))
        < text.index("htcleoLoader.Connect()", text.index("void CCmdCustomCommand::PrepareCustomCmdL")),
        "abort stop at branch merge": text.count(
            "HtcleoAknAttachTraceStop(htcleoAttachTrace,\n"
            "\t\t\t\tKHtcleoAknAttachTraceAbort);"
        ) == 1,
        "two bounded watcher waits": text.count("User::WaitForRequest(") == 2,
        "no delay": "User::After" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Akn custom-command init/entrypoint verification failed: "
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
        print(
            "HTCLEO_AKN_CUSTOM_COMMAND_INIT_TRACE=installed "
            "stages=C201-C211,CA00-CA1A,CB00-CB26 bootstrap=6 "
            "handoff=notify-ack"
        )
        return

    if text.count("HTCLEO_AKN_CUSTOM_COMMAND_LIBRARY_LOAD_SPLIT_V1") != 1:
        raise SystemExit("Akn custom-command load split must be installed first")
    include_anchor = "#include <e32const_private.h>\n"
    if text.count(include_anchor) != 1:
        raise SystemExit("Akn init-trace include anchor is not unique")
    if text.count(HELPER_ANCHOR) != 1:
        raise SystemExit("Akn init-trace helper anchor is not unique")
    if text.count(TRACE_DECL_ANCHOR) != 1:
        raise SystemExit("Akn init-trace declaration anchor is not unique")
    if text.count(CALL_ANCHOR) != 1:
        raise SystemExit("Akn init-trace call anchor is not unique")
    if text.count(STOP_ANCHOR) != 1:
        raise SystemExit("Akn init-trace stop anchor is not unique")

    text = text.replace(
        include_anchor,
        include_anchor
        + "#include <e32panic.h>\n#include <exec_enum.h>\n#include <u32std.h>\n",
        1,
    )
    text = text.replace(HELPER_ANCHOR, HELPER + HELPER_ANCHOR, 1)
    text = text.replace(
        TRACE_DECL_ANCHOR,
        "\t\t\tTHtcleoAknAttachTrace htcleoAttachTrace;\n"
        "\t\t\tconst TInt htcleoTraceStartResult =\n"
        "\t\t\t\tHtcleoAknAttachTraceStart(htcleoAttachTrace);\n"
        "\t\t\tHtcleoCustomCmdLog(0x0000CA04u, htcleoTraceStartResult, 0u);\n"
        + TRACE_DECL_ANCHOR,
        1,
    )
    text = text.replace(
        CALL_ANCHOR,
        "\t\t\t\t\terr = HtcleoAknLibraryInit(iLibrary,\n"
        "\t\t\t\t\t\thtcleoAttachTrace);",
        1,
    )
    text = text.replace(
        STOP_ANCHOR,
        "\t\t\tHtcleoAknAttachTraceStop(htcleoAttachTrace,\n"
        "\t\t\t\tKHtcleoAknAttachTraceAbort);\n"
        + STOP_ANCHOR,
        1,
    )
    path.write_text(text, encoding="utf-8", newline="\n")
    verify(path)
    print(
        "HTCLEO_AKN_CUSTOM_COMMAND_INIT_TRACE=installed "
        "stages=C201-C211,CA00-CA1A,CB00-CB26 bootstrap=6 "
        "handoff=notify-ack"
    )


if __name__ == "__main__":
    main()
