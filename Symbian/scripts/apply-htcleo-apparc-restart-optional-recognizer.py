#!/usr/bin/env python3
"""Keep restarted AppArc alive when the optional MIME recognizer server died."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_APPARC_RESTART_OPTIONAL_RECOGNIZER_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


RECOGNIZER = r'''	HtcleoApaServerLog(0x0000020Cu, KErrNone, 0u);
	iMimeTypeRecognizer=CApaScanningDataRecognizer::NewL(
		iFs, !iLoadRecognizersOnDemand);
	HtcleoApaServerLog(0x0000020Du, KErrNone,
		(TUint32)iMimeTypeRecognizer);'''


RECOGNIZER_PATCHED = r'''	HtcleoApaServerLog(0x0000020Cu, KErrNone, 0u);
	// HTCLEO_APPARC_RESTART_OPTIONAL_RECOGNIZER_V1
	// MIME recognition is not the native/JAR application list.  Preserve every
	// other failure, but let a restarted APSEXE continue when the recognizer's
	// backing server was terminated during the recovery window.
	iMimeTypeRecognizer = NULL;
	TRAPD(htcleoRecognizerResult,
		iMimeTypeRecognizer = CApaScanningDataRecognizer::NewL(
			iFs, !iLoadRecognizersOnDemand));
	HtcleoApaServerLog(0x0000020Du, htcleoRecognizerResult,
		(TUint32)iMimeTypeRecognizer);
	if (htcleoRecognizerResult != KErrNone
			&& htcleoRecognizerResult != KErrServerTerminated)
		{
		User::Leave(htcleoRecognizerResult);
		}'''


UPDATE_PLUGINS = r'''	if(!iLoadRecognizersOnDemand || iRecognizerUsageCount > 0 || (iRecognizerUnloadTimer && iRecognizerUnloadTimer->IsActive()))
		{
		TRAP_IGNORE(iMimeTypeRecognizer->LoadRecognizersL());
		}'''


UPDATE_PLUGINS_GUARDED = r'''	if(iMimeTypeRecognizer &&
		(!iLoadRecognizersOnDemand || iRecognizerUsageCount > 0 ||
		(iRecognizerUnloadTimer && iRecognizerUnloadTimer->IsActive())))
		{
		TRAP_IGNORE(iMimeTypeRecognizer->LoadRecognizersL());
		}'''


def install(source: str) -> str:
    source = replace_once(
        source, RECOGNIZER, RECOGNIZER_PATCHED, "optional MIME recognizer"
    )
    source = replace_once(
        source, UPDATE_PLUGINS, UPDATE_PLUGINS_GUARDED, "recognizer update guard"
    )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "narrow fail-open": (
            source.count("htcleoRecognizerResult != KErrServerTerminated") == 1
            and source.count("User::Leave(htcleoRecognizerResult)") == 1
        ),
        "explicit null": source.count("iMimeTypeRecognizer = NULL;") == 1,
        "result stage": source.count(
            "HtcleoApaServerLog(0x0000020Du, htcleoRecognizerResult"
        )
        == 1,
        "update guard": source.count("if(iMimeTypeRecognizer &&") == 1,
        "core AppArc retained": (
            source.count("iAppList->InitListL(this)") >= 1
            and source.count("CApaScanningDataRecognizer::NewL") >= 1
            and source.count("InitialListPopulationComplete") >= 1
        ),
        "no fake list": "AppendL( htcleo" not in source,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AppArc optional recognizer verification failed: " + ", ".join(failed)
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
    print("HTCLEO_APPARC_RESTART_RECOGNIZER=20D-serverterminated-null-guard")


if __name__ == "__main__":
    main()
