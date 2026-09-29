#!/usr/bin/env python3
"""Commit MatrixMenu's first fully constructed frame on HTC Leo.

Iteration 557 proves the real grid window, model, drawer, container, control
stack, visibility, DrawNow and DrawView all complete, while the display,
OpenWFC and NVG logs remain byte-identical to the pre-grid baseline.  Request
the standard WServ Finish boundary once after the first DrawView so all queued
drawing is processed and Screen::DoRedrawNow commits the initial frame.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_FIRST_FRAME_FINISH_V1"


OLD = r'''    iCurrentContainer->DrawView();
    HtcleoMenuLog(0x4D4D0318u, KErrNone, 1u);'''


NEW = r'''    iCurrentContainer->DrawView();
    HtcleoMenuLog(0x4D4D0318u, KErrNone, 1u);

    // HTCLEO_MATRIXMENU_FIRST_FRAME_FINISH_V1
    HtcleoMenuLog(0x4D4D0319u, KErrNone, 0u);
    const TInt htcleoFirstFrameFinish = iCoeEnv->WsSession().Finish();
    HtcleoMenuLog(0x4D4D031Au, htcleoFirstFrameFinish, 0u);
    User::LeaveIfError(htcleoFirstFrameFinish);'''


def install(source: str) -> str:
    if MARKER in source:
        return source
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"first-frame anchor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "real draw retained": source.count(
            "iCurrentContainer->DrawView();"
        ) >= 1,
        "finish once": source.count(
            "const TInt htcleoFirstFrameFinish = iCoeEnv->WsSession().Finish();"
        ) == 1,
        "pre log": source.count(
            "HtcleoMenuLog(0x4D4D0319u, KErrNone, 0u);"
        ) == 1,
        "result log": source.count(
            "HtcleoMenuLog(0x4D4D031Au, htcleoFirstFrameFinish, 0u);"
        ) == 1,
        "fail closed": source.count(
            "User::LeaveIfError(htcleoFirstFrameFinish);"
        ) == 1,
        "no normalization": (
            "TRAP" not in NEW
            and "htcleoFirstFrameFinish = KErrNone" not in NEW
            and "User::After" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    source = source_path.read_text(encoding="utf-8")
    source = install(source)
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_MATRIXMENU_FIRST_FRAME_FINISH="
        "post-drawview-wserv-finish-0319-031a-failclosed"
    )


if __name__ == "__main__":
    main()
