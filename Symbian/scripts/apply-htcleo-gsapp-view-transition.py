#!/usr/bin/env python3
"""830 observe GS enqueue and already-active-view ActivationTick, no behavior changes."""
import argparse
import hashlib
from pathlib import Path
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='AknViewAppUi.cpp'
BASE_SOURCE='b9f62b7438fb5900616282951159e2146dcfc40b41e8b16d7e215740734a9505'
BASE_BINARY='0641822ec8df81d9de7fbe556d54ce0cb99912ec6f4cbbd744c9f20ac54d8776'
MARKER='HTCLEO_GS_VIEW_ENQUEUE_TRANSITION_830'
OLD_SCOPE='''    const TBool htcleoGsActivationTrace = HtcleoGsActivationEligible(
        RProcess().SecureId().iId, iView != NULL);'''
NEW_SCOPE='''    // HTCLEO_GS_VIEW_ENQUEUE_TRANSITION_830
    // ActivationTick is view-event driven, not a periodic redraw callback.
    const TBool htcleoGsActivationTrace = (RProcess().SecureId().iId == 0x100058ecu);'''
OLD_ENQUEUE='''void CAknViewAppUi::ViewActivatedL( CAknView* aView, const TVwsViewId& aPrevViewId, TUid aCustomMessageId, const TDesC8& aCustomMessage )
\t{
\tCViewActivationItem* activation( CViewActivationItem::NewLC( aView, aCustomMessageId, aCustomMessage, aPrevViewId ) );
\tiActivationQueue->AppendL( activation );
\tCleanupStack::Pop(); // activation
\tQueueActivationTick();
\t}'''
NEW_ENQUEUE='''void CAknViewAppUi::ViewActivatedL( CAknView* aView, const TVwsViewId& aPrevViewId, TUid aCustomMessageId, const TDesC8& aCustomMessage )
\t{
    // HTCLEO_GS_VIEW_ENQUEUE_TRANSITION_830
    const TBool htcleoGsQueueTrace = (RProcess().SecureId().iId == 0x100058ecu);
    TUint htcleoGsQueueRecords = 0;
    const TUint32 htcleoViewAddress = (TUint32)aView;
    const TInt htcleoViewUid = htcleoGsQueueTrace && aView ? aView->Id().iUid : 0;
    if (htcleoGsQueueTrace) HtcleoGsActivationLog(htcleoGsQueueRecords, 0xc603u, htcleoViewUid, htcleoViewAddress);
\tCViewActivationItem* activation( CViewActivationItem::NewLC( aView, aCustomMessageId, aCustomMessage, aPrevViewId ) );
    if (htcleoGsQueueTrace) HtcleoGsActivationLog(htcleoGsQueueRecords, 0xc604u, KErrNone, (TUint32)activation);
\tiActivationQueue->AppendL( activation );
\tCleanupStack::Pop(); // activation
\tQueueActivationTick();
    if (htcleoGsQueueTrace) HtcleoGsActivationLog(htcleoGsQueueRecords, 0xc607u, htcleoViewUid, htcleoViewAddress);
\t}'''
EDITS=((OLD_SCOPE,NEW_SCOPE),(OLD_ENQUEUE,NEW_ENQUEUE))
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS transition anchor drift')
    return text.replace(old,new,1)
def transform(text,restore=False):
    if MARKER in text:
        for old,new in reversed(EDITS):text=once(text,new,old)
    elif 'htcleoGsQueueTrace' in text:raise ValueError('partial queue trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('Avkon ViewAppUi not exact829 source')
    if not restore:
        for old,new in EDITS:text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_VIEW_TRANSITION='+('restored' if a.restore else
          'GS-enqueue-C603-C604-C607-all-GS-native-ActivationTick64-no-policy-change'))
if __name__=='__main__':main()

