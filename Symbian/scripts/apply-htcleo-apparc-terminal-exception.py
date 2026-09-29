#!/usr/bin/env python3
"""873: only APSEXE's startup installs a terminal-only exception observer."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/appsupport/appfw/apparchitecture/apsexe/APSMAIN.CPP')
HELPER = 'htcleoaparcexception873.inl'
BASE_SHA = '838188a10d210371b514585477a14be237283ccc25daa93a8ead462865a41eae'
MMP = Path('sf/mw/appsupport/appfw/apparchitecture/group/APSEXE.MMP')
MMP_SHA = 'ad69c47ebde76ea25bb3a15fc452db8df0d0742987b4555a67f6e5a0d9877f50'
MMP_OLD = 'library  euser.lib  apserv.lib\n'
MMP_NEW = MMP_OLD + 'library  efsrv.lib //873 terminal-only file writer\n'
ANCHOR = '#endif //SYMBIAN_ENABLE_SPLIT_HEADERS\n'
INCLUDE = '#include "htcleoaparcexception873.inl" // HTCLEO_APPARC_TERMINAL_873\n'
OLD = '\treturn ApaServThreadStart();\n'
NEW = '\t(void)HtcleoApaInstallExceptionObserver();\n' + OLD
POLICY = 'APSEXE-only-no-existing-handler-APX1-terminal1024-stack224-no-startup-IO-restore-reraise'


def transform(text, restore=False):
    if INCLUDE in text:
        if text.count(INCLUDE) != 1 or text.count(NEW) != 1:
            raise ValueError('partial873 observer')
        text = text.replace(INCLUDE, '', 1).replace(NEW, OLD, 1)
    if hashlib.sha256(text.encode()).hexdigest() != BASE_SHA:
        raise ValueError('873 requires exact872 APSEXE main')
    if restore:
        return text
    if text.count(ANCHOR) != 1 or text.count(OLD) != 1:
        raise ValueError('873 startup anchor drift')
    return text.replace(ANCHOR, ANCHOR + INCLUDE, 1).replace(OLD, NEW, 1)


def transform_mmp(text, restore=False):
    if MMP_NEW in text:
        text = text.replace(MMP_NEW, MMP_OLD, 1)
    if hashlib.sha256(text.encode()).hexdigest() != MMP_SHA:
        raise ValueError('873 MMP/stack/heap/capability drift')
    if restore:
        return text
    if text.count(MMP_OLD) != 1:
        raise ValueError('873 MMP library anchor drift')
    return text.replace(MMP_OLD, MMP_NEW, 1)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL
    old = path.read_text()
    new = transform(old, a.restore)
    mmp_path = a.root / MMP
    mmp_old = mmp_path.read_text()
    mmp_new = transform_mmp(mmp_old, a.restore)
    if transform(new, True) != transform(old, True):
        raise ValueError('873 inverse failed')
    if not a.restore:
        (path.parent / HELPER).write_bytes((HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / HELPER).read_bytes())
    if old != new:
        path.write_text(new)
    if mmp_old != mmp_new:
        mmp_path.write_text(mmp_new)
    print('HTCLEO_APPARC_TERMINAL_EXCEPTION=' + ('restored' if a.restore else POLICY))
