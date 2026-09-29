#!/usr/bin/env python3
"""837: one ViewServer event object, frozen ABI and exact diagnostic import delta."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
HERE=Path(__file__).resolve().parent
P=runpy.run_path(str(HERE/'apply-htcleo-vws-server-event.py'))
CONTROL=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))
SDK=CONTROL['SDK'];ROOT=SDK/P['REL'];BINARY=CONTROL['BINARY'];GS=CONTROL['GS']
PARENT=HERE.parent/'output/836-symbian3-full-viewsrv-source-control-incremental/Symbian3'
DUMP='viewsrv-event-837-full-dump.txt'
ADDED={'euser':[(2103,0),(723,0),(737,0),(1472,0),(760,0),(1849,0),(758,0),(1032,0)],
       'drtaeabi':[(222,0),(135,0)],'efsrv':[(97,0),(300,0),(93,0),(105,0),(263,0)]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():return CONTROL['objects']()
def source_digests():return CONTROL['sources']()
def check_sources():
    src=(ROOT/P['NAME']).read_text(encoding='latin-1')
    if P['transform'](src)!=src:raise ValueError('Server event source drift')
def verify_imports(before,after):
    expected={n:Counter(tuple(x) for x in v) for n,v in before.items()}
    for name,rows in ADDED.items():expected.setdefault(name,Counter()).update(rows)
    if expected!={n:Counter(tuple(x) for x in v) for n,v in after.items()}:
        raise ValueError('Server event imports differ beyond exact logger delta')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true')
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--report',type=Path);a=p.parse_args()
    prior=json.loads((PARENT/'build/VIEWSRV-SOURCE-CONTROL-OBJECTS.json').read_text())
    if a.snapshot:
        if a.baseline.exists():raise ValueError('Never overwrite837 baseline')
        if sha(BINARY)!=P['BASE_BINARY'] or prior['objects']!=objects():raise ValueError('not exact836 ViewServer')
        CONTROL['check_sources']()
        a.baseline.parent.mkdir(parents=True,exist_ok=True)
        target=Path(next(n for n in objects() if Path(n).name=='VWSEVENT.o'))
        (a.baseline.parent/'parent-VWSEVENT.o').write_bytes(target.read_bytes())
        a.baseline.write_text(json.dumps(dict(binary_sha256=sha(BINARY),objects=objects(),sources=source_digests()),indent=2)+'\n')
        print('VWSEVENT837_BASE_OK nine-objects-exact836');return
    base=json.loads(a.baseline.read_text());now=objects();sources=source_digests()
    if set(now)!=set(base['objects']):raise ValueError('server object set drift')
    changed=[n for n in now if now[n]!=base['objects'][n]]
    if len(changed)!=1 or Path(changed[0]).name!='VWSEVENT.o':raise ValueError('unexpected server object delta')
    if set(sources)!=set(base['sources']) or [n for n in sources if sources[n]!=base['sources'][n]]!=[P['NAME']]:
        raise ValueError('unexpected server source/header/MMP delta')
    check_sources()
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleovwsservereventtrace.inl'
    if (ROOT/'server'/helper.name).read_bytes()!=helper.read_bytes():raise ValueError('compiled server logger drift')
    before=(PARENT/'build/viewsrv-source-control-836-full-dump.txt').read_text();after=(a.native/DUMP).read_text()
    if CONTROL['header'](before)!=CONTROL['header'](after):raise ValueError('ViewServer ABI/security/data changed')
    verify_imports(GS['imports'](before),GS['imports'](after))
    defs=list((SDK/'epoc32/build/viewsrv-build').glob('*/viewsrv_dll/armv5/urel/viewsrv{000a0000}.def'))
    if len(defs)!=1 or CONTROL['exports'](defs[0].read_text())!=CONTROL['exports']((PARENT/'build/viewsrv-stock-exports.def').read_text()):
        raise ValueError('ViewServer48 frozen export drift')
    constants=CONTROL['exported_constants'](BINARY)
    if constants!=prior['patchable_constants']:raise ValueError('ViewServer timeout/boost constant changed')
    disasm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',changed[0]],text=True)
    if 'HtcleoVwsServerLog' not in disasm:raise ValueError('server logger absent')
    for bad in ('RFile::Flush(', 'RFile::Replace(', 'User::After('):
        if bad in disasm:raise ValueError('unexpected blocking server logger API '+bad)
    result=dict(status='HTCLEO_VWS_SERVER_EVENT_OBJECTS_OK',binary_sha256=sha(BINARY),base_binary_sha256=P['BASE_BINARY'],
        baseline_sha256=sha(a.baseline),objects=now,sources=sources,changed_objects=changed,helper_sha256=sha(helper),
        header=CONTROL['header'](after),export_contract='exact48-ARM-symbol-ordinal-DATA4',patchable_constants=constants,
        import_additions=ADDED,import_contract='diagnostic-only-exact-additions',
        policy='Home-GS-Matrix-activation-ack-timeout-complete32-no-state-policy-change')
    if not a.report:raise ValueError('--report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_VWS_SERVER_EVENT_OBJECTS_OK one-of-nine objects exports48 data0 bss0 timeout-constants unchanged')
if __name__=='__main__':main()
