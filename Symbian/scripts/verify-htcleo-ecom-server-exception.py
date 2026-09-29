#!/usr/bin/env python3
"""859: calibrated two-object terminal probe, exact ABI/code/data/ROM binding."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess

HERE=Path(__file__).resolve().parent;SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-ecom-server-exception.py'))
E32=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))
CONTROL=runpy.run_path(str(HERE/'verify-htcleo-ecom-825-source-control.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
FRONT=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'));ROM=FRONT['ROM']
PARENT=HERE.parent/'output/858-symbian3-full-gsapp-font-server-lifetime-incremental/Symbian3'
PARENT_SHA='83db824d7b7a1f960b8369dbaa5dc1ef751011cd2bcfea93cf7bf8b1a2c15e59'
BINARY=SDK/'epoc32/release/armv5/urel/ecomserver.exe'
EVID=HERE.parent/'output/iteration-evidence/859-ecom-server-exception'
CONTRACT=EVID/'STANDALONE-OBJECTS.json';CONTRACT_SHA='1c46eb9cd6647512df0e37efaae405af4d6022288245c3dd1a2d7a4b27a594d0'
BASE_SHA='d9a847c0e72566c5db31356a9b31daade61ae23e7ffa18bd455c9ff1f51bffca'
DUMP='ecomserver-exception-859-full-dump.txt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def header(text):
    keys=('Flags','Secure ID','Vendor ID','Capabilities','Module Version','Min Heap Size','Max Heap Size','Stack Size','Code link addr','Data link addr')
    result={k:' '.join(re.search(r'^'+re.escape(k)+r':\s*([^\n]+)',text,re.M)[1].lower().split()) for k in keys}
    for line in ('EPOC Exe for ARMV5 CPU','Priority Foreground','Image FPU support : Soft VFP','Number of exports = 0','ARM EABI','Built against EKA2'):
        if line not in text.splitlines():raise ValueError('EComServer ABI drift '+line)
    if not re.search(r'^Uids:\s+1000007a 1000008d 10009d8f ',text,re.M):raise ValueError('server UID drift')
    return result

def contract():
    if sha(CONTRACT)!=CONTRACT_SHA:raise ValueError('859 reviewed contract drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    c=contract();expected={m:Counter(v) for m,v in before.items()}
    if set(before)!=set(after):raise ValueError('859 no new providers')
    for m,d in c['delta'].items():
        if d['removed']:raise ValueError('859 unexpected import removal')
        for ordinal,addend,count in d['added']:expected[m][(ordinal,addend)]+=count
    if expected!={m:Counter(v) for m,v in after.items()}:raise ValueError('859 imports exceed terminal observer')

def wrapper(obj):
    text=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',str(obj)],text=True)
    match=re.search(r'<HtcleoEcSoftwareException\(TExcType\)>:\n(.*?)(?:\n\n|\Z)',text,re.S)
    if not match:raise ValueError('859 naked wrapper missing')
    body=match[1];ins=re.findall(r'^\s*[0-9a-f]+:\s+([0-9a-f]{4})\s+',body,re.M)
    if ins[:2]!=['4669','4672'] or len(ins)<3 or int(ins[2],16)&0xf800!=0xe000 or 'HtcleoEcExceptionBody' not in body:
        raise ValueError('859 wrapper must capture SP/LR before allocating stack')
    symbols=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-t',str(obj)],text=True)
    for size,name in (('00000020','_ZL14gHtcleoEcTrace'),('00000400','_ZL15gHtcleoEcRecord'),('00000004','_ZL16gHtcleoEcWriting')):
        if not re.search(r'\.bss\s+'+size+r'\s+'+name+r'\s*$',symbols,re.M):raise ValueError('859 static buffer attribution drift '+name)
    return {'entry_disassembly':body.strip(),'static_zero_bytes':1060,'record_off_fault_stack':True}

def verify_objects(native):
    c=contract();base=json.loads((EVID/'CONTROL-OBJECTS.json').read_text())
    if sha(PARENT/'initrd.gz')!=PARENT_SHA or sha(EVID/'ecomserver-parent858.exe')!=BASE_SHA or sha(PARENT/'build/incremental-release-cache/ecomserver.exe')!=BASE_SHA:
        raise ValueError('859 parent drift')
    CONTROL['compare'](E32['unpack_e32'](EVID/'ecomserver-parent858.exe'),E32['unpack_e32'](EVID/'ecomserver-control858.exe'))
    now={p:sha(Path(p)) for p in base['objects']};sources={p:sha(Path(p)) for p in base['sources']}
    if now!=c['objects'] or sources!=c['sources']:raise ValueError('859 objects/source differ from reviewed standalone')
    changes=sorted(Path(p).name for p in now if now[p]!=base['objects'][p])
    if changes!=['EComServerSession.o','EComServerStart.o']:raise ValueError('859 unexpected object changes')
    for name in P['BASE']:
        text=(SDK/P['ROOT']/name).read_text()
        if P['transform'](name,text)!=text:raise ValueError('859 transform drift '+name)
    mmp=SDK/P['ROOT'].parent/'MMPFiles/EComServer.mmp'
    if sha(mmp)!=base['mmp_sha256']:raise ValueError('859 stack/heap/MMP changed')
    for n in ('htcleoecservertrace.h','htcleoecserverexception.inl'):
        if (SDK/P['ROOT']/n).read_bytes()!=(HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/n).read_bytes():raise ValueError('859 helper source drift')
        if sha(SDK/P['ROOT']/n)!=c['helper_sha256'][n]:raise ValueError('859 helper no longer the reviewed build input')
    olddump=(EVID/'ecomserver-parent858-full-dump.txt').read_text();newdump=(native/DUMP).read_text()
    if header(olddump)!=header(newdump):raise ValueError('859 ABI/stack/heap drift')
    verify_imports(GS['imports'](olddump),GS['imports'](newdump))
    raw=E32['unpack_e32'](BINARY);old=E32['unpack_e32'](EVID/'ecomserver-parent858.exe');w=lambda b,n:struct.unpack_from('<I',b,n)[0]
    if w(raw,52)!=4 or w(raw,68)!=0x520 or w(old,68)!=0xfc or w(raw,116)!=0:raise ValueError('859 data/BSS beyond static1060 bytes')
    if raw[w(raw,104):w(raw,104)+4]!=old[w(old,104):w(old,104)+4]:raise ValueError('initialized data changed')
    entry=next(Path(p) for p in now if Path(p).name=='EComServerStart.o')
    return dict(status='HTCLEO_ECOM_SERVER_EXCEPTION_OBJECTS_OK',binary_sha256=sha(BINARY),parent_binary_sha256=BASE_SHA,
        objects=now,sources=sources,changed_objects=changes,header=header(newdump),data_bytes=4,bss_bytes=1312,
        added_zero_bytes=1060,wrapper=wrapper(entry),imports=c['delta'],mmp_sha256=sha(mmp),policy=P['POLICY'])

def server_rom(image,files):
    raw=E32['unpack_e32'](BINARY);w=lambda n:struct.unpack_from('<I',raw,n)[0]
    start,_=files['sys\\bin\\ecomserver.exe'];code,data,size=struct.unpack_from('<III',image,start+0x14)
    data_size=struct.unpack_from('<I',image,start+0x24)[0];ram=struct.unpack_from('<I',image,start+0x60)[0]
    if code!=ROM['ROM_BASE']+start+120 or size!=w(48) or data_size!=w(52) or data_size!=4:raise ValueError('859 server ROM layout')
    expected=bytearray(raw[w(100):w(100)+size]);sites,_,_=FRONT['parse_e32_import_sites'](raw)
    for pos,kind in E32['code_relocations'](raw).items():
        if pos+120 in sites:continue
        value=struct.unpack_from('<I',expected,pos)[0]
        if kind!=2 and w(76)<=(value&~1)<=w(76)+size:target=value+code-w(76)
        elif kind!=1 and w(80)<=value<=w(80)+w(52)+w(68):target=value+ram-w(80)
        else:raise ValueError('unattributed server relocation '+hex(pos))
        struct.pack_into('<I',expected,pos,target)
    for pos,(m,ordinal,addend) in sites.items():
        p=files['sys\\bin\\'+m+'.dll'][0];count,address=struct.unpack_from('<II',image,p+0x3c)
        if not 1<=ordinal<=count:raise ValueError('859 invalid import ordinal')
        value=struct.unpack_from('<I',image,address-ROM['ROM_BASE']+(ordinal-1)*4)[0]
        struct.pack_into('<I',expected,pos-120,value+addend)
    if bytes(expected)!=image[start+120:start+120+size]:raise ValueError('859 ROM code differs beyond declared fixups')
    at=data-ROM['ROM_BASE']
    if at<0 or at+4>len(image) or image[at:at+4]!=raw[w(104):w(104)+4]:raise ValueError('859 ROM initialized data mismatch')
    return dict(code_bytes=size,code_address=hex(code),initialized_data_address=hex(data),private_data_base=hex(ram),
        data_bytes=4,bss_bytes=w(68),code_and_data_exact=True)

def verify_rom(a):
    proof=verify_objects(a.native)
    if a.recipe.read_text()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text():raise ValueError('859 recipe/resource changes forbidden')
    cache=PARENT/'build/incremental-release-cache';rows=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows)!=67:raise ValueError('859 parent cache count')
    for row in rows:
        digest,path,name=row.split('\t')
        if sha(cache/name)!=digest or (path!=str(BINARY) and sha(Path(path))!=digest):raise ValueError('859 unexpected binary '+name)
    old=(PARENT/'initrd.gz').read_bytes();new=a.image.read_bytes();f0=ROM['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'));f1=ROM['rom_files'](new,a.rom_log.read_text(errors='replace'))
    if set(f0)!=set(f1):raise ValueError('859 ROM membership changed')
    for n in f0:
        if not n.startswith('sys\\bin\\') and ROM['file_data'](old,f0,n)!=ROM['file_data'](new,f1,n):raise ValueError('859 resource changed '+n)
    providers=GS['verify_providers'](new,f1,GS['imports']((a.native/DUMP).read_text()))
    code=server_rom(new,f1)
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:raise ValueError('859 ROM expansion forbidden')
    return dict(status='HTCLEO_ECOM_SERVER_EXCEPTION_ROM_OK',parent_package=PARENT.parent.name,parent_sha256=PARENT_SHA,
        image_sha256=sha(a.image),image_bytes=len(new),object_proof=proof,module=code,providers=providers,
        other_cached_binaries_unchanged=66,resources_unchanged=True,membership_unchanged=True,
        rom_window=0x03a00000,ram_start=0x15c00000,hardware_result='pending')

def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--rom-log',type=Path);a=p.parse_args()
    result=verify_rom(a) if a.image else verify_objects(a.native);a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
