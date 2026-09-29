#!/usr/bin/env python3
"""Route the existing Eikon BaseConstruct checkpoints to HomeScreen HSXML.

Iteration 682 proves all three HomeScreen children reach the Avkon B518
checkpoint immediately before CEikAppUi::BaseConstructL and never reach B519.
The Eikon path already exposes B600-B615 for EikSrv and MatrixMenu.  Add only
the HomeScreen diagnostic sink in the shared one-MiB HSXML file.  No result,
branch, timing, screen policy, window operation, or leave behavior changes.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "// HTCLEO_EIKAPPUI_BASECONSTRUCT_DURABLE_LOG_V1\n"
        "static void HtcleoEikAppUiBaseLog(",
        "// HTCLEO_EIKAPPUI_BASECONSTRUCT_DURABLE_LOG_V1\n"
        "// HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1\n"
        "static void HtcleoEikAppUiBaseLog(",
        "trace marker",
    )
    source = replace_once(
        source,
        "    if (htcleoEikBaseSid != 0x10003A4Au &&\n"
        "        htcleoEikBaseSid != 0x101F4CD2u)\n",
        "    const TBool htcleoEikBaseHome =\n"
        "        htcleoEikBaseSid == 0x102750F0u;\n"
        "    if (htcleoEikBaseSid != 0x10003A4Au &&\n"
        "        htcleoEikBaseSid != 0x101F4CD2u &&\n"
        "        !htcleoEikBaseHome)\n",
        "HomeScreen SID gate",
    )
    source = replace_once(
        source,
        '    _LIT(KHtcleoEikBaseLogPath, "C:\\\\Symbian3\\\\EIKBASE.TXT");\n',
        '    _LIT(KHtcleoEikBaseLogPath, "C:\\\\Symbian3\\\\EIKBASE.TXT");\n'
        '    _LIT(KHtcleoEikHomeLogPath, "C:\\\\Symbian3\\\\HSXML.TXT");\n',
        "HomeScreen path",
    )
    source = replace_once(
        source,
        "    r = file.Open(fs, KHtcleoEikBaseLogPath, EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        r = file.Replace(fs, KHtcleoEikBaseLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "        }\n",
        "    if (htcleoEikBaseHome)\n"
        "        r = file.Open(fs, KHtcleoEikHomeLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    else\n"
        "        r = file.Open(fs, KHtcleoEikBaseLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        if (htcleoEikBaseHome)\n"
        "            r = file.Replace(fs, KHtcleoEikHomeLogPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        else\n"
        "            r = file.Replace(fs, KHtcleoEikBaseLogPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        }\n",
        "HomeScreen file selection",
    )
    source = replace_once(
        source,
        "    if (r == KErrNone && position <= ((128 * 64) - 64))\n"
        "        {\n"
        '        _LIT8(KHtcleoEikBasePrefix, "HTCLEO_EIKBASE ");\n'
        "        TBuf8<96> record;\n"
        "        record.Append(KHtcleoEikBasePrefix);\n",
        "    const TInt htcleoEikBaseLimit = htcleoEikBaseHome\n"
        "        ? (1048576 - 128) : ((128 * 64) - 64);\n"
        "    if (r == KErrNone && position <= htcleoEikBaseLimit)\n"
        "        {\n"
        '        _LIT8(KHtcleoEikBasePrefix, "HTCLEO_EIKBASE ");\n'
        '        _LIT8(KHtcleoEikHomePrefix, "HTCLEO_HEB  ");\n'
        "        TBuf8<128> record;\n"
        "        if (htcleoEikBaseHome)\n"
        "            record.Append(KHtcleoEikHomePrefix);\n"
        "        else\n"
        "            record.Append(KHtcleoEikBasePrefix);\n",
        "HomeScreen record selection",
    )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "HomeScreen SID gate": (
            source.count("htcleoEikBaseSid == 0x102750F0u") == 1
            and source.count("!htcleoEikBaseHome") == 1
        ),
        "shared one-MiB HSXML": (
            source.count(r'C:\\Symbian3\\HSXML.TXT') == 1
            and source.count('"HTCLEO_HEB  "') == 1
            and source.count("1048576 - 128") == 1
        ),
        "all B600-B615 stages": all(
            source.count(f"0x0000{stage:04X}u") == 1
            for stage in range(0xB600, 0xB616)
        ),
        "single writer no flush": (
            source.count("file.Write(record)") == 1
            and "file.Flush();" not in source
        ),
        "behavior neutral": (
            "User::After" not in source
            and "HalFunction" not in source
            and "HtcleoEikHomeResult" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKAPPUI.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE="
        "HSXML-1m-B600-B615-behavior-neutral"
    )


if __name__ == "__main__":
    main()
