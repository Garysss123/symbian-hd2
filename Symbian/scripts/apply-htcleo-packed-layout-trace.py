#!/usr/bin/env python3
"""781: exactly one client method, five bounded records, original IPC unchanged."""
import argparse
from pathlib import Path

INC = '#include "htcleopackedlayouttrace.inl"\n'
OLD = '''EXPORT_C HBufC8* RAknUiServer::GetPackedConfigL() const
    {
    TInt size = 0;
    TPckg<TInt> pckg(size);
    User::LeaveIfError(SendReceive(EAknEikAppUiLayoutConfigSize, TIpcArgs(&pckg)));
    
    HBufC8* buf = HBufC8::NewMaxLC(size);
    TPtr8 ptr = buf->Des();
    User::LeaveIfError(SendReceive(EAknEikAppUiGetLayoutConfig, TIpcArgs(&ptr)));
    
    CleanupStack::Pop(buf);
    return buf;
    }
'''
NEW = '''EXPORT_C HBufC8* RAknUiServer::GetPackedConfigL() const
    {
    // HTCLEO_PACKED_LAYOUT_IPC_TRACE_V1
    const TBool htcleoTrace = HtcleoTracePackedLayoutCaller();
    if (htcleoTrace)
        HtcleoPackedLayoutLog(0x0300u, KErrNone, (TUint)Handle(), ServerName());
    TInt size = 0;
    TPckg<TInt> pckg(size);
    if (htcleoTrace)
        HtcleoPackedLayoutLog(0x0310u, KErrNone, EAknEikAppUiLayoutConfigSize);
    const TInt htcleoSizeResult = SendReceive(EAknEikAppUiLayoutConfigSize, TIpcArgs(&pckg));
    if (htcleoTrace)
        HtcleoPackedLayoutLog(0x0311u, htcleoSizeResult, (TUint)size);
    User::LeaveIfError(htcleoSizeResult);
    
    HBufC8* buf = HBufC8::NewMaxLC(size);
    TPtr8 ptr = buf->Des();
    if (htcleoTrace)
        HtcleoPackedLayoutLog(0x0320u, KErrNone, (TUint)ptr.MaxLength());
    const TInt htcleoDataResult = SendReceive(EAknEikAppUiGetLayoutConfig, TIpcArgs(&ptr));
    if (htcleoTrace)
        HtcleoPackedLayoutLog(0x0321u, htcleoDataResult, (TUint)ptr.Length());
    User::LeaveIfError(htcleoDataResult);
    
    CleanupStack::Pop(buf);
    return buf;
    }
'''


def transform(source, restore=False):
    if INC in source:
        if source.count(INC) != 1 or source.count(NEW) != 1:
            raise ValueError('partial packed-layout trace')
        source = source.replace(NEW, OLD, 1).replace(INC, '', 1)
    elif 'HTCLEO_PACKED_LAYOUT_IPC_TRACE' in source:
        raise ValueError('partial packed-layout trace')
    if not restore:
        anchor = '#include <e32property.h>\n'
        if source.count(anchor) != 1 or source.count(OLD) != 1:
            raise ValueError('client anchor changed')
        source = source.replace(anchor, anchor + INC, 1).replace(OLD, NEW, 1)
    return source


def main():
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--restore', action='store_true')
    a = p.parse_args()
    directory = a.root / 'sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/clientsrc'
    path = directory / 'AknCapServerClient.cpp'
    old = path.read_text(encoding='latin-1')
    new = transform(old, a.restore)
    if not a.restore:
        if transform(new) != new or transform(new, True) != transform(old, True):
            raise ValueError('not reversible/idempotent')
        body = (Path(__file__).parents[1] / 'hd2/qsd8250-native-bsp/diagnostics/htcleopackedlayouttrace.inl').read_text()
        for forbidden in ('Flush(', 'Replace(', 'Delete(', 'RWsSession', 'SetOrdinal', 'RTimer', 'WaitForRequest', 'HalFunction'):
            if forbidden in body:
                raise ValueError('out-of-scope observer: ' + forbidden)
        (directory / 'htcleopackedlayouttrace.inl').write_text(body)
    if new != old:
        path.write_text(new, encoding='latin-1')
    print('HTCLEO_PACKED_LAYOUT_IPC_TRACE=' + ('restored' if a.restore else 'matrix-first-ten-records-no-flush-no-behavior-change'))


if __name__ == '__main__':
    main()
