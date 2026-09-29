#!/usr/bin/env python3
"""813: route existing Eikon BaseConstruct checkpoints for Settings only."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/commonuisupport/uikon/coresrc')
NAME='EIKAPPUI.CPP'
BASE_SHA='4b8c75fac0a2dc53e177009c067d144488993aca73813d64b1f7b210a12183fb'
BASE_BINARY='6b890aff24a0be95baaba8616e27ca4cb2ab9fbc3e2e9834367209a47be5204d'
INC='#include "htcleogseikbase.inl"\n'
ANCHOR='static void HtcleoEikAppUiBaseLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n'
OLD='    const TUint32 htcleoEikBaseSid = RProcess().SecureId().iId;\n'
NEW=OLD+'''    if (htcleoEikBaseSid == 0x100058ecu)
        {
        HtcleoGsEikBaseTrace(htcleoEikBaseSid, aStage, aResult, aDetail);
        return;
        }
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GSApp Eikon base anchor drift')
    return text.replace(old,new,1)


def transform(text,restore=False):
    if INC in text:
        text=once(text,INC,'');text=once(text,NEW,OLD)
    elif 'HtcleoGsEikBaseTrace' in text:raise ValueError('partial Eikon base observer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('EikAppUi differs from exact812 source')
    if not restore:
        text=once(text,ANCHOR,INC+ANCHOR);text=once(text,OLD,NEW)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('Eikon base inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogseikbase.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_EIKBASE='+('restored' if a.restore else 'sid100058ec-existing-B600-B615-GSBOOT1m-no-policy-change'))


if __name__=='__main__':main()
