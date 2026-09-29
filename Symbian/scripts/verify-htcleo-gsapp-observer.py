#!/usr/bin/env python3
"""806: pin GSApp translation, diagnostic-only import delta and ROM providers."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct

HERE = Path(__file__).resolve().parent
STOCK = '833f67e9c88528eac08b60efd2b374583d9a60e385879dc0d0f7c1f42f2d7829'
BASELINE = 'd857f69dcc865d2fd46d84c955aa7ca570b5fc60efeaaea688e55acca7a1c343'
PARENT806 = '17cdfc53c31c54e33023f37f32d4f07024f5c2960e65c8547a98cac21363b008'
# Exact imports emitted by the local native EikStart implementation plus the
# no-field CEikonEnv derived accessor/vtable. No other provider or API allowed.
EIKSTART_ADDED = {
    'apparc': [(243, 0)],
    'cone': [(184, 0), (184, 0), (179, 0), (179, 0), (669, 0), (669, 0),
             (138, 0), (138, 0), (139, 0), (139, 0), (466, 0), (466, 0),
             (467, 0), (467, 0), (93, 0), (93, 0), (638, 0), (639, 0),
             (726, 0), (727, 0), (725, 0)],
    'drtaeabi': [(127, 8)],
    'efsrv': [(12, 0), (199, 0)],
    'eikcore': [(224, 0), (224, 0), (191, 0), (191, 0), (199, 0), (199, 0),
                (213, 0), (213, 0), (344, 0), (344, 0), (496, 0), (496, 0),
                (497, 0), (497, 0), (498, 0), (498, 0), (499, 0), (499, 0),
                (500, 0), (500, 0), (501, 0), (501, 0), (502, 0), (502, 0),
                (503, 0), (503, 0), (504, 0), (504, 0), (505, 0), (505, 0),
                (371, 0), (371, 0), (396, 0), (280, 0), (283, 0)],
    'euser': [(2128, 0), (1853, 0), (598, 0), (607, 0), (1160, 0)],
}
ADDED = {
    'drtaeabi': [(127, 8), (135, 0)],
    'efsrv': [(105, 0), (263, 0), (390, 0), (93, 0), (68, 0), (97, 0), (300, 0)],
    'euser': [(2128, 0), (2128, 0), (1089, 0), (1089, 0), (1901, 0),
              (1901, 0), (928, 0), (760, 0), (1090, 0), (723, 0),
              (427, 0), (1472, 0), (1032, 0), (1094, 0), (929, 0),
              (925, 0), (758, 0), (1849, 0), (424, 0), (120, 0),
              (1091, 0), (737, 0), (2103, 0), (1088, 0), (1793, 0)],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(text):
    result, module, remaining = {}, None, 0
    for line in text.splitlines():
        match = re.fullmatch(r'(\d+) imports? from ([^{\s]+)\{[0-9a-fA-F]+\}(?:\[[0-9a-fA-F]+\])?\.dll', line)
        if not match and re.match(r'\d+ imports? from ', line):
            raise ValueError('malformed E32 import provider: ' + line)
        if match:
            if remaining:
                raise ValueError('incomplete import table')
            module, remaining = match[2].lower(), int(match[1])
            if module in result:
                raise ValueError('duplicate import provider')
            result[module] = []
        elif remaining:
            entry = re.fullmatch(r'\s*(\d+)(?: offset by (\d+))?\s*', line)
            if not entry:
                raise ValueError('invalid import entry')
            result[module].append((int(entry[1]), int(entry[2] or 0)))
            remaining -= 1
    if remaining or not result:
        raise ValueError('missing imports')
    return result


def verify_delta(before, after):
    expected = {name: Counter(values) for name, values in before.items()}
    for name, values in ADDED.items():
        if name not in expected:
            raise ValueError('missing calibration provider')
        expected[name].update(values)
    if expected != {name: Counter(values) for name, values in after.items()}:
        raise ValueError('GSApp imports differ beyond exact diagnostic delta')


def verify_eikstart_delta(before, after):
    expected = {name: Counter(values) for name, values in before.items()}
    if expected.get('eikcore', {}).get((394, 0), 0) != 1:
        raise ValueError('806 must import native EikStart once')
    del expected['eikcore'][(394, 0)]
    for name, values in EIKSTART_ADDED.items():
        if name not in expected:
            raise ValueError('local EikStart unexpectedly adds a provider')
        expected[name].update(values)
    if expected != {name: Counter(values) for name, values in after.items()}:
        raise ValueError('GSApp local EikStart import delta differs')


def header_contract(text):
    keys = ('Flags', 'Secure ID', 'Vendor ID', 'Capabilities', 'Module Version',
            'Min Heap Size', 'Max Heap Size', 'Stack Size', 'Code link addr')
    result = {}
    for key in keys:
        match = re.search(r'^' + re.escape(key) + r':\s*([^\n]+)', text, re.M)
        if not match:
            raise ValueError('missing header field ' + key)
        result[key] = ' '.join(match[1].lower().split())
    for line in ('EPOC Exe for ARMV5 CPU', 'Priority Foreground',
                 'Image FPU support : Soft VFP', 'Number of exports = 0',
                 'ARM EABI', 'Built against EKA2'):
        if line not in text.splitlines():
            raise ValueError('GSApp ABI contract: ' + line)
    if not re.search(r'^Uids:\s+1000007a 100039ce 100058ec ', text, re.M):
        raise ValueError('GSApp UID contract changed')
    return result


def verify_providers(raw, files, table, rom_base=0x12200000):
    rows = []
    for module, entries in sorted(table.items()):
        name = 'sys\\bin\\' + module + '.dll'
        if name not in files:
            raise ValueError('GSApp provider missing from actual ROM: ' + name)
        start, _ = files[name]
        if start < 0 or start + 120 > len(raw):
            raise ValueError('truncated ROM provider header')
        code, = struct.unpack_from('<I', raw, start + 0x14)
        code_size, = struct.unpack_from('<I', raw, start + 0x1c)
        count, address = struct.unpack_from('<II', raw, start + 0x3c)
        position = address - rom_base
        if not 0 < count < 10000 or position < 0 or position + 4 * count > len(raw):
            raise ValueError('invalid actual ROM export table: ' + name)
        if code != rom_base + start + 120 or code_size <= 0 or code + code_size > rom_base + len(raw):
            raise ValueError('invalid provider code bounds: ' + name)
        exports = struct.unpack_from('<' + 'I' * count, raw, position)
        for ordinal, offset in entries:
            if not 1 <= ordinal <= count:
                raise ValueError('unresolved ordinal: %s/%d' % (name, ordinal))
            target = exports[ordinal - 1]
            # All GSApp imports in this fixed profile are code/RO exports,
            # including the EABI vtable offsets. Do not accept arbitrary RAM.
            if not code <= (target & ~1) < code + code_size or not code <= ((target + offset) & ~1) < code + code_size:
                raise ValueError('null/out-of-provider export: %s/%d' % (name, ordinal))
        rows.append(dict(provider=name, exports=count, imports=len(entries)))
    return rows


def verify(raw, files, native, binary, stock_in_parent, eikstart_parent=None):
    if sha(native / 'gsapp-stock-805.exe') != STOCK or sha(stock_in_parent) != (PARENT806 if eikstart_parent else STOCK):
        raise ValueError('not immutable805 GSApp stock')
    if sha(native / 'gsapp-gcce-baseline-806.exe') != BASELINE:
        raise ValueError('unattributed GCCE calibration binary')
    dumps = [(native / name).read_text() for name in (
        'gsapp-stock-805-e32-dump.txt', 'gsapp-gcce-baseline-e32-dump.txt', 'gsapp-e32-dump.txt')]
    contracts = [header_contract(text) for text in dumps]
    if contracts[0] != contracts[1] or contracts[1] != contracts[2]:
        raise ValueError('GSApp security/heap/stack/ABI changed')
    before, after = imports(dumps[1]), imports(dumps[2])
    if len(after) != 22:
        raise ValueError('GSApp provider count drift')
    eikstart = None
    if eikstart_parent:
        parent_dump = (eikstart_parent / 'build/gsapp-e32-dump.txt').read_text()
        if header_contract(parent_dump) != contracts[2]:
            raise ValueError('806 GSApp ABI drift')
        parent_imports = imports(parent_dump)
        verify_delta(before, parent_imports)
        verify_eikstart_delta(parent_imports, after)
        eikstart = runpy.run_path(str(HERE / 'apply-htcleo-gsapp-eikstart-frontier.py'))
        source = Path('/root/symbian3-full') / eikstart['EIKSTART_REL']
        expected = eikstart['helper'](source.read_text(encoding='latin-1'))
        actual = Path('/root/symbian3-full') / eikstart['REL'] / 'Src/htcleogseikstart.inl'
        if actual.read_text(encoding='latin-1') != expected:
            raise ValueError('local EikStart not derived from pinned native body')
        env_source = source.with_name('EIKENV.CPP').read_text(encoding='latin-1')
        if 'TInt CEikonEnv::ConstructorError() const\n    {\n    return CoeEnvConstructorError();\n    }' not in env_source:
            raise ValueError('native constructor-error accessor changed')
    else:
        verify_delta(before, after)
    patch = runpy.run_path(str(HERE / 'apply-htcleo-gsapp-startup-observer.py'))
    sdk = Path('/root/symbian3-full') / patch['REL']
    for name in patch['BASE']:
        source = (sdk / name).read_text(encoding='latin-1')
        if eikstart and name == eikstart['NAME']:
            restored = eikstart['transform'](source, True)
            if eikstart['transform'](restored) != source:
                raise ValueError('GSApp local EikStart source drift')
            source = restored
        if patch['transform'](patch['transform'](source, name, True), name) != source:
            raise ValueError('GSApp observer source drift: ' + name)
    if (sdk / 'GSApplication_htcleo.mmp').read_text(encoding='latin-1') != patch['code_only_mmp']((sdk / 'GSApplication.mmp').read_text(encoding='latin-1')):
        raise ValueError('GSApp build contract drift')
    for name in ('htcleogsboot.h', 'htcleogsboot.cpp', 'htcleogslogoffset.inl', 'htcleogsheartbeat.inl'):
        if (sdk / ('Inc' if name.endswith('.h') else 'Src') / name).read_bytes() != (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / name).read_bytes():
            raise ValueError('GSApp compiled helper drift: ' + name)
    return dict(status='HTCLEO_GSAPP_OBSERVER_ABI_OK', binary_sha256=sha(binary),
                stock_sha256=STOCK, calibration_sha256=BASELINE, contract=contracts[0],
                gsapp_rom_header=files['sys\\bin\\gsapp.exe'][0] + 0x12200000,
                gsapp_rom_code=struct.unpack_from('<I', raw, files['sys\\bin\\gsapp.exe'][0] + 0x14)[0],
                diagnostic_import_additions=ADDED,
                eikstart_import_additions=EIKSTART_ADDED if eikstart else None,
                eikstart_removed_import=('eikcore394' if eikstart else None),
                rom_providers=verify_providers(raw, files, after),
                policy=('local-native-eikstart-6002-6070-6082-no-error-bypass-shared-core-unchanged' if eikstart else 'native-ui-no-resource-or-backup-key-policy-change-startup128-owned-ui5s-GSBOOT1m'),
                translation='first-GSApp-source-GCCE-build-calibrated-against-unmodified-source',
                hardware_result='pending-no-UI-pass-implied')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('image', 'rom-log', 'native', 'binary', 'stock', 'report'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--eikstart-parent', type=Path)
    args = parser.parse_args()
    rom = runpy.run_path(str(HERE / 'verify-htcleo-gate17-entry.py'))
    raw = args.image.read_bytes()
    files = rom['rom_files'](raw, args.rom_log.read_text(errors='replace'))
    result = verify(raw, files, args.native, args.binary, args.stock, args.eikstart_parent)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
