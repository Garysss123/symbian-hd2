#!/usr/bin/env python3
"""855: replace854 census with one owned, bounded font-load diagnostic."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
PREVIOUS=runpy.run_path(str(HERE/'apply-htcleo-gsapp-font-census.py'))
REL=PREVIOUS['REL'];NAME=PREVIOUS['NAME']
BASE_SHA='de7b5c085e873088cb51d37b891551958dcdacb6dd8d8eee1eb81acd9986becd'
MARKER='HTCLEO_GS_FONT_LOAD_BOUNDARY_855'
INCLUDE_OLD='#include    <eiklbm.h>\n'
INCLUDE_NEW=INCLUDE_OLD+'#include    <ecom/ecom.h>\n#include    <ecom/implementationinformation.h>\n'
OLD=PREVIOUS['BLOCK']
BLOCK=PREVIOUS['PREFIX']+r'''// HTCLEO_GS_FONT_LOAD_BOUNDARY_855
struct THtcleoGsFontLoadState
    {
    CWsScreenDevice* iDevice;
    CFont* iFont;
    TInt iFileId;
    TBool iAdded;
    RFs iFs;
    RLibrary iLibrary;
    RImplInfoPtrArray iImplementations;
    };

static void HtcleoGsFontLoadCleanup(TAny* aPtr)
    {
    THtcleoGsFontLoadState* state = static_cast<THtcleoGsFontLoadState*>(aPtr);
    if (state->iFont)
        {
        state->iDevice->ReleaseFont(state->iFont);
        state->iFont = NULL;
        }
    // RemoveFile(0) means ALL fonts. Never use that default, even if the
    // server reports success with an invalid handle. Balance only our AddFile.
    if (state->iAdded && state->iFileId != 0)
        {
        state->iDevice->RemoveFile(state->iFileId);
        state->iAdded = EFalse;
        }
    state->iImplementations.ResetAndDestroy();
    state->iLibrary.Close();
    state->iFs.Close();
    }

static void HtcleoGsFontLoadBoundary()
    {
    // At most19 records once per root, after native Draw returned. No retry,
    // timer, font selection change, file write, or server startup change.
    THtcleoGsFontLoadState state;
    state.iDevice = CCoeEnv::Static()->ScreenDevice();
    state.iFont = NULL;
    state.iFileId = 0;
    state.iAdded = EFalse;
    CleanupStack::PushL(TCleanupItem(HtcleoGsFontLoadCleanup, &state));
    _LIT(KFontFile, "z:\\resource\\fonts\\s60snr_v4196.ttf");
    _LIT(KRasterizer, "z:\\sys\\bin\\freetype.dll");
    _LIT(KFamily, "DejaVu Sans");
    HtcleoGsBootLog(0x6130u, state.iDevice->NumTypefaces(), 0x101f7f5du);
    const TInt fsError = state.iFs.Connect();
    HtcleoGsBootLog(0x6131u, fsError, 0u);
    if (fsError == KErrNone)
        {
        TEntry entry;
        const TInt entryError = state.iFs.Entry(KFontFile, entry);
        HtcleoGsBootLog(0x6132u, entryError,
            entryError == KErrNone ? (TUint32)entry.iSize : 0u);
        }

    const TUid interfaceUid = { 0x101f7f5d };
    HtcleoGsBootLog(0x6133u, 0, (TUint32)interfaceUid.iUid);
    TRAPD(listError, REComSession::ListImplementationsL(interfaceUid, state.iImplementations));
    const TInt count = state.iImplementations.Count();
    HtcleoGsBootLog(0x6134u, listError, (TUint32)count);
    TInt found = 0;
    const TInt limit = count > 32 ? 32 : count;
    for (TInt i = 0; i < limit; ++i)
        if (state.iImplementations[i]->ImplementationUid().iUid == 0x101f7f5e) ++found;
    HtcleoGsBootLog(0x6135u, found, (TUint32)limit);

    // Loading the DLL is not instantiating its rasterizer or proving that
    // FBServ installed it. Keep these boundaries separate in the decoder.
    HtcleoGsBootLog(0x6136u, 0, 0x100012a7u);
    const TInt libraryError = state.iLibrary.Load(KRasterizer);
    HtcleoGsBootLog(0x6137u, libraryError, libraryError == KErrNone ?
        (TUint32)state.iLibrary.Type()[2].iUid : 0u);

    HtcleoGsBootLog(0x6138u, 0, 0u);
    const TInt addError = state.iDevice->AddFile(KFontFile, state.iFileId);
    state.iAdded = addError == KErrNone && state.iFileId != 0;
    HtcleoGsBootLog(0x6139u, addError, (TUint32)state.iFileId);
    HtcleoGsBootLog(0x613au, state.iDevice->NumTypefaces(), state.iAdded ? 1u : 0u);
    TFontSpec request(KFamily, 20);
    request.iTypeface.SetIsSymbol(EFalse);
    request.iTypeface.SetIsProportional(ETrue);
    const TInt requestError = state.iDevice->GetNearestFontToDesignHeightInPixels(state.iFont, request);
    HtcleoGsBootLog(0x613bu, requestError, (TUint32)state.iFont);
    if (requestError == KErrNone && state.iFont)
        {
        _LIT(KMeasure, "General");
        HtcleoGsBootLog(0x613cu, state.iFont->HeightInPixels(),
            (TUint32)state.iFont->TextWidthInPixels(KMeasure));
        const TFontSpec actual = state.iFont->FontSpecInTwips();
        HtcleoGsBootLog(0x613du, actual.iTypeface.iName.Length(), (TUint32)actual.iHeight);
        HtcleoGsTextFour(0x613eu, actual.iTypeface.iName, 0);
        HtcleoGsTextFour(0x613fu, actual.iTypeface.iName, 4);
        HtcleoGsTextFour(0x6140u, actual.iTypeface.iName, 8);
        }
    CleanupStack::PopAndDestroy();
    HtcleoGsBootLog(0x6141u, addError, (TUint32)state.iFileId);
    HtcleoGsBootLog(0x6142u, state.iDevice->NumTypefaces(), 0u);
    }
// HTCLEO_GS_FONT_LOAD_BOUNDARY_855_END
'''
CALL_OLD=PREVIOUS['CALL_NEW']
CALL_NEW='        if (witness) HtcleoGsFontLoadBoundary();\n'
POLICY='first-root-entry-ecom-list-library-load-owned-FBS-add-request-release-remove-max19-no-startup-change'

def transform(text,restore=False):
    if MARKER in text:
        if text.count(BLOCK)!=1 or text.count(CALL_NEW)!=1 or text.count(INCLUDE_NEW)!=1:
            raise ValueError('partial855 font load boundary')
        text=text.replace(BLOCK,OLD,1).replace(CALL_NEW,CALL_OLD,1).replace(INCLUDE_NEW,INCLUDE_OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('855 requires exact854 root')
    if not restore:
        if text.count(OLD)!=1 or text.count(CALL_OLD)!=1:raise ValueError('854 census missing')
        text=text.replace(OLD,BLOCK,1).replace(CALL_OLD,CALL_NEW,1).replace(INCLUDE_OLD,INCLUDE_NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('855 inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_FONT_LOAD_BOUNDARY='+('restored' if a.restore else POLICY))
if __name__=='__main__':main()
