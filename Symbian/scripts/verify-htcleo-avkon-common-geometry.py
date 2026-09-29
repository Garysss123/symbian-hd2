#!/usr/bin/env python3
"""851: three EikCoCtl objects, exact ABI/imports, immutable850 ROM contract."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PARENT=HERE.parent/'output/850-symbian3-full-gsapp-root-bitmap-background-incremental/Symbian3'
PARENT_SHA='073eec12d89adc87533b6b488172a31d75429f2aadf076a59c90ab5b71f5b601'
EVID=HERE.parent/'output/iteration-evidence/851-avkon-common-geometry'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='645bdac7e42d5f9dc733fbd3452c0708834ee734f68a50045525c180ff1fd8f0'
PATCH=runpy.run_path(str(HERE/'apply-htcleo-avkon-common-geometry.py'))
PRIOR=runpy.run_path(str(HERE/'verify-htcleo-gsapp-statuspane-frontier.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
ROM=runpy.run_path(str(HERE/'verify-htcleo-gate17-entry.py'))
FRONT=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
E32=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))
BINARY=SDK/'epoc32/release/armv5/urel/eikcoctl.dll'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def contract():
    if sha(CONTRACT)!=CONTRACT_SHA:raise ValueError('851 standalone contract drift')
    return json.loads(CONTRACT.read_text())

def verify_objects(native):
    c=contract();base=json.loads((PARENT/'build/GSAPP-STATUSPANE-OBJECTS.json').read_text())
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('not immutable850')
    if c['parent_binary_sha256']!=base['binary_sha256']:raise ValueError('wrong parentEikCoCtl certificate')
    objects=PRIOR['objects']()
    if objects!=c['objects'] or len(objects)!=89:raise ValueError('objects differ from reviewed851 standalone')
    changed=[p for p in objects if objects[p]!=base['objects'][p]]
    if changed!=c['changed_objects'] or {Path(p).name for p in changed}!={'EIKCOLIB.o','eikspane.o','eikcba.o'}:
        raise ValueError('851 changes beyond three geometry units')
    for name in PATCH['BASE']:
        source=SDK/PATCH['REL']/name;text=source.read_text(encoding='latin-1')
        if sha(source)!=c['sources'][name] or PATCH['transform'](text,name)!=text:
            raise ValueError('851 source drift '+name)
    helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/PATCH['HELPER']
    if sha(helper)!=c['helper_sha256'] or helper.read_bytes()!=(SDK/PATCH['REL']/PATCH['HELPER']).read_bytes():
        raise ValueError('851 shared helper mismatch')
    before=(PARENT/'build/eikcoctl-e32-dump.txt').read_text();after=(native/'eikcoctl-geometry-851-full-dump.txt').read_text()
    if PRIOR['header'](before)!=PRIOR['header'](after):raise ValueError('EikCoCtl ABI/data/security changed')
    if {m:Counter(v) for m,v in GS['imports'](before).items()}!={m:Counter(v) for m,v in GS['imports'](after).items()}:
        raise ValueError('851 must add no imports or new providers')
    defs=list((SDK/'epoc32/build/eikcoctl-build').glob('*/eikcoctl_dll/armv5/urel/eikcoctl{000a0000}.def'))
    if len(defs)!=1 or defs[0].read_bytes()!=(PARENT/'build/eikcoctl-generated-exports.def').read_bytes():
        raise ValueError('851 frozen2022 export contract drift')
    return dict(status='HTCLEO_AVKON_COMMON_GEOMETRY_OBJECTS_OK',parent=PARENT.parent.name,
        binary_sha256=sha(BINARY),objects=objects,changed_objects=changed,sources=c['sources'],
        helper_sha256=c['helper_sha256'],data=0,bss=0,imports='exact850',
        policy='four portrait layout exits no appUID; logical CBA reduction; no ApplicationRect or input change')

def absent_exports(raw):
    # E32ImageHeaderV: export descriptor size/type at152/154, bytes at155.
    # Native elf2e32 E32ImageFile::CheckExportDescription defines these masks.
    if len(raw)<156:raise ValueError('truncated E32V header')
    count=struct.unpack_from('<I',raw,92)[0]
    code_offset=struct.unpack_from('<I',raw,100)[0]
    size,kind=struct.unpack_from('<HB',raw,152)
    if 155+size>code_offset or code_offset>len(raw):raise ValueError('invalid export descriptor extent')
    data=raw[155:155+size];nbytes=(count+7)//8
    if kind==0:
        if size:raise ValueError('unexpected no-holes descriptor bytes')
        return []
    if kind==1:
        if size!=nbytes:raise ValueError('invalid full export bitmap')
        bitmap=data
    elif kind==2:
        meta_size=(nbytes+7)//8
        if size<meta_size:raise ValueError('truncated sparse export bitmap')
        bitmap=bytearray([255]*nbytes);pos=meta_size
        for i in range(nbytes):
            if data[i//8]&(1<<(i%8)):
                if pos>=size or data[pos]==255:raise ValueError('invalid sparse export group')
                bitmap[i]=data[pos];pos+=1
        if pos!=size:raise ValueError('extra sparse export bytes')
    else:raise ValueError('unsupported E32 export descriptor type')
    return [i+1 for i in range(count) if not bitmap[i//8]&(1<<(i%8))]

def apply_absent_exports(expected,raw,address):
    holes=absent_exports(raw)
    word=lambda at:struct.unpack_from('<I',raw,at)[0]
    for ordinal in holes:
        at=word(88)-word(100)+(ordinal-1)*4
        if at<0 or at+4>len(expected):raise ValueError('absent export outside code')
        # E32 uses the entry point as its absent-export sentinel. ROM emits0.
        if word(word(88)+(ordinal-1)*4)!=word(76)+word(72):
            raise ValueError('absent export missing native E32 sentinel')
        if struct.unpack_from('<I',expected,at)[0]!=address+word(72):
            raise ValueError('absent export not its exact relocated sentinel')
        struct.pack_into('<I',expected,at,0)
    return holes

def verify_code(image,files,path):
    raw=E32['unpack_e32'](path);w=lambda off:struct.unpack_from('<I',raw,off)[0]
    start,end,address,size=FRONT['rom_code_span'](image,files,'sys\\bin\\'+path.name)
    if size!=w(48) or w(52)!=0:raise ValueError('unexpected geometry module shape')
    expected=bytearray(raw[w(100):w(100)+size]);ram=struct.unpack_from('<I',image,start+0x60)[0]
    sites,_,_=FRONT['parse_e32_import_sites'](raw)
    for offset,kind in E32['code_relocations'](raw).items():
        if offset+120 in sites:continue
        value=struct.unpack_from('<I',expected,offset)[0]
        if kind!=2 and w(76)<=(value&~1)<=w(76)+size:target=value+address-w(76)
        elif kind!=1 and w(80)<=value<=w(80)+w(68):target=value+ram-w(80)
        else:raise ValueError('unattributed relocation '+path.name+' '+hex(offset))
        struct.pack_into('<I',expected,offset,target)
    for offset,(module,ordinal,addend) in sites.items():
        provider=files['sys\\bin\\'+module+'.dll'][0]
        count,table=struct.unpack_from('<II',image,provider+0x3c)
        if ordinal<1 or ordinal>count:raise ValueError('missing851 provider ordinal')
        target=struct.unpack_from('<I',image,table-ROM['ROM_BASE']+(ordinal-1)*4)[0]
        if not target:raise ValueError('null851 import target')
        struct.pack_into('<I',expected,offset-120,target+addend)
    holes=apply_absent_exports(expected,raw,address)
    if holes!=absent_exports(E32['unpack_e32'](PARENT/'build/incremental-release-cache'/path.name)):
        raise ValueError('851 altered parent absent export set')
    if bytes(expected)!=image[start+120:end]:raise ValueError('actual851 ROM code differs '+path.name)
    return {'module':path.name,'code_address':hex(address),'code_bytes':size,'bss':w(68),'absent_exports':holes}

def verify_rom(a):
    proof=verify_objects(a.native)
    if a.recipe.read_bytes()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_bytes():raise ValueError('851 recipe changed')
    lines=(PARENT/'build/incremental-release-cache/RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines)!=65:raise ValueError('851 parent cache count')
    for line in lines:
        digest,path,name=line.split('\t')
        if sha(PARENT/'build/incremental-release-cache'/name)!=digest:raise ValueError('parent cache corrupted '+name)
        if path!=str(BINARY) and sha(Path(path))!=digest:raise ValueError('unexpected851 binary change '+name)
    old=(PARENT/'initrd.gz').read_bytes();new=a.image.read_bytes()
    f0=ROM['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text());f1=ROM['rom_files'](new,a.rom_log.read_text())
    if set(f0)!=set(f1):raise ValueError('851 membership changed')
    for name in f0:
        if not name.startswith('sys\\bin\\') and ROM['file_data'](old,f0,name)!=ROM['file_data'](new,f1,name):
            raise ValueError('851 resource changed '+name)
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:raise ValueError('851 ROM expansion forbidden')
    code=[verify_code(new,f1,BINARY),verify_code(new,f1,SDK/'epoc32/release/armv5/urel/gsapp.exe')]
    return dict(status='HTCLEO_AVKON_COMMON_GEOMETRY_ROM_OK',parent=PARENT.parent.name,parent_sha256=PARENT_SHA,
        image_sha256=hashlib.sha256(new).hexdigest(),image_bytes=len(new),unchanged_cached_binaries=64,
        resources_unchanged=True,membership_unchanged=True,rom_window=0x03a00000,ram_start=0x15c00000,
        relocated_code=code,object_proof=proof,hardware_result='pending')

def main():
    p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--image',type=Path)
    p.add_argument('--recipe',type=Path);p.add_argument('--rom-log',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    result=verify_rom(a) if a.image else verify_objects(a.native)
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
