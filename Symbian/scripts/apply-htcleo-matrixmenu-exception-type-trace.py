#!/usr/bin/env python3
"""Log MatrixMenu's unhandled TExcType, then preserve fatal termination."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE_V1"

FUNCTION_ANCHOR = "// HTCLEO_MATRIXMENU_EIKSTART_DURABLE_LOG_V2\n"
FUNCTION_NEW = r'''// HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE_V1
_LIT(KHtcleoMatrixMenuException, "HTCLEO-EXC");

static void HtcleoMatrixMenuExceptionHandler(TExcType aType)
    {
    HtcleoMenuLog(0x4D4D12A1u, static_cast<TInt>(aType), 0u);
    // ECausedException is the kernel-private symbolic name for reason 3.
    User::Panic(KHtcleoMatrixMenuException, 3);
    }

// HTCLEO_MATRIXMENU_EIKSTART_DURABLE_LOG_V2
'''

MAIN_ANCHOR = r'''GLDEF_C TInt E32Main()
	{
    HtcleoMenuLog(0x4D4D0000u, KErrNone, 0u);
'''

MAIN_NEW = r'''GLDEF_C TInt E32Main()
	{
    HtcleoMenuLog(0x4D4D0000u, KErrNone, 0u);
    const TInt htcleoExceptionHandlerResult = User::SetExceptionHandler(
        HtcleoMatrixMenuExceptionHandler, 0xFFFFFFFFu);
    HtcleoMenuLog(0x4D4D12A0u, htcleoExceptionHandlerResult,
        User::ExceptionHandler() == HtcleoMatrixMenuExceptionHandler ? 1u : 0u);
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        text = text.replace(
            "User::Panic(KHtcleoMatrixMenuException, ECausedException);",
            "// ECausedException is the kernel-private symbolic name for reason 3.\n"
            "    User::Panic(KHtcleoMatrixMenuException, 3);",
            1,
        )
        return text
    text = replace_once(
        text, FUNCTION_ANCHOR, FUNCTION_NEW, "exception handler declaration"
    )
    text = replace_once(text, MAIN_ANCHOR, MAIN_NEW, "E32Main install")
    return text


def verify(text: str) -> None:
    caller_stack = "HTCLEO_MATRIXMENU_CALLER_STACK_TRACE_V1" in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "single handler": (
            text.count("HtcleoMatrixMenuExceptionHandler")
            == (6 if caller_stack else 3)
        ),
        "all exception mask": text.count("0xFFFFFFFFu") == 1,
        "install stage": text.count("0x4D4D12A0u") == 1,
        "type stage": text.count("0x4D4D12A1u") == 1,
        "fatal behavior retained": (
            text.count("User::Panic(KHtcleoMatrixMenuException, 3)") == 1
        ),
        "normal entry retained": text.count("0x4D4D0000u") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu exception type verification failed: " + ", ".join(failed)
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
        "HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE="
        "all-mask-log-type-12a0-12a1-repanic"
    )


if __name__ == "__main__":
    main()
