#!/usr/bin/env python3
"""Add an AknCap-SID-gated Feature Manager startup trace.

Iteration 444 proves CEikonEnv::ConstructL leaves while executing
CAknEnv::InstallAknEnvAsExtensionL.  Its first operation is
FeatureManager::InitializeLibL.  This transform uses the already-defined
AknCap P&S key and never opens a file, waits, retries, or changes an error.
Only successful outer returns publish a later stage, so a deep failure is not
hidden while the leave unwinds.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_FEATMGR_AKNCAP_TRACE_V1"
MACRO = "__HTCLEO_FEATMGR_AKNCAP_TRACE__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_function(
    text: str, start: str, next_comment_title: str, replacement: str, label: str
) -> str:
    begin = text.find(start)
    if begin < 0 or text.find(start, begin + 1) >= 0:
        raise SystemExit(f"{label}: function anchor is missing or ambiguous")
    title = f"// {next_comment_title}\n"
    title_pos = text.find(title, begin)
    if title_pos < 0:
        raise SystemExit(f"{label}: next function title not found")
    separator = text.rfind("// -----------------------------------------------------------------------------\n", begin, title_pos)
    if separator < 0:
        raise SystemExit(f"{label}: next separator not found")
    return text[:begin] + replacement + "\n\n" + text[separator:]


def install_mmp(text: str) -> str:
    return replace_once(
        text,
        "SMPSAFE\n",
        "// HTCLEO_FEATMGR_AKNCAP_TRACE_V1\n"
        "MACRO           __HTCLEO_FEATMGR_AKNCAP_TRACE__\n\n"
        "SMPSAFE\n",
        "featmgr MMP macro",
    )


def install_featmgr(text: str) -> str:
    text = replace_once(
        text,
        '#include "featmgrdebug.h"\n#include <e32std.h>\n',
        '#include "featmgrdebug.h"\n'
        '#include "htcleo_featmgr_trace.h"\n'
        '#include <e32property.h>\n'
        '#include <e32std.h>\n',
        "featmgr trace includes",
    )
    text = replace_once(
        text,
        '_LIT( KPanicCategory, "FeatMgr" );\n',
        '_LIT( KPanicCategory, "FeatMgr" );\n\n'
        '#ifdef __HTCLEO_FEATMGR_AKNCAP_TRACE__\n'
        '// HTCLEO_FEATMGR_AKNCAP_TRACE_V1\n'
        'const TUid KHtcleoFeatMgrTraceCategory = {0x10207218};\n'
        'const TUint KHtcleoFeatMgrTraceKey = 0x7f044301u;\n\n'
        'void HtcleoFeatMgrAknCapTrace(TUint32 aStage, TInt aResult)\n'
        '    {\n'
        '    if (RProcess().SecureId().iId != KHtcleoFeatMgrTraceCategory.iUid)\n'
        '        {\n'
        '        return;\n'
        '        }\n'
        '    const TUint32 value = ((aStage & 0xffffu) << 16) |\n'
        '        ((TUint32)aResult & 0xffffu);\n'
        '    (void)RProperty::Set(\n'
        '        KHtcleoFeatMgrTraceCategory,\n'
        '        KHtcleoFeatMgrTraceKey,\n'
        '        (TInt)value);\n'
        '    }\n'
        '#endif\n',
        "featmgr trace helper",
    )
    old = (
        "EXPORT_C void FeatureManager::InitializeLibL()\n"
        "    {\n"
        "\tFUNC_LOG\n\n"
        "    if ( !Dll::Tls() )\n"
        "        {\n"
        "        Dll::SetTls( CFeatMgrTlsData::NewL() );\n"
        "        }\n\n"
        "\t// Increase the client count (self)\n"
        "\tTlsData()->IncreaseClientCount();\n"
        "\t}\n"
    )
    new = (
        "EXPORT_C void FeatureManager::InitializeLibL()\n"
        "    {\n"
        "\tFUNC_LOG\n"
        "    HtcleoFeatMgrAknCapTrace(0xE500u, Dll::Tls() ? 1 : 0);\n\n"
        "    if ( !Dll::Tls() )\n"
        "        {\n"
        "        HtcleoFeatMgrAknCapTrace(0xE501u, KErrNone);\n"
        "        CFeatMgrTlsData* tlsData = CFeatMgrTlsData::NewL();\n"
        "        HtcleoFeatMgrAknCapTrace(0xE502u, KErrNone);\n"
        "        Dll::SetTls( tlsData );\n"
        "        HtcleoFeatMgrAknCapTrace(0xE503u, KErrNone);\n"
        "        }\n\n"
        "\t// Increase the client count (self)\n"
        "\tTlsData()->IncreaseClientCount();\n"
        "    HtcleoFeatMgrAknCapTrace(0xE504u, KErrNone);\n"
        "\t}\n"
    )
    return replace_once(text, old, new, "FeatureManager::InitializeLibL")


def install_tls(text: str) -> str:
    text = replace_once(
        text,
        '#include "featmgrdebug.h"\n',
        '#include "featmgrdebug.h"\n#include "htcleo_featmgr_trace.h"\n',
        "TLS trace include",
    )
    text = replace_once(
        text,
        "void CFeatMgrTlsData::ConstructL()\n"
        "    {\n"
        "    // Connect to Feature Manager server\n"
        "    FUNC_LOG\n"
        "    TInt err( iFeatMgrClient.Connect() );\n"
        "    User::LeaveIfError(err);\n"
        "    }\n",
        "void CFeatMgrTlsData::ConstructL()\n"
        "    {\n"
        "    // Connect to Feature Manager server\n"
        "    FUNC_LOG\n"
        "    HtcleoFeatMgrAknCapTrace(0xE520u, KErrNone);\n"
        "    HtcleoFeatMgrAknCapTrace(0xE521u, KErrNone);\n"
        "    TInt err( iFeatMgrClient.Connect() );\n"
        "    if (err == KErrNone)\n"
        "        {\n"
        "        HtcleoFeatMgrAknCapTrace(0xE522u, err);\n"
        "        }\n"
        "    User::LeaveIfError(err);\n"
        "    HtcleoFeatMgrAknCapTrace(0xE523u, KErrNone);\n"
        "    }\n",
        "CFeatMgrTlsData::ConstructL",
    )
    return replace_once(
        text,
        "CFeatMgrTlsData* CFeatMgrTlsData::NewL()\n"
        "    {\n"
        "    CFeatMgrTlsData* self = new( ELeave ) CFeatMgrTlsData();\n"
        "    CleanupStack::PushL( self );\n"
        "    self->ConstructL();\n"
        "    CleanupStack::Pop( self );\n"
        "    return self;\n"
        "    }\n",
        "CFeatMgrTlsData* CFeatMgrTlsData::NewL()\n"
        "    {\n"
        "    HtcleoFeatMgrAknCapTrace(0xE510u, KErrNone);\n"
        "    CFeatMgrTlsData* self = new( ELeave ) CFeatMgrTlsData();\n"
        "    HtcleoFeatMgrAknCapTrace(0xE511u, self ? KErrNone : KErrNoMemory);\n"
        "    CleanupStack::PushL( self );\n"
        "    HtcleoFeatMgrAknCapTrace(0xE512u, KErrNone);\n"
        "    self->ConstructL();\n"
        "    HtcleoFeatMgrAknCapTrace(0xE513u, KErrNone);\n"
        "    CleanupStack::Pop( self );\n"
        "    HtcleoFeatMgrAknCapTrace(0xE514u, KErrNone);\n"
        "    return self;\n"
        "    }\n",
        "CFeatMgrTlsData::NewL",
    )


def install_client(text: str) -> str:
    text = replace_once(
        text,
        '#include "featmgrclientserver.h"\n',
        '#include "featmgrclientserver.h"\n#include "htcleo_featmgr_trace.h"\n',
        "client trace include",
    )
    connect = """TInt RFeatMgrClient::Connect()
    {
    FUNC_LOG
    HtcleoFeatMgrAknCapTrace(0xE530u, KErrNone);

    // Try this twice
    TInt retry( KRetry );
    TInt err( KErrNone );

    while ( retry > 0 )
        {
        // Try to create a FeatMgr Server session
        HtcleoFeatMgrAknCapTrace(0xE531u, retry);
        err = CreateSession( KServerProcessName,
                             ServerVersion(),
                             KDefaultAsyncSlots );
        if (err == KErrNone)
            {
            HtcleoFeatMgrAknCapTrace(0xE532u, err);
            }
        else if (err == KErrNotFound || err == KErrServerTerminated)
            {
            HtcleoFeatMgrAknCapTrace(0xE533u, err);
            }
        else
            {
            HtcleoFeatMgrAknCapTrace(0xE536u, err);
            }

        LOG_IF_ERROR1( err, "RFeatMgrClient::Connect - CreateSession returned: %d", err );

        if ( err != KErrNotFound && err != KErrServerTerminated )
            {
            // KErrNone or unrecoverable error
            retry = 0;
            }
        else
            {
            // Return code was KErrNotFound or KErrServerTerminated.
            // Try to start a new FeatMgr Server
            err = StartServer();

            LOG_IF_ERROR1( err, "RFeatMgrClient::Connect - StartServer returned: %d", err );

            if ( err != KErrNone && err != KErrAlreadyExists )
                {
                // Unrecoverable error.  StartServer preserves its deepest stage.
                retry = 0;
                }
            else
                {
                HtcleoFeatMgrAknCapTrace(0xE534u, err);
                }
            }

        retry--;
        }

    if (err == KErrNone)
        {
        HtcleoFeatMgrAknCapTrace(0xE535u, err);
        }
    return err;
    }"""
    text = replace_function(
        text,
        "TInt RFeatMgrClient::Connect()\n",
        "RFeatMgrClient::StartServer",
        connect,
        "RFeatMgrClient::Connect",
    )
    start_server = """TInt RFeatMgrClient::StartServer()
    {
    FUNC_LOG
    TIMESTAMP( "StartServer start: " )
    HtcleoFeatMgrAknCapTrace(0xE540u, KErrNone);

    RProcess server;
    const TUidType serverUid( KNullUid, KServerUid2, KNullUid );
    HtcleoFeatMgrAknCapTrace(0xE541u, KErrNone);
    TInt err = server.Create( KServerExeName, // FeatMgrServer.exe
                           KNullDesC, // A descriptor containing data passed as
                                      // an argument to the thread function of
                                      // the new process's main thread, when it
                                      // is first scheduled.
                           serverUid, // FeatMgr server UID
                           EOwnerProcess ); // Ownership of this process handle
    HtcleoFeatMgrAknCapTrace(0xE542u, err);

    // Return error code if we couldn't create a process
    if ( err == KErrNone )
        {
        // Rendezvous is used to detect server start
        TRequestStatus stat;
        server.Rendezvous( stat );
        HtcleoFeatMgrAknCapTrace(0xE543u, stat.Int());

        const TBool pending = (stat == KRequestPending);
        HtcleoFeatMgrAknCapTrace(0xE544u, pending);
        if ( !pending )
            {
            server.Kill( KErrNone ); // Abort startup
            }
        else
            {
            server.Resume();  // Logon OK - start the server
            }
        HtcleoFeatMgrAknCapTrace(0xE545u, pending);

        INFO_LOG( "RFeatMgrClient::StartServer - Waiting server startup" );
        HtcleoFeatMgrAknCapTrace(0xE546u, stat.Int());
        User::WaitForRequest( stat ); // Wait for start or death
        HtcleoFeatMgrAknCapTrace(0xE547u, stat.Int());

        INFO_LOG( "RFeatMgrClient::StartServer - Server startup wait finished" );

        // We can't use the 'exit reason' if the server paniced as this
        // is the panic 'reason' and may be '0' which cannot be distinguished
        // from KErrNone
        const TExitType exitType = server.ExitType();
        err = (exitType == EExitPanic)? KErrGeneral : stat.Int();
        const TInt exitAndResult = (((TInt)exitType & 0xf) << 12) |
            ((TUint32)err & 0xfffu);
        HtcleoFeatMgrAknCapTrace(0xE548u, exitAndResult);

        // We can close the handle now
        server.Close();
        }

    TIMESTAMP( "StartServer end: " )

    return err;
    }"""
    return replace_function(
        text,
        "TInt RFeatMgrClient::StartServer()\n",
        "RFeatMgrClient::ServerVersion",
        start_server,
        "RFeatMgrClient::StartServer",
    )


def verify(paths: dict[str, Path]) -> None:
    texts = {name: path.read_text(encoding="latin-1") for name, path in paths.items()}
    combined = "\n".join(texts.values())
    stages = (
        list(range(0xE500, 0xE505))
        + list(range(0xE510, 0xE515))
        + list(range(0xE520, 0xE524))
        + list(range(0xE530, 0xE537))
        + list(range(0xE540, 0xE549))
    )
    checks = {
        "source marker": texts["featmgr"].count(MARKER) == 1,
        "MMP marker": texts["mmp"].count(MARKER) == 1,
        "header marker": texts["header"].count(
            "HTCLEO_FEATMGR_AKNCAP_TRACE_V1_HEADER"
        ) == 1,
        "MMP macro": texts["mmp"].count(f"MACRO           {MACRO}") == 1,
        "helper declaration": texts["header"].count(
            "void HtcleoFeatMgrAknCapTrace(TUint32 aStage, TInt aResult);"
        ) == 1,
        "helper definition": texts["featmgr"].count(
            "void HtcleoFeatMgrAknCapTrace(TUint32 aStage, TInt aResult)"
        ) == 1,
        "single property write": combined.count("(void)RProperty::Set(") == 1,
        "SID gate": combined.count(
            "RProcess().SecureId().iId != KHtcleoFeatMgrTraceCategory.iUid"
        ) == 1,
        "all stages": all(combined.count(f"0x{stage:04X}u") == 1 for stage in stages),
        "stock wait retained once": texts["client"].count("User::WaitForRequest( stat )") == 1,
        "no delay": "User::After" not in combined,
        "no durable IO": "AKNCAP.TXT" not in combined,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/os/persistentdata/featuremgmt/featuremgr"
    paths = {
        "mmp": component / "group/featmgr.mmp",
        "header": component / "src/inc/htcleo_featmgr_trace.h",
        "featmgr": component / "src/clientdll/featmgr.cpp",
        "tls": component / "src/clientdll/featmgrtlsdata.cpp",
        "client": component / "src/clientdll/featmgrclient.cpp",
    }

    texts = {
        name: path.read_text(encoding="latin-1")
        for name, path in paths.items()
        if name != "header" and path.exists()
    }
    if MARKER not in texts["featmgr"]:
        texts["mmp"] = install_mmp(texts["mmp"])
        texts["featmgr"] = install_featmgr(texts["featmgr"])
        texts["tls"] = install_tls(texts["tls"])
        texts["client"] = install_client(texts["client"])
        for name, text in texts.items():
            paths[name].write_text(text, encoding="latin-1")
        paths["header"].write_text(
            "#ifndef HTCLEO_FEATMGR_TRACE_H\n"
            "#define HTCLEO_FEATMGR_TRACE_H\n\n"
            "#include <e32std.h>\n\n"
            "#ifdef __HTCLEO_FEATMGR_AKNCAP_TRACE__\n"
            "// HTCLEO_FEATMGR_AKNCAP_TRACE_V1_HEADER\n"
            "void HtcleoFeatMgrAknCapTrace(TUint32 aStage, TInt aResult);\n"
            "#else\n"
            "inline void HtcleoFeatMgrAknCapTrace(TUint32, TInt) {}\n"
            "#endif\n\n"
            "#endif\n",
            encoding="latin-1",
        )
    verify(paths)
    print("HTCLEO_FEATMGR_AKNCAP_TRACE=installed stages=E500-E548 count=30")


if __name__ == "__main__":
    main()
