#!/usr/bin/env python3
"""820: GS no-active-view activation transaction trace; native policy unchanged."""
import argparse
import hashlib
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/classicui/uifw/AvKon/src')
NAME='AknViewAppUi.cpp'
BASE_SHA='b901ae03a98f0c323e4e28af276dc5d41595da810d317cf18620b0b1a427bb9c'
BASE_BINARY='b3928c2e06e07e906e78f252ab145ef07bc80e20b4b8e2f271c4709090413930'
INC='#include "htcleogsactivationtrace.inl"\n'
START='void CAknViewAppUi::ActivationTick()\n\t{\n'
END='void CAknViewAppUi::QueueActivationTick()'
INIT='''    const TBool htcleoGsActivationTrace = HtcleoGsActivationEligible(
        RProcess().SecureId().iId, iView != NULL);
    TUint htcleoGsActivationRecords = 0;
'''
SUFFIX=' // HTCLEO_GS_ACTIVATION_TRANSACTION_TRACE\n'


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS activation anchor drift: '+repr(old))
    return text.replace(old,new,1)


def log(stage,result='KErrNone',detail='0u'):
    return '    if (htcleoGsActivationTrace) HtcleoGsActivationLog(htcleoGsActivationRecords, 0x%04xu, %s, %s);'%(stage,result,detail)+SUFFIX


def wrap_line(body,line,before,after,result='KErrNone',detail='0u',expected=1):
    pattern=r'(?m)^([ \t]*)'+re.escape(line)+r'\n'
    def change(m):
        return (log(before,result,detail) if before else '')+m[0]+(log(after,result,detail) if after else '')
    body,n=re.subn(pattern,change,body)
    if n!=expected:raise ValueError('GS activation statement count: '+line+' '+str(n))
    return body


def apply_body(text):
    a=text.index(START);b=text.index(END,a);body=text[a:b]
    body=once(body,START,START+INIT+log(0xc600,detail='(TUint32)iActivationQueue'))
    body=wrap_line(body,'CViewActivationItem* item( iActivationQueue->At( 0 ) );',None,0xc601,detail='(TUint32)item')
    body=wrap_line(body,'iActivationQueue->Delete( 0 );',0xc60e,0xc60f,expected=2)
    body=wrap_line(body,'TBool exit( EFalse );',None,0xc602,detail='(TUint32)iView')
    # The pinned release compiles the non-split branch. Both native branches
    # are retained; common cleanup remains observable regardless.
    marker='#else\n\tif ( item->iNewView == iView && '
    s=body.index(marker);e=body.index('#endif // RD_SPLIT_VIEW',s)
    local=body[s:e]
    trap=r'(?m)^[ \t]*TRAPD\( error, item->iNewView->AknViewActivatedL\([\s\S]*?\) \);\n'
    local,n=re.subn(trap,lambda m:log(0xc605,detail='(TUint32)item->iNewView')+m[0]+log(0xc606,'error','(TUint32)item->iNewView'),local)
    if n!=1:raise ValueError('GS activation native TRAPD drift')
    local=wrap_line(local,'iExtension->iActiveViews.Append( item->iNewView );',0xc618,0xc619,detail='(TUint32)item->iNewView')
    local=wrap_line(local,'iView = item->iNewView;',None,0xc609,'error','(TUint32)iView')
    local=wrap_line(local,'item->iNewView->AknViewDeactivated();',0xc61a,0xc61b,'error')
    local=wrap_line(local,'iEikonEnv->HandleError( error );',0xc61c,0xc61d,'error')
    body=body[:s]+local+body[e:]
    body=wrap_line(body,'delete iClearer;',0xc60c,None,detail='(TUint32)iClearer')
    body=wrap_line(body,'iClearer = NULL;',None,0xc60d)
    body=wrap_line(body,'delete item;',0xc610,0xc611)
    body=wrap_line(body,'TRAP_IGNORE( HandleForegroundEventL( EFalse ) );',0xc612,0xc613)
    body=wrap_line(body,'RunAppShutter();',None,0xc614)
    body=wrap_line(body,'QueueActivationTick();',0xc615,0xc616)
    close=body.rfind('\t}')
    if close<0:raise ValueError('activation closing brace absent')
    body=body[:close]+log(0xc617,'exit','(TUint32)iView')+body[close:]
    return text[:a]+body+text[b:]


def transform(text,restore=False):
    old=text
    if INC in text:
        a=text.index(START);b=text.index(END,a);body=text[a:b]
        body,n=re.subn(r'(?m)^[ \t]*if \(htcleoGsActivationTrace\) HtcleoGsActivationLog\([^\n]*\); // HTCLEO_GS_ACTIVATION_TRANSACTION_TRACE\n','',body)
        if n!=26:raise ValueError('GS activation trace count drift: '+str(n))
        body=once(body,START+INIT,START)
        text=once(text[:a]+body+text[b:],INC,'')
    elif 'htcleoGsActivationRecords' in text:raise ValueError('partial activation trace')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:raise ValueError('ViewAppUi differs from exact819 source')
    patched=apply_body(once(text,'// CONSTANTS\n',INC+'// CONSTANTS\n'))
    if INC in old and old!=patched:raise ValueError('modified activation trace cannot be silently removed')
    return text if restore else patched


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore:
        if transform(new)!=new or transform(new,True)!=transform(old,True):raise ValueError('activation inverse/idempotence failed')
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleogsactivationtrace.inl'
        path.with_name(helper.name).write_bytes(helper.read_bytes())
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_ACTIVATION='+('restored' if a.restore else 'GS-no-active-view-transaction64-native-activation-cleanup-unchanged'))


if __name__=='__main__':main()
