#!/usr/bin/env python3
"""Capture the MatrixMenu abort caller stack before the C handler prologue."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_CALLER_STACK_TRACE_V1"

OLD_HANDLER = r'''// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1
// HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1
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

NEW_HANDLER = r'''// HTCLEO_MATRIXMENU_ABORT_STACK_TRACE_V1
// HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1
// HTCLEO_MATRIXMENU_CALLER_STACK_TRACE_V1
extern "C" void HtcleoMatrixMenuExceptionHandlerBody(
    TExcType aType, const TUint32* aCallerStack);

static void __attribute__((naked))
HtcleoMatrixMenuExceptionHandler(TExcType /*aType*/)
    {
    // Preserve r0=aType and pass the entry SP in r1 before any C prologue can
    // allocate locals.  A tail branch deliberately retains the original LR.
    __asm__ __volatile__(
        "mov r1, sp\n\t"
        "b HtcleoMatrixMenuExceptionHandlerBody\n\t");
    }

extern "C" void HtcleoMatrixMenuExceptionHandlerBody(
    TExcType aType, const TUint32* aCallerStack)
    {
    HtcleoMenuLog(0x4D4D12A1u, static_cast<TInt>(aType), 0u);
    HtcleoMenuLog(0x4D4D12A5u, 96,
        reinterpret_cast<TUint32>(aCallerStack));
    HtcleoMenuLog(0x4D4D12A6u, KErrNone,
        reinterpret_cast<TUint32>(__builtin_return_address(0)));
    for (TInt htcleoCallerStackIndex=0;
            htcleoCallerStackIndex<96; ++htcleoCallerStackIndex)
        {
        HtcleoMenuLog(0x4D4D12B0u+
            static_cast<TUint32>(htcleoCallerStackIndex),
            htcleoCallerStackIndex,
            aCallerStack[htcleoCallerStackIndex]);
        }
    // ECausedException is the kernel-private symbolic name for reason 3.
    User::Panic(KHtcleoMatrixMenuException, 3);
    }
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if "HTCLEO_MATRIXMENU_TERMINATE_HANDLER_RETIREMENT_V1" not in text:
        raise SystemExit("caller stack trace requires handler retirement first")
    count = text.count(OLD_HANDLER)
    if count != 1:
        raise SystemExit(f"exception handler: expected one anchor, found {count}")
    return text.replace(OLD_HANDLER, NEW_HANDLER, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "naked entry wrapper": (
            text.count("__attribute__((naked))") == 1
            and text.count('"mov r1, sp\\n\\t"') == 1
            and text.count('"b HtcleoMatrixMenuExceptionHandlerBody\\n\\t"') == 1
        ),
        "body declaration and definition": (
            text.count("HtcleoMatrixMenuExceptionHandlerBody(") == 2
        ),
        "entry stack pointer": (
            text.count("reinterpret_cast<TUint32>(aCallerStack)") == 1
        ),
        "entry return address": (
            text.count("__builtin_return_address(0)") == 1
            and text.count("0x4D4D12A6u") == 1
        ),
        "bounded direct caller scan": (
            text.count("htcleoCallerStackIndex<96") == 1
            and text.count("aCallerStack[htcleoCallerStackIndex]") == 1
            and "TUint32 htcleoStackWords[32]" not in text
            and "htcleoStackIndex<32" not in text
        ),
        "stack record base": text.count("0x4D4D12B0u+") == 1,
        "fatal behavior retained": (
            text.count("User::Panic(KHtcleoMatrixMenuException, 3)") == 1
        ),
        "regressive runtime hooks absent": all(
            token not in text
            for token in (
                "std::set_terminate",
                "std::set_unexpected",
                "HtcleoMatrixMenuTerminateHandler",
                "HtcleoMatrixMenuUnexpectedHandler",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu caller stack verification failed: " + ", ".join(failed)
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
        "HTCLEO_MATRIXMENU_CALLER_STACK_TRACE="
        "naked-entry-sp-lr-96words-12a5-130f-repanic"
    )


if __name__ == "__main__":
    main()
