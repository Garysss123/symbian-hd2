#!/usr/bin/env python3
"""Create an immutable decoder for HTCLEO EFILE loader-log records."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


STAGES = (
    (0x00001001, "ELoadLibrary dispatch armed after .dll extension"),
    (0x00001002, "loader search path IPC read returned"),
    (0x00001003, "substituted-drive path normalization returned"),
    (0x00001004, "TLdrInfo IPC read returned; detail is requested UID3"),
    (0x00001005, "before LoadLibrary; detail is owner type"),
    (0x00001006, "LoadLibrary returned; detail is library handle"),
    (0x00001101, "LoadLibrary entry; detail is requested UID3"),
    (0x00001102, "client thread lookup returned"),
    (0x00001103, "client process lookup returned"),
    (0x00001104, "client code-segment attributes resolved"),
    (0x00001105, "E32Image allocation completed"),
    (0x00001106, "before top-level E32Image::LoadCodeSeg"),
    (0x00001107, "top-level E32Image::LoadCodeSeg returned"),
    (0x00001108, "before E32Loader::LibraryCreate"),
    (0x00001109, "E32Loader::LibraryCreate returned"),
    (0x0000110A, "TLdrInfo reply update returned"),
    (0x0000110B, "LoadLibrary final return boundary"),
    (0x000011E1, "LoadLibrary rejected unexpected UID1"),
    (0x00002001, "E32Image::LoadCodeSeg entry"),
    (0x00002002, "RImageFinder::Set returned"),
    (0x00002003, "before RImageFinder::Search"),
    (0x00002004, "RImageFinder::Search returned"),
    (0x00002005, "before request-form DoLoadCodeSeg"),
    (0x00002006, "request-form DoLoadCodeSeg returned"),
    (0x00002101, "request-form DoLoadCodeSeg entry"),
    (0x00002102, "E32Image::Construct returned; detail is UID3"),
    (0x00002104, "before E32Loader::CodeSegCreate"),
    (0x00002105, "E32Loader::CodeSegCreate returned"),
    (0x00002106, "before RAM image load"),
    (0x00002107, "RAM image load returned"),
    (0x00002108, "before main-image ProcessImports"),
    (0x00002109, "main-image ProcessImports returned"),
    (0x0000210A, "E32Loader::CodeSegLoaded returned"),
    (0x0000210B, "request-form DoLoadCodeSeg final return"),
    (0x000021E1, "EXE dependency compatibility rejection"),
    (0x000021E2, "main DLL ABI compatibility rejection"),
    (0x000021E3, "already-loaded or always-loaded early success"),
    (0x00002201, "LoadToRam entry"),
    (0x00002202, "rest-of-file allocation completed"),
    (0x00002203, "LoadFile returned"),
    (0x00002204, "code relocation validation returned"),
    (0x00002205, "data relocation validation returned"),
    (0x00002206, "RelocateCode returned"),
    (0x00002207, "LoadAndRelocateData returned"),
    (0x00002208, "ReadImportData returned"),
    (0x00002209, "LoadToRam final return"),
    (0x00002301, "LoadFile entry; detail is compression UID"),
    (0x00002302, "decompression/read route returned"),
    (0x00002303, "LoadFile final return after temporary data release"),
    (0x00002401, "ROM-XIP DoLoadCodeSeg entry; detail is UID3"),
    (0x00002402, "ROM-XIP always-loaded early success"),
    (0x00002403, "ROM-XIP already-loaded check returned"),
    (0x00002404, "before ROM-XIP CodeSegCreate"),
    (0x00002405, "ROM-XIP CodeSegCreate returned"),
    (0x00003001, "ProcessImports entry; detail is dependency count"),
    (0x00003002, "ProcessImports no-import/always-loaded success"),
    (0x00003003, "main image added to recursive array"),
    (0x00003004, "recursive LoadDlls returned"),
    (0x00003005, "FixupDlls returned"),
    (0x00003006, "FinaliseDlls returned"),
    (0x00003007, "ProcessImports final return after cleanup"),
    (0x00004001, "LoadDlls recursion entry"),
    (0x0000400F, "LoadDlls recursion successful return"),
    (0x00004010, "dependency iteration entry; detail index/count"),
    (0x00004011, "RAM dependency name parsed; detail requested UID3"),
    (0x00004012, "required import-list extraction returned"),
    (0x00004013, "before dependency finder Set"),
    (0x00004014, "dependency finder Set returned"),
    (0x00004015, "before SearchExisting"),
    (0x00004016, "SearchExisting returned"),
    (0x00004017, "before dependency Search"),
    (0x00004018, "dependency Search returned"),
    (0x00004019, "existing dependency resolution merged"),
    (0x00004020, "new dependency E32Image allocation completed"),
    (0x00004021, "before dependency DoLoadCodeSeg"),
    (0x00004022, "dependency DoLoadCodeSeg returned"),
    (0x00004023, "new dependency added to recursive array"),
    (0x00004024, "before child recursive LoadDlls"),
    (0x00004025, "child recursive LoadDlls returned"),
    (0x00004026, "before CodeSegAddDependency"),
    (0x00004027, "CodeSegAddDependency returned"),
    (0x00005001, "RImageFinder::Search entry"),
    (0x00005002, "before explicit-path search"),
    (0x00005003, "explicit-path search returned"),
    (0x00005004, "before default-path search"),
    (0x00005005, "default-path search returned"),
    (0x00005006, "RImageFinder::Search final result"),
    (0x00005101, "before Z: SearchSingleDir"),
    (0x00005102, "Z: SearchSingleDir returned"),
    (0x00005201, "RImageFinder::Try candidate entry; detail UID3"),
    (0x00005202, "RImageFinder::Try accepted candidate"),
    (0x00006001, "ELoadLibrary switch case exited; detail is message function"),
    (0x00006002, "RLdrReq::Close entry; detail bits are filename/cmd/path allocations"),
    (0x00006003, "request filename delete returned"),
    (0x00006004, "request command delete returned"),
    (0x00006005, "request path delete returned"),
    (0x00006006, "client thread handle Close returned"),
    (0x00006007, "client process handle Close returned"),
    (0x00006008, "RLdrReq::Close final return boundary"),
    (0x00006009, "loader request cleanup finished; detail is message-null flag"),
    (0x0000600A, "immediately before client aMessage.Complete"),
    (0x0000600B, "client aMessage.Complete returned"),
)


def tag(name: str) -> int:
    base = re.split(r"[\\/]", name)[-1].lower()
    value = 2166136261
    for byte in base.encode("latin-1"):
        value ^= byte
        value = (value * 16777619) & 0xFFFFFFFF
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="nvgrenderstage.dll")
    parser.add_argument("--log-file", default="LDRLOG.TXT")
    parser.add_argument("recipe", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    target = args.target.lower()
    if re.fullmatch(r"[a-z0-9_.-]+\.dll", target) is None:
        raise SystemExit(f"invalid target DLL basename: {args.target}")
    log_file = args.log_file.upper()
    if re.fullmatch(r"[A-Z0-9]{1,8}\.[A-Z0-9]{1,3}", log_file) is None:
        raise SystemExit(f"log file is not an 8.3 basename: {args.log_file}")
    text = args.recipe.read_text(encoding="utf-8", errors="replace")
    destinations = set()
    for match in re.finditer(r'"(sys\\bin\\[^"\\]+)"', text, re.IGNORECASE):
        destinations.add(match.group(1).split("\\")[-1].lower())

    by_tag: dict[int, str] = {tag(""): "<empty>"}
    for name in sorted(destinations):
        value = tag(name)
        previous = by_tag.get(value)
        if previous is not None and previous != name:
            raise SystemExit(
                f"FNV-1a collision 0x{value:08x}: {previous} versus {name}"
            )
        by_tag[value] = name

    lines = [
        "STATUS=HTCLEO_LOADER_LOG_MAP_OK",
        "RECORD_FORMAT=HTCLEO_LDR-seq4-stage8-result8-tag8-detail8",
        "RECORD_BYTES=53",
        "MAX_RECORDS=1024",
        f"TRACE_GATE=top-level-{target}-ELoadLibrary-only",
        f"LOG_PATH=C:\\Symbian3\\{log_file}",
        "TAG_ALGORITHM=FNV1a32-lowercase-basename",
        f"STAGE_COUNT={len(STAGES)}",
        f"MODULE_COUNT={len(by_tag)}",
        "",
        "[STAGES]",
    ]
    lines.extend(f"{stage:08x}\t{description}" for stage, description in STAGES)
    lines.extend(("", "[MODULES]"))
    lines.extend(f"{value:08x}\t{name}" for value, name in sorted(by_tag.items()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"HTCLEO_LOADER_LOG_MAP={args.output} "
        f"stages={len(STAGES)} modules={len(by_tag)}"
    )


if __name__ == "__main__":
    main()
