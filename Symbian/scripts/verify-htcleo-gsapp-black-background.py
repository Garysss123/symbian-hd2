#!/usr/bin/env python3
"""Pinned Settings appearance steps: palette, static flag, owned root window."""
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
PATCH=runpy.run_path(str(HERE/'apply-htcleo-gsapp-black-background.py'))
STATIC=runpy.run_path(str(HERE/'apply-htcleo-gsapp-static-background.py'))
ROOT_WINDOW=runpy.run_path(str(HERE/'apply-htcleo-gsapp-window-background.py'))
ROOT_SKIN=runpy.run_path(str(HERE/'apply-htcleo-gsapp-root-skin-background.py'))
OWNER=runpy.run_path(str(HERE/'apply-htcleo-gsapp-root-background-owner.py'))
OWNER_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
PAINT=runpy.run_path(str(HERE/'apply-htcleo-gsapp-root-paint-witness.py'))
PAINT_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-paint-witness.py'))
BITMAP=runpy.run_path(str(HERE/'apply-htcleo-gsapp-root-bitmap-background.py'))
BITMAP_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-bitmap-background.py'))
TEXT=runpy.run_path(str(HERE/'apply-htcleo-gsapp-text-witness.py'))
TEXT_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-text-witness.py'))
CENSUS=runpy.run_path(str(HERE/'apply-htcleo-gsapp-font-census.py'))
CENSUS_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-font-census.py'))
FONT_LOAD=runpy.run_path(str(HERE/'apply-htcleo-gsapp-font-load-boundary.py'))
FONT_LOAD_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-font-load-boundary.py'))
FONT_LIFE=runpy.run_path(str(HERE/'apply-htcleo-gsapp-font-server-lifetime.py'))
FONT_LIFE_VERIFY=runpy.run_path(str(HERE/'verify-htcleo-gsapp-font-server-lifetime.py'))
GS=runpy.run_path(str(HERE/'verify-htcleo-gsapp-observer.py'))
EX=runpy.run_path(str(HERE/'verify-htcleo-gsapp-exception-witness.py'))
ROM=runpy.run_path(str(HERE/'verify-htcleo-gate17-entry.py'))
FRONT=runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
E32=runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))
PARENT=HERE.parent/'output/842-symbian3-full-about-no-global-rescan-recovery/Symbian3'
PARENT_SHA='cf5f3f7f6d04f532e9bdac180aafa190328dacb5604a199235f55496f3239ca1'
PARENT_PROFILES={
    '843':('842-symbian3-full-about-no-global-rescan-recovery',PARENT_SHA,68),
    '844':('840-symbian3-full-home-background-priority-ab-incremental',
           'fe998b6beb289709b764fced9f0e1f01f3ad73c154c0ae21d40168024c6658dd',65),
    '845':('844-symbian3-full-gsapp-black-on840-incremental',
           'baa196d241c8dbb90b26d3cb01cf3725ca089fe618703f282785c902a0d695b0',65),
    '846':('845-symbian3-full-gsapp-static-background-incremental',
           '7408b5f66c7410f3a3fc1a05f932de83859254e0a2f4879a20926bafcb70a999',65),
    '847':('846-symbian3-full-gsapp-window-background-incremental',
           'db6c50cafdab4e1eb489c3d394c359a80b3e51b1f564335275d9670ad8039098',65),
    '848':('847-symbian3-full-gsapp-root-skin-background-incremental',
           '1ac3485b50adabfdfedb091c0bf3b278d65ede22e5299b2a7f09a18d7b9640fe',65),
    '849':('848-symbian3-full-gsapp-root-background-owner-incremental',
           'ed92825faaeb0fb456dba39e82df4e2435c9119a9f9926eb79d60c6f3a044bee',65),
    '850':('849-symbian3-full-gsapp-root-paint-witness-incremental',
           '0b7e4eeae2c4af6b092187617f044c9c4797eed56a243d6bc0204fe41ba12a17',65),
    '853':('852-symbian3-full-font-family-binding-incremental',
           '51ab0e8752d2323f4b1c39ce5bf62298441c0f86ca4b22b3912a5be081a84458',66),
    '854':('853-symbian3-full-gsapp-text-witness-incremental',
           '2e470b6c3cedcb3ae18492c29f6d621fb7b989ece8aa8933a29b5938f9379613',66),
    '855':('854-symbian3-full-gsapp-font-census-incremental',
           'b2de7b9e7d13dad6d1a80fb0b23280da2993503b605310fc9c85cceea835f7fa',66),
    '858':('857-symbian3-full-fbs-rom-rasterizer-incremental',
           'c6057efd4bda2dd9eb3d0e9c96e58638152152e818965518969e30ec474741fa',67),
}
PROFILE='843'
EXPECTED_CACHE=68
BINARY=SDK/'epoc32/release/armv5/urel/gsapp.exe'
# The original six-object baseline is shared: both840 and842 contain the same
# retained829 GSApp. Verify that certificate against the selected parent below;
# do not replace the old snapshot or claim843's failed hardware as validation.
EVID=HERE.parent/'output/iteration-evidence/843-gsapp-black-background'
DUMP='gsapp-black-843-full-dump.txt'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def select_profile(profile):
    global PARENT,PARENT_SHA,PROFILE,EXPECTED_CACHE,DUMP
    if profile not in PARENT_PROFILES:raise ValueError('unknown palette parent profile')
    package,PARENT_SHA,EXPECTED_CACHE=PARENT_PROFILES[profile]
    PARENT=HERE.parent/'output'/package/'Symbian3'
    PROFILE=profile;DUMP='gsapp-black-'+profile+'-full-dump.txt'
    if profile=='853':DUMP='gsapp-text-853-full-dump.txt'
    if profile=='854':DUMP='gsapp-census-854-full-dump.txt'
    if profile=='855':DUMP='gsapp-font-load-855-full-dump.txt'
    if profile=='858':DUMP='gsapp-font-server-858-full-dump.txt'

def verify_parent_baseline(base):
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('palette parent identity changed')
    prior_name='GSAPP-BLACK-OBJECTS.json' if PROFILE in ('845','846','847','848','849','850','853','854','855','858') else 'GSAPP-ASYNC-OBJECTS.json'
    prior=json.loads((PARENT/'build'/prior_name).read_text())
    expected_binary={
        '845':'2e7a0c8c55d6dba649a86fa8b593afe58c24d971de3f48a12f59cd577a19f668',
        '846':'582fe208dc618627eb905c38b6f41f4e12203b063dbfb52fec0aa63fefde5ac5',
        '847':'45ed1d0d03bc00c9d2073ca1ef7d755d9cbc074c95d59ba754cfcc58abcf7bca',
        '848':'cd02f85832d1a15c302bafd3622cb0dec5b80c20aacc9822b8fc8d0e2d378bb2',
        '849':'054320693a2b8f75e9b42685b4a1b694d6f2497b29c3d4ab21a80d56e67a8053',
        '850':'ae54c0d349ed923e1b9460898f6259bb3a4fc7ebe7361ef8e7840ebfc85d2b1d',
        '853':'2df4bb5586027e6be3317e49b078de81fdf1841d949d94301fff4e7c8c5b215f',
        '854':'e44aafc17bc63b9f436ecd0f9835fdfc857eeb09434290d02519e62e6b884ca9',
        '855':'765e9368014533c46355447887f974e959ae64f0a2810111591122b256f13a3b',
        '858':'ff342b041db390b31ba4c74f6625790c153adf8bbe0f8b1703c5adfff137f302',
    }.get(PROFILE,PATCH['BASE_BINARY'])
    if base['binary_sha256']!=expected_binary or base['objects']!=prior['objects']:
        raise ValueError('shared GS baseline is not the selected parent certificate')
    rows=[line.split('\t') for line in
          (PARENT/'build/incremental-release-cache/RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()]
    match=[row for row in rows if row[1]==str(BINARY)]
    if len(match)!=1 or match[0][0]!=expected_binary or sha(PARENT/'build/incremental-release-cache'/match[0][2])!=expected_binary:
        raise ValueError('selected parent GSApp is not the shared baseline binary')

def verify_static_flag_delta(before,after):
    # 844 linked CGSUi::ConstructL=0x8f1c. Its arg sequence is movs r1,#0x94;
    # mov r0,r4; lsls r1,#17. GCCE845 changes only the two immediates:
    # movs r1,#0xca; mov r0,r4; lsls r1,#18. XOR flags =0x02000000.
    code_offset=struct.unpack_from('<I',before,100)[0]
    if struct.unpack_from('<I',before,76)[0]!=0x8000 or len(before)!=len(after):
        raise ValueError('static flag changed E32 link/shape')
    site=code_offset+0xf3e
    if before[site:site+6]!=bytes.fromhex('9421201c4904'):
        raise ValueError('844 BaseConstructL argument instructions drift')
    expected=bytearray(before);expected[site]=0xca;expected[site+4]=0x89
    expected[20:24]=after[20:24] # header CRC, checked by E32 loading
    expected[36:44]=after[36:44] # normal compiler/link timestamp
    if bytes(expected)!=after:raise ValueError('845 differs beyond native background flag and header timestamp/CRC')
    if ((0x94<<17)^(0xca<<18))!=0x02000000:raise ValueError('wrong background flag mask')
    return dict(before_flags='01280000',after_flags='03280000',xor_mask='02000000',
                source_flag='EAknDisableAnimationBackground',code_changed_rvas=[0xf3e,0xf42])

def source_hashes():
    return {p.name:sha(p) for p in sorted((SDK/PATCH['REL']/'Src').glob('*.cpp'))}

def verify_imports(before,after):
    expected={n:Counter(v) for n,v in before.items()}
    expected['egul'].update([(4,0),(184,0)]) # native EGUL_DATACAGEDU.DEF SetColor/Count
    if expected!={n:Counter(v) for n,v in after.items()}:
        delta={n:dict(added=list((Counter(after.get(n,[]))-Counter(before.get(n,[]))).elements()),
                      removed=list((Counter(before.get(n,[]))-Counter(after.get(n,[]))).elements()))
               for n in set(before)|set(after) if Counter(before.get(n,[]))!=Counter(after.get(n,[]))}
        raise ValueError('palette import delta beyond Count/SetColor '+repr(delta))

WINDOW_IMPORTS={'cone':[(279,0)],'egul':[(122,0)],'eikcoctl':[(1225,0)],'ws32':[(269,0)]}
SKIN_IMPORTS={'eikctl':[(198,0),(476,0)]}

def verify_window_imports(before,after):
    expected={m:Counter(v) for m,v in before.items()}
    for module,entries in WINDOW_IMPORTS.items():expected[module].update(entries)
    if expected!={m:Counter(v) for m,v in after.items()}:
        raise ValueError('root-window import delta beyond Window/SetBackgroundColor/Color/View.BackColor')

def verify_skin_imports(before,after):
    expected={m:Counter(v) for m,v in before.items()}
    expected['eikctl'].update(SKIN_IMPORTS['eikctl'])
    if expected!={m:Counter(v) for m,v in after.items()}:
        raise ValueError('root-list skin delta beyond SetSkinEnabledL/SkinBackgroundContext')

def snapshot(path):
    if path.exists():raise ValueError('never overwrite palette baseline')
    if sha(PARENT/'initrd.gz')!=PARENT_SHA or sha(BINARY)!=PATCH['BASE_BINARY']:
        raise ValueError('not exact842 predecessor')
    source=SDK/PATCH['REL']/PATCH['NAME']
    if sha(source)!=PATCH['BASE_SOURCE']:raise ValueError('unexpected GSUi source')
    prior=json.loads((PARENT/'build/GSAPP-ASYNC-OBJECTS.json').read_text())
    objects=EX['objects']()
    if objects!=prior['objects']:raise ValueError('GS object provenance no longer matches retained829')
    headers={p.name:sha(p) for p in sorted((SDK/PATCH['REL']/'Inc').glob('*.h'))}
    path.write_text(json.dumps(dict(binary_sha256=sha(BINARY),objects=objects,sources=source_hashes(),
                                   headers=headers),indent=2)+'\n')
    print('GS_BLACK_BASELINE_OK six objects and842binary pinned')

def verify_objects(native):
    baseline=EVID/'BASE-OBJECTS.json';base=json.loads(baseline.read_text());now=EX['objects']()
    if PROFILE in ('845','846','847','848','849','850','853','854','855','858'):
        original_headers=base['headers']
        baseline=PARENT/'build/GSAPP-BLACK-OBJECTS.json'
        base=json.loads(baseline.read_text());base['headers']=original_headers
    verify_parent_baseline(base)
    changed=[p for p in now if now[p]!=base['objects'][p]]
    expected_object='GSMainContainer.o' if PROFILE in ('846','847','848','849','850','853','854','855','858') else 'GSUi.o'
    if len(changed)!=1 or Path(changed[0]).name!=expected_object:raise ValueError('unexpected GS object change '+repr(changed))
    sources=source_hashes()
    expected_source='GSMainContainer.cpp' if PROFILE in ('846','847','848','849','850','853','854','855','858') else 'GSUi.cpp'
    if [n for n in sources if sources[n]!=base['sources'][n]]!=[expected_source]:
        raise ValueError('unexpected GS source change')
    headers={p.name:sha(p) for p in sorted((SDK/PATCH['REL']/'Inc').glob('*.h'))}
    if headers!=base['headers']:raise ValueError('GS class headers changed')
    text=(SDK/PATCH['REL']/PATCH['NAME']).read_text(encoding='latin-1')
    flag_proof=None
    if PROFILE in ('845','846','847','848','849','850','853','854','855','858'):
        if STATIC['transform'](text)!=text:raise ValueError('native static background source drift')
        text=STATIC['transform'](text,True)
    if PATCH['transform'](text)!=text:raise ValueError('palette source drift')
    if PROFILE in ('846','847','848','849','850','853','854','855','858'):
        root_text=(SDK/ROOT_WINDOW['REL']).read_text(encoding='latin-1')
        if PROFILE=='858':
            if FONT_LIFE['transform'](root_text)!=root_text:raise ValueError('858 observer source drift')
            root_text=FONT_LIFE['transform'](root_text,True)
        if PROFILE in ('855','858'):
            if FONT_LOAD['transform'](root_text)!=root_text:raise ValueError('855 font load source drift')
            root_text=FONT_LOAD['transform'](root_text,True)
        if PROFILE in ('854','855','858'):
            if CENSUS['transform'](root_text)!=root_text:raise ValueError('854 font census source drift')
            root_text=CENSUS['transform'](root_text,True)
        if PROFILE in ('853','854','855','858'):
            if TEXT['transform'](root_text)!=root_text:raise ValueError('853 text witness source drift')
            root_text=TEXT['transform'](root_text,True)
        if PROFILE in ('850','853','854','855','858'):
            if BITMAP['transform'](root_text)!=root_text:raise ValueError('root bitmap source drift')
            root_text=BITMAP['transform'](root_text,True)
        if PROFILE in ('849','850','853','854','855','858'):
            if PAINT['transform'](root_text)!=root_text:raise ValueError('root paint witness source drift')
            root_text=PAINT['transform'](root_text,True)
        if PROFILE in ('848','849','850','853','854','855','858'):
            if OWNER['transform'](root_text)!=root_text:raise ValueError('root background owner source drift')
            root_text=OWNER['transform'](root_text,True)
        if PROFILE in ('847','848','849','850','853','854','855','858'):
            if ROOT_SKIN['transform'](root_text)!=root_text:raise ValueError('root-list skin source drift')
            root_text=ROOT_SKIN['transform'](root_text,True)
        if ROOT_WINDOW['transform'](root_text)!=root_text:raise ValueError('root window source drift')
        flag_proof={'retained_from':'845','flags':'03280000','gsui_object_unchanged':True}
    before=(PARENT/'build/gsapp-e32-dump.txt').read_text();after=(native/DUMP).read_text()
    if GS['header_contract'](before)!=GS['header_contract'](after):raise ValueError('GS ABI/security/heap/stack drift')
    for dump in (before,after):
        if not re.search(r'^Data Size:\s*00000000\s*$',dump,re.M) or not re.search(r'^Bss\s+000014\s*$',dump,re.M):
            raise ValueError('GS Data0/BSS20 changed')
    owner_import_proof=None;owner_proof=None
    if PROFILE=='858':
        owner_import_proof=FONT_LIFE_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=FONT_LIFE_VERIFY['verify_object'](SDK/FONT_LIFE['REL']/FONT_LIFE['NAME'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='855':
        owner_import_proof=FONT_LOAD_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=FONT_LOAD_VERIFY['verify_object'](SDK/FONT_LOAD['REL']/FONT_LOAD['NAME'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='854':
        owner_import_proof=CENSUS_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=CENSUS_VERIFY['verify_object'](SDK/CENSUS['REL']/CENSUS['NAME'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='853':
        owner_import_proof=TEXT_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=TEXT_VERIFY['verify_object'](SDK/TEXT['REL']/TEXT['NAME'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='850':
        owner_import_proof=BITMAP_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=BITMAP_VERIFY['verify_object'](SDK/BITMAP['REL'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='849':
        owner_import_proof=PAINT_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=PAINT_VERIFY['verify_object'](SDK/PAINT['REL'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='848':
        owner_import_proof=OWNER_VERIFY['verify_imports'](GS['imports'](before),GS['imports'](after))
        owner_proof=OWNER_VERIFY['verify_object'](SDK/OWNER['REL'],Path(changed[0]),Path(str(BINARY)+'.map'),E32['unpack_e32'](BINARY))
    elif PROFILE=='847':
        verify_skin_imports(GS['imports'](before),GS['imports'](after))
    elif PROFILE=='846':
        verify_window_imports(GS['imports'](before),GS['imports'](after))
    elif PROFILE=='845':
        if GS['imports'](before)!=GS['imports'](after):raise ValueError('native flag must add no imports')
        flag_proof=verify_static_flag_delta(E32['unpack_e32'](PARENT/'build/incremental-release-cache/gsapp.exe'),E32['unpack_e32'](BINARY))
    else:verify_imports(GS['imports'](before),GS['imports'](after))
    dis=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-drC',changed[0]],text=True)
    if PROFILE in ('846','847','848','849','850','853','854','855','858'):
        expected_calls=['RWindow::SetBackgroundColor(TRgb)','CColorList::Count() const',
                        'CColorList::Color(TLogicalColor) const','CListBoxView::BackColor() const']
        if PROFILE in ('847','848','849','850','853','854','855','858'):expected_calls+=['CColumnListBoxData::SetSkinEnabledL(int)','CColumnListBoxData::SkinBackgroundContext() const']
        for name in expected_calls:
            count=2 if PROFILE in ('848','849','850','853','854','855','858') and name=='CListBoxView::BackColor() const' else 1
            if len(re.findall(r'R_ARM_\S+\s+'+re.escape(name),dis))!=count:
                raise ValueError('root constructor must call exactly once '+name)
    else:
        if len(re.findall(r'R_ARM_\S+\s+CColorList::SetColor\(TLogicalColor, TRgb\)',dis))!=4:
            raise ValueError('expected four private SetColor calls')
        if len(re.findall(r'R_ARM_\S+\s+CColorList::Count\(\) const',dis))!=1:
            raise ValueError('expected one palette bound check')
    if 'UpdateSystemColorList' in dis:raise ValueError('global system palette write forbidden')
    return dict(status='HTCLEO_GS_BLACK_OBJECTS_OK',profile=PROFILE,parent_package=PARENT.parent.name,
        binary_sha256=sha(BINARY),base_binary_sha256=base['binary_sha256'],
        baseline_sha256=sha(baseline),objects=now,sources=sources,changed_objects=changed,
        data=0,bss=20,new_imports=owner_import_proof if PROFILE in ('848','849','850','853','854','855','858') else (SKIN_IMPORTS if PROFILE=='847' else (WINDOW_IMPORTS if PROFILE=='846' else ({} if PROFILE=='845' else {'egul':[[4,0],[184,0]]}))),exception_wrapper=EX['verify_wrapper'](),
        static_background=flag_proof,
        background_owner=owner_proof,
        policy={
            '858':'first-root-held-ECom-process-exit-before-after-same-font-query13',
            '855':'first-root-font-load-boundary19-owned-temporary-FBS-file-reference',
            '854':'first-root-font-census32-temporary-explicit-family-request-and-release',
            '853':'first-root-native-draw-return-text-font-glyph-read-only-witness14',
            '850':'root-owned1x1-black-bitmap-native-foreground-allocation-error-fallback',
            '849':'root-first-paint-witness-max7-per-view-retain848-behavior',
            '848':'private-root-view-single-background-fill-native-foreground-mask-cleanup',
            '847':'root-list-skin-background-disabled-three-init-reads-no-global-or-child-change',
            '846':'owned-root-window-black-two-init-colour-reads-no-child-or-chrome-change',
            '845':'native-static-background-flag-only-on844-palette',
        }.get(PROFILE,'GS-private-palette-only-no-global-storage-no-new-log-no-geometry-or-input-change'))

def verify_rom(a):
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('palette parent identity changed')
    if a.recipe.read_text()!=(PARENT/'build/htcleo_symbian3_full_native.oby').read_text():
        raise ValueError('black background must not change any recipe/resource')
    cache=PARENT/'build/incremental-release-cache';lines=(cache/'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines)!=EXPECTED_CACHE:raise ValueError('unexpected selected parent cache count')
    for line in lines:
        oldhash,source,name=line.split('\t')
        if sha(cache/name)!=oldhash:raise ValueError('parent cache corruption')
        if source!=str(BINARY) and sha(Path(source))!=oldhash:raise ValueError('unexpected binary changed '+name)
    proof=verify_objects(a.native)
    old=(PARENT/'initrd.gz').read_bytes();new=a.image.read_bytes()
    files0=ROM['rom_files'](old,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace'))
    files1=ROM['rom_files'](new,a.rom_log.read_text(errors='replace'))
    if set(files0)!=set(files1):raise ValueError('black palette changed ROM membership')
    if PROFILE in ('844','845','846','847','848','849','850','853','854','855','858') and any('sys\\bin\\'+name in files1 for name in
        ('about.exe','aboutgsplugin.dll','gsdevicemanagementplugin.dll')):
        raise ValueError('844 must not carry the withdrawn About startup additions')
    for name in files0:
        if not name.startswith('sys\\bin\\') and ROM['file_data'](old,files0,name)!=ROM['file_data'](new,files1,name):
            raise ValueError('black palette changed resource '+name)
    table=GS['imports']((a.native/DUMP).read_text())
    providers=GS['verify_providers'](new,files1,table)
    # Reconstruct the actual GS code from its pinned new E32 and declared
    # code/data relocations/imports; BSS20 has the original private RAM base.
    raw=E32['unpack_e32'](BINARY);w=lambda o:struct.unpack_from('<I',raw,o)[0]
    start,end,code,size=FRONT['rom_code_span'](new,files1,'sys\\bin\\gsapp.exe')
    if size!=w(48) or w(52)!=0 or w(68)!=20:raise ValueError('unexpected GS ROM shape')
    expected=bytearray(raw[w(100):w(100)+size]);ram=struct.unpack_from('<I',new,start+0x60)[0]
    sites,_,_=FRONT['parse_e32_import_sites'](raw)
    for offset,kind in E32['code_relocations'](raw).items():
        if offset+120 in sites:continue
        value=struct.unpack_from('<I',expected,offset)[0]
        if kind!=2 and w(76)<=(value&~1)<=w(76)+size: target=value+code-w(76)
        elif kind!=1 and w(80)<=value<=w(80)+w(68):target=value+ram-w(80)
        else:raise ValueError('unattributed GS relocation '+hex(offset))
        struct.pack_into('<I',expected,offset,target)
    for offset,(module,ordinal,addend) in sites.items():
        p=files1['sys\\bin\\'+module+'.dll'][0];count,address=struct.unpack_from('<II',new,p+0x3c)
        exports=struct.unpack_from('<'+'I'*count,new,address-ROM['ROM_BASE'])
        struct.pack_into('<I',expected,offset-120,exports[ordinal-1]+addend)
    if bytes(expected)!=new[start+120:end]:raise ValueError('GS ROM differs beyond declared linker fixups')
    if PROFILE in ('848','849','850','853','854','855','858'):
        proof['background_owner']['rom_virtual_targets']=OWNER_VERIFY['verify_rom'](new,start+120,code,proof['background_owner'])
    if PROFILE=='845':
        a,b,parent_code,parent_size=FRONT['rom_code_span'](old,files0,'sys\\bin\\gsapp.exe')
        if (a,b,parent_code,parent_size)!=(start,end,code,size):raise ValueError('static flag moved GS ROM code')
        expected_parent=bytearray(old[a+120:b]);expected_parent[0xf3e]=0xca;expected_parent[0xf42]=0x89
        if bytes(expected_parent)!=new[start+120:end]:raise ValueError('ROM delta beyond two background-flag bytes')
        proof['static_background']['rom_changed_addresses']=[code+0xf3e,code+0xf42]
    window=(len(new)+1048575)//1048576*1048576
    if window!=0x03a00000:raise ValueError('no ROM expansion for palette')
    return dict(status='HTCLEO_GS_BLACK_ROM_OK',profile=PROFILE,parent_package=PARENT.parent.name,
                parent_sha256=PARENT_SHA,image_sha256=hashlib.sha256(new).hexdigest(),
                unchanged_cached_binaries=EXPECTED_CACHE-1,resources_unchanged=True,membership_unchanged=True,
                rom_window=window,ram_start=ROM['ROM_BASE']+window,code_bytes=size,providers=providers,
                object_proof=proof,hardware_result='pending')

def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',action='store_true');p.add_argument('--native',type=Path,required=True)
    p.add_argument('--profile',choices=tuple(PARENT_PROFILES),default='843')
    p.add_argument('--image',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--rom-log',type=Path)
    p.add_argument('--report',type=Path);a=p.parse_args()
    select_profile(a.profile)
    if a.snapshot:
        if PROFILE!='843':raise ValueError('844 reuses the checked retained829 baseline; no new snapshot')
        snapshot(EVID/'BASE-OBJECTS.json');return
    result=verify_rom(a) if a.image else verify_objects(a.native)
    if not a.report:raise ValueError('report required')
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
