#!/usr/bin/env python3
"""848 helper: pin inherited-vtable imports and actual root factory/Draw slots."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

HERE=Path(__file__).resolve().parent
EVID=HERE.parent/'output/iteration-evidence/848-gsapp-root-background-owner'
CONTRACT=EVID/'IMPORT-CONTRACT.json'
CONTRACT_SHA='c72b33290540fc7e6a62f7cd1493410538303f6ed51e135457371d3fa4ba6480'
NAMES={
    'view_vtable':'_ZTV21CHtcleoGsRootListView',
    'view_draw':'_ZNK21CHtcleoGsRootListView4DrawEPK5TRect',
    'box_vtable':'_ZTV20CHtcleoGsRootListBox',
    'box_factory':'_ZN20CHtcleoGsRootListBox22MakeViewClassInstanceLEv',
}

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:
        raise ValueError('848 import/vtable attribution contract changed')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    c=contract();expected={m:Counter(v) for m,v in before.items()}
    if set(before)!=set(after):raise ValueError('848 must not introduce a DLL dependency')
    for module,delta in c['delta'].items():
        for ordinal,addend,count,_ in delta['removed']:
            key=(ordinal,addend)
            if expected[module][key]<count:raise ValueError('848 missing constructor predecessor')
            expected[module][key]-=count
            if not expected[module][key]:del expected[module][key]
        for ordinal,addend,count,_ in delta['added']:
            expected[module][(ordinal,addend)]+=count
    if expected!={m:Counter(v) for m,v in after.items()}:
        raise ValueError('848 import delta exceeds attributed inherited-vtable/native drawing contract')
    return {'contract_sha256':CONTRACT_SHA,'new_dlls':[],
            'constructor_change':'CAknSingleLargeStyleListBox C1 -> inherited C2',
            'delta':c['delta']}

def symbols(map_path):
    text=map_path.read_text();result={}
    for key,name in NAMES.items():
        hits=set(int(x,16) for x in re.findall(r'^\s*(0x[0-9a-fA-F]+)\s+'+re.escape(name)+r'\s*$',text,re.M))
        if len(hits)!=1:raise ValueError('848 private symbol attribution failed '+name)
        result[key]=hits.pop()
    return result

def relocation_section(text,name):
    match=re.search(r'RELOCATION RECORDS FOR \['+re.escape(name)+r'\]:\n(.*?)(?:\n\n|\Z)',text,re.S)
    if not match:raise ValueError('missing848 vtable relocation section '+name)
    return {int(at,16):symbol for at,symbol in re.findall(r'^([0-9a-fA-F]+)\s+R_ARM_ABS32\s+(\S+)',match.group(1),re.M)}

def verify_object(source,object_path,map_path,raw,*,reviewed_contract=None,class_layout=None):
    c=contract() if reviewed_contract is None else reviewed_contract
    if hashlib.sha256(source.read_bytes()).hexdigest()!=c['source_sha256']:
        raise ValueError('848 owner source no longer exact reviewed block')
    if hashlib.sha256(object_path.read_bytes()).hexdigest()!=c['object_sha256']:
        raise ValueError('848 compiled object differs from standalone reviewed attribution')
    rel=subprocess.check_output(['/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump','-r',str(object_path)],text=True)
    view=relocation_section(rel,'.rodata.'+NAMES['view_vtable'])
    box=relocation_section(rel,'.rodata.'+NAMES['box_vtable'])
    expected_view={0x4c:NAMES['view_draw'],0x20:'_ZN21CAknColumnListBoxView19CalcBottomItemIndexEv',
        0x64:'_ZNK12CListBoxView16XYPosToItemIndexE6TPointRi',0x6c:'_ZNK21CAknColumnListBoxView13DrawEmptyListERK5TRect'}
    expected_box={0xfc:NAMES['box_factory'],0x68:'_ZN27CAknSingleLargeStyleListBox19HandlePointerEventLERK13TPointerEvent',
        0x74:'_ZN27CAknSingleLargeStyleListBox11SizeChangedEv',0x11c:'_ZN17CAknColumnListBox12CreateModelLEv',
        0x118:'_ZN17CEikColumnListBox17CreateItemDrawerLEv'}
    for table,expected in ((view,expected_view),(box,expected_box)):
        for slot,name in expected.items():
            if table.get(slot)!=name:raise ValueError('848 native virtual dispatch drift '+name)
    s=symbols(map_path);link=struct.unpack_from('<I',raw,76)[0];offset=struct.unpack_from('<I',raw,100)[0]
    for table,slot,target in (('view_vtable',0x4c,'view_draw'),('box_vtable',0xfc,'box_factory')):
        if struct.unpack_from('<I',raw,offset+s[table]-link+slot)[0]!=(s[target]|1):
            raise ValueError('848 E32 factory/draw slot not installed')
    return {'symbols':s,'view_native_slots':expected_view,'box_native_slots':expected_box,
            'source_sha256':c['source_sha256'],'object_sha256':c['object_sha256'],
            'class_layout':class_layout or 'compile-time sizeof equals original native classes',
            'cleanup':'restore only0x1400 temporary bits on success/native leave; no error swallowing'}

def verify_rom(image,code_offset,code_address,proof):
    s=proof['symbols'];out={}
    for table,slot,target in (('view_vtable',0x4c,'view_draw'),('box_vtable',0xfc,'box_factory')):
        at=code_offset+s[table]-0x8000+slot;expected=(code_address+s[target]-0x8000)|1
        if struct.unpack_from('<I',image,at)[0]!=expected:
            raise ValueError('848 actual ROM virtual slot differs '+table)
        out[target]=hex(expected)
    return out
