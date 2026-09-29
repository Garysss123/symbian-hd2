#!/usr/bin/env python3
"""873 built-in checks: source-control, one APSEXE object and actual ROM code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import struct
import subprocess

HERE = Path(__file__).resolve().parent
SDK = Path('/root/symbian3-full')
P = runpy.run_path(str(HERE / 'apply-htcleo-apparc-terminal-exception.py'))
X = runpy.run_path(str(HERE / 'verify-htcleo-ecom-server-exception.py'))
E32, ROM, GS, FRONT = (X[n] for n in ('E32', 'ROM', 'GS', 'FRONT'))
PARENT = HERE.parent / 'output/872-symbian3-full-apparc-enumeration-end-incremental/Symbian3'
PARENT_SHA = 'f8c50231a1359354295530fa044a6838c6ce7b936cdb240e6e23789cbbe4584c'
BINARY = SDK / 'epoc32/release/armv5/urel/apsexe.exe'
EVID = HERE.parent / 'output/iteration-evidence/873-apparc-terminal-exception'
CONTRACT = EVID / 'STANDALONE-OBJECTS.json'
CONTRACT_SHA = 'e8662f8484ce2e73705056405a44791718becde88742be6eab9d56a8d9701f9f'
DUMP = 'apsexe-exception-873-full-dump.txt'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def state():
    base = json.loads((EVID / 'BASE-OBJECTS.json').read_text())
    return dict(objects={p: sha(Path(p)) for p in base['objects']},
                sources={p: sha(Path(p)) for p in base['sources']},
                mmp_sha256=sha(SDK / 'sf/mw/appsupport/appfw/apparchitecture/group/APSEXE.MMP'),
                binary_sha256=sha(BINARY))


def control():
    old = E32['unpack_e32'](EVID / 'apsexe-parent872.exe')
    now = E32['unpack_e32'](BINARY)
    if len(old) != len(now):
        raise ValueError('873 unmodified APSEXE control length changed')
    offsets = [n for n, (a, b) in enumerate(zip(old, now)) if a != b]
    if any(n not in set(range(20, 24)) | set(range(36, 44)) for n in offsets):
        raise ValueError('873 APSEXE control differs beyond timestamp/headerCRC: ' + repr(offsets[:32]))
    base = json.loads((EVID / 'BASE-OBJECTS.json').read_text())
    current = state()
    if current['sources'] != base['sources'] or current['mmp_sha256'] != base['mmp_sha256']:
        raise ValueError('873 control source/MMP drift')
    if sha(PARENT / 'build/incremental-release-cache/apsexe.exe') != base['binary_sha256']:
        raise ValueError('873 parent cache mismatch')
    if (EVID / 'CONTROL.json').exists():
        raise ValueError('do not overwrite869 control')
    shutil.copyfile(BINARY, EVID / 'apsexe-control872.exe')
    result = dict(status='APSEXE_872_CONTROL_EXACT', different_offsets=offsets,
                  ignored_fields='headerCRC20..23,timestamp36..43-only', state=current,
                  parent_sha256=base['binary_sha256'])
    (EVID / 'CONTROL.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def header(text):
    keys = ('Flags', 'Secure ID', 'Vendor ID', 'Capabilities', 'Module Version',
            'Min Heap Size', 'Max Heap Size', 'Stack Size', 'Code link addr', 'Data link addr', 'Data Size')
    fields = {k: ' '.join(re.search(r'^' + re.escape(k) + r':\s*([^\n]+)', text, re.M)[1].split()) for k in keys}
    for literal in ('EPOC Exe for ARMV5 CPU', 'Image FPU support : Soft VFP', 'ARM EABI', 'Built against EKA2'):
        if literal not in text:
            raise ValueError('APSEXE platform drift: ' + literal)
    fields['exports'] = re.search(r'Number of exports = (\d+)', text)[1]
    fields['BSS'] = re.search(r'^Bss\s+(\S+)', text, re.M)[1]
    fields['UIDs'] = ' '.join(re.search(r'^Uids:\s*([^\n]+)', text, re.M)[1].split())
    return fields


def objects(native):
    if sha(PARENT / 'initrd.gz') != PARENT_SHA or sha(CONTRACT) != CONTRACT_SHA:
        raise ValueError('873 parent/contract drift')
    c = json.loads(CONTRACT.read_text())
    base = json.loads((EVID / 'CONTROL.json').read_text())['state']
    current = state()
    if any(current[k] != c[k] for k in ('objects', 'sources', 'mmp_sha256')):
        raise ValueError('873 source/objects differ from reviewed standalone')
    changed = [Path(p).name for p in current['objects'] if current['objects'][p] != base['objects'][p]]
    if sorted(changed) != ['APSMAIN.o']:
        raise ValueError('873 changes exceed one APSEXE main object')
    mmp = (SDK / P['MMP']).read_text()
    if P['transform_mmp'](mmp) != mmp or hashlib.sha256(P['transform_mmp'](mmp, True).encode()).hexdigest() != base['mmp_sha256']:
        raise ValueError('873 MMP changes exceed the terminal efsrv import library')
    body = (SDK / P['REL']).read_text()
    if P['transform'](body) != body:
        raise ValueError('873 finder patch drift')
    before = (EVID / 'apsexe-parent872-full-dump.txt').read_text()
    after = (native / DUMP).read_text()
    h0, h1 = header(before), header(after)
    if h0.pop('BSS') != '000000' or h1.pop('BSS') != '000404':
        raise ValueError('873 must add exactly1028 zero-initialized bytes')
    if h0.pop('Data link addr') != '00000000' or h1.pop('Data link addr') != '00400000' or h0 != h1:
        raise ValueError('873 APSEXE ABI/stack/heap/capabilities changed')
    expected = {m: Counter(v) for m, v in GS['imports'](before).items()}
    delta = {'efsrv': (97, 300, 68, 93, 105, 390, 263),
             'euser': (1033, 1793, 1801, 1849, 1854, 1951, 2103, 602, 620, 635)}
    for module, ordinals in delta.items():
        target = expected.setdefault(module, Counter())
        for ordinal in ordinals:
            target[(ordinal, 0)] += 1
    if expected != {m: Counter(v) for m, v in GS['imports'](after).items()}:
        raise ValueError('873 imports exceed the reviewed terminal writer and handler APIs')
    helper = SDK / P['REL'].parent / P['HELPER']
    if sha(helper) != c['helper_sha256'] or helper.read_bytes() != (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / P['HELPER']).read_bytes():
        raise ValueError('873 exception helper drift')
    obj = Path(next(iter(current['objects'])))
    disasm = subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump', '-drC', str(obj)], text=True)
    wrapper = re.search(r'<HtcleoApaSoftwareException\(TExcType\)>:\n(.*?)(?:\n\n|\Z)', disasm, re.S)
    if not wrapper:
        raise ValueError('873 naked wrapper missing')
    instructions = re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{4})\s+', wrapper[1], re.M)
    if instructions[:2] != ['4669', '4672'] or len(instructions) < 3 or int(instructions[2], 16)&0xf800 != 0xe000 or 'HtcleoApaExceptionBody' not in wrapper[1]:
        raise ValueError('873 wrapper must capture entrySP/LR before allocating stack')
    symbols = subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump', '-tC', str(obj)], text=True)
    for size, name in (('00000400', 'gHtcleoApaExceptionRecord'), ('00000004', 'gHtcleoApaExceptionWriting')):
        if not re.search(r'\.bss\s+' + size + r'\s+' + name + r'\s*$', symbols, re.M):
            raise ValueError('873 static terminal buffer attribution drift')
    raw = E32['unpack_e32'](BINARY)
    if tuple(struct.unpack_from('<I', raw, n)[0] for n in (52, 68, 116)) != (0, 1028, 0):
        raise ValueError('873 data/BSS/data-relocations exceed terminal buffer')
    return dict(status='APSEXE_TERMINAL_EXCEPTION_OBJECTS_OK', **current,
                changed_objects=changed, header=header(after), import_delta=delta,
                helper_sha256=c['helper_sha256'], wrapper=wrapper[1].strip(),
                no_startup_file_io=True, data_bytes=0, bss_bytes=1028, policy=P['POLICY'])


def module_rom(image, files):
    raw = E32['unpack_e32'](BINARY)
    w = lambda n: struct.unpack_from('<I', raw, n)[0]
    start, _ = files['sys\\bin\\apsexe.exe']
    code, data, size = struct.unpack_from('<III', image, start + 0x14)
    if code != ROM['ROM_BASE'] + start + 120 or size != w(48) or struct.unpack_from('<I', image, start + 0x24)[0]:
        raise ValueError('873 APSEXE module layout changed')
    expected = bytearray(raw[w(100):w(100) + size])
    ram = struct.unpack_from('<I', image, start + 0x60)[0]
    sites, _, _ = FRONT['parse_e32_import_sites'](raw)
    for pos, kind in E32['code_relocations'](raw).items():
        if pos + 120 in sites:
            continue
        value = struct.unpack_from('<I', expected, pos)[0]
        if kind != 2 and w(76) <= (value & ~1) <= w(76) + size:
            resolved = value + code - w(76)
        elif kind != 1 and w(80) <= value <= w(80) + w(68):
            resolved = value + ram - w(80)
        else:
            raise ValueError('873 unattributed code/BSS relocation ' + hex(pos))
        struct.pack_into('<I', expected, pos, resolved)
    for pos, (module, ordinal, addend) in sites.items():
        at = files['sys\\bin\\' + module + '.dll'][0]
        count, address = struct.unpack_from('<II', image, at + 0x3c)
        if not 1 <= ordinal <= count:
            raise ValueError('873 missing import ordinal')
        target = struct.unpack_from('<I', image, address - ROM['ROM_BASE'] + (ordinal - 1) * 4)[0]
        if not target:
            raise ValueError('873 absent import')
        struct.pack_into('<I', expected, pos - 120, target + addend)
    if bytes(expected) != image[start + 120:start + 120 + size]:
        raise ValueError('873 actual ROM differs beyond native code/import relocations')
    return dict(code_address=hex(code), code_bytes=size, data_bytes=0, bss_bytes=1028,
                private_data_base=hex(ram), code_exact=True)


def verify(a):
    proof = objects(a.native)
    if a.recipe.read_text() != (PARENT / 'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('873 ROM recipe changed')
    cache = PARENT / 'build/incremental-release-cache'
    rows = (cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows) != 67:
        raise ValueError('873 cache count changed')
    for row in rows:
        digest, path, name = row.split('\t')
        if sha(cache / name) != digest or (path != str(BINARY) and sha(Path(path)) != digest):
            raise ValueError('873 changed another binary: ' + name)
    old = (PARENT / 'initrd.gz').read_bytes()
    new = a.image.read_bytes()
    f0 = ROM['rom_files'](old, (PARENT / 'build/ROMBUILD.LOG').read_text(errors='replace'))
    f1 = ROM['rom_files'](new, a.rom_log.read_text(errors='replace'))
    if set(f0) != set(f1):
        raise ValueError('873 ROM membership changed')
    for name in f0:
        if not name.startswith('sys\\bin\\') and ROM['file_data'](old, f0, name) != ROM['file_data'](new, f1, name):
            raise ValueError('873 changed resource: ' + name)
    if (len(new) + 1048575) // 1048576 * 1048576 != 0x03a00000:
        raise ValueError('873 ROM window changed')
    return dict(status='APSEXE_TERMINAL_EXCEPTION_ROM_OK', parent_package=PARENT.parent.name,
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
