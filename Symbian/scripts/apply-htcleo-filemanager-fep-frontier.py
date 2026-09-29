#!/usr/bin/env python3
"""887: bounded FileManager FEP startup observation; all native policy retained."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = Path('sf/mw/classicui/lafagnosticuifoundation/cone/src')
HELPER = 'htcleofmfep887.inl'
BASE = {
    'COEFEP.CPP': 'de0e27e17a8517b9b67111a80350a7eaba6b5cca700e2f14158ce0bea6ceb65b',
    'COEMAINSECUREFEP.CPP': '6e7e0f34efc3968c592925e12c1c466e700228e39d51196c0e0f8bc11e3aa59e',
}
INC = '#include "' + HELPER + '"\n'

def log(stage, result='KErrNone', detail='0u'):
    return '\tHtcleoFmFepLog(0x%04xu, %s, %s);\n' % (stage, result, detail)

EDITS = {
 'COEFEP.CPP': [
    ('#include "coedefkeys.h"\n', '#include "coedefkeys.h"\n' + INC),
    ('void CCoeFepLoader::RunL()\n\t{\n\tiCoeEnv.EnsureCorrectFepIsLoadedL();\n',
     'void CCoeFepLoader::RunL()\n\t{\n' + log(0xf100, 'iStatus.Int()', '(TUint32)iFirstRunL') +
     '\tiCoeEnv.EnsureCorrectFepIsLoadedL();\n' + log(0xf101)),
    ('    delete this;\n\t}\n\nTInt CCoeFepLoader::RunError',
     log(0xf102) + '    delete this;\n\t}\n\nTInt CCoeFepLoader::RunError'),
    ('TInt CCoeFepLoader::RunError(TInt aError)\n\t{\n',
     'TInt CCoeFepLoader::RunError(TInt aError)\n\t{\n' + log(0xf103, 'aError')),
 ],
 'COEMAINSECUREFEP.CPP': [
    ('#include <ecom/ecom.h>\n', '#include <ecom/ecom.h>\n' + INC),
    ('void CCoeEnv::EnsureSpecifiedFepIsLoadedL(TUid aFepUid)\n\t{\n',
     'void CCoeEnv::EnsureSpecifiedFepIsLoadedL(TUid aFepUid)\n\t{\n' +
     log(0xf110, 'aFepUid.iUid', '(TUint32)iExtra->iFep.iFepUid.iUid')),
    ('\t\t\tnewFep.iFepPlugIn = CCoeFepPlugIn::NewL(aFepUid);\n',
     log(0xf111, detail='(TUint32)aFepUid.iUid') +
     '\t\t\tnewFep.iFepPlugIn = CCoeFepPlugIn::NewL(aFepUid);\n' +
     log(0xf112, detail='(TUint32)newFep.iFepPlugIn')),
    ('\t\t\tnewFep.iFep = newFep.iFepPlugIn->NewFepL(*this, *dummyFepParameters);\n',
     log(0xf113, detail='(TUint32)aFepUid.iUid') +
     '\t\t\tnewFep.iFep = newFep.iFepPlugIn->NewFepL(*this, *dummyFepParameters);\n' +
     log(0xf114, detail='(TUint32)newFep.iFep')),
    ('\t\t\tCleanupStack::Pop(&newFep);\n\t\t\tCCoeEnvExtra::DestroyFep(iExtra->iFep);\n',
     '\t\t\tCleanupStack::Pop(&newFep);\n' + log(0xf115) +
     '\t\t\tCCoeEnvExtra::DestroyFep(iExtra->iFep);\n' + log(0xf116)),
    ('\t\t\tiExtra->iFep = newFep;\n\t\t\tiExtra->HandleChangeInLoadedFep();\n',
     '\t\t\tiExtra->iFep = newFep;\n' + log(0xf117) +
     '\t\t\tiExtra->HandleChangeInLoadedFep();\n' + log(0xf118)),
    ('\t\t\t}\n\t\t}\n\t}\n\nstatic void CleanupResetEComImpArray',
     '\t\t\t}\n\t\t}\n' + log(0xf119) + '\t}\n\nstatic void CleanupResetEComImpArray'),
 ],
}

def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('887 anchor drift: ' + repr(old))
    return text.replace(old, new, 1)

def transform(text, name, restore=False):
    if name not in BASE:
        raise ValueError('wrong887 source')
    if INC in text:
        for old, new in reversed(EDITS[name]):
            text = once(text, new, old)
    if hashlib.sha256(text.encode('latin-1')).hexdigest() != BASE[name]:
        raise ValueError('not exact886 FEP source: ' + name)
    if not restore:
        for old, new in EDITS[name]:
            text = once(text, old, new)
    return text

def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    changes = []
    for name in BASE:
        path = a.root / REL / name
        old = path.read_text(encoding='latin-1')
        new = transform(old, name, a.restore)
        if transform(new, name, True) != transform(old, name, True):
            raise ValueError('887 inverse')
        if not a.restore and transform(new, name) != new:
            raise ValueError('887 idempotence')
        changes.append((path, old, new))
    for path, old, new in changes:
        if old != new:
            path.write_text(new, encoding='latin-1')
    if not a.restore:
        (a.root / REL / HELPER).write_bytes(
            (HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / HELPER).read_bytes())
    print('HTCLEO_FILEMANAGER_FEP=' + ('restored' if a.restore else
          'FileManager-only-FEP-loader-plugin-cleanup32-FMFEP-no-policy-change'))

if __name__ == '__main__':
    main()
