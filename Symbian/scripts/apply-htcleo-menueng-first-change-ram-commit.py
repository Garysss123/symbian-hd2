#!/usr/bin/env python3
"""Commit the first HTC Leo MenuContent mutation in RAM without XCFW save.

Hardware iteration 567 reaches EEvtSavingComplete for the initial 12-App
scanner update but never returns to CMenuEng::RunL(ESaveFile) or the scanner's
completion callback.  The server then restarts and reconstructs the same
matrixmenudata content.  The UI requires the in-memory tree and EngineEvents,
not an on-disk XML rewrite during this first boot race.

Only the first *changed* operation in mcsmenuserver is committed in RAM and
completed through the stock no-change completion path.  Later changes retain
the stock asynchronous SaveTempFileL/ReplaceRamFileL persistence path.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MENUENG_FIRST_CHANGE_RAM_COMMIT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


CONSTRUCTOR = r'''CMenuEng::CMenuEng( MMenuEngObserver& aObserver )
: CActive( CActive::EPriorityStandard ), iObserver( aObserver )
    {
    CActiveScheduler::Add( this );
    iLegacyFormat = EFalse;
    }'''


CONSTRUCTOR_PATCHED = r'''CMenuEng::CMenuEng( MMenuEngObserver& aObserver )
: CActive( CActive::EPriorityStandard ), iObserver( aObserver )
    {
    CActiveScheduler::Add( this );
    iLegacyFormat = EFalse;
    iHtcleoFirstChangedOperation = ETrue;
    }'''


SAVE_CHANGES = r'''void CMenuEng::SaveChangesL()
    {
    // This method is part of ExecuteOperationL.
    // (Post-operation processing.)
    __ASSERT_DEBUG( EExecuteOp == iState, User::Invariant() );
    if ( iChanged || iDiskWasFullAndRamFileWasNotCreated )
        {
        // Tree changed, async save.
        iState = ESaveFile;
        SaveTempFileL();
        }
    else
        {
        // Tree not changed, we are done.
        CompleteCurrentOperation( KErrNone );
        if ( iOperations.Count() )
            {
            // Go for the next operation (async).
            iState = EExecuteOp; // Same as current value, code clarity.
            SelfComplete( KErrNone );
            }
        else
            {
            // No pending operations, we stop here.
            // Next QueueOperationL will kick us back to operation.
            iState = EReady;
            }
        }
    }'''


SAVE_CHANGES_PATCHED = r'''void CMenuEng::SaveChangesL()
    {
    // This method is part of ExecuteOperationL.
    // (Post-operation processing.)
    __ASSERT_DEBUG( EExecuteOp == iState, User::Invariant() );

    // HTCLEO_MENUENG_FIRST_CHANGE_RAM_COMMIT_V1
    // The first changed operation is the restored AppArc population on this
    // dedicated ROM.  Hardware reaches XCFW saving-complete but loses the
    // server before ESaveFile RunL can complete the operation.  Keep the real
    // mutated DOM, flush its real notifications and avoid only that first XML
    // persistence cycle.  All later changed operations remain stock.
    if ( iHtcleoFirstChangedOperation && iChanged
            && RProcess().SecureId().iId == 0x200113DDu )
        {
        iHtcleoFirstChangedOperation = EFalse;
        HtcleoMenuEngLog(0x4D450530u, KErrNone,
            (TUint32)iNotifyQueue.Count());
        iChanged = EFalse;
        iDiskWasFullAndRamFileWasNotCreated = EFalse;
        CompleteCurrentOperation( KErrNone );
        HtcleoMenuEngLog(0x4D450531u, KErrNone,
            (TUint32)iOperations.Count());
        if ( iOperations.Count() )
            {
            iState = EExecuteOp;
            SelfComplete( KErrNone );
            }
        else
            {
            iState = EReady;
            }
        return;
        }

    if ( iChanged || iDiskWasFullAndRamFileWasNotCreated )
        {
        if ( iChanged )
            {
            iHtcleoFirstChangedOperation = EFalse;
            }
        // Tree changed, async save.
        iState = ESaveFile;
        SaveTempFileL();
        }
    else
        {
        // Tree not changed, we are done.
        CompleteCurrentOperation( KErrNone );
        if ( iOperations.Count() )
            {
            // Go for the next operation (async).
            iState = EExecuteOp; // Same as current value, code clarity.
            SelfComplete( KErrNone );
            }
        else
            {
            // No pending operations, we stop here.
            // Next QueueOperationL will kick us back to operation.
            iState = EReady;
            }
        }
    }'''


HEADER_TAIL = r'''    TBool iDiskWasFullAndRamFileWasNotCreated;
    };'''


HEADER_TAIL_PATCHED = r'''    TBool iDiskWasFullAndRamFileWasNotCreated;

    // HTCLEO_MENUENG_FIRST_CHANGE_RAM_COMMIT_V1
    TBool iHtcleoFirstChangedOperation;
    };'''


def install(source: str, header: str) -> tuple[str, str]:
    source = replace_once(
        source, CONSTRUCTOR, CONSTRUCTOR_PATCHED, "first-change initialization"
    )
    source = replace_once(
        source, SAVE_CHANGES, SAVE_CHANGES_PATCHED, "first-change RAM commit"
    )
    header = replace_once(
        header, HEADER_TAIL, HEADER_TAIL_PATCHED, "first-change state"
    )
    return source, header


def verify(source: str, header: str) -> None:
    checks = {
        "source marker": source.count(MARKER) == 1,
        "header marker": header.count(MARKER) == 1,
        "state init": source.count("iHtcleoFirstChangedOperation = ETrue;") == 1,
        "state member": header.count("TBool iHtcleoFirstChangedOperation;") == 1,
        "server SID scope": source.count("0x200113DDu") == 2,
        "RAM commit stages": (
            source.count("0x4D450530u") == 1
            and source.count("0x4D450531u") == 1
        ),
        "real completion": source.count("CompleteCurrentOperation( KErrNone );") == 2,
        "later save retained": source.count("SaveTempFileL();") >= 2,
        "no wait or display": (
            "User::After" not in source
            and "User::WaitForRequest" not in source
            and "HalFunction" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MenuEng first-change RAM commit verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    source_path = component / "engsrc/menueng.cpp"
    header_path = component / "enginc/menueng.h"
    if not source_path.is_file() or not header_path.is_file():
        raise SystemExit("missing MenuEng source/header")
    source = source_path.read_text(encoding="latin-1")
    header = header_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source, header = install(source, header)
    verify(source, header)
    source_path.write_text(source, encoding="latin-1")
    header_path.write_text(header, encoding="latin-1")
    print(
        "HTCLEO_MENUENG_FIRST_CHANGE_POLICY="
        "ram-only-first-changed-operation-notify-flush-530-531"
    )


if __name__ == "__main__":
    main()
