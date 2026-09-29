#!/usr/bin/env python3
"""776: exact two-resource recipe delta and retained CMI/ESK ROM-byte check."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

PARENT_SHA = '5fec3636d88c4156cf7abf03cd3381e6daf6bad9c2f9d9db08315919413f0884'
DISABLED = {
    r'private\101f7988\esock_bt.cmi',
    r'private\101f7989\esock\bt.bt_v2.esk',
}
SOURCE_TAILS = ('/private/101f7988/esock_bt.cmi',
                '/private/101f7989/esock/bt.bt_v2.esk')
MARKER = 'REM HTCLEO disabled optional Bluetooth startup/protocol: '


def destination(line: str):
    names = re.findall(r'"([^"\r\n]+)"', line)
    return names[-1].replace('/', '\\').lower() if names else None


def recipe_delta(before: str, after: str):
    old = before.replace('\r', '').splitlines()
    new = after.replace('\r', '').splitlines()
    expected, removed = [], set()
    for line in old:
        dest = destination(line)
        if not line.lstrip().upper().startswith('REM') and dest in DISABLED:
            if dest in removed:
                raise ValueError('duplicate disabled resource')
            removed.add(dest)
            expected.append(MARKER + line)
        else:
            expected.append(line)
    if removed != DISABLED or new != expected:
        raise ValueError('recipe differs beyond the exact two Bluetooth resources')
    return sorted(removed)


def resources(log: str, rom: bytes):
    sizes = {name: int(size) for name, size in
             re.findall(r'(?m)^([^\r\n]+\.(?:cmi|esk))\t(\d+)\r?$', log, re.I)}
    records = {}
    for name, addr in re.findall(
            r'(?m)^Reading resource (.+\.(?:cmi|esk)) to rom linear address ([0-9a-f]+)\r?$',
            log, re.I):
        if name not in sizes:
            raise ValueError('missing resource length: ' + name)
        start, size = int(addr, 16) - 0x12200000, sizes[name]
        if name in records or start < 0 or start + size > len(rom):
            raise ValueError('invalid/duplicate ROM resource: ' + name)
        records[name] = rom[start:start+size]
    if not records:
        raise ValueError('no CMI/ESK resources found')
    return records


def is_disabled(name: str):
    return name.lower().endswith(SOURCE_TAILS)


def check_bindings(records):
    for name, data in records.items():
        if name.lower().endswith('.cmi') and not is_disabled(name):
            text = data.decode('latin-1')
            if re.search(r'^\s*Binding\d+\s*=.*\bESock_Bt\s*:', text, re.I | re.M):
                raise ValueError('retained CMI has a reverse Bluetooth binding: ' + name)


def self_test():
    old = '\n'.join(['data=/a "' + d + '"' for d in sorted(DISABLED)] +
                    ['file=/b "sys\\bin\\esocksvr.dll"'])
    new = '\n'.join(MARKER + line if destination(line) in DISABLED else line
                    for line in old.splitlines())
    assert len(recipe_delta(old, new)) == 2
    for bad in (old, new + '\nfile=/c "sys\\bin\\other.dll"'):
        try:
            recipe_delta(old, bad)
        except ValueError:
            pass
        else:
            raise AssertionError('bad recipe accepted')
    try:
        check_bindings({'/other.cmi': b'Binding0=ESock_Main:0,ESock_Bt:2,ECustom,20,20'})
    except ValueError:
        pass
    else:
        raise AssertionError('reverse dependency accepted')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent', type=Path, required=True, help='immutable775 Symbian3 dir')
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--image', type=Path)
    p.add_argument('--rom-log', type=Path)
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    self_test()
    before = (a.parent / 'initrd.gz').read_bytes()
    if hashlib.sha256(before).hexdigest() != PARENT_SHA:
        raise ValueError('not the pinned775 ROM')
    removed = recipe_delta(
        (a.parent / 'build/htcleo_symbian3_full_native.oby').read_text(),
        a.recipe.read_text())
    old_resources = resources((a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace'), before)
    disabled_sources = {name for name in old_resources if is_disabled(name)}
    if len(disabled_sources) != 2:
        raise ValueError('parent Bluetooth resource membership changed')
    check_bindings(old_resources)
    report = {'parent_sha256': PARENT_SHA, 'removed_destinations': removed,
              'reverse_bindings': 0, 'binary_policy': 'all54-parent-binaries-unchanged',
              'stage': 'recipe-only', 'hardware_result': 'pending'}
    if a.image or a.rom_log:
        if not (a.image and a.rom_log):
            raise ValueError('image and rom-log must be supplied together')
        image = a.image.read_bytes()
        current = resources(a.rom_log.read_text(errors='replace'), image)
        retained = {k: v for k, v in old_resources.items() if not is_disabled(k)}
        if current != retained:
            raise ValueError('ROM CMI/ESK set or retained resource bytes changed')
        check_bindings(current)
        report.update(stage='rom-bytes', image_sha256=hashlib.sha256(image).hexdigest(),
                      retained_cmi_esk_count=len(retained))
    if a.report:
        a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('HTCLEO_BLUETOOTH_BYPASS_PASS ' + json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
