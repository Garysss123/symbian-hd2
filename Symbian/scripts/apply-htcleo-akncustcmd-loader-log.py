#!/usr/bin/env python3
"""Retarget the proven HTCLEO EFILE trace to ``akncustcmds.dll``.

The dense loader instrumentation itself is unchanged.  This transform only
changes its exact top-level basename gate, durable filename and cleanup tag
from the already-proven NVG request to the iteration-433 frontier.  It adds no
loader policy, retry, delay, file-system session or result reclassification.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCUSTCMD_LOADER_RETARGET_V1"
BASE_MARKER = "HTCLEO_LOADER_DURABLE_LOG_V1"
TAIL_MARKER = "HTCLEO_LOADER_COMPLETION_TAIL_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(root: Path) -> None:
    sfile = root / "userlibandfileserver/fileserver/sfile"
    logger = (sfile / "HtcleoLoaderLog.cpp").read_text(encoding="utf-8")
    loader = (sfile / "sf_ldr.cpp").read_text(encoding="utf-8")
    combined = logger + loader
    checks = {
        "retarget marker": logger.count(MARKER) == 1,
        "base marker": logger.count(BASE_MARKER) == 1,
        "completion tail": loader.count(TAIL_MARKER) == 1,
        "exact logger target": logger.count('"akncustcmds.dll"') == 1,
        "exact cleanup target": loader.count('"akncustcmds.dll"') == 1,
        "old target retired": '"nvgrenderstage.dll"' not in combined,
        "new path": logger.count("C:\\\\Symbian3\\\\AKNLDR.TXT") == 1,
        "old path retired": "C:\\\\Symbian3\\\\LDRLOG.TXT" not in logger,
        "single stop": loader.count("HtcleoLoaderTraceStop();") == 1,
        "all tail stages": all(
            loader.count(f"0x000060{value:02X}u") == 1
            for value in range(1, 12)
        ),
        "existing fs only": "gTheLoaderFs" in logger and "RFs fs" not in logger,
        "durable writes": (
            "file.Write(record)" in logger and "file.Flush()" in logger
        ),
        "no waits": (
            "User::After" not in logger
            and "User::WaitForRequest" not in logger
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "akncustcmd loader retarget verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="kernelhwsrv source root")
    args = parser.parse_args()
    sfile = args.root / "userlibandfileserver/fileserver/sfile"
    logger_path = sfile / "HtcleoLoaderLog.cpp"
    loader_path = sfile / "sf_ldr.cpp"
    if not logger_path.is_file() or not loader_path.is_file():
        raise SystemExit("installed EFILE durable-loader sources are missing")

    logger = logger_path.read_text(encoding="utf-8")
    loader = loader_path.read_text(encoding="utf-8")
    if MARKER in logger:
        verify(args.root)
        print(
            "HTCLEO_AKNCUSTCMD_LOADER_LOG=installed "
            "gate=akncustcmds.dll path=C:\\Symbian3\\AKNLDR.TXT"
        )
        return

    if BASE_MARKER not in logger or TAIL_MARKER not in loader:
        raise SystemExit(
            "proven loader durable-log and completion-tail transforms "
            "must be installed first"
        )

    logger = replace_once(
        logger,
        "// HTCLEO_LOADER_DURABLE_LOG_V1\n",
        "// HTCLEO_LOADER_DURABLE_LOG_V1\n"
        f"// {MARKER}\n",
        "retarget marker",
    )
    logger = replace_once(
        logger,
        '_LIT8(KHtcleoNvgDll, "nvgrenderstage.dll");',
        '_LIT8(KHtcleoNvgDll, "akncustcmds.dll");',
        "exact basename gate",
    )
    logger = replace_once(
        logger,
        "C:\\\\Symbian3\\\\LDRLOG.TXT",
        "C:\\\\Symbian3\\\\AKNLDR.TXT",
        "durable log path",
    )
    loader = replace_once(
        loader,
        '_LIT8(KHtcleoLoaderTailName, "nvgrenderstage.dll");',
        '_LIT8(KHtcleoLoaderTailName, "akncustcmds.dll");',
        "cleanup record target",
    )

    logger_path.write_text(logger, encoding="utf-8", newline="\n")
    loader_path.write_text(loader, encoding="utf-8", newline="\n")
    verify(args.root)
    print(
        "HTCLEO_AKNCUSTCMD_LOADER_LOG=installed "
        "gate=akncustcmds.dll path=C:\\Symbian3\\AKNLDR.TXT"
    )


if __name__ == "__main__":
    main()
