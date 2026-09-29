#!/usr/bin/env python3
"""850: root-only opaque1x1 bitmap fill, retain849 native foreground/witness."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
PAINT=runpy.run_path(str(HERE/'apply-htcleo-gsapp-root-paint-witness.py'))
REL=PAINT['REL']
BASE_SOURCE='9b356b1b0372455e1d6ff936305f0f17b2846d484bb815669aa986242cee2a2f'
MARKER='HTCLEO_GS_ROOT_BITMAP_BACKGROUND_850'
INCLUDE='#include    <eikclbd.h>\n'
INCLUDE_NEW=INCLUDE+'#include    <fbs.h>\n'
OLD=PAINT['NEW']
PREPARE='''    // HTCLEO_GS_ROOT_BITMAP_BACKGROUND_850
    CHtcleoGsRootListView() : iPaintWitness(0), iBlackBitmap(NULL) {}
    virtual ~CHtcleoGsRootListView() { delete iBlackBitmap; }
    TInt PrepareBlackBitmap()
        {
        // Optional appearance asset. Failure retains849's existing rectangle
        // path; it must not prevent Settings from opening.
        TRAPD(error, iBlackBitmap = new(ELeave) CFbsBitmap);
        if (error == KErrNone)
            error = iBlackBitmap->Create(TSize(1, 1), EColor64K);
        if (error == KErrNone)
            {
            iBlackBitmap->BeginDataAccess();
            TUint32* data = iBlackBitmap->DataAddress();
            if (data)
                *reinterpret_cast<TUint16*>(data) = 0; // opaque RGB565 black
            else
                error = KErrCorrupt;
            iBlackBitmap->EndDataAccess();
            }
        if (error != KErrNone)
            {
            delete iBlackBitmap;
            iBlackBitmap = NULL;
            }
        return error;
        }
'''
NEW=OLD.replace('    CHtcleoGsRootListView() : iPaintWitness(0) {}\n',PREPARE,1).replace(
'''        iGc->DrawRect(iViewRect);''','''        if (iBlackBitmap)
            iGc->DrawBitmap(iViewRect, iBlackBitmap);
        else
            iGc->DrawRect(iViewRect);''',1).replace(
'''    mutable TUint iPaintWitness;
''','''    mutable TUint iPaintWitness;
    CFbsBitmap* iBlackBitmap;
''',1).replace(
'''        HtcleoGsBootLog(0x60f5u, (TInt)view, 0x1020723bu);
        return view;''','''        HtcleoGsBootLog(0x60f5u, (TInt)view, 0x1020723bu);
        const TInt bitmapResult = view->PrepareBlackBitmap();
        HtcleoGsBootLog(0x60fcu, bitmapResult, (TUint32)view);
        return view;''',1).replace(
'sizeof(CAknColumnListBoxView) + sizeof(TUint)',
'sizeof(CAknColumnListBoxView) + sizeof(TUint) + sizeof(CFbsBitmap*)',1)

def transform(text,restore=False):
    if MARKER in text:
        if text.count(NEW)!=1 or text.count(INCLUDE_NEW)!=1:raise ValueError('partial850 bitmap overlay')
        text=text.replace(NEW,OLD,1).replace(INCLUDE_NEW,INCLUDE,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('850 requires exact849 root source')
    if not restore:
        if text.count(OLD)!=1 or text.count(INCLUDE)!=1:raise ValueError('ambiguous849 root owner')
        text=text.replace(OLD,NEW,1).replace(INCLUDE,INCLUDE_NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('850 inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_ROOT_BITMAP_BACKGROUND='+('restored' if a.restore else 'root-owned-1x1-RGB565-black-DrawBitmap-native-foreground-fallback-on-allocation-error'))

if __name__=='__main__':main()
