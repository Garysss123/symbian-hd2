#!/usr/bin/env python3
"""825: a failed GS ECom subscription is not a successful registry change."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSFramework')
NAME=Path('src/GSEComNotifier.cpp')
BASE_SOURCE='1c84822d7002a300f6827d55a7ffabb13fea8ab98264611f6fccb8a5879ade5f'
BASE_BINARY='4521bcec67615afffecb902868f4d3a356e87352d9feb20291c019ab8aac7b52'
MARKER='HTCLEO_GS_ECOM_NOTIFY_GUARD_825'
HEADER='#include "GsLogger.h"'
GUARD="""    // HTCLEO_GS_ECOM_NOTIFY_GUARD_825
    // The completed failed subscription is not a registry-change event.
    // Retire only this GS subscription; do not query or rearm a dead session.
    // Successful notifications and non-GS consumers retain native behavior.
    if (iStatus.Int() != KErrNone && RProcess().SecureId().iId == 0x100058ecu)
        {
        TUint htcleoCount = 0;
        HtcleoGsPluginLog(htcleoCount, 0xc730u, iStatus.Int(), 0x10207236u);
        return;
        }

"""
ANCHOR='    if( PluginCountDeltaL() < 0 )'
EDITS=((HEADER,HEADER+'\n#include "htcleogsplugintrace.inl"'),
       (ANCHOR,GUARD+ANCHOR))

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GSEComNotifier anchor drift: '+repr(old))
    return text.replace(old,new,1)

def transform(text,restore=False):
    if MARKER in text:
        for old,new in reversed(EDITS):text=once(text,new,old)
    elif 'htcleogsplugintrace' in text or 'HtcleoGsPluginLog' in text:
        raise ValueError('partial GS notifier overlay')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('GSEComNotifier is not exact824 source')
    if not restore:
        for old,new in EDITS:text=once(text,old,new)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1')
    new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    helper=Path(__file__).resolve().parent.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsplugintrace.inl'
    if not a.restore:(path.parent/helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_GSAPP_ECOM_NOTIFY_GUARD='+('restored' if a.restore else
          'GS-negative-notify-retire-C730-no-list-no-rearm-success-native'))
if __name__=='__main__':main()

