#!/usr/bin/env python3
"""816: GSApp zero-session fade query uses its real local flag; first-get trace."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='aknsgcc.cpp'
BASE_SHA='530fab97a1a4f38b192490099a20db39246a635244a0b00851a33e0e1e7361ec'
BASE_BINARY='29aab9b2b03e90403c0c5af029a1d21d8c282c8d016343814a1ec49b70aabffb'
INC='#include "htcleogssystemfade.inl"\n'
ENUM_OLD='\tEHtcleoGsChangeTraceUsed // private bit4; existing bits0-3 unchanged\n'
ENUM_NEW='\tEHtcleoGsChangeTraceUsed, // private bit4; existing bits0-3 unchanged\n\tEHtcleoGsFadeTraceUsed // private bit5; first GS fade getter only\n'
START='TBool CAknSgcClient::DoIsSystemFaded() const\n\t{\n'
END='void CAknSgcClient::SetLegacyOrientationAndScreenModeAppUiFlags'
INIT='''    const TUint32 htcleoGsFadeSid = RProcess().SecureId().iId;
    const TBool htcleoGsTraceFade = HtcleoGsSystemFadeTraceEnabled(
        htcleoGsFadeSid, iFlags[EHtcleoGsFadeTraceUsed]);
    if (htcleoGsTraceFade)
        {
        const_cast<CAknSgcClient*>(this)->iFlags.Set(EHtcleoGsFadeTraceUsed);
        }
'''
HANDLE='\tconst TInt htcleoAknSrvHandle = iAknSrv.Handle();\n'
HANDLE_NEW=HANDLE+'''    HtcleoGsSystemFadeLog(htcleoGsTraceFade, 0xc580u,
        iFlags[EInAknSrv], (TUint32)htcleoAknSrvHandle);
'''
SERVER='\tif (iFlags[EInAknSrv])\n\t\t{\n'
SERVER_NEW=SERVER+'''        HtcleoGsSystemFadeLog(htcleoGsTraceFade, 0xc581u,
            iFlags[ESystemFaded], (TUint32)htcleoAknSrvHandle);
'''
MATRIX='\telse if (htcleoAknSrvHandle == 0 &&\n\t\tRProcess().SecureId().iId == 0x101f4cd2u)'
LOCAL='''    else if (HtcleoGsSystemFadeLocal(htcleoGsFadeSid, htcleoAknSrvHandle))
        {
        // No endpoint exists; keep the real local fade state, not forced false.
        HtcleoGsSystemFadeLog(htcleoGsTraceFade, 0xc582u,
            KErrNotSupported, (TUint32)iFlags[ESystemFaded]);
        return iFlags[ESystemFaded];
        }
'''
CALL='\t\tiAknSrv.IsSystemFaded(fade);\n'
CALL_NEW='''        HtcleoGsSystemFadeLog(htcleoGsTraceFade, 0xc583u,
            KErrNone, (TUint32)htcleoAknSrvHandle);
'''+CALL+'''        HtcleoGsSystemFadeLog(htcleoGsTraceFade, 0xc584u,
            fade, (TUint32)htcleoAknSrvHandle);
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS fade anchor drift: '+repr(old))
    return text.replace(old,new,1)


def body_transform(text,restore=False):
    begin=text.index(START);end=text.index(END,begin);body=text[begin:end]
    pairs=((START,START+INIT),(HANDLE,HANDLE_NEW),(SERVER,SERVER_NEW),(MATRIX,LOCAL+MATRIX),(CALL,CALL_NEW))
    for old,new in (reversed(pairs) if restore else pairs):
        body=once(body,new,old) if restore else once(body,old,new)
    return text[:begin]+body+text[end:]


def transform(text,restore=False):
    if INC in text:
        text=body_transform(text,True);text=once(text,INC,'');text=once(text,ENUM_NEW,ENUM_OLD)
    elif 'htcleoGsTraceFade' in text or 'EHtcleoGsFadeTraceUsed' in text:
        raise ValueError('partial GS fade compatibility')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('SGC differs from exact815 source')
    if not restore:
        text=once(text,'enum TSgcClientFlags\n',INC+'enum TSgcClientFlags\n')
        text=once(text,ENUM_OLD,ENUM_NEW);text=body_transform(text)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('GS fade inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogssystemfade.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_SGC_FADE='+('restored' if a.restore else 'sid100058ec-handle0-real-local-fade-firstget3-GSBOOT1m'))


if __name__=='__main__':main()
