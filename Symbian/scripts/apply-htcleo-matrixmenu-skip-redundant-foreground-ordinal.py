#!/usr/bin/env python3
"""Do not reorder MatrixMenu when its root window group already has focus."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_REDUNDANT_FOREGROUND_ORDINAL_SKIP_V1"
PREREQUISITE = "HTCLEO_MATRIXMENU_FOREGROUND_ORDINAL_NO_SYSTEM_EVENT_V1"
FOCUS_RESTORE = "HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1"
STATE_ONLY_FOCUS = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2"


OLD = r'''    const TInt htcleoOrdinalResult =
        htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0);
    HtcleoMenuLog(0x4D4D0355u, htcleoOrdinalResult,
        (TUint32)htcleoRootWg);'''


NEW = r'''    // HTCLEO_MATRIXMENU_REDUNDANT_FOREGROUND_ORDINAL_SKIP_V1
    // Hardware 664 reports focus WG == root WG before this operation.  A
    // redundant reorder creates a gain/lost/gain event cycle, so only issue
    // the real WServ ordinal request when another group actually has focus.
    TInt htcleoOrdinalResult = KErrNone;
    const TBool htcleoOrdinalIssued = htcleoFocusBefore != htcleoRootWg;
    if (htcleoOrdinalIssued)
        {
        htcleoOrdinalResult =
            htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0);
        }
    HtcleoMenuLog(0x4D4D0355u, htcleoOrdinalResult,
        (TUint32)htcleoRootWg);
    HtcleoMenuLog(0x4D4D0356u, KErrNone,
        htcleoOrdinalIssued ? 1u : 0u);'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("ordinal-only foreground prerequisite is missing")
    count = text.count(OLD)
    if count != 1:
        raise SystemExit(f"redundant ordinal anchor: expected one, found {count}")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "markers": text.count(MARKER) == 1 and text.count(PREREQUISITE) == 1,
        "focus comparison": text.count(
            "htcleoFocusBefore != htcleoRootWg"
        ) == (1 if FOCUS_RESTORE in text or STATE_ONLY_FOCUS in text else 2),
        "single startup ordinal call": text.count(
            "htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)"
        ) == 1,
        "stages": (
            text.count("0x4D4D0355u") == 1
            and text.count("0x4D4D0356u") == 1
        ),
        "no synthetic event": (
            "htcleoTask.BringToForeground();" not in text
            and "htcleoMenuTask.BringToForeground();" not in text
        ),
        "no delay or fabricated UI": all(
            token not in NEW
            for token in ("User::After", "RTimer", "CreateWindowL", "SetPixel")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu redundant ordinal skip verification failed: "
            + "; ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu AppUi source: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_REDUNDANT_FOREGROUND_ORDINAL="
        "skip-when-focus-equals-root-0355-0356"
    )


if __name__ == "__main__":
    main()
