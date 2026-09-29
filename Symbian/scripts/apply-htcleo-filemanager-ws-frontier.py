#!/usr/bin/env python3
"""891: first16 FileManager WS transactions; no native dispatch policy change."""
import argparse
import hashlib
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/uifw/AvKon/src')
BASE = {'AknAppUi.cpp': '187ebdc34d9418cb7e4d7d13572cff8f21c318661bf104aaa65d1110c9c08342'}
HELPER = 'htcleofmws891.inl'
INC = '#include "' + HELPER + '"\n'
INC_ANCHOR = 'CAknAppUiExtension* CAknAppUiExtension::NewL()\n'
START = 'EXPORT_C void CAknAppUi::HandleWsEventL(const TWsEvent& aEvent,CCoeControl* aDestination)\n    {\n'
END = 'TBool CAknAppUi::SimulateHashKeyMarkingEventL('
SID_LINE = '    const TUint32 htcleoGsFocusSid = RProcess().SecureId().iId;\n'
MARKER = ' // HTCLEO_FM_WS_BOUNDARY_891'
INIT = '''    //891: existing32-bit private flags bits6-10 only; native0-4 and focus-probe5 stay.
    TUint htcleoFmWsSerial = 0;
    TUint32 htcleoFmWsDetail = 0;
    if (htcleoGsFocusSid == 0x101f84ebu && iExtension)
        {
        const TInt htcleoPointerType = aEvent.Type() == EEventPointer ?
            (TInt)aEvent.Pointer()->iType : -1;
        htcleoFmWsSerial = HtcleoFmWsTake(htcleoGsFocusSid, aEvent.Type(),
            htcleoPointerType, iExtension->iFlags);
        htcleoFmWsDetail = (htcleoFmWsSerial << 16) |
            ((TUint32)htcleoPointerType & 0xffffu);
        }
'''

def log(stage, indent='    '):
    return indent + 'if (htcleoFmWsSerial) HtcleoFmWsLog(0x%04xu, aEvent.Type(), htcleoFmWsDetail);' % stage + MARKER + '\n'

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('891 anchor drift ' + repr(old))
    return text.replace(old, new, 1)

def body_transform(text, restore=False):
    begin = text.index(START)
    end = text.index(END, begin)
    body = text[begin:end]
    if restore:
        body, count = re.subn(r'(?m)^[ \t]*if \(htcleoFmWsSerial\) HtcleoFmWsLog\([^\n]*\); // HTCLEO_FM_WS_BOUNDARY_891\n', '', body)
        if count != 9:
            raise ValueError('891 expected9 observer sites, got ' + str(count))
        body = once(body, SID_LINE + INIT, SID_LINE)
    else:
        body = once(body, SID_LINE, SID_LINE + INIT + log(0xd400))
        call = '        CAknAppUiBase::HandleWsEventL(aEvent, aDestination);\n'
        body = once(body, call, log(0xd401, '        ') + call + log(0xd402, '        '))
        body, count = re.subn(r'(?m)^([ \t]*)return;',
            lambda m: log(0xd404, m[1]) + m[0], body)
        if count != 5:
            raise ValueError('891 expected5 native early returns, got ' + str(count))
        tail = '    }\n    \n// This method watches for hash key presses'
        body = once(body, tail, log(0xd403) + tail)
    return text[:begin] + body + text[end:]

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong891 source')
    if INC in text:
        text = body_transform(text, True)
        text = once(text, INC, '')
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact890 AppUi source')
    if not restore:
        text = once(text, INC_ANCHOR, INC + INC_ANCHOR)
        text = body_transform(text)
    return text

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    path = a.root / REL / 'AknAppUi.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, 'AknAppUi.cpp', a.restore)
    if transform(new, 'AknAppUi.cpp', True) != transform(old, 'AknAppUi.cpp', True):
        raise ValueError('891 inverse')
    if not a.restore:
        if transform(new, 'AknAppUi.cpp') != new:
            raise ValueError('891 idempotence')
        (a.root / REL / HELPER).write_bytes(
            (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / HELPER).read_bytes())
    if old != new:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_FILEMANAGER_WS=' + ('restored' if a.restore else
          'FileManager-first16-WS-and-button-edges-FMWS64-private-bits6-10-native-dispatch'))

if __name__ == '__main__':
    main()
