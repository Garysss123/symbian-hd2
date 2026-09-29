#!/usr/bin/env python3
"""Create the deployable HTCLEO full-ROM image with routine displays retired.

The native full-ROM build intentionally retains the ten FAT progress calls, the
final ESTART UDF and the three early-extension renderer calls as an explicitly
named diagnostic image.  Normal packages must consume the canonical image made
by this tool instead.  Every patched instruction is re-resolved and verified
against the same build before it is replaced with an ARM NOP.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
import tempfile
from pathlib import Path


ROM_BASE = 0x12200000
NOP = 0xE1A00000
UDF = 0xE7F000F0
TOP_MASK = 0xFFFF0FFF
TOP_VALUE = 0xE24F0008
BL_MASK = 0xFF000000
BL_VALUE = 0xEB000000
PRE_UDF = 0xE24F0004
POST_UDF = 0xE1A00004
FAT_STAGES = tuple(f"F13{x}" for x in "123456789A")
EXTENSION_PATTERNS = (
    ("StartExtensions", 0xE1A00006, 0xE3E00000, 0xE12FFF36),
    ("InitExt0", 0xE1A00004, 0xE3E00001, 0xE12FFF34),
    ("InitData", 0xE38E120A, 0xE3E00002, 0xE12FFF34),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_kv(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if "=" in raw:
            key, value = raw.split("=", 1)
            result[key] = value
    return result


def word(data: bytes | bytearray, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise ValueError(f"ROM word offset out of range: 0x{offset:08x}")
    return struct.unpack_from("<I", data, offset)[0]


def write_word(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<I", data, offset, value)


def parse_runtime(mapping: dict[str, str], key: str) -> int:
    raw = mapping.get(key, "")
    if len(raw) != 10 or not raw.startswith("0x"):
        raise ValueError(f"missing or malformed active map entry: {key}")
    try:
        value = int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"missing or malformed active map entry: {key}") from exc
    if not 0 <= value <= 0xFFFFFFFF:
        raise ValueError(f"runtime address is not uint32: {key}={raw}")
    return value


def branch_target(call_runtime: int, instruction: int) -> int:
    if instruction & BL_MASK != BL_VALUE:
        raise ValueError(
            f"0x{call_runtime:08X} is not an ARM BL: 0x{instruction:08X}"
        )
    immediate = instruction & 0x00FFFFFF
    if immediate & 0x00800000:
        immediate -= 0x01000000
    return (call_runtime + 8 + immediate * 4) & 0xFFFFFFFF


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("active_image", type=Path)
    parser.add_argument("active_probe_map", type=Path)
    parser.add_argument("canonical_image", type=Path)
    parser.add_argument("retirement_map", type=Path)
    args = parser.parse_args()

    active_image = args.active_image.resolve()
    active_map_path = args.active_probe_map.resolve()
    canonical_image = args.canonical_image.resolve()
    retirement_map = args.retirement_map.resolve()
    if canonical_image == active_image:
        raise SystemExit("refusing to patch the diagnostic image in place")
    if retirement_map in (active_image, canonical_image, active_map_path):
        raise SystemExit("retirement map path aliases an input or image")
    if not active_image.is_file() or not active_map_path.is_file():
        raise SystemExit("active image or same-build probe map is missing")

    source = active_image.read_bytes()
    if not source or len(source) % 4:
        raise SystemExit("active image is empty or not ARM-word aligned")
    output = bytearray(source)
    mapping = read_kv(active_map_path)
    if mapping.get("RETURNING_CHECKPOINT_COUNT") != "10":
        raise SystemExit("active map does not contain ten returning checkpoints")
    if mapping.get("EFAT32_RETURNING_CHECKPOINT_COUNT") != "10":
        raise SystemExit("active map does not contain ten EFAT32 checkpoints")

    retired_offsets: set[int] = set()
    fat_records: list[tuple[str, int, int, int, int]] = []
    fat_target: int | None = None
    for stage in FAT_STAGES:
        top_runtime = parse_runtime(mapping, f"CHECKPOINT_{stage}_RUNTIME_ADDRESS")
        top_offset = top_runtime - ROM_BASE
        top_word = word(source, top_offset)
        if top_word & TOP_MASK != TOP_VALUE:
            raise SystemExit(
                f"{stage}: top 0x{top_runtime:08X} is not sub Rd,pc,#8 "
                f"(0x{top_word:08X})"
            )

        call_offset = -1
        call_word = 0
        for delta in range(4, 65, 4):
            candidate = word(source, top_offset + delta)
            if candidate & BL_MASK == BL_VALUE:
                call_offset = top_offset + delta
                call_word = candidate
                break
        if call_offset < 0:
            raise SystemExit(f"{stage}: no ARM BL in reporter window")
        call_runtime = ROM_BASE + call_offset
        target = branch_target(call_runtime, call_word)
        if fat_target is None:
            fat_target = target
        elif target != fat_target:
            raise SystemExit(
                f"{stage}: HAL target 0x{target:08X} differs from "
                f"0x{fat_target:08X}"
            )
        retired_offsets.add(call_offset)
        write_word(output, call_offset, NOP)
        fat_records.append((stage, top_runtime, call_runtime, call_word, target))

    udf_runtime = parse_runtime(mapping, "ESTART_UDF_RUNTIME_ADDRESS")
    udf_offset = udf_runtime - ROM_BASE
    if (
        word(source, udf_offset - 4) != PRE_UDF
        or word(source, udf_offset) != UDF
        or word(source, udf_offset + 4) != POST_UDF
    ):
        raise SystemExit("final ESTART UDF neighbourhood differs from same-build map")
    retired_offsets.add(udf_offset)
    write_word(output, udf_offset, NOP)

    extension_records: list[tuple[str, int, int, int]] = []
    extension_target: int | None = None
    search_words = min(len(source) // 4 - 3, 0x00200000 // 4)
    for name, before, after, tail in EXTENSION_PATTERNS:
        matches: list[int] = []
        for index in range(1, search_words):
            candidate = word(source, index * 4)
            if (
                word(source, (index - 1) * 4) == before
                and candidate & BL_MASK == BL_VALUE
                and word(source, (index + 1) * 4) == after
                and word(source, (index + 2) * 4) == tail
            ):
                matches.append(index * 4)
        if len(matches) != 1:
            raise SystemExit(
                f"{name}: expected one same-image renderer call, found {len(matches)}"
            )
        call_offset = matches[0]
        call_runtime = ROM_BASE + call_offset
        call_word = word(source, call_offset)
        target = branch_target(call_runtime, call_word)
        if extension_target is None:
            extension_target = target
        elif target != extension_target:
            raise SystemExit(
                f"{name}: renderer target 0x{target:08X} differs from "
                f"0x{extension_target:08X}"
            )
        retired_offsets.add(call_offset)
        write_word(output, call_offset, NOP)
        extension_records.append((name, call_runtime, call_word, target))

    if extension_target is None or fat_target is None:
        raise SystemExit("failed to resolve display targets")
    all_extension_calls: set[int] = set()
    for offset in range(0, len(source), 4):
        instruction = word(source, offset)
        if instruction & BL_MASK == BL_VALUE:
            if branch_target(ROM_BASE + offset, instruction) == extension_target:
                all_extension_calls.add(offset)
    classified_extension_calls = {runtime - ROM_BASE for _, runtime, _, _ in extension_records}
    if all_extension_calls != classified_extension_calls:
        raise SystemExit(
            "extension renderer call inventory differs from the three classified sites: "
            f"all={len(all_extension_calls)} classified={len(classified_extension_calls)}"
        )
    if len(retired_offsets) != 14:
        raise SystemExit(
            f"expected exactly fourteen retired instructions, got {len(retired_offsets)}"
        )

    changed_offsets = [
        offset for offset, (old, new) in enumerate(zip(source, output)) if old != new
    ]
    if not 14 <= len(changed_offsets) <= 56:
        raise SystemExit(
            "unexpected changed-byte count for fourteen ARM words: "
            f"{len(changed_offsets)}"
        )
    for offset in changed_offsets:
        if offset - offset % 4 not in retired_offsets:
            raise SystemExit(f"unexpected ROM byte change at 0x{offset:08X}")
    if any(word(output, offset) != NOP for offset in retired_offsets):
        raise SystemExit("one or more retired instructions are not ARM NOPs")

    output_bytes = bytes(output)
    lines = [
        "STATUS=HTCLEO_CANONICAL_NO_DISPLAY_OK",
        "CANONICAL_BASELINE_ITERATION=419",
        "FUNCTIONAL_LINEAGE=430",
        f"ACTIVE_IMAGE={active_image}",
        f"ACTIVE_PROBE_MAP={active_map_path}",
        f"ACTIVE_SHA256={sha256(source)}",
        f"CANONICAL_IMAGE={canonical_image}",
        f"CANONICAL_SHA256={sha256(output_bytes)}",
        f"SIZE={len(output_bytes)}",
        "ROM_LINEAR_BASE=0x12200000",
        "RETIRED_FAT_DISPLAY_CALLS=10",
        "RETIRED_ESTART_UDF=1",
        "RETIRED_EXTENSION_DISPLAY_CALLS=3",
        "TOTAL_RETIRED_RUNTIME_INSTRUCTIONS=14",
        f"ROM_MODIFIED_BYTE_COUNT={len(changed_offsets)}",
        f"FAT_HAL_TARGET=0x{fat_target:08X}",
    ]
    for stage, top, call, original, _ in fat_records:
        lines.extend(
            (
                f"{stage}_TOP=0x{top:08X}",
                f"{stage}_CALL=0x{call:08X}",
                f"{stage}_ORIGINAL_WORD=0x{original:08X}",
                f"{stage}_REPLACEMENT_WORD=0x{NOP:08X}",
            )
        )
    lines.extend(
        (
            f"ESTART_UDF_RUNTIME_ADDRESS=0x{udf_runtime:08X}",
            f"ESTART_ORIGINAL_WORD=0x{UDF:08X}",
            f"ESTART_REPLACEMENT_WORD=0x{NOP:08X}",
            f"EXTENSION_RENDERER_TARGET=0x{extension_target:08X}",
        )
    )
    for name, call, original, _ in extension_records:
        key = name.upper()
        lines.extend(
            (
                f"{key}_CALL=0x{call:08X}",
                f"{key}_ORIGINAL_WORD=0x{original:08X}",
                f"{key}_REPLACEMENT_WORD=0x{NOP:08X}",
            )
        )
    lines.extend(
        (
            "PROGRESS_DISPLAY_CALLS_REMAINING=0",
            "ROUTINE_FRAMEBUFFER_WRITERS=0",
            "DIAGNOSTIC_ACTIVE_IMAGE_RETAINED=yes",
            "SD_DEPLOYED=no",
        )
    )

    atomic_write(canonical_image, output_bytes)
    atomic_write(retirement_map, ("\n".join(lines) + "\n").encode("utf-8"))
    print("STATUS=HTCLEO_CANONICAL_NO_DISPLAY_OK")
    print(f"ACTIVE_SHA256={sha256(source)}")
    print(f"CANONICAL_SHA256={sha256(output_bytes)}")
    print("TOTAL_RETIRED_RUNTIME_INSTRUCTIONS=14")
    print(f"ROM_MODIFIED_BYTE_COUNT={len(changed_offsets)}")
    print("PROGRESS_DISPLAY_CALLS_REMAINING=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
