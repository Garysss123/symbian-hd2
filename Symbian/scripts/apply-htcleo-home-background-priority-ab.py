#!/usr/bin/env python3
"""840 controlled A/B: retain Home's current priority after its real menu handoff.

This is an attributed one-byte E32 code overlay, NOT a source-built permanent
scheduler fix. The original743 source/control binary stays available. No IPC
completion, view event, priority number, timer, window ordinal or log is faked.
"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct

HERE = Path(__file__).resolve().parent
SDK = Path('/root/symbian3-full')
PARENT = HERE.parent/'output/839-symbian3-full-home-kernel-watch-incremental/Symbian3'
PARENT_SHA = '2c435f9eb3780b481a08f5f14bae1b9ef5859737d0ff58ecf21b28ff42f8c409'
BASE_BINARY = 'b9fd5ebf7117d1b8c676d12a4f74ba55dd07b63a1f0bc9cc5fb2d6a7d4d53cb4'
BINARY = SDK/'epoc32/release/armv5/urel/xn3layoutengine.dll'
LINK = 0x8000
ARG_LINK = 0x12f3e
ARG_RVA = ARG_LINK - LINK
BLOCK_LINK = 0x12f2a
BLOCK = bytes.fromhex('404600212ff07aee4046391c00222ff0a0ec041c022140462ff070ee')
POLICY = 'Home-only-handoff-ComputeOff2-to-Disabled0-retain-current-priority-one-byte-AB-not-global-fix'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unpack(path):
    return runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))['unpack_e32'](path)

def transform(raw):
    if len(raw) < 156 or raw[16:20] != b'EPOC':
        raise ValueError('not an E32 image')
    word = lambda offset: struct.unpack_from('<I', raw, offset)[0]
    if word(28) != 0 or word(76) != LINK or word(100) != 156:
        raise ValueError('unexpected compression/link/code offset')
    at = word(100) + ARG_RVA
    start = word(100) + BLOCK_LINK - LINK
    if raw[start:start+len(BLOCK)] != BLOCK:
        raise ValueError('839 handoff exact block drift or overlay already applied')
    if raw[at:at+2] != bytes.fromhex('0221'):
        raise ValueError('expected Thumb movs r1,#2')
    patched = bytearray(raw)
    patched[at] = 0  # Thumb movs r1,#0, EPriorityControlDisabled.
    return bytes(patched)

def base_raw():
    base = PARENT/'build/incremental-release-cache/xn3layoutengine.dll'
    if sha(base) != BASE_BINARY:
        raise ValueError('839 Xn immutable identity drift')
    return unpack(base)

def verify_binary(path=BINARY):
    raw = base_raw()
    actual = unpack(path)
    if actual != transform(raw):
        raise ValueError('child E32 is not exactly the declared one-byte overlay')
    return dict(status='HTCLEO_HOME_PRIORITY_AB_BINARY_OK', policy=POLICY,
        base_binary_sha256=BASE_BINARY, binary_sha256=sha(path),
        argument_link=ARG_LINK, argument_rva=ARG_RVA,
        raw_changed_offsets=[156+ARG_RVA], before='0221', after='0021',
        unchanged='all other decompressed E32 bytes including imports/exports/header/data/relocations')

def verify_rom(old, new, files0, files1):
    api = runpy.run_path(str(HERE/'verify-htcleo-matrix-pointer-frontier.py'))
    name = 'sys\\bin\\xn3layoutengine.dll'
    a, b, old_addr, old_size = api['rom_code_span'](old, files0, name)
    c, d, new_addr, new_size = api['rom_code_span'](new, files1, name)
    # The code layout/length is deliberately unchanged; no relocation excuse.
    if (a,b,old_addr,old_size) != (c,d,new_addr,new_size):
        raise ValueError('one-byte overlay unexpectedly moved the Xn ROM code')
    # rom_code_span begins at the120-byte TRomImageHeader, not at code.
    old_code_start, new_code_start = a+120, c+120
    code = bytearray(old[old_code_start:b])
    start = BLOCK_LINK-LINK
    if code[start:start+len(BLOCK)] != BLOCK:
        raise ValueError('839 actual ROM handoff bytes differ from the E32 attribution')
    code[ARG_RVA] = 0
    if bytes(code) != new[new_code_start:d]:
        bad=[(hex(i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(code,new[new_code_start:d])) if x!=y]
        raise ValueError('actual Xn ROM code differs beyond the sole ComputeMode argument '+repr(bad[:24]))
    proof = verify_binary()
    proof.update(rom_argument_address=new_addr+ARG_RVA, rom_code_size=new_size,
                 rom_changed_offsets=[new_code_start+ARG_RVA], same_rom_code_location=True)
    return proof

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    p.add_argument('--report', type=Path, required=True)
    a=p.parse_args()
    if a.apply:
        if BINARY.resolve() != Path('/root/symbian3-full/epoc32/release/armv5/urel/xn3layoutengine.dll'):
            raise ValueError('refuse non-release write')
        if sha(BINARY) != BASE_BINARY:
            raise ValueError('overlay requires exact promoted743/839 control; no stacking')
        # Decompression is a standard E32 container conversion; payload change
        # is exactly one byte. Keeping it uncompressed does not enlarge ROM code.
        BINARY.write_bytes(transform(base_raw()))
    proof=verify_binary()
    a.report.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))

if __name__ == '__main__':
    main()
