#!/usr/bin/env python3
"""Trace MatrixMenu's blocking dummy-grid constructor inside mmwidgets.dll.

Iteration 525 traps CMmWidgetContainer::NewGridContainerL() but never records
its return, proving that the call blocks rather than Leaves.  Add MatrixMenu-
only close-only MMWLOG checkpoints around the wrapper, grid two-phase
construction, base skin/long-tap setup, window creation, grid creation and
activation.  No control flow or error result is changed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MMWIDGETS_DUMMY_GRID_DURABLE_LOG_V1"
BUILD_CLOSURE_MARKER = "HTCLEO_MMWIDGETS_HN_BUILD_CLOSURE_V1"
ABI_CLOSURE_MARKER = "HTCLEO_MMWIDGETS_SETMANUALHIGHLIGHT_EABI_CLOSURE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HEADER = r'''#ifndef HTCLEO_MMW_LOG_H
#define HTCLEO_MMW_LOG_H

#include <e32std.h>

void HtcleoMmwLog(TUint32 aStage, TInt aResult, TUint32 aDetail);

#endif
'''


LOGGER = r'''#include "htcleommwlog.h"

#include <e32base.h>
#include <f32file.h>

// HTCLEO_MMWIDGETS_DUMMY_GRID_DURABLE_LOG_V1
void HtcleoMmwLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101F4CD2u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoMmwLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMmwLogPath, "C:\\Symbian3\\MMWLOG.TXT");
    r = fs.MkDirAll(KHtcleoMmwLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMmwLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMmwLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((128 * 64) - 64))
        {
        _LIT8(KHtcleoMmwPrefix, "HTCLEO_MMW ");
        TBuf8<96> record;
        record.Append(KHtcleoMmwPrefix);
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
        file.Write(record);
        }
    file.Close();
    fs.Close();
    }
'''


def install_widget(source: str) -> str:
    source = replace_once(
        source,
        '#include "mmwidgetcontainer.h"\n',
        '#include "mmwidgetcontainer.h"\n#include "htcleommwlog.h"\n',
        "widget logger include",
    )
    source = replace_once(
        source,
        """    {
    return CMmGridContainer::NewL( aRect, aObjectProvider, aLibrary );
    }
""",
        """    {
    HtcleoMmwLog(0x4D570100u, KErrNone, 0u);
    CMmWidgetContainer* result =
        CMmGridContainer::NewL( aRect, aObjectProvider, aLibrary );
    HtcleoMmwLog(0x4D570101u, KErrNone, result ? 1u : 0u);
    return result;
    }
""",
        "NewGridContainerL boundary",
    )
    source = replace_once(
        source,
        """void CMmWidgetContainer::ConstructL()
    {
    iBgContext = CAknsBasicBackgroundControlContext::NewL(
            KAknsIIDQsnBgAreaMainAppsGrid, Rect(), EFalse );
    iLongTapDetector = CAknLongTapDetector::NewL( this );
    iLongTapDetector->EnableLongTapAnimation( ETrue );
    }
""",
        """void CMmWidgetContainer::ConstructL()
    {
    HtcleoMmwLog(0x4D570110u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570111u, KErrNone, 0u);
    iBgContext = CAknsBasicBackgroundControlContext::NewL(
            KAknsIIDQsnBgAreaMainAppsGrid, Rect(), EFalse );
    HtcleoMmwLog(0x4D570112u, KErrNone, iBgContext ? 1u : 0u);
    HtcleoMmwLog(0x4D570113u, KErrNone, 0u);
    iLongTapDetector = CAknLongTapDetector::NewL( this );
    HtcleoMmwLog(0x4D570114u, KErrNone,
        iLongTapDetector ? 1u : 0u);
    HtcleoMmwLog(0x4D570115u, KErrNone, 0u);
    iLongTapDetector->EnableLongTapAnimation( ETrue );
    HtcleoMmwLog(0x4D570116u, KErrNone, 0u);
    }
""",
        "widget base ConstructL",
    )
    return source


def install_grid(source: str) -> str:
    source = replace_once(
        source,
        '#include "mmgridcontainer.h"\n',
        '#include "mmgridcontainer.h"\n#include "htcleommwlog.h"\n',
        "grid logger include",
    )
    source = replace_once(
        source,
        """    {
    CMmGridContainer* self = new( ELeave ) CMmGridContainer();
    CleanupStack::PushL( self );
    self->ConstructL( aRect, aObjectProvider, aLibrary );
    return self;
    }

// -----------------------------------------------------------------------------
// CMmGridContainer::NewL()
""",
        """    {
    HtcleoMmwLog(0x4D570120u, KErrNone, 0u);
    CMmGridContainer* self = new( ELeave ) CMmGridContainer();
    HtcleoMmwLog(0x4D570121u, KErrNone, self ? 1u : 0u);
    CleanupStack::PushL( self );
    HtcleoMmwLog(0x4D570122u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570123u, KErrNone, 0u);
    self->ConstructL( aRect, aObjectProvider, aLibrary );
    HtcleoMmwLog(0x4D570124u, KErrNone, 0u);
    return self;
    }

// -----------------------------------------------------------------------------
// CMmGridContainer::NewL()
""",
        "grid NewLC boundary",
    )
    source = replace_once(
        source,
        """    {
    CMmGridContainer* self = NewLC( aRect, aObjectProvider, aLibrary);
    CleanupStack::Pop( self );
    return self;
    }
""",
        """    {
    HtcleoMmwLog(0x4D570130u, KErrNone, 0u);
    CMmGridContainer* self = NewLC( aRect, aObjectProvider, aLibrary);
    HtcleoMmwLog(0x4D570131u, KErrNone, self ? 1u : 0u);
    CleanupStack::Pop( self );
    HtcleoMmwLog(0x4D570132u, KErrNone, 0u);
    return self;
    }
""",
        "grid NewL boundary",
    )
    source = replace_once(
        source,
        """    {
    CMmWidgetContainer::ConstructL();

    SetMopParent( aObjectProvider );
    CreateWindowL(); // Creates window.
    iWidget = CreateGridL(aTemplateLibrary);
    iWidget->SetListBoxObserver( this );
    SetRect( aRect ); // Sets rectangle of frame.
    ActivateL(); // Activates window. ( Ready to draw )
    SetupDrawer();
    SetHighlightVisibilityL( !AknLayoutUtils::PenEnabled() );
    iPostProcessor = CMmPostEvaluationProcessor::NewL( *iDrawer );
    }
""",
        """    {
    HtcleoMmwLog(0x4D570140u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570141u, KErrNone, 0u);
    CMmWidgetContainer::ConstructL();
    HtcleoMmwLog(0x4D570142u, KErrNone, 0u);

    SetMopParent( aObjectProvider );
    HtcleoMmwLog(0x4D570143u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570144u, KErrNone, 0u);
    CreateWindowL(); // Creates window.
    HtcleoMmwLog(0x4D570145u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570146u, KErrNone, 0u);
    iWidget = CreateGridL(aTemplateLibrary);
    HtcleoMmwLog(0x4D570147u, KErrNone, iWidget ? 1u : 0u);
    iWidget->SetListBoxObserver( this );
    HtcleoMmwLog(0x4D570148u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570149u, KErrNone, 0u);
    SetRect( aRect ); // Sets rectangle of frame.
    HtcleoMmwLog(0x4D57014Au, KErrNone, 0u);
    HtcleoMmwLog(0x4D57014Bu, KErrNone, 0u);
    ActivateL(); // Activates window. ( Ready to draw )
    HtcleoMmwLog(0x4D57014Cu, KErrNone, 0u);
    HtcleoMmwLog(0x4D57014Du, KErrNone, 0u);
    SetupDrawer();
    HtcleoMmwLog(0x4D57014Eu, KErrNone, 0u);
    HtcleoMmwLog(0x4D57014Fu, KErrNone, 0u);
    SetHighlightVisibilityL( !AknLayoutUtils::PenEnabled() );
    HtcleoMmwLog(0x4D570150u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570151u, KErrNone, 0u);
    iPostProcessor = CMmPostEvaluationProcessor::NewL( *iDrawer );
    HtcleoMmwLog(0x4D570152u, KErrNone,
        iPostProcessor ? 1u : 0u);
    }
""",
        "grid ConstructL body",
    )
    source = replace_once(
        source,
        """    {
    iGrid = CMmGrid::NewL( this,
        EAknListBoxSelectionList | EAknListBoxLoopScrolling | EAknListBoxDisableHighlight , aTemplateLibrary );
    iGrid->SetContainerWindowL( *this );
    iGrid->CreateScrollBarFrameL( ETrue );
    iGrid->SetPrimaryScrollingType(
          CAknGridView::EScrollFollowsItemsAndLoops );
    iGrid->SetSecondaryScrollingType(
          CAknGridView::EScrollFollowsGrid );
    iGrid->ScrollBarFrame()->SetScrollBarVisibilityL(
        CEikScrollBarFrame::EAuto, CEikScrollBarFrame::EAuto );
    iGrid->ScrollBarFrame()->DrawBackground( EFalse, EFalse );
    return iGrid;
    }
""",
        """    {
    HtcleoMmwLog(0x4D570160u, KErrNone, 0u);
    iGrid = CMmGrid::NewL( this,
        EAknListBoxSelectionList | EAknListBoxLoopScrolling | EAknListBoxDisableHighlight , aTemplateLibrary );
    HtcleoMmwLog(0x4D570161u, KErrNone, iGrid ? 1u : 0u);
    iGrid->SetContainerWindowL( *this );
    HtcleoMmwLog(0x4D570162u, KErrNone, 0u);
    iGrid->CreateScrollBarFrameL( ETrue );
    HtcleoMmwLog(0x4D570163u, KErrNone, 0u);
    iGrid->SetPrimaryScrollingType(
          CAknGridView::EScrollFollowsItemsAndLoops );
    HtcleoMmwLog(0x4D570164u, KErrNone, 0u);
    iGrid->SetSecondaryScrollingType(
          CAknGridView::EScrollFollowsGrid );
    HtcleoMmwLog(0x4D570165u, KErrNone, 0u);
    iGrid->ScrollBarFrame()->SetScrollBarVisibilityL(
        CEikScrollBarFrame::EAuto, CEikScrollBarFrame::EAuto );
    HtcleoMmwLog(0x4D570166u, KErrNone, 0u);
    iGrid->ScrollBarFrame()->DrawBackground( EFalse, EFalse );
    HtcleoMmwLog(0x4D570167u, KErrNone, 0u);
    HtcleoMmwLog(0x4D570168u, KErrNone, iGrid ? 1u : 0u);
    return iGrid;
    }
""",
        "CreateGridL body",
    )
    return source


def verify(widget: str, grid: str, widget_header: str, mmp: str, logger: str) -> None:
    combined = widget + grid
    expected = [
        *range(0x4D570100, 0x4D570102),
        *range(0x4D570110, 0x4D570117),
        *range(0x4D570120, 0x4D570125),
        *range(0x4D570130, 0x4D570133),
        *range(0x4D570140, 0x4D570153),
        *range(0x4D570160, 0x4D570169),
    ]
    missing = [
        f"0x{stage:08X}u"
        for stage in expected
        if combined.count(f"0x{stage:08X}u") != 1
    ]
    checks = {
        "logger marker": logger.count(MARKER) == 1,
        "durable path": logger.count(r"C:\\Symbian3\\MMWLOG.TXT") == 1,
        "MatrixMenu SID gate": logger.count("0x101F4CD2u") == 1,
        "close-only write": (
            logger.count("file.Write(record);") == 1
            and "file.Flush" not in logger
        ),
        "single logger source": mmp.count("SOURCE          htcleommwlog.cpp") == 1,
        "file-server import": mmp.count("LIBRARY           efsrv.lib") == 1,
        "HN build closure": (
            mmp.count(BUILD_CLOSURE_MARKER) == 1
            and mmp.count("../../../hierarchynavigator/hnengine/inc") == 1
            and mmp.count("../../../hierarchynavigator/hnmetadatamodel/inc") == 1
            and mmp.count("../../../hierarchynavigator/hnpresentationmodel/inc") == 1
            and mmp.count("../../../hierarchynavigator/hnutilities/inc") == 1
        ),
        "stock 42-export ABI closure": (
            widget_header.count(ABI_CLOSURE_MARKER) == 1
            and "IMPORT_C virtual void SetManualHighlightL" not in widget_header
            and widget_header.count(
                "virtual void SetManualHighlightL(TInt aItemIndex,  TBool aRedraw = ETrue );"
            ) == 1
        ),
        "base logger includes": (
            widget.count('#include "htcleommwlog.h"') == 1
            and grid.count('#include "htcleommwlog.h"') == 1
        ),
        "control flow retained": (
            combined.count("CMmWidgetContainer::ConstructL();") == 1
            and combined.count("CreateWindowL();") == 1
            and combined.count("iWidget = CreateGridL(aTemplateLibrary);") == 1
            and combined.count("ActivateL();") == 1
        ),
        "no timer display or normalization": (
            "User::After" not in LOGGER
            and "HalFunction" not in LOGGER
            and "KErrNotSupported" not in LOGGER
            and "User::LeaveIfError" not in LOGGER
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if missing:
        failed.append("missing/duplicate stages=" + ",".join(missing))
    if failed:
        raise SystemExit("mmwidgets trace verification failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/mmwidgets"
    )
    widget_path = component / "src/mmwidgetcontainer.cpp"
    grid_path = component / "src/mmgridcontainer.cpp"
    widget_header_path = component / "inc/mmwidgetcontainer.h"
    header_path = component / "inc/htcleommwlog.h"
    logger_path = component / "src/htcleommwlog.cpp"
    mmp_path = component / "group/mmwidgets.mmp"
    for path in (widget_path, grid_path, widget_header_path, mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing mmwidgets input: {path}")

    widget = widget_path.read_text(encoding="latin-1")
    grid = grid_path.read_text(encoding="latin-1")
    widget_header = widget_header_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    if MARKER not in (logger_path.read_text(encoding="latin-1") if logger_path.is_file() else ""):
        widget = install_widget(widget)
        grid = install_grid(grid)
        mmp = replace_once(
            mmp,
            "SOURCE          mmwidgetcontainer.cpp \n",
            "SOURCE          mmwidgetcontainer.cpp \nSOURCE          htcleommwlog.cpp\n",
            "logger translation unit",
        )
        mmp = replace_once(
            mmp,
            "LIBRARY           euser.lib\n",
            "LIBRARY           euser.lib\nLIBRARY           efsrv.lib\n",
            "file-server import",
        )

    if BUILD_CLOSURE_MARKER not in mmp:
        mmp = replace_once(
            mmp,
            "USERINCLUDE     ../inc\n",
            "USERINCLUDE     ../inc\n"
            "// HTCLEO_MMWIDGETS_HN_BUILD_CLOSURE_V1\n"
            "USERINCLUDE     ../../../hierarchynavigator/hnengine/inc\n"
            "USERINCLUDE     ../../../hierarchynavigator/hnmetadatamodel/inc\n"
            "USERINCLUDE     ../../../hierarchynavigator/hnpresentationmodel/inc\n"
            "USERINCLUDE     ../../../hierarchynavigator/hnutilities/inc\n",
            "hierarchy navigator include closure",
        )

    if ABI_CLOSURE_MARKER not in widget_header:
        widget_header = replace_once(
            widget_header,
            "    IMPORT_C virtual void SetManualHighlightL(TInt aItemIndex,  TBool aRedraw = ETrue );\n",
            "    // HTCLEO_MMWIDGETS_SETMANUALHIGHLIGHT_EABI_CLOSURE_V1\n"
            "    // The frozen EABI has 42 exports and omits this internal virtual.\n"
            "    virtual void SetManualHighlightL(TInt aItemIndex,  TBool aRedraw = ETrue );\n",
            "SetManualHighlightL frozen ABI closure",
        )

    logger = LOGGER
    verify(widget, grid, widget_header, mmp, logger)
    for path, content in (
        (widget_path, widget),
        (grid_path, grid),
        (widget_header_path, widget_header),
        (header_path, HEADER),
        (logger_path, logger),
        (mmp_path, mmp),
    ):
        path.write_text(content, encoding="latin-1")
    print(
        "HTCLEO_MMWIDGETS_DUMMY_GRID_LOG=installed "
        "path=C:\\Symbian3\\MMWLOG.TXT stages=4D570100-4D570168"
    )


if __name__ == "__main__":
    main()
