#!/usr/bin/env python3
"""854: exact observer replacement and temporary-font ownership contract."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
EVID=HERE.parent/'output/iteration-evidence/854-gsapp-font-census'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='101844e4bb7d455c467127aa6f0536c7f1f8a2a09030111821ae66790e0423e2'

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:raise ValueError('854 contract drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    c=contract();expected={m:Counter(v) for m,v in before.items()}
    for m,delta in c['delta'].items():
        for ordinal,addend,count in delta['removed']:
            if expected[m][(ordinal,addend)]<count:raise ValueError('missing853 import to retire')
            expected[m][(ordinal,addend)]-=count
            if not expected[m][(ordinal,addend)]:del expected[m][(ordinal,addend)]
        for ordinal,addend,count in delta['added']:expected[m][(ordinal,addend)]+=count
    if expected!={m:Counter(v) for m,v in after.items()} or set(after)!=set(before):
        raise ValueError('854 imports beyond census/request replacement')
    return {'new_dlls':[],'delta':c['delta'],'policy':'same providers; bounded census/direct temporary font request'}

def verify_object(source,object_path,map_path,raw):
    c=contract();mmp=source.parent.parent/'GSApplication_htcleo.mmp'
    if hashlib.sha256(mmp.read_bytes()).hexdigest()!=c['mmp_sha256']:raise ValueError('854 unexpected MMP change')
    return OWNER['verify_object'](source,object_path,map_path,raw,reviewed_contract=c,
        class_layout='same850 private8-byte state and853 gdi linkage; no class field or public ABI changes')

verify_rom=OWNER['verify_rom']
