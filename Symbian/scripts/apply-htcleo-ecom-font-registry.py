#!/usr/bin/env python3
"""862: observe FreeType discovery/security in RAM, preserve861 behavior exactly."""
import argparse
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path('sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame')
BASE = {
    'EComServerStart.cpp': 'c6660100da7de0f4b5a50313a4985105523cfee17a9a2c725f24f3886ed7b612',
    'RegistryData.cpp': '0f76051a8242712f5117fe19feb761f02cbd24c6fcb726c45688d175b6c0fd48',
    'Registrar.cpp': '96ee1f609ab79f7eb8fd467425104d060a29193a0d5692021da0eda416e7cdca',
    'htcleoecserverexception.inl': 'df4f8c30ad380b151dc0364453f295b880d4a1e3220326181725888e78d0e746',
}
MARKER = 'HTCLEO_ECOM_FONT_REGISTRY_862'
POLICY = 'FreeType-only-RAM28-registration-index-security-snapshot-in-existing-ECX2-no-new-file-writes'
INC = '#include "htcleoecfontregistry.h" // ' + MARKER + '\n'
EDITS = {
    'EComServerStart.cpp': [
        ('#include "htcleoecserverexception.inl"',
         '#include "htcleoecfontregistry.inl" // ' + MARKER + '\n#include "htcleoecserverexception.inl"'),
    ],
    'htcleoecserverexception.inl': [
        ('    gHtcleoEcRecord[1] = 1;', '    gHtcleoEcRecord[1] = 2; // ' + MARKER),
        ('    for (TInt i = 0; i < 8; ++i) gHtcleoEcRecord[16+i] = gHtcleoEcTrace[i];',
         '    for (TInt i = 0; i < 8; ++i) gHtcleoEcRecord[16+i] = gHtcleoEcTrace[i];\n'
         '    gHtcleoEcRecord[24] = 0x31544646u; // FTF1; fields25..31 are persistent per-process RAM state\n'
         '    for (TInt i = 0; i < 7; ++i) gHtcleoEcRecord[25+i] = gHtcleoEcFont[i];'),
    ],
    'Registrar.cpp': [
        ('#include "Registrar.h"\n', '#include "Registrar.h"\n' + INC),
        ('\tTBool found = EFalse;\n\tTBool update = EFalse;',
         '\tif (aDirEntry->iDllThirdUid.iUid == 0x100012a7) HtcleoEcFontMark(1u, 0, 0);\n'
         '\tTBool found = EFalse;\n\tTBool update = EFalse;'),
        ('\tTRAP(error, ParseL(aEntry,*dll));',
         '\tif (aEntry->iDllThirdUid.iUid == 0x100012a7) HtcleoEcFontMark(2u, 0, 0);\n'
         '\tTRAP(error, ParseL(aEntry,*dll));\n'
         '\tif (aEntry->iDllThirdUid.iUid == 0x100012a7) HtcleoEcFontMark(4u, 1, (TUint32)error);'),
        ('\t\tCleanupStack::Pop(dll);',
         '\t\tif (aEntry->iDllThirdUid.iUid == 0x100012a7) HtcleoEcFontMark(8u, 0, 0);\n'
         '\t\tCleanupStack::Pop(dll);'),
        ('\t\tconst TUid interfaceUid = {theReader.ReadInt32L()};',
         '\t\tconst TUid interfaceUid = {theReader.ReadInt32L()};\n'
         '\t\tif (aEntry->iDllThirdUid.iUid == 0x100012a7 && interfaceUid.iUid == 0x101f7f5d)\n'
         '\t\t\tHtcleoEcFontMark(4096u, 0, 0);'),
    ],
    'RegistryData.cpp': [
        ('#include "HtcleoEcomServerLog.h"\n', '#include "HtcleoEcomServerLog.h"\n' + INC),
        ('\tTInt ret = RLibrary::GetInfo(dllFullName, infoBuf);',
         '\tconst TBool htcleoFontDll = iDllEntry->GetThirdUid().iUid == 0x100012a7;\n'
         '\tif (htcleoFontDll) HtcleoEcFontMark(64u, 0, 0);\n'
         '\tTInt ret = RLibrary::GetInfo(dllFullName, infoBuf);\n'
         '\tif (htcleoFontDll)\n'
         '\t\t{\n'
         '\t\tHtcleoEcFontMark(128u, 3, (TUint32)ret);\n'
         '\t\tif (ret == KErrNone)\n'
         '\t\t\t{\n'
         '\t\t\tHtcleoEcFontMark(256u, 4, infoBuf().iSecurityInfo.iSecureId.iId);\n'
         '\t\t\tHtcleoEcFontMark(0u, 5, (TUint32)infoBuf().iUids[1].iUid);\n'
         '\t\t\t}\n'
         '\t\t}'),
        ('\tiSecurityChecked = ETrue;\n\treturn ETrue;',
         '\tif (htcleoFontDll) HtcleoEcFontMark(512u, 0, 0);\n'
         '\tiSecurityChecked = ETrue;\n\treturn ETrue;'),
        ('\t\tindex = IndexedFind(aInterfaceUid);',
         '\t\tindex = IndexedFind(aInterfaceUid);\n'
         '\t\tif (aInterfaceUid.iUid == 0x101f7f5d)\n'
         '\t\t\tHtcleoEcFontMark(16u | (index >= 0 ? 32u : 0u), 2, (TUint32)index);'),
        ('\t\t\t\tDeleteDllL(dll);\n\t\t\t\tHtcleoEcomServerLog(0x0000F3F9u, j, (TUint32)dll);',
         '\t\t\t\tif (dll->iDllEntry->GetThirdUid().iUid == 0x100012a7) HtcleoEcFontMark(1024u, 0, 0);\n'
         '\t\t\t\tDeleteDllL(dll);\n'
         '\t\t\t\tif (dll->iDllEntry->GetThirdUid().iUid == 0x100012a7) HtcleoEcFontMark(2048u, 0, 0);\n'
         '\t\t\t\tHtcleoEcomServerLog(0x0000F3F9u, j, (TUint32)dll);'),
    ],
}


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('862 anchor drift ' + repr(old[:100]))
    return text.replace(old, new, 1)


def transform(name, text, restore=False):
    if MARKER in text:
        for old, new in reversed(EDITS[name]):
            text = once(text, new, old)
    if hashlib.sha256(text.encode()).hexdigest() != BASE[name]:
        raise ValueError('862 expected exact861 source: ' + name)
    if not restore:
        for old, new in EDITS[name]:
            text = once(text, old, new)
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    # Validate every source before changing any, including exact inverse.
    changes = []
    for name in BASE:
        path = a.root / ROOT / name
        old = path.read_text()
        new = transform(name, old, a.restore)
        if transform(name, new, True) != transform(name, old, True):
            raise ValueError('862 inverse drift ' + name)
        changes.append((path, old, new))
    for path, old, new in changes:
        if old != new:
            path.write_text(new)
    if not a.restore:
        for name in ('htcleoecfontregistry.h', 'htcleoecfontregistry.inl'):
            (a.root / ROOT / name).write_bytes((HERE.parent / 'hd2/qsd8250-native-bsp/diagnostics' / name).read_bytes())
    print('HTCLEO_ECOM_FONT_REGISTRY=' + ('restored' if a.restore else POLICY))


if __name__ == '__main__':
    main()
