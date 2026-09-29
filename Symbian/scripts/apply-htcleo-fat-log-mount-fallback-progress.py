#!/usr/bin/env python3
"""Replace the blocked E: readiness delay with an explicit FAT mount fallback.

Hardware reached F607/FFEE: the writer Connect returned, the first E: Volume
call returned KErrNotReady, and User::After did not return.  V30 retires F601-
F60A, removes that timer dependency, mounts the already-loaded FAT object on E:
when needed, and traces the complete fallback plus BOOTLOG write path as F701-
F70A.  The final UDF remains the only halting success checkpoint.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_FAT_LOG_MOUNT_FALLBACK_PROGRESS_V30"
V29_MARKER = "HTCLEO_FAT_LOG_WRITER_ENTRY_PROGRESS_V29"
V31_MARKER = "HTCLEO_FAT_LOG_REMOUNT_RECOVERY_PROGRESS_V31"
V32_MARKER = "HTCLEO_EFILE_E_REMOUNT_PROGRESS_V32"
V33_MARKER = "HTCLEO_EFAT_E_MOUNTL_PROGRESS_V33"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def transform_header(text: str) -> str:
    anchor = (
        "/* HTCLEO_FAT_LOG_WRITER_ENTRY_PROGRESS_V29: "
        "post-Run writer Connect and E: Volume readiness. */\n"
    )
    return replace_once(
        text,
        anchor,
        anchor
        + f"/* {MARKER}: timer-free E: FAT mount and durable write. */\n",
        "V30 FAT mount-fallback marker",
    )


def transform_estart_main(text: str) -> str:
    start = text.index("static TInt HtcleoWriteFatBootRecord()\n")
    end = text.index("\nGLDEF_C TInt E32Main()", start)
    old = text[start:end]
    if old.count("HTCLEO_ESTART_PROGRESS(0xf60") != 10:
        raise SystemExit("V30 requires exactly ten installed F601-F60A calls")
    if old.count("User::After(100000);") != 1:
        raise SystemExit("V30 requires the single hardware-blocked retry delay")

    new = '''static TInt HtcleoWriteFatBootRecord()
\t{
\tHTCLEO_ESTART_PROGRESS(0xf7010000u);
\tRFs fs;
\tTInt result=fs.Connect();
\tHTCLEO_ESTART_PROGRESS(0xf7020000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result!=KErrNone)
\t\treturn HtcleoFatLogStageResult(1u,result);

\tTVolumeInfo volume;
\tTInt volumeResult=fs.Volume(volume,EDriveE);
\tHTCLEO_ESTART_PROGRESS(0xf7030000u |
\t\t(TUint32(volumeResult) & 0xffffu));
\tif (volumeResult!=KErrNone)
\t\t{
\t\t_LIT(KFatObject,"FAT");
\t\tHTCLEO_ESTART_PROGRESS(0xf7040000u |
\t\t\t(TUint32(volumeResult) & 0xffffu));
\t\tconst TInt mountResult=fs.MountFileSystem(
\t\t\tKFatObject,EDriveE,EFalse);
\t\tHTCLEO_ESTART_PROGRESS(0xf7050000u |
\t\t\t(TUint32(mountResult) & 0xffffu));
\t\tif (mountResult!=KErrNone && mountResult!=KErrAlreadyExists)
\t\t\t{
\t\t\tfs.Close();
\t\t\treturn HtcleoFatLogStageResult(2u,mountResult);
\t\t\t}
\t\tvolumeResult=fs.Volume(volume,EDriveE);
\t\tHTCLEO_ESTART_PROGRESS(0xf7060000u |
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
\tHTCLEO_ESTART_PROGRESS(0xf7070000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result!=KErrNone)
\t\t{
\t\tfs.Close();
\t\treturn HtcleoFatLogStageResult(3u,result);
\t\t}
\tTUint32 failureStage=4u;
\tresult=file.Write(record);
\tHTCLEO_ESTART_PROGRESS(0xf7080000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result==KErrNone)
\t\t{
\t\tfailureStage=5u;
\t\tresult=file.Flush();
\t\tHTCLEO_ESTART_PROGRESS(0xf7090000u |
\t\t\t(TUint32(result) & 0xffffu));
\t\t}
\tfile.Close();
\tfs.Close();
\tHTCLEO_ESTART_PROGRESS(0xf70a0000u |
\t\t(TUint32(result) & 0xffffu));
\tif (result!=KErrNone)
\t\treturn HtcleoFatLogStageResult(failureStage,result);
\treturn KErrNone;
\t}
'''
    return text[:start] + new + text[end:]


def verify(header: str, estart_main: str, sdcard: str) -> None:
    joined = "\n".join((header, estart_main, sdcard))
    if header.count(MARKER) != 1:
        raise SystemExit("V30 mount-fallback marker missing or duplicated")
    if "0xf60" in joined:
        raise SystemExit("retired F601-F60A display stage remains")
    if V31_MARKER in header:
        if "0xf70" in joined:
            raise SystemExit("F701-F70A executable stage remains after V31")
        if V32_MARKER in header:
            if "0xf80" in joined:
                raise SystemExit("F801-F80A executable stage remains after V32")
        else:
            for suffix in "123456789a":
                stage = f"0xf80{suffix}0000u"
                if estart_main.count(stage) != 1:
                    raise SystemExit(f"V31 checkpoint missing or duplicated: {stage}")
            if estart_main.count("0xf80") != 10:
                raise SystemExit("V31 does not contain exactly ten ESTART checkpoints")
        if "User::After(100000);" in estart_main:
            raise SystemExit("V31 hardware-blocked retry delay remains")
        if joined.count("0xe7f000f0") != 1:
            raise SystemExit("durable ESTART final UDF invariant failed")
        return
    for suffix in "123456789a":
        stage = f"0xf70{suffix}0000u"
        if estart_main.count(stage) != 1:
            raise SystemExit(f"F7 checkpoint missing or duplicated: {stage}")
    if estart_main.count("0xf70") != 10:
        raise SystemExit("F701-F70A are not exactly ten ESTART checkpoints")
    if "User::After(100000);" in estart_main:
        raise SystemExit("hardware-blocked E-volume retry delay remains")
    expected_log_path = r'_LIT(KLogPath,"E:\\Symbian3\\BOOTLOG.TXT");'
    if estart_main.count(expected_log_path) != 1:
        raise SystemExit(
            "BOOTLOG C++ path is not exactly E:\\\\Symbian3\\\\BOOTLOG.TXT")
    if estart_main.count("fs.MountFileSystem(") != 1:
        raise SystemExit("explicit E: FAT mount fallback missing or duplicated")
    if "KFatObject,EDriveE,EFalse" not in estart_main:
        raise SystemExit("explicit FAT mount fallback targets the wrong drive")
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
    if V29_MARKER not in header:
        raise SystemExit("V30 requires installed V29 writer-entry progress")
    if MARKER not in header:
        header = transform_header(header)
        estart_main = transform_estart_main(estart_main)
    else:
        # Repair the first installed V30 draft, whose Python string escaping
        # emitted single C++ backslashes. Keep this migration idempotent.
        bad_log_path = r'_LIT(KLogPath,"E:\Symbian3\BOOTLOG.TXT");'
        good_log_path = r'_LIT(KLogPath,"E:\\Symbian3\\BOOTLOG.TXT");'
        if bad_log_path in estart_main:
            estart_main = replace_once(
                estart_main, bad_log_path, good_log_path,
                "V30 BOOTLOG C++ path escaping")
    verify(header, estart_main, sdcard)
    header_path.write_text(header, encoding="utf-8")
    estart_path.write_text(estart_main, encoding="utf-8")
    if V33_MARKER in header:
        print("HTCLEO_FAT_LOG_MOUNT_FALLBACK=preserved F701_F70A=retired-by-V33")
    elif V32_MARKER in header:
        print("HTCLEO_FAT_LOG_MOUNT_FALLBACK=preserved F701_F70A=retired-by-V32")
    elif V31_MARKER in header:
        print("HTCLEO_FAT_LOG_MOUNT_FALLBACK=preserved F701_F70A=retired-by-V31")
    else:
        print("HTCLEO_FAT_LOG_MOUNT_FALLBACK=10 F701_F70A=installed")


if __name__ == "__main__":
    main()
