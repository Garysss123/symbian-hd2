#!/usr/bin/env python3
"""Trace MatrixMenu's common CONE event/redraw scheduler boundaries."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_CONE_EVENT_PUMP_DURABLE_TRACE_V1"
REDRAW_MARKER = "HTCLEO_CONE_REDRAW_PUMP_DURABLE_TRACE_V1"
REDRAW_PREREQUISITE = "HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1"


LOGGER_ANCHOR = "//#define CONE_SHOW_TRACE\t\t\t\n"
LOGGER = r'''// HTCLEO_CONE_EVENT_PUMP_DURABLE_TRACE_V1
void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	if (RProcess().SecureId().iId != 0x101F4CD2u)
		{
		return;
		}
	RFs fs;
	TInt r = fs.Connect();
	if (r != KErrNone)
		{
		return;
		}
	_LIT(KHtcleoConeDir, "C:\\Symbian3\\");
	_LIT(KHtcleoConePath, "C:\\Symbian3\\CONELOG.TXT");
	r = fs.MkDirAll(KHtcleoConeDir);
	if (r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}
	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoConePath, EFileWrite | EFileShareAny);
	if (r == KErrNotFound || r == KErrPathNotFound)
		{
		r = file.Replace(fs, KHtcleoConePath, EFileWrite | EFileShareAny);
		}
	else if (r == KErrNone)
		{
		r = file.Seek(ESeekEnd, position);
		}
	if (r == KErrNone && position <= ((16384 * 64) - 64))
		{
		_LIT8(KHtcleoConePrefix, "HTCLEO_COE ");
		TBuf8<96> record;
		record.Append(KHtcleoConePrefix);
		record.AppendNumFixedWidth((TUint32)position, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
		record.Append(_L8("\r\n"));
		file.Write(record);
		}
	file.Close();
	fs.Close();
	}

'''


WAIT_OLD = r'''EXPORT_C void CCoeScheduler::WaitForAnyRequest()
/** Waits for an asynchronous request to complete. */
	{
	iCoeEnv->DoFlush();
	CBaActiveScheduler::WaitForAnyRequest();
	}'''


WAIT_NEW = r'''EXPORT_C void CCoeScheduler::WaitForAnyRequest()
/** Waits for an asynchronous request to complete. */
	{
	HtcleoConeLog(0x434F0100u, KErrNone,
		(TUint32)iCoeEnv->WsSession().Handle());
	iCoeEnv->DoFlush();
	HtcleoConeLog(0x434F0101u, KErrNone,
		(TUint32)iCoeEnv->WsSession().Handle());
	HtcleoConeLog(0x434F0102u, KErrNone, 0u);
	CBaActiveScheduler::WaitForAnyRequest();
	HtcleoConeLog(0x434F0103u, KErrNone, 0u);
	}'''


FLUSH_OLD = r'''void CCoeEnv::DoFlush()
/** Flush WSERV's command buffer */
	{
	CCoeScheduler* coeScheduler=static_cast<CCoeScheduler*>(CActiveScheduler::Current());
	if (coeScheduler->Flush())
		iWsSession.Flush();
	else
		coeScheduler->SetFlush(ETrue);
	}'''


FLUSH_NEW = r'''void CCoeEnv::DoFlush()
/** Flush WSERV's command buffer */
	{
	CCoeScheduler* coeScheduler=static_cast<CCoeScheduler*>(CActiveScheduler::Current());
	HtcleoConeLog(0x434F0400u, coeScheduler->Flush() ? 1 : 0,
		(TUint32)iWsSession.Handle());
	if (coeScheduler->Flush())
		{
		HtcleoConeLog(0x434F0401u, KErrNone,
			(TUint32)iWsSession.Handle());
		iWsSession.Flush();
		HtcleoConeLog(0x434F0402u, KErrNone,
			(TUint32)iWsSession.Handle());
		}
	else
		{
		coeScheduler->SetFlush(ETrue);
		HtcleoConeLog(0x434F0403u, KErrNone, 0u);
		}
	}'''


QUEUE_OLD = r'''void CCoeRedrawer::Queue()
	{
	// HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1
	const TBool htcleoArmBeforeReady =
		(RProcess().SecureId().iId == 0x101f4cd2u);
	if (htcleoArmBeforeReady)
		{
		iStatus = KRequestPending;
		SetActive();
		iWsSession.RedrawReady(&iStatus);
		}
	else
		{
		iWsSession.RedrawReady(&iStatus);
		SetActive();
		}
	}'''


QUEUE_NEW = r'''void CCoeRedrawer::Queue()
	{
	// HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1
	// HTCLEO_CONE_REDRAW_PUMP_DURABLE_TRACE_V1
	const TBool htcleoArmBeforeReady =
		(RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoConeLog(0x434F0300u, IsActive() ? 1 : 0,
		(TUint32)iWsSession.Handle());
	if (htcleoArmBeforeReady)
		{
		iStatus = KRequestPending;
		SetActive();
		HtcleoConeLog(0x434F0301u, iStatus.Int(), 1u);
		iWsSession.RedrawReady(&iStatus);
		HtcleoConeLog(0x434F0302u, iStatus.Int(), 1u);
		}
	else
		{
		iWsSession.RedrawReady(&iStatus);
		SetActive();
		}
	}'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_main(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(text, LOGGER_ANCHOR, LOGGER + LOGGER_ANCHOR, "logger")
    text = replace_once(text, WAIT_OLD, WAIT_NEW, "scheduler wait")
    text = replace_once(text, FLUSH_OLD, FLUSH_NEW, "scheduler flush")
    text = replace_once(
        text,
        "EXPORT_C void CCoeEnv::RunL()\n\t{\n\tswitch (iStatus.Int())",
        "EXPORT_C void CCoeEnv::RunL()\n\t{\n"
        "\tHtcleoConeLog(0x434F0200u, iStatus.Int(), "
        "(TUint32)iWsSession.Handle());\n\tswitch (iStatus.Int())",
        "event RunL entry",
    )
    text = replace_once(
        text,
        "\tTWsEvent event;\n\tiWsSession.GetEvent(event);\n"
        "\tRequestEventNotification();\t\t//Request now so that WSERV has time to respond (on SMP systems) before the return to the Active Scheduler\n"
        "\tconst TUint handle=event.Handle();",
        "\tHtcleoConeLog(0x434F0201u, KErrNone, 0u);\n"
        "\tTWsEvent event;\n\tiWsSession.GetEvent(event);\n"
        "\tHtcleoConeLog(0x434F0202u, event.Type(), (TUint32)event.Handle());\n"
        "\tRequestEventNotification();\t\t//Request now so that WSERV has time to respond (on SMP systems) before the return to the Active Scheduler\n"
        "\tHtcleoConeLog(0x434F0203u, iStatus.Int(), IsActive() ? 1u : 0u);\n"
        "\tconst TUint handle=event.Handle();",
        "event get and re-arm",
    )
    text = replace_once(
        text,
        "\t\tiLastEvent=event;\n\t\tiAppUi->MonitorWsEvent(event);",
        "\t\tiLastEvent=event;\n"
        "\t\tHtcleoConeLog(0x434F0204u, event.Type(), handle);\n"
        "\t\tiAppUi->MonitorWsEvent(event);\n"
        "\t\tHtcleoConeLog(0x434F0205u, event.Type(), handle);",
        "event monitor",
    )
    text = replace_once(
        text,
        "\t\tiAppUi->HandleWsEventL(event,window);\n\t\t}\n\t}",
        "\t\tHtcleoConeLog(0x434F0206u, event.Type(), handle);\n"
        "\t\tiAppUi->HandleWsEventL(event,window);\n"
        "\t\tHtcleoConeLog(0x434F0207u, event.Type(), handle);\n"
        "\t\t}\n\tHtcleoConeLog(0x434F0208u, KErrNone, 0u);\n\t}",
        "event handler return",
    )
    return text


def install_private(text: str) -> str:
    if REDRAW_MARKER in text:
        return text
    if REDRAW_PREREQUISITE not in text:
        raise SystemExit("redraw arm prerequisite is missing")
    text = replace_once(
        text,
        "#include <coecntrl.h>\t// class CCoeControl\n",
        "#include <coecntrl.h>\t// class CCoeControl\n\n"
        "void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n",
        "redraw logger declaration",
    )
    text = replace_once(text, QUEUE_OLD, QUEUE_NEW, "redraw queue")
    text = replace_once(
        text,
        "void CCoeRedrawer::RunL()\n\t{\n    User::LeaveIfError( iStatus.Int() );",
        "void CCoeRedrawer::RunL()\n\t{\n"
        "\tHtcleoConeLog(0x434F0310u, iStatus.Int(), "
        "(TUint32)iWsSession.Handle());\n"
        "    User::LeaveIfError( iStatus.Int() );",
        "redraw RunL entry",
    )
    text = replace_once(
        text,
        "\tiWsSession.GetRedraw(redraw);\n\tconst TUint handle = redraw.Handle();",
        "\tiWsSession.GetRedraw(redraw);\n"
        "\tHtcleoConeLog(0x434F0311u, KErrNone, (TUint32)redraw.Handle());\n"
        "\tconst TUint handle = redraw.Handle();",
        "redraw fetch",
    )
    text = replace_once(
        text,
        "\tCCoeControl* window=REINTERPRET_CAST(CCoeControl*,handle);\n\tQueue();\n#if defined(_DEBUG)",
        "\tCCoeControl* window=REINTERPRET_CAST(CCoeControl*,handle);\n"
        "\tQueue();\n\tHtcleoConeLog(0x434F0312u, KErrNone, handle);\n"
        "\tHtcleoConeLog(0x434F0313u, KErrNone, handle);\n#if defined(_DEBUG)",
        "redraw re-arm",
    )
    text = replace_once(
        text,
        "#endif\n\tiWsSession.Flush();\t//flush the window-server client-side buffer *after* HandleRedrawEvent has done any drawing",
        "#endif\n\tHtcleoConeLog(0x434F0314u, KErrNone, handle);\n"
        "\tHtcleoConeLog(0x434F0315u, KErrNone, (TUint32)iWsSession.Handle());\n"
        "\tiWsSession.Flush();\t//flush the window-server client-side buffer *after* HandleRedrawEvent has done any drawing\n"
        "\tHtcleoConeLog(0x434F0316u, KErrNone, (TUint32)iWsSession.Handle());",
        "redraw handler and flush",
    )
    return text


def verify(main: str, private: str) -> None:
    combined = main + private
    expected = (
        list(range(0x434F0100, 0x434F0104))
        + list(range(0x434F0200, 0x434F0209))
        + list(range(0x434F0300, 0x434F0303))
        + list(range(0x434F0310, 0x434F0317))
        + list(range(0x434F0400, 0x434F0404))
    )
    checks = {
        "markers": main.count(MARKER) == 1 and private.count(REDRAW_MARKER) == 1,
        "stages": all(combined.count(f"0x{stage:08X}u") == 1 for stage in expected),
        "logger": (
            main.count("void HtcleoConeLog(") == 1
            and private.count("void HtcleoConeLog(") == 1
            and main.count(r"C:\\Symbian3\\CONELOG.TXT") == 1
            and main.count("position <= ((16384 * 64) - 64)") == 1
            # A later HomeScreen-only router intentionally adds a second
            # writer while preserving this exact MatrixMenu logger.
            and main.count("file.Write(record);") >= 1
            and "file.Flush" not in main
        ),
        "event rearm retained": main.count("RequestEventNotification();") >= 2,
        "event handler retained": main.count(
            "iAppUi->HandleWsEventL(event,window);"
        ) == 1,
        "scheduler wait retained": main.count(
            "CBaActiveScheduler::WaitForAnyRequest();"
        ) == 1,
        "redraw real handler retained": private.count(
            "window->HandleRedrawEvent(redraw.Rect());"
        ) >= 1,
        "redraw flush retained": private.count("iWsSession.Flush();") == 1,
        "no behavior bypass": all(
            token not in LOGGER + WAIT_NEW + FLUSH_NEW + QUEUE_NEW
            for token in ("TRAP_IGNORE", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("CONE event-pump trace failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/classicui/lafagnosticuifoundation/cone/src"
    main_path = base / "COEMAIN.CPP"
    private_path = base / "COEPRIV.CPP"
    if not main_path.is_file() or not private_path.is_file():
        raise SystemExit("missing CONE event-pump source")
    main_text = main_path.read_text(encoding="latin-1")
    private_text = private_path.read_text(encoding="latin-1")
    main_text = install_main(main_text)
    private_text = install_private(private_text)
    verify(main_text, private_text)
    main_path.write_text(main_text, encoding="latin-1")
    private_path.write_text(private_text, encoding="latin-1")
    print(
        "HTCLEO_CONE_EVENT_PUMP_TRACE="
        "CONELOG-1m-scheduler-event-redraw-flush-0100-0403"
    )


if __name__ == "__main__":
    main()
