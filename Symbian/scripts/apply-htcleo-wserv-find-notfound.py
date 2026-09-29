#!/usr/bin/env python3
"""Preserve caught native NotFound for one final Matrix lookup; no new logging.

The optional object certificate is used for this critical WServ change only:
rebuild/pin exact742 first, then require that only CLIENT.o changes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct

HERE=Path(__file__).resolve().parent
REL=Path('sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc')
NAME='CLIENT.CPP'
BASE_SHA='eacdc8b2c10893d4632c484d287d28aec81b94824d50699f3be603fcd26271e9'
CONTROL_SHA='b8a2fb688e3a920923330d12819a1e8b048bca52cbfe2142721ab446889c421b'
ANCHOR='            const TBool htcleoCompatibilityError =\n'
INCLUDE='#include "htcleowservfindnotfound.inl"\n'
CONTROL=HERE.parent/'output/742-symbian3-full-matrix-unowned-kick-retired-incremental/Symbian3/build/incremental-release-cache/wserv_nga.exe'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(text):return hashlib.sha256(text.encode('latin-1')).hexdigest()


def header_contract(path):
    # E32ImageHeader/V, platform/f32image.h. Offsets that must NOT change:
    # UIDs/signature, module/compression/tools, flags, data/heap/stack/BSS,
    # link bases, DLL count, export count, header size, priority/CPU and security.
    raw=path.read_bytes()
    if len(raw)<0x9c or raw[0x10:0x14]!=b'EPOC':raise ValueError('not a V-format E32 image')
    offsets=(0,4,8,12,16,24,28,32,44,52,56,60,64,68,76,80,84,92,100,120,128,132,136,140)
    return {hex(n):struct.unpack_from('<I',raw,n)[0] for n in offsets}


def transform(text,restore=False):
    if INCLUDE in text:
        if text.count(INCLUDE)!=1:raise ValueError('duplicate native-find result layer')
        text=text.replace(INCLUDE,'',1)
    if digest(text)!=BASE_SHA:raise ValueError('WServ client source differs from verified742/801 control')
    if not restore:
        if text.count(ANCHOR)!=1:raise ValueError('ambiguous compatibility catch')
        text=text.replace(ANCHOR,INCLUDE+ANCHOR,1)
    return text


def objects(root):
    base=root/'epoc32/build/wserv-nga-build'
    paths=sorted(p for p in base.glob('*/wserv_nga_exe/armv5/urel/*.o') if p.is_file())
    if len(paths)<50 or len([p for p in paths if p.name=='CLIENT.o'])!=1:
        raise ValueError('incomplete/ambiguous WServ object set')
    return {str(p.relative_to(base)):sha(p) for p in paths}


def record_base(root,output):
    source=root/REL/NAME
    if digest(source.read_text(encoding='latin-1'))!=BASE_SHA:raise ValueError('base source not restored')
    binary=root/'epoc32/release/armv5/urel/wserv_nga.exe'
    if sha(binary)!=CONTROL_SHA:raise ValueError('base must be independently rebuilt and pinned742 first')
    output.parent.mkdir(parents=True,exist_ok=True)
    data=dict(base_source_sha256=BASE_SHA,base_binary_sha256=CONTROL_SHA,
        header_contract=header_contract(binary),objects=objects(root))
    for suffix in ('.sym','.map'):
        data['base'+suffix+'_sha256']=sha(binary.with_name(binary.name+suffix))
    if output.exists():
        # A failed later ROM verifier may be retried. Keep the FIRST certificate;
        # reuse is allowed only after another exact base reconstruction matches
        # every object, contract and preserved symbol artifact byte-for-byte.
        if json.loads(output.read_text())!=data:
            raise ValueError('reconstructed base differs from preserved certificate')
        for suffix in ('.sym','.map'):
            if sha(output.with_name('base742-wserv'+suffix))!=data['base'+suffix+'_sha256']:
                raise ValueError('preserved base symbols corrupted')
        print('HTCLEO_WSERV_FIND_BASE_REUSED_EXACT objects='+str(len(data['objects'])))
        return
    for suffix in ('.sym','.map'):
        path=binary.with_name(binary.name+suffix)
        target=output.with_name('base742-wserv'+suffix)
        if target.exists():raise ValueError('base symbol evidence already exists')
        shutil.copyfile(path,target)
        if sha(target)!=data['base'+suffix+'_sha256']:raise ValueError('base symbol copy mismatch')
    output.write_text(json.dumps(data,indent=2)+'\n')
    print('HTCLEO_WSERV_FIND_BASE_OK objects='+str(len(data['objects'])))


def verify_derived(root,base_file,report):
    data=json.loads(base_file.read_text())
    if data['base_source_sha256']!=BASE_SHA or data['base_binary_sha256']!=CONTROL_SHA:
        raise ValueError('wrong WServ base certificate')
    source=(root/REL/NAME).read_text(encoding='latin-1')
    if transform(transform(source,True))!=source:raise ValueError('derived source drift')
    asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleowservfindnotfound.inl'
    if (root/REL/asset.name).read_bytes()!=asset.read_bytes():raise ValueError('compiled lookup helper drift')
    after=objects(root);before=data['objects']
    if set(after)!=set(before):raise ValueError('WServ object membership changed')
    changed=[p for p in after if after[p]!=before[p]]
    if len(changed)!=1 or Path(changed[0]).name!='CLIENT.o':
        raise ValueError('unexpected WServ object deltas: '+repr(changed))
    binary=root/'epoc32/release/armv5/urel/wserv_nga.exe'
    if sha(binary)==CONTROL_SHA:raise ValueError('derived WServ binary did not change')
    if sha(CONTROL)!=CONTROL_SHA or header_contract(binary)!=header_contract(CONTROL):
        raise ValueError('WServ ABI/security/heap/stack/priority contract changed')
    result=dict(status='HTCLEO_WSERV_FIND_NOTFOUND_OBJECTS_OK',base_binary_sha256=CONTROL_SHA,
        binary_sha256=sha(binary),source_sha256=digest(source),helper_sha256=sha(asset),
        changed_objects=changed,unchanged_objects=len(after)-1,base_certificate_sha256=sha(base_file),
        header_contract=header_contract(binary),
        policy='matrix-final-name-query-native-notfound-no-new-log')
    report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    group=p.add_mutually_exclusive_group();group.add_argument('--restore',action='store_true')
    group.add_argument('--record-base',type=Path);group.add_argument('--verify-derived',type=Path)
    p.add_argument('--report',type=Path);a=p.parse_args()
    if a.record_base:record_base(a.root,a.record_base);return
    if a.verify_derived:
        if not a.report:p.error('--report required with --verify-derived')
        verify_derived(a.root,a.verify_derived,a.report);return
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore and (transform(new)!=new or transform(new,True)!=transform(old,True)):
        raise ValueError('WServ lookup inverse/idempotence failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleowservfindnotfound.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    print('HTCLEO_WSERV_FIND_NOTFOUND='+('restored' if a.restore else 'matrix-final-name-query-native-notfound-no-new-log'))

if __name__=='__main__':main()
