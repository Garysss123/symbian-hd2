#!/usr/bin/env python3
"""830 one Avkon object, same original ABI, source-only GS view observation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-view-transition.py'))
BASE=runpy.run_path(str(HERE/'verify-htcleo-gsapp-lifetime-observer.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/stem_avkon.dll'
PARENT=HERE.parent/'output/829-symbian3-full-gsapp-async-view-event-incremental/Symbian3'
DUMP='avkon-view-transition-830-full-dump.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return BASE['objects']()
def sources():
    return {p.name:sha(p) for p in (SDK/P['REL']).glob('*.cpp')}
def verify_imports(old,new):
    if {n:sorted(v) for n,v in old.items()}!={n:sorted(v) for n,v in new.items()}:
        raise ValueError('View observation imports changed')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    src=SDK/P['REL']/P['NAME'];helper=SDK/P['REL']/'htcleogsactivationtrace.inl'
    prior=json.loads((PARENT/'build/GSAPP-LIFETIME-OBJECTS.json').read_text())
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Immutable view baseline exists')
        if sha(BINARY)!=P['BASE_BINARY'] or sha(src)!=P['BASE_SOURCE'] or prior['objects']!=objects():
            raise ValueError('Parent Avkon binary/object/source mismatch')
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        target=next(p for p in objects() if Path(p).name=='AknViewAppUi.o')
        (a.baseline.parent/'parent-AknViewAppUi.o').write_bytes(Path(target).read_bytes())
        a.baseline.write_text(json.dumps(dict(base_binary_sha256=sha(BINARY),objects=objects(),
           sources=sources(),helper_sha256=sha(helper)),indent=2)+'\n')
        print('GSVIEW_BASE_OK198-parent-certified');return
    receipt=json.loads(a.baseline.read_text());now=objects()
    changed=[n for n in now if now[n]!=receipt['objects'][n]]
    if len(changed)!=1 or Path(changed[0]).name!='AknViewAppUi.o':
        raise ValueError('Unexpected changed Avkon objects '+repr(changed))
    current=sources()
    if sorted(n for n in current if current[n]!=receipt['sources'][n])!=['AknViewAppUi.cpp']:
        raise ValueError('Unexpected Avkon source changes')
    if P['transform'](src.read_text(encoding='latin-1'))!=src.read_text(encoding='latin-1'):
        raise ValueError('Source observation drift')
    if sha(helper)!=receipt['helper_sha256']:raise ValueError('Shared logger changed')
    before=(PARENT/'build/avkon-lifetime-823-full-dump.txt').read_text()
    after=(a.native/DUMP).read_text()
    if BASE['header'](before)!=BASE['header'](after):raise ValueError('Avkon ABI/security/data drift')
    verify_imports(GS['imports'](before),GS['imports'](after))
    deffiles=list((SDK/'epoc32/build/stem-avkon-build').glob('*/stem_avkon_dll/armv5/urel/stem_avkon{000a0000}.def'))
    if len(deffiles)!=1 or deffiles[0].read_bytes()!=(PARENT/'build/avkon-stock-822-exports.def').read_bytes():
        raise ValueError('4613 frozen Avkon exports differ')
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',changed[0]],text=True)
    if 'HtcleoGsActivationLog' not in disasm:raise ValueError('View logger absent')
    for bad in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After('):
        if bad in disasm:raise ValueError('Unexpected blocking API in observed object')
    result=dict(status='HTCLEO_GSAPP_TRANSITION_OBJECTS_OK',binary_sha256=sha(BINARY),
        base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),objects=now,sources=current,
        changed_objects=changed,helper_sha256=sha(helper),header=BASE['header'](after),
        exports='exact4613',imports='identical829',policy='GS-enqueue-C603-C604-C607-all-GS-native-ActivationTick64-no-policy-change')
    if not a.report:raise ValueError('Report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_GSAPP_TRANSITION_OBJECTS_OK198 changed=AknViewAppUi.o exports4613 imports/data/BSS unchanged')
if __name__=='__main__':main()

