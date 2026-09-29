#!/usr/bin/env python3
"""870: one external AppArc exit watch after the original client has closed."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 'apply-htcleo-filemanager-registration-census.py'))
REL = P['REL']
PARENT_SHA = '27dee4f0d376ef90202026a26b653f3421f589a260721304d4d0f659235a004c'
MARKER = 'HTCLEO_APPARC_EXIT_WATCH_870'
HOLD = r'''// HTCLEO_APPARC_EXIT_WATCH_870
// Select one live AppArc SID while the successful registration session exists.
// A population match is not an IPC endpoint proof; ambiguity fails closed.
static void HtcleoG19HoldAppArc(RProcess& aObserved)
    {
    TFindProcess finder(_L("*"));
    TFullName name;
    TInt matches = 0;
    TInt result = KErrNotFound;
    TInt next = KErrNone;
    TInt visited = 0;
    for (; visited < 512; ++visited)
        {
        next = finder.Next(name);
        if (next != KErrNone) break;
        RProcess candidate;
        if (candidate.Open(name, EOwnerThread) == KErrNone)
            {
            if (candidate.SecureId().iId == 0x10003a3fu && candidate.ExitType() == EExitPending)
                {
                ++matches;
                if (matches == 1) result = aObserved.Open(candidate.Id(), EOwnerThread);
                else { aObserved.Close(); result = KErrInUse; }
                }
            candidate.Close();
            }
        if (matches > 1) break;
        }
    if (visited == 512)
        { aObserved.Close(); result = KErrOverflow; }
    else if (next != KErrNone && next != KErrNotFound)
        { aObserved.Close(); result = next; }
    HtcleoG17SettingsLog(0x0260, result, (TUint)matches);
    if (result == KErrNone && aObserved.Handle())
        HtcleoG17SettingsLog(0x0261, (TInt)aObserved.ExitType(), (TUint)aObserved.Id().Id());
    }

'''
WATCH = r'''// Called after the original RApaLsSession cleanup, never holding a client
// session open to keep the target alive. No restart, kill, suspend or recovery.
static void HtcleoG19ObserveAppArcExit(RProcess& aObserved)
    {
    const TUint began = User::NTickCount();
    TRequestStatus death;
    aObserved.Logon(death);
    HtcleoG17SettingsLog(0x0262, death.Int(), (TUint)aObserved.Id().Id());
    if (death == KRequestPending)
        {
        RTimer timer;
        const TInt timerResult = timer.CreateLocal();
        HtcleoG17SettingsLog(0x0263, timerResult, 30000000u);
        if (timerResult == KErrNone)
            {
            TRequestStatus timeout;
            timer.HighRes(timeout, 30000000);
            User::WaitForRequest(death, timeout);
            HtcleoG17SettingsLog(0x0264, death.Int(), (TUint)timeout.Int());
            if (timeout == KRequestPending)
                { timer.Cancel(); User::WaitForRequest(timeout); }
            timer.Close();
            }
        if (death == KRequestPending)
            { aObserved.LogonCancel(death); User::WaitForRequest(death); }
        }
    const TExitType kind = aObserved.ExitType();
    HtcleoG17SettingsLog(0x0265, (TInt)kind, (TUint)aObserved.Id().Id());
    HtcleoG17SettingsLog(0x0266, kind == EExitPending ? KErrNotReady : aObserved.ExitReason(),
                        User::NTickCount() - began);
    if (kind != EExitPending)
        {
        const TExitCategoryName category = aObserved.ExitCategory();
        HtcleoG17SettingsLog(0x0267, category.Length(), 0u);
        for (TInt i = 0; i < category.Length() && i < 16; i += 4)
            {
            TUint a = 0, b = 0;
            for (TInt j = 0; j < 4 && i+j < category.Length(); ++j)
                {
                const TUint c = (TUint)category[i+j];
                if (j < 2) a |= c << (16*j);
                else b |= c << (16*(j-2));
                }
            HtcleoG17SettingsLog(0x0270 + (TUint)(i/4), (TInt)a, b);
            }
        }
    }
// HTCLEO_APPARC_EXIT_WATCH_870_END

'''
BLOCK = HOLD + WATCH
CHANGES = [
    ('static void HtcleoG19FileManagerCensus(RApaLsSession& apa)',
     'static void HtcleoG19FileManagerCensus(RApaLsSession& apa, RProcess& aObserved)'),
    ('    HtcleoG17SettingsLog(0x0254, r, r == KErrNone ? (TUint)appType.iUid : 0u);\n',
     '    HtcleoG17SettingsLog(0x0254, r, r == KErrNone ? (TUint)appType.iUid : 0u);\n    if (r == KErrNone) HtcleoG19HoldAppArc(aObserved);\n'),
    ('static TInt HtcleoG19RegisterFileManager(RApaLsSession& apa)',
     'static TInt HtcleoG19RegisterFileManager(RApaLsSession& apa, RProcess& aObserved)'),
    ('HtcleoG19FileManagerCensus(apa);', 'HtcleoG19FileManagerCensus(apa, aObserved);'),
    ('static void HtcleoG17RegisterSettingsL()', 'static void HtcleoG17RegisterSettingsL(RProcess& aObserved)'),
    ('(void)HtcleoG19RegisterFileManager(apa);', '(void)HtcleoG19RegisterFileManager(apa, aObserved);'),
    ('    TRAPD(r, HtcleoG17RegisterSettingsL());',
     '    RProcess observedAppArc;\n    TRAPD(r, HtcleoG17RegisterSettingsL(observedAppArc));'),
    ('    HtcleoG17Mark(8u);\n    delete cleanup;',
     '    HtcleoG17Mark(8u);\n    if (r == KErrNone && observedAppArc.Handle()) HtcleoG19ObserveAppArcExit(observedAppArc);\n    observedAppArc.Close();\n    delete cleanup;'),
]
ANCHOR = '// HTCLEO_FILEMANAGER_REGISTRATION_CENSUS_868\n'
POLICY = 'retain869-registration-select-unique-live-AppArc-SID-after-member0-close-original-session-then-one-30s-Logon-exit-watch'


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('870 anchor drift: ' + repr(old[:70]))
    return text.replace(old, new, 1)


def transform(text, restore=False):
    if MARKER in text:
        text = once(text, BLOCK, '')
        for old, new in reversed(CHANGES):
            text = once(text, new, old)
    text = P['transform'](text)
    if hashlib.sha256(text.encode()).hexdigest() != PARENT_SHA:
        raise ValueError('870 requires exact869 launcher helper')
    if restore:
        return P['transform'](text, True)
    for old, new in CHANGES:
        text = once(text, old, new)
    return once(text, ANCHOR, BLOCK + ANCHOR)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('870 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_FILEMANAGER_REGISTRATION=' + ('restored' if a.restore else POLICY))
