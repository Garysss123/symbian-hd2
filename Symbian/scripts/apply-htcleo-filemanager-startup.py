#!/usr/bin/env python3
"""882: sparse FileManager startup observation in one Eikon-core component."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/commonuisupport/uikon/coresrc')
HELPER='htcleofmstartup882.inl'
BASE={
 'EIKSTART.CPP':'a08868e67061c56c025378ef57655e1c9f806d31e041fbc872193557ab647ae3',
 'EIKENV.CPP':'6c8998486f9b420223134dfd2712e6d7c3ea133cc4b69d87e77d712b06c89667',
}
EDITS={
 'EIKSTART.CPP':[
 ('// HTCLEO_EIKSTART_HOMESCREEN_TRACE_V1', '#include "'+HELPER+'"\n\n// HTCLEO_EIKSTART_HOMESCREEN_TRACE_V1'),
 ('    if (RProcess().SecureId().iId != 0x102750F0u)\n',
 '''    if (RProcess().SecureId().iId == 0x101f84ebu)
        {
        HtcleoFmStartupLog(aStage, aResult, aDetail);
        return;
        }
    if (RProcess().SecureId().iId != 0x102750F0u)
'''),
 ('\t\t(RProcess().SecureId().iId == 0x102750F0u);',
  '\t\t(RProcess().SecureId().iId == 0x102750F0u ||\n\t\t RProcess().SecureId().iId == 0x101f84ebu); //882 log gate only'),
 ],
 'EIKENV.CPP':[
 ('#include "htcleogsenvtrace.inl"\n', '#include "htcleogsenvtrace.inl"\n#include "'+HELPER+'"\n'),
 ('''    else if (sid == 0x100058ecu)
        {
        HtcleoGsEnvTrace(sid, aStage, aResult);
        }
''', '''    else if (sid == 0x100058ecu)
        {
        HtcleoGsEnvTrace(sid, aStage, aResult);
        }
    else if (sid == 0x101f84ebu)
        {
        HtcleoFmStartupLog(aStage, aResult, 0u);
        }
'''),
 ('EXPORT_C void CEikonEnv::HandleError(TInt aError)\n    {\n',
  'EXPORT_C void CEikonEnv::HandleError(TInt aError)\n    {\n    HtcleoFmStartupLog(0xe3f0u, aError, iInfoMsgWin ? 1u : 0u); //882 observation only\n'),
 ],
}
def once(text,old,new):
    if text.count(old)!=1:raise ValueError('882 source anchor drift '+repr(old))
    return text.replace(old,new,1)
def transform(text,name,restore=False):
    if '#include "'+HELPER+'"' in text:
        for old,new in reversed(EDITS[name]):text=once(text,new,old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact881 Eikon source '+name)
    if not restore:
        for old,new in EDITS[name]:text=once(text,old,new)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    pending=[]
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('882 inverse')
        if not a.restore and transform(new,name)!=new:raise ValueError('882 idempotence')
        pending.append((path,old,new))
    for path,old,new in pending:
        if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        (a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    print('HTCLEO_FILEMANAGER_STARTUP='+('restored' if a.restore else '20-filtered-stages-native-error-policy-preserved'))
if __name__=='__main__':main()
