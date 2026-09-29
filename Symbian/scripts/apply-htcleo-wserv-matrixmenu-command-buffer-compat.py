#!/usr/bin/env python3
"""Apply MatrixMenu-wide WServ command-buffer compatibility on HTC Leo.

The real grid reaches CCoeControl::CreateWindowL but never reaches the
EWsClOpCreateWindow handler.  RWindowBase::construct() synchronously flushes
all previously queued WServ commands.  In UREL WServ, a leave from a non-final
buffered command sets the reply but does not complete the client message,
stranding WriteReplyWs forever.

For the MatrixMenu SID only, trace every command in the property-armed buffer,
skip the redraw-store cleanup commands proven to hard-hang before the real grid,
continue past the three compatibility errors repeatedly established during HTC
Leo bring-up, and make every other leave complete the message fail-closed.  No
window handle, new draw, geometry, activation or successful return is forged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


DISPATCH_MARKER = "HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V1"
DISPATCH_MARKER_V2 = "HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V2"
COMPLETION_MARKER = "HTCLEO_WSERV_MATRIXMENU_FATAL_COMPLETION_V1"


OLD_DISPATCH = (
    "\t\t// Dispatch the command to the WServ object that will process it\n"
    "\t\tiDestObj->CommandL(opcode, cmdParams);\t// (call #5)"
)


NEW_DISPATCH = r'''        // Dispatch the command to the WServ object that will process it
        // HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V1
        TInt htcleoGridPointer = 0;
        const TBool htcleoMatrixMenuBuffer =
            SecureId().iId == 0x101F4CD2u
            && RProperty::Get(TUid::Uid(0x101F4CD2),
                0x7F4D5701u, htcleoGridPointer) == KErrNone
            && htcleoGridPointer != 0;
        if (htcleoMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000442u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }
        const TBool htcleoRedrawStoreCleanup =
            (iDestObj->Type() == WS_HANDLE_WINDOW
                && opcode == EWsWinOpClearRedrawStore)
            || (iDestObj->Type() == WS_HANDLE_CLIENT
                && opcode == EWsClOpClearAllRedrawStores);
        if (htcleoMatrixMenuBuffer && htcleoRedrawStoreCleanup)
            {
            HtcleoWsLog(0x00000445u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            continue;
            }
        TRAPD(htcleoCommandError,
            iDestObj->CommandL(opcode, cmdParams));
        if (htcleoCommandError != KErrNone)
            {
            const TBool htcleoCompatibilityError =
                htcleoCommandError == KErrNotSupported
                || htcleoCommandError == KErrNotFound
                || htcleoCommandError == KErrServerTerminated;
            if (htcleoMatrixMenuBuffer && htcleoCompatibilityError)
                {
                HtcleoWsLog(0x00000440u, htcleoCommandError,
                    ((TUint32)iDestObj->Type() << 16)
                    | (opcode & 0xFFFFu));
                continue;
                }
            if (htcleoMatrixMenuBuffer)
                {
                HtcleoWsLog(0x00000441u, htcleoCommandError,
                    ((TUint32)iDestObj->Type() << 16)
                    | (opcode & 0xFFFFu));
                }
            User::Leave(htcleoCommandError);
            }
        if (htcleoMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000443u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }'''


OLD_ARMED_DISPATCH_V1 = r'''        if (htcleoMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000442u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }
        TRAPD(htcleoCommandError,'''


NEW_ARMED_DISPATCH_V2 = r'''        if (htcleoMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000442u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }
        const TBool htcleoRedrawStoreCleanup =
            (iDestObj->Type() == WS_HANDLE_WINDOW
                && opcode == EWsWinOpClearRedrawStore)
            || (iDestObj->Type() == WS_HANDLE_CLIENT
                && opcode == EWsClOpClearAllRedrawStores);
        if (htcleoMatrixMenuBuffer && htcleoRedrawStoreCleanup)
            {
            HtcleoWsLog(0x00000445u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            continue;
            }
        TRAPD(htcleoCommandError,'''


OLD_COMPLETION = (
    "\tif (err<KErrNone)\n"
    "\t\tSetReply(err);\n\n"
    "\tif (iInternalFlags&(EFinishedProcessingCommands|EPanicClientAsSoonAsPossible))\n"
    "\t\tCompleteMessage(iClientMessage,iReply);\t// (finish)"
)


NEW_COMPLETION = r'''	if (err<KErrNone)
		{
		SetReply(err);
		// HTCLEO_WSERV_MATRIXMENU_FATAL_COMPLETION_V1
		// Stock UREL leaves a synchronous non-final command message pending.
		// MatrixMenu must receive the real error instead of hanging forever.
		if (SecureId().iId == 0x101F4CD2u
				&& !(iInternalFlags &
					(EFinishedProcessingCommands|EPanicClientAsSoonAsPossible)))
			{
			HtcleoWsLog(0x00000444u, err,
				(TUint32)iCurrentCommand.iOpcode);
			iInternalFlags |= EFinishedProcessingCommands;
			}
		}

	if (iInternalFlags&(EFinishedProcessingCommands|EPanicClientAsSoonAsPossible))
		CompleteMessage(iClientMessage,iReply);	// (finish)'''


TRACE_HEAD_V1 = r'''        // HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V1
        TInt htcleoGridPointer = 0;
        const TBool htcleoMatrixMenuBuffer =
            SecureId().iId == 0x101F4CD2u
            && RProperty::Get(TUid::Uid(0x101F4CD2),
                0x7F4D5701u, htcleoGridPointer) == KErrNone
            && htcleoGridPointer != 0;
        if (htcleoMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000442u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }'''


TRACE_HEAD_V2 = r'''        // HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT_V2
        TInt htcleoGridPointer = 0;
        const TBool htcleoMatrixMenuBuffer =
            SecureId().iId == 0x101F4CD2u
            && RProperty::Get(TUid::Uid(0x101F4CD2),
                0x7F4D5701u, htcleoGridPointer) == KErrNone
            && htcleoGridPointer != 0;
        // The 0442/0443 pair is historical proof, not a runtime event stream.
        // Bound it so the 512-record file retains the later touch snapshots.
        static TInt htcleoMatrixMenuTraceCount = 0;
        const TBool htcleoTraceMatrixMenuBuffer =
            htcleoMatrixMenuBuffer && htcleoMatrixMenuTraceCount < 32;
        if (htcleoTraceMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000442u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            ++htcleoMatrixMenuTraceCount;
            }'''


TRACE_TAIL_V1 = r'''        if (htcleoMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000443u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }'''


TRACE_TAIL_V2 = r'''        if (htcleoTraceMatrixMenuBuffer)
            {
            HtcleoWsLog(0x00000443u, (TInt)opcode,
                (TUint32)iDestObj->Type());
            }'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    if DISPATCH_MARKER not in source and DISPATCH_MARKER_V2 not in source:
        source = replace_once(
            source, OLD_DISPATCH, NEW_DISPATCH, "per-command dispatch"
        )
    elif DISPATCH_MARKER_V2 not in source and "0x00000445u" not in source:
        source = replace_once(
            source,
            OLD_ARMED_DISPATCH_V1,
            NEW_ARMED_DISPATCH_V2,
            "redraw-store cleanup upgrade",
        )
    if DISPATCH_MARKER_V2 not in source:
        source = replace_once(
            source, TRACE_HEAD_V1, TRACE_HEAD_V2,
            "bounded MatrixMenu command trace head",
        )
        source = replace_once(
            source, TRACE_TAIL_V1, TRACE_TAIL_V2,
            "bounded MatrixMenu command trace tail",
        )
    if COMPLETION_MARKER not in source:
        source = replace_once(
            source, OLD_COMPLETION, NEW_COMPLETION, "fatal completion"
        )
    return source


def verify(source: str) -> None:
    checks = {
        "single dispatch marker": (
            source.count(DISPATCH_MARKER_V2) == 1
            and source.count(DISPATCH_MARKER) == 0
        ),
        "single completion marker": source.count(COMPLETION_MARKER) == 1,
        "matrixmenu scope": source.count("SecureId().iId == 0x101F4CD2u") == 2,
        "property arm": (
            source.count("0x7F4D5701u") >= 2
            and source.count("htcleoGridPointer != 0") == 1
        ),
        "single real command": source.count(
            "iDestObj->CommandL(opcode, cmdParams)"
        ) == 1,
        "trap real command": source.count(
            "TRAPD(htcleoCommandError,"
        ) == 1,
        "narrow errors": all(
            source.count(error) >= 1
            for error in (
                "htcleoCommandError == KErrNotSupported",
                "htcleoCommandError == KErrNotFound",
                "htcleoCommandError == KErrServerTerminated",
            )
        ),
        "whole-buffer stages": all(
            source.count(f"0x{stage:08X}u") == 1
            for stage in (0x440, 0x441, 0x442, 0x443, 0x444, 0x445)
        ),
        "redraw cleanup only": (
            source.count("opcode == EWsWinOpClearRedrawStore") == 1
            and source.count("opcode == EWsClOpClearAllRedrawStores") == 1
            and source.count("htcleoRedrawStoreCleanup") == 2
        ),
        "fatal releave": source.count("User::Leave(htcleoCommandError);") == 1,
        "fatal completion": source.count(
            "iInternalFlags |= EFinishedProcessingCommands;"
        ) == 1,
        "bounded historical trace": (
            source.count("htcleoMatrixMenuTraceCount < 32") == 1
            and source.count("++htcleoMatrixMenuTraceCount") == 1
            and source.count("htcleoTraceMatrixMenuBuffer") == 3
        ),
        "no fabricated success": (
            "SetReply(KErrNone)" not in NEW_COMPLETION
            and "htcleoCommandError = KErrNone" not in NEW_DISPATCH
            and "iReply = KErrNone" not in NEW_COMPLETION
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
        / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/CLIENT.CPP"
    )
    source = source_path.read_text(encoding="utf-8")
    source = install(source)
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_WSERV_MATRIXMENU_COMMAND_BUFFER_COMPAT="
        "sid-scoped-property-armed-0440-0445-first32-trace-redraw-cleanup-and-optional-errors-skip-fatal-complete"
    )


if __name__ == "__main__":
    main()
