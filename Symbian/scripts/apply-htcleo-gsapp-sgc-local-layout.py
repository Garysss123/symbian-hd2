#!/usr/bin/env python3
"""810: guarded Settings local SGC layout on real missing-server/null-handle state."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='aknsgcc.cpp'
BASE_SHA='3e0061865324319cb0319c1764939e2f9a83c43ba182a3dda5b5284820462ffb'
BASE_BINARY='7136a1aa89c915f8e9c2aa71db1eaee09d7fe389dd4c800028244a44e40e4587'
INC='#include "htcleogssgctrace.inl"\n'
ANCHOR='static void HtcleoAknSgcMenuLog(\n'
LOG_OLD='''    const TUint32 htcleoSid = RProcess().SecureId().iId;
    const TBool htcleoHome = (htcleoSid == 0x102750f0u);
'''
LOG_NEW='''    const TUint32 htcleoSid = RProcess().SecureId().iId;
    if (htcleoSid == 0x100058ecu)
        {
        HtcleoGsSgcTrace(htcleoSid, aStage, aResult, aDetail);
        return;
        }
    const TBool htcleoHome = (htcleoSid == 0x102750f0u);
'''
GUARD_OLD='\tif (!htcleoMatrixMenuAknCapFailOpen)\n'
GUARD_NEW='''    const TUint32 htcleoSgcSid = RProcess().SecureId().iId;
    const TInt htcleoSgcHandle = iAknSrv.Handle();
    const TBool htcleoGsUseLocal = HtcleoGsSgcLocalAllowed(
        htcleoSgcSid, aknServerError, htcleoSgcHandle);
    HtcleoGsSgcTrace(htcleoSgcSid, 0x4d4da134u, aknServerError, (TUint32)htcleoSgcHandle);
    HtcleoGsSgcTrace(htcleoSgcSid, 0x4d4da135u, aknServerError, htcleoGsUseLocal ? 1u : 0u);
	if (!htcleoMatrixMenuAknCapFailOpen && !htcleoGsUseLocal)
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GSApp SGC anchor drift')
    return text.replace(old,new,1)


def transform(text,restore=False):
    if INC in text:
        text=once(text,INC,'');text=once(text,LOG_NEW,LOG_OLD);text=once(text,GUARD_NEW,GUARD_OLD)
    elif 'HtcleoGsSgc' in text or 'htcleoGsUseLocal' in text:raise ValueError('partial GSApp SGC compatibility')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('SGC differs from exact809 source')
    if not restore:
        text=once(text,ANCHOR,INC+ANCHOR);text=once(text,LOG_OLD,LOG_NEW);text=once(text,GUARD_OLD,GUARD_NEW)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('SGC inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogssgctrace.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_SGC='+('restored' if a.restore else 'sid100058ec-notfound-or-terminated-nullhandle-native-local-layout-GSBOOT1m'))


if __name__=='__main__':main()
