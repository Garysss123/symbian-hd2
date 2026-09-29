#!/usr/bin/env python3
"""Skip only MatrixMenu's redundant second empty task-name refresh.

Iteration 540 proves that the first CEikonEnv::UpdateTaskNameL() returns at
E323/E324, MatrixMenu fully constructs, and the command-line document name is
still empty at E32F.  SetMainDocFileNameL() then returns at E330, but the same
UpdateTaskNameL() call never returns at E331.  With an empty document name the
second refresh cannot add document metadata: the caption, application UID and
empty document name were already published by the first successful call.

For MatrixMenu only, defer that second refresh when the new document name is
empty.  Non-empty document launches and every other application retain the
stock refresh.  This adds no wait, retry, fabricated document, display call or
success result for any mandatory UI construction operation.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_MATRIXMENU_UNCHANGED_TASKNAME_DEFER_V1"
POSTAPPUI_MARKER = "HTCLEO_EIKCORE_POSTAPPUI_TRACE_V1"


OLD = r'''	iProcess->SetMainDocFileNameL(*modifiedDocumentName);
	HtcleoEikCorePreFactoryTrace(0xE330u, KErrNone);
	UpdateTaskNameL();
	HtcleoEikCorePreFactoryTrace(0xE331u, KErrNone);
'''


NEW = r'''	iProcess->SetMainDocFileNameL(*modifiedDocumentName);
	HtcleoEikCorePreFactoryTrace(0xE330u, KErrNone);
	// HTCLEO_EIKCORE_MATRIXMENU_UNCHANGED_TASKNAME_DEFER_V1
	// The first task-name publication already returned at E324.  MatrixMenu
	// has no command-line document, so repeating the same synchronous WServ
	// refresh cannot publish new state and is unsafe on the HTCLEO port.
	const TBool htcleoDeferUnchangedTaskName =
		(RProcess().SecureId().iId == 0x101f4cd2u &&
		 modifiedDocumentName->Length() == 0);
	HtcleoEikCorePreFactoryTrace(0xE342u, htcleoDeferUnchangedTaskName);
	if (!htcleoDeferUnchangedTaskName)
		UpdateTaskNameL();
	HtcleoEikCorePreFactoryTrace(
		0xE331u,
		htcleoDeferUnchangedTaskName ? KErrNotSupported : KErrNone);
'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"second UpdateTaskName anchor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    checks = {
        "post-AppUi trace prerequisite": source.count(POSTAPPUI_MARKER) == 1,
        "single marker": source.count(MARKER) == 1,
        "single policy decision stage": source.count("0xE342u") == 1,
        "MatrixMenu SID only": source.count(
            "const TBool htcleoDeferUnchangedTaskName =\n"
            "\t\t(RProcess().SecureId().iId == 0x101f4cd2u &&"
        ) == 1,
        "empty document only": source.count(
            "modifiedDocumentName->Length() == 0"
        ) == 1,
        "stock call retained": source.count("UpdateTaskNameL();") == 2,
        "first call remains unconditional": (
            "HtcleoEikCorePreFactoryTrace(0xE323u, KErrNone);\n"
            "\tUpdateTaskNameL();\n"
            "\tHtcleoEikCorePreFactoryTrace(0xE324u, KErrNone);"
            in source
        ),
        "non-empty/other-app call retained": (
            "if (!htcleoDeferUnchangedTaskName)\n\t\tUpdateTaskNameL();"
            in source
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
        "HTCLEO_EIKCORE_MATRIXMENU_TASKNAME="
        "defer-second-refresh-only-if-empty stage=E342 other-apps=stock"
    )


if __name__ == "__main__":
    main()
