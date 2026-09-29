#!/usr/bin/env python3
"""890: FileManager enqueue/deferred ActivationTick observation, native policy intact."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/uifw/AvKon/src')
BASE = {'AknViewAppUi.cpp': '5d94955f1174ab2992022cfb6d6b75ceb72f75b854c031e4b9dd85f438e0895d'}
ORIGINAL = 'htcleogsactivationtrace.inl'
ORIGINAL_SHA = '728c195ee28cc74704c0e84defd35ce81b44a98638248b2f0a702a41dfb4a9c4'
HELPER = 'htcleofmactivation890.inl'
WRITER = 'htcleofmactivationwriter890.inl'
QUEUE = '    const TBool htcleoGsQueueTrace = (RProcess().SecureId().iId == 0x100058ecu);\n'
EXTRA_QUEUE = '    const TBool htcleoFmQueueTrace = (RProcess().SecureId().iId == 0x101f84ebu); //890 observation only\n'
TICK = '    const TBool htcleoGsActivationTrace = (RProcess().SecureId().iId == 0x100058ecu);'
NEW_TICK = '    const TBool htcleoGsActivationTrace = HtcleoFmActivationScope(RProcess().SecureId().iId); //890 observation only'
ROUTE = '''    if (RProcess().SecureId().iId == 0x101f84ebu)
        {
        HtcleoFmActivationWrite(aStage, aResult, aDetail);
        return;
        }
'''
EDITS = [
    ('#include "' + ORIGINAL + '"', '#include "' + HELPER + '"'),
    (QUEUE, QUEUE + EXTRA_QUEUE),
    (TICK, NEW_TICK),
]
for stage in ('c603', 'c604', 'c607'):
    old = '    if (htcleoGsQueueTrace) HtcleoGsActivationLog(htcleoGsQueueRecords, 0x' + stage + 'u,'
    new = old.replace('if (htcleoGsQueueTrace)', 'if (htcleoGsQueueTrace || htcleoFmQueueTrace)')
    EDITS.append((old, new))

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('890 anchor drift ' + repr(old))
    return text.replace(old, new, 1)

def derive_helper(raw, writer):
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError('original GS activation helper drift')
    text = raw.decode('latin-1').replace('\r\n', '\n')
    anchor = '    if (!HtcleoGsActivationTake(aCount, aStage)) return;\n'
    return writer + b'\n' + once(text, anchor, anchor + ROUTE).encode('latin-1')

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong890 source')
    if '#include "' + HELPER + '"' in text:
        for old, new in reversed(EDITS):
            text = once(text, new, old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact889 ViewAppUi source')
    if not restore:
        for old, new in EDITS:
            text = once(text, old, new)
    return text

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL / 'AknViewAppUi.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, 'AknViewAppUi.cpp', a.restore)
    if transform(new, 'AknViewAppUi.cpp', True) != transform(old, 'AknViewAppUi.cpp', True):
        raise ValueError('890 inverse')
    if not a.restore:
        if transform(new, 'AknViewAppUi.cpp') != new:
            raise ValueError('890 idempotence')
        assets = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics'
        raw = (assets / ORIGINAL).read_bytes()
        if (a.root / REL / ORIGINAL).read_bytes() != raw:
            raise ValueError('SDK original activation helper changed')
        (a.root / REL / HELPER).write_bytes(derive_helper(raw, (assets / WRITER).read_bytes()))
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_FILEMANAGER_ACTIVATION=' + ('restored' if a.restore else
          'FileManager-enqueue-deferred-ActivationTick-FMACT64-native-errors-cleanup-unchanged'))

if __name__ == '__main__':
    main()
