#!/usr/bin/env python3
"""845: request Avkon's native static-background mode in Settings only."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSUi.cpp')
BASE_SOURCE='91e40d38b9508d65bab4495093ae7fb0357a943d6cde480f66a1727a3265d87e'
MARKER='HTCLEO_GS_STATIC_BACKGROUND_845'
BEFORE='    BaseConstructL( EAknEnableSkin | EAknEnableMSK |EAknSingleClickCompatible );\n'
AFTER='''    // HTCLEO_GS_STATIC_BACKGROUND_845: keep skin/MSK/single-click;
    // use Avkon's static background instead of animation alpha clearing.
    BaseConstructL( EAknEnableSkin | EAknEnableMSK |EAknSingleClickCompatible |
                    EAknDisableAnimationBackground );
'''

def transform(text,restore=False):
    if MARKER in text:
        if text.count(AFTER)!=1:raise ValueError('partial static-background flag overlay')
        text=text.replace(AFTER,BEFORE,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('static background requires exact844 GSUi source')
    if not restore:
        if text.count(BEFORE)!=1:raise ValueError('ambiguous BaseConstructL call')
        text=text.replace(BEFORE,AFTER,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('static flag inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_STATIC_BACKGROUND='+('restored' if a.restore else 'native-EAknDisableAnimationBackground-skin-MSK-singleclick-retained'))

if __name__=='__main__':main()
