#!/usr/bin/env python3
"""Create the immutable runtime-address map for HTCLEO screen reporters."""

from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys


EXTENSION = re.compile(
    r'^extension(?:\[[^\]]+\])?=([^\t"]+?)\s+"([^"]+)"', re.IGNORECASE
)
CODE_LINE = re.compile(r"^([0-9a-fA-F]{6,8}):\s+((?:[0-9a-fA-F]{8}\s+)+)")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_e32_words(
    elf2e32: pathlib.Path, image: pathlib.Path
) -> dict[int, int]:
    result = subprocess.run(
        [str(elf2e32), "--dump=c", f"--e32input={image}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    words: dict[int, int] = {}
    for line in result.stdout.splitlines():
        match = CODE_LINE.match(line)
        if not match:
            continue
        base = int(match.group(1), 16)
        for index, word in enumerate(match.group(2).split()):
            words[base + index * 4] = int(word, 16)
    return words


def parse_estart_udf(
    elf2e32: pathlib.Path, image: pathlib.Path
) -> tuple[int, int, list[int]]:
    words = parse_e32_words(elf2e32, image)
    udf_offsets = [offset for offset, word in words.items() if word == 0xE7F000F0]
    if len(udf_offsets) != 1:
        raise SystemExit(
            f"expected one UDF #0 in ESTART E32 code, found {len(udf_offsets)}"
        )
    udf_offset = udf_offsets[0]
    previous = words.get(udf_offset - 4)
    if previous != 0xE24F0004:
        raise SystemExit(
            "ESTART UDF is not immediately preceded by ARM sub r0,pc,#4: "
            f"{previous!r}"
        )
    progress_offsets = capture_offsets(words)
    return udf_offset, previous, progress_offsets


def capture_offsets(words: dict[int, int]) -> list[int]:
    # Each returning reporter captures the address of its own instruction with
    # `sub Rd,pc,#8`. Mask only Rd so register allocation may vary while an
    # unrelated PC arithmetic instruction is still rejected.
    return sorted(
        offset
        for offset, word in words.items()
        if word & 0xFFFF0FFF == 0xE24F0008
    )


def parse_checkpoint_image(
    elf2e32: pathlib.Path, image: pathlib.Path, expected: int
) -> list[int]:
    words = parse_e32_words(elf2e32, image)
    udf_offsets = [offset for offset, word in words.items() if word == 0xE7F000F0]
    if udf_offsets:
        raise SystemExit(f"returning checkpoint image contains UDF #0: {image}")
    offsets = capture_offsets(words)
    if len(offsets) != expected:
        raise SystemExit(
            f"expected {expected} returning captures in {image}, found "
            f"{len(offsets)}"
        )
    return offsets


def map_checkpoint_stages(
    elf2e32: pathlib.Path,
    image: pathlib.Path,
    prefix: int,
    stage_names: tuple[str, ...],
) -> dict[str, int]:
    """Pair each capture with the stage literal used by its HAL call.

    GCCE emits fixed stages as PC-relative literal loads.  Dynamic E709/E70A
    values are instead assembled from immediate ORRs before the HAL call.
    Decode both forms instead of assuming source/function link order.
    """
    words = parse_e32_words(elf2e32, image)
    family = prefix >> 20
    all_stages = {
        f"{family:03X}{index:X}": prefix | (index << 16)
        for index in range(1, 11)
    }
    wanted = {all_stages[stage]: stage for stage in stage_names}
    wanted_high = {value & 0xFFFF0000: value for value in wanted}

    def arm_immediate(instruction: int) -> int:
        immediate = instruction & 0xFF
        rotation = ((instruction >> 8) & 0xF) * 2
        if rotation:
            immediate = (
                (immediate >> rotation)
                | (immediate << (32 - rotation))
            ) & 0xFFFFFFFF
        return immediate

    def scan_window(
        words: dict[int, int], offsets: range, stop_on_branch: bool
    ) -> set[int]:
        matches: set[int] = set()
        immediate_value = 0
        for instruction_offset in offsets:
            instruction = words.get(instruction_offset)
            if instruction is None:
                continue
            # Ignore ARM condition bits. Returning payload construction may
            # select a route bit with conditional PC-relative literal loads.
            if instruction & 0x0FFF0000 == 0x059F0000:
                literal_offset = instruction_offset + 8 + (instruction & 0xFFF)
                literal = words.get(literal_offset)
                if literal is not None:
                    stage_value = wanted_high.get(literal & 0xFFFF0000)
                    if stage_value is not None:
                        matches.add(stage_value)
            if instruction & (1 << 25):
                opcode = (instruction >> 21) & 0xF
                if opcode in (0x4, 0xC):  # ADD/ORR immediate constant pieces
                    immediate_value |= arm_immediate(instruction)
                    stage_value = wanted_high.get(
                        immediate_value & 0xFFFF0000
                    )
                    if stage_value is not None:
                        matches.add(stage_value)
            # Conditional branches commonly select payload bits immediately
            # after the capture. Keep scanning both paths, but stop at the
            # first unconditional B or BL. The inline reporter's BL is the HAL
            # call boundary; scanning beyond it can incorrectly consume the
            # next adjacent reporter's stage literal.
            if (stop_on_branch and
                    instruction & 0xFE000000 == 0xEA000000):
                break
        return matches

    result: dict[str, int] = {}
    unmatched_captures: list[int] = []
    for capture in capture_offsets(words):
        # Payloads that include command, direction and block-count fields may
        # need several instructions before GCCE emits the stage-nibble ORR.
        # Ninety-two bytes still stays within the inline reporter sequence and
        # stops at an unconditional tail branch.
        matches = scan_window(
            words, range(capture + 4, capture + 96, 4), True
        )
        # A single native SDCC checkpoint can have a longer inline payload
        # construction than the generic reporters.
        if not matches and len(stage_names) == 1:
            matches = scan_window(
                words, range(capture + 4, capture + 192, 4), True
            )
        # GCCE normally constructs the stage after the location capture.  It
        # can instead hoist a dynamic stage into the branch that reaches a
        # shared reporter (EE02 and F80A are examples). Search backwards from
        # the capture in progressively wider windows and stop at the nearest
        # complete stage.  This prevents an adjacent reporter's older stage
        # from being folded into the same match set.
        if not matches:
            for backward_window in (16, 24, 32, 48):
                matches = scan_window(
                    words,
                    range(capture - backward_window, capture, 4),
                    False,
                )
                if matches:
                    break
        if not matches:
            unmatched_captures.append(capture)
            continue
        if len(matches) != 1:
            raise SystemExit(
                f"capture 0x{capture:08X} in {image} has {len(matches)} "
                "nearby checkpoint stage literals"
            )
        stage = wanted[matches.pop()]
        if stage in result:
            raise SystemExit(f"duplicate checkpoint stage in {image}: {stage}")
        result[stage] = capture
    missing_stages = set(stage_names) - set(result)
    # GCCE hoists FF04's pure ``0xff040000 | err`` construction to the entry
    # of the large ExecCommandSM state machine while leaving its address
    # capture at the EStCommandIssued return boundary.  Preserve fail-closed
    # attribution through the exact seven-capture/seven-stage bijection: this
    # fallback is accepted only for the known FF02..FF08 image and only when
    # every other capture maps uniquely, leaving one capture and one stage.
    if (unmatched_captures or missing_stages) and (
            stage_names == (
                "FF02", "FF03", "FF04", "FF05", "FF06", "FF07", "FF08"
            ) and
            len(unmatched_captures) == 1 and missing_stages == {"FF04"}):
        result["FF04"] = unmatched_captures.pop()
        missing_stages.clear()
    # In the explicit-stop image GCCE moves two stage constructions away from
    # their address captures.  F201 calls Direction() before assembling its
    # stage, so the normal forward scan stops at that helper call.  F204 keeps
    # its already-assembled stage in r8 from the function prologue.  Attribute
    # these only when every other F2 stage mapped and the two capture-site
    # instruction fingerprints are exact; do not infer them from address order.
    if (unmatched_captures or missing_stages) and (
            stage_names == (
                "F201", "F202", "F203", "F204", "F205",
                "F206", "F207", "F208", "F209", "F20A",
            ) and
            len(unmatched_captures) == 2 and
            missing_stages == {"F201", "F204"}):
        f201 = [
            capture for capture in unmatched_captures
            if words.get(capture + 4) == 0xE5997000
            and words.get(capture + 8) == 0xE5936088
        ]
        f204 = [
            capture for capture in unmatched_captures
            if words.get(capture + 4) == 0xE3A0001D
            and words.get(capture + 8) == 0xE1A03008
            and words.get(capture + 12) == 0xE3A01002
            and words.get(capture + 16, 0) & 0x0F000000 == 0x0B000000
        ]
        if len(f201) == 1 and len(f204) == 1 and f201[0] != f204[0]:
            result["F201"] = f201[0]
            result["F204"] = f204[0]
            unmatched_captures.clear()
            missing_stages.clear()
    # GCCE hoists F113's two conditional stage literals (F1130000 and
    # F1138000) into callee-saved registers at RequestFreeClusters() entry.
    # The capture remains beside the current-free-count payload. Attribute
    # this one stage only when the other nine map normally and the unmatched
    # site has the exact select-and-merge instruction fingerprint; this keeps
    # the map fail-closed without depending on a link-time address.
    if (unmatched_captures or missing_stages) and (
            stage_names == (
                "F111", "F112", "F113", "F114", "F115",
                "F116", "F117", "F118", "F119", "F11A",
            ) and
            len(unmatched_captures) == 1 and
            missing_stages == {"F113"}):
        f113 = [
            capture for capture in unmatched_captures
            if words.get(capture + 4) == 0xE1A0E880
            and words.get(capture + 8) == 0xE3500000
            and words.get(capture + 12) == 0x11A00007
            and words.get(capture + 16) == 0x01A00008
            and words.get(capture + 20) == 0xE1A038AE
            and words.get(capture + 24) == 0xE1803003
            and words.get(capture + 28) == 0xE3A0001D
        ]
        if len(f113) == 1:
            result["F113"] = f113[0]
            unmatched_captures.clear()
            missing_stages.clear()
    if unmatched_captures:
        captures = ", ".join(
            f"0x{capture:08X}" for capture in unmatched_captures
        )
        raise SystemExit(
            f"captures in {image} have no nearby checkpoint stage literal: "
            f"{captures}; missing stages: {', '.join(sorted(missing_stages))}"
        )
    if missing_stages or set(result) != set(stage_names):
        raise SystemExit(f"incomplete checkpoint mapping in {image}")
    return result


def parse_rombuild(log: pathlib.Path) -> dict[str, dict[str, int]]:
    text = log.read_bytes().decode("latin-1", errors="replace").replace("\x00", "")
    records: dict[str, dict[str, int]] = {}
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("Processing file "):
            current = line[len("Processing file ") :].strip()
            records.setdefault(current, {})
            continue
        if current is None:
            continue
        if line.startswith("Entry point:"):
            records[current]["entry"] = int(line.split(":", 1)[1].strip(), 16)
        elif line.startswith("Code start addr:"):
            records[current]["code_start"] = int(line.split(":", 1)[1].strip(), 16)
    return records


def parse_extensions(recipe: pathlib.Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for raw_line in recipe.read_text(encoding="utf-8").splitlines():
        match = EXTENSION.match(raw_line.strip())
        if match:
            entries.append((match.group(1).strip(), match.group(2)))
    if not entries:
        raise SystemExit("no active extension entries found in final OBY")
    return entries


def main() -> None:
    if len(sys.argv) != 12:
        raise SystemExit(
            "usage: create-htcleo-probe-map.py ELF2E32 ESTART_E32 "
            "EFILE_E32 ELOCD_E32 MEDMMC_E32 EFAT32_E32 EPBUSSD_E32 "
            "HTCLEO_SDCC_E32 ROMBUILD_LOG FINAL_OBY OUTPUT"
        )
    (elf2e32, estart, efile, elocd, medmmc, efat32, epbussd, sdcc,
     log, recipe, output) = map(
        pathlib.Path, sys.argv[1:]
    )
    for path in (elf2e32, estart, efile, elocd, medmmc, efat32,
                 epbussd, sdcc, log, recipe):
        if not path.is_file():
            raise SystemExit(f"missing probe-map input: {path}")

    udf_offset, previous, estart_offsets = parse_estart_udf(elf2e32, estart)
    if len(estart_offsets) != 0:
        raise SystemExit(
            "expected no returning-location captures in ESTART, found "
            f"{len(estart_offsets)}"
        )
    efile_offsets = parse_checkpoint_image(elf2e32, efile, 0)
    elocd_offsets = parse_checkpoint_image(elf2e32, elocd, 0)
    medmmc_offsets = parse_checkpoint_image(elf2e32, medmmc, 0)
    efat32_offsets = parse_checkpoint_image(elf2e32, efat32, 10)
    epbussd_offsets = parse_checkpoint_image(elf2e32, epbussd, 0)
    sdcc_offsets = parse_checkpoint_image(elf2e32, sdcc, 0)
    stage_names = (
        "F131", "F132", "F133", "F134", "F135",
        "F136", "F137", "F138", "F139", "F13A",
    )
    efat32_stages = map_checkpoint_stages(
        elf2e32, efat32, 0xF1300000,
        stage_names,
    )
    records = parse_rombuild(log)
    estart_record = records.get(str(estart))
    if not estart_record or "code_start" not in estart_record:
        raise SystemExit(f"ESTART code start is absent from ROMBUILD log: {estart}")
    efile_record = records.get(str(efile))
    if not efile_record or "code_start" not in efile_record:
        raise SystemExit(f"EFILE code start is absent from ROMBUILD log: {efile}")
    estart_code_start = estart_record["code_start"]
    efile_code_start = efile_record["code_start"]
    elocd_record = records.get(str(elocd))
    if not elocd_record or "code_start" not in elocd_record:
        raise SystemExit(f"ELOCD code start is absent from ROMBUILD log: {elocd}")
    medmmc_record = records.get(str(medmmc))
    if not medmmc_record or "code_start" not in medmmc_record:
        raise SystemExit(f"MEDMMC code start is absent from ROMBUILD log: {medmmc}")
    elocd_code_start = elocd_record["code_start"]
    medmmc_code_start = medmmc_record["code_start"]
    efat32_record = records.get(str(efat32))
    if not efat32_record or "code_start" not in efat32_record:
        raise SystemExit(f"EFAT32 code start is absent from ROMBUILD log: {efat32}")
    efat32_code_start = efat32_record["code_start"]
    epbussd_record = records.get(str(epbussd))
    if not epbussd_record or "code_start" not in epbussd_record:
        raise SystemExit(f"EPBUSSD code start is absent from ROMBUILD log: {epbussd}")
    sdcc_record = records.get(str(sdcc))
    if not sdcc_record or "code_start" not in sdcc_record:
        raise SystemExit(f"HTCLEO SDCC code start is absent from ROMBUILD log: {sdcc}")
    epbussd_code_start = epbussd_record["code_start"]
    sdcc_code_start = sdcc_record["code_start"]
    runtime_udf = estart_code_start + udf_offset
    if not 0x12200000 <= runtime_udf < 0x15800000:
        raise SystemExit(f"ESTART UDF is outside the full-ROM window: {runtime_udf:08X}")
    progress_runtime = sorted(
        [estart_code_start + offset for offset in estart_offsets]
        + [efile_code_start + offset for offset in efile_offsets]
        + [elocd_code_start + offset for offset in elocd_offsets]
        + [medmmc_code_start + offset for offset in medmmc_offsets]
        + [efat32_code_start + offset for offset in efat32_offsets]
        + [epbussd_code_start + offset for offset in epbussd_offsets]
        + [sdcc_code_start + offset for offset in sdcc_offsets]
    )
    stage_runtime = {}
    for code_start, stages in (
        (efat32_code_start, efat32_stages),
    ):
        stage_runtime.update(
            {stage: code_start + offset for stage, offset in stages.items()}
        )
    if set(stage_runtime.values()) != set(progress_runtime):
        raise SystemExit("checkpoint stage/address pairing differs from address set")
    if len(set(progress_runtime)) != 10 or any(
        not 0x12200000 <= address < 0x15800000
        for address in progress_runtime
    ):
        raise SystemExit("EFAT32 BOOTLOG write checkpoint address set is invalid")
    if runtime_udf in progress_runtime:
        raise SystemExit("final ESTART UDF overlaps a returning checkpoint")

    mapped_extensions: list[tuple[int, str, str]] = []
    for source, destination in parse_extensions(recipe):
        record = records.get(source)
        if not record or "entry" not in record:
            raise SystemExit(f"extension entry point absent from ROMBUILD log: {source}")
        mapped_extensions.append((record["entry"], destination, source))
    entries = [entry for entry, _, _ in mapped_extensions]
    if len(entries) != len(set(entries)):
        raise SystemExit("duplicate runtime extension entry points in probe map")

    lines = [
        "STATUS=HTCLEO_RUNTIME_PROBE_MAP_OK",
        f"ESTART_IMAGE={estart}",
        f"ESTART_IMAGE_SHA256={sha256(estart)}",
        f"ESTART_CODE_START=0x{estart_code_start:08X}",
        f"ESTART_UDF_CODE_OFFSET=0x{udf_offset:08X}",
        f"ESTART_UDF_PREVIOUS_WORD=0x{previous:08X}",
        f"ESTART_UDF_RUNTIME_ADDRESS=0x{runtime_udf:08X}",
        "ESTART_RETURNING_CHECKPOINT_COUNT=0",
        f"EFILE_IMAGE={efile}",
        f"EFILE_IMAGE_SHA256={sha256(efile)}",
        f"EFILE_CODE_START=0x{efile_code_start:08X}",
        "EFILE_RETURNING_CHECKPOINT_COUNT=0",
        f"ELOCD_IMAGE={elocd}",
        f"ELOCD_IMAGE_SHA256={sha256(elocd)}",
        f"ELOCD_CODE_START=0x{elocd_code_start:08X}",
        "ELOCD_RETURNING_CHECKPOINT_COUNT=0",
        f"MEDMMC_IMAGE={medmmc}",
        f"MEDMMC_IMAGE_SHA256={sha256(medmmc)}",
        f"MEDMMC_CODE_START=0x{medmmc_code_start:08X}",
        "MEDMMC_RETURNING_CHECKPOINT_COUNT=0",
        f"EFAT32_IMAGE={efat32}",
        f"EFAT32_IMAGE_SHA256={sha256(efat32)}",
        f"EFAT32_CODE_START=0x{efat32_code_start:08X}",
        "EFAT32_RETURNING_CHECKPOINT_COUNT=10",
        f"EPBUSSD_IMAGE={epbussd}",
        f"EPBUSSD_IMAGE_SHA256={sha256(epbussd)}",
        f"EPBUSSD_CODE_START=0x{epbussd_code_start:08X}",
        "EPBUSSD_RETURNING_CHECKPOINT_COUNT=0",
        f"HTCLEO_SDCC_IMAGE={sdcc}",
        f"HTCLEO_SDCC_IMAGE_SHA256={sha256(sdcc)}",
        f"HTCLEO_SDCC_CODE_START=0x{sdcc_code_start:08X}",
        "HTCLEO_SDCC_RETURNING_CHECKPOINT_COUNT=0",
        "RETURNING_CHECKPOINT_COUNT=10",
        "RETURNING_CHECKPOINT_SCOPE=efat32-drive-c-stock-synchronous-free-space-scan-through-exact-bootlog-allocation",
        "RETURNING_CHECKPOINT_RUNTIME_ADDRESSES="
        + ",".join(f"0x{address:08X}" for address in progress_runtime),
        "RETURNING_CHECKPOINT_ADDRESS_ORDER=sorted-runtime-set-not-stage-order",
        *(
            f"CHECKPOINT_{stage}_RUNTIME_ADDRESS=0x{stage_runtime[stage]:08X}"
            for stage in stage_names
        ),
        "CHECKPOINT_01=F1310000|DriveC FAT32 async policy read; bit15 async-enabled low8 drive number",
        "CHECKPOINT_02=F1320000|32KiB synchronous FAT scan buffer allocated; low16 sectors per buffer",
        "CHECKPOINT_03=F1330000|scan start time returned; low16 total FAT sectors",
        "CHECKPOINT_04=F1340000|first synchronous raw FAT read returned; low16 result",
        "CHECKPOINT_05=F1350000|first FAT chunk parse returned; bit15 first-free-found low15 chunk free count",
        "CHECKPOINT_06=F1360000|second synchronous raw FAT read returned; low16 result",
        "CHECKPOINT_07=F1370000|whole FAT loop and end-time call returned; high nibble prior phase low12 chunks",
        "CHECKPOINT_08=F1380000|free count and hint published and buffer destroyed; bit15 any-free low15 first-free",
        "CHECKPOINT_09=F1390000|synchronous count returned and FAT state mounted; low16 count result",
        "CHECKPOINT_0A=F13A0000|exact BOOTLOG RequestFreeClusters returned; bit15 enough bit14 no-helper low13 request",
        "ESTART_FINAL_UDF=C BOOTLOG Write Flush Close passed",
        "RETURNING_DISPLAY_TOP=actual runtime checkpoint instruction address",
        "RETURNING_DISPLAY_BOTTOM=F131 through F13A synchronous FAT scan/allocation stage",
        "DISPLAY_TOP=actual runtime extension entry point",
        "DISPLAY_BOTTOM=A00000nn VariantInit0/data pass",
        "DISPLAY_BOTTOM=B00000nn ExtensionInit0 pass",
        "DISPLAY_BOTTOM=C00000nn ExtensionInit1 pass",
        f"ACTIVE_EXTENSION_COUNT={len(mapped_extensions)}",
        "",
        "RUNTIME_ENTRY\tROM_DESTINATION\tSOURCE_BINARY",
    ]
    lines.extend(
        f"0x{entry:08X}\t{destination}\t{source}"
        for entry, destination, source in mapped_extensions
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"HTCLEO_PROBE_MAP={output}")


if __name__ == "__main__":
    main()
