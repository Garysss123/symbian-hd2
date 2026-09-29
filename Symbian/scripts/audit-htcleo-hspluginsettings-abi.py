#!/usr/bin/env python3
"""Verify the HomeScreen settings DLL preserves its 90 frozen exports."""

from __future__ import annotations

import argparse
from pathlib import Path


def normalized(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="latin-1").splitlines()
        if line.strip()
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frozen", type=Path)
    parser.add_argument("generated", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    frozen = normalized(args.frozen)
    generated = normalized(args.generated)
    if len(frozen) != 91 or frozen[0] != "EXPORTS":
        raise SystemExit(f"unexpected frozen ABI length/header: {len(frozen)}")
    if generated != frozen:
        if generated[: len(frozen)] != frozen:
            raise SystemExit("generated settings ABI does not preserve frozen prefix")
        raise SystemExit(f"unexpected generated settings ABI tail: {generated[len(frozen):]}")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "hspluginsettings-frozen-exports.def").write_text(
        "\n".join(frozen) + "\n", encoding="ascii"
    )
    (args.output / "hspluginsettings-generated-exports.def").write_text(
        "\n".join(generated) + "\n", encoding="ascii"
    )
    (args.output / "HSPLUGINSETTINGS-ABI-RESULT.txt").write_text(
        "STATUS=HTCLEO_HSPLUGINSETTINGS_ABI_OK\n"
        "FROZEN_EXPORTS=90\n"
        "GENERATED_EXPORTS=90\n",
        encoding="ascii",
    )
    print("STATUS=HTCLEO_HSPLUGINSETTINGS_ABI_OK")
    print("FROZEN_EXPORTS=90")
    print("GENERATED_EXPORTS=90")


if __name__ == "__main__":
    main()
