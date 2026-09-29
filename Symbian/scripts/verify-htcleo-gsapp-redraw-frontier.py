#!/usr/bin/env python3
"""822: CONE first-redraw observation, exact one-object/ABI/import verification."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PATCH=runpy.run_path(str(HERE/'apply-htcleo-gsapp-redraw-frontier.py'))
IMPORT=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))['imports']
BINARY=SDK/'epoc32/release/armv5/urel/stem_cone.dll'
ADDED={'drtaeabi':[(135,0)],'efsrv':[(105,0)],'euser':[(723,0),(1032,0)]}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def objects():
    result={str(path):sha(path) for path in sorted((SDK/'epoc32/build/stem-cone-build').glob('*/stem_cone_dll/armv5/urel/*.o'))}
    if len(result)!=23 or sum(Path(name).name=='COEPRIV.o' for name in result)!=1:
        raise ValueError('CONE object set ambiguous/incomplete')
    return result


def header(text):
    result={}
    for key in ('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size','Max Heap Size',
                'Stack Size','Code link addr','Data link addr','Data Size'):
        m=re.search(r'^'+re.escape(key)+r':\s*([^\n]+)',text,re.M)
        if not m: raise ValueError('missing CONE ABI field: '+key)
        result[key]=' '.join(m[1].split())
    for literal in ('EPOC Dll for ARMV5 CPU','SMP Safe : True','Image FPU support : Soft VFP'):
        if literal not in text: raise ValueError('CONE platform contract changed')
    if not re.search(r'^Uids:\s+10000079 1000008d 10003a41 ',text,re.M):raise ValueError('CONE UID changed')
    if not re.search(r'^Bss\s+000000\s*$',text,re.M):raise ValueError('new DLL global data')
    return result


def verify_imports(before,after):
    expected={name:Counter(values) for name,values in before.items()}
    for name,values in ADDED.items():
        if name not in expected:raise ValueError('unexpected new logger provider')
        expected[name].update(values)
    if expected!={name:Counter(values) for name,values in after.items()}:
        raise ValueError('CONE imports differ beyond pinned logger additions')


def verify_queue_disassembly(text):
    start=text.index('<_ZN12CCoeRedrawer5QueueEv>:\n')
    tail=text[start:]
    end=re.search(r'\n[0-9a-f]+ <[^>]+>:\n',tail,re.I)
    body=tail[:end.start()] if end else tail
    calls=re.findall(r'R_ARM_\S*CALL\s+(\S+)',body)
    ready='_ZN10RWsSession11RedrawReadyEP14TRequestStatus'
    active='_ZN7CActive9SetActiveEv'
    selected=[s for s in calls if s in (ready,active)]
    # Compiler splits the original stock branch into unobserved and GS-first
    # paths. Matrix retains arm-before-ready; these are mutually exclusive,
    # not three requests in one Queue invocation. Source inverse is also exact.
    if selected != [ready,active,ready,active,active,ready]:
        raise ValueError('Queue request/arm path order changed: '+repr(selected))
    for marker in ('0000c801','0000c802','0000c803','101f4cd2'):
        if marker not in body: raise ValueError('Missing queue selector/stage '+marker)
    if re.search(r'WaitForRequest|RequestComplete|User::After',text):
        raise ValueError('New wait/completion in changed redraw object')
    return 'three-mutually-exclusive-paths-stock-stock-Matrix-one-request-each'


def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    if a.snapshot:
        if a.baseline.exists():raise ValueError('never overwrite CONE base-object snapshot')
        if sha(BINARY)!=PATCH['BASE_BINARY']:raise ValueError('not exact821 CONE')
        text=(SDK/PATCH['REL']/PATCH['NAME']).read_text(encoding='latin-1')
        if PATCH['transform'](text,True)!=text:raise ValueError('snapshot requires restored COEPRIV source')
        result=dict(binary_sha256=sha(BINARY),source_sha256=PATCH['BASE_SHA'],objects=objects())
        a.baseline.write_text(json.dumps(result,indent=2)+'\n')
        print('CONE_BASE_SNAPSHOT_OK objects='+str(len(result['objects'])))
        return
    base=json.loads(a.baseline.read_text());now=objects()
    if sha(BINARY)==PATCH['BASE_BINARY']:raise ValueError('CONE relink not completed; binary is still the parent')
    if base['binary_sha256']!=PATCH['BASE_BINARY'] or base['source_sha256']!=PATCH['BASE_SHA'] or set(now)!=set(base['objects']):
        raise ValueError('CONE object provenance changed')
    changed=[name for name,value in now.items() if value!=base['objects'][name]]
    if len(changed)!=1 or Path(changed[0]).name!='COEPRIV.o':raise ValueError('unexpected CONE changed objects: '+repr(changed))
    source=(SDK/PATCH['REL']/PATCH['NAME']).read_text(encoding='latin-1')
    if PATCH['transform'](PATCH['transform'](source,True))!=source:raise ValueError('COEPRIV source drift')
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsredrawtrace.inl'
    if (SDK/PATCH['REL']/helper.name).read_bytes()!=helper.read_bytes():raise ValueError('compiled helper drift')
    before=(a.native/'cone-stock-821-full-dump.txt').read_text()
    after=(a.native/'cone-redraw-822-full-dump.txt').read_text()
    if header(before)!=header(after):raise ValueError('CONE ABI changed')
    old_imports=IMPORT(before);new_imports=IMPORT(after)
    verify_imports(old_imports,new_imports)
    queue_proof=verify_queue_disassembly((a.native/'stem-cone-redrawer-arm-before-ready-urel.disasm').read_text())
    old_def=(a.native/'cone-stock-821-exports.def').read_bytes()
    new_defs=list((SDK/'epoc32/build/stem-cone-build').glob('*/stem_cone_dll/armv5/urel/stem_cone{000a0000}.def'))
    if len(new_defs)!=1 or new_defs[0].read_bytes()!=old_def:raise ValueError('757 CONE exports changed')
    result=dict(status='HTCLEO_GSAPP_REDRAW_OBJECTS_OK',binary_sha256=sha(BINARY),base_binary_sha256=PATCH['BASE_BINARY'],
                changed_objects=changed,objects=now,baseline_sha256=sha(a.baseline),helper_sha256=sha(helper),
                source_sha256=hashlib.sha256(source.encode('latin-1')).hexdigest(),header=header(after),
                import_contract='diagnostic-only-additions-no-removals',import_additions=ADDED,export_contract='exact757-def-bytes',
                queue_proof=queue_proof,
                policy='GS-first-native-redraw-and-pre-native-panic-no-queue-drawing-or-error-change')
    if not a.report:raise ValueError('--report is required')
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
