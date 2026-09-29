#!/usr/bin/env python3
"""875: publish the trusted offline-preload scan, not an unfinished installer scan."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/appsupport/appfw/apparchitecture/apserv/APSSES.CPP')
BASE_SHA = '01738b91959360beb5a540738e0ede0ed76f2df3063f08205614d58e5e632438'
MARKER = 'HTCLEO_APPARC_PRELOAD_PUBLICATION_875'
OLD = '\tiAppArcSrv.UpdateAppsByForceRegistration();\n'
NEW = '''\t// HTCLEO_APPARC_PRELOAD_PUBLICATION_875
\t// ailaunch registers the already deployed, host-verified offline preload.
\t// No installer will copy the final resources and cause a later FS rescan.
\t// Use the normal observed scan for this trusted, nonempty bootstrap only.
\t// NotifyUpdate/NotifyScanComplete remain native; no synthetic menu entries.
\t// All other clients (including Java/SWI) retain deferred ForceRegistration.
\tif (count > 0 && aMessage.SecureId().iId == 0x200286e3u)
\t\t{
\t\tHtcleoApaServerLog(0x00001480u, KErrNone, count);
\t\tiAppArcSrv.UpdateApps();
\t\t}
\telse
\t\tiAppArcSrv.UpdateAppsByForceRegistration();
'''
POLICY = 'ailaunch-SID200286e3-nonempty-offline-preload-normal-observed-scan-native-notify-other-installers-deferred-1480'


def transform(text, restore=False):
    if MARKER in text:
        if text.count(NEW) != 1:
            raise ValueError('partial875 preload publication patch')
        text = text.replace(NEW, OLD, 1)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('875 requires exact874 AppArc session source')
    if restore:
        return text
    if text.count(OLD) != 1:
        raise ValueError('875 registration anchor drift')
    return text.replace(OLD, NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root/REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('875 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_APPARC_PRELOAD_PUBLICATION=' + ('restored' if a.restore else POLICY))
