#!/usr/bin/env python3
"""826: reuse native one-reconnect ECom path for GS creation, never fake success."""
import argparse
import hashlib
from pathlib import Path
REL=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework')
NAME=Path('frame/EComSession.cpp')
BASE_SOURCE='a4a2ab56ae4aa70e12aabf77cf62fbb253ea980484ff0d474607c79bc742a259'
BASE_BINARY='d2eaf4828f00355d746deb4bb1900cb8a10ae3dcc7776f7d7eba21e01d3e3cd3'
MARKER='HTCLEO_GS_ECOM_CREATE_RECONNECT_826'
BEGIN='TAny* REComSession::ResolveAndCreateImplL(TInt aServiceId,'
END='\tCleanupStack::PopAndDestroy(&matchStrExtInfBuf);'
HEADER='#include "HtcleoEcomLog.h"'
SCOPE='\tconst TBool htcleoUiShell =\n\t\thtcleoMatrixMenu || htcleoHomeScreen;\n'
SCOPE_NEW=SCOPE+'''    // HTCLEO_GS_ECOM_CREATE_RECONNECT_826
    const TBool htcleoGsSettings = (RProcess().SecureId().iId == 0x100058ecu);
    TUint htcleoGsRetryLogCount = 0;
'''
CONDITION='if(htcleoUiShell && htcleoSendResult == KErrServerTerminated)'
CONDITION_NEW='if((htcleoUiShell || htcleoGsSettings) && htcleoSendResult == KErrServerTerminated)'
TRACE_EDITS=[]
for old_stage,new_stage,result in ((0x312,0xc731,'htcleoSendResult'),
                                   (0x313,0xc732,'htcleoReconnectResult'),
                                   (0x314,0xc733,'htcleoSendResult')):
    old=f'        HtcleoEcomLog(0x{old_stage:08x}u, {result},\n            (TUint32)aInterfaceUid.iUid);'
    new=f'''        if (htcleoGsSettings)
            HtcleoGsPluginLog(htcleoGsRetryLogCount, 0x{new_stage:04x}u,
                {result}, (TUint32)aInterfaceUid.iUid);
        else
{old}'''
    TRACE_EDITS.append((old,new))
EDITS=((SCOPE,SCOPE_NEW),(CONDITION,CONDITION_NEW),*TRACE_EDITS)

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS ECom create anchor drift: '+repr(old[:100]))
    return text.replace(old,new,1)
def span(text):
    start=text.index(BEGIN);end=text.index(END,start)+len(END)
    return start,end
def transform(text,restore=False):
    if MARKER in text:
        start,end=span(text);block=text[start:end]
        for old,new in reversed(EDITS):block=once(block,new,old)
        text=text[:start]+block+text[end:]
        text=once(text,HEADER+'\n#include "htcleogsplugintrace.inl"',HEADER)
    elif 'htcleogsplugintrace.inl' in text or 'htcleoGsSettings' in text:
        raise ValueError('Partial ECom GS overlay')
    if hashlib.sha256(text.encode('utf-8')).hexdigest()!=BASE_SOURCE:
        raise ValueError('EComSession is not exact825 source')
    if not restore:
        start,end=span(text);block=text[start:end]
        for old,new in EDITS:block=once(block,old,new)
        text=text[:start]+block+text[end:]
        text=once(text,HEADER,HEADER+'\n#include "htcleogsplugintrace.inl"')
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text();new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('Inverse failed')
    if old!=new:path.write_text(new)
    if not a.restore:
        helper=Path(__file__).resolve().parent.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsplugintrace.inl'
        (path.parent/helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_GSAPP_ECOM_CREATE_RETRY='+('restored' if a.restore else
          'GS-create-minus15-one-native-reconnect-C731-C733-real-result-no-empty-fallback'))
if __name__=='__main__':main()

