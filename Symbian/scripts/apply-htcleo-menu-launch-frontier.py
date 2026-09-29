#!/usr/bin/env python3
"""793: finite observations in the existing app handler, no launch policy change."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/homescreensrv/menucontentsrv/handlersrc')
NAME = 'menuapphandler.cpp'
BASE_SHA = '40fa727cb90c4b4bbd5df830e59540ec52808c413c22bd11df09c20519959fe5'
INC = '''#include "htcleomcsactiontrace.inl"

// Return the native result unchanged, before the original LeaveIfError.
static TInt HtcleoMenuLaunchResult(TUint32 aStage, TInt aResult, TUid aUid)
    {
    HtcleoMcsActionLog(aStage, aResult, aUid.iUid, 0u);
    return aResult;
    }
'''
ADDITIONS = [
    ('    if ( aCommand == KMenuCmdOpen() && aItem.Type() == KMenuTypeApp() )\n',
     '    HtcleoMcsActionLog(0x2a00u, aCommand.Length(), aItem.Id(), 0u);\n', False),
    ('        TPtrC url = aItem.GetAttributeL( KMenuAttrUid(), attrExists );\n',
     '        HtcleoMcsActionLog(0x2a02u, attrExists, aItem.Id(), (TUint32)url.Length());\n', True),
    ('        TInt err = MenuUtils::GetTUint( url, appUidNo );\n',
     '        HtcleoMcsActionLog(0x2a03u, err, aItem.Id(), err == KErrNone ? appUidNo : 0u);\n', True),
    ('        TPtrC view = aItem.GetAttributeL( KMenuAttrView(), attrExists );\n',
     '        HtcleoMcsActionLog(0x2a04u, attrExists, aItem.Id(), (TUint32)view.Length());\n', True),
    ('        LaunchApplicationL( TUid::Uid( appUidNo ), aParams, viewId );\n',
     '        HtcleoMcsActionLog(0x2a05u, viewId, (TInt)appUidNo, 0u);\n', False),
    ('        LaunchApplicationL( TUid::Uid( appUidNo ), aParams, viewId );\n',
     '        HtcleoMcsActionLog(0x2a06u, KErrNone, (TInt)appUidNo, 0u);\n', True),
    ('    if ( aViewId > 0 && iEikEnv )\n',
     '    HtcleoMcsActionLog(0x2a10u, aViewId, aUid.iUid, iEikEnv ? 1u : 0u);\n', False),
    ('        iEikEnv->EikAppUi()->ActivateViewL( view );\n',
     '        HtcleoMcsActionLog(0x2a11u, aViewId, aUid.iUid, 0u);\n', False),
    ('        iEikEnv->EikAppUi()->ActivateViewL( view );\n',
     '        HtcleoMcsActionLog(0x2a12u, KErrNone, aUid.iUid, 0u);\n', True),
    ('        RWsSession wsSession;\n',
     '        HtcleoMcsActionLog(0x2a20u, KErrNone, aUid.iUid, 0u);\n', True),
    ('        CMenuTaskList* taskList = CMenuTaskList::NewL( wsSession );',
     '        HtcleoMcsActionLog(0x2a22u, KErrNone, aUid.iUid, 0u);\n', False),
    ('        TApaTask task = taskList->FindRootApp( aUid );\n',
     '        HtcleoMcsActionLog(0x2a23u, KErrNone, aUid.iUid, 0u);\n', False),
    ('        delete taskList;\n',
     '        HtcleoMcsActionLog(0x2a24u, KErrNone, aUid.iUid, 0u);\n', True),
    ('            task.BringToForeground();\n',
     '            HtcleoMcsActionLog(0x2a25u, KErrNone, aUid.iUid, 0u);\n', False),
    ('            task.BringToForeground();\n',
     '            HtcleoMcsActionLog(0x2a26u, KErrNone, aUid.iUid, 0u);\n', True),
    ('            TApaAppInfo appInfo;\n',
     '            HtcleoMcsActionLog(0x2a30u, KErrNone, aUid.iUid, 0u);\n', False),
    ('            User::LeaveIfError( appArcSession.GetAppInfo( appInfo, aUid ) );\n',
     '            HtcleoMcsActionLog(0x2a32u, KErrNone, aUid.iUid, 0u);\n', False),
    ('            User::LeaveIfError( appArcSession.GetAppCapability( capabilityBuf, aUid ) );\n',
     '            HtcleoMcsActionLog(0x2a34u, KErrNone, aUid.iUid, 0u);\n', False),
    ('            CApaCommandLine* cmdLine = CApaCommandLine::NewLC();\n',
     '            HtcleoMcsActionLog(0x2a36u, KErrNone, aUid.iUid, (TUint32)appName.Length());\n', False),
    ('            cmdLine->SetTailEndL( aParam );\n',
     '            HtcleoMcsActionLog(0x2a38u, KErrNone, aUid.iUid, 0u);\n', True),
    ('        CleanupStack::PopAndDestroy( &wsSession );\n',
     '        HtcleoMcsActionLog(0x2a3au, KErrNone, aUid.iUid, 0u);\n', True),
]
RESULTS = [
    ('wsSession.Connect()', 'HtcleoMenuLaunchResult(0x2a21u, wsSession.Connect(), aUid)'),
    ('appArcSession.Connect()', 'HtcleoMenuLaunchResult(0x2a31u, appArcSession.Connect(), aUid)'),
    ('appArcSession.GetAppInfo( appInfo, aUid )', 'HtcleoMenuLaunchResult(0x2a33u, appArcSession.GetAppInfo( appInfo, aUid ), aUid)'),
    ('appArcSession.GetAppCapability( capabilityBuf, aUid )', 'HtcleoMenuLaunchResult(0x2a35u, appArcSession.GetAppCapability( capabilityBuf, aUid ), aUid)'),
    ('appArcSession.StartApp( *cmdLine )', 'HtcleoMenuLaunchResult(0x2a39u, appArcSession.StartApp( *cmdLine ), aUid)'),
]


def transform(text, restore=False):
    if INC in text:
        if text.count(INC) != 1:
            raise ValueError('duplicate handler witness include')
        text = text.replace(INC, '', 1)
        for _, addition, _ in ADDITIONS:
            if text.count(addition) != 1:
                raise ValueError('partial handler witness')
            text = text.replace(addition, '', 1)
        for old, new in RESULTS:
            if text.count(new) != 1:
                raise ValueError('partial native result witness')
            text = text.replace(new, old, 1)
    elif 'HtcleoMenuLaunch' in text or 'HtcleoMcsAction' in text:
        raise ValueError('unpaired handler witness')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE_SHA:
        raise ValueError('original792 handler source drift')
    if not restore:
        anchor = '#include <vwsdef.h>\n'
        if text.count(anchor) != 1:
            raise ValueError('handler include anchor changed')
        text = text.replace(anchor, anchor + INC, 1)
        for anchor, addition, after in ADDITIONS:
            if text.count(anchor) != 1:
                raise ValueError('handler checkpoint anchor changed: ' + repr(anchor))
            text = text.replace(anchor, anchor + addition if after else addition + anchor, 1)
        for old, new in RESULTS:
            if text.count(old) != 1:
                raise ValueError('native call must be evaluated once: ' + old)
            text = text.replace(old, new, 1)
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
        raise ValueError('handler observation must be reversible and idempotent')
    if old != new:
        path.write_text(new, encoding='latin-1')
    if not a.restore:
        asset = Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleomcsactiontrace.inl'
        (path.parent / asset.name).write_text(asset.read_text())
    print('HTCLEO_MENU_LAUNCH_FRONTIER=' + ('restored' if a.restore else 'native-handler-results-unchanged-shared-first64'))


if __name__ == '__main__':
    main()
