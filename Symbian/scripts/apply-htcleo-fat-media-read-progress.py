#!/usr/bin/env python3
"""Trace one attributed FAT directory-cache media read across EFAT/EFILE/ELOCD/MMC.

Iteration 380 reached FC05 immediately before the first 16 KiB
TDriveInterface::ReadNonCritical() issued by the exact C: volume-label lookup.
Retire FC01-FC0A, preserve the stack-local attribution token, and put an
otherwise-unused bit in TLocalDriveMessageData::iFlags for only that read.  The
bit is diagnostic metadata: normal local-media code ignores it, while the ten
FD01-FD0A returning checkpoints use it to reject every unrelated I/O request.
"""

from __future__ import annotations

import pathlib
import re
import sys


OLD_MARKER = "HTCLEO_FAT_DIRECTORY_CACHE_READ_PROGRESS_V20"
NEW_MARKER = "HTCLEO_FAT_MEDIA_READ_PROGRESS_V21"
FAT_MACRO = "__HTCLEO_FAT_MOUNT_PROGRESS__"
EFILE_MACRO = "__HTCLEO_LOW_ROM_PD_FIX_PROBE__"
OLD_REPORTER = "HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS"
FAT_REPORTER = "HTCLEO_FAT_MEDIA_READ_PROGRESS"
KERNEL_REPORTER = "HTCLEO_LOCALMEDIA_CAPS_PROGRESS"
TRACE_FLAG = "0x10000000u"
TRACE_MAGIC = "0x46445244u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def replace_region(text: str, start: str, end: str, new: str, label: str) -> str:
    if text.count(start) != 1:
        raise SystemExit(f"{label}: expected one start marker, found {text.count(start)}")
    start_at = text.index(start)
    end_at = text.find(end, start_at + len(start))
    if end_at < 0:
        raise SystemExit(f"{label}: end marker not found")
    return text[:start_at] + new + text[end_at:]


def retire_fc_stage_blocks(text: str, label: str) -> str:
    stage = re.compile(
        rf"#if defined\({re.escape(FAT_MACRO)}\)\n"
        rf"(?:(?!#endif\n).)*?{OLD_REPORTER}\(0xfc0[1-9a]0000u"
        r"(?:(?!#endif\n).)*?#endif\n",
        re.DOTALL,
    )
    text, count = stage.subn("", text)
    if count == 0:
        raise SystemExit(f"{label}: no FC stage blocks retired")
    return text


def retire_fc_trace_state(text: str) -> str:
    """Remove the V20 cache-hit phase shortcut after the trace token changed."""
    old = (
        f"#if defined({FAT_MACRO})\n"
        "            if (aHtcleoTrace && aHtcleoTrace->iPhase == 3)\n"
        "                aHtcleoTrace->iPhase = 7;\n"
        "#endif\n"
    )
    if old in text:
        return text.replace(old, "", 1)
    return text


def fat_reporter_block() -> str:
    return (
        f"/* {NEW_MARKER} */\n"
        f"#if defined({FAT_MACRO})\n"
        "#include <u32hal.h>\n"
        "class THtcleoFatDirReadTrace\n"
        "    {\n"
        "public:\n"
        "    TUint32 iMarker;\n"
        "    };\n"
        f"#define HTCLEO_FAT_MEDIA_DRIVER_FLAG {TRACE_FLAG}\n"
        f"#define {FAT_REPORTER}(aStage) \\\n"
        "    do \\\n"
        "        { \\\n"
        "        TUint32 htcleoProgressLocation; \\\n"
        "        asm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\"); \\\n"
        "        (void)UserSvr::HalFunction(EHalGroupPlatformSpecific1,2, \\\n"
        "            (TAny*)htcleoProgressLocation,(TAny*)(TUint32)(aStage)); \\\n"
        "        } while (0)\n"
        "#endif\n\n"
    )


def transform_cache_header(text: str) -> str:
    start = f"/* {OLD_MARKER} */\n"
    end = "//-- dedicated FAT directory cache related stuff\n"
    return replace_region(text, start, end, fat_reporter_block() + end,
                          "replace V20 reporter")


def transform_std_header(text: str) -> str:
    early_forward = (
        f"#if defined({FAT_MACRO})\n"
        "class THtcleoFatDirReadTrace;\n"
        "#endif\n\n"
    )
    if early_forward not in text[:text.index("class TDriveInterface")]:
        text = replace_once(text, "class TDriveInterface\n",
                            early_forward + "class TDriveInterface\n",
                            "early trace forward declaration")
    text = replace_once(
        text,
        "\tTInt ReadNonCritical(TInt64 aPos,TInt aLength,TDes8& aTrg) const;\n",
        "\tTInt ReadNonCritical(TInt64 aPos,TInt aLength,TDes8& aTrg) const;\n"
        f"#if defined({FAT_MACRO})\n"
        "\tTInt HtcleoReadNonCritical(TInt64 aPos,TInt aLength,TDes8& aTrg, THtcleoFatDirReadTrace* aTrace) const;\n"
        "#endif\n",
        "attributed TDriveInterface read declaration",
    )
    text = replace_once(
        text,
        "        TInt Read(TInt64 aPos,TInt aLength,TDes8& aTrg) const;\n",
        "        TInt Read(TInt64 aPos,TInt aLength,TDes8& aTrg) const;\n"
        f"#if defined({FAT_MACRO})\n"
        "        TInt HtcleoRead(TInt64 aPos,TInt aLength,TDes8& aTrg, THtcleoFatDirReadTrace* aTrace) const;\n"
        "#endif\n",
        "attributed wrapper read declaration",
    )
    return text


def attributed_read_function() -> str:
    return r'''#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
TInt TDriveInterface::HtcleoReadNonCritical(TInt64 aPos, TInt aLength, TDes8& aTrg, THtcleoFatDirReadTrace* aTrace) const
{
    if (!aTrace || aTrace->iMarker != 0x46445244u)
        return ReadNonCritical(aPos, aLength, aTrg);

    HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfd010000u |
        (TUint32(aLength) & 0xffffu));
    TInt nRes = KErrNone;
    TInt cntRetry = KMaxRecoverableRetries;
    for(;;)
    {
        nRes = iProxyDrive.HtcleoRead(aPos, aLength, aTrg, aTrace);
        if (nRes == KErrNone)
            break;
        if (--cntRetry <= 0)
        {
            nRes = KErrCorrupt;
            break;
        }
        nRes = HandleRecoverableError(nRes);
        if (nRes != ERetry)
            break;
    }
    return nRes;
}
#endif

'''


def attributed_wrapper_function() -> str:
    return r'''#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
TInt TDriveInterface::XProxyDriveWrapper::HtcleoRead(TInt64 aPos, TInt aLength, TDes8& aTrg, THtcleoFatDirReadTrace* aTrace) const
{
    if (!aTrace || aTrace->iMarker != 0x46445244u)
        return Read(aPos, aLength, aTrg);
    EnterCriticalSection();
    const TUint htcleoFlags = RLocalDrive::ELocDrvMetaData | HTCLEO_FAT_MEDIA_DRIVER_FLAG;
    HTCLEO_FAT_MEDIA_READ_PROGRESS(0xfd020000u |
        ((htcleoFlags >> 16) & 0xffffu));
    TInt nRes = iLocalDrive->Read(aPos, aLength, &aTrg,
        KLocalMessageHandle, 0, htcleoFlags);
    LeaveCriticalSection();
    return nRes;
}
#endif

'''


def transform_fat_drive(text: str) -> str:
    anchor = "//---------------------------------------------------------------------------------------------------------------------------------------\n\n/**\n    Read data from the media via CProxyDrive interface. \n"
    # The first occurrence follows the three-argument ReadNonCritical body.
    at = text.find(anchor, text.index("TInt TDriveInterface::ReadNonCritical(TInt64 aPos, TInt aLength, TDes8& aTrg) const"))
    if at < 0:
        raise SystemExit("sl_drv.cpp: attributed read insertion anchor absent")
    text = text[:at] + attributed_read_function() + text[at:]

    wrapper_anchor = (
        "TInt TDriveInterface::XProxyDriveWrapper::Write(TInt64 aPos,TInt aLength,const TAny* aSrc,const RMessagePtr2 &aMessage,TInt anOffset, TUint aFlag)\n"
    )
    text = replace_once(text, wrapper_anchor,
                        attributed_wrapper_function() + wrapper_anchor,
                        "attributed wrapper implementation")
    return text


def traced_update_active_function() -> str:
    return r'''TDynamicDirCachePage* CDynamicDirCache::UpdateActivePageL(TInt64 aPos HTCLEO_FAT_TRACE_DEF)
	{
    TInt64 pageStartMedPos = CalcPageStartPos(aPos);
    ASSERT(!iLockedQ.IsEmpty());
    TDynamicDirCachePage* activePage = iLockedQ.Last();
    if (activePage->StartPos() == pageStartMedPos && activePage->IsValid())
        return activePage;

	activePage->Deque();
	LookupTblRemove(activePage->StartPos());
	activePage->SetPos(pageStartMedPos);
	TUint8* data = activePage->PtrInPage(activePage->iStartMedPos);
    TPtr8 dataPtr(data, iPageSizeInBytes);
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    const TInt nErr = (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u)
        ? iDrive.HtcleoReadNonCritical(activePage->iStartMedPos, iPageSizeInBytes, dataPtr, aHtcleoTrace)
        : iDrive.ReadNonCritical(activePage->iStartMedPos, iPageSizeInBytes, dataPtr);
#else
    const TInt nErr = iDrive.ReadNonCritical(activePage->iStartMedPos, iPageSizeInBytes, dataPtr);
#endif

	iLockedQ.AddLast(*activePage);
	LookupTblAdd(activePage);
    if(nErr != KErrNone)
        {
        DoInvalidateCache();
        User::Leave(nErr);
        }
    activePage->SetValid(ETrue);
    return activePage;
	}

'''


def traced_dir_read_function() -> str:
    return r'''void CFatMountCB::DirReadL(const TEntryPos& aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DEF) const
    {
    const TInt64 posAddr=MakeLinAddrL(aPos);
    MWTCacheInterface* const htcleoDirCache=iRawDisk->DirCacheInterface();
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iMarker == 0x46445244u && htcleoDirCache)
        {
        htcleoDirCache->HtcleoTraceReadL(posAddr, aLength, aDes, aHtcleoTrace);
        return;
        }
#endif
    if(!htcleoDirCache)
        iRawDisk->ReadCachedL(posAddr,aLength,aDes);
    else
        htcleoDirCache->ReadL(posAddr, aLength, aDes);
    }

'''


def transform_fat_paths(dynamic: str, mount: str) -> tuple[str, str]:
    dynamic = retire_fc_stage_blocks(dynamic, "sl_dir_cache.cpp")
    dynamic = retire_fc_trace_state(dynamic)
    update_start = "TDynamicDirCachePage* CDynamicDirCache::UpdateActivePageL(TInt64 aPos HTCLEO_FAT_TRACE_DEF)\n"
    update_end = "/**\nCheck if the number of (locked pages + iActive page)"
    dynamic = replace_region(dynamic, update_start, update_end,
                             traced_update_active_function(),
                             "attributed active-page media read")

    # FC01/FC0A live inside the whole diagnostic DirReadL branch, so replace
    # that function rather than deleting the reporter blocks in isolation.
    dir_start = "void CFatMountCB::DirReadL(const TEntryPos& aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DEF) const\n"
    dir_end = "//-----------------------------------------------------------------------------------------\n\n/**\n    Write a FAT directory entry"
    mount = replace_region(mount, dir_start, dir_end,
                           traced_dir_read_function(), "attributed DirReadL")
    mount = replace_once(
        mount,
        "    htcleoTrace.iPhase = 0;\n    htcleoTrace.iCacheKind = 0;\n",
        f"    htcleoTrace.iMarker = {TRACE_MAGIC};\n",
        "stack-token marker",
    )
    return dynamic, mount


def efile_reporter_block() -> str:
    return (
        f"#if defined({EFILE_MACRO})\n"
        "#include <u32hal.h>\n"
        f"#define HTCLEO_FAT_MEDIA_DRIVER_FLAG {TRACE_FLAG}\n"
        "#define HTCLEO_EFILE_MEDIA_READ_PROGRESS(aStage) \\\n"
        "    do \\\n"
        "        { \\\n"
        "        TUint32 htcleoProgressLocation; \\\n"
        "        asm volatile(\"sub %0,pc,#8\" : \"=r\"(htcleoProgressLocation) : : \"memory\"); \\\n"
        "        (void)UserSvr::HalFunction(EHalGroupPlatformSpecific1,2, \\\n"
        "            (TAny*)htcleoProgressLocation,(TAny*)(TUint32)(aStage)); \\\n"
        "        } while (0)\n"
        "#endif\n\n"
    )


def transform_efile(text: str) -> str:
    text = replace_once(text, '#include "sf_std.h"\n',
                        '#include "sf_std.h"\n' + efile_reporter_block(),
                        "EFILE media-read reporter")
    signature = (
        "TInt CLocalProxyDrive::Read(TInt64 aPos,TInt aLength,const TAny* aTrg,TInt aThreadHandle,TInt aOffset, TInt aFlags)\n"
        "\t{\n"
    )
    stage = (
        signature +
        f"#if defined({EFILE_MACRO})\n"
        "\tif ((TUint(aFlags) & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\tHTCLEO_EFILE_MEDIA_READ_PROGRESS(0xfd030000u |\n"
        "\t\t\t((TUint(aFlags) >> 16) & 0xffffu));\n"
        "#endif\n"
    )
    return replace_once(text, signature, stage, "EFILE tagged read entry")


def transform_locmedia(text: str) -> str:
    text = replace_once(
        text,
        "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage) do { } while (0)\n#endif\n",
        "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage) do { } while (0)\n#endif\n"
        f"#define HTCLEO_FAT_MEDIA_DRIVER_FLAG {TRACE_FLAG}\n",
        "ELOCD tagged flag",
    )
    text = replace_once(
        text,
        "\t\t\tr=m.ProcessMessageData(a1);\n\t\t\t__TRACE_TIMING(1);\n",
        "\t\t\tr=m.ProcessMessageData(a1);\n"
        "\t\t\tif (r == KErrNone && (m.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd040000u |\n"
        "\t\t\t\t\t((m.DriverFlags() >> 16) & 0xffffu));\n"
        "\t\t\t__TRACE_TIMING(1);\n",
        "FD04 ProcessMessageData boundary",
    )
    request_prefix = "#endif\n\t\t}\n\n"
    request_anchor = request_prefix + "\tif (iDfcQ)\n\t\t{\n"
    request_stage = (
        request_prefix +
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif ((aReq.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t{\n"
        "\t\tTUint32 htcleoRoute = iDfcQ ? 0x8000u : 0u;\n"
        "#ifdef __DEMAND_PAGING__\n"
        "\t\tif (DataPagingDeviceRegistered)\n"
        "\t\t\thtcleoRoute |= 0x4000u;\n"
        "#endif\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd050000u | htcleoRoute |\n"
        "\t\t\t(TUint32(aReq.Drive()->iDriveNumber) & 0xffu));\n"
        "\t\t}\n"
        "#endif\n\n"
        + "\tif (iDfcQ)\n\t\t{\n"
    )
    text = replace_once(text, request_anchor, request_stage,
                        "FD05 request routing boundary")
    send_anchor = "\tDDmaHelper* dmaHelper = aReq.Drive()->iDmaHelper;\n"
    text = replace_once(
        text,
        send_anchor,
        send_anchor +
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif ((aReq.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd060000u |\n"
        "\t\t\t(dmaHelper ? 0x8000u : 0u) |\n"
        "\t\t\t(TUint32(aReq.Drive()->iDriveNumber) & 0xffu));\n"
        "#endif\n",
        "FD06 converged SendReceive boundary",
    )
    do_request_anchor = "\tTInt r=KErrNone;\n\t\n\tOstTraceDefExt5( OST_TRACE_CATEGORY_RND, TRACE_REQUEST, DPRIMARYMEDIABASE_DOREQUEST,"
    text = replace_once(
        text,
        do_request_anchor,
        "\tTInt r=KErrNone;\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif ((m.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd070000u |\n"
        "\t\t\t((TUint32(iState) & 0xffu) << 8) |\n"
        "\t\t\t(TUint32(m.Drive()->iDriveNumber) & 0xffu));\n"
        "#endif\n\t\n"
        "\tOstTraceDefExt5( OST_TRACE_CATEGORY_RND, TRACE_REQUEST, DPRIMARYMEDIABASE_DOREQUEST,",
        "FD07 DoRequest entry",
    )
    driver_anchor = (
        "\t\t\tOstTraceDefExt2( OST_TRACE_CATEGORY_RND, TRACE_INTERNALS, DPRIMARYMEDIABASE_DOREQUEST_START, \"req Id=%d; Remote Thread=0x%x\", (TInt) m.Id(), (TUint) m.RemoteThread());\n"
        "\t\t\tr=media->iDriver->Request(m);\n"
    )
    text = replace_once(
        text,
        driver_anchor,
        "\t\t\tOstTraceDefExt2( OST_TRACE_CATEGORY_RND, TRACE_INTERNALS, DPRIMARYMEDIABASE_DOREQUEST_START, \"req Id=%d; Remote Thread=0x%x\", (TInt) m.Id(), (TUint) m.RemoteThread());\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\tif ((m.DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd080000u |\n"
        "\t\t\t\t\t((m.Flags() & TLocDrvRequest::EAdjusted) ? 0x8000u : 0u) |\n"
        "\t\t\t\t\t(TUint32(m.Drive()->iDriveNumber) & 0xffu));\n"
        "#endif\n"
        "\t\t\tr=media->iDriver->Request(m);\n",
        "FD08 media-driver dispatch boundary",
    )
    return text


def transform_medmmc(text: str) -> str:
    text = replace_once(
        text,
        "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage) do { } while (0)\n#endif\n",
        "#define HTCLEO_LOCALMEDIA_CAPS_PROGRESS(aStage) do { } while (0)\n#endif\n"
        f"#define HTCLEO_FAT_MEDIA_DRIVER_FLAG {TRACE_FLAG}\n",
        "MEDMMC tagged flag",
    )
    request_anchor = (
        "\t\tiCurrentReq=&aRequest;\n"
        "\t\tTUint partitionType = iCurrentReq->Drive()->iPartitionType;\n"
        "\t\tTBool readOnly = (partitionType == KPartitionTypeRofs || partitionType == KPartitionTypeROM);\n"
    )
    text = replace_once(
        text,
        request_anchor,
        request_anchor +
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (id == DLocalDrive::ERead &&\n"
        "\t\t\t(iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd090000u |\n"
        "\t\t\t\t(readOnly ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(iCurrentReq->Drive()->iDriveNumber) & 0xffu));\n"
        "#endif\n",
        "FD09 MEDMMC read dispatch",
    )
    cache_anchor = (
        "\t\tTBool allDone(EFalse);\n"
        "\t\tif ( ((r = ReadDataUntilCacheExhausted(&allDone)) == KErrNone) && !allDone)\n"
    )
    text = replace_once(
        text,
        cache_anchor,
        "\t\tTBool allDone(EFalse);\n"
        "\t\tr = ReadDataUntilCacheExhausted(&allDone);\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif ((iCurrentReq->DriverFlags() & HTCLEO_FAT_MEDIA_DRIVER_FLAG) != 0)\n"
        "\t\t\tHTCLEO_LOCALMEDIA_CAPS_PROGRESS(0xfd0a0000u |\n"
        "\t\t\t\t(allDone ? 0x8000u : 0u) |\n"
        "\t\t\t\t(TUint32(r) & 0x7fffu));\n"
        "#endif\n"
        "\t\tif (r == KErrNone && !allDone)\n",
        "FD0A MMC cache/launch boundary",
    )
    return text


def verify(files: dict[str, str]) -> None:
    joined = "\n".join(files.values())
    if OLD_REPORTER + "(0xfc0" in joined:
        raise SystemExit("retired FC01-FC0A reporter remains")
    if joined.count(NEW_MARKER) != 1:
        raise SystemExit("V21 marker must exist exactly once")
    for suffix in "123456789a":
        stage = f"0xfd0{suffix}0000u"
        if joined.count(stage) != 1:
            raise SystemExit(f"FD checkpoint missing or duplicated: {stage}")
    expected = {"fat_drv": 2, "efile": 1, "locmedia": 5, "medmmc": 2}
    for name, count in expected.items():
        if files[name].count("0xfd0") != count:
            raise SystemExit(f"{name}: expected {count} FD checkpoints")
    if joined.count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART UDF invariant failed")
    if "0xe7f000f0" in "\n".join(
        files[name] for name in ("fat_drv", "efile", "locmedia", "medmmc")
    ):
        raise SystemExit("physical UDF leaked into a returning-checkpoint image")
    if files["mount"].count("THtcleoFatDirReadTrace htcleoTrace;") != 1:
        raise SystemExit("stack-local FAT attribution token invariant failed")
    if files["mount"].count(f"htcleoTrace.iMarker = {TRACE_MAGIC};") != 1:
        raise SystemExit("stack-local FAT attribution marker invariant failed")
    if "iPhase" in files["dynamic"] or "iCacheKind" in files["dynamic"]:
        raise SystemExit("retired V20 trace-state mutation remains in dynamic cache")
    if files["dynamic"].count("HtcleoReadNonCritical(") != 1:
        raise SystemExit("dynamic cache does not issue exactly one attributed read")
    if files["fat_drv"].count("KLocalMessageHandle, 0, htcleoFlags") != 1:
        raise SystemExit("EFAT tagged local-message handoff invariant failed")
    for name in ("efile", "locmedia", "medmmc"):
        if TRACE_FLAG not in files[name]:
            raise SystemExit(f"{name}: tagged DriverFlags bit absent")
    if "static volatile" in joined:
        raise SystemExit("forbidden persistent global trace state remains")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    fat = root / "userlibandfileserver/fileserver/sfat32"
    paths = {
        "mount": fat / "sl_mnt.cpp",
        "std_header": fat / "inc/sl_std.h",
        "cache_header": fat / "sl_cache.h",
        "dynamic": fat / "sl_dir_cache.cpp",
        "fat_drv": fat / "sl_drv.cpp",
        "efile": root / "userlibandfileserver/fileserver/sfile/sf_ext.cpp",
        "locmedia": root / "kernel/eka/drivers/locmedia/locmedia.cpp",
        "medmmc": root / "kernel/eka/drivers/medmmc/medmmc.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    if NEW_MARKER in files["cache_header"]:
        early_forward = (
            f"#if defined({FAT_MACRO})\n"
            "class THtcleoFatDirReadTrace;\n"
            "#endif\n\n"
        )
        repaired = False
        if early_forward not in files["std_header"][:files["std_header"].index("class TDriveInterface")]:
            files["std_header"] = replace_once(
                files["std_header"], "class TDriveInterface\n",
                early_forward + "class TDriveInterface\n",
                "repair early trace forward declaration",
            )
            repaired = True
        repaired_dynamic = retire_fc_trace_state(files["dynamic"])
        if repaired_dynamic != files["dynamic"]:
            files["dynamic"] = repaired_dynamic
            repaired = True
        if repaired:
            paths["std_header"].write_text(files["std_header"], encoding="utf-8")
            paths["dynamic"].write_text(files["dynamic"], encoding="utf-8")
        verify(files)
        print("HTCLEO_FAT_MEDIA_READ_PROGRESS=10 FD01_FD0A=installed")
        return
    if OLD_MARKER not in files["cache_header"]:
        raise SystemExit("V20 FC01-FC0A baseline is absent")

    files["cache_header"] = transform_cache_header(files["cache_header"])
    files["std_header"] = transform_std_header(files["std_header"])
    files["fat_drv"] = transform_fat_drive(files["fat_drv"])
    files["dynamic"], files["mount"] = transform_fat_paths(
        files["dynamic"], files["mount"]
    )
    files["efile"] = transform_efile(files["efile"])
    files["locmedia"] = transform_locmedia(files["locmedia"])
    files["medmmc"] = transform_medmmc(files["medmmc"])
    verify(files)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    print("HTCLEO_FAT_MEDIA_READ_PROGRESS=10 FD01_FD0A=installed")


if __name__ == "__main__":
    main()
