#!/usr/bin/env python3
"""796: retain only a diagnostic RThread handle across the existing action TRAP."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ACTION = runpy.run_path(str(HERE / 'apply-htcleo-mcs-action-frontier.py'))
REL = ACTION['REL']
NAME = 'mcsexecuteaction.cpp'
BASE = '89ad41481e8221dbb70d98c15f1573c66f349ada34eb172fe94268afec217536'
INC = '#include "htcleomcsserverwatch.inl"\n'
BEFORE = '''    //796: observer errors never replace the original action result.
    const TInt htcleoObservedItem = iItemId;
    const TBool htcleoObserveServer = err == KErrNone && htcleoObservedItem == 13 &&
        RProcess().SecureId().iId == 0x101f4cd2u;
    RThread htcleoServerThread;
    TUint32 htcleoServerPid = 0;
    TInt htcleoServerCandidates = 0;
    TInt htcleoServerOpen = KErrNotSupported;
    if (htcleoObserveServer)
        {
        htcleoServerOpen = HtcleoOpenMenuServerThread(htcleoServerThread,
            htcleoServerPid, htcleoServerCandidates);
        HtcleoMcsActionLog(0x2d00u, htcleoServerOpen, htcleoObservedItem,
            (TUint32)htcleoServerCandidates);
        if (htcleoServerOpen == KErrNone)
            {
            HtcleoMcsActionLog(0x2d01u, (TInt)htcleoServerThread.Id().Id(),
                htcleoObservedItem, htcleoServerPid);
            HtcleoMenuServerSnapshot(htcleoServerThread, htcleoServerPid,
                htcleoObservedItem, EFalse);
            }
        }
'''
AFTER = '''    if (htcleoObserveServer && htcleoServerOpen == KErrNone)
        HtcleoMenuServerSnapshot(htcleoServerThread, htcleoServerPid,
            htcleoObservedItem, ETrue);
    // Close before NotifyRequestResult can delete this action and its callback.
    htcleoServerThread.Close();
'''


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('server watch anchor changed: ' + repr(old))
    return text.replace(old, new, 1)


def transform(text, restore=False):
    if INC in text:
        text = once(text, INC, '')
        text = once(text, BEFORE, '')
        text = once(text, AFTER, '')
    elif 'htcleoObserveServer' in text or 'HtcleoMenuServerSnapshot' in text:
        raise ValueError('partial server watch')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE:
        if restore and hashlib.sha256(ACTION['transform'](text, NAME).encode('latin-1')).hexdigest() == BASE:
            return text
        raise ValueError('server watch base is not exact795 action')
    if not restore:
        text = once(text, ACTION['INC'], ACTION['INC'] + INC)
        enter = '    HtcleoMcsActionLog(0x2830u, err, iItemId, 0u);\n'
        leave = '    HtcleoMcsActionLog(0x2831u, err, iItemId, 0u);\n'
        text = once(text, enter, enter + BEFORE)
        text = once(text, leave, AFTER + leave)
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL / NAME
    old = path.read_text(encoding='latin-1')
    new = transform(old, a.restore)
    if not a.restore and (transform(new) != new or transform(new, True) != transform(old, True)):
        raise ValueError('server watch must be reversible/idempotent')
    if old != new:
        path.write_text(new, encoding='latin-1')
    if not a.restore:
        asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsserverwatch.inl'
        (path.parent / asset.name).write_text(asset.read_text())
    print('HTCLEO_MCS_SERVER_EXIT_WATCH=' + ('restored' if a.restore else 'caller-item13-unique-menu-thread-before-after-native-action-no-wait'))


if __name__ == '__main__':
    main()
