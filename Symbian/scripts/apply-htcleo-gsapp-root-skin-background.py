#!/usr/bin/env python3
"""847: disable only the root column list's skin background; disambiguate RGB IDs."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
WINDOW=runpy.run_path(str(HERE/'apply-htcleo-gsapp-window-background.py'))
REL=WINDOW['REL']
BASE_SOURCE='4ae9fe2610d932b4d70119b7e0051511322aa0511ec7751ad14caa303b1cb38e'
MARKER='HTCLEO_GS_ROOT_SKIN_BACKGROUND_847'
# 60F0 is already used by htcleogsheartbeat.inl. Preserve846 historical bytes,
# but move this observation to60F2 so it cannot be mistaken for timer arming.
PALETTE_BLOCK=WINDOW['BLOCK'].replace('60F0','60F2').replace('0x60f0u','0x60f2u')
LIST_BLOCK='''    // HTCLEO_GS_ROOT_SKIN_BACKGROUND_847: only this root list's data.
    CColumnListBoxData* htcleoRootBackgroundData =
        iListBox->ItemDrawer()->ColumnData();
    htcleoRootBackgroundData->SetSkinEnabledL(EFalse);
    // 60F3: local skin-context presence / view RGB; 60F4: drawer flags / RGB.
    // Init-only object values, not pixels or Window Server acknowledgement.
    HtcleoGsBootLog(0x60f3u,
        htcleoRootBackgroundData->SkinBackgroundContext() ? 1 : 0,
        (TUint32)iListBox->View()->BackColor().Value());
    HtcleoGsBootLog(0x60f4u, (TInt)iListBox->ItemDrawer()->Flags(),
        (TUint32)iListBox->ItemDrawer()->BackColor().Value());
'''

def transform(text,restore=False):
    if MARKER in text:
        if text.count(PALETTE_BLOCK)!=1 or text.count(LIST_BLOCK)!=1:
            raise ValueError('partial root-list skin overlay')
        text=text.replace(PALETTE_BLOCK,WINDOW['BLOCK'],1).replace(LIST_BLOCK,WINDOW['LIST_BLOCK'],1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('root-list skin background requires exact846 source')
    if not restore:
        if text.count(WINDOW['BLOCK'])!=1 or text.count(WINDOW['LIST_BLOCK'])!=1:
            raise ValueError('root window observation anchors changed')
        text=text.replace(WINDOW['BLOCK'],PALETTE_BLOCK,1).replace(WINDOW['LIST_BLOCK'],LIST_BLOCK,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('root-list skin inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_ROOT_SKIN_BACKGROUND='+('restored' if a.restore else 'root-column-data-skin-disabled-60F2-60F4-init-only-no-global-skin-change'))

if __name__=='__main__':main()
