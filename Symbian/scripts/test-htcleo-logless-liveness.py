#!/usr/bin/env python3
"""Host-only contract tests for the single logless772 badge (not hardware proof)."""
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'output/771-symbian3-full-readyqueue-endpoint-context-incremental/Symbian3/build'


def strip_native(text):
    text = text.replace('#include <e32btrace.h>\n', '').replace('#include <kernel/arm/arm_types.h>\n', '')
    for old, new in (
        ('\n#include "htcleo_liveness.inl"\n', ''),
        ('            case 22: return HtcleoLifeDiagnosticHal(a1, a2);\n', ''),
        ('        NTimer iLifeTimer;\n', ''),
        ('iTimer(NULL, this), iLifeTimer(HtcleoLifeTimer, &iLifeTimer), iPollDfc',
         'iTimer(NULL, this), iPollDfc'),
        ('        if (timerResult == KErrNone) HtcleoStartLifeProbe(iLifeTimer);\n', ''),
    ):
        text = text.replace(old, new)
    return text


def strip_user(text):
    for marker in (
        '#ifdef HTCLEO_G17_WORKER_STATE_V1\n#include "htcleog17state.inl"\n#endif\n',
        '#ifdef HTCLEO_G17_WORKER_STATE_V1\n'
        '        if (result == KErrNone) HtcleoObserveG17State(fs, sequence - 1u);\n#endif\n',
        '#include "htcleologlesspulse.inl"\n',
        '        HtcleoLoglessIoMark(1, sequence);\n',
        '        HtcleoLoglessIoMark(result == KErrNone ? 2u : 3u,\n'
        '            result == KErrNone ? sequence : (TUint32)result);\n',
        '    HtcleoStartLoglessUserPulse();\n',
    ):
        text = text.replace(marker, '')
    return text


def check():
    native = ROOT / 'hd2/qsd8250-native-bsp/baseport/htcleo/input'
    diag = ROOT / 'hd2/qsd8250-native-bsp/diagnostics'
    body = (native / 'htcleo_liveness.inl').read_text()
    strip_life = runpy.run_path(str(ROOT / 'scripts/test-htcleo-crash-notice.py'))['strip_life']
    body = strip_life(body)
    touch = (native / 'htcleo_touch.cpp').read_text()
    user = (diag / 'htcleologlesspulse.inl').read_text()
    watcher = (diag / 'htcleokernelwatch.inl').read_text()
    assert strip_user(watcher) == (PARENT / 'htcleokernelwatch.inl').read_text()
    assert (native / 'htcleo_threadstate.inl').read_text() == (PARENT / 'htcleo_threadstate.inl').read_text()
    assert touch.count('#include "htcleo_liveness.inl"') == 1
    assert touch.count('case 22:') == 1 and touch.count('NTimer iLifeTimer;') == 1
    assert touch.count('HtcleoStartLifeProbe(iLifeTimer);') == 1
    assert 'if (timerResult == KErrNone) HtcleoStartLifeProbe(iLifeTimer);' in touch
    assert 'NTimer::' not in body  # only native member API calls, not queue patches
    assert 'OneShot(gHtcleoLifePeriod)' in body and 'NKern::TimerTicks(1000)' in body
    assert 'Epoc::LinearToPhysical(KHwBaseFrameBuffer) != KHwPhysFrameBuffer' in body
    for token in ('HtcleoI2c', 'HtcleoGpio', 'RFs', 'RFile', 'RProperty', 'UserSvr',
                  'NanoWait', 'NKern::LockSystem', 'Suspend(', 'Resume(', 'SetPriority('):
        assert token not in body, token
    assert re.findall(r'WriteReg\([^;]+;', body) == ['WriteReg(KHwBaseMdp, 0x44u, 0u);']
    for offset in ('0x90008u', '0x90004u', '0x9000cu'):
        assert f'ReadReg(KHwBaseMdp, {offset})' in body
    assert '0x200286e3u' in body and 'return KErrPermissionDenied' in body
    assert 'gHtcleoTouchSamples,' in body
    for token in ('RFs', 'RFile', 'RWs', 'RProperty', 'HtcleoHomeLog', 'SetOrdinal', 'After('):
        assert token not in user, token
    assert user.count('EPriorityAbsoluteForegroundNormal') == 1
    assert 'pulseTimer.HighRes(wait, 1000000)' in user
    assert user.count('User::WaitForRequest(wait)') == 1
    assert user.count('static TBool started = EFalse;') == 1
    assert watcher.count('HtcleoLoglessIoMark(1, sequence);') == 1

    # Exercise the actual glyph address formula over every column/row written.
    glyph_x = [4 + f*72 + d*12 for f in range(4) for d in range(5)] + [284]
    addresses = [((4+y*2+dy)*480+x+gx*2+dx)*2
                 for x in glyph_x for y in range(7) for gx in range(5)
                 for dy in range(2) for dx in range(2)]
    assert min(addresses) >= 0 and max(addresses)+2 <= 480*800*2
    assert max(a//960 for a in addresses) == 17
    assert max((a//2)%480 for a in addresses) == 293
    assert len(addresses) == 2940
    print('HTCLEO_LOGLESS_LIVENESS_HOST_PASS one-badge bbox4,4-293,17 pixels2940 timer-isr independent-user no-files exact771-observer-preserved')


if __name__ == '__main__':
    check()
