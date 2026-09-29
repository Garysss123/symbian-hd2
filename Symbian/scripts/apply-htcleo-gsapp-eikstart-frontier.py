#!/usr/bin/env python3
"""807: local native EikStart pre-factory edges; shared EikCore unchanged."""
import argparse
import hashlib
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
LOWER = runpy.run_path(str(HERE / 'apply-htcleo-gsapp-startup-observer.py'))
UPSTREAM = runpy.run_path(str(HERE / 'apply-htcleo-eikstart-homescreen-trace.py'))
REL = LOWER['REL']
NAME = 'Src/GSApp.cpp'
EIKSTART_REL = Path('sf/mw/classicui/commonuisupport/uikon/coresrc/EIKSTART.CPP')
EIKSTART_SHA = 'a08868e67061c56c025378ef57655e1c9f806d31e041fbc872193557ab647ae3'
INC = '#include "htcleogseikstart.inl"\n'
OLD_CALL = '    const TInt result = EikStart::RunApplication( NewApplication );'
NEW_CALL = '''    HtcleoGsBootLog(0x6002u, KErrNone, 0u); // prior entry log returned
    const TInt result = HtcleoGsRunApplication( NewApplication );'''
PREFIX = '''// Derived from the pinned native EIKSTART.CPP, not MatrixMenu's bypasses.
// Copyright (c) 1997-2009 Nokia Corporation and/or its subsidiary(-ies).
// Eclipse Public License v1.0, same as the source EikStart implementation.
#include <eikenv.h>
#include <f32file.h>
#if defined(_DEBUG) || defined(ALLOC_COUNTING)
#error This local EikStart derivation is verified only for UREL
#endif

class CHtcleoGsEikonEnv : public CEikonEnv
    {
public:
    TInt HtcleoConstructorError() const { return CoeEnvConstructorError(); }
    };
// CEikonEnv::ConstructorError in the pinned shared source is this same accessor.
// No fields or virtual overrides. Constructor errors are NOT ignored.
__ASSERT_COMPILE(sizeof(CHtcleoGsEikonEnv) == sizeof(CEikonEnv));

'''


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('GSApp EikStart anchor drift: ' + repr(old))
    return text.replace(old, new, 1)


def helper(source):
    if hashlib.sha256(source.encode('latin-1')).hexdigest() != EIKSTART_SHA:
        raise ValueError('shared EikStart source changed from806')
    start, end = UPSTREAM['find_function'](source)
    text = source[start:end]
    if text != UPSTREAM['FUNCTION']:
        raise ValueError('not exact pinned native EikStart body')
    text = once(text, 'EXPORT_C TInt EikStart::RunApplication', 'static TInt HtcleoGsRunApplication')
    text = once(text, '\tconst TBool htcleoHome =\n\t\t(RProcess().SecureId().iId == 0x102750F0u);\n', '')
    text, count = re.subn(r'^\s*if \(htcleoHome\)\n', '\n', text, flags=re.M)
    if count != 19:
        raise ValueError('unexpected native diagnostic stage count')
    text = text.replace('HtcleoHomeEikStartLog', 'HtcleoGsBootLog')
    for stage in range(19):
        text = once(text, '0x485900%02Xu' % stage, '0x%04xu' % (0x6070 + stage))
    text = once(text, 'CEikonEnv* env = new CEikonEnv;', 'CHtcleoGsEikonEnv* env = new CHtcleoGsEikonEnv;')
    text = once(text, 'env->ConstructorError()', 'env->HtcleoConstructorError()')
    return PREFIX + text + '\n'


def transform(text, restore=False):
    if INC in text:
        text = once(text, INC, '')
        text = once(text, NEW_CALL, OLD_CALL)
    elif 'HtcleoGsRunApplication' in text or '0x6002u' in text:
        raise ValueError('partial GSApp local EikStart overlay')
    original = LOWER['transform'](text, NAME, True)
    parent = LOWER['transform'](original, NAME)
    if restore:
        return text  # exact lower layer or exact original accepted by LOWER
    if text != parent:
        raise ValueError('apply806 observer before807 local EikStart')
    text = once(text, '#include "htcleogsboot.h"\n', '#include "htcleogsboot.h"\n' + INC)
    return once(text, OLD_CALL, NEW_CALL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    path = args.root / REL / NAME
    old = path.read_text(encoding='latin-1')
    new = transform(old, args.restore)
    if not args.restore:
        if transform(new) != new or transform(new, True) != transform(old, True):
            raise ValueError('GSApp EikStart inverse/idempotence mismatch')
        text = helper((args.root / EIKSTART_REL).read_text(encoding='latin-1'))
        path.with_name('htcleogseikstart.inl').write_text(text, encoding='latin-1')
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_GSAPP_EIKSTART=' + ('restored' if args.restore else 'native-local-6002-6070-6082-no-bypass-shared-eikcore-unchanged'))


if __name__ == '__main__':
    main()
