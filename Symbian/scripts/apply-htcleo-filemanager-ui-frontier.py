#!/usr/bin/env python3
"""889: bounded native FileManager first-redraw/view-activation witnesses."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
BASE = {
    'COEPRIV.CPP': '71d5c48296a6a4ff07d35640f1d18bb11f9b0fe3e638b3f44f14676459bc758c',
    'coevwman.cpp': 'b5dda9c4b811c90fee6a1dffc56f5a084fe01cb76adc13f3bbe545b11ad8bc6d',
}
HELPERS = {
    'htcleogsredrawtrace.inl': ('htcleofmredraw889.inl', '2a54161067071d0365d21e36ee6590a9bf7f45f271dc34513ab0219260566783'),
    'htcleohomevieweventtrace.inl': ('htcleofmview889.inl', 'eaaba2d0b511b3cc4d2b9aa1a246a18dfb3596051172ea0919df02854f8fb140'),
}
INCLUDES = dict(zip(BASE, HELPERS))
WRITER = 'htcleofmuiwriter889.inl'
OLD_REDRAW = 'return aSid == 0x100058ecu && aFirstRedraw;'
NEW_REDRAW = 'return (aSid == 0x100058ecu || aSid == 0x101f84ebu) && aFirstRedraw;'
OLD_VIEW = 'return aSid == 0x100058ecu || aSid == 0x102750f0u;'
NEW_VIEW = 'return aSid == 0x100058ecu || aSid == 0x102750f0u || aSid == 0x101f84ebu;'
ROUTE = '''    if (RProcess().SecureId().iId == 0x101f84ebu)
        {
        HtcleoFmUiWrite(aStage, aResult, aDetail);
        return;
        }
'''

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('889 anchor drift ' + repr(old))
    return text.replace(old, new, 1)

def derive_helper(raw, name, writer):
    if name not in HELPERS or hashlib.sha256(raw).hexdigest() != HELPERS[name][1]:
        raise ValueError('original UI observer drift ' + name)
    text = raw.decode('latin-1').replace('\r\n', '\n')
    if name == 'htcleogsredrawtrace.inl':
        text = once(text, OLD_REDRAW, NEW_REDRAW)
        anchor = '    if (!HtcleoGsRedrawTake(aCount, aStage)) return;\n'
    else:
        text = once(text, OLD_VIEW, NEW_VIEW)
        anchor = '    if (!HtcleoGsViewEventTake(aCount, aStage)) return;\n'
    text = once(text, anchor, anchor + ROUTE)
    return writer + b'\n' + text.encode('latin-1')

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong889 source')
    original = INCLUDES[name]
    old = '#include "' + original + '"'
    new = '#include "' + HELPERS[original][0] + '"'
    if new in text:
        text = once(text, new, old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact888 UI source ' + name)
    return text if restore else once(text, old, new)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    changes = []
    for name in BASE:
        path = a.root / REL / name
        old = path.read_text(encoding='latin-1')
        new = transform(old, name, a.restore)
        if transform(new, name, True) != transform(old, name, True):
            raise ValueError('889 inverse')
        if not a.restore and transform(new, name) != new:
            raise ValueError('889 idempotence')
        changes.append((path, old, new))
    if not a.restore:
        assets = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics'
        writer = (assets / WRITER).read_bytes()
        pending = []
        for original, (derived, _) in HELPERS.items():
            raw = (assets / original).read_bytes()
            if (a.root / REL / original).read_bytes() != raw:
                raise ValueError('SDK original helper changed ' + original)
            pending.append((a.root / REL / derived, derive_helper(raw, original, writer)))
        for path, raw in pending:
            path.write_bytes(raw)
    for path, old, new in changes:
        if old != new:
            path.write_text(new, encoding='latin-1')
    print('HTCLEO_FILEMANAGER_UI=' + ('restored' if a.restore else
          'FileManager-first-redraw-view-boundaries-FMUI64-no-native-policy-change'))

if __name__ == '__main__':
    main()
