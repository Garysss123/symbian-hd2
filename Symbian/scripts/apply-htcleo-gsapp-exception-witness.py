#!/usr/bin/env python3
"""824: GSApp-only terminal exception witness; retain every normal startup call."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
NAME='Src/GSApp.cpp'
BASE_SHA='1d8dfb529fabae2fe6d28c56e139c057b9b9ffea89f33f896f1c79dd80398efe'
BASE_BINARY='c2b4216e919af1d53333df8a3dd5507b9abb1dd96338e3644a7c4160c97c9b22'
INC='#include "htcleogsexceptionstack.inl"\n'
ANCHOR='#include "htcleogseikstart.inl"\n'
ENTRY='    HtcleoGsBootLog(0x6000u, KErrNone, 0x100058ecu);\n'
INSTALL='''    const TInt htcleoGsObserver = HtcleoInstallGsExceptionObserver();
    HtcleoGsBootLog(0x60e0u, htcleoGsObserver, (TUint32)HtcleoGsExceptionObserverState());
'''
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS exception anchor drift: '+repr(old))
    return text.replace(old,new,1)
def transform(text,restore=False):
    if INC in text:
        text=once(text,INC,'');text=once(text,INSTALL,'')
    elif 'HtcleoInstallGsExceptionObserver' in text:raise ValueError('partial GS exception witness')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('not exact823 GSApp source')
    if not restore:
        text=once(text,ANCHOR,ANCHOR+INC);text=once(text,ENTRY,ENTRY+INSTALL)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    source=a.root/REL/NAME;old=source.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('exception inverse failed')
    if not a.restore and transform(new)!=new:raise ValueError('exception idempotence failed')
    if old!=new:source.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsexceptionstack.inl'
        (source.parent/helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_GSAPP_EXCEPTION='+('restored' if a.restore else 'GS-no-existing-handler-install60E0-GSX1-bounded240-terminal-restore-reraise'))
if __name__=='__main__':main()
