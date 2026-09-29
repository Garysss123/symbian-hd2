#!/usr/bin/env python3
"""819: GSApp missing-session key-block guard; preserve native valid/server paths."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='aknsgcc.cpp'
BASE_SHA='aea42b26fcd4e328c81730aafecb3b66df79406ba0b74783267c097b622ee0b0'
BASE_BINARY='b44d533d5cd2ef88f3d1df098d8780f551ddbb8b9ef4f03bf6577f769c5c8b1f'
INC='#include "htcleogskeyblock.inl"\n'
ENUM_OLD='\tEHtcleoGsFadeTraceUsed // private bit5; first GS fade getter only\n'
ENUM_NEW='\tEHtcleoGsFadeTraceUsed, // private bit5; first GS fade getter only\n\tEHtcleoGsKeyBlockTraceUsed // private bit6; native/previous bits0-5 unchanged\n'
START='void CAknSgcClient::DoSetKeyBlockMode(TAknKeySoundOpcode aMode)\n    {\n'
END='void CAknSgcClient::DoSetKeyboardRepeatRate('
INIT='''    const TUint32 htcleoGsKeyBlockSid = RProcess().SecureId().iId;
    const TBool htcleoGsTraceKeyBlock = HtcleoGsKeyBlockTraceEnabled(
        htcleoGsKeyBlockSid, iFlags[EHtcleoGsKeyBlockTraceUsed]);
    if (htcleoGsTraceKeyBlock)
        {
        iFlags.Set(EHtcleoGsKeyBlockTraceUsed);
        }
'''
HANDLE='    const TInt htcleoAknSrvHandle = iAknSrv.Handle();\n'
HANDLE_NEW=HANDLE+'''    HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a0u,
        aMode, (TUint32)htcleoAknSrvHandle);
    HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a1u,
        iFlags[EInAknSrv], 0u);
'''
HOME='\telse if (htcleoHomeKeyBlock && htcleoAknSrvHandle == 0)'
SKIP='''    else if (HtcleoGsKeyBlockSkip(htcleoGsKeyBlockSid, htcleoAknSrvHandle))
        {
        // No server endpoint can apply this mode. The AppUi's iBlockMode stays unchanged.
        HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a4u, KErrNotReady, aMode);
        }
'''
RAW='        iEikonEnv->WsSession().SimulateRawEvent(event);\n'
RAW_NEW='''        HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a2u, KErrNone, opcode);
'''+RAW+'''        HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a3u, KErrNone, opcode);
'''
REMOTE='\t\tiAknSrv.SetKeyblockMode(aMode);\n'
REMOTE_NEW='''        HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a5u, KErrNone, htcleoAknSrvHandle);
'''+REMOTE+'''        HtcleoGsKeyBlockLog(htcleoGsTraceKeyBlock, 0xc5a6u, KErrNone, htcleoAknSrvHandle);
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS keyblock anchor drift: '+repr(old))
    return text.replace(old,new,1)


def body_transform(text,restore=False):
    a=text.index(START);b=text.index(END,a);body=text[a:b]
    pairs=((START,START+INIT),(HANDLE,HANDLE_NEW),(HOME,SKIP+HOME),(RAW,RAW_NEW),(REMOTE,REMOTE_NEW))
    for old,new in (reversed(pairs) if restore else pairs):
        body=once(body,new,old) if restore else once(body,old,new)
    return text[:a]+body+text[b:]


def transform(text,restore=False):
    if INC in text:
        text=body_transform(text,True);text=once(text,INC,'');text=once(text,ENUM_NEW,ENUM_OLD)
    elif 'htcleoGsTraceKeyBlock' in text or 'EHtcleoGsKeyBlockTraceUsed' in text:raise ValueError('partial GS keyblock guard')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('SGC differs from exact818 source')
    if not restore:
        text=once(text,'enum TSgcClientFlags\n',INC+'enum TSgcClientFlags\n')
        text=once(text,ENUM_OLD,ENUM_NEW);text=body_transform(text)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('GS keyblock inverse/idempotence failed')
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogskeyblock.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_KEYBLOCK='+('restored' if a.restore else 'GS-only-zero-session-no-keyblock-IPC-firstcall4-private-bit6'))


if __name__=='__main__':main()
