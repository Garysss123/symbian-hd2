#!/usr/bin/env python3
"""Retire per-node HSPS tracing and keep nonempty map completions."""

from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "HTCLEO_HSPSPROVIDER_LOG_RETIREMENT_V1"
OLD = '''    if (RProcess().SecureId().iId != 0x102750f0u)
        return;
    RFs fs;'''
NEW = '''    if (RProcess().SecureId().iId != 0x102750f0u)
        return;
    // HTCLEO_HSPSPROVIDER_LOG_RETIREMENT_V1
    // No writable static data in this DLL. Empty-node enumeration is noisy;
    // retain only completion of the few real nonempty plugin lists.
    if ((aStage & 0xffu) != 0x15u || aDetail == 0u)
        return;
    RFs fs;'''


def patch(text: str) -> str:
    if MARKER in text and "static TUint32 htcleoSeen" in text:
        start = text.index("    // " + MARKER)
        end = text.index("    RFs fs;", start)
        text = text[:start] + NEW[NEW.index("    // " + MARKER):] + text[end + len("    RFs fs;"):]
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise SystemExit("HSPS provider logger anchor mismatch")
        text = text.replace(OLD, NEW, 1)
    if text.count(NEW) != 1:
        raise SystemExit("HSPS provider log-retirement verification failed")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/mw/homescreensrv/homescreensrv_plat/sapi_homescreenplugin/src/hspsliwutilities.cpp"
    path.write_text(patch(path.read_text(encoding="utf-8")), encoding="utf-8")
    print("HTCLEO_HSPSPROVIDER_LOG_RETIREMENT=nonempty-completion-only-no-map-change")


if __name__ == "__main__":
    main()
