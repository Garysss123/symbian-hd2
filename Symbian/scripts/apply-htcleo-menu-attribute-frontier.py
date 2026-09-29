#!/usr/bin/env python3
"""794: observe item13 UID IPC client/session/engine without changing results."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/homescreensrv/menucontentsrv')
BASE = {
    'src/menu.cpp': '6c3d4acd799f3f73179da745a6a0c1da062b370737f57cc0a99b99b9d7c05c03',
    'srvsrc/menusrvsession.cpp': 'c0985285cdc9dddaff1850c854256287255b8e75aabebf4d0e51dba2d267dbf6',
    'srvsrc/menusrveng.cpp': '82ddf562a6a0781c0da7e52f5cc120f13debaf19b84e680e87aa41ad23bf39c8',
}
INC = '#include "htcleomcsactiontrace.inl"\n'
WRAPPER = '''// Native IPC result is observed once and returned unchanged.
static TInt HtcleoMenuAttributeResult(TBool aTrace, TInt aResult, TInt aId)
    {
    if (aTrace) HtcleoMcsActionLog(0x2b03u, aResult, aId, 0u);
    return aResult;
    }
'''
SCOPES = {
    'src/menu.cpp': ('HBufC* RMenu::GetAttributeL(', 'void RMenu::GetAttributeListL('),
    'srvsrc/menusrvsession.cpp': ('        case EMenuItemGetAttribute:\n', '        case EMenuItemGetAttributeList:\n'),
    'srvsrc/menusrveng.cpp': ('void CMenuSrvEng::GetAttributeL(\n', '// CMenuSrvEng::GetRunningAppsL()'),
}
INCLUDES = {
    'src/menu.cpp': '#include "menuhandlereng.h"\n',
    'srvsrc/menusrvsession.cpp': '#include <s32strm.h>\n',
    'srvsrc/menusrveng.cpp': '#include "menusrveng.h"\n',
}


def trace(stage, result, item, detail='0u', indent='    '):
    return indent + f'if (htcleoUidTrace) HtcleoMcsActionLog(0x{stage:x}u, {result}, {item}, {detail});\n'


ADDITIONS = {
    'src/menu.cpp': [
        ('    RBuf ptr;\n', '''    // Diagnostic scope only: the observed Settings item, not a per-app fix.
    const TBool htcleoUidTrace = aId == 13 &&
        RProcess().SecureId().iId == 0x101f4cd2u && aAttrName == KMenuAttrUid();
''' + trace(0x2b00, 'KErrNone', 'aId', '(TUint32)Handle()'), False),
        ('    ptr.CreateL(KMenuMaxAttrValueLen);\n', trace(0x2b01, 'KErrNone', 'aId', '(TUint32)ptr.MaxLength()'), True),
        ('    TIpcArgs args( aId, &aAttrName, &attrExists, &ptr );\n', trace(0x2b02, 'KErrNone', 'aId', '(TUint32)aAttrName.Length()'), True),
    ],
    'srvsrc/menusrvsession.cpp': [
        ('            TInt id = aMessage.Int0();\n', '''            const TBool htcleoUidTrace = id == 13 &&
                aMessage.SecureId().iId == 0x101f4cd2u;
''' + trace(0x2b10, 'KErrNone', 'id', 'iSharedEng ? 1u : 0u', '            '), True),
        ('            name.CreateL( aMessage.GetDesLengthL( KParamIndAttrName ) );\n', trace(0x2b11, 'KErrNone', 'id', '(TUint32)name.MaxLength()', '            '), True),
        ('            aMessage.ReadL( KParamIndAttrName, name );\n', trace(0x2b12, 'KErrNone', 'id', '(TUint32)name.Length()', '            '), True),
        ('        \tattrVal.CreateL(KMenuMaxAttrValueLen);\n', trace(0x2b13, 'KErrNone', 'id', '(TUint32)attrVal.MaxLength()', '            '), True),
        ('        \tiSharedEng->GetAttributeL( id, name, attrExists, attrVal);\n', trace(0x2b14, 'KErrNone', 'id', '0u', '            '), False),
        ('        \tiSharedEng->GetAttributeL( id, name, attrExists, attrVal);\n', trace(0x2b15, 'attrExists', 'id', '(TUint32)attrVal.Length()', '            '), True),
        ('            aMessage.WriteL( KParamIndAttrEx, attrExistsBuf );\n', trace(0x2b16, 'KErrNone', 'id', '0u', '            '), True),
        ('                aMessage.WriteL( KParamIndAttrVal, attrVal );\n', trace(0x2b17, 'KErrNone', 'id', '(TUint32)attrVal.Length()', '                '), True),
        ('            CleanupStack::PopAndDestroy( &name );\n', trace(0x2b18, 'KErrNone', 'id', '0u', '            '), True),
    ],
    'srvsrc/menusrveng.cpp': [
        ('    TBool dummy;\n', '''    const TBool htcleoUidTrace = aId == 13 && aAttrName == KMenuAttrUid();
''' + trace(0x2b20, 'KErrNone', 'aId', 'iEng ? 1u : 0u'), False),
        ('    aAttrExists = iEng->ObjectL(aId).FindAttribute( aAttrName, val, dummy);\n', trace(0x2b22, 'aAttrExists', 'aId', '(TUint32)val.Length()'), True),
        ('        aAttrExists = iCacheHandler->iAttrCache.Find( aId, aAttrName, aAttrVal );\n', trace(0x2b23, 'KErrNone', 'aId', 'iCacheHandler ? 1u : 0u', '        '), False),
        ('        aAttrExists = iCacheHandler->iAttrCache.Find( aId, aAttrName, aAttrVal );\n', trace(0x2b29, 'aAttrExists', 'aId', '(TUint32)aAttrVal.Length()', '        '), True),
        ('        aAttrVal = val;\n', trace(0x2b24, 'val.Length()', 'aId', '(TUint32)aAttrVal.MaxLength()', '        '), False),
        ('        aAttrVal = val;\n', trace(0x2b25, 'KErrNone', 'aId', '(TUint32)aAttrVal.Length()', '        '), True),
        ('    \tGetExtendedAttributesL( aId, aAttrName, aAttrExists, aAttrVal );\n', trace(0x2b26, 'KErrNone', 'aId', '0u', '        '), False),
        ('    \tGetExtendedAttributesL( aId, aAttrName, aAttrExists, aAttrVal );\n', trace(0x2b27, 'aAttrExists', 'aId', '(TUint32)aAttrVal.Length()', '        '), True),
    ],
}
REPLACES = {
    'src/menu.cpp': [
        ('SendReceive( EMenuItemGetAttribute, args )',
         'HtcleoMenuAttributeResult(htcleoUidTrace, SendReceive( EMenuItemGetAttribute, args ), aId)'),
    ],
    'srvsrc/menusrvsession.cpp': [],
    'srvsrc/menusrveng.cpp': [
        ('    aAttrExists = iEng->ObjectL(aId).FindAttribute( aAttrName, val, dummy);\n',
         '    const CMenuEngObject& htcleoAttributeObject = iEng->ObjectL(aId);\n' +
         trace(0x2b21, 'KErrNone', 'aId') +
         '    aAttrExists = htcleoAttributeObject.FindAttribute( aAttrName, val, dummy);\n'),
    ],
}


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('attribute anchor count changed: ' + repr(before))
    return text.replace(before, after, 1)


def transform(text, name, restore=False):
    if INC in text:
        text = replace_once(text, INC, '')
        if name == 'src/menu.cpp':
            text = replace_once(text, WRAPPER, '')
        for old, new in REPLACES[name]:
            text = replace_once(text, new, old)
        for _, addition, _ in ADDITIONS[name]:
            text = replace_once(text, addition, '')
    elif 'htcleoUidTrace' in text or 'HtcleoMenuAttribute' in text:
        raise ValueError('partial attribute trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('original793 MCS source drift: ' + name)
    if not restore:
        inc = INC + (WRAPPER if name == 'src/menu.cpp' else '')
        text = replace_once(text, INCLUDES[name], INCLUDES[name] + inc)
        start, end = SCOPES[name]
        left = text.index(start)
        right = text.index(end, left + len(start))
        body = text[left:right]
        for anchor, addition, after in ADDITIONS[name]:
            body = replace_once(body, anchor, anchor + addition if after else addition + anchor)
        for old, new in REPLACES[name]:
            body = replace_once(body, old, new)
        text = text[:left] + body + text[right:]
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
            raise ValueError('attribute observation must be reversible/idempotent')
        pending.append((path, old, new))
    for path, old, new in pending:
        if old != new:
            path.write_text(new, encoding='latin-1')
        if not a.restore:
            asset = Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsactiontrace.inl'
            (path.parent / asset.name).write_text(asset.read_text())
    print('HTCLEO_MENU_ATTRIBUTE_FRONTIER=' + ('restored' if a.restore else 'item13-uid-client-server-engine-native-results-shared64'))


if __name__ == '__main__':
    main()
