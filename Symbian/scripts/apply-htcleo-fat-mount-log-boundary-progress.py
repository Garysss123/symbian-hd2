#!/usr/bin/env python3
"""Move the ten returning checkpoints from FAT label scan to BOOTLOG entry.

Iteration 387 proved the first C: root-directory label scan returned
KErrNotFound.  V28 retires only the F401-F40A display calls, preserving the
verified CMD12 repair, media/cache unwind and stack-local attribution.  The
new F501-F50A window follows the normal boot-sector-label fallback through the
C: mount return, TFSStartup::Run return and the E: volume-ready boundary just
before BOOTLOG Replace.  No persistent breadcrumb or extra I/O is introduced.
"""

from __future__ import annotations

import pathlib
import re
import sys


MARKER = "HTCLEO_FAT_MOUNT_LOG_BOUNDARY_PROGRESS_V28"
V27_MARKER = "HTCLEO_FAT_CACHE_UNWIND_PROGRESS_V27"
V29_MARKER = "HTCLEO_FAT_LOG_WRITER_ENTRY_PROGRESS_V29"
V30_MARKER = "HTCLEO_FAT_LOG_MOUNT_FALLBACK_PROGRESS_V30"
V31_MARKER = "HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31"
V32_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32"
V33_MARKER = "HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def retire_call(text: str, suffix: str) -> str:
    pattern = re.compile(
        rf"(?m)^[ \t]*HTCLEO_[A-Z0-9_]+\(0xf40{suffix}0000u\s*\|"
        rf".*?\);\n",
        re.DOTALL,
    )
    text, count = pattern.subn("", text)
    if count != 1:
        raise SystemExit(
            f"retire F40{suffix.upper()}: expected one display call, found {count}"
        )
    return text


def transform_header(text: str) -> str:
    anchor = (
        "/* HTCLEO_FAT_CACHE_UNWIND_PROGRESS_V27: "
        "phases 2-11 trace cache and first label unwind. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"/* {MARKER}: label fallback through E: BOOTLOG readiness. */\n",
        "V28 FAT/log marker",
    )


def retire_dynamic(text: str) -> str:
    for suffix in "123456":
        text = retire_call(text, suffix)
    return text


def transform_mount(text: str) -> str:
    for suffix in "789":
        text = retire_call(text, suffix)

    old_f40a = (
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (DriveNumber() == EDriveC && State() == EInit_R)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf40a0000u |\n"
        "            (TUint32(r) & 0xffffu));\n"
        "#endif\n"
    )
    text = replace_once(text, old_f40a, "", "retire F40A")

    fallback = (
        "    TInt r = ReadVolumeLabelFile(volName8);\n"
        "    if(r != KErrNone)   // No volume label file in root directory\n"
        "        volName8 = aBootSector.VolumeLabel();\n"
        "    TrimVolumeLabel(volName8);\n\n"
        "    TBuf16<KVolumeLabelSize> volName16;\n"
        "    LocaleUtils::ConvertToUnicodeL(volName16, volName8);\n"
        "    SetVolumeName(volName16.AllocL());\n"
    )
    progress = (
        "    TInt r = ReadVolumeLabelFile(volName8);\n"
        "    if(r != KErrNone)   // No volume label file in root directory\n"
        "        volName8 = aBootSector.VolumeLabel();\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (DriveNumber() == EDriveC && State() == EInit_R)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf5010000u |\n"
        "            (TUint32(r) & 0xffffu));\n"
        "#endif\n"
        "    TrimVolumeLabel(volName8);\n\n"
        "    TBuf16<KVolumeLabelSize> volName16;\n"
        "    LocaleUtils::ConvertToUnicodeL(volName16, volName8);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (DriveNumber() == EDriveC && State() == EInit_R)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf5020000u |\n"
        "            (TUint32(volName16.Length()) & 0xffffu));\n"
        "#endif\n"
        "    SetVolumeName(volName16.AllocL());\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (DriveNumber() == EDriveC && State() == EInit_R)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf5030000u |\n"
        "            (TUint32(volName16.Length()) & 0xffffu));\n"
        "#endif\n"
    )
    return replace_once(text, fallback, progress, "F501-F503 label fallback")


def transform_mount32(text: str) -> str:
    old = (
        "    GetVolumeLabelFromDiskL(bootSector);\n\n"
        "\t__PRINT2(_L(\"CFatMountCB::MountL() Completed, drv: %d, state:%d\"), DriveNumber(), State());\n"
    )
    new = (
        "    GetVolumeLabelFromDiskL(bootSector);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (DriveNumber() == EDriveC && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xf5040000u |\n"
        "            ((TUint32(State()) & 0xffu) << 8) |\n"
        "            (TUint32(DriveNumber()) & 0xffu));\n"
        "#endif\n\n"
        "\t__PRINT2(_L(\"CFatMountCB::MountL() Completed, drv: %d, state:%d\"), DriveNumber(), State());\n"
    )
    return replace_once(text, old, new, "F504 FAT MountL return")


def reporter_block(marker: str, macro: str) -> str:
    return (
        "#include <u32hal.h>\n\n"
        f"/* {marker} */\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        f"#define {macro}(aStage) \\\n"
        "\tdo \\\n"
        "\t\t{ \\\n"
        "\t\tTUint32 htcleoProgressLocation; \\\n"
        "\t\tasm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\"); \\\n"
        "\t\t(void)UserSvr::HalFunction(EHalGroupPlatformSpecific1,2, \\\n"
        "\t\t\t(TAny*)htcleoProgressLocation,(TAny*)(TUint32)(aStage)); \\\n"
        "\t\t} while (0)\n"
        "#else\n"
        f"#define {macro}(aStage) do {{ }} while (0)\n"
        "#endif\n"
    )


def transform_sf_drv(text: str) -> str:
    text = replace_once(
        text,
        '#include "sf_file_cache.h"\n',
        '#include "sf_file_cache.h"\n'
        + reporter_block(
            "HTCLEO_EFILE_MOUNT_LOG_BOUNDARY_DRV_V28",
            "HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS",
        ),
        "EFILE drive reporter",
    )
    old = (
        "    apMount->MountL(aForceMount);      //-- mount the file system  \n"
        "\tMount().AddL(apMount,EFalse);      //-- add mount object to the mounts container.  \n\n"
        "\tiCurrentMount=apMount;\n"
    )
    new = (
        "    apMount->MountL(aForceMount);      //-- mount the file system  \n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "    if (DriveNumber() == EDriveC && !aForceMount)\n"
        "        HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf5050000u |\n"
        "            (TUint32(DriveNumber()) & 0xffffu));\n"
        "#endif\n"
        "\tMount().AddL(apMount,EFalse);      //-- add mount object to the mounts container.  \n\n"
        "\tiCurrentMount=apMount;\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "    if (DriveNumber() == EDriveC && !aForceMount)\n"
        "        HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf5060000u |\n"
        "            (iCurrentMount ? 0x8000u : 0u) |\n"
        "            (TUint32(DriveNumber()) & 0xffu));\n"
        "#endif\n"
    )
    return replace_once(text, old, new, "F505-F506 EFILE mount return")


def transform_sf_sys(text: str) -> str:
    text = replace_once(
        text,
        '#include "sf_file_cache.h"\n',
        '#include "sf_file_cache.h"\n'
        + reporter_block(
            "HTCLEO_EFILE_MOUNT_LOG_BOUNDARY_SYS_V28",
            "HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS",
        ),
        "EFILE request reporter",
    )
    old = "\tTInt r=DoMountFileSystem(aRequest);\n\tif( KErrNone == r )\n"
    new = (
        "\tTInt r=DoMountFileSystem(aRequest);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (aRequest->Message().Int1() == EDriveC &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf5070000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n"
        "#endif\n"
        "\tif( KErrNone == r )\n"
    )
    return replace_once(text, old, new, "F507 EFILE request return")


def transform_estart(text: str) -> str:
    old = (
        "\t\telse\n"
        "\t\t\tr=iFs.MountFileSystem(objname,drive,isSync);\n"
        "\t\t\t\t\n"
        "\t\tDEBUGPRINT4(\"MountFileSystem(%S) on drive %c: -> %d (sync=%d)\",&objname,(drive+'A'),r,isSync);\n"
    )
    new = (
        "\t\telse\n"
        "\t\t\tr=iFs.MountFileSystem(objname,drive,isSync);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (drive == EDriveC)\n"
        "\t\t\tHTCLEO_ESTART_PROGRESS(0xf5080000u |\n"
        "\t\t\t\t(TUint32(r) & 0xffffu));\n"
        "#endif\n"
        "\t\t\t\t\n"
        "\t\tDEBUGPRINT4(\"MountFileSystem(%S) on drive %c: -> %d (sync=%d)\",&objname,(drive+'A'),r,isSync);\n"
    )
    return replace_once(text, old, new, "F508 ESTART C mount return")


def transform_estart_main(text: str) -> str:
    volume = (
        "\tfor (TInt retry=0; retry<100; ++retry)\n"
        "\t\t{\n"
        "\t\tvolumeResult=fs.Volume(volume,EDriveE);\n"
        "\t\tif (volumeResult==KErrNone)\n"
        "\t\t\tbreak;\n"
        "\t\tUser::After(100000);\n"
        "\t\t}\n"
        "\tif (volumeResult!=KErrNone)\n"
    )
    volume_progress = (
        "\tfor (TInt retry=0; retry<100; ++retry)\n"
        "\t\t{\n"
        "\t\tvolumeResult=fs.Volume(volume,EDriveE);\n"
        "\t\tif (volumeResult==KErrNone)\n"
        "\t\t\tbreak;\n"
        "\t\tUser::After(100000);\n"
        "\t\t}\n"
        "\tHTCLEO_ESTART_PROGRESS(0xf50a0000u |\n"
        "\t\t(TUint32(volumeResult) & 0xffffu));\n"
        "\tif (volumeResult!=KErrNone)\n"
    )
    text = replace_once(text, volume, volume_progress, "F50A E volume result")
    run = "\tfsStart.Run();\n\n\tconst TInt htcleoFatLogResult=HtcleoWriteFatBootRecord();\n"
    run_progress = (
        "\tfsStart.Run();\n"
        "\tHTCLEO_ESTART_PROGRESS(0xf5090000u);\n\n"
        "\tconst TInt htcleoFatLogResult=HtcleoWriteFatBootRecord();\n"
    )
    return replace_once(text, run, run_progress, "F509 Run return")


def verify(files: dict[str, str]) -> None:
    joined = "\n".join(files.values())
    if files["fat_header"].count(MARKER) != 1:
        raise SystemExit("V28 marker missing or duplicated")
    if any(f"0xf40{suffix}0000u" in joined for suffix in "123456789a"):
        raise SystemExit("retired F401-F40A display stage remains")
    if V31_MARKER in files["fat_header"]:
        if any(f"0xf50{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V31 marker exists but retired F501-F50A stage remains")
        if any(f"0xf60{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V31 marker exists but retired F601-F60A stage remains")
        if any(f"0xf70{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V31 marker exists but retired F701-F70A stage remains")
        if V33_MARKER in files["fat_header"]:
            if "0xf80" in joined or "0xf90" in joined:
                raise SystemExit("V33 marker exists but retired F8/F9 stage remains")
            if joined.count("0xfa1") != 10:
                raise SystemExit("V33 EFAT32 MountL checkpoint count is not ten")
        elif V32_MARKER in files["fat_header"]:
            if "0xf80" in joined:
                raise SystemExit("V32 marker exists but retired F801-F80A stage remains")
            if joined.count("0xf90") != 10:
                raise SystemExit("V32 EFILE remount checkpoint count is not ten")
        else:
            for suffix in "123456789a":
                if files["estart_main"].count(f"0xf80{suffix}0000u") != 1:
                    raise SystemExit("V31 remount-recovery checkpoint is missing or duplicated")
            if files["estart_main"].count("0xf80") != 10:
                raise SystemExit("V31 remount-recovery checkpoint count is not ten")
        if "User::After(100000);" in files["estart_main"]:
            raise SystemExit("V31 hardware-blocked retry delay remains")
        if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
            raise SystemExit("verified explicit CMD12 repair was lost")
        if joined.count("0xe7f000f0") != 1:
            raise SystemExit("durable ESTART final UDF invariant failed")
        if "static volatile" in joined:
            raise SystemExit("forbidden persistent breadcrumb introduced")
        return
    if V30_MARKER in files["fat_header"]:
        if any(f"0xf50{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V30 marker exists but retired F501-F50A stage remains")
        if any(f"0xf60{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V30 marker exists but retired F601-F60A stage remains")
        for suffix in "123456789a":
            if files["estart_main"].count(f"0xf70{suffix}0000u") != 1:
                raise SystemExit("V30 mount-fallback checkpoint is missing or duplicated")
        if files["estart_main"].count("0xf70") != 10:
            raise SystemExit("V30 mount-fallback checkpoint count is not ten")
        if "User::After(100000);" in files["estart_main"]:
            raise SystemExit("V30 hardware-blocked retry delay remains")
        if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
            raise SystemExit("verified explicit CMD12 repair was lost")
        if joined.count("0xe7f000f0") != 1:
            raise SystemExit("durable ESTART final UDF invariant failed")
        if "static volatile" in joined:
            raise SystemExit("forbidden persistent breadcrumb introduced")
        return
    if V29_MARKER in files["fat_header"]:
        if any(f"0xf50{suffix}0000u" in joined for suffix in "123456789a"):
            raise SystemExit("V29 marker exists but retired F501-F50A stage remains")
        for suffix in "123456789a":
            if files["estart_main"].count(f"0xf60{suffix}0000u") != 1:
                raise SystemExit("V29 writer-entry checkpoint is missing or duplicated")
        if files["estart_main"].count("0xf60") != 10:
            raise SystemExit("V29 writer-entry checkpoint count is not ten")
        if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
            raise SystemExit("verified explicit CMD12 repair was lost")
        if joined.count("0xe7f000f0") != 1:
            raise SystemExit("durable ESTART final UDF invariant failed")
        if "static volatile" in joined:
            raise SystemExit("forbidden persistent breadcrumb introduced")
        return
    for suffix in "123456789a":
        stage = f"0xf50{suffix}0000u"
        if joined.count(stage) != 1:
            raise SystemExit(f"F5 checkpoint missing or duplicated: {stage}")
    expected = {
        "fat_mount": 3,
        "fat_mount32": 1,
        "efile_drv": 2,
        "efile_sys": 1,
        "estart": 1,
        "estart_main": 2,
    }
    for name, count in expected.items():
        if files[name].count("0xf50") != count:
            raise SystemExit(f"F5 distribution mismatch in {name}")
    if files["fat_dynamic"].count("0xf50") != 0:
        raise SystemExit("F5 checkpoint leaked into retired dynamic-cache window")
    if files["sdcard"].count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("verified explicit CMD12 repair was lost")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART final UDF invariant failed")
    if "static volatile" in joined:
        raise SystemExit("forbidden persistent breadcrumb introduced")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "fat_header": root / "userlibandfileserver/fileserver/sfat32/sl_cache.h",
        "fat_dynamic": root / "userlibandfileserver/fileserver/sfat32/sl_dir_cache.cpp",
        "fat_mount": root / "userlibandfileserver/fileserver/sfat32/sl_mnt.cpp",
        "fat_mount32": root / "userlibandfileserver/fileserver/sfat32/sl_mnt32.cpp",
        "efile_drv": root / "userlibandfileserver/fileserver/sfile/sf_drv.cpp",
        "efile_sys": root / "userlibandfileserver/fileserver/sfile/sf_sys.cpp",
        "estart": root / "userlibandfileserver/fileserver/estart/estart.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
        "sdcard": root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    if V27_MARKER not in files["fat_header"]:
        raise SystemExit("V28 requires installed V27 cache-unwind attribution")
    if MARKER not in files["fat_header"]:
        files["fat_header"] = transform_header(files["fat_header"])
        files["fat_dynamic"] = retire_dynamic(files["fat_dynamic"])
        files["fat_mount"] = transform_mount(files["fat_mount"])
        files["fat_mount32"] = transform_mount32(files["fat_mount32"])
        files["efile_drv"] = transform_sf_drv(files["efile_drv"])
        files["efile_sys"] = transform_sf_sys(files["efile_sys"])
        files["estart"] = transform_estart(files["estart"])
        files["estart_main"] = transform_estart_main(files["estart_main"])
    verify(files)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    if V33_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_MOUNT_LOG_BOUNDARY=preserved F501_F50A=retired-by-V33")
    elif V32_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_MOUNT_LOG_BOUNDARY=preserved F501_F50A=retired-by-V32")
    elif V31_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_MOUNT_LOG_BOUNDARY=preserved F501_F50A=retired-by-V31")
    elif V30_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_MOUNT_LOG_BOUNDARY=preserved F501_F50A=retired-by-V30")
    elif V29_MARKER in files["fat_header"]:
        print("HTCLEO_FAT_MOUNT_LOG_BOUNDARY=preserved F501_F50A=retired-by-V29")
    else:
        print("HTCLEO_FAT_MOUNT_LOG_BOUNDARY=10 F501_F50A=installed")


if __name__ == "__main__":
    main()
