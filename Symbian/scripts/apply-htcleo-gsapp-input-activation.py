#!/usr/bin/env python3
"""828: selection already visible; observe only list notification and activation."""
import argparse
import hashlib
from pathlib import Path
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
BASE_BINARY='357f146ed426b06f5a6ab273c5bea146ebf7be4de622c9615b0004a6bd32b6eb'
NAME='Src/GSMainContainer.cpp'
BASE={NAME:'5b53b012320154b0da7d29b023ff8aac6aa169433ded8e12cd7001831694bd0a'}
MARKER='HTCLEO_GS_LIST_ACTIVATION_828'
LIST_EDITS=(
('#include    "GSMainContainer.h"','#include    "GSMainContainer.h"\n#include "htcleogsboot.h"'),
('''    TListBoxEvent aEventType )
    {
    __GSLOGSTRING1(''','''    TListBoxEvent aEventType )
    {
    // HTCLEO_GS_LIST_ACTIVATION_828
    static TUint htcleoGsListEvents = 0;
    const TBool htcleoTrace = htcleoGsListEvents < 8u;
    if (htcleoTrace)
        {
        ++htcleoGsListEvents;
        HtcleoGsBootLog(0x60c0u, aEventType, (TUint32)aListBox);
        }
    __GSLOGSTRING1('''),
('''            if (aListBox->CurrentItemIndex() < 0)''','''            const TInt htcleoFirstIndex = aListBox->CurrentItemIndex();
            if (htcleoTrace) HtcleoGsBootLog(0x60c1u, htcleoFirstIndex, 0u);
            if (htcleoFirstIndex < 0)'''),
('''            if ( iExt->iDblClickPreventer->IsActive() )''','''            const TBool htcleoBlocked = iExt->iDblClickPreventer->IsActive();
            if (htcleoTrace) HtcleoGsBootLog(0x60c2u, htcleoBlocked, 0u);
            if ( htcleoBlocked )'''),
('''            CGSPluginInterface* selectedPlugin = iVisiblePlugins->operator[](
                    aListBox->CurrentItemIndex());''','''            const TInt htcleoSelectedIndex = aListBox->CurrentItemIndex();
            CGSPluginInterface* selectedPlugin = iVisiblePlugins->operator[](
                    htcleoSelectedIndex);
            if (htcleoTrace) HtcleoGsBootLog(0x60c3u, htcleoSelectedIndex, (TUint32)selectedPlugin);'''),
('''            switch (selectedPlugin->ItemType())''','''            const TInt htcleoItemType = selectedPlugin->ItemType();
            if (htcleoTrace) HtcleoGsBootLog(0x60c4u, htcleoItemType, 0u);
            switch (htcleoItemType)'''),
('''                    iAppUi->ActivateLocalViewL(selectedPlugin->Id());
                    break;''','''                    {
                    const TUid htcleoViewUid = selectedPlugin->Id();
                    if (htcleoTrace) HtcleoGsBootLog(0x60c5u, KErrNone, (TUint32)htcleoViewUid.iUid);
                    iAppUi->ActivateLocalViewL(htcleoViewUid);
                    if (htcleoTrace) HtcleoGsBootLog(0x60c6u, KErrNone, (TUint32)htcleoViewUid.iUid);
                    }
                    break;'''),
)
EDITS={NAME:LIST_EDITS}
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS list anchor drift '+repr(old[:90]))
    return text.replace(old,new,1)
def transform(text,name=NAME,restore=False):
    if MARKER in text:
        for old,new in reversed(EDITS[name]):text=once(text,new,old)
    elif 'htcleoGsListEvents' in text:
        raise ValueError('Partial list witness')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('GS list predecessor drift '+name)
    if not restore:
        for old,new in EDITS[name]:text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('Inverse failed')
        if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_INPUT_ACTIVATION='+('restored' if a.restore else
          'GS-first8-list-events-index-block-type-native-activation-60C0-C6-no-policy-change'))
if __name__=='__main__':main()
