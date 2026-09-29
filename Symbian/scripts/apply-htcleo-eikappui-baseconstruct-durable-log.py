#!/usr/bin/env python3
"""Add an EikSrv-only durable trace inside CEikAppUi::BaseConstructL.

Iteration 477 reaches the Avkon B518 checkpoint immediately before this call
but never reaches B519.  This transform changes no branch or failure policy;
it brackets the short stock Eikon construction sequence in EIKBASE.TXT.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKAPPUI_BASECONSTRUCT_DURABLE_LOG_V1"
MACRO = "__HTCLEO_EIKAPPUI_BASECONSTRUCT_LOG__"
MATRIXMENU_FINAL_SCREEN_MARKER = (
    "HTCLEO_EIKAPPUI_MATRIXMENU_FINAL_SCREEN_CHANGE_DEFER_V1"
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''

#ifdef __HTCLEO_EIKAPPUI_BASECONSTRUCT_LOG__
#include <f32file.h>

// HTCLEO_EIKAPPUI_BASECONSTRUCT_DURABLE_LOG_V1
static void HtcleoEikAppUiBaseLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // eikcore.dll is shared; only the EikSrv process owns this stream.
    if (RProcess().SecureId().iId != 0x10003A4A)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikBaseLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikBaseLogPath, "C:\\Symbian3\\EIKBASE.TXT");
    r = fs.MkDirAll(KHtcleoEikBaseLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoEikBaseLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoEikBaseLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((128 * 64) - 64))
        {
        _LIT8(KHtcleoEikBasePrefix, "HTCLEO_EIKBASE ");
        TBuf8<96> record;
        record.Append(KHtcleoEikBasePrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            }
        }
    file.Close();
    fs.Close();
    }
#else
inline void HtcleoEikAppUiBaseLog(TUint32, TInt, TUint32) {}
#endif
'''


MALFORMED_PATHS = r'''    _LIT(KHtcleoEikBaseLogDir, "C:\Symbian3\");
    _LIT(KHtcleoEikBaseLogPath, "C:\Symbian3\EIKBASE.TXT");'''

CORRECT_PATHS = r'''    _LIT(KHtcleoEikBaseLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikBaseLogPath, "C:\\Symbian3\\EIKBASE.TXT");'''


BASE_OLD = r'''EXPORT_C void CEikAppUi::BaseConstructL(TInt aAppUiFlags)
    {
    TWsEvent event;
    event.SetType(EEventNull);
    
	MEikAppUiFactory* appUiFactory = iEikonEnv->AppUiFactory(*this);
	ASSERT(appUiFactory);
    iContainerAppUi = static_cast<CEikAppUi*>(iCoeEnv->SetAppUi(this));
    iAppUiExtra = new (ELeave) CEikAppUiExtra(*this); 
	if (iContainerAppUi)
		{
        HandleApplicationSpecificEventL( KEikNotifyPreCreateEmbeddedL, event );
		appUiFactory->CreateEmbeddedL(*iEikonEnv);
		iFlags |= EEmbedded;
		HandleApplicationSpecificEventL( KEikNotifyPostCreateEmbeddedL, event );
		TRAP_IGNORE(iContainerAppUi->HandleResourceChangeL(KEikMessageEmbedLevelChange));
		iContainerAppUi->HandleStackedControlsResourceChange(KEikMessageEmbedLevelChange);
		}
		
    CCoeAppUi::ConstructL(iContainerAppUi);
    HandleApplicationSpecificEventL( KEikPostCoeAppUiConstructL, event );
	if (!iContainerAppUi)
		iEikonEnv->ControlStackReadyL();
	
	if (!(aAppUiFlags&(ENoAppResourceFile|ENonStandardResourceFile)))
	    ReadAppInfoResourceL();
	
	else if (!(aAppUiFlags&ENoScreenFurniture))
		CreateResourceIndependentFurnitureL();
	
	iCoeEnv->AddMessageObserverL(*this);
	iEikonEnv->PostAppUiInitializeL();
	iCoeEnv->RootWin().EnableScreenChangeEvents();
    }
'''


BASE_NEW = r'''EXPORT_C void CEikAppUi::BaseConstructL(TInt aAppUiFlags)
    {
    HtcleoEikAppUiBaseLog(0x0000B600u, KErrNone, (TUint32)aAppUiFlags);
    TWsEvent event;
    event.SetType(EEventNull);
    HtcleoEikAppUiBaseLog(0x0000B601u, KErrNone, 0u);
    
	MEikAppUiFactory* appUiFactory = iEikonEnv->AppUiFactory(*this);
	ASSERT(appUiFactory);
    HtcleoEikAppUiBaseLog(0x0000B602u, KErrNone, appUiFactory != NULL);
    iContainerAppUi = static_cast<CEikAppUi*>(iCoeEnv->SetAppUi(this));
    HtcleoEikAppUiBaseLog(0x0000B603u, KErrNone, iContainerAppUi != NULL);
    iAppUiExtra = new (ELeave) CEikAppUiExtra(*this); 
    HtcleoEikAppUiBaseLog(0x0000B604u, KErrNone, iAppUiExtra != NULL);
	HtcleoEikAppUiBaseLog(0x0000B605u, KErrNone, iContainerAppUi != NULL);
	if (iContainerAppUi)
		{
        HandleApplicationSpecificEventL( KEikNotifyPreCreateEmbeddedL, event );
        HtcleoEikAppUiBaseLog(0x0000B606u, KErrNone, 0u);
		appUiFactory->CreateEmbeddedL(*iEikonEnv);
        HtcleoEikAppUiBaseLog(0x0000B607u, KErrNone, 0u);
		iFlags |= EEmbedded;
		HandleApplicationSpecificEventL( KEikNotifyPostCreateEmbeddedL, event );
		TRAP_IGNORE(iContainerAppUi->HandleResourceChangeL(KEikMessageEmbedLevelChange));
		iContainerAppUi->HandleStackedControlsResourceChange(KEikMessageEmbedLevelChange);
        HtcleoEikAppUiBaseLog(0x0000B608u, KErrNone, (TUint32)iFlags);
		}
		
    HtcleoEikAppUiBaseLog(0x0000B609u, KErrNone, iContainerAppUi != NULL);
    CCoeAppUi::ConstructL(iContainerAppUi);
    HtcleoEikAppUiBaseLog(0x0000B60Au, KErrNone, 0u);
    HandleApplicationSpecificEventL( KEikPostCoeAppUiConstructL, event );
    HtcleoEikAppUiBaseLog(0x0000B60Bu, KErrNone, 0u);
	HtcleoEikAppUiBaseLog(0x0000B60Cu, KErrNone, iContainerAppUi != NULL);
	if (!iContainerAppUi)
		iEikonEnv->ControlStackReadyL();
    HtcleoEikAppUiBaseLog(0x0000B60Du, KErrNone, 0u);
	
	HtcleoEikAppUiBaseLog(0x0000B60Eu, KErrNone, (TUint32)aAppUiFlags);
	if (!(aAppUiFlags&(ENoAppResourceFile|ENonStandardResourceFile)))
	    ReadAppInfoResourceL();
	
	else if (!(aAppUiFlags&ENoScreenFurniture))
		CreateResourceIndependentFurnitureL();
    HtcleoEikAppUiBaseLog(0x0000B60Fu, KErrNone, 0u);
	
    HtcleoEikAppUiBaseLog(0x0000B610u, KErrNone, 0u);
	iCoeEnv->AddMessageObserverL(*this);
    HtcleoEikAppUiBaseLog(0x0000B611u, KErrNone, 0u);
    HtcleoEikAppUiBaseLog(0x0000B612u, KErrNone, 0u);
	iEikonEnv->PostAppUiInitializeL();
    HtcleoEikAppUiBaseLog(0x0000B613u, KErrNone, 0u);
    HtcleoEikAppUiBaseLog(0x0000B614u, KErrNone, 0u);
	const TInt htcleoEikScreenChangeResult =
        iCoeEnv->RootWin().EnableScreenChangeEvents();
    HtcleoEikAppUiBaseLog(0x0000B615u, htcleoEikScreenChangeResult,
        0x53434E32u);
    }
'''


def verify(source: str, mmp: str) -> None:
    stages = range(0xB600, 0xB616)
    matrixmenu_final_screen = MATRIXMENU_FINAL_SCREEN_MARKER in source
    homescreen_trace = (
        "HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1" in source
    )
    checks = {
        "marker": source.count(MARKER) == 1,
        "durable path": (
            source.count(r"C:\\Symbian3\\EIKBASE.TXT") == 1
            and (
                source.count(r"C:\\Symbian3\\HSXML.TXT") == 1
                if homescreen_trace
                else True
            )
        ),
        "bounded durable log": (
            source.count("position <= htcleoEikBaseLimit") == 1
            and source.count("1048576 - 128") == 1
            if homescreen_trace
            else source.count("position <= ((128 * 64) - 64)") == 1
        ),
        "exact durable-log SID gate": (
            source.count("htcleoEikBaseSid != 0x10003A4Au") == 1
            and source.count("htcleoEikBaseSid != 0x101F4CD2u") == 1
            and source.count("!htcleoEikBaseHome") == 1
            if homescreen_trace
            else source.count("htcleoEikBaseSid != 0x10003A4Au") == 1
            and source.count("htcleoEikBaseSid != 0x101F4CD2u") == 1
            if matrixmenu_final_screen
            else source.count("RProcess().SecureId().iId != 0x10003A4A") == 1
        ),
        "all stages": all(
            source.count(f"0x0000{stage:04X}u") == 1 for stage in stages
        ),
        "stock core construct retained": source.count(
            "CCoeAppUi::ConstructL(iContainerAppUi);"
        ) == 1,
        "stock control stack retained": source.count(
            "iEikonEnv->ControlStackReadyL();"
        ) == 1,
        "stock observer retained": source.count(
            "iCoeEnv->AddMessageObserverL(*this);"
        ) == 1,
        "stock post initialize retained": source.count(
            "iEikonEnv->PostAppUiInitializeL();"
        ) == 1,
        "stock screen change retained": source.count(
            "iCoeEnv->RootWin().EnableScreenChangeEvents();"
        ) == 1,
        "logger flush policy": (
            source.count("file.Flush();") == 0
            if matrixmenu_final_screen
            else source.count("file.Flush();") == 1
        ),
        "screen change detail": source.count("0x53434E32u") == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "no delay": "User::After" not in HELPER,
        "no display probe": "HalFunction" not in HELPER,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("EikAppUi BaseConstruct verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    component = args.root / "sf/mw/classicui/commonuisupport/uikon"
    source_path = component / "coresrc/EIKAPPUI.CPP"
    mmp_path = component / "group/EIKCORE.MMP"
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    # Repair the one malformed path emitted by the first local draft before
    # its compile failure. Fresh source never takes this compatibility branch.
    if MARKER in source and MALFORMED_PATHS in source:
        source = replace_once(
            source,
            MALFORMED_PATHS,
            CORRECT_PATHS,
            "malformed first-draft durable paths",
        )
    if MARKER in source and "position < (128 * 64)" in source:
        source = replace_once(
            source,
            "position < (128 * 64)",
            "position <= ((128 * 64) - 64)",
            "first-draft durable bound",
        )
    if MARKER not in source:
        source = replace_once(
            source,
            '#include "eikdefconst.h"\n',
            '#include "eikdefconst.h"\n' + HELPER,
            "durable helper",
        )
        source = replace_once(source, BASE_OLD, BASE_NEW, "BaseConstructL body")
    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(source, mmp)
    if source != source_path.read_text(encoding="latin-1"):
        source_path.write_text(source, encoding="latin-1")
    if mmp != mmp_path.read_text(encoding="latin-1"):
        mmp_path.write_text(mmp, encoding="latin-1")
    print("HTCLEO_EIKAPPUI_BASECONSTRUCT_DURABLE_LOG=installed stages=B600-B615")


if __name__ == "__main__":
    main()
