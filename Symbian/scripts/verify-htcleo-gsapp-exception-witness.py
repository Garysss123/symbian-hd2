#!/usr/bin/env python3
"""824 GSApp-only exception witness: original ABI, one changed object, naked entry."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PATCH=runpy.run_path(str(HERE/'apply-htcleo-gsapp-exception-witness.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/gsapp.exe'
ADDED={'euser':[(635,0),(1033,0),(1801,0),(620,0),(1854,0),(1951,0),(602,0)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():
    out={str(p):sha(p) for p in sorted((SDK/'epoc32/build/gsapp-build').glob('*/gsapp_exe/armv5/urel/*.o'))}
    if len(out)!=6 or sum(Path(p).name=='GSApp.o' for p in out)!=1:raise ValueError('GSApp object set drift')
    return out
def headers(before,after):
    if GS['header_contract'](before)!=GS['header_contract'](after):raise ValueError('GSApp ABI/security/heap/stack changed')
    for text in (before,after):
        if not re.search(r'^Data Size:\s*00000000\s*$',text,re.M) or not re.search(r'^Bss\s+000010\s*$',text,re.M):
            raise ValueError('GSApp Data/BSS changed')
    return GS['header_contract'](after)
def verify_imports(before,after):
    expected={n:Counter(v) for n,v in before.items()}
    for name,values in ADDED.items():
        if name not in expected:raise ValueError('new exception provider')
        expected[name].update(values)
    if expected!={n:Counter(v) for n,v in after.items()}:
        delta={n:{'added':list((Counter(after.get(n,[]))-Counter(before.get(n,[]))).elements()),
                  'removed':list((Counter(before.get(n,[]))-Counter(after.get(n,[]))).elements())}
               for n in set(before)|set(after) if Counter(before.get(n,[]))!=Counter(after.get(n,[]))}
        raise ValueError('imports beyond exception witness; actual='+repr(delta))
def verify_wrapper():
    files=list((SDK/'epoc32/build/gsapp-build').glob('*/gsapp_exe/armv5/urel/GSApp.o'))
    if len(files)!=1:raise ValueError('GSApp entry object ambiguous')
    text=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',str(files[0])],text=True)
    m=re.search(r'<HtcleoGsSoftwareException\(TExcType\)>:\n(.*?)(?:\n\n|\Z)',text,re.S)
    if not m:raise ValueError('naked GS entry absent')
    body=m[1]
    instructions=re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{4})\s+',body,re.M)
    if (instructions[:2]!=['4669','4672'] or len(instructions)<3 or int(instructions[2],16)&0xf800!=0xe000 or
        'R_ARM_THM_JUMP11' not in body or 'HtcleoGsExceptionStackBody' not in body):
        raise ValueError('GS handler entry no longer captures SP/LR then tail branches')
    return dict(object=str(files[0]),sha256=sha(files[0]),entry_disassembly=body.strip())
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    source=SDK/PATCH['REL']/PATCH['NAME'];text=source.read_text(encoding='latin-1')
    if a.snapshot:
        if a.baseline.exists():raise ValueError('never overwrite GS baseline')
        if sha(BINARY)!=PATCH['BASE_BINARY'] or PATCH['transform'](text,True)!=text:raise ValueError('not original823 GSApp')
        a.baseline.write_text(json.dumps(dict(binary_sha256=sha(BINARY),source_sha256=PATCH['BASE_SHA'],objects=objects()),indent=2)+'\n')
        print('GSAPP_EXCEPTION_BASE_OK objects=6');return
    base=json.loads(a.baseline.read_text());now=objects()
    if base['binary_sha256']!=PATCH['BASE_BINARY'] or base['source_sha256']!=PATCH['BASE_SHA'] or set(base['objects'])!=set(now):
        raise ValueError('GS exception provenance changed')
    changed=[n for n in now if now[n]!=base['objects'][n]]
    if len(changed)!=1 or Path(changed[0]).name!='GSApp.o':raise ValueError('unexpected changed GS objects '+repr(changed))
    if PATCH['transform'](text)!=text:raise ValueError('GS source overlay drift')
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsexceptionstack.inl'
    if helper.read_bytes()!=(source.parent/helper.name).read_bytes():raise ValueError('GS compiled helper drift')
    before=(a.native/'gsapp-stock-823-full-dump.txt').read_text()
    after=(a.native/'gsapp-exception-824-full-dump.txt').read_text()
    header=headers(before,after);verify_imports(GS['imports'](before),GS['imports'](after))
    wrapper=verify_wrapper()
    if not a.report:raise ValueError('report required')
    data=dict(status='HTCLEO_GSAPP_EXCEPTION_OBJECTS_OK',binary_sha256=sha(BINARY),base_binary_sha256=PATCH['BASE_BINARY'],
              changed_objects=changed,objects=now,source_sha256=sha(source),helper_sha256=sha(helper),
              baseline_sha256=sha(a.baseline),header=header,import_additions=ADDED,entry_wrapper=wrapper,
              policy='GS-no-existing-handler-GSX1-bounded240-terminal-restore-reraise-no-normal-policy-change')
    a.report.write_text(json.dumps(data,indent=2)+'\n')
    print('HTCLEO_GSAPP_EXCEPTION_OBJECTS_OK objects=6 changed=GSApp.o data=0 bss=16 exports=0')
if __name__=='__main__':main()
