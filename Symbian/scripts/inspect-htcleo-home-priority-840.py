#!/usr/bin/env python3
"""Read-only attribution of the retained Xn Home handoff before an A/B decision."""
import hashlib
import json
from pathlib import Path
import runpy
import struct
import subprocess

HERE = Path(__file__).resolve().parent
SDK = Path('/root/symbian3-full')
PARENT = HERE.parent/'output/839-symbian3-full-home-kernel-watch-incremental/Symbian3'
PIN = 'b9fd5ebf7117d1b8c676d12a4f74ba55dd07b63a1f0bc9cc5fb2d6a7d4d53cb4'

def main():
    unpack = runpy.run_path(str(HERE/'verify-htcleo-viewsrv-source-control.py'))['unpack_e32']
    binary = PARENT/'build/incremental-release-cache/xn3layoutengine.dll'
    if hashlib.sha256(binary.read_bytes()).hexdigest() != PIN:
        raise ValueError('839 Xn identity mismatch')
    raw = unpack(binary)
    word = lambda o: struct.unpack_from('<I', raw, o)[0]
    code_offset, link = word(100), word(76)
    sym = SDK/'epoc32/release/armv5/urel/xn3layoutengine.dll.sym'
    # The instructions below contain both ComputeMode calls and the real ordinal call.
    expected = bytes.fromhex('404600212ff07aee4046391c00222ff0a0ec041c022140462ff070ee')
    pos = code_offset + 0x12f2a - link
    if raw[pos:pos+len(expected)] != expected:
        raise ValueError('retained743 handoff instruction block does not match839')
    dis = subprocess.check_output([
        '/root/gcce-native-4.4.1/bin/arm-none-symbianelf-objdump', '-d', '-C',
        '--start-address=0x12f20', '--stop-address=0x12f60', str(sym)], text=True)
    if 'RWsSession::ComputeMode' not in dis or 'SetWindowGroupOrdinalPosition' not in dis:
        raise ValueError('symbol call attribution unavailable')
    print(json.dumps(dict(binary_sha256=PIN, code_offset=code_offset, link=link,
        argument_link=0x12f3e, argument_rva=0x12f3e-link,
        argument_file_offset=code_offset+0x12f3e-link, parent_bytes=expected.hex()), indent=2))
    print(dis)

if __name__ == '__main__':
    main()
