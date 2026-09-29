#!/usr/bin/env python3
"""839: existing ailaunch sampler retargeted to its known newborn Home, no kernel change."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
HERE=Path(__file__).resolve().parent
P=runpy.run_path(str(HERE/'apply-htcleo-home-kernel-watch.py'))
SDK=Path('/root/symbian3-full');ROOT=SDK/P['REL']
BINARY=SDK/'epoc32/release/armv5/urel/ailaunch.exe'
PARENT=HERE.parent/'output/838-symbian3-full-vws-session-deactivation-incremental/Symbian3'
EVID=HERE.parent/'output/iteration-evidence/839-home-kernel-watch'
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
E32=runpy.run_path(str(HERE/'verify-htcleo-viewcli-source-control.py'))
DUMP='ailaunch-home-watch-839-full-dump.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():
    paths=list((SDK/'epoc32/build/homescreen-build').glob('*/ailaunch_exe/armv5/urel/*.o'))
    if len(paths)!=4 or {p.name for p in paths}!={'hslaunch.o','hsprocessmonitor.o','hsshutdownmonitor.o','htcleohomelog.o'}:
        raise ValueError('unexpected ailaunch objects')
    return {str(p):sha(p) for p in paths}
def control_proof():
    parent=PARENT/'build/incremental-release-cache/ailaunch.exe'
    if sha(parent)!=P['BASE_BINARY'] or sha(EVID/'ailaunch-parent838.exe')!=P['BASE_BINARY']:
        raise ValueError('ailaunch parent identity drift')
    original=E32['unpack_e32'](parent);now=E32['unpack_e32'](BINARY)
    if len(original)!=len(now):raise ValueError('ailaunch unmodified-control length changed')
    differences=[i for i,(a,b) in enumerate(zip(original,now)) if a!=b]
    if any(i not in set(range(20,24))|set(range(36,44)) for i in differences):
        raise ValueError('ailaunch control differs beyond timestamp/headerCRC '+repr(differences[:32]))
    return dict(parent_sha256=sha(parent),control_sha256=sha(BINARY),uncompressed_bytes=len(now),
                ignored_offsets='headerCRC20..23,timestamp36..43-only',different_offsets=differences)
def header(text):
    import re
    out={}
    for key in ('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size','Max Heap Size',
                'Stack Size','Code link addr','Data link addr','Data Size'):
        m=re.search(r'^'+re.escape(key)+r':\s*([^\n]+)',text,re.M)
        if not m:raise ValueError('missing launch ABI '+key)
        out[key]=' '.join(m[1].split())
    for literal in ('EPOC Exe for ARMV5 CPU','Priority Foreground','Image FPU support : Soft VFP','Number of exports = 0'):
        if literal not in text:raise ValueError('launch platform/export drift')
    if not re.search(r'^Uids:\s+1000007a 1000008d 200286e3 ',text,re.M):raise ValueError('launcher UID drift')
    m=re.search(r'^Bss\s+(\S+)\s*$',text,re.M)
    if not m:raise ValueError('launcher BSS missing')
    out['BSS']=m[1]
    return out
def check_sources():
    body=(ROOT/P['NAME']).read_text(encoding='latin-1')
    if P['transform'](body)!=body:raise ValueError('Home watcher overlay drift')
    if sha(ROOT/'hslaunch.cpp')!=P['MAIN_SHA']:raise ValueError('normal supervisor code changed')
def main():
    p=argparse.ArgumentParser();p.add_argument('--control-check',action='store_true');p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,default=EVID/'BASE-OBJECTS.json')
    p.add_argument('--native',type=Path,default=HERE.parent/'output/qsd8250-native-full-rom');p.add_argument('--report',type=Path);a=p.parse_args()
    if a.control_check:
        proof=control_proof();report=EVID/'CONTROL-PROOF.json'
        if report.exists():raise ValueError('do not overwrite control proof')
        report.write_text(json.dumps(proof,indent=2)+'\n');shutil.copyfile(BINARY,EVID/'ailaunch-control.exe')
        print('AILAUNCH_CONTROL_EXACT except timestamp/headerCRC');return
    if a.snapshot:
        if a.baseline.exists():raise ValueError('never overwrite839 baseline')
        proof=json.loads((EVID/'CONTROL-PROOF.json').read_text())
        if sha(BINARY)!=P['BASE_BINARY'] or sha(ROOT/P['NAME'])!=P['BASE_SOURCE'] or sha(ROOT/'hslaunch.cpp')!=P['MAIN_SHA']:
            raise ValueError('not exact838 launcher')
        a.baseline.write_text(json.dumps(dict(binary_sha256=sha(BINARY),objects=objects(),
           helper_sha256=sha(ROOT/P['NAME']),main_sha256=sha(ROOT/'hslaunch.cpp'),
           control_proof_sha256=sha(EVID/'CONTROL-PROOF.json')),indent=2)+'\n')
        target=next(Path(n) for n in objects() if Path(n).name=='hslaunch.o')
        shutil.copyfile(target,EVID/'parent-hslaunch.o');print('HOME_WATCH_BASE_OK4');return
    base=json.loads(a.baseline.read_text());now=objects()
    if set(now)!=set(base['objects']):raise ValueError('launcher object inventory drift')
    changed=[n for n in now if now[n]!=base['objects'][n]]
    if len(changed)!=1 or Path(changed[0]).name!='hslaunch.o':raise ValueError('unexpected launcher object changes '+repr(changed))
    check_sources()
    before=(PARENT/'build/ailaunch-e32-dump.txt').read_text();after=(a.native/DUMP).read_text()
    if header(before)!=header(after):raise ValueError('launcher ABI/data/BSS changed')
    norm=lambda x:{n:Counter(tuple(v) for v in vals) for n,vals in x.items()}
    if norm(GS['imports'](before))!=norm(GS['imports'](after)):raise ValueError('launcher imports changed')
    result=dict(status='HTCLEO_HOME_KERNEL_WATCH_OBJECTS_OK',binary_sha256=sha(BINARY),
       base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),objects=now,changed_objects=changed,
       helper_sha256=sha(ROOT/P['NAME']),main_sha256=sha(ROOT/'hslaunch.cpp'),header=header(after),
       imports='identical838',exports='zero',control_proof_sha256=sha(EVID/'CONTROL-PROOF.json'),
       policy='existing5s-HAL21-sampler-known-newborn-Home-PID-unique-initial-thread-no-target-mutation')
    if not a.report:raise ValueError('--report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_HOME_KERNEL_WATCH_OBJECTS_OK onlyhslaunch.o ABI/imports/data/BSS unchanged')
if __name__=='__main__':main()
