#!/usr/bin/env python3
"""817: GSApp-owned bounded WS dispatch and first main-view activation trace."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication')
BASE_BINARY='fcfaa869dba953e1d033d8564763885a454b292af663a8c11ae5fef3cd890137'
BASE={
 'Src/GSUi.cpp':'4358a7530597ed01f9ad7a33f02f216e0badedbfcd8ba7c01bc15dee95fa9293',
 'Src/GSMainView.cpp':'67da344c90b6670bab7e520307e4c8dc4a0ec921bed8823deeb4c3c30ab3830b',
 'Inc/GSUi.h':'f18ec882aaf6328f9546cf4d5c0a9d1055fb7a55336e27e6c103f5981ddf3741',
}
WS_GATE='''static TBool HtcleoGsTraceWsEvent(TInt aType, TUint& aCount)
    {
    if (aType == EEventPointer || aCount >= 8u) return EFalse;
    ++aCount;
    return ETrue;
    }

'''
WS_METHOD=WS_GATE+'''void CGSUi::HandleWsEventL(const TWsEvent& aEvent, CCoeControl* aControl)
    {
    static TUint htcleoGsWsTraceCount = 0; // EXE-owned bounded counter
    const TBool trace = HtcleoGsTraceWsEvent(aEvent.Type(), htcleoGsWsTraceCount);
    if (trace)
        {
        HtcleoGsBootLog(0x60d0u, aEvent.Type(), htcleoGsWsTraceCount);
        HtcleoGsBootLog(0x60d1u, aControl ? 1 : 0, (TUint32)aEvent.Handle());
        }
    CAknViewAppUi::HandleWsEventL(aEvent, aControl);
    if (trace) HtcleoGsBootLog(0x60d2u, aEvent.Type(), (TUint32)aEvent.Handle());
    }


'''
WS_ANCHOR='void CGSUi::HandleResourceChangeL( TInt aType )\n'
DECL_OLD='        void HandleCommandL( TInt aCommand );\n'
DECL_NEW=DECL_OLD+'''
        // Bounded startup observation; every event still delegates natively.
        virtual void HandleWsEventL(const TWsEvent& aEvent, CCoeControl* aControl);
'''
INCLUDE_OLD='#include    "GSUi.h"\n'
INCLUDE_NEW=INCLUDE_OLD+'#include    "htcleogsboot.h"\n'
VIEW_START='void CGSMainView::DoActivateL('
VIEW_END='void CGSMainView::DoDeactivate()'
VIEW_INIT='''    static TBool htcleoGsActivationTraced = EFalse; // EXE-owned first activation
    const TBool trace = !htcleoGsActivationTraced;
    htcleoGsActivationTraced = ETrue;
    if (trace) HtcleoGsBootLog(0x60a0u, KErrNone, iContainer ? 1u : 0u);
'''
VIEW_EDITS=(
 ('    __GSLOGSTRING( "[CGSMainView] DoActivateL()" );\n','    __GSLOGSTRING( "[CGSMainView] DoActivateL()" );\n'+VIEW_INIT),
 ('    iPluginLoader->RequestPriority( CActive::EPriorityHigh );\n','    iPluginLoader->RequestPriority( CActive::EPriorityHigh );\n    if (trace) HtcleoGsBootLog(0x60a1u, KErrNone, 0u);\n'),
 ('    NewContainerL();\n','    if (trace) HtcleoGsBootLog(0x60a2u, KErrNone, 0u);\n    NewContainerL();\n    if (trace) HtcleoGsBootLog(0x60a3u, KErrNone, iContainer ? 1u : 0u);\n'),
 ('    iContainer->SetListBoxEmptyTextL( empty );\n','    iContainer->SetListBoxEmptyTextL( empty );\n    if (trace) HtcleoGsBootLog(0x60a4u, KErrNone, 0u);\n'),
 ('    iContainer->UpdateListBoxL();\n','    iContainer->UpdateListBoxL();\n    if (trace) HtcleoGsBootLog(0x60a5u, KErrNone, 0u);\n'),
 ('    iAppUi->AddToViewStackL( *this, iContainer );\n','    if (trace) HtcleoGsBootLog(0x60a6u, KErrNone, 0u);\n    iAppUi->AddToViewStackL( *this, iContainer );\n    if (trace) HtcleoGsBootLog(0x60a7u, KErrNone, 0u);\n'),
 ('    GfxTransEffect::EndFullScreen();\n','    if (trace) HtcleoGsBootLog(0x60a8u, KErrNone, 0u);\n    GfxTransEffect::EndFullScreen();\n    if (trace) HtcleoGsBootLog(0x60a9u, KErrNone, 0u);\n'),
)


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('GS view anchor drift: '+repr(old))
    return text.replace(old,new,1)


def view_body(text,restore=False):
    begin=text.index(VIEW_START);end=text.index(VIEW_END,begin);body=text[begin:end]
    for old,new in (reversed(VIEW_EDITS) if restore else VIEW_EDITS):
        body=once(body,new,old) if restore else once(body,old,new)
    return text[:begin]+body+text[end:]


def transform(text,name,restore=False):
    if name=='Src/GSUi.cpp':
        if WS_METHOD in text:text=once(text,WS_METHOD,'')
        elif 'htcleoGsWsTraceCount' in text or 'CGSUi::HandleWsEventL' in text:raise ValueError('partial GS WS trace')
    elif name=='Inc/GSUi.h':
        if DECL_NEW in text:text=once(text,DECL_NEW,DECL_OLD)
        elif 'HandleWsEventL' in text:raise ValueError('partial GS WS declaration')
    elif name=='Src/GSMainView.cpp':
        if INCLUDE_NEW in text:
            text=view_body(text,True);text=once(text,INCLUDE_NEW,INCLUDE_OLD)
        elif 'htcleoGsActivationTraced' in text:raise ValueError('partial GS activation trace')
    else:raise ValueError('unexpected GS source')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('GS source differs from exact816: '+name)
    if not restore:
        if name=='Src/GSUi.cpp':text=once(text,WS_ANCHOR,WS_METHOD+WS_ANCHOR)
        elif name=='Inc/GSUi.h':text=once(text,DECL_OLD,DECL_NEW)
        else:text=view_body(once(text,INCLUDE_OLD,INCLUDE_NEW))
    return text


def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if not a.restore:
            if transform(new,name)!=new or transform(new,name,True)!=transform(old,name,True):raise ValueError('GS view inverse/idempotence failed')
        if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GSAPP_VIEW='+('restored' if a.restore else 'ws-first8-nonpointer-native-pass-through-first-activation-60A0-A9-GSBOOT-existing'))


if __name__=='__main__':main()
