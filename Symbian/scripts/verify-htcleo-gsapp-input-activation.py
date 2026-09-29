#!/usr/bin/env python3
"""828 exact one GSApp object change, four diagnostic BSS bytes, unchanged imports."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-input-activation.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
EX=runpy.run_path(str(HERE/'verify-htcleo-gsapp-exception-witness.py'))
BINARY=SDK/'epoc32/release/armv5/urel/gsapp.exe'
PARENT=HERE.parent/'output/827-symbian3-full-gsapp-child-frontier-incremental/Symbian3'
DUMP='gsapp-list-828-full-dump.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return EX['objects']()
def sources():
    paths=list((SDK/P['REL']/'Src').glob('*.cpp'))
    if len(paths)!=6:raise ValueError('Expected six GSApp sources')
    return {p.name:sha(p) for p in paths}
def verify_imports(before,after):
    if {k:sorted(v) for k,v in before.items()}!={k:sorted(v) for k,v in after.items()}:
        raise ValueError('GS list-only import contract drift')
def headers(before,after):
    if GS['header_contract'](before)!=GS['header_contract'](after):
        raise ValueError('GSApp ABI/security/heap/stack drift')
    for dump,bss in ((before,'000010'),(after,'000014')):
        if not re.search(r'^Data Size:\s*00000000\s*$',dump,re.M) or not re.search(r'^Bss\s+'+bss+r'\s*$',dump,re.M):
            raise ValueError('Expected only four diagnostic BSS bytes')
    return GS['header_contract'](after)
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    source=SDK/P['REL']/P['NAME'];header=SDK/P['REL']/'Inc/GSMainContainer.h'
    before=(PARENT/'build/gsapp-exception-824-full-dump.txt').read_text()
    prior=json.loads((PARENT/'build/GSAPP-EXCEPTION-OBJECTS.json').read_text())
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Immutable list baseline exists')
        if sha(BINARY)!=P['BASE_BINARY'] or sha(source)!=P['BASE'][P['NAME']] or prior['objects']!=objects():
            raise ValueError('Not exact827 GSApp object/binary predecessor')
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        saved=a.baseline.parent/'parent-objects';saved.mkdir()
        for path in objects():(saved/Path(path).name).write_bytes(Path(path).read_bytes())
        a.baseline.write_text(json.dumps(dict(base_binary_sha256=sha(BINARY),objects=objects(),
            sources=sources(),class_header_sha256=sha(header)),indent=2)+'\n')
        print('GSLIST_BASE_OK six-objects-parent-certificate');return
    base=json.loads(a.baseline.read_text());now=objects()
    changed=[p for p in now if now[p]!=base['objects'][p]]
    if len(changed)!=1 or Path(changed[0]).name!='GSMainContainer.o':
        raise ValueError('Unexpected GS list object delta '+repr(changed))
    current=sources()
    if [n for n in current if current[n]!=base['sources'][n]]!=['GSMainContainer.cpp']:
        raise ValueError('Unexpected GS source delta')
    if sha(header)!=base['class_header_sha256']:raise ValueError('GS class layout changed')
    text=source.read_text(encoding='latin-1')
    if P['transform'](text)!=text:raise ValueError('Missing exact list witness')
    after=(a.native/DUMP).read_text()
    h=headers(before,after);verify_imports(GS['imports'](before),GS['imports'](after))
    obj=Path(changed[0])
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',str(obj)],text=True)
    if 'HtcleoGsBootLog' not in disasm:raise ValueError('List log calls missing')
    for bad in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After(', 'RThread::Create'):
        if bad in disasm:raise ValueError('Unexpected new I/O/timer/thread')
    report=dict(status='HTCLEO_GSAPP_LIST_OBJECTS_OK',binary_sha256=sha(BINARY),
        base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),objects=now,sources=current,
        changed_objects=changed,class_header_sha256=sha(header),header=h,import_policy='identical827',
        bss_before=16,bss_after=20,exception_wrapper=EX['verify_wrapper'](),
        policy='GS-first8-list-events-index-block-type-native-activation-60C0-C6-no-policy-change')
    if not a.report:raise ValueError('Report required')
    a.report.write_text(json.dumps(report,indent=2)+'\n')
    print('HTCLEO_GSAPP_LIST_OBJECTS_OK changed=GSMainContainer.o exports=0 imports=identical data=0 bss=20')
if __name__=='__main__':main()

