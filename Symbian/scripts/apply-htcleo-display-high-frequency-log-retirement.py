#!/usr/bin/env python3
"""Retire per-frame DSPR FAT writes after the display path is proven."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_DISPLAY_HIGH_FREQUENCY_LOG_RETIREMENT_V1"
PREREQUISITE = "HTCLEO_DISPLAY_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if text.count(PREREQUISITE) != 1:
        raise SystemExit("display durable-log prerequisite is missing")
    if MARKER in text:
        return text
    return replace_once(
        text,
        '''void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
\t{
\tRFs fs;''',
        '''void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
\t{
\t// HTCLEO_DISPLAY_HIGH_FREQUENCY_LOG_RETIREMENT_V1
\t// Keep one component-load marker; HSLOG supplies the low-rate UI heartbeat.
\tif ((aStage & 0xFFFFu) != 0x1000u)
\t\t{
\t\treturn;
\t\t}
\tRFs fs;''',
        "DSPR stage allowlist",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "startup-only gate": text.count(
            "(aStage & 0xFFFFu) != 0x1000u"
        ) == 1,
        "writer retained": (
            text.count("HtcleoDsprLog(TUint32 aStage") == 2
            and text.count("file.Write(record)") == 1
            and text.count(r"C:\\Symbian3\\DSPRLOG.TXT") == 1
        ),
        "all render calls retained": text.count("HtcleoDsprLog(") > 3,
        "no render behavior change": all(
            token not in text[text.index(f"// {MARKER}"):text.index("RFs fs;", text.index(f"// {MARKER}"))]
            for token in ("User::After", "RTimer", "TRAP", "SetHandle")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "display log-retirement audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/os/graphics/windowing/windowserverplugins/openwfc/src/stdplugin.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing display logger source: {path}")
    text = patch(path.read_text(encoding="latin-1"))
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_DISPLAY_HIGH_FREQUENCY_LOG_RETIREMENT="
        "DSPR-stage1000-only-per-frame-fat-writes-retired"
    )


if __name__ == "__main__":
    main()
