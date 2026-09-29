#!/usr/bin/env python3
"""Use stock AppArc firmware-version invalidation for changed ROM registrations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
BASE = runpy.run_path(str(HERE / 'prepare-htcleo-gate17-entry.py'))
VERIFY = runpy.run_path(str(HERE / 'verify-htcleo-gate17-entry.py'))
PARENT = '778-symbian3-full-english-font-settings-entry-incremental'
PARENT_SHA = '52134621bdc38bc77e958e99322513fe23a05affc0fe73310eff86735569475f'
TARGET = r'resource\versions\sw.txt'
CHANGED = '/root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe'


def catalog_version(recipe):
    files = BASE['entries'](recipe)
    registered = sorted((name, BASE['sha'](source)) for name, (source, _) in files.items()
                        if re.fullmatch(r'private\\10003a3f\\(?:import\\)?apps\\[^\\]+\.rsc', name))
    if not registered or not any(name.endswith(r'\gsapp_reg.rsc') for name, _ in registered):
        raise ValueError('ROM application registration set/GSApp missing')
    fingerprint = hashlib.sha256(json.dumps(registered).encode()).hexdigest()
    # A content-derived product identity, not a probe or iteration number.
    value = 'V HTCLEO REG-' + fingerprint[:12] + r'\nPDK3.0.4\nS60-52\n(c)NMP'
    if len(value) > 64:
        raise ValueError('software version exceeds reviewed SysUtil text budget')
    return b'\xff\xfe' + value.encode('utf-16le'), fingerprint, len(registered)


def expected_recipe(parent_recipe, output_path):
    original = BASE['entries'](parent_recipe)[TARGET][1]
    new = 'data=' + str(output_path) + ' \t"' + TARGET + '"'
    if parent_recipe.splitlines().count(original) != 1:
        raise ValueError('software-version mapping changed')
    return parent_recipe.replace(original, new, 1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--version-file', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--image', type=Path)
    p.add_argument('--rom-log', type=Path)
    a = p.parse_args()
    old_rom = (a.parent / 'initrd.gz').read_bytes()
    if hashlib.sha256(old_rom).hexdigest() != PARENT_SHA:
        raise ValueError('not immutable778')
    original = (a.parent / 'build/htcleo_symbian3_full_native.oby').read_text()
    version, fingerprint, count = catalog_version(original)
    expected = expected_recipe(original, a.version_file)
    if a.apply:
        if a.recipe.read_text() != original:
            raise ValueError('pre-overlay recipe differs from778')
        if not str(a.version_file.resolve()).startswith('/root/symbian3-full-work/htcleo-native/'):
            raise ValueError('version output outside mutable build directory')
        a.version_file.write_bytes(version)
        a.recipe.write_text(expected)
    if a.recipe.read_text() != expected or a.version_file.read_bytes() != version:
        raise ValueError('unreviewed recipe/version delta')
    parent_cache = a.parent / 'build/incremental-release-cache'
    lines = (parent_cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines) != 61:
        raise ValueError('expected61 parent inputs')
    changed = []
    for line in lines:
        digest, source, name = line.split('\t')
        if BASE['sha'](parent_cache / name) != digest:
            raise ValueError('parent cache corrupted')
        if BASE['sha'](Path(source)) != digest:
            changed.append(source)
    if changed != [CHANGED]:
        raise ValueError('expected only observer ailaunch change: ' + repr(changed))
    report = dict(status='HTCLEO_ROM_REGISTRATION_VERSION_OK', parent=PARENT,
                  parent_sha256=PARENT_SHA, fingerprint=fingerprint, registrations=count,
                  software_version=version[2:].decode('utf-16le'),
                  version_sha256=hashlib.sha256(version).hexdigest(),
                  changed_binary=CHANGED, changed_binary_sha256=BASE['sha'](Path(CHANGED)),
                  unchanged_parent_binaries=60,
                  cache_policy='stock-SysUtil-version-mismatch-rebuild-no-host-cache-deletion',
                  observer='two-delayed-readonly-offscreen-samples-no-ui-or-focus-change',
                  hardware_result='pending', stage='recipe-only')
    if a.image or a.rom_log:
        if not (a.image and a.rom_log):
            raise ValueError('image/log required together')
        new_rom = a.image.read_bytes()
        old_log = (a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace')
        new_log = a.rom_log.read_text(errors='replace')
        old_files = VERIFY['rom_files'](old_rom, old_log)
        new_files = VERIFY['rom_files'](new_rom, new_log)
        if set(old_files) != set(new_files):
            raise ValueError('ROM file membership changed')
        preserved = 0
        for name in old_files:
            if name.startswith('sys\\bin\\'):
                continue
            data = VERIFY['file_data'](new_rom, new_files, name)
            expected_data = version if name == TARGET else VERIFY['file_data'](old_rom, old_files, name)
            if data != expected_data:
                raise ValueError('resource changed outside version: ' + name)
            preserved += int(name != TARGET)
        window = (len(new_rom) + 1048575) // 1048576 * 1048576
        if window != 0x03a00000:
            raise ValueError('ROM/RAM boundary changed')
        report.update(stage='rom-bytes', preserved_resources=preserved,
                      rom_window=window, ram_start=0x12200000 + window,
                      payload_sha256=hashlib.sha256(new_rom).hexdigest())
    a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('HTCLEO_ROM_REGISTRATION_VERSION_PASS ' + json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
