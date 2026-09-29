#!/usr/bin/env python3
"""853: root first-draw text/font/glyph witness; no selection or paint policy."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
NAME='Src/GSMainContainer.cpp'
BASE_SHA='358a93a9076799a136bce2bfe37df3f99f08fdd9c6d400bcfa1e5db5f5a2fe4d'
MARKER='HTCLEO_GS_TEXT_WITNESS_853'
INC='#include    <fbs.h>\n'
INC_NEW=INC+'#include    <openfont.h>\n#include    <eiklbm.h>\n'
ANCHOR='//CONSTANTS\n'
BLOCK='''
// HTCLEO_GS_TEXT_WITNESS_853
static TUint32 HtcleoGsTwoChars(const TDesC& aText, TInt aOffset)
    {
    TUint32 value = 0;
    if (aOffset < aText.Length()) value = aText[aOffset];
    if (aOffset + 1 < aText.Length()) value |= (TUint32)aText[aOffset + 1] << 16;
    return value;
    }

static void HtcleoGsTextFour(TUint32 aStage, const TDesC& aText, TInt aOffset)
    {
    HtcleoGsBootLog(aStage, (TInt)HtcleoGsTwoChars(aText, aOffset),
        HtcleoGsTwoChars(aText, aOffset + 2));
    }

static void HtcleoGsTextWitness(CColumnListBoxItemDrawer* aDrawer,
                               MListBoxModel* aModel)
    {
    // Called only after the FIRST valid native root Draw has returned.
    // A maximum of14 records per root view; never a frame/glyph stream.
    const TInt count = aModel ? aModel->NumberOfItems() : -1;
    HtcleoGsBootLog(0x6100u, count, (TUint32)aDrawer);
    if (!aDrawer || count <= 0) return;
    const TPtrC text = static_cast<MTextListBoxModel*>(aModel)->ItemText(0);
    HtcleoGsBootLog(0x6101u, text.Length(), (TUint32)aDrawer->TextColor().Value());
    HtcleoGsTextFour(0x6102u, text, 0);
    HtcleoGsTextFour(0x6103u, text, 4);
    CColumnListBoxData* data = aDrawer->ColumnData();
    const CFont* rowFont = data ? data->RowAndColumnFont(0, 1) : NULL;
    const CFont* colFont = data ? data->ColumnFont(1) : NULL;
    // Mirrors native CColumnListBoxData selection. If both are NULL, report
    // that fact, not an invented replacement; TAknLayoutText may then fallback.
    const CFont* font = rowFont ? rowFont : colFont;
    HtcleoGsBootLog(0x6104u, rowFont ? 1 : (colFont ? 2 : 0), (TUint32)font);
    HtcleoGsBootLog(0x6105u, data ? data->ColumnWidthPixel(1) : -1,
        data ? (TUint32)data->ColumnBaselinePos(1) : 0u);
    if (!font) return;
    _LIT(KGsMeasureText, "General");
    const TInt height = font->HeightInPixels();
    const TInt width = font->TextWidthInPixels(KGsMeasureText);
    HtcleoGsBootLog(0x6106u, height, (TUint32)width);
    const TFontSpec spec = font->FontSpecInTwips();
    HtcleoGsBootLog(0x6107u, spec.iHeight, (TUint32)spec.iTypeface.iName.Length());
    HtcleoGsTextFour(0x6108u, spec.iTypeface.iName, 0);
    HtcleoGsTextFour(0x6109u, spec.iTypeface.iName, 4);
    HtcleoGsTextFour(0x610au, spec.iTypeface.iName, 8);
    HtcleoGsBootLog(0x610bu, 0x47, (TUint32)font);
    TOpenFontCharMetrics metrics;
    const TUint8* bitmap = NULL;
    TSize bitmapSize(0, 0);
    const CFont::TCharacterDataAvailability available =
        font->GetCharacterData(0x47u, metrics, bitmap, bitmapSize);
    HtcleoGsBootLog(0x610cu, (TInt)available,
        ((TUint32)(bitmapSize.iWidth & 0xffff) << 16) | (TUint32)(bitmapSize.iHeight & 0xffff));
    HtcleoGsBootLog(0x610du, bitmap ? 1 : 0, (TUint32)metrics.HorizAdvance());
    }
// HTCLEO_GS_TEXT_WITNESS_853_END
'''
CALL_OLD='''        if (witness) HtcleoGsBootLog(0x60fbu, (TInt)drawer->Flags(), (TUint32)this);
'''
CALL_NEW=CALL_OLD+'''        if (witness) HtcleoGsTextWitness(
            static_cast<CColumnListBoxItemDrawer*>(drawer), iModel);
'''
MMP_LINE='LIBRARY gdi.lib // HTCLEO_GS_TEXT_WITNESS_853: existing ROM provider, read-only font API\n'

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('853 anchor drift '+repr(old[:80]))
    return text.replace(old,new,1)

def transform(text,restore=False):
    if MARKER in text:
        text=once(text,BLOCK,'');text=once(text,CALL_NEW,CALL_OLD);text=once(text,INC_NEW,INC)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('853 requires exact retained850/852 root source')
    if not restore:
        text=once(text,INC,INC_NEW);text=once(text,ANCHOR,ANCHOR+BLOCK);text=once(text,CALL_OLD,CALL_NEW)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('853 inverse failed')
    mmp=a.root/REL/'GSApplication_htcleo.mmp';m=mmp.read_text(encoding='latin-1')
    if MMP_LINE in m:m=once(m,MMP_LINE,'')
    if not a.restore:
        if 'LIBRARY gdi.lib' in m:raise ValueError('unexpected existing gdi line')
        m=once(m,'//End of File',MMP_LINE+'//End of File')
    if old!=new:path.write_text(new,encoding='latin-1')
    if mmp.read_text(encoding='latin-1')!=m:mmp.write_text(m,encoding='latin-1')
    print('HTCLEO_GS_TEXT_WITNESS='+('restored' if a.restore else 'first-native-root-draw-text-font-G-glyph-max14-no-selection-paint-or-layout-change'))

if __name__=='__main__':main()
