#!/usr/bin/env python3
"""832: include Home in the existing CONE view trace and bracket native deactivation."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
NAME='coevwman.cpp'
BASE_SOURCE='11d61d61a078e95535acb7d49129d02d96383868c1b18664fbbb11ea32678c3b'
BASE_BINARY='98351626248a92a6a6e9a3f25400bb890bbc8851d94e78f8bbeb2b5a758b1b6d'
INC='#include "htcleohomevieweventtrace.inl"\n'
OLD_INC='#include "htcleogsvieweventtrace.inl"\n'
MARKER='HTCLEO_HOME_VIEW_DEACTIVATION_832'
START='void CCoeViewManager::DoDeactivation(const TVwsViewId& aViewId, const TVwsViewId& aActiveViewId, const TVwsViewEvent::TVwsViewEventType aType)\n\t{\n'
INIT="""    // HTCLEO_HOME_VIEW_DEACTIVATION_832
    const TBool htcleoGsViewTrace = HtcleoGsViewEventEligible(RProcess().SecureId().iId);
    TUint htcleoGsViewRecords = 0;
"""
def log(stage,result='KErrNone',detail='0u'):
    return '    if (htcleoGsViewTrace) HtcleoGsViewEventLog(htcleoGsViewRecords, 0x%04xu, %s, %s);\n'%(stage,result,detail)
EDITS=[
 (OLD_INC,INC),
 (START,START+INIT+log(0xc916,'aType','(TUint32)aViewId.iViewUid.iUid')+
  log(0xc917,'aActiveViewId.iAppUid.iUid','(TUint32)aActiveViewId.iViewUid.iUid')),
 ('\tconst TInt numObservers=iViewDeactivationObserverArray.Count();\n',
  '\tconst TInt numObservers=iViewDeactivationObserverArray.Count();\n'+log(0xc918,'numObservers','(TUint32)aViewId.iViewUid.iUid')),
 ('\t\tiViewDeactivationObserverArray[ii]->HandleViewDeactivation(aViewId,aActiveViewId);\n\t\t}\n',
  '\t\tiViewDeactivationObserverArray[ii]->HandleViewDeactivation(aViewId,aActiveViewId);\n\t\t}\n'+log(0xc919,detail='(TUint32)aViewId.iViewUid.iUid')),
 ('\t\tTInt indexToDeactivate=ViewIndex(aViewId);\n',
  '\t\tTInt indexToDeactivate=ViewIndex(aViewId);\n'+log(0xc91a,'indexToDeactivate','(TUint32)aViewId.iViewUid.iUid')),
 ('\t\tiViewArray[indexToDeactivate]->iView.ViewDeactivated();\n',
  log(0xc91b,detail='(TUint32)aViewId.iViewUid.iUid')+
  '\t\tiViewArray[indexToDeactivate]->iView.ViewDeactivated();\n'+log(0xc91c,detail='(TUint32)aViewId.iViewUid.iUid')),
 ('\t}\n\nTVwsViewIdAndMessage CCoeViewManager::HandleScreenDeviceChangedL',
  log(0xc91d,'iActiveViewIndex','(TUint32)iActiveViewId.iViewUid.iUid')+'\t}\n\nTVwsViewIdAndMessage CCoeViewManager::HandleScreenDeviceChangedL'),
]
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('Home view-event anchor drift '+repr(old[:90]))
    return text.replace(old,new,1)
def transform(text,restore=False):
    if INC in text:
        for old,new in reversed(EDITS):text=once(text,new,old)
    elif MARKER in text:raise ValueError('partial Home view trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('CONE differs from exact831 source')
    if not restore:
        for old,new in EDITS:text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('Home view trace inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleohomevieweventtrace.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_HOME_VIEW_EVENT='+('restored' if a.restore else
      'Home-plus-GS-native-view-events-deactivation32-separate-owner-sinks-no-policy-change'))
if __name__=='__main__':main()
