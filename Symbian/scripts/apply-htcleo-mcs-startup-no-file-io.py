#!/usr/bin/env python3
"""Keep MCS registration/rendezvous/scheduler entry free of diagnostic file IPC."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MCS_STARTUP_NO_FILE_IO_V1"
CLIENT_MARKER = "HTCLEO_MCS_MATRIX_CLIENT_CONNECT_TRACE_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"MCS startup boundary anchor mismatch: {old[:96]!r}")
    return text.replace(old, new, 1)


def patch_engine(text: str) -> str:
    if MARKER in text:
        return text
    old = '''void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x200113DDu)
        {
        return;
        }'''
    new = '''void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // HTCLEO_MCS_STARTUP_NO_FILE_IO_V1
    // Start registered the server and armed its receive AO. Between this,
    // Rendezvous and scheduler entry, no RFs IPC may consume a ready signal.
    // Suppress only the two diagnostics in that window, not real requests.
    if (aStage == 0x4D430144u || aStage == 0x4D430145u)
        return;
    if (RProcess().SecureId().iId != 0x200113DDu)
        {
        // The client only records its coarse connect/start-return boundaries.
        if (RProcess().SecureId().iId != 0x101F4CD2u ||
                aStage < 0x4D430190u || aStage > 0x4D430193u)
            return;
        }'''
    text = once(text, old, new)
    return once(text, "position <= ((256 * 64) - 64)", "position <= ((16384 * 64) - 64)")


def patch_client(text: str) -> str:
    if CLIENT_MARKER in text:
        return text
    text = once(text, "#include <e32debug.h>\n", "#include <e32debug.h>\n\nvoid HtcleoMcsLog(TUint32, TInt, TUint32);\n")
    old = '''TInt RMenu::ConnectSession()
    {
    TVersion version( KMenuMajorVersion, KMenuMinorVersion, KMenuBuild );
    TInt err = CreateSession( KMenuSrvName, version );'''
    text = once(text, old, '''TInt RMenu::ConnectSession()
    {
    // HTCLEO_MCS_MATRIX_CLIENT_CONNECT_TRACE_V1
    const TBool htcleoMatrixClient = RProcess().SecureId().iId == 0x101F4CD2u;
    if (htcleoMatrixClient)
        HtcleoMcsLog(0x4D430190u, KErrNone, (TUint32)RProcess().Id().Id());
    TVersion version( KMenuMajorVersion, KMenuMinorVersion, KMenuBuild );
    TInt err = CreateSession( KMenuSrvName, version );
    if (htcleoMatrixClient)
        HtcleoMcsLog(0x4D430191u, err, (TUint32)Handle());''')
    start = text.index("TInt RMenu::ConnectSession()")
    end = text.index("\n    }\n", start) + len("\n    }\n")
    section = text[start:end]
    section = once(section, "        err = StartServer();", '''        err = StartServer();
        if (htcleoMatrixClient)
            HtcleoMcsLog(0x4D430192u, err, 0u);''')
    section = once(section, "    return err;", '''    if (htcleoMatrixClient)
        HtcleoMcsLog(0x4D430193u, err, (TUint32)Handle());
    return err;''')
    return text[:start] + section + text[end:]


def verify(engine: str, client: str, server: str) -> None:
    if engine.count(MARKER) != 1 or client.count(CLIENT_MARKER) != 1:
        raise SystemExit("MCS startup/client markers missing")
    start = engine.index("void HtcleoMcsLog(")
    fs = engine.index("    RFs fs;", start)
    gate = engine[start:fs]
    if "if (aStage == 0x4D430144u || aStage == 0x4D430145u)\n        return;" not in gate:
        raise SystemExit("critical-window diagnostics must return before file IPC")
    if "position <= ((16384 * 64) - 64)" not in engine:
        raise SystemExit("server/client logger must keep 1 MiB capacity")
    start = server.index("err = server->Start( KMenuSrvName );")
    end = server.index("CActiveScheduler::Start();", start)
    window = server[start:end]
    if (window.count("HtcleoMcsLog(") != 2 or
            "0x4D430144u" not in window or "0x4D430145u" not in window or
            window.count("RProcess::Rendezvous( err );") != 1):
        raise SystemExit("server startup window changed; re-audit no-I/O path")
    for stage in range(0x190, 0x194):
        if client.count(f"0x4D430{stage:03X}u") != 1:
            raise SystemExit("client connect boundary stage missing/duplicated")
    start = client.index("LOCAL_C TInt StartServer()")
    end = client.index("// ================= MEMBER FUNCTIONS", start)
    if "HtcleoMcsLog" in client[start:end]:
        raise SystemExit("do not put diagnostic file IPC inside rendezvous wait")
    if client.count("CreateSession( KMenuSrvName, version )") != 2:
        raise SystemExit("stock initial/retry session creation must remain")
    if any(call in window for call in ("RequestComplete", "User::After", "WaitForRequest", "RFs")):
        raise SystemExit("do not inject requests, waits or filesystem access at server startup")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/homescreensrv/menucontentsrv"
    engine_path = base / "srvsrc/menusrveng.cpp"
    client_path = base / "src/menu.cpp"
    engine = patch_engine(engine_path.read_text(encoding="latin-1"))
    client = patch_client(client_path.read_text(encoding="latin-1"))
    verify(engine, client, (base / "srvsrc/menusrv.cpp").read_text(encoding="latin-1"))
    engine_path.write_text(engine, encoding="latin-1")
    client_path.write_text(client, encoding="latin-1")
    print("HTCLEO_MCS_STARTUP_LOG_POLICY=144-145-no-file-io-registration-rendezvous-scheduler")
    print("HTCLEO_MCS_CLIENT_CONNECT_TRACE=matrix-only-190-193-startserver-return-real-session-results-1m")


if __name__ == "__main__":
    main()
