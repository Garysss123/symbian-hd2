#!/usr/bin/env python3
"""800: single-plugin recovery/control for799 UI spin; preserve799 MCS isolation."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/homescreensrv/menucontentsrv')
LAUNCH=runpy.run_path(str(HERE/'apply-htcleo-menu-launch-frontier.py'))
BASE={
    'handlersrc/menuapphandler.cpp':'c8a8ae96f883625c690b616a0ac1c755f2bee237905034918f500f771c8b1a11',
    'handlerinc/menuapphandler.h':'226c4c558eb0697e3c5b10d22fc62c9a5e19912605409a8ad513be2d73c741c4',
    'handlersrc/menutasklist.cpp':'bf3234ac2273482ba52e836e2316d9876f632bafd0e936b1b9905ac88dcc89e6',
    'handlerinc/menutasklist.h':'0d7cb1e44ecc9de5fb92b0bdc9f79bd2451b1382723a029fc25e5ec9d13b8e0d',
}
OLD_LOOKUP='''TApaTask CMenuTaskList::FindRootApp(TUid aAppUid) const
    {
    TApaTask task(iWs);
    task.SetWgId(0);        // initialise task to non-existant task
    // wgId = 0 tells FindAppByUid to start looking for apps
    TInt wgId=0;
    FOREVER
        {
        CApaWindowGroupName::FindByAppUid(aAppUid, iWs, wgId);
        // KErrNotFound means that no more apps can be found
        if (wgId == KErrNotFound)
            break;
        if (IsRootWindowGroup(wgId))
            {
            // Found a root wg with the right app UID, return it.
            task.SetWgId(wgId);
            break;
            }
        }
    return task;
    }
'''
NEW_LOOKUP='#include "htcleomenutasklookup.inl"\n'
APP_EDITS=[
    ('#include "htcleomcsactiontrace.inl"\n','#include "htcleomenulaunchtrace.inl"\n'),
    ('        LaunchApplicationL( TUid::Uid( appUidNo ), aParams, viewId );\n',
     '        const TInt htcleoLaunchResult = LaunchApplicationL( TUid::Uid( appUidNo ), aParams, viewId );\n'),
    ('HtcleoMcsActionLog(0x2a06u, KErrNone,','HtcleoMcsActionLog(0x2a06u, htcleoLaunchResult,'),
    ('( iMenu, CActive::EPriorityStandard, aStatus, KErrNone );',
     '( iMenu, CActive::EPriorityStandard, aStatus, htcleoLaunchResult );'),
    ('void CMenuAppHandler::LaunchApplicationL(', 'TInt CMenuAppHandler::LaunchApplicationL('),
    ('        TApaTask task = taskList->FindRootApp( aUid );\n',
     '        TInt htcleoLookupResult = KErrNone;\n        TApaTask task = taskList->FindRootApp( aUid, htcleoLookupResult );\n'),
    ('        HtcleoMcsActionLog(0x2a24u, KErrNone, aUid.iUid, 0u);\n',
     '''        HtcleoMcsActionLog(0x2a24u, htcleoLookupResult, aUid.iUid, 0u);
        if (htcleoLookupResult != KErrNone)
            {
            CleanupStack::PopAndDestroy( &wsSession );
            return htcleoLookupResult; //800 native completed-operation reports this error
            }
'''),
    ('        HtcleoMcsActionLog(0x2a3au, KErrNone, aUid.iUid, 0u);\n        }\n    }',
     '        HtcleoMcsActionLog(0x2a3au, KErrNone, aUid.iUid, 0u);\n        }\n    return KErrNone; //800 unchanged successful launch/activation\n    }'),
]
EDITS={
    'handlersrc/menuapphandler.cpp':APP_EDITS,
    'handlerinc/menuapphandler.h':[('    void LaunchApplicationL(', '    TInt LaunchApplicationL(')],
    'handlersrc/menutasklist.cpp':[
        ('#include "menutasklist.h"\n','#include "menutasklist.h"\n#include "htcleomenulaunchtrace.inl"\n'),
        (OLD_LOOKUP,NEW_LOOKUP)],
    'handlerinc/menutasklist.h':[
        ('TApaTask FindRootApp(TUid aAppUid) const;',
         'TApaTask FindRootApp(TUid aAppUid, TInt& aResult) const; //800 error is not absence')],
}


def digest(text): return hashlib.sha256(text.encode('latin-1')).hexdigest()
def once(text,old,new):
    if text.count(old)!=1: raise ValueError('task lookup anchor changed: '+repr(old))
    return text.replace(old,new,1)


def transform(text,name,restore=False):
    edits=EDITS[name]
    if any(new in text for old,new in edits):
        for old,new in reversed(edits): text=once(text,new,old)
    if digest(text)!=BASE[name]:
        if restore and name=='handlersrc/menuapphandler.cpp' and digest(LAUNCH['transform'](text))==BASE[name]:
            return text
        raise ValueError('task lookup requires exact799 plugin source: '+name)
    if not restore:
        for old,new in edits: text=once(text,old,new)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    pending=[]
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if not a.restore and (transform(new,name)!=new or transform(new,name,True)!=transform(old,name,True)):
            raise ValueError('lookup inverse/idempotence failed')
        pending.append((path,old,new))
    for path,old,new in pending:
        if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        for name in ('htcleomenulaunchtrace.inl','htcleomenutasklookup.inl'):
            asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/name
            (a.root/REL/'handlersrc'/name).write_bytes(asset.read_bytes())
    print('HTCLEO_MENU_TASK_LOOKUP='+('restored' if a.restore else 'bounded-native-query-invalid-result-error-MLAUNCH128-control'))

if __name__=='__main__':main()
