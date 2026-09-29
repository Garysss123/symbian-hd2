#!/usr/bin/env python3
"""Record the exact active object selected after each MatrixMenu scheduler wake."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_CONE_READY_AO_IDENTITY_TRACE_V1"
PUMP_MARKER = "HTCLEO_CONE_EVENT_PUMP_DURABLE_TRACE_V1"


HELPER = r'''// HTCLEO_CONE_READY_AO_IDENTITY_TRACE_V1
// Diagnostic-only translation unit: expose the scheduler queue layout in this
// file so the derived CONE scheduler can identify, without dispatching, the
// same first ready AO that euser will select immediately after Wait returns.
#define private public
#include <e32base.h>
#undef private

void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail);

void HtcleoTraceReadyAo(CActiveScheduler* aScheduler)
    {
    if (RProcess().SecureId().iId != 0x101F4CD2u || !aScheduler)
        {
        return;
        }

    TDblQueIter<CActive> iterator(aScheduler->iActiveQ);
    TUint32 position = 0;
    for (CActive* active = iterator++; active; active = iterator++, ++position)
        {
        if (active->IsActive() && active->iStatus != KRequestPending)
            {
            const TUint32 vtable =
                *reinterpret_cast<const TUint32*>(active);
            HtcleoConeLog(0x414F0100u, active->Priority(),
                (TUint32)active);
            HtcleoConeLog(0x414F0101u, active->iStatus.Int(), vtable);
            HtcleoConeLog(0x414F0102u, KErrNone, position);
            return;
            }
        }
    HtcleoConeLog(0x414F010Fu, KErrNotFound, position);
    }
'''


WAIT_OLD = r'''	CBaActiveScheduler::WaitForAnyRequest();
	HtcleoConeLog(0x434F0103u, KErrNone, 0u);'''


WAIT_NEW = r'''	CBaActiveScheduler::WaitForAnyRequest();
	HtcleoTraceReadyAo(this);
	HtcleoConeLog(0x434F0103u, KErrNone, 0u);'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_main(text: str) -> str:
    if "HtcleoTraceReadyAo(this);" in text:
        return text
    if PUMP_MARKER not in text:
        raise SystemExit("CONE event-pump trace prerequisite is missing")
    text = replace_once(
        text,
        "// Class CCoeScheduler\n//\n",
        "// Class CCoeScheduler\n//\n\n"
        "void HtcleoTraceReadyAo(CActiveScheduler* aScheduler);\n",
        "ready AO declaration",
    )
    return replace_once(text, WAIT_OLD, WAIT_NEW, "post-wait AO scan")


def install_mmp(text: str) -> str:
    if "source  htcleoschedulertrace.cpp" in text:
        return text
    return replace_once(
        text,
        "source  COEFEP.CPP    COEHELP.CPP  COEMAIN.CPP\n",
        "source  COEFEP.CPP    COEHELP.CPP  COEMAIN.CPP\n"
        "source  htcleoschedulertrace.cpp\n",
        "scheduler trace source",
    )


def verify(main: str, helper: str, mmp: str) -> None:
    checks = {
        "marker": helper.count(MARKER) == 1,
        "queue visibility local": (
            helper.count("#define private public") == 1
            and helper.count("#undef private") == 1
            and helper.count("aScheduler->iActiveQ") == 1
        ),
        "scheduler-equivalent selection": (
            helper.count("active->IsActive()") == 1
            and helper.count("active->iStatus != KRequestPending") == 1
        ),
        "identity fields": (
            helper.count("active->Priority()") == 1
            and helper.count("active->iStatus.Int()") == 1
            and helper.count("reinterpret_cast<const TUint32*>(active)") == 1
        ),
        "stages": all(
            helper.count(f"0x{stage:08X}u") == 1
            for stage in (0x414F0100, 0x414F0101, 0x414F0102, 0x414F010F)
        ),
        "post-wait call": main.count("HtcleoTraceReadyAo(this);") == 1,
        "pump retained": (
            main.count(PUMP_MARKER) == 1
            and main.count("CBaActiveScheduler::WaitForAnyRequest();") == 1
            and main.count("0x434F0103u") == 1
        ),
        "build source": mmp.count("source  htcleoschedulertrace.cpp") == 1,
        "no dispatch or behavior change": all(
            token not in helper
            for token in ("RunL()", "RunIfReady", "SetActive", "RequestComplete")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("CONE ready-AO identity trace failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    cone = args.root / "sf/mw/classicui/lafagnosticuifoundation/cone"
    main_path = cone / "src/COEMAIN.CPP"
    helper_path = cone / "src/htcleoschedulertrace.cpp"
    mmp_path = args.root / "sf/incubator/stemkit/breakdeps/CONE.MMP"
    if not main_path.is_file() or not mmp_path.is_file():
        raise SystemExit("missing CONE scheduler inputs")
    main_text = install_main(main_path.read_text(encoding="latin-1"))
    mmp_text = install_mmp(mmp_path.read_text(encoding="latin-1"))
    helper_text = HELPER
    verify(main_text, helper_text, mmp_text)
    main_path.write_text(main_text, encoding="latin-1")
    helper_path.write_text(helper_text, encoding="latin-1")
    mmp_path.write_text(mmp_text, encoding="latin-1")
    print(
        "HTCLEO_CONE_READY_AO_TRACE="
        "object-vtable-priority-status-ao100-aof"
    )


if __name__ == "__main__":
    main()
