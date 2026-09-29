#!/usr/bin/env python3
"""835: one ViewCLI object, wrapper result/state observation on834."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
P=runpy.run_path(str(HERE/'apply-htcleo-vws-client-state.py'))
CONTROL=runpy.run_path(str(HERE/'verify-htcleo-viewcli-source-control.py'))
SDK=CONTROL['SDK'];ROOT=SDK/P['REL'];BINARY=CONTROL['BINARY']
PARENT=HERE.parent/'output/834-symbian3-full-vws-client-queue-incremental/Symbian3'
DUMP='viewcli-state-835-full-dump.txt'
GS=CONTROL['GS']
# No new imports are expected; snapshot uses inline CActive accessors.
ADDED={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return CONTROL['objects']()
def source_digests():return CONTROL['sources']()
def check_sources():
    for name,expected in P['BASE'].items():
        source=(ROOT/name).read_text(encoding='latin-1')
        if P['transform'](source,name)!=source:raise ValueError('VWS source overlay drift '+name)
        if hashlib.sha256(P['transform'](source,name,True).encode('latin-1')).hexdigest()!=expected:
            raise ValueError('VWS original source drift '+name)
def verify_imports(before,after):
    expected={n:Counter(tuple(x) for x in v) for n,v in before.items()}
    for name,values in ADDED.items():expected.setdefault(name,Counter()).update(values)
    actual={n:Counter(tuple(x) for x in v) for n,v in after.items()}
    if expected!=actual:raise ValueError('VWS imports differ from exact diagnostic additions')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True)
    p.add_argument('--report',type=Path);a=p.parse_args()
    prior=json.loads((PARENT/'build/VWS-CLIENT-QUEUE-OBJECTS.json').read_text())
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Never overwrite835 baseline')
        if sha(BINARY)!=P['BASE_BINARY'] or prior['objects']!=objects():raise ValueError('not exact834 ViewCLI')
        runpy.run_path(str(HERE/'verify-htcleo-vws-client-queue.py'))['check_sources']()
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        target=Path(next(iter(objects())))
        (a.baseline.parent/'parent-VIEWCLI.o').write_bytes(target.read_bytes())
        a.baseline.write_text(json.dumps(dict(binary_sha256=sha(BINARY),objects=objects(),sources=source_digests()),indent=2)+'\n')
        print('VWS835_BASE_OK one-object-exact834');return
    base=json.loads(a.baseline.read_text());now=objects();sources=source_digests()
    if set(now)!=set(base['objects']) or list(now.values())==list(base['objects'].values()):
        raise ValueError('Expected one changed ViewCLI object')
    changed_sources=sorted(n for n in sources if sources[n]!=base['sources'][n])
    if set(sources)!=set(base['sources']) or changed_sources!=sorted(P['BASE']):
        raise ValueError('VWS unexpected source/header changes '+repr(changed_sources))
    check_sources()
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleovwsclientstatetrace.inl'
    if (ROOT/'client'/helper.name).read_bytes()!=helper.read_bytes():raise ValueError('VWS compiled helper drift')
    before=(PARENT/'build/viewcli-queue-834-full-dump.txt').read_text()
    after=(a.native/DUMP).read_text()
    if CONTROL['header'](before)!=CONTROL['header'](after):raise ValueError('ViewCLI ABI changed')
    verify_imports(GS['imports'](before),GS['imports'](after))
    defs=list((SDK/'epoc32/build/viewcli-build').glob('*/viewcli_dll/armv5/urel/viewcli{000a0000}.def'))
    if len(defs)!=1 or CONTROL['exports'](defs[0].read_text())!=CONTROL['exports']((PARENT/'build/viewcli-stock-exports.def').read_text()):
        raise ValueError('ViewCLI45 frozen export drift')
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',next(iter(now))],text=True)
    if 'HtcleoVwsClientLog' not in disasm:raise ValueError('VWS diagnostic absent')
    for forbidden in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After('):
        if forbidden in disasm:raise ValueError('VWS new forbidden API '+forbidden)
    result=dict(status='HTCLEO_VWS_CLIENT_STATE_OBJECTS_OK',binary_sha256=sha(BINARY),
        base_binary_sha256=P['BASE_BINARY'],baseline_sha256=sha(a.baseline),
        objects=now,sources=sources,changed_objects=list(now),helper_sha256=sha(helper),
        header=CONTROL['header'](after),export_contract='exact45-ARM-symbol-ordinal-pairs',
        import_additions=ADDED,import_contract='diagnostic-only-exact-additions',
        policy='Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change')
    if not a.report:raise ValueError('--report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_VWS_CLIENT_STATE_OBJECTS_OK VIEWCLI.o exports45 data0 bss0 same-native-flow')
if __name__=='__main__':main()
