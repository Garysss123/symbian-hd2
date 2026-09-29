#!/usr/bin/env python3
"""Activate MatrixMenu's real top view synchronously before Execute.

Iterations 542-545 prove that application construction succeeds and that the
stock startup-view active object is created, armed, completed, signalled and
raised above other normal priorities, yet the MatrixMenu scheduler never
dispatches its RunL.  With the frontier reduced to this one compatibility
boundary, perform the same real CEikAppUi::ActivateTopViewL() call directly
after CheckInitializeViewsL() for MatrixMenu.

The call remains leaving/fail-closed: application construction only succeeds
if real view activation returns.  MatrixMenu does not create the redundant
async activator, avoiding double activation.  Other applications retain the
stock async path.  No dummy view, render bypass, input bypass or fake success
is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW_V1"
PREREQUISITE = "HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY_V1"
RETIRE_MARKER = "HTCLEO_EIKCORE_MATRIXMENU_POST_CONTAINER_VIEW_RETIRE_V1"


OLD = r'''	const TBool htcleoNeedsViewActivator =
		(startAppInForeground && command!=EApaCommandViewActivate);
	HtcleoEikCorePreFactoryTrace(0xE32Bu, htcleoNeedsViewActivator);
	if (htcleoNeedsViewActivator)
		{
		iEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);
		}
'''


NEW = r'''	const TBool htcleoNeedsViewActivator =
		(startAppInForeground && command!=EApaCommandViewActivate);
	HtcleoEikCorePreFactoryTrace(0xE32Bu, htcleoNeedsViewActivator);
	// HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW_V1
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
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);
'''


LEGACY_BRANCH_TAIL = r'''		HtcleoEikCorePreFactoryTrace(0xE367u, KErrNone);
		appUi.ActivateTopViewL();
		HtcleoEikCorePreFactoryTrace(0xE368u, KErrNone);
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);
		}
	else if (htcleoNeedsViewActivator)
		{
		iEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);
		}
'''


MERGED_BRANCH_TAIL = r'''		HtcleoEikCorePreFactoryTrace(0xE367u, KErrNone);
		appUi.ActivateTopViewL();
		HtcleoEikCorePreFactoryTrace(0xE368u, KErrNone);
		}
	else if (htcleoNeedsViewActivator)
		{
		iEikEnvExtra->iViewActivator = CEikStartUpViewActivator::NewL(appUi, *this, iEikEnvExtra->iViewActivator);
		}
	if (htcleoNeedsViewActivator)
		HtcleoEikCorePreFactoryTrace(0xE32Cu, KErrNone);
'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"view activator branch: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    retired = RETIRE_MARKER in source
    checks = {
        "priority prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "MatrixMenu direct gate": (
            source.count(
                "const TBool htcleoDirectStartupView =\n"
                "\t\t(htcleoNeedsViewActivator &&\n"
                "\t\t RProcess().SecureId().iId == 0x101f4cd2u);"
            ) == 1
            or (
                retired
                and source.count("const TBool htcleoRetireStartupView =") == 1
            )
        ),
        "real direct activation": (
            source.count("appUi.ActivateTopViewL();") == 1
            or (retired and source.count("appUi.ActivateTopViewL();") == 0)
        ),
        "stock async activation retained": (
            source.count("CEikStartUpViewActivator::NewL(appUi, *this,") == 1
            and source.count("iAppUi.ActivateTopViewL();") == 1
        ),
        "direct and async mutually exclusive": source.count(
            "else if (htcleoNeedsViewActivator)"
        ) == 1,
        "all direct stages": all(
            source.count(f"0xE{stage:03X}u") == 1
            for stage in range(0x366, 0x369)
        ),
        "construction remains fail-closed": (
            "TRAP" not in NEW
            and "KErrNotSupported" not in NEW
            and "TRAP_IGNORE" not in NEW
        ),
        "no dummy render or input bypass": (
            "User::After" not in NEW
            and "HalFunction" not in NEW
            and "RunIfReady" not in NEW
            and "RequestComplete" not in NEW
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
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    elif LEGACY_BRANCH_TAIL in source:
        source = source.replace(LEGACY_BRANCH_TAIL, MERGED_BRANCH_TAIL, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    if RETIRE_MARKER in source:
        print(
            "HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW="
            "superseded-by-post-container-retirement"
        )
    else:
        print(
            "HTCLEO_EIKCORE_MATRIXMENU_DIRECT_STARTUP_VIEW="
            "real-failclosed-e366-e368 async-other-apps-stock"
        )


if __name__ == "__main__":
    main()
