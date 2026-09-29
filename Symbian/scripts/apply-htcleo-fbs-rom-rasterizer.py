#!/usr/bin/env python3
"""857: one attributed FBServ argument byte, native ROM-only resolver A/B."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent
SDK=Path('/root/symbian3-full')
PARENT=HERE.parent/'output/856-symbian3-full-font-ecom-list-reconnect-incremental/Symbian3'
PARENT_SHA='30874c71be5588b94073a00eb87d7354a8246a91d4beb05d4136d2c43a8f71e3'
EVID=HERE.parent/'output/iteration-evidence/857-fbs-rom-rasterizer'
STOCK=EVID/'fbserv-parent856.exe'
MAP=EVID/'fbserv-parent856.map'
BASE_SHA='ebd2e0705567ddac8ee7311921bb192d0c83237b2b85ae2a1aba8dc0f79e8d15'
MAP_SHA='4ad990b0576e7a09202ccf0a1cc6debaf5ff1501cf5ff0e6ba630f4405e5cd92'
BINARY=SDK/'epoc32/release/armv5/urel/fbserv.exe'
LINK=0x8000;CALLER=0xa15e;SITE=0xa16c;CALLEE=0x9f3c
REGION=bytes.fromhex('f1b588b0070002a8fef73ae87a4800224068019001a802a9fff7e1fe02a8fef79aea060000241be0210002a8fef7a0ea0568fef788ea009069683800fff7d0ff0098fef740ea0ae0fef706e9fef764ea03e0fef700e9fef7aeeafef700e9641cb442e1db02a801f043ff04e7')
POLICY='FBServ-LoadOpenFontLibraries-native-ROM-only-resolver-r2-false-to-true-one-byte-no-relink'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def unpack(path):
    return runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))['unpack_e32'](path)

def base_raw():
    if sha(STOCK)!=BASE_SHA or sha(MAP)!=MAP_SHA:raise ValueError('FBServ parent/map identity drift')
    text=MAP.read_text()
    if not all(x in text for x in ('CFbTop::LoadOpenFontLibraries()','0x0000a15f','ListImplementationsWithRetry(TUid&,','0x00009f3d')):
        raise ValueError('FBServ source-map attribution absent')
    return unpack(STOCK)

def transform(raw):
    word=lambda off:struct.unpack_from('<I',raw,off)[0]
    if len(raw)<156 or raw[16:20]!=b'EPOC' or word(28)!=0 or word(76)!=LINK or word(100)!=156:
        raise ValueError('FBServ E32 layout drift')
    pos=word(100)+CALLER-LINK
    if raw[pos:pos+len(REGION)]!=REGION:raise ValueError('FBServ attributed caller bytes drift')
    # r2 is the third argument. It is not overwritten between movs r2,#0
    # atA16C and bl9F3C atA176. All EH/cleanup/loop/UID/import code stays exact.
    out=bytearray(raw);out[word(100)+SITE-LINK]=1
    return bytes(out)

def expected_rom():
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('not immutable856')
    old=(PARENT/'initrd.gz').read_bytes()
    api=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
    files=api['ROM']['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    start,end,code,size=api['rom_code_span'](old,files,'sys\\bin\\fbserv.exe')
    raw=base_raw()
    if size!=struct.unpack_from('<I',raw,48)[0]:raise ValueError('FBServ ROM/source size drift')
    begin=start+120+CALLER-LINK;site=start+120+SITE-LINK
    if old[begin:begin+len(REGION)]!=REGION or site>=end:raise ValueError('FBServ actual ROM caller drift')
    new=bytearray(old);new[site]=1
    word_offset=site&~3
    delta=struct.unpack_from('<I',new,word_offset)[0]-struct.unpack_from('<I',old,word_offset)[0]
    checksum=(struct.unpack_from('<I',old,0xa8)[0]-delta)&0xffffffff
    struct.pack_into('<I',new,0xa8,checksum)
    return old,bytes(new),dict(offset=site,rom_address=hex(code+SITE-LINK),link_address=hex(SITE),
        before='0022',after='0122',register='r2',callee_link=hex(CALLEE),
        checksum_offset='0xa8',checksum_before=hex(struct.unpack_from('<I',old,0xa8)[0]),checksum_after=hex(checksum))

def verify_binary():
    raw=base_raw();new=transform(raw)
    if unpack(BINARY)!=new:raise ValueError('FBServ differs beyond the one argument byte')
    return dict(status='HTCLEO_FBS_ROM_RASTERIZER_BINARY_OK',policy=POLICY,
        binary_sha256=sha(BINARY),parent_binary_sha256=BASE_SHA,map_sha256=MAP_SHA,
        changed_raw_bytes=1,header_data_import_export_relocation_exception_tables='unchanged after decompression')

def prepare_parent(manifest):
    raw=base_raw()
    if sha(BINARY)!=BASE_SHA:
        if unpack(BINARY)!=transform(raw):raise ValueError('unexpected FBServ before parent restore')
        BINARY.write_bytes(STOCK.read_bytes())
    expected_rom()
    if not manifest.resolve().is_relative_to(Path('/root/symbian3-full-work/htcleo-native')):raise ValueError('out-of-work release manifest')
    lines=manifest.read_text().splitlines()
    if len(lines)!=66 or any(row.split(None,1)[1]==str(BINARY) for row in lines):raise ValueError('expected66 inputs before tracking FBServ')
    for row in lines:
        digest,path=row.split(None,1)
        if sha(Path(path))!=digest:raise ValueError('parent input changed '+path)
    lines.append(BASE_SHA+'  '+str(BINARY));manifest.write_text('\n'.join(sorted(lines))+'\n')
    print('HTCLEO_FBS_ROM_RASTERIZER_PARENT=66-plus1-pinned-original-FBServ')

def main():
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--extend-release-manifest',type=Path)
    p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    if a.extend_release_manifest:prepare_parent(a.extend_release_manifest);return
    if a.apply:
        if sha(BINARY)!=BASE_SHA:raise ValueError('857 requires original FBServ before apply')
        BINARY.write_bytes(transform(base_raw()))
    proof=verify_binary()
    if a.image:
        old,expected,site=expected_rom();actual=a.image.read_bytes()
        if actual!=expected:raise ValueError('857 entire ROM differs beyond argument byte and derived checksum')
        if not a.recipe or a.recipe.read_text()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text():raise ValueError('857 recipe/resources must remain856')
        cache=PARENT/'build/incremental-release-cache';rows=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
        if len(rows)!=66:raise ValueError('856 cache set drift')
        for row in rows:
            digest,source,name=row.split('\t')
            if sha(cache/name)!=digest or sha(Path(source))!=digest:raise ValueError('857 changed a retained input '+name)
        proof.update(status='HTCLEO_FBS_ROM_RASTERIZER_ROM_OK',parent_package=PARENT.parent.name,parent_sha256=PARENT_SHA,
            image_sha256=sha(a.image),image_bytes=len(actual),changed_rom_bytes=sum(x!=y for x,y in zip(old,actual)),site=site,
            other_cached_binaries_unchanged=66,all_other_rom_bytes='exact856; only argument and derived checksum change',
            rom_window=0x03a00000,ram_start=0x15c00000,hardware_result='pending')
    if not a.report:raise ValueError('report required')
    a.report.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,sort_keys=True))
if __name__=='__main__':main()
