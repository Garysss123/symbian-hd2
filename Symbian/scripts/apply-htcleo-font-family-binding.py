#!/usr/bin/env python3
"""852: three attributed FontProvider constdata typeface names, no code change."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PARENT=HERE.parent/'output/851-symbian3-full-avkon-common-geometry-incremental/Symbian3'
PARENT_SHA='eada39ab3ea630c91bb3cbcf2df68102a93d7f3a6ed5b6a754a71f756a4b12fe'
EVID=HERE.parent/'output/iteration-evidence/852-font-family-binding'
STOCK=EVID/'FontProvider-stock-851.dll'
BASE_SHA='b742ec3aa25e63a675b4169add3e10b032d77234295f22cdd17c277cd1e0d429'
BINARY=SDK/'epoc32/release/armv5/urel/FontProvider.dll'
LINK=0x8000
TARGET='DejaVu Sans'
SITES=(('KS60Digital',0xb524,36,'Series 60 ZDigi'),
       ('KS60Sans',0xb548,36,'Series 60 Sans'),
       ('KS60SansTitleSemiBold',0xb56c,56,'Series 60 Sans TitleSmBd'))
POLICY='FontProvider-three-constdata-families-to-existing-DejaVu-Sans-no-code-fontfile-or-layout-change'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def base_raw():
    if sha(STOCK)!=BASE_SHA:raise ValueError('stock FontProvider identity changed')
    return runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))['unpack_e32'](STOCK)

def patch_region(blob,base_offset):
    result=bytearray(blob);ranges=[]
    for name,address,size,old in SITES:
        offset=base_offset+address-LINK;encoded=old.encode('utf-16le')
        if offset<0 or offset+size>len(blob):raise ValueError('font literal outside image')
        if struct.unpack_from('<I',blob,offset)[0]!=len(old) or blob[offset+4:offset+4+len(encoded)]!=encoded:
            raise ValueError('unexpected native TLitC '+name)
        if blob[offset+4+len(encoded):offset+6+len(encoded)]!=b'\0\0':raise ValueError('font literal terminator drift')
        replacement=TARGET.encode('utf-16le')
        if len(replacement)>len(encoded):raise ValueError('no literal storage growth allowed')
        struct.pack_into('<I',result,offset,len(TARGET))
        result[offset+4:offset+4+len(encoded)]=replacement+b'\0'*(len(encoded)-len(replacement))
        ranges.append({'symbol':name,'link_address':hex(address),'offset':offset,'bytes':4+len(encoded),'before':old,'after':TARGET})
    return bytes(result),ranges

def transform(raw):
    word=lambda off:struct.unpack_from('<I',raw,off)[0]
    if len(raw)<156 or raw[16:20]!=b'EPOC' or word(28)!=0 or word(76)!=LINK or word(100)!=156:
        raise ValueError('unexpected FontProvider E32 container')
    return patch_region(raw,word(100))[0]

def expected_rom():
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('not immutable851')
    old=(PARENT/'initrd.gz').read_bytes()
    api=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
    files=api['ROM']['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text())
    start,end,code,size=api['rom_code_span'](old,files,'sys\\bin\\fontprovider.dll')
    raw=base_raw()
    if size!=struct.unpack_from('<I',raw,48)[0]:raise ValueError('FontProvider source/ROM size mismatch')
    patched,ranges=patch_region(old,start+120)
    for r in ranges:
        if r['offset']+r['bytes']>end:raise ValueError('literal crosses module')
        r['rom_address']=hex(code+int(r['link_address'],16)-LINK)
    # TRomHeader::iCheckSum at0xA8 preserves the configured32-bit image sum.
    # Derive its new value only from words touched by our three data objects;
    # no checksum field or unrelated byte is masked during final comparison.
    words={i&~3 for r in ranges for i in range(r['offset'],r['offset']+r['bytes'])}
    if 0xa8 in words:raise ValueError('font data overlaps ROM checksum')
    delta=sum(struct.unpack_from('<I',patched,i)[0]-struct.unpack_from('<I',old,i)[0] for i in words)
    checksum=(struct.unpack_from('<I',old,0xa8)[0]-delta)&0xffffffff
    patched=patched[:0xa8]+struct.pack('<I',checksum)+patched[0xac:]
    return old,patched,ranges

def verify_binary():
    raw=base_raw();expected=transform(raw)
    unpack=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))['unpack_e32']
    if unpack(BINARY)!=expected:raise ValueError('FontProvider differs beyond three data descriptors')
    return dict(status='HTCLEO_FONT_FAMILY_BINARY_OK',policy=POLICY,base_binary_sha256=BASE_SHA,
        binary_sha256=sha(BINARY),changed_raw_bytes=sum(x!=y for x,y in zip(raw,expected)),
        changes=patch_region(raw,156)[1],instructions_headers_imports_exports_relocations='unchanged after E32 decompression')

def prepare_parent(manifest):
    raw=base_raw()
    if sha(BINARY)!=BASE_SHA:
        unpack=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))['unpack_e32']
        if unpack(BINARY)!=transform(raw):raise ValueError('unexpected FontProvider before parent restore')
        BINARY.write_bytes(STOCK.read_bytes())
    expected_rom() # Attribute the same literals to the immutable parent.
    if not manifest.resolve().is_relative_to(Path('/root/symbian3-full-work/htcleo-native')):
        raise ValueError('refuse out-of-work release manifest')
    lines=manifest.read_text().splitlines()
    if len(lines)!=65 or any(line.split(None,1)[1]==str(BINARY) for line in lines):
        raise ValueError('expected65 tracked inputs before adding stock FontProvider')
    for line in lines:
        digest,path=line.split(None,1)
        if sha(Path(path))!=digest:raise ValueError('parent input changed '+path)
    lines.append(BASE_SHA+'  '+str(BINARY));manifest.write_text('\n'.join(sorted(lines))+'\n')
    print('HTCLEO_FONT_FAMILY_PARENT=65-plus1-original-FontProvider-pinned-to851')

def main():
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--extend-release-manifest',type=Path)
    p.add_argument('--image',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    if a.extend_release_manifest:
        prepare_parent(a.extend_release_manifest);return
    if a.apply:
        if sha(BINARY)!=BASE_SHA:raise ValueError('852 requires exact stock FontProvider before apply')
        BINARY.write_bytes(transform(base_raw()))
    proof=verify_binary()
    if a.image:
        old,new,ranges=expected_rom();actual=a.image.read_bytes()
        if actual!=new:raise ValueError('852 full ROM differs beyond font data and its derived checksum')
        proof.update(status='HTCLEO_FONT_FAMILY_ROM_OK',parent=PARENT.parent.name,parent_sha256=PARENT_SHA,
            image_sha256=sha(a.image),image_bytes=len(actual),changed_rom_bytes=sum(x!=y for x,y in zip(old,new)),
            rom_changes=ranges,rom_checksum={'offset':'0xa8','before':hex(struct.unpack_from('<I',old,0xa8)[0]),'after':hex(struct.unpack_from('<I',new,0xa8)[0]),'rule':'preserve parent32-bit sum using exact changed-word delta'},
            all_other_rom_bytes='identical851 including geometry; only derived ROM checksum additionally changes',
            rom_window=0x03a00000,ram_start=0x15c00000,hardware_result='pending')
    if not a.report:raise ValueError('report required')
    a.report.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,sort_keys=True))

if __name__=='__main__':main()
