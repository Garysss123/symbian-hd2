#!/usr/bin/env python3
"""806: Settings-owned startup trace and5s UI-scheduler pulse, native UI policy kept."""
import argparse
import hashlib
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
BASE={
 'Src/GSApp.cpp':'18d7cf9c4f7820d8a628cea916c6d41dd61bd580eca95c37e521e9f6ae38283b',
 'Src/GSDocument.cpp':'f1db93c8406e88e9bf73564a2bf80288a71b3636abb19da83cf4eb513b76821b',
 'Src/GSUi.cpp':'8feb54ab3eba11ca2bc1fba349db705277fa27892f37c587668ae8d3f91e9e22',
 'Inc/GSUi.h':'7beab5f4e851c3b9e73c0bdcc555ee118cba296595bd732908d2f27d03f99994',
}
MMP_SHA='4e3e69c47249769865661c8651e8d03f6629265ef98383a4e0ff433981d004a9'
INCLUDE='#include "htcleogsboot.h"\n'
EDITS={
 'Src/GSApp.cpp':[
  ('#include    <gsfwviewuids.h>\n','#include    <gsfwviewuids.h>\n'+INCLUDE),
  ('    return CGSDocument::NewL(*this);','    HtcleoGsBootLog(0x6012u, KErrNone, 0u);\n    CApaDocument* document = CGSDocument::NewL(*this);\n    HtcleoGsBootLog(0x6013u, KErrNone, (TUint32)document);\n    return document;'),
  ('    return new CGSApp;','    HtcleoGsBootLog(0x6010u, KErrNone, 0u);\n    CGSApp* app = new CGSApp;\n    HtcleoGsBootLog(0x6011u, KErrNone, (TUint32)app);\n    return app;'),
  ('    return EikStart::RunApplication( NewApplication );','    HtcleoGsBootLog(0x6000u, KErrNone, 0x100058ecu);\n    const TInt result = EikStart::RunApplication( NewApplication );\n    HtcleoGsBootLog(0x6001u, result, 0u);\n    return result;'),
 ],
 'Src/GSDocument.cpp':[
  ('#include    "gspluginloader.h"\n','#include    "gspluginloader.h"\n'+INCLUDE),
  ('    CGSBaseDocument::ConstructL();','    HtcleoGsBootLog(0x6020u, KErrNone, 0u);\n    CGSBaseDocument::ConstructL();\n    HtcleoGsBootLog(0x6021u, KErrNone, 0u);'),
  ('    CGSUi* appUi = new(ELeave) CGSUi();','    HtcleoGsBootLog(0x6022u, KErrNone, 0u);\n    CGSUi* appUi = new(ELeave) CGSUi();\n    HtcleoGsBootLog(0x6023u, KErrNone, (TUint32)appUi);'),
 ],
 'Src/GSUi.cpp':[
  ('#include    "GSUi.h"\n','#include    "GSUi.h"\n'+INCLUDE),
  ('CGSUi::CGSUi()\n    {','CGSUi::CGSUi()\n    : iHtcleoGsPulse(NULL)\n    {'),
  ('CGSUi::~CGSUi()\n    {','CGSUi::~CGSUi()\n    {\n    HtcleoGsBootLog(0x6040u, KErrNone, iHtcleoGsPulse ? 1u : 0u);\n    delete iHtcleoGsPulse;\n    iHtcleoGsPulse = NULL;'),
  ('    FeatureManager::InitializeLibL();','    HtcleoGsBootLog(0x6030u, KErrNone, 0u);\n    FeatureManager::InitializeLibL();\n    HtcleoGsBootLog(0x6031u, KErrNone, 0u);'),
  ('    BaseConstructL( EAknEnableSkin | EAknEnableMSK |EAknSingleClickCompatible );','    BaseConstructL( EAknEnableSkin | EAknEnableMSK |EAknSingleClickCompatible );\n    HtcleoGsBootLog(0x6032u, KErrNone, 0u);'),
  ('                             backupInfo );','                             backupInfo );\n  HtcleoGsBootLog(0x6033u, error, (TUint32)backupInfo);'),
  ('      SetDefaultViewL( *iMainView );','      SetDefaultViewL( *iMainView );\n      HtcleoGsBootLog(0x6037u, KErrNone, (TUint32)iMainView);'),
  ('    GSDocument().PreparePluginCacheL( *this );','    HtcleoGsBootLog(0x6038u, KErrNone, iMainView ? 1u : 0u);\n    GSDocument().PreparePluginCacheL( *this );\n    HtcleoGsBootLog(0x6039u, KErrNone, 0u);'),
  ('    iEComNotifier = CGSEComNotifier::NewL( this, GSDocument().GetImplInfo() );','    HtcleoGsBootLog(0x603au, KErrNone, 0u);\n    iEComNotifier = CGSEComNotifier::NewL( this, GSDocument().GetImplInfo() );\n    HtcleoGsBootLog(0x603bu, KErrNone, (TUint32)iEComNotifier);\n    HtcleoGsBootLog(0x603cu, KErrNone, iMainView ? 1u : 0u);\n    iHtcleoGsPulse = CHtcleoGsUiPulse::New();'),
  ('    iMainView = CGSMainView::NewL();','    HtcleoGsBootLog(0x6034u, KErrNone, 0u);\n    iMainView = CGSMainView::NewL();\n    HtcleoGsBootLog(0x6035u, KErrNone, (TUint32)iMainView);'),
  ('    AddViewL( iMainView );         // transfer ownership to CAknViewAppUi','    AddViewL( iMainView );         // transfer ownership to CAknViewAppUi\n    HtcleoGsBootLog(0x6036u, KErrNone, 0u);'),
  ('    __GSLOGSTRING1( "[CGSUi] HandleCommandL(%d)", aCommand );','    __GSLOGSTRING1( "[CGSUi] HandleCommandL(%d)", aCommand );\n    HtcleoGsBootLog(0x6041u, aCommand, 0u);'),
 ],
 'Inc/GSUi.h':[
  ('class CGSDocument;','class CGSDocument;\nclass CHtcleoGsUiPulse;'),
  ('        CGSEComNotifier* iEComNotifier;','        CGSEComNotifier* iEComNotifier;\n        CHtcleoGsUiPulse* iHtcleoGsPulse; // owned diagnostic, cancelled in destructor'),
 ],
}

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GSApp anchor drift: '+repr(old))
    return text.replace(old,new,1)

def transform(text,name,restore=False):
    edits=EDITS[name]
    marker=edits[0][1]
    if marker in text:
        for old,new in reversed(edits):text=once(text,new,old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('GSApp source differs from pinned805 source: '+name)
    if not restore:
        for old,new in edits:text=once(text,old,new)
    return text

def code_only_mmp(text):
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=MMP_SHA:raise ValueError('GSApp MMP drift')
    result,n=re.subn(r'^START RESOURCE\s+.*?^END[^\n]*\n','',text,flags=re.M|re.S)
    if n!=2:raise ValueError('Expected two GSApp resource sections')
    return once(result,'SOURCE          GSApp.cpp\n','SOURCE          GSApp.cpp\nSOURCE          htcleogsboot.cpp\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path)
    mode=p.add_mutually_exclusive_group();mode.add_argument('--restore',action='store_true');mode.add_argument('--baseline',action='store_true');a=p.parse_args()
    base=a.root/REL
    for name in BASE:
        path=base/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore or a.baseline)
        if not (a.restore or a.baseline) and (transform(new,name)!=new or transform(new,name,True)!=transform(old,name,True)):
            raise ValueError('GSApp inverse/idempotence failure')
        if old!=new:path.write_text(new,encoding='latin-1')
    if a.baseline:
        text=code_only_mmp((base/'GSApplication.mmp').read_text(encoding='latin-1'))
        text=once(text,'SOURCE          htcleogsboot.cpp\n','')
        text=once(text,'TARGET          gsapp.exe','TARGET          gsapp_baseline.exe')
        (base/'GSApplication_baseline.mmp').write_text(text,encoding='latin-1')
        print('HTCLEO_GSAPP_BASELINE=unmodified-source-code-only-separate-local-target')
        return
    if not a.restore:
        # Windows-source spelling, exact same exported SDK resource IDs.
        header=a.root/'epoc32/include/gsframeworkrsc.rsg'
        alias=header.with_name('GSFrameworkRsc.rsg')
        if not header.is_file():raise ValueError('GSFramework resource-ID header missing')
        if not alias.exists():alias.symlink_to(header.name)
        if alias.read_bytes()!=header.read_bytes():raise ValueError('GSFramework header alias differs')
        assets=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'
        for name in ('htcleogsboot.h','htcleogsboot.cpp','htcleogslogoffset.inl','htcleogsheartbeat.inl'):
            (base/('Inc' if name.endswith('.h') else 'Src')/name).write_bytes((assets/name).read_bytes())
        (base/'GSApplication_htcleo.mmp').write_text(code_only_mmp((base/'GSApplication.mmp').read_text(encoding='latin-1')),encoding='latin-1')
    print('HTCLEO_GSAPP_OBSERVER='+('restored' if a.restore else 'native-startup-edges-no-policy-change-owned-ui5s-GSBOOT1m'))

if __name__=='__main__':main()
