#!/usr/bin/env python3
"""Do not queue MMWidgets post-processing outside the real item range."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MMWIDGETS_POSTPROCESS_BOUNDS_GUARD_V1"
TRACE_MARKER = "HTCLEO_MMWIDGETS_POSTPROCESS_AO_TRACE_V1"


OLD = r'''void CMmPostEvaluationProcessor::StartAt( TInt aIndex )
	{
	HtcleoMmwLog(0x4D570210u, aIndex,
		(TUint32)iDrawer.iMmModel->NumberOfItems());
	Cancel();
	HtcleoMmwLog(0x4D570211u, iStatus.Int(), IsActive() ? 1u : 0u);
	iIndexToProcess = aIndex;
	SetActive();
	HtcleoMmwLog(0x4D570212u, iStatus.Int(), IsActive() ? 1u : 0u);
	TRequestStatus* status = &iStatus;
	User::RequestComplete( status, KErrNone );
	HtcleoMmwLog(0x4D570213u, iStatus.Int(), IsActive() ? 1u : 0u);
	}'''


NEW = r'''void CMmPostEvaluationProcessor::StartAt( TInt aIndex )
	{
	// HTCLEO_MMWIDGETS_POSTPROCESS_BOUNDS_GUARD_V1
	const TInt htcleoItemCount = iDrawer.iMmModel->NumberOfItems();
	HtcleoMmwLog(0x4D570210u, aIndex, (TUint32)htcleoItemCount);
	Cancel();
	HtcleoMmwLog(0x4D570211u, iStatus.Int(), IsActive() ? 1u : 0u);
	iIndexToProcess = aIndex;
	if (aIndex < 0 || aIndex >= htcleoItemCount)
		{
		// Nothing exists below the current visible range.  Do not leave a
		// completed low-priority AO in the scheduler with an invalid index.
		HtcleoMmwLog(0x4D570216u, KErrArgument,
			(((TUint32)aIndex & 0xFFFFu) << 16)
			| ((TUint32)htcleoItemCount & 0xFFFFu));
		return;
		}
	SetActive();
	HtcleoMmwLog(0x4D570212u, iStatus.Int(), IsActive() ? 1u : 0u);
	TRequestStatus* status = &iStatus;
	User::RequestComplete( status, KErrNone );
	HtcleoMmwLog(0x4D570213u, iStatus.Int(), IsActive() ? 1u : 0u);
	}'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if TRACE_MARKER not in text:
        raise SystemExit("postprocessor AO trace prerequisite is missing")
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"postprocessor bounds anchor: expected one, found {count}")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "markers": text.count(MARKER) == 1 and text.count(TRACE_MARKER) == 1,
        "real bound": (
            text.count("aIndex < 0 || aIndex >= htcleoItemCount") == 1
            and text.count("iDrawer.iMmModel->NumberOfItems()") >= 2
        ),
        "skip stage": text.count("0x4D570216u") == 1,
        "normal AO path retained": (
            text.count("SetActive();") == 2
            and text.count("User::RequestComplete( status, KErrNone );") == 2
        ),
        "real post work retained": text.count(
            "iDrawer.SetupSubCellsL( EFalse, iIndexToProcess );"
        ) == 1,
        "no fake item timer or draw": all(
            token not in NEW
            for token in ("AppendL", "RTimer", "DrawNow", "MakeVisible")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MMWidgets postprocessor bounds guard failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/mmwidgets/src/"
        "mmpostevaluationprocessor.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing postprocessor source: {path}")
    text = install(path.read_text(encoding="latin-1"))
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MMWIDGETS_POSTPROCESS_POLICY="
        "queue-only-real-index-range-stage-216"
    )


if __name__ == "__main__":
    main()
