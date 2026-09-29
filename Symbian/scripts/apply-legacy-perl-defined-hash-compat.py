#!/usr/bin/env python3
"""Make the PDK 3.0.4 romutl module loadable by current Perl.

Perl removed ``defined(%hash)`` after the PDK was released.  The original
check only asks whether a platform key already exists, so ``exists`` preserves
the intended predicate without changing spitool's archive output.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MARKER = "HTCLEO_MODERN_PERL_DEFINED_HASH_COMPAT_V1"


def verify(path: Path) -> None:
    text = path.read_text(encoding="latin-1")
    checks = {
        "marker": text.count(MARKER) == 1,
        "BSF predicate": text.count("if (exists $Plat{$BSF}) {") == 1,
        "root predicate": text.count(
            "if (exists $Plat{$root} || $Armv5Flag)"
        ) == 1,
        "ASSP predicate": text.count("if (exists $Plat{$ASSP}) {") == 1,
        "removed syntax": re.search(r"defined\s+%\{\$Plat", text) is None,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("romutl Perl compatibility audit failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()
    path = args.epocroot / "epoc32/tools/romutl.pm"
    if not path.is_file():
        raise SystemExit(f"missing PDK romutl module: {path}")
    text = path.read_text(encoding="latin-1")
    replacements = (
        (
            "        if (defined %{$Plat{$BSF}}) {",
            "        if (exists $Plat{$BSF}) {",
        ),
        (
            "        if (defined %{$Plat{$root}} || $Armv5Flag) ",
            "        if (exists $Plat{$root} || $Armv5Flag) ",
        ),
        (
            "        if (defined %{$Plat{$ASSP}}) {",
            "        if (exists $Plat{$ASSP}) {",
        ),
    )
    for old, new in replacements:
        if old in text:
            if text.count(old) != 1:
                raise SystemExit(
                    f"expected one legacy predicate {old!r}, found {text.count(old)}"
                )
            text = text.replace(old, new, 1)
        elif text.count(new) != 1:
            raise SystemExit(f"legacy and modern predicates are both absent: {old!r}")
    if MARKER not in text:
        anchor = "        if (exists $Plat{$BSF}) {"
        text = text.replace(
            anchor,
            f"        # {MARKER}\n{anchor}",
            1,
        )
    path.write_text(text, encoding="latin-1")
    verify(path)
    print("HTCLEO_MODERN_PERL_DEFINED_HASH_COMPAT=installed module=romutl.pm")


if __name__ == "__main__":
    main()
