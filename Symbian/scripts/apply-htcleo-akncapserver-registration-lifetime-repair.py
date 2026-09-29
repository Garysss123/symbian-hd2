#!/usr/bin/env python3
"""Keep the HTCLEO AknCap app server registered after readiness.

The 509 hardware run proved that ConstructAppFromCommandLineL returned and the
ready property reached value 1, but neither the fixed server name nor any
*_10207218_AppServer candidate remained in the kernel registry.  This repair
validates the registration in the AknCap process itself, retries the exported
CEikAppServer::ConstructL path once when the exact name is absent, and retains
the post-critical breadcrumb property so an unexpected scheduler return is
observable without changing scheduler behaviour.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR_V1"

INCLUDE_ANCHOR = "#include <eikenv.h>\n"
INCLUDE_REPLACEMENT = "#include <eikenv.h>\n#include <eikserverapp.h>\n"

FUNCTION_ANCHOR = """class CHtcleoAknCapEikonEnv : public CEikonEnv
    {
public:
    TInt HtcleoConstructorError() const
        {
        return CoeEnvConstructorError();
        }
    };

static TInt HtcleoRunAknCapApplication(
    TApaApplicationFactory aApplicationFactory)
"""

STATE_ANCHOR = r'''    TBool disableShutdownChecks = EFalse;
    TInt error = CApaCommandLine::GetCommandLineFromProcessEnvironment(
'''

STATE_REPLACEMENT = r'''    TBool disableShutdownChecks = EFalse;
    TInt htcleoAknServerRegistration = KErrNotReady;
    TInt error = CApaCommandLine::GetCommandLineFromProcessEnvironment(
'''

HELPER = r'''// HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR_V1
static TInt HtcleoEnsureAknCapServerRegistered(CEikonEnv& aEnv)
    {
    _LIT(KHtcleoAknCapServerNameFormat, "%08x_%08x_AppServer");
    TName expectedName;
    expectedName.Format(
        KHtcleoAknCapServerNameFormat,
        KUikonUidPluginInterfaceNotifiers,
        KAknCapServerUid.iUid);

    TFullName foundName;
    TFindServer finder(expectedName);
    TInt findResult = finder.Next(foundName);
    HtcleoAknCapLog(0x0000E219u, findResult,
        (TUint32)foundName.Length());
    if (findResult == KErrNone)
        {
        return KErrNone;
        }

    CEikAppServer* appServer = aEnv.AppServer();
    TInt repairResult = appServer ? KErrNone : KErrNotReady;
    if (appServer)
        {
        TRAP(repairResult, appServer->ConstructL(expectedName));
        }
    HtcleoAknCapLog(0x0000E21Au, repairResult,
        appServer ? 1u : 0u);

    foundName.Zero();
    TFindServer verifier(expectedName);
    const TInt verifyResult = verifier.Next(foundName);
    HtcleoAknCapLog(0x0000E21Bu, verifyResult,
        (TUint32)foundName.Length());
    return verifyResult;
    }

class CHtcleoAknCapEikonEnv : public CEikonEnv
    {
public:
    TInt HtcleoConstructorError() const
        {
        return CoeEnvConstructorError();
        }
    };

static TInt HtcleoRunAknCapApplication(
    TApaApplicationFactory aApplicationFactory)
'''

DELETE_ANCHOR = r'''        (void)RProperty::Delete(
            KHtcleoAknCapTraceCategory,
            KHtcleoEikCoreTraceKey);
        HtcleoAknCapLog(0x0000E209u, error, 0u);
'''

DELETE_REPLACEMENT = r'''        // Keep the property alive: every post-E100 lifecycle record uses
        // this key, and deleting it here made all later breadcrumbs vanish.
        htcleoAknServerRegistration = error;
        if (error == KErrNone)
            {
            htcleoAknServerRegistration =
                HtcleoEnsureAknCapServerRegistered(*env);
            }
        HtcleoAknCapLog(0x0000E209u, error,
            (TUint32)htcleoAknServerRegistration);
'''

READY_ANCHOR = r'''        const TInt htcleoAknReadySet = RProperty::Set(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey, 1);
        HtcleoAknCapLog(0x0000E218u, htcleoAknReadySet, 1u);
'''

READY_REPLACEMENT = r'''        const TInt htcleoAknReadyValue =
            (htcleoAknServerRegistration == KErrNone) ? 1 : 2;
        const TInt htcleoAknReadySet = RProperty::Set(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey,
            htcleoAknReadyValue);
        HtcleoAknCapLog(0x0000E218u, htcleoAknReadySet,
            (TUint32)htcleoAknReadyValue);
'''

def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "server header": source.count("#include <eikserverapp.h>") == 1,
        "single helper": source.count(
            "static TInt HtcleoEnsureAknCapServerRegistered"
        ) == 1,
        "exact stock name format": source.count(
            'KHtcleoAknCapServerNameFormat, "%08x_%08x_AppServer"'
        ) == 1,
        "single exported repair": source.count(
            "appServer->ConstructL(expectedName)"
        ) == 1,
        "function-scope registration state": source.count(
            "TInt htcleoAknServerRegistration = KErrNotReady;"
        ) == 1,
        "registration stages": all(
            source.count(f"HtcleoAknCapLog(0x0000E{stage}u") == 1
            for stage in ("219", "21A", "21B")
        ),
        "trace property retained": source.count(
            "(void)RProperty::Delete("
        ) == 0,
        "ready encodes registration": source.count(
            "htcleoAknReadyValue"
        ) == 3,
        "single scheduler": source.count("env->Execute();") == 1,
        "scheduler behavior unchanged": (
            "User::After(" not in source
            and "while (error == KErrNone);" not in source
        ),
        "no display probe": (
            "EHalGroupPlatformSpecific1, 2" not in source
            and "c6400000" not in source.lower()
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknCap registration/lifetime verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src/"
          "AknCapServerEntry.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing AknCap server input: {source_path}")

    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        source = replace_once(
            source, INCLUDE_ANCHOR, INCLUDE_REPLACEMENT, "server header"
        )
        source = replace_once(
            source, FUNCTION_ANCHOR, HELPER, "registration helper"
        )
        source = replace_once(
            source, STATE_ANCHOR, STATE_REPLACEMENT,
            "registration state",
        )
        source = replace_once(
            source, DELETE_ANCHOR, DELETE_REPLACEMENT,
            "retained breadcrumb property",
        )
        source = replace_once(
            source, READY_ANCHOR, READY_REPLACEMENT,
            "registration-aware ready value",
        )
    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR=installed "
        "stages=E219-E21B ready=1-registered-2-missing"
    )


if __name__ == "__main__":
    main()
