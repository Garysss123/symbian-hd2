#!/usr/bin/env python3
"""Recover an E: FSY that is registered but not mounted, then write BOOTLOG.

Iteration 390 reached F705/FFEB.  EFILE returns KErrAccessDenied from
DoMountFsInitialise when the drive thread and GetFSys() already exist, so adding
FAT again is the wrong recovery operation.  V31 retires F701-F70A, queries the
registered E: FSY name, dismounts that unready instance to reset its mount
failure state, mounts the same FSY again, and traces the complete recovery and
BOOTLOG write as F801-F80A.  It never forces a media/socket remount.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31"
V30_MARKER = "HTCLEO_FAT_LOG_MOUNT_FALLBACK_PROGRESS_V30"
V32_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32"
V33_MARKER = "HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transform_header(text: str) -> str:
    anchor = (
        "/* HTCLEO_FAT_LOG_MOUNT_FALLBACK_PROGRESS_V30: "
        "timer-free E: FAT mount and durable write. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"/* {MARKER}: reset registered E: FSY and remount before BOOTLOG. */\n",
        "V31 E FSY remount-recovery marker",
    )


def transform_estart_main(text: str) -> str:
    start = text.index("static TInt HtcleoWriteFatBootRecord()\n")
    end = text.index("\nGLDEF_C TInt E32Main()", start)
    old = text[start:end]
    if old.count("HTCLEO_ESTART_PROGRESS(0xf70") != 10:
        raise SystemExit("V31 requires exactly ten installed F701-F70A calls")
    if old.count("fs.MountFileSystem(") != 1:
        raise SystemExit("V31 requires the single V30 explicit mount attempt")
    if "User::After(100000);" in old:
        raise SystemExit("V31 source unexpectedly restored the blocked timer")

    new = '''static TInt HtcleoWriteFatBootRecord()
\t{
\tHTCLEO_ESTART_PROGRESS(0xf8010000u);
\tRFs fs;
\tTInt result=fs.Connect();
\tHTCLEO_ESTART_PROGRESS(0xf8020000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result!=KErrNone)
\t\treturn HtcleoFatLogStageResult(1u,result);

\tTVolumeInfo volume;
\tTInt volumeResult=fs.Volume(volume,EDriveE);
\tHTCLEO_ESTART_PROGRESS(0xf8030000u |
\t\t(TUint32(volumeResult) & 0xffffu));
\tif (volumeResult!=KErrNone)
\t\t{
\t\tTFileName fileSystemName;
\t\tresult=fs.FileSystemName(fileSystemName,EDriveE);
\t\tHTCLEO_ESTART_PROGRESS(0xf8040000u |
\t\t\t(TUint32(result) & 0xffffu));
\t\tif (result!=KErrNone)
\t\t\t{
\t\t\tfs.Close();
\t\t\treturn HtcleoFatLogStageResult(2u,result);
\t\t\t}

\t\tresult=fs.DismountFileSystem(fileSystemName,EDriveE);
\t\tHTCLEO_ESTART_PROGRESS(0xf8050000u |
\t\t\t(TUint32(result) & 0xffffu));
\t\tif (result!=KErrNone)
\t\t\t{
\t\t\tfs.Close();
\t\t\treturn HtcleoFatLogStageResult(2u,result);
\t\t\t}

\t\tresult=fs.MountFileSystem(fileSystemName,EDriveE,EFalse);
\t\tHTCLEO_ESTART_PROGRESS(0xf8060000u |
\t\t\t(TUint32(result) & 0xffffu));
\t\tif (result!=KErrNone)
\t\t\t{
\t\t\tfs.Close();
\t\t\treturn HtcleoFatLogStageResult(2u,result);
\t\t\t}

\t\tvolumeResult=fs.Volume(volume,EDriveE);
\t\tHTCLEO_ESTART_PROGRESS(0xf8070000u |
\t\t\t(TUint32(volumeResult) & 0xffffu));
\t\t}
\tif (volumeResult!=KErrNone)
\t\t{
\t\tfs.Close();
\t\treturn HtcleoFatLogStageResult(2u,volumeResult);
\t\t}

\t_LIT(KLogPath,"E:\\\\Symbian3\\\\BOOTLOG.TXT");
\t_LIT8(KBody,"HTCLEO_FAT_LOG_V1\\r\\nRECORD_VERSION=00000001\\r\\nGATE7=PASS\\r\\nF32_E_DRIVE=READY\\r\\n");
\tTBuf8<160> record(KBody);
\trecord.AppendFormat(_L8("CRC32=%08X\\r\\n"),HtcleoFatLogCrc32(KBody));
\tRFile file;
\tresult=file.Replace(fs,KLogPath,EFileWrite|EFileShareExclusive);
\tHTCLEO_ESTART_PROGRESS(0xf8080000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result!=KErrNone)
\t\t{
\t\tfs.Close();
\t\treturn HtcleoFatLogStageResult(3u,result);
\t\t}
\tTUint32 failureStage=4u;
\tresult=file.Write(record);
\tHTCLEO_ESTART_PROGRESS(0xf8090000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result==KErrNone)
\t\t{
\t\tfailureStage=5u;
\t\tresult=file.Flush();
\t\tHTCLEO_ESTART_PROGRESS(0xf80a0000u |
\t\t\t(TUint32(result) & 0xffffu));
\t\t}
\tfile.Close();
\tfs.Close();
\tif (result!=KErrNone)
\t\treturn HtcleoFatLogStageResult(failureStage,result);
\treturn KErrNone;
\t}
'''
    return text[:start] + new + text[end:]


def verify(header: str, estart_main: str, sdcard: str) -> None:
    joined = "\n".join((header, estart_main, sdcard))
    if header.count(MARKER) != 1:
        raise SystemExit("V31 remount-recovery marker missing or duplicated")
    if "0xf60" in joined or "0xf70" in joined:
        raise SystemExit("retired F601-F70A display stage remains")
    if V33_MARKER in header:
        if "0xf80" in joined or "0xf90" in joined:
            raise SystemExit("F801-F90A executable stage remains after V33")
    elif V32_MARKER in header:
        if "0xf80" in joined:
            raise SystemExit("F801-F80A executable stage remains after V32")
    else:
        for suffix in "123456789a":
            stage = f"0xf80{suffix}0000u"
            if estart_main.count(stage) != 1:
                raise SystemExit(f"F8 checkpoint missing or duplicated: {stage}")
        if estart_main.count("0xf80") != 10:
            raise SystemExit("F801-F80A are not exactly ten ESTART checkpoints")
    if "User::After(100000);" in estart_main:
        raise SystemExit("hardware-blocked E-volume retry delay remains")
    if estart_main.count("fs.FileSystemName(") != 1:
        raise SystemExit("registered E: FSY query missing or duplicated")
    if estart_main.count("fs.DismountFileSystem(") != 1:
        raise SystemExit("E: FSY dismount recovery missing or duplicated")
    if estart_main.count("fs.MountFileSystem(") != 1:
        raise SystemExit("E: FSY remount recovery missing or duplicated")
    if "fileSystemName,EDriveE,EFalse" not in estart_main:
        raise SystemExit("FSY remount recovery targets the wrong drive")
    expected_log_path = r'_LIT(KLogPath,"E:\\Symbian3\\BOOTLOG.TXT");'
    if estart_main.count(expected_log_path) != 1:
        raise SystemExit(
            "BOOTLOG C++ path is not exactly E:\\\\Symbian3\\\\BOOTLOG.TXT")
    if sdcard.count("s.FillCommandDesc(ECmdStopTransmission, 0);") != 1:
        raise SystemExit("verified explicit CMD12 repair was lost")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART final UDF invariant failed")
    if "static volatile" in joined:
        raise SystemExit("forbidden persistent breadcrumb introduced")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    header_path = root / "userlibandfileserver/fileserver/sfat32/sl_cache.h"
    estart_path = root / "userlibandfileserver/fileserver/estart/estartmain.cpp"
    sdcard_path = root / "kernel/eka/drivers/pbus/mmc/sdcard/sdcard3c/sdcard.cpp"
    for path in (header_path, estart_path, sdcard_path):
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    header = header_path.read_text(encoding="utf-8")
    estart_main = estart_path.read_text(encoding="utf-8")
    sdcard = sdcard_path.read_text(encoding="utf-8")
    if V30_MARKER not in header:
        raise SystemExit("V31 requires installed V30 mount-fallback progress")
    if MARKER not in header:
        header = transform_header(header)
        estart_main = transform_estart_main(estart_main)
    verify(header, estart_main, sdcard)
    header_path.write_text(header, encoding="utf-8")
    estart_path.write_text(estart_main, encoding="utf-8")
    if V33_MARKER in header:
        print("HTCLEO_FAT_LOG_REMOUNT_RECOVERY=preserved F801_F80A=retired-by-V33")
    elif V32_MARKER in header:
        print("HTCLEO_FAT_LOG_REMOUNT_RECOVERY=preserved F801_F80A=retired-by-V32")
    else:
        print("HTCLEO_FAT_LOG_REMOUNT_RECOVERY=10 F801_F80A=installed")


if __name__ == "__main__":
    main()
