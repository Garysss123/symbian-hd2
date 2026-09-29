#!/usr/bin/env python3
"""898: FileManager ECom destroy/close boundaries; unchanged native cleanup and ABI."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import shutil
import struct
import subprocess

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-filemanager-ecom-destroy.py'))
X=runpy.run_path(str(HERE/'verify-htcleo-ecom-server-exception.py'))
E32,ROM,GS,FRONT=(X[k] for k in ('E32','ROM','GS','FRONT'))
PARENT=HERE.parent/'output/897-symbian3-full-filemanager-async-frontier-incremental/Symbian3'
PARENT_SHA='a08ffe7eede9802a453aefb16e974635e470beaee08f06d3de7ad85be835752e'
BASE_SHA='d41fbbbb966eb544e3cbbeaa63f8a509e7824f728e9fc7ec217052228e41ae45'
BINARY=SDK/'epoc32/release/armv5/urel/ecom.dll'
OBJ=SDK/'epoc32/build/ecom-client-build/c_31e9d313475cf635/ecom_dll/armv5/urel'
EVID=HERE.parent/'output/iteration-evidence/898-filemanager-idle-frontier'
DUMP='ecom-destroy-898-full-dump.txt'
# Reuse only parent ECom imports; no new imports are allowed.
ADDED_IMPORTS={}
ABS=runpy.run_path(str(HERE/'verify-htcleo-avkon-common-geometry.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def state():
    objs={str(p):sha(p) for p in sorted(OBJ.glob('*.o'))}
    if len(objs)!=7:raise ValueError('ECom object inventory')
    inputs=set()
    for p in OBJ.glob('*.o.d'):
        inputs.update(Path(s) for s in re.findall(r'/[^\s\\]+\.(?:cpp|h|hrh|mmh|inl)\b',p.read_text(),re.I) if Path(s).is_file())
    inputs.update((SDK/P['REL'].parent/'MMPFiles/ECom.mmp',
                   HERE.parent/'hd2/qsd8250-native-bsp/ecom-client-build/bld.inf'))
    return dict(objects=objs,inputs={str(p):sha(p) for p in sorted(inputs)},binary_sha256=sha(BINARY))

def dump():
    return subprocess.check_output([str(SDK/'epoc32/tools/elf2e32'),
        '--dump=hseit','--e32input='+str(BINARY)],text=True)

def snapshot():
    if (EVID/'BASE.json').exists():raise ValueError('Never overwrite898 base')
    if sha(BINARY)!=BASE_SHA or sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('Not897 parent')
    for name in P['BASE']:
        text=(SDK/P['REL']/name).read_text(encoding='latin-1')
        if P['transform'](text,name,True)!=text:raise ValueError('snapshot requires897 source')
    now=state();prior=prior_control()
    if now['binary_sha256']!=prior['binary_sha256'] or {Path(k).name:v for k,v in now['objects'].items()}!=prior['objects']:
        raise ValueError('897 ECom object provenance drift')
    for name,digest in prior['sources'].items():
        if sha(SDK/P['REL']/name)!=digest:raise ValueError('897 ECom source provenance drift')
    if sha(SDK/P['REL'].parent/'MMPFiles/ECom.mmp')!=prior['mmp_sha256']:raise ValueError('ECom MMP provenance drift')
    EVID.mkdir(parents=True,exist_ok=True)
    shutil.copy2(BINARY,EVID/'ecom-parent897.dll')
    (EVID/'BASE.json').write_text(json.dumps(now,indent=2)+'\n')
    (EVID/'ecom-parent897-full-dump.txt').write_text(dump())
    shutil.copy2(OBJ/'ecom{000a0000}.def',EVID/'ecom-parent897-exports.def')
    print('FM_DESTROY_BASE=897 calibrated ECom7 objects/sources/inputs/frozen exports captured')

PRIOR_SHA='05cbd8a9762b7246610ace772ea08a79fa8eff8d6edda7e4162d9f64a3684682'
def prior_control():
    path=PARENT/'build/FONT-ECOM-OBJECTS.json'
    if sha(path)!=PRIOR_SHA:raise ValueError('ECom calibrated897 receipt drift')
    return json.loads(path.read_text())

def header(text):
    keys=('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size','Max Heap Size','Stack Size','Code link addr','Data link addr','Data Size')
    out={k:' '.join(re.search(r'^'+re.escape(k)+r':\s*([^\n]+)',text,re.M)[1].split()) for k in keys}
    out['BSS']=re.search(r'^Bss\s+(\S+)',text,re.M)[1]
    out['exports']=re.search(r'Number of exports = (\d+)',text)[1]
    out['UIDs']=' '.join(re.search(r'^Uids:\s*([^\n]+)',text,re.M)[1].split())
    for term in ('EPOC Dll for ARMV5 CPU','ARM EABI','Built against EKA2'):
        if term not in text:raise ValueError('DLL platform contract')
    return out

def relocations(raw,field):
    if not struct.unpack_from('<I',raw,field)[0]:return {}
    temporary=bytearray(raw)
    struct.pack_into('<I',temporary,112,struct.unpack_from('<I',raw,field)[0])
    return E32['code_relocations'](temporary)

def verify_objects(native):
    base=json.loads((EVID/'BASE.json').read_text());now=state()
    if (EVID/'STANDALONE.json').exists():
        approved=json.loads((EVID/'STANDALONE.json').read_text())
        if any(now[k]!=approved[k] for k in ('objects','inputs','binary_sha256')):
            raise ValueError('compiled candidate differs from reviewed standalone inputs/objects')
    if base['binary_sha256']!=BASE_SHA or sha(EVID/'ecom-parent897.dll')!=BASE_SHA:raise ValueError('baseline provenance')
    if set(now['objects'])!=set(base['objects']):raise ValueError('object set changed')
    changes=[p for p,v in now['objects'].items() if base['objects'][p]!=v]
    if [Path(p).name for p in changes]!=['EComSession.o']:raise ValueError('unexpected object changes '+repr(changes))
    expected={str(SDK/P['REL']/n) for n in P['BASE']}
    changed={p for p,v in base['inputs'].items() if now['inputs'].get(p)!=v}
    added=set(now['inputs'])-set(base['inputs'])
    helpers={P['HELPER']}
    if changed!=expected or added!={str(SDK/P['REL']/P['HELPER'])}:raise ValueError('unexpected source/header changes '+repr((changed,added)))
    for name in P['BASE']:
        text=(SDK/P['REL']/name).read_text(encoding='latin-1')
        if P['transform'](P['transform'](text,name,True),name)!=text:raise ValueError('source transform mismatch')
    helper_hashes={}
    for n in helpers:
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/n
        if (SDK/P['REL']/n).read_bytes()!=asset.read_bytes():raise ValueError('helper mismatch')
        helper_hashes[n]=sha(asset)
    for path in changes:
        asm=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',path],text=True)
        if 'HtcleoFmDestroy' not in asm:raise ValueError('destroy boundary observer absent')
        for bad in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After(', 'SetExceptionHandler', 'RunIfReady(', 'RequestComplete(', 'SetActive('):
            if bad in asm:raise ValueError('unexpected observer side effect '+bad)
    old=(EVID/'ecom-parent897-full-dump.txt').read_text();new=(native/DUMP).read_text()
    if header(old)!=header(new):raise ValueError('ABI/export count/data/BSS changed')
    a=GS['imports'](old);b=GS['imports'](new)
    delta={k:list((Counter(b.get(k,[]))-Counter(a.get(k,[]))).elements()) for k in set(a)|set(b)}
    delta={k:sorted(v) for k,v in delta.items() if v}
    for k in a:
        if Counter(a[k])-Counter(b.get(k,[])):raise ValueError('old imports removed '+k)
    if delta!=ADDED_IMPORTS:raise ValueError('unreviewed import delta '+repr(delta))
    raw=E32['unpack_e32'](BINARY)
    if struct.unpack_from('<I',raw,52)[0]!=0 or struct.unpack_from('<I',raw,68)[0]!=0:raise ValueError('ECom data/BSS drift')
    parent_raw=E32['unpack_e32'](EVID/'ecom-parent897.dll')
    if relocations(raw,116) or relocations(parent_raw,116):raise ValueError('unexpected ECom data relocation')
    if (OBJ/'ecom{000a0000}.def').read_bytes()!=(EVID/'ecom-parent897-exports.def').read_bytes():raise ValueError('39 export table changed')
    prior_control()
    return dict(status='HTCLEO_FILEMANAGER_DESTROY_OBJECTS_OK',**now,changed_objects=changes,header=header(new),imports_added=delta,helper_sha256=helper_hashes)

def verify_rom(a):
    proof=verify_objects(a.native)
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('897 ROM changed')
    if a.recipe.read_bytes()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_bytes():raise ValueError('Recipe change forbidden')
    cache=PARENT/'build/incremental-release-cache'
    rows=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows)!=67:raise ValueError('cache count')
    for row in rows:
        digest,path,name=row.split('\t')
        if sha(cache/name)!=digest or (path!=str(BINARY) and sha(Path(path))!=digest):raise ValueError('other cached binary changed '+name)
    old=(PARENT/'initrd.gz').read_bytes();new=a.image.read_bytes()
    f0=ROM['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    f1=ROM['rom_files'](new,a.rom_log.read_text(errors='replace'))
    if set(f0)!=set(f1):raise ValueError('ROM membership changed')
    for n in f0:
        if not n.startswith('sys\\bin\\') and ROM['file_data'](old,f0,n)!=ROM['file_data'](new,f1,n):raise ValueError('resource changed '+n)
    raw=E32['unpack_e32'](BINARY);w=lambda n:struct.unpack_from('<I',raw,n)[0]
    start=f1['sys\\bin\\ecom.dll'][0]
    code,size=struct.unpack_from('<I',new,start+0x14)[0],struct.unpack_from('<I',new,start+0x1c)[0]
    if code!=ROM['ROM_BASE']+start+120 or size!=w(48):raise ValueError('DLL code layout')
    ram=struct.unpack_from('<I',new,start+0x60)[0]
    old_start=f0['sys\\bin\\ecom.dll'][0]
    if ram!=struct.unpack_from('<I',old,old_start+0x60)[0] or struct.unpack_from('<I',new,start+0x28)[0]!=0:raise ValueError('ECom private BSS layout moved')
    expected=bytearray(raw[w(100):w(100)+size]);sites,_,_=FRONT['parse_e32_import_sites'](raw)
    expected_data=bytearray(raw[w(104):w(104)+w(52)])
    def rebase(buffer,at,kind):
        value=struct.unpack_from('<I',buffer,at)[0]
        if kind==1 or (kind==3 and w(76)<=(value&~1)<=w(76)+size):delta=code-w(76)
        elif kind==2 or (kind==3 and w(80)<=value<=w(80)+w(52)+w(68)):delta=ram-w(80)
        else:raise ValueError('unexpected ECom relocation '+hex(value))
        struct.pack_into('<I',buffer,at,(value+delta)&0xffffffff)
    for at,kind in relocations(raw,112).items():
        if at+120 not in sites:rebase(expected,at,kind)
    for at,kind in relocations(raw,116).items():rebase(expected_data,at,kind)
    for at,(module,ordinal,addend) in sites.items():
        pos=f1['sys\\bin\\'+module+'.dll'][0];count,address=struct.unpack_from('<II',new,pos+0x3c)
        if not 1<=ordinal<=count:raise ValueError('provider ordinal')
        target=struct.unpack_from('<I',new,address-ROM['ROM_BASE']+(ordinal-1)*4)[0]
        if not target:raise ValueError('absent provider')
        struct.pack_into('<I',expected,at-120,target+addend)
    holes=ABS['apply_absent_exports'](expected,raw,code)
    if holes!=ABS['absent_exports'](E32['unpack_e32'](EVID/'ecom-parent897.dll')):raise ValueError('absent exports changed')
    if bytes(expected)!=new[start+120:start+120+size]:raise ValueError('actual ROM DLL code mismatch')
    data=struct.unpack_from('<I',new,start+0x18)[0]-ROM['ROM_BASE']
    if struct.unpack_from('<I',new,start+0x24)[0]!=0 or expected_data:raise ValueError('actual ECom ROM initialized data mismatch')
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:raise ValueError('ROM expansion forbidden')
    return dict(status='HTCLEO_FILEMANAGER_DESTROY_ROM_OK',parent_package=PARENT.parent.name,parent_sha256=PARENT_SHA,
        image_sha256=sha(a.image),image_bytes=len(new),object_proof=proof,actual_code_exact=True,
        other_cached_binaries_unchanged=66,resources_unchanged=True,membership_unchanged=True,
        rom_window=0x03a00000,ram_start=0x15c00000,hardware_result='pending')
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true');p.add_argument('--native',type=Path)
    p.add_argument('--report',type=Path);p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--rom-log',type=Path)
    a=p.parse_args()
    if a.snapshot:snapshot();return
    result=verify_rom(a) if a.image else verify_objects(a.native)
    if not a.report:raise ValueError('report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']+' '+result.get('image_sha256',result.get('binary_sha256','')))
if __name__=='__main__':main()
