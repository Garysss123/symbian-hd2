#!/usr/bin/env python3
"""Trace the exact first C: volume-label directory-cache read.

Iteration 379 reached FB08 immediately before MWTCacheInterface::ReadL() and
did not reach FB09.  Retire FB01-FB0A and carry a stack-local trace token from
FindVolumeLabelFileL() into that one virtual cache call.  This prevents the
UID cache, FAT scanner, another drive, or a concurrent request from consuming
the FC01-FC0A checkpoints.
"""

from __future__ import annotations

import pathlib
import re
import sys


OLD_MARKER = "HTCLEO_FAT_FIRST_DIRENTRY_PROGRESS_V19"
NEW_MARKER = "HTCLEO_FAT_DIRECTORY_CACHE_READ_PROGRESS_V20"
FAT_MACRO = "__HTCLEO_FAT_MOUNT_PROGRESS__"
OLD_REPORTER = "HTCLEO_FAT_DIRENTRY_PROGRESS"
REPORTER = "HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def replace_region(text: str, start: str, end: str, new: str, label: str) -> str:
    start_count = text.count(start)
    if start_count != 1:
        raise SystemExit(f"{label}: expected one start marker, found {start_count}")
    start_at = text.index(start)
    end_at = text.find(end, start_at + len(start))
    if end_at < 0:
        raise SystemExit(f"{label}: end marker not found")
    return text[:start_at] + new + text[end_at:]


def retire_v19_common(text: str) -> str:
    reporter = re.compile(
        rf"/\* {OLD_MARKER} \*/\n"
        rf"#if defined\({re.escape(FAT_MACRO)}\)\n"
        r"(?:(?!#endif\n).)*?#endif\n\n",
        re.DOTALL,
    )
    text, count = reporter.subn("", text)
    if count != 1:
        raise SystemExit(f"sl_mnt.cpp: expected one V19 reporter, found {count}")

    stage = re.compile(
        rf"#if defined\({re.escape(FAT_MACRO)}\)\n"
        rf"(?:(?!#endif\n).)*?{OLD_REPORTER}\(0xfb0[1-9a]0000u"
        r"(?:(?!#endif\n).)*?#endif\n",
        re.DOTALL,
    )
    text, count = stage.subn("", text)
    if count != 10:
        raise SystemExit(f"sl_mnt.cpp: expected ten V19 stages, found {count}")

    text = replace_once(
        text,
        f"#if defined({FAT_MACRO})\n"
        "    if (iHtcleoMountProgressPhase == 0 && DriveNumber() == EDriveC &&\n"
        "        State() == EInit_R && aDosEntryPos.iPos == 0)\n"
        "        iHtcleoMountProgressPhase = 1;\n"
        "#endif\n",
        "",
        "retire V19 volume-label arm",
    )
    text = replace_once(
        text,
        f"#if defined({FAT_MACRO})\n"
        "    iHtcleoMountProgressPhase = 0;\n"
        "#endif\n",
        "",
        "retire V19 constructor phase",
    )
    return text


def trace_declaration_macros() -> str:
    return (
        "class MWTCacheInterface;\n\n"
        f"#if defined({FAT_MACRO})\n"
        "class THtcleoFatDirReadTrace;\n"
        "#define HTCLEO_FAT_TRACE_DECL , THtcleoFatDirReadTrace* aHtcleoTrace = NULL\n"
        "#define HTCLEO_FAT_TRACE_DEF , THtcleoFatDirReadTrace* aHtcleoTrace\n"
        "#define HTCLEO_FAT_TRACE_ARG , aHtcleoTrace\n"
        "#define HTCLEO_FAT_TRACE_NULL_ARG , NULL\n"
        "#else\n"
        "#define HTCLEO_FAT_TRACE_DECL\n"
        "#define HTCLEO_FAT_TRACE_DEF\n"
        "#define HTCLEO_FAT_TRACE_ARG\n"
        "#define HTCLEO_FAT_TRACE_NULL_ARG\n"
        "#endif\n"
    )


def transform_std_header(text: str) -> str:
    text = replace_once(
        text,
        f"#if defined({FAT_MACRO})\n"
        "    mutable TUint32 iHtcleoMountProgressPhase;\n"
        "#endif\n\n",
        "",
        "retire V19 mount phase member",
    )
    text = replace_once(
        text,
        "class MWTCacheInterface;\n",
        trace_declaration_macros(),
        "trace declaration macros",
    )
    declarations = {
        "    void ReadDirEntryL(const TEntryPos& aPos,TFatDirEntry& aDirEntry) const;":
            "    void ReadDirEntryL(const TEntryPos& aPos,TFatDirEntry& aDirEntry HTCLEO_FAT_TRACE_DECL) const;",
        "    void DirReadL(const TEntryPos& aPos,TInt aLength,TDes8& aDes) const;":
            "    void DirReadL(const TEntryPos& aPos,TInt aLength,TDes8& aDes HTCLEO_FAT_TRACE_DECL) const;",
        "\tTInt GetDirEntry(TEntryPos& aPos,TFatDirEntry& aDosEntry,TFatDirEntry& aStartEntry,TDes& aLongFileName) const;":
            "\tTInt GetDirEntry(TEntryPos& aPos,TFatDirEntry& aDosEntry,TFatDirEntry& aStartEntry,TDes& aLongFileName HTCLEO_FAT_TRACE_DECL) const;",
        "    TBool DoGetDirEntryL(TEntryPos& aPos,TFatDirEntry& aDosEntry,TFatDirEntry& aStartEntry,TDes& aLongFileName) const;":
            "    TBool DoGetDirEntryL(TEntryPos& aPos,TFatDirEntry& aDosEntry,TFatDirEntry& aStartEntry,TDes& aLongFileName HTCLEO_FAT_TRACE_DECL) const;",
    }
    for old, new in declarations.items():
        text = replace_once(text, old, new, f"trace declaration {old.strip().split('(')[0]}")
    return text


def cache_reporter_block() -> str:
    return (
        f"/* {NEW_MARKER} */\n"
        f"#if defined({FAT_MACRO})\n"
        "#include <u32hal.h>\n"
        "class THtcleoFatDirReadTrace\n"
        "    {\n"
        "public:\n"
        "    TUint32 iPhase;\n"
        "    TUint32 iCacheKind;\n"
        "    };\n"
        f"#define {REPORTER}(aStage) \\\n"
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
    text = replace_once(
        text,
        "//-- dedicated FAT directory cache related stuff\n",
        cache_reporter_block() + "//-- dedicated FAT directory cache related stuff\n",
        "V20 reporter and trace type",
    )
    text = replace_once(
        text,
        "        virtual void    ReadL(TInt64 aPos, TInt aLength, TDes8& aDes)=0;\n",
        "        virtual void    ReadL(TInt64 aPos, TInt aLength, TDes8& aDes)=0;\n"
        f"#if defined({FAT_MACRO})\n"
        "        virtual TUint32 HtcleoTraceKind() const=0;\n"
        "        virtual void HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace* aTrace)=0;\n"
        "#endif\n",
        "diagnostic cache virtual interface",
    )
    text = replace_once(
        text,
        "        void    ReadL (TInt64 aPos,TInt aLength,TDes8& aDes);\n",
        "        void    ReadL (TInt64 aPos,TInt aLength,TDes8& aDes);\n"
        f"#if defined({FAT_MACRO})\n"
        "        TUint32 HtcleoTraceKind() const;\n"
        "        void HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace* aTrace);\n"
        "#endif\n",
        "legacy cache diagnostic declarations",
    )
    return text


def transform_dynamic_header(text: str) -> str:
    text = replace_once(
        text,
        "\tvoid    ReadL (TInt64 aPos, TInt aLength, TDes8& aDes);\n",
        "\tvoid    ReadL (TInt64 aPos, TInt aLength, TDes8& aDes);\n"
        f"#if defined({FAT_MACRO})\n"
        "\tTUint32 HtcleoTraceKind() const;\n"
        "\tvoid HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace* aTrace);\n"
        "#endif\n",
        "dynamic cache diagnostic declarations",
    )
    text = replace_once(
        text,
        "\tvoid ReadDataFromSinglePageL(TInt64 aPos, TInt aLength, TDes8& aDes);\n",
        "\tvoid ReadDataFromSinglePageL(TInt64 aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DECL);\n"
        "\tvoid HtcleoDoReadL(TInt64 aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DECL);\n",
        "dynamic single-page trace helper",
    )
    text = replace_once(
        text,
        "\tTDynamicDirCachePage* UpdateActivePageL(TInt64 aPos);\n",
        "\tTDynamicDirCachePage* UpdateActivePageL(TInt64 aPos HTCLEO_FAT_TRACE_DECL);\n",
        "dynamic active-page trace helper",
    )
    return text


def transform_legacy_cache(text: str) -> str:
    anchor = (
        "void CMediaWTCache::ReadL(TInt64 aPos,TInt aLength,TDes8& aDes)\n"
        "    {\n"
    )
    diagnostic = (
        f"#if defined({FAT_MACRO})\n"
        "TUint32 CMediaWTCache::HtcleoTraceKind() const\n"
        "    {\n"
        "    return 2;\n"
        "    }\n\n"
        "void CMediaWTCache::HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace*)\n"
        "    {\n"
        "    ReadL(aPos, aLength, aDes);\n"
        "    }\n"
        "#endif\n\n"
    )
    return replace_once(text, anchor, diagnostic + anchor, "legacy diagnostic implementation")


def read_data_function() -> str:
    return r'''void CDynamicDirCache::ReadDataFromSinglePageL(TInt64 aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DEF)
	{
    //-- the data section is in the cache page entirely, take data directly from the cache
	TDynamicDirCachePage* pPage = FindPageByPos(aPos);
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 2)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc030000u |
            (pPage ? 0x8000u : 0u) |
            (pPage && pPage->IsLocked() ? 0x4000u : 0u) |
            (pPage && pPage->IsValid() ? 0x2000u : 0u) |
            (TUint32(aLength) & 0xffu));
        aHtcleoTrace->iPhase = 3;
        }
#endif
    if (pPage)
    	{
		// lock page before reading,
    	if (LockPage(pPage) != NULL)
    		{
    		// read data and append them to the descriptor
            aDes.Append(pPage->PtrInPage(aPos), aLength);
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
            if (aHtcleoTrace && aHtcleoTrace->iPhase == 3)
                aHtcleoTrace->iPhase = 7;
#endif

            // if page is from unlocked queue, try to keep it locked until we move to a
            // different page from the unlocked queue
            if (pPage->PageType() == TDynamicDirCachePage::EUnlocked
                && iLastVisitedPage != pPage)
                {
                if(iLastVisitedPage && iLastVisitedPage->PageType() == TDynamicDirCachePage::EUnlocked)
                    User::LeaveIfError(UnlockPage(iLastVisitedPage));
                iLastVisitedPage = pPage;
            	}
    		}
    	else
    		{
    		ASSERT(pPage->PageType() == TDynamicDirCachePage::EUnlocked);
    		DeQueue(pPage);
    		LookupTblRemove(pPage->StartPos());
    		DecommitPage(pPage);
    		delete pPage;
    		pPage = NULL;
    		}
    	}

	if (!pPage)
		{
        pPage = UpdateActivePageL(aPos HTCLEO_FAT_TRACE_ARG);
        aDes.Append(pPage->PtrInPage(aPos), aLength);
    	}

#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 7)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc080000u |
            (pPage && pPage->IsValid() ? 0x8000u : 0u) |
            (pPage && pPage->IsLocked() ? 0x4000u : 0u) |
            (TUint32(aLength) & 0xffu));
        aHtcleoTrace->iPhase = 8;
        }
#endif
	}

'''


def read_dispatch_functions() -> str:
    return r'''void CDynamicDirCache::ReadL(TInt64 aPos, TInt aLength, TDes8& aDes)
	{
    HtcleoDoReadL(aPos, aLength, aDes HTCLEO_FAT_TRACE_NULL_ARG);
	}

#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
TUint32 CDynamicDirCache::HtcleoTraceKind() const
    {
    return 1;
    }

void CDynamicDirCache::HtcleoTraceReadL(TInt64 aPos, TInt aLength, TDes8& aDes, THtcleoFatDirReadTrace* aTrace)
    {
    HtcleoDoReadL(aPos, aLength, aDes, aTrace);
    }
#endif

void CDynamicDirCache::HtcleoDoReadL(TInt64 aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DEF)
	{
#ifdef _DEBUG
    if(iCacheDisabled)
        {
        __PRINT(_L("CDynamicDirCache disabled"));
        User::LeaveIfError(iDrive.ReadNonCritical(aPos, aLength, aDes));
        return;
        }
#endif //_DEBUG

    aDes.Zero();
    const TUint32 PageSz = iPageSizeInBytes;
    TInt64 pageStartMedPos = CalcPageStartPos(aPos);
    const TUint32 bytesToPageEnd = (TUint32)(pageStartMedPos + PageSz - aPos);
    const TBool htcleoSinglePage = (TUint32)aLength <= bytesToPageEnd;
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 1)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc020000u |
            (htcleoSinglePage ? 0x8000u : 0u) |
            ((iPageSizeLog2 & 0x7fu) << 8) |
            (TUint32(aLength) & 0xffu));
        aHtcleoTrace->iPhase = 2;
        }
#endif

    if(htcleoSinglePage)
        {
        ReadDataFromSinglePageL(aPos, aLength, aDes HTCLEO_FAT_TRACE_ARG);
        }
    else
        {
        __PRINT(_L("CDynamicDirCache::ReadL() CROSS PAGE!"));
        TUint32 dataLen(aLength);
        TInt64 currMediaPos(aPos);
        ReadDataFromSinglePageL(currMediaPos, bytesToPageEnd, aDes HTCLEO_FAT_TRACE_ARG);
        dataLen -= bytesToPageEnd;
        currMediaPos += bytesToPageEnd;
        while (dataLen >= PageSz)
        	{
            ReadDataFromSinglePageL(currMediaPos, PageSz, aDes HTCLEO_FAT_TRACE_ARG);
            currMediaPos += PageSz;
            dataLen -= PageSz;
        	}
        if(dataLen > 0)
            ReadDataFromSinglePageL(currMediaPos, dataLen, aDes HTCLEO_FAT_TRACE_ARG);
        }
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 8)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc090000u |
            (htcleoSinglePage ? 0x8000u : 0u) |
            (TUint32(aDes.Length()) & 0x7fffu));
        aHtcleoTrace->iPhase = 9;
        }
#endif
	}

'''


def update_active_function() -> str:
    return r'''TDynamicDirCachePage* CDynamicDirCache::UpdateActivePageL(TInt64 aPos HTCLEO_FAT_TRACE_DEF)
	{
    TInt64 pageStartMedPos = CalcPageStartPos(aPos);
    ASSERT(!iLockedQ.IsEmpty());
    TDynamicDirCachePage* activePage = iLockedQ.Last();

#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 3)
        {
        const TBool htcleoSamePage = activePage->StartPos() == pageStartMedPos;
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc040000u |
            (htcleoSamePage ? 0x8000u : 0u) |
            (activePage->IsValid() ? 0x4000u : 0u) |
            (activePage->IsLocked() ? 0x2000u : 0u) |
            (TUint32(iPageSizeLog2) & 0xffu));
        aHtcleoTrace->iPhase = (htcleoSamePage && activePage->IsValid()) ? 7 : 4;
        }
#endif
    if (activePage->StartPos() == pageStartMedPos && activePage->IsValid())
        return activePage;

	activePage->Deque();
	const TInt htcleoRemoveResult = LookupTblRemove(activePage->StartPos());
	activePage->SetPos(pageStartMedPos);
	TUint8* data = activePage->PtrInPage(activePage->iStartMedPos);
    TPtr8 dataPtr(data, iPageSizeInBytes);
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 4)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc050000u |
            ((iPageSizeLog2 & 0xffu) << 8) |
            (TUint32(htcleoRemoveResult) & 0xffu));
        aHtcleoTrace->iPhase = 5;
        }
#endif

    const TInt nErr = iDrive.ReadNonCritical(activePage->iStartMedPos, iPageSizeInBytes, dataPtr);
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 5)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc060000u |
            (TUint32(nErr) & 0xffffu));
        aHtcleoTrace->iPhase = 6;
        }
#endif

	iLockedQ.AddLast(*activePage);
	const TInt htcleoAddResult = LookupTblAdd(activePage);
    if(nErr != KErrNone)
        {
        DoInvalidateCache();
        User::Leave(nErr);
        }
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace && aHtcleoTrace->iPhase == 6)
        {
        HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc070000u |
            (TUint32(htcleoAddResult) & 0xffffu));
        aHtcleoTrace->iPhase = 7;
        }
#endif
    activePage->SetValid(ETrue);
    return activePage;
	}

'''


def transform_dynamic_cache(text: str) -> str:
    read_data_start = "void CDynamicDirCache::ReadDataFromSinglePageL(TInt64 aPos, TInt aLength, TDes8& aDes)\n"
    read_data_end = "//====================================================================\n/**\nImplementation of pure virtual function."
    text = replace_region(text, read_data_start, read_data_end, read_data_function(), "dynamic single-page read")

    read_start = "void CDynamicDirCache::ReadL(TInt64 aPos, TInt aLength, TDes8& aDes)\n"
    read_end = "/**\nWrite data through a single page."
    text = replace_region(text, read_start, read_end, read_dispatch_functions(), "dynamic ReadL dispatch")

    update_start = "TDynamicDirCachePage* CDynamicDirCache::UpdateActivePageL(TInt64 aPos)\n"
    update_end = "/**\nCheck if the number of (locked pages + iActive page)"
    text = replace_region(text, update_start, update_end, update_active_function(), "dynamic active-page read")
    return text


def dir_read_function() -> str:
    return r'''void CFatMountCB::DirReadL(const TEntryPos& aPos, TInt aLength, TDes8& aDes HTCLEO_FAT_TRACE_DEF) const
    {
    const TInt64 posAddr=MakeLinAddrL(aPos);
    MWTCacheInterface* const htcleoDirCache=iRawDisk->DirCacheInterface();
#if defined(__HTCLEO_FAT_MOUNT_PROGRESS__)
    if (aHtcleoTrace)
        {
        const TUint32 htcleoCacheKind = htcleoDirCache ? htcleoDirCache->HtcleoTraceKind() : 0;
        aHtcleoTrace->iCacheKind = htcleoCacheKind;
        if (aHtcleoTrace->iPhase == 0)
            {
            HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc010000u |
                (htcleoCacheKind == 1 ? 0x8000u : 0u) |
                (htcleoCacheKind == 2 ? 0x4000u : 0u) |
                (TUint32(aLength) & 0x3fffu));
            aHtcleoTrace->iPhase = 1;
            }
        if (htcleoDirCache)
            htcleoDirCache->HtcleoTraceReadL(posAddr, aLength, aDes, aHtcleoTrace);
        else
            iRawDisk->ReadCachedL(posAddr, aLength, aDes);
        if ((htcleoCacheKind == 1 && aHtcleoTrace->iPhase == 9) ||
            (htcleoCacheKind != 1 && aHtcleoTrace->iPhase == 1))
            {
            HTCLEO_FAT_DIRECTORY_CACHE_PROGRESS(0xfc0a0000u |
                (htcleoCacheKind == 1 ? 0x8000u : 0u) |
                (htcleoCacheKind == 2 ? 0x4000u : 0u) |
                (TUint32(aDes.Length()) & 0x3fffu));
            aHtcleoTrace->iPhase = 10;
            }
        return;
        }
#endif
    if(!htcleoDirCache)
        iRawDisk->ReadCachedL(posAddr,aLength,aDes);
    else
        htcleoDirCache->ReadL(posAddr, aLength, aDes);
    }

'''


def transform_mount_common(text: str) -> str:
    text = retire_v19_common(text)
    definitions = {
        "TBool CFatMountCB::DoGetDirEntryL(TEntryPos& aPos, TFatDirEntry& aDosEntry, TFatDirEntry& aStartEntry, TDes& aLongFileName) const":
            "TBool CFatMountCB::DoGetDirEntryL(TEntryPos& aPos, TFatDirEntry& aDosEntry, TFatDirEntry& aStartEntry, TDes& aLongFileName HTCLEO_FAT_TRACE_DEF) const",
        "TInt CFatMountCB::GetDirEntry(TEntryPos& aPos,TFatDirEntry& aDosEntry,TFatDirEntry& aStartEntry,TDes& aLongFileName) const":
            "TInt CFatMountCB::GetDirEntry(TEntryPos& aPos,TFatDirEntry& aDosEntry,TFatDirEntry& aStartEntry,TDes& aLongFileName HTCLEO_FAT_TRACE_DEF) const",
        "void CFatMountCB::ReadDirEntryL(const TEntryPos& aPos,TFatDirEntry& aDirEntry) const":
            "void CFatMountCB::ReadDirEntryL(const TEntryPos& aPos,TFatDirEntry& aDirEntry HTCLEO_FAT_TRACE_DEF) const",
    }
    for old, new in definitions.items():
        text = replace_once(text, old, new, f"trace definition {old.split('(')[0]}")
    text = replace_once(
        text,
        "    ReadDirEntryL(aPos,aStartEntry);\n",
        "    ReadDirEntryL(aPos,aStartEntry HTCLEO_FAT_TRACE_ARG);\n",
        "first directory entry trace propagation",
    )
    text = replace_once(
        text,
        "    TRAPD(nErr, bEntryOK = DoGetDirEntryL(aPos, aDosEntry, aStartEntry, aLongFileName));\n",
        "    TRAPD(nErr, bEntryOK = DoGetDirEntryL(aPos, aDosEntry, aStartEntry, aLongFileName HTCLEO_FAT_TRACE_ARG));\n",
        "GetDirEntry trace propagation",
    )
    text = replace_once(
        text,
        "    DirReadL(aPos,KSizeOfFatDirEntry,buf);\n",
        "    DirReadL(aPos,KSizeOfFatDirEntry,buf HTCLEO_FAT_TRACE_ARG);\n",
        "ReadDirEntry trace propagation",
    )

    dir_start = "void CFatMountCB::DirReadL(const TEntryPos& aPos, TInt aLength, TDes8& aDes) const\n"
    dir_end = "//-----------------------------------------------------------------------------------------\n\n/**\n    Write a FAT directory entry"
    text = replace_region(text, dir_start, dir_end, dir_read_function(), "exact traced DirReadL")

    find_signature = (
        "void CFatMountCB::FindVolumeLabelFileL(TDes8& aLabel, TEntryPos& aDosEntryPos, TFatDirEntry& aDosEntry)\n"
        "    {\n"
    )
    text = replace_once(
        text,
        find_signature,
        find_signature +
        f"#if defined({FAT_MACRO})\n"
        "    THtcleoFatDirReadTrace htcleoTrace;\n"
        "    htcleoTrace.iPhase = 0;\n"
        "    htcleoTrace.iCacheKind = 0;\n"
        "    THtcleoFatDirReadTrace* htcleoTracePtr =\n"
        "        (DriveNumber() == EDriveC && State() == EInit_R && aDosEntryPos.iPos == 0)\n"
        "        ? &htcleoTrace : NULL;\n"
        "#endif\n",
        "stack-local first volume-label trace",
    )
    text = replace_once(
        text,
        "        TInt htcleoDirEntryResult=GetDirEntry(aDosEntryPos, aDosEntry, startEntry, dummyLongName);\n"
        "        User::LeaveIfError(htcleoDirEntryResult);\n",
        f"#if defined({FAT_MACRO})\n"
        "        TInt htcleoDirEntryResult=GetDirEntry(aDosEntryPos, aDosEntry, startEntry, dummyLongName, htcleoTracePtr);\n"
        "        htcleoTracePtr = NULL;\n"
        "#else\n"
        "        TInt htcleoDirEntryResult=GetDirEntry(aDosEntryPos, aDosEntry, startEntry, dummyLongName);\n"
        "#endif\n"
        "        User::LeaveIfError(htcleoDirEntryResult);\n",
        "one-shot volume-label trace call",
    )
    return text


def verify(files: dict[str, str]) -> None:
    joined = "\n".join(files.values())
    if OLD_MARKER in joined or f"{OLD_REPORTER}(0xfb0" in joined:
        raise SystemExit("retired FB01-FB0A reporter remains")
    if joined.count(NEW_MARKER) != 1:
        raise SystemExit("V20 marker must exist exactly once")
    for suffix in "123456789a":
        stage = f"fc0{suffix}0000u"
        if joined.count(f"{REPORTER}(0x{stage}") != 1:
            raise SystemExit(f"FC checkpoint missing or duplicated: {stage}")
    if files["mount"].count(f"{REPORTER}(0xfc") != 2:
        raise SystemExit("sl_mnt.cpp must contain FC01 and FC0A only")
    if files["dynamic_cpp"].count(f"{REPORTER}(0xfc") != 8:
        raise SystemExit("sl_dir_cache.cpp must contain FC02 through FC09")
    if f"{REPORTER}(0xfc" in files["legacy_cpp"]:
        raise SystemExit("legacy cache must not own physical FC checkpoints")
    if "iHtcleoMountProgressPhase" in joined or "static volatile" in joined:
        raise SystemExit("forbidden persistent/global trace state remains")
    if joined.count("THtcleoFatDirReadTrace htcleoTrace;") != 1:
        raise SystemExit("stack-local trace token invariant failed")
    if joined.count("HtcleoTraceReadL") < 6:
        raise SystemExit("diagnostic virtual route is incomplete")
    if files["mmp"].count(f"MACRO           {FAT_MACRO}") != 1:
        raise SystemExit("efat32 probe macro invariant failed")
    if files["mmp"].count("ALWAYS_BUILD_AS_ARM") != 1:
        raise SystemExit("efat32 ARM checkpoint invariant failed")
    if files["estart_main"].count("0xe7f000f0") != 1:
        raise SystemExit("durable ESTART UDF invariant failed")
    for name in ("mount", "dynamic_cpp", "legacy_cpp"):
        if "0xe7f000f0" in files[name]:
            raise SystemExit(f"physical UDF leaked into {name}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    base = root / "userlibandfileserver/fileserver/sfat32"
    paths = {
        "mount": base / "sl_mnt.cpp",
        "std_header": base / "inc/sl_std.h",
        "cache_header": base / "sl_cache.h",
        "dynamic_header": base / "sl_dir_cache.h",
        "legacy_cpp": base / "sl_cache.cpp",
        "dynamic_cpp": base / "sl_dir_cache.cpp",
        "mmp": base / "efat32.mmp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}

    if NEW_MARKER in files["cache_header"]:
        verify(files)
        print("HTCLEO_FAT_DIRECTORY_CACHE_READ_PROGRESS=10 FC01_FC0A=installed")
        return
    if OLD_MARKER not in files["mount"]:
        raise SystemExit("V19 FB01-FB0A baseline is absent")

    files["std_header"] = transform_std_header(files["std_header"])
    files["cache_header"] = transform_cache_header(files["cache_header"])
    files["dynamic_header"] = transform_dynamic_header(files["dynamic_header"])
    files["legacy_cpp"] = transform_legacy_cache(files["legacy_cpp"])
    files["dynamic_cpp"] = transform_dynamic_cache(files["dynamic_cpp"])
    files["mount"] = transform_mount_common(files["mount"])
    verify(files)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    print("HTCLEO_FAT_DIRECTORY_CACHE_READ_PROGRESS=10 FC01_FC0A=installed")


if __name__ == "__main__":
    main()
