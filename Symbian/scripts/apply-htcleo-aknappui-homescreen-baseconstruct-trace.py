#!/usr/bin/env python3
"""Route the existing Avkon BaseConstruct checkpoints to HomeScreen HSXML.

Iteration 681 proves that all three HomeScreen children enter
CXnAppUiAdapter::ConstructL and stop after its pre-CAknViewAppUi::BaseConstructL
checkpoint.  The Avkon BaseConstruct path already has dense B500-B520
checkpoints used by MatrixMenu.  This transform only adds the HomeScreen SID
as a diagnostic sink, using the shared one-MiB HSXML log; it changes no result,
branch, timer, layout policy, window operation, or leave behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "// HTCLEO_AKNAPPUI_BASECONSTRUCT_DURABLE_LOG_V1\n"
        "void HtcleoAknAppUiBaseLog(",
        "// HTCLEO_AKNAPPUI_BASECONSTRUCT_DURABLE_LOG_V1\n"
        "// HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1\n"
        "void HtcleoAknAppUiBaseLog(",
        "trace marker",
    )
    source = replace_once(
        source,
        "    const TBool htcleoLogEikSrv = htcleoLogSid == 0x10003A4Au;\n"
        "    const TBool htcleoLogMatrixMenu = htcleoLogSid == 0x101F4CD2u;\n"
        "    if (!htcleoLogEikSrv && !htcleoLogMatrixMenu)\n",
        "    const TBool htcleoLogEikSrv = htcleoLogSid == 0x10003A4Au;\n"
        "    const TBool htcleoLogMatrixMenu = htcleoLogSid == 0x101F4CD2u;\n"
        "    const TBool htcleoLogHomeScreen = htcleoLogSid == 0x102750F0u;\n"
        "    if (!htcleoLogEikSrv && !htcleoLogMatrixMenu &&\n"
        "        !htcleoLogHomeScreen)\n",
        "HomeScreen SID gate",
    )
    source = replace_once(
        source,
        "    if (htcleoLogEikSrv &&\n"
        "        (aStage < 0x0000B51Cu || aStage > 0x0000B520u))\n"
        "        {\n"
        "        return;\n"
        "        }\n",
        "    if (htcleoLogEikSrv &&\n"
        "        (aStage < 0x0000B51Cu || aStage > 0x0000B520u))\n"
        "        {\n"
        "        return;\n"
        "        }\n"
        "    if (htcleoLogHomeScreen &&\n"
        "        (aStage < 0x0000B500u || aStage > 0x0000B520u))\n"
        "        {\n"
        "        return;\n"
        "        }\n",
        "HomeScreen stage bound",
    )
    source = replace_once(
        source,
        '    _LIT(KHtcleoAknBaseLogPath, "C:\\\\Symbian3\\\\AKNBASE.TXT");\n',
        '    _LIT(KHtcleoAknBaseLogPath, "C:\\\\Symbian3\\\\AKNBASE.TXT");\n'
        '    _LIT(KHtcleoAknHomeLogPath, "C:\\\\Symbian3\\\\HSXML.TXT");\n',
        "HomeScreen path",
    )
    source = replace_once(
        source,
        "    r = file.Open(fs, KHtcleoAknBaseLogPath, EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        r = file.Replace(fs, KHtcleoAknBaseLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "        }\n",
        "    if (htcleoLogHomeScreen)\n"
        "        r = file.Open(fs, KHtcleoAknHomeLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    else\n"
        "        r = file.Open(fs, KHtcleoAknBaseLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        if (htcleoLogHomeScreen)\n"
        "            r = file.Replace(fs, KHtcleoAknHomeLogPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        else\n"
        "            r = file.Replace(fs, KHtcleoAknBaseLogPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        }\n",
        "HomeScreen file selection",
    )
    source = replace_once(
        source,
        "    if (r == KErrNone && position < (128 * 64))\n"
        "        {\n"
        '        _LIT8(KHtcleoAknBasePrefix, "HTCLEO_AKNBASE ");\n'
        "        TBuf8<96> record;\n"
        "        record.Append(KHtcleoAknBasePrefix);\n",
        "    const TInt htcleoLogLimit = htcleoLogHomeScreen\n"
        "        ? (1048576 - 128) : (128 * 64);\n"
        "    if (r == KErrNone && position < htcleoLogLimit)\n"
        "        {\n"
        '        _LIT8(KHtcleoAknBasePrefix, "HTCLEO_AKNBASE ");\n'
        '        _LIT8(KHtcleoAknHomePrefix, "HTCLEO_HAB  ");\n'
        "        TBuf8<128> record;\n"
        "        if (htcleoLogHomeScreen)\n"
        "            record.Append(KHtcleoAknHomePrefix);\n"
        "        else\n"
        "            record.Append(KHtcleoAknBasePrefix);\n",
        "HomeScreen record selection",
    )
    return source


def verify(source: str) -> None:
    postcoe_trace = (
        "HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE_V1" in source
    )
    checks = {
        "marker": source.count(MARKER) == 1,
        "HomeScreen SID": (
            source.count("htcleoLogSid == 0x102750F0u") == 1
            and source.count("!htcleoLogHomeScreen") == 1
        ),
        "bounded B500-B520": (
            source.count("aStage >= 0x0000B500u") == 1
            and source.count("aStage <= 0x0000B520u") == 1
            if postcoe_trace
            else source.count("aStage < 0x0000B500u") == 1
            and source.count("aStage > 0x0000B520u") >= 2
        ),
        "shared one-MiB HSXML": (
            source.count(r'C:\\Symbian3\\HSXML.TXT') == 1
            and source.count('"HTCLEO_HAB  "') == 1
            and source.count("1048576 - 128") == 1
        ),
        "single writer": source.count("file.Write(record)") == 1,
        "behavior neutral": (
            "User::After" not in source
            and (
                "HalFunction" not in source
                or (
                    (
                        source.count("HTCLEO_AVKON_FOCUS_TOUCH_REARM_V1")
                        + source.count("HTCLEO_AVKON_POST_FOCUS_TOUCH_REARM_V2")
                    ) == 1
                    and source.count("UserSvr::HalFunction") == 3
                )
            )
            and "HtcleoAknHomeResult" not in source
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
        args.root / "sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE="
        "HSXML-1m-B500-B520-behavior-neutral"
    )


if __name__ == "__main__":
    main()
