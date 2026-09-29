#!/usr/bin/env python3
"""831: GS-only CONE view registration, inbound event and native dispatch witness."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
NAME='coevwman.cpp'
BASE_SOURCE='c264e888f2c884b95d31bf88bacd2aa3c668a0b826724b0a57e35131f16644d5'
BASE_BINARY='a267a5862d864872c067881667703d1c717e70c2e9a1018cddd9162b6dbb845b'
MARKER='HTCLEO_GS_CONE_VIEW_EVENT_831'
INC='#include "htcleogsvieweventtrace.inl"\n'
INIT="""    // HTCLEO_GS_CONE_VIEW_EVENT_831
    const TBool htcleoGsViewTrace = HtcleoGsViewEventEligible(RProcess().SecureId().iId);
    TUint htcleoGsViewRecords = 0;
"""
def log(stage,result='KErrNone',detail='0u'):
    return '    if (htcleoGsViewTrace) HtcleoGsViewEventLog(htcleoGsViewRecords, 0x%04xu, %s, %s);\n'%(stage,result,detail)
EDITS=[('#include <coecntss.h>\n','#include <coecntss.h>\n'+INC)]
for signature in (
 'void CCoeViewManager::RegisterViewL(MCoeView& aView)',
 'void CCoeViewManager::DeregisterView(const MCoeView& aView)',
 'void CCoeViewManager::CreateActivateViewEventL(const TVwsViewId& aViewId,const TUid& aCustomMessageId,const TDesC8& aCustomMessage)',
 'void CCoeViewManager::HandleViewEventL(const TVwsViewEvent& aEvent)',
 'void CCoeViewManager::DoActivationL(const TVwsViewId& aViewId,const TVwsViewId& aPreviousViewId,const TUid& aCustomMessageId,TInt aCustomMessageLength)'):
    start=signature+'\n\t{\n'
    EDITS.append((start,start+INIT))
EDITS += [
 ('\t\tTInt err=iVwsSession->AddView(aView.ViewId());',
  '\t\tconst TVwsViewId htcleoRegisterId = aView.ViewId();\n'+
  log(0xc902,'htcleoRegisterId.iViewUid.iUid','(TUint32)&aView')+
  '\t\tTInt err=iVwsSession->AddView(htcleoRegisterId);\n'+
  log(0xc903,'err','(TUint32)htcleoRegisterId.iViewUid.iUid').rstrip('\n')),
 ('\t\tiVwsSession->RemoveView(aView.ViewId());\t// Ignore error.',
  '\t\tconst TVwsViewId htcleoRemoveId = aView.ViewId();\n'+
  log(0xc904,'htcleoRemoveId.iViewUid.iUid','(TUint32)&aView')+
  '\t\tconst TInt htcleoRemoveResult = iVwsSession->RemoveView(htcleoRemoveId); // Still ignore native error.\n'+
  log(0xc905,'htcleoRemoveResult','(TUint32)htcleoRemoveId.iViewUid.iUid').rstrip('\n')),
 ('\tTInt err = iVwsSession->CreateActivateViewEvent(aViewId,aCustomMessageId,aCustomMessage, iCustomControl);',
  log(0xc900,'aViewId.iAppUid.iUid','(TUint32)aViewId.iViewUid.iUid')+
  '\tTInt err = iVwsSession->CreateActivateViewEvent(aViewId,aCustomMessageId,aCustomMessage, iCustomControl);\n'+
  log(0xc901,'err','(TUint32)aViewId.iViewUid.iUid').rstrip('\n')),
 (INIT+'\tswitch (aEvent.iEventType)\n',
  INIT+log(0xc906,'aEvent.iEventType','(TUint32)aEvent.iViewOneId.iViewUid.iUid')+
  log(0xc907,'aEvent.iViewOneId.iAppUid.iUid','(TUint32)aEvent.iViewTwoId.iAppUid.iUid')+
  log(0xc908,'aEvent.iViewTwoId.iViewUid.iUid','(TUint32)aEvent.iCustomMessageLength')+
  '\tswitch (aEvent.iEventType)\n'),
 ('\t\tiViewObserverArray[ii]->HandleViewEventL(aEvent);\n\t\t}\n\t}',
  '\t\tiViewObserverArray[ii]->HandleViewEventL(aEvent);\n\t\t}\n'+
  log(0xc909,'aEvent.iEventType','(TUint32)aEvent.iViewOneId.iViewUid.iUid')+'\t}'),
 ('\t// Retrieve custom message from server if necessary.\n',
  log(0xc90a,'aPreviousViewId.iViewUid.iUid','(TUint32)aViewId.iViewUid.iUid')+
  '\t// Retrieve custom message from server if necessary.\n'),
 ('\tTInt indexToActivate=ViewIndex(aViewId);\n',
  '\tTInt indexToActivate=ViewIndex(aViewId);\n'+log(0xc90b,'indexToActivate','(TUint32)aViewId.iViewUid.iUid')),
 ('\tCCoeView& viewToActivate=*(iViewArray[indexToActivate]);\n',
  '\tCCoeView& viewToActivate=*(iViewArray[indexToActivate]);\n'+log(0xc90c,'viewToActivate.iConstructed','(TUint32)&viewToActivate.iView')),
 ('\t\tviewToActivate.iView.ViewConstructL();\n',
  log(0xc90d,detail='(TUint32)aViewId.iViewUid.iUid')+'\t\tviewToActivate.iView.ViewConstructL();\n'+log(0xc90e,detail='(TUint32)aViewId.iViewUid.iUid')),
 ('\tviewToActivate.iView.PrepareForViewActivation();\n',
  log(0xc90f,detail='(TUint32)aViewId.iViewUid.iUid')+'\tviewToActivate.iView.PrepareForViewActivation();\n'+log(0xc910,detail='(TUint32)aViewId.iViewUid.iUid')),
 ('\tconst TInt screenMode=iCoeEnv.ScreenDevice()->CurrentScreenMode();\n\tif (!viewToActivate',
  '\tconst TInt screenMode=iCoeEnv.ScreenDevice()->CurrentScreenMode();\n'+log(0xc911,'screenMode','(TUint32)aViewId.iViewUid.iUid')+'\tif (!viewToActivate'),
 ('\tiActivatingViewId = aViewId;\n\t// Do the activation.',
  log(0xc912,'screenMode','(TUint32)aViewId.iViewUid.iUid')+
  '\tiActivatingViewId = aViewId;\n'+log(0xc913,detail='(TUint32)&viewToActivate.iView')+'\t// Do the activation.'),
 ('\tCompleteActivation(indexToActivate,aViewId,aPreviousViewId);\n',
  log(0xc914,detail='(TUint32)aViewId.iViewUid.iUid')+
  '\tCompleteActivation(indexToActivate,aViewId,aPreviousViewId);\n'+log(0xc915,detail='(TUint32)aViewId.iViewUid.iUid')),
]
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('CONE view-event anchor drift: '+repr(old[:90]))
    return text.replace(old,new,1)
def transform(text,restore=False):
    if INC in text:
        for old,new in reversed(EDITS):text=once(text,new,old)
    elif MARKER in text:raise ValueError('partial CONE view trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('CONE view manager differs from exact830 source')
    if not restore:
        for old,new in EDITS:text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('CONE view-event inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsvieweventtrace.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_GSAPP_CONE_VIEW_EVENT='+('restored' if a.restore else
      'GS-only-registration-inbound-dispatch32-native-policy-no-new-trap'))
if __name__=='__main__':main()
