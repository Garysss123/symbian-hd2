#!/usr/bin/env python3
"""855: exact font-load observer/ownership and existing-provider import delta."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
EVID=HERE.parent/'output/iteration-evidence/855-gsapp-font-load-boundary'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='a26d69e0381681e3fb5308a47a08fafb927e8f14a6dfd53a8b7a6d40496fdb52'

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:raise ValueError('855 contract drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    c=contract();expected={m:Counter(v) for m,v in before.items()}
    if set(after)-set(before)!={'ecom'} or set(before)-set(after):raise ValueError('855 only adds direct existing ECom provider')
    expected['ecom']=Counter()
    for m,delta in c['delta'].items():
        for ordinal,addend,count in delta['removed']:
            if expected[m][(ordinal,addend)]<count:raise ValueError('missing854 import to retire')
            expected[m][(ordinal,addend)]-=count
            if not expected[m][(ordinal,addend)]:del expected[m][(ordinal,addend)]
        for ordinal,addend,count in delta['added']:expected[m][(ordinal,addend)]+=count
    if expected!={m:Counter(v) for m,v in after.items()}:raise ValueError('855 imports beyond reviewed boundary observer')
    return {'new_direct_providers':['ecom'],'new_rom_dlls':[], 'delta':c['delta'],
        'policy':'ECom4 native ListImplementationsL; existing ROM provider unchanged; no new MMP library'}

def verify_object(source,object_path,map_path,raw):
    c=contract();mmp=source.parent.parent/'GSApplication_htcleo.mmp'
    if hashlib.sha256(mmp.read_bytes()).hexdigest()!=c['mmp_sha256']:raise ValueError('855 MMP changed')
    return OWNER['verify_object'](source,object_path,map_path,raw,reviewed_contract=c,
        class_layout='same850 private8 bytes/public classes; local observer state only; unchanged854 MMP')

verify_rom=OWNER['verify_rom']
