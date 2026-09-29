#!/usr/bin/env python3
"""Publish AknCap post-construction readiness for the HTCLEO parent wait."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAPSERVER_PROPERTY_READY_SIGNAL_V1"

CONSTANT_ANCHOR = '#include <UikonInternalPSKeys.h>'
CONSTANTS = r'''// HTCLEO_AKNCAPSERVER_PROPERTY_READY_SIGNAL_V1
const TUid KHtcleoAknReadyCategory = {0x10207218};
const TUint KHtcleoAknReadyKey = 0x7f044302u;

#include <UikonInternalPSKeys.h>'''

OLD_READY = r'''    if (!error)
        {
        // HTCLEO_AKNCAPSERVER_RENDEZVOUS_READY_COMPAT_V1
        // ConstructAppFromCommandLineL has completed every application,
        // document, AppUi and SetAppReady boundary.  Explicitly complete the
        // process readiness request before entering the permanent scheduler.
        HtcleoAknCapLog(0x0000E215u, KRequestPending, 0u);
        RProcess::Rendezvous(KErrNone);
        HtcleoAknCapLog(0x0000E216u, KErrNone, 0u);
        HtcleoAknCapLog(0x0000E20Bu, KErrNone, 0u);
        env->Execute();
        HtcleoAknCapLog(0x0000E20Cu, KErrNone, 0u);
        }
'''

NEW_READY = r'''    if (!error)
        {
        // HTCLEO_AKNCAPSERVER_PROPERTY_READY_SIGNAL_V1
        // The caller subscribed while this process was suspended. Publish
        // only after complete application/document/AppUi construction, then
        // preserve the reference rendezvous signal and permanent scheduler.
        HtcleoAknCapLog(0x0000E217u, KRequestPending,
            KHtcleoAknReadyKey);
        const TInt htcleoAknReadySet = RProperty::Set(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey, 1);
        HtcleoAknCapLog(0x0000E218u, htcleoAknReadySet, 1u);
        if(htcleoAknReadySet != KErrNone)
            {
            error = htcleoAknReadySet;
            }
        }

    if (!error)
        {
        // HTCLEO_AKNCAPSERVER_RENDEZVOUS_READY_COMPAT_V1
        HtcleoAknCapLog(0x0000E215u, KRequestPending, 0u);
        RProcess::Rendezvous(KErrNone);
        HtcleoAknCapLog(0x0000E216u, KErrNone, 0u);
        HtcleoAknCapLog(0x0000E20Bu, KErrNone, 0u);
        env->Execute();
        HtcleoAknCapLog(0x0000E20Cu, KErrNone, 0u);
        }
'''


def verify(source: str) -> None:
    checks = {
        "two scoped markers": source.count(MARKER) == 2,
        "single ready key": source.count(
            "KHtcleoAknReadyKey = 0x7f044302u"
        ) == 1,
        "single ready set": source.count(
            "const TInt htcleoAknReadySet = RProperty::Set("
        ) == 1,
        "registration-aware ready value": (
            source.count(
                "KHtcleoAknReadyCategory, KHtcleoAknReadyKey, 1"
            ) == 1
            if "HTCLEO_AKNCAPSERVER_REGISTRATION_LIFETIME_REPAIR_V1"
            not in source
            else source.count("htcleoAknReadyValue") == 3
        ),
        "set before rendezvous": (
            source.index("const TInt htcleoAknReadySet")
            < source.index("RProcess::Rendezvous(KErrNone)")
        ),
        "fail closed": source.count("error = htcleoAknReadySet;") == 1,
        "ready stages": all(
            source.count(f"HtcleoAknCapLog(0x{stage:08X}u") == 1
            for stage in (0xE217, 0xE218)
        ),
        "reference rendezvous retained": source.count(
            "RProcess::Rendezvous(KErrNone)"
        ) == 1,
        "single scheduler": source.count("env->Execute();") == 1,
        "no startup timer or wait": (
            "User::After(" not in source
            and "User::WaitForRequest" not in source
        ),
        "no display probe": (
            "EHalGroupPlatformSpecific1, 2" not in source
            and "c6400000" not in source.lower()
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknCap readiness signal verification failed: "
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
        if source.count(CONSTANT_ANCHOR) != 1:
            raise SystemExit("AknCap readiness constant anchor is not unique")
        if source.count(OLD_READY) != 1:
            raise SystemExit(
                "AknCap readiness body anchor: expected one, found "
                + str(source.count(OLD_READY))
            )
        source = source.replace(CONSTANT_ANCHOR, CONSTANTS, 1)
        source = source.replace(OLD_READY, NEW_READY, 1)

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAPSERVER_PROPERTY_READY_SIGNAL=installed "
        "stages=E217-E218"
    )


if __name__ == "__main__":
    main()
