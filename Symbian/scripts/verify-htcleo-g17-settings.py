#!/usr/bin/env python3
"""Settings-only guard against the explicitly pinned functional parent."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROM = runpy.run_path(str(HERE / 'verify-htcleo-gate17-entry.py'))
PARENTS = {
    '778-symbian3-full-english-font-settings-entry-incremental':
        '52134621bdc38bc77e958e99322513fe23a05affc0fe73310eff86735569475f',
    '781-symbian3-full-packed-layout-ipc-trace-incremental':
        '1fb5e8e52b390a67e95854c4e04886142c545a974d87035d2c1394aed6c673d4',
    '785-symbian3-full-matrix-local-fade-guard-incremental':
        'fc1b637222feac7be57b33f40ab5075c4722a9469e647308ff8508d6580c487f',
    '787-symbian3-full-settings-worker-observe-on-785-incremental':
        '4f8ce13f803417d46b52ef46db39a9417f6745eaf75fe7ca4abbfcfda7a06ac7',
    '788-symbian3-full-settings-worker-state-incremental':
        '4e42574a1e99604929f41db7d7a7dfc806256e8b5f7d842bbeee601a612ad096',
    '790-symbian3-full-settings-query-off-control-incremental':
        '961b221099cc0cbbb40d10b3be113806cfb92c9c6fd9ac9843b200c54b6d8969',
}
CHANGED = '/root/symbian3-full/epoc32/release/armv5/urel/ailaunch.exe'
WORKER = Path('/root/symbian3-full/sf/mw/homescreensrv/idlefw/hslaunch/src/htcleog17settings.inl')
STATE_INCLUDE = '#ifdef HTCLEO_G17_WORKER_STATE_V1\n#include "htcleog17state.inl"\n#endif\n'
STATE_SAMPLE = ('#ifdef HTCLEO_G17_WORKER_STATE_V1\n'
                '        if (result == KErrNone) HtcleoObserveG17State(fs, sequence - 1u);\n#endif\n')


def validate_direct_registration(before, after, watch_before, watch_after, state_before, state_after):
    if watch_before != watch_after or state_before != state_after:
        raise ValueError('791 cannot change790 activation/observer/sink')
    begin = '    // HTCLEO_G17_DIRECT_REGISTRATION_BEGIN\n'
    end = '    // HTCLEO_G17_DIRECT_REGISTRATION_END\n'
    if after.count(begin) != 1 or after.count(end) != 1:
        raise ValueError('partial direct-registration gate')
    start, finish = after.index(begin), after.index(end) + len(end)
    block = after[start:finish]
    expected = '''    // HTCLEO_G17_DIRECT_REGISTRATION_BEGIN
    const TBool directRegistration = gHtcleoG17SkipAppInfoQuery;
    if (directRegistration)
        {
        // Intent only:0231 is not a native completion or invented NotFound.
        HtcleoG17SettingsLog(0x0231, KErrNone, (TUint32)settings.iUid);
        }
    else
        {
        r = apa.GetAppInfo(info, settings);
        HtcleoG17SettingsLog(0x0211, r, settings.iUid);
        }
    // HTCLEO_G17_DIRECT_REGISTRATION_END
'''
    if block != expected:
        raise ValueError('direct branch must not perform the preliminary query')
    old_start = before.index('    // HTCLEO_G17_QUERY_OFF_BRANCH_BEGIN\n')
    old_finish = before.index('    if (r == KErrNotFound)\n', old_start)
    restored = after[:start] + before[old_start:old_finish] + after[finish:]
    pairs = (
        ('    if (directRegistration || r == KErrNotFound)\n', '    if (r == KErrNotFound)\n'),
        ('        if (!directRegistration && r == KErrNone)\n', '        if (r == KErrNone)\n'),
        ('// 791: keep both GetAppInfo queries disabled; register the trusted ROM entry.\n',
         '// 790 A/B: retain native query imports/code, but do not execute the query.\n'),
    )
    for new, old in pairs:
        if restored.count(new) != 1:
            raise ValueError('partial791 native registration routing')
        restored = restored.replace(new, old, 1)
    if restored != before:
        raise ValueError('791 changed outside declared790 registration delta')
    if after.count('apa.ForceRegistration(') != 1 or after.count('static volatile TBool gHtcleoG17SkipAppInfoQuery = ETrue;') != 1:
        raise ValueError('must keep one real ForceRegistration and both queries disabled')


def strip_query_off_control(text):
    for prefix in ('// HTCLEO_G17_QUERY_OFF_CONTROL', '    // HTCLEO_G17_QUERY_OFF_BRANCH'):
        begin, end = prefix + '_BEGIN\n', prefix + '_END\n'
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError('partial790 query-off control')
        start, finish = text.index(begin), text.index(end) + len(end)
        if prefix.startswith('//') and text[finish:finish+1] == '\n':
            finish += 1
        text = text[:start] + text[finish:]
    return text


def validate_query_off_control(before, after, watch_before, watch_after, reference_state, current_state):
    if strip_query_off_control(after) != before:
        raise ValueError('790 changes beyond the query-off gate')
    if watch_before != watch_after or reference_state != current_state:
        raise ValueError('790 must preserve788 Matrix sampling and exact789 activation control')
    if after.count('gHtcleoG17SkipAppInfoQuery') != 2 or 'static volatile TBool gHtcleoG17SkipAppInfoQuery = ETrue;' not in after:
        raise ValueError('query-off gate must be volatile, enabled and never reassigned')
    begin = after.index('    // HTCLEO_G17_QUERY_OFF_BRANCH_BEGIN')
    finish = after.index('    // HTCLEO_G17_QUERY_OFF_BRANCH_END')
    branch = after[begin:finish]
    if ('HtcleoG17SettingsLog(0x0230, KErrNotSupported, 0x4e4f5152u);' not in branch or
            'CleanupStack::PopAndDestroy(&apa);' not in branch or 'return;' not in branch):
        raise ValueError('query-off control must log NOT-ATTEMPTED and close native session')
    if not after.index('CleanupClosePushL(apa);') < after.index('TApaAppInfo info;') < begin < finish < after.index('apa.GetAppInfo('):
        raise ValueError('control must retain Connect and stop before GetAppInfo')


def apparc_imports(dump):
    result, current, remaining = {}, None, 0
    for line in dump.splitlines():
        module = re.fullmatch(r'(\d+) imports? from (\S+)', line)
        if module:
            if current and remaining:
                raise ValueError('incomplete AppArc import dump')
            name = module[2].split('{')[0]
            current = name if name in ('apgrfx', 'apparc') else None
            remaining = int(module[1]) if current else 0
            if current:
                result[current] = []
        elif current and remaining:
            entry = re.fullmatch(r'\s*(\d+)(?: offset by (\d+))?\s*', line)
            if entry:
                result[current].append((int(entry[1]), int(entry[2] or 0)))
                remaining -= 1
    if (current and remaining) or set(result) != {'apgrfx', 'apparc'}:
        raise ValueError('native AppArc imports missing')
    return result


def validate_deferred_worker(before, after, watch_before, watch_after, state_before, state_after):
    if before != after or watch_before != watch_after:
        raise ValueError('789 must keep788 worker and Matrix sampler exactly')
    begin = '// HTCLEO_G17_DEFERRED_ACTIVATION_BEGIN\n'
    end = '// HTCLEO_G17_DEFERRED_ACTIVATION_END\n'
    if state_after.count(begin) != 1 or state_after.count(end) != 1:
        raise ValueError('partial deferred activation controller')
    start, finish = state_after.index(begin), state_after.index(end) + len(end)
    stripped = state_after[:start] + state_after[finish:]
    for header in ('#include <e32property.h>\n', '#include <ssm/startupdomainpskeys.h>\n'):
        if stripped.count(header) != 1:
            raise ValueError('unexpected activation includes')
        stripped = stripped.replace(header, '', 1)
    new = '''    const TBool event = HtcleoMaybeActivateG17(aSequence);
    const TBool after = gHtcleoG17ActivationState == 1u &&
        aSequence == gHtcleoG17ActivationAt + 3u;
    if (!event && !after && aSequence != 1u && aSequence != 6u && aSequence != 12u) return;
    const TUint32 wireSequence = aSequence | (event ? 0x80000000u : 0u) |
        (after ? 0x40000000u : 0u);
'''
    if stripped.count(new) != 1:
        raise ValueError('unexpected deferred state record schedule')
    stripped = stripped.replace(new, '    if (aSequence != 1u && aSequence != 6u && aSequence != 12u) return;\n', 1)
    stripped = stripped.replace('{wireSequence, User::NTickCount()', '{aSequence, User::NTickCount()', 1)
    extra = '''processPriority,
        gHtcleoG17ActivationState, (TUint32)gHtcleoG17ActivationResult,
        gHtcleoG17ReadyCount, (TUint32)gHtcleoG17ReadyValue};'''
    if stripped.count(extra) != 1:
        raise ValueError('unexpected activation record fields')
    stripped = stripped.replace(extra, 'processPriority};', 1)
    def normalized(text):
        return re.sub(r'\s+', '', re.sub(r'//[^\n]*|/\*.*?\*/', '', text, flags=re.S))
    if normalized(stripped) != normalized(state_before):
        raise ValueError('unreviewed change to788 state collector/sink')


def validate_worker_state(before, after, watch_before, watch_after):
    """788 adds only RAM witnesses and three opt-in external state reads."""
    stripped = after
    for stage in range(1, 9):
        call = '    HtcleoG17Mark(%du);\n' % stage
        if stripped.count(call) != 1:
            raise ValueError('missing/duplicated RAM worker phase')
        stripped = stripped.replace(call, '', 1)
    publish = '    HtcleoG17PublishWorker(thread, r);\n'
    if stripped.count(publish) != 1:
        raise ValueError('missing/duplicated owned worker publication')
    stripped = stripped.replace(publish, '', 1)
    if stripped != before:
        raise ValueError('worker changed beyond RAM state witnesses; priority must stay787')
    for block in (STATE_INCLUDE, STATE_SAMPLE):
        if watch_after.count(block) != 1:
            raise ValueError('missing/duplicated opt-in external state read')
        watch_after = watch_after.replace(block, '', 1)
    if watch_after != watch_before:
        raise ValueError('original Matrix sampler/sink changed')


def validate_worker_control(before, after):
    """787: inverse the six witnesses and require785 worker tokens exactly."""
    calls = (
        'HtcleoHomeLog(0x484F02A0u, KErrNone, started ? 1u : 0u);',
        'HtcleoHomeLog(0x484F02A1u, r, (TUint32)thread.Handle());',
        'HtcleoHomeLog(0x484F02A2u, KErrNone, (TUint32)EPriorityLess);',
        'HtcleoHomeLog(0x484F02B0u, KErrNone, 0u);',
        'HtcleoHomeLog(0x484F02B1u, cleanup ? KErrNone : KErrNoMemory, cleanup ? 1u : 0u);',
        'HtcleoHomeLog(0x484F02B2u, r, 0u);',
    )

    def normalized(text):
        text = re.sub(r'//[^\n]*|/\*.*?\*/', '', text, flags=re.S)
        return re.sub(r'\s+', '', text)

    actual = normalized(after)
    for call in calls:
        call = normalized(call)
        if actual.count(call) != 1:
            raise ValueError('missing/duplicated/non785 startup witness: ' + call)
        actual = actual.replace(call, '', 1)
    if actual != normalized(before):
        raise ValueError('787 worker behavior differs from785 beyond six witnesses')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_recipe(old, new):
    if old != new:
        raise ValueError('Settings-only requires exact parent recipe, including sw.txt/fonts/SPI')


def validate_parent(name, digest):
    if name not in PARENTS or PARENTS[name] != digest:
        raise ValueError('not a pinned Settings parent')


def main():
    p = argparse.ArgumentParser()
    for name in ('parent', 'recipe', 'image', 'rom-log', 'report'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    parent_name = a.parent.parent.name
    parent_sha = sha(a.parent / 'initrd.gz')
    validate_parent(parent_name, parent_sha)
    worker_control = 'not-applicable'
    if parent_name == '785-symbian3-full-matrix-local-fade-guard-incremental':
        before = (a.parent / 'build/htcleog17settings.inl').read_text()
        current = (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics/htcleog17settings.inl').read_text()
        validate_worker_control(before, current)
        if WORKER.read_text() != current:
            raise ValueError('SDK worker differs from the checked787 source')
        worker_control = 'exact785-plus-six-startup-witnesses-priority-less'
    if parent_name == '787-symbian3-full-settings-worker-observe-on-785-incremental':
        assets = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics'
        current = (assets / 'htcleog17settings.inl').read_text()
        validate_worker_state((a.parent / 'build/htcleog17settings.inl').read_text(), current,
                              (a.parent / 'build/htcleokernelwatch.inl').read_text(),
                              (assets / 'htcleokernelwatch.inl').read_text())
        for local_name, sdk_name in (('htcleog17settings.inl', 'htcleog17settings.inl'),
                                    ('htcleokernelwatch.inl', 'htcleothreadwatch.inl'),
                                    ('htcleog17state.inl', 'htcleog17state.inl')):
            if (assets / local_name).read_text() != (WORKER.parent / sdk_name).read_text():
                raise ValueError('SDK observer input differs from checked788 source')
        worker_control = 'exact787-priority-and-rpc-ram-phases-three-external-samples'
    if parent_name == '788-symbian3-full-settings-worker-state-incremental':
        assets = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics'
        parent_build = a.parent / 'build'
        reference = a.parent.parent.parent / '789-symbian3-full-settings-deferred-activation-incremental/Symbian3'
        if sha(reference / 'initrd.gz') != '59097eee913f1a8216562ff16bd98897fb4c0e49a35e975204e790e5f98e3361':
            raise ValueError('frozen789 comparison package changed')
        validate_query_off_control((parent_build / 'htcleog17settings.inl').read_text(),
            (assets / 'htcleog17settings.inl').read_text(),
            (parent_build / 'htcleokernelwatch.inl').read_text(), (assets / 'htcleokernelwatch.inl').read_text(),
            (reference / 'build/htcleog17state.inl').read_text(), (assets / 'htcleog17state.inl').read_text())
        previous_imports = apparc_imports((reference / 'build/ailaunch-e32-dump.txt').read_text())
        current_imports = apparc_imports((HERE.parent / 'output/qsd8250-native-full-rom/ailaunch-e32-dump.txt').read_text())
        if previous_imports != current_imports:
            raise ValueError('query-off control changed AppArc import closure')
        for local_name, sdk_name in (('htcleog17settings.inl', 'htcleog17settings.inl'),
                                    ('htcleokernelwatch.inl', 'htcleothreadwatch.inl'),
                                    ('htcleog17state.inl', 'htcleog17state.inl')):
            if (assets / local_name).read_text() != (WORKER.parent / sdk_name).read_text():
                raise ValueError('SDK query-off control differs from checked790 source')
        worker_control = '788-base-exact789-deferred-activation-connect-close-retained-getappinfo-not-attempted'
    if parent_name == '790-symbian3-full-settings-query-off-control-incremental':
        assets = HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics'
        parent_build = a.parent / 'build'
        validate_direct_registration((parent_build / 'htcleog17settings.inl').read_text(),
            (assets / 'htcleog17settings.inl').read_text(),
            (parent_build / 'htcleokernelwatch.inl').read_text(), (assets / 'htcleokernelwatch.inl').read_text(),
            (parent_build / 'htcleog17state.inl').read_text(), (assets / 'htcleog17state.inl').read_text())
        if apparc_imports((parent_build / 'ailaunch-e32-dump.txt').read_text()) != apparc_imports(
                (HERE.parent / 'output/qsd8250-native-full-rom/ailaunch-e32-dump.txt').read_text()):
            raise ValueError('791 changed native AppArc import family')
        for local_name, sdk_name in (('htcleog17settings.inl', 'htcleog17settings.inl'),
                                    ('htcleokernelwatch.inl', 'htcleothreadwatch.inl'),
                                    ('htcleog17state.inl', 'htcleog17state.inl')):
            if (assets / local_name).read_text() != (WORKER.parent / sdk_name).read_text():
                raise ValueError('SDK direct registration differs from checked791 source')
        worker_control = 'exact790-activation-one-native-rom-force-registration-no-pre-or-post-getappinfo'
    validate_recipe((a.parent / 'build/htcleo_symbian3_full_native.oby').read_text(), a.recipe.read_text())
    cache = a.parent / 'build/incremental-release-cache'
    lines = (cache / 'RELEASE-CACHE-MANIFEST.tsv').read_text().splitlines()
    if len(lines) != 61:
        raise ValueError('expected61 parent binaries')
    changed = []
    for line in lines:
        digest, source, name = line.split('\t')
        if sha(cache / name) != digest:
            raise ValueError('immutable cache corrupted: ' + name)
        if sha(Path(source)) != digest:
            changed.append(source)
    if changed != [CHANGED]:
        raise ValueError('unexpected binary deltas: ' + repr(changed))
    old, new = (a.parent / 'initrd.gz').read_bytes(), a.image.read_bytes()
    files0 = ROM['rom_files'](old, (a.parent / 'build/ROMBUILD.LOG').read_text(errors='replace'))
    files1 = ROM['rom_files'](new, a.rom_log.read_text(errors='replace'))
    if set(files0) != set(files1):
        raise ValueError('ROM membership changed')
    count = 0
    for name in files0:
        if name.startswith('sys\\bin\\'):
            continue
        if ROM['file_data'](old, files0, name) != ROM['file_data'](new, files1, name):
            raise ValueError('resource bytes changed: ' + name)
        count += 1
    window = (len(new) + 1048575) // 1048576 * 1048576
    if window != 0x03a00000:
        raise ValueError('ROM/RAM boundary changed')
    result = dict(status='HTCLEO_G17_SETTINGS_ONLY_OK', parent=parent_name, parent_sha256=parent_sha,
                  changed_binary=CHANGED, changed_sha256=sha(Path(CHANGED)),
                  unchanged_binaries=60, preserved_resources=count,
                  rom_window=window, ram_start=0x12200000 + window,
                  payload_sha256=sha(a.image), font_changes=False,
                  software_version='exact778', worker_control=worker_control,
                  hardware_result='pending')
    a.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
