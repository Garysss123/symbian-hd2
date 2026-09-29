#!/usr/bin/env python3
"""817: exact GSApp-only object/ABI evidence, eight bytes of diagnostic BSS."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-view-frontier.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/gsapp.exe'
CHANGED={'GSUi.o','GSMainView.o'}
ADDED={}
REMOVED={'avkon':[(368,0)]} # GSUi vtable now owns the override; the direct native delegate remains.


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def objects():
    out={str(p):sha(p) for p in sorted((SDK/'epoc32/build/gsapp-build').glob('*/gsapp_exe/armv5/urel/*.o'))}
    if len(out)<5 or any(sum(Path(n).name==x for n in out)!=1 for x in CHANGED):raise ValueError('GSApp object set ambiguous')
    return out


def verify_imports(before,after):
    if Counter(before.get('avkon',[]))[(368,0)]!=2 or Counter(after.get('avkon',[]))[(368,0)]!=1:
        raise ValueError('native CAknViewAppUi::HandleWsEventL delegate contract changed')
    expected={n:Counter(v) for n,v in before.items()}
    for n,values in REMOVED.items():
        if n not in expected:raise ValueError('removed provider absent')
        for v in values:
            if expected[n][v]<=0:raise ValueError('removed import absent')
            expected[n][v]-=1
            if not expected[n][v]:del expected[n][v]
    for n,values in ADDED.items():
        if n not in expected:raise ValueError('unexpected new provider')
        expected[n].update(values)
    if expected!={n:Counter(v) for n,v in after.items()}:raise ValueError('GSApp imports differ beyond exact delegate contract')


def check_headers(before,after):
    if GS['header_contract'](before)!=GS['header_contract'](after):raise ValueError('GSApp ABI/security/heap/stack changed')
    for key in ('Data Size','Data link addr'):
        def field(text):
            m=re.search(r'^'+re.escape(key)+r':\s*([^\n]+)',text,re.M)
            if not m:raise ValueError('missing '+key)
            return m[1].strip()
        if field(before)!=field(after):raise ValueError('GSApp '+key+' changed')
    def bss(t):
        m=re.search(r'^Bss\s+([0-9a-f]+)\s*$',t,re.M|re.I)
        if not m:raise ValueError('BSS absent')
        return int(m[1],16)
    if bss(before)!=8 or bss(after)!=16:raise ValueError('GSApp BSS delta is not exact two 32-bit counters')
    return GS['header_contract'](after)


def main():
    a=argparse.ArgumentParser();a.add_argument('--snapshot',action='store_true')
    a.add_argument('--baseline',type=Path,required=True);a.add_argument('--native',type=Path,required=True)
    a.add_argument('--report',type=Path);q=a.parse_args()
    root=SDK/P['REL']
    if q.snapshot:
        if q.baseline.exists():raise ValueError('Never overwrite GSApp baseline snapshot')
        if sha(BINARY)!=P['BASE_BINARY']:raise ValueError('not exact816 GSApp')
        for name in P['BASE']:
            text=(root/name).read_text(encoding='latin-1')
            if P['transform'](text,name,True)!=text:raise ValueError('snapshot requires816 source')
        data=dict(binary_sha256=sha(BINARY),sources=P['BASE'],objects=objects())
        q.baseline.write_text(json.dumps(data,indent=2)+'\n')
        print('GSAPP_BASE_SNAPSHOT_OK objects='+str(len(data['objects'])));return
    old=json.loads(q.baseline.read_text());now=objects()
    if old['binary_sha256']!=P['BASE_BINARY'] or old['sources']!=P['BASE'] or set(old['objects'])!=set(now):raise ValueError('GSApp base provenance drift')
    if sha(BINARY)==P['BASE_BINARY']:raise ValueError('GSApp relink did not happen')
    changed=[n for n in now if now[n]!=old['objects'][n]]
    if {Path(n).name for n in changed}!=CHANGED or len(changed)!=len(CHANGED):raise ValueError('unexpected GSApp changed objects: '+repr(changed))
    sources={}
    for name in P['BASE']:
        text=(root/name).read_text(encoding='latin-1')
        if P['transform'](text,name)!=text:raise ValueError('GSApp view overlay missing')
        P['transform'](text,name,True);sources[name]=sha(root/name)
    before=(q.native/'gsapp-stock-816-full-dump.txt').read_text()
    after=(q.native/'gsapp-view-817-full-dump.txt').read_text()
    header=check_headers(before,after);verify_imports(GS['imports'](before),GS['imports'](after))
    if not q.report:raise ValueError('report required')
    data=dict(status='HTCLEO_GSAPP_VIEW_OBJECTS_OK',binary_sha256=sha(BINARY),base_binary_sha256=P['BASE_BINARY'],
        objects=now,changed_objects=changed,baseline_sha256=sha(q.baseline),sources=sources,header=header,
        bss_before=8,bss_after=16,import_additions=ADDED,import_removals=REMOVED,
        policy='GSApp-eight-nonpointer-events-native-delegate-first-view-activation-no-scheduler-change')
    q.report.write_text(json.dumps(data,indent=2)+'\n')
    print('HTCLEO_GSAPP_VIEW_OBJECTS_OK objects=%d changed=%s sha256=%s' % (len(now),','.join(sorted(CHANGED)),data['binary_sha256']))


if __name__=='__main__':main()
