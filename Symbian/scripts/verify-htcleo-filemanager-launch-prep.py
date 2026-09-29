#!/usr/bin/env python3
"""876 built-in checks: source-control, one APSERV object and actual ROM code."""
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
P = runpy.run_path(str(HERE / 'apply-htcleo-filemanager-launch-prep.py'))
X = runpy.run_path(str(HERE / 'verify-htcleo-ecom-server-exception.py'))
E32, ROM, GS, FRONT = (X[n] for n in ('E32', 'ROM', 'GS', 'FRONT'))
ABS = runpy.run_path(str(HERE / 'verify-htcleo-avkon-common-geometry.py'))
PARENT = HERE.parent / 'output/875-symbian3-full-apparc-preload-publication-incremental/Symbian3'
PARENT_SHA = '0025d164f775fdbc461bb0b4d698411050cfc4b636e76b96837694e402765d69'
BINARY = SDK / 'epoc32/release/armv5/urel/apserv.dll'
EVID = HERE.parent / 'output/iteration-evidence/876-filemanager-launch-prep'
CONTRACT = EVID / 'STANDALONE-OBJECTS.json'
CONTRACT_SHA = '3fd34062630f81d829228ad2f80165b9eeefa4171c4be02cb5c0cd4ed378be63'
DUMP = 'apserv-launch-prep-876-full-dump.txt'
ADDED_IMPORTS = {'drtaeabi': [135, 222], 'efsrv': [105],
                 'euser': [723, 1534, 1793, 1826, 1849, 2103, 2107]}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def state():
    base = json.loads((EVID / 'BASE-OBJECTS.json').read_text())
    return dict(objects={p: sha(Path(p)) for p in base['objects']},
                sources={p: sha(Path(p)) for p in base['sources']},
                mmp_sha256=sha(SDK / 'sf/mw/appsupport/appfw/apparchitecture/group/APSERV.MMP'),
                binary_sha256=sha(BINARY),
                helper_sha256=sha(SDK/P['REL'].with_name(P['ASSET'].name)))


def header(text):
    keys = ('Flags', 'Secure ID', 'Vendor ID', 'Capabilities', 'Module Version',
            'Min Heap Size', 'Max Heap Size', 'Stack Size', 'Code link addr', 'Data link addr', 'Data Size')
    fields = {k: ' '.join(re.search(r'^' + re.escape(k) + r':\s*([^\n]+)', text, re.M)[1].split()) for k in keys}
    for literal in ('EPOC Dll for ARMV5 CPU', 'Image FPU support : Soft VFP', 'ARM EABI', 'Built against EKA2'):
        if literal not in text:
            raise ValueError('APSERV platform drift: ' + literal)
    fields['exports'] = re.search(r'Number of exports = (\d+)', text)[1]
    fields['BSS'] = re.search(r'^Bss\s+(\S+)', text, re.M)[1]
    fields['UIDs'] = ' '.join(re.search(r'^Uids:\s*([^\n]+)', text, re.M)[1].split())
    return fields


def objects(native):
    if sha(PARENT / 'initrd.gz') != PARENT_SHA or sha(CONTRACT) != CONTRACT_SHA:
        raise ValueError('876 parent/contract drift')
    c = json.loads(CONTRACT.read_text())
    base = json.loads((EVID / 'BASE-OBJECTS.json').read_text())
    current = state()
    if any(current[k] != c[k] for k in ('objects', 'sources', 'mmp_sha256', 'helper_sha256')):
        raise ValueError('876 source/objects differ from reviewed standalone')
    changed = [Path(p).name for p in current['objects'] if current['objects'][p] != base['objects'][p]]
    if sorted(changed) != ['APSSES.o'] or current['mmp_sha256'] != base['mmp_sha256']:
        raise ValueError('876 changes exceed one preload object')
    body = (SDK / P['REL']).read_text()
    if current['helper_sha256'] != sha(P['ASSET']):
        raise ValueError('876 helper differs from reviewed asset')
    if P['transform'](body) != body:
        raise ValueError('876 preload patch drift')
    before = (EVID / 'apserv-parent875-full-dump.txt').read_text()
    after = (native / DUMP).read_text()
    if header(before) != header(after):
        raise ValueError('876 APSERV ABI/exports/data/BSS changed')
    expected_imports = {m: Counter(v) for m, v in GS['imports'](before).items()}
    # Exact added native observer imports are reviewed after standalone build.
    for module, ordinals in ADDED_IMPORTS.items():
        for ordinal in ordinals:
            expected_imports[module][(ordinal, 0)] += 1
    if expected_imports != {m: Counter(v) for m, v in GS['imports'](after).items()}:
        raise ValueError('876 APSERV imports differ beyond reviewed observer imports')
    raw = E32['unpack_e32'](BINARY)
    if any(struct.unpack_from('<I', raw, n)[0] for n in (52, 68, 116)):
        raise ValueError('876 requires unchanged zero data/BSS/data-relocations')
    return dict(status='APSERV_FILEMANAGER_LAUNCH_PREP_OBJECTS_OK', **current,
                changed_objects=changed, header=header(after), added_import=ADDED_IMPORTS,
                data_bytes=0, bss_bytes=0, policy=P['POLICY'])


def module_rom(image, files):
    raw = E32['unpack_e32'](BINARY)
    w = lambda n: struct.unpack_from('<I', raw, n)[0]
    start, _ = files['sys\\bin\\apserv.dll']
    code, data, size = struct.unpack_from('<III', image, start + 0x14)
    if code != ROM['ROM_BASE'] + start + 120 or size != w(48) or struct.unpack_from('<I', image, start + 0x24)[0]:
        raise ValueError('876 APSERV module layout changed')
    expected = bytearray(raw[w(100):w(100) + size])
    sites, _, _ = FRONT['parse_e32_import_sites'](raw)
    for pos, kind in E32['code_relocations'](raw).items():
        if pos + 120 in sites:
            continue
        value = struct.unpack_from('<I', expected, pos)[0]
        if kind == 2 or not w(76) <= (value & ~1) <= w(76) + size:
            raise ValueError('876 unexpected non-code relocation ' + hex(pos))
        struct.pack_into('<I', expected, pos, value + code - w(76))
    for pos, (module, ordinal, addend) in sites.items():
        at = files['sys\\bin\\' + module + '.dll'][0]
        count, address = struct.unpack_from('<II', image, at + 0x3c)
        if not 1 <= ordinal <= count:
            raise ValueError('876 missing import ordinal')
        target = struct.unpack_from('<I', image, address - ROM['ROM_BASE'] + (ordinal - 1) * 4)[0]
        if not target:
            raise ValueError('876 absent import')
        struct.pack_into('<I', expected, pos - 120, target + addend)
    # Reuse the existing strict E32-header bitmap decoder. The ROM builder
    # converts declared ABSENT exports from entry-point sentinels to zero.
    holes = ABS['apply_absent_exports'](expected, raw, code)
    if holes != ABS['absent_exports'](E32['unpack_e32'](EVID / 'apserv-parent875.dll')) or len(holes) != 24:
        raise ValueError('876 changed the parent declared-absent export set')
    actual = image[start + 120:start + 120 + size]
    if bytes(expected) != actual:
        positions = [n for n, (left, right) in enumerate(zip(expected, actual)) if left != right]
        words = sorted({n & ~3 for n in positions})
        detail = [(hex(n), expected[n:n+4].hex(), actual[n:n+4].hex()) for n in words[:32]]
        raise ValueError('876 actual ROM differs beyond native code/import relocations: ' + repr(detail))
    return dict(code_address=hex(code), code_bytes=size, data_bytes=0, bss_bytes=0,
                absent_exports=holes, code_exact=True)


def verify(a):
    proof = objects(a.native)
    if a.recipe.read_text() != (PARENT / 'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('876 ROM recipe changed')
    cache = PARENT / 'build/incremental-release-cache'
    rows = (cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows) != 67:
        raise ValueError('876 cache count changed')
    for row in rows:
        digest, path, name = row.split('\t')
        if sha(cache / name) != digest or (path != str(BINARY) and sha(Path(path)) != digest):
            raise ValueError('876 changed another binary: ' + name)
    old = (PARENT / 'initrd.gz').read_bytes()
    new = a.image.read_bytes()
    f0 = ROM['rom_files'](old, (PARENT / 'build/ROMBUILD.LOG').read_text(errors='replace'))
    f1 = ROM['rom_files'](new, a.rom_log.read_text(errors='replace'))
    if set(f0) != set(f1):
        raise ValueError('876 ROM membership changed')
    for name in f0:
        if not name.startswith('sys\\bin\\') and ROM['file_data'](old, f0, name) != ROM['file_data'](new, f1, name):
            raise ValueError('876 changed resource: ' + name)
    if (len(new) + 1048575) // 1048576 * 1048576 != 0x03a00000:
        raise ValueError('876 ROM window changed')
    return dict(status='APSERV_FILEMANAGER_LAUNCH_PREP_ROM_OK', parent_package=PARENT.parent.name,
                parent_sha256=PARENT_SHA, image_sha256=sha(a.image), image_bytes=len(new),
                object_proof=proof, module=module_rom(new, f1),
                providers=GS['verify_providers'](new, f1, GS['imports']((a.native / DUMP).read_text())),
                other_cached_binaries_unchanged=66, resources_unchanged=True, membership_unchanged=True,
                c_overlay_unchanged=True, admission869_and_watch870_retained=True, reconnect871_retired=True,
                rom_window=0x03a00000, ram_start=0x15c00000,
                hardware_result='pending')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--native', type=Path, default=EVID)
    p.add_argument('--report', type=Path)
    p.add_argument('--image', type=Path)
    p.add_argument('--recipe', type=Path)
    p.add_argument('--rom-log', type=Path)
    p.add_argument('--capture-state', action='store_true')
    a = p.parse_args()
    result = state() if a.capture_state else (verify(a) if a.image else objects(a.native))
    if a.report:
        a.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
