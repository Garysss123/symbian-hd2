#!/usr/bin/env python3
"""Targeted Avkon object/ABI/import evidence for819, no blanket relaxation."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PATCH=runpy.run_path(str(HERE/'apply-htcleo-gsapp-keyblock-local.py'))
IMPORT=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))['imports']
BINARY=SDK/'epoc32/release/armv5/urel/stem_avkon.dll'
ADDED={}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def objects():
    result={str(path):sha(path) for path in sorted((SDK/'epoc32/build/stem-avkon-build').glob('*/stem_avkon_dll/armv5/urel/*.o'))}
    if len(result)<20 or sum(Path(name).name=='aknsgcc.o' for name in result)!=1:
        raise ValueError('Avkon object set ambiguous/incomplete')
    return result


def header(text):
    result={}
    for key in ('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size','Max Heap Size',
                'Stack Size','Code link addr','Data link addr','Data Size'):
        m=re.search(r'^'+re.escape(key)+r':\s*([^\n]+)',text,re.M)
        if not m: raise ValueError('missing Avkon ABI field: '+key)
        result[key]=' '.join(m[1].split())
    for literal in ('EPOC Dll for ARMV5 CPU','SMP Safe : False','Image FPU support : Soft VFP'):
        if literal not in text: raise ValueError('Avkon platform contract changed')
    if not re.search(r'^Uids:\s+10000079 1000008d 100056c6 ',text,re.M):raise ValueError('Avkon UID changed')
    if not re.search(r'^Bss\s+000028\s*$',text,re.M):raise ValueError('new DLL global data')
    return result


def verify_imports(before,after):
    expected={name:Counter(values) for name,values in before.items()}
    for name,values in ADDED.items():
        if name not in expected:raise ValueError('unexpected new logger provider')
        expected[name].update(values)
    if expected!={name:Counter(values) for name,values in after.items()}:
        raise ValueError('Avkon imports differ beyond exact logger additions')


def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    if a.snapshot:
        if a.baseline.exists():raise ValueError('never overwrite Avkon base-object snapshot')
        if sha(BINARY)!=PATCH['BASE_BINARY']:raise ValueError('not exact818 Avkon')
        text=(SDK/PATCH['REL']/PATCH['NAME']).read_text(encoding='latin-1')
        if PATCH['transform'](text,True)!=text:raise ValueError('snapshot requires restored SGC source')
        result=dict(binary_sha256=sha(BINARY),source_sha256=PATCH['BASE_SHA'],objects=objects())
        a.baseline.write_text(json.dumps(result,indent=2)+'\n')
        print('AVKON_BASE_SNAPSHOT_OK objects='+str(len(result['objects'])))
        return
    base=json.loads(a.baseline.read_text());now=objects()
    if sha(BINARY)==PATCH['BASE_BINARY']:raise ValueError('Avkon relink not completed; binary is still the parent')
    if base['binary_sha256']!=PATCH['BASE_BINARY'] or base['source_sha256']!=PATCH['BASE_SHA'] or set(now)!=set(base['objects']):
        raise ValueError('Avkon object provenance changed')
    changed=[name for name,value in now.items() if value!=base['objects'][name]]
    if len(changed)!=1 or Path(changed[0]).name!='aknsgcc.o':raise ValueError('unexpected Avkon changed objects: '+repr(changed))
    source=(SDK/PATCH['REL']/PATCH['NAME']).read_text(encoding='latin-1')
    if PATCH['transform'](PATCH['transform'](source,True))!=source:raise ValueError('SGC source drift')
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogskeyblock.inl'
    if (SDK/PATCH['REL']/helper.name).read_bytes()!=helper.read_bytes():raise ValueError('compiled helper drift')
    before=(a.native/'avkon-stock-818-full-dump.txt').read_text()
    after=(a.native/'avkon-keyblock-819-full-dump.txt').read_text()
    if header(before)!=header(after):raise ValueError('Avkon ABI changed')
    old_imports=IMPORT(before);new_imports=IMPORT(after)
    verify_imports(old_imports,new_imports)
    old_def=(a.native/'avkon-stock-818-exports.def').read_bytes()
    new_defs=list((SDK/'epoc32/build/stem-avkon-build').glob('*/stem_avkon_dll/armv5/urel/stem_avkon{000a0000}.def'))
    if len(new_defs)!=1 or new_defs[0].read_bytes()!=old_def:raise ValueError('4613 Avkon exports changed')
    result=dict(status='HTCLEO_GSAPP_KEYBLOCK_OBJECTS_OK',binary_sha256=sha(BINARY),base_binary_sha256=PATCH['BASE_BINARY'],
                changed_objects=changed,objects=now,baseline_sha256=sha(a.baseline),helper_sha256=sha(helper),
                source_sha256=hashlib.sha256(source.encode('latin-1')).hexdigest(),header=header(after),
                import_contract='exact-logger-import-contract',import_additions=ADDED,export_contract='exact4613-def-bytes',
                policy='GSApp-zero-handle-keyblock-IPC-skip-first-call4-private-bit6-valid-and-server-retained')
    if not a.report:raise ValueError('--report is required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_GSAPP_KEYBLOCK_OBJECTS_OK objects=%d changed=%s sha256=%s' % (len(now),Path(changed[0]).name,result['binary_sha256']))


if __name__=='__main__':main()
