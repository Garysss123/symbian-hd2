#!/usr/bin/env python3
"""874: preserve missing optional icon-name result without server unwinding."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/appsupport/appfw/apparchitecture/apserv/APSSES.CPP')
BASE_SHA = '123148d2e48d5c9ab1c3dae9983f9ef4e3f49342c1ac1125cde4948d701f3233'
MARKER = 'HTCLEO_APPARC_EMPTY_ICON_NAME_874'
OLD = '\t\tif (iconFileName.Length() == 0)\n\t\t\tUser::Leave(KErrNotFound);\n'
NEW = '''\t\tif (iconFileName.Length() == 0)
\t\t\t{
\t\t\t// HTCLEO_APPARC_EMPTY_ICON_NAME_874
\t\t\t// An app may legitimately have no separate icon file. Preserve -1
\t\t\t// for the caller's existing fallback without unwinding the server.
\t\t\t// No per-icon file log: repeated misses must not add IO pressure.
\t\t\taMessage.Complete(KErrNotFound);
\t\t\treturn;
\t\t\t}
'''
POLICY = 'IconFileName-empty-native-Complete-NotFound-no-unwind-no-new-IO-no-style-or-other-error-change'


def transform(text, restore=False):
    if MARKER in text:
        if text.count(NEW) != 1:
            raise ValueError('partial874 empty icon-name patch')
        text = text.replace(NEW, OLD, 1)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('874 requires exact873 AppArc session source')
    if restore:
        return text
    if text.count(OLD) != 1:
        raise ValueError('874 icon-name anchor drift')
    return text.replace(OLD, NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root/REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('874 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_APPARC_EMPTY_ICON_NAME=' + ('restored' if a.restore else POLICY))
