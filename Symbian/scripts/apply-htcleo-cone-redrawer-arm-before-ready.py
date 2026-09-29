#!/usr/bin/env python3
"""Arm MatrixMenu's CCoeRedrawer before asking WServ for the next redraw.

Hardware 592 attributes the final root-white frame to scheduler entry.  CONE's
redraw AO processes that first frame, then calls RedrawReady before SetActive.
When another redraw is already queued, this QSD8K port can complete the status
synchronously and lose it before the AO is armed.  Use the conventional
pending -> SetActive -> request order only in the MatrixMenu process.  Other
applications retain stock order and all redraw handlers/content stay real.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_CONE_MATRIXMENU_REDRAW_ARM_BEFORE_READY_V1"

OLD = r'''void CCoeRedrawer::Queue()
	{
	iWsSession.RedrawReady(&iStatus);
	SetActive();
	}'''

NEW = r'''void CCoeRedrawer::Queue()
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/lafagnosticuifoundation/cone/src/COEPRIV.CPP"
    )
    mmp_path = args.root / "sf/incubator/stemkit/breakdeps/CONE.MMP"
    coemain_path = (
        args.root
        / "sf/mw/classicui/lafagnosticuifoundation/cone/src/COEMAIN.CPP"
    )
    if not path.is_file():
        raise SystemExit(f"missing CONE redraw source: {path}")
    if not mmp_path.is_file():
        raise SystemExit(f"missing STEM CONE MMP: {mmp_path}")
    if not coemain_path.is_file():
        raise SystemExit(f"missing CONE main source: {coemain_path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise SystemExit(
                "CONE redraw queue: expected one stock block, "
                f"found {text.count(OLD)}"
            )
        text = text.replace(OLD, NEW, 1)

    marker_index = text.index(MARKER)
    block = text[marker_index : marker_index + 700]
    checks = {
        "single marker": text.count(MARKER) == 1,
        "MatrixMenu SID": block.count("0x101f4cd2u") == 1,
        "pending before active before request": (
            block.index("iStatus = KRequestPending;")
            < block.index("SetActive();")
            < block.index("iWsSession.RedrawReady(&iStatus);")
        ),
        "stock order retained": block.count(
            "iWsSession.RedrawReady(&iStatus);\n\t\tSetActive();"
        ) == 1,
        "one request each branch": block.count(
            "iWsSession.RedrawReady(&iStatus);"
        ) == 2,
        "real handler retained": text.count(
            "window->HandleRedrawEvent(redraw.Rect());"
        ) >= 1,
        "queue after get retained": text.count("Queue();") >= 1,
        "no timer wait fake draw": all(
            token not in NEW
            for token in (
                "User::After",
                "RTimer",
                "WaitForRequest",
                "DrawNow",
                "MakeVisible",
                "RequestComplete",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "CONE redraw arm verification failed: " + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")

    # Raptor treats MMP include/source paths as EPOC-rooted.  Normalize an
    # interrupted earlier attempt back to /sf/... so EPOCROOT is not doubled.
    mmp_text = mmp_path.read_text(encoding="latin-1")
    source_root = str(args.root).rstrip("/")
    mmp_replacements = {
        "userinclude\t\t"
        + source_root
        + "/sf/mw/classicui/lafagnosticuifoundation/cone/inc":
            "userinclude\t\t/sf/mw/classicui/lafagnosticuifoundation/cone/inc",
        "USERINCLUDE     "
        + source_root
        + "/sf/mw/classicui/lafagnosticuifoundation/cone/src":
            "USERINCLUDE     /sf/mw/classicui/lafagnosticuifoundation/cone/src",
    }
    for old, new in mmp_replacements.items():
        if old in mmp_text:
            mmp_text = mmp_text.replace(old, new, 1)
        elif new not in mmp_text:
            raise SystemExit(f"STEM CONE MMP path not recognized: {old}")
    if any(mmp_text.count(new) != 1 for new in mmp_replacements.values()):
        raise SystemExit("STEM CONE MMP EPOC-root path verification failed")
    # SOURCEPATH is EPOC-rooted by Raptor and must remain /sf/...; making it a
    # host absolute path causes Raptor to prepend EPOCROOT a second time.
    source_path = "SOURCEPATH\t/sf/mw/classicui/lafagnosticuifoundation/cone/src"
    doubled_source_path = (
        "SOURCEPATH\t"
        + source_root
        + "/sf/mw/classicui/lafagnosticuifoundation/cone/src"
    )
    if doubled_source_path in mmp_text:
        mmp_text = mmp_text.replace(doubled_source_path, source_path, 1)
    elif source_path not in mmp_text:
        raise SystemExit("STEM CONE MMP SOURCEPATH not recognized")
    if mmp_text.count(source_path) != 1:
        raise SystemExit("STEM CONE MMP SOURCEPATH verification failed")
    mmp_path.write_text(mmp_text, encoding="latin-1")

    # Windows-era source includes this one private header with lowercase text,
    # while the checked-in filename is uppercase.  Correct only the include
    # spelling; this has no target-code semantic effect.
    coemain_text = coemain_path.read_text(encoding="latin-1")
    if '#include "coever.h"' in coemain_text:
        coemain_text = coemain_text.replace(
            '#include "coever.h"', '#include "COEVER.H"', 1
        )
    if coemain_text.count('#include "COEVER.H"') != 1:
        raise SystemExit("CONE COEVER.H include-case verification failed")
    coemain_path.write_text(coemain_text, encoding="latin-1")
    print(
        "HTCLEO_CONE_REDRAW_QUEUE="
        "matrixmenu-pending-setactive-redrawready-other-apps-stock"
    )


if __name__ == "__main__":
    main()
