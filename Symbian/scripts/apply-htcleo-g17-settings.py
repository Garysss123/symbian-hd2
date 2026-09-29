#!/usr/bin/env python3
"""Reversible Settings-only worker; leave native launcher/watch behavior intact."""
import argparse
from pathlib import Path

INC = '#include "htcleog17settings.inl"\n'
STATE_DEFINE = '#define HTCLEO_G17_WORKER_STATE_V1\n'
OLD = '        HtcleoWatchHomeProcess(process.Id());\n'
NEW = OLD + '        HtcleoStartG17Settings(); // HTCLEO_G17_SETTINGS_V1\n'
LIBS = '\n// HTCLEO_G17_SETTINGS_LIBS_V1\nLIBRARY apgrfx.lib apparc.lib\n'


def transform(source, mmp, restore=False):
    if INC in source:
        if source.count(INC) != 1 or source.count(NEW) != 1 or mmp.count(LIBS) != 1:
            raise ValueError('partial Settings-only hook')
        source = source.replace(NEW, OLD, 1).replace(INC, '', 1)
        if source.count(STATE_DEFINE) > 1:
            raise ValueError('duplicated worker state opt-in')
        source = source.replace(STATE_DEFINE, '', 1)
        mmp = mmp.replace(LIBS, '', 1)
    elif 'HTCLEO_G17_SETTINGS' in source + mmp or STATE_DEFINE in source:
        raise ValueError('partial Settings-only hook')
    if not restore:
        if 'htcleogate17observer' in source or 'HTCLEO_GATE17_OBSERVER' in mmp:
            raise ValueError('779 font observer must be restored first')
        anchor = '#include "htcleothreadwatch.inl"\n'
        if source.count(anchor) != 1 or source.count(OLD) != 1:
            raise ValueError('Home watcher anchor changed')
        source = source.replace(anchor, STATE_DEFINE + anchor + INC, 1).replace(OLD, NEW, 1)
        mmp += LIBS
    return source, mmp


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    component = a.root / 'sf/mw/homescreensrv/idlefw/hslaunch'
    src, mmp = component / 'src/hslaunch.cpp', component / 'group/hslaunch.mmp'
    old = src.read_text(encoding='latin-1'), mmp.read_text()
    new = transform(*old, restore=a.restore)
    if not a.restore:
        if transform(*new) != new or transform(*new, restore=True) != transform(*old, restore=True):
            raise ValueError('Settings hook not reversible/idempotent')
        body = (Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleog17settings.inl').read_text()
        for forbidden in ('RFbs', 'EComSession', 'RWsSession', 'SetOrdinal', 'SendEvent', 'file.Flush', 'file.Replace', 'fs.Delete'):
            if forbidden in body:
                raise ValueError('out-of-scope operation: ' + forbidden)
        (component / 'src/htcleog17settings.inl').write_text(body)
        state = Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleog17state.inl'
        (component / 'src/htcleog17state.inl').write_text(state.read_text())
    if new != old:
        src.write_text(new[0], encoding='latin-1')
        mmp.write_text(new[1])
    print('HTCLEO_G17_SETTINGS=' + ('restored' if a.restore else 'home-ready-single-rom-registration-worker'))


if __name__ == '__main__':
    main()
