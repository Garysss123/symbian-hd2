#!/usr/bin/env python3
"""811: Settings AppUi BaseConstruct boundaries, keep810 SGC compatibility."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='AknAppUi.cpp'
BASE_SHA='bc050d23aadcfd64eedd56d9b93b112ead05a84a62f9cdc2cfc7f36fbab45a08'
BASE_BINARY='c1ff4b544fa1cd5487b28351b64b3ac78fa8fb543e26ed818ae029080f1745a5'
INC='#include "htcleogsappuitrace.inl"\n'
ANCHOR='void HtcleoAknAppUiBaseLog(TUint32 aStage, TInt aResult, TUint32 aDetail)\n'
LOG_OLD='    const TUint32 htcleoLogSid = RProcess().SecureId().iId;\n'
LOG_NEW=LOG_OLD+'''    if (htcleoLogSid == 0x100058ecu)
        {
        HtcleoGsAppUiTrace(htcleoLogSid, aStage, aResult, aDetail);
        return;
        }
'''
START='EXPORT_C void CAknAppUi::BaseConstructL(TInt aAppUiFlags)'
END='EXPORT_C void CAknAppUi::HandleTouchPaneSizeChange()'
TRACE='    HtcleoGsAppUiTrace(htcleoGsBaseSid, %s, %s, %s);\n'
EDITS=[
 ('    TInt skinParamErr = KErrNone;','''    const TUint32 htcleoGsBaseSid = RProcess().SecureId().iId;
    HtcleoGsAppUiTrace(htcleoGsBaseSid, 0xb560u, KErrNone, (TUint32)aAppUiFlags);
    TInt skinParamErr = KErrNone;'''),
 ('    TRAPD( skinErr, AknsUtils::InitSkinSupportL() );',
  TRACE%('0xb561u','skinParamErr','0u')+TRACE%('0xb562u','KErrNone','0u')+'    TRAPD( skinErr, AknsUtils::InitSkinSupportL() );\n'+TRACE%('0xb563u','skinErr','0u')),
 ('    TRAPD( allocErr, DecideWsClientBufferSizesL() );',
  TRACE%('0xb564u','KErrNone','0u')+'    TRAPD( allocErr, DecideWsClientBufferSizesL() );\n'+TRACE%('0xb565u','allocErr','0u')),
 ('    CAknAppUiBase::BaseConstructL(aAppUiFlags);',
  TRACE%('0xb566u','KErrNone','(TUint32)aAppUiFlags')+'    CAknAppUiBase::BaseConstructL(aAppUiFlags);\n'+TRACE%('0xb567u','KErrNone','0u')),
 ('    User::LeaveIfError( skinErr );','    User::LeaveIfError( skinErr );\n'+TRACE%('0xb568u','KErrNone','0u')),
 ('        AknsUtils::SetAvkonSkinEnabledL( ETrue );',
  TRACE%('0xb569u','KErrNone','0u')+'        AknsUtils::SetAvkonSkinEnabledL( ETrue );\n'+TRACE%('0xb56au','KErrNone','0u')),
 ('#ifdef RD_SCALABLE_UI_V2',TRACE%('0xb56bu','KErrNone','0u')+'#ifdef RD_SCALABLE_UI_V2'),
 ('    if (StatusPane())',TRACE%('0xb56cu','KErrNone','0u')+'    if (StatusPane())'),
 ('    TInt uid = KErrNotFound;',TRACE%('0xb56du','KErrNone','0u')+'    TInt uid = KErrNotFound;'),
 ('    ReplaceKeySoundsL(uid);',TRACE%('0xb56eu','KErrNone','(TUint32)uid')+'    ReplaceKeySoundsL(uid);\n'+TRACE%('0xb56fu','KErrNone','0u')),
 ('    AddViewDeactivationObserverL(this);',TRACE%('0xb570u','KErrNone','0u')+'    AddViewDeactivationObserverL(this);\n'+TRACE%('0xb571u','KErrNone','0u')),
 ('    iAppShutter = CAknAppShutter::NewL(*iEikonEnv, this, &iAppShutter);',TRACE%('0xb572u','KErrNone','0u')+'    iAppShutter = CAknAppShutter::NewL(*iEikonEnv, this, &iAppShutter);\n'+TRACE%('0xb573u','KErrNone','0u')),
 ('    if(!iExtension)',TRACE%('0xb574u','KErrNone','0u')+'    if(!iExtension)'),
 ('    AddViewActivationObserverL(iExtension);',TRACE%('0xb575u','KErrNone','0u')+'    AddViewActivationObserverL(iExtension);\n'+TRACE%('0xb576u','KErrNone','0u')),
 ('        iExtension->iFlags.Assign(CAknAppUiExtension::EAppIsHiddenInBackground, isBackground);','        iExtension->iFlags.Assign(CAknAppUiExtension::EAppIsHiddenInBackground, isBackground);'),
]


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GSApp AppUi anchor drift: '+repr(old))
    return text.replace(old,new,1)


def body_transform(text,restore=False):
    start=text.index(START);end=text.index(END,start)
    body=text[start:end]
    if restore:
        body=once(body,TRACE%('0xb57fu','KErrNone','0u')+'    }','    }')
        for old,new in reversed(EDITS):body=once(body,new,old)
    else:
        for old,new in EDITS:body=once(body,old,new)
        closing=body.rfind('    }')
        body=body[:closing]+TRACE%('0xb57fu','KErrNone','0u')+body[closing:]
    return text[:start]+body+text[end:]


def transform(text,restore=False):
    if INC in text:
        text=body_transform(text,True);text=once(text,INC,'');text=once(text,LOG_NEW,LOG_OLD)
    elif 'HtcleoGsAppUiTrace' in text or 'htcleoGsBaseSid' in text:raise ValueError('partial GSApp AppUi observer')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('AppUi differs from exact810 source')
    if not restore:
        text=once(text,ANCHOR,INC+ANCHOR);text=once(text,LOG_OLD,LOG_NEW);text=body_transform(text)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('AppUi inverse/idempotence failed')
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsappuitrace.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_APPUI='+('restored' if a.restore else 'sid100058ec-B500-B547-B560-B57F-GSBOOT1m-no-policy-change'))


if __name__=='__main__':main()
