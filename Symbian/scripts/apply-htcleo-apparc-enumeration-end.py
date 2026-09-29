#!/usr/bin/env python3
"""872: complete only normal app-enumeration EOF with the original error code."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/appsupport/appfw/apparchitecture/apserv/APSSES.CPP')
BASE_SHA = 'f287358cc832d8715fd6126702a9b945ab860a26dc3a00b21bb6829163299bcf'
MARKER = 'HTCLEO_APPARC_ENUMERATION_END_872'
OLD = '\tif (!iApaAppInfoArray.Count())\n\t\tUser::Leave(KErrNotFound);\n'
NEW = '''\tif (!iApaAppInfoArray.Count())
\t\t{
\t\t// HTCLEO_APPARC_ENUMERATION_END_872
\t\t// End of a fully populated/consumed list is a normal IPC result.
\t\t// Preserve -1 for the native client's ENoMoreAppsInList mapping;
\t\t// do not unwind through the server for this expected empty case.
\t\taMessage.Complete(KErrNotFound);
\t\tHtcleoApaServerLog(0x00001470u, KErrNotFound, 0u);
\t\treturn;
\t\t}
'''
POLICY = 'GetNextApp-empty-list-native-Complete-NotFound-not-Leave-no-other-errors-changed-1470'


def transform(text, restore=False):
    if MARKER in text:
        if text.count(NEW) != 1:
            raise ValueError('partial872 enumeration end patch')
        text = text.replace(NEW, OLD, 1)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('872 requires exact870 APSSession source')
    if restore:
        return text
    if text.count(OLD) != 1:
        raise ValueError('872 EOF anchor drift')
    return text.replace(OLD, NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('872 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_APPARC_ENUMERATION_END=' + ('restored' if a.restore else POLICY))
