#!/usr/bin/env python3
"""Fix FeatMgrServer registry construction order and add fail-open P&S trace.

The stock source dereferences iRegistry to obtain the backup-registration path
before constructing iRegistry.  The functional change moves registry creation
ahead of that first use.  The trace is a single integer property owned by the
FeatMgrServer SID; it adds no file I/O, wait, retry, delay, display path or
error suppression.  On server-start failure the existing AknCap-side trace
copies the deepest E6xx server stage into its durable AKNCAP stream.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE_V1"
PRESERVE_MARKER = "HTCLEO_FEATMGRSERVER_DEEPEST_STAGE_PRESERVE_V2"
MACRO = "__HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def replace_function(
    text: str, signature: str, next_marker: str, replacement: str, label: str
) -> str:
    start = text.find(signature)
    if start < 0:
        raise SystemExit(f"{label}: signature not found")
    end = text.find(next_marker, start + len(signature))
    if end < 0:
        raise SystemExit(f"{label}: next marker not found")
    return text[:start] + replacement.rstrip() + "\n\n" + text[end:]


HEADER = r'''#ifndef HTCLEO_FEATMGRSERVER_TRACE_H
#define HTCLEO_FEATMGRSERVER_TRACE_H

#include <e32std.h>

#ifdef __HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE__
// HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE_V1_HEADER
void HtcleoFeatMgrServerTrace(TUint32 aStage, TInt aResult);
TInt HtcleoFeatMgrServerTraceReset();
#else
inline void HtcleoFeatMgrServerTrace(TUint32, TInt) {}
inline TInt HtcleoFeatMgrServerTraceReset() { return KErrNone; }
#endif

#endif
'''


STARTUP_HELPER = r'''
#ifdef __HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE__
// HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE_V1
const TUid KHtcleoFeatMgrServerTraceCategory = {0x10205054};
const TUint KHtcleoFeatMgrServerTraceKey = 0x7f044302u;
_LIT_SECURITY_POLICY_PASS(KHtcleoFeatMgrServerTraceReadPolicy);
_LIT_SECURITY_POLICY_S0(KHtcleoFeatMgrServerTraceWritePolicy, 0x10205054);

void HtcleoFeatMgrServerTrace(TUint32 aStage, TInt aResult)
    {
    const TInt value = (TInt)(((aStage & 0xffffu) << 16) |
        ((TUint32)aResult & 0xffffu));
    (void)RProperty::Set(KHtcleoFeatMgrServerTraceCategory,
        KHtcleoFeatMgrServerTraceKey, value);
    }

TInt HtcleoFeatMgrServerTraceReset()
    {
    TInt result = RProperty::Define(KHtcleoFeatMgrServerTraceCategory,
        KHtcleoFeatMgrServerTraceKey, RProperty::EInt,
        KHtcleoFeatMgrServerTraceReadPolicy,
        KHtcleoFeatMgrServerTraceWritePolicy);
    if (result == KErrAlreadyExists)
        {
        result = KErrNone;
        }
    if (result == KErrNone)
        {
        result = RProperty::Set(KHtcleoFeatMgrServerTraceCategory,
            KHtcleoFeatMgrServerTraceKey, 0);
        }
    return result;
    }
#endif
'''


RUN_SERVER = r'''static void RunServerL()
    {
    FUNC_LOG
    HtcleoFeatMgrServerTrace(0xE610u, KErrNone);

    // Naming the server thread after the startup helps to debug panics
    const TInt processRename = User::RenameProcess(KServerProcessName);
    HtcleoFeatMgrServerTrace(0xE611u, processRename);
    User::LeaveIfError(processRename);

    const TInt threadRename = User::RenameThread(KServerProcessName);
    HtcleoFeatMgrServerTrace(0xE612u, threadRename);
    User::LeaveIfError(threadRename);

    // Create and install the active scheduler we need
    CActiveScheduler* scheduler = new(ELeave) CActiveScheduler;
    HtcleoFeatMgrServerTrace(0xE613u, scheduler ? KErrNone : KErrNoMemory);
    CleanupStack::PushL(scheduler);

    CActiveScheduler::Install(scheduler);
    HtcleoFeatMgrServerTrace(0xE614u, KErrNone);

    // Now we are ready to instantiate the actual CServer2 instance
    HtcleoFeatMgrServerTrace(0xE615u, KErrNone);
    CFeatMgrServer* server = CFeatMgrServer::NewLC(KServerCActivePriority);
    HtcleoFeatMgrServerTrace(0xE616u, KErrNone);

    // Initialisation complete, now signal the client
    HtcleoFeatMgrServerTrace(0xE617u, KErrNone);
    RProcess::Rendezvous(KErrNone);
    HtcleoFeatMgrServerTrace(0xE618u, KErrNone);

    INFO_LOG("RunServerL() - Starting scheduler...");

    // Ready to run
    CActiveScheduler::Start();
    HtcleoFeatMgrServerTrace(0xE619u, KErrNone);

    INFO_LOG("RunServerL() - Scheduler stopped");

    // Cleanup the server and scheduler
    CleanupStack::PopAndDestroy(server);
    CleanupStack::PopAndDestroy(scheduler);
    }'''


E32_MAIN = r'''TInt E32Main()
    {
    FUNC_LOG

    __UHEAP_MARK;

    const TInt traceSetup = HtcleoFeatMgrServerTraceReset();
    HtcleoFeatMgrServerTrace(0xE600u, traceSetup);

    CTrapCleanup* cleanup = CTrapCleanup::New();
    TInt ret = KErrNoMemory;
    HtcleoFeatMgrServerTrace(0xE601u,
        cleanup ? KErrNone : KErrNoMemory);

    if (cleanup)
        {
        HtcleoFeatMgrServerTrace(0xE602u, KErrNone);
        TRAP(ret, RunServerL());

        // HTCLEO_FEATMGRSERVER_DEEPEST_STAGE_PRESERVE_V2
        // Every real RunServerL path publishes E610 before it can leave.  Do
        // not let the outer trap's E603 unwind record overwrite the last
        // reached E61x/E62x/E63x boundary.  The AknCap E209/E20A records still
        // carry the raw RunServerL leave code.
        TInt serverTraceValue = 0;
        const TInt serverTraceRead = RProperty::Get(
            KHtcleoFeatMgrServerTraceCategory,
            KHtcleoFeatMgrServerTraceKey, serverTraceValue);
        const TUint32 serverTraceStage =
            ((TUint32)serverTraceValue >> 16) & 0xffffu;
        if (serverTraceRead != KErrNone ||
            serverTraceStage < 0xE610u || serverTraceStage > 0xE63Eu)
            {
            HtcleoFeatMgrServerTrace(0xE603u, ret);
            }
        delete cleanup;
        }

    __UHEAP_MARKEND;

    return ret;
    }'''


CONSTRUCT_L = r'''void CFeatMgrServer::ConstructL()
    {
    FUNC_LOG
    HtcleoFeatMgrServerTrace(0xE630u, KErrNone);

#ifndef EXTENDED_FEATURE_MANAGER_TEST
    // Set server process system critical
    User::SetProcessCritical(User::ESystemCritical);
#else
    iShutdown.ConstructL();
    // ensure the server still exits even if the 1st client fails to connect
    if (!iShutdown.IsActive())
        {
        iShutdown.Start();
        }
#endif
    HtcleoFeatMgrServerTrace(0xE631u, KErrNone);

    // Add server to active scheduler
    StartL(KServerProcessName);
    HtcleoFeatMgrServerTrace(0xE632u, KErrNone);

    // Connect to file server.
    const TInt fsResult = iFs.Connect();
    HtcleoFeatMgrServerTrace(0xE633u, fsResult);
    User::LeaveIfError(fsResult);

    // Construct the registry before its first use below.  The stock source
    // called iRegistry->GetFeaturesFilePathAndName() while iRegistry was NULL.
    HtcleoFeatMgrServerTrace(0xE634u, KErrNone);
    iRegistry = CFeatMgrFeatureRegistry::NewL(iFs, *this);
    HtcleoFeatMgrServerTrace(0xE635u, KErrNone);

    // Register BUR.
    iBackupNotification = CBaBackupSessionWrapper::NewL();
    HtcleoFeatMgrServerTrace(0xE636u, KErrNone);

    TFileName temp(iRegistry->GetFeaturesFilePathAndName());
    HtcleoFeatMgrServerTrace(0xE637u, KErrNone);
    iBackupNotification->RegisterFileL(temp, *this);
    HtcleoFeatMgrServerTrace(0xE638u, KErrNone);

    TRAPD(err, iRegistry->ReadFeatureFilesL());
    HtcleoFeatMgrServerTrace(0xE639u, err);
    switch (err)
        {
        case KErrNotFound:
            ERROR_LOG("CFeatMgrServer::ConstructL() - no feature files found in ROM - going to panic");
            ::FmgrFatalErrorL(err, KPanicCategory, EPanicNoFeatureFiles);
            break;
        case KErrCorrupt:
            ERROR_LOG("CFeatMgrServer::ConstructL() - feature information in ROM is invalid - going to panic");
            ::FmgrFatalErrorL(err, KPanicCategory, EPanicInvalidFeatureInfo);
            break;
        default:
            User::LeaveIfError(err);
            break;
        }
    HtcleoFeatMgrServerTrace(0xE63Au, KErrNone);

    // List and load plugins and feature info.
    HtcleoFeatMgrServerTrace(0xE63Bu, KErrNone);
    TBool found = LoadPluginsL();
    HtcleoFeatMgrServerTrace(0xE63Cu, found);

    if (found)
        {
        // Timer for deleting plugins and for comparing feature lists.
        iTimer = CFeatMgrTimer::NewL(*this);
        }
    else
        {
        iRegistry->ReadRuntimeFeaturesL(iFeaturesReady);
        }
    HtcleoFeatMgrServerTrace(0xE63Du, found);
    HtcleoFeatMgrServerTrace(0xE63Eu, KErrNone);
    }'''


NEW_LC = r'''CFeatMgrServer* CFeatMgrServer::NewLC(const TInt aPriority)
    {
    FUNC_LOG
    HtcleoFeatMgrServerTrace(0xE620u, KErrNone);

    CFeatMgrServer* self = new(ELeave)
        CFeatMgrServer(aPriority, EUnsharableSessions);
    HtcleoFeatMgrServerTrace(0xE621u,
        self ? KErrNone : KErrNoMemory);

    CleanupStack::PushL(self);
    HtcleoFeatMgrServerTrace(0xE622u, KErrNone);
    self->ConstructL();
    HtcleoFeatMgrServerTrace(0xE623u, KErrNone);

    return self;
    }'''


CLIENT_FAILURE_BRIDGE = r'''        HtcleoFeatMgrAknCapTrace(0xE548u, exitAndResult);

        // If startup failed, preserve the deepest server-side E6xx stage in
        // the existing AknCap property.  Missing/invalid trace data leaves the
        // already-published E548 completion untouched.
        if (err != KErrNone)
            {
            TInt serverTraceValue = 0;
            const TInt serverTraceRead = RProperty::Get(
                TUid::Uid(0x10205054), 0x7f044302u, serverTraceValue);
            const TUint32 serverStage =
                ((TUint32)serverTraceValue >> 16) & 0xffffu;
            if (serverTraceRead == KErrNone &&
                serverStage >= 0xE600u && serverStage <= 0xE63Eu)
                {
                HtcleoFeatMgrAknCapTrace(serverStage,
                    (TInt)(TInt16)(serverTraceValue & 0xffff));
                }
            }
'''


def install_startup(text: str) -> str:
    text = replace_once(
        text,
        '#include "featmgrconfiguration.h"\n',
        '#include "featmgrconfiguration.h"\n'
        '#include "htcleo_featmgrserver_trace.h"\n'
        '#include <e32property.h>\n' + STARTUP_HELPER,
        "startup includes/helper",
    )
    text = replace_function(
        text,
        "static void RunServerL()\n",
        "// -----------------------------------------------------------------------------\n"
        "// Main function",
        RUN_SERVER,
        "RunServerL",
    )
    return replace_function(
        text, "TInt E32Main()\n", "", E32_MAIN, "E32Main"
    ) if False else replace_once(
        text,
        text[text.find("TInt E32Main()\n"):],
        E32_MAIN + "\n",
        "E32Main tail",
    )


def install_server(text: str) -> str:
    text = replace_once(
        text,
        '#include "featmgrsecuritypolicy.h"\n',
        '#include "featmgrsecuritypolicy.h"\n'
        '#include "htcleo_featmgrserver_trace.h"\n',
        "server trace include",
    )
    text = replace_function(
        text,
        "void CFeatMgrServer::ConstructL()\n",
        "// -----------------------------------------------------------------------------\n"
        "// CFeatMgrServer::NewLC",
        CONSTRUCT_L,
        "CFeatMgrServer::ConstructL",
    )
    return replace_function(
        text,
        "CFeatMgrServer* CFeatMgrServer::NewLC(const TInt aPriority)\n",
        "#ifdef EXTENDED_FEATURE_MANAGER_TEST",
        NEW_LC,
        "CFeatMgrServer::NewLC",
    )


def install_client(text: str) -> str:
    text = replace_once(
        text,
        '#include "htcleo_featmgr_trace.h"\n',
        '#include "htcleo_featmgr_trace.h"\n#include <e32property.h>\n',
        "client property include",
    )
    return replace_once(
        text,
        "        HtcleoFeatMgrAknCapTrace(0xE548u, exitAndResult);\n",
        CLIENT_FAILURE_BRIDGE,
        "client server-stage bridge",
    )


def verify(paths: dict[str, Path]) -> None:
    texts = {name: path.read_text(encoding="latin-1") for name, path in paths.items()}
    server_trace = texts["startup"] + "\n" + texts["server"]
    stages = (
        list(range(0xE600, 0xE604))
        + list(range(0xE610, 0xE61A))
        + list(range(0xE620, 0xE624))
        + list(range(0xE630, 0xE63F))
    )
    registry_create = "iRegistry = CFeatMgrFeatureRegistry::NewL(iFs, *this);"
    registry_use = "TFileName temp(iRegistry->GetFeaturesFilePathAndName());"
    preserve_bounds = (
        "serverTraceStage < 0xE610u || serverTraceStage > 0xE63Eu",
        "serverTraceStage < 0xE610u || serverTraceStage > 0xE64Fu",
    )
    checks = {
        "startup marker": texts["startup"].count(MARKER) == 1,
        "header marker": texts["header"].count(MARKER + "_HEADER") == 1,
        "MMP marker": texts["mmp"].count(MARKER) == 1,
        "MMP macro": texts["mmp"].count(f"MACRO           {MACRO}") == 1,
        "deepest-stage preserve marker": texts["startup"].count(
            PRESERVE_MARKER
        ) == 1,
        "server helper definition": texts["startup"].count(
            "void HtcleoFeatMgrServerTrace(TUint32 aStage, TInt aResult)"
        ) == 1,
        "single Define": texts["startup"].count("RProperty::Define(") == 1,
        "helper Set plus reset Set": texts["startup"].count("RProperty::Set(") == 2,
        "server unwind Get": texts["startup"].count(
            "const TInt serverTraceRead = RProperty::Get("
        ) == 1,
        "E603 fallback only": sum(
            texts["startup"].count(bound) for bound in preserve_bounds
        ) == 1,
        "client Get": texts["client"].count(
            "const TInt serverTraceRead = RProperty::Get("
        ) == 1,
        "all server stages": all(
            server_trace.count(
                f"HtcleoFeatMgrServerTrace(0x{stage:04X}u"
            ) == 1
            for stage in stages
        ),
        "registry constructed once": texts["server"].count(registry_create) == 1,
        "fixed registry path used once": texts["server"].count(registry_use) == 1,
        "registry order fixed": texts["server"].find(registry_create)
        < texts["server"].find(registry_use),
        "stock wait retained": texts["client"].count("User::WaitForRequest( stat )") == 1,
        "no delay": "User::After" not in server_trace,
        "no display": "HalFunction" not in server_trace,
        "no trace file": "AKNCAP.TXT" not in server_trace,
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
        "mmp": component / "group/featmgrserver.mmp",
        "header": component / "src/inc/htcleo_featmgrserver_trace.h",
        "startup": component / "src/serverexe/featmgrstartup.cpp",
        "server": component / "src/serverexe/featmgrserver.cpp",
        "client": component / "src/clientdll/featmgrclient.cpp",
    }
    texts = {
        name: path.read_text(encoding="latin-1")
        for name, path in paths.items()
        if name != "header" and path.exists()
    }
    if MARKER not in texts["startup"]:
        texts["mmp"] = replace_once(
            texts["mmp"],
            "SMPSAFE\n",
            f"// {MARKER}\nMACRO           {MACRO}\n\nSMPSAFE\n",
            "featmgrserver MMP macro",
        )
        texts["startup"] = install_startup(texts["startup"])
        texts["server"] = install_server(texts["server"])
        texts["client"] = install_client(texts["client"])
        for name, text in texts.items():
            paths[name].write_text(text, encoding="latin-1")
        paths["header"].write_text(HEADER, encoding="latin-1")
    elif PRESERVE_MARKER not in texts["startup"]:
        texts["startup"] = replace_once(
            texts["startup"],
            "        TRAP(ret, RunServerL());\n"
            "        HtcleoFeatMgrServerTrace(0xE603u, ret);\n",
            "        TRAP(ret, RunServerL());\n\n"
            "        // HTCLEO_FEATMGRSERVER_DEEPEST_STAGE_PRESERVE_V2\n"
            "        // Every real RunServerL path publishes E610 before it can leave.  Do\n"
            "        // not let the outer trap's E603 unwind record overwrite the last\n"
            "        // reached E61x/E62x/E63x boundary.  The AknCap E209/E20A records still\n"
            "        // carry the raw RunServerL leave code.\n"
            "        TInt serverTraceValue = 0;\n"
            "        const TInt serverTraceRead = RProperty::Get(\n"
            "            KHtcleoFeatMgrServerTraceCategory,\n"
            "            KHtcleoFeatMgrServerTraceKey, serverTraceValue);\n"
            "        const TUint32 serverTraceStage =\n"
            "            ((TUint32)serverTraceValue >> 16) & 0xffffu;\n"
            "        if (serverTraceRead != KErrNone ||\n"
            "            serverTraceStage < 0xE610u || serverTraceStage > 0xE63Eu)\n"
            "            {\n"
            "            HtcleoFeatMgrServerTrace(0xE603u, ret);\n"
            "            }\n",
            "preserve deepest server stage across unwind",
        )
        paths["startup"].write_text(texts["startup"], encoding="latin-1")
    elif texts["server"].count(
        "HtcleoFeatMgrServerTrace(0xE631u, KErrNone);"
    ) == 2:
        # Normalize the first generated draft: E631 is one logical runtime
        # checkpoint shared by the test and production preprocessor branches.
        texts["server"] = replace_once(
            texts["server"],
            "    User::SetProcessCritical(User::ESystemCritical);\n"
            "    HtcleoFeatMgrServerTrace(0xE631u, KErrNone);\n",
            "    User::SetProcessCritical(User::ESystemCritical);\n",
            "normalize production E631",
        )
        texts["server"] = replace_once(
            texts["server"],
            "        iShutdown.Start();\n"
            "        }\n"
            "    HtcleoFeatMgrServerTrace(0xE631u, KErrNone);\n"
            "#endif\n",
            "        iShutdown.Start();\n"
            "        }\n"
            "#endif\n"
            "    HtcleoFeatMgrServerTrace(0xE631u, KErrNone);\n",
            "normalize test E631",
        )
        paths["server"].write_text(texts["server"], encoding="latin-1")
    verify(paths)
    print(
        "HTCLEO_FEATMGRSERVER_STARTUP_FIX_TRACE=installed "
        "stages=E600-E63E deepest-stage-preserve=installed"
    )


if __name__ == "__main__":
    main()
