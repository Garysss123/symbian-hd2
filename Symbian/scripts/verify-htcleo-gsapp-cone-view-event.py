#!/usr/bin/env python3
"""831 one CONE object, exact native ABI and GS-only view-event observation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-cone-view-event.py'))
BASE=runpy.run_path(str(HERE/'verify-htcleo-gsapp-redraw-frontier.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/stem_cone.dll'
PARENT=HERE.parent/'output/830-symbian3-full-gsapp-view-transition-incremental/Symbian3'
DUMP='cone-view-event-831-full-dump.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return BASE['objects']()
def sources():
    return {p.name:sha(p) for p in (SDK/P['REL']).iterdir() if p.suffix.lower()=='.cpp'}
def verify_imports(old,new):
    if {n:sorted(v) for n,v in old.items()}!={n:sorted(v) for n,v in new.items()}:
        raise ValueError('View observation imports changed')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    src=SDK/P['REL']/P['NAME'];helper=SDK/P['REL']/'htcleogsvieweventtrace.inl'
    prior=json.loads((PARENT/'build/GSAPP-REDRAW-OBJECTS.json').read_text())
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Immutable view baseline exists')
        if sha(BINARY)!=P['BASE_BINARY'] or sha(src)!=P['BASE_SOURCE'] or prior['objects']!=objects():
            raise ValueError('Parent CONE binary/object/source mismatch')
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        target=next(p for p in objects() if Path(p).name=='coevwman.o')
        (a.baseline.parent/'parent-coevwman.o').write_bytes(Path(target).read_bytes())
        a.baseline.write_text(json.dumps(dict(base_binary_sha256=sha(BINARY),objects=objects(),
           sources=sources()),indent=2)+'\n')
        print('GSVIEW_BASE_OK23-parent-certified');return
    receipt=json.loads(a.baseline.read_text());now=objects()
    if set(now)!=set(receipt['objects']):raise ValueError('CONE object inventory drift')
    changed=[n for n in now if now[n]!=receipt['objects'][n]]
    if len(changed)!=1 or Path(changed[0]).name!='coevwman.o':
        raise ValueError('Unexpected changed CONE objects '+repr(changed))
    current=sources()
    if set(current)!=set(receipt['sources']):raise ValueError('CONE source inventory drift')
    if sorted(n for n in current if current[n]!=receipt['sources'][n])!=['coevwman.cpp']:
        raise ValueError('Unexpected CONE source changes')
    if P['transform'](src.read_text(encoding='latin-1'))!=src.read_text(encoding='latin-1'):
        raise ValueError('Source observation drift')
    if helper.read_bytes()!=(HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/helper.name).read_bytes():raise ValueError('Compiled logger drift')
    before=(PARENT/'build/cone-redraw-822-full-dump.txt').read_text()
    after=(a.native/DUMP).read_text()
    if BASE['header'](before)!=BASE['header'](after):raise ValueError('CONE ABI/security/data drift')
    verify_imports(GS['imports'](before),GS['imports'](after))
    deffiles=list((SDK/'epoc32/build/stem-cone-build').glob('*/stem_cone_dll/armv5/urel/stem_cone{000a0000}.def'))
    if len(deffiles)!=1 or deffiles[0].read_bytes()!=(PARENT/'build/cone-stock-821-exports.def').read_bytes():
        raise ValueError('757 frozen CONE exports differ')
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',changed[0]],text=True)
    if 'HtcleoGsViewEventLog' not in disasm:raise ValueError('View logger absent')
    for bad in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After('):
        if bad in disasm:raise ValueError('Unexpected blocking API in observed object')
    result=dict(status='HTCLEO_GSAPP_CONE_EVENT_OBJECTS_OK',binary_sha256=sha(BINARY),
        base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),objects=now,sources=current,
        changed_objects=changed,helper_sha256=sha(helper),header=BASE['header'](after),
        exports='exact757',imports='identical830',policy='GS-only-registration-inbound-dispatch32-native-policy-no-new-trap')
    if not a.report:raise ValueError('Report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_GSAPP_CONE_EVENT_OBJECTS_OK23 changed=coevwman.o exports757 imports/data/BSS unchanged')
if __name__=='__main__':main()
