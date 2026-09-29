#!/usr/bin/env python3
"""Isolate WServ diagnostic FAT waits from the window/input server thread.

The UI thread is the sole producer. A private-heap worker owns all RFs/RFile
handles. Its queue is bounded and drops new evidence instead of blocking UI.
This tests an observation-induced stall; it does not assert that FAT is faulty.
"""
from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "HTCLEO_WSERV_NONBLOCKING_LOG_V1"
SIGNATURE = "void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n\t{"

QUEUE = r'''// HTCLEO_WSERV_NONBLOCKING_LOG_V1
// SPSC: only the WServ thread publishes; only the diagnostic thread consumes.
// Private worker heap prevents FAT allocation/locks from owning the UI heap.
struct THtcleoWsRecord
	{
	TUint32 iSequence, iStage, iResult, iDetail;
	TUint32 iPid, iTid, iTick, iFocus, iDropped;
	};
static const TUint32 KHtcleoWsQueueSize = 8192;
static THtcleoWsRecord gHtcleoWsQueue[KHtcleoWsQueueSize];
static volatile TUint32 gHtcleoWsWrite = 0;
static volatile TUint32 gHtcleoWsRead = 0;
static TUint32 gHtcleoWsDropped = 0;
static TUint32 gHtcleoWsProducerTid = 0;
static TBool gHtcleoWsWorkerAttempted = EFalse;
static TInt gHtcleoWsWorkerResult = KErrNotReady;

static void HtcleoWsEnqueue(const THtcleoWsRecord& aRecord)
	{
	const TUint32 write = __e32_atomic_load_acq32(&gHtcleoWsWrite);
	const TUint32 read = __e32_atomic_load_acq32(&gHtcleoWsRead);
	if (write - read >= KHtcleoWsQueueSize)
		{
		++gHtcleoWsDropped;
		return; // Never wait for the writer, even when SD I/O stops.
		}
	gHtcleoWsQueue[write % KHtcleoWsQueueSize] = aRecord;
	__e32_atomic_store_rel32(&gHtcleoWsWrite, write + 1);
	}

static TBool HtcleoWsDequeue(THtcleoWsRecord& aRecord)
	{
	const TUint32 read = __e32_atomic_load_acq32(&gHtcleoWsRead);
	const TUint32 write = __e32_atomic_load_acq32(&gHtcleoWsWrite);
	if (read == write)
		return EFalse;
	aRecord = gHtcleoWsQueue[read % KHtcleoWsQueueSize];
	__e32_atomic_store_rel32(&gHtcleoWsRead, read + 1);
	return ETrue;
	}

'''

WORKER = r'''static TInt HtcleoWsLogWorker(TAny*)
	{
	CTrapCleanup* cleanup = CTrapCleanup::New();
	if (!cleanup)
		return KErrNoMemory;
	for (;;)
		{
		THtcleoWsRecord entry;
		for (TInt batch = 0; batch < 32 && HtcleoWsDequeue(entry); ++batch)
			HtcleoWsWriteRecord(entry);
		// This timer/wait belongs to the private worker, never the UI thread.
		User::After(100000);
		}
	delete cleanup;
	return KErrNone;
	}

'''

PRODUCER = r'''	// HTCLEO_WSERV_LOG_CAPACITY_512_V1: superseded by the byte ring below.
	const TUint32 tid = (TUint32)RThread().Id().Id();
	if (!gHtcleoWsWorkerAttempted)
		{
		gHtcleoWsWorkerAttempted = ETrue;
		gHtcleoWsProducerTid = tid;
		_LIT(KWorkerName, "HtcleoWsLog");
		RThread worker;
		gHtcleoWsWorkerResult = worker.Create(KWorkerName, HtcleoWsLogWorker,
			0x4000, 0x1000, 0x10000, NULL, EOwnerProcess);
		if (gHtcleoWsWorkerResult == KErrNone)
			{
			worker.SetPriority(EPriorityLess);
			worker.Resume();
			worker.Close(); // Does not stop the running thread.
			}
		}
	if (gHtcleoWsWorkerResult != KErrNone || tid != gHtcleoWsProducerTid)
		return; // No synchronous-file fallback and no second producer.
	THtcleoWsRecord entry;
	entry.iSequence = gHtcleoWsLogSequence++;
	entry.iStage = aStage;
	entry.iResult = (TUint32)aResult;
	entry.iDetail = aDetail;
	entry.iPid = (TUint32)RProcess().Id().Id();
	entry.iTid = tid;
	entry.iTick = (TUint32)User::NTickCount();
	CWsWindowGroup* focus = CWsTop::CurrentFocusScreen() ?
		CWsTop::FocusWindowGroup() : NULL;
	entry.iFocus = focus ? (TUint32)focus->Identifier() : 0u;
	entry.iDropped = gHtcleoWsDropped;
	HtcleoWsEnqueue(entry);
	}
'''


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"nonblocking WServ anchor missing/duplicated: {old[:100]!r}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if MARKER in text:
        # Upgrade an un-packaged V1 build candidate to a normal Symbian thread
        # cleanup stack before its component compilation.
        if "CTrapCleanup* cleanup = CTrapCleanup::New();" not in text:
            without_cleanup = WORKER.replace(
                "\tCTrapCleanup* cleanup = CTrapCleanup::New();\n"
                "\tif (!cleanup)\n\t\treturn KErrNoMemory;\n", ""
            ).replace("\tdelete cleanup;\n", "")
            text = once(text, without_cleanup, WORKER)
        verify(text)
        return text
    if "HTCLEO_WSERV_SHELL_HANDOFF_LOG_GATE_V1" not in text:
        raise SystemExit("require iteration744 handoff and liveness log filters")
    text = once(text, "#include <f32file.h>",
                "#include <f32file.h>\n#include <e32atomics.h>")
    start = text.index(SIGNATURE)
    end = text.index("#else\nstatic inline void HtcleoWsLog", start)
    old = text[start:end]
    body = old.index("\t// HTCLEO_WSERV_LOG_CAPACITY_512_V1")
    gate = old[:body]
    writer_body = old[old.index("\t// HTCLEO_WSERV_LOG_RING_1M_V1"):]
    writer_body = writer_body.replace("gHtcleoWsLogSequence,", "entry.iSequence,")
    for old_value, new_value in (
        ("aStage,", "entry.iStage,"),
        ("(TUint32)aResult,", "entry.iResult,"),
        ("aDetail,", "entry.iDetail,"),
        ("(TUint32)RProcess().Id().Id(),", "entry.iPid,"),
        ("(TUint32)RThread().Id().Id(),", "entry.iTid,"),
    ):
        writer_body = once(writer_body, old_value, new_value)
    writer_body = writer_body.replace("(TUint32)User::NTickCount(),", "entry.iTick,")
    writer_body = once(writer_body,
        "\t\tCWsWindowGroup* focus = CWsTop::CurrentFocusScreen() ?\n"
        "\t\t\tCWsTop::FocusWindowGroup() : NULL;\n"
        "\t\trecord.AppendNumFixedWidth(focus ? (TUint32)focus->Identifier() : 0u,",
        "\t\trecord.AppendNumFixedWidth(entry.iFocus,")
    writer_body = once(writer_body,
        "\t\trecord.AppendNumFixedWidth((TUint32)htcleoPreviousIoResult, EHex, 8);",
        "\t\trecord.AppendNumFixedWidth((TUint32)htcleoPreviousIoResult, EHex, 8);\n"
        "\t\trecord.Append(' ');\n"
        "\t\trecord.AppendNumFixedWidth(entry.iDropped, EHex, 8);\n"
        "\t\trecord.Append(' ');\n"
        "\t\trecord.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);")
    writer_body = once(writer_body, "\t\t\t++gHtcleoWsLogSequence;\n", "")
    writer = "static void HtcleoWsWriteRecord(const THtcleoWsRecord& entry)\n\t{\n" + writer_body
    text = text[:start] + QUEUE + writer + WORKER + gate + PRODUCER + text[end:]
    text = once(text,
        "// Best-effort startup evidence.  The Window Server main thread is sole writer.",
        "// Best-effort evidence. WServ enqueues; a private worker is the sole FAT writer.")
    verify(text)
    return text


def verify(text: str) -> None:
    start = text.index(SIGNATURE)
    end = text.index("#else\nstatic inline void HtcleoWsLog", start)
    producer = text[start:end]
    writer = text[text.index("static void HtcleoWsWriteRecord"):text.index("static TInt HtcleoWsLogWorker")]
    checks = {
        "one marker": text.count(MARKER) == 1,
        "unchanged stage gates": all(s in producer for s in
            ("htcleoTouchStage", "htcleoFatalStage", "htcleoHeartbeat", "htcleoHandoffStage")),
        "no producer I/O/wait": all(s not in producer for s in
            ("RFs ", "RFile ", "file.", "fs.", "User::After", "WaitFor", "RequestComplete", "Rendezvous", "Logon")),
        "no cross-thread server/handle use": all(s not in writer for s in
            ("CWsTop", "CWsWindowGroup", "RProcess().Id", "RThread().Id")),
        "bounded release/acquire queue": QUEUE in text,
        "private worker": WORKER in text and PRODUCER in producer,
        "retained durable worker": text.count("file.Write(record)") == 1
            and text.count("file.Flush()") == 1 and "KCapacity = 1048576" in writer,
        "source-time identity plus backlog metadata": all(s in writer for s in
            ("entry.iTick", "entry.iTid", "entry.iFocus", "entry.iDropped", "User::NTickCount()")),
    }
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("nonblocking WServ verification: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/WSTOP.CPP"
    path.write_text(patch(path.read_text(encoding="utf-8")), encoding="utf-8")
    print("HTCLEO_WSERV_NONBLOCKING_LOG=private-worker-spsc8192-drop-not-wait-1m-file-captured-ui-identity")


if __name__ == "__main__":
    main()
