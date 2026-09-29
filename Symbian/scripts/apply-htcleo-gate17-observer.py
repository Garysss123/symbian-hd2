#!/usr/bin/env python3
"""One temporary worker after Home creation; never blocks the launcher thread."""
import argparse
from pathlib import Path

INC = '#include "htcleogate17observer.inl"\n'
OLD = '        HtcleoWatchHomeProcess(process.Id());\n'
NEW = OLD + '        HtcleoStartGate17Observer(); // HTCLEO_GATE17_OBSERVER_V1\n'
OLD_LIBS = '\n// HTCLEO_GATE17_OBSERVER_LIBS_V1\nLIBRARY apgrfx.lib fbscli.lib bitgdi.lib gdi.lib ecom.lib\n'
LIBS = '\n// HTCLEO_GATE17_OBSERVER_LIBS_V1\nLIBRARY apgrfx.lib apparc.lib fbscli.lib bitgdi.lib gdi.lib ecom.lib\n'


def transform(source, mmp, restore=False):
    if INC in source:
        found_libs = [item for item in (OLD_LIBS, LIBS) if mmp.count(item) == 1]
        if source.count(INC) != 1 or source.count(NEW) != 1 or len(found_libs) != 1:
            raise ValueError('partial Gate17 observer hook')
        source, mmp = source.replace(NEW, OLD, 1).replace(INC, '', 1), mmp.replace(found_libs[0], '', 1)
    elif 'HTCLEO_GATE17_OBSERVER' in source + mmp:
        raise ValueError('partial Gate17 observer')
    if not restore:
        anchor = '#include "htcleothreadwatch.inl"\n'
        if source.count(anchor) != 1 or source.count(OLD) != 1:
            raise ValueError('existing Home watcher anchor changed')
        source = source.replace(anchor, anchor + INC, 1).replace(OLD, NEW, 1)
        mmp += LIBS
    return source, mmp


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    component = a.root / 'sf/mw/homescreensrv/idlefw/hslaunch'
    src, mmp = component / 'src/hslaunch.cpp', component / 'group/hslaunch.mmp'
    old = (src.read_text(encoding='latin-1'), mmp.read_text())
    updated = transform(*old, restore=a.restore)
    if not a.restore:
        if transform(*updated) != updated or transform(*updated, restore=True) != transform(*old, restore=True):
            raise ValueError('observer not exactly reversible/idempotent')
        body = (Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleogate17observer.inl').read_text()
        for forbidden in ('RWsSession', 'SetOrdinal', 'SendEvent', 'CreateWindow', 'file.Replace', 'file.Flush', 'fs.Delete'):
            if forbidden in body:
                raise ValueError('observer exceeds read-only off-screen scope: ' + forbidden)
        (component / 'src/htcleogate17observer.inl').write_text(body)
    if updated != old:
        src.write_text(updated[0], encoding='latin-1')
        mmp.write_text(updated[1])
    print('HTCLEO_GATE17_OBSERVER=' + ('restored' if a.restore else 'two-samples-offscreen-20s-30s-1m-cap'))


if __name__ == '__main__':
    main()
