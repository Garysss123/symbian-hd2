#!/usr/bin/env python3
"""Fail closed on the source-built eikcoctl.dll export ABI.

The GCCE rebuild exposes four source symbols that the released RVCT image kept
implicit.  They may be appended only after the exact frozen 1-2018 prefix;
existing symbols, ordinals, NONAME and ABSENT semantics must not move.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil


EXPECTED_ADDITIONS = (
    (
        "_ZN11CAknToolbar22ConstructFromResourceLER15TResourceReader",
        2019,
        False,
    ),
    ("_ZN15CListItemDrawerC1Ev", 2020, False),
    ("_ZN18CEikStatusPaneBaseC1ER9CEikonEnvP12RWindowGroup", 2021, False),
    (
        "_ZN9CEikEdwin18CEikEdwinExtension25TAknEdwinPictographDrawer"
        "18DrawPictographAreaEv",
        2022,
        False,
    ),
)

EXPORT = re.compile(
    r"^\s*(\S+)\s+@\s+(\d+)\s+NONAME(?:\s+(ABSENT))?(?:\s*;.*)?$"
)


def read_lines(path: pathlib.Path) -> list[str]:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"missing or empty DEF: {path}")
    return path.read_text(encoding="latin-1").splitlines()


def semantic(line: str) -> str:
    return line.split(";", 1)[0].rstrip()


def exports(lines: list[str], label: str) -> list[tuple[str, int, bool]]:
    parsed: list[tuple[str, int, bool]] = []
    for line in lines:
        match = EXPORT.match(line)
        if match:
            parsed.append(
                (match.group(1), int(match.group(2)), match.group(3) == "ABSENT")
            )
    if not parsed:
        raise SystemExit(f"no exports parsed from {label}")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("frozen_def", type=pathlib.Path)
    parser.add_argument("generated_def", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    args = parser.parse_args()

    frozen_lines = read_lines(args.frozen_def)
    generated_lines = read_lines(args.generated_def)
    if len(generated_lines) <= len(frozen_lines):
        raise SystemExit("generated DEF does not contain the reviewed GCCE suffix")

    for line_no, (frozen, generated) in enumerate(
        zip(frozen_lines, generated_lines), 1
    ):
        if semantic(frozen) != semantic(generated):
            raise SystemExit(
                f"frozen-prefix mismatch at line {line_no}: "
                f"{frozen!r} != {generated!r}"
            )

    frozen_exports = exports(frozen_lines, "frozen DEF")
    generated_exports = exports(generated_lines, "generated DEF")
    if len(frozen_exports) != 2018:
        raise SystemExit(
            f"frozen export count is {len(frozen_exports)}, expected 2018"
        )
    if [ordinal for _, ordinal, _ in frozen_exports] != list(range(1, 2019)):
        raise SystemExit("frozen ordinals are not the exact 1-2018 sequence")
    if generated_exports[:2018] != frozen_exports:
        raise SystemExit("generated ordinals 1-2018 differ from the frozen ABI")
    if tuple(generated_exports[2018:]) != EXPECTED_ADDITIONS:
        raise SystemExit(
            "generated GCCE suffix differs from the four reviewed symbols"
        )
    if generated_lines.count("; NEW:") != 1:
        raise SystemExit("generated DEF does not contain exactly one NEW separator")
    if generated_lines[len(frozen_lines) - 1] != "; NEW:":
        raise SystemExit(
            "NEW separator is not immediately after frozen ordinal 2018"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        args.frozen_def, args.output_dir / "eikcoctl-frozen-exports.def"
    )
    shutil.copyfile(
        args.generated_def, args.output_dir / "eikcoctl-generated-exports.def"
    )
    prefix = generated_lines[: len(frozen_lines)]
    (args.output_dir / "eikcoctl-generated-frozen-prefix.def").write_text(
        "\n".join(prefix) + "\n", encoding="latin-1"
    )
    result = (
        "STATUS=HTCLEO_EIKCOCTL_ABI_OK\n"
        "FROZEN_EXPORTS=2018\n"
        "GENERATED_FROZEN_PREFIX=exact-symbol-ordinal-noname-absent\n"
        "GCCE_APPENDED_REVIEWED_SYMBOLS=4\n"
        "GENERATED_EXPORTS=2022\n"
    )
    (args.output_dir / "EIKCOCTL-ABI-RESULT.txt").write_text(
        result, encoding="ascii"
    )
    print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
