#!/usr/bin/env python3
"""812: GSApp zero-handle SetSgcParams protection plus first-change trace."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='aknsgcc.cpp'
BASE_SHA='55e3e3b8465f4e11bf2520c3b525506884894e1a71cb082587223d4ea13121ad'
BASE_BINARY='424d8d92d7ff40e94b782b9407ddef94ab10cd6a3a8c0a023fdec7a55dcb7801'
INC='#include "htcleogssgcchange.inl"\n'
ENUM_OLD='\tENeverRelinquish\n'
ENUM_NEW='\tENeverRelinquish,\n\tEHtcleoGsChangeTraceUsed // private bit4; existing bits0-3 unchanged\n'
START='void CAknSgcClient::DoHandleChangeL()\n\t{\n'
END='CAknSgcClient::CAknSgcClient()'
TRACE_INIT='''    const TUint32 htcleoChangeSid = RProcess().SecureId().iId;
    const TBool htcleoTraceChange = htcleoChangeSid == 0x100058ecu &&
        !iFlags[EHtcleoGsChangeTraceUsed];
    if (htcleoTraceChange) iFlags.Set(EHtcleoGsChangeTraceUsed);
    TUint htcleoChangeRecords = 0;
'''
CALL_OLD='HtcleoAknAppUiBaseLog('
CALL_NEW='HtcleoGsChangeLog(htcleoChangeSid, htcleoTraceChange, htcleoChangeRecords, '
DECL_OLD='\t\tTInt htcleoSgcSetResult = KErrNotSupported;'
DECL_NEW='''        const TInt htcleoGsParamsHandle = iAknSrv.Handle();
        const TBool htcleoGsLocalParams = HtcleoGsSgcParamsLocal(
            htcleoSgcProcessSid, htcleoGsParamsHandle);
        HtcleoGsChangeLog(htcleoChangeSid, htcleoTraceChange, htcleoChangeRecords,
            0xc52du, htcleoGsLocalParams ? KErrNotSupported : KErrNone,
            (TUint32)htcleoGsParamsHandle);
\t\tTInt htcleoSgcSetResult = KErrNotSupported;'''
IF_OLD='if (!htcleoDeferSgcParams)'
IF_NEW='if (!htcleoDeferSgcParams && !htcleoGsLocalParams)'
DETAIL_OLD='htcleoDeferSgcParams ? 0x53474350u : (TUint32)spLayout'
DETAIL_NEW='(htcleoDeferSgcParams || htcleoGsLocalParams) ? 0x53474350u : (TUint32)spLayout'


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('SGC params anchor drift: '+repr(old))
    return text.replace(old,new,1)


def body_transform(text,restore=False):
    start=text.index(START);end=text.index(END,start);body=text[start:end]
    if restore:
        body=once(body,TRACE_INIT,'');body=once(body,DECL_NEW,DECL_OLD)
        if body.count(IF_NEW)!=2:raise ValueError('SGC local guard count')
        body=body.replace(IF_NEW,IF_OLD);body=once(body,DETAIL_NEW,DETAIL_OLD)
        body=body.replace(CALL_NEW,CALL_OLD)
    else:
        # One first-transaction budget; re-entry and later changes stay silent.
        body=once(body,START,START+TRACE_INIT)
        body=body.replace(CALL_OLD,CALL_NEW)
        body=once(body,DECL_OLD,DECL_NEW)
        if body.count(IF_OLD)!=2:raise ValueError('SGC native guard count')
        body=body.replace(IF_OLD,IF_NEW);body=once(body,DETAIL_OLD,DETAIL_NEW)
    return text[:start]+body+text[end:]


def transform(text,restore=False):
    if INC in text:
        text=body_transform(text,True);text=once(text,INC,'');text=once(text,ENUM_NEW,ENUM_OLD)
    elif 'htcleoGsLocalParams' in text or 'EHtcleoGsChangeTraceUsed' in text:raise ValueError('partial SGC params compatibility')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('SGC differs from exact811 source')
    if not restore:
        text=once(text,'enum TSgcClientFlags\n',INC+'enum TSgcClientFlags\n')
        text=once(text,ENUM_OLD,ENUM_NEW);text=body_transform(text)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('SGC params inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogssgcchange.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_SGC_PARAMS='+('restored' if a.restore else 'sid100058ec-nullhandle-local-fields-no-SetSgcParams-firstchange64-GSBOOT1m'))


if __name__=='__main__':main()
