#!/usr/bin/env python3
"""Trace HomeScreen SGC construction and reuse the proven local-layout path.

Iteration 679 proves all three HomeScreen children leave in
CAknSgcClient::CreateL, after CAknEnv A00B and before A00C.  Route the existing
A100-A133 checkpoints to the shared one-MiB HSXML log for HomeScreen.  Extend
the MatrixMenu-only AknCap connection fail-open to HomeScreen for only
KErrNotFound/KErrServerTerminated; retain the real null handle and stock local
packed-layout construction.  Every other SID and error remains unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "// HTCLEO_AKNSGC_MATRIXMENU_DURABLE_LOG_V1\n"
        "static void HtcleoAknSgcMenuLog(\n",
        "// HTCLEO_AKNSGC_MATRIXMENU_DURABLE_LOG_V1\n"
        "// HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN_V1\n"
        "static void HtcleoAknSgcMenuLog(\n",
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
        '    _LIT(KHtcleoAknSgcMenuPath, "C:\\\\Symbian3\\\\MENULOG.TXT");\n',
        '    _LIT(KHtcleoAknSgcMenuPath, "C:\\\\Symbian3\\\\MENULOG.TXT");\n'
        '    _LIT(KHtcleoAknSgcHomePath, "C:\\\\Symbian3\\\\HSXML.TXT");\n',
        "HomeScreen log path",
    )
    source = replace_once(
        source,
        "    r = file.Open(fs, KHtcleoAknSgcMenuPath, EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        r = file.Replace(fs, KHtcleoAknSgcMenuPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "        }\n",
        "    if (htcleoHome)\n"
        "        r = file.Open(fs, KHtcleoAknSgcHomePath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    else\n"
        "        r = file.Open(fs, KHtcleoAknSgcMenuPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "    if (r == KErrNotFound || r == KErrPathNotFound)\n"
        "        {\n"
        "        if (htcleoHome)\n"
        "            r = file.Replace(fs, KHtcleoAknSgcHomePath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        else\n"
        "            r = file.Replace(fs, KHtcleoAknSgcMenuPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "        }\n",
        "HomeScreen file selection",
    )
    source = replace_once(
        source,
        "    if (r == KErrNone && position <= ((256 * 64) - 64))\n"
        "        {\n"
        '        _LIT8(KHtcleoAknSgcMenuPrefix, "HTCLEO_MENU ");\n'
        "        TBuf8<96> record;\n"
        "        record.Append(KHtcleoAknSgcMenuPrefix);\n",
        "    const TInt htcleoLimit = htcleoHome\n"
        "        ? (1048576 - 128) : ((256 * 64) - 64);\n"
        "    if (r == KErrNone && position <= htcleoLimit)\n"
        "        {\n"
        '        _LIT8(KHtcleoAknSgcMenuPrefix, "HTCLEO_MENU ");\n'
        '        _LIT8(KHtcleoAknSgcHomePrefix, "HTCLEO_HSG  ");\n'
        "        TBuf8<128> record;\n"
        "        if (htcleoHome)\n"
        "            record.Append(KHtcleoAknSgcHomePrefix);\n"
        "        else\n"
        "            record.Append(KHtcleoAknSgcMenuPrefix);\n",
        "HomeScreen record selection",
    )
    source = replace_once(
        source,
        "\tconst TBool htcleoMatrixMenuAknCapFailOpen =\n"
        "\t\t(RProcess().SecureId().iId == 0x101f4cd2u &&\n"
        "\t\t(aknServerError == KErrNotFound ||\n"
        "\t\t aknServerError == KErrServerTerminated));\n",
        "\tconst TBool htcleoMatrixMenuAknCapFailOpen =\n"
        "\t\t((RProcess().SecureId().iId == 0x101f4cd2u ||\n"
        "\t\t  RProcess().SecureId().iId == 0x102750f0u) &&\n"
        "\t\t (aknServerError == KErrNotFound ||\n"
        "\t\t  aknServerError == KErrServerTerminated));\n",
        "HomeScreen local-layout fail-open",
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
            and source.count('"HTCLEO_HSG  "') == 1
            and source.count("1048576 - 128") == 1
        ),
        "both fail-open SIDs": (
            source.count(
                "RProcess().SecureId().iId == 0x101f4cd2u ||"
            ) == 1
            and source.count(
                "RProcess().SecureId().iId == 0x102750f0u) &&"
            ) == 1
        ),
        "narrow errors": (
            source.count("aknServerError == KErrNotFound") == 1
            and source.count(
                "aknServerError == KErrServerTerminated"
            ) == 1
        ),
        "real null-handle path": (
            source.count("User::LeaveIfError(aknServerError);") == 1
            and source.count(
                "packedBuf = iLayoutConfig->CreatePackedBufL();"
            ) == 1
            and "iAknSrv.SetHandle" not in source
        ),
        "one writer": source.count("file.Write(record)") == 1,
        "no timer display or fake handle": (
            "User::After" not in source
            and "HalFunction" not in source
            and "RTimer" not in source
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
        args.root / "sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNSGC_HOMESCREEN_TRACE_AKNCAP_FAIL_OPEN="
        "HSXML-1m-A100-A133-real-null-handle-local-layout"
    )


if __name__ == "__main__":
    main()
