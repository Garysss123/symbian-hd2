#!/usr/bin/env python3
"""798: replace only797's terminal recorder, preserving every normal call site."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
SOFT = runpy.run_path(str(HERE / 'apply-htcleo-mcs-software-exception-observer.py'))
REL = SOFT['REL']
NAME = 'srvsrc/menusrv.cpp'
BASE_SHA = '285c561f9e53f3b5ec89062f5a08f4d8dc083af07f4278850d0815a2cede353c'
OLD = SOFT['INC']
NEW = '#include "htcleomcsexceptionstack.inl"\n'


def transform(text, restore=False):
    if NEW in text:
        text = SOFT['once'](text, NEW, OLD)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE_SHA:
        # Build restoration may already have removed lower797/795 layers.
        if restore and OLD not in text and NEW not in text:
            SOFT['transform'](text, NAME, True)
            return text
        raise ValueError('stack observer requires exact797 server source')
    return text if restore else SOFT['once'](text, OLD, NEW)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    path = args.root / REL / NAME
    old = path.read_text(encoding='latin-1')
    new = transform(old, args.restore)
    if not args.restore and (transform(new) != new or transform(new, True) != transform(old, True)):
        raise ValueError('stack observer inverse/idempotence failed')
    if old != new:
        path.write_text(new, encoding='latin-1')
    if not args.restore:
        asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsexceptionstack.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    print('HTCLEO_MCS_EXCEPTION_STACK=' + ('restored' if args.restore else 'entry-sp-lr-bounded240-fixed1024-terminal-reraise'))


if __name__ == '__main__':
    main()
