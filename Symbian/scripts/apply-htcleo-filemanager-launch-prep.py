#!/usr/bin/env python3
"""876: observe FileManager launch preparation without changing launch policy."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/appsupport/appfw/apparchitecture/apserv/APSSES.CPP')
BASE_SHA = '58ee17f5bacabbde1205e1f174df0f08f3f4cbfd64aeb5c29a454c78d6e2382b'
MARKER = 'HTCLEO_FILEMANAGER_LAUNCH_PREP_876'
ASSET = HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleofilemanagerprep876.inl'
INCLUDE = '\n// HTCLEO_FILEMANAGER_LAUNCH_PREP_876\n#include "htcleofilemanagerprep876.inl"\n'
PERMISSION = 'void CApaAppArcServSession::AquirePermissionToLaunchAppL(const RMessage2& aMessage) const\n\t{\n'
CHANGES = [
    (PERMISSION, PERMISSION + '''\tTUint32 htcleoDrive = 0;
\tconst TBool htcleoPrep = HtcleoFileManagerPrepMessage(aMessage, 0, htcleoDrive);
\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c00u, KErrNone, 0x101f84eb, htcleoDrive);
'''),
    ('\t\t// Proceed with launch if rule based plug-in framework was not initialized\n',
     '\t\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c02u, ETrue, theNumImp, iServ.WsSession().Handle() ? 1u : 0u);\n\t\t// Proceed with launch if rule based plug-in framework was not initialized\n'),
    ('\t// Ge the application\'s UID from its name\n',
     '\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c03u, KErrNone, theNumImp, 0u);\n\t// Ge the application\'s UID from its name\n'),
    ('\tconst TUid theUid = iAppListSession->AppUidFromFullFileNameL(theFullFileNamePtr);\n',
     '\tconst TUid theUid = iAppListSession->AppUidFromFullFileNameL(theFullFileNamePtr);\n\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c04u, KErrNone, theUid.iUid, 0u);\n'),
    ('\tconst TBool okayToLaunch = (theLaunchCode != CAppLaunchChecker::EAppLaunchDecline);\n',
     '\tconst TBool okayToLaunch = (theLaunchCode != CAppLaunchChecker::EAppLaunchDecline);\n\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c05u, okayToLaunch, theUid.iUid, (TUint32)theLaunchCode);\n'),
    ('\taMessage.ReadL(1, logicalExecutableName);\n\tCApaAppData* const appData=iAppListSession->AppList().AppDataByFileName(logicalExecutableName);\n',
     '''\taMessage.ReadL(1, logicalExecutableName);
\tconst TBool htcleoPrep = HtcleoFileManagerPrepName(logicalExecutableName);
\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c10u, KErrNone, logicalExecutableName.Length(), 0u);
\tCApaAppData* const appData=iAppListSession->AppList().AppDataByFileName(logicalExecutableName);
\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c11u, KErrNone, appData ? 1 : 0, 0u);
'''),
    ('\tCleanupStack::PopAndDestroy(&logicalExecutableName);\n',
     '''\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c12u, KErrNone, appData ? 1 : 0, 0u);
\tCleanupStack::PopAndDestroy(&logicalExecutableName);
\tif (htcleoPrep) HtcleoFileManagerPrepLog(0x2c13u, KErrNone, 0, 0u);
'''),
]
POLICY = 'FileManager-only-native-rule-and-opaque-IPC-boundaries-existing-MLAUNCH128-no-Flush-retry-or-policy-change-2c00-2c13'


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('876 anchor drift: '+repr(old[:90]))
    return text.replace(old, new, 1)


def transform(text, restore=False):
    if MARKER in text:
        text = once(text, INCLUDE, '')
        for old, new in reversed(CHANGES):
            text = once(text, new, old)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('876 requires exact875 AppArc session source')
    if restore:
        return text
    text = once(text, '#include "htcleoapalog.h"\n', '#include "htcleoapalog.h"\n'+INCLUDE)
    for old, new in CHANGES:
        text = once(text, old, new)
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root/REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('876 inverse failed')
    if old != new:
        path.write_text(new)
    if not a.restore:
        path.with_name(ASSET.name).write_bytes(ASSET.read_bytes())
    print('HTCLEO_FILEMANAGER_LAUNCH_PREP=' + ('restored' if a.restore else POLICY))
