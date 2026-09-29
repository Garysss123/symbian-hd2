#!/usr/bin/env python3
"""Trace the exact tagged FAT read from post-CMD12 completion back to EFAT32.

Iteration 385 proved that the HTCLEO explicit CMD12 compatibility path returns
the card to Tran state with no R1 or transport error.  V26 retires the F201-
F20A screen calls while preserving that repair and its request-local phase
chain.  F301-F30A then follow only the already-tagged first C: volume-label
16 KiB request through the SD state-machine unwind, MMC scheduler completion,
MEDMMC copy/completion, ELOCD message completion, and the EFAT32 caller return.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_POST_STOP_RETURN_PROGRESS_V26"
FAT_MARKER = "HTCLEO_FAT_POST_STOP_USER_RETURN_PROGRESS_V26"
V25_MARKER = "HTCLEO_SD_EXPLICIT_STOP_PROGRESS_V25"
TRACE_FLAG = "HTCLEO_FAT_MEDIA_DRIVER_FLAG"
RETURN_FLAG = "HTCLEO_FAT_MEDIA_RETURN_FLAG"
V27_MARKER = "HTCLEO_FAT_CACHE_UNWIND_PROGRESS_V27"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transform_mmc_header(text: str) -> str:
    anchor = (
        f"\t/* {V25_MARKER}: phases 30-38 trace explicit CMD12 and post-stop CMD13. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"\t/* {MARKER}: phases 39-46 trace the successful read return. */\n",
        "V26 MMC session marker",
    )


def transform_fat_header(text: str) -> str:
    old = (
        "class THtcleoFatDirReadTrace\n"
        "    {\n"
        "public:\n"
        "    TUint32 iMarker;\n"
        "    };\n"
    )
    new = (
        f"/* {FAT_MARKER}: caller-local phase follows the tagged read return. */\n"
        "class THtcleoFatDirReadTrace\n"
        "    {\n"
        "public:\n"
        "    TUint32 iMarker;\n"
        "    TUint32 iPhase;\n"
        "    };\n"
    )
    return replace_once(text, old, new, "FAT trace caller phase")


def phase_only(phase: int, next_phase: int) -> str:
    return (
        f"\t\tif (s.HtcleoFatPhysicalReadTraceAt({phase}u))\n"
        f"\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace({next_phase}u);\n"
    )


def transform_sdcard(text: str) -> str:
    replacements = (
        (
            "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
            "\t\t\t\t\t{\n"
            "\t\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2010000u |\n"
            "\t\t\t\t\t\t(TUint32(htcleoTransferCommand.iCommand) & 0xffu) |\n"
            "\t\t\t\t\t\t(htcleoTransferCommand.iSpec.iMultipleBlocks ? 0x0100u : 0u) |\n"
            "\t\t\t\t\t\t(htcleoTransferCommand.iSpec.iUseStopTransmission ? 0x0200u : 0u) |\n"
            "\t\t\t\t\t\t((TUint32(htcleoTransferCommand.Direction()) & 0x0fu) << 12));\n"
            "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(30u);\n"
            "\t\t\t\t\t}\n",
            "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(15u))\n"
            "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(30u);\n",
            "retire F201",
        ),
        (
            "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(30u))\n"
            "\t\t\t\t\t{\n"
            "\t\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2020000u |\n"
            "\t\t\t\t\t\t((TUint32(s.iLastStatus) >> 16) & 0xffffu));\n"
            "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(31u);\n"
            "\t\t\t\t\t}\n",
            "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(30u))\n"
            "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(31u);\n",
            "retire F202",
        ),
        (
            "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(31u))\n"
            "\t\t\t\t\t{\n"
            "\t\t\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2030000u |\n"
            "\t\t\t\t\t\t(TUint32(s.Command().iCommand) & 0xffffu));\n"
            "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(32u);\n"
            "\t\t\t\t\t}\n",
            "\t\t\t\tif (s.HtcleoFatPhysicalReadTraceAt(31u))\n"
            "\t\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(32u);\n",
            "retire F203",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(32u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2040000u |\n"
            "\t\t\t\t(TUint32(htcleoStopResult) & 0xffffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(33u);\n"
            "\t\t\t}\n",
            phase_only(32, 33),
            "retire F204",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(33u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2050000u |\n"
            "\t\t\t\t((TUint32(htcleoStopStatus) >> 16) & 0xffffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(34u);\n"
            "\t\t\t}\n",
            phase_only(33, 34),
            "retire F205",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(34u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2060000u |\n"
            "\t\t\t\t(TUint32(htcleoStopStatus) & 0xffffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(35u);\n"
            "\t\t\t}\n",
            phase_only(34, 35),
            "retire F206",
        ),
        (
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
            "\t\t\t}\n",
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(35u))\n"
            "\t\t\t{\n"
            "\t\t\tif (htcleoStopResult != KMMCErrNone || htcleoStopStatus.Error())\n"
            "\t\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
            "\t\t\telse\n"
            "\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(36u);\n"
            "\t\t\t}\n",
            "retire F207",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(36u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2080000u |\n"
            "\t\t\t\t(TUint32(s.Command().iCommand) & 0xffffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(37u);\n"
            "\t\t\t}\n",
            phase_only(36, 37),
            "retire F208",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(37u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf2090000u |\n"
            "\t\t\t\t((((TUint32(status.State()) >> 9) & 0x0fu) << 12)) |\n"
            "\t\t\t\t(TUint32(err) & 0x0fffu));\n"
            "\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(38u);\n"
            "\t\t\t}\n",
            phase_only(37, 38),
            "retire F209",
        ),
        (
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(38u))\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf20a0000u |\n"
            "\t\t\t\t((((TUint32(st1) >> 9) & 0x0fu) << 12)) |\n"
            "\t\t\t\t(status.Error() ? 0x0800u : 0u) |\n"
            "\t\t\t\t(TUint32(err) & 0x07ffu));\n"
            "\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
            "\t\t\t}\n",
            "\t\tif (s.HtcleoFatPhysicalReadTraceAt(38u))\n"
            "\t\t\t{\n"
            "\t\t\tif (err == KMMCErrNone && !status.Error())\n"
            "\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(39u);\n"
            "\t\t\telse\n"
            "\t\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
            "\t\t\t}\n",
            "retire F20A and continue V26",
        ),
    )
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    anchor = (
        "\tSMF_STATE(EStRWFinish)\n\n"
        "        OstTrace0( TRACE_INTERNALS, DSDSTACK_CIMREADWRITEBLOCKSSM10, \"EStRWFinish\" );\n"
    )
    stage = anchor + (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(39u))\n"
        "\t\t\t{\n"
        "\t\t\tconst TBool htcleoStatusError = TMMCStatus(s.ResponseP()).Error() != 0;\n"
        "\t\t\tHTCLEO_SD_PHYSICAL_READ_PROGRESS(0xf3010000u |\n"
        "\t\t\t\t(htcleoStatusError ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(s.Command().iCommand) & 0xffu));\n"
        "\t\t\tif (!htcleoStatusError)\n"
        "\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(40u);\n"
        "\t\t\telse\n"
        "\t\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n"
    )
    return replace_once(text, anchor, stage, "F301 SD finish entry")


def transform_stack(text: str) -> str:
    dispatch = "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n\n"
    dispatch_stage = (
        "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n"
        "\tif (iSessionP->HtcleoFatPhysicalReadTraceAt(40u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xf3020000u |\n"
        "\t\t\t(TUint32(exitCode) & 0xffffu));\n"
        "\t\tif ((exitCode & ~KMMCErrBypass) == KMMCErrNone)\n"
        "\t\t\tiSessionP->HtcleoAdvanceFatPhysicalReadTrace(41u);\n"
        "\t\telse\n"
        "\t\t\tiSessionP->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t}\n\n"
    )
    text = replace_once(text, dispatch, dispatch_stage, "F302 scheduler dispatch return")

    callback = (
        "\t\t\tif(doCallback)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t// call media driver completion routine or StackSessionCBST().\n"
        "\t\t\t\tsessP->iCallBack.CallBack();\n"
        "\t\t\t\t}\n"
    )
    callback_stage = (
        "\t\t\tif(doCallback)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t// call media driver completion routine or StackSessionCBST().\n"
        "\t\t\t\tif (sessP->HtcleoFatPhysicalReadTraceAt(41u))\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tconst TInt htcleoResult = sessP->EpocErrorCode();\n"
        "\t\t\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xf3030000u |\n"
        "\t\t\t\t\t\t(TUint32(htcleoResult) & 0xffffu));\n"
        "\t\t\t\t\tif (htcleoResult == KErrNone)\n"
        "\t\t\t\t\t\tsessP->HtcleoAdvanceFatPhysicalReadTrace(42u);\n"
        "\t\t\t\t\telse\n"
        "\t\t\t\t\t\tsessP->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\tsessP->iCallBack.CallBack();\n"
        "\t\t\t\t}\n"
    )
    return replace_once(text, callback, callback_stage, "F303 scheduler callback boundary")


def transform_medmmc(text: str) -> str:
    text = replace_once(
        text,
        f"#define {TRACE_FLAG} 0x10000000u\n",
        f"#define {TRACE_FLAG} 0x10000000u\n"
        f"#define {RETURN_FLAG} 0x20000000u\n",
        "MEDMMC return tag",
    )
    callback = (
        "\t__ASSERT_DEBUG(! md.iSessionEndDfc.Queued(), Panic(ESECBQueued));\n"
        "\tmd.iSessionEndDfc.Enque();\n"
    )
    callback_stage = callback + (
        "\tif (md.iSession && md.iSession->HtcleoFatPhysicalReadTraceAt(42u))\n"
        "\t\t{\n"
        "\t\tconst TInt htcleoResult = md.iSession->EpocErrorCode();\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3040000u |\n"
        "\t\t\t(TUint32(htcleoResult) & 0xffffu));\n"
        "\t\tif (htcleoResult == KErrNone)\n"
        "\t\t\tmd.iSession->HtcleoAdvanceFatPhysicalReadTrace(43u);\n"
        "\t\telse\n"
        "\t\t\tmd.iSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t}\n"
    )
    text = replace_once(text, callback, callback_stage, "F304 MEDMMC callback enqueue")

    preflight = (
        "\tif (r==KErrNone)\n"
        "\t\t{\n"
        "\t\tr = iSession->EpocErrorCode();\n\n"
        "\t\tswitch (CurrentRequest())\n"
    )
    preflight_stage = (
        "\tif (r==KErrNone)\n"
        "\t\t{\n"
        "\t\tr = iSession->EpocErrorCode();\n"
        "\t\tif (iSession->HtcleoFatPhysicalReadTraceAt(43u))\n"
        "\t\t\t{\n"
        "\t\t\tconst TBool htcleoRead = CurrentRequest() == EMReqRead;\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3050000u |\n"
        "\t\t\t\t(htcleoRead ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(r) & 0x7fffu));\n"
        "\t\t\tif (htcleoRead && r == KErrNone)\n"
        "\t\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(44u);\n"
        "\t\t\telse\n"
        "\t\t\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n\n"
        "\t\tswitch (CurrentRequest())\n"
    )
    text = replace_once(text, preflight, preflight_stage, "F305 MEDMMC DFC preflight")

    copy_return = (
        "\t\t\t\telse\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tr = WriteDataToUser(&iIntBuf[I64LOW(iReqCur - iPhysStart)]);\n"
        "\t\t\t\t\t}\n\n"
        "\t\t\t\tif (r != KErrNone)\n"
    )
    copy_return_stage = (
        "\t\t\t\telse\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tr = WriteDataToUser(&iIntBuf[I64LOW(iReqCur - iPhysStart)]);\n"
        "\t\t\t\t\t}\n\n"
        "\t\t\t\tif (iSession->HtcleoFatPhysicalReadTraceAt(44u))\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3060000u |\n"
        "\t\t\t\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\t\t\t\tif (r == KErrNone)\n"
        "\t\t\t\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(45u);\n"
        "\t\t\t\t\telse\n"
        "\t\t\t\t\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t\t\t}\n\n"
        "\t\t\t\tif (r != KErrNone)\n"
    )
    text = replace_once(text, copy_return, copy_return_stage, "F306 user-copy return")

    complete = (
        "\t// r != KErrNone => complete\n"
        "\t__ASSERT_DEBUG(!(r != KErrNone) || complete, Panic(EDSEDNotErrComplete));\n\n"
        "\tif (complete)\n"
    )
    complete_stage = (
        "\t// r != KErrNone => complete\n"
        "\t__ASSERT_DEBUG(!(r != KErrNone) || complete, Panic(EDSEDNotErrComplete));\n\n"
        "\tif (iSession && iSession->HtcleoFatPhysicalReadTraceAt(45u))\n"
        "\t\t{\n"
        "\t\tconst TBool htcleoRead = CurrentRequest() == EMReqRead;\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3070000u |\n"
        "\t\t\t(complete ? 0x8000u : 0u) |\n"
        "\t\t\t(htcleoRead ? 0x4000u : 0u) |\n"
        "\t\t\t(TUint32(r) & 0x3fffu));\n"
        "\t\tif (complete && htcleoRead && r == KErrNone && iCurrentReq &&\n"
        f"\t\t\t(iCurrentReq->DriverFlags() & {TRACE_FLAG}) != 0)\n"
        "\t\t\t{\n"
        f"\t\t\tiCurrentReq->DriverFlags() |= {RETURN_FLAG};\n"
        "\t\t\tiSession->HtcleoAdvanceFatPhysicalReadTrace(46u);\n"
        "\t\t\t}\n"
        "\t\telse\n"
        "\t\t\tiSession->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t}\n\n"
        "\tif (complete)\n"
    )
    return replace_once(text, complete, complete_stage, "F307 complete decision")


def transform_locmedia(text: str) -> str:
    text = replace_once(
        text,
        f"#define {TRACE_FLAG} 0x10000000u\n",
        f"#define {TRACE_FLAG} 0x10000000u\n"
        f"#define {RETURN_FLAG} 0x20000000u\n",
        "ELOCD return tag",
    )
    completion = (
        "\tOstTraceFunctionEntry1( DPRIMARYMEDIABASE_COMPLETEREQUEST_ENTRY, this );\n"
        "\tOstTraceDefExt2(OST_TRACE_CATEGORY_RND, TRACE_REQUEST, DPRIMARYMEDIABASE_COMPLETEREQUEST1, \"TLocDrvRequest Object=0x%x; aResult=%d\", (TUint) &aMsg, aResult);\n"
        "\taMsg.Complete(aResult,EFalse);\n"
        "\tOstTraceFunctionExit1( DPRIMARYMEDIABASE_COMPLETEREQUEST_EXIT, this );\n"
    )
    completion_stage = (
        "\tOstTraceFunctionEntry1( DPRIMARYMEDIABASE_COMPLETEREQUEST_ENTRY, this );\n"
        "\tOstTraceDefExt2(OST_TRACE_CATEGORY_RND, TRACE_REQUEST, DPRIMARYMEDIABASE_COMPLETEREQUEST1, \"TLocDrvRequest Object=0x%x; aResult=%d\", (TUint) &aMsg, aResult);\n"
        f"\tconst TBool htcleoTaggedReturn = (aMsg.DriverFlags() & ({TRACE_FLAG} | {RETURN_FLAG})) ==\n"
        f"\t\t({TRACE_FLAG} | {RETURN_FLAG});\n"
        "\taMsg.Complete(aResult,EFalse);\n"
        "\tif (htcleoTaggedReturn)\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3080000u |\n"
        "\t\t\t(TUint32(aResult) & 0xffffu));\n"
        "\tOstTraceFunctionExit1( DPRIMARYMEDIABASE_COMPLETEREQUEST_EXIT, this );\n"
    )
    return replace_once(text, completion, completion_stage, "F308 ELOCD completion return")


def transform_fat(text: str) -> str:
    wrapper = (
        "    EnterCriticalSection();\n"
        f"    const TUint htcleoFlags = RLocalDrive::ELocDrvMetaData | {TRACE_FLAG};\n"
        "    TInt nRes = iLocalDrive->Read(aPos, aLength, &aTrg,\n"
        "        KLocalMessageHandle, 0, htcleoFlags);\n"
        "    LeaveCriticalSection();\n"
        "    return nRes;\n"
    )
    wrapper_stage = (
        "    EnterCriticalSection();\n"
        f"    const TUint htcleoFlags = RLocalDrive::ELocDrvMetaData | {TRACE_FLAG};\n"
        "    TInt nRes = iLocalDrive->Read(aPos, aLength, &aTrg,\n"
        "        KLocalMessageHandle, 0, htcleoFlags);\n"
        "    LeaveCriticalSection();\n"
        "    if (aTrace->iPhase == 0u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf3090000u |\n"
        "            (TUint32(nRes) & 0xffffu));\n"
        "        aTrace->iPhase = 1u;\n"
        "        }\n"
        "    return nRes;\n"
    )
    text = replace_once(text, wrapper, wrapper_stage, "F309 local-drive read return")

    final = (
        "        nRes = HandleRecoverableError(nRes);\n"
        "        if (nRes != ERetry)\n"
        "            break;\n"
        "    }\n"
        "    return nRes;\n"
        "}\n"
        "#endif\n"
    )
    final_stage = (
        "        nRes = HandleRecoverableError(nRes);\n"
        "        if (nRes != ERetry)\n"
        "            break;\n"
        "    }\n"
        "    if (aTrace->iPhase == 1u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf30a0000u |\n"
        "            (TUint32(nRes) & 0xffffu));\n"
        "        aTrace->iPhase = 2u;\n"
        "        }\n"
        "    return nRes;\n"
        "}\n"
        "#endif\n"
    )
    return replace_once(text, final, final_stage, "F30A noncritical read return")


def transform_fat_mount(text: str) -> str:
    return replace_once(
        text,
        "    htcleoTrace.iMarker = 0x46445244u;\n",
        "    htcleoTrace.iMarker = 0x46445244u;\n"
        "    htcleoTrace.iPhase = 0u;\n",
        "initialise FAT caller phase",
    )


def verify(files: dict[str, str]) -> None:
    joined = "\n".join(files.values())
    if files["mmc_header"].count(MARKER) != 1:
        raise SystemExit("V26 MMC marker missing or duplicated")
    if files["fat_header"].count(FAT_MARKER) != 1:
        raise SystemExit("V26 FAT marker missing or duplicated")
    upgraded = V27_MARKER in files["fat_header"]
    if upgraded:
        if any(f"0xf30{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V27 marker exists but retired F301-F30A stage remains")
    else:
        for suffix in "123456789a":
            stage = f"0xf30{suffix}0000u"
            if joined.count(stage) != 1:
                raise SystemExit(f"F3 checkpoint missing or duplicated: {stage}")
    if any(f"0xf20{suffix}0000u" in joined for suffix in "123456789a"):
        raise SystemExit("retired F201-F20A screen stage remains")
    if not upgraded:
        expected = {
            "sdcard": 1,
            "stack": 2,
            "medmmc": 4,
            "locmedia": 1,
            "fat_drv": 2,
        }
        for name, count in expected.items():
            if files[name].count("0xf30") != count:
                raise SystemExit(f"{name}: expected {count} F3 checkpoints")
    if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("verified explicit CMD12 repair was lost")
    if files["fat_header"].count("TUint32 iPhase;") != 1:
        raise SystemExit("caller-local FAT return phase missing")
    if files["fat_mount"].count("htcleoTrace.iPhase = 0u;") != 1:
        raise SystemExit("caller-local FAT return phase is not initialized once")
    if files["medmmc"].count(RETURN_FLAG) < 2 or files["locmedia"].count(RETURN_FLAG) < 2:
        raise SystemExit("kernel completion return attribution flag missing")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART final UDF invariant failed")
    if "static volatile" in "\n".join(
        files[name] for name in ("sdcard", "stack", "medmmc", "locmedia", "fat_drv")
    ):
        raise SystemExit("forbidden global trace phase introduced")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "mmc_header": root / "kernel/eka/include/drivers/mmc.h",
        "fat_header": root / "userlibandfileserver/fileserver/sfat32/sl_cache.h",
        "fat_drv": root / "userlibandfileserver/fileserver/sfat32/sl_drv.cpp",
        "fat_mount": root / "userlibandfileserver/fileserver/sfat32/sl_mnt.cpp",
        "locmedia": root / "kernel/eka/drivers/locmedia/locmedia.cpp",
        "medmmc": root / "kernel/eka/drivers/medmmc/medmmc.cpp",
        "stack": root / "kernel/eka/drivers/pbus/mmc/stack.cpp",
        "sdcard": root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    if V25_MARKER not in files["mmc_header"]:
        raise SystemExit("V26 requires the verified V25 explicit CMD12 repair")
    if MARKER not in files["mmc_header"]:
        files["mmc_header"] = transform_mmc_header(files["mmc_header"])
        files["fat_header"] = transform_fat_header(files["fat_header"])
        files["sdcard"] = transform_sdcard(files["sdcard"])
        files["stack"] = transform_stack(files["stack"])
        files["medmmc"] = transform_medmmc(files["medmmc"])
        files["locmedia"] = transform_locmedia(files["locmedia"])
        files["fat_drv"] = transform_fat(files["fat_drv"])
        files["fat_mount"] = transform_fat_mount(files["fat_mount"])
    verify(files)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    if V27_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_POST_STOP_RETURN=preserved F301_F30A=retired-by-V27")
    else:
        print("HTCLEO_FAT_POST_STOP_RETURN_PROGRESS=10 F301_F30A=installed")


if __name__ == "__main__":
    main()
