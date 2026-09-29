#!/usr/bin/env python3
"""827: extend existing first-two plugin-loader observation to General's children."""
import argparse
import hashlib
from pathlib import Path
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSFramework')
NAME=Path('src/GSPluginLoader.cpp')
BASE_SOURCE='beb92fbc61171159457fbef8b812da53cdb5839fb96232500d7a4e3348248a49'
BASE_BINARY='1c9e75f7b6cd5a6cb00de8fba2fc4830e73d701ddacbf4f86bf685100ea357b5'
MARKER='HTCLEO_GS_GENERAL_CHILD_FRONTIER_827'
HEADER='#include "htcleogsplugintrace.inl"'
HELPER='''
// HTCLEO_GS_GENERAL_CHILD_FRONTIER_827
static TBool HtcleoGsRootOrGeneralEligible(TUint32 aParent, TInt aRound, TUint32 aSid)
    {
    return HtcleoGsPluginEligible(aParent, aRound, aSid) ||
        (aParent == 0x10207237u && aRound >= 1 && aRound <= 2 &&
         aSid == 0x100058ecu);
    }
'''
OLD_CALL='const TBool htcleoTrace = HtcleoGsPluginEligible('
NEW_CALL='const TBool htcleoTrace = HtcleoGsRootOrGeneralEligible('
ENTRY='    if (htcleoTrace) HtcleoGsPluginLog(htcleoTraceCount, 0xc700u, iRunLDebugCount, (TUint32)iImplInfoArray.Count());'
NEW_ENTRY='''    if (htcleoTrace && iParentUid.iUid == 0x10207237)
        HtcleoGsPluginLog(htcleoTraceCount, 0xc734u, iStatus.Int(), (TUint32)iParentUid.iUid);
'''+ENTRY

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS child anchor drift')
    return text.replace(old,new,1)
def transform(text,restore=False):
    if MARKER in text:
        text=once(text,HEADER+HELPER,HEADER)
        text=once(text,NEW_ENTRY,ENTRY)
        if text.count(NEW_CALL)!=3:raise ValueError('Expected three child gates')
        text=text.replace(NEW_CALL,OLD_CALL)
    elif 'HtcleoGsRootOrGeneralEligible' in text or '0xc734u' in text:
        raise ValueError('Partial child witness')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('GSPluginLoader is not exact826 source')
    if not restore:
        text=once(text,HEADER,HEADER+HELPER)
        text=once(text,ENTRY,NEW_ENTRY)
        if text.count(OLD_CALL)!=3:raise ValueError('Three original gates expected')
        text=text.replace(OLD_CALL,NEW_CALL)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('Inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_CHILD_FRONTIER='+('restored' if a.restore else
          'GS-root-and-General-first2-C734-parent-no-loading-policy-change'))
if __name__=='__main__':main()

