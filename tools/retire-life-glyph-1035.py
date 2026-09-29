#!/usr/bin/env python3
"""One exact historical E32 only. No ROM/SDK/card access or overwrite."""
import argparse
import hashlib
from pathlib import Path
import struct

ORIGINAL = '5e809535d9d02dd75c36cbbce33e671c13436f56a53e25d75c4c2b693a080f76'
RETIRED = '56133702ced1047ef44516c39ab31fe75e3daf8eb26d1856de907e505232a527'
SIZE = 15060
NOP = 0xE1A00000
GROUPS = ((336, 356, 360, 364), (396, 416, 420, 424),
          (456, 476, 480, 484), (528, 532, 536, 540), (596, 604, 612, 620))
WORDS = (3788120240, 3787989168, 3787923632, 3787858096)

def retire(original):
    if len(original) != SIZE or hashlib.sha256(original).hexdigest() != ORIGINAL:
        raise ValueError('Exact original1034 E32 required; re-audit any other build')
    candidate = bytearray(original)
    for group in GROUPS:
        for offset, word in zip(group, WORDS):
            if struct.unpack_from('<I', original, offset)[0] != word:
                raise ValueError('Original normal STRH mismatch')
            struct.pack_into('<I', candidate, offset, NOP)
    if hashlib.sha256(candidate).hexdigest() != RETIRED:
        raise ValueError('Whole-file output hash mismatch')
    return bytes(candidate)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    # Never open the input for writing; exclusive output creation also refuses in-place use.
    result = retire(args.original.read_bytes())
    with args.output.open('xb') as output:
        output.write(result)
    print(f'20 normal stores retired; {len(result)} bytes; SHA256 {RETIRED}')

if __name__ == '__main__':
    main()
