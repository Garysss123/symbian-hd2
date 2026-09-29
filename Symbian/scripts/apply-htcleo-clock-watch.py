#!/usr/bin/env python3
"""Observe ordinary/high-res timers from an independent Home diagnostic thread."""
from __future__ import annotations
import argparse
from pathlib import Path

INCLUDE = '#include "htcleoclockwatch.inl"\n'
HOOK = '''    // HTCLEO_CLOCK_WATCH_START_V1
    if (htcleoLogHomeScreen)
        HtcleoClockObserve(aStage, aResult);
'''


def patch(text: str) -> str:
    if 'HTCLEO_CLOCK_WATCH_START_V1' in text:
        if text.count(HOOK) != 1 or text.count(INCLUDE) != 1:
            raise SystemExit('clock watcher installed inconsistently')
        return text
    include_anchor = '#ifdef __HTCLEO_AKNAPPUI_BASECONSTRUCT_LOG__\n#include <f32file.h>\n'
    hook_anchor = '    const TBool htcleoLogHomeScreen = htcleoLogSid == 0x102750F0u;\n'
    if text.count(include_anchor) != 1 or text.count(hook_anchor) != 1:
        raise SystemExit('Avkon logger anchors missing')
    updated = text.replace(include_anchor, include_anchor + INCLUDE, 1)
    updated = updated.replace(hook_anchor, hook_anchor + HOOK, 1)
    if updated.replace(INCLUDE, '', 1).replace(HOOK, '', 1) != text:
        raise SystemExit('unexpected change outside logger observer hook')
    return updated


def restore(text: str) -> str:
    if 'HTCLEO_CLOCK_WATCH_START_V1' not in text:
        if INCLUDE in text or 'HtcleoClockObserve(aStage, aResult);' in text:
            raise SystemExit('partial clock watcher installation')
        return text
    if text.count(HOOK) != 1 or text.count(INCLUDE) != 1:
        raise SystemExit('clock watcher removal anchor mismatch')
    restored = text.replace(INCLUDE, '', 1).replace(HOOK, '', 1)
    if patch(restored) != text:
        raise SystemExit('clock watcher reversal changed unrelated source')
    return restored


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--restore', action='store_true')
    args = ap.parse_args()
    source = args.root / 'sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp'
    before = source.read_text(encoding='latin-1')
    transform = restore if args.restore else patch
    after = transform(before)
    if transform(after) != after:
        raise SystemExit('clock watcher transform is not idempotent')
    asset = Path(__file__).resolve().parent.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleoclockwatch.inl'
    worker = asset.read_text(encoding='ascii')
    writer = worker[worker.index('static TInt HtcleoClockThread'):worker.index('static void HtcleoClockObserve')]
    if 'classicTimer' in writer or '.After(' in writer or '.Cancel(' in writer:
        raise SystemExit('high-resolution witness depends on ordinary timer')
    if worker.count('EPriorityAbsoluteForegroundNormal') != 2:
        raise SystemExit('both diagnostic threads require fixed priority12')
    if any(x in worker for x in ('DrawNow(', 'SetOrdinalPosition(', 'RequestComplete(',
                                  'HtcleoI2c', 'EHalGroupPlatformSpecific2, 10')):
        raise SystemExit('clock watcher must not mutate UI or controller')
    if not args.check:
        if after != before:
            source.write_text(after, encoding='latin-1')
        if not args.restore:
            (source.parent / 'htcleoclockwatch.inl').write_text(worker, encoding='ascii')
    if args.restore:
        print('HTCLEO_CLOCK_WATCH=761-frozen-no-worker-exact760-control')
    else:
        print('HTCLEO_CLOCK_WATCH=split-tester-writer-absolute12-highres5s-classic4s-readonly-hal-1m-ring')


if __name__ == '__main__':
    main()
