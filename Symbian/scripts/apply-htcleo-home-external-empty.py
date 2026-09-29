#!/usr/bin/env python3
"""861 recovery on859: only optional Home external interface joins FeatMgr empty exit."""
import argparse
import hashlib
from pathlib import Path
REL=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp')
BASE_SHA='2b1088ef28c4ae1ee374a029132f7ca33cb5a653a3abb47672d74a07cf7479e4'
MARKER='HTCLEO_HOME_EXTERNAL_EMPTY_861'
OLD='''\t\t\t// Feature Manager explicitly supports a product with no
\t\t\t// adaptation plug-ins.  Preserve stock ECom errors for every
\t\t\t// other interface, but represent this one optional interface
\t\t\t// as the empty list expected by its existing count==0 path.
\t\t\tif(aInterfaceUid.iUid == 0x10205057u)
'''
NEW='''\t\t\t// HTCLEO_HOME_EXTERNAL_EMPTY_861
\t\t\t// Preserve859 for every other interface. Home external controls
\t\t\t// are optional and already have an empty-list fallback; include
\t\t\t// only that known interface alongside the original FeatMgr case.
\t\t\tif(aInterfaceUid.iUid == 0x10205057u ||
\t\t\t   aInterfaceUid.iUid == 0x200286dfu)
'''
POLICY='on859-only-optional-Home-external200286df-and-original-FeatMgr-empty-no-global-change'

def transform(text,restore=False):
    if MARKER in text:
        if text.count(NEW)!=1:raise ValueError('partial861 optional Home change')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode()).hexdigest()!=BASE_SHA:raise ValueError('861 requires exact859 registry source')
    if not restore:
        if text.count(OLD)!=1:raise ValueError('859 FeatMgr branch missing')
        text=text.replace(OLD,NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text();new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('861 inverse drift')
    if old!=new:path.write_text(new)
    print('HTCLEO_HOME_EXTERNAL_EMPTY='+('restored' if a.restore else POLICY))
if __name__=='__main__':main()
