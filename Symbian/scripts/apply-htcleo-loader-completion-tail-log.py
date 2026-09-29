#!/usr/bin/env python3
"""Extend the exact NVG EFILE trace through cleanup and IPC completion.

Iteration 415 proved that the internal ``LoadLibrary`` path returned success,
but the ECom client did not reach its post-``RLibrary::Load`` checkpoint.  This
transform keeps the existing exact-basename gate armed until the loader request
has closed its temporary handles and completed the client message.  It adds no
new file-system session, delay, retry, display call, UDF, or policy change.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_LOADER_COMPLETION_TAIL_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    stages = tuple(f"000060{value:02X}" for value in range(1, 12))
    checks = {
        "marker": text.count(MARKER) == 1,
        "tail name": text.count('KHtcleoLoaderTailName') == 12,
        "stages": all(text.count(f"0x{stage}u") == 1 for stage in stages),
        "single late stop": text.count("HtcleoLoaderTraceStop();") == 1,
        "old scoped gate removed": "htcleoLoaderTrace" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("loader completion-tail verification failed: " +
                         ", ".join(failed))

    close_order = [text.index(f"0x000060{value:02X}u")
                   for value in range(2, 8)]
    if close_order != sorted(close_order):
        raise SystemExit("RLdrReq cleanup checkpoints are not in source order")
    tail_order = [text.index("0x00006001u")] + [
        text.index(f"0x000060{value:02X}u") for value in range(8, 12)]
    if tail_order != sorted(tail_order):
        raise SystemExit("outer completion checkpoints are not in source order")
    complete_pos = text.rindex("aMessage.Complete(r);")
    if text.index("0x0000600Au") > complete_pos:
        raise SystemExit("pre-complete checkpoint is not before Complete")
    if text.index("0x0000600Bu") < complete_pos:
        raise SystemExit("post-complete checkpoint is not after Complete")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="kernelhwsrv source root")
    args = parser.parse_args()
    path = (args.root /
            "userlibandfileserver/fileserver/sfile/sf_ldr.cpp")
    logger = (args.root /
              "userlibandfileserver/fileserver/sfile/HtcleoLoaderLog.cpp")
    if not path.is_file() or not logger.is_file():
        raise SystemExit("loader durable-log V1 must be installed first")

    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        verify(path)
        print("HTCLEO_LOADER_COMPLETION_TAIL=installed stages=06001-0600B")
        return

    if "HTCLEO_LOADER_DURABLE_LOG_V1" not in logger.read_text(
            encoding="utf-8"):
        raise SystemExit("loader durable-log V1 marker is absent")

    text = replace_once(
        text,
        '#include "HtcleoLoaderLog.h"\n',
        '#include "HtcleoLoaderLog.h"\n'
        f'// {MARKER}\n'
        '_LIT8(KHtcleoLoaderTailName, "nvgrenderstage.dll");\n',
        "completion-tail marker")

    text = replace_once(
        text,
        '''\t\t\tTBool htcleoLoaderTrace = EFalse;\n''',
        "",
        "scoped trace flag")
    text = replace_once(
        text,
        '''\t\t\t\thtcleoLoaderTrace = HtcleoLoaderTraceStart(*ldrReq.iFileName);\n''',
        '''\t\t\t\tHtcleoLoaderTraceStart(*ldrReq.iFileName);\n''',
        "trace start assignment")
    text = replace_once(
        text,
        '''\t\t\tif(htcleoLoaderTrace)\n\t\t\t\tHtcleoLoaderTraceStop();\n''',
        "",
        "early trace stop")

    text = replace_once(
        text,
        '''void RLdrReq::Close()\n\t{\n\tdelete iFileName;\n\tdelete iCmd;\n\tdelete iPath;\n\tiClientThread.Close();\n\tiClientProcess.Close();\n\t}\n''',
        '''void RLdrReq::Close()\n\t{\n\tHtcleoLoaderLog(0x00006002u, KErrNone, KHtcleoLoaderTailName,\n\t\t\t(iFileName ? 1u : 0u) | (iCmd ? 2u : 0u) |\n\t\t\t(iPath ? 4u : 0u));\n\tdelete iFileName;\n\tHtcleoLoaderLog(0x00006003u, KErrNone, KHtcleoLoaderTailName, 0u);\n\tdelete iCmd;\n\tHtcleoLoaderLog(0x00006004u, KErrNone, KHtcleoLoaderTailName, 0u);\n\tdelete iPath;\n\tHtcleoLoaderLog(0x00006005u, KErrNone, KHtcleoLoaderTailName, 0u);\n\tiClientThread.Close();\n\tHtcleoLoaderLog(0x00006006u, KErrNone, KHtcleoLoaderTailName, 0u);\n\tiClientProcess.Close();\n\tHtcleoLoaderLog(0x00006007u, KErrNone, KHtcleoLoaderTailName, 0u);\n\t}\n''',
        "RLdrReq cleanup stages")

    text = replace_once(
        text,
        '''\t\tdefault:\n\t\t\tr=KErrNotSupported;\n\t\t\tbreak;\n\t\t}\n\t\n\tldrReq.Close();\n''',
        '''\t\tdefault:\n\t\t\tr=KErrNotSupported;\n\t\t\tbreak;\n\t\t}\n\n\tHtcleoLoaderLog(0x00006001u, r, KHtcleoLoaderTailName, (TUint32)mid);\n\tldrReq.Close();\n\tHtcleoLoaderLog(0x00006008u, r, KHtcleoLoaderTailName, 0u);\n''',
        "switch-to-cleanup boundary")

    text = replace_once(
        text,
        '''error:\n#ifdef _DEBUG\n\tgTheLoaderFs.ResourceCountMarkEnd();\n#endif\n\tif (!aMessage.IsNull())\n\t\t{\n\t\t__IF_DEBUG(Printf("Loader: msg complete %d", r));\n\t\taMessage.Complete(r);\n\t\t}\n\t}\n''',
        '''error:\n#ifdef _DEBUG\n\tgTheLoaderFs.ResourceCountMarkEnd();\n#endif\n\tHtcleoLoaderLog(0x00006009u, r, KHtcleoLoaderTailName,\n\t\t\taMessage.IsNull() ? 1u : 0u);\n\tif (!aMessage.IsNull())\n\t\t{\n\t\t__IF_DEBUG(Printf("Loader: msg complete %d", r));\n\t\tHtcleoLoaderLog(0x0000600Au, r, KHtcleoLoaderTailName, 0u);\n\t\taMessage.Complete(r);\n\t\tHtcleoLoaderLog(0x0000600Bu, r, KHtcleoLoaderTailName, 0u);\n\t\t}\n\tHtcleoLoaderTraceStop();\n\t}\n''',
        "message completion stages")

    path.write_text(text, encoding="utf-8", newline="\n")
    verify(path)
    print("HTCLEO_LOADER_COMPLETION_TAIL=installed stages=06001-0600B")


if __name__ == "__main__":
    main()
