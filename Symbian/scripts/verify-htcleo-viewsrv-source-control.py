#!/usr/bin/env python3
"""836: unmodified VWS server source control; frozen ABI, attributed parent code."""
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
EVID=HERE.parent/'output/iteration-evidence/836-viewsrv-source-control'
STOCK=EVID/'viewsrv-stock-835.dll'
STOCK_SHA='fe031c4e1ab4d2d44c16871af7ca56145d664fcee74937a36b8437013d8fcab9'
PARENT=HERE.parent/'output/835-symbian3-full-vws-client-state-incremental/Symbian3'
PARENT_SHA='422dbcdc11bbdc6c06dab75819e9957f7c0584a5420ddf0831b84b91fb793557'
BINARY=SDK/'epoc32/release/armv5/urel/viewsrv.dll'
DUMP='viewsrv-source-control-836-full-dump.txt'
INPUTS={
  "server/VWSMAIN.CPP": "35788ba39131f3772901835dbc719bcf44188b0dc161f32017f1e945ff0c86d3",
  "server/VWSERVER.CPP": "deb8d99f105bdd84d97368676e8e0577905dda2a6c4344c44cf7d54d1e4f186a",
  "server/VWSSESSN.CPP": "ee20d005264ed483ba96ccbc8931c1ece6b82f804ebb2eeed91e9b4d3cbfc62c",
  "server/VWSQUEUE.CPP": "7e28099f638ca505b0d25b288307970541efa3b34ca0b5422192b697af629c9e",
  "server/VWSEVENT.CPP": "14a07b3d7375b7878ae621ec640ae7d2676f6ebae9f7134cc43b41e11bd71204",
  "server/VWSSEVNT.CPP": "16e5f0575114778a468053dd29a50ec899a12cd8b32aa7fb1d3de1ec754eb5ee",
  "server/VWSWEVNT.CPP": "23d7593751dc28b8698d98b5f152555e5cd70dc90c4012eee63365cf966475e6",
  "server/VWSDEBUG.CPP": "d7c79cd434d2d45d76eaa6a785929ab35ca25b151bf292bdadf5d1a7c96c2b0a",
  "server/vwspatchdata.cpp": "8b7b27a90ace2abbae16b01407be5b07c9f4da6f4239e77da1b6e84f47f2b242",
  "group/VIEWSRV.MMP": "cacac3330540d3a74172e7fbf653bc56b6dae30e91e98e4de0edd1f84b13dae6",
  "eabi/VIEWSRVU.DEF": "600b25cbb57601717177ad7a121f56ee5851ea2bf36b1bb53bdabab902222bd9"
}
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objects():
    paths=list((SDK/'epoc32/build/viewsrv-build').glob('*/viewsrv_dll/armv5/urel/*.o'))
    expected={'VWSMAIN.o','VWSERVER.o','VWSSESSN.o','VWSQUEUE.o','VWSEVENT.o','VWSSEVNT.o','VWSWEVNT.o','VWSDEBUG.o','vwspatchdata.o'}
    if len(paths)!=9 or {p.name for p in paths}!=expected:raise ValueError('ambiguous ViewSrv object inventory')
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
                 'Image FPU support : Soft VFP','Debuggable : False','Number of exports = 48'):
        if term not in text:raise ValueError('ViewSrv platform/export contract drift '+term)
    if result['Flags']!='1200402b' or result['Data Size']!='00000000':
        raise ValueError('ViewSrv flags/data changed')
    if not re.search(r'^Bss\s+000000\s*$',text,re.M):raise ValueError('ViewSrv new DLL BSS')
    if not re.search(r'^Uids:\s+10000079 1000008d 10003f3c ',text,re.M):raise ValueError('ViewSrv UID drift')
    return result
def exports(text):
    text='\n'.join(line.split(';',1)[0].strip() for line in text.splitlines())
    rows=re.findall(r'^\s*(\S+)\s+@\s+(\d+)\s+NONAME(?:\s+DATA\s+(\d+))?\s*$',text,re.M)
    if [int(row[1]) for row in rows]!=list(range(1,49)):raise ValueError('ViewSrv must have exact ARM ordinals1..48')
    if [(int(row[1]),row[2]) for row in rows if row[2]]!=[(47,'4'),(48,'4')]:raise ValueError('ViewSrv patchable DATA export contract changed')
    return rows

def exported_constants(path):
    raw=unpack_e32(path)
    word=lambda off:struct.unpack_from('<I',raw,off)[0]
    code_size,link,offset,table,count=word(48),word(76),word(100),word(88),word(92)
    if count!=48:raise ValueError('ViewSrv data export count')
    result={}
    for ordinal in (47,48):
        address=word(table+(ordinal-1)*4)
        if not link<=address<=link+code_size-4:raise ValueError('ViewSrv constant outside RO code')
        result[str(ordinal)]=word(offset+address-link)
    return result
def unpack_e32(path):
    with tempfile.TemporaryDirectory(prefix='htcleo-viewsrv-parent-') as d:
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
    if len(re.findall(r'^file='+re.escape(str(BINARY))+r'\s+"sys\\bin\\viewsrv.dll"\s*$',recipe,re.M|re.I))!=1:
        raise ValueError('ViewSrv original recipe mapping drift')
    rom=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
    old=(PARENT/'initrd.gz').read_bytes()
    files=rom['ROM']['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    start,end,code,size=rom['rom_code_span'](old,files,'sys\\bin\\viewsrv.dll')
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
def verify_viewcli_rom_binding(old,new,files0,files1):
    """Reconstruct the unchanged835 client in both ROMs, including the changed server import."""
    source=SDK/'epoc32/release/armv5/urel/viewcli.dll'
    if sha(source)!='1330252e5e0919bdc025703e1cfaa619713ee4c70775bc71cf2336116c1516ce':
        raise ValueError('835 ViewCLI source binary changed')
    rom=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
    raw=unpack_e32(source);word=lambda off:struct.unpack_from('<I',raw,off)[0]
    code_size,code_offset,link=word(48),word(100),word(76)
    sites,_,_=rom['parse_e32_import_sites'](raw);relocs=code_relocations(raw)
    if word(52) or word(68):raise ValueError('unexpected client data/BSS')
    server_imports=[]
    for image,files in ((old,files0),(new,files1)):
        start,end,base,size=rom['rom_code_span'](image,files,'sys\\bin\\viewcli.dll')
        if size!=code_size:raise ValueError('ViewCLI code size changed in ROM')
        expected=bytearray(raw[code_offset:code_offset+code_size])
        for site,kind in relocs.items():
            if site+120 in sites:continue
            val=struct.unpack_from('<I',expected,site)[0]
            if kind==2 or not link<=(val&~1)<link+code_size:raise ValueError('unexpected client relocation')
            struct.pack_into('<I',expected,site,val+base-link)
        resolved=[]
        for site,(module,ordinal,addend) in sites.items():
            exports,_,_=rom['rom_export_table'](image,files,'sys\\bin\\'+module+'.dll')
            if not 1<=ordinal<=len(exports):raise ValueError('unresolved client import')
            value=exports[ordinal-1]+addend
            struct.pack_into('<I',expected,site-120,value)
            if module=='viewsrv':resolved.append(dict(ordinal=ordinal,addend=addend,target=value))
        if bytes(expected)!=image[start+120:end]:raise ValueError('ViewCLI ROM code differs beyond declared relocations')
        if len(resolved)!=1 or resolved[0]['ordinal']!=1 or resolved[0]['addend']!=0:
            raise ValueError('Unexpected ViewCLI-to-ViewServer import contract')
        server_imports.append(resolved[0])
    return dict(consumer_sha256=sha(source),code_bytes=code_size,server_imports=server_imports,
                policy='whole-unchanged-client-code-exact-with-declared-relocations-and-server-ordinal1')

def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true');p.add_argument('--parent-proof',action='store_true')
    p.add_argument('--native',type=Path,default=HERE.parent/'output/qsd8250-native-full-rom')
    p.add_argument('--report',type=Path);a=p.parse_args()
    check_sources()
    proof=verify_parent_member()
    if a.parent_proof:
        print(json.dumps(proof));return
    base=EVID/'CONTROL-OBJECTS.json'
    before=(a.native/'viewsrv-stock-835-full-dump.txt').read_text()
    after=(EVID/'viewsrv-control-full-dump.txt').read_text() if a.snapshot else (a.native/DUMP).read_text()
    if header(before)!=header(after):raise ValueError('Unmodified control ABI differs from original')
    defs=list((SDK/'epoc32/build/viewsrv-build').glob('*/viewsrv_dll/armv5/urel/viewsrv{000a0000}.def'))
    original=exports((ROOT/'eabi/VIEWSRVU.DEF').read_text())
    if len(defs)!=1 or exports(defs[0].read_text())!=original:raise ValueError('ARM frozen export identities changed')
    constants=exported_constants(BINARY)
    if constants!=exported_constants(STOCK):raise ValueError('ViewSrv boost/timeout DATA values changed')
    dso=SDK/'epoc32/release/armv5/lib/viewsrv{000a0000}.dso'
    if b'viewsrv{000a0000}[10003f3c].dll\0' not in dso.read_bytes():raise ValueError('ViewSrv DSO link identity drift')
    if a.snapshot:
        if base.exists():raise ValueError('Never overwrite source control evidence')
        result=dict(stock_sha256=STOCK_SHA,binary_sha256=sha(BINARY),objects=objects(),sources=sources(),
                    header=header(after),exports=original,imports=GS['imports'](after),parent_proof=proof,patchable_constants=constants)
        base.write_text(json.dumps(result,indent=2)+'\n')
        shutil.copyfile(BINARY,EVID/'viewsrv-source-control.dll')
        print('VIEWSRV_SOURCE_CONTROL_SNAPSHOT_OK exports48 noentry data0 bss0');return
    control=json.loads(base.read_text())
    if control['objects']!=objects() or control['sources']!=sources():raise ValueError('control object/source drift')
    current_imports=GS['imports'](after)
    normalized=lambda table:{name:sorted(tuple(row) for row in values) for name,values in table.items()}
    if normalized(current_imports)!=normalized(control['imports']):raise ValueError('control import drift')
    if sha(BINARY)==STOCK_SHA:raise ValueError('ViewSrv control not relinked')
    result=dict(status='HTCLEO_VIEWSRV_SOURCE_CONTROL_OBJECTS_OK',binary_sha256=sha(BINARY),stock_sha256=STOCK_SHA,
       control_receipt_sha256=sha(base),objects=objects(),
       sources=sources(),header=header(after),export_contract='exact48-ARM-symbol-ordinal-pairs',
       import_contract='exact-unmodified-GCCE-control',imports=current_imports,
       parent_proof=proof,patchable_constants=constants,policy='unmodified-native-ViewServer-source-GCCE-control-no-new-log-or-timeout-change')
    if not a.report:raise ValueError('--report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print('HTCLEO_VIEWSRV_SOURCE_CONTROL_OBJECTS_OK nine-source-objects exports48 ABI/source unchanged from control')
if __name__=='__main__':main()
