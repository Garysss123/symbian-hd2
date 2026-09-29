#!/usr/bin/env python3
"""803 on801 recovery base: direct finite window-name enumeration, no WServ edit."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil

HERE=Path(__file__).resolve().parent
LOOKUP=runpy.run_path(str(HERE/'apply-htcleo-menu-task-lookup-control.py'))
REL=LOOKUP['REL']
NAME='handlersrc/menutasklist.cpp'
BASE_SHA='38c7a260769de3e3dbaa1bd62a1dcd7f692546716bc1d64fd5fd701065b7e247'
OLD=LOOKUP['NEW_LOOKUP']
NEW='#include "htcleomenutaskenumeration.inl"\n'

def transform(text,restore=False):
    if NEW in text:
        text=LOOKUP['once'](text,NEW,OLD)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:
        if restore and OLD not in text and NEW not in text:
            LOOKUP['transform'](text,NAME,True)
            return text
        raise ValueError('enumeration requires exact801 task-list source')
    return text if restore else LOOKUP['once'](text,OLD,NEW)

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    p.add_argument('--restore-wserv-symbols',type=Path);a=p.parse_args()
    if a.restore_wserv_symbols:
        native=a.restore_wserv_symbols
        cert=json.loads((native/'wserv-find-notfound-base-802.json').read_text())
        binary=a.root/'epoc32/release/armv5/urel/wserv_nga.exe'
        expected='b8a2fb688e3a920923330d12819a1e8b048bca52cbfe2142721ab446889c421b'
        if cert['base_binary_sha256']!=expected or hashlib.sha256(binary.read_bytes()).hexdigest()!=expected:
            raise ValueError('cannot attach742 symbols to non742 WServ')
        for ext,digest in (('sym','4a11c2c6eaca7faad81a149d1385a7b65c2fc2212fd93ab776832a31ae63ddd6'),
                           ('map','5340d2e7ebb2a9631d3117a0815dfd65b73d88fac91a42c7f0f6d3db8fa95e6f')):
            source=native/('base742-wserv.'+ext)
            if cert['base.'+ext+'_sha256']!=digest or hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
                raise ValueError('unpinned reconstructed742 symbols')
            shutil.copyfile(source,binary.with_suffix('.exe.'+ext))
        print('HTCLEO_WSERV_SYMBOLS=restored-verified-reconstruction742-binary-byte-identical801')
        return
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore and (transform(new)!=new or transform(new,True)!=transform(old,True)):
        raise ValueError('enumeration inverse/idempotence failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleomenutaskenumeration.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    print('HTCLEO_MENU_TASK_ENUMERATION='+('restored' if a.restore else 'finite-root-window-names-native-errors-no-global-wserv-change'))

if __name__=='__main__':main()
