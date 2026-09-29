#!/usr/bin/env python3
"""795: header/attribute request continuity; preserve native security and dispatch."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ATTR = runpy.run_path(str(HERE / 'apply-htcleo-menu-attribute-frontier.py'))
REL = ATTR['REL']
BASE = {
    'src/menu.cpp': 'b336caacc3a183b7c5345512af90842c35e1f4381ad8d7a46a9262728b7992ed',
    'srvsrc/menusrvsession.cpp': '8489be5ab4d4f460c15a3cd95389f38056045456caa1d9d89fce9eae0bbc6e1e',
    'srvsrc/menusrv.cpp': 'e570f9325939ddbae27cdaf9fd6e754d501e1e3abfe9c779e384ffd3f199447c',
}
INC = '#include "htcleomenurequesttrace.inl"\n'
HELPERS = {
    'src/menu.cpp': '''static TInt HtcleoMenuHeaderResult(TBool aTrace, TInt aResult, TInt aId, TInt aHandle)
    {
    if (aTrace) HtcleoMenuRequestLog(0x2c31u, aResult, aId, (TUint32)aHandle);
    return aResult;
    }
''',
    'srvsrc/menusrvsession.cpp': '''static TBool HtcleoMenuReadResult(TBool aTrace, TBool aResult, TInt aId, TInt aFunction)
    {
    if (aTrace) HtcleoMenuRequestLog(0x2c12u, aResult, aId, (TUint32)aFunction);
    return aResult;
    }
''',
    'srvsrc/menusrv.cpp': '',
}
SERVER_SCOPE = '''    const TInt htcleoRequestFunction = aMessage.Function();
    const TInt htcleoRequestItem = aMessage.Int0();
    const TBool htcleoRequestTrace = htcleoRequestItem == 13 &&
        (htcleoRequestFunction == EMenuGetHdr || htcleoRequestFunction == EMenuItemGetAttribute);
'''
OLD_FILTER = '''            const TBool htcleoUidTrace = id == 13 &&
                aMessage.SecureId().iId == 0x101f4cd2u;
'''
NEW_FILTER = '''            // Trace filter only: native security checks already ran unchanged.
            const TBool htcleoUidTrace = id == 13;
'''


def pairs(name):
    if name == 'src/menu.cpp':
        return [
            ('    TPckg<TMenuItem> pckg( (TMenuItem&)iData->iBuf );\n',
             '''    const TBool htcleoRequestTrace = aId == 13 && RProcess().SecureId().iId == 0x101f4cd2u;
    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c30u, EMenuGetHdr, aId, (TUint32)Handle());
    TPckg<TMenuItem> pckg( (TMenuItem&)iData->iBuf );
'''),
            ('SendReceive( EMenuGetHdr, args )',
             'HtcleoMenuHeaderResult(htcleoRequestTrace, SendReceive( EMenuGetHdr, args ), aId, Handle())'),
        ]
    if name == 'srvsrc/menusrvsession.cpp':
        return [
            ('''void CMenuSrvSession::ServiceL( const RMessage2& aMessage )
    {
''', '''void CMenuSrvSession::ServiceL( const RMessage2& aMessage )
    {
''' + SERVER_SCOPE + '''    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c10u, iEngineDead, htcleoRequestItem, (TUint32)htcleoRequestFunction);
'''),
            ('        // The rest of the functions does not work with a dead engine.\n',
             '''        if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c11u, iEngineDead, htcleoRequestItem, (TUint32)htcleoRequestFunction);
        // The rest of the functions does not work with a dead engine.
'''),
            ('ServiceCapReadL( aMessage )',
             'HtcleoMenuReadResult(htcleoRequestTrace, ServiceCapReadL( aMessage ), htcleoRequestItem, htcleoRequestFunction)'),
            ('''            TPckgBuf<TMenuItem> hdr;
            iSharedEng->Engine().GetItemL( id, hdr() );
            aMessage.WriteL( 1, hdr );
''', '''            if (id == 13) HtcleoMenuRequestLog(0x2c20u, KErrNone, id, iSharedEng ? 1u : 0u);
            TPckgBuf<TMenuItem> hdr;
            iSharedEng->Engine().GetItemL( id, hdr() );
            if (id == 13) HtcleoMenuRequestLog(0x2c21u, KErrNone, id, 0u);
            aMessage.WriteL( 1, hdr );
            if (id == 13) HtcleoMenuRequestLog(0x2c22u, KErrNone, id, 0u);
'''),
            (OLD_FILTER, NEW_FILTER),
            ('''void CMenuSrvSession::ServiceError( const RMessage2& aMessage, TInt aError )
    {
''', '''void CMenuSrvSession::ServiceError( const RMessage2& aMessage, TInt aError )
    {
''' + SERVER_SCOPE + '''    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c14u, aError, htcleoRequestItem, (TUint32)htcleoRequestFunction);
'''),
        ]
    return [
        ('    TInt func = aMsg.Function();\n', '''    TInt func = aMsg.Function();
    const TInt htcleoRequestItem = aMsg.Int0();
    const TBool htcleoRequestTrace = htcleoRequestItem == 13 &&
        (func == EMenuGetHdr || func == EMenuItemGetAttribute);
    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c00u, func, htcleoRequestItem, 0u);
'''),
        ('    return ret;\n', '''    if (htcleoRequestTrace) HtcleoMenuRequestLog(0x2c01u, (TInt)ret, htcleoRequestItem, (TUint32)func);
    return ret;
'''),
    ]


def once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('request anchor changed: ' + repr(before))
    return text.replace(before, after, 1)


def transform(text, name, restore=False):
    if INC in text:
        text = once(text, INC + HELPERS[name], '')
        for old, new in reversed(pairs(name)):
            text = once(text, new, old)
    elif 'htcleoRequestTrace' in text or 'HtcleoMenuRequestLog' in text or NEW_FILTER in text:
        raise ValueError('partial request trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        # Restore order also accepts the exact lower-layer793 state, but apply
        # requires794 installed. Unknown source is never accepted unchanged.
        if restore and name in ATTR['BASE']:
            normalized = ATTR['transform'](text, name)
            if hashlib.sha256(normalized.encode('latin-1')).hexdigest() == BASE[name]:
                return text
        raise ValueError('request base is not exact794: ' + name)
    if not restore:
        anchor = '#include "menumsg.h"\n'
        text = once(text, anchor, anchor + INC + HELPERS[name])
        for old, new in pairs(name):
            text = once(text, old, new)
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
            raise ValueError('request trace must be reversible/idempotent')
        pending.append((path, old, new))
    for path, old, new in pending:
        if old != new:
            path.write_text(new, encoding='latin-1')
        if not a.restore:
            asset = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleomenurequesttrace.inl'
            (path.parent / asset.name).write_text(asset.read_text())
    print('HTCLEO_MENU_REQUEST_FRONTIER=' + ('restored' if a.restore else 'item13-header-attribute-policy-session-original-security-shared64'))


if __name__ == '__main__':
    main()
