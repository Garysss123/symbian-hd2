#!/usr/bin/env python3
"""Run MatrixMenu's one-shot startup-view activator before other ready AOs.

Iteration 544 provides a fresh request signal immediately before the stock
scheduler starts, yet the ready startup-view AO still does not reach E350.
The activator's stock priority is FepLoader+10 (160), below IPC-high (200) and
clock-timer (300).  A higher-priority ready AO can therefore consume the first
dispatch and block before the one-shot view activator runs.

For MatrixMenu only, construct this one-shot activator at ClockTimer+10 (310).
It deletes itself after RunL, so the priority cannot persist or starve normal
events.  Other apps keep priority 160.  The stock scheduler, focus decision,
RunL and real ActivateTopViewL call are retained without direct dispatch.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY_V1"
PREREQUISITE = "HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO_ARM_V1"


OLD = r'''CEikStartUpViewActivator::CEikStartUpViewActivator(CEikAppUi& aAppUi, CEikonEnv& aEikonEnv, CEikStartUpViewActivator*& aOwner)
	: CActive(KStartUpViewActivatorPriority), iAppUi(aAppUi), iEnv(aEikonEnv), iOwner(aOwner)
	{
	// HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO_ARM_V1
	const TBool htcleoArmBeforeComplete =
		(RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE360u, htcleoArmBeforeComplete);'''


NEW = r'''CEikStartUpViewActivator::CEikStartUpViewActivator(CEikAppUi& aAppUi, CEikonEnv& aEikonEnv, CEikStartUpViewActivator*& aOwner)
	// HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY_V1
	: CActive(RProcess().SecureId().iId == 0x101f4cd2u
		? EActivePriorityClockTimer + 10
		: KStartUpViewActivatorPriority),
	  iAppUi(aAppUi), iEnv(aEikonEnv), iOwner(aOwner)
	{
	// HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO_ARM_V1
	const TBool htcleoArmBeforeComplete =
		(RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE360u, htcleoArmBeforeComplete);
	HtcleoEikCorePreFactoryTrace(0xE365u,
		htcleoArmBeforeComplete
		? EActivePriorityClockTimer + 10
		: KStartUpViewActivatorPriority);'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"startup-view priority anchor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "AO arm prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "single priority stage": source.count("0xE365u") == 1,
        "MatrixMenu priority 310": source.count(
            "RProcess().SecureId().iId == 0x101f4cd2u\n"
            "\t\t? EActivePriorityClockTimer + 10"
        ) == 1,
        "stock priority retained": source.count(
            "\t\t: KStartUpViewActivatorPriority),"
        ) == 1,
        "stock RunL retained": source.count("iAppUi.ActivateTopViewL();") == 1,
        "one-shot deletion retained": source.count("delete this;") >= 2,
        "no direct dispatch or wait": (
            "RunIfReady" not in NEW
            and "User::After" not in NEW
            and "WaitFor" not in NEW
            and "ActivateTopViewL" not in NEW
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
        "HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_PRIORITY="
        "310-one-shot stage=E365 other-apps=160-stock"
    )


if __name__ == "__main__":
    main()
