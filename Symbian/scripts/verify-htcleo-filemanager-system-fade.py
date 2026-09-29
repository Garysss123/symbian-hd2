#!/usr/bin/env python3
"""895: FileManager zero-session system-fade setter, exact ABI and ROM closure."""
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
P=runpy.run_path(str(HERE/'apply-htcleo-filemanager-system-fade.py'))
X=runpy.run_path(str(HERE/'verify-htcleo-ecom-server-exception.py'))
E32,ROM,GS,FRONT=(X[k] for k in ('E32','ROM','GS','FRONT'))
PARENT=HERE.parent/'output/894-symbian3-full-filemanager-progress-frontier-incremental/Symbian3'
PARENT_SHA='74d75350457ab3c177c630757559ee95fe2a8959f92a92c8d7728986fd85cd69'
BASE_SHA='2a992a441b4a3511a5bad3fbc33cf81491b413c2fa83b7ea15df2088fb7119b9'
BINARY=SDK/'epoc32/release/armv5/urel/stem_avkon.dll'
OBJ=SDK/'epoc32/build/stem-avkon-build/c_481fcdd39640aeed/stem_avkon_dll/armv5/urel'
EVID=HERE.parent/'output/iteration-evidence/895-filemanager-system-fade'
DUMP='avkon-systemfade-895-full-dump.txt'
ADDED_IMPORTS={}
ABS=runpy.run_path(str(HERE/'verify-htcleo-avkon-common-geometry.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def state():
    objs={str(p):sha(p) for p in sorted(OBJ.glob('*.o'))}
    if len(objs)!=198:raise ValueError('Avkon object inventory')
    inputs=set()
    for p in OBJ.glob('*.o.d'):
        inputs.update(Path(s) for s in re.findall(r'/[^\s\\]+\.(?:cpp|h|hrh|mmh|inl)\b',p.read_text(),re.I) if Path(s).is_file())
    inputs.update((SDK/'sf/incubator/stemkit/breakdeps/avkon.mmp',
                   SDK/'sf/mw/classicui/uifw/AvKon/EABI/AVKONU.DEF',
                   HERE.parent/'config/avkon-gcce.xml',HERE/'htcleo-gcce-avkon-cc-wrapper.sh',HERE/'promote-htcleo-avkon-frozen-abi.py'))
    return dict(objects=objs,inputs={str(p):sha(p) for p in sorted(inputs)},binary_sha256=sha(BINARY))

CONTROL_PARENT=HERE.parent/'output/iteration-evidence/884-filemanager-aknenv'
PRIOR=HERE.parent/'output/iteration-evidence/894-filemanager-progress-frontier'
CONTROL_SHA='459969e26a4519c804a495896a01cb046374d2472af07be4c866a4d40b0c4dc9'
PRIOR_STANDALONE_SHA='69ad1db2b7079e299e8f1c572c98e5106c3dd795e17aee011ecdb9fa444a60c9'

def prior_control():
    if sha(CONTROL_PARENT/'CONTROL.json')!=CONTROL_SHA or sha(PRIOR/'STANDALONE.json')!=PRIOR_STANDALONE_SHA:raise ValueError('884 calibration drift')
    return json.loads((PRIOR/'STANDALONE.json').read_text())

def snapshot():
    if (EVID/'BASE.json').exists():raise ValueError('Never overwrite895 base')
    if sha(BINARY)!=BASE_SHA or sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('Not894 parent')
    text=(SDK/P['REL']/'aknsgcc.cpp').read_text(encoding='latin-1')
    if P['transform'](text,'aknsgcc.cpp',True)!=text:raise ValueError('snapshot requires894 source')
    prior=prior_control();now=state()
    if any(now[k]!=prior[k] for k in ('objects','inputs','binary_sha256')):raise ValueError('894 compiler objects/inputs drift')
    EVID.mkdir(parents=True,exist_ok=True)
    shutil.copy2(BINARY,EVID/'avkon-parent894.dll')
    (EVID/'BASE.json').write_text(json.dumps(now,indent=2)+'\n')
    dump=subprocess.check_output([str(SDK/'epoc32/tools/elf2e32'),'--dump=hseit','--e32input='+str(BINARY)],text=True)
    (EVID/'avkon-parent894-full-dump.txt').write_text(dump)
    shutil.copy2(OBJ/'stem_avkon{000a0000}.def',EVID/'avkon-parent894-exports.def')
    print('FM_SYSTEM_FADE_BASE=894 exact calibrated198 objects/inputs and frozen exports captured')

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
    if base['binary_sha256']!=BASE_SHA or sha(EVID/'avkon-parent894.dll')!=BASE_SHA:raise ValueError('baseline provenance')
    if set(now['objects'])!=set(base['objects']):raise ValueError('object set changed')
    changes=[p for p,v in now['objects'].items() if base['objects'][p]!=v]
    if [Path(p).name for p in changes]!=['aknsgcc.o']:raise ValueError('unexpected object changes '+repr(changes))
    expected={str(SDK/P['REL']/n) for n in P['BASE']}
    changed={p for p,v in base['inputs'].items() if now['inputs'].get(p)!=v}
    added=set(now['inputs'])-set(base['inputs'])
    if changed!=expected or added!={str(SDK/P['REL']/P['HELPER'])}:raise ValueError('unexpected source/input changes '+repr((changed,added)))
    for name in P['BASE']:
        text=(SDK/P['REL']/name).read_text(encoding='latin-1')
        if P['transform'](P['transform'](text,name,True),name)!=text:raise ValueError('source transform mismatch')
    asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/P['HELPER']
    if (SDK/P['REL']/P['HELPER']).read_bytes()!=asset.read_bytes():raise ValueError('compiled helper mismatch')
    helper_hashes={P['HELPER']:sha(asset)}
    old=(EVID/'avkon-parent894-full-dump.txt').read_text();new=(native/DUMP).read_text()
    if header(old)!=header(new):raise ValueError('ABI/export count/data/BSS changed')
    a=GS['imports'](old);b=GS['imports'](new)
    delta={k:list((Counter(b.get(k,[]))-Counter(a.get(k,[]))).elements()) for k in set(a)|set(b)}
    delta={k:sorted(v) for k,v in delta.items() if v}
    for k in a:
        if Counter(a[k])-Counter(b.get(k,[])):raise ValueError('old imports removed '+k)
    if delta!=ADDED_IMPORTS:raise ValueError('unreviewed import delta '+repr(delta))
    raw=E32['unpack_e32'](BINARY)
    if struct.unpack_from('<I',raw,52)[0]!=8 or struct.unpack_from('<I',raw,68)[0]!=40:raise ValueError('Avkon data/BSS drift')
    parent_raw=E32['unpack_e32'](EVID/'avkon-parent894.dll')
    dp=struct.unpack_from('<I',raw,104)[0];old_dp=struct.unpack_from('<I',parent_raw,104)[0]
    if raw[dp:dp+8]!=parent_raw[old_dp:old_dp+8] or relocations(raw,116)!=relocations(parent_raw,116):raise ValueError('existing initialized data changed')
    if (OBJ/'stem_avkon{000a0000}.def').read_bytes()!=(EVID/'avkon-parent894-exports.def').read_bytes():raise ValueError('4613 export table changed')
    prior_control() #Reuse the proven884 control, not a routine repeat rebuild.
    return dict(status='HTCLEO_FILEMANAGER_SYSTEM_FADE_OBJECTS_OK',**now,changed_objects=changes,header=header(new),imports_added=delta,helper_sha256=helper_hashes)

def verify_rom(a):
    proof=verify_objects(a.native)
    if sha(PARENT/'initrd.gz')!=PARENT_SHA:raise ValueError('894 ROM changed')
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
    if set(f0)!=set(f1):raise ValueError('ROM membership changed')
    for n in f0:
        if not n.startswith('sys\\bin\\') and ROM['file_data'](old,f0,n)!=ROM['file_data'](new,f1,n):raise ValueError('resource changed '+n)
    raw=E32['unpack_e32'](BINARY);w=lambda n:struct.unpack_from('<I',raw,n)[0]
    start=f1['sys\\bin\\avkon.dll'][0]
    code,size=struct.unpack_from('<I',new,start+0x14)[0],struct.unpack_from('<I',new,start+0x1c)[0]
    if code!=ROM['ROM_BASE']+start+120 or size!=w(48):raise ValueError('DLL code layout')
    ram=struct.unpack_from('<I',new,start+0x60)[0]
    old_start=f0['sys\\bin\\avkon.dll'][0]
    if ram!=struct.unpack_from('<I',old,old_start+0x60)[0] or struct.unpack_from('<I',new,start+0x28)[0]!=40:raise ValueError('Avkon private BSS layout moved')
    expected=bytearray(raw[w(100):w(100)+size]);sites,_,_=FRONT['parse_e32_import_sites'](raw)
    expected_data=bytearray(raw[w(104):w(104)+w(52)])
    def rebase(buffer,at,kind):
        value=struct.unpack_from('<I',buffer,at)[0]
        if kind==1 or (kind==3 and w(76)<=(value&~1)<=w(76)+size):delta=code-w(76)
        elif kind==2 or (kind==3 and w(80)<=value<=w(80)+w(52)+w(68)):delta=ram-w(80)
        else:raise ValueError('unexpected Avkon relocation '+hex(value))
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
    if holes!=ABS['absent_exports'](E32['unpack_e32'](EVID/'avkon-parent894.dll')):raise ValueError('absent exports changed')
    if bytes(expected)!=new[start+120:start+120+size]:raise ValueError('actual ROM DLL code mismatch')
    data=struct.unpack_from('<I',new,start+0x18)[0]-ROM['ROM_BASE']
    if struct.unpack_from('<I',new,start+0x24)[0]!=8 or data<0 or new[data:data+8]!=expected_data:raise ValueError('actual Avkon ROM initialized data mismatch')
    if (len(new)+1048575)//1048576*1048576!=0x03a00000:raise ValueError('ROM expansion forbidden')
    return dict(status='HTCLEO_FILEMANAGER_SYSTEM_FADE_ROM_OK',parent_package=PARENT.parent.name,parent_sha256=PARENT_SHA,
        image_sha256=sha(a.image),image_bytes=len(new),object_proof=proof,actual_code_exact=True,
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
