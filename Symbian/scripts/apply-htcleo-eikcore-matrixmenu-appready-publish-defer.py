#!/usr/bin/env python3
"""Keep MatrixMenu locally ready while deferring its late WServ republish.

Iteration 541 passes the complete post-AppUi framework tail and process
rendezvous, then stops between E340 and E341 inside CEikonEnv::SetAppReady().
That function first updates CApaWindowGroupName's local ready bit and then
synchronously republishes the full name with RWindowGroup::SetName().  The
same late window-group publication pattern is already the proven 540 stall.

Preserve the local ready bit for every process.  For MatrixMenu only, defer
the late SetWindowGroupName() republish; all other applications keep stock
behavior.  The default-view activator does not consume the published task-list
ready bit, so real view creation, activation, WServ rendering and input remain
mandatory downstream evidence.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_APPREADY_PUBLISH_DEFER_V1"
PREREQUISITE = "HTCLEO_EIKCORE_MATRIXMENU_UNCHANGED_TASKNAME_DEFER_V1"


OLD = r'''void CEikonEnv::SetAppReady()
	{
	iWgName->SetAppReady(ETrue);
	iWgName->SetWindowGroupName(iRootWin);
	}'''


NEW = r'''void CEikonEnv::SetAppReady()
	{
	// HTCLEO_EIKCORE_MATRIXMENU_APPREADY_PUBLISH_DEFER_V1
	HtcleoEikCorePreFactoryTrace(0xE343u, KErrNone);
	iWgName->SetAppReady(ETrue);
	HtcleoEikCorePreFactoryTrace(0xE344u, KErrNone);
	const TBool htcleoDeferAppReadyPublish =
		(RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE345u, htcleoDeferAppReadyPublish);
	if (!htcleoDeferAppReadyPublish)
		iWgName->SetWindowGroupName(iRootWin);
	HtcleoEikCorePreFactoryTrace(
		0xE346u,
		htcleoDeferAppReadyPublish ? KErrNotSupported : KErrNone);
	}'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"SetAppReady anchor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "task-name prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "local ready retained": source.count("iWgName->SetAppReady(ETrue);") == 1,
        "single publish retained": source.count(
            "iWgName->SetWindowGroupName(iRootWin);"
        ) >= 1,
        "MatrixMenu SID only": source.count(
            "const TBool htcleoDeferAppReadyPublish =\n"
            "\t\t(RProcess().SecureId().iId == 0x101f4cd2u);"
        ) == 1,
        "other apps publish": (
            "if (!htcleoDeferAppReadyPublish)\n"
            "\t\tiWgName->SetWindowGroupName(iRootWin);"
            in source
        ),
        "all stages": all(
            source.count(f"0xE{stage:03X}u") == 1
            for stage in range(0x343, 0x347)
        ),
        "no wait or display": (
            "User::After" not in NEW and "HalFunction" not in NEW
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
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_MATRIXMENU_APPREADY="
        "local-ready-retained late-wserv-publish-deferred stages=E343-E346"
    )


if __name__ == "__main__":
    main()
