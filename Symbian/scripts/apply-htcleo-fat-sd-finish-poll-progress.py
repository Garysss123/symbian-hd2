#!/usr/bin/env python3
"""Trace the exact tagged read from its first CMD13 result to SD completion.

Iteration 383 proved that CMD18 and the first CMD13 finish poll both return
KMMCErrNone.  V24 retires FF01-FF0A screen calls while preserving the exact
request/session attribution up to phase 16.  F101-F10A then distinguish the
first R1 state, the bounded synchronous ProgramTimerSM retry and the second
CMD13 result.  No reporter executes while a data command is active.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_SD_FINISH_POLL_PROGRESS_V24"
SDCC_MARKER = "HTCLEO_FAT_SD_FINISH_POLL_SDCC_PROGRESS_V24"
V25_MARKER = "HTCLEO_SD_EXPLICIT_STOP_PROGRESS_V25"
V26_MARKER = "HTCLEO_FAT_POST_STOP_RETURN_PROGRESS_V26"
V23_MARKER = "HTCLEO_FAT_SDCC_COMPLETION_PROGRESS_V23"
V23_SDCC_MARKER = "HTCLEO_FAT_SDCC_COMPLETION_SDCC_PROGRESS_V23"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transform_header(text: str) -> str:
    anchor = (
        f"\t/* {V23_MARKER}: phases 10-19 cover post-launch completion only. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor +
        f"\t/* {MARKER}: phases 20-28 trace the first SD finish-poll retry. */\n",
        "V24 session marker",
    )


def retire_ff_medmmc(text: str) -> str:
    callback = (
        "\tif (md.iSession && md.iSession->HtcleoFatPhysicalReadTraceAt(18u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xff090000u |\n"
        "\t\t\t(TUint32(md.iSession->EpocErrorCode()) & 0xffffu));\n"
        "\t\tmd.iSession->HtcleoAdvanceFatPhysicalReadTrace(19u);\n"
        "\t\t}\n"
    )
    text = replace_once(text, callback, "", "retire FF09")
    dfc = (
        "\t\tif (iSession->HtcleoFatPhysicalReadTraceAt(19u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xff0a0000u |\n"
        "\t\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n"
    )
    return replace_once(text, dfc, "", "retire FF0A")


def retire_ff_stack(text: str) -> str:
    blocks = (
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(11u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff020000u |\n"
            "\t\t\t\t(TUint32(err) & 0xffffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(12u);\n"
            "\t\t\t}\n",
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(11u))\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(12u);\n",
            "FF02",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(12u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff030000u |\n"
            "\t\t\t\t(TUint32(exitCode) & 0xffffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(13u);\n"
            "\t\t\t}\n",
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(12u))\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(13u);\n",
            "FF03",
        ),
        (
            "\t\t/* HTCLEO_FF04_LOCAL_STAGE_V23 */\n"
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(13u))\n"
            "\t\t\t{\n"
            "\t\t\tTUint32 htcleoProgress = TUint32(err) & 0xffffu;\n"
            "\t\t\tasm volatile(\"orr %0,%0,#0xff000000\\n\\t\"\n"
            "\t\t\t\t\"orr %0,%0,#0x00040000\"\n"
            "\t\t\t\t: \"+r\"(htcleoProgress) : : \"memory\");\n"
            "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(htcleoProgress);\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(14u);\n"
            "\t\t\t}\n",
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(13u))\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(14u);\n",
            "FF04",
        ),
        (
            "\tif (iSessionP->HtcleoFatPhysicalReadTraceAt(17u))\n"
            "\t\t{\n"
            "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff080000u |\n"
            "\t\t\t(TUint32(exitCode) & 0xffffu));\n"
            "\t\tiSessionP->HtcleoAdvanceFatPhysicalReadTrace(18u);\n"
            "\t\t}\n",
            "",
            "FF08",
        ),
    )
    for old, new, label in blocks:
        text = replace_once(text, old, new, f"retire {label}")
    return text


def transform_program_timer(text: str) -> str:
    session_anchor = (
        "#if defined(__EPOC32__) && !defined(__HTCLEO_MMC_SYNC_SESSION_TIMERS__)\n"
        "\tDMMCSession &s = Session();\n"
        "\tOstTrace1( TRACE_INTERNALS, DMMCSTACK_PROGRAMTIMERSM1, \"Current session=0x%x\", &s );\n"
        "#endif\n"
    )
    session_replacement = (
        "#ifdef __EPOC32__\n"
        "\tDMMCSession &s = Session();\n"
        "#if !defined(__HTCLEO_MMC_SYNC_SESSION_TIMERS__)\n"
        "\tOstTrace1( TRACE_INTERNALS, DMMCSTACK_PROGRAMTIMERSM1, \"Current session=0x%x\", &s );\n"
        "#endif\n"
        "#endif\n"
    )
    text = replace_once(text, session_anchor, session_replacement,
                        "ProgramTimer session access")
    sync_anchor = (
        "\t\t// HTCLEO reports a 1 ms program period. Preserve that bounded delay\n"
        "\t\t// without depending on the same non-resuming NTimer/DFC path.\n"
        "\t\tKern::NanoWait(ProgramPeriodInMilliSeconds() * 1000000u);\n"
    )
    sync_replacement = (
        "\t\t// HTCLEO reports a 1 ms program period. Preserve that bounded delay\n"
        "\t\t// without depending on the same non-resuming NTimer/DFC path.\n"
        "\t\tconst TUint32 htcleoProgramPeriod = ProgramPeriodInMilliSeconds();\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(24u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xf1060000u |\n"
        "\t\t\t\t(htcleoProgramPeriod & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(25u);\n"
        "\t\t\t}\n"
        "\t\tKern::NanoWait(htcleoProgramPeriod * 1000000u);\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(25u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xf1070000u |\n"
        "\t\t\t\t(htcleoProgramPeriod & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(26u);\n"
        "\t\t\t}\n"
    )
    return replace_once(text, sync_anchor, sync_replacement,
                        "F106/F107 synchronous ProgramTimer")


def retire_and_transform_sdcard(text: str) -> str:
    ff05 = (
        "\t\t/* HTCLEO_FF05_LOCAL_STAGE_V23 */\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(14u))\n"
        "\t\t\t{\n"
        "\t\t\tTUint32 htcleoProgress = TUint32(err) & 0xffffu;\n"
        "\t\t\tasm volatile(\"orr %0,%0,#0xff000000\\n\\t\"\n"
        "\t\t\t\t\"orr %0,%0,#0x00050000\"\n"
        "\t\t\t\t: \"+r\"(htcleoProgress) : : \"memory\");\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(htcleoProgress);\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(15u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(
        text, ff05,
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(14u))\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(15u);\n",
        "retire FF05",
    )
    ff06 = (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xff060000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(16u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(
        text, ff06,
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(16u);\n",
        "retire FF06",
    )
    ff07 = (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(16u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xff070000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(17u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(text, ff07, "", "retire FF07")

    wait_anchor = (
        "\tSMF_STATE(EStWaitFinish)\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM8, \"EStWaitFinish\" );\n"
    )
    wait_stage = wait_anchor + (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(26u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1080000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(27u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(text, wait_anchor, wait_stage,
                        "F108 ProgramTimer return")

    issue_anchor = (
        "\t\ts.PushCommandStack();\n"
        "\t\ts.FillCommandDesc(ECmdSendStatus, 0);\n"
        "\t\tSMF_INVOKES(ExecCommandSMST, EStWaitFinish1)\n"
    )
    issue_stage = (
        "\t\ts.PushCommandStack();\n"
        "\t\ts.FillCommandDesc(ECmdSendStatus, 0);\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(27u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1090000u |\n"
        "\t\t\t\t(TUint32(s.Command().iCommand) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(28u);\n"
        "\t\t\t}\n"
        "\t\tSMF_INVOKES(ExecCommandSMST, EStWaitFinish1)\n"
    )
    text = replace_once(text, issue_anchor, issue_stage,
                        "F109 second CMD13 launch")

    entry_anchor = (
        "\tSMF_STATE(EStWaitFinish1)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM9, \"EStWaitFinish1\" );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(16u);\n"
        "\t\tconst TMMCStatus status(s.ResponseP());\n"
        "\t\ts.PopCommandStack();\n"
    )
    entry_stage = (
        "\tSMF_STATE(EStWaitFinish1)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM9, \"EStWaitFinish1\" );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(16u);\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(28u))\n"
        "\t\t\t{\n"
        "\t\t\tconst TMMCStatus htcleoSecondStatus(s.ResponseP());\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf10a0000u |\n"
        "\t\t\t\t(((TUint32(htcleoSecondStatus.State()) >> 9) & 0x0fu) << 12) |\n"
        "\t\t\t\t(TUint32(err) & 0x0fffu));\n"
        "\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n"
        "\t\telse if (s.HtcleoFatPhysicalReadTraceAt(16u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1010000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(20u);\n"
        "\t\t\t}\n"
        "\t\tconst TMMCStatus status(s.ResponseP());\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(20u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1020000u |\n"
        "\t\t\t\t((TUint32(status) >> 16) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(21u);\n"
        "\t\t\t}\n"
        "\t\ts.PopCommandStack();\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(21u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1030000u |\n"
        "\t\t\t\t(TUint32(status) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(22u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(text, entry_anchor, entry_stage,
                        "F101-F103 CMD13 status capture")

    state_anchor = (
        "\t\tconst TMMCardStateEnum st1 = status.State();\n\n"
        "\t\tif (st1 == ECardStatePrg || st1 == ECardStateRcv || st1 == ECardStateData)\n"
        "\t\t\t{\n"
        "\t\t\tSMF_INVOKES(ProgramTimerSMST, EStWaitFinish);\n"
        "\t\t\t}\n"
    )
    state_stage = (
        "\t\tconst TMMCardStateEnum st1 = status.State();\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(22u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1040000u |\n"
        "\t\t\t\t((TUint32(st1) >> 9) & 0x00ffu) |\n"
        "\t\t\t\t(status.Error() ? 0x8000u : 0u));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(23u);\n"
        "\t\t\t}\n\n"
        "\t\tif (st1 == ECardStatePrg || st1 == ECardStateRcv || st1 == ECardStateData)\n"
        "\t\t\t{\n"
        "\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(23u))\n"
        "\t\t\t\t{\n"
        "\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1050000u |\n"
        "\t\t\t\t\t((TUint32(st1) >> 9) & 0xffffu));\n"
        "\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(24u);\n"
        "\t\t\t\t}\n"
        "\t\t\tSMF_INVOKES(ProgramTimerSMST, EStWaitFinish);\n"
        "\t\t\t}\n"
    )
    return replace_once(text, state_anchor, state_stage,
                        "F104/F105 card-state branch")


def retire_ff_sdcc(text: str) -> str:
    old = (
        "    if (aSession.HtcleoFatPhysicalReadTraceAt(10u))\n"
        "        {\n"
        "        TUint32 htcleoProgressLocation;\n"
        "        asm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\");\n"
        "        ShowEstartProgress(htcleoProgressLocation, 0xff010000u |\n"
        "            ((aReason & 0x0fu) << 12) | (aStatus & 0x0fffu));\n"
        "        aSession.HtcleoAdvanceFatPhysicalReadTrace(11u);\n"
        "        }\n"
    )
    new = (
        "    if (aSession.HtcleoFatPhysicalReadTraceAt(10u))\n"
        "        aSession.HtcleoAdvanceFatPhysicalReadTrace(11u);\n"
    )
    text = replace_once(text, old, new, "retire FF01")
    marker = (
        f"/* {V23_SDCC_MARKER}: render only after the active SDCC transfer is terminal. */\n"
    )
    return replace_once(
        text, marker,
        marker + f"/* {SDCC_MARKER}: V24 retires the terminal screen call. */\n",
        "V24 SDCC marker",
    )


def verify(files: dict[str, str], sdcc: str) -> None:
    joined = "\n".join(files.values()) + "\n" + sdcc
    if files["mmc_header"].count(MARKER) != 1:
        raise SystemExit("V24 generic marker must exist exactly once")
    if sdcc.count(SDCC_MARKER) != 1:
        raise SystemExit("V24 SDCC marker must exist exactly once")
    for index in range(1, 11):
        stage = f"0xf10{index:x}0000u"
        if joined.count(stage) != 1:
            raise SystemExit(f"F101-F10A stage missing or duplicated: {stage}")
    if any(f"0xff0{suffix}0000u" in joined for suffix in "123456789a"):
        raise SystemExit("retired FF01-FF0A screen stage remains")
    if files["stack"].count("0xf10") != 2:
        raise SystemExit("stack.cpp must contain F106/F107 only")
    if files["sdcard"].count("0xf10") != 8:
        raise SystemExit("sdcard.cpp must contain eight F1 checkpoints")
    if "0xf10" in files["medmmc"] or "0xf10" in files["session"] or "0xf10" in sdcc:
        raise SystemExit("F1 checkpoint leaked outside EPBUSSD")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART UDF invariant failed")
    if "static volatile" in "\n".join(
        files[name] for name in ("medmmc", "session", "stack", "sdcard")
    ):
        raise SystemExit("forbidden persistent global phase state introduced")
    if "Kern::NanoWait(htcleoProgramPeriod * 1000000u);" not in files["stack"]:
        raise SystemExit("bounded synchronous ProgramTimer path missing")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE HTCLEO_SDCC_CPP")
    root = pathlib.Path(sys.argv[1]).resolve()
    sdcc_path = pathlib.Path(sys.argv[2]).resolve()
    paths = {
        "mmc_header": root / "kernel/eka/include/drivers/mmc.h",
        "medmmc": root / "kernel/eka/drivers/medmmc/medmmc.cpp",
        "session": root / "kernel/eka/drivers/pbus/mmc/session.cpp",
        "stack": root / "kernel/eka/drivers/pbus/mmc/stack.cpp",
        "sdcard": root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
    }
    for path in (*paths.values(), sdcc_path):
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    sdcc = sdcc_path.read_text(encoding="utf-8")
    if V23_MARKER not in files["mmc_header"] or V23_SDCC_MARKER not in sdcc:
        raise SystemExit("V24 requires installed V23 generic and SDCC attribution")

    # V25 deliberately retires every F101-F10A display call after hardware
    # proved the card remained in Data state.  Keep this predecessor transform
    # safely idempotent when a later build starts from the already-upgraded
    # kernel tree; V25 performs its own full source verification immediately
    # after this script returns.
    if V25_MARKER in files["mmc_header"]:
        if SDCC_MARKER not in sdcc:
            sdcc = retire_ff_sdcc(sdcc)
            sdcc_path.write_text(sdcc, encoding="utf-8")
        joined = "\n".join(files.values()) + "\n" + sdcc
        if any(f"0xf10{index:x}0000u" in joined for index in range(1, 11)):
            raise SystemExit("V25 marker exists but retired F101-F10A stage remains")
        f2_count = sum(
            joined.count(f"0xf20{index:x}0000u") for index in range(1, 11)
        )
        if V26_MARKER in files["mmc_header"]:
            if f2_count != 0:
                raise SystemExit("V26 marker exists but retired F201-F20A stage remains")
        elif f2_count != 10:
            raise SystemExit("V25 marker exists without exact F201-F20A stage set")
        print("HTCLEO_FAT_SD_FINISH_POLL_PROGRESS=retired-by-V25")
        return

    if MARKER not in files["mmc_header"]:
        files["mmc_header"] = transform_header(files["mmc_header"])
        files["medmmc"] = retire_ff_medmmc(files["medmmc"])
        files["stack"] = transform_program_timer(retire_ff_stack(files["stack"]))
        files["sdcard"] = retire_and_transform_sdcard(files["sdcard"])
    if SDCC_MARKER not in sdcc:
        sdcc = retire_ff_sdcc(sdcc)

    verify(files, sdcc)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    sdcc_path.write_text(sdcc, encoding="utf-8")
    print("HTCLEO_FAT_SD_FINISH_POLL_PROGRESS=10 F101_F10A=installed")


if __name__ == "__main__":
    main()
