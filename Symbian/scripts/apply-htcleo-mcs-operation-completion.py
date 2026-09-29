#!/usr/bin/env python3
"""801: single-watcher error-completion recovery, no query or shared runtime fix."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/homescreensrv/homescreensrv_plat/sapi_menucontent/mcsservice/src')
NAME='mcsmenuopwatcher.cpp'
BASE_SHA='6a154fbfbb04815e34c1132260c6156172f3e5226282fe3d6e72387782acf0a7'
INC='#include "htcleomenulaunchtrace.inl"\n'
OLD='''void CMCSMenuOpWatcher::RunL()
    {
    delete iOperation;
    iOperation = NULL; 
    iOperationManager.Remove( this );//delete this object and remove it 
                                         //from operation manager      
    TRAP_IGNORE( iObserver.MenuOpCompletedL(iStatus.Int() ) );
    User::LeaveIfError( iStatus.Int() );
    
    delete this;
    }
'''
NEW='#include "htcleomcsopcompletion.inl"\n'


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('operation-completion anchor changed: '+repr(old))
    return text.replace(old,new,1)


def transform(text,restore=False):
    if NEW in text:
        text=once(text,NEW,OLD)
        text=once(text,INC,'')
    elif INC in text:
        raise ValueError('partial completion layer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:
        raise ValueError('operation completion requires exact800 watcher')
    if not restore:
        text=once(text,'#include "mcsoperationmanager.h"\n','#include "mcsoperationmanager.h"\n'+INC)
        text=once(text,OLD,NEW)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore and (transform(new)!=new or transform(new,True)!=transform(old,True)):
        raise ValueError('completion inverse/idempotence failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        for name in ('htcleomenulaunchtrace.inl','htcleomcsopcompletion.inl'):
            asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/name
            path.with_name(name).write_bytes(asset.read_bytes())
    print('HTCLEO_MCS_OPERATION_COMPLETION='+('restored' if a.restore else 'original-error-callback-once-nonresource-cleanup-no-rethrow'))

if __name__=='__main__':main()
