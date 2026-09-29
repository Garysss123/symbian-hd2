#!/usr/bin/env python3
"""Arm MatrixMenu's startup-view active object before self-completion.

Iteration 542 proves the complete synchronous Eikon construction tail and
enters env->Execute() at MatrixMenu stage 100B, but the already-created
CEikStartUpViewActivator never reaches RunL stage E350.  The stock constructor
self-completes iStatus before SetActive().  Reference EKA2 tolerates that
ordering, while this QSD8K port has repeatedly lost completions armed after
the completing event.

For MatrixMenu only, use the conventional self-completing active-object order:
set KRequestPending, SetActive(), then User::RequestComplete().  Other apps keep
the stock order.  No timer, wait, retry, direct view activation, fake success,
render bypass or input bypass is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO_ARM_V1"
PREREQUISITE = "HTCLEO_EIKCORE_MATRIXMENU_APPREADY_PUBLISH_DEFER_V1"


OLD = r'''	{
	CActiveScheduler::Add(this);
	TRequestStatus* status = &iStatus;
	User::RequestComplete(status, KErrNone);
	SetActive();
	}'''


NEW = r'''	{
	// HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO_ARM_V1
	const TBool htcleoArmBeforeComplete =
		(RProcess().SecureId().iId == 0x101f4cd2u);
	HtcleoEikCorePreFactoryTrace(0xE360u, htcleoArmBeforeComplete);
	CActiveScheduler::Add(this);
	HtcleoEikCorePreFactoryTrace(0xE361u, KErrNone);
	TRequestStatus* status = &iStatus;
	HtcleoEikCorePreFactoryTrace(0xE362u, iStatus.Int());
	if (htcleoArmBeforeComplete)
		{
		iStatus = KRequestPending;
		SetActive();
		HtcleoEikCorePreFactoryTrace(0xE363u, iStatus.Int());
		User::RequestComplete(status, KErrNone);
		HtcleoEikCorePreFactoryTrace(0xE364u, iStatus.Int());
		}
	else
		{
		User::RequestComplete(status, KErrNone);
		SetActive();
		}
	}'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"startup-view AO constructor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "app-ready prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "MatrixMenu named policy": source.count(
            "const TBool htcleoArmBeforeComplete =\n"
            "\t\t(RProcess().SecureId().iId == 0x101f4cd2u);"
        ) == 1,
        "pending before active": (
            source.index("iStatus = KRequestPending;", source.index(MARKER))
            < source.index("SetActive();", source.index(MARKER))
        ),
        "active before complete": (
            source.index("SetActive();", source.index(MARKER))
            < source.index(
                "User::RequestComplete(status, KErrNone);",
                source.index(MARKER),
            )
        ),
        "stock order retained for other apps": (
            "else\n\t\t{\n"
            "\t\tUser::RequestComplete(status, KErrNone);\n"
            "\t\tSetActive();\n\t\t}"
            in source
        ),
        "single scheduler add": source.count("CActiveScheduler::Add(this);") >= 1,
        "all stages": all(
            source.count(f"0xE{stage:03X}u") == 1
            for stage in range(0x360, 0x365)
        ),
        "no wait timer or direct activation": (
            "User::After" not in NEW
            and "RTimer" not in NEW
            and "ActivateTopViewL" not in NEW
            and "HalFunction" not in NEW
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
        "HTCLEO_EIKCORE_MATRIXMENU_STARTUP_VIEW_AO="
        "pending-setactive-complete stages=E360-E364 other-apps=stock"
    )


if __name__ == "__main__":
    main()
