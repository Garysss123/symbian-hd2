#!/usr/bin/env python3
"""821: source-only root loader observation against unmodified GCCE calibration."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PATCH=runpy.run_path(str(HERE/'apply-htcleo-gsapp-plugin-frontier.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/gsframework.dll'
CALIBRATION_SHA='338cec8c3f23ef97f914d6bc3d61239151d2a64a4126d2a657f03e567d4ac62c'
ADDED={'drtaeabi':[(135,0),(222,0)],
       'efsrv':[(105,0),(263,0),(390,0),(93,0),(68,0),(97,0),(300,0)],
       'euser':[(760,0),(723,0),(1472,0),(1032,0),(1854,0),(758,0),(1849,0),(737,0),(2103,0),(1793,0)]}
CONSTRUCTORS=['_ZN11CGSBaseViewC1Ev','_ZN15CGSBaseDocumentC1ER15CEikApplication',
         '_ZN15CGSParentPluginC1Ev','_ZN16CGSBaseContainerC1Ev']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def objects(baseline=False):
    root=SDK/'epoc32/build'/('gsframework-baseline' if baseline else 'gsframework-build')
    files=list(root.glob('*/*/armv5/urel/*.o'))
    result={p.name:sha(p) for p in files}
    if len(files)!=15 or len(result)!=15 or 'GSPluginLoader.o' not in result:
        raise ValueError('Expected exact15 GSFramework objects')
    return result

def sources():
    root=SDK/PATCH['REL'];out={}
    for p in sorted((root/'src').glob('*.cpp')):
        text=p.read_text(encoding='latin-1')
        if p.name=='GSPluginLoader.cpp': text=PATCH['transform'](text,True)
        out[p.name]=hashlib.sha256(text.encode('latin-1')).hexdigest()
    # GSPluginInterface.cpp also exists here but is not compiled by this MMP.
    if len(out)!=16 or 'GSPluginInterface.cpp' not in out or out['GSPluginLoader.cpp']!=PATCH['BASE_SOURCE']:
        raise ValueError('Unexpected GSFramework source set')
    return out

def header(text):
    out={}
    for k in ('Flags','Secure ID','Vendor ID','Capabilities','Module Version',
              'Min Heap Size','Max Heap Size','Stack Size','Code link addr','Data link addr','Data Size'):
        m=re.search(r'^'+re.escape(k)+r':\s*([^\n]+)',text,re.M)
        if not m: raise ValueError('Missing header '+k)
        out[k]=' '.join(m[1].lower().split())
    for s in ('EPOC Dll for ARMV5 CPU','Image FPU support : Soft VFP','ARM EABI','Built against EKA2'):
        if s not in text.splitlines(): raise ValueError('ABI missing '+s)
    if not re.search(r'^Uids:\s+10000079 1000008d 1020723f ',text,re.M): raise ValueError('UID drift')
    if not re.search(r'^Bss\s+000000\s*$',text,re.M): raise ValueError('DLL BSS changed')
    if out['Data Size']!='00000000': raise ValueError('DLL initialized data changed')
    return out

def verify_delta(before,after):
    expected={n:Counter(v) for n,v in before.items()}
    for n,v in ADDED.items():
        if n not in expected: raise ValueError('Unexpected new import provider')
        expected[n].update(v)
    if expected!={n:Counter(v) for n,v in after.items()}: raise ValueError('Import delta beyond bounded logger')

def def_entries(text):
    return [(m[1],int(m[2])) for m in re.finditer(r'^\s*(\S+)\s+@\s+(\d+)\s+NONAME',text,re.M)]

def verify_exports(dump,baseline=False):
    root=SDK/'epoc32/build'/('gsframework-baseline' if baseline else 'gsframework-build')
    paths=list(root.glob('*/*/armv5/urel/*.def'))
    if len(paths)!=1: raise ValueError('Ambiguous generated export DEF')
    frozen=SDK/PATCH['REL'].parent/'EABI/GSFrameworkU.DEF'
    if sha(frozen)!=PATCH['BASE_DEF']: raise ValueError('Frozen DEF drift')
    base=def_entries(frozen.read_text());now=def_entries(paths[0].read_text())
    expected=base+[(s,124+i) for i,s in enumerate(CONSTRUCTORS)]
    if len(base)!=123 or now!=expected: raise ValueError('Original123 export ordinals not preserved')
    values={int(m[1]):int(m[2],16) for m in re.finditer(r'^\s*Ordinal\s+(\d+):\s*([0-9a-f]+)',dump,re.M|re.I)}
    if len(values)!=127 or any(v==0 for v in values.values()): raise ValueError('Expected123 originals plus4 compiler C1 constructors')
    ords=dict(now)
    for symbol in CONSTRUCTORS:
        # GCCE emits complete-object C1 constructors in addition to the frozen
        # base-object C2 entries. Virtual-base initialization can differ: do
        # not pretend these are address-identical aliases. No old ordinal moves.
        if symbol.replace('C1','C2') not in dict(base):
            raise ValueError('Extra C1 constructor lacks its original C2 entry')
    return sha(paths[0])

def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    evidence=a.baseline.parent
    stock=evidence/'gsframework-stock-820.dll'
    calibration=evidence/'gsframework-gcce-baseline-821.dll'
    if sha(stock)!=PATCH['BASE_BINARY'] or sha(calibration)!=CALIBRATION_SHA:
        raise ValueError('Calibration/stock provenance drift')
    original=(a.native/'gsframework-stock-820-full-dump.txt').read_text()
    base=(a.native/'gsframework-calibration-821-full-dump.txt').read_text()
    if header(original)!=header(base): raise ValueError('GCCE calibration ABI/security changed')
    baseline_def_sha=verify_exports(base,True)
    if a.snapshot:
        if a.baseline.exists(): raise ValueError('Never overwrite calibration receipt')
        data=dict(stock_sha256=sha(stock),calibration_sha256=sha(calibration),
                  sources=sources(),objects=objects(True),baseline_def_sha256=baseline_def_sha)
        a.baseline.write_text(json.dumps(data,indent=2)+'\n')
        print('GSPLUGIN_BASE_SNAPSHOT_OK objects=15 original123+4C1constructors');return
    receipt=json.loads(a.baseline.read_text())
    if receipt['sources']!=sources() or receipt['objects']!=objects(True) or receipt['calibration_sha256']!=CALIBRATION_SHA or receipt['baseline_def_sha256']!=baseline_def_sha:
        raise ValueError('Calibration receipt mismatch')
    now=objects();changed=[n for n in now if now[n]!=receipt['objects'][n]]
    if changed!=['GSPluginLoader.o']: raise ValueError('Unexpected changed objects '+repr(changed))
    path=SDK/PATCH['REL']/'src/GSPluginLoader.cpp';source=path.read_text(encoding='latin-1')
    if PATCH['transform'](source)!=source: raise ValueError('Missing source overlay')
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsplugintrace.inl'
    if helper.read_bytes()!=(path.parent/helper.name).read_bytes(): raise ValueError('Compiled helper drift')
    mmp=SDK/PATCH['REL']/'GSFramework_htcleo.mmp'
    if mmp.read_text(encoding='latin-1')!=PATCH['code_mmp']((mmp.parent/'GSFramework.mmp').read_text(encoding='latin-1')):
        raise ValueError('Code-only MMP drift')
    after=(a.native/'gsframework-plugin-821-full-dump.txt').read_text()
    if header(base)!=header(after): raise ValueError('Diagnostic ABI/security drift')
    verify_delta(GS['imports'](base),GS['imports'](after))
    exports=verify_exports(after)
    if not a.report: raise ValueError('Report required')
    data=dict(status='HTCLEO_GSAPP_PLUGIN_OBJECTS_OK',binary_sha256=sha(BINARY),
              base_binary_sha256=sha(stock),calibration_sha256=sha(calibration),objects=now,
              changed_objects=changed,sources=sources(),loader_sha256=sha(path),helper_sha256=sha(helper),
              baseline_sha256=sha(a.baseline),export_def_sha256=exports,header=header(after),
              original_exports=123,compiler_C1_constructors=CONSTRUCTORS,import_additions=ADDED,
              policy='GS-root-first2-RunL-LoadNext-RunError-32-records-per-invocation-no-policy-change')
    a.report.write_text(json.dumps(data,indent=2)+'\n')
    print('HTCLEO_GSAPP_PLUGIN_OBJECTS_OK objects=15 changed=GSPluginLoader.o exports=123+4C1constructors data=0 bss=0')

if __name__=='__main__': main()
