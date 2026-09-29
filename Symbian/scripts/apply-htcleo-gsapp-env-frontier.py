#!/usr/bin/env python3
"""808: GSApp-only routing of existing native environment checkpoints."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/commonuisupport/uikon/coresrc')
NAME = 'EIKENV.CPP'
BASE_SHA = 'd726dd2130a806b979e0bf5c99d2b62773b05e2b2980a3daa06649d20462f566'
BASE_BINARY = '07cd59cab63934c014abdf2b0bc70ad9dfaf6b004dd44f14c7f2931b5b023f52'
INC = '#include "htcleogsenvtrace.inl"\n'
ANCHOR = 'static void HtcleoEikCorePreFactoryTrace(TUint32 aStage, TInt aResult)\n'
OLD = '''    else if (sid == KHtcleoHomeScreenSid)
        {
        HtcleoEikCoreHomeScreenTrace(aStage, aResult);
        }
'''
NEW = OLD + '''    else if (sid == 0x100058ecu)
        {
        HtcleoGsEnvTrace(sid, aStage, aResult);
        }
'''


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('GSApp environment routing anchor drift')
    return text.replace(old, new, 1)


def transform(text, restore=False):
    if INC in text:
        text = once(text, INC, '')
        text = once(text, NEW, OLD)
    elif 'HtcleoGsEnvTrace(' in text:
        raise ValueError('partial GSApp environment route')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE_SHA:
        raise ValueError('EikEnv differs from exact807 source')
    if not restore:
        text = once(text, ANCHOR, INC + ANCHOR)
        text = once(text, OLD, NEW)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    path = args.root / REL / NAME
    old = path.read_text(encoding='latin-1')
    new = transform(old, args.restore)
    if not args.restore:
        if transform(new) != new or transform(new, True) != transform(old, True):
            raise ValueError('GSApp environment inverse/idempotence failed')
        source = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleogsenvtrace.inl'
        path.with_name(source.name).write_bytes(source.read_bytes())
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_GSAPP_ENV=' + ('restored' if args.restore else 'sid100058ec-existing-E300-E320-E400-E425-GSBOOT1m-no-policy-change'))


if __name__ == '__main__': main()
