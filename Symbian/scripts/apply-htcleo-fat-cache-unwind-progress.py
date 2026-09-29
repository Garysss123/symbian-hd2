#!/usr/bin/env python3
"""Trace the proven tagged FAT read through cache and volume-label unwind.

Iteration 386 proved that the exact first C: volume-label 16 KiB physical read
returned to EFAT32 with KErrNone.  V27 retires every F301-F30A screen call while
preserving the verified CMD12 repair, kernel completion chain and stack-local
trace phase.  F401-F40A then cover only the remaining dynamic-cache, directory
entry and first volume-label scan return path.  No persistent breadcrumb is
introduced.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_CACHE_UNWIND_PROGRESS_V27"
V26_MARKER = "HTCLEO_FAT_POST_STOP_USER_RETURN_PROGRESS_V26"
V28_MARKER = "HTCLEO_FAT_MOUNT_LOG_BOUNDARY_PROGRESS_V28"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transform_header(text: str) -> str:
    anchor = (
        "/* HTCLEO_FAT_POST_STOP_USER_RETURN_PROGRESS_V26: "
        "caller-local phase follows the tagged read return. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"/* {MARKER}: phases 2-11 trace cache and first label unwind. */\n",
        "V27 FAT trace marker",
    )


def retire_sdcard(text: str) -> str:
    old = (
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
    new = (
        "\t\tif (s.HtcleoFatPhysicalReadTraceAt(39u))\n"
        "\t\t\t{\n"
        "\t\t\tconst TBool htcleoStatusError = TMMCStatus(s.ResponseP()).Error() != 0;\n"
        "\t\t\tif (!htcleoStatusError)\n"
        "\t\t\t\ts.HtcleoAdvanceFatPhysicalReadTrace(40u);\n"
        "\t\t\telse\n"
        "\t\t\t\ts.HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t}\n"
    )
    return replace_once(text, old, new, "retire F301")


def retire_stack(text: str) -> str:
    old_dispatch = (
        "\tif (iSessionP->HtcleoFatPhysicalReadTraceAt(40u))\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xf3020000u |\n"
        "\t\t\t(TUint32(exitCode) & 0xffffu));\n"
        "\t\tif ((exitCode & ~KMMCErrBypass) == KMMCErrNone)\n"
        "\t\t\tiSessionP->HtcleoAdvanceFatPhysicalReadTrace(41u);\n"
        "\t\telse\n"
        "\t\t\tiSessionP->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t}\n"
    )
    new_dispatch = (
        "\tif (iSessionP->HtcleoFatPhysicalReadTraceAt(40u))\n"
        "\t\t{\n"
        "\t\tif ((exitCode & ~KMMCErrBypass) == KMMCErrNone)\n"
        "\t\t\tiSessionP->HtcleoAdvanceFatPhysicalReadTrace(41u);\n"
        "\t\telse\n"
        "\t\t\tiSessionP->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t}\n"
    )
    text = replace_once(text, old_dispatch, new_dispatch, "retire F302")
    old_callback = (
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
    )
    new_callback = (
        "\t\t\t\tif (sessP->HtcleoFatPhysicalReadTraceAt(41u))\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tconst TInt htcleoResult = sessP->EpocErrorCode();\n"
        "\t\t\t\t\tif (htcleoResult == KErrNone)\n"
        "\t\t\t\t\t\tsessP->HtcleoAdvanceFatPhysicalReadTrace(42u);\n"
        "\t\t\t\t\telse\n"
        "\t\t\t\t\t\tsessP->HtcleoClearFatPhysicalReadTrace();\n"
        "\t\t\t\t\t}\n"
    )
    return replace_once(text, old_callback, new_callback, "retire F303")


def retire_medmmc(text: str) -> str:
    replacements = (
        (
            "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3040000u |\n"
            "\t\t\t(TUint32(htcleoResult) & 0xffffu));\n",
            "",
            "retire F304",
        ),
        (
            "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3050000u |\n"
            "\t\t\t\t(htcleoRead ? 0x8000u : 0u) |\n"
            "\t\t\t\t(TUint32(r) & 0x7fffu));\n",
            "",
            "retire F305",
        ),
        (
            "\t\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3060000u |\n"
            "\t\t\t\t\t\t(TUint32(r) & 0xffffu));\n",
            "",
            "retire F306",
        ),
        (
            "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3070000u |\n"
            "\t\t\t(complete ? 0x8000u : 0u) |\n"
            "\t\t\t(htcleoRead ? 0x4000u : 0u) |\n"
            "\t\t\t(TUint32(r) & 0x3fffu));\n",
            "",
            "retire F307",
        ),
    )
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)
    return text


def retire_locmedia(text: str) -> str:
    old = (
        "\tif (htcleoTaggedReturn)\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xf3080000u |\n"
        "\t\t\t(TUint32(aResult) & 0xffffu));\n"
    )
    return replace_once(
        text, old, "\t(void)htcleoTaggedReturn;\n", "retire F308"
    )


def retire_fat_driver(text: str) -> str:
    old_f309 = (
        "    if (aTrace->iPhase == 0u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf3090000u |\n"
        "            (TUint32(nRes) & 0xffffu));\n"
        "        aTrace->iPhase = 1u;\n"
        "        }\n"
    )
    new_f309 = (
        "    if (aTrace->iPhase == 0u)\n"
        "        aTrace->iPhase = 1u;\n"
    )
    text = replace_once(text, old_f309, new_f309, "retire F309")
    old_f30a = (
        "    if (aTrace->iPhase == 1u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf30a0000u |\n"
        "            (TUint32(nRes) & 0xffffu));\n"
        "        aTrace->iPhase = 2u;\n"
        "        }\n"
    )
    new_f30a = (
        "    if (aTrace->iPhase == 1u)\n"
        "        aTrace->iPhase = 2u;\n"
    )
    return replace_once(text, old_f30a, new_f30a, "retire F30A")


def transform_dynamic_cache(text: str) -> str:
    read_return = (
        "#else\n"
        "    const TInt nErr = iDrive.ReadNonCritical(activePage->iStartMedPos, iPageSizeInBytes, dataPtr);\n"
        "#endif\n\n"
    )
    read_return_stage = read_return + (
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "        aHtcleoTrace->iPhase == 2u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4010000u |\n"
        "            (TUint32(nErr) & 0xffffu));\n"
        "        if (nErr == KErrNone)\n"
        "            aHtcleoTrace->iPhase = 3u;\n"
        "        else\n"
        "            aHtcleoTrace->iMarker = 0u;\n"
        "        }\n"
        "#endif\n\n"
    )
    text = replace_once(text, read_return, read_return_stage, "F401 media return")

    lookup = (
        "\tiLockedQ.AddLast(*activePage);\n"
        "\tLookupTblAdd(activePage);\n"
        "    if(nErr != KErrNone)\n"
    )
    lookup_stage = (
        "\tiLockedQ.AddLast(*activePage);\n"
        "\tLookupTblAdd(activePage);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "        aHtcleoTrace->iPhase == 3u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4020000u |\n"
        "            (TUint32(nErr) & 0xffffu));\n"
        "        aHtcleoTrace->iPhase = 4u;\n"
        "        }\n"
        "#endif\n"
        "    if(nErr != KErrNone)\n"
    )
    text = replace_once(text, lookup, lookup_stage, "F402 lookup restore")

    valid = (
        "    activePage->SetValid(ETrue);\n"
        "    return activePage;\n"
    )
    valid_stage = (
        "    activePage->SetValid(ETrue);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "        aHtcleoTrace->iPhase == 4u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4030000u |\n"
        "            (activePage->IsValid() ? 0x8000u : 0u) |\n"
        "            (iPageSizeInBytes & 0x7fffu));\n"
        "        aHtcleoTrace->iPhase = 5u;\n"
        "        }\n"
        "#endif\n"
        "    return activePage;\n"
    )
    text = replace_once(text, valid, valid_stage, "F403 page valid")

    caller = (
        "        pPage = UpdateActivePageL(aPos HTCLEO_FAT_TRACE_ARG);\n"
        "        aDes.Append(pPage->PtrInPage(aPos), aLength);\n"
    )
    caller_stage = (
        "        pPage = UpdateActivePageL(aPos HTCLEO_FAT_TRACE_ARG);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "        if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "            aHtcleoTrace->iPhase == 5u)\n"
        "            {\n"
        "            HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4040000u |\n"
        "                (pPage ? 0x8000u : 0u) |\n"
        "                (TUint32(aLength) & 0x7fffu));\n"
        "            aHtcleoTrace->iPhase = 6u;\n"
        "            }\n"
        "#endif\n"
        "        aDes.Append(pPage->PtrInPage(aPos), aLength);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "        if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "            aHtcleoTrace->iPhase == 6u)\n"
        "            {\n"
        "            HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4050000u |\n"
        "                (TUint32(aDes.Length()) & 0xffffu));\n"
        "            aHtcleoTrace->iPhase = 7u;\n"
        "            }\n"
        "#endif\n"
    )
    text = replace_once(text, caller, caller_stage, "F404/F405 caller unwind")

    wrapper = (
        "void CDynamicDirCache::HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace* aTrace)\n"
        "    {\n"
        "    HtcleoDoReadL(aPos, aLength, aDes, aTrace);\n"
        "    }\n"
    )
    wrapper_stage = (
        "void CDynamicDirCache::HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace* aTrace)\n"
        "    {\n"
        "    HtcleoDoReadL(aPos, aLength, aDes, aTrace);\n"
        "    if (aTrace && aTrace->iMarker == 0x46445244u && aTrace->iPhase == 7u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4060000u |\n"
        "            (TUint32(aDes.Length()) & 0xffffu));\n"
        "        aTrace->iPhase = 8u;\n"
        "        }\n"
        "    }\n"
    )
    return replace_once(text, wrapper, wrapper_stage, "F406 cache virtual return")


def transform_mount(text: str) -> str:
    dir_read = (
        "        htcleoDirCache->HtcleoTraceReadL(posAddr, aLength, aDes, aHtcleoTrace);\n"
        "        return;\n"
    )
    dir_read_stage = (
        "        htcleoDirCache->HtcleoTraceReadL(posAddr, aLength, aDes, aHtcleoTrace);\n"
        "        if (aHtcleoTrace->iPhase == 8u)\n"
        "            {\n"
        "            HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4070000u |\n"
        "                (TUint32(aDes.Length()) & 0xffffu));\n"
        "            aHtcleoTrace->iPhase = 9u;\n"
        "            }\n"
        "        return;\n"
    )
    text = replace_once(text, dir_read, dir_read_stage, "F407 DirRead return")

    entry_read = (
        "    DirReadL(aPos,KSizeOfFatDirEntry,buf HTCLEO_FAT_TRACE_ARG);\n"
        "    }\n"
    )
    entry_read_stage = (
        "    DirReadL(aPos,KSizeOfFatDirEntry,buf HTCLEO_FAT_TRACE_ARG);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "        aHtcleoTrace->iPhase == 9u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4080000u |\n"
        "            (aDirEntry.IsEndOfDirectory() ? 0x8000u : 0u) |\n"
        "            (aDirEntry.IsErased() ? 0x4000u : 0u) |\n"
        "            (aDirEntry.IsVFatEntry() ? 0x2000u : 0u) |\n"
        "            (TUint32(aDirEntry.Attributes()) & 0xffu));\n"
        "        aHtcleoTrace->iPhase = 10u;\n"
        "        }\n"
        "#endif\n"
        "    }\n"
    )
    text = replace_once(text, entry_read, entry_read_stage, "F408 directory entry")

    get_entry = (
        "    TBool bEntryOK=ETrue;\n"
        "    TRAPD(nErr, bEntryOK = DoGetDirEntryL(aPos, aDosEntry, aStartEntry, aLongFileName HTCLEO_FAT_TRACE_ARG));\n\n"
        "    if(nErr !=KErrNone)\n"
    )
    get_entry_stage = (
        "    TBool bEntryOK=ETrue;\n"
        "    TRAPD(nErr, bEntryOK = DoGetDirEntryL(aPos, aDosEntry, aStartEntry, aLongFileName HTCLEO_FAT_TRACE_ARG));\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u &&\n"
        "        aHtcleoTrace->iPhase == 10u)\n"
        "        {\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf4090000u |\n"
        "            (bEntryOK ? 0x8000u : 0u) |\n"
        "            (TUint32(nErr) & 0x7fffu));\n"
        "        aHtcleoTrace->iPhase = 11u;\n"
        "        }\n"
        "#endif\n\n"
        "    if(nErr !=KErrNone)\n"
    )
    text = replace_once(text, get_entry, get_entry_stage, "F409 GetDirEntry return")

    label = (
        "    TRAPD(r, FindVolumeLabelFileL(aLabel, pos, entry));\n"
        "    __PRINT1(_L(\"-CFatMountCB::ReadVolumeLabelFile: %d\"),r);\n"
    )
    label_stage = (
        "    TRAPD(r, FindVolumeLabelFileL(aLabel, pos, entry));\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (DriveNumber() == EDriveC && State() == EInit_R)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf40a0000u |\n"
        "            (TUint32(r) & 0xffffu));\n"
        "#endif\n"
        "    __PRINT1(_L(\"-CFatMountCB::ReadVolumeLabelFile: %d\"),r);\n"
    )
    return replace_once(text, label, label_stage, "F40A volume-label scan return")


def verify(files: dict[str, str]) -> None:
    joined = "\n".join(files.values())
    if files["fat_header"].count(MARKER) != 1:
        raise SystemExit("V27 FAT marker missing or duplicated")
    if any(f"0xf30{suffix}0000u" in joined for suffix in "123456789a"):
        raise SystemExit("retired F301-F30A screen stage remains")
    if V28_MARKER in files["fat_header"]:
        if any(f"0xf40{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V28 marker exists but retired F401-F40A stage remains")
        if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
            raise SystemExit("verified explicit CMD12 repair was lost")
        if files["fat_mount"].count("htcleoTrace.iPhase = 0u;") != 1:
            raise SystemExit("stack-local trace is not preserved exactly once")
        if joined.count("0xe7f000f0") != 1:
            raise SystemExit("durable ESTART final UDF invariant failed")
        return
    for suffix in "123456789a":
        stage = f"0xf40{suffix}0000u"
        if joined.count(stage) != 1:
            raise SystemExit(f"F4 checkpoint missing or duplicated: {stage}")
    if files["fat_dynamic"].count("0xf40") != 6:
        raise SystemExit("dynamic cache must contain F401-F406")
    if files["fat_mount"].count("0xf40") != 4:
        raise SystemExit("FAT mount must contain F407-F40A")
    for name in ("sdcard", "stack", "medmmc", "locmedia", "fat_drv"):
        if "0xf40" in files[name]:
            raise SystemExit(f"F4 checkpoint leaked into {name}")
    if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("verified explicit CMD12 repair was lost")
    if files["fat_mount"].count("htcleoTrace.iPhase = 0u;") != 1:
        raise SystemExit("stack-local trace is not initialized exactly once")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART final UDF invariant failed")
    if "static volatile" in "\n".join(
        files[name] for name in (
            "sdcard", "stack", "medmmc", "locmedia", "fat_drv",
            "fat_dynamic", "fat_mount",
        )
    ):
        raise SystemExit("forbidden persistent trace phase introduced")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "fat_header": root / "userlibandfileserver/fileserver/sfat32/sl_cache.h",
        "fat_drv": root / "userlibandfileserver/fileserver/sfat32/sl_drv.cpp",
        "fat_dynamic": root / "userlibandfileserver/fileserver/sfat32/sl_dir_cache.cpp",
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
    if V26_MARKER not in files["fat_header"]:
        raise SystemExit("V27 requires installed V26 post-stop return attribution")
    if MARKER not in files["fat_header"]:
        files["fat_header"] = transform_header(files["fat_header"])
        files["sdcard"] = retire_sdcard(files["sdcard"])
        files["stack"] = retire_stack(files["stack"])
        files["medmmc"] = retire_medmmc(files["medmmc"])
        files["locmedia"] = retire_locmedia(files["locmedia"])
        files["fat_drv"] = retire_fat_driver(files["fat_drv"])
        files["fat_dynamic"] = transform_dynamic_cache(files["fat_dynamic"])
        files["fat_mount"] = transform_mount(files["fat_mount"])
    verify(files)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    if V28_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_CACHE_UNWIND_PROGRESS=preserved F401_F40A=retired-by-V28")
    else:
        print("HTCLEO_FAT_CACHE_UNWIND_PROGRESS=10 F401_F40A=installed")


if __name__ == "__main__":
    main()
