#!/usr/bin/env python3
"""885: expose native SGC Connect result/handle without changing recovery policy."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
HELPER='htcleofmsgc885.inl'
BASE={'aknsgcc.cpp':'5cf238fe330f3ec193697391d72b300401815da9a329a8a5403743a7f0102028'}
EDITS=[
 ('#include "htcleogssgctrace.inl"\n','#include "htcleogssgctrace.inl"\n#include "'+HELPER+'"\n'),
 ('    const TUint32 htcleoSid = RProcess().SecureId().iId;\n',
  '    const TUint32 htcleoSid = RProcess().SecureId().iId;\n'
  '    if (htcleoSid == 0x101f84ebu)\n'
  '        {\n'
  '        HtcleoFmStartupLog(aStage, aResult, aDetail);\n'
  '        return;\n'
  '        }\n'),
 ('    const TInt htcleoSgcHandle = iAknSrv.Handle();\n',
  '    const TInt htcleoSgcHandle = iAknSrv.Handle();\n'
  '    HtcleoFmStartupLog(0x4d4da136u, aknServerError, (TUint32)htcleoSgcHandle); //885 read-only\n'),
]
def once(text,a,b):
    if text.count(a)!=1:raise ValueError('885 anchor drift '+repr(a))
    return text.replace(a,b,1)
def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong885 source')
    if '#include "'+HELPER+'"' in text:
        for a,b in reversed(EDITS):text=once(text,b,a)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact884 SGC source')
    if not restore:
        for a,b in EDITS:text=once(text,a,b)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/'aknsgcc.cpp';old=path.read_text(encoding='latin-1');new=transform(old,'aknsgcc.cpp',a.restore)
    if transform(new,'aknsgcc.cpp',True)!=transform(old,'aknsgcc.cpp',True):raise ValueError('885 inverse')
    if not a.restore and transform(new,'aknsgcc.cpp')!=new:raise ValueError('885 idempotence')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:(a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    print('HTCLEO_FILEMANAGER_SGC='+('restored' if a.restore else '13-stages-native-connect-handle-no-policy-change'))
if __name__=='__main__':main()

