#!/usr/bin/env python3
"""Add HTCLEO explicit CMD12 handling and ten returning checkpoints.

Iteration 384 proved that the exact tagged CMD18 completed twice through the
SD finish poll while the card stayed in Data state.  The generic Symbian MMC
contract marks CMD18/CMD25 with iUseStopTransmission and documents that the
controller must issue CMD12, but the native HTCLEO PIO PSL does not auto-stop
the transfer.  V25 therefore adds an EPBUSSD-local compatibility path which
issues CMD12 through the ordinary ExecCommandSM machinery before polling CMD13.

F201-F20A replace the retired F101-F10A screen calls.  They remain attached to
the existing one-request session phase and never execute while CMD18 is active.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_SD_EXPLICIT_STOP_PROGRESS_V25"
V24_MARKER = "HTCLEO_FAT_SD_FINISH_POLL_PROGRESS_V24"
V26_MARKER = "HTCLEO_FAT_POST_STOP_RETURN_PROGRESS_V26"
MMP_MACRO = "__HTCLEO_SD_EXPLICIT_STOP_TRANSMISSION__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transform_header(text: str) -> str:
    anchor = (
        f"\t/* {V24_MARKER}: phases 20-28 trace the first SD finish-poll retry. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"\t/* {MARKER}: phases 30-38 trace explicit CMD12 and post-stop CMD13. */\n",
        "V25 session marker",
    )


def transform_mmp(text: str) -> str:
    anchor = "MACRO\t\t\t\t__HTCLEO_MMC_SYNC_SESSION_TIMERS__\n"
    return replace_once(
        text,
        anchor,
        anchor + f"MACRO\t\t\t\t{MMP_MACRO}\n",
        "EPBUSSD explicit-stop macro",
    )


def retire_f1_stack(text: str) -> str:
    session = (
        "#ifdef __EPOC32__\n"
        "\tDMMCSession &s = Session();\n"
        "#if !defined(__HTCLEO_MMC_SYNC_SESSION_TIMERS__)\n"
        "\tOstTrace1( TRACE_INTERNALS, DMMCSTACK_PROGRAMTIMERSM1, \"Current session=0x%x\", &s );\n"
        "#endif\n"
        "#endif\n"
    )
    session_replacement = (
        "#if defined(__EPOC32__) && !defined(__HTCLEO_MMC_SYNC_SESSION_TIMERS__)\n"
        "\tDMMCSession &s = Session();\n"
        "\tOstTrace1( TRACE_INTERNALS, DMMCSTACK_PROGRAMTIMERSM1, \"Current session=0x%x\", &s );\n"
        "#endif\n"
    )
    text = replace_once(
        text, session, session_replacement, "retire V24 ProgramTimer session"
    )
    progress = (
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
    replacement = (
        "\t\t// HTCLEO reports a 1 ms program period. Preserve that bounded delay\n"
        "\t\t// without depending on the same non-resuming NTimer/DFC path.\n"
        "\t\tconst TUint32 htcleoProgramPeriod = ProgramPeriodInMilliSeconds();\n"
        "\t\tKern::NanoWait(htcleoProgramPeriod * 1000000u);\n"
    )
    return replace_once(text, progress, replacement, "retire F106/F107")


def transform_sdcard(text: str) -> str:
    text = replace_once(
        text,
        "\t\t\tEStIssued,\n\t\t\tEStWaitFinish,\n",
        "\t\t\tEStIssued,\n\t\t\tEStStopIssued,\n\t\t\tEStWaitFinish,\n",
        "explicit-stop state enum",
    )

    issued = (
        "\tSMF_STATE(EStIssued)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM7, \"EStIssued\" );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(14u))\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(15u);\n"
        "\t\t// check state of card after data transfer with CMD13.\n"
        "\t\tif (s.Command().Direction() != 0)\n"
        "\t\t\t{\n"
        "\t\t\tSMF_GOTOS(EStWaitFinish)\n"
        "\t\t\t}\n\n"
        "\t\tSMF_GOTOS(EStRWFinish);\n\n"
    )
    explicit = (
        "\tSMF_STATE(EStIssued)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM7, \"EStIssued\" );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(14u))\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(15u);\n"
        "\t\t// The MMC command table marks CMD18/CMD25 as requiring CMD12.\n"
        "\t\t// HTCLEO's native PIO PSL returns after DATAEND and cannot issue the\n"
        "\t\t// controller-owned stop automatically, so do it here through the\n"
        "\t\t// normal command state machine before the existing CMD13 poll.\n"
        "\t\tif (s.Command().Direction() != 0)\n"
        "\t\t\t{\n"
        f"#ifdef {MMP_MACRO}\n"
        "\t\t\tTMMCCommandDesc& htcleoTransferCommand = s.Command();\n"
        "\t\t\tif (htcleoTransferCommand.iSpec.iMultipleBlocks &&\n"
        "\t\t\t\thtcleoTransferCommand.iSpec.iUseStopTransmission &&\n"
        "\t\t\t\t(htcleoTransferCommand.iCommand == ECmdReadMultipleBlock ||\n"
        "\t\t\t\t htcleoTransferCommand.iCommand == ECmdWriteMultipleBlock))\n"
        "\t\t\t\t{\n"
        "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2010000u |\n"
        "\t\t\t\t\t\t(TUint32(htcleoTransferCommand.iCommand) & 0xffu) |\n"
        "\t\t\t\t\t\t(htcleoTransferCommand.iSpec.iMultipleBlocks ? 0x0100u : 0u) |\n"
        "\t\t\t\t\t\t(htcleoTransferCommand.iSpec.iUseStopTransmission ? 0x0200u : 0u) |\n"
        "\t\t\t\t\t\t((TUint32(htcleoTransferCommand.Direction()) & 0x0fu) << 12));\n"
        "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(30u);\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\tTMMC::BigEndian4Bytes(s.ResponseP(), s.iLastStatus);\n"
        "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(30u))\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2020000u |\n"
        "\t\t\t\t\t\t((TUint32(s.iLastStatus) >> 16) & 0xffffu));\n"
        "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(31u);\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\ts.PushCommandStack();\n"
        "\t\t\t\ts.FillCommandDesc(ECmdStopTransmission, 0);\n"
        "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(31u))\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2030000u |\n"
        "\t\t\t\t\t\t(TUint32(s.Command().iCommand) & 0xffffu));\n"
        "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(32u);\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\tSMF_INVOKES(ExecCommandSMST, EStStopIssued)\n"
        "\t\t\t\t}\n"
        f"#endif // {MMP_MACRO}\n"
        "\t\t\tSMF_GOTOS(EStWaitFinish)\n"
        "\t\t\t}\n\n"
        "\t\tSMF_GOTOS(EStRWFinish);\n\n"
        "\tSMF_STATE(EStStopIssued)\n\n"
        "\t\tconst TMMCErr htcleoStopResult = err;\n"
        "\t\tconst TMMCStatus htcleoStopStatus(s.ResponseP());\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(32u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2040000u |\n"
        "\t\t\t\t(TUint32(htcleoStopResult) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(33u);\n"
        "\t\t\t}\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(33u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2050000u |\n"
        "\t\t\t\t((TUint32(htcleoStopStatus) >> 16) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(34u);\n"
        "\t\t\t}\n"
        "\t\ts.PopCommandStack();\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(34u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2060000u |\n"
        "\t\t\t\t(TUint32(htcleoStopStatus) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(35u);\n"
        "\t\t\t}\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(35u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2070000u |\n"
        "\t\t\t\t((((TUint32(htcleoStopStatus.State()) >> 9) & 0x0fu) << 12)) |\n"
        "\t\t\t\t(htcleoStopStatus.Error() ? 0x0800u : 0u) |\n"
        "\t\t\t\t(TUint32(htcleoStopResult) & 0x07ffu));\n"
        "\t\t\tif (htcleoStopResult != KMMCErrNone || htcleoStopStatus.Error())\n"
        "\t\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\telse\n"
        "\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(36u);\n"
        "\t\t\t}\n"
        "\t\tif (htcleoStopResult != KMMCErrNone)\n"
        "\t\t\tSMF_RETURN(htcleoStopResult)\n"
        "\t\tif (htcleoStopStatus.Error())\n"
        "\t\t\tSMF_RETURN(KMMCErrStatus)\n"
        "\t\tSMF_GOTOS(EStWaitFinish)\n\n"
    )
    text = replace_once(text, issued, explicit, "CMD12 compatibility path")

    old_wait_prefix = (
        "\tSMF_STATE(EStWaitFinish)\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM8, \"EStWaitFinish\" );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(26u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf1080000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(27u);\n"
        "\t\t\t}\n"
    )
    new_wait_prefix = (
        "\tSMF_STATE(EStWaitFinish)\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM8, \"EStWaitFinish\" );\n"
    )
    text = replace_once(text, old_wait_prefix, new_wait_prefix, "retire F108")

    old_issue = (
        "\t\t// ...else issue CMD13 to poll for the card finishing and check for errors\n"
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
    new_issue = (
        "\t\t// ...else issue CMD13 to poll for the card finishing and check for errors\n"
        "\t\ts.PushCommandStack();\n"
        "\t\ts.FillCommandDesc(ECmdSendStatus, 0);\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(36u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2080000u |\n"
        "\t\t\t\t(TUint32(s.Command().iCommand) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(37u);\n"
        "\t\t\t}\n"
        "\t\tSMF_INVOKES(ExecCommandSMST, EStWaitFinish1)\n"
    )
    text = replace_once(text, old_issue, new_issue, "F208 post-stop CMD13")

    old_entry = (
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
    new_entry = (
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM9, \"EStWaitFinish1\" );\n"
        "\t\tconst TMMCStatus status(s.ResponseP());\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(37u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2090000u |\n"
        "\t\t\t\t((((TUint32(status.State()) >> 9) & 0x0fu) << 12)) |\n"
        "\t\t\t\t(TUint32(err) & 0x0fffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(38u);\n"
        "\t\t\t}\n"
        "\t\ts.PopCommandStack();\n"
    )
    text = replace_once(text, old_entry, new_entry, "retire F101-F103/add F209")

    old_state = (
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
        "\t\t\t}\n\n"
    )
    new_state = (
        "\t\tconst TMMCardStateEnum st1 = status.State();\n"
        "\t\tif (st1 == ECardStatePrg || st1 == ECardStateRcv || st1 == ECardStateData)\n"
        "\t\t\t{\n"
        "\t\t\tSMF_INVOKES(ProgramTimerSMST, EStWaitFinish);\n"
        "\t\t\t}\n\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(38u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf20a0000u |\n"
        "\t\t\t\t((((TUint32(st1) >> 9) & 0x0fu) << 12)) |\n"
        "\t\t\t\t(status.Error() ? 0x0800u : 0u) |\n"
        "\t\t\t\t(TUint32(err) & 0x07ffu));\n"
        "\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n\n"
    )
    return replace_once(text, old_state, new_state, "retire F104/F105/add F20A")


def verify(header: str, stack: str, sdcard: str, mmp: str) -> None:
    joined = "\n".join((header, stack, sdcard, mmp))
    if header.count(MARKER) != 1:
        raise SystemExit("V25 header marker must exist exactly once")
    if mmp.count(MMP_MACRO) != 1:
        raise SystemExit("explicit-stop MMP macro must exist exactly once")
    if sdcard.count("EStStopIssued") != 3:
        raise SystemExit("explicit-stop state must have enum, invoke and state sites")
    if sdcard.count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("explicit CMD12 launch missing or duplicated")
    if V26_MARKER in header:
        if any(f"0xf20{index:x}0000u" in joined for index in range(1, 11)):
            raise SystemExit("V26 marker exists but retired F201-F20A stage remains")
    else:
        for index in range(1, 11):
            stage = f"0xf20{index:x}0000u"
            if joined.count(stage) != 1:
                raise SystemExit(f"F201-F20A stage missing or duplicated: {stage}")
    if any(f"0xf10{index:x}0000u" in joined for index in range(1, 11)):
        raise SystemExit("retired F101-F10A screen stage remains")
    if V26_MARKER not in header and (
            stack.count("0xf20") != 0 or sdcard.count("0xf20") != 10):
        raise SystemExit("F201-F20A must be ten EPBUSSD sdcard checkpoints")
    if "Kern::NanoWait(htcleoProgramPeriod * 1000000u);" not in stack:
        raise SystemExit("bounded synchronous ProgramTimer path missing")
    if joined.count("0xe7f000f0") != 0:
        raise SystemExit("unexpected UDF leaked into MMC/EPBUSSD sources")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "header": root / "kernel/eka/include/drivers/mmc.h",
        "stack": root / "kernel/eka/drivers/pbus/mmc/stack.cpp",
        "sdcard": root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp",
        "mmp": root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/epbussd.mmp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    if V24_MARKER not in files["header"]:
        raise SystemExit("V25 requires installed V24 finish-poll attribution")
    if MARKER not in files["header"]:
        files["header"] = transform_header(files["header"])
        files["stack"] = retire_f1_stack(files["stack"])
        files["sdcard"] = transform_sdcard(files["sdcard"])
        files["mmp"] = transform_mmp(files["mmp"])
    verify(files["header"], files["stack"], files["sdcard"], files["mmp"])
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    if V26_MARKER in files["header"]:
        print("HTCLEO_SD_EXPLICIT_STOP_REPAIR=preserved F201_F20A=retired-by-V26")
    else:
        print("HTCLEO_SD_EXPLICIT_STOP_PROGRESS=10 F201_F20A=installed")


if __name__ == "__main__":
    main()
