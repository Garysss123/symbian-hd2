#!/usr/bin/env python3
"""888: extend only the existing first-focus diagnostic selector to FileManager."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/uifw/AvKon/src')
BASE = {'AknAppUi.cpp': '4dc7473f39941e05416191cf5346a22902a3b2f61ee91700bd1a04f236bcbe54'}
ORIGINAL = 'htcleogsfocustrace.inl'
HELPER = 'htcleofmfocus888.inl'
WRITER = 'htcleofmfocuswriter888.inl'
ORIGINAL_SHA = '267c36b10e38b6115f318926143d4b203b7bc80adc9eddba7023994c6b1b25d3'
OLD = 'return aSid == 0x100058ecu && aEvent == EEventFocusGained'
NEW = 'return (aSid == 0x100058ecu || aSid == 0x101f84ebu) && aEvent == EEventFocusGained'
WRITE_ENTRY = 'static void HtcleoGsFocusWrite(TBool aEnabled, TUint32 aStage, TInt aResult, TUint32 aDetail)\n    {\n'
FM_ROUTE = '''    if (aEnabled && RProcess().SecureId().iId == 0x101f84ebu)
        {
        HtcleoFmFocusWrite(aStage, aResult, aDetail);
        return;
        }
'''

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('888 anchor drift ' + repr(old))
    return text.replace(old, new, 1)

def derive_helper(raw, writer):
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError('original GS focus helper drift')
    text = raw.decode('latin-1').replace('\r\n', '\n')
    text = once(text, OLD, NEW)
    text = once(text, WRITE_ENTRY, WRITE_ENTRY + FM_ROUTE)
    return writer + b'\n' + text.encode('latin-1')

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong888 source')
    old = '#include "' + ORIGINAL + '"'
    new = '#include "' + HELPER + '"'
    if new in text:
        text = once(text, new, old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact887 AppUi source')
    return text if restore else once(text, old, new)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL / 'AknAppUi.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, 'AknAppUi.cpp', a.restore)
    if transform(new, 'AknAppUi.cpp', True) != transform(old, 'AknAppUi.cpp', True):
        raise ValueError('888 inverse')
    if not a.restore:
        assets = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics'
        original = (assets / ORIGINAL).read_bytes()
        if (a.root / REL / ORIGINAL).read_bytes() != original:
            raise ValueError('SDK original helper changed')
        raw = derive_helper(original, (assets / WRITER).read_bytes())
        (a.root / REL / HELPER).write_bytes(raw)
        if transform(new, 'AknAppUi.cpp') != new:
            raise ValueError('888 idempotence')
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_FILEMANAGER_FOCUS=' + ('restored' if a.restore else
          'FileManager-first-FocusGained-existing16-boundaries-private-diagnostic-bit5-FMFOCUS32-native-policy'))

if __name__ == '__main__':
    main()
