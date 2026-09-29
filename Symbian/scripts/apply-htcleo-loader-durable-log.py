#!/usr/bin/env python3
"""Install NVG-attributed dense durable logging in the native EFILE loader.

The trace is armed only for the top-level ``nvgrenderstage.dll``
``ELoadLibrary`` request.  While that request is active, completed loader
boundaries append fixed 53-byte records to ``C:\\Symbian3\\LDRLOG.TXT``.
Logging reuses EFILE's already-connected ``gTheLoaderFs`` session, is
fail-open, and never changes a loader result or adds a delay.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_LOADER_DURABLE_LOG_V1"
MACRO = "__HTCLEO_LOADER_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HEADER = r'''#ifndef HTCLEO_LOADER_DURABLE_LOG_H
#define HTCLEO_LOADER_DURABLE_LOG_H

#include <e32std.h>

#ifdef __HTCLEO_LOADER_DURABLE_LOG__
TBool HtcleoLoaderTraceStart(const TDesC8& aName);
void HtcleoLoaderTraceStop();
void HtcleoLoaderLog(TUint32 aStage, TInt aResult,
                     const TDesC8& aName, TUint32 aDetail);
#else
static inline TBool HtcleoLoaderTraceStart(const TDesC8&) { return EFalse; }
static inline void HtcleoLoaderTraceStop() {}
static inline void HtcleoLoaderLog(TUint32, TInt, const TDesC8&, TUint32) {}
#endif

#endif
'''


LOGGER = r'''// HTCLEO_LOADER_DURABLE_LOG_V1
#include "sf_std.h"
#include "sf_image.h"
#include "HtcleoLoaderLog.h"

#ifdef __HTCLEO_LOADER_DURABLE_LOG__

static TBool gHtcleoLoaderTraceActive = EFalse;
static TBool gHtcleoLoaderReplaceLog = EFalse;

static TUint32 HtcleoLoaderNameTag(const TDesC8& aName)
	{
	TInt slash = aName.LocateReverse('\\');
	TInt forward = aName.LocateReverse('/');
	TInt start = (slash > forward ? slash : forward) + 1;
	TUint32 hash = 2166136261u;
	for(TInt i=start; i<aName.Length(); ++i)
		{
		TUint8 c = aName[i];
		if(c >= 'A' && c <= 'Z')
			c = (TUint8)(c + ('a' - 'A'));
		hash ^= c;
		hash *= 16777619u;
		}
	return hash;
	}

TBool HtcleoLoaderTraceStart(const TDesC8& aName)
	{
	_LIT8(KHtcleoNvgDll, "nvgrenderstage.dll");
	TInt slash = aName.LocateReverse('\\');
	TInt forward = aName.LocateReverse('/');
	TInt start = (slash > forward ? slash : forward) + 1;
	TPtrC8 base(aName.Mid(start));
	if(base.FindF(KHtcleoNvgDll) != 0)
		return EFalse;
	gHtcleoLoaderTraceActive = ETrue;
	gHtcleoLoaderReplaceLog = ETrue;
	return ETrue;
	}

void HtcleoLoaderTraceStop()
	{
	gHtcleoLoaderTraceActive = EFalse;
	gHtcleoLoaderReplaceLog = EFalse;
	}

void HtcleoLoaderLog(TUint32 aStage, TInt aResult,
					 const TDesC8& aName, TUint32 aDetail)
					 __attribute__((noinline));

void HtcleoLoaderLog(TUint32 aStage, TInt aResult,
					 const TDesC8& aName, TUint32 aDetail)
	{
	if(!gHtcleoLoaderTraceActive)
		return;

	_LIT(KHtcleoLoaderLogPath, "C:\\Symbian3\\LDRLOG.TXT");
	RFile file;
	TInt position = 0;
	TInt r;
	if(gHtcleoLoaderReplaceLog)
		{
		r = file.Replace(gTheLoaderFs, KHtcleoLoaderLogPath,
						 EFileWrite | EFileShareAny);
		if(r == KErrNone)
			gHtcleoLoaderReplaceLog = EFalse;
		}
	else
		{
		r = file.Open(gTheLoaderFs, KHtcleoLoaderLogPath,
					  EFileWrite | EFileShareAny);
		if(r == KErrNone)
			r = file.Seek(ESeekEnd, position);
		}

	// Every record is exactly 53 bytes.  The file offset is the sequence
	// source, so failed writes cannot corrupt an in-memory sequence counter.
	if(r == KErrNone && position < (1024 * 53))
		{
		_LIT8(KHtcleoLoaderPrefix, "HTCLEO_LDR ");
		TBuf8<64> record;
		record.Append(KHtcleoLoaderPrefix);
		record.AppendNumFixedWidth((TUint)(position / 53), EHex, 4);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(HtcleoLoaderNameTag(aName), EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(_L8("\r\n"));
		r = file.Write(record);
		if(r == KErrNone)
			(void)file.Flush();
		}
	file.Close();
	}
#endif
'''


LOAD_LIBRARY_CASE = r'''		case ELoadLibrary:
			{
			r=E32Loader::CheckClientState(msg.Handle());
			if (r!=KErrNone)
				ldrReq.Panic(ELoadLibraryWithoutDllLock);
			else
				r=ldrReq.AddFileExtension(KFileExtensionDll);
			TBool htcleoLoaderTrace = EFalse;
			if (r==KErrNone)
				{
				htcleoLoaderTrace = HtcleoLoaderTraceStart(*ldrReq.iFileName);
				HtcleoLoaderLog(0x00001001u, r, *ldrReq.iFileName, (TUint32)mid);
				}
			if (r==KErrNone)
				{
				r=msg.GetString(ldrReq.iPath, 2, KMaxPath, 0, ETrue);
				HtcleoLoaderLog(0x00001002u, r, *ldrReq.iFileName,
							ldrReq.iPath ? (TUint32)ldrReq.iPath->Length() : 0u);
				}
			if (ldrReq.iPath)
				{
				__IF_DEBUG(Printf("Path: %S", ldrReq.iPath));
				}
			if (r==KErrNone)
				{
				r = ldrReq.CheckForSubstDrivesInPath();
				HtcleoLoaderLog(0x00001003u, r, *ldrReq.iFileName,
							ldrReq.iPath ? (TUint32)ldrReq.iPath->Length() : 0u);
				}
			if (ldrReq.iPath)
				{
				__IF_DEBUG(Printf("Post-subst Path: %S", ldrReq.iPath));
				}
			if (r==KErrNone)
				{
				r=msg.GetLdrInfo(ldrReq);
				HtcleoLoaderLog(0x00001004u, r, *ldrReq.iFileName,
							(TUint32)ldrReq.iRequestedUids[2].iUid);
				}
			if (r==KErrNone)
				{
				HtcleoLoaderLog(0x00001005u, r, *ldrReq.iFileName,
							(TUint32)ldrReq.iOwnerType);
				r=LoadLibrary(ldrReq);
				HtcleoLoaderLog(0x00001006u, r, *ldrReq.iFileName,
							(TUint32)ldrReq.iHandle);
				}
			if(htcleoLoaderTrace)
				HtcleoLoaderTraceStop();
			break;
			}
'''


LOAD_LIBRARY_FUNCTION = r'''TInt LoadLibrary(RLdrReq& aReq)
	{
	__LDRTRACE(aReq.Dump("LoadLibrary:"));
	HtcleoLoaderLog(0x00001101u, KErrNone, *aReq.iFileName,
					(TUint32)aReq.iRequestedUids[2].iUid);
	TInt32* uid=(TInt32*)&aReq.iRequestedUids;
	if (uid[0] && uid[0]!=KDynamicLibraryUidValue)
		{
		HtcleoLoaderLog(0x000011e1u, KErrNotSupported, *aReq.iFileName,
					(TUint32)uid[0]);
		return KErrNotSupported;
		}
	uid[0]=KDynamicLibraryUidValue;
	TInt r=KErrNone;
	if (aReq.iMsg)
		{
		r = aReq.iMsg->Client(aReq.iClientThread);
		HtcleoLoaderLog(0x00001102u, r, *aReq.iFileName,
					(TUint32)aReq.iClientThread.Handle());
		if (r==KErrNone)
			{
			r = aReq.iClientThread.Process(aReq.iClientProcess);
			HtcleoLoaderLog(0x00001103u, r, *aReq.iFileName,
						(TUint32)aReq.iClientProcess.Handle());
			}
		if (r!=KErrNone)
			return r;
		}
	else
		{
		aReq.iClientThread.SetHandle(KCurrentThreadHandle);
		aReq.iClientProcess.SetHandle(KCurrentProcessHandle);
		HtcleoLoaderLog(0x00001103u, KErrNone, *aReq.iFileName,
					(TUint32)aReq.iClientProcess.Handle());
		}
	E32Loader::CodeSegDeferDeletes();
	gExeCodeSeg=E32Loader::ThreadProcessCodeSeg(aReq.iClientThread.Handle());
	SSecurityInfo si;
	gExeAttr=GetCodeSegAttr(gExeCodeSeg, &si, NULL);
	aReq.iPlatSecCaps=si.iCaps;
	E32Loader::CodeSegEndDeferDeletes();
	HtcleoLoaderLog(0x00001104u, KErrNone, *aReq.iFileName, gExeAttr);
	E32Image* e=new E32Image;
	HtcleoLoaderLog(0x00001105u, e ? KErrNone : KErrNoMemory,
					*aReq.iFileName, e ? 1u : 0u);
	if (!e)
		return KErrNoMemory;
	e->iMain=e;
	e->iClientProcessHandle=aReq.iClientProcess.Handle();
	__IF_DEBUG(Printf("e->iClientProcessHandle = %08x", e->iClientProcessHandle));
	if (r==KErrNone)
		{
		HtcleoLoaderLog(0x00001106u, r, *aReq.iFileName,
					(TUint32)e->iClientProcessHandle);
		r=e->LoadCodeSeg(aReq);
		HtcleoLoaderLog(0x00001107u, r, *aReq.iFileName,
					(TUint32)e->iHandle);
		}
	if (r==KErrNone)
		{
		TLibraryCreateInfo libInfo;
		libInfo.iCodeSegHandle=e->iHandle;
		libInfo.iClientHandle=aReq.iClientThread.Handle();
		libInfo.iLibraryHandle=0;
		libInfo.iOwnerType=aReq.iOwnerType;
		HtcleoLoaderLog(0x00001108u, r, *aReq.iFileName,
					(TUint32)e->iHandle);
		r=E32Loader::LibraryCreate(libInfo);
		HtcleoLoaderLog(0x00001109u, r, *aReq.iFileName,
					(TUint32)libInfo.iLibraryHandle);
		if (r==KErrNone)
			{
			aReq.iHandle=libInfo.iLibraryHandle;
			if (aReq.iMsg)
				{
				r=aReq.iMsg->UpdateLdrInfo(aReq);
				HtcleoLoaderLog(0x0000110au, r, *aReq.iFileName,
							(TUint32)aReq.iHandle);
				if (r!=KErrNone)
					aReq.Panic(KErrBadDescriptor);
				}
			}
		}
	delete e;
	HtcleoLoaderLog(0x0000110bu, r, *aReq.iFileName,
					(TUint32)aReq.iHandle);
	return r;
	}
'''


LOAD_CODESEG_FUNCTION = r'''TInt E32Image::LoadCodeSeg(const RLdrReq& aReq)
	{
	__LDRTRACE(aReq.Dump(">E32Image::LoadCodeSeg"));
	HtcleoLoaderLog(0x00002001u, KErrNone, *aReq.iFileName,
					(TUint32)aReq.iRequestedUids[2].iUid);

#ifdef __X86__
	if (iMain==this && iClientProcessHandle)
		{
		RProcess p;
		p.SetHandle(iClientProcessHandle);
		TFileName f(p.FileName());
		if (f.Length()>=2 && f[1]==':')
			{
			TInt d = f[0];
			if (d=='a' || d=='A')
				UseFloppy = EDriveA;
			else if (d=='b' || d=='B')
				UseFloppy = EDriveB;
			}
		}
#endif

	RImageFinder finder;
	TInt r = finder.Set(aReq);
	HtcleoLoaderLog(0x00002002u, r, *aReq.iFileName, 0u);
	if (r == KErrNone)
		{
		HtcleoLoaderLog(0x00002003u, r, *aReq.iFileName, 0u);
		r = finder.Search();
		HtcleoLoaderLog(0x00002004u, r, *aReq.iFileName,
					(finder.iExisting ? 1u : 0u) | (finder.iNewValid ? 2u : 0u));
		}
	if (r!=KErrNone)
		{
		finder.Close();
		return r;
		}
	HtcleoLoaderLog(0x00002005u, r, *aReq.iFileName, 0u);
	r = DoLoadCodeSeg(aReq, finder);
	HtcleoLoaderLog(0x00002006u, r, *aReq.iFileName, (TUint32)iHandle);
	return r;
	}
'''


DO_LOAD_CODESEG_FUNCTION = r'''TInt E32Image::DoLoadCodeSeg(const RLdrReq& aReq, RImageFinder& aFinder)
	{
	__LDRTRACE(aReq.Dump(">E32Image::DoLoadCodeSeg"));
	HtcleoLoaderLog(0x00002101u, KErrNone, *aReq.iFileName, 0u);

	TInt r = Construct(aFinder);	// needs to find it if it's already loaded
	aFinder.Close();
	HtcleoLoaderLog(0x00002102u, r, iFileName, (TUint32)iUids[2].iUid);
	if (r!=KErrNone)
		return r;
	__IF_DEBUG(Printf("epv=%x, fep=%x, codesize=%x, textsize=%x, uid3=%x",iEntryPtVeneer,iFileEntryPoint,iCodeSize,iTextSize,iUids[2]));
	__IF_DEBUG(Printf("attr=%08x, gExeAttr=%08x",iAttr,gExeAttr));

	if (gExeCodeSeg && !iIsDll && iMain!=this && iHandle!=gExeCodeSeg)
		{
		HtcleoLoaderLog(0x000021e1u, KErrNotSupported, iFileName, iAttr);
		return KErrNotSupported;
		}
	if (iIsDll && iMain==this && (iAttr & ECodeSegAttABIMask)!=(gExeAttr & ECodeSegAttABIMask) )
		{
		HtcleoLoaderLog(0x000021e2u, KErrNotSupported, iFileName, iAttr);
		return KErrNotSupported;
		}
	if (iAlreadyLoaded || (iMain!=this && AlwaysLoaded()) )
		{
		HtcleoLoaderLog(0x000021e3u, KErrNone, iFileName,
					(iAlreadyLoaded ? 1u : 0u) | (AlwaysLoaded() ? 2u : 0u));
		return KErrNone;
		}

	__IF_DEBUG(Printf("CodeSeg create"));
	HtcleoLoaderLog(0x00002104u, KErrNone, iFileName, iAttr);
	r=E32Loader::CodeSegCreate(*this);
	HtcleoLoaderLog(0x00002105u, r, iFileName, (TUint32)iHandle);
	if (r!=KErrNone)
		return r;

	iCloseCodeSeg=iHandle;
	if (!iRomImageHeader)
		{
		HtcleoLoaderLog(0x00002106u, r, iFileName, iRestOfFileSize);
		r=LoadToRam();
		HtcleoLoaderLog(0x00002107u, r, iFileName, iRestOfFileSize);
		}
	if (r==KErrNone)
		{
		iCloseCodeSeg=NULL;
		if (iMain==this)
			{
			HtcleoLoaderLog(0x00002108u, r, iFileName, (TUint32)iDepCount);
			r=ProcessImports();
			HtcleoLoaderLog(0x00002109u, r, iFileName, (TUint32)iDepCount);
			if (r==KErrNone)
				{
				r=E32Loader::CodeSegLoaded(*this);
				HtcleoLoaderLog(0x0000210au, r, iFileName, (TUint32)iHandle);
				if ((r==KErrNone) && iUseCodePaging)
					{
					iFileClamp.iCookie[0]=0;
					iFileClamp.iCookie[1]=0;
					}
				}
			}
		}

	__IF_DEBUG(Printf("<DoLoadCodeSeg, r=%d, iIsDll=%d",r,iIsDll));
	HtcleoLoaderLog(0x0000210bu, r, iFileName, (TUint32)iHandle);
	return r;
	}
'''


ROM_LOAD_CODESEG_FUNCTION = r'''TInt E32Image::DoLoadCodeSeg(const TRomImageHeader& a)
	{
	__IF_DEBUG(Printf("E32Image::DoLoadCodeSeg ROM XIP @%08x",&a));
	HtcleoLoaderLog(0x00002401u, KErrNone, iMain->iFileName,
					(TUint32)a.iUid3);
	Construct(a);
	if (AlwaysLoaded())
		{
		GetRomFileName();
		HtcleoLoaderLog(0x00002402u, KErrNone, iFileName, 1u);
		return KErrNone;
		}
	TInt r=CheckRomXIPAlreadyLoaded();
	HtcleoLoaderLog(0x00002403u, r, iFileName,
					(iAlreadyLoaded ? 1u : 0u));
	if (r!=KErrNone || iAlreadyLoaded)
		return r;
	GetRomFileName();
	HtcleoLoaderLog(0x00002404u, r, iFileName, iAttr);
	r=E32Loader::CodeSegCreate(*this);
	HtcleoLoaderLog(0x00002405u, r, iFileName, (TUint32)iHandle);

	__IF_DEBUG(Printf("<DoLoadCodeSeg, r=%d",r));
	return r;
	}
'''


LOAD_TO_RAM_FUNCTION = r'''TInt E32Image::LoadToRam()
	{
	__IF_DEBUG(Printf("E32Image::LoadToRam %S",&iFileName));
	HtcleoLoaderLog(0x00002201u, KErrNone, iFileName, 0u);
	iConversionOffset = iHeader->iCodeOffset + iHeader->iCodeSize;
	TUint totalSize = ((E32ImageHeaderV*)iHeader)->iUncompressedSize;
	TUint remainder = totalSize-iConversionOffset;
	if(remainder>totalSize)
		RETURN_FAILURE(KErrCorrupt);

	iRestOfFileData = (TUint8*)User::Alloc(remainder);
	HtcleoLoaderLog(0x00002202u, iRestOfFileData ? KErrNone : KErrNoMemory,
					iFileName, remainder);
	if(!iRestOfFileData)
		return KErrNoMemory;
	iRestOfFileSize = remainder;

	TInt r = LoadFile();
	HtcleoLoaderLog(0x00002203u, r, iFileName, remainder);
	if(r!=KErrNone)
		return r;

	r = ((E32ImageHeaderV*)iHeader)->ValidateRelocations(iRestOfFileData,iRestOfFileSize,iHeader->iCodeRelocOffset,iHeader->iCodeSize,iCodeRelocSection);
	HtcleoLoaderLog(0x00002204u, r, iFileName, iHeader->iCodeRelocOffset);
	if(r!=KErrNone)
		return r;
	r = ((E32ImageHeaderV*)iHeader)->ValidateRelocations(iRestOfFileData,iRestOfFileSize,iHeader->iDataRelocOffset,iHeader->iDataSize,iDataRelocSection);
	HtcleoLoaderLog(0x00002205u, r, iFileName, iHeader->iDataRelocOffset);
	if(r!=KErrNone)
		return r;

	iCodeDelta = iCodeRunAddress-iHeader->iCodeBase;
	iDataDelta = iDataRunAddress-iHeader->iDataBase;
	if(r==KErrNone)
		{
		r = RelocateCode();
		HtcleoLoaderLog(0x00002206u, r, iFileName, iCodeDelta);
		}
	if(r==KErrNone)
		{
		r = LoadAndRelocateData();
		HtcleoLoaderLog(0x00002207u, r, iFileName, iDataDelta);
		}
	if(r==KErrNone)
		{
		r = ReadImportData();
		HtcleoLoaderLog(0x00002208u, r, iFileName, (TUint32)iDepCount);
		}
	HtcleoLoaderLog(0x00002209u, r, iFileName, iRestOfFileSize);
	return r;
	}
'''


LOAD_FILE_FUNCTION = r'''TInt E32Image::LoadFile()
	{
	__IF_DEBUG(Printf("E32Image::LoadFile %S 0x%08x",&iFileName,iHeader->CompressionType()));
	TUint compression = iHeader->CompressionType();
	HtcleoLoaderLog(0x00002301u, KErrNone, iFileName, compression);

	TInt r=KErrNone;
	if(compression==KFormatNotCompressed)
		{
		r = LoadFileNoCompress();
		CHECK_FAILURE(r);
		}
	else if(compression==KUidCompressionDeflate)
		{
		TRAP(r,LoadFileInflateL());
		CHECK_FAILURE(r);
		}
	else if(compression==KUidCompressionBytePair)
		{
		TRAP(r,LoadFileBytePairUnpakL());
		CHECK_FAILURE(r);
		}
	else
		{
		r = KErrNotSupported;
		CHECK_FAILURE(r);
		}
	HtcleoLoaderLog(0x00002302u, r, iFileName, compression);

	if(iFileData)
		{
		gFileDataAllocator.Free(iFileData);
		iFileData=NULL;
		}
	HtcleoLoaderLog(0x00002303u, r, iFileName, iFileSize);
	__IF_DEBUG(Printf("E32Image::LoadFile exiting %S r=%d",&iFileName,r));
	return r;
	}
'''


PROCESS_IMPORTS_FUNCTION = r'''TInt E32Image::ProcessImports()
//
// This function is only ever called on the exe/dll loaded from RProcess/RLibrary.
//
	{
	__IF_DEBUG(Printf("E32Image::ProcessImports %S",&iFileName));
	__IF_DEBUG(Printf("DepCount=%d",iDepCount));
	HtcleoLoaderLog(0x00003001u, KErrNone, iFileName, (TUint32)iDepCount);
	if (iDepCount==0 || AlwaysLoaded())
		{
		HtcleoLoaderLog(0x00003002u, KErrNone, iFileName,
					(AlwaysLoaded() ? 1u : 0u));
		return KErrNone;
		}

	TFileNameInfo fi;
	fi.Set(iFileName, 0);
	gLoadeePath.Zero();
	fi.GetName(gLoadeePath, TFileNameInfo::EIncludeDrivePath);
	if (PlatSec::ConfigSetting(PlatSec::EPlatSecEnforceSysBin)
			&& gLoadeePath.Length()==11
			&& KSysBin().CompareF(TPtrC8(gLoadeePath.Ptr()+1,10))==0)
		gLoadeePath.Zero();
#ifdef __X86__
	if (gLoadeePath.Length()>=2 && gLoadeePath[1]==':')
		{
		TInt d = gLoadeePath[0];
		if (d=='a' || d=='A') UseFloppy = EDriveA;
		else if (d=='b' || d=='B') UseFloppy = EDriveB;
		}
#endif
	RImageArray array;
	TInt r = array.Add(this);
	HtcleoLoaderLog(0x00003003u, r, iFileName, (TUint32)array.Count());
	if (r==KErrNone)
		{
		r = LoadDlls(array);
		HtcleoLoaderLog(0x00003004u, r, iFileName, (TUint32)array.Count());
		}
	if (r==KErrNone)
		{
		r = FixupDlls(array);
		HtcleoLoaderLog(0x00003005u, r, iFileName, (TUint32)array.Count());
		}
	if (r==KErrNone)
		{
		r = FinaliseDlls(array);
		HtcleoLoaderLog(0x00003006u, r, iFileName, (TUint32)array.Count());
		}
	CleanupDlls(array);
	array.Close();
	HtcleoLoaderLog(0x00003007u, r, iFileName, 0u);
	__IF_DEBUG(Printf("E32Image::ProcessImports returns %d",r));
	return r;
	}
'''


def verify(root: Path) -> None:
    sfile = root / "userlibandfileserver/fileserver/sfile"
    ldr = (sfile / "sf_ldr.cpp").read_text(encoding="utf-8")
    lepoc = (sfile / "sf_lepoc.cpp").read_text(encoding="utf-8")
    logger = (sfile / "HtcleoLoaderLog.cpp").read_text(encoding="utf-8")
    header = (sfile / "HtcleoLoaderLog.h").read_text(encoding="utf-8")
    mmp = (sfile / "efile.mmp").read_text(encoding="utf-8")
    combined = ldr + lepoc
    required = (
        "00001001", "00001006", "00001101", "0000110b",
        "00002001", "00002006", "00002101", "0000210b",
        "00002201", "00002209", "00002301", "00002303",
        "00002401", "00002405", "00003001", "00003007",
        "00004001", "0000400f", "00004011", "00004027",
        "00005001", "00005006", "00005101", "00005102",
        "00005201", "00005202",
    )
    checks = {
        "marker": logger.count(MARKER) == 1,
        "macro": mmp.count(f"MACRO\t\t\t{MACRO}") == 1,
        "logger source": mmp.count("SOURCE\t\t\t HtcleoLoaderLog.cpp") == 1,
        "includes": ldr.count('#include "HtcleoLoaderLog.h"') == 1
        and lepoc.count('#include "HtcleoLoaderLog.h"') == 1,
        "path": logger.count("C:\\\\Symbian3\\\\LDRLOG.TXT") == 1,
        "prefix": logger.count("HTCLEO_LDR ") == 1,
        "fixed record": "Every record is exactly 53 bytes" in logger,
        "existing fs": "gTheLoaderFs" in logger and "RFs fs" not in logger,
        "write flush": "file.Write(record)" in logger and "file.Flush()" in logger,
        "target gate": logger.count("nvgrenderstage.dll") == 1,
        "stages": all(combined.count(f"0x{stage}u") == 1 for stage in required),
        "descriptor-safe existing image log":
        "e ? e->iFileName : rootname" not in lepoc and "\n+\n" not in lepoc,
        "no delays": "User::After" not in logger,
        "header": "HTCLEO_LOADER_DURABLE_LOG_H" in header,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("loader durable-log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="kernelhwsrv source root")
    args = parser.parse_args()
    sfile = args.root / "userlibandfileserver/fileserver/sfile"
    ldr_path = sfile / "sf_ldr.cpp"
    lepoc_path = sfile / "sf_lepoc.cpp"
    mmp_path = sfile / "efile.mmp"
    header_path = sfile / "HtcleoLoaderLog.h"
    logger_path = sfile / "HtcleoLoaderLog.cpp"
    for path in (ldr_path, lepoc_path, mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing native EFILE source: {path}")

    if logger_path.is_file() and MARKER in logger_path.read_text(encoding="utf-8"):
        # V1 was briefly installed with a GCCE-incompatible conditional whose
        # two descriptor operands have different concrete TBuf8 types, plus a
        # stray patch marker.  Migrate that exact installed form in place so a
        # failed first build does not require restoring the whole source tree.
        lepoc = lepoc_path.read_text(encoding="utf-8")
        bad_existing_log = '''\t\tHtcleoLoaderLog(0x00004019u, r, e ? e->iFileName : rootname,\n\t\t\t\t\te ? 1u : 0u);\n+\n'''
        good_existing_log = '''\t\tif (e)\n\t\t\tHtcleoLoaderLog(0x00004019u, r, e->iFileName, 1u);\n\t\telse\n\t\t\tHtcleoLoaderLog(0x00004019u, r, rootname, 0u);\n\n'''
        if bad_existing_log in lepoc:
            if lepoc.count(bad_existing_log) != 1:
                raise SystemExit("installed descriptor migration anchor is ambiguous")
            lepoc_path.write_text(lepoc.replace(bad_existing_log,
                                                 good_existing_log, 1),
                                  encoding="utf-8", newline="\n")
        verify(args.root)
        print("HTCLEO_LOADER_DURABLE_LOG=installed records=1024 path=C:\\Symbian3\\LDRLOG.TXT")
        return

    ldr = ldr_path.read_text(encoding="utf-8")
    lepoc = lepoc_path.read_text(encoding="utf-8")
    mmp = mmp_path.read_text(encoding="utf-8")

    ldr = replace_once(ldr, '#include "sf_image.h"\n',
                       '#include "sf_image.h"\n#include "HtcleoLoaderLog.h"\n',
                       "sf_ldr logger include")
    lepoc = replace_once(lepoc, '#include "sf_image.h"\n',
                         '#include "sf_image.h"\n#include "HtcleoLoaderLog.h"\n',
                         "sf_lepoc logger include")

    old_case = '''\t\tcase ELoadLibrary:\n\t\t\t{\n\t\t\tr=E32Loader::CheckClientState(msg.Handle());\n\t\t\tif (r!=KErrNone)\n\t\t\t\tldrReq.Panic(ELoadLibraryWithoutDllLock);\n\t\t\telse\n\t\t\t\tr=ldrReq.AddFileExtension(KFileExtensionDll);\n\t\t\tif (r==KErrNone)\n\t\t\t\tr=msg.GetString(ldrReq.iPath, 2, KMaxPath, 0, ETrue);\n\t\t\tif (ldrReq.iPath)\n\t\t\t\t{\n\t\t\t\t__IF_DEBUG(Printf("Path: %S", ldrReq.iPath));\n\t\t\t\t}\n\t\t\tif (r==KErrNone)\n\t\t\t\tr = ldrReq.CheckForSubstDrivesInPath();\n\t\t\tif (ldrReq.iPath)\n\t\t\t\t{\n\t\t\t\t__IF_DEBUG(Printf("Post-subst Path: %S", ldrReq.iPath));\n\t\t\t\t}\n\t\t\tif (r==KErrNone)\n\t\t\t\tr=msg.GetLdrInfo(ldrReq);\n\t\t\tif (r==KErrNone)\n\t\t\t\tr=LoadLibrary(ldrReq);\n\t\t\tbreak;\n\t\t\t}\n'''
    ldr = replace_once(ldr, old_case, LOAD_LIBRARY_CASE, "ELoadLibrary dispatch")

    old_load_start = ldr.index("TInt LoadLibrary(RLdrReq& aReq)\n")
    old_load_end = ldr.index("\n\t\nstruct TFatUtilityFunctions;", old_load_start)
    ldr = ldr[:old_load_start] + LOAD_LIBRARY_FUNCTION + ldr[old_load_end:]

    def replace_function(source: str, signature: str, next_anchor: str,
                         replacement: str, label: str) -> str:
        if source.count(signature) != 1:
            raise SystemExit(f"{label}: expected one signature")
        start = source.index(signature)
        end = source.index(next_anchor, start + len(signature))
        return source[:start] + replacement + "\n\n" + source[end:]

    lepoc = replace_function(lepoc, "TInt E32Image::LoadCodeSeg(const RLdrReq& aReq)\n",
                             "// Load a code segment, plus all imports if main loadee\nTInt E32Image::DoLoadCodeSeg",
                             LOAD_CODESEG_FUNCTION, "LoadCodeSeg")
    lepoc = replace_function(lepoc, "TInt E32Image::DoLoadCodeSeg(const RLdrReq& aReq, RImageFinder& aFinder)\n",
                             "// Load a ROM XIP code segment as part of another load\n",
                             DO_LOAD_CODESEG_FUNCTION, "DoLoadCodeSeg request")
    lepoc = replace_function(lepoc, "TInt E32Image::DoLoadCodeSeg(const TRomImageHeader& a)\n",
                             "/******************************************************************************\n * EPOC specific E32Image functions",
                             ROM_LOAD_CODESEG_FUNCTION, "DoLoadCodeSeg ROM")
    lepoc = replace_function(lepoc, "TInt E32Image::LoadToRam()\n",
                             "TInt E32Image::ShouldBeCodePaged",
                             LOAD_TO_RAM_FUNCTION, "LoadToRam")
    lepoc = replace_function(lepoc, "TInt E32Image::LoadFile()\n",
                             "/**\nRead data from the image's file",
                             LOAD_FILE_FUNCTION, "LoadFile")
    lepoc = replace_function(lepoc, "TInt E32Image::ProcessImports()\n",
                             "void E32Image::CleanupDlls",
                             PROCESS_IMPORTS_FUNCTION, "ProcessImports")

    # RImageFinder: bracket the overall search and the one Z: directory pass.
    lepoc = replace_once(lepoc,
        '''TInt RImageFinder::Search()\n\t{\n\t__LDRTRACE(iReq->Dump(\">RImageFinder::Search\"));\n''',
        '''TInt RImageFinder::Search()\n\t{\n\t__LDRTRACE(iReq->Dump(\">RImageFinder::Search\"));\n\tHtcleoLoaderLog(0x00005001u, KErrNone, *iReq->iFileName,\n\t\t\t\t\t(TUint32)iReq->iRequestedUids[2].iUid);\n''', "finder Search entry")
    lepoc = replace_once(lepoc,
        '''\t\tTPtrC8 drive_and_path(fi.DriveAndPath());\n\t\tr = Search(&drive_and_path, 0);\n''',
        '''\t\tTPtrC8 drive_and_path(fi.DriveAndPath());\n\t\tHtcleoLoaderLog(0x00005002u, r, *iReq->iFileName,\n\t\t\t\t\t(TUint32)drive_and_path.Length());\n\t\tr = Search(&drive_and_path, 0);\n\t\tHtcleoLoaderLog(0x00005003u, r, *iReq->iFileName,\n\t\t\t\t\t(TUint32)drive_and_path.Length());\n''', "finder explicit path")
    lepoc = replace_once(lepoc,
        '''\t\tr = Search(defpath, drv);\n\t\t}\n''',
        '''\t\tHtcleoLoaderLog(0x00005004u, r, *iReq->iFileName,\n\t\t\t\t\t(TUint32)defpath->Length());\n\t\tr = Search(defpath, drv);\n\t\tHtcleoLoaderLog(0x00005005u, r, *iReq->iFileName,\n\t\t\t\t\t(TUint32)defpath->Length());\n\t\t}\n''', "finder default path")
    lepoc = replace_once(lepoc,
        '''\t__LDRTRACE(Dump(\"<RImageFinder::Search\", r));\n\treturn r;\n\t}\n\nTInt RImageFinder::Search(const TDesC8* aPath, TInt aDrive)\n''',
        '''\t__LDRTRACE(Dump(\"<RImageFinder::Search\", r));\n\tHtcleoLoaderLog(0x00005006u, r, *iReq->iFileName,\n\t\t\t\t\t(iExisting ? 1u : 0u) | (iNewValid ? 2u : 0u));\n\treturn r;\n\t}\n\nTInt RImageFinder::Search(const TDesC8* aPath, TInt aDrive)\n''', "finder Search return")
    lepoc = replace_once(lepoc,
        '''\t\tr = SearchSingleDir();\n\t\t\tif (r == KErrNoMemory)''',
        '''\t\tif(iCurrentDrive == EDriveZ)\n\t\t\tHtcleoLoaderLog(0x00005101u, KErrNone, *iReq->iFileName,\n\t\t\t\t\t\t(TUint32)iCurrentDrive);\n\t\tr = SearchSingleDir();\n\t\tif(iCurrentDrive == EDriveZ)\n\t\t\tHtcleoLoaderLog(0x00005102u, r, *iReq->iFileName,\n\t\t\t\t\t\t(TUint32)iCurrentDrive);\n\t\t\tif (r == KErrNoMemory)''', "finder Z directory")
    lepoc = replace_once(lepoc,
        '''TInt RImageFinder::Try(RImageInfo& aInfo, const TDesC8& aRootName, const TDesC8& aDriveAndPath)\n\t{\n\t__IF_DEBUG(Printf(\">RImageFinder::Try %S%S\", &aDriveAndPath, &aRootName));\n''',
        '''TInt RImageFinder::Try(RImageInfo& aInfo, const TDesC8& aRootName, const TDesC8& aDriveAndPath)\n\t{\n\t__IF_DEBUG(Printf(\">RImageFinder::Try %S%S\", &aDriveAndPath, &aRootName));\n\tHtcleoLoaderLog(0x00005201u, KErrNone, aRootName,\n\t\t\t\t\t(TUint32)aInfo.iUid[2]);\n''', "finder Try entry")
    lepoc = replace_once(lepoc,
        '''\t__IF_DEBUG(Printf(\"<RImageFinder::Try OK\"));\n\treturn KErrNone;\n\t}\n''',
        '''\t__IF_DEBUG(Printf(\"<RImageFinder::Try OK\"));\n\tHtcleoLoaderLog(0x00005202u, KErrNone, aRootName,\n\t\t\t\t\t(TUint32)aInfo.iUid[2]);\n\treturn KErrNone;\n\t}\n''', "finder Try success")

    # Recursive import walk.  Repeated runtime records carry the current
    # importer/dependency tag; stage IDs identify the exact call boundary.
    lepoc = replace_once(lepoc,
        '''\t__IF_DEBUG(Printf(\"E32Image::LoadDlls\"));\n\tTInt r=KErrNone;\n''',
        '''\t__IF_DEBUG(Printf(\"E32Image::LoadDlls\"));\n\tHtcleoLoaderLog(0x00004001u, KErrNone, iFileName, (TUint32)iDepCount);\n\tTInt r=KErrNone;\n''', "LoadDlls entry")
    lepoc = replace_once(lepoc,
        '''\t\tTBuf8<KMaxKernelName> rootname;\n\t\treq.iFileName = (HBufC8*)&rootname;\n''',
        '''\t\tTBuf8<KMaxKernelName> rootname;\n\t\treq.iFileName = (HBufC8*)&rootname;\n\t\tHtcleoLoaderLog(0x00004010u, KErrNone, iFileName,\n\t\t\t\t\t((TUint32)i << 16) | (TUint32)iDepCount);\n''', "LoadDlls dependency entry")
    lepoc = replace_once(lepoc,
        '''\t\t\tfni.GetName(rootname, TFileNameInfo::EIncludeBaseExt);\n\t\t\tTUint32* uid=(TUint32*)&req.iRequestedUids;\n\t\t\tuid[2] = fni.Uid();\n''',
        '''\t\t\tfni.GetName(rootname, TFileNameInfo::EIncludeBaseExt);\n\t\t\tTUint32* uid=(TUint32*)&req.iRequestedUids;\n\t\t\tuid[2] = fni.Uid();\n\t\t\tHtcleoLoaderLog(0x00004011u, r, rootname, uid[2]);\n''', "LoadDlls parsed dependency")
    lepoc = replace_once(lepoc,
        '''\t\t\tr = GetCurrentImportList(block);\t// get list of required exports from this exporter\n\t\t\tif (r!=KErrNone)\n''',
        '''\t\t\tr = GetCurrentImportList(block);\t// get list of required exports from this exporter\n\t\t\tHtcleoLoaderLog(0x00004012u, r, rootname,\n\t\t\t\t\t(TUint32)iCurrentImportCount);\n\t\t\tif (r!=KErrNone)\n''', "LoadDlls import list")
    lepoc = replace_once(lepoc,
        '''\t\t\tr = finder.Set(req);\n\t\t\tif (r == KErrNone)\n\t\t\t\tr = finder.SearchExisting(aArray);\t// see what we've already got\n''',
        '''\t\t\tHtcleoLoaderLog(0x00004013u, r, rootname, 0u);\n\t\t\tr = finder.Set(req);\n\t\t\tHtcleoLoaderLog(0x00004014u, r, rootname, 0u);\n\t\t\tif (r == KErrNone)\n\t\t\t\t{\n\t\t\t\tHtcleoLoaderLog(0x00004015u, r, rootname,\n\t\t\t\t\t\t(TUint32)aArray.Count());\n\t\t\t\tr = finder.SearchExisting(aArray);\n\t\t\t\tHtcleoLoaderLog(0x00004016u, r, rootname,\n\t\t\t\t\t\tfinder.iExisting ? 1u : 0u);\n\t\t\t\t}\n''', "LoadDlls finder setup")
    lepoc = replace_once(lepoc,
        '''\t\t\t\tif (search)\n\t\t\t\t\tr = finder.Search();\t\t// see what else is available\n''',
        '''\t\t\t\tif (search)\n\t\t\t\t\t{\n\t\t\t\t\tHtcleoLoaderLog(0x00004017u, r, rootname, 0u);\n\t\t\t\t\tr = finder.Search();\n\t\t\t\t\tHtcleoLoaderLog(0x00004018u, r, rootname,\n\t\t\t\t\t\t\t(finder.iExisting ? 1u : 0u) |\n\t\t\t\t\t\t\t(finder.iNewValid ? 2u : 0u));\n\t\t\t\t\t}\n''', "LoadDlls finder search")
    lepoc = replace_once(lepoc,
        '''\t\t// If it's already in the array, go on to the next module\n\t\tif (e)\n''',
        '''\t\tif (e)\n\t\t\tHtcleoLoaderLog(0x00004019u, r, e->iFileName, 1u);\n\t\telse\n\t\t\tHtcleoLoaderLog(0x00004019u, r, rootname, 0u);\n\n\t\t// If it's already in the array, go on to the next module\n\t\tif (e)\n''', "LoadDlls existing result")
    lepoc = replace_once(lepoc,
        '''\t\t\te = new E32Image;\n\t\t\tif (!e)\n''',
        '''\t\t\te = new E32Image;\n\t\t\tHtcleoLoaderLog(0x00004020u, e ? KErrNone : KErrNoMemory,\n\t\t\t\t\trootname, e ? 1u : 0u);\n\t\t\tif (!e)\n''', "LoadDlls allocation")
    lepoc = replace_once(lepoc,
        '''\t\t\tif (rih)\n\t\t\t\t{\n\t\t\t\t// loading a specified ROM XIP DLL\n\t\t\t\tr = e->DoLoadCodeSeg(*rih);\n\t\t\t\t}\n\t\t\telse\n\t\t\t\t{\n\t\t\t\t// loading a DLL by name\n\t\t\t\tr = e->DoLoadCodeSeg(req, finder); // also closes 'finder'\n\t\t\t\t__IF_DEBUG(Printf(\"%S DoLoadCodeSeg returned %d\",req.iFileName,r));\n\t\t\t\t}\n''',
        '''\t\t\tHtcleoLoaderLog(0x00004021u, r, rootname,\n\t\t\t\t\t(rih ? 0x80000000u : 0u) | (TUint32)i);\n\t\t\tif (rih)\n\t\t\t\t{\n\t\t\t\tr = e->DoLoadCodeSeg(*rih);\n\t\t\t\t}\n\t\t\telse\n\t\t\t\t{\n\t\t\t\tr = e->DoLoadCodeSeg(req, finder);\n\t\t\t\t__IF_DEBUG(Printf(\"%S DoLoadCodeSeg returned %d\",req.iFileName,r));\n\t\t\t\t}\n\t\t\tHtcleoLoaderLog(0x00004022u, r, e->iFileName,\n\t\t\t\t\t(TUint32)e->iHandle);\n''', "LoadDlls child load")
    lepoc = replace_once(lepoc,
        '''\t\t\t\tr = aArray.Add(e);\n\t\t\t\t}\n\t\t\tif (r!=KErrNone)\n''',
        '''\t\t\t\tr = aArray.Add(e);\n\t\t\t\tHtcleoLoaderLog(0x00004023u, r, e->iFileName,\n\t\t\t\t\t\t(TUint32)aArray.Count());\n\t\t\t\t}\n\t\t\tif (r!=KErrNone)\n''', "LoadDlls array add")
    lepoc = replace_once(lepoc,
        '''\t\t\t\t__IF_DEBUG(Printf(\"****Going recursive****\"));\n\t\t\t\tr = e->LoadDlls(aArray);\n\t\t\t\t__IF_DEBUG(Printf(\"****Returned from recursion****\"));\n''',
        '''\t\t\t\t__IF_DEBUG(Printf(\"****Going recursive****\"));\n\t\t\t\tHtcleoLoaderLog(0x00004024u, r, e->iFileName,\n\t\t\t\t\t\t(TUint32)e->iDepCount);\n\t\t\t\tr = e->LoadDlls(aArray);\n\t\t\t\tHtcleoLoaderLog(0x00004025u, r, e->iFileName,\n\t\t\t\t\t\t(TUint32)aArray.Count());\n\t\t\t\t__IF_DEBUG(Printf(\"****Returned from recursion****\"));\n''', "LoadDlls recursion")
    lepoc = replace_once(lepoc,
        '''\t\tif (e->iHandle)\n\t\t\t{\n\t\t\t//\tRecord the dependence of this on e\n\t\t\tr=E32Loader::CodeSegAddDependency(iHandle, e->iHandle);\n\t\t\tif (r!=KErrNone)\n''',
        '''\t\tif (e->iHandle)\n\t\t\t{\n\t\t\tHtcleoLoaderLog(0x00004026u, r, e->iFileName,\n\t\t\t\t\t(TUint32)e->iHandle);\n\t\t\tr=E32Loader::CodeSegAddDependency(iHandle, e->iHandle);\n\t\t\tHtcleoLoaderLog(0x00004027u, r, e->iFileName,\n\t\t\t\t\t(TUint32)e->iHandle);\n\t\t\tif (r!=KErrNone)\n''', "LoadDlls add dependency")
    lepoc = replace_once(lepoc,
        '''\t__IF_DEBUG(Printf(\"E32Image::LoadDlls OK\"));\n\treturn KErrNone;\n\t}\n''',
        '''\t__IF_DEBUG(Printf(\"E32Image::LoadDlls OK\"));\n\tHtcleoLoaderLog(0x0000400fu, KErrNone, iFileName,\n\t\t\t\t\t(TUint32)aArray.Count());\n\treturn KErrNone;\n\t}\n''', "LoadDlls return")

    mmp = replace_once(mmp,
        "MACRO\t\t\t__HTCLEO_LOW_ROM_PD_FIX_PROBE__\n",
        "MACRO\t\t\t__HTCLEO_LOW_ROM_PD_FIX_PROBE__\n"
        f"MACRO\t\t\t{MACRO}\n",
        "efile logger macro")
    mmp = replace_once(mmp, '#include "efile.mmh"\n',
                       '#include "efile.mmh"\nSOURCE\t\t\t HtcleoLoaderLog.cpp\n',
                       "efile logger source")

    header_path.write_text(HEADER, encoding="utf-8", newline="\n")
    logger_path.write_text(LOGGER, encoding="utf-8", newline="\n")
    ldr_path.write_text(ldr, encoding="utf-8", newline="\n")
    lepoc_path.write_text(lepoc, encoding="utf-8", newline="\n")
    mmp_path.write_text(mmp, encoding="utf-8", newline="\n")
    verify(args.root)
    print("HTCLEO_LOADER_DURABLE_LOG=installed records=1024 path=C:\\Symbian3\\LDRLOG.TXT")


if __name__ == "__main__":
    main()
