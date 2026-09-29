#!/usr/bin/env python3
"""Reconstruct the current source-control candidate; actual825 E32 decides identity."""
import argparse
import hashlib
from pathlib import Path
import re
import runpy
HERE=Path(__file__).resolve().parent
SP=runpy.run_path(str(HERE/'apply-htcleo-sparse-fat-logs.py'))
REL=Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/HtcleoEcomLog.cpp')
BASE='57cd2385329094b0003346ead06bba7405047b35116d9eabb161c32d702b7df2'
UNLOAD_BASE='7eaff0e0357e5c0329e9d66c36ec901d90acefc673adceeae6352f8906d90808'

def normalize_unload(text):
    # The old generator accumulates empty lines at the exec-helper boundary.
    # Restore only a byte-exact known control source, never normalize code.
    if hashlib.sha256(text.encode('utf-8')).hexdigest()==UNLOAD_BASE:return text
    for m in re.finditer(r'\n{3,}',text):
        for count in range(2,len(m[0])):
            candidate=text[:m.start()]+'\n'*count+text[m.end():]
            if hashlib.sha256(candidate.encode('utf-8')).hexdigest()==UNLOAD_BASE:
                return candidate
    raise ValueError('UnloadPolicy drift is not the known blank-line-only generator drift')
def transform(text):
    base=SP['restore'](text)
    if hashlib.sha256(base.encode('latin-1')).hexdigest()!=BASE:raise ValueError('825 logger source drift')
    return base
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old)
    if old!=new:path.write_text(new,encoding='latin-1')
    unload=path.with_name('UnloadPolicy.cpp');old=unload.read_text();new=normalize_unload(old)
    if old!=new:unload.write_text(new)
    print('ECOM825_SOURCE_CONTROL=exact-control-logger-and-unload-source-no-runtime-policy-change')
if __name__=='__main__':main()
