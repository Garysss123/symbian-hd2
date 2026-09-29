#!/usr/bin/env python3
"""Add the AknCap-side P&S bridge for the eikcore pre-factory trace.

The shared DLL only updates one integer property while running in the exact
AknCap SID. The isolated executable owns the property and writes its final
value to the already-established AKNCAP.TXT stream after the trapped exported
call returns. No error, wait or application control flow is changed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_EIKCORE_TRACE_BRIDGE_V5"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


CONSTANTS = r'''
#ifdef __HTCLEO_AKNCAPSERVER_STARTUP_LOG__
// HTCLEO_AKNCAPSERVER_EIKCORE_TRACE_BRIDGE_V5
const TUid KHtcleoAknCapTraceCategory = {0x10207218};
const TUint KHtcleoEikCoreTraceKey = 0x7f044301u;
_LIT_SECURITY_POLICY_PASS(KHtcleoEikCoreTraceReadPolicy);
_LIT_SECURITY_POLICY_C1(KHtcleoEikCoreTraceWritePolicy,
    ECapabilityWriteDeviceData);
#endif
'''


OLD_CALL = r'''        HtcleoAknCapLog(0x0000E207u, KErrNone, 1u);
        HtcleoAknCapLog(0x0000E208u, KErrNone, 0u);
        TRAP(error,
            env->ConstructAppFromCommandLineL(
                aApplicationFactory, *commandLine));
        HtcleoAknCapLog(0x0000E209u, error, 0u);
'''


NEW_CALL = r'''        TInt traceSetup = RProperty::Define(
            KHtcleoAknCapTraceCategory,
            KHtcleoEikCoreTraceKey,
            RProperty::EInt,
            KHtcleoEikCoreTraceReadPolicy,
            KHtcleoEikCoreTraceWritePolicy);
        if (traceSetup == KErrAlreadyExists)
            {
            traceSetup = KErrNone;
            }
        if (traceSetup == KErrNone)
            {
            traceSetup = RProperty::Set(
                KHtcleoAknCapTraceCategory,
                KHtcleoEikCoreTraceKey,
                0);
            }
        HtcleoAknCapLog(0x0000E213u, traceSetup, 0u);

        HtcleoAknCapLog(0x0000E207u, KErrNone, 1u);
        HtcleoAknCapLog(0x0000E208u, KErrNone, 0u);
        TRAP(error,
            env->ConstructAppFromCommandLineL(
                aApplicationFactory, *commandLine));

        TInt traceValue = -1;
        const TInt traceRead = RProperty::Get(
            KHtcleoAknCapTraceCategory,
            KHtcleoEikCoreTraceKey,
            traceValue);
        HtcleoAknCapLog(0x0000E214u, traceRead,
            (TUint32)traceValue);
        (void)RProperty::Delete(
            KHtcleoAknCapTraceCategory,
            KHtcleoEikCoreTraceKey);
        HtcleoAknCapLog(0x0000E209u, error, 0u);
'''


def verify(source: str) -> None:
    checks = {
        "bridge marker": source.count(MARKER) == 1,
        "category": source.count(
            "KHtcleoAknCapTraceCategory = {0x10207218}"
        ) == 1,
        "key": source.count("KHtcleoEikCoreTraceKey = 0x7f044301u") == 1,
        "single define": source.count(
            "TInt traceSetup = RProperty::Define("
        ) == 1,
        "single bridge set": source.count(
            "traceSetup = RProperty::Set("
        ) == 1,
        "single bridge get": source.count(
            "const TInt traceRead = RProperty::Get("
        ) == 1,
        "delete before lifetime repair or retain after it": (
            source.count("(void)RProperty::Delete(") == 1
            if "HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR_V1"
            not in source
            else source.count("(void)RProperty::Delete(") == 0
        ),
        "setup record": source.count(
            "HtcleoAknCapLog(0x0000E213u"
        ) == 1,
        "result record": source.count(
            "HtcleoAknCapLog(0x0000E214u"
        ) == 1,
        "single exported call": source.count(
            "env->ConstructAppFromCommandLineL("
        ) == 1,
        "original result retained": (
            source.count("HtcleoAknCapLog(0x0000E209u, error, 0u)") == 1
            if "HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR_V1"
            not in source
            else source.count(
                "HtcleoAknCapLog(0x0000E209u, error,"
            ) == 1
            and "(TUint32)htcleoAknServerRegistration" in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src/"
        / "AknCapServerEntry.cpp"
    )
    source = source_path.read_text(encoding="utf-8")

    if MARKER not in source:
        source = replace_once(
            source,
            "#include <e32property.h>\n",
            "#include <e32property.h>\n" + CONSTANTS,
            "trace constants",
        )
        source = replace_once(
            source,
            OLD_CALL,
            NEW_CALL,
            "exported ConstructApp trace bridge",
        )

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print("HTCLEO_AKNCAPSERVER_EIKCORE_TRACE_BRIDGE=installed stages=E213-E214")


if __name__ == "__main__":
    main()
