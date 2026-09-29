#!/usr/bin/env python3
"""824 host-only repair of GSFramework import-library identity, no DLL rebuild."""
import argparse
import hashlib
from pathlib import Path
import subprocess
SDK=Path('/root/symbian3-full')
DEF=SDK/'sf/mw/gsprofilesrv/gssettingsuis/Gs/EABI/GSFrameworkU.DEF'
DEFSHA='7ae491a2a98ab69f8f783c708dcf58bf97ca815ce9af1dc97a0afec5837ba4ff'
DLL=SDK/'epoc32/release/armv5/urel/gsframework.dll'
DLLSHA='4521bcec67615afffecb902868f4d3a356e87352d9feb20291c019ab8aac7b52'
DSO=SDK/'epoc32/release/armv5/lib/gsframework.dso'
NAME=b'gsframework{000a0000}[1020723f].dll'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    if sha(DEF)!=DEFSHA or sha(DLL)!=DLLSHA:raise ValueError('not pinned823 GSFramework DEF/DLL')
    before=sha(DLL)
    subprocess.run([str(SDK/'epoc32/tools/elf2e32'),'--definput='+str(DEF),'--dso='+str(DSO),
                    '--linkas='+NAME.decode()],check=True)
    raw=DSO.read_bytes()
    if raw.count(NAME)!=1 or b'{000a0000}{000a0000}' in raw or sha(DLL)!=before:
        raise ValueError('incorrect import identity or changed runtime DLL')
    a.report.write_text('STATUS=GSFRAMEWORK_IMPORT_IDENTITY_OK\nRUNTIME_DLL_UNCHANGED='+before+
        '\nFROZEN_DEF_SHA256='+DEFSHA+'\nDSO_SHA256='+sha(DSO)+
        '\nLINKAS='+NAME.decode()+'\nORDINALS=original123\n')
    print('GSFRAMEWORK_IMPORT_IDENTITY_OK original123 runtime-unchanged')
if __name__=='__main__':main()
