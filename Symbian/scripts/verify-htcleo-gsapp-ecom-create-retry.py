#!/usr/bin/env python3
"""826 one EComSession object, preserved provider ABI and native reconnect policy."""
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
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-ecom-create-retry.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
CONTROL=runpy.run_path(str(HERE/'verify-htcleo-ecom-825-source-control.py'))
BINARY=SDK/'epoc32/release/armv5/urel/ecom.dll'
DUMP='ecom-create-retry-826-full-dump.txt'
NAMES={'EComSession','ImplementationInformation','UnloadPolicy','LoadManager','EComEntry','TlsData','HtcleoEcomLog'}
# Bounded GSBOOT helper only: integer divide/remainder, RFile::Create,
# TDes8::AppendFill and RThread::Id (frozen SDK DEF ordinals).
ADDED={'drtaeabi':[(135,0)],'efsrv':[(105,0)],'euser':[(723,0),(1793,0)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():
    paths=list((SDK/'epoc32/build/ecom-client-build').glob('*/*/armv5/urel/*.o'))
    if len(paths)!=7 or {p.stem for p in paths}!=NAMES:raise ValueError('ECom exact7 objects drift')
    return {p.name:sha(p) for p in paths}
def sources():
    root=SDK/P['REL']/'frame'
    return {name+'.cpp':sha(root/(name+'.cpp')) for name in NAMES}
def exports():
    paths=list((SDK/'epoc32/build/ecom-client-build').glob('*/*/armv5/urel/*.def'))
    if len(paths)!=1:raise ValueError('Generated ECom DEF ambiguous')
    text=paths[0].read_text()
    if 'MISSING' in text:raise ValueError('Missing ECom exports')
    entries=[(m[1],int(m[2])) for m in re.finditer(r'^\s*(\S+)\s+@\s+(\d+)\s+NONAME',text,re.M)]
    if len(entries)!=39 or sorted(x[1] for x in entries)!=list(range(1,40)):raise ValueError('ECom39 ABI drift')
    return entries
def header(text):
    result={}
    for key in ('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size',
                'Max Heap Size','Stack Size','Code link addr','Data link addr','Data Size'):
        m=re.search(r'^'+re.escape(key)+r':\s*([^\n]+)',text,re.M)
        if not m:raise ValueError('Missing header '+key)
        result[key]=' '.join(m[1].lower().split())
    if result['Data Size']!='00000000' or not re.search(r'^Bss\s+000000\s*$',text,re.M):
        raise ValueError('ECom DLL data or BSS changed')
    for line in ('EPOC Dll for ARMV5 CPU','Image FPU support : Soft VFP','ARM EABI','Built against EKA2'):
        if line not in text.splitlines():raise ValueError('ECom ABI changed')
    if not re.search(r'^Uids:\s+10000079 1000008d 10009d8e ',text,re.M):raise ValueError('ECom UID drift')
    values=[int(m[1],16) for m in re.finditer(r'^\s*Ordinal\s+\d+:\s*([0-9a-f]+)',text,re.M|re.I)]
    if len(values)!=39 or not all(values):raise ValueError('ECom export holes')
    return result
def verify_imports(before,after):
    expected={k:Counter(v) for k,v in before.items()}
    for k,values in ADDED.items():expected[k].update(values)
    if expected!={k:Counter(v) for k,v in after.items()}:
        added={k:list((Counter(v)-Counter(before.get(k,()))).elements()) for k,v in after.items()}
        removed={k:list((Counter(v)-Counter(after.get(k,()))).elements()) for k,v in before.items()}
        raise ValueError('Unexpected ECom import delta '+repr((added,removed)))
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    path=SDK/P['REL']/P['NAME'];mmp=SDK/P['REL']/'MMPFiles/ECom.mmp'
    stock=(a.native/'ecom-stock-825-full-dump.txt').read_text()
    control=a.baseline.parent/'ecom-native-source-control-825.dll'
    control_proof=json.loads((a.baseline.parent/'SOURCE-CONTROL.json').read_text())
    if (control_proof['status']!='ECOM825_SOURCE_CONTROL_OK' or
            control_proof['parent_sha256']!=P['BASE_BINARY'] or
            control_proof['control_sha256']!=sha(control) or
            not control_proof['no_code_data_import_export_or_relocation_exclusions']):
        raise ValueError('825 source control provenance drift')
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Immutable826 baseline exists')
        if sha(BINARY)!=sha(control) or sha(path)!=P['BASE_SOURCE']:raise ValueError('Not reconstructed825 control')
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        a.baseline.write_text(json.dumps(dict(base_binary_sha256=P['BASE_BINARY'],control_sha256=sha(control),objects=objects(),
            sources=sources(),mmp_sha256=sha(mmp),exports=exports(),header=header(stock),
            imports=GS['imports'](stock)),indent=2)+'\n')
        print('GSCREATE_BASE_OK objects=7 exports=39');return
    base=json.loads(a.baseline.read_text());now=objects()
    if base['control_sha256']!=sha(control):raise ValueError('Control snapshot drift')
    changes=sorted(k for k in now if now[k]!=base['objects'][k])
    if changes!=['EComSession.o']:raise ValueError('Unexpected ECom objects '+repr(changes))
    current=sources()
    if sorted(k for k in current if current[k]!=base['sources'][k])!=['EComSession.cpp']:
        raise ValueError('Unexpected ECom source delta')
    source=path.read_text()
    if P['transform'](source)!=source or sha(mmp)!=base['mmp_sha256']:raise ValueError('ECom source/MMP drift')
    if [list(x) for x in exports()]!=base['exports']:raise ValueError('Frozen39 exports changed')
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsplugintrace.inl'
    if (path.parent/helper.name).read_bytes()!=helper.read_bytes():raise ValueError('Bounded GS logger drift')
    after=(a.native/DUMP).read_text()
    if header(after)!=base['header'] or header(stock)!=base['header']:raise ValueError('ECom ABI/security drift')
    verify_imports(GS['imports'](stock),GS['imports'](after))
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',
        str(next((SDK/'epoc32/build/ecom-client-build').glob('*/*/armv5/urel/EComSession.o')))],text=True)
    if 'HtcleoGsPluginLog' not in disasm:raise ValueError('GS retry logger missing')
    # Existing legacy logger has Flush in another unchanged object; the new sink must not.
    for bad in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After('):
        if bad in disasm:raise ValueError('New EComSession high-rate/blocking API '+bad)
    result=dict(status='HTCLEO_GSAPP_CREATE_RETRY_OBJECTS_OK',binary_sha256=sha(BINARY),
        base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),
        control_sha256=sha(control),source_control=control_proof,
        changed_objects=changes,objects=now,sources=current,header=header(after),exports=base['exports'],
        import_additions=ADDED,helper_sha256=sha(helper),mmp_sha256=sha(mmp),
        policy='GS-create-minus15-one-native-reconnect-C731-C733-real-result-no-empty-fallback')
    if not a.report:raise ValueError('Report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_GSAPP_CREATE_RETRY_OBJECTS_OK objects=7 changed=EComSession.o exports=39 data=0 bss=0')
if __name__=='__main__':main()
