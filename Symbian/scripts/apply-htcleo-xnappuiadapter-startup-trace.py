#!/usr/bin/env python3
"""Trace the HomeScreen Xn AppUi adapter constructor without changing flow."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XNAPPUIADAPTER_STARTUP_TRACE_V1"
HOME_SID = "0x102750f0u"
MXML_MARKER = "HTCLEO_XN_MXMLATTRIBUTES_FORWARD_DECL_V1"


MXML_FORWARD_HEADER = r'''#ifndef HTCLEO_XN_MXMLATTRIBUTES_FORWARD_H
#define HTCLEO_XN_MXMLATTRIBUTES_FORWARD_H

// HTCLEO_XN_MXMLATTRIBUTES_FORWARD_DECL_V1
// SVGListener uses this omitted private parser type only by reference.
class MXMLAttributes;

#endif
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
// HTCLEO_XNAPPUIADAPTER_STARTUP_TRACE_V1
static void HtcleoXnAdapterLog(TUint32 aStage, TInt aResult,
                               TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x102750f0u)
        return;
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;
    _LIT(KDir, "C:\\Symbian3\\");
    _LIT(KPath, "C:\\Symbian3\\HSXML.TXT");
    (void)fs.MkDirAll(KDir);
    RFile file;
    r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
    TInt position = 0;
    if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);
    if (r == KErrNone && position <= (1048576 - 128))
        {
        _LIT8(KPrefix, "HTCLEO_HXA  ");
        TBuf8<128> record;
        record.Append(KPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
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
        '#include "debug.h"\n',
        '#include "debug.h"\n#include <f32file.h>\n',
        "filesystem include",
    )
    source = replace_once(
        source,
        '_LIT8( KActivateDefaultView, "activatedefault" );\n',
        HELPER + '_LIT8( KActivateDefaultView, "activatedefault" );\n',
        "trace helper",
    )
    source = replace_once(
        source,
        "EXPORT_C void CXnAppUiAdapter::ConstructL()\n"
        "    {\n"
        '    __TICK( "CXnAppUiAdapter::ConstructL" );',
        "EXPORT_C void CXnAppUiAdapter::ConstructL()\n"
        "    {\n"
        "    HtcleoXnAdapterLog(0x48581000u, KErrNone, (TUint32)this);\n"
        '    __TICK( "CXnAppUiAdapter::ConstructL" );',
        "ConstructL entry",
    )
    source = replace_once(
        source,
        "    EnableLocalScreenClearer( EFalse );\n"
        "    \n"
        "    CAknViewAppUi::BaseConstructL( EAknEnableSkin | EAknEnableMSK | EAknSingleClickCompatible );",
        "    EnableLocalScreenClearer( EFalse );\n"
        "    HtcleoXnAdapterLog(0x48581001u, KErrNone, 0u);\n"
        "    \n"
        "    HtcleoXnAdapterLog(0x48581002u, KErrNone, 0u);\n"
        "    CAknViewAppUi::BaseConstructL( EAknEnableSkin | EAknEnableMSK | EAknSingleClickCompatible );\n"
        "    HtcleoXnAdapterLog(0x48581003u, KErrNone, 0u);",
        "base construction",
    )
    source = replace_once(
        source,
        "    CAknToolbar* toolbar( CurrentFixedToolbar() );\n\n"
        "    if ( toolbar )",
        "    CAknToolbar* toolbar( CurrentFixedToolbar() );\n"
        "    HtcleoXnAdapterLog(0x48581004u, KErrNone, (TUint32)toolbar);\n\n"
        "    if ( toolbar )",
        "toolbar lookup",
    )
    source = replace_once(
        source,
        "        toolbar->SetToolbarVisibility( EFalse );\n\n"
        "        toolbar->DisableToolbarL( ETrue );",
        "        HtcleoXnAdapterLog(0x48581005u, KErrNone, 0u);\n"
        "        toolbar->SetToolbarVisibility( EFalse );\n"
        "        HtcleoXnAdapterLog(0x48581006u, KErrNone, 0u);\n\n"
        "        HtcleoXnAdapterLog(0x48581007u, KErrNone, 0u);\n"
        "        toolbar->DisableToolbarL( ETrue );\n"
        "        HtcleoXnAdapterLog(0x48581008u, KErrNone, 0u);",
        "toolbar operations",
    )
    source = replace_once(
        source,
        "    CEikStatusPane* sp( StatusPane() );\n"
        "    if ( sp )",
        "    CEikStatusPane* sp( StatusPane() );\n"
        "    HtcleoXnAdapterLog(0x48581009u, KErrNone, (TUint32)sp);\n"
        "    if ( sp )",
        "status pane lookup",
    )
    source = replace_once(
        source,
        "        sp->EnableTransparent( ETrue );",
        "        HtcleoXnAdapterLog(0x4858100Au, KErrNone, 0u);\n"
        "        sp->EnableTransparent( ETrue );\n"
        "        HtcleoXnAdapterLog(0x4858100Bu, KErrNone, 0u);",
        "status pane operation",
    )
    source = replace_once(
        source,
        "    iImpl = CXnAppUiAdapterImpl::NewL( iApplicationUid, *this );\n"
        "    iImpl->ConstructL();",
        "    HtcleoXnAdapterLog(0x4858100Cu, KErrNone, 0u);\n"
        "    iImpl = CXnAppUiAdapterImpl::NewL( iApplicationUid, *this );\n"
        "    HtcleoXnAdapterLog(0x4858100Du, KErrNone, (TUint32)iImpl);\n"
        "    HtcleoXnAdapterLog(0x4858100Eu, KErrNone, 0u);\n"
        "    iImpl->ConstructL();\n"
        "    HtcleoXnAdapterLog(0x4858100Fu, KErrNone, 0u);",
        "implementation construction",
    )
    source = replace_once(
        source,
        '    __TIME_ENDMARK( "CXnAppUiAdapter::ConstructL, done", time );\n',
        "    HtcleoXnAdapterLog(0x48581010u, KErrNone, 0u);\n"
        '    __TIME_ENDMARK( "CXnAppUiAdapter::ConstructL, done", time );\n',
        "ConstructL exit",
    )
    return source


def verify(source: str, mxml: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "SID gate": source.count(
            f"RProcess().SecureId().iId != {HOME_SID}"
        ) == 1,
        "path/capacity/prefix": (
            source.count(r"C:\\Symbian3\\HSXML.TXT") == 1
            and source.count("1048576 - 128") == 1
            and source.count('"HTCLEO_HXA  "') == 1
        ),
        "all stages": all(
            source.count(f"0x485810{stage:02X}u") == 1
            for stage in range(0x11)
        ),
        "stock calls retained": all(
            source.count(call) == 1
            for call in (
                "EnableLocalScreenClearer( EFalse );",
                "CAknViewAppUi::BaseConstructL( EAknEnableSkin | EAknEnableMSK | EAknSingleClickCompatible );",
                "toolbar->SetToolbarVisibility( EFalse );",
                "toolbar->DisableToolbarL( ETrue );",
                "sp->EnableTransparent( ETrue );",
                "iImpl = CXnAppUiAdapterImpl::NewL( iApplicationUid, *this );",
                "iImpl->ConstructL();",
            )
        ),
        "single writer": source.count("file.Write(record)") == 1,
        "MXML forward declaration": (
            mxml.count(MXML_MARKER) == 1
            and mxml.count("class MXMLAttributes;") == 1
        ),
        "no behavior change": (
            "User::After" not in HELPER
            and "RTimer" not in HELPER
            and "HalFunction" not in HELPER
            and "TRAP" not in HELPER
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
        / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src/xnappuiadapter.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    mxml_path = source_path.parent.parent / "inc/MXMLAttributes.h"
    mxml_path.write_text(MXML_FORWARD_HEADER, encoding="latin-1")
    mxml = mxml_path.read_text(encoding="latin-1")
    verify(source, mxml)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_XNAPPUIADAPTER_STARTUP_TRACE="
        "HSXML-1m-48581000-48581010-behavior-neutral"
    )


if __name__ == "__main__":
    main()
