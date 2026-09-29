#!/usr/bin/env python3
"""886: opt FileManager into the existing Settings zero-handle SGC mode."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
BASE={'aknsgcc.cpp':'57e7d2530e7fce257f509f8c98a6293f54ce8c96b8ee8174c845e67606c7c8de'}
HELPERS={
 'htcleogssgctrace.inl':('htcleofmsgcguard886.inl','7176bc29844eaafd54eedb24709f6ca03b142e89d19b48789efbf51d0aa9d0c6'),
 'htcleogssgcchange.inl':('htcleofmsgcparams886.inl','52bb2a76cd3e9ea93dab952861f2d35c4cd17703ffc29f5cce014e7942d1cfa5'),
 'htcleogssystemfade.inl':('htcleofmsgcfade886.inl','e7d9b8ec1888165002d7ee6e62c1c50da39b14ce5a27311802c2607d67aece8d'),
 'htcleogskeyblock.inl':('htcleofmsgckeyblock886.inl','e72c52b09ca6219df18d26601596351dc396e7fd46c33c7b7e428dc0760eb7b1'),
}
PREFIX='//886: FileManager may use the proven Settings zero-handle SGC mode.\n//Only the behavioral SID predicate is extended; original GS logging stays GS-only.\n'
PREDICATE_OLD='return aSid == 0x100058ecu && aHandle == 0'
PREDICATE_NEW='return (aSid == 0x100058ecu || aSid == 0x101f84ebu) && aHandle == 0'
def derive_helper(raw,name):
    if name not in HELPERS or hashlib.sha256(raw).hexdigest()!=HELPERS[name][1]:raise ValueError('original helper drift '+name)
    text=raw.decode('latin-1').replace('\r\n','\n')
    if text.count(PREDICATE_OLD)!=1:raise ValueError('behavior predicate drift '+name)
    return (PREFIX+text.replace(PREDICATE_OLD,PREDICATE_NEW,1)).encode('latin-1')
def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong886 source')
    patched=[new for old,(new,_) in HELPERS.items() if '#include "'+new+'"' in text]
    if patched:
        if len(patched)!=4:raise ValueError('partial886 includes')
        for old,(new,_) in HELPERS.items():
            needle='#include "'+new+'"'
            if text.count(needle)!=1:raise ValueError('duplicate886 include')
            text=text.replace(needle,'#include "'+old+'"',1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact885 SGC source')
    if not restore:
        for old,(new,_) in HELPERS.items():
            needle='#include "'+old+'"'
            if text.count(needle)!=1:raise ValueError('old helper include drift')
            text=text.replace(needle,'#include "'+new+'"',1)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/'aknsgcc.cpp';old=path.read_text(encoding='latin-1');new=transform(old,'aknsgcc.cpp',a.restore)
    if transform(new,'aknsgcc.cpp',True)!=transform(old,'aknsgcc.cpp',True):raise ValueError('886 inverse')
    if not a.restore and transform(new,'aknsgcc.cpp')!=new:raise ValueError('886 idempotence')
    assets=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'
    pending=[]
    if not a.restore:
        for original,(derived,_) in HELPERS.items():
            raw=derive_helper((assets/original).read_bytes(),original)
            if (assets/derived).read_bytes()!=raw:raise ValueError('derived helper differs '+derived)
            if (a.root/REL/original).read_bytes()!=(assets/original).read_bytes():raise ValueError('original SDK helper drift '+original)
            pending.append((a.root/REL/derived,raw))
    for target,raw in pending:target.write_bytes(raw)
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_SGC_LOCAL='+('restored' if a.restore else 'FileManager-existing-GS-zero-handle-mode-entry-params-fade-keyblock-no-live-session-change'))
if __name__=='__main__':main()
