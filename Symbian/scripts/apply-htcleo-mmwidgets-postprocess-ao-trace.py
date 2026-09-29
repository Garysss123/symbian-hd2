#!/usr/bin/env python3
"""Trace MatrixMenu's deferred item post-processing and drawer timer AOs."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MMWIDGETS_POSTPROCESS_AO_TRACE_V1"
DRAWER_MARKER = "HTCLEO_MMWIDGETS_DRAWER_AO_TRACE_V1"
CAPACITY_MARKER = "HTCLEO_MMWIDGETS_LOG_CAPACITY_1M_V1"


POST_RUN_OLD = r'''void CMmPostEvaluationProcessor::RunL()
    {      
    const TDesC8& mm_template = iDrawer.iMmModel->GetAttributeAsText( 
    		iIndexToProcess, KMmTemplate8 );      
    
    if ( mm_template.Compare( KNullDesC8 ) && mm_template.Compare( KEmpty8 ) )
    	{
        iDrawer.SetupSubCellsL( EFalse, iIndexToProcess );
    	}
    
    if ( ++iIndexToProcess < iDrawer.iMmModel->NumberOfItems() )
    	{
    	SetActive();
    	TRequestStatus* status = &iStatus;
    	User::RequestComplete( status, KErrNone );
    	}
    }'''


POST_RUN_NEW = r'''void CMmPostEvaluationProcessor::RunL()
    {
    // HTCLEO_MMWIDGETS_POSTPROCESS_AO_TRACE_V1
    const TInt htcleoItemCount = iDrawer.iMmModel->NumberOfItems();
    HtcleoMmwLog(0x4D570200u, iIndexToProcess,
        (TUint32)htcleoItemCount);
    HtcleoMmwLog(0x4D570201u, KErrNone,
        (TUint32)iIndexToProcess);
    const TDesC8& mm_template = iDrawer.iMmModel->GetAttributeAsText(
            iIndexToProcess, KMmTemplate8 );
    HtcleoMmwLog(0x4D570202u, KErrNone,
        (TUint32)mm_template.Length());

    if ( mm_template.Compare( KNullDesC8 ) && mm_template.Compare( KEmpty8 ) )
        {
        HtcleoMmwLog(0x4D570203u, KErrNone,
            (TUint32)iIndexToProcess);
        iDrawer.SetupSubCellsL( EFalse, iIndexToProcess );
        HtcleoMmwLog(0x4D570204u, KErrNone,
            (TUint32)iIndexToProcess);
        }

    ++iIndexToProcess;
    HtcleoMmwLog(0x4D570205u, iIndexToProcess,
        (TUint32)htcleoItemCount);
    if ( iIndexToProcess < htcleoItemCount )
        {
        HtcleoMmwLog(0x4D570206u, KErrNone,
            (TUint32)iIndexToProcess);
        SetActive();
        HtcleoMmwLog(0x4D570207u, iStatus.Int(),
            IsActive() ? 1u : 0u);
        TRequestStatus* status = &iStatus;
        User::RequestComplete( status, KErrNone );
        HtcleoMmwLog(0x4D570208u, iStatus.Int(),
            IsActive() ? 1u : 0u);
        }
    HtcleoMmwLog(0x4D570209u, KErrNone,
        (TUint32)iIndexToProcess);
    }'''


POST_ERROR_OLD = r'''TInt CMmPostEvaluationProcessor::RunError(TInt aError)
    {
    return aError;
    }'''


POST_ERROR_NEW = r'''TInt CMmPostEvaluationProcessor::RunError(TInt aError)
    {
    HtcleoMmwLog(0x4D57020Fu, aError, (TUint32)iIndexToProcess);
    return aError;
    }'''


POST_START_OLD = r'''void CMmPostEvaluationProcessor::StartAt( TInt aIndex )
	{
	Cancel();
	iIndexToProcess = aIndex;
	SetActive();
	TRequestStatus* status = &iStatus;
	User::RequestComplete( status, KErrNone );
	}'''


POST_START_NEW = r'''void CMmPostEvaluationProcessor::StartAt( TInt aIndex )
	{
	HtcleoMmwLog(0x4D570210u, aIndex,
		(TUint32)iDrawer.iMmModel->NumberOfItems());
	Cancel();
	HtcleoMmwLog(0x4D570211u, iStatus.Int(), IsActive() ? 1u : 0u);
	iIndexToProcess = aIndex;
	SetActive();
	HtcleoMmwLog(0x4D570212u, iStatus.Int(), IsActive() ? 1u : 0u);
	TRequestStatus* status = &iStatus;
	User::RequestComplete( status, KErrNone );
	HtcleoMmwLog(0x4D570213u, iStatus.Int(), IsActive() ? 1u : 0u);
	}'''


DRAWER_CONSTRUCT_OLD = r'''void CMmDrawerAnimator::ConstructL()
    {
    User::LeaveIfError( iTimer.CreateLocal() ); // Initialize timer
    CActiveScheduler::Add( this ); // Add to scheduler
    }'''


DRAWER_CONSTRUCT_NEW = r'''void CMmDrawerAnimator::ConstructL()
    {
    // HTCLEO_MMWIDGETS_DRAWER_AO_TRACE_V1
    const TInt htcleoTimerResult = iTimer.CreateLocal();
    HtcleoMmwLog(0x4D570220u, htcleoTimerResult,
        (TUint32)iTimer.Handle());
    User::LeaveIfError( htcleoTimerResult ); // Initialize timer
    CActiveScheduler::Add( this ); // Add to scheduler
    HtcleoMmwLog(0x4D570221u, KErrNone, (TUint32)this);
    }'''


DRAWER_CANCEL_OLD = r'''void CMmDrawerAnimator::DoCancel()
    {
    iTimer.Cancel();
    if( iDrawer.GetFloatingItemCount() == 0 )
        {
        TRAP_IGNORE(TriggerMoveItemL());
        }
    }'''


DRAWER_CANCEL_NEW = r'''void CMmDrawerAnimator::DoCancel()
    {
    HtcleoMmwLog(0x4D570222u, KErrNone, (TUint32)iTimer.Handle());
    iTimer.Cancel();
    HtcleoMmwLog(0x4D570223u, KErrNone,
        (TUint32)iDrawer.GetFloatingItemCount());
    if( iDrawer.GetFloatingItemCount() == 0 )
        {
        TRAP_IGNORE(TriggerMoveItemL());
        }
    }'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_post(text: str) -> str:
    if MARKER in text:
        return text
    if '#include "htcleommwlog.h"' not in text:
        text = replace_once(
            text,
            '#include "mmpostevaluationprocessor.h"\n',
            '#include "mmpostevaluationprocessor.h"\n#include "htcleommwlog.h"\n',
            "post logger include",
        )
    text = replace_once(text, POST_RUN_OLD, POST_RUN_NEW, "post RunL")
    text = replace_once(text, POST_ERROR_OLD, POST_ERROR_NEW, "post RunError")
    return replace_once(text, POST_START_OLD, POST_START_NEW, "post StartAt")


def install_widget(text: str) -> str:
    old = r'''    iPostProcessor->StartAt( iWidget->BottomItemIndex() + 1 );'''
    new = r'''    const TInt htcleoPostStartIndex = iWidget->BottomItemIndex() + 1;
    HtcleoMmwLog(0x4D570214u, htcleoPostStartIndex,
        (TUint32)GetMmModel()->NumberOfItems());
    iPostProcessor->StartAt( htcleoPostStartIndex );
    HtcleoMmwLog(0x4D570215u, KErrNone,
        iPostProcessor->IsActive() ? 1u : 0u);'''
    if "0x4D570214u" in text:
        return text
    return replace_once(text, old, new, "postprocessor caller")


def install_drawer(text: str) -> str:
    if DRAWER_MARKER in text:
        return text
    if '#include "htcleommwlog.h"' not in text:
        text = replace_once(
            text,
            '#include "mmdraweranimator.h"\n',
            '#include "mmdraweranimator.h"\n#include "htcleommwlog.h"\n',
            "drawer logger include",
        )
    text = replace_once(
        text, DRAWER_CONSTRUCT_OLD, DRAWER_CONSTRUCT_NEW, "drawer ConstructL"
    )
    text = replace_once(
        text, DRAWER_CANCEL_OLD, DRAWER_CANCEL_NEW, "drawer DoCancel"
    )
    text = replace_once(
        text,
        "void CMmDrawerAnimator::RunL()\n    {\n    if( iPreparedForGarbage )",
        "void CMmDrawerAnimator::RunL()\n    {\n"
        "    HtcleoMmwLog(0x4D570224u, iPreparedForGarbage ? 1 : 0,\n"
        "        (TUint32)iDrawer.GetFloatingItemCount());\n"
        "    if( iPreparedForGarbage )",
        "drawer RunL entry",
    )
    text = replace_once(
        text,
        "#endif\n        }\n    }\n\n// -----------------------------------------------------------------------------\n//\n// -----------------------------------------------------------------------------\n//\nTRect CMmDrawerAnimator::AdjustRefreshRectToNonTouch",
        "#endif\n        }\n"
        "    HtcleoMmwLog(0x4D570225u, KErrNone,\n"
        "        (TUint32)iDrawer.GetFloatingItemCount());\n"
        "    }\n\n// -----------------------------------------------------------------------------\n//\n// -----------------------------------------------------------------------------\n//\nTRect CMmDrawerAnimator::AdjustRefreshRectToNonTouch",
        "drawer RunL exit",
    )
    text = replace_once(
        text,
        "TInt CMmDrawerAnimator::Trigger()\n    {\n    if( iPreparedForGarbage )",
        "TInt CMmDrawerAnimator::Trigger()\n    {\n"
        "    HtcleoMmwLog(0x4D570226u, IsActive() ? 1 : 0,\n"
        "        (TUint32)iDrawer.GetFloatingItemCount());\n"
        "    if( iPreparedForGarbage )",
        "drawer Trigger entry",
    )
    text = replace_once(
        text,
        "        iTimer.After( iStatus, TTimeIntervalMicroSeconds32(\n"
        "                MmEffects::KAnimationFrameDelay ) );\n"
        "        SetActive();",
        "        HtcleoMmwLog(0x4D570227u, iStatus.Int(),\n"
        "            (TUint32)iTimer.Handle());\n"
        "        iTimer.After( iStatus, TTimeIntervalMicroSeconds32(\n"
        "                MmEffects::KAnimationFrameDelay ) );\n"
        "        HtcleoMmwLog(0x4D570228u, iStatus.Int(),\n"
        "            (TUint32)iTimer.Handle());\n"
        "        SetActive();\n"
        "        HtcleoMmwLog(0x4D570229u, iStatus.Int(),\n"
        "            IsActive() ? 1u : 0u);",
        "drawer timer arm",
    )
    text = replace_once(
        text,
        "TInt CMmDrawerAnimator::RunError( TInt aError )\n    {\n    return aError;\n    }",
        "TInt CMmDrawerAnimator::RunError( TInt aError )\n    {\n"
        "    HtcleoMmwLog(0x4D57022Fu, aError,\n"
        "        (TUint32)iDrawer.GetFloatingItemCount());\n"
        "    return aError;\n    }",
        "drawer RunError",
    )
    return text


def install_capacity(text: str) -> str:
    if CAPACITY_MARKER in text:
        return text
    text = replace_once(
        text,
        "// HTCLEO_MMWIDGETS_DUMMY_GRID_DURABLE_LOG_V1\n",
        "// HTCLEO_MMWIDGETS_DUMMY_GRID_DURABLE_LOG_V1\n"
        f"// {CAPACITY_MARKER}\n",
        "capacity marker",
    )
    return replace_once(
        text,
        "position <= ((128 * 64) - 64)",
        "position <= ((16384 * 64) - 64)",
        "MMW log capacity",
    )


def verify(post: str, widget: str, drawer: str, logger: str) -> None:
    combined = post + widget + drawer
    expected = (
        list(range(0x4D570200, 0x4D57020A))
        + [0x4D57020F]
        + list(range(0x4D570210, 0x4D570216))
        + list(range(0x4D570220, 0x4D57022A))
        + [0x4D57022F]
    )
    checks = {
        "markers": (
            post.count(MARKER) == 1
            and drawer.count(DRAWER_MARKER) == 1
            and logger.count(CAPACITY_MARKER) == 1
        ),
        "logger includes": (
            post.count('#include "htcleommwlog.h"') == 1
            and drawer.count('#include "htcleommwlog.h"') == 1
        ),
        "stages": all(combined.count(f"0x{stage:08X}u") == 1 for stage in expected),
        "real post work retained": (
            post.count("iDrawer.SetupSubCellsL( EFalse, iIndexToProcess );") == 1
            and post.count("User::RequestComplete( status, KErrNone );") == 2
        ),
        "real timer retained": (
            drawer.count("iTimer.After( iStatus") == 1
            and drawer.count("iTimer.Cancel();") == 1
        ),
        "capacity": (
            logger.count("position <= ((16384 * 64) - 64)") == 1
            and "position <= ((128 * 64) - 64)" not in logger
            and logger.count("file.Write(record);") == 1
            and "file.Flush" not in logger
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MMWidgets deferred AO trace failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/app/homescreen/menufw/menufwui/mmwidgets"
    post_path = component / "src/mmpostevaluationprocessor.cpp"
    widget_path = component / "src/mmwidgetcontainer.cpp"
    drawer_path = component / "src/mmdraweranimator.cpp"
    logger_path = component / "src/htcleommwlog.cpp"
    paths = (post_path, widget_path, drawer_path, logger_path)
    if not all(path.is_file() for path in paths):
        raise SystemExit("missing MMWidgets deferred AO source")
    post = install_post(post_path.read_text(encoding="latin-1"))
    widget = install_widget(widget_path.read_text(encoding="latin-1"))
    drawer = install_drawer(drawer_path.read_text(encoding="latin-1"))
    logger = install_capacity(logger_path.read_text(encoding="latin-1"))
    verify(post, widget, drawer, logger)
    post_path.write_text(post, encoding="latin-1")
    widget_path.write_text(widget, encoding="latin-1")
    drawer_path.write_text(drawer, encoding="latin-1")
    logger_path.write_text(logger, encoding="latin-1")
    print(
        "HTCLEO_MMWIDGETS_DEFERRED_AO_TRACE="
        "postprocess-200-215-drawer-220-22f-log-1m"
    )


if __name__ == "__main__":
    main()
