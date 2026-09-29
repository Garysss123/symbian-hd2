#!/usr/bin/env python3
"""775 fatal subject: exact774 normal path, native ABI/bounds, no HW proof."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / 'output/772-symbian3-full-logless-liveness-badge-incremental/Symbian3/build'


def strip_life(text):
    text = strip_sw_life(text)
    for marker in (
        '#include "htcleo_crashnotice.inl"\n\n',
        '    if (gHtcleoCrashNotified) return;\n',
        '    HtcleoLifeGlyph(308, KHtcleoCrashH, 0xffffu);\n',
        '    HtcleoLifeGlyph(320, KHtcleoLifeHex[HtcleoCrashHookOwned() ? 1 : 0], 0xffffu);\n',
    ):
        text = text.replace(marker, '')
    return text.replace(
        '    if (gHtcleoLifePeriod > 0)\n        {\n        HtcleoInstallCrashNotice();\n'
        '        (void)aTimer.OneShot(gHtcleoLifePeriod);\n        }',
        '    if (gHtcleoLifePeriod > 0)\n        (void)aTimer.OneShot(gHtcleoLifePeriod);')


def strip_sw_life(text):
    return re.sub(r'    // HTCLEO_SW_EXCEPTION_BADGE_V1_BEGIN\n.*?    // HTCLEO_SW_EXCEPTION_BADGE_V1_END\n',
                  '', text, count=1, flags=re.S)


def strip_sw_crash(text):
    if '// HTCLEO_FATAL_GLYPH_OUTLINE_V1_BEGIN' in text:
        original = (ROOT / 'output/920-symbian3-full-java-help-entry-c-only/Symbian3/build/htcleo_crashnotice.inl').read_text()
        glyph = original[original.index('static void HtcleoCrashGlyph('):original.index('static void HtcleoCrashRow(')].rstrip()
        text = re.sub(r'// HTCLEO_FATAL_GLYPH_OUTLINE_V1_BEGIN\n.*?// HTCLEO_FATAL_GLYPH_OUTLINE_V1_END',
                      lambda _: glyph,text,count=1,flags=re.S)
    text = text.replace('static void __attribute__((noinline)) HtcleoCrashGlyph(',
                        'static void HtcleoCrashGlyph(')
    if '// HTCLEO_SW_EXCEPTION_INCLUDE_V1' in text and 'static TAny* volatile* gHtcleoCrashRegsSlot;' not in text:
        text = text.replace('static TScheduler* gHtcleoCrashScheduler;\n',
            'static TScheduler* gHtcleoCrashScheduler;\nstatic TAny* volatile* gHtcleoCrashRegsSlot;\n')
        text = text.replace('    const SFullArmRegSet* regs = gHtcleoCrashScheduler ?\n'
            '        static_cast<const SFullArmRegSet*>(gHtcleoCrashScheduler->i_Regs) : NULL;',
            '    const SFullArmRegSet* regs = gHtcleoCrashRegsSlot ?\n'
            '        static_cast<const SFullArmRegSet*>(*gHtcleoCrashRegsSlot) : NULL;')
        text = text.replace('    gHtcleoCrashScheduler = TScheduler::Ptr();\n',
            '    gHtcleoCrashScheduler = TScheduler::Ptr();\n'
            '    gHtcleoCrashRegsSlot = &gHtcleoCrashScheduler->i_Regs;\n')
    text = text.replace('\n// HTCLEO_SW_EXCEPTION_INCLUDE_V1\n#include "htcleo_swexception.inl"\n', '')
    text = re.sub(r'// HTCLEO_SW_EXCEPTION_PAINT_V1_BEGIN\n.*?// HTCLEO_SW_EXCEPTION_PAINT_V1_END\n\n',
                  '', text, count=1, flags=re.S)
    text = text.replace('    HtcleoSwExceptionPaint(subject,category); //HTCLEO_SW_EXCEPTION_SUBJECT_V1\n', '')
    return text.replace('    HtcleoInstallSwExceptionObserver(); //HTCLEO_SW_EXCEPTION_INSTALL_V1\n', '')


def check():
    source = ROOT / 'hd2/qsd8250-native-bsp/baseport/htcleo/input'
    # Frozen775 contract;the additional observer has separate behavior tests.
    life = strip_sw_life((source / 'htcleo_liveness.inl').read_text())
    body = strip_sw_crash((source / 'htcleo_crashnotice.inl').read_text())
    touch = (source / 'htcleo_touch.cpp').read_text()
    assert strip_life(life) == (PARENT / 'htcleo_liveness.inl').read_text()
    original_touch = touch.replace('#include <e32btrace.h>\n', '').replace('#include <kernel/arm/arm_types.h>\n', '')
    assert original_touch == (PARENT / 'htcleo_touch.cpp').read_text()
    parent774 = ROOT / 'output/774-symbian3-full-native-crash-notice-incremental/Symbian3/build'
    assert life == (parent774 / 'htcleo_liveness.inl').read_text()
    assert touch == (parent774 / 'htcleo_touch.cpp').read_text()
    stripped = re.sub(r'// HTCLEO_CRASH_SUBJECT_V1_BEGIN\n.*?// HTCLEO_CRASH_SUBJECT_V1_END\n\n',
                      '', body, count=1, flags=re.S)
    stripped = stripped.replace('for (TInt y=0; y<258; ++y)', 'for (TInt y=0; y<90; ++y)')
    stripped = stripped.replace('    HtcleoCrashSubjectPaint(data);\n', '')
    assert stripped == (parent774 / 'htcleo_crashnotice.inl').read_text()
    assert body.count('BTrace::SetHandlers(') == 1
    assert body.count('if (function == BTrace::ECtrlSystemCrashed) HtcleoCrashNoticePaint();') == 1
    assert 'gHtcleoPreviousTrace(h,h2,context,a1,a2,a3,extra,pc)' in body
    assert 'gHtcleoPreviousControl(function,a1,a2)' in body
    assert 'iBTraceHandler == HtcleoTraceForward' in body
    assert 'if (gHtcleoCrashInstalled) return;' in body
    for bad in ('RFs', 'RFile', 'Printf(', 'WaitFor', 'NanoWait', 'OneShot(', 'RestoreInterrupts(',
                'EnableAllInterrupts(', 'LockSystem(', 'ThreadGetUserContext', 'SetFilter(', '.Suspend(', '.Resume('):
        assert bad not in body, bad
    callback = body[body.index('// HTCLEO_CRASH_SUBJECT_V1_BEGIN'):body.index('static void HtcleoInstallCrashNotice()')]
    callback = re.sub(r'//[^\n]*', '', callback)
    for bad in ('Kern::', 'NKern::', 'BTrace::Control(', 'TScheduler::Ptr(', '.Length()', '->Ptr()', '->Length()'):
        assert bad not in callback, bad
    assert '(packed >> 28) == 1u && length <= 1024u' in body
    assert 'i<length && i<8u' in body
    assert body.index('HtcleoCrashRow(34,data+2,second)') < body.index('const TUint32* descriptor')
    assert 'sizeof(SFullArmRegSet) == 1024' in body and 'iCrashArgs) == 1012' in body
    assert body.index('HtcleoCrashRow(62,data+4,third)') < body.index('HtcleoCrashSubjectPaint(data);')
    assert body.index('HtcleoCrashRow(146,subject+4,exit)') < body.index('if (categoryBytes)')
    for token in ('aOuter[0] == 4u', 'aOuter[1] == 0x7fffffffu',
                  'aOuter[4] == 0x4b45524eu', 'aOuter[5] == 0u',
                  'thread->iContainerID == EThread+1', 'owner->iContainerID == EProcess+1',
                  'sizeof(TBufC<KMaxExitCategoryName>) == 20',
                  '(packed >> 28) == 0u && (packed & 0x0fffffffu) <= 16u'):
        assert token in body, token
    addresses = [((y0+y*3+dy)*480+8+column*240+digit*18+x*3+dx)*2
                 for y0 in range(6,231,28) for column in range(2) for digit in range(9)
                 for y in range(7) for x in range(5) for dy in range(3) for dx in range(3)]
    assert len(addresses) == 51030 and max(addresses)+2 < 480*800*2
    assert max(a//960 for a in addresses) == 250 and max((a//2)%480 for a in addresses) == 406
    assert 258*480*2 < 480*800*2
    # Byte-exact model of the bounded kernel EBufC8 descriptor decoder.
    def decode_category(packed, payload):
        size = packed & 0x0fffffff
        if packed >> 28 or size > 16:
            return None
        if len(payload) < size:
            raise ValueError('truncated inline descriptor fixture')
        padded = payload[:size].ljust(16, b'\0')
        return [int.from_bytes(padded[i:i+4], 'big') for i in range(0,16,4)]
    assert decode_category(12, b'C32:ESock_Bt') == [0x4333323a,0x45536f63,0x6b5f4274,0]
    assert decode_category(0,b'') == [0,0,0,0]
    assert decode_category(16,b'0123456789ABCDEF')[-1] == 0x43444546
    assert decode_category(17,b'x'*17) is None
    assert decode_category(0x10000004,b'test') is None
    core = Path('/root/symbian/epoc32/release/armv5/urel/_htcleo_ekern.exe')
    assert hashlib.sha256(core.read_bytes()).hexdigest() == '11b1e892ed118d8002d1bc1813b7c432b591e400bbd14cd351235e772e32e055'
    original = Path('/root/symbian-oss/kernelhwsrv-gccsurge/kernel/eka/kernel/sutils.cpp')
    assert hashlib.sha256(original.read_bytes()).hexdigest() == 'b314f67c3a9a4372b4d9b5a0b6c8bc1372d06a27505241fa09d50a3cd5c451e5'
    args = tuple(range(8))
    def forward(handler, values): return handler(*values) if handler else False
    assert forward(lambda *v: (v,17), args) == (args,17)
    assert forward(None,args) is False
    print('HTCLEO_CRASH_NOTICE_HOST_PASS exact774-normal-path exact772-core/source KERN4-only-subject kernel-EBufC8 bounded258rows no-live-API-in-crash')


if __name__ == '__main__':
    check()
