#!/usr/bin/env python3
"""Expose the legacy Xn template/class symbols required by its frozen ABI."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


BREADTH_TARGETS = {
    "_ZTI27CXnNodeBreadthFirstIteratorI7CXnNodeE",
    "_ZTV27CXnNodeBreadthFirstIteratorI7CXnNodeE",
}

ICON_TARGETS = {
    "_ZTIN21CXnControlAdapterImpl13TIconProviderE",
    "_ZTVN21CXnControlAdapterImpl13TIconProviderE",
}

TARGETS_BY_OBJECT = {
    "xnuiengineimpl.o": BREADTH_TARGETS,
    "xnutils.o": BREADTH_TARGETS,
    "xncontroladapterimpl.o": ICON_TARGETS,
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
    targets = TARGETS_BY_OBJECT.get(args.object.name)
    if targets is None:
        raise SystemExit(f"unexpected Xn ABI object: {args.object.name}")

    data = bytearray(args.object.read_bytes())
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
        raise SystemExit("expected little-endian ELF32 object")
    shoff = struct.unpack_from("<I", data, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", data, 46)
    if shentsize < 40 or shnum == 0:
        raise SystemExit("invalid ELF32 section table")
    sections = [
        struct.unpack_from("<10I", data, shoff + i * shentsize)
        for i in range(shnum)
    ]

    found: dict[str, int] = {}
    changed: set[str] = set()
    for section in sections:
        _, section_type, _, _, offset, size, link, _, _, entsize = section
        if section_type != 2:
            continue
        if link >= len(sections) or entsize < 16 or size % entsize:
            raise SystemExit("invalid ELF32 symbol table")
        string_offset = sections[link][4]
        for item in range(size // entsize):
            symbol_offset = offset + item * entsize
            name_offset = struct.unpack_from("<I", data, symbol_offset)[0]
            if not name_offset:
                continue
            name = c_string(data, string_offset + name_offset)
            if name not in targets:
                continue
            found[name] = found.get(name, 0) + 1
            section_index = struct.unpack_from("<H", data, symbol_offset + 14)[0]
            if section_index == 0:
                raise SystemExit(f"undefined frozen Xn ABI symbol: {name}")
            info = data[symbol_offset + 12]
            binding, symbol_type = info >> 4, info & 0x0F
            if binding == 2:
                data[symbol_offset + 12] = (1 << 4) | symbol_type
                changed.add(name)
            elif binding != 1:
                raise SystemExit(f"unexpected binding {binding} for {name}")
            other = data[symbol_offset + 13]
            visibility = other & 0x03
            if visibility == 2:
                data[symbol_offset + 13] = other & ~0x03
                changed.add(name)
            elif visibility != 0:
                raise SystemExit(f"unexpected visibility {visibility} for {name}")

    if set(found) != targets or any(count != 1 for count in found.values()):
        missing = sorted(targets - set(found))
        duplicate = sorted(k for k, v in found.items() if v != 1)
        raise SystemExit(
            f"frozen Xn ABI mismatch missing={missing} duplicate={duplicate}"
        )
    if changed:
        args.object.write_bytes(data)
    print(
        "HTCLEO_XN3LAYOUTENGINE_FROZEN_ABI="
        + ("promoted" if changed else "installed")
        + f" object={args.object.name} symbols={len(targets)} "
        + f"changed={len(changed)}"
    )


if __name__ == "__main__":
    main()
