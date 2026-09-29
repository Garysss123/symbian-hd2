#!/usr/bin/env python3
"""834: observe the native VWS client event request/dispatch/re-arm/cancel for Home/GS."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/appsupport/appfw/viewserver')
BASE_BINARY='946ca0c4353b21cc59c8f6adaf16370264019a85d5716c10a80f47751764c0e8'
BASE={'client/VIEWCLI.CPP':'b93f4bf51233616fd55731becf3b6b53c952bf333860a4b9ff69d3f72c082b6f',
      'group/VIEWCLI.MMP':'a9fc49e56f94f538bf2beed0191861e7128a0ce27d4f5756eaf59b4e805b9fae'}
INC='#include "htcleovwsclienttrace.inl"\n'
INIT="""    // HTCLEO_VWS_CLIENT_QUEUE_834
    const TBool htcleoVwsTrace = HtcleoVwsClientEligible(RProcess().SecureId().iId);
    TUint htcleoVwsRecords = 0;
"""
def log(stage,result='KErrNone',detail='(TUint32)this'):
    return '    if (htcleoVwsTrace) HtcleoVwsClientLog(htcleoVwsRecords, 0x%04xu, %s, %s);\n'%(stage,result,detail)
QUEUE_OLD="""void CVwsSessionEventHandler::Queue()
	{
	ASSERT(!IsActive());

	if (iDoActivationNextQueue)
		{
		iDoActivationNextQueue=EFalse;
		iVwsSession.RequestViewEvent(iViewEventBuf,iLastError,iViewActivationBuf,iCustomMessage,iStatus);
		}
	else
		{
		iVwsSession.RequestViewEvent(iViewEventBuf,iLastError,iStatus);
		}
	SetActive();
	}
"""
QUEUE_NEW="""void CVwsSessionEventHandler::Queue()
	{
"""+INIT+log(0xca00,'IsActive() ? 1 : 0')+"""
	ASSERT(!IsActive());
"""+log(0xca01,'iLastError','(TUint32)iVwsSession.Handle()')+"""
	if (iDoActivationNextQueue)
		{
		iDoActivationNextQueue=EFalse;
"""+log(0xca05,'1')+"""
		iVwsSession.RequestViewEvent(iViewEventBuf,iLastError,iViewActivationBuf,iCustomMessage,iStatus);
		}
	else
		{
"""+log(0xca05,'0')+"""
		iVwsSession.RequestViewEvent(iViewEventBuf,iLastError,iStatus);
		}
"""+log(0xca02,'iStatus.Int()')+"""
	SetActive();
"""+log(0xca03,'iStatus.Int()')+"""
	}
"""
RUN_OLD="""void CVwsSessionEventHandler::RunL()
	{
	TRAP(iLastError,iObserver.HandleViewEventL(iViewEventBuf()));
	Queue();
	}
"""
RUN_NEW="""void CVwsSessionEventHandler::RunL()
	{
"""+INIT+log(0xca10,'iStatus.Int()')+"""
    // Do not read uninitialised/stale event contents for an error completion.
    if (htcleoVwsTrace && iStatus.Int() == KErrNone)
        HtcleoVwsClientLog(htcleoVwsRecords, 0xca11u,
            iViewEventBuf().iEventType, (TUint32)iViewEventBuf().iViewOneId.iViewUid.iUid);
	TRAP(iLastError,iObserver.HandleViewEventL(iViewEventBuf()));
"""+log(0xca12,'iLastError')+"""
	Queue();
"""+log(0xca13,'IsActive() ? 1 : 0')+"""
	}
"""
CANCEL_OLD="""void CVwsSessionEventHandler::DoCancel()
	{
	iVwsSession.RequestViewEventCancel();
	}
"""
CANCEL_NEW="""void CVwsSessionEventHandler::DoCancel()
	{
"""+INIT+log(0xca18,'iStatus.Int()')+"""
	iVwsSession.RequestViewEventCancel();
"""+log(0xca19,'iStatus.Int()')+"""
	}
"""
EDITS={'client/VIEWCLI.CPP':[
 ('#include "VWSERVER.H"\n','#include "VWSERVER.H"\n'+INC),
 (QUEUE_OLD,QUEUE_NEW),(RUN_OLD,RUN_NEW),(CANCEL_OLD,CANCEL_NEW)],
 'group/VIEWCLI.MMP':[('LIBRARY        euser.lib viewsrv.lib','LIBRARY        euser.lib viewsrv.lib\nLIBRARY        efsrv.lib // HTCLEO_VWS_CLIENT_QUEUE_834')]}
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('VWS client anchor drift '+repr(old[:85]))
    return text.replace(old,new,1)
def transform(text,name,restore=False):
    if 'HTCLEO_VWS_CLIENT_QUEUE_834' in text:
        for old,new in reversed(EDITS[name]):text=once(text,new,old)
    elif 'htcleovwsclienttrace.inl' in text:raise ValueError('partial VWS trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('VWS input not exact833 '+name)
    if not restore:
        for old,new in EDITS[name]:text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('VWS inverse failed')
        if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleovwsclienttrace.inl'
        (a.root/REL/'client'/helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_VWS_CLIENT_QUEUE='+('restored' if a.restore else
      'Home-GS-native-request-RunL-rearm-cancel32-no-recovery-no-new-timer'))
if __name__=='__main__':main()
