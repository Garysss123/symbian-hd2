#!/usr/bin/env python3
"""Add a narrow P&S trace inside CFeatMgrServer::LoadPluginsL()."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_FEATMGRSERVER_LOADPLUGINS_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def widen_once(text: str, old: str, new: str, label: str) -> str:
    old_count = text.count(old)
    new_count = text.count(new)
    if old_count == 1 and new_count == 0:
        return text.replace(old, new, 1)
    if old_count == 0 and new_count == 1:
        return text
    raise SystemExit(
        f"{label}: expected old/new counts 1/0 or 0/1, got "
        f"{old_count}/{new_count}"
    )


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


LOAD_PLUGINS = r'''TBool CFeatMgrServer::LoadPluginsL()
    {
    FUNC_LOG
    // HTCLEO_FEATMGRSERVER_LOADPLUGINS_TRACE_V1
    HtcleoFeatMgrServerTrace(0xE640u, KErrNone);

    RImplInfoPtrArray implInfoArray;
    TBool ret( EFalse );

    // Use ECom to read information about existing interface implementations.
    _LIT8( KEmptyString, "" );
    TEComResolverParams resolverParams;
    resolverParams.SetDataType(KEmptyString);
    resolverParams.SetWildcardMatch(ETrue);
    HtcleoFeatMgrServerTrace(0xE641u, KErrNone);

    TCleanupItem cleanupItem(ResetAndDestroyArray, &implInfoArray);
    CleanupStack::PushL(cleanupItem);
    HtcleoFeatMgrServerTrace(0xE642u, KErrNone);

    // Preserve the stock call and leave semantics, but record its exact return
    // before re-leaving so the outer E63B boundary is no longer ambiguous.
    HtcleoFeatMgrServerTrace(0xE643u, KErrNone);
    TInt listResult = KErrNone;
#ifdef EXTENDED_FEATURE_MANAGER_TEST
    TRAP(listResult, REComSession::ListImplementationsL(
        KFeatureInfoPluginInterfaceUid, implInfoArray));
#else
    TRAP(listResult, REComSession::ListImplementationsL(
        KFeatureInfoPluginInterfaceUid, resolverParams,
        KRomOnlyResolverUid, implInfoArray));
#endif
    HtcleoFeatMgrServerTrace(0xE644u, listResult);
    User::LeaveIfError(listResult);

    const TInt count = implInfoArray.Count();
    HtcleoFeatMgrServerTrace(0xE645u, count);
    if (count == 0)
        {
        iPluginsReady = ETrue;
        ret = EFalse;
        HtcleoFeatMgrServerTrace(0xE646u, KErrNone);
        }
    else
        {
        for (TInt i = 0; i < count; ++i)
            {
            HtcleoFeatMgrServerTrace(0xE647u, i);
            CFeatMgrPluginHandler* pluginHandler = NULL;
            TRAPD(err, pluginHandler = CFeatMgrPluginHandler::NewL(
                implInfoArray[i]->ImplementationUid(), *this));
            HtcleoFeatMgrServerTrace(0xE648u, err);
            if (err == KErrNone)
                {
                CleanupStack::PushL(pluginHandler);
                TRAP(err, pluginHandler->SendCommandL(
                    FeatureInfoCommand::ELoadFeatureInfoCmdId));
                HtcleoFeatMgrServerTrace(0xE649u, err);
                if (err == KErrNotSupported)
                    {
                    TRAP(err, pluginHandler->SendCommandL(
                        FeatureInfoCommand::ELoadEnhancedFeatureInfoCmdId));
                    HtcleoFeatMgrServerTrace(0xE64Au, err);
                    }
                }
            if (err == KErrNoMemory)
                {
                User::Leave(err);
                }
            else if (err != KErrNone)
                {
                ::FmgrFatalErrorL(err, KPanicCategory, EPanicLoadPluginError);
                }

            SFeatMgrPluginInfo plugin;
            plugin.iPluginHandler = pluginHandler;
            plugin.iPluginReady = EFalse;
            const TInt appendResult = iPluginList.Append(plugin);
            HtcleoFeatMgrServerTrace(0xE64Bu, appendResult);
            User::LeaveIfError(appendResult);
            CleanupStack::Pop(pluginHandler);
            }
        HtcleoFeatMgrServerTrace(0xE64Cu, count);
        ret = ETrue;
        }

    HtcleoFeatMgrServerTrace(0xE64Du, ret);
    CleanupStack::PopAndDestroy(&implInfoArray);
    HtcleoFeatMgrServerTrace(0xE64Eu, ret);
    HtcleoFeatMgrServerTrace(0xE64Fu, ret);
    return ret;
    }'''


def verify(startup: Path, server: Path, client: Path) -> None:
    startup_text = startup.read_text(encoding="latin-1")
    server_text = server.read_text(encoding="latin-1")
    client_text = client.read_text(encoding="latin-1")
    stages = range(0xE640, 0xE650)
    checks = {
        "marker": server_text.count(MARKER) == 1,
        "all stages": all(
            server_text.count(f"HtcleoFeatMgrServerTrace(0x{stage:04X}u") == 1
            for stage in stages
        ),
        "list trap": server_text.count("TRAP(listResult,") == 2,
        "list result re-leave": server_text.count(
            "User::LeaveIfError(listResult);"
        ) == 1,
        "single append": server_text.count("iPluginList.Append(plugin)") == 1,
        "server preserve upper": startup_text.count(
            "serverTraceStage < 0xE610u || serverTraceStage > 0xE64Fu"
        ) == 1,
        "client bridge upper": client_text.count(
            "serverStage >= 0xE600u && serverStage <= 0xE64Fu"
        ) == 1,
        "no delay": "User::After" not in LOAD_PLUGINS,
        "no display": "HalFunction" not in LOAD_PLUGINS,
        "no file log": "AKNCAP.TXT" not in LOAD_PLUGINS,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("LoadPlugins trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/os/persistentdata/featuremgmt/featuremgr"
    startup = component / "src/serverexe/featmgrstartup.cpp"
    server = component / "src/serverexe/featmgrserver.cpp"
    client = component / "src/clientdll/featmgrclient.cpp"
    for path in (startup, server, client):
        if not path.is_file():
            raise SystemExit(f"missing source: {path}")

    startup_text = widen_once(
        startup.read_text(encoding="latin-1"),
        "serverTraceStage < 0xE610u || serverTraceStage > 0xE63Eu",
        "serverTraceStage < 0xE610u || serverTraceStage > 0xE64Fu",
        "server preserve range",
    )
    client_text = widen_once(
        client.read_text(encoding="latin-1"),
        "serverStage >= 0xE600u && serverStage <= 0xE63Eu",
        "serverStage >= 0xE600u && serverStage <= 0xE64Fu",
        "client bridge range",
    )
    server_text = server.read_text(encoding="latin-1")
    if MARKER not in server_text:
        server_text = replace_function(
            server_text,
            "TBool CFeatMgrServer::LoadPluginsL()\n",
            "// -----------------------------------------------------------------------------\n"
            "// CFeatMgrServer::PluginsReady()",
            LOAD_PLUGINS,
            "CFeatMgrServer::LoadPluginsL",
        )

    startup.write_text(startup_text, encoding="latin-1")
    client.write_text(client_text, encoding="latin-1")
    server.write_text(server_text, encoding="latin-1")
    verify(startup, server, client)
    print(
        "HTCLEO_FEATMGRSERVER_LOADPLUGINS_TRACE=installed "
        "stages=E640-E64F preserve=E610-E64F"
    )


if __name__ == "__main__":
    main()
