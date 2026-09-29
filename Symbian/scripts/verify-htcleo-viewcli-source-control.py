#!/usr/bin/env python3
"""833: unmodified VWS client source control; frozen ABI, attributed parent code."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import struct
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
ROOT=SDK/'sf/mw/appsupport/appfw/viewserver'
EVID=HERE.parent/'output/iteration-evidence/833-vws-client-queue'
STOCK=EVID/'viewcli-stock-832.dll'
STOCK_SHA='15accd51bf36e6d6d1667bff4b3ed9319c68465156433b1fa24e2b6ff23b8fd2'
PARENT=HERE.parent/'output/832-symbian3-full-home-view-event-incremental/Symbian3'
PARENT_SHA='7dc370a3e2303585d2e1a8851c19d8123bc237ad07d09913a3510dafc1a0d6fa'
BINARY=SDK/'epoc32/release/armv5/urel/viewcli.dll'
DUMP='viewcli-source-control-833-full-dump.txt'
INPUTS={'client/VIEWCLI.CPP':'b93f4bf51233616fd55731becf3b6b53c952bf333860a4b9ff69d3f72c082b6f',
 'group/VIEWCLI.MMP':'a9fc49e56f94f538bf2beed0191861e7128a0ce27d4f5756eaf59b4e805b9fae',
 'eabi/VIEWCLIU.DEF':'58cbea976aa97b31b3e634e9e575768c0e1dc957d8baf70b728675b941dbb051'}
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():
    paths=list((SDK/'epoc32/build/viewcli-build').glob('*/viewcli_dll/armv5/urel/*.o'))
    if len(paths)!=1 or paths[0].name!='VIEWCLI.o':raise ValueError('ambiguous ViewCLI object inventory')
    return {str(p):sha(p) for p in paths}
def sources():
    paths=[ROOT/k for k in INPUTS]+list((ROOT/'inc').iterdir())
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if p.is_file()}
def check_sources():
    for name,expected in INPUTS.items():
        if sha(ROOT/name)!=expected:raise ValueError('Unmodified source-control input changed '+name)
def header(text):
    result={}
    for key in ('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size',
                'Max Heap Size','Stack Size','Code link addr','Data link addr','Data Size'):
        m=re.search(r'^'+re.escape(key)+r':\s*([^\n]+)',text,re.M)
        if not m:raise ValueError('missing ABI field '+key)
        result[key]=' '.join(m[1].split())
    for term in ('Entry points are not called','EPOC Dll for ARMV5 CPU','SMP Safe : True',
                 'Image FPU support : Soft VFP','Debuggable : False','Number of exports = 45'):
        if term not in text:raise ValueError('ViewCLI platform/export contract drift '+term)
    if result['Flags']!='1200402b' or result['Data Size']!='00000000':
        raise ValueError('ViewCLI flags/data changed')
    if not re.search(r'^Bss\s+000000\s*$',text,re.M):raise ValueError('ViewCLI new DLL BSS')
    if not re.search(r'^Uids:\s+10000079 1000008d 10003f33 ',text,re.M):raise ValueError('ViewCLI UID drift')
    return result
def exports(text):
    text='\n'.join(line.split(';',1)[0].strip() for line in text.splitlines())
    rows=re.findall(r'^\s*(\S+)\s+@\s+(\d+)\s+NONAME\s*$',text,re.M)
    if [int(o) for _,o in rows]!=list(range(1,46)):raise ValueError('ViewCLI must have exact ARM ordinals1..45')
    return rows
def unpack_e32(path):
    with tempfile.TemporaryDirectory(prefix='htcleo-viewcli-parent-') as d:
        target=Path(d)/'stock.e32';shutil.copyfile(path,target)
        if struct.unpack_from('<I',target.read_bytes(),28)[0]:
            subprocess.run([str(SDK/'epoc32/tools/petran'),'-nocompress',str(target)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
        return target.read_bytes()
def code_relocations(raw):
    word=lambda off:struct.unpack_from('<I',raw,off)[0]
    base=word(112);size,count=word(base),word(base+4)
    pos=base+8;end=pos+size;out={}
    if end>len(raw):raise ValueError('truncated code reloc section')
    while pos<end:
        page,block=struct.unpack_from('<II',raw,pos)
        if block<8 or block%4 or pos+block>end:raise ValueError('invalid code relocation block')
        for at in range(pos+8,pos+block,2):
            r,=struct.unpack_from('<H',raw,at)
            if not r:continue
            offset=page+(r&0xfff)
            if offset in out or offset&3 or r>>12 not in (1,2,3):raise ValueError('invalid relocation')
            out[offset]=r>>12
        pos+=block
    if len(out)!=count:raise ValueError('relocation count mismatch')
    return out
def verify_parent_member():
    if sha(STOCK)!=STOCK_SHA or sha(PARENT/'initrd.gz')!=PARENT_SHA:
        raise ValueError('Stock/parent tuple drift')
    recipe=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text()
    if len(re.findall(r'^file='+re.escape(str(BINARY))+r'\s+"sys\\bin\\viewcli.dll"\s*$',recipe,re.M|re.I))!=1:
        raise ValueError('ViewCLI original recipe mapping drift')
    rom=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
    old=(PARENT/'initrd.gz').read_bytes()
    files=rom['ROM']['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    start,end,code,size=rom['rom_code_span'](old,files,'sys\\bin\\viewcli.dll')
    raw=unpack_e32(STOCK)
    word=lambda off:struct.unpack_from('<I',raw,off)[0]
    code_size,code_offset,link=word(48),word(100),word(76)
    if size!=code_size or link!=0x8000 or word(52) or word(68):raise ValueError('Stock code/data contract')
    expected=bytearray(raw[code_offset:code_offset+code_size])
    sites,imports,_=rom['parse_e32_import_sites'](raw)
    relocations=code_relocations(raw)
    for site,kind in relocations.items():
        if site+4>code_size:raise ValueError('relocation outside code')
        if site+120 in sites:continue
        before=struct.unpack_from('<I',expected,site)[0]
        if kind==2 or not link<=(before&~1)<link+code_size:raise ValueError('unexpected non-code relocation '+hex(site))
        struct.pack_into('<I',expected,site,before+code-link)
    for site,(module,ordinal,addend) in sites.items():
        table,_,_=rom['rom_export_table'](old,files,'sys\\bin\\'+module+'.dll')
        if not 1<=ordinal<=len(table):raise ValueError('unresolved original import')
        struct.pack_into('<I',expected,site-120,table[ordinal-1]+addend)
    actual=old[start+120:end]
    if bytes(expected)!=actual:
        bad=[i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
        raise ValueError('parent ROM differs outside exact source relocations '+repr(bad[:12]))
    return dict(stock_sha256=STOCK_SHA,parent_sha256=PARENT_SHA,code_size=code_size,
                original_code_relocations=len(relocations),original_import_sites=len(sites),
                policy='whole-stock-code-exact-after-declared-relocations-and-ordinal-resolution-no-mask')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true');p.add_argument('--parent-proof',action='store_true')
    p.add_argument('--native',type=Path,default=HERE.parent/'output/qsd8250-native-full-rom')
    p.add_argument('--report',type=Path);a=p.parse_args()
    check_sources()
    proof=verify_parent_member()
    if a.parent_proof:
        print(json.dumps(proof));return
    base=EVID/'CONTROL-OBJECTS.json'
    before=(a.native/'viewcli-stock-832-full-dump.txt').read_text()
    after=(EVID/'viewcli-control-full-dump.txt').read_text() if a.snapshot else (a.native/DUMP).read_text()
    if header(before)!=header(after):raise ValueError('Unmodified control ABI differs from original')
    defs=list((SDK/'epoc32/build/viewcli-build').glob('*/viewcli_dll/armv5/urel/viewcli{000a0000}.def'))
    original=exports((ROOT/'eabi/VIEWCLIU.DEF').read_text())
    if len(defs)!=1 or exports(defs[0].read_text())!=original:raise ValueError('ARM frozen export identities changed')
    dso=SDK/'epoc32/release/armv5/lib/viewcli{000a0000}.dso'
    if b'viewcli{000a0000}[10003f33].dll\0' not in dso.read_bytes():raise ValueError('ViewCLI DSO link identity drift')
    if a.snapshot:
        if base.exists():raise ValueError('Never overwrite source control evidence')
        result=dict(stock_sha256=STOCK_SHA,binary_sha256=sha(BINARY),objects=objects(),sources=sources(),
                    header=header(after),exports=original,imports=GS['imports'](after),parent_proof=proof)
        base.write_text(json.dumps(result,indent=2)+'\n')
        shutil.copyfile(BINARY,EVID/'viewcli-source-control.dll')
        print('VIEWCLI_SOURCE_CONTROL_SNAPSHOT_OK exports45 noentry data0 bss0');return
    control=json.loads(base.read_text())
    if control['objects']!=objects() or control['sources']!=sources():raise ValueError('control object/source drift')
    current_imports=GS['imports'](after)
    normalized=lambda table:{name:sorted(tuple(row) for row in values) for name,values in table.items()}
    if normalized(current_imports)!=normalized(control['imports']):raise ValueError('control import drift')
    if sha(BINARY)==STOCK_SHA:raise ValueError('ViewCLI control not relinked')
    result=dict(status='HTCLEO_VIEWCLI_SOURCE_CONTROL_OBJECTS_OK',binary_sha256=sha(BINARY),stock_sha256=STOCK_SHA,
       control_receipt_sha256=sha(base),control_object_sha256=next(iter(objects().values())),objects=objects(),
       sources=sources(),header=header(after),export_contract='exact45-ARM-symbol-ordinal-pairs',
       import_contract='exact-unmodified-GCCE-control',imports=current_imports,
       parent_proof=proof,policy='unmodified-native-ViewCLI-source-GCCE-control-no-new-log-or-behavior-patch')
    if not a.report:raise ValueError('--report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_VIEWCLI_SOURCE_CONTROL_OBJECTS_OK one-source-object exports45 ABI/source unchanged from control')
if __name__=='__main__':main()
