#!/usr/bin/env python3
"""896: shift the bounded FileManager candidate window later; no dispatch change."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
BASE={'htcleoschedulertrace.cpp':'bd5af7fed409a64a952499145f45b028efc2cccb56f48cbe5cdbc75cd1a7a379'}
HELPER='htcleofmlate896.inl'
IDS='htcleofmcallback893_ids.h'
INC='#include "'+HELPER+'"\n'
OLD_INC='#include "htcleofmcallback893.inl"\n'
EDITS=((OLD_INC,INC),)

def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong896 source')
    if INC in text:
        if text.count(INC)!=1:raise ValueError('896 duplicate include')
        text=text.replace(INC,OLD_INC,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('not exact895 scheduler observer source')
    if not restore:
        if text.count(OLD_INC)!=1:raise ValueError('896 source anchor')
        text=text.replace(OLD_INC,INC,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    a=p.parse_args();path=a.root/REL/'htcleoschedulertrace.cpp'
    old=path.read_text(encoding='latin-1');new=transform(old,path.name,a.restore)
    if transform(new,path.name,True)!=transform(old,path.name,True):raise ValueError('896 inverse')
    if not a.restore:
        if transform(new,path.name)!=new:raise ValueError('896 idempotence')
        for helper in (HELPER,IDS):
            (a.root/REL/helper).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/helper).read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_LATE='+('restored' if a.restore else 'wait25-56-same32-record-cap-no-dispatch'))

if __name__=='__main__':main()
