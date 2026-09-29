#!/usr/bin/env python3
"""898: bounded FileManager ECom destroy boundaries; preserve cleanup policy."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame')
BASE={'EComSession.cpp':'b847feeaa35030a1e40958a9a969f2e1910174c4824d910577d755b4db7cf932'}
HELPER='htcleofmdestroy898.inl'
INC='#include "'+HELPER+'"\n'
ANCHOR='#include "HtcleoEcomLog.h"\n'
OLD='''EXPORT_C void REComSession::DestroyedImplementation(TUid aInstanceKey)
\t{
\tif(aInstanceKey != KNullUid)
\t\t{
\t\tCGlobalData* globalData = CGlobalData::Instance();
\t\tif(globalData)
\t\t\t{
\t\t\tif(globalData->LoadManager().DestroyedThis(aInstanceKey))
\t\t\t\t{
\t\t\t\tglobalData->EComSession().Close();
\t\t\t\t}
\t\t\t}
\t\t}
\t}
'''
NEW='''EXPORT_C void REComSession::DestroyedImplementation(TUid aInstanceKey)
\t{
    const TUint32 htcleoFmCaller = (TUint32)__builtin_return_address(0);
    const TBool htcleoFmDestroy = HtcleoFmDestroyEnabled(RProcess().SecureId().iId, aInstanceKey.iUid);
    HtcleoFmDestroyLog(htcleoFmDestroy, 0xe800u, aInstanceKey.iUid, htcleoFmCaller);
\tif(aInstanceKey != KNullUid)
\t\t{
\t\tCGlobalData* globalData = CGlobalData::Instance();
        HtcleoFmDestroyLog(htcleoFmDestroy, 0xe801u, aInstanceKey.iUid, (TUint32)globalData);
\t\tif(globalData)
\t\t\t{
            HtcleoFmDestroyLog(htcleoFmDestroy, 0xe802u, aInstanceKey.iUid, (TUint32)globalData);
            const TBool htcleoDestroyed = globalData->LoadManager().DestroyedThis(aInstanceKey);
            HtcleoFmDestroyLog(htcleoFmDestroy, 0xe803u, aInstanceKey.iUid, (TUint32)htcleoDestroyed);
\t\t\tif(htcleoDestroyed)
\t\t\t\t{
                HtcleoFmDestroyLog(htcleoFmDestroy, 0xe804u, aInstanceKey.iUid, (TUint32)globalData);
\t\t\t\tglobalData->EComSession().Close();
                //Close may release globalData: do not inspect it after this call.
                HtcleoFmDestroyLog(htcleoFmDestroy, 0xe805u, aInstanceKey.iUid, 0u);
\t\t\t\t}
\t\t\t}
\t\t}
    HtcleoFmDestroyLog(htcleoFmDestroy, 0xe806u, aInstanceKey.iUid, 0u);
\t}
'''

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('898 exact anchor drift '+repr(old[:70]))
    return text.replace(old,new,1)

def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong898 source')
    if INC in text:
        text=once(text,NEW,OLD);text=once(text,INC,'')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact897 EComSession source')
    if not restore:
        text=once(text,ANCHOR,ANCHOR+INC);text=once(text,OLD,NEW)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    a=p.parse_args();path=a.root/REL/'EComSession.cpp'
    old=path.read_text(encoding='latin-1');new=transform(old,path.name,a.restore)
    if transform(new,path.name,True)!=transform(old,path.name,True):raise ValueError('898 inverse')
    if not a.restore:
        if transform(new,path.name)!=new:raise ValueError('898 idempotence')
        (a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_ECOM_DESTROY='+('restored' if a.restore else 'FileManager-nonzero-key64-native-destroy-close-unchanged'))

if __name__=='__main__':main()
