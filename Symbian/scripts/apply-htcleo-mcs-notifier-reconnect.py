#!/usr/bin/env python3
"""871: bounded native AppArc notification reconnect after server termination."""
import argparse
import hashlib
from pathlib import Path

REL = Path('sf/mw/homescreensrv/menucontentsrv/srvsrc/htcleomcsapplistnotifier.inl')
BASE_SHA = 'b832e9538bdb9260c4b35300587acaa77a4f6677527410dcecde0fe95cd798e8'
MARKER = 'HTCLEO_MCS_NOTIFIER_RECONNECT_871'
CHANGES = [
    ('        Cancel();\n        iLsSession.Close();',
     '        Cancel();\n        iReconnectTimer.Close();\n        iLsSession.Close();'),
    (': CActive(aPriority), iObserver(aObserver)',
     ': CActive(aPriority), iObserver(aObserver), iReconnectAttempts(0), iReconnecting(EFalse), iSnapshotPending(EFalse)'),
    ('        iLsSession.CancelNotify();',
     '        if (iReconnecting) iReconnectTimer.Cancel();\n        else iLsSession.CancelNotify();'),
    ('        const TInt status = iStatus.Int();\n',
     '''        const TInt status = iStatus.Int();
        // HTCLEO_MCS_NOTIFIER_RECONNECT_871
        if (iReconnecting)
            {
            iReconnecting = EFalse;
            if (status != KErrNone)
                {
                HtcleoMcsActionLog(0x2f11u, status, iReconnectAttempts, 0u);
                return;
                }
            const TInt connected = iLsSession.Connect();
            HtcleoMcsActionLog(0x2f12u, connected, iReconnectAttempts, 0u);
            if (connected == KErrNone)
                {
                // Ask the real server for a current-list/scan-complete result.
                // Do not synthesize an observer event or poll the app list.
                iSnapshotPending = ETrue;
                iLsSession.SetNotify(ETrue, iStatus);
                SetActive();
                return;
                }
            iLsSession.Close();
            if (connected == KErrNotFound || connected == KErrServerTerminated)
                ScheduleReconnect();
            return; // Other connect errors remain recorded and stopped.
            }
        if (iSnapshotPending)
            {
            iSnapshotPending = EFalse;
            HtcleoMcsActionLog(0x2f14u, status, iReconnectAttempts, 0u);
            }
'''),
    ('''            // The completed AO is already inactive. Do NOT requeue a dead
            // session, throw through the broken path, or notify a fake change.
            // This subscription stays stopped until the scanner is recreated.
''', '''            // The completed AO is inactive. Close the dead session and
            // retry asynchronously, never dispatching a fake list change.
'''),
    ('            HtcleoMcsActionLog(0x2f00u, status, 0, 0x35314e4du); // MN15\n            return;',
     '            HtcleoMcsActionLog(0x2f00u, status, 0, 0x35314e4du); // MN15\n            ScheduleReconnect();\n            return;'),
    ('    TInt RunError(TInt /*aError*/)\n', '''    void ScheduleReconnect()
        {
        // Lifetime budget: no reset after a successful reconnect, so repeated
        // server failures cannot create an unlimited retry/logging loop.
        if (iReconnectAttempts >= 12)
            {
            HtcleoMcsActionLog(0x2f13u, KErrTimedOut, iReconnectAttempts, 0u);
            return;
            }
        if (!iReconnectTimer.Handle())
            {
            const TInt result = iReconnectTimer.CreateLocal();
            HtcleoMcsActionLog(0x2f10u, result, iReconnectAttempts, 5000000u);
            if (result != KErrNone) return;
            }
        ++iReconnectAttempts;
        iReconnecting = ETrue;
        iReconnectTimer.HighRes(iStatus, 5000000);
        SetActive();
        }

    TInt RunError(TInt /*aError*/)
'''),
    ('    RApaLsSession iLsSession;\n',
     '    RApaLsSession iLsSession;\n    RTimer iReconnectTimer;\n    TInt iReconnectAttempts;\n    TBool iReconnecting;\n    TBool iSnapshotPending;\n'),
]
POLICY = 'MCS-only-dead-notification-5s-async-reconnect-max12-lifetime-native-SetNotifyTrue-snapshot-no-restart'


def transform(text, restore=False):
    if MARKER in text:
        for old, new in reversed(CHANGES):
            if text.count(new) != 1:
                raise ValueError('partial871 notifier reconnect')
            text = text.replace(new, old, 1)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('871 requires exact799-870 notifier')
    if restore:
        return text
    for old, new in CHANGES:
        if text.count(old) != 1:
            raise ValueError('871 notifier anchor drift: ' + repr(old[:60]))
        text = text.replace(old, new, 1)
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('871 inverse failed')
    if old != new:
        path.write_text(new)
    print('HTCLEO_MCS_NOTIFIER_RECONNECT=' + ('restored' if a.restore else POLICY))
