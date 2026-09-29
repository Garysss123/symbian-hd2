#!/usr/bin/env python3
"""814: Settings AppInfo resource/furniture startup routing, no behavior change."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/EikStd/coctlsrc')
NAME='EIKCOLIB.CPP'
BASE_SHA='d7e6517fbbc22f3e4140a90469ece224ad99ae5e4e2cc032a12f9d083b5b9e6c'
BASE_BINARY='00b74434db307b44af17f18ed3181f3743d17b64b005614a0ff2ec00089b9574'
INC='#include "htcleogsappinfo.inl"\n'
ANCHOR='static void HtcleoEikAppInfoLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n'
OLD='    const TUint32 htcleoEikAppInfoSid = RProcess().SecureId().iId;\n'
NEW=OLD+'''    if (htcleoEikAppInfoSid == 0x100058ecu)
        {
        HtcleoGsAppInfoTrace(htcleoEikAppInfoSid, aStage, aResult, aDetail);
        return;
        }
'''
ENTRY='''void CEikAppUiFactory::ReadAppInfoResourceL(TInt aResourceFileOffset, CEikAppUi* aAppUi)
    {
'''
ENTRY_NEW=ENTRY+'''    HtcleoGsAppInfoTrace(RProcess().SecureId().iId, 0xb61fu,
        KErrNone, (TUint32)aResourceFileOffset);
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('AppInfo observer anchor drift')
    return text.replace(old,new,1)


def transform(text,restore=False):
    if INC in text:
        text=once(text,INC,'');text=once(text,NEW,OLD);text=once(text,ENTRY_NEW,ENTRY)
    elif 'HtcleoGsAppInfoTrace' in text:raise ValueError('partial AppInfo observer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('EikCoCtl differs from exact813 source')
    if not restore:
        text=once(text,ANCHOR,INC+ANCHOR);text=once(text,OLD,NEW);text=once(text,ENTRY,ENTRY_NEW)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('AppInfo inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsappinfo.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_APPINFO='+('restored' if a.restore else 'sid100058ec-B61F-B631-GSBOOT1m-native-resource-furniture-unchanged'))


if __name__=='__main__':main()
