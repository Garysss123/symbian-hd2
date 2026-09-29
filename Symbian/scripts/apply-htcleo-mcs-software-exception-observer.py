#!/usr/bin/env python3
"""797 terminal observer: discover exception type and retain the native panic."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
REQ = runpy.run_path(str(HERE / 'apply-htcleo-menu-request-frontier.py'))
REL = REQ['REL']
BASE = {
    'srvsrc/menusrv.cpp': '4f6ab7b7270018973ac315edd54b4bf30c452a44949ebc112861dbbb1e2fb81c',
    'srvsrc/menusrvsession.cpp': '069cec7c26f9e119334c3ff9ec59d480a62404e74f1b7f871d30b6bd22f288da',
}
INC = '#include "htcleomcssoftwareexception.inl"\n'
INSTALL = '        HtcleoInstallMcsExceptionObserver(); //797 terminal diagnostic, no startup file I/O.\n'
STATE = '    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2e00u, HtcleoMcsExceptionObserverState(), htcleoRequestItem, (TUint32)func);\n'
BEGIN = '''	const TBool htcleoCompleteTrace = aMessage.Function() == EMenuGetHdr && aMessage.Int0() == 13;
'''
COMPLETE_OLD = '''		aMessage.Complete( KErrNone );// Sync request -> complete it now.
'''
COMPLETE_NEW = '''        if (htcleoCompleteTrace) HtcleoMenuRequestLog(0x2e10u, KErrNone, 13, EMenuGetHdr);
		aMessage.Complete( KErrNone );// Sync request -> complete it now.
        if (htcleoCompleteTrace) HtcleoMenuRequestLog(0x2e11u, KErrNone, 13, EMenuGetHdr);
'''


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('software-exception anchor changed: ' + repr(old))
    return text.replace(old, new, 1)


def normalize_base(text, name):
    lower = REQ['transform'](text, name, True)
    if name in REQ['ATTR']['BASE']:
        lower = REQ['ATTR']['transform'](lower, name)
    return REQ['transform'](lower, name)


def transform(text, name, restore=False):
    if name == 'srvsrc/menusrv.cpp' and INC in text:
        text = once(text, INC, '')
        text = once(text, INSTALL, '')
        text = once(text, STATE, '')
    elif name == 'srvsrc/menusrvsession.cpp' and BEGIN in text:
        text = once(text, BEGIN, '')
        text = once(text, COMPLETE_NEW, COMPLETE_OLD)
    elif 'HtcleoInstallMcsExceptionObserver' in text or 'htcleoCompleteTrace' in text or 'HtcleoMcsExceptionObserverState' in text:
        raise ValueError('partial software-exception observer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        if restore and hashlib.sha256(normalize_base(text, name).encode('latin-1')).hexdigest() == BASE[name]:
            return text
        raise ValueError('software observer base is not exact796: ' + name)
    if not restore:
        if name == 'srvsrc/menusrv.cpp':
            anchor = '#include "htcleomenurequesttrace.inl"\n'
            text = once(text, anchor, anchor + INC)
            anchor = '        CActiveScheduler::Start(); // Start off. Exit timer will stop it.\n'
            text = once(text, anchor, INSTALL + anchor)
            anchor = '    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c00u, func, htcleoRequestItem, 0u);\n'
            text = once(text, anchor, anchor + STATE)
        else:
            start = text.index('TBool CMenuSrvSession::ServiceCapReadL(')
            end = text.index('TBool CMenuSrvSession::ServiceCapWriteL(', start)
            body = text[start:end]
            body = once(body, '\tTBool serviced = ETrue;\n', '\tTBool serviced = ETrue;\n' + BEGIN)
            body = once(body, COMPLETE_OLD, COMPLETE_NEW)
            text = text[:start] + body + text[end:]
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    pending = []
    for name in BASE:
        path = a.root / REL / name
        old = path.read_text(encoding='latin-1')
        new = transform(old, name, a.restore)
        if not a.restore and (transform(new, name) != new or transform(new, name, True) != transform(old, name, True)):
            raise ValueError('terminal observer must be reversible/idempotent')
        pending.append((path, old, new))
    for path, old, new in pending:
        if old != new:
            path.write_text(new, encoding='latin-1')
    if not a.restore:
        asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcssoftwareexception.inl'
        (a.root / REL / 'srvsrc' / asset.name).write_text(asset.read_text())
    print('HTCLEO_MCS_SOFTWARE_EXCEPTION=' + ('restored' if a.restore else 'server-no-existing-handler-capture-fixed32-restore-reraise'))


if __name__ == '__main__':
    main()
