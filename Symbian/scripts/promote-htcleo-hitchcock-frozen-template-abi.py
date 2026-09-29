#!/usr/bin/env python3
"""Promote four GCCE template ABI symbols from weak to global binding.

The released Hitchcock frozen DEF exports two CHuiFxGenericParameter RTTI
objects and two vtables.  GCCE 4.4 emits template COMDAT objects with weak
binding, while the matching vintage elf2e32 accepts only global definitions
for frozen exports.  Change only ELF32 ``st_info`` binding in the one
source-built trace object; contents, relocations and symbol names are left
untouched.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


TARGETS = {
    "_ZTI22CHuiFxGenericParameterI4TRgb14RHuiFxTimeLineIS0_mEL19THuiFxParameterType1EE",
    "_ZTI22CHuiFxGenericParameterIf14RHuiFxTimeLineIflEL19THuiFxParameterType0EE",
    "_ZTV22CHuiFxGenericParameterI4TRgb14RHuiFxTimeLineIS0_mEL19THuiFxParameterType1EE",
    "_ZTV22CHuiFxGenericParameterIf14RHuiFxTimeLineIflEL19THuiFxParameterType0EE",
}


def c_string(data: bytearray, offset: int) -> str:
    end = data.find(b"\0", offset)
    if end < 0:
        raise SystemExit("unterminated ELF string table entry")
    return bytes(data[offset:end]).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("object", type=Path)
    args = parser.parse_args()

    data = bytearray(args.object.read_bytes())
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
        raise SystemExit("expected little-endian ELF32 object")

    shoff = struct.unpack_from("<I", data, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", data, 46)
    if shentsize < 40 or shnum == 0:
        raise SystemExit("invalid ELF32 section table")
    sections = [
        struct.unpack_from("<10I", data, shoff + index * shentsize)
        for index in range(shnum)
    ]

    found: dict[str, int] = {}
    changed: list[str] = []
    for section in sections:
        _, section_type, _, _, offset, size, link, _, _, entsize = section
        if section_type != 2:  # SHT_SYMTAB
            continue
        if link >= len(sections) or entsize < 16 or size % entsize:
            raise SystemExit("invalid ELF32 symbol table")
        string_section = sections[link]
        string_offset = string_section[4]
        for item in range(size // entsize):
            symbol_offset = offset + item * entsize
            name_offset = struct.unpack_from("<I", data, symbol_offset)[0]
            if not name_offset:
                continue
            name = c_string(data, string_offset + name_offset)
            if name not in TARGETS:
                continue
            found[name] = found.get(name, 0) + 1
            info = data[symbol_offset + 12]
            binding, symbol_type = info >> 4, info & 0x0F
            if binding == 2:  # STB_WEAK -> STB_GLOBAL
                data[symbol_offset + 12] = (1 << 4) | symbol_type
                changed.append(name)
            elif binding != 1:
                raise SystemExit(f"unexpected binding {binding} for {name}")

    if set(found) != TARGETS or any(count != 1 for count in found.values()):
        missing = sorted(TARGETS - set(found))
        raise SystemExit(f"frozen template ABI symbol mismatch; missing={missing}")
    if len(changed) not in (0, len(TARGETS)):
        raise SystemExit("partially promoted frozen template ABI object")
    if changed:
        args.object.write_bytes(data)
    print(
        "HTCLEO_HITCHCOCK_TEMPLATE_ABI="
        + ("promoted" if changed else "installed")
        + f" symbols={len(TARGETS)}"
    )


if __name__ == "__main__":
    main()
