#!/usr/bin/env python3
"""809: GSApp-only routing of existing AknEnv startup stages, no recovery change."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='aknenv.cpp'
BASE_SHA='97bf972e6501f33f4d44d8cdba97d97c7fe334c24a34b365972739cb685df277'
BASE_BINARY='e88f400c829a3a44cf1f2db863946825758120eabf6474db7372dfc9da644ede'
INC='#include "htcleogsaknenvtrace.inl"\n'
ANCHOR='static void HtcleoAknEnvMenuLog(\n'
OLD='''    const TUint32 htcleoSid = RProcess().SecureId().iId;
    const TBool htcleoHome = (htcleoSid == 0x102750f0u);
'''
NEW='''    const TUint32 htcleoSid = RProcess().SecureId().iId;
    if (htcleoSid == 0x100058ecu)
        {
        HtcleoGsAknEnvTrace(htcleoSid, aStage, aResult, aDetail);
        return;
        }
    const TBool htcleoHome = (htcleoSid == 0x102750f0u);
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GSApp AknEnv routing anchor drift')
    return text.replace(old,new,1)


def transform(text,restore=False):
    if INC in text:
        text=once(text,INC,'');text=once(text,NEW,OLD)
    elif 'HtcleoGsAknEnvTrace(' in text:raise ValueError('partial GSApp AknEnv observer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:
        raise ValueError('AknEnv differs from exact808 source')
    if not restore:
        text=once(text,ANCHOR,INC+ANCHOR);text=once(text,OLD,NEW)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('AknEnv inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsaknenvtrace.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_AKNENV='+('restored' if a.restore else 'sid100058ec-existing-A000-A01E-GSBOOT1m-no-CDL-policy-change'))


if __name__=='__main__':main()
