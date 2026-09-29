#!/usr/bin/env python3
"""849: preserve848 ABI/dispatch; attribute the bounded private Draw witness."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
OWNER=runpy.run_path(str(HERE/'verify-htcleo-gsapp-root-background-owner.py'))
EVID=HERE.parent/'output/iteration-evidence/849-gsapp-root-paint-witness'
CONTRACT=EVID/'STANDALONE-OBJECTS.json'
CONTRACT_SHA='744b66add15189b8551881b767402c4005fad18d5679756a8d5dcd591e80d1fc'

def contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest()!=CONTRACT_SHA:
        raise ValueError('849 standalone source/object attribution drift')
    return json.loads(CONTRACT.read_text())

def verify_imports(before,after):
    expected={m:Counter(v) for m,v in before.items()}
    # Mem::Copy of the live GC vtable word compiles to existing euser memmove.
    # Native euseru.def ordinal1954; no other new library/function allowed.
    expected['euser'].update([(1954,0)])
    if expected!={m:Counter(v) for m,v in after.items()}:
        raise ValueError('849 witness delta exceeds one euser1954 memmove')
    return {'new_dlls':[],'import_delta':{'euser':[[1954,0,1,'memmove']]},
            'policy':'848 imports plus one native4-byte GC vtable copy'}

def verify_object(source,object_path,map_path,raw):
    return OWNER['verify_object'](source,object_path,map_path,raw,reviewed_contract=contract(),
        class_layout='private view adds one4-byte witness; native public classes/box unchanged; ARM sizeof assertions')

verify_rom=OWNER['verify_rom']
