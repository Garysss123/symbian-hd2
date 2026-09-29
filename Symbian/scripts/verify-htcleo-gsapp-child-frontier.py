#!/usr/bin/env python3
"""827 exact GSPluginLoader observation delta, not plugin-load policy change."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-gsapp-child-frontier.py'))
PL=runpy.run_path(str(HERE/'verify-htcleo-gsapp-plugin-frontier.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
BINARY=SDK/'epoc32/release/armv5/urel/gsframework.dll'
PARENT=HERE.parent/'output/826-symbian3-full-gsapp-ecom-create-retry-incremental/Symbian3'
DUMP='gsframework-child-827-full-dump.txt'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return PL['objects']()
def sources():
    paths=list((SDK/P['REL']/'src').glob('*.cpp'))
    if len(paths)!=16:raise ValueError('GSFramework source-set drift')
    return {p.name:sha(p) for p in paths}
def verify_imports(before,after):
    if {k:sorted(v) for k,v in before.items()}!={k:sorted(v) for k,v in after.items()}:
        raise ValueError('Child witness import drift')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    parent_dump=(PARENT/'build/gsframework-notify-825-full-dump.txt').read_text()
    prior=json.loads((PARENT/'build/GSAPP-NOTIFY-OBJECTS.json').read_text())
    source=SDK/P['REL']/P['NAME']
    header=SDK/'sf/mw/gsprofilesrv/gsprofilesrv_plat/settings_framework_api/inc/GSPluginLoader.h'
    helper=source.parent/'htcleogsplugintrace.inl'
    asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsplugintrace.inl'
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Immutable child baseline exists')
        if sha(BINARY)!=P['BASE_BINARY'] or sha(source)!=P['BASE_SOURCE']:
            raise ValueError('Not exact826 GSFramework')
        if prior['binary_sha256']!=sha(BINARY) or prior['objects']!=objects() or prior['sources']!=sources():
            raise ValueError('GSFramework parent objects/source do not match retained certificate')
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        # Keep actual objects too: a hash alone cannot recover/debug compiler metadata drift.
        object_copy=a.baseline.parent/'parent-objects';object_copy.mkdir(exist_ok=True)
        for path in (SDK/'epoc32/build/gsframework-build').glob('*/*/armv5/urel/*.o'):
            target=object_copy/path.name
            if target.exists():
                if sha(target)!=sha(path):raise ValueError('Existing control object mismatch')
            else:target.write_bytes(path.read_bytes())
        data=dict(base_binary_sha256=sha(BINARY),objects=objects(),sources=sources(),
                  class_header_sha256=sha(header),helper_sha256=sha(helper))
        a.baseline.write_text(json.dumps(data,indent=2)+'\n')
        print('GSCHILD_BASE_OK objects=15 exact-parent-certificate');return
    base=json.loads(a.baseline.read_text());now=objects()
    changed=sorted(k for k in now if now[k]!=base['objects'][k])
    if changed!=['GSPluginLoader.o']:raise ValueError('Unexpected child objects '+repr(changed))
    current=sources()
    if sorted(k for k in current if current[k]!=base['sources'][k])!=['GSPluginLoader.cpp']:
        raise ValueError('Unexpected child source delta')
    if P['transform'](source.read_text(encoding='latin-1'))!=source.read_text(encoding='latin-1'):
        raise ValueError('Missing exact child witness')
    if sha(header)!=base['class_header_sha256'] or sha(helper)!=base['helper_sha256'] or sha(helper)!=sha(asset):
        raise ValueError('Class layout/shared logger changed')
    dump=(a.native/DUMP).read_text()
    if PL['header'](dump)!=PL['header'](parent_dump):raise ValueError('GSFramework ABI/security drift')
    verify_imports(GS['imports'](parent_dump),GS['imports'](dump))
    exports=PL['verify_exports'](dump)
    obj=next((SDK/'epoc32/build/gsframework-build').glob('*/*/armv5/urel/GSPluginLoader.o'))
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',str(obj)],text=True)
    if 'HtcleoGsPluginLog' not in disasm:raise ValueError('Logger missing')
    for forbidden in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After('):
        if forbidden in disasm:raise ValueError('Unexpected blocking/IO delta '+forbidden)
    data=dict(status='HTCLEO_GSAPP_CHILD_OBJECTS_OK',binary_sha256=sha(BINARY),
              base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),
              changed_objects=changed,objects=now,sources=current,helper_sha256=sha(helper),
              class_header_sha256=sha(header),export_def_sha256=exports,header=PL['header'](dump),
              import_policy='identical826',policy='GS-root-and-General-first2-C734-parent-no-loading-policy-change')
    if not a.report:raise ValueError('Report required')
    a.report.write_text(json.dumps(data,indent=2)+'\n')
    print('HTCLEO_GSAPP_CHILD_OBJECTS_OK objects=15 changed=GSPluginLoader.o exports=127 data=0 bss=0 imports=identical')
if __name__=='__main__':main()
