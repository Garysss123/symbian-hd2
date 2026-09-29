#!/usr/bin/env python3
"""Retire MatrixMenu's now-redundant direct top-view activation."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_POST_CONTAINER_VIEW_RETIRE_V1"
LEGACY_MARKER = "HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW_V1"


OLD = r'''    // HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW_V1
	const TBool htcleoDirectStartupView =
		(htcleoNeedsViewActivator &&
		 RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE366u, htcleoDirectStartupView);
	if (htcleoDirectStartupView)
		{
		HtcleoEikCorePreFactoryTrace(0xE367u, KErrNone);
		appUi.ActivateTopViewL();
		HtcleoEikCorePreFactoryTrace(0xE368u, KErrNone);
		}
	else if (htcleoNeedsViewActivator)
		{
		iEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);
		}
	if (htcleoNeedsViewActivator)
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);'''
OLD = OLD.replace("    //", "\t//", 1)


NEW = r'''    // HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW_V1
	// HTCLEO_EIKCORE_MATRIXMENU_POST_CONTAINER_VIEW_RETIRE_V1
	// MatrixMenu now commits and draws its real five-item container during
	// ConstructL.  A second ActivateTopViewL after that first frame replaces
	// the working container.  Retire only that duplicate MatrixMenu action;
	// other applications retain the stock asynchronous view activator.
	const TBool htcleoRetireStartupView =
		(htcleoNeedsViewActivator &&
		 RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE366u, htcleoRetireStartupView);
	if (htcleoRetireStartupView)
		{
		HtcleoEikCorePreFactoryTrace(0xE367u, KErrNotSupported);
		HtcleoEikCorePreFactoryTrace(0xE368u, KErrNone);
		}
	else if (htcleoNeedsViewActivator)
		{
		iEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);
		}
	if (htcleoNeedsViewActivator)
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);'''
NEW = NEW.replace("    //", "\t//", 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    if text.count(OLD) != 1:
        raise SystemExit(
            "MatrixMenu startup-view retire: expected one direct branch, "
            f"found {text.count(OLD)}"
        )
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "legacy marker": text.count(LEGACY_MARKER) == 1,
        "retire marker": text.count(MARKER) == 1,
        "MatrixMenu scope": text.count(
            "const TBool htcleoRetireStartupView ="
        ) == 1 and text.count("0x101f4cd2u") >= 1,
        "duplicate direct activation gone": (
            text.count("appUi.ActivateTopViewL();") == 0
        ),
        "stock async retained": (
            text.count("CEikStartUpViewActivator::NewL(appUi, *this,") == 1
            and text.count("iAppUi.ActivateTopViewL();") == 1
        ),
        "stages retained": all(
            text.count(f"0xE{stage:03X}u") == 1
            for stage in range(0x366, 0x369)
        ),
        "honest retirement": text.count(
            "HtcleoEikCorePreFactoryTrace(0xE367u, KErrNotSupported);"
        ) == 1,
        "no fake or wait": all(
            token not in NEW for token in ("User::After", "RTimer", "RunIfReady")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu startup-view retirement verification failed: "
            + ", ".join(failed)
        )


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
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW="
        "retired-after-real-container-e366-e368-async-other-apps-stock"
    )


if __name__ == "__main__":
    main()
