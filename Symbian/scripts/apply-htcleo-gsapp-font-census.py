#!/usr/bin/env python3
"""854: replace853 observation with bounded system font census/direct request."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
TEXT=runpy.run_path(str(HERE/'apply-htcleo-gsapp-text-witness.py'))
REL=TEXT['REL'];NAME=TEXT['NAME']
BASE_SHA='6670c64b5cad70f9e8df9bbf6773c97520827749cd05ffdad06e0c29194bd0f8'
MARKER='HTCLEO_GS_FONT_CENSUS_854'
OLD=TEXT['BLOCK']
PREFIX=OLD[:OLD.index('static void HtcleoGsTextWitness')]
BLOCK=PREFIX+'''// HTCLEO_GS_FONT_CENSUS_854
struct THtcleoGsRequestedFont
    {
    CWsScreenDevice* iDevice;
    CFont* iFont;
    };

static void HtcleoGsReleaseRequestedFont(TAny* aPtr)
    {
    THtcleoGsRequestedFont* state = static_cast<THtcleoGsRequestedFont*>(aPtr);
    if (state->iFont)
        {
        state->iDevice->ReleaseFont(state->iFont);
        state->iFont = NULL;
        }
    }

static void HtcleoGsFontCensus()
    {
    // Only once per root, after native Draw. Never install/load/remove font
    // files or replace the control's font. At most32 TypefaceSupport queries.
    CWsScreenDevice* device = CCoeEnv::Static()->ScreenDevice();
    const TInt count = device->NumTypefaces();
    const TInt limit = count > 32 ? 32 : (count > 0 ? count : 0);
    HtcleoGsBootLog(0x6120u, count, (TUint32)limit);
    _LIT(KFamily, "DejaVu Sans");
    TInt nonSymbols = 0;
    TInt symbols = 0;
    TInt target = -1;
    TBuf<KMaxTypefaceNameLength> firstNonSymbol;
    for (TInt i = 0; i < limit; ++i)
        {
        TTypefaceSupport info;
        device->TypefaceSupport(info, i);
        if (info.iTypeface.IsSymbol())
            ++symbols;
        else
            {
            ++nonSymbols;
            if (firstNonSymbol.Length() == 0) firstNonSymbol.Copy(info.iTypeface.iName);
            }
        if (info.iTypeface.iName.CompareF(KFamily) == 0) target = i;
        }
    HtcleoGsBootLog(0x6121u, nonSymbols, (TUint32)symbols);
    HtcleoGsBootLog(0x6122u, target, (TUint32)firstNonSymbol.Length());
    HtcleoGsTextFour(0x6123u, firstNonSymbol, 0);
    HtcleoGsTextFour(0x6124u, firstNonSymbol, 4);
    HtcleoGsTextFour(0x6125u, firstNonSymbol, 8);

    THtcleoGsRequestedFont state = { device, NULL };
    // Own the temporary request before acquisition, including error/leave paths.
    CleanupStack::PushL(TCleanupItem(HtcleoGsReleaseRequestedFont, &state));
    TFontSpec request(KFamily, 20); // Pixel units for the API below.
    request.iTypeface.SetIsSymbol(EFalse);
    request.iTypeface.SetIsProportional(ETrue);
    HtcleoGsBootLog(0x6126u, 20, 0x4456534eu);
    const TInt error = device->GetNearestFontToDesignHeightInPixels(state.iFont, request);
    HtcleoGsBootLog(0x6127u, error, (TUint32)state.iFont);
    if (error == KErrNone && state.iFont)
        {
        _LIT(KMeasure, "General");
        const TInt height = state.iFont->HeightInPixels();
        const TInt width = state.iFont->TextWidthInPixels(KMeasure);
        HtcleoGsBootLog(0x6128u, height, (TUint32)width);
        const TFontSpec actual = state.iFont->FontSpecInTwips();
        HtcleoGsBootLog(0x6129u, actual.iHeight, (TUint32)actual.iTypeface.iName.Length());
        HtcleoGsTextFour(0x612au, actual.iTypeface.iName, 0);
        HtcleoGsTextFour(0x612bu, actual.iTypeface.iName, 4);
        HtcleoGsTextFour(0x612cu, actual.iTypeface.iName, 8);
        }
    CleanupStack::PopAndDestroy();
    HtcleoGsBootLog(0x612du, error, 0u);
    }
// HTCLEO_GS_FONT_CENSUS_854_END
'''
CALL_OLD='''        if (witness) HtcleoGsTextWitness(
            static_cast<CColumnListBoxItemDrawer*>(drawer), iModel);
'''
CALL_NEW='''        if (witness) HtcleoGsFontCensus();
'''

def transform(text,restore=False):
    if MARKER in text:
        if text.count(BLOCK)!=1 or text.count(CALL_NEW)!=1:raise ValueError('partial854 font census')
        text=text.replace(BLOCK,OLD,1).replace(CALL_NEW,CALL_OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('854 requires exact853 root')
    if not restore:
        if text.count(OLD)!=1 or text.count(CALL_OLD)!=1:raise ValueError('853 witness missing')
        text=text.replace(OLD,BLOCK,1).replace(CALL_OLD,CALL_NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('854 inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_FONT_CENSUS='+('restored' if a.restore else 'first-root-system-typefaces32-direct-DejaVu20-request-release-no-font-install-or-selection'))

if __name__=='__main__':main()
