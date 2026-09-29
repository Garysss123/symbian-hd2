#!/usr/bin/env python3
"""Trace the exact NVG RLibrary::Init attach/entrypoint sequence durably.

Iteration 417 proved that the loader IPC returned, the library handle was
published and the loader session closed, then stopped immediately before
RLibrary::Init().  For that already name/UID-gated NVG path only, reproduce
the stock ARM RLibrary::InitL control flow and log LibraryAttach, every DLL
process-attach entrypoint, and LibraryAttached.  V6 starts a low-priority
watcher before RLoader acquires the process DLL lock and uses a kernel
notify/ack semaphore pair to flush each exact LibraryAttach stage before that
diagnostic caller continues.  Before the real attach it also executes six
side-effect-free bootstrap calls that isolate SVC dispatch, user metadata
reads, semaphore-handle resolution and the first notify/ack exchange.
V6 also gives both private executive wrappers an explicit Thumb-entry/ARM-SWI
interworking veneer.  EKA2's ARM vector reads the 32-bit SWI opcode at LR-4;
a Thumb SVC instruction is therefore not a valid executive stub on this port.
Non-NVG loads retain stock paths.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V6"
UPGRADE_MARKERS = (
    "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V5",
    "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V4",
    "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V3",
    "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V2",
)
LEGACY_MARKER = "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V1"
INCLUDE_ANCHOR = "#include <e32const_private.h>\n"
BODY_ANCHOR = "// Design Note:\n"
CALL_ANCHOR = "\t\t\t\t\thtcleoLoadResult = iLibrary.Init();"
OLD_CALL = "\t\t\t\t\thtcleoLoadResult = HtcleoNvgLibraryInit(iLibrary);"
TRACE_DECL_ANCHOR = "\t\t\tTInt htcleoHandle = 0;\n"
STOP_ANCHOR = "\t\t\tHtcleoEcomLog(0x00000809u, htcleoLoadResult,\n"


HELPER = r'''
// HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG_V6
// EExecLibraryAttach/EExecLibraryAttached are private user-side executive
// calls normally emitted inside euser's RLibrary::InitL.  ECom is compiled as
// Thumb, but EKA2's ARM SWI vector reads a 32-bit opcode at LR-4.  Enter each
// local wrapper in Thumb state, use BX PC to interwork into an aligned ARM SWI,
// then BX LR back to the Thumb caller.  Keep euser.dll and all other callers
// byte-for-byte untouched.
#if defined(__MARM__)
static TInt HtcleoNvgLibraryAttachExec(TInt, TInt&, TLinAddr*)
                          __attribute__((naked));
static TInt HtcleoNvgLibraryAttachExec(TInt, TInt&, TLinAddr*)
	{
	asm("bx pc");
	asm("nop");
	asm(".code 32");
	asm("swi %a0" : : "i" (EExecLibraryAttach));
	asm("bx lr");
	asm(".code 16");
	}

static TInt HtcleoNvgLibraryAttachedExec(TInt)
                          __attribute__((naked));
static TInt HtcleoNvgLibraryAttachedExec(TInt)
	{
	asm("bx pc");
	asm("nop");
	asm(".code 32");
	asm("swi %a0" : : "i" (EExecLibraryAttached));
	asm("bx lr");
	asm(".code 16");
	}
#endif

const TUint32 KHtcleoAttachTraceMagic = 0x484c3432u;
const TUint32 KHtcleoAttachTraceFlag = 0x40000000u;
const TUint32 KHtcleoAttachBootstrapBase = 0x42000100u;
const TUint32 KHtcleoAttachBootstrapValue = 0xa0b60000u;
const TUint32 KHtcleoAttachTraceDone = 0xa0ff0000u;
const TUint32 KHtcleoAttachTraceAbort = 0xa0fe0000u;

struct THtcleoNvgAttachBuffer
	{
	TLinAddr iEntryPoints[KMaxLibraryEntryPoints];
	volatile TUint32 iProgress;
	TInt iNotifyHandle;
	TInt iAckHandle;
	};

__ASSERT_COMPILE(_FOFF(THtcleoNvgAttachBuffer, iProgress) ==
	(sizeof(TLinAddr) * KMaxLibraryEntryPoints));
__ASSERT_COMPILE(sizeof(THtcleoNvgAttachBuffer) ==
	(sizeof(TLinAddr) * (KMaxLibraryEntryPoints + 3)));

struct THtcleoNvgAttachTrace
	{
	THtcleoNvgAttachBuffer iBuffer;
	RSemaphore iStart;
	RSemaphore iArmed;
	RSemaphore iKernelNotify;
	RSemaphore iKernelAck;
	RThread iThread;
	TRequestStatus iExit;
	TBool iRunning;
	TBool iArmedForAttach;
	};

static TInt HtcleoNvgAttachWatchThread(TAny* aContext)
	{
	THtcleoNvgAttachTrace* trace =
		(THtcleoNvgAttachTrace*)aContext;
	HtcleoEcomLog(0x00000a00u, KErrNone, 0u);
	RThread::Rendezvous(KErrNone);
	trace->iStart.Wait();
	TUint32 last = trace->iBuffer.iProgress;
	if(last == KHtcleoAttachTraceAbort)
		{
		HtcleoEcomLog(0x00000a03u, KErrNone, last);
		return KErrNone;
		}
	HtcleoEcomLog(0x00000a01u, KErrNone, last);
	trace->iArmed.Signal();
	// Stay blocked until either the exact kernel opt-in path publishes one
	// stage or the caller requests terminal shutdown.  For every kernel stage,
	// acknowledge only after the fixed ECOMLOG record has been flushed.
	for(;;)
		{
		trace->iKernelNotify.Wait();
		const TUint32 value = trace->iBuffer.iProgress;
		if(value == KHtcleoAttachTraceDone)
			{
			HtcleoEcomLog(0x00000a02u, KErrNone, value);
			return KErrNone;
			}
		if(value == KHtcleoAttachTraceAbort)
			{
			HtcleoEcomLog(0x00000a03u, KErrNone, value);
			return KErrNone;
			}
		if(value == KHtcleoAttachBootstrapValue)
			HtcleoEcomLog(0x0000b006u, KErrNone, value);
		else if(value != last &&
				(value & 0xff000000u) == 0xa0000000u)
			{
			const TUint32 step = (value >> 16) & 0xffu;
			if(step >= 1u && step <= 10u)
				{
				const TInt payload = (TInt)(TInt16)(value & 0xffffu);
				HtcleoEcomLog(0x00000a10u + step, payload, value);
				}
			else
				HtcleoEcomLog(0x00000a05u, KErrCorrupt, value);
			}
		else
			HtcleoEcomLog(0x00000a05u, KErrCorrupt, value);
		last = value;
		trace->iKernelAck.Signal();
		}
	}

static TInt HtcleoNvgAttachTraceStart(THtcleoNvgAttachTrace& aTrace)
	{
	aTrace.iRunning = EFalse;
	aTrace.iArmedForAttach = EFalse;
	aTrace.iBuffer.iProgress = KHtcleoAttachTraceMagic;
	aTrace.iBuffer.iNotifyHandle = 0;
	aTrace.iBuffer.iAckHandle = 0;
	TInt r = aTrace.iStart.CreateLocal(0);
	if(r != KErrNone)
		return r;
	r = aTrace.iArmed.CreateLocal(0);
	if(r != KErrNone)
		{
		aTrace.iStart.Close();
		return r;
		}
	r = aTrace.iKernelNotify.CreateLocal(0);
	if(r != KErrNone)
		{
		aTrace.iArmed.Close();
		aTrace.iStart.Close();
		return r;
		}
	r = aTrace.iKernelAck.CreateLocal(0);
	if(r != KErrNone)
		{
		aTrace.iKernelNotify.Close();
		aTrace.iArmed.Close();
		aTrace.iStart.Close();
		return r;
		}
	aTrace.iBuffer.iNotifyHandle = aTrace.iKernelNotify.Handle();
	aTrace.iBuffer.iAckHandle = aTrace.iKernelAck.Handle();
	_LIT(KHtcleoAttachWatchName, "HtcleoNvgAttachWatch");
	r = aTrace.iThread.Create(KHtcleoAttachWatchName,
		HtcleoNvgAttachWatchThread, 0x2000, 0x2000, 0x10000, &aTrace);
	if(r != KErrNone)
		{
		aTrace.iKernelAck.Close();
		aTrace.iKernelNotify.Close();
		aTrace.iArmed.Close();
		aTrace.iStart.Close();
		return r;
		}
	// Low priority is now safe: each exact kernel stage signals iKernelNotify
	// and blocks the diagnostic caller on iKernelAck until this watcher flushes.
	aTrace.iThread.SetPriority(EPriorityMuchLess);
	TRequestStatus rendezvous;
	aTrace.iThread.Rendezvous(rendezvous);
	aTrace.iThread.Resume();
	User::WaitForRequest(rendezvous);
	r = rendezvous.Int();
	if(r != KErrNone)
		{
		aTrace.iThread.Close();
		aTrace.iKernelAck.Close();
		aTrace.iKernelNotify.Close();
		aTrace.iArmed.Close();
		aTrace.iStart.Close();
		return r;
		}
	aTrace.iThread.Logon(aTrace.iExit);
	aTrace.iRunning = ETrue;
	return KErrNone;
	}

static TBool HtcleoNvgAttachTraceArm(THtcleoNvgAttachTrace& aTrace)
	{
	if(!aTrace.iRunning)
		return EFalse;
	aTrace.iBuffer.iProgress = KHtcleoAttachTraceMagic;
	aTrace.iStart.Signal();
	aTrace.iArmed.Wait();
	aTrace.iArmedForAttach = ETrue;
	return ETrue;
	}

static void HtcleoNvgAttachTraceStop(THtcleoNvgAttachTrace& aTrace,
		TUint32 aTerminal)
	{
	if(!aTrace.iRunning)
		return;
	aTrace.iBuffer.iProgress = aTerminal;
	if(!aTrace.iArmedForAttach)
		aTrace.iStart.Signal();
	else
		aTrace.iKernelNotify.Signal();
	User::WaitForRequest(aTrace.iExit);
	aTrace.iThread.Close();
	aTrace.iKernelAck.Close();
	aTrace.iKernelNotify.Close();
	aTrace.iArmed.Close();
	aTrace.iStart.Close();
	aTrace.iRunning = EFalse;
	}

#if defined(__MARM__)
static TInt HtcleoNvgAttachBootstrap(RLibrary& aLibrary,
		THtcleoNvgAttachTrace& aTrace)
	{
	HtcleoEcomLog(0x0000b000u, aTrace.iBuffer.iNotifyHandle,
		(TUint32)aTrace.iBuffer.iAckHandle);
	for(TInt phase = 1; phase <= 6; ++phase)
		{
		TInt bootstrapWord = (TInt)(KHtcleoAttachBootstrapBase |
			((TUint32)phase << 16));
		HtcleoEcomLog(0x0000b100u + (TUint32)phase, KErrNone,
			(TUint32)bootstrapWord);
		const TInt result = HtcleoNvgLibraryAttachExec(aLibrary.Handle(),
			bootstrapWord, aTrace.iBuffer.iEntryPoints);
		HtcleoEcomLog(0x0000b200u + (TUint32)phase, result,
			(TUint32)bootstrapWord);
		if(result != KErrNone)
			return result;
		if(phase == 6)
			aTrace.iBuffer.iProgress = KHtcleoAttachTraceMagic;
		}
	return KErrNone;
	}

static TInt HtcleoNvgLibraryInitL(RLibrary& aLibrary,
		THtcleoNvgAttachTrace& aTrace)
	{
	HtcleoEcomLog(0x00000901u, KErrNone, (TUint32)aLibrary.Handle());
	const TBool traceEnabled = HtcleoNvgAttachTraceArm(aTrace);
	const TInt bootstrapResult = traceEnabled ?
		HtcleoNvgAttachBootstrap(aLibrary, aTrace) : KErrNone;
	TInt numEntryPoints = KMaxLibraryEntryPoints;
	if(traceEnabled && bootstrapResult == KErrNone)
		numEntryPoints |= (TInt)KHtcleoAttachTraceFlag;
	TInt attachResult = bootstrapResult;
	if(bootstrapResult == KErrNone)
		{
		HtcleoEcomLog(0x00000902u, KErrNone,
			(TUint32)KMaxLibraryEntryPoints);
		attachResult = HtcleoNvgLibraryAttachExec(aLibrary.Handle(),
			numEntryPoints, aTrace.iBuffer.iEntryPoints);
		}
	HtcleoNvgAttachTraceStop(aTrace, KHtcleoAttachTraceDone);
	if(bootstrapResult != KErrNone)
		return bootstrapResult;
	HtcleoEcomLog(0x00000903u, attachResult,
		(TUint32)numEntryPoints);
	if(attachResult != KErrNone)
		return attachResult;
	if(numEntryPoints == 0)
		{
		HtcleoEcomLog(0x00000904u, KErrNone,
			(TUint32)aLibrary.Handle());
		return KErrNone;
		}

	for(TInt index = 0; index < numEntryPoints; ++index)
		{
		const TLinAddr entryAddress = aTrace.iBuffer.iEntryPoints[index];
		HtcleoEcomLog(0x00000910u, index, (TUint32)entryAddress);
		const TLibraryEntry entry = (TLibraryEntry)entryAddress;
		const TInt entryResult = (*entry)(KModuleEntryReasonProcessAttach);
		HtcleoEcomLog(0x00000911u, entryResult, (TUint32)index);
		if(entryResult != KErrNone)
			{
			HtcleoEcomLog(0x00000905u, entryResult, (TUint32)index);
			return entryResult;
			}
		}

	HtcleoEcomLog(0x00000906u, KErrNone, (TUint32)aLibrary.Handle());
	const TInt attachedResult =
		HtcleoNvgLibraryAttachedExec(aLibrary.Handle());
	HtcleoEcomLog(0x00000907u, attachedResult,
		(TUint32)aLibrary.Handle());
	return attachedResult;
	}
#endif

static TInt HtcleoNvgLibraryInit(RLibrary& aLibrary,
		THtcleoNvgAttachTrace& aTrace)
	{
#if defined(__MARM__)
	TInt initResult = KErrNone;
	TRAPD(leaveResult, initResult = HtcleoNvgLibraryInitL(aLibrary, aTrace));
	HtcleoEcomLog(0x00000908u, leaveResult, (TUint32)initResult);
	if(leaveResult != KErrNone)
		{
		_LIT(KHtcleoUserPanicCategory, "USER");
		User::Panic(KHtcleoUserPanicCategory, EDllStaticConstructorLeave);
		}
	HtcleoEcomLog(0x00000909u, initResult,
		(TUint32)aLibrary.Handle());
	return initResult;
#else
	HtcleoNvgAttachTraceStop(aTrace, KHtcleoAttachTraceAbort);
	return aLibrary.Init();
#endif
	}

'''


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    fixed_stages = tuple(f"0x0000090{index:X}u" for index in range(1, 10))
    checks = {
        "marker": text.count(MARKER) == 1,
        "old markers absent": all(marker not in text for marker in UPGRADE_MARKERS)
        and LEGACY_MARKER not in text,
        "panic include": text.count("#include <e32panic.h>") == 1,
        "exec enum include": text.count("#include <exec_enum.h>") == 1,
        "module reason include": text.count("#include <u32std.h>") == 1,
        "fixed stages": all(text.count(stage) == 1 for stage in fixed_stages),
        "entrypoint pre": text.count("0x00000910u") == 1,
        "entrypoint post": text.count("0x00000911u") == 1,
        "attach exec": text.count("HtcleoNvgLibraryAttachExec") == 4,
        "attached exec": text.count("HtcleoNvgLibraryAttachedExec") == 3,
        "thumb entry arm swi veneers":
            text.count('asm("bx pc")') == 2
            and text.count('asm("nop")') == 2
            and text.count('asm(".code 32")') == 2
            and text.count('asm(".code 16")') == 2,
        "exact init helper call": text.count(
            "htcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
            "\t\t\t\t\t\thtcleoAttachTrace);"
        ) == 1,
        "watcher start": text.count("HtcleoNvgAttachTraceStart(") == 2,
        "watcher stop": text.count("HtcleoNvgAttachTraceStop(") == 4,
        "watcher thread": text.count("HtcleoNvgAttachWatchThread") == 2,
        "watcher create": text.count("iThread.Create(") == 1,
        "watcher low priority": text.count(
            "iThread.SetPriority(EPriorityMuchLess)"
        ) == 1,
        "watcher rendezvous": text.count("RThread::Rendezvous(KErrNone)") == 1,
        "watcher arm semaphores": text.count("iStart.Signal()") == 2
        and text.count("iArmed.Wait()") == 1,
        "kernel notify semaphore":
            text.count("iKernelNotify.CreateLocal(0)") == 1
            and text.count("iKernelNotify.Wait()") == 1
            and text.count("iKernelNotify.Signal()") == 1
            and text.count("iKernelNotify.Handle()") == 1,
        "kernel ack semaphore":
            text.count("iKernelAck.CreateLocal(0)") == 1
            and text.count("iKernelAck.Signal()") == 1
            and text.count("iKernelAck.Handle()") == 1,
        "old observe handoff absent":
            "iObserve" not in text
            and "HtcleoNvgAttachTraceObserve" not in text,
        "watcher fixed stages": all(
            text.count(f"0x00000a0{stage}u") == (2 if stage == 3 else 1)
            for stage in range(5)
        ),
        "watcher protocol anomaly": text.count("0x00000a05u") == 2,
        "watcher dynamic stage": text.count("0x00000a10u + step") == 1,
        "bootstrap constants":
            text.count("0x42000100u") == 1
            and text.count("0xa0b60000u") == 1,
        "bootstrap fixed stages":
            text.count("0x0000b000u") == 1
            and text.count("0x0000b006u") == 1,
        "bootstrap dynamic stages":
            text.count("0x0000b100u + (TUint32)phase") == 1
            and text.count("0x0000b200u + (TUint32)phase") == 1
            and text.count("phase <= 6") == 1,
        "bootstrap helper": text.count("HtcleoNvgAttachBootstrap(") == 2,
        "attach error fails closed":
            text.count("if(attachResult != KErrNone)") == 1,
        "exact trace flag": text.count("0x40000000u") == 1,
        "exact trace magic": text.count("0x484c3432u") == 1,
        "259-word buffer": text.count(
            "sizeof(TLinAddr) * (KMaxLibraryEntryPoints + 3)"
        ) == 1,
        "buffer semaphore handles":
            text.count("iNotifyHandle") == 4
            and text.count("iAckHandle") == 4,
        "stock init call only fallback": text.count("return aLibrary.Init();") == 1,
        "old exact call absent": CALL_ANCHOR not in text,
        "no delay": "User::After" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom library-init entrypoint-log verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    path = (
        args.root
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/UnloadPolicy.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing ECom source: {path}")

    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        begin = text.index("// " + MARKER + "\n")
        finish = text.index(BODY_ANCHOR, begin)
        if text[begin:finish] != HELPER:
            text = text[:begin] + HELPER + text[finish:]
            path.write_text(text, encoding="utf-8")
        if "#include <u32std.h>" not in text:
            include = "#include <exec_enum.h>\n"
            if text.count(include) != 1:
                raise SystemExit("installed ECom init-log include anchor is not unique")
            text = text.replace(include, include + "#include <u32std.h>\n", 1)
            path.write_text(text, encoding="utf-8")
        verify(path)
        print(
            "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG=installed "
            "stages=0901-0911,A000-A005,A11-A1A,B000,B006,B101-B106,B201-B206 "
            "bootstrap=6 handoff=notify-ack"
        )
        return

    # V2/V3/V4/V5 already have the trace object, call signature and lifecycle hooks.
    # Replace only the helper region and do not inject a second declaration.
    installed_upgrade = next(
        (marker for marker in UPGRADE_MARKERS if marker in text), None
    )
    if installed_upgrade is not None:
        old_start = "// " + installed_upgrade + "\n"
        if text.count(old_start) != 1:
            raise SystemExit("installed helper start is not unique")
        begin = text.index(old_start)
        finish = text.index(BODY_ANCHOR, begin)
        text = text[:begin] + HELPER + text[finish:]
        path.write_text(text, encoding="utf-8")
        verify(path)
        print(
            "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG=installed "
            "stages=0901-0911,A000-A005,A11-A1A,B000,B006,B101-B106,B201-B206 "
            "bootstrap=6 handoff=notify-ack"
        )
        return

    if text.count(BODY_ANCHOR) != 1:
        raise SystemExit("ECom init-log helper anchor is not unique")

    if LEGACY_MARKER in text:
        old_start = "// " + LEGACY_MARKER + "\n"
        if text.count(old_start) != 1:
            raise SystemExit("installed V1 helper start is not unique")
        begin = text.index(old_start)
        finish = text.index(BODY_ANCHOR, begin)
        text = text[:begin] + HELPER + text[finish:]
    else:
        if text.count(INCLUDE_ANCHOR) != 1:
            raise SystemExit("ECom init-log include anchor is not unique")
        text = text.replace(
            INCLUDE_ANCHOR,
            INCLUDE_ANCHOR
            + "#include <e32panic.h>\n#include <exec_enum.h>\n#include <u32std.h>\n",
            1,
        )
        text = text.replace(BODY_ANCHOR, HELPER + BODY_ANCHOR, 1)

    if text.count(TRACE_DECL_ANCHOR) != 1:
        raise SystemExit("ECom trace declaration anchor is not unique")
    text = text.replace(
        TRACE_DECL_ANCHOR,
        TRACE_DECL_ANCHOR
        + "\t\t\tTHtcleoNvgAttachTrace htcleoAttachTrace;\n"
        + "\t\t\tconst TInt htcleoTraceStartResult =\n"
        + "\t\t\t\tHtcleoNvgAttachTraceStart(htcleoAttachTrace);\n"
        + "\t\t\tHtcleoEcomLog(0x00000a04u, htcleoTraceStartResult, 0u);\n",
        1,
    )

    if text.count(OLD_CALL) == 1:
        call = OLD_CALL
    elif text.count(CALL_ANCHOR) == 1:
        call = CALL_ANCHOR
    else:
        raise SystemExit("ECom init-log call anchor is not unique")
    text = text.replace(
        call,
        "\t\t\t\t\thtcleoLoadResult = HtcleoNvgLibraryInit(iLibrary,\n"
        "\t\t\t\t\t\thtcleoAttachTrace);",
        1,
    )

    if text.count(STOP_ANCHOR) != 1:
        raise SystemExit("ECom watcher-stop anchor is not unique")
    text = text.replace(
        STOP_ANCHOR,
        "\t\t\tHtcleoNvgAttachTraceStop(htcleoAttachTrace,\n"
        "\t\t\t\tKHtcleoAttachTraceAbort);\n"
        + STOP_ANCHOR,
        1,
    )
    path.write_text(text, encoding="utf-8")
    verify(path)
    print(
        "HTCLEO_ECOM_LIBRARY_INIT_ENTRYPOINT_LOG=installed "
        "stages=0901-0911,A000-A005,A11-A1A,B000,B006,B101-B106,B201-B206 "
        "bootstrap=6 handoff=notify-ack"
    )


if __name__ == "__main__":
    main()
