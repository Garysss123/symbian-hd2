#!/usr/bin/env python3
"""853: pinned one-object text witness and exact native font getter imports."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
EVID=HERE.parent/'output/iteration-evidence/853-gsapp-text-witness'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='0fc5e8302f804598fe3ad46f596e200bbd39477f58eb7cad9fc142ac4149ea24'
ADDED={'eikctl':[(469,0),(470,0),(471,0),(457,0)],'euser':[(1806,0)],
       'gdi':[(225,0),(311,0),(312,0),(314,0)]}

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:raise ValueError('853 contract drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    expected={m:Counter(v) for m,v in before.items()}
    for module,items in ADDED.items():expected.setdefault(module,Counter()).update(items)
    if expected!={m:Counter(v) for m,v in after.items()}:raise ValueError('853 import delta exceeds font/text getters')
    if set(after)-set(before)!={'gdi'}:raise ValueError('853 only new direct provider is existing ROM gdi')
    return {'added':ADDED,'new_direct_dll':'gdi (already ROM-resident)','policy':'font/text getters only'}

def verify_object(source,object_path,map_path,raw):
    c=contract();mmp=source.parent.parent/'GSApplication_htcleo.mmp'
    if hashlib.sha256(mmp.read_bytes()).hexdigest()!=c['mmp_sha256']:raise ValueError('853 MMP differs beyond gdi linkage')
    return OWNER['verify_object'](source,object_path,map_path,raw,reviewed_contract=c,
        class_layout='same850 private-view8-byte state; no new fields/public/native ABI change')

verify_rom=OWNER['verify_rom']
