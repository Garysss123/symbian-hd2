#!/usr/bin/env python3
"""Expose only the legacy Avkon symbols required by its frozen ABI.

GCCE 4.4 emits the concrete list-box template instantiations as weak symbols
and keeps the NONSHARABLE long-tap destructor hidden.  Vintage ``elf2e32``
accepts neither state for a frozen export, even though the implementations are
present.  The popup template RTTI/vtable is emitted in five COMDAT objects, so
all five copies must agree or the linker may select an unpromoted definition.
Change only ELF32 symbol binding/visibility in the affected objects; names,
contents, relocations and section placement remain untouched.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


LONG_TAP_TARGETS = {
    "_ZN19CAknLongTapDetectorD0Ev",
    "_ZN19CAknLongTapDetectorD1Ev",
    "_ZN19CAknLongTapDetectorD2Ev",
}

LIST_TARGETS = {
    "_ZN23AknListBoxLinesTemplateI17CAknColumnListBoxE11SizeChangedEv",
    "_ZN23AknListBoxLinesTemplateI17CAknColumnListBoxEC1Ei",
    "_ZN23AknListBoxLinesTemplateI17CAknColumnListBoxEC2Ei",
    "_ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxE11SizeChangedEv",
    "_ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxEC1Ei",
    "_ZN23AknListBoxLinesTemplateI19CEikSettingsListBoxEC2Ei",
    "_ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxE11SizeChangedEv",
    "_ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxEC1Ei",
    "_ZN23AknListBoxLinesTemplateI24CEikFormattedCellListBoxEC2Ei",
    "_ZNK17AknPopupListEmptyI24CEikFormattedCellListBoxE4DrawERK5TRect",
    "_ZNK23AknListBoxLinesTemplateI17CAknColumnListBoxE16ComponentControlEi",
    "_ZNK23AknListBoxLinesTemplateI17CAknColumnListBoxE22CountComponentControlsEv",
    "_ZNK23AknListBoxLinesTemplateI17CAknColumnListBoxE4DrawERK5TRect",
    "_ZNK23AknListBoxLinesTemplateI19CEikSettingsListBoxE16ComponentControlEi",
    "_ZNK23AknListBoxLinesTemplateI19CEikSettingsListBoxE22CountComponentControlsEv",
    "_ZNK23AknListBoxLinesTemplateI19CEikSettingsListBoxE4DrawERK5TRect",
    "_ZNK23AknListBoxLinesTemplateI24CEikFormattedCellListBoxE16ComponentControlEi",
    "_ZNK23AknListBoxLinesTemplateI24CEikFormattedCellListBoxE22CountComponentControlsEv",
    "_ZNK23AknListBoxLinesTemplateI24CEikFormattedCellListBoxE4DrawERK5TRect",
    "_ZTI17AknPopupListEmptyI24CEikFormattedCellListBoxE",
    "_ZTI23AknListBoxLinesTemplateI17CAknColumnListBoxE",
    "_ZTI23AknListBoxLinesTemplateI19CEikSettingsListBoxE",
    "_ZTI23AknListBoxLinesTemplateI24CEikFormattedCellListBoxE",
    "_ZTV17AknPopupListEmptyI24CEikFormattedCellListBoxE",
    "_ZTV23AknListBoxLinesTemplateI17CAknColumnListBoxE",
    "_ZTV23AknListBoxLinesTemplateI19CEikSettingsListBoxE",
    "_ZTV23AknListBoxLinesTemplateI24CEikFormattedCellListBoxE",
}

POPUP_COMDAT_TARGETS = {
    "_ZTI17AknPopupListEmptyI24CEikFormattedCellListBoxE",
    "_ZTV17AknPopupListEmptyI24CEikFormattedCellListBoxE",
}

TARGETS_BY_OBJECT = {
    "aknlongtapdetector.o": LONG_TAP_TARGETS,
    "aknlists.o": LIST_TARGETS,
    "AknPopupField.o": POPUP_COMDAT_TARGETS,
    "AknPopupSettingPage.o": POPUP_COMDAT_TARGETS,
    "aknenv.o": POPUP_COMDAT_TARGETS,
    "aknlib.o": POPUP_COMDAT_TARGETS,
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
        raise SystemExit(f"unexpected Avkon ABI object: {args.object.name}")

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
    changed: set[str] = set()
    for section in sections:
        _, section_type, _, _, offset, size, link, _, _, entsize = section
        if section_type != 2:  # SHT_SYMTAB
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
                raise SystemExit(f"undefined frozen Avkon ABI symbol: {name}")

            info = data[symbol_offset + 12]
            binding, symbol_type = info >> 4, info & 0x0F
            if binding == 2:  # STB_WEAK -> STB_GLOBAL
                data[symbol_offset + 12] = (1 << 4) | symbol_type
                changed.add(name)
            elif binding != 1:
                raise SystemExit(f"unexpected binding {binding} for {name}")

            other = data[symbol_offset + 13]
            visibility = other & 0x03
            if visibility == 2:  # STV_HIDDEN -> STV_DEFAULT
                data[symbol_offset + 13] = other & ~0x03
                changed.add(name)
            elif visibility != 0:
                raise SystemExit(f"unexpected visibility {visibility} for {name}")

    if set(found) != targets or any(count != 1 for count in found.values()):
        missing = sorted(targets - set(found))
        duplicates = sorted(name for name, count in found.items() if count != 1)
        raise SystemExit(
            "frozen Avkon ABI symbol mismatch; "
            f"missing={missing} duplicates={duplicates}"
        )

    if changed:
        args.object.write_bytes(data)
    print(
        "HTCLEO_AVKON_FROZEN_ABI="
        + ("promoted" if changed else "installed")
        + f" object={args.object.name} symbols={len(targets)} changed={len(changed)}"
    )


if __name__ == "__main__":
    main()
