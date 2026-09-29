#!/usr/bin/env python3
"""Capture MatrixMenu C++ termination source and fatal ARM stack words."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1"

RUNTIME_DECLARATIONS = r'''extern "C" IMPORT_C void abort();
namespace std
    {
    typedef void (*terminate_handler)();
    typedef void (*unexpected_handler)();
    IMPORT_C terminate_handler set_terminate(terminate_handler) throw();
    IMPORT_C unexpected_handler set_unexpected(unexpected_handler) throw();
    }

'''

HANDLER_OLD = r'''static void HtcleoMatrixMenuExceptionHandler(TExcType aType)
    {
    HtcleoMenuLog(0x4D4D12A1u, static_cast<TInt>(aType), 0u);
    // ECausedException is the kernel-private symbolic name for reason 3.
    User::Panic(KHtcleoMatrixMenuException, 3);
    }
'''

HANDLER_NEW = RUNTIME_DECLARATIONS + r'''// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1
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

static void HtcleoMatrixMenuExceptionHandler(TExcType aType)
    {
    HtcleoMenuLog(0x4D4D12A1u, static_cast<TInt>(aType), 0u);
    TUint32 htcleoStackPointer=0u;
    __asm__ __volatile__("mov %0, sp" : "=r" (htcleoStackPointer));
    const TUint32* htcleoStackSource=
        reinterpret_cast<const TUint32*>(htcleoStackPointer);
    TUint32 htcleoStackWords[32];
    for (TInt htcleoStackIndex=0; htcleoStackIndex<32; ++htcleoStackIndex)
        {
        htcleoStackWords[htcleoStackIndex]=htcleoStackSource[htcleoStackIndex];
        }
    HtcleoMenuLog(0x4D4D12A5u, 32, htcleoStackPointer);
    for (TInt htcleoStackIndex=0; htcleoStackIndex<32; ++htcleoStackIndex)
        {
        HtcleoMenuLog(0x4D4D12B0u+
            static_cast<TUint32>(htcleoStackIndex),
            htcleoStackIndex, htcleoStackWords[htcleoStackIndex]);
        }
    // ECausedException is the kernel-private symbolic name for reason 3.
    User::Panic(KHtcleoMatrixMenuException, 3);
    }
'''

INSTALL_ANCHOR = r'''    HtcleoMenuLog(0x4D4D12A0u, htcleoExceptionHandlerResult,
        User::ExceptionHandler() == HtcleoMatrixMenuExceptionHandler ? 1u : 0u);
'''

INSTALL_NEW = INSTALL_ANCHOR + r'''    const TBool htcleoOldTerminatePresent=
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
        text = text.replace("#include <exception>\n#include <stdlib.h>\n", "", 1)
        if (
            "HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1" not in text
            and "IMPORT_C terminate_handler set_terminate" not in text
        ):
            text = replace_once(
                text,
                "// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1\n",
                RUNTIME_DECLARATIONS
                + "// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1\n",
                "manual C++ runtime declarations",
            )
        return text
    if "HTCLEO_MATRIXMENU_EXCEPTION_TYPE_TRACE_V1" not in text:
        raise SystemExit("abort stack trace requires exception type trace first")
    text = replace_once(text, HANDLER_OLD, HANDLER_NEW, "exception handler")
    text = replace_once(text, INSTALL_ANCHOR, INSTALL_NEW, "C++ handler install")
    return text


def verify(text: str) -> None:
    retired = "HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1" in text
    caller_stack = "HTCLEO_MATRIXMENU_CALLER_STACK_TRACE_V1" in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "terminate handler": (
            (
                text.count("HtcleoMatrixMenuTerminateHandler") == 0
                and text.count("0x4D4D12A2u") == 0
            )
            if retired
            else (
                text.count("HtcleoMatrixMenuTerminateHandler") == 2
                and text.count("0x4D4D12A2u") == 1
            )
        ),
        "unexpected handler": (
            (
                text.count("HtcleoMatrixMenuUnexpectedHandler") == 0
                and text.count("0x4D4D12A3u") == 0
            )
            if retired
            else (
                text.count("HtcleoMatrixMenuUnexpectedHandler") == 2
                and text.count("0x4D4D12A3u") == 1
            )
        ),
        "handler install stage": text.count("0x4D4D12A4u") == (0 if retired else 1),
        "manual runtime ABI": (
            (
                text.count("IMPORT_C terminate_handler set_terminate") == 0
                and text.count("IMPORT_C unexpected_handler set_unexpected") == 0
                and text.count('extern "C" IMPORT_C void abort()') == 0
            )
            if retired
            else (
                text.count("IMPORT_C terminate_handler set_terminate") == 1
                and text.count("IMPORT_C unexpected_handler set_unexpected") == 1
                and text.count('extern "C" IMPORT_C void abort()') == 1
                and "#include <exception>" not in text
            )
        ),
        "stack pointer stage": text.count("0x4D4D12A5u") == 1,
        "bounded stack copy": (
            (
                text.count("htcleoCallerStackIndex<96") == 1
                and text.count("aCallerStack[htcleoCallerStackIndex]") == 1
                and "TUint32 htcleoStackWords[32]" not in text
                and "htcleoStackIndex<32" not in text
            )
            if caller_stack
            else (
                text.count("TUint32 htcleoStackWords[32]") == 1
                and text.count("htcleoStackIndex<32") == 2
            )
        ),
        "stack record base": text.count("0x4D4D12B0u+") == 1,
        "fatal behavior retained": (
            text.count("User::Panic(KHtcleoMatrixMenuException, 3)") == 1
        ),
        "type stage retained": text.count("0x4D4D12A1u") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu abort stack verification failed: " + ", ".join(failed)
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
        "HTCLEO_MATRIXMENU_ABORT_STACK_TRACE="
        "terminate-unexpected-sp-32words-12a2-12cf-repanic"
    )


if __name__ == "__main__":
    main()
