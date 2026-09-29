#!/usr/bin/env python3
"""Prove reconstructed ECom control equals825 except E32 timestamp/header CRC."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'output/825-symbian3-full-gsapp-ecom-notify-guard-incremental/Symbian3/build/incremental-release-cache/ecom.dll'
EXPECTED='d2eaf4828f00355d746deb4bb1900cb8a10ae3dcc7776f7d7eba21e01d3e3cd3'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def decode(path):
    with tempfile.TemporaryDirectory(prefix='ecom825-control-') as d:
        p=Path(d)/'copy.e32';shutil.copyfile(path,p)
        if struct.unpack_from('<I',p.read_bytes(),28)[0]:
            subprocess.run(['/root/symbian3-full/epoc32/tools/petran','-nocompress',str(p)],
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
        return p.read_bytes()
def compare(before,after):
    if len(before)!=len(after):
        co0,co1=struct.unpack_from('<I',before,100)[0],struct.unpack_from('<I',after,100)[0]
        cs0,cs1=struct.unpack_from('<I',before,48)[0],struct.unpack_from('<I',after,48)[0]
        edits=difflib.SequenceMatcher(None,before[co0:co0+cs0],after[co1:co1+cs1],autojunk=False).get_opcodes()
        print('LARGE_CODE_EDITS',[(tag,hex(i+0x8000),j-i,hex(k+0x8000),l-k) for tag,i,j,k,l in edits if tag!='equal' and (j-i>8 or l-k>8)])
        diffs=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b and i>=156]
        details=[(hex(i),before[max(0,i-8):i+12].hex(),after[max(0,i-8):i+12].hex()) for i in diffs[:12]]
        raise ValueError('ECom control size drift '+str((len(before),len(after),details)))
    if before[16:20]!=b'EPOC' or after[16:20]!=b'EPOC':raise ValueError('Not E32')
    # Header CRC covers the timestamp. Never mask code, data, imports or relocations.
    allowed=set(range(20,24))|set(range(36,44))
    differences=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b and i not in allowed]
    if differences:raise ValueError('ECom control non-metadata differences '+repr(differences[:48]))
    return dict(equal_except_header_crc_and_timestamp=True,decoded_bytes=len(before),
                excluded_offsets=[20,21,22,23,36,37,38,39,40,41,42,43])
def main():
    p=argparse.ArgumentParser();p.add_argument('control',type=Path)
    p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    if sha(PARENT)!=EXPECTED:raise ValueError('Immutable825 ECom hash mismatch')
    result=compare(decode(PARENT),decode(a.control))
    result.update(status='ECOM825_SOURCE_CONTROL_OK',parent_sha256=sha(PARENT),
                  control_sha256=sha(a.control),no_code_data_import_export_or_relocation_exclusions=True)
    a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
