#!/usr/bin/env python3
"""Keep touch observations alive with five-second snapshots and a 1 MiB ring."""

from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "HTCLEO_WSERV_LOW_RATE_TOUCH_HEARTBEAT_V1"
RING_MARKER = "HTCLEO_WSERV_LOG_RING_1M_V1"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"expected one anchor: {old[:90]!r}")
    return text.replace(old, new, 1)


def patch_event(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(text, "iHtcleoTouchProbe->Start(250000, 250000,",
                        "iHtcleoTouchProbe->Start(5000000, 5000000,")
    text = replace_once(text,
        "\tCRawEventReceiver* self = static_cast<CRawEventReceiver*>(aPtr);",
        "\t// " + MARKER + "\n"
        "\tCRawEventReceiver* self = static_cast<CRawEventReceiver*>(aPtr);\n"
        "\tHtcleoWsLog(0x00000477u, self->IsActive(),\n"
        "\t\tstatic_cast<TUint32>(self->iStatus.Int()));")
    start = text.index("\tif (self->iHtcleoProbeTicks == 0 ||", text.index(MARKER))
    end = text.index("\t++self->iHtcleoProbeTicks;", start)
    text = text[:start] + '''	// Snapshot cumulative counters even when no point is down right now.
	HtcleoWsLog(0x00000462u, htcleoTouchRawFirst,
		static_cast<TUint32>(htcleoTouchRawSecond));
	HtcleoWsLog(0x00000463u, htcleoTouchPoints,
		static_cast<TUint32>(htcleoTouchTransitions));
	HtcleoWsLog(0x00000464u, htcleoTouchSamples,
		static_cast<TUint32>(htcleoTouchEvents));
	HtcleoWsLog(0x00000465u, htcleoTouchStage,
		static_cast<TUint32>(htcleoTouchResult));
''' + text[end:]
    text = replace_once(text,
        "\t++self->iHtcleoProbeTicks;\n\treturn self->iHtcleoProbeTicks < 240;",
        "\tself->iHtcleoProbeTicks = (self->iHtcleoProbeTicks + 1) & 0x3fffffff;\n"
        "\treturn ETrue; // CPeriodic ignores callback return values.")
    return text


LOGGER = r'''void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	// HTCLEO_WSERV_TOUCH_ONLY_LOG_V1
	const TBool htcleoTouchStage =
		aStage >= 0x0000045Au && aStage <= 0x00000465u;
	const TBool htcleoFatalStage =
		aStage >= 0x0000046Cu && aStage <= 0x00000476u;
	const TBool htcleoHeartbeat = aStage == 0x00000477u;
	if (!htcleoTouchStage && !htcleoFatalStage && !htcleoHeartbeat)
		return;
	// HTCLEO_WSERV_LOG_CAPACITY_512_V1: superseded by the byte ring below.
	// HTCLEO_WSERV_LOG_RING_1M_V1
	static TInt htcleoWritePosition = 0;
	static TInt htcleoPreviousIoResult = KErrNone;
	const TInt KCapacity = 1048576;
	const TInt KRecordSize = 128;
	RFs fs;
	TInt r = fs.Connect();
	if (r != KErrNone)
		{
		htcleoPreviousIoResult = r;
		return;
		}
	_LIT(KDir, "C:\\Symbian3\\");
	_LIT(KPath, "C:\\Symbian3\\WSLOG.TXT");
	r = fs.MkDirAll(KDir);
	if (r != KErrNone && r != KErrAlreadyExists)
		{
		htcleoPreviousIoResult = r;
		fs.Close();
		return;
		}
	RFile file;
	if (!gHtcleoWsLogStarted)
		r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
	else
		{
		r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
		if (r == KErrNotFound || r == KErrPathNotFound)
			{
			r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
			htcleoWritePosition = 0;
			}
		}
	TInt position = htcleoWritePosition;
	const TBool wrapped = position >= KCapacity;
	if (wrapped)
		position = 0;
	if (r == KErrNone)
		r = file.Seek(ESeekStart, position);
	if (r == KErrNone)
		{
		TBuf8<256> record;
		if (wrapped)
			{
			record.Append(_L8("WRAP "));
			record.AppendNumFixedWidth(gHtcleoWsLogSequence, EHex, 8);
			record.Append(' ');
			record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
			record.AppendFill(' ', KRecordSize - 2 - record.Length());
			record.Append(_L8("\r\n"));
			}
		const TInt recordEnd = record.Length() + KRecordSize;
		record.Append(_L8("HTCLEO_WS "));
		record.AppendNumFixedWidth(gHtcleoWsLogSequence, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
		record.Append(' ');
		CWsWindowGroup* focus = CWsTop::CurrentFocusScreen() ?
			CWsTop::FocusWindowGroup() : NULL;
		record.AppendNumFixedWidth(focus ? (TUint32)focus->Identifier() : 0u,
			EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)htcleoPreviousIoResult, EHex, 8);
		record.AppendFill(' ', recordEnd - 2 - record.Length());
		record.Append(_L8("\r\n"));
		r = file.Write(record);
		if (r == KErrNone)
			{
			htcleoWritePosition = position + record.Length();
			gHtcleoWsLogStarted = ETrue;
			++gHtcleoWsLogSequence;
			r = file.Flush();
			}
		}
	file.Close();
	fs.Close();
	htcleoPreviousIoResult = r;
	}
'''


def patch_logger(text: str) -> str:
    if RING_MARKER in text:
        return text
    start = text.index("void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n\t{")
    end = text.index("#else\nstatic inline void HtcleoWsLog", start)
    text = text[:start] + LOGGER + text[end:]
    return replace_once(text, "static TInt gHtcleoWsLogSequence = 0;",
                        "static TUint32 gHtcleoWsLogSequence = 0;")


def verify(event: str, logger: str) -> None:
    checks = {
        "markers": event.count(MARKER) == 1 and logger.count(RING_MARKER) == 1,
        "period": event.count("Start(5000000, 5000000,") == 1,
        "continuous": "iHtcleoProbeTicks < 240" not in event
            and "iHtcleoProbeTicks == 239" not in event,
        "stages": all(event.count(f"0x0000{stage:04X}u") == 1
                      for stage in [*range(0x45A, 0x466), 0x477]),
        "real input": event.count("UserSvr::CaptureEventHook();") == 1
            and event.count("UserSvr::RequestEvent(iEventBuf,iStatus);") == 1,
        "ring": "KCapacity = 1048576" in logger
            and "KRecordSize = 128" in logger
            and "gHtcleoWsLogSequence >= 512" not in logger
            and 'record.Append(_L8("WRAP "))' in logger,
        "durable": logger.count("file.Write(record)") == 1
            and logger.count("file.Flush()") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("WServ low-rate heartbeat verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    event_path = base / "EVENT.CPP"
    logger_path = base / "openwfc/WSTOP.CPP"
    event = patch_event(event_path.read_text(encoding="latin-1"))
    logger = patch_logger(logger_path.read_text(encoding="utf-8"))
    verify(event, logger)
    event_path.write_text(event, encoding="latin-1")
    logger_path.write_text(logger, encoding="utf-8")
    print("HTCLEO_WSERV_LOW_RATE_TOUCH_HEARTBEAT=5s-continuous-0477-request-0462-0465-counters-1m-ring")


if __name__ == "__main__":
    main()
