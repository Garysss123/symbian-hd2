#!/usr/bin/env python3
"""Trace the exact E: FAT MountL failure reached by iteration 392.

Iteration 392 returned F90A9FEE: EFILE created and initialised the new mount,
then CFatMountCB::MountL left with KErrNotReady.  V33 retires all executable
F901-F90A EFILE checkpoints and places FA11-FA1A only in the EFAT32 MountL
implementation.  Every site is returning; the existing BOOTLOG-success UDF is
still the sole halting probe.

The checkpoints are gated per invocation by E: and !aForceMount.  The initial
boot-time E: attempt may therefore draw them, but the later ESTART recovery
attempt is guaranteed to overwrite that panel and its failure has no later E:
MountL call.  No process-global breadcrumb or persistent state is introduced.
"""

from __future__ import annotations

import pathlib
import sys


V32_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32"
V33_MARKER = "HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33"
SYS_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_SYS_V32"
DRV_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_DRV_V32"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def remove_probe_if_blocks(text: str) -> str:
    """Remove V32-only preprocessor blocks without touching V28 reporter defs."""

    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].startswith(
            "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)"
        ):
            depth = 1
            end = index + 1
            while end < len(lines) and depth:
                stripped = lines[end].lstrip()
                if stripped.startswith("#if"):
                    depth += 1
                elif stripped.startswith("#endif"):
                    depth -= 1
                end += 1
            if depth:
                raise SystemExit("unterminated low-ROM probe preprocessor block")
            block = "".join(lines[index:end])
            if "0xf90" in block or (
                "gHtcleoEstartERemountPhase = 0x100u;" in block
            ):
                index = end
                continue
        output.append(lines[index])
        index += 1
    return "".join(output)


def retire_v32_efile(sf_sys: str, sf_drv: str) -> tuple[str, str]:
    sys_gate = (
        f"/* {SYS_MARKER} */\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "volatile TUint32 gHtcleoEstartERemountPhase = 0;\n"
        "#endif\n"
    )
    drv_gate = (
        f"/* {DRV_MARKER} */\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "extern volatile TUint32 gHtcleoEstartERemountPhase;\n"
        "#endif\n"
    )
    sf_sys = replace_once(sf_sys, sys_gate, "", "retire V32 sf_sys gate")
    sf_drv = replace_once(sf_drv, drv_gate, "", "retire V32 sf_drv gate")
    sf_sys = remove_probe_if_blocks(sf_sys)
    sf_drv = remove_probe_if_blocks(sf_drv)

    sf_sys = replace_once(
        sf_sys,
        "\tTInt r=DoDismountFileSystem(name, drive, EFalse, EFalse);\n"
        "\treturn r;\n",
        "\treturn DoDismountFileSystem(name, drive, EFalse, EFalse);\n",
        "restore direct EFILE dismount return",
    )
    sf_drv = replace_once(
        sf_drv,
        "\t\tTBool htcleoRemounted=ReMount();\n"
        "\t\tif (!htcleoRemounted)\t    //\tHave we just remounted a mount we have previously encountered?\n",
        "\t\tif (!ReMount())\t    //\tHave we just remounted a mount we have previously encountered?\n",
        "restore stock ReMount branch",
    )
    return sf_sys, sf_drv


def transform_header(text: str) -> str:
    anchor = (
        f"/* {V32_MARKER}: exact post-dismount EFILE remount trace. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"/* {V33_MARKER}: exact E: EFAT32 MountL failure trace. */\n",
        "V33 header marker",
    )


def transform_mount32(text: str) -> str:
    old_entry = (
        "    const TInt driveNo = Drive().DriveNumber();\n"
        "    \n"
        "    __PRINT3(_L(\"CFatMountCB::MountL() drv:%d, forceMount=%d, RuggedFAT:%d\\n\"), driveNo, aForceMount, IsRuggedFSys());\n"
    )
    new_entry = (
        "    const TInt driveNo = Drive().DriveNumber();\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa110000u |\n"
        "            (TUint32(driveNo) & 0xffffu));\n"
        "#endif\n"
        "    \n"
        "    __PRINT3(_L(\"CFatMountCB::MountL() drv:%d, forceMount=%d, RuggedFAT:%d\\n\"), driveNo, aForceMount, IsRuggedFSys());\n"
    )
    text = replace_once(text, old_entry, new_entry, "FA11 MountL entry")

    old_create = (
        "\tTInt htcleoCreateDriveResult=CreateDrive(driveNo);\n"
        "\tUser::LeaveIfError(htcleoCreateDriveResult);\n"
    )
    new_create = (
        "\tTInt htcleoCreateDriveResult=CreateDrive(driveNo);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "\tif (driveNo == EDriveE && !aForceMount)\n"
        "\t\tHTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa120000u |\n"
        "\t\t\t(TUint32(htcleoCreateDriveResult) & 0xffffu));\n"
        "#endif\n"
        "\tUser::LeaveIfError(htcleoCreateDriveResult);\n"
    )
    text = replace_once(text, old_create, new_create, "FA12 CreateDrive result")

    old_driver = (
        "    const TBool htcleoDriverInit=iDriverInterface.Init(this);\n"
        "    if(!htcleoDriverInit)\n"
    )
    new_driver = (
        "    const TBool htcleoDriverInit=iDriverInterface.Init(this);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa130000u |\n"
        "            (htcleoDriverInit ? 0x8000u : 0u) |\n"
        "            (TUint32(driveNo) & 0xffu));\n"
        "#endif\n"
        "    if(!htcleoDriverInit)\n"
    )
    text = replace_once(text, old_driver, new_driver, "FA13 driver Init result")

    old_caps = (
        "\tTInt htcleoCapsResult=LocalDrive()->Caps(capsBuf);\n"
        "\tUser::LeaveIfError(htcleoCapsResult);\n"
    )
    new_caps = (
        "\tTInt htcleoCapsResult=LocalDrive()->Caps(capsBuf);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "\tif (driveNo == EDriveE && !aForceMount)\n"
        "\t\tHTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa140000u |\n"
        "\t\t\t(TUint32(htcleoCapsResult) & 0xffffu));\n"
        "#endif\n"
        "\tUser::LeaveIfError(htcleoCapsResult);\n"
    )
    text = replace_once(text, old_caps, new_caps, "FA14 local-drive Caps result")

    old_boot = (
        "    TFatBootSector bootSector;\n"
        "    TInt htcleoBootResult=ReadBootSector(bootSector, iRamDrive);\n"
        "    User::LeaveIfError(htcleoBootResult);\n"
    )
    new_boot = (
        "    TFatBootSector bootSector;\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa150000u |\n"
        "            (TUint32(driveNo) & 0xffffu));\n"
        "#endif\n"
        "    TInt htcleoBootResult=ReadBootSector(bootSector, iRamDrive);\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa160000u |\n"
        "            (TUint32(htcleoBootResult) & 0xffffu));\n"
        "#endif\n"
        "    User::LeaveIfError(htcleoBootResult);\n"
    )
    text = replace_once(text, old_boot, new_boot, "FA15/FA16 boot-sector read")

    old_init = (
        "    //-- initialize the volume\n"
        "    InitializeL(capsBuf());\n"
        "    ASSERT(State()==EInit_R);\n"
    )
    new_init = (
        "    //-- initialize the volume\n"
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa170000u |\n"
        "            (TUint32(driveNo) & 0xffffu));\n"
        "    TRAPD(htcleoInitializeResult, InitializeL(capsBuf()));\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa180000u |\n"
        "            (TUint32(htcleoInitializeResult) & 0xffffu));\n"
        "    User::LeaveIfError(htcleoInitializeResult);\n"
        "#else\n"
        "    InitializeL(capsBuf());\n"
        "#endif\n"
        "    ASSERT(State()==EInit_R);\n"
    )
    text = replace_once(text, old_init, new_init, "FA17/FA18 InitializeL")

    old_label = "    GetVolumeLabelFromDiskL(bootSector);\n"
    new_label = (
        "#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa190000u |\n"
        "            ((TUint32(State()) & 0xffu) << 8) |\n"
        "            (TUint32(driveNo) & 0xffu));\n"
        "    TRAPD(htcleoVolumeLabelResult, GetVolumeLabelFromDiskL(bootSector));\n"
        "    if (driveNo == EDriveE && !aForceMount)\n"
        "        HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfa1a0000u |\n"
        "            (TUint32(htcleoVolumeLabelResult) & 0xffffu));\n"
        "    User::LeaveIfError(htcleoVolumeLabelResult);\n"
        "#else\n"
        "    GetVolumeLabelFromDiskL(bootSector);\n"
        "#endif\n"
    )
    return replace_once(text, old_label, new_label, "FA19/FA1A volume label")


def verify(
    header: str,
    estart: str,
    sf_sys: str,
    sf_drv: str,
    mount32: str,
    sdcard: str,
) -> None:
    joined = "\n".join((header, estart, sf_sys, sf_drv, mount32, sdcard))
    if header.count(V33_MARKER) != 1:
        raise SystemExit("V33 marker missing or duplicated")
    if SYS_MARKER in joined or DRV_MARKER in joined:
        raise SystemExit("retired V32 EFILE phase marker remains")
    if "gHtcleoEstartERemountPhase" in joined or "0xf90" in joined:
        raise SystemExit("retired V32 EFILE executable checkpoint remains")
    for suffix in "123456789a":
        stage = f"0xfa1{suffix}0000u"
        if mount32.count(stage) != 1:
            raise SystemExit(f"FA1 checkpoint missing or duplicated: {stage}")
    if mount32.count("0xfa1") != 10 or joined.count("0xfa1") != 10:
        raise SystemExit("FA11-FA1A are not exactly ten EFAT32 checkpoints")
    if estart.count("fs.FileSystemName(") != 1:
        raise SystemExit("registered E: FSY query was lost")
    if estart.count("fs.DismountFileSystem(") != 1:
        raise SystemExit("verified E: dismount recovery was lost")
    if estart.count("fs.MountFileSystem(") != 1:
        raise SystemExit("verified E: remount recovery was lost")
    if "fileSystemName,EDriveE,EFalse" not in estart:
        raise SystemExit("E: remount target changed")
    if estart.count("fs.RemountDrive(") != 0:
        raise SystemExit("forbidden media/socket remount introduced")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable final UDF invariant failed")
    if "static volatile" in joined:
        raise SystemExit("forbidden persistent breadcrumb introduced")
    if sdcard.count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("verified explicit CMD12 repair was lost")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    header_path = root / "userlibandfileserver/fileserver/sfat32/sl_cache.h"
    mount32_path = root / "userlibandfileserver/fileserver/sfat32/sl_mnt32.cpp"
    estart_path = root / "userlibandfileserver/fileserver/estart/estartmain.cpp"
    sf_sys_path = root / "userlibandfileserver/fileserver/sfile/sf_sys.cpp"
    sf_drv_path = root / "userlibandfileserver/fileserver/sfile/sf_drv.cpp"
    sdcard_path = root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp"
    paths = (
        header_path,
        mount32_path,
        estart_path,
        sf_sys_path,
        sf_drv_path,
        sdcard_path,
    )
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")

    header, mount32, estart, sf_sys, sf_drv, sdcard = (
        path.read_text(encoding="utf-8") for path in paths
    )
    if V32_MARKER not in header:
        raise SystemExit("V33 requires installed V32 exact E: remount trace")
    if V33_MARKER not in header:
        header = transform_header(header)
        sf_sys, sf_drv = retire_v32_efile(sf_sys, sf_drv)
        mount32 = transform_mount32(mount32)
    verify(header, estart, sf_sys, sf_drv, mount32, sdcard)

    for path, text in zip(
        paths[:-1], (header, mount32, estart, sf_sys, sf_drv)
    ):
        path.write_text(text, encoding="utf-8")
    print("HTCLEO_EFAT_E_MOUNTL_PROGRESS=10 FA11_FA1A=installed")


if __name__ == "__main__":
    main()
