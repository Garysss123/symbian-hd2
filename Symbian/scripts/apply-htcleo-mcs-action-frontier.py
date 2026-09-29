#!/usr/bin/env python3
"""792: observe existing async menu action; leave all dispatch/ownership intact."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/homescreensrv/homescreensrv_plat/sapi_menucontent/mcsservice/src')
INC = '#include "htcleomcsactiontrace.inl"\n'
BASE = {
    'mcsservice.cpp': '03f1f49c07619f0593e9bd5cf8a25f04fe86deac998ae61fa55e7ab104d2dcbc',
    'mcsexecuteaction.cpp': '67991987fdcd776645041c7eaf7dee9597b82d1babe1640e5f367ba4909b0e88',
}
SERVICE = [
    ('\tCMCSExecuteAction* executeAO = CMCSExecuteAction::NewL(',
     '    HtcleoMcsActionLog(0x2800u, aAction.Length(), aItemId, HtcleoMcsActionTag(aAction));\n', False),
    ('\tCleanupStack::PushL( executeAO );\n',
     '    HtcleoMcsActionLog(0x2801u, KErrNone, aItemId, executeAO ? 1u : 0u);\n', True),
    ('\tCleanupStack::Pop(executeAO);\n',
     '    HtcleoMcsActionLog(0x2802u, KErrNone, aItemId, 0u);\n', True),
    ('\texecuteAO->ExecuteActionL( aItemId, aAction);\n',
     '    HtcleoMcsActionLog(0x2803u, KErrNone, aItemId, 0u);\n', True),
]
ACTION = [
    ('    ActivateRequest( KErrNone );\n',
     '    HtcleoMcsActionLog(0x2810u, KErrNone, aItemId, (TUint32)iAction.Length());\n', False),
    ('    ActivateRequest( KErrNone );\n',
     '    HtcleoMcsActionLog(0x2811u, iStatus.Int(), aItemId, 0u);\n', True),
    ('    CMenuItem* item = CMenuItem::OpenL( iMCS, aItemId );\n',
     '    HtcleoMcsActionLog(0x2820u, KErrNone, aItemId, (TUint32)aAction.Length());\n', False),
    ('\tCleanupStack::PushL( item );\n',
     '    HtcleoMcsActionLog(0x2821u, KErrNone, aItemId, item ? 1u : 0u);\n', True),
    ('\tCMCSMenuOpWatcher* watcherAO =  CMCSMenuOpWatcher::NewL(',
     '    HtcleoMcsActionLog(0x2822u, KErrNone, aItemId, 0u);\n', False),
    ('\tCleanupStack::PushL( watcherAO );\n',
     '    HtcleoMcsActionLog(0x2823u, KErrNone, aItemId, watcherAO ? 1u : 0u);\n', True),
    ('\tiOperationManager.AddL( watcherAO );\n',
     '    HtcleoMcsActionLog(0x2824u, KErrNone, aItemId, 0u);\n', True),
    ('\tCMenuOperation* operation = item->HandleCommandL(',
     '    HtcleoMcsActionLog(0x2825u, KErrNone, aItemId, 0u);\n', False),
    ('\twatcherAO->Watch( *operation );\n',
     '    HtcleoMcsActionLog(0x2826u, KErrNone, aItemId, operation ? 1u : 0u);\n', False),
    ('\twatcherAO->Watch( *operation );\n',
     '    HtcleoMcsActionLog(0x2827u, KErrNone, aItemId, 0u);\n', True),
    ('\tCleanupStack::PopAndDestroy( item );\n',
     '    HtcleoMcsActionLog(0x2828u, KErrNone, aItemId, 0u);\n', True),
    ('\tTInt err = iStatus.Int();\n',
     '    HtcleoMcsActionLog(0x2830u, err, iItemId, 0u);\n', True),
    ('    if(err != KErrNone)\n',
     '    HtcleoMcsActionLog(0x2831u, err, iItemId, 0u);\n', False),
    ('    iOperationManager.Remove( this );',
     '    HtcleoMcsActionLog(0x2840u, aReason, iItemId, iCallback ? 1u : 0u);\n', False),
    ('\tNotifyRequestResult( aStatus );\n',
     '    HtcleoMcsActionLog(0x2841u, aStatus, iItemId, 0u);\n', False),
    ('    NotifyRequestResult( aError );\n',
     '    HtcleoMcsActionLog(0x2842u, aError, iItemId, 0u);\n', False),
]


def transform(text, name, restore=False):
    additions = SERVICE if name == 'mcsservice.cpp' else ACTION
    if INC in text:
        if text.count(INC) != 1:
            raise ValueError('duplicate action witness include')
        text = text.replace(INC, '', 1)
        for _, addition, _ in additions:
            if text.count(addition) != 1:
                raise ValueError('partial action witness')
            text = text.replace(addition, '', 1)
    elif 'HtcleoMcsAction' in text:
        raise ValueError('unpaired action witness')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('original791 action source drift: ' + name)
    if not restore:
        anchor = '#include "mcsoperationmanager.h"\n' if name == 'mcsexecuteaction.cpp' else '#include "mcsorganizeimpl.h"\n'
        if text.count(anchor) != 1:
            raise ValueError('action include anchor changed')
        text = text.replace(anchor, anchor + INC, 1)
        for anchor, addition, after in additions:
            if text.count(anchor) != 1:
                raise ValueError('action checkpoint anchor changed: ' + repr(anchor))
            text = text.replace(anchor, anchor + addition if after else addition + anchor, 1)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--restore', action='store_true')
    a = parser.parse_args()
    pending = []
    for name in BASE:
        path = a.root / REL / name
        old = path.read_text(encoding='latin-1')
        new = transform(old, name, a.restore)
        if not a.restore and (transform(new, name) != new or transform(new, name, True) != transform(old, name, True)):
            raise ValueError('action trace must be reversible/idempotent')
        pending.append((path, old, new))
    for path, old, new in pending:
        if old != new:
            path.write_text(new, encoding='latin-1')
    if not a.restore:
        asset = Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsactiontrace.inl'
        (a.root / REL / asset.name).write_text(asset.read_text())
    print('HTCLEO_MCS_ACTION_FRONTIER=' + ('restored' if a.restore else 'async-action-only-original-dispatch-first64-no-flush'))


if __name__ == '__main__':
    main()
