#!/usr/bin/env python3
"""858: pinned observer replacement, no new provider or app/class policy."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
CONTRACT=HERE.parent/'output/iteration-evidence/858-gsapp-font-server-lifetime/STANDALONE-OBJECTS.json'
CONTRACT_SHA='dc151870cc7a826b5ce67f7498fef64b0784e17b80ab6f667a31fad40e14943e'

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:raise ValueError('858 contract drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    c=contract();expected={m:Counter(v) for m,v in before.items()}
    if set(before)-set(after)!={'gdi'} or set(after)-set(before):raise ValueError('858 only retires direct gdi dependency')
    for m,delta in c['delta'].items():
        for ordinal,addend,count in delta['removed']:
            if expected[m][(ordinal,addend)]<count:raise ValueError('missing855 import to retire')
            expected[m][(ordinal,addend)]-=count
            if not expected[m][(ordinal,addend)]:del expected[m][(ordinal,addend)]
        for ordinal,addend,count in delta['added']:expected[m][(ordinal,addend)]+=count
    if expected.pop('gdi'):raise ValueError('gdi not fully retired')
    if expected!={m:Counter(v) for m,v in after.items()}:raise ValueError('858 import delta exceeds reviewed process getters')
    return {'new_rom_dlls':[],'removed_direct_providers':['gdi'],'delta':c['delta'],
        'policy':'existing euser process getters only; no process/thread mutation'}

def verify_object(source,object_path,map_path,raw):
    c=contract();mmp=source.parent.parent/'GSApplication_htcleo.mmp'
    if hashlib.sha256(mmp.read_bytes()).hexdigest()!=c['mmp_sha256']:raise ValueError('858 MMP drift')
    return OWNER['verify_object'](source,object_path,map_path,raw,reviewed_contract=c,
        class_layout='same private8 bytes/public classes; all new process handles are local observer state')
verify_rom=OWNER['verify_rom']
