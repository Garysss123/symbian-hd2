#!/usr/bin/env python3
"""867: let AppArc read its own private registration file; keep client caps."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 'apply-htcleo-filemanager-registration.py'))
REL = P['REL']
PARENT_SHA = 'b08d8b41cd605e9e24af61dbdfc90e09a00d909c620d6ecaf02084a93ce4c2e9'
MARKER = 'HTCLEO_FILEMANAGER_CLIENT_BOUNDARY_867'
BLOCK = r'''// HTCLEO_FILEMANAGER_CLIENT_BOUNDARY_867
//866's client RFs::Entry failed with KErrPermissionDenied before registration.
// The immutable C: payload is checked by the host deployment contract. Send its
// fixed path to the native AppArc owner; do not grant AllFiles to ailaunch.
static TInt HtcleoG19RegisterFileManager(RApaLsSession& apa)
    {
    HtcleoG17SettingsLog(0x0246, KErrNone, 0x101f84ebu);
    _LIT(KFileManagerRegistration, "C:\\private\\10003a3f\\import\\apps\\filemanager_reg.rsc");
    const TDesC& path = KFileManagerRegistration();
    RPointerArray<TDesC> registrations;
    TInt r = registrations.Append(&path);
    HtcleoG17SettingsLog(0x0242, r, (TUint)registrations.Count());
    if (r == KErrNone)
        {
        r = apa.ForceRegistration(registrations);
        HtcleoG17SettingsLog(0x0243, r, 0x101f84ebu);
        }
    registrations.Close();
    HtcleoG17SettingsLog(0x0244, r, 0u);
    return r;
    }
// HTCLEO_FILEMANAGER_CLIENT_BOUNDARY_867_END

'''
CALL_OLD = P['CALL_OLD']
CALL_NEW = '''    //867 retains866's single call after successful Settings registration.
    //0243/0244 are the FileManager result;02ff remains Settings-only.
    if (r == KErrNone) (void)HtcleoG19RegisterFileManager(apa);
''' + CALL_OLD
POLICY = 'home-ready-after-Settings-one-native-C-FileManager-registration-no-client-private-Entry-no-capability-change'


def transform(text, restore=False):
    if MARKER in text:
        if text.count(BLOCK) != 1 or text.count(CALL_NEW) != 1:
            raise ValueError('partial867 client-boundary overlay')
        text = text.replace(BLOCK, P['BLOCK'], 1).replace(CALL_NEW, P['CALL_NEW'], 1)
    text = P['transform'](text)
    if hashlib.sha256(text.encode()).hexdigest() != PARENT_SHA:
        raise ValueError('867 requires exact866 worker')
    if restore:
        return P['transform'](text, True)
    return text.replace(P['BLOCK'], BLOCK, 1).replace(P['CALL_NEW'], CALL_NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('867 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_FILEMANAGER_REGISTRATION=' + ('restored' if a.restore else POLICY))
