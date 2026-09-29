#!/usr/bin/env python3
"""881: native FileManager thread/process samples; do not change other apps."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/homescreensrv/menucontentsrv')
HELPER='htcleofmlifewatch881.inl'
BASE={
 'handlersrc/menuapphandler.cpp':'e3616a3dc5376cc539be62772881927ee20be790732468e47384f4a0f9ab0434',
 'handlerinc/menuapphandler.h':'0e05ab8d90e930ff7138f5956f2866ba901a6665dfd6972f5b70c020dc29318a',
}
EDITS={
 'handlersrc/menuapphandler.cpp':[
 ('#include "htcleomenulaunchtrace.inl"\n','#include "htcleomenulaunchtrace.inl"\n#include "'+HELPER+'"\n'),
 ('CMenuAppHandler::~CMenuAppHandler()\n    {\n','CMenuAppHandler::~CMenuAppHandler()\n    {\n    delete iHtcleoFmWatch;\n'),
 (': CMenuHandlerPlugin( aMenu )\n',': CMenuHandlerPlugin( aMenu ), iHtcleoFmWatch(NULL)\n'),
 ('            User::LeaveIfError( HtcleoMenuLaunchResult(0x2a39u, appArcSession.StartApp( *cmdLine ), aUid) );',
 '''            TInt htcleoStartResult;
            if (aUid.iUid == 0x101f84eb &&
                appName.CompareF(_L("C:\\\\sys\\\\bin\\\\FileManager.exe")) == 0)
                {
                if (!iHtcleoFmWatch) iHtcleoFmWatch = CHtcleoFmLifeWatch::New();
                htcleoStartResult = iHtcleoFmWatch ?
                    iHtcleoFmWatch->Start(appArcSession, *cmdLine) : appArcSession.StartApp(*cmdLine);
                }
            else htcleoStartResult = appArcSession.StartApp(*cmdLine);
            User::LeaveIfError( HtcleoMenuLaunchResult(0x2a39u, htcleoStartResult, aUid) );'''),
 ],
 'handlerinc/menuapphandler.h':[
 ('class CEikonEnv;','class CEikonEnv;\nclass CHtcleoFmLifeWatch;'),
 ('    CEikonEnv* iEikEnv;','    CEikonEnv* iEikEnv;\n    CHtcleoFmLifeWatch* iHtcleoFmWatch; //881 owned, cancelled in destructor'),
 ],
}
def once(text,old,new):
    if text.count(old)!=1: raise ValueError('FileManager lifetime anchor drift: '+repr(old))
    return text.replace(old,new,1)
def transform(text,name,restore=False):
    edits=EDITS[name]
    if edits[0][1] in text:
        for old,new in reversed(edits): text=once(text,new,old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('Not exact880 menu handler: '+name)
    if not restore:
        for old,new in edits: text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    pending=[]
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('inverse failed')
        if not a.restore and transform(new,name)!=new:raise ValueError('idempotence failed')
        pending.append((path,old,new))
    for path,old,new in pending:
        if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        (a.root/REL/'handlersrc'/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    print('HTCLEO_FILEMANAGER_LIFETIME='+('restored' if a.restore else 'native-ID-owned5s30s-no-block-no-target-mutation'))
if __name__=='__main__':main()
