#!/usr/bin/env python3
"""883: refine the FileManager-only Eikon environment observation filter."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/commonuisupport/uikon/coresrc')
HELPER='htcleofmenv883.inl'
BASE={'EIKENV.CPP':'c090a37714ac974ba1b805b57c9884cf0a83e69fd7b1c8e3635d3c408a37081c'}
OLD='#include "htcleofmstartup882.inl"'
NEW='#include "htcleofmenv883.inl"'
def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong883 source')
    if NEW in text:
        if text.count(NEW)!=1:raise ValueError('duplicate883 layer')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact882 EIKENV source')
    if text.count(OLD)!=1:raise ValueError('882 route drift')
    return text if restore else text.replace(OLD,NEW,1)
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/'EIKENV.CPP';old=path.read_text(encoding='latin-1');new=transform(old,'EIKENV.CPP',a.restore)
    if transform(new,'EIKENV.CPP',True)!=transform(old,'EIKENV.CPP',True):raise ValueError('883 inverse')
    if not a.restore and transform(new,'EIKENV.CPP')!=new:raise ValueError('883 idempotence')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:(a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    print('HTCLEO_FILEMANAGER_ENV='+('restored' if a.restore else '20-filtered-env-stages-same-writer-budget-no-policy-change'))
if __name__=='__main__':main()

