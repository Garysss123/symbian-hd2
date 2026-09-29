#!/usr/bin/env python3
"""799: stop only MCS's failed AppArc subscription before its -15 Leave/requeue."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = 'sf/mw/homescreensrv/menucontentsrv'
BASE = {
    'srvsrc/menusrvappscanner.cpp': 'bb61f9247498a1338ca5de8252c884e786637b37a4e0643435b2f47a4777a42b',
    'srvinc/menusrvappscanner.h': '3b742aba3ecf284bbd8e13a1e74728a4a709e6abaf0e12a8d4d33b1aec43ee93',
}
INCLUDE = '#include "htcleomcsactiontrace.inl"\n#include "htcleomcsapplistnotifier.inl"\n'
OLD_FACTORY = 'iNotifier = CApaAppListNotifier::NewL('
NEW_FACTORY = 'iNotifier = CHtcleoMcsAppListNotifier::NewL('
OLD_MEMBER = '    CApaAppListNotifier* iNotifier; ///< Change notifier. Own.\n'
NEW_MEMBER = '    CActive* iNotifier; ///<799 local notifier, virtual destructor; pointer layout unchanged.\n'


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('notifier anchor changed: ' + repr(old))
    return text.replace(old, new, 1)


def transform(text, name, restore=False):
    if name.endswith('.cpp'):
        if INCLUDE in text:
            text = once(text, INCLUDE, '')
            text = once(text, NEW_FACTORY, OLD_FACTORY)
        elif NEW_FACTORY in text or 'htcleomcsapplistnotifier.inl' in text:
            raise ValueError('partial notifier layer')
    elif NEW_MEMBER in text:
        text = once(text, NEW_MEMBER, OLD_MEMBER)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('notifier requires exact798 scanner source: ' + name)
    if restore:
        return text
    if name.endswith('.cpp'):
        text = once(text, '#include "menuutil.h"\n', '#include "menuutil.h"\n' + INCLUDE)
        return once(text, OLD_FACTORY, NEW_FACTORY)
    return once(text, OLD_MEMBER, NEW_MEMBER)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    pending = []
    for name in BASE:
        path = args.root / REL / name
        old = path.read_text(encoding='latin-1')
        new = transform(old, name, args.restore)
        if not args.restore and (transform(new, name) != new or transform(new, name, True) != transform(old, name, True)):
            raise ValueError('notifier inverse/idempotence failed')
        pending.append((path, old, new))
    for path, old, new in pending:
        if old != new:
            path.write_text(new, encoding='latin-1')
    if not args.restore:
        for name in ('htcleomcsactiontrace.inl', 'htcleomcsapplistnotifier.inl'):
            asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / name
            (args.root / REL / 'srvsrc' / name).write_bytes(asset.read_bytes())
    print('HTCLEO_MCS_APPLIST_NOTIFIER=' + ('restored' if args.restore else 'local-native-positive-events-stop-dead-subscription-minus15'))


if __name__ == '__main__':
    main()
