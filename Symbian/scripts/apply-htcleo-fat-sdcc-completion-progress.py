#!/usr/bin/env python3
"""Move the exact tagged FAT read probe past SDCC transport completion.

Iteration 382 proved that the selected C: volume-label request reaches the
native SDCC2 command-register boundary as CMD18/32 blocks.  V23 retires the
FE01-FE0A display calls while preserving their request-local/session-local
attribution.  It deliberately performs no framebuffer drawing while CMD18 is
active: the first FF checkpoint is emitted only after the bounded native SDCC
transport has recorded its terminal result.  FF02-FF0A then follow the same
session through generic response handling, SD CMD13 completion, scheduler
completion and the MEDMMC completion DFC.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_SDCC_COMPLETION_PROGRESS_V23"
SDCC_MARKER = "HTCLEO_FAT_SDCC_COMPLETION_SDCC_PROGRESS_V23"
V22_MARKER = "HTCLEO_FAT_PHYSICAL_READ_PROGRESS_V22"
V22_SDCC_MARKER = "HTCLEO_FAT_PHYSICAL_READ_SDCC_PROGRESS_V22"
FF04_LOCAL_MARKER = "HTCLEO_FF04_LOCAL_STAGE_V23"
FF05_LOCAL_MARKER = "HTCLEO_FF05_LOCAL_STAGE_V23"
V24_MARKER = "HTCLEO_FAT_SD_FINISH_POLL_PROGRESS_V24"
V24_SDCC_MARKER = "HTCLEO_FAT_SD_FINISH_POLL_SDCC_PROGRESS_V24"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def retire_fe_medmmc(text: str) -> str:
    text = replace_once(
        text,
        "\t\t\t\tiSession->HtcleoArmFatPhysicalReadTrace();\n"
        "\t\t\t\tTUint32 htcleoRoute = iCurrentReq->IsPhysicalAddress() ? 0x8000u : 0u;\n"
        "\t\t\t\tif ((iReqEnd - iPhysStart) > iMaxBufSize &&\n"
        "\t\t\t\t\tiSocket->SupportsDoubleBuffering() && !iReadToEndOfCard)\n"
        "\t\t\t\t\thtcleoRoute |= 0x4000u;\n"
        "\t\t\t\tif (iReadToEndOfCard)\n"
        "\t\t\t\t\thtcleoRoute |= 0x2000u;\n"
        "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfe010000u | htcleoRoute |\n"
        "\t\t\t\t\t((length >> KMMCardHighCapBlockSizeLog2) & 0x1fffu));\n"
        "\t\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(1u);\n",
        "\t\t\t\tiSession->HtcleoArmFatPhysicalReadTrace();\n"
        "\t\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(1u);\n",
        "retire FE01 display",
    )
    text = replace_once(
        text,
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfe020000u |\n"
        "\t\t\t((iCurrentReq && (iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG)) ? 0x8000u : 0u) |\n"
        "\t\t\t(TUint32(aRequest) & 0xffu));\n",
        "",
        "retire FE02 display",
    )
    return replace_once(
        text,
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfe030000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n",
        "",
        "retire FE03 display",
    )


def retire_fe_session(text: str) -> str:
    return replace_once(
        text,
        "\t\tHTCLEO_MMC_PHYSICAL_READ_PROGRESS(0xfe040000u |\n"
        "\t\t\t((TUint32(doorState) & 0xffu) << 8) |\n"
        "\t\t\t(TUint32(iSessionID) & 0xffu));\n",
        "",
        "retire FE04 display",
    )


def retire_fe_stack(text: str) -> str:
    for old, label in (
        (
            "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xfe050000u |\n"
            "\t\t\t(TUint32(aSessP->iState) & 0xffffu));\n",
            "FE05",
        ),
        (
            "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xfe060000u |\n"
            "\t\t\t((TUint32(iSessionP->SessionID()) & 0xffu) << 8) |\n"
            "\t\t\t(TUint32(iSessionP->iState) & 0xffu));\n",
            "FE06",
        ),
        (
            "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xfe090000u |\n"
            "\t\t\t\t((TUint32(cmd.iCommand) & 0xffu) << 8) |\n"
            "\t\t\t\t((TUint32(cmd.Direction()) & 0x0fu) << 4) |\n"
            "\t\t\t\t(TUint32(cmd.BlockLength() >> 9) & 0x0fu));\n",
            "FE09",
        ),
    ):
        text = replace_once(text, old, "", f"retire {label} display")
    return text


def retire_fe_sdcard(text: str) -> str:
    text = replace_once(
        text,
        "\t\tconst TSDCard* htcleoCard = static_cast<const TSDCard*>(s.iCardP);\n"
        "\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xfe070000u |\n"
        "\t\t\t((s.iCardP && s.iCardP->IsReady()) ? 0x8000u : 0u) |\n"
        "\t\t\t((htcleoCard && htcleoCard->IsSDCard()) ? 0x4000u : 0u) |\n"
        "\t\t\t(TUint32(s.SessionID()) & 0xffu));\n",
        "",
        "retire FE07 display",
    )
    return replace_once(
        text,
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xfe080000u |\n"
        "\t\t\t\t((TUint32(cmd.iCommand) & 0xffu) << 8) |\n"
        "\t\t\t\t(TUint32(blocks) & 0xffu));\n",
        "",
        "retire FE08 display",
    )


def transform_header(text: str) -> str:
    anchor = f"\t/* {V22_MARKER}: iSpare[21] is an ABI-neutral one-request trace slot. */\n"
    addition = anchor + f"\t/* {MARKER}: phases 10-19 cover post-launch completion only. */\n"
    return replace_once(text, anchor, addition, "V23 session marker")


def transform_stack(text: str) -> str:
    issue_return_anchor = (
        "\tSMF_STATE(EStCommandIssued)\n\n"
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_ISSUECOMMANDCHECKRESPONSESM5, \"EStCommandIssued\" );\n"
    )
    issue_return_stage = issue_return_anchor + (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(11u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff020000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(12u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(text, issue_return_anchor, issue_return_stage,
                        "FF02 ASSP child return")

    analysed_anchor = (
        "\t\tOstTraceFunctionExitExt( DMMCSTACK_ISSUECOMMANDCHECKRESPONSESM_EXIT, this, ( TInt ) exitCode );\n"
        "\t\tSMF_RETURN(exitCode)\n"
    )
    analysed_stage = (
        "\t\tOstTraceFunctionExitExt( DMMCSTACK_ISSUECOMMANDCHECKRESPONSESM_EXIT, this, ( TInt ) exitCode );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(12u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff030000u |\n"
        "\t\t\t\t(TUint32(exitCode) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(13u);\n"
        "\t\t\t}\n"
        "\t\tSMF_RETURN(exitCode)\n"
    )
    text = replace_once(text, analysed_anchor, analysed_stage,
                        "FF03 generic response analysis")

    exec_anchor = (
        "\tSMF_STATE(EStCommandIssued)\n\n"
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_EXECCOMMANDSM13, \"EStCommandIssued\" );\n"
        "\t\t// If command was succesful then we've finished.\n"
    )
    exec_stage = (
        "\tSMF_STATE(EStCommandIssued)\n\n"
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_EXECCOMMANDSM13, \"EStCommandIssued\" );\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(13u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff040000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(14u);\n"
        "\t\t\t}\n"
        "\t\t// If command was succesful then we've finished.\n"
    )
    text = replace_once(text, exec_anchor, exec_stage, "FF04 ExecCommand return")

    dispatch_anchor = "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n\n"
    dispatch_stage = (
        "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n"
        "\tif (iSessionP->HtcleoFatPhysicalReadTraceAt(17u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff080000u |\n"
        "\t\t\t(TUint32(exitCode) & 0xffffu));\n"
        "\t\tiSessionP->HtcleoAdvanceFatPhysicalReadTrace(18u);\n"
        "\t\t}\n\n"
    )
    return replace_once(text, dispatch_anchor, dispatch_stage,
                        "FF08 scheduler dispatch return")


def transform_sdcard(text: str) -> str:
    issued_anchor = (
        "\tSMF_STATE(EStIssued)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM7, \"EStIssued\" );\n"
    )
    issued_stage = issued_anchor + (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(14u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xff050000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(15u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(text, issued_anchor, issued_stage, "FF05 CMD18 return")

    wait_anchor = (
        "\tSMF_STATE(EStWaitFinish1)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM9, \"EStWaitFinish1\" );\n"
    )
    wait_stage = wait_anchor + (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xff060000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(16u);\n"
        "\t\t\t}\n"
    )
    text = replace_once(text, wait_anchor, wait_stage, "FF06 CMD13 return")

    finish_anchor = (
        "\tSMF_STATE(EStRWFinish)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM10, \"EStRWFinish\" );\n"
    )
    finish_stage = finish_anchor + (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(16u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xff070000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(17u);\n"
        "\t\t\t}\n"
    )
    return replace_once(text, finish_anchor, finish_stage,
                        "FF07 SD read/write finish")


def refine_hoisted_stages(stack: str, sdcard: str) -> tuple[str, str]:
    """Keep FF04/FF05 stage construction beside their physical reporters.

    GCCE otherwise hoists these two pure stage expressions to the entry of
    their large state-machine functions.  The inline ORRs retain identical
    runtime values while making immutable E32 address-to-stage attribution
    local and unambiguous.
    """
    old_ff04 = (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(13u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xff040000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(14u);\n"
        "\t\t\t}\n"
    )
    new_ff04 = (
        f"\t\t/* {FF04_LOCAL_MARKER} */\n"
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(13u))\n"
        "\t\t\t{\n"
        "\t\t\tTUint32 htcleoProgress = TUint32(err) & 0xffffu;\n"
        "\t\t\tasm volatile(\"orr %0,%0,#0xff000000\\n\\t\"\n"
        "\t\t\t\t\"orr %0,%0,#0x00040000\"\n"
        "\t\t\t\t: \"+r\"(htcleoProgress) : : \"memory\");\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(htcleoProgress);\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(14u);\n"
        "\t\t\t}\n"
    )
    if FF04_LOCAL_MARKER not in stack:
        stack = replace_once(stack, old_ff04, new_ff04,
                             "localise FF04 stage construction")

    old_ff05 = (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(14u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xff050000u |\n"
        "\t\t\t\t(TUint32(err) & 0xffffu));\n"
        "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(15u);\n"
        "\t\t\t}\n"
    )
    new_ff05 = (
        f"\t\t/* {FF05_LOCAL_MARKER} */\n"
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
    if FF05_LOCAL_MARKER not in sdcard:
        sdcard = replace_once(sdcard, old_ff05, new_ff05,
                              "localise FF05 stage construction")
    return stack, sdcard


def transform_medmmc_completion(text: str) -> str:
    callback_anchor = (
        "\t__ASSERT_DEBUG(! md.iSessionEndDfc.Queued(), Panic(ESECBQueued));\n"
        "\tmd.iSessionEndDfc.Enque();\n"
    )
    callback_stage = callback_anchor + (
        "\tif (md.iSession && md.iSession->HtcleoFatPhysicalReadTraceAt(18u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xff090000u |\n"
        "\t\t\t(TUint32(md.iSession->EpocErrorCode()) & 0xffffu));\n"
        "\t\tmd.iSession->HtcleoAdvanceFatPhysicalReadTrace(19u);\n"
        "\t\t}\n"
    )
    text = replace_once(text, callback_anchor, callback_stage,
                        "FF09 MEDMMC session callback")

    dfc_anchor = (
        "\tif (r==KErrNone)\n"
        "\t\t{\n"
        "\t\tr = iSession->EpocErrorCode();\n\n"
        "\t\tswitch (CurrentRequest())\n"
    )
    dfc_stage = (
        "\tif (r==KErrNone)\n"
        "\t\t{\n"
        "\t\tr = iSession->EpocErrorCode();\n"
        "\t\tif (iSession->HtcleoFatPhysicalReadTraceAt(19u))\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xff0a0000u |\n"
        "\t\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n\n"
        "\t\tswitch (CurrentRequest())\n"
    )
    return replace_once(text, dfc_anchor, dfc_stage,
                        "FF0A MEDMMC completion DFC")


def transform_sdcc(text: str) -> str:
    helper_anchor = "TMMCErr DHtcleoSdStack::IssueMMCCommandSM()\n"
    helper = (
        f"/* {SDCC_MARKER}: render only after the active SDCC transfer is terminal. */\n"
        "static TMMCErr HtcleoRecordTaggedCommandResult(\n"
        "    DMMCSession& aSession, TUint32 aCommand, TUint32 aArgument,\n"
        "    TUint32 aReason, TUint32 aStatus, TMMCErr aResult)\n"
        "    {\n"
        "    const TMMCErr result = RecordCommandResult(\n"
        "        aCommand, aArgument, aReason, aStatus, aResult);\n"
        "    if (aSession.HtcleoFatPhysicalReadTraceAt(10u))\n"
        "        {\n"
        "        TUint32 htcleoProgressLocation;\n"
        "        asm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\");\n"
        "        ShowEstartProgress(htcleoProgressLocation, 0xff010000u |\n"
        "            ((aReason & 0x0fu) << 12) | (aStatus & 0x0fffu));\n"
        "        aSession.HtcleoAdvanceFatPhysicalReadTrace(11u);\n"
        "        }\n"
        "    return result;\n"
        "    }\n\n"
        + helper_anchor
    )
    text = replace_once(text, helper_anchor, helper, "FF01 SDCC result helper")

    begin = text.index(helper_anchor)
    end = text.index("class DHtcleoSdPsu", begin)
    function = text[begin:end]
    expected_calls = function.count("RecordCommandResult(")
    if expected_calls != 8:
        raise SystemExit(
            f"SDCC result call count changed: expected 8, found {expected_calls}"
        )
    function = function.replace(
        "RecordCommandResult(", "HtcleoRecordTaggedCommandResult(Session(), "
    )
    text = text[:begin] + function + text[end:]

    v22_block = (
        f"    /* {V22_SDCC_MARKER} */\n"
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
    )
    phase_only = (
        f"    /* {V22_SDCC_MARKER}; display retired by {SDCC_MARKER}. */\n"
        "    DMMCSession& htcleoSession = Session();\n"
        "    if (htcleoSession.HtcleoFatPhysicalReadTraceAt(9u))\n"
        "        htcleoSession.HtcleoAdvanceFatPhysicalReadTrace(10u);\n"
    )
    if v22_block in text:
        text = replace_once(text, v22_block, phase_only,
                            "retire FE0A and arm V23")
    else:
        pristine_anchor = (
            "    HtcleoSdcc::Register(HtcleoSdcc::EArgument) = command.iArgument;\n"
            "    Barrier();\n"
            "    HtcleoSdcc::Register(HtcleoSdcc::ECommand) = encoded;\n"
        )
        text = replace_once(text, pristine_anchor, phase_only + pristine_anchor,
                            "arm V23 in fresh staged SDCC")
    return text


def verify(files: dict[str, str], sdcc: str) -> None:
    joined = "\n".join(files.values()) + "\n" + sdcc
    if files["mmc_header"].count(MARKER) != 1:
        raise SystemExit("V23 generic marker must exist exactly once")
    if sdcc.count(SDCC_MARKER) != 2:
        # One occurrence labels the helper and one labels the retired V22 site.
        raise SystemExit("V23 SDCC marker must exist exactly twice")
    if files["stack"].count(FF04_LOCAL_MARKER) != 1:
        raise SystemExit("FF04 local-stage marker must exist exactly once")
    if files["sdcard"].count(FF05_LOCAL_MARKER) != 1:
        raise SystemExit("FF05 local-stage marker must exist exactly once")
    for suffix in "1236789a":
        stage = f"0xff0{suffix}0000u"
        if joined.count(stage) != 1:
            raise SystemExit(f"FF checkpoint missing or duplicated: {stage}")
    if files["stack"].count("#0x00040000") != 1:
        raise SystemExit("FF04 local stage immediate missing or duplicated")
    if files["sdcard"].count("#0x00050000") != 1:
        raise SystemExit("FF05 local stage immediate missing or duplicated")
    if "0xfe0" in "\n".join(
        files[name] for name in ("medmmc", "session", "stack", "sdcard")
    ) or "0xfe0a0000u" in sdcc:
        raise SystemExit("retired FE returning checkpoint remains")
    expected = {"medmmc": 2, "session": 0, "stack": 4, "sdcard": 3}
    for name, count in expected.items():
        if files[name].count("0xff0") != count:
            raise SystemExit(f"{name}: expected {count} FF checkpoints")
    if sdcc.count("0xff0") != 1:
        raise SystemExit("sdcc: expected one FF checkpoint")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART UDF invariant failed")
    if "0xe7f000f0" in "\n".join(
        files[name] for name in ("medmmc", "session", "stack", "sdcard")
    ) or "0xe7f000f0" in sdcc:
        raise SystemExit("physical UDF leaked into returning-checkpoint images")
    if "static volatile" in "\n".join(
        files[name] for name in ("medmmc", "session", "stack", "sdcard")
    ):
        raise SystemExit("forbidden persistent global phase state introduced")
    if files["mmc_header"].count("iSpare[21] = 0x48545000u;") != 1:
        raise SystemExit("request-local session trace slot invariant failed")


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

    # The generic kernel tree persists between builds while the HTCLEO BSP is
    # restaged from the workspace every time.  Once V24 has retired the V23
    # generic screen sites, still install V23 attribution into a freshly
    # staged SDCC source so the V24 transform can retire its FF01 call too.
    if V24_MARKER in files["mmc_header"]:
        if V24_SDCC_MARKER not in sdcc and SDCC_MARKER not in sdcc:
            sdcc = transform_sdcc(sdcc)
            sdcc_path.write_text(sdcc, encoding="utf-8")
        print("HTCLEO_FAT_SDCC_COMPLETION_PROGRESS=retired-by-V24")
        return

    if MARKER not in files["mmc_header"]:
        if V22_MARKER not in files["mmc_header"]:
            raise SystemExit("V23 requires the installed V22 request attribution")
        files["mmc_header"] = transform_header(files["mmc_header"])
        files["medmmc"] = transform_medmmc_completion(
            retire_fe_medmmc(files["medmmc"])
        )
        files["session"] = retire_fe_session(files["session"])
        files["stack"] = transform_stack(retire_fe_stack(files["stack"]))
        files["sdcard"] = transform_sdcard(retire_fe_sdcard(files["sdcard"]))
    if SDCC_MARKER not in sdcc:
        sdcc = transform_sdcc(sdcc)
    files["stack"], files["sdcard"] = refine_hoisted_stages(
        files["stack"], files["sdcard"]
    )

    verify(files, sdcc)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    sdcc_path.write_text(sdcc, encoding="utf-8")
    print("HTCLEO_FAT_SDCC_COMPLETION_PROGRESS=10 FF01_FF0A=installed")


if __name__ == "__main__":
    main()
