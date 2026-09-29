#!/usr/bin/env python3
"""849: bounded first-paint witness; retain848 drawing/input behavior."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'apply-htcleo-gsapp-root-background-owner.py'))
REL=OWNER['REL']
BASE_SOURCE='34be9c0ba6c5f045208dfa8226a0275cf4b602f1d5d6cf167c7d9da8f149f43a'
MARKER='HTCLEO_GS_ROOT_PAINT_WITNESS_849'
OLD=OWNER['BLOCK']
NEW=OLD.replace('public:\n    virtual void Draw', '''public:
    // HTCLEO_GS_ROOT_PAINT_WITNESS_849: at most seven records per root view.
    CHtcleoGsRootListView() : iPaintWitness(0) {}
    virtual void Draw''',1).replace('''        if (!drawer || !iGc || RedrawDisabled() || !IsVisible() ||
            iViewRect.IsEmpty())''','''        const TUint gate = (drawer ? 1u : 0u) | (iGc ? 2u : 0u) |
            (!RedrawDisabled() ? 4u : 0u) | (IsVisible() ? 8u : 0u) |
            (!iViewRect.IsEmpty() ? 16u : 0u);
        if (!(iPaintWitness & 1u))
            {
            iPaintWitness |= 1u;
            HtcleoGsBootLog(0x60f6u, (TInt)gate, (TUint32)this);
            }
        if (gate != 31u)''',1).replace('''        THtcleoGsBackgroundFlags state = { drawer, drawer->Flags() };''','''        const TBool witness = !(iPaintWitness & 2u);
        iPaintWitness |= 2u; // Set before logging/drawing; never retry on leave.
        const TRgb colour = BackColor();
        if (witness)
            {
            TUint32 gcVtable = 0;
            Mem::Copy(&gcVtable, iGc, sizeof(gcVtable));
            HtcleoGsBootLog(0x60f7u, (TInt)iGc, gcVtable);
            const TUint32 xy = ((TUint32)iViewRect.iTl.iX & 0xffffu) << 16 |
                ((TUint32)iViewRect.iTl.iY & 0xffffu);
            const TUint32 wh = ((TUint32)(iViewRect.iBr.iX - iViewRect.iTl.iX) & 0xffffu) << 16 |
                ((TUint32)(iViewRect.iBr.iY - iViewRect.iTl.iY) & 0xffffu);
            HtcleoGsBootLog(0x60f8u, (TInt)xy, wh);
            HtcleoGsBootLog(0x60f9u, (TInt)drawer->Flags(), (TUint32)colour.Value());
            }
        THtcleoGsBackgroundFlags state = { drawer, drawer->Flags() };''',1).replace('iGc->SetBrushColor(BackColor());','iGc->SetBrushColor(colour);',1).replace('''        iGc->DrawRect(iViewRect);
''','''        iGc->DrawRect(iViewRect);
        if (witness) HtcleoGsBootLog(0x60fau, KErrNone, (TUint32)this);
''',1).replace('''        CleanupStack::PopAndDestroy();
        }
    };''','''        CleanupStack::PopAndDestroy();
        if (witness) HtcleoGsBootLog(0x60fbu, (TInt)drawer->Flags(), (TUint32)this);
        }
private:
    mutable TUint iPaintWitness;
    };''',1).replace('''        return new(ELeave) CHtcleoGsRootListView;''','''        CHtcleoGsRootListView* view = new(ELeave) CHtcleoGsRootListView;
        HtcleoGsBootLog(0x60f5u, (TInt)view, 0x1020723bu);
        return view;''',1).replace('''sizeof(CHtcleoGsRootListView) == sizeof(CAknColumnListBoxView)''','''sizeof(CHtcleoGsRootListView) == sizeof(CAknColumnListBoxView) + sizeof(TUint)''',1)

def transform(text,restore=False):
    if MARKER in text:
        if text.count(NEW)!=1:raise ValueError('partial849 paint witness')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('paint witness requires exact848 root source')
    if not restore:
        if text.count(OLD)!=1:raise ValueError('848 private draw block missing')
        text=text.replace(OLD,NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('paint witness inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_ROOT_PAINT_WITNESS='+('restored' if a.restore else 'root-private-first-entry-gc-rect-fill-native-return-max7-per-view-no-behavior-change'))

if __name__=='__main__':main()
