#!/usr/bin/env python3
"""Materialise missing GCCE import DSOs for the Hitchcock source build.

The S60 PDK ships these dependencies as E32 DLLs plus frozen EABI DEF files,
but omits their GCCE ``.dso`` import libraries.  Generate import-only DSOs
from those immutable interfaces; no runtime DLL is rebuilt or replaced.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ImportSpec:
    library: str
    binary: str
    definition: str


SPECS = (
    ImportSpec(
        "aknskins", "AKNSKINS.dll",
        "sf/mw/uiresources/skins/AknSkins/EABI/AKNSKINSU.DEF",
    ),
    ImportSpec(
        "aknskinsrv", "AKNSKINSRV.dll",
        "sf/mw/uiresources/skins/AknSkins/EABI/AKNSKINSRVU.DEF",
    ),
    ImportSpec(
        "aknicon", "AknIcon.dll",
        "sf/mw/uiresources/uigraphics/AknIcon/EABI/AknIconU.DEF",
    ),
    ImportSpec(
        "fontutils", "FontUtils.dll",
        "sf/mw/uiresources/fontsupport/fontutils/FontUtils/EABI/FONTUTILSU.DEF",
    ),
    ImportSpec(
        "aknpictograph", "AknPictograph.dll",
        "sf/mw/uiresources/pictographs/AknPictograph/EABI/AknPictographU.DEF",
    ),
    ImportSpec(
        "cdlengine", "CdlEngine.dll",
        "sf/mw/uiresources/layouts/cdl/CdlEngine/EABI/CdlEngineU.DEF",
    ),
    ImportSpec(
        "aknlayout2scalable", "AknLayout2Scalable.dll",
        "sf/mw/uiresources/layouts/aknlayout2/EABI/AknLayout2ScalableU.DEF",
    ),
    ImportSpec(
        "fontprovider", "FontProvider.dll",
        "sf/mw/uiresources/fontsupport/fontprovider/EABI/FONTPROVIDERU.DEF",
    ),
)


def checked_output(command: list[str]) -> str:
    return subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    ).stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    root = args.root.resolve()
    elf2e32 = root / "epoc32/tools/elf2e32"
    readelf = Path("/root/gcce-native-4.4.1/bin/arm-none-symbianelf-readelf")
    release = root / "epoc32/release/armv5/urel"
    libdir = root / "epoc32/release/armv5/lib"
    libdir.mkdir(parents=True, exist_ok=True)

    for spec in SPECS:
        binary = release / spec.binary
        definition = root / spec.definition
        for required in (elf2e32, readelf, binary, definition):
            if not required.is_file():
                raise SystemExit(f"missing Hitchcock import input: {required}")

        header = checked_output([
            str(elf2e32), "--dump=hseit", f"--e32input={binary}",
        ])
        sid_match = re.search(r"^Secure ID:\s*([0-9a-fA-F]+)$", header, re.M)
        version_match = re.search(
            r"^Module Version:\s*(\d+)\.(\d+)$", header, re.M
        )
        exports_match = re.search(
            r"^Number of exports\s*=\s*(\d+)$", header, re.M
        )
        if not (sid_match and version_match and exports_match):
            raise SystemExit(f"could not parse E32 ABI header: {binary}")

        major = int(version_match.group(1))
        minor = int(version_match.group(2))
        version = f"{major}.{minor}"
        version_tag = f"{major:04x}{minor:04x}"
        expected_exports = int(exports_match.group(1))
        ordinals = [
            int(value)
            for value in re.findall(
                r"@\s*(\d+)\s+NONAME(?:\s|$)",
                definition.read_text(encoding="utf-8", errors="strict"),
            )
        ]
        if not ordinals or max(ordinals) != expected_exports:
            raise SystemExit(
                f"DEF/E32 export mismatch for {spec.library}: "
                f"max DEF ordinal={max(ordinals) if ordinals else 0}, "
                f"E32 exports={expected_exports}"
            )

        versioned = libdir / f"{spec.library}{{{version_tag}}}.dso"
        unversioned = libdir / f"{spec.library}.dso"
        command = [
            str(elf2e32),
            f"--sid=0x{sid_match.group(1)}",
            f"--version={version}",
            f"--definput={definition}",
            f"--dso={versioned}",
            f"--linkas={binary.stem}{{{version_tag}}}.dll",
        ]
        subprocess.run(command, check=True)
        shutil.copy2(versioned, unversioned)

        dynamic = checked_output([str(readelf), "-d", str(versioned)])
        expected_soname = f"{spec.library}{{{version_tag}}}.dso"
        if expected_soname not in dynamic:
            raise SystemExit(
                f"unexpected import DSO SONAME for {spec.library}: "
                f"expected {expected_soname}"
            )
        if versioned.read_bytes() != unversioned.read_bytes():
            raise SystemExit(f"versioned DSO copy mismatch: {spec.library}")
        print(
            f"HTCLEO_HITCHCOCK_IMPORT_DSO={spec.library} "
            f"sid={sid_match.group(1).lower()} version={version} "
            f"exports={expected_exports}"
        )


if __name__ == "__main__":
    main()
