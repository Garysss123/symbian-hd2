#!/usr/bin/env python3
"""895: complete FileManager's existing no-session system-fade contract."""
import argparse
import hashlib
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
BASE={'aknsgcc.cpp':'a70b1e6e0ddce9a9a998a145d79e692050162ad839d692f838ca976017b6dd9b'}
HELPER='htcleofmsystemfade895.inl'
INC='#include "'+HELPER+'"\n'
ANCHOR='#include "htcleofmsgc885.inl"\n'
START='void CAknSgcClient::DoSetSystemFaded(TBool aFade)\n'
END='TBool CAknSgcClient::DoIsSystemFaded() const\n'
MARKER=' // HTCLEO_FM_SYSTEM_FADE_895'
OLD_INIT='\tconst TBool htcleoHomeSystemFade =\n\t\t(RProcess().SecureId().iId == 0x102750F0u);\n'
NEW_INIT='''\tconst TUint32 htcleoSystemFadeSid = RProcess().SecureId().iId;
\tconst TBool htcleoHomeSystemFade = (htcleoSystemFadeSid == 0x102750F0u);
\tconst TBool htcleoFmSystemFade = (htcleoSystemFadeSid == 0x101f84ebu);
'''
BRANCH='''\telse if (HtcleoFmSystemFadeLocal(htcleoSystemFadeSid, htcleoAknSrvHandle))
\t\t{
\t\t//895: the getter already uses this flag when no server endpoint exists.
\t\t//Keep requested local state; do not claim system-wide pixels were faded.
\t\tHtcleoFmSystemFadeLog(htcleoFmSystemFade, 0xd601u,
\t\t\tiFlags[ESystemFaded], (TUint32)htcleoAknSrvHandle);
\t\tiFlags.Assign(ESystemFaded, aFade);
\t\tHtcleoFmSystemFadeLog(htcleoFmSystemFade, 0xd602u,
\t\t\tiFlags[ESystemFaded], (TUint32)htcleoAknSrvHandle);
\t\t}
'''

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('895 anchor drift '+repr(old))
    return text.replace(old,new,1)

def log(stage):
    return ('\tHtcleoFmSystemFadeLog(htcleoFmSystemFade, 0x%04xu, aFade, '
            '(TUint32)htcleoAknSrvHandle);'%stage)+MARKER+'\n'

def body_transform(text,restore=False):
    begin=text.index(START);end=text.index(END,begin);body=text[begin:end]
    if restore:
        body=once(body,BRANCH,'')
        body,count=re.subn(r'^.*'+re.escape(MARKER)+r'\n','',body,flags=re.M)
        if count!=6:raise ValueError('895 expected6 common observer sites')
        body=once(body,NEW_INIT,OLD_INIT)
    else:
        body=once(body,OLD_INIT,NEW_INIT)
        handle='\tconst TInt htcleoAknSrvHandle = iAknSrv.Handle();\n'
        body=once(body,handle,handle+log(0xd600))
        server='\t\tiEikonEnv->WsSession().SetSystemFaded(aFade);\n'
        body=once(body,server,log(0xd605)+server+log(0xd606))
        matrix='\telse if (htcleoAknSrvHandle == 0 &&\n\t\tRProcess().SecureId().iId == 0x101f4cd2u)\n'
        body=once(body,matrix,BRANCH+matrix)
        remote='\t\tiAknSrv.SetSystemFaded(aFade);\n'
        body=once(body,remote,log(0xd603)+remote+log(0xd604))
        body=once(body,'\n\t}\n\n','\n'+log(0xd607)+'\t}\n\n')
    return text[:begin]+body+text[end:]

def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong895 source')
    if INC in text:
        text=body_transform(text,True)
        text=once(text,INC,'')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('not exact894 SGC source')
    if not restore:
        text=once(text,ANCHOR,ANCHOR+INC)
        text=body_transform(text)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    a=p.parse_args();path=a.root/REL/'aknsgcc.cpp'
    old=path.read_text(encoding='latin-1');new=transform(old,path.name,a.restore)
    if transform(new,path.name,True)!=transform(old,path.name,True):raise ValueError('895 inverse')
    if not a.restore:
        if transform(new,path.name)!=new:raise ValueError('895 idempotence')
        (a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_SYSTEM_FADE='+('restored' if a.restore else 'zero-session-client-local-set-real-flag-live-server-unchanged'))

if __name__=='__main__':main()
