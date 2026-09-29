#!/usr/bin/env python3
"""Fail closed on the source-built Avkon frozen export ABI."""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil


EXPECTED_ADDITIONS = (
    ("_ZN12CAknDocumentC1ER15CEikApplication", 4605, False),
    ("_ZN16CAknAnimatedViewC1Ev", 4606, False),
    ("_ZN19AknListBoxShortCutsC1Ev", 4607, False),
    ("_ZN20CAknEdwinSettingPageC1EPK7TDesC16iiii", 4608, False),
    ("_ZN20CAknEdwinSettingPageC1Ei", 4609, False),
    ("_ZN22CAknIntegerSettingItemC1EiRi", 4610, False),
    ("_ZN23CAknPasswordSettingPageC1EPK7TDesC16iiiiR6TDes16RS1_", 4611, False),
    ("_ZN23CAknPasswordSettingPageC1EiR6TDes16RK7TDesC16", 4612, False),
    ("_ZN8CAknViewC1Ev", 4613, False),
)

EXPORT = re.compile(
    r"^\s*(\S+)\s+@\s*(\d+)(?:\s+(NONAME))?(?:\s+(ABSENT))?\s*(?:;.*)?$"
)


def read_lines(path: pathlib.Path) -> list[str]:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"missing or empty DEF: {path}")
    return path.read_text(encoding="latin-1").splitlines()


def trim_trailing_empty(lines: list[str]) -> list[str]:
    result = list(lines)
    while result and not result[-1].strip():
        result.pop()
    return result


def semantic(line: str) -> str:
    value = " ".join(line.split(";", 1)[0].split())
    value = re.sub(r"@(?=\d)", "@ ", value)
    # The released DEF omits NONAME on ABSENT placeholders; Raptor writes it
    # back explicitly.  Both encode the same missing ordinal slot.
    return re.sub(r"(@\s+\d+)\s+ABSENT$", r"\1 NONAME ABSENT", value)


def exports(lines: list[str], label: str) -> list[tuple[str, int, bool]]:
    parsed: list[tuple[str, int, bool]] = []
    for line in lines:
        match = EXPORT.match(line)
        if match:
            if match.group(3) != "NONAME" and match.group(4) != "ABSENT":
                raise SystemExit(f"named non-ABSENT export in {label}: {line}")
            parsed.append(
                (match.group(1), int(match.group(2)), match.group(4) == "ABSENT")
            )
        elif "@" in line and not line.lstrip().startswith(";"):
            raise SystemExit(f"unparsed export in {label}: {line}")
    if not parsed:
        raise SystemExit(f"no exports parsed from {label}")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("frozen_def", type=pathlib.Path)
    parser.add_argument("generated_def", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    args = parser.parse_args()

    frozen_lines = trim_trailing_empty(read_lines(args.frozen_def))
    generated_lines = read_lines(args.generated_def)
    if generated_lines.count("; NEW:") != 1:
        raise SystemExit("generated DEF does not contain exactly one NEW separator")
    separator = generated_lines.index("; NEW:")
    generated_prefix = trim_trailing_empty(generated_lines[:separator])
    if len(generated_prefix) != len(frozen_lines):
        raise SystemExit("generated frozen prefix has a different line count")
    for line_no, (frozen, generated) in enumerate(
        zip(frozen_lines, generated_prefix), 1
    ):
        if semantic(frozen) != semantic(generated):
            raise SystemExit(
                f"frozen-prefix mismatch at line {line_no}: "
                f"{frozen!r} != {generated!r}"
            )

    frozen_exports = exports(frozen_lines, "frozen DEF")
    generated_exports = exports(generated_lines, "generated DEF")
    if len(frozen_exports) != 4604:
        raise SystemExit(
            f"frozen export count is {len(frozen_exports)}, expected 4604"
        )
    if [ordinal for _, ordinal, _ in frozen_exports] != list(range(1, 4605)):
        raise SystemExit("frozen ordinals are not the exact 1-4604 sequence")
    if generated_exports[:4604] != frozen_exports:
        raise SystemExit("generated ordinals 1-4604 differ from the frozen ABI")
    if tuple(generated_exports[4604:]) != EXPECTED_ADDITIONS:
        raise SystemExit("generated GCCE suffix differs from the reviewed aliases")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.frozen_def, args.output_dir / "stem-avkon-frozen-exports.def")
    shutil.copyfile(
        args.generated_def, args.output_dir / "stem-avkon-generated-exports.def"
    )
    (args.output_dir / "stem-avkon-generated-frozen-prefix.def").write_text(
        "\n".join(generated_prefix) + "\n", encoding="latin-1"
    )
    result = (
        "STATUS=HTCLEO_AVKON_ABI_OK\n"
        "FROZEN_EXPORTS=4604\n"
        "GENERATED_FROZEN_PREFIX=exact-symbol-ordinal-noname-absent\n"
        "GCCE_APPENDED_CONSTRUCTOR_ALIASES=9\n"
        "GENERATED_EXPORTS=4613\n"
    )
    (args.output_dir / "STEM-AVKON-ABI-RESULT.txt").write_text(
        result, encoding="ascii"
    )
    print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
