#!/usr/bin/env python3
"""835: snapshot native VWS wrapper result and later handler state, without re-arm policy."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/appsupport/appfw/viewserver')
BASE_BINARY='c283435efd47e00b460ed2702afec4484ab3e15fb4cc3e5d3dc5f6e3b7b710f2'
BASE={'client/VIEWCLI.CPP':'a36e963cd280e8f401f9848050f9180748c02115f07f3c865a6888e303161a24'}
OLD_INC='#include "htcleovwsclienttrace.inl"\n'
INC='#include "htcleovwsclientstatetrace.inl"\n'
START='EXPORT_C TInt CVwsSessionWrapper::ActivateView(const TVwsViewId& aViewId,TUid aCustomMessageId,const TDesC8& aCustomMessage, TInt aCustomControl)\n\t{\n\tCONNECT_AS_REQUIRED\n'
END='EXPORT_C void CVwsSessionWrapper::ActivateView('
INIT="""    // HTCLEO_VWS_CLIENT_STATE_835
    const TBool htcleoStateTrace = HtcleoVwsClientEligible(RProcess().SecureId().iId);
    TUint htcleoStateRecords = 0;
    const TUint32 htcleoTargetViewUid = htcleoStateTrace ? (TUint32)aViewId.iViewUid.iUid : 0u;
"""
CREATE_OLD="""EXPORT_C TInt CVwsSessionWrapper::CreateActivateViewEvent(const TVwsViewId& aViewId,TUid aCustomMessageId,const TDesC8& aCustomMessage, TInt aCustomControl)
	{
	CONNECT_AS_REQUIRED

	return iVwsSession->ActivateView(aViewId, aCustomMessageId, aCustomMessage, aCustomControl);
	}
"""
CREATE_NEW="""EXPORT_C TInt CVwsSessionWrapper::CreateActivateViewEvent(const TVwsViewId& aViewId,TUid aCustomMessageId,const TDesC8& aCustomMessage, TInt aCustomControl)
	{
	CONNECT_AS_REQUIRED
"""+INIT+"""
    if (htcleoStateTrace)
        {
        HtcleoVwsClientLog(htcleoStateRecords, 0xcb17u, aCustomControl, htcleoTargetViewUid);
        HtcleoVwsClientSnapshot(htcleoStateRecords, 0xcb10u, iViewEventHandler);
        }
    const TInt htcleoResult = iVwsSession->ActivateView(aViewId, aCustomMessageId, aCustomMessage, aCustomControl);
    if (htcleoStateTrace)
        {
        HtcleoVwsClientLog(htcleoStateRecords, 0xcb13u, htcleoResult, htcleoTargetViewUid);
        HtcleoVwsClientSnapshot(htcleoStateRecords, 0xcb14u, iViewEventHandler);
        }
    return htcleoResult;
	}
"""
RETURN_OLD='\t\treturn (error != KErrNone) ? error : status.Int();'
RETURN_NEW="""        const TInt htcleoResult = (error != KErrNone) ? error : status.Int();
        if (htcleoStateTrace)
            {
            HtcleoVwsClientLog(htcleoStateRecords, 0xcb01u, htcleoResult, htcleoTargetViewUid);
            HtcleoVwsClientLog(htcleoStateRecords, 0xcb02u, error, (TUint32)status.Int());
            }
        return htcleoResult;"""
NOSCHED_OLD='\t\treturn iVwsSession->ActivateView(aViewId,aCustomMessageId,aCustomMessage, aCustomControl);'
NOSCHED_NEW="""        const TInt htcleoResult = iVwsSession->ActivateView(aViewId,aCustomMessageId,aCustomMessage, aCustomControl);
        if (htcleoStateTrace)
            HtcleoVwsClientLog(htcleoStateRecords, 0xcb07u, htcleoResult, htcleoTargetViewUid);
        return htcleoResult;"""
def once(t,a,b):
    if t.count(a)!=1:raise ValueError('VWS state anchor drift '+repr(a[:85]))
    return t.replace(a,b,1)
def transform(text,name,restore=False):
    if name not in BASE:raise ValueError('unsupported VWS state file')
    if INC in text:
        a=text.index(START);b=text.index(END,a);body=text[a:b]
        body=once(body,START+INIT+'    if (htcleoStateTrace) HtcleoVwsClientLog(htcleoStateRecords, 0xcb00u, aCustomControl, htcleoTargetViewUid);\n    if (htcleoStateTrace) HtcleoVwsClientSnapshot(htcleoStateRecords, 0xcb04u, iViewEventHandler);\n',START)
        body=once(body,RETURN_NEW,RETURN_OLD);body=once(body,NOSCHED_NEW,NOSCHED_OLD)
        text=text[:a]+body+text[b:]
        text=once(text,CREATE_NEW,CREATE_OLD);text=once(text,INC,OLD_INC)
    elif 'HTCLEO_VWS_CLIENT_STATE_835' in text:raise ValueError('partial VWS state observation')
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE[name]:raise ValueError('not exact834 VWS source')
    if not restore:
        text=once(text,OLD_INC,INC)
        a=text.index(START);b=text.index(END,a);body=text[a:b]
        body=once(body,START,START+INIT+'    if (htcleoStateTrace) HtcleoVwsClientLog(htcleoStateRecords, 0xcb00u, aCustomControl, htcleoTargetViewUid);\n    if (htcleoStateTrace) HtcleoVwsClientSnapshot(htcleoStateRecords, 0xcb04u, iViewEventHandler);\n')
        body=once(body,RETURN_OLD,RETURN_NEW);body=once(body,NOSCHED_OLD,NOSCHED_NEW)
        text=text[:a]+body+text[b:]
        text=once(text,CREATE_OLD,CREATE_NEW)
    return text
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    for name in BASE:
        path=a.root/REL/name;old=path.read_text(encoding='latin-1');new=transform(old,name,a.restore)
        if transform(new,name,True)!=transform(old,name,True):raise ValueError('VWS state inverse failed')
        if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        helper=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleovwsclientstatetrace.inl'
        (a.root/REL/'client'/helper.name).write_bytes(helper.read_bytes())
    print('HTCLEO_VWS_CLIENT_STATE='+('restored' if a.restore else
          'Home-GS-sync-result-and-create-handler-state32-no-recovery-or-priority-change'))
if __name__=='__main__':main()
