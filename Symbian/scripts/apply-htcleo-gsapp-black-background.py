#!/usr/bin/env python3
"""843: Settings-local dark palette only; no global scheme, file I/O or UI policy."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
NAME='Src/GSUi.cpp'
BASE_SOURCE='aeea30d09de850cb6fa75d0cddc02c02ee5f4a9ed0ab3c56784cb193123379c6'
BASE_BINARY='4a326826636fd435b4c53eb6beb841584f70f514d6cbc4401d5b467d9207f86c'
MARKER='HTCLEO_GS_LOCAL_BLACK_BACKGROUND_843'
ANCHOR='    BaseConstructL( EAknEnableSkin | EAknEnableMSK |EAknSingleClickCompatible );\n'
BLOCK='''    // HTCLEO_GS_LOCAL_BLACK_BACKGROUND_843
    // This is this application's private palette, not the persisted system
    // colour scheme. Keep all highlight/dimmed/CBA-specific colour slots.
    CColorList& htcleoGsColors = iEikonEnv->ColorList();
    if (htcleoGsColors.Count() > EColorControlText)
        {
        htcleoGsColors.SetColor(EColorWindowBackground, KRgbBlack);
        htcleoGsColors.SetColor(EColorWindowText, KRgbWhite);
        htcleoGsColors.SetColor(EColorControlBackground, KRgbBlack);
        htcleoGsColors.SetColor(EColorControlText, KRgbWhite);
        }
'''

def transform(text,restore=False):
    if MARKER in text:
        if text.count(BLOCK)!=1: raise ValueError('partial Settings palette overlay')
        text=text.replace(BLOCK,'',1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('Settings UI source is not exact842 predecessor')
    if not restore:
        if text.count(ANCHOR)!=1: raise ValueError('ambiguous Settings BaseConstructL')
        text=text.replace(ANCHOR,ANCHOR+BLOCK,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True): raise ValueError('palette inverse failed')
    if new!=old:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_LOCAL_BLACK_BACKGROUND='+('restored' if a.restore else 'GS-private-window-control-black-white-palette-no-global-storage-or-UI-policy'))

if __name__=='__main__':main()
