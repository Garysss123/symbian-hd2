#!/usr/bin/env python3
"""815: Settings StatusPane startup routing; native constructors unchanged."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/EikStd/coctlsrc')
NAME='eikspane.cpp'
BASE_SHA='80d35d282f305404fce69933892765b08541ab4d42b96fbdacd908d1d5b49064'
BASE_BINARY='4ec6224573b5ed4061f9547f6ecf8c0d49070ba4729e489031475dacf5229672'
INC='#include "htcleogsstatuspane.inl"\n'
ANCHOR='static void HtcleoStatusPaneLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n'
OLD='    const TUint32 htcleoStatusPaneSid = RProcess().SecureId().iId;\n'
NEW=OLD+'''    if (htcleoStatusPaneSid == 0x100058ecu)
        {
        HtcleoGsStatusPaneTrace(htcleoStatusPaneSid, aStage, aResult, aDetail);
        return;
        }
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('StatusPane observer anchor drift')
    return text.replace(old,new,1)


def transform(text,restore=False):
    if INC in text:
        text=once(text,INC,'');text=once(text,NEW,OLD)
    elif 'HtcleoGsStatusPaneTrace' in text:raise ValueError('partial StatusPane observer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('eikspane differs from exact814 source')
    if not restore:
        text=once(text,ANCHOR,INC+ANCHOR);text=once(text,OLD,NEW)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('StatusPane inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsstatuspane.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_STATUSPANE='+('restored' if a.restore else 'sid100058ec-B640-B67B-GSBOOT1m-native-statuspane-unchanged'))


if __name__=='__main__':main()
