#!/usr/bin/env python3
"""856: extend the existing single ECom reconnect to font-rasterizer lists only."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp')
BASE_SOURCE='f6f8cbebffb42340cfc5adced847661e55e82c7e2fb2b7a6164efe760e7c2736'
BASE_BINARY='b7eb498a6c35714d5f622cf9cce65ac0337f41805c8b4cf83e399c6e94f3bef5'
MARKER='HTCLEO_FONT_ECOM_LIST_RECONNECT_856'
OLD='\tif(htcleoUiShellList && error == KErrServerTerminated)\n'
NEW='''\t// HTCLEO_FONT_ECOM_LIST_RECONNECT_856: the existing one-reconnect body;
\t// no new success/empty fallback, no plugin destruction or additional loop.
\tif((htcleoUiShellList || aInterfaceUid.iUid == 0x101f7f5du) && error == KErrServerTerminated)
'''
POLICY='font-interface101f7f5d-minus15-one-existing-native-reconnect-real-result-no-failopen'

def transform(text,restore=False):
    if MARKER in text:
        if text.count(NEW)!=1:raise ValueError('partial856 font reconnect')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode()).hexdigest()!=BASE_SOURCE:raise ValueError('856 requires exact retained826 ECom source')
    if not restore:
        if text.count(OLD)!=1:raise ValueError('856 list reconnect anchor drift')
        text=text.replace(OLD,NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text();new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('856 inverse drift')
    if old!=new:path.write_text(new)
    print('HTCLEO_FONT_ECOM_LIST_RECONNECT='+('restored' if a.restore else POLICY))
if __name__=='__main__':main()
