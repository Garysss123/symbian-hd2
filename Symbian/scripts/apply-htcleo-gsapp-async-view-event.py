#!/usr/bin/env python3
"""829: native async view event at the root Settings activation call site."""
import argparse
import hashlib
from pathlib import Path
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
NAME='Src/GSMainContainer.cpp'
BASE_SOURCE='1e9bc15776275d9dcc0a0645bd8aa6fa61297798902da35baba5bce41bada71a'
BASE_BINARY='2a33806f404d498eb2f50e1c1dae46a0e2ff0323147c687e4666605367511972'
MARKER='HTCLEO_GS_NATIVE_ASYNC_VIEW_EVENT_829'
OLD='                    iAppUi->ActivateLocalViewL(htcleoViewUid);'
NEW='''                    // HTCLEO_GS_NATIVE_ASYNC_VIEW_EVENT_829
                    // Queue through the native view server; do not wait inside the list callback.
                    // C6 means request returned, not that activation/rendering has completed.
                    iAppUi->CreateActivateViewEventL(
                        TVwsViewId(KUidGS, htcleoViewUid), KNullUid, KNullDesC8);'''
def transform(text,restore=False):
    if MARKER in text:
        if text.count(NEW)!=1:raise ValueError('Async view event overlay drift')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('GSMainContainer is not exact828 source')
    if not restore:
        if text.count(OLD)!=1:raise ValueError('Expected one root view activation')
        text=text.replace(OLD,NEW,1)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('Inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_ASYNC_VIEW_EVENT='+('restored' if a.restore else
          'GS-root-native-CreateActivateViewEventL-no-sync-completion-wait-no-forced-view'))
if __name__=='__main__':main()

