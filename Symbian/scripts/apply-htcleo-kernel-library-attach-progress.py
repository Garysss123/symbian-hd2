#!/usr/bin/env python3
"""Add an opt-in, non-display LibraryAttach durable handoff and bootstrap.

The normal EExecLibraryAttach ABI and every stock caller remain unchanged.
Only the HTCLEO ECom NVG diagnostic caller passes the exact trace flag and
reserves a progress word plus two semaphore handles after its 256-entry
buffer.  Six read-only bootstrap calls isolate SVC dispatch, metadata reads,
handle resolution and the first notify/ack exchange before the real attach.
At each of ten attach boundaries the kernel writes the progress word, wakes the
already-blocked watcher, and waits until that watcher has flushed the exact
record to ECOMLOG.TXT.  Stock callers never enter either diagnostic path.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_KERNEL_LIBRARY_ATTACH_PROGRESS_V3"
START = "// Accept a DLibrary just after a load and extract a list of entry points\n"
END = "// Signal that entry points have been completed and release DLL lock\n"


REPLACEMENT = r'''// Accept a DLibrary just after a load and extract a list of entry points
// HTCLEO_KERNEL_LIBRARY_ATTACH_PROGRESS_V3
// This is deliberately an exact opt-in ABI extension.  Stock callers pass a
// plain positive entry-count and never touch this path.  The HTCLEO ECom NVG
// diagnostic caller passes 0x40000100 and reserves entries 256..258 for the
// progress word plus process-owned notify/ack semaphore handles.  A second
// 0x42pp0100 namespace performs six side-effect-free bootstrap queries before
// the real attach.  Each handoff blocks only that diagnostic caller until the
// low-priority watcher has durably flushed the corresponding ECOMLOG record.
struct THtcleoLibraryAttachTrace
	{
	TLinAddr* iProgress;
	DSemaphore* iNotify;
	DSemaphore* iAck;
	};

static TInt HtcleoLibraryAttachExchange(THtcleoLibraryAttachTrace* aTrace,
		TUint32 aValue) __attribute__((noinline));

static TInt HtcleoLibraryAttachExchange(THtcleoLibraryAttachTrace* aTrace,
		TUint32 aValue)
	{
	if (!aTrace || !aTrace->iProgress || !aTrace->iNotify || !aTrace->iAck)
		return KErrArgument;
	TInt r=Kern::KUSafeWrite(aTrace->iProgress, &aValue, sizeof(aValue));
	if (r!=KErrNone)
		return r;
	Kern::SemaphoreSignal(*aTrace->iNotify);
	return Kern::SemaphoreWait(*aTrace->iAck);
	}

static TInt HtcleoLibraryAttachProgress(THtcleoLibraryAttachTrace* aTrace,
		TUint32 aStage, TInt aPayload) __attribute__((noinline));

static TInt HtcleoLibraryAttachProgress(THtcleoLibraryAttachTrace* aTrace,
		TUint32 aStage, TInt aPayload)
	{
	const TUint32 value = 0xa0000000u |
		((aStage & 0xffu) << 16) |
		(TUint32(aPayload) & 0xffffu);
	return HtcleoLibraryAttachExchange(aTrace, value);
	}

static TInt HtcleoLibraryAttachReturn(TInt& aNumEps, TUint32 aValue,
		TInt aResult)
	{
	const TInt value=(TInt)aValue;
	kumemput32(&aNumEps, &value, sizeof(value));
	return aResult;
	}

TInt ExecHandler::LibraryAttach(TInt aHandle, TInt& aNumEps, TLinAddr* aEpList)
	{
	__KTRACE_OPT2(KEXEC,KDLL,Kern::Printf(">Exec::LibraryAttach"));
	DThread& t=*TheCurrentThread;
	DProcess& p=*t.iOwningProcess;
	const TUint32 KHtcleoLibraryAttachTraceFlag = 0x40000000u;
	const TUint32 KHtcleoLibraryAttachTraceMagic = 0x484c3432u;
	const TUint32 KHtcleoLibraryAttachBootstrapBase = 0x42000100u;
	const TUint32 KHtcleoLibraryAttachBootstrapMask = 0xff00ffffu;
	const TUint32 KHtcleoLibraryAttachBootstrapValue = 0xa0b60000u;
	const TInt KHtcleoLibraryAttachTraceMax = 0x100;
	TInt rawMaxEps;
	TInt maxEps;
	TInt numEps=0;
	THtcleoLibraryAttachTrace htcleoTrace;
	htcleoTrace.iProgress=NULL;
	htcleoTrace.iNotify=NULL;
	htcleoTrace.iAck=NULL;
	kumemget32(&rawMaxEps, &aNumEps, sizeof(TInt));
	maxEps=rawMaxEps;
	const TUint32 rawMaxValue=TUint32(rawMaxEps);
	if ((rawMaxValue & KHtcleoLibraryAttachBootstrapMask)==
			KHtcleoLibraryAttachBootstrapBase)
		{
		const TUint32 phase=(rawMaxValue >> 16) & 0xffu;
		if (phase<1u || phase>6u)
			return HtcleoLibraryAttachReturn(aNumEps, phase, KErrArgument);
		TUint32 magic=0;
		TInt notifyHandle=0;
		TInt ackHandle=0;
		TUint32 bootstrapValue=rawMaxValue;
		TInt bootstrapResult=KErrNone;
		if (phase>=2u)
			{
			kumemget32(&magic, aEpList+KHtcleoLibraryAttachTraceMax,
				sizeof(magic));
			bootstrapValue=magic;
			}
		if (phase>=3u)
			{
			kumemget32(&notifyHandle,
				aEpList+KHtcleoLibraryAttachTraceMax+1,
				sizeof(notifyHandle));
			bootstrapValue=TUint32(notifyHandle);
			}
		if (phase>=4u)
			{
			kumemget32(&ackHandle,
				aEpList+KHtcleoLibraryAttachTraceMax+2,
				sizeof(ackHandle));
			bootstrapValue=TUint32(ackHandle);
			}
		if (phase>=5u)
			{
			if (phase==5u)
				{
				kumemget32(&notifyHandle,
					aEpList+KHtcleoLibraryAttachTraceMax+1,
					sizeof(notifyHandle));
				}
			NKern::LockSystem();
			htcleoTrace.iNotify=(DSemaphore*)t.ObjectFromHandle(
				notifyHandle, ESemaphore);
			htcleoTrace.iAck=(DSemaphore*)t.ObjectFromHandle(
				ackHandle, ESemaphore);
			NKern::UnlockSystem();
			TUint32 mask=0;
			if (htcleoTrace.iNotify)
				mask|=1u;
			if (htcleoTrace.iAck)
				mask|=2u;
			if (htcleoTrace.iNotify && htcleoTrace.iAck &&
					htcleoTrace.iNotify!=htcleoTrace.iAck)
				mask|=4u;
			bootstrapValue=mask;
			if (mask!=7u)
				bootstrapResult=KErrBadHandle;
			}
		if (phase==6u && bootstrapResult==KErrNone)
			{
			htcleoTrace.iProgress=aEpList+KHtcleoLibraryAttachTraceMax;
			bootstrapValue=KHtcleoLibraryAttachBootstrapValue;
			bootstrapResult=HtcleoLibraryAttachExchange(&htcleoTrace,
				bootstrapValue);
			}
		return HtcleoLibraryAttachReturn(aNumEps, bootstrapValue,
			bootstrapResult);
		}
	if (TUint32(rawMaxEps) ==
			(KHtcleoLibraryAttachTraceFlag |
			 TUint32(KHtcleoLibraryAttachTraceMax)))
		{
		TUint32 magic=0;
		TInt notifyHandle=0;
		TInt ackHandle=0;
		maxEps=KHtcleoLibraryAttachTraceMax;
		kumemget32(&magic, aEpList+maxEps, sizeof(magic));
		kumemget32(&notifyHandle, aEpList+maxEps+1, sizeof(notifyHandle));
		kumemget32(&ackHandle, aEpList+maxEps+2, sizeof(ackHandle));
		if (magic!=KHtcleoLibraryAttachTraceMagic)
			return HtcleoLibraryAttachReturn(aNumEps, 0xb3010000u,
				KErrCorrupt);
		if (notifyHandle<=0 || ackHandle<=0 || notifyHandle==ackHandle)
			return HtcleoLibraryAttachReturn(aNumEps, 0xb3020000u,
				KErrArgument);
		NKern::LockSystem();
		htcleoTrace.iNotify=(DSemaphore*)t.ObjectFromHandle(
			notifyHandle, ESemaphore);
		htcleoTrace.iAck=(DSemaphore*)t.ObjectFromHandle(
			ackHandle, ESemaphore);
		NKern::UnlockSystem();
		if (!htcleoTrace.iNotify || !htcleoTrace.iAck ||
				htcleoTrace.iNotify==htcleoTrace.iAck)
			return HtcleoLibraryAttachReturn(aNumEps, 0xb3030000u,
				KErrBadHandle);
		htcleoTrace.iProgress=aEpList+maxEps;
		}
	const TInt firstHandoff=HtcleoLibraryAttachProgress(&htcleoTrace, 1u,
		maxEps);
	if (TUint32(rawMaxEps)==
			(KHtcleoLibraryAttachTraceFlag |
			 TUint32(KHtcleoLibraryAttachTraceMax)) &&
			firstHandoff!=KErrNone)
		return HtcleoLibraryAttachReturn(aNumEps, 0xb3040000u |
			(TUint32(-firstHandoff) & 0xffffu), firstHandoff);
	__ASSERT_ALWAYS(	p.iDllLock->iCleanup.iThread==&t &&
						t.iClosingLibs.IsEmpty() &&
						maxEps>0,
					K::PanicKernExec(ELibraryAttachInvalid));
	(void)HtcleoLibraryAttachProgress(&htcleoTrace, 2u, KErrNone);
	Kern::AccessCode();
	(void)HtcleoLibraryAttachProgress(&htcleoTrace, 3u, KErrNone);
	NKern::LockSystem();
	DLibrary* pL=(DLibrary*)t.ObjectFromHandle(aHandle,ELibrary);
	NKern::UnlockSystem();
	if (!pL)
		{
		Kern::EndAccessCode();
		K::PanicKernExec(EBadHandle);
		}
	(void)HtcleoLibraryAttachProgress(&htcleoTrace, 4u, TInt(pL->iState));
	DCodeSeg* pS=pL->iCodeSeg;
	TInt r=KErrNone;
	if (pL->iState!=DLibrary::EAttached)	// already loaded or no entry points required
		{
		SDblQue cs_list;
		(void)HtcleoLibraryAttachProgress(&htcleoTrace, 5u, KErrNone);
		numEps=p.CallList(cs_list, pS, DProcess::ETraverseFlagRestrict);
		(void)HtcleoLibraryAttachProgress(&htcleoTrace, 6u, numEps);
		if (numEps>maxEps)
			r=ETooManyEntryPoints;
		else if (numEps>0)
			{
			(void)HtcleoLibraryAttachProgress(&htcleoTrace, 7u, numEps);
			r=DCodeSeg::WriteCallList(cs_list, aEpList, ETrue);
			DCodeSeg::EmptyQueue(cs_list, 0);
			if (r==KErrNone)
				pL->iState=DLibrary::EAttaching;
			}
		else
			pL->iState=DLibrary::EAttached;
		(void)HtcleoLibraryAttachProgress(&htcleoTrace, 8u, r);
		}
	Kern::EndAccessCode();
	(void)HtcleoLibraryAttachProgress(&htcleoTrace, 9u, r);
	if (r>0 || numEps==0)
		p.SignalDllLock();
	if (r>0)
		K::PanicKernExec(r);
	kumemput32(&aNumEps,&numEps,sizeof(TInt));
	(void)HtcleoLibraryAttachProgress(&htcleoTrace, 10u, numEps);
	__KTRACE_OPT2(KEXEC,KDLL,Kern::Printf("<Exec::LibraryAttach numEps=%d r=%d",numEps,r));
	return r;
	}

'''


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    begin = text.index("// " + MARKER)
    finish = text.index(END, begin)
    region = text[begin:finish]
    checks = {
        "marker": text.count(MARKER) == 1,
        "one function": text.count("TInt ExecHandler::LibraryAttach(") == 1,
        "helper definition and ten calls":
            region.count("HtcleoLibraryAttachProgress(") == 12,
        "exact flag": region.count("0x40000000u") == 1,
        "exact magic": region.count("0x484c3432u") == 1,
        "exact max": region.count("KHtcleoLibraryAttachTraceMax = 0x100") == 1,
        "six-phase bootstrap":
            region.count("0x42000100u") == 1
            and region.count("0xff00ffffu") == 1
            and region.count("0xa0b60000u") == 1
            and "phase<1u || phase>6u" in region,
        "safe writes": region.count(
            "Kern::KUSafeWrite(aTrace->iProgress"
        ) == 1,
        "durable notify ack handoff":
            region.count("Kern::SemaphoreSignal(*aTrace->iNotify)") == 1
            and region.count("Kern::SemaphoreWait(*aTrace->iAck)") == 1,
        "semaphore handle lookup":
            region.count("ObjectFromHandle(") == 5
            and region.count("ESemaphore") == 4,
        "exact validation fails closed":
            all(code in region for code in (
                "0xb3010000u", "0xb3020000u", "0xb3030000u",
                "0xb3040000u",
            )),
        "three reserved words":
            "aEpList+maxEps+1" in region
            and "aEpList+maxEps+2" in region,
        "stock call list": region.count(
            "p.CallList(cs_list, pS, DProcess::ETraverseFlagRestrict)"
        ) == 1,
        "stock write list": region.count(
            "DCodeSeg::WriteCallList(cs_list, aEpList, ETrue)"
        ) == 1,
        "stock num write": region.count(
            "kumemput32(&aNumEps,&numEps,sizeof(TInt))"
        ) == 1,
        "no display or delay": all(
            token not in REPLACEMENT
            for token in ("HalFunction", "User::After", "e7f000f0")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "kernel LibraryAttach progress verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    path = args.root / "kernel/eka/kernel/scodeseg.cpp"
    if not path.is_file():
        raise SystemExit(f"missing kernel source: {path}")

    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        verify(path)
        print(
            "HTCLEO_KERNEL_LIBRARY_ATTACH_PROGRESS=installed stages=A01-A0A "
            "bootstrap=6 handoff=notify-ack"
        )
        return

    if text.count(START) != 1 or text.count(END) != 1:
        raise SystemExit("kernel LibraryAttach replacement anchors are not unique")
    begin = text.index(START)
    finish = text.index(END, begin)
    text = text[:begin] + REPLACEMENT + text[finish:]
    path.write_text(text, encoding="utf-8")
    verify(path)
    print(
        "HTCLEO_KERNEL_LIBRARY_ATTACH_PROGRESS=installed stages=A01-A0A "
        "bootstrap=6 handoff=notify-ack"
    )


if __name__ == "__main__":
    main()
