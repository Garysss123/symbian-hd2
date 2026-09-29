#!/usr/bin/env python3
"""Trace a bounded set of real Type2A events through WServ."""

from __future__ import annotations

import argparse
from pathlib import Path


EVENT_MARKER = "HTCLEO_WSERV_TYPE2A_RAW_RECEIVER_TRACE_V1"
POINTER_MARKER = "HTCLEO_WSERV_TYPE2A_HITTEST_TRACE_V1"

EVENT_DECL_ANCHOR = "GLREF_D CDebugLogBase *wsDebugLog;\n"
EVENT_DECL = r'''GLREF_D CDebugLogBase *wsDebugLog;
extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
static TInt gHtcleoRawPointerTraceCount = 0;
'''

EVENT_OLD = r'''void CRawEventReceiver::RunL()
	{
//__PROFILE_START(11);
	if (TWsPointer::PreProcessDriverEvent(iEventBuf.Event()
#if defined(__WINS__)
											,ETrue
#endif
													  ))
		TWindowServerEvent::ProcessRawEvent(iEventBuf.Event());
	Request();
//__PROFILE_END(11);
	}
'''

EVENT_NEW = r'''void CRawEventReceiver::RunL()
	{
//__PROFILE_START(11);
	TRawEvent& htcleoRawEvent = iEventBuf.Event();
	const TRawEvent::TType htcleoRawType = htcleoRawEvent.Type();
	const TBool htcleoPointerEvent =
		TWsPointer::IsPointerEventType(htcleoRawType);
	const TBool htcleoTraceEvent =
		htcleoPointerEvent && gHtcleoRawPointerTraceCount < 16;
	if (htcleoTraceEvent)
		{
		// HTCLEO_WSERV_TYPE2A_RAW_RECEIVER_TRACE_V1
		const TPoint htcleoRawPos = htcleoRawEvent.Pos();
		HtcleoWsLog(0x00000452u, static_cast<TInt>(htcleoRawType),
			(static_cast<TUint32>(htcleoRawPos.iX & 0xffff) << 16) |
			static_cast<TUint32>(htcleoRawPos.iY & 0xffff));
		}
	const TBool htcleoAccepted = TWsPointer::PreProcessDriverEvent(htcleoRawEvent
#if defined(__WINS__)
											,ETrue
#endif
													  );
	if (htcleoTraceEvent)
		HtcleoWsLog(0x00000453u, static_cast<TInt>(htcleoAccepted),
			static_cast<TUint32>(htcleoRawType));
	if (htcleoAccepted)
		TWindowServerEvent::ProcessRawEvent(htcleoRawEvent);
	if (htcleoTraceEvent)
		{
		HtcleoWsLog(0x00000454u, KErrNone,
			static_cast<TUint32>(htcleoRawType));
		++gHtcleoRawPointerTraceCount;
		}
	Request();
//__PROFILE_END(11);
	}
'''

POINTER_DECL_ANCHOR = "TWsPointer::iYOffsetMax;\n"
POINTER_DECL = (
    POINTER_DECL_ANCHOR
    + "static TInt gHtcleoPointerHitTraceCount = 0;\n"
)

POINTER_OLD = r'''void TWsPointer::ProcessPointerEvent(TWsEvent& aEvent)
	{
	if (iCurrentWindow && iCurrentWindow!=iRootWindow)
'''

POINTER_NEW = r'''void TWsPointer::ProcessPointerEvent(TWsEvent& aEvent)
	{
	if (gHtcleoPointerHitTraceCount < 16)
		{
		// HTCLEO_WSERV_TYPE2A_HITTEST_TRACE_V1
		const TInt htcleoWindowState =
			(iCurrentWindow ? 1 : 0) |
			(iCurrentWindow == iRootWindow ? 2 : 0);
		const TUint32 htcleoWindowHandle =
			iCurrentWindow ?
			static_cast<TUint32>(iCurrentWindow->ClientHandle()) : 0u;
		HtcleoWsLog(0x00000458u, htcleoWindowState,
			htcleoWindowHandle);
		HtcleoWsLog(0x00000459u,
			static_cast<TInt>(aEvent.Pointer()->iType),
			htcleoWindowHandle);
		++gHtcleoPointerHitTraceCount;
		}
	if (iCurrentWindow && iCurrentWindow!=iRootWindow)
'''


def install(event: str, pointer: str) -> tuple[str, str]:
    if EVENT_MARKER not in event:
        if event.count(EVENT_DECL_ANCHOR) != 1:
            raise SystemExit("WServ raw trace declaration anchor mismatch")
        event = event.replace(EVENT_DECL_ANCHOR, EVENT_DECL, 1)
        start_token = "void CRawEventReceiver::RunL()"
        end_token = "\n//\n// TEventRequestQueue //"
        if event.count(start_token) != 1:
            raise SystemExit("WServ raw receiver start mismatch")
        start = event.index(start_token)
        end = event.index(end_token, start)
        event = event[:start] + EVENT_NEW + event[end:]
    if POINTER_MARKER not in pointer:
        if pointer.count(POINTER_DECL_ANCHOR) != 1:
            raise SystemExit("WServ hit-test declaration anchor mismatch")
        if pointer.count(POINTER_OLD) != 1:
            raise SystemExit("WServ hit-test function anchor mismatch")
        pointer = pointer.replace(POINTER_DECL_ANCHOR, POINTER_DECL, 1)
        pointer = pointer.replace(POINTER_OLD, POINTER_NEW, 1)
    return event, pointer


def verify(event: str, pointer: str) -> None:
    checks = {
        "markers": (
            event.count(EVENT_MARKER) == 1
            and pointer.count(POINTER_MARKER) == 1
        ),
        "bounded raw": (
            event.count("gHtcleoRawPointerTraceCount < 16") == 1
            and event.count("++gHtcleoRawPointerTraceCount") == 1
        ),
        "bounded hit": (
            pointer.count("gHtcleoPointerHitTraceCount < 16") == 1
            and pointer.count("++gHtcleoPointerHitTraceCount") == 1
        ),
        "raw stages": all(
            event.count(f"0x0000{stage:04X}u") == 1
            for stage in range(0x452, 0x455)
        ),
        "hit stages": all(
            pointer.count(f"0x0000{stage:04X}u") == 1
            for stage in range(0x458, 0x45A)
        ),
        "stock processing retained": (
            event.count("TWindowServerEvent::ProcessRawEvent(htcleoRawEvent)")
            == 1
            and pointer.count(
                "if (iCurrentWindow && iCurrentWindow!=iRootWindow)"
            ) == 1
        ),
        "no fabricated event or wait": all(
            token not in EVENT_NEW + POINTER_NEW
            for token in ("Kern::AddEvent", "event.Set", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "WServ Type2A raw-path verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    event_path = base / "EVENT.CPP"
    pointer_path = base / "POINTER.CPP"
    event = event_path.read_text(encoding="latin-1")
    pointer = pointer_path.read_text(encoding="latin-1")
    event, pointer = install(event, pointer)
    verify(event, pointer)
    event_path.write_text(event, encoding="latin-1")
    pointer_path.write_text(pointer, encoding="latin-1")
    print(
        "HTCLEO_WSERV_TYPE2A_RAW_PATH_TRACE="
        "bounded-16-receiver-preprocess-process-hittest-0452-0454-0458-0459"
    )


if __name__ == "__main__":
    main()
