#!/usr/bin/env python3
"""894: observe the real FileManager progress-dialog callback; no UI policy change."""
import argparse
import hashlib
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/uifw/AvKon/src')
BASE = {'AknProgressDialog.cpp': '6b10081d5432174140c44b95dc504b5d351a356ec52910cbdf0a303f600296cf'}
HELPER = 'htcleofmprogress894.inl'
INC = '#include "' + HELPER + '"\n'
ANCHOR = '#include "akntrace.h"\n'
MARKER = ' // HTCLEO_FM_PROGRESS_BOUNDARY_894'
START = 'TInt CAknProgressDialog::DialogTimerEvent()\n'
END = 'EXPORT_C void CAknProgressDialog::ProcessFinishedL()'
INIT = '''    //894: cache identity/state before native calls; TryExitL can delete this.
    const TBool htcleoFmProgress = RProcess().SecureId().iId == 0x101f84ebu;
    const TInt htcleoFmState = (TInt)iState;
    const TUint32 htcleoFmObject = (TUint32)this;
'''
CALLBACK_OLD = '''TInt CAknProgressDialog::DialogTimerCallback(TAny* aPtr)
\t{
\treturn STATIC_CAST(CAknProgressDialog*, aPtr)->DialogTimerEvent();
\t}
'''
CALLBACK_NEW = '''TInt CAknProgressDialog::DialogTimerCallback(TAny* aPtr)
\t{
    const TBool htcleoFmProgress = RProcess().SecureId().iId == 0x101f84ebu;
    const TUint32 htcleoFmObject = (TUint32)aPtr;
    if (htcleoFmProgress) HtcleoFmProgressLog(0xd500u, -1, htcleoFmObject);
    const TInt result = STATIC_CAST(CAknProgressDialog*, aPtr)->DialogTimerEvent();
    //The native call may delete the dialog: do not inspect aPtr afterwards.
    if (htcleoFmProgress) HtcleoFmProgressLog(0xd502u, result, htcleoFmObject);
    return result;
\t}
'''
STAGES = (0xd500, 0xd501, 0xd502, 0xd508, 0xd509, *range(0xd510, 0xd51f),
          0xd520, 0xd521, *range(0xd530, 0xd535), 0xd540, 0xd541, 0xd5ff)

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('894 anchor drift '+repr(old))
    return text.replace(old,new,1)

def log(stage):
    return ('    if (htcleoFmProgress) HtcleoFmProgressLog(0x%04xu, '
            'htcleoFmState, htcleoFmObject);'%stage)+MARKER+'\n'

def after_line(text, needle, stage):
    matches=list(re.finditer(r'^.*'+re.escape(needle)+r'.*\n',text,re.M))
    if len(matches)!=1:raise ValueError('894 line anchor '+needle)
    m=matches[0]
    return text[:m.end()]+log(stage)+text[m.end():]

def body_transform(text, restore=False):
    begin=text.index(START);end=text.index(END,begin)
    body=text[begin:end]
    if restore:
        body,count=re.subn(r'^.*'+re.escape(MARKER)+r'\n','',body,flags=re.M)
        if count!=28:raise ValueError('894 expected28 event boundaries, got '+str(count))
        body=once(body,INIT,'')
    else:
        # Match only the function opening, never another nested native brace.
        body=once(body,START+'    {\n',START+'    {\n'+INIT+log(0xd501))
        split=body.index('        case EProcessOnDisplayOn:')
        first=body[:split];rest=body[split:]
        first=once(first,'        case EProcessOnDisplayOff:\n\t\t\t{\n',
                   '        case EProcessOnDisplayOff:\n\t\t\t{\n'+log(0xd508))
        first=once(first,'            iState = EProcessOnDisplayOn;\n',
                   log(0xd509)+'            iState = EProcessOnDisplayOn;\n'+log(0xd510))
        for needle,stage in (
            ('ControlAttributes()->InvalidateLayout();',0xd511),
            ('            Layout();',0xd512),
            ('CEikDialog::SlideDialog();',0xd513),
            ('\t\t\tDrawableWindow()->SetOrdinalPosition(0);',0xd514),
            ('            MakeVisible(ETrue);',0xd515),
            ('CCoeControl* cba = ButtonGroupContainer().ButtonGroup()->AsControl();',0xd516),
            ('iEikonEnv->RemoveFromStack(cba);',0xd517),
            ('__ASSERT_DEBUG_NO_LEAVE(iEikonEnv->EikAppUi()->AddToStackL(',0xd518),
            ('cba->DrawableWindow()->SetOrdinalPosition(0);',0xd519),
            ('cba->MakeVisible(ETrue);',0xd51a),
            ('ReportUserActivity();',0xd51b),('PlayTone();',0xd51c),
            ('iCancelWhileHidden = NULL;',0xd51d)):
            first=after_line(first,needle,stage)
        first=once(first,'            break;\n',log(0xd51e)+'            break;\n')
        split=rest.index('        case EProcessOffDisplayOff:')
        second=rest[:split];rest=rest[split:]
        second=after_line(second,'case EProcessOnDisplayOn:',0xd520)
        second=after_line(second,'iProgressDialogTimer = NULL;',0xd521)
        split=rest.index('        default:')
        third=rest[:split];tail=rest[split:]
        third=after_line(third,'case EProcessOffDisplayOn:',0xd530)
        for needle,stage in (('iProgressDialogTimer = NULL;',0xd531),
                             ('ReportUserActivity();',0xd532),('PlayTone();',0xd533),
                             ('TRAP_IGNORE(TryExitL( EAknSoftkeyDone ));',0xd534)):
            third=after_line(third,needle,stage)
        tail=after_line(tail,'default:',0xd540)
        tail=after_line(tail,'iProgressDialogTimer = NULL;',0xd541)
        tail=once(tail,'    return KErrNone;\n',log(0xd5ff)+'    return KErrNone;\n')
        body=first+second+third+tail
    return text[:begin]+body+text[end:]

def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('wrong894 source')
    if INC in text:
        text=body_transform(text,True)
        text=once(text,CALLBACK_NEW,CALLBACK_OLD)
        text=once(text,INC,'')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:
        raise ValueError('not exact893 progress-dialog source')
    if not restore:
        text=once(text,ANCHOR,ANCHOR+INC)
        text=once(text,CALLBACK_OLD,CALLBACK_NEW)
        text=body_transform(text)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true')
    a=p.parse_args();path=a.root/REL/'AknProgressDialog.cpp'
    old=path.read_text(encoding='latin-1');new=transform(old,path.name,a.restore)
    if transform(new,path.name,True)!=transform(old,path.name,True):raise ValueError('894 inverse')
    if not a.restore:
        if transform(new,path.name)!=new:raise ValueError('894 idempotence')
        (a.root/REL/HELPER).write_bytes((HERE.parent/'hd2/qsd8250-native-bsp/diagnostics'/HELPER).read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_FILEMANAGER_PROGRESS='+('restored' if a.restore else 'actual-progress-dialog-callback48-no-policy-change'))

if __name__=='__main__':main()
