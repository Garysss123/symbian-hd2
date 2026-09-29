#!/usr/bin/env python3
"""Trace WServ event-hook state and poll the real Type2A counters briefly."""

from __future__ import annotations

import argparse
from pathlib import Path


HEADER_MARKER = "HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_V1"
SOURCE_MARKER = "HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_IMPL_V1"
HEADER_MARKER_V2 = "HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_V2"
SOURCE_MARKER_V2 = "HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_IMPL_V2"

HEADER_OLD = r'''protected:
	void Request();
	void DoCancel();
	void RunL();
private:
	TRawEventBuf iEventBuf;
'''

HEADER_NEW = r'''protected:
	void Request();
	void DoCancel();
	void RunL();
private:
	// HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_V1
	static TInt HtcleoTouchProbe(TAny* aPtr);
	TRawEventBuf iEventBuf;
	CPeriodic* iHtcleoTouchProbe;
	TInt iHtcleoLastTouchEvents;
	TInt iHtcleoProbeTicks;
	TInt iHtcleoRequestTraceCount;
'''

CONSTRUCTOR_OLD = r'''CRawEventReceiver::CRawEventReceiver(TInt aPriority) : CActive(aPriority)
//
// Constructor
//
	{
'''

CONSTRUCTOR_NEW = r'''CRawEventReceiver::CRawEventReceiver(TInt aPriority) :
	CActive(aPriority), iHtcleoTouchProbe(NULL),
	iHtcleoLastTouchEvents(0), iHtcleoProbeTicks(0),
	iHtcleoRequestTraceCount(0)
//
// Constructor
//
	{
'''

DESTRUCTOR_OLD = r'''CRawEventReceiver::~CRawEventReceiver()
	{
	CActive::Cancel();
	}
'''

DESTRUCTOR_NEW = r'''CRawEventReceiver::~CRawEventReceiver()
	{
	CActive::Cancel();
	delete iHtcleoTouchProbe;
	iHtcleoTouchProbe = NULL;
	}
'''

CONSTRUCT_OLD = r'''void CRawEventReceiver::ConstructL()
	{
	CActiveScheduler::Add(this);
	UserSvr::CaptureEventHook();
	Request();
	}
'''

CONSTRUCT_NEW = r'''void CRawEventReceiver::ConstructL()
	{
	CActiveScheduler::Add(this);
	// HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_IMPL_V1
	HtcleoWsLog(0x0000045Au, KErrNone, 0u);
	UserSvr::CaptureEventHook();
	HtcleoWsLog(0x0000045Bu, KErrNone, 0u);
	iHtcleoLastTouchEvents = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 4, 0, 0);
	const TInt htcleoTouchStage = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 0, 0, 0);
	HtcleoWsLog(0x0000045Cu, iHtcleoLastTouchEvents,
		static_cast<TUint32>(htcleoTouchStage));
	iHtcleoTouchProbe = CPeriodic::NewL(CActive::EPriorityLow);
	iHtcleoTouchProbe->Start(250000, 250000,
		TCallBack(HtcleoTouchProbe, this));
	Request();
	}
'''

REQUEST_OLD = r'''void CRawEventReceiver::Request()
//
// Issue a request for the next event.
//
	{
	UserSvr::RequestEvent(iEventBuf,iStatus);
	SetActive();
	}
'''

REQUEST_NEW = r'''void CRawEventReceiver::Request()
//
// Issue a request for the next event.
//
	{
	UserSvr::RequestEvent(iEventBuf,iStatus);
	if (iHtcleoRequestTraceCount < 4)
		{
		HtcleoWsLog(0x0000045Du, iStatus.Int(),
			static_cast<TUint32>(iHtcleoRequestTraceCount));
		++iHtcleoRequestTraceCount;
		}
	SetActive();
	}
'''

RUNL_ANCHOR = r'''void CRawEventReceiver::RunL()
	{
//__PROFILE_START(11);
'''

RUNL_REPLACEMENT = r'''void CRawEventReceiver::RunL()
	{
//__PROFILE_START(11);
	HtcleoWsLog(0x0000045Eu, iStatus.Int(),
		static_cast<TUint32>(iEventBuf.Event().Type()));
'''

CALLBACK = r'''
TInt CRawEventReceiver::HtcleoTouchProbe(TAny* aPtr)
	{
	CRawEventReceiver* self = static_cast<CRawEventReceiver*>(aPtr);
	const TInt htcleoTouchStage = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 0, 0, 0);
	const TInt htcleoTouchResult = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 1, 0, 0);
	const TInt htcleoTouchEvents = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 4, 0, 0);
	const TInt htcleoTouchXY = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 5, 0, 0);
	if (self->iHtcleoProbeTicks == 0)
		HtcleoWsLog(0x0000045Fu, htcleoTouchEvents,
			static_cast<TUint32>(htcleoTouchStage));
	if (htcleoTouchEvents != self->iHtcleoLastTouchEvents)
		{
		HtcleoWsLog(0x00000460u, htcleoTouchEvents,
			static_cast<TUint32>(htcleoTouchXY));
		HtcleoWsLog(0x00000461u, htcleoTouchResult,
			static_cast<TUint32>(htcleoTouchStage));
		self->iHtcleoLastTouchEvents = htcleoTouchEvents;
		}
	++self->iHtcleoProbeTicks;
	return self->iHtcleoProbeTicks < 240;
	}

'''

HEADER_V2 = r'''protected:
	void Request();
	void DoCancel();
	void RunL();
private:
	// HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_V2
	static TInt HtcleoTouchProbe(TAny* aPtr);
	TRawEventBuf iEventBuf;
	CPeriodic* iHtcleoTouchProbe;
	TInt iHtcleoLastTouchEvents;
	TInt iHtcleoLastTouchRawFirst;
	TInt iHtcleoLastTouchRawSecond;
	TInt iHtcleoLastTouchPoints;
	TInt iHtcleoLastTouchTransitions;
	TInt iHtcleoProbeTicks;
	TInt iHtcleoRequestTraceCount;
	TInt iHtcleoRawTraceCount;
'''

CONSTRUCTOR_V2 = r'''CRawEventReceiver::CRawEventReceiver(TInt aPriority) :
	CActive(aPriority), iHtcleoTouchProbe(NULL),
	iHtcleoLastTouchEvents(0), iHtcleoLastTouchRawFirst(0),
	iHtcleoLastTouchRawSecond(0), iHtcleoLastTouchPoints(0),
	iHtcleoLastTouchTransitions(0), iHtcleoProbeTicks(0),
	iHtcleoRequestTraceCount(0), iHtcleoRawTraceCount(0)
//
// Constructor
//
	{
'''

CONSTRUCT_V2 = r'''void CRawEventReceiver::ConstructL()
	{
	CActiveScheduler::Add(this);
	// HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER_IMPL_V2
	HtcleoWsLog(0x0000045Au, KErrNone, 0u);
	UserSvr::CaptureEventHook();
	HtcleoWsLog(0x0000045Bu, KErrNone, 0u);
	iHtcleoLastTouchEvents = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 4, 0, 0);
	iHtcleoLastTouchRawFirst = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 6, 0, 0);
	iHtcleoLastTouchRawSecond = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 7, 0, 0);
	iHtcleoLastTouchPoints = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 8, 0, 0);
	iHtcleoLastTouchTransitions = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 9, 0, 0);
	const TInt htcleoTouchStage = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 0, 0, 0);
	HtcleoWsLog(0x0000045Cu, iHtcleoLastTouchEvents,
		static_cast<TUint32>(htcleoTouchStage));
	iHtcleoTouchProbe = CPeriodic::NewL(CActive::EPriorityLow);
	iHtcleoTouchProbe->Start(250000, 250000,
		TCallBack(HtcleoTouchProbe, this));
	Request();
	}
'''

CALLBACK_V2 = r'''
TInt CRawEventReceiver::HtcleoTouchProbe(TAny* aPtr)
	{
	CRawEventReceiver* self = static_cast<CRawEventReceiver*>(aPtr);
	const TInt htcleoTouchStage = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 0, 0, 0);
	const TInt htcleoTouchResult = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 1, 0, 0);
	const TInt htcleoTouchSamples = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 3, 0, 0);
	const TInt htcleoTouchEvents = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 4, 0, 0);
	const TInt htcleoTouchXY = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 5, 0, 0);
	const TInt htcleoTouchRawFirst = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 6, 0, 0);
	const TInt htcleoTouchRawSecond = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 7, 0, 0);
	const TInt htcleoTouchPoints = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 8, 0, 0);
	const TInt htcleoTouchTransitions = UserSvr::HalFunction(
		EHalGroupPlatformSpecific2, 9, 0, 0);
	if (self->iHtcleoProbeTicks == 0)
		HtcleoWsLog(0x0000045Fu, htcleoTouchEvents,
			static_cast<TUint32>(htcleoTouchStage));
	if (htcleoTouchEvents != self->iHtcleoLastTouchEvents)
		{
		HtcleoWsLog(0x00000460u, htcleoTouchEvents,
			static_cast<TUint32>(htcleoTouchXY));
		HtcleoWsLog(0x00000461u, htcleoTouchResult,
			static_cast<TUint32>(htcleoTouchStage));
		self->iHtcleoLastTouchEvents = htcleoTouchEvents;
		}
	if (self->iHtcleoProbeTicks == 0 ||
		htcleoTouchRawFirst != self->iHtcleoLastTouchRawFirst ||
		htcleoTouchRawSecond != self->iHtcleoLastTouchRawSecond ||
		htcleoTouchPoints != self->iHtcleoLastTouchPoints ||
		htcleoTouchTransitions != self->iHtcleoLastTouchTransitions)
		{
		if (self->iHtcleoRawTraceCount < 32)
			{
			HtcleoWsLog(0x00000462u, htcleoTouchRawFirst,
				static_cast<TUint32>(htcleoTouchRawSecond));
			HtcleoWsLog(0x00000463u, htcleoTouchPoints,
				static_cast<TUint32>(htcleoTouchTransitions));
			++self->iHtcleoRawTraceCount;
			}
		self->iHtcleoLastTouchRawFirst = htcleoTouchRawFirst;
		self->iHtcleoLastTouchRawSecond = htcleoTouchRawSecond;
		self->iHtcleoLastTouchPoints = htcleoTouchPoints;
		self->iHtcleoLastTouchTransitions = htcleoTouchTransitions;
		}
	if (self->iHtcleoProbeTicks == 239)
		{
		HtcleoWsLog(0x00000464u, htcleoTouchSamples,
			static_cast<TUint32>(htcleoTouchEvents));
		HtcleoWsLog(0x00000465u, htcleoTouchStage,
			static_cast<TUint32>(htcleoTouchResult));
		}
	++self->iHtcleoProbeTicks;
	return self->iHtcleoProbeTicks < 240;
	}

'''


def install(header: str, source: str) -> tuple[str, str]:
    if "#include <u32hal.h>" not in source:
        include_anchor = "#include <hal.h>\n"
        if source.count(include_anchor) != 1:
            raise SystemExit("WServ event-hook HAL include anchor mismatch")
        source = source.replace(
            include_anchor, include_anchor + "#include <u32hal.h>\n", 1
        )
    if HEADER_MARKER not in header and HEADER_MARKER_V2 not in header:
        if header.count(HEADER_OLD) != 1:
            raise SystemExit("WServ event-hook header anchor mismatch")
        header = header.replace(HEADER_OLD, HEADER_NEW, 1)
    if SOURCE_MARKER not in source and SOURCE_MARKER_V2 not in source:
        anchors = {
            "constructor": CONSTRUCTOR_OLD,
            "destructor": DESTRUCTOR_OLD,
            "construct": CONSTRUCT_OLD,
            "request": REQUEST_OLD,
            "runl": RUNL_ANCHOR,
        }
        failed = [name for name, anchor in anchors.items()
                  if source.count(anchor) != 1]
        if failed:
            raise SystemExit(
                "WServ event-hook source anchor mismatch: " + ", ".join(failed)
            )
        source = source.replace(CONSTRUCTOR_OLD, CONSTRUCTOR_NEW, 1)
        source = source.replace(DESTRUCTOR_OLD, DESTRUCTOR_NEW, 1)
        source = source.replace(CONSTRUCT_OLD, CONSTRUCT_NEW, 1)
        source = source.replace(REQUEST_OLD, REQUEST_NEW, 1)
        source = source.replace(RUNL_ANCHOR, RUNL_REPLACEMENT, 1)
        callback_anchor = "\n//\n// TEventRequestQueue //"
        insert = source.index(callback_anchor)
        source = source[:insert] + CALLBACK + source[insert:]
    if HEADER_MARKER_V2 not in header:
        if header.count(HEADER_NEW) != 1:
            raise SystemExit("WServ touch raw-snapshot V2 header anchor mismatch")
        header = header.replace(HEADER_NEW, HEADER_V2, 1)
    if SOURCE_MARKER_V2 not in source:
        upgrades = {
            "constructor": (CONSTRUCTOR_NEW, CONSTRUCTOR_V2),
            "construct": (CONSTRUCT_NEW, CONSTRUCT_V2),
            "callback": (CALLBACK, CALLBACK_V2),
        }
        failed = [name for name, (old, _) in upgrades.items()
                  if source.count(old) != 1]
        if failed:
            raise SystemExit(
                "WServ touch raw-snapshot V2 source anchor mismatch: "
                + ", ".join(failed)
            )
        for old, new in upgrades.values():
            source = source.replace(old, new, 1)
    return header, source


def verify(header: str, source: str) -> None:
    checks = {
        "markers": (
            header.count(HEADER_MARKER_V2) == 1
            and source.count(SOURCE_MARKER_V2) == 1
            and header.count(HEADER_MARKER) == 0
            and source.count(SOURCE_MARKER) == 0
        ),
        "HAL include": source.count("#include <u32hal.h>") == 1,
        "periodic observation policy": (
            source.count("CPeriodic::NewL") == 1
            and (
                (source.count("self->iHtcleoProbeTicks < 240") == 1
                 and source.count("250000, 250000") == 1)
                or ("HTCLEO_WSERV_LOW_RATE_TOUCH_HEARTBEAT_V1" in source
                    and source.count("5000000, 5000000") == 1)
            )
        ),
        "real counters": all(
            source.count(f"EHalGroupPlatformSpecific2, {function}, 0, 0")
            >= 1
            for function in (0, 1, 3, 4, 5, 6, 7, 8, 9)
        ),
        "stages": all(
            source.count(f"0x0000{stage:04X}u") == 1
            for stage in range(0x45A, 0x466)
        ),
        "stock hook/request retained": (
            source.count("UserSvr::CaptureEventHook();") == 1
            and source.count("UserSvr::RequestEvent(iEventBuf,iStatus);") == 1
        ),
        "no fabricated event/window/pixel": all(
            token not in CONSTRUCT_NEW + REQUEST_NEW + CALLBACK
            for token in ("Kern::AddEvent", "UserSvr::AddEvent", "event.Set",
                          "MakeVisible", "DrawNow", "BitBlt")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "WServ event-hook touch-counter verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    header_path = base / "EVENT.H"
    source_path = base / "EVENT.CPP"
    header = header_path.read_text(encoding="latin-1")
    source = source_path.read_text(encoding="latin-1")
    header, source = install(header, source)
    verify(header, source)
    header_path.write_text(header, encoding="latin-1")
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_WSERV_EVENT_HOOK_TOUCH_COUNTER="
        "capture-request-plus-60s-real-event-and-raw-snapshot-045a-0465"
    )


if __name__ == "__main__":
    main()
