#!/usr/bin/env python3
"""781 recovery guard: exact778 recipe/resources, one client DLL may change."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROM = runpy.run_path(str(HERE / 'verify-htcleo-gate17-entry.py'))
PARENT_SHA = '52134621bdc38bc77e958e99322513fe23a05affc0fe73310eff86735569475f'
CHANGED = '/root/symbian3-full/epoc32/release/armv5/urel/akncapserverclient.dll'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    for name in ('parent', 'recipe', 'image', 'rom-log', 'report'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    if sha(a.parent / 'initrd.gz') != PARENT_SHA:
        raise ValueError('not immutable778')
    if a.recipe.read_text() != (a.parent / 'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('recipe drift from778')
    cache = a.parent / 'build/incremental-release-cache'
    lines = (cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines) != 61:
        raise ValueError('expected61 parent binaries')
    changed = []
    for line in lines:
        digest, source, name = line.split('\t')
        if sha(cache / name) != digest:
            raise ValueError('immutable cache corrupted: ' + name)
        if sha(Path(source)) != digest:
            changed.append(source)
    if changed != [CHANGED]:
        raise ValueError('unexpected binary deltas: ' + repr(changed))
    old, new = (a.parent / 'initrd.gz').read_bytes(), a.image.read_bytes()
    files0 = ROM['rom_files'](old, (a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace'))
    files1 = ROM['rom_files'](new, a.rom_log.read_text(errors='replace'))
    if set(files0) != set(files1):
        raise ValueError('ROM membership changed')
    count = 0
    for name in files0:
        if name.startswith('sys\\bin\\'):
            continue
        if ROM['file_data'](old, files0, name) != ROM['file_data'](new, files1, name):
            raise ValueError('resource bytes changed: ' + name)
        count += 1
    window = (len(new) + 1048575) // 1048576 * 1048576
    if window != 0x03a00000:
        raise ValueError('ROM/RAM boundary changed')
    result = dict(status='HTCLEO_PACKED_LAYOUT_TRACE_OK', parent_sha256=PARENT_SHA,
                  changed_binary=CHANGED, changed_sha256=sha(Path(CHANGED)),
                  unchanged_binaries=60, preserved_resources=count,
                  rom_window=window, ram_start=0x12200000 + window,
                  payload_sha256=sha(a.image), font_changes=False,
                  settings_worker='retired-exact778-ailaunch', software_version='exact778',
                  hardware_result='pending')
    a.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
