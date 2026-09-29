#!/usr/bin/env python3
"""897: typed CAsyncCallBack late candidates; retain896 limits and functional code."""
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
P=runpy.run_path(str(HERE/'apply-htcleo-filemanager-async-frontier.py'))
X=runpy.run_path(str(HERE/'verify-htcleo-ecom-server-exception.py'))
E32,ROM,GS,FRONT=(X[k] for k in ('E32','ROM','GS','FRONT'))
PARENT=HERE.parent/'output/896-symbian3-full-filemanager-late-frontier-incremental/Symbian3'
PARENT_SHA='a314276678ee026d9c4cfba3f962b8a9d0abb61b75646fe27cbe7eaa04fd2dbf'
BASE_SHA='4a744c5e242771314db67d93625a4e54ed8a4873616dee59495e103016c3948c'
BINARY=SDK/'epoc32/release/armv5/urel/stem_cone.dll'
OBJ=SDK/'epoc32/build/stem-cone-build/c_9a864c9b64dadef0/stem_cone_dll/armv5/urel'
EVID=HERE.parent/'output/iteration-evidence/897-filemanager-async-frontier'
DUMP='cone-async-897-full-dump.txt'
# Parent already imports memset for its snapshot; no new imports are allowed.
ADDED_IMPORTS={}
ABS=runpy.run_path(str(HERE/'verify-htcleo-avkon-common-geometry.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verify_callback_tables(image, files):
    start=files['sys\\bin\\euser.dll'][0]
    count,address=struct.unpack_from('<II',image,start+0x3c)
    exports=struct.unpack_from('<'+'I'*count,image,address-ROM['ROM_BASE'])
    definitions=(SDK/'sf/os/kernelhwsrv/kernel/eka/eabi/euseru.def').read_text()
    expected_names={1936:'_ZTV5CIdle',1948:'_ZTV9CPeriodic',686:'_ZN5CIdleD1Ev',
                    685:'_ZN5CIdleD0Ev',680:'_ZN5CIdle4RunLEv',1385:'_ZN9CPeriodicD1Ev',
                    1384:'_ZN9CPeriodicD0Ev',1380:'_ZN9CPeriodic4RunLEv',
                    1931:'_ZTV14CAsyncCallBack',349:'_ZN14CAsyncCallBackD1Ev',348:'_ZN14CAsyncCallBackD0Ev'}
    for ordinal,name in expected_names.items():
        if not re.search(r'^\s*'+re.escape(name)+r'\s+@\s+'+str(ordinal)+r'\s',definitions,re.M):
            raise ValueError('EUSER frozen ordinal drift')
    ids=(HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/P['IDS']).read_text()
    result={}
    for name,table,ordinal,slots in (
        ('CIdle',0x1232d668,1936,{0:686,1:685,4:680}),
        ('Periodic',0x1232e140,1948,{0:1385,1:1384,4:1380}),
        ('Async',0x1232d6f8,1931,{0:349,1:348})):
        if exports[ordinal-1]+8!=table:raise ValueError('Same-ROM vtable address changed')
        if not re.search(r'KHTCLEOFm'+name+r'Vptr897\s*=\s*'+hex(table)+r'u;',ids):
            raise ValueError('Compiled candidate class identity differs')
        for slot,entry in slots.items():
            if struct.unpack_from('<I',image,table-ROM['ROM_BASE']+4*slot)[0]!=exports[entry-1]:
                raise ValueError('Same-ROM vtable class proof failed')
        result[name]=dict(vptr=table,vtable_export=ordinal,slots=slots)
        if name=='Async':
            runl=struct.unpack_from('<I',image,table-ROM['ROM_BASE']+16)[0]
            for delta,word in ((0,0xe5903020),(24,0xe5900024),(28,0xe12fff33)):
                if struct.unpack_from('<I',image,runl-ROM['ROM_BASE']+delta)[0]!=word:
                    raise ValueError('CAsyncCallBack member/RunL contract changed')
            result[name].update(runl=runl,callback_function_offset=32,callback_argument_offset=36)
    return result

def state():
    objs={str(p):sha(p) for p in sorted(OBJ.glob('*.o'))}
    if len(objs)!=23:raise ValueError('CONE object inventory')
    inputs=set()
    for p in OBJ.glob('*.o.d'):
        inputs.update(Path(s) for s in re.findall(r'/[^\s\\]+\.(?:cpp|h|hrh|mmh|inl)\b',p.read_text(),re.I) if Path(s).is_file())
    inputs.update((SDK/'sf/incubator/stemkit/breakdeps/CONE.MMP',
                   SDK/'sf/mw/classicui/lafagnosticuifoundation/cone/eabi/CONEU.DEF',
                   HERE.parent/'hd2/qsd8250-native-bsp/stem-cone-build/bld.inf'))
    return dict(objects=objs,inputs={str(p):sha(p) for p in sorted(inputs)},binary_sha256=sha(BINARY))

def dump():
    return subprocess.check_output([str(SDK/'epoc32/tools/elf2e32'),
        '--dump=hseit','--e32input='+str(BINARY)],text=True)

def snapshot():
    if (EVID/'BASE.json').exists():raise ValueError('Never overwrite897 base')
    if sha(BINARY)!=BASE_SHA or sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('Not896 parent')
    for name in P['BASE']:
        text=(SDK/P['REL']/name).read_text(encoding='latin-1')
        if P['transform'](text,name,True)!=text:raise ValueError('snapshot requires896 source')
    original=(PARENT/'initrd.gz').read_bytes()
    verify_callback_tables(original,ROM['rom_files'](original,(PARENT/'build/ROMBUILD.LOG').read_text(errors='replace')))
    now=state();prior=prior_control()
    if any(now[k]!=prior[k] for k in ('objects','inputs','binary_sha256')):raise ValueError('896 CONE provenance drift')
    EVID.mkdir(parents=True,exist_ok=True)
    shutil.copy2(BINARY,EVID/'cone-parent896.dll')
    (EVID/'BASE.json').write_text(json.dumps(now,indent=2)+'\n')
    (EVID/'cone-parent896-full-dump.txt').write_text(dump())
    shutil.copy2(OBJ/'stem_cone{000a0000}.def',EVID/'cone-parent896-exports.def')
    print('FM_ASYNC_BASE=896 calibrated source/23 objects/inputs/frozen exports captured')

PRIOR=HERE.parent/'output/iteration-evidence/896-filemanager-late-frontier'
CONTROL_PARENT=HERE.parent/'output/iteration-evidence/887-filemanager-fep-frontier'
PRIOR_SHA='a2ca793320abae8d88bd8e3b2acd11d049b5d04e277b01c4f80ba277d83b632d'
CONTROL_SHA='9dc09eea01345a45767169b5e1526612c47447410375017c9bb8bacda4f2dcc4'

def prior_control():
    if sha(PRIOR/'STANDALONE.json')!=PRIOR_SHA or sha(CONTROL_PARENT/'CONTROL.json')!=CONTROL_SHA:
        raise ValueError('887 calibration chain drift')
    return json.loads((PRIOR/'STANDALONE.json').read_text())

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
    if base['binary_sha256']!=BASE_SHA or sha(EVID/'cone-parent896.dll')!=BASE_SHA:raise ValueError('baseline provenance')
    if set(now['objects'])!=set(base['objects']):raise ValueError('object set changed')
    changes=[p for p,v in now['objects'].items() if base['objects'][p]!=v]
    if [Path(p).name for p in changes]!=['htcleoschedulertrace.o']:raise ValueError('unexpected object changes '+repr(changes))
    expected={str(SDK/P['REL']/n) for n in P['BASE']}
    changed={p for p,v in base['inputs'].items() if now['inputs'].get(p)!=v}
    added=set(now['inputs'])-set(base['inputs'])
    retired={str(SDK/P['REL']/n) for n in ('htcleofmlate896.inl','htcleofmcallback893_ids.h')}
    helpers={P['HELPER'],P['IDS']}
    if changed!=expected|retired or added!={str(SDK/P['REL']/n) for n in helpers}:raise ValueError('unexpected source/header changes '+repr((changed,added)))
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
        if 'HtcleoFmReady' not in asm:raise ValueError('ready candidate observer absent')
        for bad in ('RFile::Flush(', 'RFile::Replace(', 'RTimer::', 'User::After(', 'SetExceptionHandler', 'RunIfReady(', 'RequestComplete(', 'SetActive('):
            if bad in asm:raise ValueError('unexpected observer side effect '+bad)
    old=(EVID/'cone-parent896-full-dump.txt').read_text();new=(native/DUMP).read_text()
    if header(old)!=header(new):raise ValueError('ABI/export count/data/BSS changed')
    a=GS['imports'](old);b=GS['imports'](new)
    delta={k:list((Counter(b.get(k,[]))-Counter(a.get(k,[]))).elements()) for k in set(a)|set(b)}
    delta={k:sorted(v) for k,v in delta.items() if v}
    for k in a:
        if Counter(a[k])-Counter(b.get(k,[])):raise ValueError('old imports removed '+k)
    if delta!=ADDED_IMPORTS:raise ValueError('unreviewed import delta '+repr(delta))
    raw=E32['unpack_e32'](BINARY)
    if struct.unpack_from('<I',raw,52)[0]!=0 or struct.unpack_from('<I',raw,68)[0]!=0:raise ValueError('CONE data/BSS drift')
    parent_raw=E32['unpack_e32'](EVID/'cone-parent896.dll')
    if relocations(raw,116) or relocations(parent_raw,116):raise ValueError('unexpected CONE data relocation')
    if (OBJ/'stem_cone{000a0000}.def').read_bytes()!=(EVID/'cone-parent896-exports.def').read_bytes():raise ValueError('757 export table changed')
    prior_control()
    return dict(status='HTCLEO_FILEMANAGER_ASYNC_OBJECTS_OK',**now,changed_objects=changes,header=header(new),imports_added=delta,helper_sha256=helper_hashes)

def verify_rom(a):
    proof=verify_objects(a.native)
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('896 ROM changed')
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
    callback_class_proof=verify_callback_tables(new,f1)
    if set(f0)!=set(f1):raise ValueError('ROM membership changed')
    for n in f0:
        if not n.startswith('sys\\bin\\') and ROM['file_data'](old,f0,n)!=ROM['file_data'](new,f1,n):raise ValueError('resource changed '+n)
    raw=E32['unpack_e32'](BINARY);w=lambda n:struct.unpack_from('<I',raw,n)[0]
    start=f1['sys\\bin\\cone.dll'][0]
    code,size=struct.unpack_from('<I',new,start+0x14)[0],struct.unpack_from('<I',new,start+0x1c)[0]
    if code!=ROM['ROM_BASE']+start+120 or size!=w(48):raise ValueError('DLL code layout')
    ram=struct.unpack_from('<I',new,start+0x60)[0]
    old_start=f0['sys\\bin\\cone.dll'][0]
    if ram!=struct.unpack_from('<I',old,old_start+0x60)[0] or struct.unpack_from('<I',new,start+0x28)[0]!=0:raise ValueError('CONE private BSS layout moved')
    expected=bytearray(raw[w(100):w(100)+size]);sites,_,_=FRONT['parse_e32_import_sites'](raw)
    expected_data=bytearray(raw[w(104):w(104)+w(52)])
    def rebase(buffer,at,kind):
        value=struct.unpack_from('<I',buffer,at)[0]
        if kind==1 or (kind==3 and w(76)<=(value&~1)<=w(76)+size):delta=code-w(76)
        elif kind==2 or (kind==3 and w(80)<=value<=w(80)+w(52)+w(68)):delta=ram-w(80)
        else:raise ValueError('unexpected CONE relocation '+hex(value))
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
    if holes!=ABS['absent_exports'](E32['unpack_e32'](EVID/'cone-parent896.dll')):raise ValueError('absent exports changed')
    if bytes(expected)!=new[start+120:start+120+size]:raise ValueError('actual ROM DLL code mismatch')
    data=struct.unpack_from('<I',new,start+0x18)[0]-ROM['ROM_BASE']
    if struct.unpack_from('<I',new,start+0x24)[0]!=0 or expected_data:raise ValueError('actual CONE ROM initialized data mismatch')
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:raise ValueError('ROM expansion forbidden')
    return dict(status='HTCLEO_FILEMANAGER_ASYNC_ROM_OK',parent_package=PARENT.parent.name,parent_sha256=PARENT_SHA,
        image_sha256=sha(a.image),image_bytes=len(new),object_proof=proof,actual_code_exact=True,
        callback_class_proof=callback_class_proof,candidate_only=True,dispatch_observed=False,
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
