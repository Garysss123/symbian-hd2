#!/usr/bin/env python3
"""897: add CAsyncCallBack to typed late snapshots; no invocation or dispatch."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
BASE={'htcleoschedulertrace.cpp':'2723d4d54d4c8f972553f484a06c6d2364f29ac1f9f5738349e6f5dcd2519695'}
HELPER='htcleofmasync897.inl'
IDS='htcleofmasync897_ids.h'
INC='#include "'+HELPER+'"\n'
OLD_INC='#include "htcleofmlate896.inl"\n'
EDITS=((OLD_INC,INC),)

def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong897 source')
    if INC in text:
        if text.count(INC)!=1:raise ValueError('897 duplicate include')
        text=text.replace(INC,OLD_INC,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('not exact896 scheduler observer source')
    if not restore:
        if text.count(OLD_INC)!=1:raise ValueError('897 source anchor')
        text=text.replace(OLD_INC,INC,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    a=p.parse_args();path=a.root/REL/'htcleoschedulertrace.cpp'
    old=path.read_text(encoding='latin-1');new=transform(old,path.name,a.restore)
    if transform(new,path.name,True)!=transform(old,path.name,True):raise ValueError('897 inverse')
    if not a.restore:
        if transform(new,path.name)!=new:raise ValueError('897 idempotence')
        for helper in (HELPER,IDS):
            (a.root/REL/helper).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/helper).read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_ASYNC='+('restored' if a.restore else 'late32-known-async-callback-owner-no-dispatch'))

if __name__=='__main__':main()
