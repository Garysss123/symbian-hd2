#!/usr/bin/env python3
"""870: one ailaunch object/worker delta, unchanged UI resources and C: payload."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-apparc-exit-watch.py'))
H=runpy.run_path(str(HERE/'verify-htcleo-home-kernel-watch.py'))
X=runpy.run_path(str(HERE/'verify-htcleo-ecom-server-exception.py'))
E32=X['E32'];ROM=X['ROM'];GS=X['GS'];FRONT=X['FRONT']
PARENT=HERE.parent/'output/869-symbian3-full-apparc-forced-native-registration-incremental/Symbian3'
PARENT_SHA='5f13452a274680d9a04818360cfbc564a9ef1ab9e20de364b802d808f04eb484'
BINARY=SDK/'epoc32/release/armv5/urel/ailaunch.exe'
EVID=HERE.parent/'output/iteration-evidence/870-apparc-exit-watch'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='366727d762871751d284768681a4ccf0053550a28fcb6c6b868729610995f8b0'
DUMP='ailaunch-exit-watch-870-full-dump.txt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def objects(native):
    if sha(PARENT/'initrd.gz')!=PARENT_SHA or sha(CONTRACT)!=CONTRACT_SHA:
        raise ValueError('870 parent/contract drift')
    if sha(PARENT/'MANIFEST.json')!='0618dbd5adb72c601165dae509b64b6643417344874b52a1feb5aadc6ac54b02':
        raise ValueError('870 must retain the exact865 C: contract')
    base=json.loads((EVID/'BASE-OBJECTS.json').read_text());c=json.loads(CONTRACT.read_text())
    obj={p:sha(Path(p)) for p in base['objects']};sources={p:sha(Path(p)) for p in base['sources']}
    if obj!=c['objects'] or sources!=c['sources']:raise ValueError('870 source/objects exceed reviewed change')
    changed=sorted(Path(p).name for p in obj if obj[p]!=base['objects'][p])
    if changed!=['hslaunch.o']:raise ValueError('870 only hslaunch.o may change')
    body=(SDK/P['REL']).read_text()
    if P['transform'](body)!=body:raise ValueError('870 worker patch drift')
    mmp=SDK/'sf/mw/homescreensrv/idlefw/hslaunch/group/hslaunch.mmp'
    if sha(mmp)!=base['mmp_sha256']:raise ValueError('870 MMP/stack/heap changed')
    before=(EVID/'ailaunch-parent869-full-dump.txt').read_text();after=(native/DUMP).read_text()
    if H['header'](before)!=H['header'](after):raise ValueError('870 ABI/data/BSS changed')
    expected={name:Counter(values) for name,values in GS['imports'](before).items()}
    for module,ordinal in (('euser',216),('euser',605),('euser',929)):
        expected[module][(ordinal,0)]+=1
    if expected!={name:Counter(values) for name,values in GS['imports'](after).items()}:
        raise ValueError('870 imports exceed the reviewed passive exit-watch primitives')
    raw=E32['unpack_e32'](BINARY);old=E32['unpack_e32'](EVID/'ailaunch-parent869.exe')
    w=lambda b,p:struct.unpack_from('<I',b,p)[0]
    if (w(raw,52),w(raw,68),w(raw,116))!=(20,52,0):raise ValueError('870 data/relocation drift')
    if raw[w(raw,104):w(raw,104)+20]!=old[w(old,104):w(old,104)+20]:raise ValueError('870 initialized data changed')
    return dict(status='HTCLEO_FILEMANAGER_REGISTRATION_OBJECTS_OK',objects=obj,sources=sources,
        changed_objects=changed,binary_sha256=sha(BINARY),base_binary_sha256=base['binary_sha256'],
        header=H['header'](after),mmp_sha256=sha(mmp),data_bytes=20,bss_bytes=52,
        import_delta_counts=c['import_delta_counts'],worker_same_priority_stack=True,
        observation_wait_us=30000000,original_session_closed_before_wait=True,policy=P['POLICY'])


def module_rom(image,files):
    raw=E32['unpack_e32'](BINARY);w=lambda n:struct.unpack_from('<I',raw,n)[0]
    start,_=files['sys\\bin\\ailaunch.exe']
    code,data,size=struct.unpack_from('<III',image,start+0x14)
    data_size=struct.unpack_from('<I',image,start+0x24)[0]
    ram=struct.unpack_from('<I',image,start+0x60)[0]
    if code!=ROM['ROM_BASE']+start+120 or size!=w(48) or data_size!=20:raise ValueError('870 module layout')
    expected=bytearray(raw[w(100):w(100)+size])
    sites,_,_=FRONT['parse_e32_import_sites'](raw)
    for pos,kind in E32['code_relocations'](raw).items():
        if pos+120 in sites:continue
        value=struct.unpack_from('<I',expected,pos)[0]
        if kind!=2 and w(76)<=(value&~1)<=w(76)+size:target=value+code-w(76)
        elif kind!=1 and w(80)<=value<=w(80)+w(52)+w(68):target=value+ram-w(80)
        else:raise ValueError('870 unknown relocation '+hex(pos))
        struct.pack_into('<I',expected,pos,target)
    for pos,(module,ordinal,addend) in sites.items():
        at=files['sys\\bin\\'+module+'.dll'][0]
        count,address=struct.unpack_from('<II',image,at+0x3c)
        if not 1<=ordinal<=count:raise ValueError('870 import out of ROM range')
        target=struct.unpack_from('<I',image,address-ROM['ROM_BASE']+(ordinal-1)*4)[0]
        if not target:raise ValueError('870 absent import')
        struct.pack_into('<I',expected,pos-120,target+addend)
    if bytes(expected)!=image[start+120:start+120+size]:raise ValueError('870 ROM code differs beyond fixups')
    at=data-ROM['ROM_BASE']
    if at<0 or image[at:at+20]!=raw[w(104):w(104)+20]:raise ValueError('870 ROM data differs')
    return dict(code_address=hex(code),code_bytes=size,data_bytes=20,bss_bytes=52,
                private_data_base=hex(ram),code_data_exact=True)


def verify(a):
    proof=objects(a.native)
    if a.recipe.read_text()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('870 must retain all869 ROM resource paths')
    cache=PARENT/'build/incremental-release-cache'
    rows=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows)!=67:raise ValueError('870 cache count')
    for row in rows:
        digest,path,name=row.split('\t')
        if sha(cache/name)!=digest or (path!=str(BINARY) and sha(Path(path))!=digest):
            raise ValueError('870 changed other binary '+name)
    old=(PARENT/'initrd.gz').read_bytes();new=a.image.read_bytes()
    f0=ROM['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    f1=ROM['rom_files'](new,a.rom_log.read_text(errors='replace'))
    if set(f0)!=set(f1):raise ValueError('870 membership changed')
    for name in f0:
        if not name.startswith('sys\\bin\\') and ROM['file_data'](old,f0,name)!=ROM['file_data'](new,f1,name):
            raise ValueError('870 resource changed '+name)
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:raise ValueError('870 ROM window changed')
    providers=GS['verify_providers'](new,f1,GS['imports']((a.native/DUMP).read_text()))
    return dict(status='HTCLEO_FILEMANAGER_REGISTRATION_ROM_OK',parent_package=PARENT.parent.name,
        parent_sha256=PARENT_SHA,image_sha256=sha(a.image),image_bytes=len(new),
        object_proof=proof,module=module_rom(new,f1),providers=providers,
        other_cached_binaries_unchanged=66,resources_unchanged=True,membership_unchanged=True,
        c_overlay_origin='865',c_overlay_unchanged=True,rom_window=0x03a00000,ram_start=0x15c00000,
        hardware_result='pending')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--rom-log',type=Path)
    a=p.parse_args();result=verify(a) if a.image else objects(a.native)
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
