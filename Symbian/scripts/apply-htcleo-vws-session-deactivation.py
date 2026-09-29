#!/usr/bin/env python3
"""838: native per-session deactivation delivery/ack trace; no session policy changes."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/appsupport/appfw/viewserver')
NAME='server/VWSSEVNT.CPP'
BASE_SOURCE='16e5f0575114778a468053dd29a50ec899a12cd8b32aa7fb1d3de1ec754eb5ee'
BASE_BINARY='584f712ac727a64a871cfde2c876a08af9e8c2d8ed78341d44e27593fea5d561'
INC='#include "htcleovwssessiontrace.inl"\n'
INIT="""    // HTCLEO_VWS_SESSION_DEACTIVATION_838
    const TUint32 htcleoApp = (TUint32)iViewId.iAppUid.iUid;
    const TUint32 htcleoView = (TUint32)iViewId.iViewUid.iUid;
    const TUint32 htcleoEvent = (TUint32)this;
    const TBool htcleoTrace = HtcleoVwsSessionEligible(htcleoApp);
    TUint htcleoRecords = 0;
"""
def log(stage,result='KErrNone',detail='0u'):
    return '    if (htcleoTrace) HtcleoVwsSessionLog(htcleoRecords, 0x%04xu, %s, %s, htcleoApp, htcleoView, htcleoEvent);\n'%(stage,result,detail)
OPEN='\n\t{\n'
CTOR='CVwsSessionEvent_Deactivation::CVwsSessionEvent_Deactivation('
DTOR='CVwsSessionEvent_Deactivation::~CVwsSessionEvent_Deactivation()'
PROCESS='void CVwsSessionEvent_Deactivation::ProcessEventL()'
REQUEST='void CVwsSessionEvent_Deactivation::HandleViewEventRequestL('
SEND='void CVwsSessionEvent_Deactivation::RequestDeactivationL()'
COMPLETE='void CVwsSessionEvent_Deactivation::Complete('
NEXT='CVwsSessionEvent_ScreenDeviceChangeNotification::CVwsSessionEvent_ScreenDeviceChangeNotification('
REGIONS=[
 (CTOR,DTOR,[(OPEN+'\t}',OPEN+INIT+
   log(0xde00,'iActiveViewId.iAppUid.iUid','(TUint32)iActiveViewId.iViewUid.iUid')+
   log(0xde01,'(TInt)iObserver','(TUint32)&iSession')+'\t}')]),
 (PROCESS,REQUEST,[(OPEN,OPEN+INIT),
   ('\tif (iSession.State()==CVwsSession::EClientRequestPending)',
    '\tconst TInt htcleoSessionState = iSession.State();\n'+log(0xde02,'iState','(TUint32)htcleoSessionState')+
    '\tif (htcleoSessionState==CVwsSession::EClientRequestPending)'),
   ('\t\tiState=EWaitingForClientViewEventRequest;',
    '\t\tiState=EWaitingForClientViewEventRequest;\n'+log(0xde03,'iState','(TUint32)htcleoSessionState').rstrip('\n'))]),
 (REQUEST,SEND,[(OPEN,OPEN+INIT+log(0xde04,'aError','(TUint32)iState'))]),
 (SEND,COMPLETE,[(OPEN,OPEN+INIT+log(0xde05,'iDifferentInstanceOfSameApp','(TUint32)&iSession')),
   ('\tiState=EWaitingForAcknowledgementOfDeactivation;',
    '\tiState=EWaitingForAcknowledgementOfDeactivation;\n'+log(0xde06,'iState','(TUint32)&iSession').rstrip('\n'))]),
 (COMPLETE,NEXT,[(OPEN,OPEN+INIT+
    log(0xde08,'aError','(TUint32)iState')+log(0xde09,'(TInt)iObserver','(TUint32)&iSession'))]),
]
def once(t,a,b):
    if t.count(a)!=1:raise ValueError('Session deactivation anchor drift '+repr(a[:90]))
    return t.replace(a,b,1)
def region(text,start,end,edits,restore=False):
    a=text.index(start);b=text.index(end,a);body=text[a:b]
    for old,new in (reversed(edits) if restore else edits):
        body=once(body,new,old) if restore else once(body,old,new)
    return text[:a]+body+text[b:]
def transform(text,restore=False):
    if INC in text:
        for start,end,edits in reversed(REGIONS):text=region(text,start,end,edits,True)
        text=once(text,INC,'')
    elif 'HTCLEO_VWS_SESSION_DEACTIVATION_838' in text:raise ValueError('partial session trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:raise ValueError('not exact837 session event source')
    if not restore:
        anchor='#include "VWSDEBUG.H"\n';text=once(text,anchor,anchor+INC)
        for start,end,edits in REGIONS:text=region(text,start,end,edits)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('session trace inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleovwssessiontrace.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_VWS_SESSION_DEACTIVATION='+('restored' if a.restore else
      'UI-session-deactivation-created-processing-send-ack32-no-policy-change'))
if __name__=='__main__':main()
