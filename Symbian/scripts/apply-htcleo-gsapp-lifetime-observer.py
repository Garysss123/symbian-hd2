#!/usr/bin/env python3
"""823: GS lifetime in existing Home CLOCKLOG padding; no new writer/thread."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='htcleoclockwatch.inl'
BASE_SHA='3cb81d100ada267e688fad1414082b0deffd75ccd9fa02c80af68ddecdfd7bab'
BASE_BINARY='b13d8516e804f2bd89538dc8af0f857a14634627a25211b3388bdb33141e7ea5'
APPUI_SHA='4dc7473f39941e05416191cf5346a22902a3b2f61ee91700bd1a04f236bcbe54'
EDITS=(
 ('#include <f32file.h>\n','#include <f32file.h>\n#include "htcleogslifewatch.inl"\n',1),
 ('    TInt aHighResult, TInt aClassicStatus, TUint32 aClassicDone)\n','    TInt aHighResult, TInt aClassicStatus, TUint32 aClassicDone,\n    const THtcleoGsLifeWatch& aGsLife)\n',1),
 ('    const TUint32 slot = aSequence % 2048u;\n','    aGsLife.Append(line); //823: use padding; original36 fields/512-byte write unchanged.\n    const TUint32 slot = aSequence % 2048u;\n',1),
 ('    RThread mainThread;\n','    THtcleoGsLifeWatch gsLife; //Owned only by this existing observer thread.\n    RThread mainThread;\n',1),
 ('            gHtcleoClockClassicDone);','            gHtcleoClockClassicDone, gsLife);',3),
 ('        result = highStatus.Int();\n','        result = highStatus.Int();\n        if (result == KErrNone) gsLife.Sample(fs); //No assignment to clock result.\n',1),
)
def replace(text,old,new,count):
    if text.count(old)!=count: raise ValueError('clock lifetime anchor drift: '+repr(old))
    return text.replace(old,new)
def transform(text,restore=False):
    if '#include "htcleogslifewatch.inl"' in text:
        for old,new,count in reversed(EDITS): text=replace(text,new,old,count)
    elif 'gsLife' in text or 'aGsLife' in text: raise ValueError('partial lifetime layer')
    if hashlib.sha256(text.encode('ascii')).hexdigest()!=BASE_SHA: raise ValueError('not exact822 clock worker')
    if not restore:
        for old,new,count in EDITS: text=replace(text,old,new,count)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    source=a.root/REL/NAME;old=source.read_text(encoding='ascii');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True): raise ValueError('lifetime inverse failed')
    if not a.restore and transform(new)!=new: raise ValueError('lifetime idempotence failed')
    if old!=new: source.write_text(new,encoding='ascii')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogslifewatch.inl'
        (source.parent/helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_GSAPP_LIFETIME='+('restored' if a.restore else 'Home-existing-clock5s-native-GS-process-thread-exit-CLOCKLOG-padding-no-new-io-writer'))
if __name__=='__main__': main()
