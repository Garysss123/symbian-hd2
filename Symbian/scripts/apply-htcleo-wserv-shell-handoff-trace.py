#!/usr/bin/env python3
"""Attribute native shell ordinal dispatch and its synchronous reply."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_WSERV_SHELL_HANDOFF_TRACE_V1"
OLD_ORDINAL = '''\t\tcase EWsClOpSetWindowGroupOrdinalPosition:
\t\t\tCWsWindowGroup::WindowGroupFromIdentifierL(pData.SetWindowGroupOrdinalPosition->identifier)->SetOrdinalPosition(pData.SetWindowGroupOrdinalPosition->position);
\t\t\tbreak;'''
NEW_ORDINAL = '''\t\tcase EWsClOpSetWindowGroupOrdinalPosition:
\t\t\t{
\t\t\t// HTCLEO_WSERV_SHELL_HANDOFF_TRACE_V1
\t\t\tconst TUint32 htcleoHandoffSid = SecureId().iId;
\t\t\tconst TBool htcleoHandoff = htcleoHandoffSid == 0x102750F0u ||
\t\t\t\thtcleoHandoffSid == 0x101F4CD2u;
\t\t\tconst TInt htcleoTarget = pData.SetWindowGroupOrdinalPosition->identifier;
\t\t\tif (htcleoHandoff)
\t\t\t\tHtcleoWsLog(0x0000047Bu, (TInt)htcleoHandoffSid, (TUint32)htcleoTarget);
\t\t\tCWsWindowGroup::WindowGroupFromIdentifierL(pData.SetWindowGroupOrdinalPosition->identifier)->SetOrdinalPosition(pData.SetWindowGroupOrdinalPosition->position);
\t\t\tif (htcleoHandoff)
\t\t\t\tHtcleoWsLog(0x0000047Cu, (TInt)htcleoHandoffSid, (TUint32)htcleoTarget);
\t\t\t}
\t\t\tbreak;'''

REPLY_START = '''void CWsClient::CompleteMessage(const RMessage2& aMessage,TInt aReason)
\t{'''
REPLY_PREFIX = '''
\t// Only the active synchronous ordinal command, not queued EventReady or
\t// arbitrary replies. Capture context before Complete invalidates the message.
\tconst TUint32 htcleoReplySid = SecureId().iId;
\tconst TBool htcleoHandoffReply =
\t\t(htcleoReplySid == 0x102750F0u || htcleoReplySid == 0x101F4CD2u) &&
\t\tiCurrentClient == this && iDestObj && iDestObj->Type() == WS_HANDLE_CLIENT &&
\t\tiCurrentCommand.iOpcode == EWsClOpSetWindowGroupOrdinalPosition &&
\t\t!aMessage.IsNull() && aMessage.Function() == EWservMessSyncMsgBuf;
\tif (htcleoHandoffReply)
\t\tHtcleoWsLog(0x0000047Du, aReason, htcleoReplySid);'''
REPLY_SUFFIX = '''
\tif (htcleoHandoffReply)
\t\tHtcleoWsLog(0x0000047Eu, aReason, htcleoReplySid);
'''


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"shell handoff trace anchor missing/duplicated: {old[:90]!r}")
    return text.replace(old, new, 1)


def patch_client(text: str) -> str:
    if MARKER in text:
        # Resume the build-only draft: the destination is a CWsClientObject
        # wrapper, not the CWsClient session itself.
        return text.replace("iCurrentClient == this && iDestObj == this &&",
                            "iCurrentClient == this && iDestObj && iDestObj->Type() == WS_HANDLE_CLIENT &&")
    text = once(text, OLD_ORDINAL, NEW_ORDINAL)
    text = once(text, REPLY_START, REPLY_START + REPLY_PREFIX)
    start = text.index(REPLY_START)
    end = text.index("\n    }\n", start)
    return text[:end] + REPLY_SUFFIX + text[end:]


def patch_logger(text: str) -> str:
    if "HTCLEO_WSERV_SHELL_HANDOFF_LOG_GATE_V1" in text:
        return text
    return once(text,
        "\tif (!htcleoTouchStage && !htcleoFatalStage && !htcleoHeartbeat)",
        "\t// HTCLEO_WSERV_SHELL_HANDOFF_LOG_GATE_V1\n"
        "\tconst TBool htcleoHandoffStage = aStage >= 0x0000047Bu && aStage <= 0x0000047Eu;\n"
        "\tif (!htcleoTouchStage && !htcleoFatalStage && !htcleoHeartbeat && !htcleoHandoffStage)")


def verify(before: str, client: str, logger: str) -> None:
    if client.count(MARKER) != 1:
        raise SystemExit("shell handoff marker missing")
    for stage in ("0x0000047Bu", "0x0000047Cu", "0x0000047Du", "0x0000047Eu"):
        if client.count(stage) != 1:
            raise SystemExit("missing or duplicate handoff stage")
    # Stronger than token presence: removing our instrumentation must restore
    # the original entire translation unit byte-for-byte.
    restored = client.replace(NEW_ORDINAL, OLD_ORDINAL, 1)
    restored = restored.replace(REPLY_START + REPLY_PREFIX, REPLY_START, 1)
    restored = restored.replace(REPLY_SUFFIX, "", 1)
    if MARKER not in before and restored != before:
        raise SystemExit("trace changed underlying command/reply semantics")
    if "aMessage.Function() == EWservMessSyncMsgBuf" not in client or "iDestObj->Type() == WS_HANDLE_CLIENT" not in client:
        raise SystemExit("reply trace must be scoped to the actual synchronous ordinal")
    if "htcleoHandoffStage" not in logger or "KCapacity = 1048576" not in logger:
        raise SystemExit("handoff trace must preserve the existing bounded log")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc"
    cp, lp = base / "CLIENT.CPP", base / "WSTOP.CPP"
    before = cp.read_text(encoding="utf-8")
    client = patch_client(before)
    logger = patch_logger(lp.read_text(encoding="utf-8"))
    verify(before, client, logger)
    cp.write_text(client, encoding="utf-8")
    lp.write_text(logger, encoding="utf-8")
    print("HTCLEO_WSERV_SHELL_HANDOFF_TRACE=ordinal-enter-return-47b-47c-sync-reply-47d-47e-no-semantic-change")


if __name__ == "__main__":
    main()
