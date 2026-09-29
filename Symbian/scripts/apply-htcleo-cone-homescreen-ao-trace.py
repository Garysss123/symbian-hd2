#!/usr/bin/env python3
"""Route existing CONE scheduler/AO diagnostics to a HomeScreen-only log."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_CONE_HOMESCREEN_AO_TRACE_V1"
PUMP_MARKER = "HTCLEO_CONE_EVENT_PUMP_DURABLE_TRACE_V1"
READY_MARKER = "HTCLEO_CONE_READY_AO_IDENTITY_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HOME_LOGGER = r'''// HTCLEO_CONE_HOMESCREEN_AO_TRACE_V1
static void HtcleoHomeConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	if (RProcess().SecureId().iId != 0x102750F0u)
		{
		return;
		}
	RFs fs;
	TInt r = fs.Connect();
	if (r != KErrNone)
		{
		return;
		}
	_LIT(KHtcleoHomeConeDir, "C:\\Symbian3\\");
	_LIT(KHtcleoHomeConePath, "C:\\Symbian3\\HSCONE.TXT");
	(void)fs.MkDirAll(KHtcleoHomeConeDir);
	RFile file;
	r = file.Open(fs, KHtcleoHomeConePath, EFileWrite | EFileShareAny);
	if (r == KErrNotFound || r == KErrPathNotFound)
		{
		r = file.Replace(fs, KHtcleoHomeConePath,
			EFileWrite | EFileShareAny);
		}
	TInt position = 0;
	if (r == KErrNone)
		{
		r = file.Seek(ESeekEnd, position);
		}
	if (r == KErrNone && position <= (1048576 - 128))
		{
		_LIT8(KHtcleoHomeConePrefix, "HTCLEO_HCOE ");
		TBuf8<128> record;
		record.Append(KHtcleoHomeConePrefix);
		record.AppendNumFixedWidth((TUint32)position, EHex, 8);
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
		record.Append('\n');
		(void)file.Write(record);
		}
	file.Close();
	fs.Close();
	}

'''


def patch_main(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    if text.count(PUMP_MARKER) != 1:
        raise SystemExit("CONE event-pump trace prerequisite is missing")
    text = replace_once(
        text,
        f"// {PUMP_MARKER}\nvoid HtcleoConeLog",
        HOME_LOGGER + f"// {PUMP_MARKER}\nvoid HtcleoConeLog",
        "HomeScreen CONE logger",
    )
    return replace_once(
        text,
        """void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	if (RProcess().SecureId().iId != 0x101F4CD2u)
""",
        """void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	const TUint32 htcleoSid = RProcess().SecureId().iId;
	if (htcleoSid == 0x102750F0u)
		{
		HtcleoHomeConeLog(aStage, aResult, aDetail);
		return;
		}
	if (htcleoSid != 0x101F4CD2u)
""",
        "HomeScreen log routing",
    )


def patch_ready(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    if text.count(READY_MARKER) != 1:
        raise SystemExit("CONE ready-AO trace prerequisite is missing")
    text = replace_once(
        text,
        f"// {READY_MARKER}\n",
        f"// {READY_MARKER}\n// {MARKER}\n",
        "ready-AO HomeScreen marker",
    )
    return replace_once(
        text,
        """    if (RProcess().SecureId().iId != 0x101F4CD2u || !aScheduler)
        {
        return;
        }
""",
        """    const TUint32 htcleoSid = RProcess().SecureId().iId;
    if ((htcleoSid != 0x101F4CD2u && htcleoSid != 0x102750F0u) ||
        !aScheduler)
        {
        return;
        }
""",
        "ready-AO HomeScreen routing",
    )


def verify(main: str, ready: str) -> None:
    checks = {
        "main marker": main.count(MARKER) == 1,
        "ready marker": ready.count(MARKER) == 1,
        "pump retained": main.count(PUMP_MARKER) == 1,
        "ready trace retained": ready.count(READY_MARKER) == 1,
        "HomeScreen SID main": main.count("0x102750F0u") == 2,
        "HomeScreen SID ready": ready.count("0x102750F0u") == 1,
        "MatrixMenu SID main": main.count("0x101F4CD2u") == (
            2 if "HTCLEO_MATRIXMENU_CONE_FILE_TRACE_RETIRED_V1" in main else 1),
        "MatrixMenu SID ready": ready.count("0x101F4CD2u") == (
            2 if "HTCLEO_MATRIXMENU_READY_AO_TRACE_RETIRED_V1" in ready else 1),
        "dedicated path": main.count(r"C:\\Symbian3\\HSCONE.TXT") == 1,
        "one MiB": main.count("1048576 - 128") == 1,
        "process and thread": (
            HOME_LOGGER.count("RProcess().Id().Id()") == 1
            and HOME_LOGGER.count("RThread().Id().Id()") == 1
        ),
        "AO identity retained": (
            ready.count("active->Priority()") == 1
            and ready.count("active->iStatus.Int()") == 1
            and ready.count("reinterpret_cast<const TUint32*>(active)") == 1
        ),
        "no timing or dispatch": all(
            token not in HOME_LOGGER
            for token in ("User::After", "WaitForRequest", "RequestComplete")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen CONE AO trace audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    cone = args.root / "sf/mw/classicui/lafagnosticuifoundation/cone/src"
    main_path = cone / "COEMAIN.CPP"
    ready_path = cone / "htcleoschedulertrace.cpp"
    for path in (main_path, ready_path):
        if not path.is_file():
            raise SystemExit(f"missing CONE source: {path}")
    main_text = patch_main(main_path.read_text(encoding="latin-1"))
    ready_text = patch_ready(ready_path.read_text(encoding="latin-1"))
    main_path.write_text(main_text, encoding="latin-1")
    ready_path.write_text(ready_text, encoding="latin-1")
    verify(main_text, ready_text)
    print(
        "HTCLEO_CONE_HOMESCREEN_AO_TRACE="
        "HSCONE-1m-scheduler-event-redraw-ready-ao-vtable"
    )


if __name__ == "__main__":
    main()
