#!/usr/bin/env python3
"""Install a fail-open durable startup trace in the Eikon UI server stub.

Iteration 454 proves AknCapServer reaches the call to REikAppUiSession::Connect
but does not return from it.  The stock client waits for eiksrvs.exe process
rendezvous, so this trace brackets only the server-side construction and
rendezvous path.  It does not change retry, leave, panic, scheduler or display
semantics.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKSRVS_STARTUP_DURABLE_LOG_V1"
MACRO = "__HTCLEO_EIKSRVS_STARTUP_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_EIKSRVS_STARTUP_LOG__
#include <f32file.h>

// HTCLEO_EIKSRVS_STARTUP_DURABLE_LOG_V1
static void HtcleoEikSrvLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikSrvLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikSrvLogPath, "C:\\Symbian3\\EIKSRV.TXT");
    r = fs.MkDirAll(KHtcleoEikSrvLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    if (aStage == 0x0000E700u)
        {
        r = file.Replace(fs, KHtcleoEikSrvLogPath,
            EFileWrite | EFileShareAny);
        }
    else
        {
        r = file.Open(fs, KHtcleoEikSrvLogPath,
            EFileWrite | EFileShareAny);
        if (r == KErrNotFound || r == KErrPathNotFound)
            {
            r = file.Replace(fs, KHtcleoEikSrvLogPath,
                EFileWrite | EFileShareAny);
            }
        else if (r == KErrNone)
            {
            r = file.Seek(ESeekEnd, position);
            }
        }

    if (r == KErrNone && position < (128 * 64))
        {
        _LIT8(KHtcleoEikSrvPrefix, "HTCLEO_EIKSRV ");
        TBuf8<96> record;
        record.Append(KHtcleoEikSrvPrefix);
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
inline void HtcleoEikSrvLog(TUint32, TInt, TUint32) {}
#endif

'''


def verify(source: str, mmp: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "log path": source.count("C:\\\\Symbian3\\\\EIKSRV.TXT") == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "efsrv": mmp.lower().count("library         efsrv.lib") == 1,
    }
    for stage in range(0xE700, 0xE711):
        checks[f"stage {stage:04X}"] = (
            source.count(f"HtcleoEikSrvLog(0x0000{stage:04X}u") == 1
        )
    if any(token in source[source.index(MARKER) :] for token in ("User::After",)):
        checks["no delay"] = False
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()

    component = (
        args.epocroot
        / "sf/mw/classicui/commonuisupport/uikon"
    )
    source_path = component / "srvsrc/EIKSRVS.CPP"
    mmp_path = component / "group/EIKSRVS.MMP"
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = replace_once(
            source,
            "#include <eikenv.h>\n",
            "#include <eikenv.h>\n" + LOGGER,
            "logger insertion",
        )
        source = replace_once(
            source,
            """static TInt RunServer()
\t{
\tTBool oomTestingOnEiksrvStartUp=EFalse;
""",
            """static TInt RunServer()
\t{
\tHtcleoEikSrvLog(0x0000E701u, KErrNone, 0u);
\tTBool oomTestingOnEiksrvStartUp=EFalse;
""",
            "RunServer entry",
        )
        source = replace_once(
            source,
            """\tTInt error=User::RenameThread(EIKAPPUI_SERVER_THREAD_NAME);
\tif (error!=KErrNone)
""",
            """\tTInt error=User::RenameThread(EIKAPPUI_SERVER_THREAD_NAME);
\tHtcleoEikSrvLog(0x0000E702u, error, 0u);
\tif (error!=KErrNone)
""",
            "thread rename",
        )
        source = replace_once(
            source,
            """\t\tTInt error=KErrNoMemory;
\t\tCEikonEnv* coe=new CEikServEnv;
\t\tif ((coe!=NULL) && (User::TrapHandler()!=NULL))
\t\t\t{
\t\t\tTRAP(error,
\t\t\t\tcoe->ConstructL();
\t\t\t\tCEikServAppUiServer::NewL()); // the object created by CEikServAppUiServer::NewL is owned by CEikServEnv's iServer
\t\t\t}
""",
            """\t\tTInt error=KErrNoMemory;
\t\tHtcleoEikSrvLog(0x0000E703u, KErrNone, (TUint32)failRate);
\t\tCEikonEnv* coe=new CEikServEnv;
\t\tHtcleoEikSrvLog(0x0000E704u, KErrNone,
\t\t\t(coe ? 1u : 0u) | (User::TrapHandler() ? 2u : 0u));
\t\tif ((coe!=NULL) && (User::TrapHandler()!=NULL))
\t\t\t{
\t\t\tHtcleoEikSrvLog(0x0000E705u, KErrNone, 0u);
\t\t\tTRAP(error,
\t\t\t\tHtcleoEikSrvLog(0x0000E706u, KErrNone, 0u);
\t\t\t\tcoe->ConstructL();
\t\t\t\tHtcleoEikSrvLog(0x0000E707u, KErrNone, 0u);
\t\t\t\tHtcleoEikSrvLog(0x0000E708u, KErrNone, 0u);
\t\t\t\tCEikServAppUiServer::NewL();
\t\t\t\tHtcleoEikSrvLog(0x0000E709u, KErrNone, 0u)); // the object created by CEikServAppUiServer::NewL is owned by CEikServEnv's iServer
\t\t\tHtcleoEikSrvLog(0x0000E70Au, error, 0u);
\t\t\t}
""",
            "environment and server construction",
        )
        source = replace_once(
            source,
            """\t\tif ((error==KErrNone) && !tryAgain)
\t\t\t{
\t\t\tRProcess::Rendezvous(KErrNone);
\t\t\tcoe->ExecuteD();
\t\t\t}
\t\telse
\t\t\t{
\t\t\tif (coe!=NULL)
\t\t\t\t{
\t\t\t\tcoe->DestroyEnvironment();
\t\t\t\t}
""",
            """\t\tif ((error==KErrNone) && !tryAgain)
\t\t\t{
\t\t\tHtcleoEikSrvLog(0x0000E70Bu, KErrNone, 0u);
\t\t\tRProcess::Rendezvous(KErrNone);
\t\t\tHtcleoEikSrvLog(0x0000E70Cu, KErrNone, 0u);
\t\t\tHtcleoEikSrvLog(0x0000E70Du, KErrNone, 0u);
\t\t\tcoe->ExecuteD();
\t\t\t}
\t\telse
\t\t\t{
\t\t\tHtcleoEikSrvLog(0x0000E70Eu, error, tryAgain ? 1u : 0u);
\t\t\tif (coe!=NULL)
\t\t\t\t{
\t\t\t\tcoe->DestroyEnvironment();
\t\t\t\tHtcleoEikSrvLog(0x0000E70Fu, KErrNone, 0u);
\t\t\t\t}
""",
            "rendezvous and failure path",
        )
        source = replace_once(
            source,
            """TInt E32Main()
\t{
\treturn RunServer();
\t}
""",
            """TInt E32Main()
\t{
\tHtcleoEikSrvLog(0x0000E700u, KErrNone, 0u);
\tconst TInt result = RunServer();
\tHtcleoEikSrvLog(0x0000E710u, result, 0u);
\treturn result;
\t}
""",
            "E32Main",
        )

    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"
    if "library         efsrv.lib" not in mmp.lower():
        mmp += "library         efsrv.lib\n"

    verify(source, mmp)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    print("HTCLEO_EIKSRVS_STARTUP_LOG=installed stages=E700-E710")


if __name__ == "__main__":
    main()
