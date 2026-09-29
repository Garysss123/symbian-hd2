#!/usr/bin/env python3
"""899: bounded native CDL cleanup entry/return evidence; preserve order and branches."""
import argparse,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/uiresources/layouts/cdl/CdlEngine/src')
BASE={'CdlLibrary.cpp':'1a5a9a114322c5fab524f682be7c94e31f95f66d4e43eb9c334871b2776bbebe'}
HELPER='htcleofmcdl899.inl'
INC='#include "'+HELPER+'"\n'
ANCHOR='#include "CCdlEngine.h"\n'
OLD_CLOSE='''void RCdlLibrary::Close()
	{
	REComSession::DestroyedImplementation(iEcomDtorUid);
	iEcomDtorUid.iUid = 0;
	iEcomImpl = 0;
	delete iName;
	iName = NULL;
	}
'''
NEW_CLOSE='''void RCdlLibrary::Close()
	{
    const TBool htcleoFm = HtcleoFmCdlEnabled(RProcess().SecureId().iId);
    const TUint32 htcleoSelf = (TUint32)this;
    HtcleoFmCdlLog(htcleoFm, 0xe910u, htcleoSelf, (TUint32)iEcomDtorUid.iUid);
	REComSession::DestroyedImplementation(iEcomDtorUid);
    HtcleoFmCdlLog(htcleoFm, 0xe911u, htcleoSelf, 0u);
	iEcomDtorUid.iUid = 0;
	iEcomImpl = 0;
    HtcleoFmCdlLog(htcleoFm, 0xe912u, htcleoSelf, (TUint32)iName);
	delete iName;
    HtcleoFmCdlLog(htcleoFm, 0xe913u, htcleoSelf, 0u);
	iName = NULL;
    HtcleoFmCdlLog(htcleoFm, 0xe914u, htcleoSelf, 0u);
	}
'''
OLD_CALLBACK='''TInt CCdlLibManager::LazyUnload(TAny* aThis)
	{
	static_cast<CCdlLibManager*>(aThis)->DoLazyUnload();
	return 0;
	}
'''
NEW_CALLBACK='''TInt CCdlLibManager::LazyUnload(TAny* aThis)
	{
    const TBool htcleoFm = HtcleoFmCdlEnabled(RProcess().SecureId().iId);
    const TUint32 htcleoSelf = (TUint32)aThis;
    HtcleoFmCdlLog(htcleoFm, 0xe900u, htcleoSelf, 0u);
	static_cast<CCdlLibManager*>(aThis)->DoLazyUnload();
    HtcleoFmCdlLog(htcleoFm, 0xe909u, htcleoSelf, 0u);
	return 0;
	}
'''
OLD_UNLOAD='''void CCdlLibManager::DoLazyUnload()
	{
	TInt count = iLibs.Count();
	for (TInt ii=count-1; ii>=0; ii--)
		{
		RCdlLibrary* lib = iLibs[ii];
		if (lib->RefCount() <= 0)
			{
			iLibs.Delete(ii--);
			lib->Close();
			delete lib;
			}
		}

	delete iLazyUnloader;
	iLazyUnloader = 0;
	}
'''
NEW_UNLOAD='''void CCdlLibManager::DoLazyUnload()
	{
    const TBool htcleoFm = HtcleoFmCdlEnabled(RProcess().SecureId().iId);
    const TUint32 htcleoSelf = (TUint32)this;
	TInt count = iLibs.Count();
    HtcleoFmCdlLog(htcleoFm, 0xe901u, htcleoSelf, (TUint32)count);
	for (TInt ii=count-1; ii>=0; ii--)
		{
		RCdlLibrary* lib = iLibs[ii];
		if (lib->RefCount() <= 0)
			{
            const TUint32 htcleoLib = (TUint32)lib;
            HtcleoFmCdlLog(htcleoFm, 0xe902u, htcleoLib, (TUint32)ii);
			iLibs.Delete(ii--);
            HtcleoFmCdlLog(htcleoFm, 0xe903u, htcleoLib, (TUint32)ii);
			lib->Close();
            HtcleoFmCdlLog(htcleoFm, 0xe904u, htcleoLib, 0u);
			delete lib;
            HtcleoFmCdlLog(htcleoFm, 0xe905u, htcleoLib, 0u);
			}
		}

    const TUint32 htcleoCallback = (TUint32)iLazyUnloader;
    HtcleoFmCdlLog(htcleoFm, 0xe906u, htcleoSelf, htcleoCallback);
	delete iLazyUnloader;
    HtcleoFmCdlLog(htcleoFm, 0xe907u, htcleoSelf, htcleoCallback);
	iLazyUnloader = 0;
    HtcleoFmCdlLog(htcleoFm, 0xe908u, htcleoSelf, 0u);
	}
'''
PAIRS=((OLD_CLOSE,NEW_CLOSE),(OLD_CALLBACK,NEW_CALLBACK),(OLD_UNLOAD,NEW_UNLOAD))
def once(text,a,b):
    if text.count(a)!=1:raise ValueError('899 exact anchor drift '+repr(a[:60]))
    return text.replace(a,b,1)
def transform(text,name='CdlLibrary.cpp',restore=False):
    if name not in BASE:raise ValueError('Wrong899 source')
    if INC in text:
        for a,b in PAIRS:text=once(text,b,a)
        text=once(text,INC,'')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('Not exact stock898 CDL source')
    if not restore:
        text=once(text,ANCHOR,ANCHOR+INC)
        for a,b in PAIRS:text=once(text,a,b)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    f=a.root/REL/'CdlLibrary.cpp';old=f.read_text(encoding='latin-1');new=transform(old,restore=a.restore)
    if transform(new,restore=True)!=transform(old,restore=True):raise ValueError('899 inverse')
    if not a.restore:
        if transform(new)!=new:raise ValueError('899 idempotence')
        (a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    if old!=new:f.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_CDL_TAIL='+('restored' if a.restore else 'native-cleanup-order64-entry-return-no-bypass'))
if __name__=='__main__':main()
