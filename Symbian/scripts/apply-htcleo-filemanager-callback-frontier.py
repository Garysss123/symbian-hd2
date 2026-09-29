#!/usr/bin/env python3
"""893: copy known callback identities; leave scheduler/dispatch and sample cap intact."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
BASE = {'htcleoschedulertrace.cpp': 'fe2eb7b71809e66ef5f781c84b01d1e0a1f1babbb29081920538d11adbfd409c'}
HELPER = 'htcleofmcallback893.inl'
IDS = 'htcleofmcallback893_ids.h'
INC = '#include "' + HELPER + '"\n'
EDITS = (
    ('#include <e32base.h>\n',
     '#define protected public //893 TU-only callback visibility; no header edits\n'
     '#include <e32base.h>\n#undef protected\n'),
    ('#include "htcleofmready892.inl"\n', INC),
)

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('893 anchor drift ' + repr(old))
    return text.replace(old, new, 1)

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong893 source')
    if INC in text:
        for old, new in reversed(EDITS):
            text = once(text, new, old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact892 ready observer source')
    if not restore:
        for old, new in EDITS:
            text = once(text, old, new)
    return text

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL / 'htcleoschedulertrace.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, path.name, a.restore)
    if transform(new, path.name, True) != transform(old, path.name, True):
        raise ValueError('893 inverse')
    if not a.restore:
        if transform(new, path.name) != new:
            raise ValueError('893 idempotence')
        for helper in (HELPER, IDS):
            (a.root / REL / helper).write_bytes(
                (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / helper).read_bytes())
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_FILEMANAGER_CALLBACK=' + ('restored' if a.restore else
          'known-callback-identity-preIO32-no-dispatch'))

if __name__ == '__main__':
    main()
