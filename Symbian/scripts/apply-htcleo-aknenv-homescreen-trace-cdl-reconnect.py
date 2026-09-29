#!/usr/bin/env python3
"""Trace HomeScreen CAknEnv construction and reuse the proven CDL recovery.

Iteration 678 proves all three HomeScreen children leave between E409 and E40A,
inside CAknEnv::ConstructL.  Route its existing A000-A01E checkpoints to the
shared one-MiB HSXML file for HomeScreen.  The MatrixMenu-only one-shot CDL
reconnect is extended to HomeScreen, on the same KErrNotFound or
KErrServerTerminated results.  Every other SID and error retains stock flow.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "// HTCLEO_AKNENV_MATRIXMENU_DURABLE_LOG_V1\n"
        "static void HtcleoAknEnvMenuLog(\n",
        "// HTCLEO_AKNENV_MATRIXMENU_DURABLE_LOG_V1\n"
        "// HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT_V1\n"
        "static void HtcleoAknEnvMenuLog(\n",
        "trace marker",
    )
    source = replace_once(
        source,
        "    if (RProcess().SecureId().iId != 0x101f4cd2u)\n"
        "        {\n"
        "        return;\n"
        "        }\n",
        "    const TUint32 htcleoSid = RProcess().SecureId().iId;\n"
        "    const TBool htcleoHome = (htcleoSid == 0x102750f0u);\n"
        "    if (htcleoSid != 0x101f4cd2u && !htcleoHome)\n"
        "        {\n"
        "        return;\n"
        "        }\n",
        "HomeScreen SID gate",
    )
    source = replace_once(
        source,
        '    _LIT(KHtcleoAknEnvMenuPath, "C:\\\\Symbian3\\\\MENULOG.TXT");\n',
        '    _LIT(KHtcleoAknEnvMenuPath, "C:\\\\Symbian3\\\\MENULOG.TXT");\n'
        '    _LIT(KHtcleoAknEnvHomePath, "C:\\\\Symbian3\\\\HSXML.TXT");\n',
        "HomeScreen log path",
    )
    source = replace_once(
        source,
        "    r = file.Open(fs, KHtcleoAknEnvMenuPath, EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        r = file.Replace(fs, KHtcleoAknEnvMenuPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "        }\n",
        "    if (htcleoHome)\n"
        "        r = file.Open(fs, KHtcleoAknEnvHomePath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    else\n"
        "        r = file.Open(fs, KHtcleoAknEnvMenuPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        if (htcleoHome)\n"
        "            r = file.Replace(fs, KHtcleoAknEnvHomePath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        else\n"
        "            r = file.Replace(fs, KHtcleoAknEnvMenuPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        }\n",
        "HomeScreen file selection",
    )
    source = replace_once(
        source,
        "    if (r == KErrNone && position <= ((256 * 64) - 64))\n"
        "        {\n"
        '        _LIT8(KHtcleoAknEnvMenuPrefix, "HTCLEO_MENU ");\n'
        "        TBuf8<96> record;\n"
        "        record.Append(KHtcleoAknEnvMenuPrefix);\n",
        "    const TInt htcleoLimit = htcleoHome\n"
        "        ? (1048576 - 128) : ((256 * 64) - 64);\n"
        "    if (r == KErrNone && position <= htcleoLimit)\n"
        "        {\n"
        '        _LIT8(KHtcleoAknEnvMenuPrefix, "HTCLEO_MENU ");\n'
        '        _LIT8(KHtcleoAknEnvHomePrefix, "HTCLEO_HAK  ");\n'
        "        TBuf8<128> record;\n"
        "        if (htcleoHome)\n"
        "            record.Append(KHtcleoAknEnvHomePrefix);\n"
        "        else\n"
        "            record.Append(KHtcleoAknEnvMenuPrefix);\n",
        "HomeScreen record selection",
    )
    source = replace_once(
        source,
        "    const TBool htcleoMatrixMenuCdlRecovery =\n"
        "        RProcess().SecureId().iId == 0x101f4cd2u;\n",
        "    const TBool htcleoMatrixMenuCdlRecovery =\n"
        "        (RProcess().SecureId().iId == 0x101f4cd2u ||\n"
        "         RProcess().SecureId().iId == 0x102750f0u);\n",
        "HomeScreen CDL recovery",
    )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "HomeScreen SID gate": (
            source.count("htcleoSid == 0x102750f0u") == 1
            and source.count(
                "htcleoSid != 0x101f4cd2u && !htcleoHome"
            ) == 1
        ),
        "HomeScreen path and prefix": (
            source.count(r"C:\\Symbian3\\HSXML.TXT") == 1
            and source.count('"HTCLEO_HAK  "') == 1
            and source.count("1048576 - 128") == 1
        ),
        "one writer": source.count("file.Write(record)") == 1,
        "both recovery SIDs": (
            source.count(
                "RProcess().SecureId().iId == 0x101f4cd2u ||"
            ) == 1
            and source.count(
                "RProcess().SecureId().iId == 0x102750f0u);"
            ) == 1
        ),
        "narrow real recovery": (
            source.count("htcleoLayoutError == KErrNotFound") == 1
            and source.count(
                "htcleoLayoutError == KErrServerTerminated"
            ) == 1
            and source.count(
                "User::LeaveIfError(htcleoLayoutError);"
            ) == 1
        ),
        "single retry": (
            source.count("CdlEngine::CreateCdlEngineL()") == 2
            and source.count("SetLayoutRequirementsL();") == 2
        ),
        "no delay display or fake success": (
            "User::After" not in source
            and "HalFunction" not in source
            and "htcleoLayoutError = KErrNone; //" not in source
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
        args.root / "sf/mw/classicui/uifw/AvKon/src/aknenv.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNENV_HOMESCREEN_TRACE_CDL_RECONNECT="
        "HSXML-1m-A000-A01E-home-and-matrixmenu-notfound-or-terminated"
    )


if __name__ == "__main__":
    main()
