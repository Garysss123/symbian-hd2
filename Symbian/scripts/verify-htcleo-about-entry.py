#!/usr/bin/env python3
"""841: verify package-only About closure and the exact840 functional checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE=Path(__file__).resolve().parent
PREP=runpy.run_path(str(HERE/'prepare-htcleo-about-entry.py'))
ROM=runpy.run_path(str(HERE/'verify-htcleo-gate17-entry.py'))
FRONT=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
E32=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))

def digest(data): return hashlib.sha256(data).hexdigest()

def new_code_proof(item,image,files):
    raw=E32['unpack_e32'](Path(item['source']))
    w=lambda offset:struct.unpack_from('<I',raw,offset)[0]
    start,end,code,size=FRONT['rom_code_span'](image,files,item['destination'])
    if w(48)!=size or w(52) or w(68) or w(76)!=0x8000:
        raise ValueError('new About code/data contract changed '+item['destination'])
    expected=bytearray(raw[w(100):w(100)+size])
    sites,imports,_=FRONT['parse_e32_import_sites'](raw)
    # The unchanged Avkon provider legitimately contains private writable data.
    # Use the existing GS verifier, which checks actual code/RO export targets
    # without incorrectly requiring every provider to have zero data/BSS.
    provider_proof=GS['verify_providers'](image,files,imports)
    relocations=E32['code_relocations'](raw)
    for offset,kind in relocations.items():
        if offset+120 in sites: continue
        before=struct.unpack_from('<I',expected,offset)[0]
        # ARM exception descriptors legitimately carry a one-past-RO-end
        # limit (About offset0x60:0xA534). Relocate that exact section endpoint
        # too; this does not allow arbitrary addresses outside the segment.
        if kind==2 or not w(76)<=(before&~1)<=w(76)+size:
            raise ValueError('unexpected new-module relocation '+item['destination']+':'+hex(offset))
        struct.pack_into('<I',expected,offset,before+code-w(76))
    for offset,(module,ordinal,addend) in sites.items():
        provider_start=files['sys\\bin\\'+module+'.dll'][0]
        count,address=struct.unpack_from('<II',image,provider_start+0x3c)
        table=struct.unpack_from('<'+'I'*count,image,address-ROM['ROM_BASE'])
        if not 1<=ordinal<=len(table) or not table[ordinal-1]:
            raise ValueError('missing About import '+module+':'+str(ordinal))
        struct.pack_into('<I',expected,offset-120,table[ordinal-1]+addend)
    if bytes(expected)!=image[start+120:end]:
        raise ValueError('new About ROM code is not exact pinned E32 plus relocations '+item['destination'])
    return dict(destination=item['destination'],sha256=item['sha256'],code_bytes=size,
                relocations=len(relocations),import_sites=len(sites),providers=provider_proof)

def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--plan',type=Path,required=True);p.add_argument('--recipe',type=Path,required=True)
    p.add_argument('--image',type=Path,required=True);p.add_argument('--rom-log',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--config',type=Path);a=p.parse_args()
    plan=PREP['create_plan'](a.parent,a.config)
    if json.loads(a.plan.read_text())!=plan: raise ValueError('About pinned plan changed')
    parent_recipe=(a.parent/'build/htcleo_symbian3_full_native.oby').read_text()
    parent_mapping=PREP['ENTRY']['entries'](parent_recipe)
    if a.recipe.read_text()!=PREP['render_recipe'](parent_recipe,plan):
        raise ValueError('About recipe differs beyond declared append-only closure')
    cache=a.parent/'build/incremental-release-cache'
    lines=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines)!=65: raise ValueError('expected840 cache65')
    for line in lines:
        sha,source,name=line.split('\t')
        if PREP['sha'](Path(source))!=sha or PREP['sha'](cache/name)!=sha:
            raise ValueError('840 source binary changed '+name)
    old=(a.parent/'initrd.gz').read_bytes(); new=a.image.read_bytes()
    files0=ROM['rom_files'](old,(a.parent/'build/ROMBUILD.LOG').read_text(errors='replace'))
    files1=ROM['rom_files'](new,a.rom_log.read_text(errors='replace'))
    added={i['destination'] for i in plan['assets']+plan['binaries']+plan['layout_reserves']}
    if set(files1)!=set(files0)|added: raise ValueError('unexpected About ROM membership')
    spi='private\\10009d8f\\ecom-0-0.spi'; binaries=resources=0
    for name in files0:
        before=ROM['file_data'](old,files0,name); after=ROM['file_data'](new,files1,name)
        if name==spi:
            if not after.startswith(before): raise ValueError('existing ECom SPI prefix changed')
        elif name==plan['catalog_version']['destination']:
            if after!=bytes.fromhex(plan['catalog_version']['hex']): raise ValueError('About registration version mismatch')
            if not plan['catalog_version'].get('rescan',True) and after!=before:
                raise ValueError('no-global-rescan recovery changed840 software-version bytes')
        elif before!=after:
            diffs=[(hex(i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(before,after)) if x!=y]
            raise ValueError('840 ROM bytes changed outside About additions: '+name+
                             ' lengths='+repr((len(before),len(after)))+' changes='+repr(diffs[:24]))
        if name.startswith('sys\\bin\\'):
            # Preserve full code/data spans, not only the directory size.
            s0,s1=files0[name][0],files1[name][0]
            if s0!=s1: raise ValueError('841 must preserve existing executable address '+name)
            declared=parent_mapping.get(name)
            # Some LDD/DLLs are explicitly stored as data blobs, not XIP
            # TRomImageHeaders (e.g.pipelib.ldd). Their whole file was already
            # compared above; do not reinterpret compressed E32 bytes as VA.
            if declared and declared[1].lstrip().lower().startswith('data='):
                binaries+=1
                continue
            if struct.unpack_from('<I',old,s0+0x14)[0]!=ROM['ROM_BASE']+s0+120:
                raise ValueError('unexpected XIP header layout '+name)
            for addr_at,size_at in ((0x14,0x1c),(0x18,0x24)):
                address=struct.unpack_from('<I',old,s0+addr_at)[0]
                size=struct.unpack_from('<I',old,s0+size_at)[0]
                if size:
                    off=address-ROM['ROM_BASE']
                    if not 0<=off<=len(old)-size or old[off:off+size]!=new[off:off+size]:
                        bad=[hex(i) for i,(x,y) in enumerate(zip(old[off:off+size],new[off:off+size])) if x!=y]
                        raise ValueError('existing full code/data bytes changed '+name+' field='+hex(addr_at)+
                            ' address='+hex(address)+' size='+hex(size)+' differences='+repr(bad[:16]))
            binaries+=1
        else: resources+=1
    for item in plan['assets']:
        if digest(ROM['file_data'](new,files1,item['destination']))!=item['sha256']:
            raise ValueError('new About resource mismatch '+item['destination'])
    for reserve in plan['layout_reserves']:
        if files1[reserve['destination']]!=files0[reserve['original_destination']]:
            raise ValueError('old layout slot moved '+reserve['destination'])
        data=ROM['file_data'](new,files1,reserve['destination'])
        if len(data)!=reserve['bytes'] or digest(data)!=reserve['sha256']:
            raise ValueError('layout reservation is not exact840 data')
    spi_source=PREP['ENTRY']['entries'](a.recipe.read_text())[spi][0]
    _,spi_entries=ROM['SPI']['parse_spi'](spi_source)
    if len(spi_entries)!=143 or [x.name for x in spi_entries[-2:]]!=[Path(x).stem for x in plan['ecom_resources']]:
        raise ValueError('About143-entry ECom SPI order mismatch')
    if ROM['file_data'](new,files1,spi)!=spi_source.read_bytes(): raise ValueError('ROM SPI not actual verified archive')
    code_proofs=[new_code_proof(item,new,files1) for item in plan['binaries']]
    window=(len(new)+1048575)//1048576*1048576
    if window!=0x03a00000 or ROM['ROM_BASE']+window!=0x15c00000:
        raise ValueError('About must not expand840 ROM/RAM contract')
    # Existing Xn rawbyte and its source API contract must remain exactly840.
    about_ab=runpy.run_path(str(HERE/'apply-htcleo-home-background-priority-ab.py'))
    about_ab['verify_binary']()
    ab_control=None
    if not plan['catalog_version'].get('rescan',True):
        failed=HERE.parent/'output/841-symbian3-full-about-entry-incremental/Symbian3'
        failed_image=(failed/'initrd.gz').read_bytes()
        if digest(failed_image)!='d73b2c5e7d856172131c040790c9e05fa2b05f7286c41d44b722bf4cb6036992':
            raise ValueError('841 A/B reference identity changed')
        failed_files=ROM['rom_files'](failed_image,(failed/'build/ROMBUILD.LOG').read_text(errors='replace'))
        if set(failed_files)!=set(files1): raise ValueError('842 A/B changed841 membership')
        changed=[]
        for name in failed_files:
            if ROM['file_data'](failed_image,failed_files,name)!=ROM['file_data'](new,files1,name):
                changed.append(name)
        if changed!=['resource\\versions\\sw.txt']:
            raise ValueError('842 must differ from841 only in software-version logical file '+repr(changed))
        ab_control=dict(reference='immutable841',changed_logical_files=changed,
                        source_parent='immutable840',policy='remove-global-version-invalidation-only')
    report=dict(status='HTCLEO_ABOUT_ENTRY_OK',parent=plan['parent_package'],parent_sha256=plan['parent_sha256'],
        image_sha256=digest(new),image_bytes=len(new),rom_window=window,ram_start=ROM['ROM_BASE']+window,
        existing_cached_binaries=65,existing_rom_binaries=binaries,preserved_resources=resources,
        existing_rom_policy='byte-exact-all-existing-files-except-append-only-SPI-and-catalog-derived-sw-version',
        added_binary_proofs=code_proofs,added_assets=plan['assets'],layout_reserves=plan['layout_reserves'],spi_entries=143,
        product_info_changes=False,font_changes=False,catalog_version=plan['catalog_version'],
        regression_ab=ab_control,hardware_result='pending')
    a.report.write_text(json.dumps(report,indent=2)+'\n');print('HTCLEO_ABOUT_ENTRY_OK '+json.dumps(report,sort_keys=True))

if __name__=='__main__':main()
