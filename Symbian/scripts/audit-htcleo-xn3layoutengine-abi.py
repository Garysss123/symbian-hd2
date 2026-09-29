#!/usr/bin/env python3
"""Verify the Xn layout engine's frozen export prefix and reviewed aliases."""

from __future__ import annotations

import argparse
from pathlib import Path


APPENDED = {
    "_ZN19MXnComponentFactoryC1Ev @ 279 NONAME",
    "_ZN8CXnUtils18ResolveSkinItemIDLERK7TDesC16R11TAknsItemID @ 280 NONAME",
    "_ZNK15CXnNodePluginIf16IsDrawingAllowedEv @ 281 NONAME",
}


def normalized(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="latin-1").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frozen", type=Path)
    parser.add_argument("generated", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    frozen = normalized(args.frozen)
    generated = normalized(args.generated)
    if len(frozen) != 279 or frozen[0] != "EXPORTS":
        raise SystemExit(f"unexpected frozen ABI length/header: {len(frozen)}")
    if generated[: len(frozen)] != frozen:
        raise SystemExit("generated Xn ABI does not preserve frozen prefix")
    tail = generated[len(frozen) :]
    if not tail or tail[0] != "; NEW:" or set(tail[1:]) != APPENDED:
        raise SystemExit(f"unexpected reviewed Xn ABI tail: {tail}")
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "xn3layoutengine-frozen-exports.def").write_text(
        "\n".join(frozen) + "\n", encoding="ascii"
    )
    (args.output / "xn3layoutengine-generated-exports.def").write_text(
        "\n".join(generated) + "\n", encoding="ascii"
    )
    (args.output / "xn3layoutengine-generated-frozen-prefix.def").write_text(
        "\n".join(generated[: len(frozen)]) + "\n", encoding="ascii"
    )
    (args.output / "XN3LAYOUTENGINE-ABI-RESULT.txt").write_text(
        "STATUS=HTCLEO_XN3LAYOUTENGINE_ABI_OK\n"
        "FROZEN_EXPORTS=278\n"
        "GENERATED_FROZEN_PREFIX=exact-symbol-ordinal-noname\n"
        "GCCE_APPENDED_REVIEWED_SYMBOLS=3\n"
        "GENERATED_EXPORTS=281\n",
        encoding="ascii",
    )
    print("STATUS=HTCLEO_XN3LAYOUTENGINE_ABI_OK")
    print("FROZEN_EXPORTS=278")
    print("GCCE_APPENDED_REVIEWED_SYMBOLS=3")
    print("GENERATED_EXPORTS=281")


if __name__ == "__main__":
    main()
