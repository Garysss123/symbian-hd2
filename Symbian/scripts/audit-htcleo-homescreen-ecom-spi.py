#!/usr/bin/env python3
"""Fail-closed audit for the HTCLEO HomeScreen ECom SPI extension."""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import struct
from dataclasses import dataclass


SPI_UID1 = 0x10205C2B
ECOM_SPI_UID2 = 0x10205C2C
ECOM_RSC_UID1 = 0x101F4A6B
ECOM_RSC_UID2 = 0x101F747D


@dataclass(frozen=True)
class Entry:
    name: str
    data: bytes


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_spi(path: pathlib.Path) -> tuple[bytes, list[Entry]]:
    raw = path.read_bytes()
    if len(raw) < 32:
        raise SystemExit(f"SPI is shorter than its header: {path}")
    uid1, uid2, uid3 = struct.unpack_from("<III", raw, 0)
    if (uid1, uid2, uid3) != (SPI_UID1, ECOM_SPI_UID2, 0):
        raise SystemExit(
            f"unexpected SPI UID tuple: {uid1:08x},{uid2:08x},{uid3:08x}"
        )
    if raw[16:32] != bytes(16):
        raise SystemExit(f"nonzero reserved SPI header bytes: {path}")

    entries: list[Entry] = []
    offset = 32
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise SystemExit(f"truncated SPI entry header at {offset}: {path}")
        name_len, data_len = struct.unpack_from("<II", raw, offset)
        if not name_len:
            raise SystemExit(f"zero-length SPI entry name at {offset}: {path}")
        payload_end = offset + 8 + name_len + data_len
        padded_end = payload_end + ((4 - ((name_len + data_len) % 4)) % 4)
        if padded_end > len(raw):
            raise SystemExit(f"truncated SPI entry at {offset}: {path}")
        try:
            name = raw[offset + 8:offset + 8 + name_len].decode("ascii")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"non-ASCII SPI entry name at {offset}: {path}") from exc
        data = raw[offset + 8 + name_len:payload_end]
        if any(raw[payload_end:padded_end]):
            raise SystemExit(f"nonzero SPI padding at {offset}: {path}")
        entries.append(Entry(name.lower(), data))
        offset = padded_end
    if offset != len(raw):
        raise SystemExit(f"SPI parser did not end at EOF: {path}")
    names = [entry.name for entry in entries]
    if len(names) != len(set(names)):
        raise SystemExit(f"duplicate SPI entry basename: {path}")
    return raw, entries


def load_manifest(path: pathlib.Path, expected: int = 30) -> list[str]:
    names = [
        line.strip().lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(names) != expected or len(names) != len(set(names)):
        raise SystemExit(
            f"expected exactly {expected} unique SPI resources, got {len(names)}"
        )
    for name in names:
        if pathlib.PurePath(name).name != name or not name.endswith(".rsc"):
            raise SystemExit(f"invalid resource manifest basename: {name}")
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_spi", type=pathlib.Path)
    parser.add_argument("extended_spi", type=pathlib.Path)
    parser.add_argument("resource_dir", type=pathlib.Path)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("report", type=pathlib.Path)
    parser.add_argument("--expected-additions", type=int, choices=(30, 33, 35), default=30)
    args = parser.parse_args()

    wanted = load_manifest(args.manifest, args.expected_additions)
    if args.expected_additions == 35:
        previous = load_manifest(pathlib.Path(__file__).resolve().parents[1] /
                                 'config/htcleo-gate17-ecom-spi-resources.txt', 33)
        if wanted != previous + ['gsdevicemanagementplugin.rsc', 'aboutgsplugin.rsc']:
            raise SystemExit('841 must preserve the33 registrations and add only the two About-chain entries')
    base_raw, base_entries = parse_spi(args.base_spi)
    extended_raw, extended_entries = parse_spi(args.extended_spi)
    if len(base_entries) != 108:
        raise SystemExit(f"stock SPI entry count changed: {len(base_entries)}")
    base_names = {entry.name for entry in base_entries}
    wanted_stems = [pathlib.PurePath(name).stem for name in wanted]
    collisions = sorted(base_names.intersection(wanted_stems))
    if collisions:
        raise SystemExit("manifest entries already in stock SPI: " + ",".join(collisions))
    if extended_raw[:len(base_raw)] != base_raw:
        raise SystemExit("extended SPI did not preserve the stock SPI byte prefix")
    if extended_entries[:len(base_entries)] != base_entries:
        raise SystemExit("extended SPI changed a stock entry")
    appended = extended_entries[len(base_entries):]
    if [entry.name for entry in appended] != wanted_stems:
        raise SystemExit("extended SPI appended entry order/content mismatch")

    resource_hashes: list[tuple[str, str]] = []
    for manifest_name, entry in zip(wanted, appended, strict=True):
        source = args.resource_dir / manifest_name
        if not source.is_file():
            raise SystemExit(f"missing HomeScreen ECom resource: {source}")
        source_data = source.read_bytes()
        if len(source_data) < 12:
            raise SystemExit(f"short HomeScreen ECom resource: {source}")
        uid1, uid2 = struct.unpack_from("<II", source_data, 0)
        if (uid1, uid2) != (ECOM_RSC_UID1, ECOM_RSC_UID2):
            raise SystemExit(
                f"not an ECom registration resource: {source} "
                f"uids={uid1:08x},{uid2:08x}"
            )
        if entry.data != source_data:
            raise SystemExit(f"SPI payload differs from source resource: {source}")
        resource_hashes.append((manifest_name, digest(source_data)))

    report_lines = [
        "STATUS=HTCLEO_HOMESCREEN_ECOM_SPI_OK",
        f"BASE_SPI={args.base_spi}",
        f"BASE_SHA256={digest(base_raw)}",
        f"BASE_ENTRIES={len(base_entries)}",
        f"EXTENDED_SPI={args.extended_spi}",
        f"EXTENDED_SHA256={digest(extended_raw)}",
        f"EXTENDED_ENTRIES={len(extended_entries)}",
        f"APPENDED_ENTRIES={len(appended)}",
        "STOCK_ENTRIES_BYTE_IDENTICAL=1",
        "APPENDED_PAYLOADS_BYTE_IDENTICAL=1",
    ]
    report_lines.extend(
        f"APPENDED_{index:02d}={name}:{sha256}"
        for index, (name, sha256) in enumerate(resource_hashes, 1)
    )
    args.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(
        "HTCLEO_HOMESCREEN_ECOM_SPI_OK "
        f"base={len(base_entries)} appended={len(appended)} "
        f"total={len(extended_entries)}"
    )


if __name__ == "__main__":
    main()
