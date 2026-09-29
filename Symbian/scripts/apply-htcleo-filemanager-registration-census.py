#!/usr/bin/env python3
"""868: bounded AppArc membership and C-drive attributes after registration."""
import argparse
import hashlib
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
P = runpy.run_path(str(HERE / 'apply-htcleo-filemanager-client-boundary.py'))
REL = P['REL']
PARENT_SHA = '58ae274d90364b63f78b2c72278098bf9ebb57eafc5830c1ec0b74a371bbdb0d'
MARKER = 'HTCLEO_FILEMANAGER_REGISTRATION_CENSUS_868'
CENSUS = r'''// HTCLEO_FILEMANAGER_REGISTRATION_CENSUS_868
// GetAppType reads AppDataByUid directly. Unlike GetAppInfo, it does not try
// FindSpecificAppL while scanning. A completed registration is not membership.
static void HtcleoG19FileManagerCensus(RApaLsSession& apa)
    {
    HtcleoG17SettingsLog(0x0250, KErrNone, 0x101f84ebu);
    RFs fs;
    TInt r = fs.Connect();
    HtcleoG17SettingsLog(0x0251, r, (TUint)EDriveC);
    if (r == KErrNone)
        {
        TDriveInfo drive;
        r = fs.Drive(drive, EDriveC);
        HtcleoG17SettingsLog(0x0252, r, r == KErrNone ? drive.iDriveAtt : 0u);
        fs.Close();
        }
    TUid appType = KNullUid;
    r = apa.GetAppType(appType, TUid::Uid(0x100058ec));
    HtcleoG17SettingsLog(0x0253, r, r == KErrNone ? (TUint)appType.iUid : 0u);
    if (r != KErrNone) return; // failed known-Settings control is not FM absence
    appType = KNullUid;
    r = apa.GetAppType(appType, TUid::Uid(0x101f84eb));
    HtcleoG17SettingsLog(0x0254, r, r == KErrNone ? (TUint)appType.iUid : 0u);
    }
// HTCLEO_FILEMANAGER_REGISTRATION_CENSUS_868_END

'''
TAIL = '    HtcleoG17SettingsLog(0x0244, r, 0u);\n    return r;\n'
NEW_TAIL = '    HtcleoG17SettingsLog(0x0244, r, 0u);\n    if (r == KErrNone) HtcleoG19FileManagerCensus(apa);\n    return r;\n'
BLOCK = CENSUS + P['BLOCK'].replace(TAIL, NEW_TAIL, 1)
CALL_NEW = P['CALL_NEW']
CALL_OLD = P['CALL_OLD']
POLICY = 'retain867-registration-one-C-drive-attributes-known-Settings-and-FileManager-GetAppType-census-no-rescan-no-policy-change'


def transform(text, restore=False):
    if MARKER in text:
        if text.count(BLOCK) != 1:
            raise ValueError('partial868 registration census')
        text = text.replace(BLOCK, P['BLOCK'], 1)
    text = P['transform'](text)
    if hashlib.sha256(text.encode()).hexdigest() != PARENT_SHA:
        raise ValueError('868 requires exact867 worker')
    if restore:
        return P['transform'](text, True)
    return text.replace(P['BLOCK'], BLOCK, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('868 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_FILEMANAGER_REGISTRATION=' + ('restored' if a.restore else POLICY))
