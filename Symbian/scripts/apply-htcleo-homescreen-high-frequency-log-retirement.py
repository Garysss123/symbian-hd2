#!/usr/bin/env python3
"""Retire proven high-frequency HomeScreen Xn and CONE FAT traces.

Gate 16 is now represented by the low-rate HSLOG ALIV heartbeat.  Keep only a
few construction/focus milestones here so the UI thread no longer performs a
full RFs open/seek/write/close cycle for every Xn node or scheduler event.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT_V1"
XN_PREREQUISITE = "HTCLEO_XN_LOADUI_TRACE_V1"
CONE_PREREQUISITE = "HTCLEO_CONE_HOMESCREEN_AO_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


XN_GATE_OLD = '''static void HtcleoXnLoadUiLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x102750f0u)
        return;'''


XN_GATE_NEW = '''static void HtcleoXnLoadUiLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT_V1
    // Keep only LoadUi complete, per-view complete and view Occupied.
    const TUint32 htcleoLoadStage = aStage & 0xFFu;
    if (htcleoLoadStage != 0x0Cu &&
        htcleoLoadStage != 0x67u &&
        htcleoLoadStage != 0x98u)
        return;
    if (RProcess().SecureId().iId != 0x102750f0u)
        return;'''


CONE_OLD = '''\tif (htcleoSid == 0x102750F0u)
\t\t{
\t\tHtcleoHomeConeLog(aStage, aResult, aDetail);
\t\treturn;
\t\t}'''


CONE_NEW = '''\tif (htcleoSid == 0x102750F0u)
\t\t{
\t\t// HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT_V1
\t\t// HSLOG owns the persistent heartbeat.  Retain only the proven
\t\t// foreground-case and outer event-handler completion milestones.
\t\tconst TUint32 htcleoConeStage = aStage & 0xFFFFu;
\t\tif (htcleoConeStage == 0x050Fu || htcleoConeStage == 0x0207u)
\t\t\t{
\t\t\tHtcleoHomeConeLog(aStage, aResult, aDetail);
\t\t\t}
\t\treturn;
\t\t}'''


def patch_xn(text: str) -> str:
    if text.count(XN_PREREQUISITE) != 1:
        raise SystemExit("Xn LoadUi trace prerequisite is missing")
    if MARKER in text:
        return text
    return replace_once(text, XN_GATE_OLD, XN_GATE_NEW, "Xn logger gate")


def patch_cone(text: str) -> str:
    if text.count(CONE_PREREQUISITE) != 1:
        raise SystemExit("HomeScreen CONE trace prerequisite is missing")
    if MARKER in text:
        return text
    return replace_once(text, CONE_OLD, CONE_NEW, "CONE logger gate")


def verify(xn_sources: list[str], cone: str) -> None:
    checks = {
        "five Xn gates": sum(source.count(MARKER) for source in xn_sources) == 5,
        "Xn milestone allowlist": all(
            source.count("htcleoLoadStage != 0x0Cu") == 1
            and source.count("htcleoLoadStage != 0x67u") == 1
            and source.count("htcleoLoadStage != 0x98u") == 1
            for source in xn_sources
        ),
        "Xn log implementations retained": all(
            source.count("HtcleoXnLoadUiLog(") >= 2
            and source.count(r"C:\\Symbian3\\HSXML.TXT") == 1
            for source in xn_sources
        ),
        "one CONE gate": cone.count(MARKER) == 1,
        "CONE milestones": (
            cone.count("htcleoConeStage == 0x050Fu") == 1
            and cone.count("htcleoConeStage == 0x0207u") == 1
        ),
        "CONE logger retained": (
            cone.count("HtcleoHomeConeLog(aStage, aResult, aDetail);") == 1
            and cone.count(r"C:\\Symbian3\\HSCONE.TXT") == 1
        ),
        "no control-flow timing changes": all(
            token not in XN_GATE_NEW + CONE_NEW
            for token in ("User::After", "RTimer", "RequestComplete", "TRAP")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen log-retirement audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    xn_dir = args.root / (
        "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src"
    )
    xn_names = (
        "xnviewmanager.cpp",
        "xnrootdata.cpp",
        "xncomposer.cpp",
        "xnodtparser.cpp",
        "xnviewdata.cpp",
    )
    xn_paths = [xn_dir / name for name in xn_names]
    cone_path = args.root / (
        "sf/mw/classicui/lafagnosticuifoundation/cone/src/COEMAIN.CPP"
    )
    for path in [*xn_paths, cone_path]:
        if not path.is_file():
            raise SystemExit(f"missing source: {path}")
    xn_sources = [patch_xn(path.read_text(encoding="utf-8")) for path in xn_paths]
    cone = patch_cone(cone_path.read_text(encoding="latin-1"))
    verify(xn_sources, cone)
    for path, source in zip(xn_paths, xn_sources):
        path.write_text(source, encoding="utf-8")
    cone_path.write_text(cone, encoding="latin-1")
    print(
        "HTCLEO_HOMESCREEN_HIGH_FREQUENCY_LOG_RETIREMENT="
        "HLD-0c-67-98-only-HSCONE-050f-0207-only-HSLOG-ALIV-retained"
    )


if __name__ == "__main__":
    main()
