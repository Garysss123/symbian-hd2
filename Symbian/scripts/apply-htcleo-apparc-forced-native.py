#!/usr/bin/env python3
"""869: honor an explicit native forced path on SID-check KErrNotFound only."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/appsupport/appfw/apparchitecture/aplist/aplappregfinder.cpp')
BASE_SHA = 'f62575085e7e38ceb54ab69b7793cbbf79b0e4f9173033150cef370e19e1f1be'
MARKER = 'HTCLEO_APPARC_FORCED_NATIVE_869'
INCLUDE_OLD = '#include "aplappinforeader.h"\t\t\t\t// class ApaUtils\n'
INCLUDE_NEW = INCLUDE_OLD + '#include "htcleoapplistlog.h" // bounded forced-path observation only\n'
OLD = '''\t\t\t\t\telse if(err != KErrNotFound)
\t\t\t\t\t\tUser::LeaveIfError(err);
\t\t\t\t\telse
\t\t\t\t\t\tcontinue; // Can't tell. Move on to next.
'''
NEW = '''\t\t\t\t\telse if(err != KErrNotFound)
\t\t\t\t\t\tUser::LeaveIfError(err);
\t\t\t\t\telse
\t\t\t\t\t\t{
\t\t\t\t\t\t// HTCLEO_APPARC_FORCED_NATIVE_869
\t\t\t\t\t\t// Native ForceRegistration already permits explicitly named resources
\t\t\t\t\t\t// before SIS registration. Keep that exception when the native SID
\t\t\t\t\t\t// check is unavailable. Non-native types and all unlisted files stay
\t\t\t\t\t\t// excluded; other errors retain the original branch above.
\t\t\t\t\t\tconst TPtrC fullName = regFileNameParser.FullName();
\t\t\t\t\t\tTInt forcedIndex = KErrNotFound;
\t\t\t\t\t\tif (appTypeUid != KNullUid ||
\t\t\t\t\t\t    aForcedRegistrations.FindIsq(fullName, forcedIndex, ECmpFolded) != KErrNone)
\t\t\t\t\t\t\tcontinue;
\t\t\t\t\t\tHtcleoApaListLog(0x00001460u, err, (TUint32)entry[2].iUid);
\t\t\t\t\t\t}
'''
POLICY = 'native-only-explicit-full-forced-path-on-SID-check-NotFound-no-unlisted-or-Java-bypass-1460'


def transform(text, restore=False):
    if MARKER in text:
        if text.count(NEW) != 1 or text.count(INCLUDE_NEW) != 1:
            raise ValueError('partial869 forced-native overlay')
        text = text.replace(NEW, OLD, 1).replace(INCLUDE_NEW, INCLUDE_OLD, 1)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('869 requires exact868 registration finder')
    if restore:
        return text
    if text.count(OLD) != 1 or text.count(INCLUDE_OLD) != 1:
        raise ValueError('869 finder anchor drift')
    return text.replace(OLD, NEW, 1).replace(INCLUDE_OLD, INCLUDE_NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('869 inverse failed')
    if new != old:
        path.write_text(new)
    print('HTCLEO_APPARC_FORCED_NATIVE=' + ('restored' if a.restore else POLICY))
