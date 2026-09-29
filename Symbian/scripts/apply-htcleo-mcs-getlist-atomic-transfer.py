#!/usr/bin/env python3
"""Return MatrixMenu's real GetList payload in the successful size IPC."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER_V1"
SESSION_MARKER = "HTCLEO_MCS_GETLIST_SESSION_BUFFER_V2"

OLD_CLIENT = r'''EXPORT_C void RMenuSapi::GetListL( TDes8& aSerializedIn,
		RBuf8& aSerializedOut )
	{
    TInt sizeList(0);
    TPckg<TInt> sizeDes(sizeList);
    TIpcArgs args1( &aSerializedIn, &sizeDes );
    User::LeaveIfError( SendReceive( EMenuGetListSize, args1 ) );
    aSerializedOut.CreateL( sizeList );
    TIpcArgs args2( &aSerializedOut );
    User::LeaveIfError( SendReceive( EMenuGetListData, args2 ) );
	}
'''

NEW_CLIENT = r'''EXPORT_C void RMenuSapi::GetListL( TDes8& aSerializedIn,
		RBuf8& aSerializedOut )
	{
    TInt sizeList(0);
    TPckg<TInt> sizeDes(sizeList);
    // HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER_V1
    // The QSD8K bring-up server can terminate after completing Size but
    // before the stock Data IPC reaches it.  MatrixMenu has a separately
    // bounded real model (30 items), so provide ample descriptor capacity
    // and return the same serialized server payload in the successful Size
    // message.  Every other client retains Nokia's two-message protocol.
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        const TInt KHtcleoAtomicGetListCapacity = 0x10000;
        aSerializedOut.Close();
        aSerializedOut.CreateL(KHtcleoAtomicGetListCapacity);
        TIpcArgs atomicArgs(&aSerializedIn, &sizeDes, &aSerializedOut);
        User::LeaveIfError(SendReceive(EMenuGetListSize, atomicArgs));
        if (sizeList < 0 || sizeList > aSerializedOut.MaxLength())
            {
            User::Leave(KErrOverflow);
            }
        if (aSerializedOut.Length() < sizeList)
            {
            User::Leave(KErrCorrupt);
            }
        aSerializedOut.SetLength(sizeList);
        return;
        }
    TIpcArgs args1( &aSerializedIn, &sizeDes );
    User::LeaveIfError( SendReceive( EMenuGetListSize, args1 ) );
    aSerializedOut.CreateL( sizeList );
    TIpcArgs args2( &aSerializedOut );
    User::LeaveIfError( SendReceive( EMenuGetListData, args2 ) );
	}
'''

SERVER_ANCHOR = r'''            HtcleoMcsLog(0x4D430172u, size,
                (TUint32)iHtcleoGetListOutput.MaxLength());
            TPckg<TInt> sizeDes( size );
            aMessage.WriteL( KGetListReturnPos, sizeDes );
            CleanupStack::PopAndDestroy( buffer );
'''

SERVER_REPLACEMENT = r'''            HtcleoMcsLog(0x4D430172u, size,
                (TUint32)iHtcleoGetListOutput.MaxLength());
            // HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER_V1
            const TBool htcleoAtomicTransfer =
                (aMessage.SecureId().iId == 0x101F4CD2u);
            if (htcleoAtomicTransfer)
                {
                const TInt KHtcleoAtomicGetListPos = 2;
                const TInt htcleoAtomicMax =
                    aMessage.GetDesMaxLength(KHtcleoAtomicGetListPos);
                HtcleoMcsLog(0x4D430176u, htcleoAtomicMax,
                    (TUint32)iHtcleoGetListOutput.Length());
                User::LeaveIfError(htcleoAtomicMax);
                if (htcleoAtomicMax < iHtcleoGetListOutput.Length())
                    {
                    User::Leave(KErrOverflow);
                    }
                aMessage.WriteL(KHtcleoAtomicGetListPos,
                    iHtcleoGetListOutput);
                HtcleoMcsLog(0x4D430177u, KErrNone,
                    (TUint32)iHtcleoGetListOutput.Length());
                }
            TPckg<TInt> sizeDes( size );
            aMessage.WriteL( KGetListReturnPos, sizeDes );
            HtcleoMcsLog(0x4D430178u, KErrNone,
                (TUint32)htcleoAtomicTransfer);
            CleanupStack::PopAndDestroy( buffer );
            HtcleoMcsLog(0x4D430179u, KErrNone, (TUint32)size);
'''


def install(client: str, server: str) -> tuple[str, str]:
    if MARKER in client and MARKER in server:
        return client, server
    if MARKER in client or MARKER in server:
        raise SystemExit("partial MCS atomic-transfer installation")
    if SESSION_MARKER not in server:
        raise SystemExit("MCS atomic transfer requires session buffer V2")
    if client.count(OLD_CLIENT) != 1:
        raise SystemExit("MCS atomic-transfer client anchor missing or duplicated")
    if server.count(SERVER_ANCHOR) != 1:
        raise SystemExit("MCS atomic-transfer server anchor missing or duplicated")
    return (
        client.replace(OLD_CLIENT, NEW_CLIENT, 1),
        server.replace(SERVER_ANCHOR, SERVER_REPLACEMENT, 1),
    )


def verify(client: str, server: str) -> None:
    checks = {
        "markers": client.count(MARKER) == 1 and server.count(MARKER) == 1,
        "matrixmenu scope": (
            client.count("RProcess().SecureId().iId == 0x101F4CD2u") == 1
            and server.count("aMessage.SecureId().iId == 0x101F4CD2u") == 1
        ),
        "bounded descriptor": (
            client.count("KHtcleoAtomicGetListCapacity = 0x10000") == 1
            and client.count("sizeList > aSerializedOut.MaxLength()") == 1
        ),
        "single size IPC": (
            client.count("TIpcArgs atomicArgs") == 1
            and client.count("SendReceive(EMenuGetListSize, atomicArgs)") == 1
        ),
        "stock protocol retained": (
            client.count("SendReceive( EMenuGetListSize, args1 )") == 1
            and client.count("SendReceive( EMenuGetListData, args2 )") == 1
        ),
        "real session payload": (
            server.count("aMessage.WriteL(KHtcleoAtomicGetListPos,") == 1
            and server.count("iHtcleoGetListOutput);") >= 1
        ),
        "trace stages": all(
            server.count(f"0x4D430{stage:03X}u") == 1
            for stage in range(0x176, 0x17A)
        ),
        "no wait or fabricated item": all(
            token not in client + server
            for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS atomic-transfer verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    client_path = component / "src/menusapi.cpp"
    server_path = component / "srvsrc/menusrvsession.cpp"
    client = client_path.read_text(encoding="latin-1")
    server = server_path.read_text(encoding="latin-1")
    client, server = install(client, server)
    verify(client, server)
    client_path.write_text(client, encoding="latin-1")
    server_path.write_text(server, encoding="latin-1")
    print(
        "HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER="
        "matrixmenu-size-plus-real-data-one-ipc-bounded-64k-traced-176-179"
    )


if __name__ == "__main__":
    main()
