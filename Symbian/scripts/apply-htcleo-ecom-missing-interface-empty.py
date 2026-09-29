#!/usr/bin/env python3
"""860: true IndexedFind-not-found takes the existing empty-list exit, one byte."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent;SDK=Path('/root/symbian3-full')
PARENT=HERE.parent/'output/859-symbian3-full-ecom-server-exception-incremental/Symbian3'
PARENT_SHA='d97940edd3bf189a2090abcd8f7d30c8d0f5bc9578785025bc41f05c9515ca64'
EVID=HERE.parent/'output/iteration-evidence/860-ecom-missing-interface-empty'
STOCK=EVID/'ecomserver-parent859.exe';MAP=EVID/'ecomserver-parent859.map'
BASE_SHA='9ea9c1706b5728ad8ca33206f07d9204d40a88d2b616a1efd4ef005b48a2df20'
MAP_SHA='ef457b5a5e17e76a140ddf0c4739164f092e2022dab7ee6ac3b5944724dd805a'
BINARY=SDK/'epoc32/release/armv5/urel/ecomserver.exe'
LINK=0x8000;START=0xe750;SITE=0xe768;TARGET=0xe784
WINDOW=bytes.fromhex('021c2b48faf73af816e72d482d490022faf734f82c4881450cd02a4806f0c2e935e72a482a490022faf728f8284806f0bae9ede6301c06f03eea0021021c2548faf71cf8b8e7c046e0f30000e1f30000e2f30000')
POLICY='ECom-actual-IndexedFind-notfound-existing-empty-list-exit-one-branch-byte-no-global-unwind-change'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
E32=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))

def base_raw():
    if sha(STOCK)!=BASE_SHA or sha(MAP)!=MAP_SHA:raise ValueError('860 parent/map drift')
    mapping=MAP.read_text()
    if 'ListImplementationsL' not in mapping or '0x0000e524' not in mapping:raise ValueError('860 registry function attribution absent')
    return E32['unpack_e32'](STOCK)

def transform(raw):
    word=lambda n:struct.unpack_from('<I',raw,n)[0]
    if raw[16:20]!=b'EPOC' or word(28)!=0 or word(100)!=156 or word(76)!=LINK:raise ValueError('860 E32 layout drift')
    start=word(100)+START-LINK;site=word(100)+SITE-LINK
    if raw[start:start+len(WINDOW)]!=WINDOW:raise ValueError('860 not-found/feature-return code window drift')
    if word(word(100)+0xe814-LINK)!=0xffffbd94 or word(word(100)+0xe818-LINK)!=0x10205057:
        raise ValueError('860 leave error/feature UID literals drift')
    if raw[site:site+2]!=bytes.fromhex('0cd0'):raise ValueError('860 expected BEQ to native empty return')
    out=bytearray(raw);out[site+1]=0xe0 # BEQ +24 -> B +24; unchanged destination E784.
    return bytes(out)

def expected_rom():
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('860 not immutable859')
    old=(PARENT/'initrd.gz').read_bytes();api=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'));rom=api['ROM']
    files=rom['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    start,_=files['sys\\bin\\ecomserver.exe'];code=struct.unpack_from('<I',old,start+0x14)[0];size=struct.unpack_from('<I',old,start+0x1c)[0]
    raw=base_raw()
    if code!=rom['ROM_BASE']+start+120 or size!=struct.unpack_from('<I',raw,48)[0]:raise ValueError('860 ROM server code shape drift')
    at=start+120+START-LINK;site=start+120+SITE-LINK
    if old[at:at+len(WINDOW)]!=WINDOW:raise ValueError('860 actual ROM branch attribution drift')
    new=bytearray(old);new[site+1]=0xe0
    aligned=site&~3
    delta=struct.unpack_from('<I',new,aligned)[0]-struct.unpack_from('<I',old,aligned)[0]
    checksum=(struct.unpack_from('<I',old,0xa8)[0]-delta)&0xffffffff;struct.pack_into('<I',new,0xa8,checksum)
    return old,bytes(new),dict(branch_offset=site,changed_offset=site+1,rom_address=hex(code+SITE-LINK),target_rom=hex(code+TARGET-LINK),
        link_address=hex(SITE),before='0cd0',after='0ce0',source_case='IndexedFind(aInterfaceUid) == KErrNotFound; output already Reset',
        checksum_before=hex(struct.unpack_from('<I',old,0xa8)[0]),checksum_after=hex(checksum))

def verify_binary():
    expected=transform(base_raw())
    if E32['unpack_e32'](BINARY)!=expected:raise ValueError('860 server differs beyond one branch byte')
    return dict(status='HTCLEO_ECOM_EMPTY_INTERFACE_BINARY_OK',policy=POLICY,binary_sha256=sha(BINARY),parent_binary_sha256=BASE_SHA,
        changed_raw_bytes=1,headers_imports_exports_data_bss_eh='unchanged after decompression',other_errors='unchanged',
        global_unwind_fix=False,font_registration_proven=False)

def main():
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    if a.apply:
        if sha(BINARY)!=BASE_SHA:raise ValueError('860 requires exact859 binary before patch')
        BINARY.write_bytes(transform(base_raw()))
    result=verify_binary()
    if a.image:
        old,new,site=expected_rom()
        if a.image.read_bytes()!=new:raise ValueError('860 entire ROM differs beyond branch and derived checksum')
        if not a.recipe or a.recipe.read_text()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text():raise ValueError('860 recipe/membership must stay859')
        cache=PARENT/'build/incremental-release-cache';rows=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
        if len(rows)!=67:raise ValueError('860 parent cache count drift')
        for row in rows:
            digest,path,name=row.split('\t')
            if sha(cache/name)!=digest or (path!=str(BINARY) and sha(Path(path))!=digest):raise ValueError('860 unexpected binary '+name)
        result.update(status='HTCLEO_ECOM_EMPTY_INTERFACE_ROM_OK',parent_package=PARENT.parent.name,parent_sha256=PARENT_SHA,
            image_sha256=sha(a.image),image_bytes=len(new),changed_rom_bytes=sum(x!=y for x,y in zip(old,new)),site=site,
            other_cached_binaries_unchanged=66,all_other_rom_bytes='exact859 except derived checksum',rom_window=0x03a00000,ram_start=0x15c00000,hardware_result='pending')
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
