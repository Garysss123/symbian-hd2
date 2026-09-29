#!/usr/bin/env python3
"""846: set only the Settings root's real RWindow background; two init records."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp')
BASE_SOURCE='4e72b80c4e179a0acc82e444c3860f8bbaaeb7e6fb5a346f4e31e190c5df619f'
MARKER='HTCLEO_GS_ROOT_WINDOW_BACKGROUND_846'
ANCHOR='    CreateWindowL(); // Makes this control a window-owning control\n'
BLOCK='''    // HTCLEO_GS_ROOT_WINDOW_BACKGROUND_846
    // This is the already-owned Settings root window, not RootWin/CBA/Home.
    // 60F0 is an application-palette read, NOT a Window Server colour readback.
    HtcleoGsBootLog(0x60f0u, iEikonEnv->ColorList().Count(),
        (TUint32)iEikonEnv->Color(EColorControlBackground).Value());
    Window().SetBackgroundColor(KRgbBlack);
'''
LIST_ANCHOR='    iListBox->SetContainerWindowL( *this );\n'
LIST_BLOCK='''    // HTCLEO_GS_ROOT_LIST_COLOUR_846: once per root construction only.
    // Marker0 means this native getter was reached, not a render/IPC result.
    HtcleoGsBootLog(0x60f1u, 0, (TUint32)iListBox->View()->BackColor().Value());
'''

def transform(text,restore=False):
    if MARKER in text or 'HTCLEO_GS_ROOT_LIST_COLOUR_846' in text:
        if text.count(BLOCK)!=1 or text.count(LIST_BLOCK)!=1:raise ValueError('partial root-background overlay')
        text=text.replace(BLOCK,'',1).replace(LIST_BLOCK,'',1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('root background requires exact845 MainContainer')
    if not restore:
        if text.count(ANCHOR)!=1 or text.count(LIST_ANCHOR)!=1:raise ValueError('ambiguous root window/list construction')
        text=text.replace(ANCHOR,ANCHOR+BLOCK,1).replace(LIST_ANCHOR,LIST_ANCHOR+LIST_BLOCK,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('root background inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_ROOT_WINDOW_BACKGROUND='+('restored' if a.restore else 'owned-root-RWindow-black-60F0-palette-60F1-list-no-draw-loop-or-geometry-change'))

if __name__=='__main__':main()
