#!/usr/bin/env python3
"""900: bracket the existing Flush/Wait path, without dispatch or flag changes."""
import argparse,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
BASE={'COEMAIN.CPP':'a6b96b977b8d62fa38611ada1864c52b2d407c1de62a190751dcf0eddd7f0d33',
      'htcleoschedulertrace.cpp':'e02054a513a7a70ef9b3c80fc8da1ceb5e06fe782c231b9c6f6e37036ec72b2b'}
HELPER='htcleofmwait900.inl'
INC='#include "'+HELPER+'"\n'
DECL='TUint HtcleoTraceFmWait(CActiveScheduler* aScheduler, CCoeEnv* aEnv, TUint32 aStage, TUint aWindow, TBool aFlush);\n'
OLD='''EXPORT_C void CCoeScheduler::WaitForAnyRequest()
/** Waits for an asynchronous request to complete. */
	{
	HtcleoConeLog(0x434F0100u, KErrNone,
		(TUint32)iCoeEnv->WsSession().Handle());
	iCoeEnv->DoFlush();
	HtcleoConeLog(0x434F0101u, KErrNone,
		(TUint32)iCoeEnv->WsSession().Handle());
	HtcleoConeLog(0x434F0102u, KErrNone, 0u);
	CBaActiveScheduler::WaitForAnyRequest();
	HtcleoTraceReadyAo(this);
	HtcleoConeLog(0x434F0103u, KErrNone, 0u);
	}
'''
NEW='''EXPORT_C void CCoeScheduler::WaitForAnyRequest()
/** Waits for an asynchronous request to complete. */
	{
    const TUint htcleoFmWindow = HtcleoTraceFmWait(this, iCoeEnv, 0xea00u, 0u, Flush());
	HtcleoConeLog(0x434F0100u, KErrNone,
		(TUint32)iCoeEnv->WsSession().Handle());
	iCoeEnv->DoFlush();
    HtcleoTraceFmWait(this, iCoeEnv, 0xea01u, htcleoFmWindow, Flush());
	HtcleoConeLog(0x434F0101u, KErrNone,
		(TUint32)iCoeEnv->WsSession().Handle());
	HtcleoConeLog(0x434F0102u, KErrNone, 0u);
	CBaActiveScheduler::WaitForAnyRequest();
    HtcleoTraceFmWait(this, iCoeEnv, 0xea02u, htcleoFmWindow, Flush());
	HtcleoTraceReadyAo(this);
    HtcleoTraceFmWait(this, iCoeEnv, 0xea03u, htcleoFmWindow, Flush());
	HtcleoConeLog(0x434F0103u, KErrNone, 0u);
	}
'''
def once(text,a,b):
    if text.count(a)!=1:raise ValueError('900 anchor drift '+repr(a[:70]))
    return text.replace(a,b,1)
def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('Wrong900 source')
    if name=='COEMAIN.CPP' and DECL in text:
        text=once(once(text,NEW,OLD),DECL,'')
    if name=='htcleoschedulertrace.cpp' and INC in text:text=once(text,INC,'')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('Not exact899 source '+name)
    if not restore:
        if name=='COEMAIN.CPP':
            text=once(text,'void HtcleoTraceReadyAo(CActiveScheduler* aScheduler);\n','void HtcleoTraceReadyAo(CActiveScheduler* aScheduler);\n'+DECL)
            text=once(text,OLD,NEW)
        else:text=once(text,'#include "htcleofmasync897.inl"\n','#include "htcleofmasync897.inl"\n'+INC)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    prepared=[]
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('900 inverse')
        if not a.restore and transform(new,name)!=new:raise ValueError('900 idempotence')
        prepared.append((path,old,new))
    if not a.restore:(a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    for path,old,new in prepared:
        if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_WAIT_BOUNDARY='+('restored' if a.restore else 'legacy-window35-42-Flush-Wait32-raw-flags-no-policy-change'))
if __name__=='__main__':main()
