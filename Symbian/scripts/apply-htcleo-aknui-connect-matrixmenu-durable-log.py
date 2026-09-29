#!/usr/bin/env python3
"""Add MatrixMenu-only durable tracing to RAknUiServer connection.

Iteration 497 reaches CAknSgcClient::ConstructL and does not return from
iAknSrv.Connect().  This transform brackets the public Connect wrapper and
ConnectAknServer's existing-session, fallback launch, delay and retry path.
All stock calls, branches and return values are retained; only MatrixMenu SID
0x101f4cd2 appends bounded, fail-open records to MENULOG.TXT.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''
#ifdef __HTCLEO_APPARC_LAUNCH_DURABLE_LOG__
// HTCLEO_AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG_V1
static void HtcleoAknUiConnectMenuLog(
    TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101f4cd2u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoAknUiConnectMenuDir, "C:\\Symbian3\\");
    _LIT(KHtcleoAknUiConnectMenuPath, "C:\\Symbian3\\MENULOG.TXT");
    r = fs.MkDirAll(KHtcleoAknUiConnectMenuDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoAknUiConnectMenuPath,
        EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoAknUiConnectMenuPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoAknUiConnectMenuPrefix, "HTCLEO_MENU ");
        TBuf8<96> record;
        record.Append(KHtcleoAknUiConnectMenuPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            }
        }
    file.Close();
    fs.Close();
    }
#else
inline void HtcleoAknUiConnectMenuLog(TUint32, TInt, TUint32) {}
#endif

'''


CONNECT_SERVER_STOCK = r'''TInt RAknUiServer::ConnectAknServer()
    {
#ifdef _DEBUG
    RThread me;
    TName name = me.Name();
    RDebug::Print( _L( "RAknUiServer::ConnectAknServer(), handle %d, %S" ), Handle(), &name );    
#endif
    TInt err = KErrNone;
    if (Handle() == NULL)
        {
        _LIT(KServerNameFormat, "%08x_%08x_AppServer");
        TFullName serverName;
        
        serverName.Format(
            KServerNameFormat, 
            KUikonUidPluginInterfaceNotifiers, 
            KAknCapServerUid.iUid);
            
        TRAP(err, ConnectExistingByNameL(serverName));
        if (err == KErrNotFound) // This should be never true when starter is in use!
            {
            TRAP_IGNORE(StartAknCapserverL());
            User::After(500000); // No problem to wait synchronously as pure RnD support.
            TRAP(err,ConnectExistingByNameL(serverName));
            }
        }
#ifdef _DEBUG
    RDebug::Print(_L("RAknUiServer::ConnectAknServer() end"));    
#endif
    return err;
    }
'''


CONNECT_SERVER_TRACED = r'''TInt RAknUiServer::ConnectAknServer()
    {
#ifdef _DEBUG
    RThread me;
    TName name = me.Name();
    RDebug::Print( _L( "RAknUiServer::ConnectAknServer(), handle %d, %S" ), Handle(), &name );    
#endif
    HtcleoAknUiConnectMenuLog(0x4D4DA210u, KErrNone,
        (TUint32)Handle());
    TInt err = KErrNone;
    const TBool needsConnection = (Handle() == NULL);
    HtcleoAknUiConnectMenuLog(0x4D4DA211u, KErrNone,
        needsConnection ? 1u : 0u);
    if (needsConnection)
        {
        _LIT(KServerNameFormat, "%08x_%08x_AppServer");
        TFullName serverName;
        HtcleoAknUiConnectMenuLog(0x4D4DA212u, KErrNone, 0u);
        
        serverName.Format(
            KServerNameFormat, 
            KUikonUidPluginInterfaceNotifiers, 
            KAknCapServerUid.iUid);
        HtcleoAknUiConnectMenuLog(0x4D4DA213u, KErrNone,
            (TUint32)serverName.Length());
            
        HtcleoAknUiConnectMenuLog(0x4D4DA214u, KErrNone, 0u);
        TRAP(err, ConnectExistingByNameL(serverName));
        HtcleoAknUiConnectMenuLog(0x4D4DA215u, err,
            (TUint32)Handle());
        if (err == KErrNotFound) // This should be never true when starter is in use!
            {
            HtcleoAknUiConnectMenuLog(0x4D4DA216u, err, 0u);
            TRAP_IGNORE(StartAknCapserverL());
            HtcleoAknUiConnectMenuLog(0x4D4DA217u, KErrNone, 0u);
            HtcleoAknUiConnectMenuLog(0x4D4DA218u, KErrNone, 500000u);
            User::After(500000); // No problem to wait synchronously as pure RnD support.
            HtcleoAknUiConnectMenuLog(0x4D4DA219u, KErrNone, 0u);
            HtcleoAknUiConnectMenuLog(0x4D4DA21Au, KErrNone, 0u);
            TRAP(err,ConnectExistingByNameL(serverName));
            HtcleoAknUiConnectMenuLog(0x4D4DA21Bu, err,
                (TUint32)Handle());
            }
        }
#ifdef _DEBUG
    RDebug::Print(_L("RAknUiServer::ConnectAknServer() end"));    
#endif
    HtcleoAknUiConnectMenuLog(0x4D4DA21Cu, err,
        (TUint32)Handle());
    return err;
    }
'''


CONNECT_STOCK = r'''EXPORT_C TInt RAknUiServer::Connect()
    {
    RThread thread;
    if (!Handle() && thread.Name() == EIKAPPUI_SERVER_THREAD_NAME)
        {
        return KErrNone;        
        }

    return ConnectAknServer();
    }
'''


CONNECT_TRACED = r'''EXPORT_C TInt RAknUiServer::Connect()
    {
    HtcleoAknUiConnectMenuLog(0x4D4DA200u, KErrNone,
        (TUint32)Handle());
    RThread thread;
    HtcleoAknUiConnectMenuLog(0x4D4DA201u, KErrNone, 0u);
    const TBool isEikSrvThread =
        (thread.Name() == EIKAPPUI_SERVER_THREAD_NAME);
    HtcleoAknUiConnectMenuLog(0x4D4DA202u, KErrNone,
        isEikSrvThread ? 1u : 0u);
    if (!Handle() && isEikSrvThread)
        {
        HtcleoAknUiConnectMenuLog(0x4D4DA203u, KErrNone, 0u);
        return KErrNone;        
        }

    HtcleoAknUiConnectMenuLog(0x4D4DA204u, KErrNone, 0u);
    const TInt connectError = ConnectAknServer();
    HtcleoAknUiConnectMenuLog(0x4D4DA205u, connectError,
        (TUint32)Handle());
    return connectError;
    }
'''


def install(source: str) -> str:
    source = replace_once(
        source,
        "\n\n_LIT(KAknCapServerExecutable,",
        "\n" + HELPER + "_LIT(KAknCapServerExecutable,",
        "durable helper",
    )
    source = replace_once(
        source, CONNECT_SERVER_STOCK, CONNECT_SERVER_TRACED,
        "ConnectAknServer",
    )
    return replace_once(source, CONNECT_STOCK, CONNECT_TRACED, "Connect")


def verify(source: str) -> None:
    stages = (
        *range(0x4D4DA200, 0x4D4DA206),
        *range(0x4D4DA210, 0x4D4DA21D),
    )
    checks = {
        "marker": source.count(MARKER) == 1,
        "exact SID gate": source.count(
            "RProcess().SecureId().iId != 0x101f4cd2u"
        ) == 1,
        "durable path": source.count(r"C:\\Symbian3\\MENULOG.TXT") == 1,
        "all stages": all(
            source.count(f"0x{stage:08X}u") == 1 for stage in stages
        ),
        "single write and flush": (
            source.count("file.Write(record)") == 2
            and source.count("file.Flush()") == 2
        ),
        "stock connection calls": all(
            source.count(call) == count
            for call, count in (
                ("TRAP(err, ConnectExistingByNameL(serverName));", 1),
                ("TRAP(err,ConnectExistingByNameL(serverName));", 1),
                ("TRAP_IGNORE(StartAknCapserverL());", 1),
                ("User::After(500000);", 1),
                ("const TInt connectError = ConnectAknServer();", 1),
            )
        ),
        "no new delay or display": (
            "User::After" not in HELPER and "HalFunction" not in HELPER
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknUi connection trace verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/clientsrc/"
        "AknCapServerClient.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNUI_CONNECT_MATRIXMENU_DURABLE_LOG=installed "
        "stages=4D4DA200-A205,A210-A21C"
    )


if __name__ == "__main__":
    main()
