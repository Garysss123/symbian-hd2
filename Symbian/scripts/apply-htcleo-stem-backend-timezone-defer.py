#!/usr/bin/env python3
"""Defer only an unavailable TZ server during HTCLEO UI bring-up.

The stock OpenC backend treats every RTz connection failure as a fatal process
attach panic. On HTCLEO the server repeatedly terminates during early WServ
startup. Keep every other constructor error fatal, retain the closed RTz
session for later repair, and durably identify the accepted narrow fallback.
"""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE_MARKER = "HTCLEO_STEM_BACKEND_TIMEZONE_DEFER_V1"
MMP_MARKER = "HTCLEO_STEM_BACKEND_TIMEZONE_DEFER_MMP_V1"
MACRO = "__HTCLEO_STEM_BACKEND_TIMEZONE_DEFER__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install_mmp(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MMP_MARKER not in text:
        text = replace_once(
            text,
            "MACRO __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n",
            "MACRO __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
            f"MACRO {MACRO} // {MMP_MARKER}\n",
            "backend MMP macro",
        )
        path.write_text(text, encoding="utf-8")

    installed = path.read_text(encoding="utf-8")
    if installed.count(MMP_MARKER) != 1 or installed.count(f"MACRO {MACRO}") != 1:
        raise SystemExit("STEM timezone-defer MMP verification failed")


def install_source(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if SOURCE_MARKER not in text:
        old = (
            "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
            "\t\tHtcleoStemBackendLog(0x0000D122u, err, 0u);\n"
            "\t\tHtcleoStemBackendLog(0x0000D123u, err, 0u);\n"
            "#endif\n\n\n"
            "\t\t//Panic if any of the above operation returns with error\n"
        )
        new = (
            "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
            "\t\tHtcleoStemBackendLog(0x0000D122u, err, 0u);\n"
            "\t\tHtcleoStemBackendLog(0x0000D123u, err, 0u);\n"
            "#endif\n\n"
            f"#ifdef {MACRO}\n"
            f"\t\t// {SOURCE_MARKER}\n"
            "\t\t// A missing or repeatedly terminated TZ server affects only OpenC\n"
            "\t\t// localtime/mktime. Keep every other constructor error fatal.\n"
            "\t\tif (err == KErrNotFound || err == KErrServerTerminated)\n"
            "\t\t\t{\n"
            "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
            "\t\t\tHtcleoStemBackendLog(0x0000D125u, err, 1u);\n"
            "#endif\n"
            "\t\t\tiTzServer.Close();\n"
            "\t\t\terr = KErrNone;\n"
            "\t\t\t}\n"
            "#endif\n\n"
            "\t\t//Panic if any of the above operation returns with error\n"
        )
        text = replace_once(text, old, new, "timezone policy anchor")
        path.write_text(text, encoding="utf-8")

    installed = path.read_text(encoding="utf-8")
    required = (
        SOURCE_MARKER,
        f"#ifdef {MACRO}",
        "err == KErrNotFound || err == KErrServerTerminated",
        "HtcleoStemBackendLog(0x0000D125u, err, 1u);",
    )
    for needle in required:
        if installed.count(needle) != 1:
            raise SystemExit(f"STEM timezone-defer source verification failed: {needle}")
    # One close belongs to the original destructor and one to the narrow
    # constructor fallback. Anything else indicates transform drift.
    if installed.count("iTzServer.Close();") != 2:
        raise SystemExit("STEM timezone-defer RTz close-count verification failed")
    if installed.count("iTzServer.Close();\n\t\t\terr = KErrNone;\n\t\t\t}") != 1:
        raise SystemExit("STEM timezone-defer exact reset block verification failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    source = (
        root
        / "sf/os/ossrv/genericopenlibs/openenvcore/backend/src/corebackend/localif.cpp"
    )
    mmp = root / "sf/incubator/stemkit/breakdeps/backend.mmp"
    if not source.is_file() or not mmp.is_file():
        raise SystemExit(f"missing STEM backend source: {source} / {mmp}")

    install_source(source)
    install_mmp(mmp)
    print(
        "HTCLEO_STEM_BACKEND_TIMEZONE_DEFER=installed "
        "accepted=KErrNotFound,KErrServerTerminated stage=D125"
    )


if __name__ == "__main__":
    main()
