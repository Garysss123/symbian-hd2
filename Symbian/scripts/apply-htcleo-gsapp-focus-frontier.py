#!/usr/bin/env python3
"""818: first GS FocusGained trace, with all Home policies/native calls retained."""
import argparse
import hashlib
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='AknAppUi.cpp'
BASE_SHA='271d0b2f353af714d7f090960e9303861a0b8627671bb49fbc8e3909cf0a3965'
BASE_BINARY='4050b7cbd5d6879aca2e8aa1a1a89747f7af8e7f5e62b0e9f10d888948a9215d'
INC='#include "htcleogsfocustrace.inl"\n'
INC_ANCHOR='// UIDS for dialler view\n'
ENUM_OLD='        EFocusLost\n'
ENUM_NEW='        EFocusLost,\n        EHtcleoGsFocusTraceUsed // private bit5; native bits0-4 unchanged\n'
START='EXPORT_C void CAknAppUi::HandleWsEventL(const TWsEvent& aEvent,CCoeControl* aDestination)\n    {\n'
END='TBool CAknAppUi::SimulateHashKeyMarkingEventL('
INIT='''    const TUint32 htcleoGsFocusSid = RProcess().SecureId().iId;
    const TBool htcleoGsFocusTrace = HtcleoGsFocusEligible(
        htcleoGsFocusSid, aEvent.Type(), iExtension != NULL,
        iExtension ? iExtension->iFlags[CAknAppUiExtension::EHtcleoGsFocusTraceUsed] : ETrue);
    if (htcleoGsFocusTrace)
        {
        iExtension->iFlags.Set(CAknAppUiExtension::EHtcleoGsFocusTraceUsed);
        }
'''
OLD_PATTERN=r'if \(htcleoHomeFocusTrace\)\n([ \t]*)HtcleoAknAppUiBaseLog\('
NEW_PATTERN=r'if \(htcleoHomeFocusTrace \|\| htcleoGsFocusTrace\)\n([ \t]*)HtcleoGsFocusLog\(htcleoGsFocusTrace, '
CTOR_OLD='    HtcleoGsAppUiTrace(htcleoGsBaseSid, 0xb57fu, KErrNone, 0u);\n'
CTOR_NEW=CTOR_OLD+'''    HtcleoGsFocusWrite(htcleoGsBaseSid == 0x100058ecu,
        0xc5e0u, KErrNone, (TUint32)iExtension);
'''


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS focus anchor drift: '+repr(old))
    return text.replace(old,new,1)


def body_transform(text,restore=False):
    begin=text.index(START);end=text.index(END,begin);body=text[begin:end]
    if restore:
        body=once(body,START+INIT,START)
        body,n=re.subn(NEW_PATTERN,r'if (htcleoHomeFocusTrace)\n\1HtcleoAknAppUiBaseLog(',body)
    else:
        body=once(body,START,START+INIT)
        body,n=re.subn(OLD_PATTERN,r'if (htcleoHomeFocusTrace || htcleoGsFocusTrace)\n\1HtcleoGsFocusLog(htcleoGsFocusTrace, ',body)
    if n!=16:raise ValueError('Expected exactly16 log-only guard changes, got '+str(n))
    return text[:begin]+body+text[end:]


def transform(text,restore=False):
    if INC in text:
        text=body_transform(text,True);text=once(text,INC,'');text=once(text,ENUM_NEW,ENUM_OLD);text=once(text,CTOR_NEW,CTOR_OLD)
    elif 'htcleoGsFocusTrace' in text or 'EHtcleoGsFocusTraceUsed' in text:raise ValueError('partial GS focus trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('AppUi differs from exact817 source')
    if not restore:
        text=once(text,INC_ANCHOR,INC+INC_ANCHOR);text=once(text,ENUM_OLD,ENUM_NEW)
        text=once(text,CTOR_OLD,CTOR_NEW);text=body_transform(text)
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('GS focus inverse/idempotence failed')
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsfocustrace.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_FOCUS='+('restored' if a.restore else 'first-GS-FocusGained-logonly-private-ext-bit5-C560-C56E-C594-C5E0'))


if __name__=='__main__':main()
