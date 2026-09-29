#!/usr/bin/env python3
"""850: exact single-object bitmap owner and inherited/native dispatch."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
EVID=HERE.parent/'output/iteration-evidence/850-gsapp-root-bitmap-background'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='12a7094cbae71193d9c0c6d05e48ff584991159462ec514b80d21cf0fc3b389c'
ADDED={'fbscli':[(26,0),(31,0),(108,0),(249,0),(250,0)]}

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:
        raise ValueError('850 standalone attribution drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    expected={m:Counter(v) for m,v in before.items()}
    for m,entries in ADDED.items():expected[m].update(entries)
    if expected!={m:Counter(v) for m,v in after.items()}:
        raise ValueError('850 delta exceeds five nativeFBS bitmap exports')
    return {'new_dlls':[],'added':ADDED,'policy':'owned1x1 Create/Begin/Address/End/constructor only'}

def verify_object(source,object_path,map_path,raw):
    return OWNER['verify_object'](source,object_path,map_path,raw,reviewed_contract=contract(),
        class_layout='private view adds8bytes total:849 witness plus owned bitmap pointer; native/public ABI unchanged')

verify_rom=OWNER['verify_rom']
