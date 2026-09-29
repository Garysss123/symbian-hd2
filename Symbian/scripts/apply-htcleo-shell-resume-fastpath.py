#!/usr/bin/env python3
"""763 shell-only resume overlay; reversible over the verified 762 sources."""
from __future__ import annotations

import argparse
from pathlib import Path

MATRIX_MARKER = "HTCLEO_MATRIX_HOME_MATCH_OUTBOUND_V4"
HOME_MARKER = "HTCLEO_HOME_RESUME_NO_EFFECTS_V1"

MATRIX_OLD = '''        // HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3
        // 757 proved that switch-to-owner is non-blocking but leaves focus on
        // Matrix because this root group had no Home owner relationship. Bind
        // the already-resolved live Home group first. Both public WServ calls
        // are buffered and the single Flush preserves their order.
        HtcleoMenuLog(0x4D4D144Au, KErrNone,
            (TUint32)task.WgId());
        iCoeEnv->RootWin().SetOwningWindowGroup(task.WgId());
        HtcleoMenuLog(0x4D4D144Bu, KErrNone,
            (TUint32)task.WgId());
        iCoeEnv->RootWin().SetOrdinalPosition(
            KOrdinalPositionSwitchToOwningWindow);
        iCoeEnv->WsSession().Flush();
        HtcleoMenuLog(0x4D4D1443u, KErrNone,
            (TUint32)task.WgId());'''

MATRIX_NEW = '''        // HTCLEO_MATRIX_HOME_MATCH_OUTBOUND_V4
        // Match the working Home-to-Matrix submit contract. The 762 buffered
        // owner/sentinel/Flush sequence still took about 15.7 seconds to return.
        // Buffered does not mean its Flush acknowledgement cannot block.
        // Keep this caller's foreground priority until the real target ordinal
        // reply returns; restore default priority control before file logging.
        HtcleoMenuLog(0x4D4D144Au, KErrNone,
            (TUint32)task.WgId());
        RWsSession& htcleoHomeWs = iCoeEnv->WsSession();
        htcleoHomeWs.ComputeMode(RWsSession::EPriorityControlDisabled);
        HtcleoMenuLog(0x4D4D144Bu, KErrNone,
            (TUint32)task.WgId());
        const TInt htcleoHomeOrdinal =
            htcleoHomeWs.SetWindowGroupOrdinalPosition(task.WgId(), 0);
        htcleoHomeWs.ComputeMode(RWsSession::EPriorityControlComputeOff);
        HtcleoMenuLog(0x4D4D1443u, htcleoHomeOrdinal,
            (TUint32)task.WgId());
        User::LeaveIfError(htcleoHomeOrdinal);'''

HOME_OLD = '''            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Au, KErrNone, 0u);
            GfxTransEffect::Enable();
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Bu, KErrNone, 0u);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Cu, KErrNone,
                    (TUint32)iAvkonEnv);
            iAvkonEnv->TransitionEvent(AknTransEffect::EApplicationActivate);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Du, KErrNone,
                    (TUint32)iAvkonEnv);'''

HOME_NEW = '''            // HTCLEO_HOME_RESUME_NO_EFFECTS_V1
            // Xn observers and the real Avkon base/key-block path have already
            // run. Keep the proven first Home activation and all other apps.
            // A returning Home needs input/focus state, not another effects
            // activation or its optional deferred startup/view-switch work.
            static TBool htcleoHomeFocusSeen = EFalse;
            const TBool htcleoResumeFast =
                htcleoHomeFocusTrace && htcleoHomeFocusSeen;
            if (htcleoHomeFocusTrace)
                htcleoHomeFocusSeen = ETrue;
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Au, KErrNone, 0u);
            if (!htcleoResumeFast)
                GfxTransEffect::Enable();
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Bu,
                    htcleoResumeFast ? KErrNotSupported : KErrNone, 0u);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Cu, KErrNone,
                    (TUint32)iAvkonEnv);
            if (!htcleoResumeFast)
                iAvkonEnv->TransitionEvent(AknTransEffect::EApplicationActivate);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C56Du,
                    htcleoResumeFast ? KErrNotSupported : KErrNone,
                    (TUint32)iAvkonEnv);'''


def replace_exact(text: str, old: str, new: str, name: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{name}: expected one exact source block")
    return text.replace(old, new, 1)


def patch(text: str, old: str, new: str, marker: str) -> str:
    if marker in text:
        if text.count(new) != 1 or text.count(marker) != 1:
            raise ValueError(f"{marker}: partial or duplicate overlay")
        return text
    return replace_exact(text, old, new, marker)


def restore(text: str, old: str, new: str, marker: str) -> str:
    if marker not in text:
        return text
    return replace_exact(text, new, old, marker)


def verify(matrix: str, home: str) -> None:
    if matrix.count(MATRIX_NEW) != 1 or home.count(HOME_NEW) != 1:
        raise ValueError("763 source overlay missing")
    if "HTCLEO_MATRIXMENU_HOME_OWNER_BINDING_V3" in matrix:
        raise ValueError("762 owner/sentinel handoff still active")
    start = matrix.index("void CMmAppUi::OpenAppL(")
    end = matrix.index("void CMmAppUi::InitializeL", start)
    handoff = matrix[start:end]
    for token in ("task.Exists()", "task.WgId()", "lsSession.StartApp( *cmdLine )"):
        if token not in handoff:
            raise ValueError(f"existing/new app contract lost: {token}")
    if any(t in MATRIX_NEW for t in ("SetOwningWindowGroup(",
            "KOrdinalPositionSwitchToOwningWindow", "Finish()", "User::After",
            "RTimer", "SendMessageToWindowGroup", "RProcess::Create")):
        raise ValueError("763 handoff added a foreign/synthetic/wait path")
    order = [MATRIX_NEW.index(t) for t in (
        "EPriorityControlDisabled", "SetWindowGroupOrdinalPosition(task.WgId(), 0)",
        "EPriorityControlComputeOff", "0x4D4D1443u", "User::LeaveIfError")]
    if order != sorted(order):
        raise ValueError("priority restore/error propagation order changed")
    for token in ("CAknAppUiBase::HandleWsEventL(aEvent, aDestination);",
                  "UpdateKeyBlockMode();", "0x0000C594u", "0x0000C56Eu",
                  "iExtension->iFlags.Clear(CAknAppUiExtension::EFocusLost);"):
        if token not in home:
            raise ValueError(f"required foreground/input state lost: {token}")
    if HOME_NEW.count("if (!htcleoResumeFast)") != 2:
        raise ValueError("both effects calls must be gated together")
    if any(t in HOME_NEW for t in ("return;", "SetOrdinal", "HalFunction",
                                  "After(", "WaitForRequest", "Disable()")):
        raise ValueError("Home overlay exceeds optional effect reactivation")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    files = (
        (args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp",
         MATRIX_OLD, MATRIX_NEW, MATRIX_MARKER),
        (args.root / "sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp",
         HOME_OLD, HOME_NEW, HOME_MARKER),
    )
    originals = [p.read_text(encoding="latin-1") for p, *_ in files]
    results = []
    for original, (path, old, new, marker) in zip(originals, files):
        result = (restore if args.restore else patch)(original, old, new, marker)
        if not args.restore:
            if patch(result, old, new, marker) != result:
                raise ValueError("overlay is not idempotent")
            if restore(result, old, new, marker) != restore(original, old, new, marker):
                raise ValueError("overlay does not restore exact predecessor")
        results.append(result)
    if not args.restore:
        verify(*results)
    # Validate both files before either is changed.
    for original, result, (path, *_rest) in zip(originals, results, files):
        if result != original:
            path.write_text(result, encoding="latin-1")
    print("HTCLEO_SHELL_RESUME_FASTPATH=" + (
        "overlay-restored-before-legacy-source-checks" if args.restore else
        "home-resume-no-effects-matrix-match-outbound-priority-safe-ordinal"))


if __name__ == "__main__":
    main()
