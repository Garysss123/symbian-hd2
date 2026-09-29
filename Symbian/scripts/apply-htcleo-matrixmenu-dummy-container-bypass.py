#!/usr/bin/env python3
"""Defer MatrixMenu's transition-only dummy container on HTC Leo.

Iteration 526 localises the dummy grid block to CCoeControl::CreateWindowL().
The dummy container is a hidden transition placeholder; the real shell uses
iCurrentContainer and is constructed later from the selected suite.  Skip only
the startup dummy, report KErrNotSupported honestly at 0309/030A, and guard all
later placeholder-only visibility/draw/geometry uses.  Main container creation,
HN initialisation, runtime suite widgets and touch paths remain unchanged.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_DUMMY_CONTAINER_UI_FIRST_BYPASS_V1"
TAG = "0x44554D59u"  # DUMY

OLD = """    // HTCLEO_MATRIXMENU_DUMMY_GRID_RESULT_TRACE_V1
    TInt htcleoDummyGridResult = KErrNone;
    TRAP(htcleoDummyGridResult,
        iDummyContainer = CMmWidgetContainer::NewGridContainerL(
            ClientRect(), this, iDummyTemplateLib ));
    HtcleoMenuLog(0x4D4D0309u, htcleoDummyGridResult,
        iDummyContainer ? 1u : 0u);
    User::LeaveIfError(htcleoDummyGridResult);
    iDummyContainer->SetEmptyTextL( KNullDesC );
    iDummyContainer->MakeVisible( EFalse );
    AddToStackL( iDummyContainer, ECoeStackPriorityDefault,
            ECoeStackFlagRefusesFocus | ECoeStackFlagRefusesAllKeys );
    HtcleoMenuLog(0x4D4D030Au, KErrNone, 0u);
"""

NEW = """    // HTCLEO_MATRIXMENU_DUMMY_CONTAINER_UI_FIRST_BYPASS_V1
    // The hidden transition placeholder blocks in CreateWindowL on HTC Leo.
    // Keep the real iCurrentContainer path and report this defer honestly.
    iDummyContainer = NULL;
    HtcleoMenuLog(0x4D4D0309u, KErrNotSupported, 0x44554D59u);
    HtcleoMenuLog(0x4D4D030Au, KErrNotSupported, 0x44554D59u);
"""


DIRECT_DUMMY_CALL = re.compile(
    r"(?m)^([ \t]*)(iDummyContainer->(?:MakeVisible|DrawNow|SetRect)\([^;\n]*\);)$"
)


def guard_dummy_calls(source: str) -> str:
    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        statement = match.group(2)
        return (
            f"{indent}if (iDummyContainer)\n"
            f"{indent}    {{\n"
            f"{indent}    {statement}\n"
            f"{indent}    }}"
        )

    return DIRECT_DUMMY_CALL.sub(repl, source)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "blocking startup constructor retired": OLD not in source,
        "explicit null placeholder": source.count("iDummyContainer = NULL;") == 1,
        "honest 0309 defer": source.count(
            "HtcleoMenuLog(0x4D4D0309u, KErrNotSupported, 0x44554D59u);"
        ) == 1,
        "honest 030A continuation": source.count(
            "HtcleoMenuLog(0x4D4D030Au, KErrNotSupported, 0x44554D59u);"
        ) == 1,
        "dummy-specific factory retired": "ClientRect(), this, iDummyTemplateLib" not in source,
        "real suite grid factory retained": source.count(
            "aContainerToLoad = CMmWidgetContainer::NewGridContainerL("
        ) == 1,
        "HN engine retained": source.count("iHNInterface = CHnEngine::NewL( *this );") >= 1,
        "real template library retained": source.count(
            "iTemplateLibrary = CMmTemplateLibrary::NewL();"
        ) >= 1,
        "destructor safe": source.count(
            "delete iDummyContainer;"
        ) == 1,
        "boolean use null-safe": source.count(
            "!presentationChangeExpected || !iDummyContainer || !iDummyContainer->IsVisible();"
        ) == 1,
        "no timer display or fake success": (
            "User::After" not in NEW
            and "HalFunction" not in NEW
            and "KErrNone" not in NEW
        ),
    }

    lines = source.splitlines()
    unsafe: list[str] = []
    for index, line in enumerate(lines):
        if "iDummyContainer->" not in line:
            continue
        stripped = line.strip()
        if "iDummyContainer && iDummyContainer->" in stripped:
            continue
        if "!iDummyContainer || !iDummyContainer->" in stripped:
            continue
        previous = "\n".join(lines[max(0, index - 2):index])
        if "if (iDummyContainer)" not in previous:
            unsafe.append(f"{index + 1}:{stripped}")

    failed = [name for name, ok in checks.items() if not ok]
    if unsafe:
        failed.append("unguarded dummy calls=" + ",".join(unsafe))
    if failed:
        raise SystemExit(
            "MatrixMenu dummy-container bypass verification failed: "
            + "; ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing MatrixMenu app-ui input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                f"MatrixMenu dummy startup anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)
        source = source.replace(
            "    RemoveFromStack( iDummyContainer );\n",
            "    if (iDummyContainer)\n"
            "        {\n"
            "        RemoveFromStack( iDummyContainer );\n"
            "        }\n",
            1,
        )
        source = source.replace(
            "!presentationChangeExpected || !iDummyContainer->IsVisible();",
            "!presentationChangeExpected || !iDummyContainer || !iDummyContainer->IsVisible();",
            1,
        )
        source = guard_dummy_calls(source)

    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_DUMMY_CONTAINER=deferred "
        "tag=DUMY main-container=retained later-placeholder-uses=null-guarded"
    )


if __name__ == "__main__":
    main()
