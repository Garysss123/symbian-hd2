#!/usr/bin/env python3
"""Move the ten returning checkpoints from ED0A to the first C: FAT mount.

Iteration 374 reached ED0A exactly.  Retire ED01-ED0A and install ten EE01-EE0A
checkpoints across ESTART (seven) and source-built EFILE (three), beginning after
the first C: Caps call returns and ending when the first MountFileSystem(C:)
request returns to ESTART.  The removable and non-removable paths converge at the
same MountFileSystem entry.  The only physical UDF remains the durable BOOTLOG
Write/Flush/Close boundary.
"""

from __future__ import annotations

import pathlib
import re
import sys


OLD_MARKER = "HTCLEO_MMC_POST_EC0A_PARTITION_ECAPS_PROGRESS_V14"
MARKER = "HTCLEO_ESTART_FIRST_FAT_MOUNT_PROGRESS_V15"
EFILE_MARKER = "HTCLEO_EFILE_FIRST_C_FAT_MOUNT_PROGRESS_V15"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def retire_ed_reporters(path: pathlib.Path, expected: int) -> None:
    text = path.read_text(encoding="utf-8")
    gate_name = (
        "gHtcleoFirstCapsMediaOpenTrace"
        if path.name == "locmedia.cpp"
        else "gHtcleoFirstMmcMediaOpenTrace"
    )
    if ("HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0" not in text and
            gate_name not in text):
        # A failed later ESTART anchor may leave the already-retired local-media
        # files on disk.  Treat that exact clean state as an idempotent retry;
        # verify() still fails closed on every residual marker.
        return
    block = re.compile(
        r"#if defined\(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__\)\n"
        r"(?:(?!#endif\n).)*?"
        r"HTCLEO_LOCALMEDIA_CAPS_PROGRESS\(0xed0[1-9a]0000u[^;]*;\n"
        r"(?:(?!#endif\n).)*?#endif\n",
        re.DOTALL,
    )
    text, retired = block.subn("", text)
    if retired != expected:
        raise SystemExit(
            f"{path.name}: expected {expected} ED reporter blocks, found {retired}"
        )

    # These two ELOCD-only blocks armed and advanced the retired ED window but
    # did not draw a screen themselves.
    if path.name == "locmedia.cpp":
        for old, label in (
            (
                "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
                "\tif (m.iValue == DLocalDrive::ECaps && "
                "gHtcleoFirstCapsMediaOpenTrace == 0)\n"
                "\t\tgHtcleoFirstCapsMediaOpenTrace = 1;\n"
                "#endif\n",
                "retire ED ECaps arm",
            ),
            (
                "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
                "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 1)\n"
                "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 2;\n"
                "#endif\n",
                "retire ED post-open advance",
            ),
            (
                "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
                "static volatile TUint32 gHtcleoFirstCapsMediaOpenTrace = 0;\n"
                "#endif\n\n",
                "retire ED ELOCD gate",
            ),
        ):
            text = replace_once(text, old, "", label)
    else:
        text = replace_once(
            text,
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "static volatile TUint32 gHtcleoFirstMmcMediaOpenTrace = 0;\n"
            "#endif\n\n",
            "",
            "retire ED MEDMMC gate",
        )

    path.write_text(text, encoding="utf-8")


def install_estart(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        if OLD_MARKER in text:
            raise SystemExit("V14 and V15 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V14-to-V15 marker")

    text = replace_once(
        text,
        "TInt LoadCodePageDll();\n"
        "/** Maximum Codepage Dll name length. */\n",
        "TInt LoadCodePageDll();\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "static volatile TUint32 gHtcleoFirstFatMountTrace = 0;\n"
        "#endif\n"
        "/** Maximum Codepage Dll name length. */\n",
        "first FAT mount gate",
    )

    text = replace_once(
        text,
        "            infoPtr->iCapsRetCode = r = drive.Caps(caps);\n"
        "\t\t\tif (r==KErrNone && caps().iDriveAtt&KDriveAttRemovable)\n",
        "            infoPtr->iCapsRetCode = r = drive.Caps(caps);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\t\tif (i == 0 && gHtcleoFirstFatMountTrace == 0)\n"
        "\t\t\t\t{\n"
        "\t\t\t\tHTCLEO_ESTART_PROGRESS(0xee010000u | "
        "(TUint32(r) & 0xffffu));\n"
        "\t\t\t\tgHtcleoFirstFatMountTrace = 1;\n"
        "\t\t\t\t}\n"
        "\t\t\tif (i == 0 && gHtcleoFirstFatMountTrace == 1)\n"
        "\t\t\t\t{\n"
        "\t\t\t\tTUint32 htcleoDriveClass = 0u;\n"
        "\t\t\t\tif (r == KErrNone)\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\thtcleoDriveClass = 0x4000u | "
        "(TUint32(caps().iDriveAtt) & 0x3fffu);\n"
        "\t\t\t\t\tif (caps().iDriveAtt & KDriveAttRemovable)\n"
        "\t\t\t\t\t\thtcleoDriveClass |= 0x8000u;\n"
        "\t\t\t\t\t}\n"
        "\t\t\t\tHTCLEO_ESTART_PROGRESS(0xee020000u | htcleoDriveClass);\n"
        "\t\t\t\tgHtcleoFirstFatMountTrace = 2;\n"
        "\t\t\t\t}\n"
        "#endif\n"
        "\t\t\tif (r==KErrNone && caps().iDriveAtt&KDriveAttRemovable)\n",
        "EE01/EE02 Caps return and classification",
    )

    text = replace_once(
        text,
        "\tTInt flags=anInfo.iFsInfo.iFlags;\n"
        "\tTInt drive=anInfo.iDriveNumber;\n"
        "\tTPtrC fsyname;\t\n",
        "\tTInt flags=anInfo.iFsInfo.iFlags;\n"
        "\tTInt drive=anInfo.iDriveNumber;\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (drive == EDriveC && gHtcleoFirstFatMountTrace == 2)\n"
        "\t\t{\n"
        "\t\tTUint32 htcleoMountRoute = anInfo.iRemovable ? 0x8000u : 0u;\n"
        "\t\thtcleoMountRoute |= "
        "(TUint32(anInfo.iLocalDriveNumber) & 0x7fu) << 8;\n"
        "\t\thtcleoMountRoute |= TUint32(drive) & 0xffu;\n"
        "\t\tHTCLEO_ESTART_PROGRESS(0xee030000u | htcleoMountRoute);\n"
        "\t\tgHtcleoFirstFatMountTrace = 3;\n"
        "\t\t}\n"
        "#endif\n"
        "\tTPtrC fsyname;\t\n",
        "EE03 common C mount entry",
    )

    text = replace_once(
        text,
        "\t\tr=iFs.AddFileSystem(fsyname);\n"
        "\t\tDEBUGPRINT2(\"AddFileSystem(%S) -> %d\",&fsyname,r);\n",
        "\t\tr=iFs.AddFileSystem(fsyname);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (drive == EDriveC && gHtcleoFirstFatMountTrace == 3)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_ESTART_PROGRESS(0xee040000u | "
        "(TUint32(r) & 0xffffu));\n"
        "\t\t\tgHtcleoFirstFatMountTrace = 4;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\tDEBUGPRINT2(\"AddFileSystem(%S) -> %d\",&fsyname,r);\n",
        "EE04 AddFileSystem result",
    )

    text = replace_once(
        text,
        "\t\tif (flags & FS_NOT_RUGGED)\n"
        "\t\t\t{\n"
        "\t\t\tr = iFs.SetStartupConfiguration(ESetRugged, (TAny*)drive, (TAny*)EFalse);\n"
        "\t\t\tiRuggedFileSystem = 0;\n"
        "\t\t\t}\n\n"
        "\t\tobjname.Set((anInfo.iFsInfo.iObjName) ? anInfo.iFsInfo.iObjName : anInfo.iFsInfo.iFsyName);\n",
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tTInt htcleoStartupConfigurationResult = 0x7fff;\n"
        "#endif\n"
        "\t\tif (flags & FS_NOT_RUGGED)\n"
        "\t\t\t{\n"
        "\t\t\tr = iFs.SetStartupConfiguration(ESetRugged, (TAny*)drive, (TAny*)EFalse);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\t\thtcleoStartupConfigurationResult = r;\n"
        "#endif\n"
        "\t\t\tiRuggedFileSystem = 0;\n"
        "\t\t\t}\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (drive == EDriveC && gHtcleoFirstFatMountTrace == 4)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_ESTART_PROGRESS(0xee050000u | "
        "(TUint32(htcleoStartupConfigurationResult) & 0xffffu));\n"
        "\t\t\tgHtcleoFirstFatMountTrace = 5;\n"
        "\t\t\t}\n"
        "#endif\n\n"
        "\t\tobjname.Set((anInfo.iFsInfo.iObjName) ? anInfo.iFsInfo.iObjName : anInfo.iFsInfo.iFsyName);\n",
        "EE05 startup configuration result",
    )

    text = replace_once(
        text,
        "\t\tTBool isSync=(flags & FS_SYNC_DRIVE);\n"
        "\t\tif (anInfo.iFsInfo.iExtName)\n",
        "\t\tTBool isSync=(flags & FS_SYNC_DRIVE);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (drive == EDriveC && gHtcleoFirstFatMountTrace == 5)\n"
        "\t\t\t{\n"
        "\t\t\tTUint32 htcleoMountMode = anInfo.iFsInfo.iExtName ? 0x8000u : 0u;\n"
        "\t\t\tif (isSync)\n"
        "\t\t\t\thtcleoMountMode |= 0x4000u;\n"
        "\t\t\thtcleoMountMode |= TUint32(drive) & 0xffu;\n"
        "\t\t\tHTCLEO_ESTART_PROGRESS(0xee060000u | htcleoMountMode);\n"
        "\t\t\tgHtcleoFirstFatMountTrace = 6;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\tif (anInfo.iFsInfo.iExtName)\n",
        "EE06 pre-mount dispatch",
    )

    text = replace_once(
        text,
        "\t\telse\n"
        "\t\t\tr=iFs.MountFileSystem(objname,drive,isSync);\n"
        "\t\t\t\t\n"
        "\t\tDEBUGPRINT4(\"MountFileSystem(%S) on drive %c: -> %d (sync=%d)\",&objname,(drive+'A'),r,isSync);\n",
        "\t\telse\n"
        "\t\t\tr=iFs.MountFileSystem(objname,drive,isSync);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\t\tif (drive == EDriveC && gHtcleoFirstFatMountTrace == 6)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_ESTART_PROGRESS(0xee0a0000u | "
        "(TUint32(r) & 0xffffu));\n"
        "\t\t\tgHtcleoFirstFatMountTrace = 10;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\t\t\t\n"
        "\t\tDEBUGPRINT4(\"MountFileSystem(%S) on drive %c: -> %d (sync=%d)\",&objname,(drive+'A'),r,isSync);\n",
        "EE0A MountFileSystem result returned to ESTART",
    )
    path.write_text(text, encoding="utf-8")


def install_efile(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if EFILE_MARKER in text:
        return

    text = replace_once(
        text,
        "#include <f32file.h>\n\n"
        "#ifdef OST_TRACE_COMPILER_IN_USE\n",
        "#include <f32file.h>\n"
        "#include <u32hal.h>\n\n"
        "/* HTCLEO_EFILE_FIRST_C_FAT_MOUNT_PROGRESS_V15 */\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "#define HTCLEO_EFILE_MOUNT_PROGRESS(aStage) \\\n"
        "\tdo \\\n"
        "\t\t{ \\\n"
        "\t\tTUint32 htcleoProgressLocation; \\\n"
        "\t\tasm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\"); \\\n"
        "\t\t(void)UserSvr::HalFunction(EHalGroupPlatformSpecific1,2, \\\n"
        "\t\t\t(TAny*)htcleoProgressLocation,(TAny*)(TUint32)(aStage)); \\\n"
        "\t\t} while (0)\n"
        "static volatile TUint32 gHtcleoFirstEstartCMountTrace = 0;\n"
        "#else\n"
        "#define HTCLEO_EFILE_MOUNT_PROGRESS(aStage) do { } while (0)\n"
        "#endif\n\n"
        "#ifdef OST_TRACE_COMPILER_IN_USE\n",
        "EFILE returning reporter",
    )

    text = replace_once(
        text,
        "\t{\n"
        "\tTInt r=DoMountFileSystem(aRequest);\n"
        "\tif( KErrNone == r )\n",
        "\t{\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoFirstEstartCMountTrace == 1 &&\n"
        "\t\taRequest->Message().Int1() == EDriveC &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_MOUNT_PROGRESS(0xee080000u |\n"
        "\t\t\t(TUint32(aRequest->Message().Int1()) & 0xffffu));\n"
        "\t\tgHtcleoFirstEstartCMountTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
        "\tTInt r=DoMountFileSystem(aRequest);\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoFirstEstartCMountTrace == 2 &&\n"
        "\t\taRequest->Message().Int1() == EDriveC &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_MOUNT_PROGRESS(0xee090000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\tgHtcleoFirstEstartCMountTrace = 3;\n"
        "\t\t}\n"
        "#endif\n"
        "\tif( KErrNone == r )\n",
        "EFILE EE08/EE09 request dispatch and CheckMount result",
    )

    text = replace_once(
        text,
        "\tif (r == KErrNone)\n"
        "\t\tr = DoMountFsInitialise(aRequest,name,ETrue,aRequest->Message().Int3());\n"
        "\treturn r;\n",
        "\tif (r == KErrNone)\n"
        "\t\tr = DoMountFsInitialise(aRequest,name,ETrue,aRequest->Message().Int3());\n"
        "#if defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n"
        "\tif (gHtcleoFirstEstartCMountTrace == 0 &&\n"
        "\t\taRequest->Message().Int1() == EDriveC &&\n"
        "\t\taRequest->Message().SecureId().iId == 0x10272c04u)\n"
        "\t\t{\n"
        "\t\tHTCLEO_EFILE_MOUNT_PROGRESS(0xee070000u |\n"
        "\t\t\t(TUint32(r) & 0xffffu));\n"
        "\t\tgHtcleoFirstEstartCMountTrace = "
        "(r == KErrNone) ? 1u : 3u;\n"
        "\t\t}\n"
        "#endif\n"
        "\treturn r;\n",
        "EFILE EE07 Initialise result",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    efile = paths["efile"].read_text(encoding="utf-8")
    locmedia = paths["locmedia"].read_text(encoding="utf-8")
    medmmc = paths["medmmc"].read_text(encoding="utf-8")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V15 ESTART marker state is invalid")
    if estart.count("static volatile TUint32 gHtcleoFirstFatMountTrace = 0;") != 1:
        raise SystemExit("first FAT mount gate is absent or duplicated")
    for suffix in ("1", "2", "3", "4", "5", "6", "a"):
        stage = f"ee0{suffix}"
        if estart.count(f"HTCLEO_ESTART_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"ESTART mount checkpoint missing: {stage}")
    if efile.count(EFILE_MARKER) != 1:
        raise SystemExit("V15 EFILE marker state is invalid")
    if efile.count("static volatile TUint32 gHtcleoFirstEstartCMountTrace = 0;") != 1:
        raise SystemExit("first EFILE C mount gate is absent or duplicated")
    for suffix in ("7", "8", "9"):
        stage = f"ee0{suffix}"
        if efile.count(f"HTCLEO_EFILE_MOUNT_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"EFILE mount checkpoint missing: {stage}")
    if "HTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xed0" in locmedia + medmmc:
        raise SystemExit("a retired ED checkpoint remains")
    if "gHtcleoFirstCapsMediaOpenTrace" in locmedia:
        raise SystemExit("retired ELOCD ED gate remains")
    if "gHtcleoFirstMmcMediaOpenTrace" in medmmc:
        raise SystemExit("retired MEDMMC ED gate remains")
    if (main.count("0xe7f000f0") != 1 or
            "0xe7f000f0" in estart or "0xe7f000f0" in efile):
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: apply-htcleo-estart-first-fat-mount-progress.py KERNEL_SOURCE"
        )
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "estart": root / "userlibandfileserver/fileserver/estart/estart.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
        "efile": root / "userlibandfileserver/fileserver/sfile/sf_sys.cpp",
        "locmedia": root / "kernel/eka/drivers/locmedia/locmedia.cpp",
        "medmmc": root / "kernel/eka/drivers/medmmc/medmmc.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    if MARKER not in paths["estart"].read_text(encoding="utf-8"):
        retire_ed_reporters(paths["locmedia"], 5)
        retire_ed_reporters(paths["medmmc"], 5)
        install_estart(paths["estart"])
    install_efile(paths["efile"])
    verify(paths)
    print("HTCLEO_FIRST_FAT_MOUNT_PROGRESS=10 ESTART=7 EFILE=3")


if __name__ == "__main__":
    main()
