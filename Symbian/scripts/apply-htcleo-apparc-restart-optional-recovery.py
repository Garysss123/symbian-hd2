#!/usr/bin/env python3
"""Keep restarted AppArc past optional interrupted-update recovery and split 207-208."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_APPARC_RESTART_OPTIONAL_RECOVERY_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


CONSTRUCT_GAP = r'''	HtcleoApaServerLog(0x00000207u, KErrNone, (TUint32)iAppList);

	// If the phone rebooted halfway through processing updates, there will be a log file left
	// look for one and recover if neccessary
	CApsNonNativeApplicationsManager::RecoverFromUpdateLogL(iFs);

	iMimeTypeRecognizer=CApaScanningDataRecognizer::NewL(iFs, !iLoadRecognizersOnDemand);

	ConstructPathsToMonitorL();	

	if ( iAppFsMonitor )
		{
		iAppFsMonitor->Start(ENotifyFile);
		iAppFsMonitor->SetBlocked(ETrue);			
		}
	HtcleoApaServerLog(0x00000208u, KErrNone, 0u);'''


CONSTRUCT_GAP_PATCHED = r'''	HtcleoApaServerLog(0x00000207u, KErrNone, (TUint32)iAppList);

	// HTCLEO_APPARC_RESTART_OPTIONAL_RECOVERY_V1
	// Interrupted non-native update recovery is not the application list.  A
	// replacement APSEXE currently sees only KErrServerTerminated here; retain
	// all other failures and continue into the real recognizer/list pipeline.
	TRAPD(htcleoUpdateRecoveryResult,
		CApsNonNativeApplicationsManager::RecoverFromUpdateLogL(iFs));
	HtcleoApaServerLog(0x0000020Bu, htcleoUpdateRecoveryResult, 0u);
	if (htcleoUpdateRecoveryResult != KErrNone
			&& htcleoUpdateRecoveryResult != KErrServerTerminated)
		{
		User::Leave(htcleoUpdateRecoveryResult);
		}

	HtcleoApaServerLog(0x0000020Cu, KErrNone, 0u);
	iMimeTypeRecognizer=CApaScanningDataRecognizer::NewL(
		iFs, !iLoadRecognizersOnDemand);
	HtcleoApaServerLog(0x0000020Du, KErrNone,
		(TUint32)iMimeTypeRecognizer);

	HtcleoApaServerLog(0x0000020Eu, KErrNone, 0u);
	ConstructPathsToMonitorL();
	HtcleoApaServerLog(0x0000020Fu, KErrNone,
		iAppFsMonitor ? 1u : 0u);

	if ( iAppFsMonitor )
		{
		iAppFsMonitor->Start(ENotifyFile);
		iAppFsMonitor->SetBlocked(ETrue);			
		}
	HtcleoApaServerLog(0x00000208u, KErrNone, 0u);'''


def install(source: str) -> str:
    return replace_once(
        source, CONSTRUCT_GAP, CONSTRUCT_GAP_PATCHED, "AppArc 207-208 gap"
    )


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "narrow fail-open": (
            source.count("htcleoUpdateRecoveryResult != KErrServerTerminated") == 1
            and source.count("User::Leave(htcleoUpdateRecoveryResult)") == 1
        ),
        "gap stages": all(
            source.count(f"0x000002{stage:02X}u") == 1
            for stage in range(0x0B, 0x10)
        ),
        "core list retained": (
            source.count("iAppList->InitListL(this)") >= 1
            and source.count("CApaScanningDataRecognizer::NewL") >= 1
            and source.count("ConstructPathsToMonitorL();") >= 1
        ),
        "monitor retained": (
            source.count("iAppFsMonitor->Start(ENotifyFile)") >= 1
            and source.count("iAppFsMonitor->SetBlocked(ETrue)") >= 1
        ),
        "exact patched gap": (
            source.count(CONSTRUCT_GAP_PATCHED) == 1
            or (
                source.count("HTCLEO_APPARC_RESTART_OPTIONAL_RECOGNIZER_V1")
                == 1
                and source.count(
                    "HtcleoApaServerLog(0x0000020Du, htcleoRecognizerResult"
                )
                == 1
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AppArc restart recovery verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/appsupport/appfw/apparchitecture/apserv/APSSERV.CPP"
    )
    if not source_path.is_file():
        raise SystemExit("missing AppArc server source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print("HTCLEO_APPARC_RESTART_RECOVERY=20B-20F-serverterminated-failopen")


if __name__ == "__main__":
    main()
