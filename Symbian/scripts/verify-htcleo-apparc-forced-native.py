#!/usr/bin/env python3
"""869 built-in checks: source-control, one APLIST object and actual ROM code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import struct

HERE = Path(__file__).resolve().parent
SDK = Path('/root/symbian3-full')
P = runpy.run_path(str(HERE / 'apply-htcleo-apparc-forced-native.py'))
X = runpy.run_path(str(HERE / 'verify-htcleo-ecom-server-exception.py'))
E32, ROM, GS, FRONT = (X[n] for n in ('E32', 'ROM', 'GS', 'FRONT'))
PARENT = HERE.parent / 'output/868-symbian3-full-filemanager-registration-census-incremental/Symbian3'
PARENT_SHA = 'e6c9ca8b13a2d0fe6c35a5c3031c8072608b92e1c515671c1f346e22adb868b3'
BINARY = SDK / 'epoc32/release/armv5/urel/aplist.dll'
EVID = HERE.parent / 'output/iteration-evidence/869-apparc-forced-native-registration'
CONTRACT = EVID / 'STANDALONE-OBJECTS.json'
CONTRACT_SHA = 'fe45b3ae70e04ab8a2c8158ee8029388d32fc999917cbe1cbf249f12cdc16e2c'
DUMP = 'aplist-forced-native-869-full-dump.txt'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def state():
    base = json.loads((EVID / 'BASE-OBJECTS.json').read_text())
    return dict(objects={p: sha(Path(p)) for p in base['objects']},
                sources={p: sha(Path(p)) for p in base['sources']},
                mmp_sha256=sha(SDK / 'sf/mw/appsupport/appfw/apparchitecture/group/APLIST.MMP'),
                binary_sha256=sha(BINARY))


def control():
    old = E32['unpack_e32'](EVID / 'aplist-parent868.dll')
    now = E32['unpack_e32'](BINARY)
    if len(old) != len(now):
        raise ValueError('869 unmodified APLIST control length changed')
    offsets = [n for n, (a, b) in enumerate(zip(old, now)) if a != b]
    if any(n not in set(range(20, 24)) | set(range(36, 44)) for n in offsets):
        raise ValueError('869 APLIST control differs beyond timestamp/headerCRC: ' + repr(offsets[:32]))
    base = json.loads((EVID / 'BASE-OBJECTS.json').read_text())
    current = state()
    if current['sources'] != base['sources'] or current['mmp_sha256'] != base['mmp_sha256']:
        raise ValueError('869 control source/MMP drift')
    if sha(PARENT / 'build/incremental-release-cache/aplist.dll') != base['binary_sha256']:
        raise ValueError('869 parent cache mismatch')
    if (EVID / 'CONTROL.json').exists():
        raise ValueError('do not overwrite869 control')
    shutil.copyfile(BINARY, EVID / 'aplist-control868.dll')
    result = dict(status='APLIST_868_CONTROL_EXACT', different_offsets=offsets,
                  ignored_fields='headerCRC20..23,timestamp36..43-only', state=current,
                  parent_sha256=base['binary_sha256'])
    (EVID / 'CONTROL.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def header(text):
    keys = ('Flags', 'Secure ID', 'Vendor ID', 'Capabilities', 'Module Version',
            'Min Heap Size', 'Max Heap Size', 'Stack Size', 'Code link addr', 'Data link addr', 'Data Size')
    fields = {k: ' '.join(re.search(r'^' + re.escape(k) + r':\s*([^\n]+)', text, re.M)[1].split()) for k in keys}
    for literal in ('EPOC Dll for ARMV5 CPU', 'Image FPU support : Soft VFP', 'ARM EABI', 'Built against EKA2'):
        if literal not in text:
            raise ValueError('APLIST platform drift: ' + literal)
    fields['exports'] = re.search(r'Number of exports = (\d+)', text)[1]
    fields['BSS'] = re.search(r'^Bss\s+(\S+)', text, re.M)[1]
    fields['UIDs'] = ' '.join(re.search(r'^Uids:\s*([^\n]+)', text, re.M)[1].split())
    return fields


def objects(native):
    if sha(PARENT / 'initrd.gz') != PARENT_SHA or sha(CONTRACT) != CONTRACT_SHA:
        raise ValueError('869 parent/contract drift')
    c = json.loads(CONTRACT.read_text())
    base = json.loads((EVID / 'CONTROL.json').read_text())['state']
    current = state()
    if any(current[k] != c[k] for k in ('objects', 'sources', 'mmp_sha256')):
        raise ValueError('869 source/objects differ from reviewed standalone')
    changed = [Path(p).name for p in current['objects'] if current['objects'][p] != base['objects'][p]]
    if sorted(changed) != ['aplappregfinder.o'] or current['mmp_sha256'] != base['mmp_sha256']:
        raise ValueError('869 changes exceed one finder object')
    body = (SDK / P['REL']).read_text()
    if P['transform'](body) != body:
        raise ValueError('869 finder patch drift')
    before = (EVID / 'aplist-parent868-full-dump.txt').read_text()
    after = (native / DUMP).read_text()
    if header(before) != header(after):
        raise ValueError('869 APLIST ABI/exports/data/BSS changed')
    if {m: Counter(v) for m, v in GS['imports'](before).items()} != {m: Counter(v) for m, v in GS['imports'](after).items()}:
        raise ValueError('869 APLIST imports changed')
    raw = E32['unpack_e32'](BINARY)
    if any(struct.unpack_from('<I', raw, n)[0] for n in (52, 68, 116)):
        raise ValueError('869 requires unchanged zero data/BSS/data-relocations')
    return dict(status='APLIST_FORCED_NATIVE_OBJECTS_OK', **current,
                changed_objects=changed, header=header(after), imports_unchanged=True,
                data_bytes=0, bss_bytes=0, policy=P['POLICY'])


def module_rom(image, files):
    raw = E32['unpack_e32'](BINARY)
    w = lambda n: struct.unpack_from('<I', raw, n)[0]
    start, _ = files['sys\\bin\\aplist.dll']
    code, data, size = struct.unpack_from('<III', image, start + 0x14)
    if code != ROM['ROM_BASE'] + start + 120 or size != w(48) or struct.unpack_from('<I', image, start + 0x24)[0]:
        raise ValueError('869 APLIST module layout changed')
    expected = bytearray(raw[w(100):w(100) + size])
    sites, _, _ = FRONT['parse_e32_import_sites'](raw)
    for pos, kind in E32['code_relocations'](raw).items():
        if pos + 120 in sites:
            continue
        value = struct.unpack_from('<I', expected, pos)[0]
        if kind == 2 or not w(76) <= (value & ~1) <= w(76) + size:
            raise ValueError('869 unexpected non-code relocation ' + hex(pos))
        struct.pack_into('<I', expected, pos, value + code - w(76))
    for pos, (module, ordinal, addend) in sites.items():
        at = files['sys\\bin\\' + module + '.dll'][0]
        count, address = struct.unpack_from('<II', image, at + 0x3c)
        if not 1 <= ordinal <= count:
            raise ValueError('869 missing import ordinal')
        target = struct.unpack_from('<I', image, address - ROM['ROM_BASE'] + (ordinal - 1) * 4)[0]
        if not target:
            raise ValueError('869 absent import')
        struct.pack_into('<I', expected, pos - 120, target + addend)
    if bytes(expected) != image[start + 120:start + 120 + size]:
        raise ValueError('869 actual ROM differs beyond native code/import relocations')
    return dict(code_address=hex(code), code_bytes=size, data_bytes=0, bss_bytes=0, code_exact=True)


def verify(a):
    proof = objects(a.native)
    if a.recipe.read_text() != (PARENT / 'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('869 ROM recipe changed')
    cache = PARENT / 'build/incremental-release-cache'
    rows = (cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows) != 67:
        raise ValueError('869 cache count changed')
    for row in rows:
        digest, path, name = row.split('\t')
        if sha(cache / name) != digest or (path != str(BINARY) and sha(Path(path)) != digest):
            raise ValueError('869 changed another binary: ' + name)
    old = (PARENT / 'initrd.gz').read_bytes()
    new = a.image.read_bytes()
    f0 = ROM['rom_files'](old, (PARENT / 'build/ROMBUILD.LOG').read_text(errors='replace'))
    f1 = ROM['rom_files'](new, a.rom_log.read_text(errors='replace'))
    if set(f0) != set(f1):
        raise ValueError('869 ROM membership changed')
    for name in f0:
        if not name.startswith('sys\\bin\\') and ROM['file_data'](old, f0, name) != ROM['file_data'](new, f1, name):
            raise ValueError('869 changed resource: ' + name)
    if (len(new) + 1048575) // 1048576 * 1048576 != 0x03a00000:
        raise ValueError('869 ROM window changed')
    return dict(status='APLIST_FORCED_NATIVE_ROM_OK', parent_package=PARENT.parent.name,
                parent_sha256=PARENT_SHA, image_sha256=sha(a.image), image_bytes=len(new),
                object_proof=proof, module=module_rom(new, f1),
                providers=GS['verify_providers'](new, f1, GS['imports']((a.native / DUMP).read_text())),
                other_cached_binaries_unchanged=66, resources_unchanged=True, membership_unchanged=True,
                c_overlay_unchanged=True, census868_retained=True, rom_window=0x03a00000, ram_start=0x15c00000,
                hardware_result='pending')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--control', action='store_true')
    p.add_argument('--native', type=Path, default=EVID)
    p.add_argument('--report', type=Path)
    p.add_argument('--image', type=Path)
    p.add_argument('--recipe', type=Path)
    p.add_argument('--rom-log', type=Path)
    a = p.parse_args()
    result = control() if a.control else verify(a) if a.image else objects(a.native)
    if a.report:
        a.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
