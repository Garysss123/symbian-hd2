#!/usr/bin/env python3
"""837: UI-targeted server activation/ack/timeout evidence, no state-machine changes."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/appsupport/appfw/viewserver')
NAME='server/VWSEVENT.CPP'
BASE_SOURCE='14a07b3d7375b7878ae621ec640ae7d2676f6ebae9f7134cc43b41e11bd71204'
BASE_BINARY='ae4830b49adcb30d63ce5d3f58981d930d3dd80da157d784a107bd23d687a982'
INC='#include "htcleovwsservereventtrace.inl"\n'
INIT="""    // HTCLEO_VWS_SERVER_EVENT_837
    const TUint32 htcleoApp = (TUint32)iViewIdToActivate.iAppUid.iUid;
    const TUint32 htcleoView = (TUint32)iViewIdToActivate.iViewUid.iUid;
    const TUint32 htcleoEvent = (TUint32)this;
    const TBool htcleoTrace = HtcleoVwsServerEligible(htcleoApp);
    TUint htcleoRecords = 0;
"""
def log(stage,result='KErrNone',detail='0u'):
    return '    if (htcleoTrace) HtcleoVwsServerLog(htcleoRecords, 0x%04xu, %s, %s, htcleoApp, htcleoView, htcleoEvent);\n'%(stage,result,detail)
EDITS=[]
def region(text,start,end,edits,restore=False):
    a=text.index(start);b=text.index(end,a)
    body=text[a:b]
    for old,new in (reversed(edits) if restore else edits):
        body=once(body,new,old) if restore else once(body,old,new)
    return text[:a]+body+text[b:]
CTOR='CVwsServerEvent_Activate::CVwsServerEvent_Activate('
DTOR='CVwsServerEvent_Activate::~CVwsServerEvent_Activate()'
TIMEOUT='void CVwsServerEvent_Activate::HandleTimeOut('
PROCESS='void CVwsServerEvent_Activate::ProcessEventL()'
CALLBACK='#ifdef _DEBUG\nvoid CVwsServerEvent_Activate::RequestCompleted'
NOW='void CVwsServerEvent_Activate::NowObserving'
NEWVIEW='void CVwsServerEvent_Activate::RequestActivateNewView()'
SYSTEM='void CVwsServerEvent_Activate::RequestActivateSystemDefaultView()'
CLIENT='TInt CVwsServerEvent_Activate::RequestClientActivation('
CROSS='void CVwsServerEvent_Activate::CustomCrossCheck'
DOREQ='void CVwsServerEvent_Activate::DoRequestActivateNewView('
DEACT='void CVwsServerEvent_Activate::RequestDeactivateOldView()'
COMPLETE='void CVwsServerEvent_Activate::Complete(TInt aError)'
REMOVAL='void CVwsServerEvent_Activate::HandleSessionRemoval'
OPEN='\n\t{\n'
REGIONS=[
 (CTOR,DTOR,[(OPEN+'\t}',OPEN+INIT+log(0xcd00,'aCompleteRequest','(TUint32)TUint(aClientThreadId)')+'\t}')]),
 (TIMEOUT,PROCESS,[
   (OPEN,OPEN+INIT+log(0xcd02,'aTimeOut','(TUint32)iState')+log(0xcd03,'iCompleteRequest','(TUint32)TUint(iClientThreadId)')),
   ('\t\t\t\tiMessage.Complete(KErrNone);',log(0xcd04,'iState','(TUint32)iCompleteRequest')+'\t\t\t\tiMessage.Complete(KErrNone);')]),
 (PROCESS,CALLBACK,[(OPEN,OPEN+INIT+log(0xcd01,'iState','(TUint32)iCompleteRequest'))]),
 (CALLBACK,NOW,[(OPEN,OPEN+INIT+log(0xcd05,'aError','(TUint32)iState'))]),
 (NEWVIEW,SYSTEM,[
   (OPEN,OPEN+INIT+log(0xcd08,'iState','(TUint32)TUint(iClientThreadId)')),
   ('\tif (sessionWithNewView==NULL || (sessionWithNewView && sessionWithNewView->IsExiting()))',
    log(0xcd09,'KErrNone','(TUint32)sessionWithNewView')+'\tif (sessionWithNewView==NULL || (sessionWithNewView && sessionWithNewView->IsExiting()))')]),
 (CLIENT,CROSS,[
   (OPEN,OPEN+INIT+log(0xcd10,'aNewState','(TUint32)&aSession')),
   ('\tif (error)\n',log(0xcd11,'error','(TUint32)aNewState')+'\tif (error)\n'),
   ('\t\tiState=aNewState;','\t\tiState=aNewState;\n'+log(0xcd12,'iState','(TUint32)&aSession').rstrip('\n'))]),
 (DOREQ,DEACT,[
   (OPEN,OPEN+INIT+log(0xcd14,'iState','(TUint32)TUint(iNewViewClientThreadId)')),
   ('\tiEventTimer->Start(this,EFalse);',log(0xcd15,'iState','(TUint32)iEventTimer')+'\tiEventTimer->Start(this,EFalse);'),
   ('\tif (iServer.CheckViewExists(aSessionWithNewView.ClientThreadId(),iViewIdToActivate)==KErrNotFound)',
    '\tconst TInt htcleoExists = iServer.CheckViewExists(aSessionWithNewView.ClientThreadId(),iViewIdToActivate);\n'+log(0xcd16,'htcleoExists','(TUint32)iViewIdToActivate.iViewUid.iUid')+'\tif (htcleoExists==KErrNotFound)')]),
 (DEACT,COMPLETE,[
   (OPEN,OPEN+INIT+log(0xcd20,'iState','(TUint32)iCompleteRequest')),
   ('\tif (viewToDeactivate.iAppUid.iUid &&',
    log(0xcd21,'viewToDeactivate.iAppUid.iUid','(TUint32)viewToDeactivate.iViewUid.iUid')+
    log(0xcd22,'(TInt)sessionWithOldView','(TUint32)sessionWithNewView')+'\tif (viewToDeactivate.iAppUid.iUid &&'),
   ('\t\t\tTRAPD(err,sessionWithOldView->RequestClientDeactivationL(*this,viewToDeactivate,iViewIdToActivate, differentInstanceOfSameApp));',
    log(0xcd23,'differentInstanceOfSameApp','(TUint32)sessionWithOldView')+
    '\t\t\tTRAPD(err,sessionWithOldView->RequestClientDeactivationL(*this,viewToDeactivate,iViewIdToActivate, differentInstanceOfSameApp));\n'+
    log(0xcd24,'err','(TUint32)sessionWithOldView').rstrip('\n')),
   ('\t\t\t\tiState=EDeactivationRequested;','\t\t\t\tiState=EDeactivationRequested;\n'+log(0xcd25,'iState','(TUint32)sessionWithOldView').rstrip('\n'))]),
 (COMPLETE,REMOVAL,[
   (OPEN,OPEN+INIT+log(0xcd30,'aError','(TUint32)iState')+log(0xcd31,'iCompleteRequest','(TUint32)TUint(iClientThreadId)')),
   ('\tReportEventProcessed();',log(0xcd32,'aError','0u')+'\tReportEventProcessed();')]),
]
def once(text,a,b):
    if text.count(a)!=1:raise ValueError('Server event anchor drift '+repr(a[:80]))
    return text.replace(a,b,1)
def transform(text,restore=False):
    if INC in text:
        for start,end,edits in reversed(REGIONS):text=region(text,start,end,edits,True)
        text=once(text,INC,'')
    elif 'HTCLEO_VWS_SERVER_EVENT_837' in text:raise ValueError('partial server event trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:raise ValueError('not exact836 server event source')
    if not restore:
        # The include follows all native includes to keep CActive/TThreadId definitions available.
        anchor='#include "vwspatchdata.h"\n'
        text=once(text,anchor,anchor+INC)
        for start,end,edits in REGIONS:text=region(text,start,end,edits)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('Server event inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleovwsservereventtrace.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_VWS_SERVER_EVENT='+('restored' if a.restore else
       'Home-GS-Matrix-activation-ack-timeout-complete32-no-state-policy-change'))
if __name__=='__main__':main()
