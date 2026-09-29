#!/usr/bin/env python3
"""858: replace the completed font-load probe with held ECom process evidence."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
PREVIOUS=runpy.run_path(str(HERE/'apply-htcleo-gsapp-font-load-boundary.py'))
REL=PREVIOUS['REL'];NAME=PREVIOUS['NAME']
BASE_SHA='8e46536a8232f284488e5a4566c2cab409c974f02bac6a9deccd140763e31e8f'
MARKER='HTCLEO_GS_FONT_SERVER_LIFETIME_858'
OLD=PREVIOUS['BLOCK']
BLOCK=PREVIOUS['PREVIOUS']['PREFIX']+r'''// HTCLEO_GS_FONT_SERVER_LIFETIME_858
// Hold only a uniquely identified live process with the native EComServer SID.
// This retains its exit evidence, not its execution/liveness. It does not
// identify the private IPC session endpoint or prove an alive process responds.
static TInt HtcleoGsBindEcomProcess(RProcess& aProcess, TInt& aMatches)
    {
    _LIT(KServerPattern, "*ecomserver*");
    TFindProcess find(KServerPattern);
    TFullName name;
    aMatches = 0;
    TInt result = KErrNotFound;
    for (TInt i = 0; i < 16; ++i)
        {
        const TInt next = find.Next(name);
        if (next != KErrNone)
            {
            if (next != KErrNotFound) { aProcess.Close(); return next; }
            return result;
            }
        RProcess candidate;
        const TInt opened = candidate.Open(name);
        if (opened == KErrNone && candidate.SecureId().iId == 0x10009d8fu &&
            candidate.ExitType() == EExitPending)
            {
            ++aMatches;
            if (aMatches == 1) result = aProcess.Open(candidate.Id());
            }
        candidate.Close();
        if (aMatches > 1) { aProcess.Close(); return KErrAlreadyExists; }
        }
    aProcess.Close(); // Bounded scan is incomplete: do not claim uniqueness.
    return KErrOverflow;
    }

struct THtcleoGsFontServerState
    {
    RProcess iBefore;
    RProcess iAfter;
    RImplInfoPtrArray iImplementations;
    };

static void HtcleoGsFontServerCleanup(TAny* aPtr)
    {
    THtcleoGsFontServerState* state = static_cast<THtcleoGsFontServerState*>(aPtr);
    state->iImplementations.ResetAndDestroy();
    state->iBefore.Close();
    state->iAfter.Close();
    }

static void HtcleoGsFontServerLifetime()
    {
    // Once per root after native Draw; at most13 log records. Same default
    // font query as855, no extra request/retry, AddFile or DLL instantiation.
    THtcleoGsFontServerState state;
    CleanupStack::PushL(TCleanupItem(HtcleoGsFontServerCleanup, &state));
    const TInt typefaces = CCoeEnv::Static()->ScreenDevice()->NumTypefaces();
    HtcleoGsBootLog(0x6160u, typefaces, 0x10009d8fu);
    TInt matches = 0;
    const TInt bindBefore = HtcleoGsBindEcomProcess(state.iBefore, matches);
    HtcleoGsBootLog(0x6161u, bindBefore, (TUint32)matches);
    HtcleoGsBootLog(0x6162u, bindBefore == KErrNone ?
        (TInt)state.iBefore.ExitType() : KErrNotReady,
        bindBefore == KErrNone ? (TUint32)state.iBefore.Id() : 0u);

    const TUid interfaceUid = { 0x101f7f5d };
    HtcleoGsBootLog(0x6163u, 0, (TUint32)interfaceUid.iUid);
    TRAPD(listError, REComSession::ListImplementationsL(interfaceUid, state.iImplementations));
    HtcleoGsBootLog(0x6164u, listError, (TUint32)state.iImplementations.Count());
    TInt exitType = KErrNotReady;
    TInt exitReason = KErrNotReady;
    TExitCategoryName category;
    if (bindBefore == KErrNone)
        {
        exitType = state.iBefore.ExitType();
        if (exitType != EExitPending)
            {
            exitReason = state.iBefore.ExitReason();
            category = state.iBefore.ExitCategory();
            }
        }
    HtcleoGsBootLog(0x6165u, exitType, (TUint32)exitReason);
    HtcleoGsBootLog(0x6166u, category.Length(),
        bindBefore == KErrNone ? (TUint32)state.iBefore.Id() : 0u);
    HtcleoGsTextFour(0x6167u, category, 0);
    HtcleoGsTextFour(0x6168u, category, 4);
    HtcleoGsTextFour(0x6169u, category, 8);
    const TInt bindAfter = HtcleoGsBindEcomProcess(state.iAfter, matches);
    HtcleoGsBootLog(0x616au, bindAfter, (TUint32)matches);
    HtcleoGsBootLog(0x616bu, bindAfter == KErrNone ?
        (TInt)state.iAfter.ExitType() : KErrNotReady,
        bindAfter == KErrNone ? (TUint32)state.iAfter.Id() : 0u);
    CleanupStack::PopAndDestroy();
    HtcleoGsBootLog(0x616cu, listError, 0u);
    }
// HTCLEO_GS_FONT_SERVER_LIFETIME_858_END
'''
CALL_OLD=PREVIOUS['CALL_NEW']
CALL_NEW='        if (witness) HtcleoGsFontServerLifetime();\n'
POLICY='first-root-held-unique-ECom-SID-process-before-after-same-font-query13-no-server-mutation'

def transform(text,restore=False):
    if MARKER in text:
        if text.count(BLOCK)!=1 or text.count(CALL_NEW)!=1:raise ValueError('partial858 lifetime observer')
        text=text.replace(BLOCK,OLD,1).replace(CALL_NEW,CALL_OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('858 requires exact retained855 root')
    if not restore:
        if text.count(OLD)!=1 or text.count(CALL_OLD)!=1:raise ValueError('855 observer missing')
        text=text.replace(OLD,BLOCK,1).replace(CALL_OLD,CALL_NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('858 inverse drift')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_FONT_SERVER_LIFETIME='+('restored' if a.restore else POLICY))
if __name__=='__main__':main()
