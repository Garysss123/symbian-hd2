#!/usr/bin/env python3
"""Keep only touch and fatal WServ records after startup bring-up passes."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_TOUCH_ONLY_LOG_V1"
PREREQUISITE = "HTCLEO_WSERV_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if text.count(PREREQUISITE) != 1:
        raise SystemExit("WServ durable-log prerequisite is missing")
    if MARKER in text:
        return text
    return replace_once(
        text,
        '''void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
\t{
\t// HTCLEO_WSERV_LOG_CAPACITY_512_V1''',
        '''void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
\t{
\t// HTCLEO_WSERV_TOUCH_ONLY_LOG_V1
\tconst TBool htcleoTouchStage =
\t\taStage >= 0x0000045Au && aStage <= 0x00000465u;
\tconst TBool htcleoFatalStage =
\t\taStage >= 0x0000046Cu && aStage <= 0x00000476u;
\tif (!htcleoTouchStage && !htcleoFatalStage)
\t\t{
\t\treturn;
\t\t}
\t// HTCLEO_WSERV_LOG_CAPACITY_512_V1''',
        "WServ stage allowlist",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "touch range": (
            text.count("aStage >= 0x0000045Au") == 1
            and text.count("aStage <= 0x00000465u") == 1
        ),
        "fatal range": (
            text.count("aStage >= 0x0000046Cu") == 1
            and text.count("aStage <= 0x00000476u") == 1
        ),
        "writer retained": (
            text.count("file.Write(record)") == 1
            and text.count("file.Flush()") == 1
            and text.count(r"C:\\Symbian3\\WSLOG.TXT") == 1
        ),
        "capacity": (
            text.count("gHtcleoWsLogSequence >= 512") == 1
            or ("HTCLEO_WSERV_LOG_RING_1M_V1" in text
                and "KCapacity = 1048576" in text)
        ),
        "no event behavior change": all(
            token not in text[text.index(f"// {MARKER}"):text.index("// HTCLEO_WSERV_LOG_CAPACITY", text.index(f"// {MARKER}"))]
            for token in ("User::After", "RTimer", "RequestComplete", "TRAP")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("WServ touch-only log audit failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/WSTOP.CPP"
    )
    if not path.is_file():
        raise SystemExit(f"missing WServ logger source: {path}")
    text = patch(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_WSERV_TOUCH_ONLY_LOG="
        "WSLOG-045a-0465-touch-046c-0476-fatal-startup-retired"
    )


if __name__ == "__main__":
    main()
