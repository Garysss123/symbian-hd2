#!/usr/bin/env python3
"""Use Haze's real full-screen item for the MatrixMenu background.

The stock MatrixMenu asks for ``QsnBgAreaMainAppsGrid``.  The Haze source skin
does not define that item; it defines ``QsnBgScreen`` and
``QsnBgScreenIdle``.  On the current HTC Leo UI-first stack the missing area
item therefore falls back to the sparse product skin and stays white even
though Skin Server has successfully merged Haze.  Select the existing Haze
screen item without fabricating pixels or changing any widget/window logic.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MMWIDGETS_HAZE_SCREEN_BACKGROUND_V1"

OLD = r'''    iBgContext = CAknsBasicBackgroundControlContext::NewL(
            KAknsIIDQsnBgAreaMainAppsGrid, Rect(), EFalse );'''

NEW = r'''    // HTCLEO_MMWIDGETS_HAZE_SCREEN_BACKGROUND_V1
    iBgContext = CAknsBasicBackgroundControlContext::NewL(
            KAknsIIDQsnBgScreen, Rect(), EFalse );'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/mmwidgets/src/"
        "mmwidgetcontainer.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MMWidgets source: {path}")

    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "MMWidgets Haze background: expected one stock context, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    checks = {
        "single marker": text.count(MARKER) == 1,
        "screen item selected": text.count(
            "KAknsIIDQsnBgScreen, Rect(), EFalse"
        ) == 1,
        "old area item retired here": OLD not in text,
        "background context retained": text.count(
            "CAknsBasicBackgroundControlContext::NewL("
        ) >= 1,
        "no fabricated pixels": all(
            token not in NEW
            for token in ("Mem::Fill", "SetBrushColor", "Clear(", "User::After")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MMWidgets Haze background verification failed: "
            + ", ".join(failed)
        )

    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_MMWIDGETS_HAZE_BACKGROUND="
        "qsn-bg-screen-existing-haze-item-no-fabricated-pixels"
    )


if __name__ == "__main__":
    main()
