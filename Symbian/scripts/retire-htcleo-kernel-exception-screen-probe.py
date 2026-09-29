#!/usr/bin/env python3
"""Permanently retire the HTCLEO kernel exception screen renderer.

The old bring-up hook intercepted selected user/SVC aborts in the ROM window,
painted a diagnostic panel directly into the HTCLEO framebuffer, and halted.
Iteration 431 uses durable filesystem logs instead.  Leaving that hook linked
would make a later fault look like a progress checkpoint and would change the
normal Symbian exception-dispatch policy, so remove both the renderer and its
Exc::Dispatch interception block fail-closed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_KERNEL_EXCEPTION_SCREEN_PROBE_RETIRED_V1"
FUNCTION = "HtcleoEstartInitCompleteFixedExceptionScreenProbe"
CONDITION = "#if defined(__CPU_QSD8250__) && defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)"
FORBIDDEN = (
    FUNCTION,
    "0xc6400000",
    "0xc6300000",
    "0x03839000",
    "0x556500c3",
)


def remove_guarded_block(text: str, needle: str, label: str) -> str:
    position = text.find(needle)
    if position < 0:
        raise SystemExit(f"{label}: anchor not found")

    start = text.rfind(CONDITION, 0, position)
    if start < 0:
        raise SystemExit(f"{label}: opening condition not found")
    end = text.find("\n#endif", position)
    if end < 0:
        raise SystemExit(f"{label}: closing endif not found")
    end += len("\n#endif")
    if end < len(text) and text[end] == "\n":
        end += 1

    block = text[start:end]
    if FUNCTION not in block:
        raise SystemExit(f"{label}: guarded block does not contain renderer")
    return text[:start] + text[end:]


def verify(text: str) -> None:
    if text.count(MARKER) != 1:
        raise SystemExit("retirement marker must occur exactly once")
    for token in FORBIDDEN:
        if token in text:
            raise SystemExit(f"retired exception renderer token remains: {token}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kernel_source", type=Path)
    args = parser.parse_args()

    path = args.kernel_source / "kernel/eka/kernel/arm/ckernel.cpp"
    text = path.read_text(encoding="utf-8")

    if MARKER not in text:
        # Remove the renderer definition first, leaving the dispatch call as the
        # sole occurrence that identifies the second guarded block.
        text = remove_guarded_block(text, FUNCTION, "renderer definition")
        text = remove_guarded_block(text, FUNCTION, "dispatch interception")

        anchor = 'extern "C" {\nextern SFullArmRegSet DefaultRegSet;\n}\n'
        if text.count(anchor) != 1:
            raise SystemExit("marker insertion anchor is not unique")
        text = text.replace(
            anchor,
            anchor + f"\n// {MARKER}\n",
            1,
        )
        path.write_text(text, encoding="utf-8")

    verify(path.read_text(encoding="utf-8"))
    print("HTCLEO_KERNEL_EXCEPTION_SCREEN_PROBE=retired")


if __name__ == "__main__":
    main()
