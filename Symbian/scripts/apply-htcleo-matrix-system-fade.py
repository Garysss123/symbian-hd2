#!/usr/bin/env python3
"""785: mirror the tested Home fade fallback for Matrix's zero session only."""
import argparse
from pathlib import Path

INC = '#include "htcleomatrixfade.inl"\n'
ANCHOR = 'else if (htcleoHomeSystemFade && htcleoAknSrvHandle == 0)'
GET_START = 'TBool CAknSgcClient::DoIsSystemFaded() const'
GET_END = 'void CAknSgcClient::SetLegacyOrientationAndScreenModeAppUiFlags('
SET_START = 'void CAknSgcClient::DoSetSystemFaded(TBool aFade)'
SET_END = GET_START
GET_NEW = '''else if (htcleoAknSrvHandle == 0 &&
		RProcess().SecureId().iId == 0x101f4cd2u)
		{
		// HTCLEO_MATRIX_SYSTEM_FADE_GET_V1
		// No session exists. Preserve the real local flag, not a forced false.
		HtcleoMatrixFadeLog(0x2500u, iFlags[ESystemFaded], htcleoAknSrvHandle);
		return iFlags[ESystemFaded];
		}
	''' + ANCHOR
SET_NEW = '''else if (htcleoAknSrvHandle == 0 &&
		RProcess().SecureId().iId == 0x101f4cd2u)
		{
		// HTCLEO_MATRIX_SYSTEM_FADE_SET_V1
		// Match the existing Home missing-session policy: retain requested state.
		iFlags.Assign(ESystemFaded, aFade);
		HtcleoMatrixFadeLog(0x2501u, iFlags[ESystemFaded], htcleoAknSrvHandle);
		}
	''' + ANCHOR


def transform(source, restore=False):
    installed = INC in source
    if not installed and 'HTCLEO_MATRIX_SYSTEM_FADE_' in source:
        raise ValueError('partial Matrix fade overlay')
    if installed:
        if source.count(INC) != 1 or source.count(GET_NEW) != 1 or source.count(SET_NEW) != 1:
            raise ValueError('partial Matrix fade overlay')
        source = source.replace(GET_NEW, ANCHOR, 1).replace(SET_NEW, ANCHOR, 1).replace(INC, '', 1)
    if not restore:
        for start, end, new in ((SET_START, SET_END, SET_NEW), (GET_START, GET_END, GET_NEW)):
            if source.count(start) != 1 or source.count(end) != 1:
                raise ValueError('fade method boundaries changed')
            a, b = source.index(start), source.index(end)
            body = source[a:b]
            if b <= a or body.count(ANCHOR) != 1:
                raise ValueError('existing Home fallback changed')
            source = source[:a] + body.replace(ANCHOR, new, 1) + source[b:]
        # This file already uses Symbian headers; include immediately before
        # the first function definition, after its existing includes.
        anchor = '#include <eikenv.h>\n'
        if source.count(anchor) != 1:
            raise ValueError('fade include anchor changed')
        source = source.replace(anchor, anchor + INC, 1)
    return source


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / 'sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, a.restore)
    if not a.restore:
        if transform(new) != new or transform(new, True) != transform(old, True):
            raise ValueError('fade overlay not exactly reversible/idempotent')
        body = (Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleomatrixfade.inl').read_text()
        for forbidden in ('Flush(', 'Replace(', 'SetPriority', 'RTimer', 'static TInt', 'Dll::SetTls', 'HalFunction'):
            if forbidden in body:
                raise ValueError('out-of-scope fade witness: ' + forbidden)
        (path.parent / 'htcleomatrixfade.inl').write_text(body)
    if new != old:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_MATRIX_SYSTEM_FADE=' + ('restored' if a.restore else 'sid-101f4cd2-zero-session-local-get-set-real-session-stock'))


if __name__ == '__main__':
    main()
