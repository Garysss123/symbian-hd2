#!/usr/bin/env python3
"""Defer Matrix-to-Home handoff until the CBA pointer stack has returned."""
from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_HOME_HANDOFF_ASYNC_V1"


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_header(text: str) -> str:
    if MARKER in text:
        return text
    anchor = '''    CPeriodic* iHtcleoHeartbeat;
    static TInt HtcleoHeartbeatTick(TAny* aSelf);
'''
    replacement = anchor + '''
    // HTCLEO_MATRIXMENU_HOME_HANDOFF_ASYNC_V1
    CAsyncCallBack* iHtcleoHomeHandoff;
    TExitType iHtcleoPendingHomeExit;
    static TInt HtcleoHomeHandoffTick(TAny* aSelf);
'''
    return once(text, anchor, replacement, "Matrix async members")


def patch_source(text: str) -> str:
    if MARKER in text:
        callback_start = text.index("TInt CMmAppUi::HtcleoHomeHandoffTick")
        callback_end = text.index("void CMmAppUi::ExitMatrix", callback_start)
        callback = text[callback_start:callback_end]
        if "0x4D4D142Du" not in callback:
            callback = callback.replace("0x4D4D1426u", "0x4D4D142Du", 1)
            callback = callback.replace("0x4D4D1427u", "0x4D4D142Eu", 1)
            text = text[:callback_start] + callback + text[callback_end:]
        return text
    text = once(
        text,
        '''CMmAppUi::CMmAppUi()
    : iHtcleoHeartbeat(NULL)
''',
        '''CMmAppUi::CMmAppUi()
    : iHtcleoHeartbeat(NULL), iHtcleoHomeHandoff(NULL),
      iHtcleoPendingHomeExit(EExitToIdle)
''',
        "Matrix async constructor",
    )
    text = once(
        text,
        '''CMmAppUi::~CMmAppUi()
    {
    delete iHtcleoHeartbeat;
''',
        '''CMmAppUi::~CMmAppUi()
    {
    if (iHtcleoHomeHandoff)
        iHtcleoHomeHandoff->Cancel();
    delete iHtcleoHomeHandoff;
    iHtcleoHomeHandoff = NULL;
    delete iHtcleoHeartbeat;
''',
        "Matrix async destructor",
    )
    text = once(
        text,
        '''        }
    MMPERF(("CMmAppUi::ConstructL - HN ready"));
''',
        '''        }
    // HTCLEO_MATRIXMENU_HOME_HANDOFF_ASYNC_V1
    // Allocation failure retains the existing synchronous fallback below.
    if (!iHtcleoHomeHandoff)
        {
        TRAPD(htcleoHandoffAlloc,
            iHtcleoHomeHandoff = new(ELeave) CAsyncCallBack(
                TCallBack(HtcleoHomeHandoffTick, this),
                CActive::EPriorityStandard));
        HtcleoMenuLog(0x4D4D1429u, htcleoHandoffAlloc,
            iHtcleoHomeHandoff ? 1u : 0u);
        }
    MMPERF(("CMmAppUi::ConstructL - HN ready"));
''',
        "Matrix async construction",
    )
    callback = r'''
// HTCLEO_MATRIXMENU_HOME_HANDOFF_ASYNC_V1
TInt CMmAppUi::HtcleoHomeHandoffTick(TAny* aSelf)
    {
    CMmAppUi* self = static_cast<CMmAppUi*>(aSelf);
    const TExitType exitType = self->iHtcleoPendingHomeExit;
    HtcleoMenuLog(0x4D4D142Bu, KErrNone, exitType);
    TRAPD(homeResult, self->ShowHomescreenL(exitType));
    HtcleoMenuLog(0x4D4D142Du, homeResult, exitType);
    TRAPD(cleanupResult, self->CleanupForExitL(EExitKeyRed));
    HtcleoMenuLog(0x4D4D142Eu, cleanupResult, exitType);
    HtcleoMenuLog(0x4D4D142Cu, homeResult, cleanupResult);
    return KErrNone;
    }

'''
    text = once(
        text,
        '''void CMmAppUi::ExitMatrix( TExitType aExitType )
''',
        callback + '''void CMmAppUi::ExitMatrix( TExitType aExitType )
''',
        "Matrix async callback",
    )
    old = '''        TRAPD(htcleoHomeResult, ShowHomescreenL( aExitType ));
        HtcleoMenuLog(0x4D4D1426u, htcleoHomeResult, aExitType);
        TRAPD(htcleoCleanupResult, CleanupForExitL( EExitKeyRed ));
        HtcleoMenuLog(0x4D4D1427u, htcleoCleanupResult, aExitType);
'''
    new = '''        if (iHtcleoHomeHandoff)
            {
            iHtcleoPendingHomeExit = aExitType;
            const TBool alreadyQueued = iHtcleoHomeHandoff->IsActive();
            if (!alreadyQueued)
                iHtcleoHomeHandoff->CallBack();
            HtcleoMenuLog(0x4D4D142Au,
                alreadyQueued ? KErrInUse : KErrNone, aExitType);
            }
        else
            {
            // Allocation failed at startup: preserve the stock synchronous
            // behavior rather than dropping the user's navigation request.
            TRAPD(htcleoHomeResult, ShowHomescreenL( aExitType ));
            HtcleoMenuLog(0x4D4D1426u, htcleoHomeResult, aExitType);
            TRAPD(htcleoCleanupResult, CleanupForExitL( EExitKeyRed ));
            HtcleoMenuLog(0x4D4D1427u, htcleoCleanupResult, aExitType);
            }
'''
    return once(text, old, new, "Matrix synchronous Home handoff")


def verify(header: str, source: str) -> None:
    joined = header + source
    if header.count(MARKER) != 1 or source.count(MARKER) != 2:
        raise SystemExit("Matrix async handoff markers missing or duplicated")
    for token in (
        "CAsyncCallBack* iHtcleoHomeHandoff",
        "TExitType iHtcleoPendingHomeExit",
        "HtcleoHomeHandoffTick",
        "iHtcleoHomeHandoff->CallBack();",
        "iHtcleoHomeHandoff->IsActive();",
        "self->ShowHomescreenL(exitType)",
        "self->CleanupForExitL(EExitKeyRed)",
    ):
        if token not in joined:
            raise SystemExit("Matrix async handoff operation incomplete")
    for stage in ("1429", "142A", "142B", "142C", "142D", "142E"):
        if source.count(f"0x4D4D{stage}u") != 1:
            raise SystemExit(f"Matrix async stage {stage} missing")
    callback_start = source.index("TInt CMmAppUi::HtcleoHomeHandoffTick")
    callback_end = source.index("void CMmAppUi::ExitMatrix", callback_start)
    callback = source[callback_start:callback_end]
    if not (
        callback.index("ShowHomescreenL")
        < callback.index("CleanupForExitL")
        < callback.index("0x4D4D142Cu")
    ):
        raise SystemExit("Matrix async Home/cleanup order changed")
    exit_start = source.index("void CMmAppUi::ExitMatrix")
    exit_end = source.index("void CMmAppUi::CleanupForExitL", exit_start)
    exit_body = source[exit_start:exit_end]
    if not (
        exit_body.index("iHtcleoHomeHandoff->CallBack();")
        < exit_body.index("0x4D4D142Au")
        < exit_body.index("0x4D4D1428u")
    ):
        raise SystemExit("Matrix CBA return/queue order changed")
    for forbidden in (
        "User::After", "RTimer", "User::WaitForRequest", "RequestComplete",
        "HalFunction", "HtcleoI2c", "RThread", "RProcess::Create",
    ):
        if forbidden in callback or forbidden in exit_body:
            raise SystemExit("Matrix async handoff added a wait or new transport")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu"
    header_path = base / "inc/mmappui.h"
    source_path = base / "src/mmappui.cpp"
    header = patch_header(header_path.read_text(encoding="latin-1"))
    source = patch_source(source_path.read_text(encoding="latin-1"))
    verify(header, source)
    if patch_header(header) != header or patch_source(source) != source:
        raise SystemExit("Matrix async handoff is not idempotent")
    header_path.write_text(header, encoding="latin-1")
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIX_HOME_HANDOFF_ASYNC="
        "standard-casync-after-cba-return-1429-142e-sync-fallback"
    )


if __name__ == "__main__":
    main()
