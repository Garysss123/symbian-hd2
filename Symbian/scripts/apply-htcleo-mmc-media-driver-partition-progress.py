#!/usr/bin/env python3
"""Trace the post-EC0A media-driver path through initial ECaps completion.

Iteration 373 reached EC0A exactly, proving the second MMC initialisation,
PBUS power-up and the synchronous part of StartOpenMediaDrivers all returned.
Retire EC01-EC0A and install ten returning ED01-ED0A checkpoints strictly after
that boundary: asynchronous media-driver attachment, partition discovery,
    local-drive mapping and completion of the first ECaps message.
The only physical UDF remains the durable FAT-log boundary in ESTART.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12"
DRAFT_MARKER = "HTCLEO_MMC_MEDIA_DRIVER_PARTITION_PROGRESS_V13"
MARKER = "HTCLEO_MMC_POST_EC0A_PARTITION_ECAPS_PROGRESS_V14"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def reporter(stage: str, gate: str, indent: str = "\t") -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if ({gate})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0x{stage.lower()}0000u);\n"
        "#endif\n"
    )


def dynamic_reporter(
    stage: str, value: str, gate: str, indent: str = "\t"
) -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if ({gate})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0x{stage.lower()}0000u | "
        f"(TUint32({value}) & 0xffffu));\n"
        "#endif\n"
    )


def old_powerup_reporter(stage: str, phase: int, indent: str) -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == {phase})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u);\n"
        "#endif\n"
    )


def old_dynamic_powerup_reporter(
    stage: str, value: str, phase: int, indent: str
) -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == {phase})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u | "
        f"(TUint32({value}) & 0xffffu));\n"
        "#endif\n"
    )


def migrate_estart(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        if OLD_MARKER in text or DRAFT_MARKER in text:
            raise SystemExit("older and V14 ESTART markers coexist")
        return
    if DRAFT_MARKER in text:
        text = replace_once(text, DRAFT_MARKER, MARKER, "ESTART draft-to-V14 marker")
    else:
        text = replace_once(text, OLD_MARKER, MARKER, "ESTART V12-to-V14 marker")
    path.write_text(text, encoding="utf-8")


def retire_ec_stack(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    for stage, indent in (
        ("EC01", "\t\t"),
        ("EC02", "\t\t"),
        ("EC03", "\t\t"),
        ("EC04", "\t\t\t"),
        ("EC05", "\t"),
    ):
        block = (
            old_dynamic_powerup_reporter(stage, "epocErr", 7, indent)
            if stage == "EC05"
            else old_powerup_reporter(stage, 7, indent)
        )
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} stack reporter")

    ec0a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 7)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0a0000u);\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    disarm = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 7)\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "#endif\n"
    )
    if ec0a in text:
        text = replace_once(text, ec0a, disarm, "retire EC0A")
    elif "0xec0a0000u" in text:
        raise SystemExit("unrecognized EC0A stack reporter")
    elif disarm not in text:
        raise SystemExit("EC0A disarm boundary is absent")
    path.write_text(text, encoding="utf-8")


def retire_ec_spbus(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    block = old_dynamic_powerup_reporter("EC06", "anError", 7, "\t")
    if block in text:
        text = replace_once(text, block, "", "retire EC06")
    elif "0xec060000u" in text:
        raise SystemExit("unrecognized EC06 spbus reporter")
    path.write_text(text, encoding="utf-8")


def retire_ec_pbusmedia(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    block = old_dynamic_powerup_reporter(
        "EC07", "anError", 7, "\t\t\t\t\t"
    )
    if block in text:
        text = replace_once(text, block, "", "retire EC07")
    elif "0xec070000u" in text:
        raise SystemExit("unrecognized EC07 pbusmedia reporter")
    path.write_text(text, encoding="utf-8")


def retire_ec_locmedia(text: str) -> str:
    ec08 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstCapsMediaOpenTrace == 1)\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec080000u | "
        "(TUint32(anError) & 0xffffu));\n"
        "#endif\n"
    )
    if ec08 in text:
        text = replace_once(text, ec08, "", "retire EC08")
    elif "0xec080000u" in text:
        raise SystemExit("unrecognized EC08 locmedia reporter")

    ec09 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 1)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec090000u);\n"
        "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 2;\n"
        "\t\t\t}\n"
        "#endif\n"
    )
    promote = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 1)\n"
        "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 2;\n"
        "#endif\n"
    )
    if ec09 in text:
        text = replace_once(text, ec09, promote, "retire/promote EC09")
    elif "0xec090000u" in text:
        raise SystemExit("unrecognized EC09 locmedia reporter")
    elif promote not in text:
        raise SystemExit("EC09 promotion boundary is absent")
    return text


def install_locmedia(path: pathlib.Path) -> None:
    text = retire_ec_locmedia(path.read_text(encoding="utf-8"))
    # V12 named the shared framebuffer helper after the old power-up window.
    # V14 reuses it later, so migrate both the enabled and disabled definitions
    # before the idempotence return below.
    text = text.replace(
        "#define HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(aStage)",
        "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage)",
    )
    if text.count("#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage)") != 2:
        raise SystemExit("locmedia returning reporter helper is not defined twice")
    # Remove the never-built V13 draft before installing the EC0A-strict map.
    for stage, value, anchor in (
        ("ED04", "anError", "DPRIMARYMEDIABASE_DOOPENMEDIADRIVERCOMPLETE_ENTRY"),
        ("ED08", "anError", "DPRIMARYMEDIABASE_DOPARTITIONINFOCOMPLETE_ENTRY"),
    ):
        block = dynamic_reporter(
            stage, value, "gHtcleoFirstCapsMediaOpenTrace == 2"
        )
        if block in text:
            text = replace_once(text, block, "", f"retire draft {stage} at {anchor}")
    draft_ed09 = dynamic_reporter(
        "ED09", "iTotalPartitionsOpened",
        "gHtcleoFirstCapsMediaOpenTrace == 2",
    )
    if draft_ed09 in text:
        text = replace_once(text, draft_ed09, "", "retire draft ED09")
    old = (
        "\tif (iCurrentReq)\n"
        "\t\t{\n"
        "\t\tDoRequest(*iCurrentReq);\t// this sets iCurrentReq=NULL\n"
        "\t\t}\n"
    )
    new = (
        "\tif (iCurrentReq)\n"
        "\t\t{\n"
        "\t\tDoRequest(*iCurrentReq);\t// this sets iCurrentReq=NULL\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 2)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0a0000u);\n"
        "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 3;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\t}\n"
    )
    if new in text:
        text = replace_once(text, new, old, "retire draft ED0A")
    elif "0xed0a0000u" in text and "TInt s=(r==KErrCompletion)" not in text:
        raise SystemExit("unrecognized draft ED0A locmedia reporter")

    if "HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed010000u" in text:
        path.write_text(text, encoding="utf-8")
        return

    opening_old = (
        "\tif (pM->iState==DMedia::EOpening)\n"
        "\t\tpM->DoOpenMediaDriverComplete(pM->iAsyncErrorCode);\n"
    )
    opening_new = (
        "\tif (pM->iState==DMedia::EOpening)\n"
        "\t\t{\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 2)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed010000u | "
        "(TUint32(pM->iAsyncErrorCode) & 0xffffu));\n"
        "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 3;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\tpM->DoOpenMediaDriverComplete(pM->iAsyncErrorCode);\n"
        "\t\t}\n"
    )
    text = replace_once(text, opening_old, opening_new, "ED01 opening DFC")
    text = replace_once(
        text,
        "\t\t++iMediaDriversOpened;\n"
        "\t\t}\n\n\t\n"
        "\t// if no error, read partition info on media\n",
        "\t\t++iMediaDriversOpened;\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 3)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed020000u);\n"
        "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 4;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\t}\n\n\t\n"
        "\t// if no error, read partition info on media\n",
        "ED02 media driver attached",
    )
    text = replace_once(
        text,
        "\tOstTraceFunctionEntry1( DPRIMARYMEDIABASE_DOPARTITIONINFOCOMPLETE_ENTRY, this );\n",
        "\tOstTraceFunctionEntry1( DPRIMARYMEDIABASE_DOPARTITIONINFOCOMPLETE_ENTRY, this );\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstCapsMediaOpenTrace == 4)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed080000u | "
        "(TUint32(anError) & 0xffffu));\n"
        "\t\tgHtcleoFirstCapsMediaOpenTrace = 5;\n"
        "\t\t}\n"
        "#endif\n",
        "ED08 partition callback",
    )
    text = replace_once(
        text,
        "\t// media is now ready - handle current or deferred requests\n"
        "\tMediaReadyHandleRequest();\n",
        "\t// media is now ready - handle current or deferred requests\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstCapsMediaOpenTrace == 5)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed090000u | "
        "(TUint32(iTotalPartitionsOpened) & 0xffffu));\n"
        "\t\tgHtcleoFirstCapsMediaOpenTrace = 6;\n"
        "\t\t}\n"
        "#endif\n"
        "\tMediaReadyHandleRequest();\n",
        "ED09 partition mapping complete",
    )
    text = replace_once(
        text,
        "\t\t\tCompleteRequest(m, s);\n"
        "\t\t\tOstTraceDefExt2( OST_TRACE_CATEGORY_RND, TRACE_INTERNALS, "
        "DPRIMARYMEDIABASE_DOREQUEST_RETURN, \"Return Remote Thread=0x%x; "
        "retval=%d\", (TUint) m.RemoteThread(), (TInt) s);\n",
        "\t\t\tCompleteRequest(m, s);\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\tif (m.Id() == DLocalDrive::ECaps && "
        "gHtcleoFirstCapsMediaOpenTrace == 6)\n"
        "\t\t\t\t{\n"
        "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0a0000u | "
        "(TUint32(s) & 0xffffu));\n"
        "\t\t\t\tgHtcleoFirstCapsMediaOpenTrace = 7;\n"
        "\t\t\t\t}\n"
        "#endif\n"
        "\t\t\tOstTraceDefExt2( OST_TRACE_CATEGORY_RND, TRACE_INTERNALS, "
        "DPRIMARYMEDIABASE_DOREQUEST_RETURN, \"Return Remote Thread=0x%x; "
        "retval=%d\", (TUint) m.RemoteThread(), (TInt) s);\n",
        "ED0A completed ECaps message",
    )
    path.write_text(text, encoding="utf-8")


def install_medmmc(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "gHtcleoFirstMmcMediaOpenTrace" not in text:
        text = replace_once(
            text,
            "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage) do { } while (0)\n"
            "#endif\n\n"
            "#include \"OstTraceDefinitions.h\"\n",
            "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage) do { } while (0)\n"
            "#endif\n\n"
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "static volatile TUint32 gHtcleoFirstMmcMediaOpenTrace = 0;\n"
            "#endif\n\n"
            "#include \"OstTraceDefinitions.h\"\n",
            "medmmc first-open gate",
        )

    create_entry = (
        "\tOstTraceExt2(TRACE_FLOW, DPHYSICALDEVICEMEDIAMMCFLASH_CREATE_ENTRY, "
        "\"DPhysicalDeviceMediaMmcFlash::Create;aMediaId=%d;this=%x\", "
        "aMediaId, (TUint) this);\n"
    )
    create_probe = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstMmcMediaOpenTrace == 0)\n"
        "\t\t{\n"
        "\t\tgHtcleoFirstMmcMediaOpenTrace = 1;\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed010000u);\n"
        "\t\t}\n"
        "#endif\n"
    )
    if create_probe in text:
        text = replace_once(text, create_probe, "", "retire draft ED01")

    create_original = (
        "\tif (pD)\n"
        "\t\tr=pD->DoCreate(aMediaId);\n"
        "\tif (r==KErrNone)\n"
        "\t\tpD->OpenMediaDriverComplete(KErrNone);\n"
    )
    create_draft = (
        "\tif (pD)\n"
        "\t\tr=pD->DoCreate(aMediaId);\n"
        + dynamic_reporter(
            "ED02", "r", "gHtcleoFirstMmcMediaOpenTrace == 1"
        )
        + "\tif (r==KErrNone)\n"
        "\t\t{\n"
        "\t\tpD->OpenMediaDriverComplete(KErrNone);\n"
        + reporter("ED03", "gHtcleoFirstMmcMediaOpenTrace == 1", "\t\t")
        + "\t\t}\n"
    )
    if create_draft in text:
        text = replace_once(
            text, create_draft, create_original, "retire draft ED02/ED03"
        )

    draft_ed05 = reporter("ED05", "gHtcleoFirstMmcMediaOpenTrace == 1")
    if draft_ed05 in text:
        text = replace_once(text, draft_ed05, "", "retire draft ED05")
    draft_ed06 = dynamic_reporter(
        "ED06", "r", "gHtcleoFirstMmcMediaOpenTrace == 1"
    )
    if draft_ed06 in text:
        text = replace_once(text, draft_ed06, "", "retire draft ED06")
    case_original = (
        "\t\t\tcase EMReqPtnInfo:\n"
        "\t\t\t\tif (r == KErrNone)\n"
        "\t\t\t\t\tr = DecodePartitionInfo();\t\t// set up iPartitionInfo\n\n"
        "\t\t\t\tPartitionInfoComplete(r == KErrNone?KErrNone:KErrNotReady);\n"
        "\t\t\t\tbreak;\n"
    )
    case_draft = (
        "\t\t\tcase EMReqPtnInfo:\n"
        "\t\t\t\tif (r == KErrNone)\n"
        "\t\t\t\t\tr = DecodePartitionInfo();\t\t// set up iPartitionInfo\n"
        + dynamic_reporter(
            "ED07", "r", "gHtcleoFirstMmcMediaOpenTrace == 1", "\t\t\t\t"
        )
        + "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\t\tif (gHtcleoFirstMmcMediaOpenTrace == 1)\n"
        "\t\t\t\t\tgHtcleoFirstMmcMediaOpenTrace = 2;\n"
        "#endif\n\n"
        "\t\t\t\tPartitionInfoComplete(r == KErrNone?KErrNone:KErrNotReady);\n"
        "\t\t\t\tbreak;\n"
    )
    if case_draft in text:
        text = replace_once(text, case_draft, case_original, "retire draft ED07")

    if "HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed030000u" in text:
        path.write_text(text, encoding="utf-8")
        return

    partition_entry = (
        "\tOstTraceFunctionEntry1( DMMCMEDIADRIVERFLASH_PARTITIONINFO_ENTRY, this );\n"
    )
    partition_probe = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstMmcMediaOpenTrace == 0)\n"
        "\t\t{\n"
        "\t\tgHtcleoFirstMmcMediaOpenTrace = 1;\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed030000u);\n"
        "\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text, partition_entry, partition_entry + partition_probe,
        "ED03 PartitionInfo entry",
    )
    text = replace_once(
        text,
        "\tTInt r = LaunchRPIRead();\n\n"
        "\t__KTRACE_OPT(KPBUSDRV, Kern::Printf(\"<mmd:rpi:%d\", r));\n",
        "\tTInt r = LaunchRPIRead();\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstMmcMediaOpenTrace == 1)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed040000u | "
        "(TUint32(r) & 0xffffu));\n"
        "\t\tgHtcleoFirstMmcMediaOpenTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
        + "\n\t__KTRACE_OPT(KPBUSDRV, Kern::Printf(\"<mmd:rpi:%d\", r));\n",
        "ED04 partition read launched",
    )
    text = replace_once(
        text,
        "\tmd.iSessionEndDfc.Enque();\n",
        "\tmd.iSessionEndDfc.Enque();\n"
        + "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstMmcMediaOpenTrace == 2 && "
        "md.CurrentRequest() == EMReqPtnInfo)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed050000u);\n"
        "\t\tgHtcleoFirstMmcMediaOpenTrace = 3;\n"
        "\t\t}\n"
        "#endif\n",
        "ED05 session callback queued",
    )
    text = replace_once(
        text,
        "\tif (iSession == NULL)\n"
        "\t\tr = KErrNotReady;\n\n"
        "\tTBool complete = ETrue;\n",
        "\tif (iSession == NULL)\n"
        "\t\tr = KErrNotReady;\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoFirstMmcMediaOpenTrace == 3 && "
        "CurrentRequest() == EMReqPtnInfo)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed060000u | "
        "(TUint32(r) & 0xffffu));\n"
        "\t\tgHtcleoFirstMmcMediaOpenTrace = 4;\n"
        "\t\t}\n"
        "#endif\n\n"
        "\tTBool complete = ETrue;\n",
        "ED06 partition-session preflight",
    )
    text = replace_once(
        text,
        case_original,
        "\t\t\tcase EMReqPtnInfo:\n"
        "\t\t\t\tif (r == KErrNone)\n"
        "\t\t\t\t\tr = DecodePartitionInfo();\t\t// set up iPartitionInfo\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\t\tif (gHtcleoFirstMmcMediaOpenTrace == 4)\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed070000u | "
        "(TUint32(r) & 0xffffu));\n"
        "\t\t\t\t\tgHtcleoFirstMmcMediaOpenTrace = 5;\n"
        "\t\t\t\t\t}\n"
        "#endif\n\n"
        "\t\t\t\tPartitionInfoComplete(r == KErrNone?KErrNone:KErrNotReady);\n"
        "\t\t\t\tbreak;\n",
        "ED07 partition decode result",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = {
        name: paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "medmmc", "pbusmedia", "spbus", "stack")
    }
    combined = "\n".join(sources.values())
    if (estart.count(MARKER) != 1 or OLD_MARKER in estart or
            DRAFT_MARKER in estart):
        raise SystemExit("V14 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0" in combined:
        raise SystemExit("a retired EC0x checkpoint remains")
    for index in range(1, 11):
        stage = f"ed0{index:x}"
        if combined.count(f"HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"media-driver/partition checkpoint missing: {stage}")
    if sources["locmedia"].count(
        "HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0"
    ) != 5:
        raise SystemExit("locmedia ED checkpoint count is not five")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS" in sources["locmedia"]:
        raise SystemExit("retired locmedia power-up reporter helper remains")
    if sources["medmmc"].count(
        "HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0"
    ) != 5:
        raise SystemExit("medmmc ED checkpoint count is not five")
    if any("HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0" in sources[name]
           for name in ("pbusmedia", "spbus", "stack")):
        raise SystemExit("an ED checkpoint escaped locmedia/medmmc")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in combined:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: apply-htcleo-mmc-media-driver-partition-progress.py "
            "KERNEL_SOURCE"
        )
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "estart": root / "userlibandfileserver/fileserver/estart/estart.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
        "locmedia": root / "kernel/eka/drivers/locmedia/locmedia.cpp",
        "medmmc": root / "kernel/eka/drivers/medmmc/medmmc.cpp",
        "pbusmedia": root / "kernel/eka/drivers/pbus/pbusmedia.cpp",
        "spbus": root / "kernel/eka/drivers/pbus/spbus.cpp",
        "stack": root / "kernel/eka/drivers/pbus/mmc/stack.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    migrate_estart(paths["estart"])
    retire_ec_stack(paths["stack"])
    retire_ec_spbus(paths["spbus"])
    retire_ec_pbusmedia(paths["pbusmedia"])
    install_locmedia(paths["locmedia"])
    install_medmmc(paths["medmmc"])
    verify(paths)
    print("HTCLEO_MMC_POST_EC0A_PARTITION_ECAPS_PROGRESS=10")


if __name__ == "__main__":
    main()
