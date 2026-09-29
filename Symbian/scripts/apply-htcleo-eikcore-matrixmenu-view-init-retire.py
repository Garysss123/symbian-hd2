#!/usr/bin/env python3
"""Retire empty Avkon view-manager initialization for MatrixMenu.

MatrixMenu owns a classic real container rather than registered Avkon views.
Hardware iteration 546 proved ActivateTopViewL has no registered view, while
590 proves a final full 360x640 white redraw replaces the completed real menu.
Skip only MatrixMenu's post-ConstructL CheckInitializeViewsL call; other apps,
commands and view-manager behavior remain stock.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_VIEW_INIT_RETIRE_V1"
PREREQUISITES = (
    "HTCLEO_EIKCORE_POSTAPPUI_TRACE_V1",
    "HTCLEO_EIKCORE_MATRIXMENU_POST_CONTAINER_VIEW_RETIRE_V1",
)

OLD = r'''	// Unless we are running the application without views, initialize the view manager
	const TBool runAppWithoutViews = (command==EApaCommandRunWithoutViews || command==EApaCommandBackgroundAndWithoutViews);
	HtcleoEikCorePreFactoryTrace(0xE328u, runAppWithoutViews);
	if (!runAppWithoutViews)
		{
		HtcleoEikCorePreFactoryTrace(0xE329u, KErrNone);
		appUi.CheckInitializeViewsL(appUi.Application()->AppDllUid());
		HtcleoEikCorePreFactoryTrace(0xE32Au, KErrNone);
		}
'''

NEW = r'''	// Unless we are running the application without views, initialize the view manager
	const TBool runAppWithoutViews = (command==EApaCommandRunWithoutViews || command==EApaCommandBackgroundAndWithoutViews);
	HtcleoEikCorePreFactoryTrace(0xE328u, runAppWithoutViews);
	// HTCLEO_EIKCORE_MATRIXMENU_VIEW_INIT_RETIRE_V1
	// MatrixMenu has no registered Avkon view; its real classic container is
	// already constructed and committed.  Do not replace it with an empty
	// view-manager redraw.  All other applications retain stock initialization.
	const TBool htcleoRetireEmptyMatrixMenuViewInit =
		(!runAppWithoutViews &&
		 RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE369u,
		htcleoRetireEmptyMatrixMenuViewInit);
	if (!runAppWithoutViews && !htcleoRetireEmptyMatrixMenuViewInit)
		{
		HtcleoEikCorePreFactoryTrace(0xE329u, KErrNone);
		appUi.CheckInitializeViewsL(appUi.Application()->AppDllUid());
		HtcleoEikCorePreFactoryTrace(0xE32Au, KErrNone);
		}
	else if (htcleoRetireEmptyMatrixMenuViewInit)
		{
		HtcleoEikCorePreFactoryTrace(0xE36Au, KErrNotSupported);
		}
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    if not path.is_file():
        raise SystemExit(f"missing EIKENV source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise SystemExit(
                "MatrixMenu view-init retire: expected one view block, "
                f"found {text.count(OLD)}"
            )
        text = text.replace(OLD, NEW, 1)

    checks = {
        "prerequisites": all(text.count(item) == 1 for item in PREREQUISITES),
        "single marker": text.count(MARKER) == 1,
        "MatrixMenu exact SID": NEW.count("0x101f4cd2u") == 1,
        "real call retained": text.count(
            "appUi.CheckInitializeViewsL(appUi.Application()->AppDllUid());"
        ) == 1,
        "other apps stock branch": text.count(
            "if (!runAppWithoutViews && !htcleoRetireEmptyMatrixMenuViewInit)"
        ) == 1,
        "honest retirement": text.count(
            "HtcleoEikCorePreFactoryTrace(0xE36Au, KErrNotSupported);"
        ) == 1,
        "stages": all(
            text.count(f"0xE{stage:03X}u") == 1
            for stage in (0x369, 0x36A)
        ),
        "no wait trap or fake view": all(
            token not in NEW
            for token in (
                "User::After",
                "RTimer",
                "TRAP_IGNORE",
                "ActivateTopViewL",
                "CreateWindowL",
                "MakeVisible",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu view-init retirement verification failed: "
            + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_MATRIXMENU_VIEW_INIT="
        "retired-empty-avkon-view-e369-e36a-other-apps-stock"
    )


if __name__ == "__main__":
    main()
