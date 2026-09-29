#!/usr/bin/env python3
"""Route the existing EikEnv construction checkpoints to HomeScreen's log.

The E300-E36A checkpoints already exist for the proven MatrixMenu/AknCap
bring-up paths.  This transform only adds a HomeScreen SID-gated, fail-open
writer to the existing one-MiB HSXML.TXT.  It changes no branch, return value,
timing primitive, or application construction call.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE_V1"
HOME_SID = "0x102750f0u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
// HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE_V1
// Reuse the existing E300-E36A boundaries without changing control flow.
static void HtcleoEikCoreHomeScreenTrace(TUint32 aStage, TInt aResult)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;

    _LIT(KHtcleoEikCoreHomeDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikCoreHomePath, "C:\\Symbian3\\HSXML.TXT");
    (void)fs.MkDirAll(KHtcleoEikCoreHomeDir);
    RFile file;
    r = file.Open(fs, KHtcleoEikCoreHomePath,
        EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        r = file.Replace(fs, KHtcleoEikCoreHomePath,
            EFileWrite | EFileShareAny);
    TInt position = 0;
    if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);
    if (r == KErrNone && position <= (1048576 - 128))
        {
        _LIT8(KHtcleoEikCoreHomePrefix, "HTCLEO_HCE  ");
        TBuf8<128> record;
        record.Append(KHtcleoEikCoreHomePrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
        record.Append('\n');
        (void)file.Write(record);
        }
    file.Close();
    fs.Close();
    }

'''


def install(source: str) -> str:
    source = replace_once(
        source,
        "const TUint32 KHtcleoMatrixMenuSid = 0x101f4cd2u;\n",
        "const TUint32 KHtcleoMatrixMenuSid = 0x101f4cd2u;\n"
        f"const TUint32 KHtcleoHomeScreenSid = {HOME_SID};\n",
        "HomeScreen SID",
    )
    source = replace_once(
        source,
        "static void HtcleoEikCorePreFactoryTrace(TUint32 aStage, TInt aResult)\n",
        HELPER
        + "static void HtcleoEikCorePreFactoryTrace(TUint32 aStage, TInt aResult)\n",
        "trace dispatcher",
    )
    source = replace_once(
        source,
        "    else if (sid == KHtcleoMatrixMenuSid)\n"
        "        {\n"
        "        HtcleoEikCoreMatrixMenuTrace(aStage, aResult);\n"
        "        }\n",
        "    else if (sid == KHtcleoMatrixMenuSid)\n"
        "        {\n"
        "        HtcleoEikCoreMatrixMenuTrace(aStage, aResult);\n"
        "        }\n"
        "    else if (sid == KHtcleoHomeScreenSid)\n"
        "        {\n"
        "        HtcleoEikCoreHomeScreenTrace(aStage, aResult);\n"
        "        }\n",
        "HomeScreen dispatch",
    )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "SID constant": source.count(
            f"KHtcleoHomeScreenSid = {HOME_SID}"
        ) == 1,
        "SID dispatch": source.count(
            "sid == KHtcleoHomeScreenSid"
        ) == 1,
        "helper definition and call": source.count(
            "HtcleoEikCoreHomeScreenTrace("
        ) == 2,
        "shared one MiB log": (
            source.count("C:\\\\Symbian3\\\\HSXML.TXT") == 1
            and source.count("1048576 - 128") == 1
            and source.count('"HTCLEO_HCE  "') == 1
        ),
        "factory path retained": source.count(
            "iProcess->AddNewDocumentL(aApplicationFactory)"
        ) == 1,
        "no behavior change": (
            "User::After" not in HELPER
            and "HalFunction" not in HELPER
            and "LeaveIfError" not in HELPER
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
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_HOMESCREEN_CONSTRUCTAPP_TRACE="
        "HSXML-1m-sid-102750f0-existing-E300-E36A"
    )


if __name__ == "__main__":
    main()
