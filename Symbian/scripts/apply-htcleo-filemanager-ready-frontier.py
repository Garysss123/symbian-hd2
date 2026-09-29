#!/usr/bin/env python3
"""892: bounded ready-AO candidates after the existing CONE wait; no dispatch."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
BASE = {'htcleoschedulertrace.cpp': '405b3e6b71d04123ecb17143f23eb243c6e00b557935a19235005aee027ee1b3'}
HELPER = 'htcleofmready892.inl'
INC = '#include "' + HELPER + '"\n'
EDITS = (
    ('#include <e32base.h>\n#undef private\n',
     '#include <e32base.h>\n#include <coemain.h> //892 visibility only; no header/layout edits\n#undef private\n' + INC),
    ('    const TUint32 htcleoSid = RProcess().SecureId().iId;\n',
     '    const TUint32 htcleoSid = RProcess().SecureId().iId;\n'
     '    if (htcleoSid == 0x101f84ebu)\n'
     '        {\n'
     '        HtcleoFmReadySample(aScheduler);\n'
     '        return;\n'
     '        }\n'),
)

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('892 anchor drift ' + repr(old))
    return text.replace(old, new, 1)

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong892 source')
    if INC in text:
        for old, new in reversed(EDITS):
            text = once(text, new, old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact891 ready observer source')
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
        raise ValueError('892 inverse')
    if not a.restore:
        if transform(new, path.name) != new:
            raise ValueError('892 idempotence')
        (a.root / REL / HELPER).write_bytes(
            (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / HELPER).read_bytes())
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_FILEMANAGER_READY=' + ('restored' if a.restore else
          'FileManager-postwait-candidate32-walk128-FMREADY256-no-dispatch'))

if __name__ == '__main__':
    main()
