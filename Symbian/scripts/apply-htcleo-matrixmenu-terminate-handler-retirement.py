#!/usr/bin/env python3
"""Retire regressive C++ handler installs while retaining fatal stack capture."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1"

DECLARATIONS = r'''extern "C" IMPORT_C void abort();
namespace std
    {
    typedef void (*terminate_handler)();
    typedef void (*unexpected_handler)();
    IMPORT_C terminate_handler set_terminate(terminate_handler) throw();
    IMPORT_C unexpected_handler set_unexpected(unexpected_handler) throw();
    }

'''

HANDLERS = r'''// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1
static void HtcleoMatrixMenuTerminateHandler()
    {
    HtcleoMenuLog(0x4D4D12A2u, KErrNone, 0u);
    abort();
    }

static void HtcleoMatrixMenuUnexpectedHandler()
    {
    HtcleoMenuLog(0x4D4D12A3u, KErrNone, 0u);
    abort();
    }

'''

INSTALL_BLOCK = r'''    const TBool htcleoOldTerminatePresent=
        std::set_terminate(HtcleoMatrixMenuTerminateHandler) != NULL;
    const TBool htcleoOldUnexpectedPresent=
        std::set_unexpected(HtcleoMatrixMenuUnexpectedHandler) != NULL;
    HtcleoMenuLog(0x4D4D12A4u,
        htcleoOldTerminatePresent ? 1 : 0,
        htcleoOldUnexpectedPresent ? 1u : 0u);
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    if "HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1" not in text:
        raise SystemExit("termination retirement requires abort stack trace first")
    text = replace_once(text, DECLARATIONS, "", "C++ runtime declarations")
    text = replace_once(
        text,
        HANDLERS,
        "// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1\n"
        "// HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1\n",
        "terminate and unexpected handlers",
    )
    text = replace_once(text, INSTALL_BLOCK, "", "C++ runtime handler install")
    return text


def verify(text: str) -> None:
    caller_stack = "HTCLEO_MATRIXMENU_CALLER_STACK_TRACE_V1" in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "regressive handlers absent": all(
            token not in text
            for token in (
                "HtcleoMatrixMenuTerminateHandler",
                "HtcleoMatrixMenuUnexpectedHandler",
                "std::set_terminate",
                "std::set_unexpected",
                "0x4D4D12A2u",
                "0x4D4D12A3u",
                "0x4D4D12A4u",
            )
        ),
        "exception handler retained": (
            text.count("HtcleoMatrixMenuExceptionHandler")
            == (6 if caller_stack else 3)
            and text.count("0x4D4D12A1u") == 1
        ),
        "fatal stack retained": (
            text.count("0x4D4D12A5u") == 1
            and text.count("0x4D4D12B0u+") == 1
            and (
                text.count("htcleoCallerStackIndex<96") == 1
                if caller_stack
                else text.count("htcleoStackIndex<32") == 2
            )
        ),
        "fatal behavior retained": (
            text.count("User::Panic(KHtcleoMatrixMenuException, 3)") == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu terminate retirement verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmgui.cpp"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT="
        "startup-regression-retired-exception-stack-retained-12a5-12cf"
    )


if __name__ == "__main__":
    main()
