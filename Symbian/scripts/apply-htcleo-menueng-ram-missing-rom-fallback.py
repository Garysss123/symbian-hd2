#!/usr/bin/env python3
"""Use the real ROM menu tree when the writable RAM menu XML is absent.

The stock state machine intends to fall back from a missing C: menu cache to
the Z: ROM XML.  On HTC Leo the first CXCFW RAM LoadL terminates the menu server
before RunError can perform that fallback.  Check only for NotFound/PathNotFound
before invoking XCFW; existing RAM files still take the original path and the
real ROM XML, parser, ID manager and save-back flow remain mandatory.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MENUENG_RAM_MISSING_ROM_FALLBACK_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    return replace_once(
        text,
        """            iState = ELoadRamFile;
            HtcleoMenuEngLog(0x4D450310u, KErrNone, (TUint32)iState);
            LoadRamFileL();
            HtcleoMenuEngLog(0x4D450311u, KErrNone, (TUint32)iState);
            break;
""",
        """            iState = ELoadRamFile;
            HtcleoMenuEngLog(0x4D450310u, KErrNone, (TUint32)iState);
            // HTCLEO_MENUENG_RAM_MISSING_ROM_FALLBACK_V1
            TEntry htcleoRamEntry;
            const TInt htcleoRamResult =
                iFs.Entry(iRamFileName, htcleoRamEntry);
            HtcleoMenuEngLog(0x4D450520u, htcleoRamResult,
                (TUint32)iRamFileName.Length());
            if (htcleoRamResult == KErrNotFound ||
                htcleoRamResult == KErrPathNotFound)
                {
                // Match the stock error transition without entering the
                // broken first-boot RAM parser call.
                iObserver.EngineTreeReloaded();
                iState = ELoadRomFile;
                HtcleoMenuEngLog(0x4D450521u, htcleoRamResult,
                    0x524F4D46u);
                LoadRomFileL();
                HtcleoMenuEngLog(0x4D450522u, KErrNone,
                    (TUint32)iState);
                }
            else
                {
                // Existing caches and all non-missing errors retain stock
                // XCFW behavior.
                LoadRamFileL();
                HtcleoMenuEngLog(0x4D450311u, KErrNone,
                    (TUint32)iState);
                }
            break;
""",
        "initial RAM load decision",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "entry check": text.count("iFs.Entry(iRamFileName, htcleoRamEntry)") == 1,
        "not-found policy": text.count("htcleoRamResult == KErrNotFound") == 1,
        "path-not-found policy": text.count("htcleoRamResult == KErrPathNotFound") == 1,
        "real RAM load retained": text.count("LoadRamFileL();") == 1,
        "real ROM load retained": text.count("LoadRomFileL();") == 2,
        "real XCFW RAM load retained": text.count("iEngine->LoadL( *iTree, iRamFileName )") == 1,
        "real XCFW ROM load retained": text.count("iEngine->LoadL( *iTree, fname )") == 1,
        "fallback detail": text.count("0x524F4D46u") == 1,
        "no delay": "User::After" not in text,
        "no display probe": "HalFunction" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MenuEng RAM fallback verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/engsrc/menueng.cpp"
    )
    if not source_path.is_file():
        raise SystemExit("missing MenuContent engine source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MENUENG_RAM_FALLBACK=installed "
        "policy=missing-c-cache-to-real-rom stages=4D450520-4D450522"
    )


if __name__ == "__main__":
    main()
