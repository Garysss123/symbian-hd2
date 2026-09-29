#!/usr/bin/env python3
"""825 exact one-object/source delta, preserved imports/exports and source ABI."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-ecom-notify-guard.py'))
PL=runpy.run_path(str(HERE/'verify-htcleo-gsapp-plugin-frontier.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/gsframework.dll'
PARENT=HERE.parent/'output/824-symbian3-full-gsapp-exception-witness-incremental/Symbian3'
DUMP='gsframework-notify-825-full-dump.txt'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return PL['objects']()
def sources():
    root=SDK/P['REL']
    paths=list((root/'src').glob('*.cpp'))
    if len(paths)!=16:raise ValueError('GSFramework source set drift')
    return {p.name:sha(p) for p in paths}
def verify_imports(old,new):
    if {k:sorted(v) for k,v in old.items()}!={k:sorted(v) for k,v in new.items()}:
        raise ValueError('Notify guard imports differ from exact824')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    parent_dump=(PARENT/'build/gsframework-plugin-821-full-dump.txt').read_text()
    source=SDK/P['REL']/P['NAME']
    header=SDK/P['REL']/'inc/GSEComNotifier.h'
    helper=source.parent/'htcleogsplugintrace.inl'
    asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsplugintrace.inl'
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Immutable baseline exists')
        if sha(BINARY)!=P['BASE_BINARY'] or sha(source)!=P['BASE_SOURCE']:
            raise ValueError('Baseline differs from824')
        data=dict(base_binary_sha256=sha(BINARY),objects=objects(),sources=sources(),
                  class_header_sha256=sha(header),helper_sha256=sha(helper))
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        a.baseline.write_text(json.dumps(data,indent=2)+'\n')
        print('GSNOTIFY_BASE_OK objects=15');return
    base=json.loads(a.baseline.read_text())
    if base['base_binary_sha256']!=P['BASE_BINARY']:raise ValueError('Baseline receipt drift')
    now=objects();changed=sorted(n for n in now if now[n]!=base['objects'][n])
    if changed!=['GSEComNotifier.o']:raise ValueError('Unexpected objects '+repr(changed))
    now_sources=sources();changed_sources=sorted(n for n in now_sources if now_sources[n]!=base['sources'][n])
    if changed_sources!=['GSEComNotifier.cpp']:raise ValueError('Unexpected source delta')
    text=source.read_text(encoding='latin-1')
    if P['transform'](text)!=text:raise ValueError('Missing exact guard')
    if sha(header)!=base['class_header_sha256'] or sha(helper)!=base['helper_sha256'] or sha(helper)!=sha(asset):
        raise ValueError('Class layout/shared logger changed')
    dump=(a.native/DUMP).read_text()
    if PL['header'](dump)!=PL['header'](parent_dump):raise ValueError('ABI/security/data/BSS drift')
    verify_imports(GS['imports'](parent_dump),GS['imports'](dump))
    exports=PL['verify_exports'](dump)
    paths=list((SDK/'epoc32/build/gsframework-build').glob('*/*/armv5/urel/GSEComNotifier.o'))
    if len(paths)!=1:raise ValueError('Notifier object ambiguous')
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',str(paths[0])],text=True)
    if 'HtcleoGsPluginLog' not in disasm or 'CGSEComNotifier::PluginCountDeltaL()' not in disasm:
        raise ValueError('Guard/native path missing')
    for bad in ('RFile::Flush(', 'RFile::Replace(', 'User::After(', 'User::RequestComplete(', 'RTimer::'):
        if bad in disasm:raise ValueError('Unexpected new control/I/O '+bad)
    data=dict(status='HTCLEO_GSAPP_NOTIFY_OBJECTS_OK',binary_sha256=sha(BINARY),
              base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),
              changed_objects=changed,objects=now,changed_sources=changed_sources,sources=now_sources,
              class_header_sha256=sha(header),helper_sha256=sha(helper),export_def_sha256=exports,
              header=PL['header'](dump),import_policy='identical824',original_exports=123,
              compiler_C1_constructors=PL['CONSTRUCTORS'],
              policy='GS-negative-notify-retire-C730-no-list-no-rearm-success-native')
    if not a.report:raise ValueError('Report required')
    a.report.write_text(json.dumps(data,indent=2)+'\n')
    print('HTCLEO_GSAPP_NOTIFY_OBJECTS_OK objects=15 changed=GSEComNotifier.o exports=127 data=0 bss=0 imports=identical')
if __name__=='__main__':main()

