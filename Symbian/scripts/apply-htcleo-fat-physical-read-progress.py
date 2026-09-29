#!/usr/bin/env python3
"""Move the attributed FAT read probe into MMC scheduling and SDCC launch.

Iteration 381 proved that the exact first C: volume-label 16 KiB request
reaches MEDMMC immediately before physical I/O.  Keep the existing stack-local
FAT token and DriverFlags tag, retire FD01-FD0A, and carry a one-request phase
marker in DMMCSession::iSpare[21].  FE01-FE0A then bracket the selected MEDMMC
launch, session scheduling, SD protocol command construction, and the final
QSD8250 SDCC2 command-register write.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_PHYSICAL_READ_PROGRESS_V22"
SDCC_MARKER = "HTCLEO_FAT_PHYSICAL_READ_SDCC_PROGRESS_V22"
TRACE_FLAG = "0x10000000u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def remove_once(text: str, old: str, label: str) -> str:
    return replace_once(text, old, "", label)


def reporter(name: str) -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"#define {name}(aStage) \\\n"
        "    do \\\n"
        "        { \\\n"
        "        TUint32 htcleoProgressLocation; \\\n"
        "        asm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\"); \\\n"
        "        (void)Kern::HalFunction(EHalGroupPlatformSpecific1,2, \\\n"
        "            (TAny*)htcleoProgressLocation,(TAny*)(TUint32)(aStage)); \\\n"
        "        } while (0)\n"
        "#else\n"
        f"#define {name}(aStage) do {{ }} while (0)\n"
        "#endif\n\n"
    )


def transform_session_header(text: str) -> str:
    anchor = "\tinline void ResetCommandStack();\n"
    addition = (
        anchor
        + f"\n\t/* {MARKER}: iSpare[21] is an ABI-neutral one-request trace slot. */\n"
        + "\tinline void HtcleoArmFatPhysicalReadTrace()\n"
        + "\t\t{ iSpare[21] = 0x48545000u; }\n"
        + "\tinline TBool HtcleoFatPhysicalReadTraceAt(TUint32 aPhase) const\n"
        + "\t\t{ return iSpare[21] == (0x48545000u | (aPhase & 0xffu)); }\n"
        + "\tinline void HtcleoAdvanceFatPhysicalReadTrace(TUint32 aPhase)\n"
        + "\t\t{ iSpare[21] = 0x48545000u | (aPhase & 0xffu); }\n"
        + "\tinline void HtcleoClearFatPhysicalReadTrace()\n"
        + "\t\t{ iSpare[21] = 0u; }\n"
    )
    return replace_once(text, anchor, addition, "DMMCSession trace accessors")


def retire_fd_fat(text: str) -> str:
    text = remove_once(
        text,
        "    HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfd010000u |\n"
        "        (TUint32(aLength) & 0xffffu));\n",
        "retire FD01",
    )
    return remove_once(
        text,
        "    HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfd020000u |\n"
        "        ((htcleoFlags >> 16) & 0xffffu));\n",
        "retire FD02",
    )


def retire_fd_efile(text: str) -> str:
    return remove_once(
        text,
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif ((TUint(aFlags) & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\tHTCLEO_EFILE_MEDIA_READ_PROGRESS(0xfd030000u |\n"
        "\t\t\t((TUint(aFlags) >> 16) & 0xffffu));\n"
        "#endif\n",
        "retire FD03",
    )


def retire_fd_locmedia(text: str) -> str:
    blocks = (
        (
            "\t\t\tif (r == KErrNone && (m.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
            "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd040000u |\n"
            "\t\t\t\t\t((m.DriverFlags() >> 16) & 0xffffu));\n",
            "FD04",
        ),
        (
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\tif ((aReq.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
            "\t\t{\n"
            "\t\tTUint32 htcleoRoute = iDfcQ ? 0x8000u : 0u;\n"
            "#ifdef __DEMAND_PAGING__\n"
            "\t\tif (DataPagingDeviceRegistered)\n"
            "\t\t\thtcleoRoute |= 0x4000u;\n"
            "#endif\n"
            "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd050000u | htcleoRoute |\n"
            "\t\t\t(TUint32(aReq.Drive()->iDriveNumber) & 0xffu));\n"
            "\t\t}\n"
            "#endif\n\n",
            "FD05",
        ),
        (
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\tif ((aReq.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
            "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd060000u |\n"
            "\t\t\t(dmaHelper ? 0x8000u : 0u) |\n"
            "\t\t\t(TUint32(aReq.Drive()->iDriveNumber) & 0xffu));\n"
            "#endif\n",
            "FD06",
        ),
        (
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\tif ((m.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
            "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd070000u |\n"
            "\t\t\t((TUint32(iState) & 0xffu) << 8) |\n"
            "\t\t\t(TUint32(m.Drive()->iDriveNumber) & 0xffu));\n"
            "#endif\n",
            "FD07",
        ),
        (
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\t\t\tif ((m.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
            "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd080000u |\n"
            "\t\t\t\t\t((m.Flags() & TLocDrvRequest::EAdjusted) ? 0x8000u : 0u) |\n"
            "\t\t\t\t\t(TUint32(m.Drive()->iDriveNumber) & 0xffu));\n"
            "#endif\n",
            "FD08",
        ),
    )
    for block, label in blocks:
        text = remove_once(text, block, f"retire {label}")
    return text


def transform_medmmc(text: str) -> str:
    text = remove_once(
        text,
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (id == DLocalDrive::ERead &&\n"
        "\t\t\t(iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd090000u |\n"
        "\t\t\t\t(readOnly ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(iCurrentReq->Drive()->iDriveNumber) & 0xffu));\n"
        "#endif\n",
        "retire FD09",
    )
    text = remove_once(
        text,
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif ((iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd0a0000u |\n"
        "\t\t\t\t(allDone ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(r) & 0x7fffu));\n"
        "#endif\n",
        "retire FD0A",
    )
    route_anchor = (
        "\t\t\t// Re-calculate length as some data may have been recovered from cache\n"
        "\t\t\tlength = I64LOW(iReqEnd - iReqCur);\n"
        "\t\t\t\n"
    )
    route_stage = route_anchor + (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\tif ((iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\t\t{\n"
        "\t\t\t\tiSession->HtcleoArmFatPhysicalReadTrace();\n"
        "\t\t\t\tTUint32 htcleoRoute = iCurrentReq->IsPhysicalAddress() ? 0x8000u : 0u;\n"
        "\t\t\t\tif ((iReqEnd - iPhysStart) > iMaxBufSize &&\n"
        "\t\t\t\t\tiSocket->SupportsDoubleBuffering() && !iReadToEndOfCard)\n"
        "\t\t\t\t\thtcleoRoute |= 0x4000u;\n"
        "\t\t\t\tif (iReadToEndOfCard)\n"
        "\t\t\t\t\thtcleoRoute |= 0x2000u;\n"
        "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfe010000u | htcleoRoute |\n"
        "\t\t\t\t\t((length >> KMMCardHighCapBlockSizeLog2) & 0x1fffu));\n"
        "\t\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(1u);\n"
        "\t\t\t\t}\n"
        "#endif\n"
    )
    text = replace_once(text, route_anchor, route_stage, "FE01 physical route")
    engage_anchor = (
        "\t__ASSERT_DEBUG(iSession != NULL, Panic(ECFSessPtrNull));\n\n"
        "\tiMedReq = aRequest;\n"
    )
    engage_stage = (
        "\t__ASSERT_DEBUG(iSession != NULL, Panic(ECFSessPtrNull));\n\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (iSession->HtcleoFatPhysicalReadTraceAt(1u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfe020000u |\n"
        "\t\t\t((iCurrentReq && (iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG)) ? 0x8000u : 0u) |\n"
        "\t\t\t(TUint32(aRequest) & 0xffu));\n"
        "\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(2u);\n"
        "\t\t}\n"
        "\telse if (!iCurrentReq ||\n"
        "\t\t(iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) == 0)\n"
        "\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "#endif\n\n"
        "\tiMedReq = aRequest;\n"
    )
    text = replace_once(text, engage_anchor, engage_stage, "FE02 engage entry")
    critical_anchor = "\tTInt r = InCritical();\n\tif (r == KErrNone)\n"
    critical_stage = (
        "\tTInt r = InCritical();\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (iSession->HtcleoFatPhysicalReadTraceAt(2u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfe030000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\tif (r == KErrNone)\n"
        "\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(3u);\n"
        "\t\telse\n"
        "\t\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t}\n"
        "#endif\n"
        "\tif (r == KErrNone)\n"
    )
    return replace_once(text, critical_anchor, critical_stage, "FE03 InCritical result")


def transform_session(text: str) -> str:
    text = replace_once(text, "#include <drivers/mmc.h>\n",
                        "#include <drivers/mmc.h>\n\n" + reporter("HTCLEO_MMC_PHYSICAL_READ_PROGRESS"),
                        "session reporter")
    anchor = "\tSetupCIMControl(iSessionID);\n\n\tiStackP->Add(this);\n"
    stage = (
        "\tSetupCIMControl(iSessionID);\n\n"
        "\tif (HtcleoFatPhysicalReadTraceAt(3u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_MMC_PHYSICAL_READ_PROGRESS(0xfe040000u |\n"
        "\t\t\t((TUint32(doorState) & 0xffu) << 8) |\n"
        "\t\t\t(TUint32(iSessionID) & 0xffu));\n"
        "\t\tHtcleoAdvanceFatPhysicalReadTrace(4u);\n"
        "\t\t}\n\n"
        "\tiStackP->Add(this);\n"
    )
    return replace_once(text, anchor, stage, "FE04 session setup")


def transform_stack(text: str) -> str:
    # The file already has the returning HAL reporter used by earlier MMC work.
    add_anchor = (
        "\tiEntryQueue.Add( aSessP );\n"
        "\taSessP->iState |= KMMCSessStateEngaged;\n"
        "\tRESTOREPREEMPTION\n"
        "\tScheduler( iAttention );\n"
    )
    add_stage = (
        "\tiEntryQueue.Add( aSessP );\n"
        "\taSessP->iState |= KMMCSessStateEngaged;\n"
        "\tRESTOREPREEMPTION\n"
        "\tif (aSessP->HtcleoFatPhysicalReadTraceAt(4u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xfe050000u |\n"
        "\t\t\t(TUint32(aSessP->iState) & 0xffffu));\n"
        "\t\taSessP->HtcleoAdvanceFatPhysicalReadTrace(5u);\n"
        "\t\t}\n"
        "\tScheduler( iAttention );\n"
    )
    text = replace_once(text, add_anchor, add_stage, "FE05 entry queue")
    dispatch_anchor = (
        "\t// Execute the session state machine until it completes, is blocked or is aborted.\n"
        "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n"
    )
    dispatch_stage = (
        "\t// Execute the session state machine until it completes, is blocked or is aborted.\n"
        "\tif (iSessionP->HtcleoFatPhysicalReadTraceAt(5u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xfe060000u |\n"
        "\t\t\t((TUint32(iSessionP->SessionID()) & 0xffu) << 8) |\n"
        "\t\t\t(TUint32(iSessionP->iState) & 0xffu));\n"
        "\t\tiSessionP->HtcleoAdvanceFatPhysicalReadTrace(6u);\n"
        "\t\t}\n"
        "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n"
    )
    text = replace_once(text, dispatch_anchor, dispatch_stage, "FE06 scheduler dispatch")
    issue_anchor = (
        "\t\tcmd.iFlags &= ~(KMMCCmdFlagASSPFlags|KMMCCmdFlagExecSelBusy);\n"
        "\t\tcmd.iBytesDone=0;\n"
        "\t\tm.SetTraps(KMMCErrAll);\n"
        "\t\tSMF_INVOKES(IssueMMCCommandSMST,EStCommandIssued)\n"
    )
    issue_stage = (
        "\t\tcmd.iFlags &= ~(KMMCCmdFlagASSPFlags|KMMCCmdFlagExecSelBusy);\n"
        "\t\tcmd.iBytesDone=0;\n"
        "\t\tm.SetTraps(KMMCErrAll);\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(8u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xfe090000u |\n"
        "\t\t\t\t((TUint32(cmd.iCommand) & 0xffu) << 8) |\n"
        "\t\t\t\t((TUint32(cmd.Direction()) & 0x0fu) << 4) |\n"
        "\t\t\t\t(TUint32(cmd.BlockLength() >> 9) & 0x0fu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(9u);\n"
        "\t\t\t}\n"
        "\t\tSMF_INVOKES(IssueMMCCommandSMST,EStCommandIssued)\n"
    )
    return replace_once(text, issue_anchor, issue_stage, "FE09 generic command issue")


def transform_sdcard(text: str) -> str:
    text = replace_once(text, "#include <drivers/sdcard.h>\n",
                        "#include <drivers/sdcard.h>\n\n" + reporter("HTCLEO_SD_PHYSICAL_READ_PROGRESS"),
                        "SD reporter")
    begin_anchor = (
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\">SD:RWBlocksSM %x\",TUint(s.iLastStatus)));\n\n"
        "\tSMF_BEGIN\n"
    )
    begin_stage = (
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\">SD:RWBlocksSM %x\",TUint(s.iLastStatus)));\n\n"
        "\tif (s.HtcleoFatPhysicalReadTraceAt(6u))\n"
        "\t\t{\n"
        "\t\tconst TSDCard* htcleoCard = static_cast<const TSDCard*>(s.iCardP);\n"
        "\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xfe070000u |\n"
        "\t\t\t((s.iCardP && s.iCardP->IsReady()) ? 0x8000u : 0u) |\n"
        "\t\t\t((htcleoCard && htcleoCard->IsSDCard()) ? 0x4000u : 0u) |\n"
        "\t\t\t(TUint32(s.SessionID()) & 0xffu));\n"
        "\t\ts.HtcleoAdvanceFatPhysicalReadTrace(7u);\n"
        "\t\t}\n\n"
        "\tSMF_BEGIN\n"
    )
    text = replace_once(text, begin_anchor, begin_stage, "FE07 SD state machine")
    command_anchor = (
        "\t\t\tcmd.iFlags = oldFlags;\t\t\t\t// ...and restore the old command flags\n"
        "\t\t\t}\n\n"
        "\t\t// NB We need to trap KMMCErrStatus errors, because if one occurs, \n"
    )
    command_stage = (
        "\t\t\tcmd.iFlags = oldFlags;\t\t\t\t// ...and restore the old command flags\n"
        "\t\t\t}\n\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(7u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xfe080000u |\n"
        "\t\t\t\t((TUint32(cmd.iCommand) & 0xffu) << 8) |\n"
        "\t\t\t\t(TUint32(blocks) & 0xffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(8u);\n"
        "\t\t\t}\n\n"
        "\t\t// NB We need to trap KMMCErrStatus errors, because if one occurs, \n"
    )
    return replace_once(text, command_anchor, command_stage, "FE08 data command ready")


def transform_sdcc(text: str) -> str:
    anchor = (
        "    HtcleoSdcc::Register(HtcleoSdcc::EArgument) = command.iArgument;\n"
        "    Barrier();\n"
        "    HtcleoSdcc::Register(HtcleoSdcc::ECommand) = encoded;\n"
    )
    stage = (
        f"    /* {SDCC_MARKER} */\n"
        "    DMMCSession& htcleoSession = Session();\n"
        "    if (htcleoSession.HtcleoFatPhysicalReadTraceAt(9u))\n"
        "        {\n"
        "        TUint32 htcleoProgressLocation;\n"
        "        asm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\");\n"
        "        const TUint32 htcleoBlocks = command.BlockLength()\n"
        "            ? command.iTotalLength / command.BlockLength() : 0u;\n"
        "        ShowEstartProgress(htcleoProgressLocation, 0xfe0a0000u |\n"
        "            ((TUint32(command.iCommand) & 0xffu) << 8) |\n"
        "            (hasData ? 0x80u : 0u) |\n"
        "            (command.iSpec.iDirection == EDirRead ? 0x40u : 0u) |\n"
        "            (htcleoBlocks & 0x3fu));\n"
        "        htcleoSession.HtcleoClearFatPhysicalReadTrace();\n"
        "        }\n"
        "    HtcleoSdcc::Register(HtcleoSdcc::EArgument) = command.iArgument;\n"
        "    Barrier();\n"
        "    HtcleoSdcc::Register(HtcleoSdcc::ECommand) = encoded;\n"
    )
    return replace_once(text, anchor, stage, "FE0A SDCC command-register boundary")


def verify(files: dict[str, str], sdcc: str) -> None:
    joined = "\n".join(files.values()) + "\n" + sdcc
    if joined.count(MARKER) != 1:
        raise SystemExit("V22 marker must exist exactly once")
    if sdcc.count(SDCC_MARKER) != 1:
        raise SystemExit("V22 SDCC marker must exist exactly once")
    for suffix in "123456789a":
        stage = f"0xfe0{suffix}0000u"
        if joined.count(stage) != 1:
            raise SystemExit(f"FE checkpoint missing or duplicated: {stage}")
    if "0xfd0" in "\n".join(
        files[name] for name in ("fat_drv", "efile", "locmedia", "medmmc")
    ):
        raise SystemExit("retired FD checkpoint remains")
    expected = {"medmmc": 3, "session": 1, "stack": 3, "sdcard": 2}
    for name, count in expected.items():
        if files[name].count("0xfe0") != count:
            raise SystemExit(f"{name}: expected {count} FE checkpoints")
    if sdcc.count("0xfe0") != 1:
        raise SystemExit("sdcc: expected one FE checkpoint")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART UDF invariant failed")
    if "0xe7f000f0" in "\n".join(
        files[name] for name in ("medmmc", "session", "stack", "sdcard")
    ) or "0xe7f000f0" in sdcc:
        raise SystemExit("physical UDF leaked into returning-checkpoint images")
    if files["mmc_header"].count("HtcleoArmFatPhysicalReadTrace()") != 1 or \
            files["mmc_header"].count("iSpare[21] = 0x48545000u;") != 1:
        raise SystemExit("session trace arm slot invariant failed")
    if TRACE_FLAG not in files["medmmc"]:
        raise SystemExit("MEDMMC DriverFlags attribution is absent")
    if files["fat_drv"].count("KLocalMessageHandle, 0, htcleoFlags") != 1:
        raise SystemExit("EFAT-to-EFILE tagged handoff was lost")
    if "static volatile" in "\n".join(
        files[name] for name in ("medmmc", "session", "stack", "sdcard")
    ):
        raise SystemExit("forbidden persistent global phase state introduced")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE HTCLEO_SDCC_CPP")
    root = pathlib.Path(sys.argv[1]).resolve()
    sdcc_path = pathlib.Path(sys.argv[2]).resolve()
    paths = {
        "mmc_header": root / "kernel/eka/include/drivers/mmc.h",
        "fat_drv": root / "userlibandfileserver/fileserver/sfat32/sl_drv.cpp",
        "efile": root / "userlibandfileserver/fileserver/sfile/sf_ext.cpp",
        "locmedia": root / "kernel/eka/drivers/locmedia/locmedia.cpp",
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

    if MARKER not in files["mmc_header"]:
        files["mmc_header"] = transform_session_header(files["mmc_header"])
        files["fat_drv"] = retire_fd_fat(files["fat_drv"])
        files["efile"] = retire_fd_efile(files["efile"])
        files["locmedia"] = retire_fd_locmedia(files["locmedia"])
        files["medmmc"] = transform_medmmc(files["medmmc"])
        files["session"] = transform_session(files["session"])
        files["stack"] = transform_stack(files["stack"])
        files["sdcard"] = transform_sdcard(files["sdcard"])
    if SDCC_MARKER not in sdcc:
        sdcc = transform_sdcc(sdcc)

    verify(files, sdcc)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    sdcc_path.write_text(sdcc, encoding="utf-8")
    print("HTCLEO_FAT_PHYSICAL_READ_PROGRESS=10 FE01_FE0A=installed")


if __name__ == "__main__":
    main()
