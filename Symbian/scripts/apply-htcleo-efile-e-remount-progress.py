#!/usr/bin/env python3
"""Trace the exact E: remount request after the verified local dismount.

Iteration 391 reached F806/KErrNotReady.  F804 and F805 necessarily completed,
so the registered FSY name was obtained and the E:-local dismount succeeded.
V32 retires F801-F80A and arms one EFILE-local one-shot gate only after that
successful ESTART E: dismount.  F901-F90A then span the immediately following
MountFileSystem request from Initialise through CheckMount/ReMount and the FAT
MountL TRAP result.  No storage policy or media/socket remount is introduced.
"""

from __future__ import annotations

import pathlib
import sys


V31_MARKER = "HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31"
V32_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32"
V33_MARKER = "HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33"
SYS_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_SYS_V32"
DRV_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_DRV_V32"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def retire_estart_f8(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    skipping = False
    count = 0
    for line in lines:
        if not skipping and "HTCLEO_ESTART_PROGRESS(0xf80" in line:
            count += 1
            skipping = ");" not in line
            continue
        if skipping:
            if ");" in line:
                skipping = False
            continue
        output.append(line)
    if skipping:
        raise SystemExit("ESTART: unterminated F8 reporter call")
    if count != 10:
        raise SystemExit(f"ESTART: expected ten F8 reporter calls, found {count}")
    return "".join(output)


def transform_header(text: str) -> str:
    anchor = (
        "/* HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31: "
        "reset registered E: FSY and remount before BOOTLOG. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"/* {V32_MARKER}: exact post-dismount EFILE remount trace. */\n",
        "V32 header marker",
    )


def transform_sf_sys(text: str) -> str:
    reporter_anchor = (
        "#else\n"
        "#define HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(aStage) do { } while (0)\n"
        "#endif\n"
        "#include <kernel/localise.h>\n"
    )
    reporter_new = (
        "#else\n"
        "#define HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(aStage) do { } while (0)\n"
        "#endif\n"
        f"\n/* {SYS_MARKER} */\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "volatile TUint32 gHtcleoEstartERemountPhase = 0;\n"
        "#endif\n"
        "#include <kernel/localise.h>\n"
    )
    text = replace_once(
        text, reporter_anchor, reporter_new, "sf_sys.cpp V32 phase gate"
    )

    old_dismount = (
        "\tif(drive->DismountDeferred())\n"
        "\t\treturn KErrInUse;\n\n"
        "\treturn DoDismountFileSystem(name, drive, EFalse, EFalse);\n"
    )
    new_dismount = (
        "\tif(drive->DismountDeferred())\n"
        "\t\treturn KErrInUse;\n\n"
        "\tTInt r=DoDismountFileSystem(name, drive, EFalse, EFalse);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (r == KErrNone && drive->DriveNumber() == EDriveE &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\tgHtcleoEstartERemountPhase = 0x100u;\n"
        "#endif\n"
        "\treturn r;\n"
    )
    text = replace_once(
        text, old_dismount, new_dismount, "sf_sys.cpp post-dismount arm"
    )

    old_initialise = (
        "TInt TFsMountFileSystem::Initialise(CFsRequest* aRequest)\n"
        "//\n"
        "//\t\n"
        "//\n"
        "\t{\n"
        "\tTFullName name;\n"
        "\tTInt r = aRequest->Read(KMsgPtr0,name);\n"
        "\tif (r == KErrNone)\n"
        "\t\tr = DoMountFsInitialise(aRequest,name,ETrue,aRequest->Message().Int3());\n"
        "\treturn r;\n"
        "\t}\n"
    )
    new_initialise = (
        "TInt TFsMountFileSystem::Initialise(CFsRequest* aRequest)\n"
        "//\n"
        "//\t\n"
        "//\n"
        "\t{\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 0x100u &&\n"
        "\t\taRequest->Message().Int1() == EDriveE &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9010000u |\n"
        "\t\t\t(TUint32(EDriveE) & 0xffffu));\n"
        "\t\tgHtcleoEstartERemountPhase = 1u;\n"
        "\t\t}\n"
        "#endif\n"
        "\tTFullName name;\n"
        "\tTInt r = aRequest->Read(KMsgPtr0,name);\n"
        "\tif (r == KErrNone)\n"
        "\t\tr = DoMountFsInitialise(aRequest,name,ETrue,aRequest->Message().Int3());\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 1u &&\n"
        "\t\taRequest->Message().Int1() == EDriveE &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9020000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\tgHtcleoEstartERemountPhase = (r == KErrNone) ? 2u : 10u;\n"
        "\t\t}\n"
        "#endif\n"
        "\treturn r;\n"
        "\t}\n"
    )
    text = replace_once(
        text, old_initialise, new_initialise, "sf_sys.cpp F901/F902 Initialise"
    )

    old_request = (
        "TInt TFsMountFileSystem::DoRequestL(CFsRequest* aRequest)\n"
        "//\n"
        "// Mount a filesystem on a drive.\n"
        "//\n"
        "\t{\n"
        "\tTInt r=DoMountFileSystem(aRequest);\n"
    )
    new_request = (
        "TInt TFsMountFileSystem::DoRequestL(CFsRequest* aRequest)\n"
        "//\n"
        "// Mount a filesystem on a drive.\n"
        "//\n"
        "\t{\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 2u &&\n"
        "\t\taRequest->Drive()->DriveNumber() == EDriveE &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9030000u |\n"
        "\t\t\t(TUint32(EDriveE) & 0xffffu));\n"
        "\t\tgHtcleoEstartERemountPhase = 3u;\n"
        "\t\t}\n"
        "#endif\n"
        "\tTInt r=DoMountFileSystem(aRequest);\n"
    )
    text = replace_once(
        text, old_request, new_request, "sf_sys.cpp F903 DoRequestL entry"
    )

    old_mount = (
        "\tTInt r = TFileCacheSettings::ReadPropertiesFile(aRequest->Drive()->DriveNumber());\n"
        "\tif (r != KErrNone)\n"
        "\t\treturn r;\n\n"
        "\treturn(aRequest->Drive()->CheckMount());\n"
    )
    new_mount = (
        "\tTInt r = TFileCacheSettings::ReadPropertiesFile(aRequest->Drive()->DriveNumber());\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 3u &&\n"
        "\t\taRequest->Drive()->DriveNumber() == EDriveE)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9040000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\tgHtcleoEstartERemountPhase = (r == KErrNone) ? 4u : 10u;\n"
        "\t\t}\n"
        "#endif\n"
        "\tif (r != KErrNone)\n"
        "\t\treturn r;\n\n"
        "\treturn(aRequest->Drive()->CheckMount());\n"
    )
    return replace_once(
        text, old_mount, new_mount, "sf_sys.cpp F904 cache-properties result"
    )


def transform_sf_drv(text: str) -> str:
    reporter_anchor = (
        "#else\n"
        "#define HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(aStage) do { } while (0)\n"
        "#endif\n\n"
        "#ifdef OST_TRACE_COMPILER_IN_USE\n"
    )
    reporter_new = (
        "#else\n"
        "#define HTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(aStage) do { } while (0)\n"
        "#endif\n"
        f"\n/* {DRV_MARKER} */\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "extern volatile TUint32 gHtcleoEstartERemountPhase;\n"
        "#endif\n\n"
        "#ifdef OST_TRACE_COMPILER_IN_USE\n"
    )
    text = replace_once(
        text, reporter_anchor, reporter_new, "sf_drv.cpp V32 phase gate"
    )

    old_check = (
        "TInt TDrive::CheckMount()\n"
        "//\n"
        "// Check the drive and try to mount a media if not already mounted.\n"
        "//\n"
        "\t{\n"
        "\t__PRINT2(_L(\"TDrive::CheckMount Drive%d, changed:%d\"),DriveNumber(), iChanged);\n"
    )
    new_check = (
        "TInt TDrive::CheckMount()\n"
        "//\n"
        "// Check the drive and try to mount a media if not already mounted.\n"
        "//\n"
        "\t{\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 4u && DriveNumber() == EDriveE)\n"
        "\t\t{\n"
        "\t\tTUint32 htcleoState = TUint32(DriveNumber()) & 0xffu;\n"
        "\t\tif (iFSys)\n"
        "\t\t\thtcleoState |= 0x8000u;\n"
        "\t\tif (iChanged)\n"
        "\t\t\thtcleoState |= 0x4000u;\n"
        "\t\tif (IsMounted())\n"
        "\t\t\thtcleoState |= 0x2000u;\n"
        "\t\thtcleoState |= (TUint32(iMountFailures) & 0x1fu) << 8;\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9050000u | htcleoState);\n"
        "\t\tgHtcleoEstartERemountPhase = 5u;\n"
        "\t\t}\n"
        "#endif\n"
        "\t__PRINT2(_L(\"TDrive::CheckMount Drive%d, changed:%d\"),DriveNumber(), iChanged);\n"
    )
    text = replace_once(text, old_check, new_check, "sf_drv.cpp F905 CheckMount")

    old_remount = (
        "\t\tif (!ReMount())\t    //\tHave we just remounted a mount we have previously encountered?\n"
        "\t\t\t{\t\t\t\n"
        "\t\t\tMountFileSystem(EFalse);\t//\tIf not, mount it for the first time now\n"
        "\t\t\t}\n"
        "\t\telse if(IsWriteProtected() && IsWriteableResource())\n"
    )
    new_remount = (
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (gHtcleoEstartERemountPhase == 5u && DriveNumber() == EDriveE)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9060000u |\n"
        "\t\t\t\t((TUint32(iMountFailures) & 0xffu) << 8) |\n"
        "\t\t\t\t(TUint32(DriveNumber()) & 0xffu));\n"
        "\t\t\tgHtcleoEstartERemountPhase = 6u;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\tTBool htcleoRemounted=ReMount();\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (gHtcleoEstartERemountPhase == 6u && DriveNumber() == EDriveE)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9070000u |\n"
        "\t\t\t\t(htcleoRemounted ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(iReason) & 0xfffu));\n"
        "\t\t\tgHtcleoEstartERemountPhase = 7u;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\tif (!htcleoRemounted)\t    //\tHave we just remounted a mount we have previously encountered?\n"
        "\t\t\t{\t\t\t\n"
        "\t\t\tMountFileSystem(EFalse);\t//\tIf not, mount it for the first time now\n"
        "\t\t\t}\n"
        "\t\telse if(IsWriteProtected() && IsWriteableResource())\n"
    )
    text = replace_once(
        text, old_remount, new_remount, "sf_drv.cpp F906/F907 ReMount"
    )

    old_mount_entry = (
        "void TDrive::MountFileSystem(TBool aForceMount, TUint32 aFsNameHash /*=0*/ )\n"
        "\t{\n"
        "\t__PRINT2(_L(\"TDrive::MountFileSystem aForceMount=%d, FSNameHash:0x%x\"),aForceMount, aFsNameHash);\n"
        "\t__CHECK_DRIVETHREAD(iDriveNumber);\n"
    )
    new_mount_entry = (
        "void TDrive::MountFileSystem(TBool aForceMount, TUint32 aFsNameHash /*=0*/ )\n"
        "\t{\n"
        "\t__PRINT2(_L(\"TDrive::MountFileSystem aForceMount=%d, FSNameHash:0x%x\"),aForceMount, aFsNameHash);\n"
        "\t__CHECK_DRIVETHREAD(iDriveNumber);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 7u && DriveNumber() == EDriveE)\n"
        "\t\t{\n"
        "\t\tTUint32 htcleoMountState = TUint32(DriveNumber()) & 0xffu;\n"
        "\t\tif (iFSys)\n"
        "\t\t\thtcleoMountState |= 0x8000u;\n"
        "\t\tif (aForceMount)\n"
        "\t\t\thtcleoMountState |= 0x4000u;\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9080000u | htcleoMountState);\n"
        "\t\tgHtcleoEstartERemountPhase = 8u;\n"
        "\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text, old_mount_entry, new_mount_entry, "sf_drv.cpp F908 mount entry"
    )

    old_mountl = (
        "    apMount->InitL(*this, pMountsFs);  //-- initialise Mount\n"
        "    apMount->MountL(aForceMount);      //-- mount the file system  \n"
    )
    new_mountl = (
        "    apMount->InitL(*this, pMountsFs);  //-- initialise Mount\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoEstartERemountPhase == 8u && DriveNumber() == EDriveE)\n"
        "\t\t{\n"
        "\t\tTUint32 htcleoInitState = TUint32(DriveNumber()) & 0xffu;\n"
        "\t\tif (apMount)\n"
        "\t\t\thtcleoInitState |= 0x8000u;\n"
        "\t\tif (pMountsFs)\n"
        "\t\t\thtcleoInitState |= 0x4000u;\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf9090000u | htcleoInitState);\n"
        "\t\tgHtcleoEstartERemountPhase = 9u;\n"
        "\t\t}\n"
        "#endif\n"
        "    apMount->MountL(aForceMount);      //-- mount the file system  \n"
    )
    text = replace_once(
        text, old_mountl, new_mountl, "sf_drv.cpp F909 pre-MountL"
    )

    old_trap = (
        "    CMountCB* pM=NULL;\n"
        "    TRAP(iReason, DoMountFileSystemL(pM, aForceMount, aFsNameHash));\n"
        "\tif (iReason == KErrNone)\n"
    )
    new_trap = (
        "    CMountCB* pM=NULL;\n"
        "    TRAP(iReason, DoMountFileSystemL(pM, aForceMount, aFsNameHash));\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif ((gHtcleoEstartERemountPhase == 8u ||\n"
        "\t\tgHtcleoEstartERemountPhase == 9u) && DriveNumber() == EDriveE)\n"
        "\t\t{\n"
        "\t\tTUint32 htcleoPriorPhase = gHtcleoEstartERemountPhase;\n"
        "\t\tHTCLEO_EFILE_LOG_BOUNDARY_PROGRESS(0xf90a0000u |\n"
        "\t\t\t((htcleoPriorPhase & 0xfu) << 12) |\n"
        "\t\t\t(TUint32(iReason) & 0xfffu));\n"
        "\t\tgHtcleoEstartERemountPhase = 10u;\n"
        "\t\t}\n"
        "#endif\n"
        "\tif (iReason == KErrNone)\n"
    )
    return replace_once(
        text, old_trap, new_trap, "sf_drv.cpp F90A mount TRAP result"
    )


def verify(
    header: str, estart: str, sf_sys: str, sf_drv: str, sdcard: str
) -> None:
    joined = "\n".join((header, estart, sf_sys, sf_drv, sdcard))
    if header.count(V32_MARKER) != 1:
        raise SystemExit("V32 marker missing or duplicated")
    if V33_MARKER in header:
        if "0xf80" in joined or "0xf90" in joined:
            raise SystemExit("V33 exists but retired F8/F9 checkpoint remains")
        if SYS_MARKER in joined or DRV_MARKER in joined:
            raise SystemExit("V33 exists but retired V32 EFILE marker remains")
        if "gHtcleoEstartERemountPhase" in joined:
            raise SystemExit("V33 exists but V32 EFILE breadcrumb remains")
        if estart.count("fs.DismountFileSystem(") != 1:
            raise SystemExit("verified E: dismount recovery was lost")
        if estart.count("fs.MountFileSystem(") != 1:
            raise SystemExit("verified E: remount recovery was lost")
        if "fileSystemName,EDriveE,EFalse" not in estart:
            raise SystemExit("E: remount target changed")
        if joined.count("0xe7f000f0") != 1:
            raise SystemExit("durable final UDF invariant failed")
        if sdcard.count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
            raise SystemExit("verified explicit CMD12 repair was lost")
        return
    if sf_sys.count(SYS_MARKER) != 1 or sf_drv.count(DRV_MARKER) != 1:
        raise SystemExit("V32 EFILE source marker missing or duplicated")
    if "0xf80" in joined:
        raise SystemExit("retired F801-F80A stage remains")
    for suffix in "1234":
        if sf_sys.count(f"0xf90{suffix}0000u") != 1:
            raise SystemExit(f"sf_sys F90{suffix} missing or duplicated")
    for suffix in "56789a":
        if sf_drv.count(f"0xf90{suffix}0000u") != 1:
            raise SystemExit(f"sf_drv F90{suffix} missing or duplicated")
    if joined.count("0xf90") != 10:
        raise SystemExit("F901-F90A are not exactly ten source checkpoints")
    if estart.count("fs.DismountFileSystem(") != 1:
        raise SystemExit("verified E: dismount recovery was lost")
    if estart.count("fs.MountFileSystem(") != 1:
        raise SystemExit("verified E: remount recovery was lost")
    if "fileSystemName,EDriveE,EFalse" not in estart:
        raise SystemExit("E: remount target changed")
    if estart.count("fs.RemountDrive(") != 0:
        raise SystemExit("forbidden media/socket remount introduced")
    if sf_sys.count("volatile TUint32 gHtcleoEstartERemountPhase = 0;") != 1:
        raise SystemExit("EFILE one-shot remount phase gate invalid")
    if sf_drv.count("extern volatile TUint32 gHtcleoEstartERemountPhase;") != 1:
        raise SystemExit("EFILE phase-gate declaration invalid")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable final UDF invariant failed")
    if "static volatile" in joined:
        raise SystemExit("forbidden persistent static breadcrumb introduced")
    if sdcard.count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("verified explicit CMD12 repair was lost")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    header_path = root / "userlibandfileserver/fileserver/sfat32/sl_cache.h"
    estart_path = root / "userlibandfileserver/fileserver/estart/estartmain.cpp"
    sf_sys_path = root / "userlibandfileserver/fileserver/sfile/sf_sys.cpp"
    sf_drv_path = root / "userlibandfileserver/fileserver/sfile/sf_drv.cpp"
    sdcard_path = root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp"
    paths = (header_path, estart_path, sf_sys_path, sf_drv_path, sdcard_path)
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")

    header, estart, sf_sys, sf_drv, sdcard = (
        path.read_text(encoding="utf-8") for path in paths
    )
    if V31_MARKER not in header:
        raise SystemExit("V32 requires installed V31 E: remount recovery")
    if V32_MARKER not in header:
        header = transform_header(header)
        estart = retire_estart_f8(estart)
        sf_sys = transform_sf_sys(sf_sys)
        sf_drv = transform_sf_drv(sf_drv)
    verify(header, estart, sf_sys, sf_drv, sdcard)

    for path, text in zip(paths[:-1], (header, estart, sf_sys, sf_drv)):
        path.write_text(text, encoding="utf-8")
    if V33_MARKER in header:
        print("HTCLEO_EFILE_E_REMOUNT_PROGRESS=preserved F901_F90A=retired-by-V33")
    else:
        print("HTCLEO_EFILE_E_REMOUNT_PROGRESS=10 F901_F90A=installed")


if __name__ == "__main__":
    main()
