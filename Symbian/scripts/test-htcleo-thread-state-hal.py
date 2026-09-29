#!/usr/bin/env python3
"""Host source contract: HAL21 cannot alter the existing hardware paths."""
import argparse
import hashlib
from pathlib import Path
import runpy

p = argparse.ArgumentParser()
p.add_argument("staged_input", type=Path)
a = p.parse_args()
root = Path(__file__).parents[1]
src = root / "hd2/qsd8250-native-bsp/baseport/htcleo/input"
body = (src / "htcleo_touch.cpp").read_text()
header = (src / "htcleo_threadstate.inl").read_text()
inc = '#include "htcleo_threadstate.inl"\n'
old = 'static TInt TouchDiagnosticHal(TAny*, TInt aFunction, TAny*, TAny*)'
new = 'static TInt TouchDiagnosticHal(TAny*, TInt aFunction, TAny* a1, TAny* a2)'
case = '            case 21: return HtcleoReadThreadState(a1, a2);\n'

def remove_hook(s):
    strip = runpy.run_path(str(root / 'scripts/test-htcleo-logless-liveness.py'))['strip_native']
    return strip(s).replace(inc, '').replace(new, old).replace(case, '')

assert body.count(inc) == 1 and body.count(new) == 1 and body.count(case) == 1
assert remove_hook(body) == remove_hook((a.staged_input / "htcleo_touch.cpp").read_text())
assert hashlib.sha256(remove_hook(body).encode()).hexdigest() == '1acd735d772094c349e248abb51c1eecd39a05264102b460ff024b6ea822d25a'
for forbidden in ('WriteReg(', 'ReadReg(', 'SetPriority(', 'Suspend(', 'Resume(',
                  'RequestComplete(', 'ThreadRequestSignal(', 'SetContext(',
                  'HalFunction(', 'RFile', 'Printf(', 'After('):
    assert forbidden not in header, forbidden
assert header.count('NKern::LockSystem();') == 1
assert header.count('NKern::UnlockSystem();') == 1
assert header.count('NKern::ThreadEnterCS();') == 1
assert header.count('NKern::ThreadLeaveCS();') == 1
assert header.index('NKern::LockSystem();') < header.index('Kern::ObjectFromHandle(')
assert header.index('NKern::UnlockSystem();') < header.index('Kern::InfoCopy(')
assert '0x200286e3u' in header and '0x101f4cd2u' in header and '0x102750f0u' in header
assert 'msg->iClient == target' in header and '!msg->IsFree()' in header
assert 'alive ? target->iSyncMsgPtr : NULL' in header
assert 'ThreadGetUserContext(&target->iNThread, regs, words[17])' in header
assert 'ThreadGetUserContext(&endpoint->iNThread, regs, words[35])' in header
assert 'words[0] = 2u' in header
assert 'priority = 63; priority >= 0' in header and '++seen > 256' in header
assert 'item->iPriority != priority' in header
assert header.count('NKern::DisableAllInterrupts()') == 1
assert header.count('NKern::RestoreInterrupts(irq)') == 1
assert 'thread == &aCaller.iNThread' in header and 'aWords[25] = (TUint32)priority' in header
assert 'TUint32 words[37]' in header
native = Path('/root/symbian-oss/kernelhwsrv-gccsurge/kernel/eka')
sthread = (native / 'kernel/sthread.cpp').read_text()
assert 'iMState' in sthread and 'iWaitLink.iSpare1' in sthread and 'iWaitLink.iSpare2' in sthread
assert 'target->iWaitLink.iSpare1' in header and 'target->iWaitLink.iSpare2' in header
print('HTCLEO_THREAD_STATE_HOST_TEST_PASS unchanged-touch-poll-rearm read-only-lock-copy caller-target-guards')
print('TOUCH_BASE_SHA256=' + hashlib.sha256(remove_hook(body).encode()).hexdigest())

# Model the read-only queue observations, including exclusion of the observer.
def queue_model(queues, caller='observer', target='matrix', endpoint='wserv'):
    flags, highest, seen = 0, None, 0
    for priority in range(63, -1, -1):
        for node in queues.get(priority, []):
            seen += 1
            if seen > 256: return flags | 16, highest
            if node == target: flags |= 1
            if node == endpoint: flags |= 2
            if node == caller: flags |= 4
            elif highest is None:
                highest = priority
                if node == endpoint: flags |= 32
                if node == target: flags |= 64
    return flags | 8, highest
assert queue_model({23:['observer','wserv'],12:['matrix'],0:['idle']}) == (47,23)
assert queue_model({23:['observer'],12:['matrix'],0:['idle']}) == (77,12)
assert queue_model({23:['observer'],0:['idle']}) == (12,0)
assert queue_model({23:['observer'],12:['matrix']*257})[0] & 16
print('HTCLEO_READY_QUEUE_MODEL_TEST_PASS bounded exclusion membership no-mutation')
