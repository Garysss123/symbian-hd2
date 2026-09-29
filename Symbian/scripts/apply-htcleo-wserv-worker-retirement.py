#!/usr/bin/env python3
"""Controlled rollback to the user's requested iteration742 WServ.

Reconstruct the742 logger and undo only743/744 WServ-side instrumentation.
Home/Matrix pointer-log retirement and all focus/input/ordinal code remain.
This is an A/B experiment, not a claim that the worker caused the regression.
"""
from __future__ import annotations

import argparse
import hashlib
import runpy
from pathlib import Path

SIGNATURE = "void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n\t{"
WORKER_MARKER = "// HTCLEO_WSERV_NONBLOCKING_LOG_V1"
END = "#else\nstatic inline void HtcleoWsLog"
OLD_COMMENT = "// Best-effort startup evidence.  The Window Server main thread is sole writer."
WORKER_COMMENT = "// Best-effort evidence. WServ enqueues; a private worker is the sole FAT writer."
CONTROL_SHA = "b8a2fb688e3a920923330d12819a1e8b048bca52cbfe2142721ab446889c421b"


def verify_image_equivalence(rebuilt: bytes, control: bytes) -> int:
    if len(rebuilt) != len(control) or rebuilt[0x10:0x14] != b"EPOC":
        raise ValueError("E32 signature/length mismatch")
    # E32ImageHeader (platform/f32image.h): iHeaderCrc at0x14;
    # iTimeLo/iTimeHi at0x24/0x28. NO code, imports, capabilities, flags,
    # version, BSS, heap/stack or other header differences are accepted.
    allowed = set(range(0x14, 0x18)) | set(range(0x24, 0x2C))
    differences = [i for i, pair in enumerate(zip(rebuilt, control)) if pair[0] != pair[1]]
    unexpected = [i for i in differences if i not in allowed]
    if unexpected:
        raise ValueError(f"non-timestamp E32 differences: {unexpected[:16]}")
    return len(differences)


def pin_control(root: Path, rebuilt_path: Path, control_path: Path) -> None:
    expected_target = root / "epoc32/release/armv5/urel/wserv_nga.exe"
    if rebuilt_path.resolve() != expected_target.resolve():
        raise SystemExit("refuse to replace a non-WServ release artifact")
    control = control_path.read_bytes()
    if hashlib.sha256(control).hexdigest() != CONTROL_SHA:
        raise SystemExit("immutable742 control digest mismatch")
    rebuilt = rebuilt_path.read_bytes()
    changed = verify_image_equivalence(rebuilt, control)
    # Reuse the original artifact only AFTER independent recompilation proves
    # all executable/data/import/security contents match it. Never edit742.
    rebuilt_path.write_bytes(control)
    if hashlib.sha256(rebuilt_path.read_bytes()).hexdigest() != CONTROL_SHA:
        raise SystemExit("pinned control verification failed")
    print(f"HTCLEO_WSERV_742_CONTROL_PIN=code-and-metadata-match timestamp-crc-bytes={changed} rebuilt-sha={hashlib.sha256(rebuilt).hexdigest()}")


def logger744() -> str:
    scripts = Path(__file__).parent
    low = runpy.run_path(str(scripts / "apply-htcleo-wserv-low-rate-touch-heartbeat.py"))
    life = runpy.run_path(str(scripts / "apply-htcleo-home-liveness-evidence.py"))
    handoff = runpy.run_path(str(scripts / "apply-htcleo-wserv-shell-handoff-trace.py"))
    return handoff["patch_logger"](life["patch_logger"](low["LOGGER"]))


def patch(text: str) -> str:
    restored = runpy.run_path(str(Path(__file__).with_name(
        "apply-htcleo-wserv-low-rate-touch-heartbeat.py")))["LOGGER"]
    if WORKER_MARKER in text:
        if text.count(WORKER_MARKER) != 1 or text.count("#include <e32atomics.h>\n") != 1:
            raise SystemExit("unexpected worker installation; refuse broad rollback")
        start = text.index(WORKER_MARKER)
        end = text.index(END, start)
        text = text[:start] + restored + text[end:]
        text = text.replace("#include <e32atomics.h>\n", "", 1)
        if text.count(WORKER_COMMENT) != 1:
            raise SystemExit("worker ownership comment mismatch")
        text = text.replace(WORKER_COMMENT, OLD_COMMENT, 1)
    else:
        start = text.index(SIGNATURE)
        end = text.index(END, start)
        if text[start:end] not in (logger744(), restored):
            raise SystemExit("unknown WServ writer; refuse broad rollback")
        text = text[:start] + restored + text[end:]
    start = text.index(SIGNATURE)
    end = text.index(END, start)
    if text[start:end] != restored:
        raise SystemExit("WServ logger is not the exact742 implementation")
    if any(token in text for token in
           ("HtcleoWsLogWorker", "gHtcleoWsQueue", "__e32_atomic_", "User::After")):
        raise SystemExit("worker/queue residue in WServ")
    return text


def patch_client(text: str) -> str:
    scripts = Path(__file__).parent
    life = runpy.run_path(str(scripts / "apply-htcleo-home-liveness-evidence.py"))
    handoff = runpy.run_path(str(scripts / "apply-htcleo-wserv-shell-handoff-trace.py"))
    before = text
    had_handoff = handoff["MARKER"] in text
    if had_handoff:
        for old, new in (
            (handoff["NEW_ORDINAL"], handoff["OLD_ORDINAL"]),
            (handoff["REPLY_START"] + handoff["REPLY_PREFIX"], handoff["REPLY_START"]),
            (handoff["REPLY_SUFFIX"], ""),
        ):
            if text.count(old) != 1:
                raise SystemExit("744 command/reply inverse mismatch")
            text = text.replace(old, new, 1)
    had_home_exit = life["EXIT_MARKER"] in text
    old_prefix = ("\t// HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
                  "\tif (SecureId().iId==0x101F4CD2u)\n\t\t{\n")
    if had_home_exit:
        new_prefix = life["patch_client"](old_prefix)
        if text.count(new_prefix) != 1:
            raise SystemExit("743 Home exit inverse mismatch")
        text = text.replace(new_prefix, old_prefix, 1)
    restored = life["patch_client"](text) if had_home_exit else text
    restored = handoff["patch_client"](restored) if had_handoff else restored
    if restored != before:
        raise SystemExit("client inverse changed underlying behavior")
    return text


def patch_event(text: str) -> str:
    marker = "\t// HTCLEO_WSERV_HOME_HEARTBEAT_SAMPLE_V1"
    if marker not in text:
        return text
    before = text
    start = text.index(marker)
    end = text.index("\tself->iHtcleoProbeTicks =", start)
    text = text[:start] + text[end:]
    if "RProperty::" not in text:
        text = text.replace("#include <e32property.h>\n", "", 1)
    life = runpy.run_path(str(Path(__file__).with_name("apply-htcleo-home-liveness-evidence.py")))
    if life["patch_event"](text) != before:
        raise SystemExit("event inverse changed the actual input receiver")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--pin-binary", nargs=2, type=Path, metavar=("REBUILT", "CONTROL"))
    args = parser.parse_args()
    path = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/WSTOP.CPP"
    before = path.read_text(encoding="utf-8")
    after = patch(before)
    if patch(after) != after:
        raise SystemExit("worker retirement is not idempotent")
    if before[before.index(END):] != after[after.index(END):]:
        raise SystemExit("server/scheduler code changed outside logger")
    client_path = path.with_name("CLIENT.CPP")
    event_path = path.parent.parent / "EVENT.CPP"
    client = patch_client(client_path.read_text(encoding="utf-8"))
    event = patch_event(event_path.read_text(encoding="utf-8"))
    if patch_client(client) != client or patch_event(event) != event:
        raise SystemExit("742 control is not idempotent")
    if not args.check_only and not args.pin_binary:
        path.write_text(after, encoding="utf-8")
        client_path.write_text(client, encoding="utf-8")
        event_path.write_text(event, encoding="utf-8")
    if args.pin_binary:
        if args.check_only:
            raise SystemExit("pin-binary and check-only are mutually exclusive")
        pin_control(args.root, *args.pin_binary)
    print("HTCLEO_WSERV_NONBLOCKING_LOG=retired-exact742-wserv-component-control")


if __name__ == "__main__":
    main()
