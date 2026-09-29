#!/usr/bin/env python3
"""884: FileManager-only existing Avkon initialization stage routing."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
HELPER='htcleofmaknenv884.inl'
BASE={'aknenv.cpp':'3f9e7b14dbda727b3dc028a1463dd0acc3596c9d6dff8dec3be05c2b5165ce5f'}
EDITS=[
 ('#include "htcleogsaknenvtrace.inl"\n','#include "htcleogsaknenvtrace.inl"\n#include "'+HELPER+'"\n'),
 ('    const TUint32 htcleoSid = RProcess().SecureId().iId;\n',
  '    const TUint32 htcleoSid = RProcess().SecureId().iId;\n'
  '    if (htcleoSid == 0x101f84ebu)\n'
  '        {\n'
  '        HtcleoFmStartupLog(aStage, aResult, aDetail);\n'
  '        return;\n'
  '        }\n'),
]
def once(text,a,b):
    if text.count(a)!=1:raise ValueError('884 anchor drift '+repr(a))
    return text.replace(a,b,1)
def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong884 source')
    if '#include "'+HELPER+'"' in text:
        for a,b in reversed(EDITS):text=once(text,b,a)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact883 AknEnv')
    if not restore:
        for a,b in EDITS:text=once(text,a,b)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/'aknenv.cpp';old=path.read_text(encoding='latin-1');new=transform(old,'aknenv.cpp',a.restore)
    if transform(new,'aknenv.cpp',True)!=transform(old,'aknenv.cpp',True):raise ValueError('884 inverse')
    if not a.restore and transform(new,'aknenv.cpp')!=new:raise ValueError('884 idempotence')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:(a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    print('HTCLEO_FILEMANAGER_AKNENV='+('restored' if a.restore else '17-existing-stages-same-writer-no-layout-policy-change'))
if __name__=='__main__':main()

