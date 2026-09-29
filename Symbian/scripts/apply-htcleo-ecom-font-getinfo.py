#!/usr/bin/env python3
"""863: split the exact native RLibrary::GetInfo wrapper for FreeType only."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp')
BASE_SHA='471d5d1aaf08e442f7460e01508ca3e595e1729c1d8c1dbc5b351161ef2a3e31'
MARKER='HTCLEO_ECOM_FONT_GETINFO_863'
OLD='\tTInt ret = RLibrary::GetInfo(dllFullName, infoBuf);'
NEW=r'''	// HTCLEO_ECOM_FONT_GETINFO_863
	TInt ret;
	if (htcleoFontDll)
		{
		// Same Connect/GetInfo/Close sequence as native up_lib.cpp, once.
		// Record a bounded, case-folded path fingerprint in unused failure
		// SID/UID slots. On success the existing862 snapshot overwrites them.
		_LIT(KHtcleoFontPath, "z:\\sys\\bin\\freetype.dll");
		const TInt pathChars = dllFullName.Length();
		const TInt expectedChars = KHtcleoFontPath().Length();
		TBool pathMatches = pathChars == expectedChars;
		TUint32 pathHash = 2166136261u;
		for (TInt i = 0; i < pathChars; ++i)
			{
			TUint32 c = dllFullName[i];
			if (c >= 'A' && c <= 'Z') c += 'a' - 'A';
			pathHash = (pathHash ^ c) * 16777619u;
			if (i >= expectedChars || c != KHtcleoFontPath()[i]) pathMatches = EFalse;
			}
		HtcleoEcFontMark(8192u | (pathMatches ? 16384u : 0u), 4, pathHash);
		HtcleoEcFontMark(0u, 5, (TUint32)pathChars);
		RLoader loader;
		ret = loader.Connect();
		HtcleoEcFontMark(32768u, 3, (TUint32)ret);
		if (ret == KErrNone)
			{
			HtcleoEcFontMark(65536u, 0, 0);
			ret = loader.GetInfo(dllFullName, infoBuf);
			loader.Close();
			}
		}
	else
		ret = RLibrary::GetInfo(dllFullName, infoBuf);'''
POLICY='FreeType-only-native-Connect-GetInfo-Close-once-RAM-path-fingerprint-no-loader-or-security-policy-change'


def transform(text,restore=False):
    if MARKER in text:
        if text.count(NEW)!=1:
            raise ValueError('863 partial wrapper split')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode()).hexdigest()!=BASE_SHA:
        raise ValueError('863 requires exact862 registry')
    if not restore:
        if text.count(OLD)!=1:
            raise ValueError('863 GetInfo anchor drift')
        text=text.replace(OLD,NEW,1)
    return text


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    a=p.parse_args();path=a.root/REL;old=path.read_text();new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('863 inverse failed')
    if old!=new:path.write_text(new)
    print('HTCLEO_ECOM_FONT_GETINFO='+('restored' if a.restore else POLICY))
