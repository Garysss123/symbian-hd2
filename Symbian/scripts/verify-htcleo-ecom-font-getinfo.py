#!/usr/bin/env python3
"""863: one-object native GetInfo split, one verified import, no security change."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
P=runpy.run_path(str(HERE/'apply-htcleo-ecom-font-registry.py'))
Q=runpy.run_path(str(HERE/'apply-htcleo-ecom-font-getinfo.py'))
ECX=runpy.run_path(str(HERE/'verify-htcleo-ecom-server-exception.py'))
ROM=ECX['ROM']; E32=ECX['E32']; GS=ECX['GS']
PARENT=HERE.parent/'output/862-symbian3-full-ecom-font-registry-incremental/Symbian3'
PARENT_SHA='ea34f115db07eb48fdedf2968cd85e986cf54c0efa46d91a43cbc5ad6c13ddfe'
BINARY=SDK/'epoc32/release/armv5/urel/ecomserver.exe'
EVID=HERE.parent/'output/iteration-evidence/863-ecom-font-getinfo'
CONTRACT=EVID/'STANDALONE-OBJECTS-CORRECTED.json'
CONTRACT_SHA='a64fdfaa68006da51937fc3bbbca1e06977a5a2b8f2c3e29c4599cbe43f9e786'
DUMP='ecomserver-font-getinfo-863-full-dump.txt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def verify_objects(native):
    if sha(PARENT/'initrd.gz')!=PARENT_SHA or sha(CONTRACT)!=CONTRACT_SHA:
        raise ValueError('863 parent/contract drift')
    c=json.loads(CONTRACT.read_text())
    base=json.loads((PARENT/'build/ECOM-FONT-REGISTRY-OBJECTS.json').read_text())
    if base['binary_sha256']!='d4e93a19c30f0ff6864f05404be03aa2d42e3cfb6784bcecc2ae5925c343815e':
        raise ValueError('863 must retain immutable862')
    objects={f:sha(Path(f)) for f in base['objects']}
    sources={f:sha(Path(f)) for f in base['sources']}
    if objects!=c['objects'] or sources!=c['sources']:
        raise ValueError('863 objects/source exceed reviewed RegistryData split')
    changed=sorted(Path(f).name for f in objects if objects[f]!=base['objects'][f])
    if changed!=['RegistryData.o']:
        raise ValueError('863 unexpected object changes')
    for name in P['BASE']:
        text=(SDK/P['ROOT']/name).read_text()
        if name=='RegistryData.cpp':
            if Q['transform'](text)!=text:raise ValueError('863 wrapper split drift')
            text=Q['transform'](text,True)
        if P['transform'](name,text)!=text:
            raise ValueError('863 source not exact observational overlay '+name)
    for name,digest in c['helper_sha256'].items():
        if sha(SDK/P['ROOT']/name)!=digest:
            raise ValueError('863 helper changed '+name)
    for name in ('htcleoecfontregistry.h','htcleoecfontregistry.inl'):
        if (SDK/P['ROOT']/name).read_bytes()!=(HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/name).read_bytes():
            raise ValueError('863 helper not from reviewed repo '+name)
    mmp=SDK/P['ROOT'].parent/'MMPFiles/EComServer.mmp'
    if sha(mmp)!=base['mmp_sha256']:
        raise ValueError('863 MMP changed')
    before=(PARENT/'build/ecomserver-font-registry-862-full-dump.txt').read_text()
    after=(native/DUMP).read_text()
    if ECX['header'](before)!=ECX['header'](after):
        raise ValueError('863 ABI/stack/heap changed')
    expected={m:Counter(x) for m,x in GS['imports'](before).items()}
    expected['euser'][(1138,0)]+=1 # RLoader::GetInfo, native euseru.def
    if expected!={m:Counter(x) for m,x in GS['imports'](after).items()}:
        raise ValueError('863 only native RLoader GetInfo import may be added')
    raw=E32['unpack_e32'](BINARY)
    old=E32['unpack_e32'](PARENT/'build/incremental-release-cache/ecomserver.exe')
    w=lambda b,n:struct.unpack_from('<I',b,n)[0]
    if (w(raw,52),w(raw,68))!=(4,1340) or raw[w(raw,104):w(raw,104)+4]!=old[w(old,104):w(old,104)+4]:
        raise ValueError('863 data/BSS differs from862')
    entry=next(Path(f) for f in objects if Path(f).name=='EComServerStart.o')
    wrapper=ECX['wrapper'](entry)
    dump=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drCt',str(entry)],text=True)
    if not re.search(r'\.bss\s+0000001c\s+gHtcleoEcFont\s*$',dump,re.M):
        raise ValueError('863 RAM buffer is not exactly28 zero bytes')
    mark=re.search(r'<HtcleoEcFontMark\(unsigned long, int, unsigned long\)>:\n(.*?)(?:\n\n|\Z)',dump,re.S)
    if not mark or re.search(r'R_ARM_.*CALL|\bblx?\b',mark[1]):
        raise ValueError('863 RAM marking must not call any service')
    return dict(status='HTCLEO_ECOM_FONT_GETINFO_OBJECTS_OK',parent_package=PARENT.parent.name,
        binary_sha256=sha(BINARY),parent_binary_sha256=base['binary_sha256'],changed_objects=changed,
        objects=objects,sources=sources,mmp_sha256=sha(mmp),header=ECX['header'](after),
        imports='862-plus-euser1138-native-RLoader-GetInfo-only',helper_sha256=c['helper_sha256'],wrapper=wrapper,
        data_bytes=4,bss_bytes=1340,added_zero_bytes=0,normal_file_writes_added=0,policy=Q['POLICY'])


def verify_rom(a):
    proof=verify_objects(a.native)
    if a.recipe.read_text()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('863 recipe changed')
    cache=PARENT/'build/incremental-release-cache'
    rows=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(rows)!=67:
        raise ValueError('863 parent cache count')
    for row in rows:
        digest,path,name=row.split('\t')
        if sha(cache/name)!=digest or (path!=str(BINARY) and sha(Path(path))!=digest):
            raise ValueError('863 unexpected binary '+name)
    old=(PARENT/'initrd.gz').read_bytes();new=a.image.read_bytes()
    f0=ROM['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    f1=ROM['rom_files'](new,a.rom_log.read_text(errors='replace'))
    if set(f0)!=set(f1):
        raise ValueError('863 ROM membership changed')
    for n in f0:
        if not n.startswith('sys\\bin\\') and ROM['file_data'](old,f0,n)!=ROM['file_data'](new,f1,n):
            raise ValueError('863 resource changed '+n)
    providers=GS['verify_providers'](new,f1,GS['imports']((a.native/DUMP).read_text()))
    code=ECX['server_rom'](new,f1)
    euser=f1['sys\\bin\\euser.dll'][0]
    ex=struct.unpack_from('<I',new,euser+0x40)[0]
    rloader_getinfo=struct.unpack_from('<I',new,ex-ROM['ROM_BASE']+(1138-1)*4)[0]
    if rloader_getinfo!=0x122f7794:
        raise ValueError('863 native RLoader GetInfo provider address changed')
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:
        raise ValueError('863 ROM expansion forbidden')
    return dict(status='HTCLEO_ECOM_FONT_GETINFO_ROM_OK',parent_package=PARENT.parent.name,
        parent_sha256=PARENT_SHA,image_sha256=sha(a.image),image_bytes=len(new),object_proof=proof,
        module=code,providers=providers,other_cached_binaries_unchanged=66,resources_unchanged=True,
        membership_unchanged=True,rom_window=0x03a00000,ram_start=0x15c00000,hardware_result='pending')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--native',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--rom-log',type=Path)
    a=p.parse_args();result=verify_rom(a) if a.image else verify_objects(a.native)
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
