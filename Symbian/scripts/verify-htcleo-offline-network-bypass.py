#!/usr/bin/env python3
"""777: DIP reverse-binding closure, protocol ownership and exact ROM resources."""
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import runpy

BASE = runpy.run_path(str(Path(__file__).with_name('verify-htcleo-bluetooth-bypass.py')))
resources = BASE['resources']
destination = BASE['destination']
PARENT_SHA = BASE['PARENT_SHA']
MODULES = {'esock_dip', 'esock_ip', 'esock_sip', 'esock_bt'}
MARKER = 'REM HTCLEO disabled optional network startup/protocol: '
DISABLED = {
    r'private\101f7988\esock_bt.cmi',
    r'private\101f7988\esock_dip.cmi',
    r'private\101f7988\esock_mip.cmi',
    r'private\101f7988\esock_sip.cmi',
    r'private\101f7989\esock\bt.bt_v2.esk',
    r'private\101f7989\esock\ip.addressinfo_tcpip.esk',
    r'private\101f7989\esock\ip.rtp.esk',
    r'private\101f7989\esock\ip.tcpip.esk',
    r'private\101f7989\esock\ip.napt.esk',
    r'private\101f7989\esock\ip.probe.esk',
    r'private\101f7989\esock\sip.providers.esk',
}
TAILS = tuple('/' + name.replace('\\', '/') for name in sorted(DISABLED))


def disabled(name):
    return name.lower().endswith(TAILS)


def modules(records):
    result = {}
    for source, raw in records.items():
        if not source.lower().endswith('.cmi') or not raw:
            continue
        fields = {}
        for line in raw.decode('latin-1').splitlines():
            line = line.split('#', 1)[0].strip()
            if '=' in line:
                key, value = line.split('=', 1)
                fields[key.strip().lower()] = value.strip()
        name = fields.get('name', '').lower()
        if not name or name in result:
            raise ValueError('invalid/duplicate CMI module: ' + source)
        dependencies = set()
        for key, value in fields.items():
            if re.fullmatch(r'binding\d+', key):
                ends = value.split(',')[:2]
                if len(ends) != 2 or any(':' not in end for end in ends):
                    raise ValueError('invalid binding: ' + source)
                dependencies.update(end.split(':', 1)[0].strip().lower() for end in ends)
        result[name] = dict(source=source, dependencies=dependencies,
                            mask=fields.get('eskmask', '').lower())
    return result


def reverse_closure(items, seeds):
    closed = set(seeds)
    while True:
        added = {name for name, item in items.items()
                 if item['dependencies'] & closed} - closed
        if not added:
            return closed
        closed.update(added)


def check_recipe(before, after):
    seen, expected = set(), []
    for line in before.replace('\r', '').splitlines():
        target = destination(line)
        if not line.lstrip().upper().startswith('REM') and target in DISABLED:
            if target in seen:
                raise ValueError('duplicate disabled destination')
            seen.add(target)
            expected.append(MARKER + line)
        else:
            expected.append(line)
    if seen != DISABLED or after.replace('\r', '').splitlines() != expected:
        raise ValueError('recipe changed outside the exact11-resource offline closure')


def check_closed_graph(records):
    items = modules(records)
    if set(items) & MODULES:
        raise ValueError('disabled module remains present')
    if not {'esock_main', 'esock_tr', 'c32_main'} <= set(items):
        raise ValueError('shared Main/TR/C32 service configuration was lost')
    if any(item['dependencies'] & MODULES for item in items.values()):
        raise ValueError('retained reverse binding references disabled module')


def self_test():
    graph = {'esock_dip': {'dependencies': {'esock_main'}},
             'esock_ip': {'dependencies': {'esock_dip', 'esock_tr'}},
             'esock_sip': {'dependencies': {'esock_dip'}},
             'esock_bt': {'dependencies': {'esock_ip'}},
             'esock_tr': {'dependencies': {'esock_main'}}}
    assert reverse_closure(graph, {'esock_dip'}) == MODULES
    old = '\n'.join('data=/source "' + name + '"' for name in sorted(DISABLED))
    new = '\n'.join(MARKER + line for line in old.splitlines())
    check_recipe(old, new)
    try:
        check_recipe(old, new + '\nfile=/bad "sys\\bin\\esocksvr.dll"')
    except ValueError:
        pass
    else:
        raise AssertionError('unexpected recipe edit accepted')
    fixture = {'/x.cmi': b'[Loader]\nName=X\n#Binding0=X:0,ESock_DIP:1\nBinding1=X:0,ESock_Main:0\n'}
    assert modules(fixture)['x']['dependencies'] == {'x', 'esock_main'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--recipe', type=Path, required=True)
    p.add_argument('--image', type=Path)
    p.add_argument('--rom-log', type=Path)
    p.add_argument('--report', type=Path)
    a = p.parse_args()
    self_test()
    old_image = (a.parent / 'initrd.gz').read_bytes()
    if hashlib.sha256(old_image).hexdigest() != PARENT_SHA:
        raise ValueError('not the pinned775 recovery baseline')
    check_recipe((a.parent / 'build/htcleo_symbian3_full_native.oby').read_text(),
                 a.recipe.read_text())
    old = resources((a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace'), old_image)
    items = modules(old)
    closed = reverse_closure(items, {'esock_dip'})
    if closed != MODULES:
        raise ValueError('DIP reverse-dependency closure differs: ' + repr(closed))
    owned = {items[name]['source'] for name in closed}
    masks = {items[name]['mask'] for name in closed if items[name]['mask']}
    owned.update(source for source in old if source.lower().endswith('.esk') and
                 any(fnmatch.fnmatchcase(Path(source).name.lower(), mask) for mask in masks))
    selected = {source for source in old if disabled(source)}
    if owned != selected or len(selected) != len(DISABLED):
        raise ValueError('configured protocol masks do not match exact removal set')
    retained = {name: data for name, data in old.items() if name not in selected}
    check_closed_graph(retained)
    report = dict(parent_sha256=PARENT_SHA, removed_destinations=sorted(DISABLED),
                  removed_modules=sorted(closed), reverse_bindings=0,
                  retained_base_modules=['c32_main', 'esock_main', 'esock_tr'],
                  binary_policy='all54-parent775-binaries-unchanged', stage='recipe-only',
                  hardware_result='pending', java_functionality='not-yet-validated')
    if a.image or a.rom_log:
        if not (a.image and a.rom_log):
            raise ValueError('image and rom-log required together')
        image = a.image.read_bytes()
        current = resources(a.rom_log.read_text(errors='replace'), image)
        if current != retained:
            raise ValueError('retained CMI/ESK bytes or resource membership changed')
        check_closed_graph(current)
        report.update(stage='rom-bytes', image_sha256=hashlib.sha256(image).hexdigest(),
                      retained_cmi_esk_count=len(current))
    if a.report:
        a.report.write_text(json.dumps(report, indent=2) + '\n')
    print('HTCLEO_OFFLINE_NETWORK_BYPASS_PASS ' + json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
