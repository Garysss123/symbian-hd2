#!/usr/bin/env python3
"""839: retarget the existing supervisor HAL21 sampler to the known newborn Home UI."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/homescreensrv/idlefw/hslaunch/src')
NAME='htcleothreadwatch.inl'
BASE_SOURCE='53c9c9ae5dda23f50cd0664c7ab3a1780979547a908fc89df9ef94273873962d'
BASE_BINARY='4a84261beb35a025d4d55208ff2bf00c8409cb1fd24e78c9b4573cabfa071f57'
MAIN_SHA='80cc844c8545efec326b7104f3a9f9950095562531ce79546b09c813177ddbab'
EDITS=[
 ('static TInt HtcleoFindMatrixMain(TUint32& aPid, TUint32& aTid, TInt& aMatches)',
  'static TInt HtcleoFindHomeInitialThread(TProcessId aExpectedPid, TUint32& aPid, TUint32& aTid, TInt& aMatches)'),
 ('            if (owner.SecureId().iId == 0x101f4cd2u &&\n',
  '            // HTCLEO_HOME_KERNEL_WATCH_839: exact newborn process, before its Resume.\n'
  '            if (owner.Id().Id() == aExpectedPid.Id() &&\n'
  '                owner.SecureId().iId == 0x102750f0u &&\n'),
 ('static void HtcleoWatchHomeProcess(TProcessId /*aPid*/)',
  'static void HtcleoWatchHomeProcess(TProcessId aPid)'),
 ('    const TInt lookup = HtcleoFindMatrixMain(pid, tid, matches);',
  '    const TInt lookup = HtcleoFindHomeInitialThread(aPid, pid, tid, matches);'),
 ('_LIT(KName, "HTCLEO Matrix Context");','_LIT(KName, "HTCLEO Home Context");'),
]
def once(t,a,b):
    if t.count(a)!=1:raise ValueError('Home kernel watcher anchor drift '+repr(a))
    return t.replace(a,b,1)
def transform(text,restore=False):
    if 'HTCLEO_HOME_KERNEL_WATCH_839' in text:
        for a,b in reversed(EDITS):text=once(text,b,a)
    elif 'HtcleoFindHomeInitialThread' in text:raise ValueError('partial Home kernel watcher')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:raise ValueError('not exact838 watcher source')
    if not restore:
        for a,b in EDITS:text=once(text,a,b)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    directory=a.root/REL;path=directory/NAME
    original=path.read_text(encoding='latin-1');updated=transform(original,a.restore)
    # Early --restore may resume an interrupted lower-layer source unwind.
    # It changes only the hash-pinned helper. The normal apply still requires
    # the complete audited creation/Resume hook before any rebuilt output.
    if not a.restore and hashlib.sha256((directory/'hslaunch.cpp').read_bytes()).hexdigest()!=MAIN_SHA:
        raise ValueError('supervisor creation/Resume hook changed')
    if transform(updated,True)!=transform(original,True):raise ValueError('watcher inverse failed')
    if updated!=original:path.write_text(updated,encoding='latin-1')
    print('HTCLEO_HOME_KERNEL_WATCH='+('restored' if a.restore else
      'existing5s-HAL21-sampler-known-newborn-Home-PID-unique-initial-thread-no-target-mutation'))
if __name__=='__main__':main()
