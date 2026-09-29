#!/usr/bin/env python3
"""Retire synchronous AKNCAP.TXT I/O after AknCap becomes critical.

Iteration 504 writes E101 but never produces the immediately following E102
record.  Same-package disassembly excludes OFN between those points and
localises the block to completion of the E101 logger or entry/I/O of the E102
logger.  Keep the useful pre-critical trace, but turn every later
``HtcleoAknCapLog`` call into a no-op.  This changes diagnostic I/O only; AknCap
construction, ready-property publication and rendezvous remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_POSTCRITICAL_FILELOG_RETIREMENT_V1"
POLICY_TAG = "0x4E4F494Fu"  # "NOIO"


def install(source: str) -> str:
    old_logger = """static void HtcleoAknCapLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
"""
    new_logger = f"""// {MARKER}
static TBool gHtcleoAknCapFileLogRetired = EFalse;

static void HtcleoAknCapLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {{
    if (gHtcleoAknCapFileLogRetired)
        {{
        return;
        }}

    RFs fs;
"""
    if source.count(old_logger) != 1:
        raise SystemExit(
            "AKNCAP logger anchor: expected one, found "
            f"{source.count(old_logger)}"
        )
    source = source.replace(old_logger, new_logger, 1)

    old_tail = """    fs.Close();
    }
#else
"""
    new_tail = """    fs.Close();
    if (aStage == 0x0000E100u)
        {
        // All following calls run after SetCritical; avoid synchronous FAT I/O.
        gHtcleoAknCapFileLogRetired = ETrue;
        }
    }
#else
"""
    if source.count(old_tail) != 1:
        raise SystemExit(
            "AKNCAP logger tail anchor: expected one, found "
            f"{source.count(old_tail)}"
        )
    source = source.replace(old_tail, new_tail, 1)

    old_e100 = "HtcleoAknCapLog(0x0000E100u, KErrNone, 0u);"
    new_e100 = f"HtcleoAknCapLog(0x0000E100u, KErrNone, {POLICY_TAG});"
    if source.count(old_e100) != 1:
        raise SystemExit(
            "E100 policy anchor: expected one, found "
            f"{source.count(old_e100)}"
        )
    return source.replace(old_e100, new_e100, 1)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "single retirement state": source.count(
            "static TBool gHtcleoAknCapFileLogRetired = EFalse;"
        )
        == 1,
        "single early-return guard": source.count(
            "if (gHtcleoAknCapFileLogRetired)"
        )
        == 1,
        "single E100 retirement boundary": source.count(
            "if (aStage == 0x0000E100u)"
        )
        == 1,
        "single NOIO evidence tag": source.count(
            f"HtcleoAknCapLog(0x0000E100u, KErrNone, {POLICY_TAG});"
        )
        == 1,
        "old E100 call removed": source.count(
            "HtcleoAknCapLog(0x0000E100u, KErrNone, 0u);"
        )
        == 0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "post-critical AKNCAP file-log retirement verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src/AknCapServerEntry.cpp"
    )
    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAPSERVER_POSTCRITICAL_FILELOG=retired "
        "boundary=E100 evidence=NOIO startup-behavior=unchanged"
    )


if __name__ == "__main__":
    main()
