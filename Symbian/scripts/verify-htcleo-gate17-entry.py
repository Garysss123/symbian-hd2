#!/usr/bin/env python3
"""778: exact 777 overlay, real ROM font alias, SPI and offline/Java preservation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct

HERE = Path(__file__).resolve().parent
HELPER = runpy.run_path(str(HERE / 'prepare-htcleo-gate17-entry.py'))
NETWORK = runpy.run_path(str(HERE / 'verify-htcleo-offline-network-bypass.py'))
SPI = runpy.run_path(str(HERE / 'audit-htcleo-homescreen-ecom-spi.py'))
ROM_BASE = 0x12200000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def rom_files(raw, log):
    """TRomDir/TRomEntry, e32rom.h; use this ROM's root from its link log."""
    roots = re.findall(r'^Directory\s+0\s+0c0b0001\s+([0-9a-f]+)\s*$', log, re.M | re.I)
    if len(roots) != 1:
        raise ValueError('expected one HTCLEO variant root')
    result, seen = {}, set()

    def walk(address, prefix, depth):
        offset = address - ROM_BASE
        if depth > 32 or offset in seen or not 0 <= offset < len(raw) - 4:
            raise ValueError('bad/recursive ROM directory')
        seen.add(offset)
        size = struct.unpack_from('<I', raw, offset)[0]
        pos, end = offset + 4, offset + 4 + size
        if end > len(raw):
            raise ValueError('directory extends beyond ROM')
        while pos < end:
            if pos + 10 > end or len(result) > 30000:
                raise ValueError('invalid directory entry count/length')
            length, addr, attr, chars = struct.unpack_from('<IIBB', raw, pos)
            name_end = pos + 10 + chars * 2
            if chars == 0 or name_end > end:
                raise ValueError('invalid ROM name length')
            name = raw[pos + 10:name_end].decode('utf-16le').lower()
            if '\\' in name or '/' in name or '\x00' in name:
                raise ValueError('invalid ROM name')
            target = prefix + name
            if attr & 0x10:
                walk(addr, target + '\\', depth + 1)
            else:
                start = addr - ROM_BASE
                # rombuild represents empty data files with a null address.
                if length == 0 and addr == 0:
                    start = 0
                if target in result or start < 0 or start + length > len(raw):
                    raise ValueError(f'invalid/duplicate ROM file: {target} start={start:#x} '
                                     f'length={length} duplicate={target in result}')
                result[target] = (start, length)
            pos = (name_end + 3) & ~3
        if pos != end:
            raise ValueError('ROM directory did not end at its declared size')
    walk(int(roots[0], 16), '', 0)
    return result


def file_data(raw, mapping, name):
    start, size = mapping[name]
    return raw[start:start + size]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--image', type=Path)
    p.add_argument('--rom-log', type=Path)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    cfg = json.loads(HELPER['CONFIG'].read_text())
    plan = HELPER['create_plan'](a.sdk, a.parent, cfg)
    if json.loads(a.plan.read_text()) != plan:
        raise ValueError('Gate17 pinned input plan changed')
    before = (a.parent / 'build/htcleo_symbian3_full_native.oby').read_text()
    expected = HELPER['render_recipe'](before, plan)
    if a.recipe.read_text() != expected:
        raise ValueError('recipe changed outside the reviewed Gate17 overlay')
    old_cache = a.parent / 'build/incremental-release-cache'
    lines = (old_cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines) != 54:
        raise ValueError('unexpected parent cache')
    for line in lines:
        digest, source, filename = line.split('\t')
        if sha(Path(source).read_bytes()) != digest or sha((old_cache / filename).read_bytes()) != digest:
            raise ValueError('existing 777 binary changed: ' + filename)
    report = dict(status='HTCLEO_GATE17_ENTRY_OK', stage='recipe-only',
                  parent=plan['parent_package'], parent_sha256=plan['parent_sha256'],
                  existing_54_binaries_byte_identical=True,
                  added_binaries=[r['destination'] for r in plan['binaries']],
                  added_assets=[r['destination'] for r in plan['assets']],
                  optional_adapter=plan['optional_adapter'], hardware_result='pending',
                  java_runtime_verified=False)
    if a.image or a.rom_log:
        if not a.image or not a.rom_log:
            raise ValueError('need image and rom-log together')
        old = (a.parent / 'initrd.gz').read_bytes()
        current = a.image.read_bytes()
        log0 = (a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace')
        log1 = a.rom_log.read_text(errors='replace')
        files0, files1 = rom_files(old, log0), rom_files(current, log1)
        previous = NETWORK['resources'](log0, old)
        retained = NETWORK['resources'](log1, current)
        if previous != retained:
            raise ValueError('777 offline CMI/ESK set or bytes changed')
        NETWORK['check_closed_graph'](retained)
        spi_name = 'private\\10009d8f\\ecom-0-0.spi'
        resources = 0
        java_resources = 0
        # Preserve every existing non-executable logical file, including font
        # names and Java ODC/policies. Only SPI may gain an append-only suffix.
        for name in files0:
            if name.startswith('sys\\bin\\'):
                continue
            original = file_data(old, files0, name)
            actual = file_data(current, files1, name)
            if name == spi_name:
                if not actual.startswith(original):
                    raise ValueError('777 ECom SPI byte prefix changed')
            elif actual != original:
                raise ValueError('existing resource content changed: ' + name)
            resources += 1
            java_resources += int('java' in name or name.endswith('.odc'))
        for item in plan['assets']:
            if sha(file_data(current, files1, item['destination'])) != item['sha256']:
                raise ValueError('new ROM asset mismatch: ' + item['destination'])
        for item in plan['font_aliases']:
            if files1[item['source']] != files1[item['alias']]:
                raise ValueError('font alias does not share the original ROM data')
        for item in plan['binaries']:
            if item['destination'] not in files1:
                raise ValueError('new executable missing in ROM: ' + item['destination'])
        new_spi = HELPER['entries'](a.recipe.read_text())[spi_name][0]
        _, spi_entries = SPI['parse_spi'](new_spi)
        if len(spi_entries) != 141:
            raise ValueError('expected exactly 141 ECom entries')
        if [e.name for e in spi_entries[-3:]] != [Path(n).stem for n in plan['ecom_resources']]:
            raise ValueError('wrong Gate17 ECom extension order')
        for entry, name in zip(spi_entries[-3:], plan['ecom_resources']):
            if entry.data != (a.sdk / 'epoc32/data/z/resource/plugins' / name).read_bytes():
                raise ValueError('wrong Gate17 registration payload')
        if file_data(current, files1, spi_name) != new_spi.read_bytes():
            raise ValueError('actual ROM SPI differs from validated archive')
        window = (len(current) + 1048575) // 1048576 * 1048576
        if window != 0x03a00000 or ROM_BASE + window != 0x15c00000:
            raise ValueError('Gate17 must not change the 777 ROM/RAM boundary')
        report.update(stage='rom-bytes', image_sha256=sha(current),
                      rom_window=window, ram_start=ROM_BASE + window,
                      retained_cmi_esk_count=len(retained), preserved_resources=resources,
                      preserved_java_resources=java_resources, spi_entries=141,
                      font_alias_shared_address=True)
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('HTCLEO_GATE17_ENTRY_PASS ' + json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
