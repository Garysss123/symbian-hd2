#!/usr/bin/env python3
"""Run AppArc's first application scan without the broken timer path.

On HTCLEO the AppArc CPeriodic object is created and Start() returns, but its
first callback is never delivered.  Keep later rescan behaviour unchanged;
only the initial population is completed synchronously before APSEXE enters
its active scheduler.  Icon failures are fail-open so one malformed optional
application cannot prevent the UI command list from continuing.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_APPARC_FIRST_SCAN_SYNCHRONOUS_V1"
DURABLE_MARKER = "HTCLEO_APPARC_DURABLE_LOG_V1"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    source = (
        args.root
        / "sf/mw/appsupport/appfw/apparchitecture/aplist/aplapplist.cpp"
    )
    if not source.is_file():
        raise SystemExit(f"missing AppArc source: {source}")

    text = source.read_text(encoding="utf-8")
    if DURABLE_MARKER not in text:
        raise SystemExit("AppArc durable logging must be installed first")

    if MARKER not in text:
        anchor = (
            "\tiAppRegFinder->FindAllAppsL(CApaAppRegFinder::EScanAllDrives);\n"
            "\tHtcleoApaListLog(0x00001101u, KErrNone, 0u);\n"
            " \n"
            " \t// DEF072701\n"
        )
        replacement = (
            "\tiAppRegFinder->FindAllAppsL(CApaAppRegFinder::EScanAllDrives);\n"
            "\tHtcleoApaListLog(0x00001101u, KErrNone, 0u);\n"
            "\n"
            f"\t// {MARKER}\n"
            "\t// HTCLEO's timer completion path does not deliver the first\n"
            "\t// CPeriodic callback.  Complete only the boot scan inline; later\n"
            "\t// rescans retain the stock asynchronous policy below.\n"
            "\tif (!IsFirstScanComplete())\n"
            "\t\t{\n"
            "\t\tHtcleoApaListLog(0x00001140u, KErrNone, 0u);\n"
            "\t\tTUint32 htcleoScanCalls = 0u;\n"
            "\t\tTBool htcleoMore = EFalse;\n"
            "\t\tdo\n"
            "\t\t\t{\n"
            "\t\t\thtcleoMore = IdleUpdateL();\n"
            "\t\t\t++htcleoScanCalls;\n"
            "\t\t\t}\n"
            "\t\twhile (htcleoMore);\n"
            "\t\tHtcleoApaListLog(0x00001141u, KErrNone, htcleoScanCalls);\n"
            "\n"
            "\t\t// The CPeriodic has not been armed yet and is safe to retire.\n"
            "\t\tStopIdler();\n"
            "\t\tTInt htcleoFirstIconError = KErrNone;\n"
            "\t\tTUint32 htcleoIconsAttempted = 0u;\n"
            "\t\tif (!iLoadMbmIconsOnDemand)\n"
            "\t\t\t{\n"
            "\t\t\tfor (CApaAppData* htcleoApp = iAppData; htcleoApp;\n"
            "\t\t\t\thtcleoApp = htcleoApp->Next())\n"
            "\t\t\t\t{\n"
            "\t\t\t\tif (htcleoApp->MbmIconsRequireLoading())\n"
            "\t\t\t\t\t{\n"
            "\t\t\t\t\tTRAPD(htcleoIconError, htcleoApp->LoadIconsL());\n"
            "\t\t\t\t\t++htcleoIconsAttempted;\n"
            "\t\t\t\t\tif (htcleoFirstIconError == KErrNone &&\n"
            "\t\t\t\t\t\thtcleoIconError != KErrNone)\n"
            "\t\t\t\t\t\thtcleoFirstIconError = htcleoIconError;\n"
            "\t\t\t\t\t}\n"
            "\t\t\t\t}\n"
            "\t\t\t}\n"
            "\t\tHtcleoApaListLog(0x00001142u, htcleoFirstIconError,\n"
            "\t\t\thtcleoIconsAttempted);\n"
            "\t\tInitiateStoringOfAppList();\n"
            "\t\tHtcleoApaListLog(0x00001143u, KErrNone, (TUint32)Count());\n"
            "\t\treturn;\n"
            "\t\t}\n"
            " \n"
            " \t// DEF072701\n"
        )
        count = text.count(anchor)
        if count != 1:
            raise SystemExit(
                f"first-scan insertion anchor: expected one, found {count}"
            )
        text = text.replace(anchor, replacement, 1)
        source.write_text(text, encoding="utf-8")

    text = source.read_text(encoding="utf-8")
    checks = {
        "single marker": text.count(MARKER) == 1,
        "single synchronous loop": text.count("while (htcleoMore);") == 1,
        "boot-only guard": text.count("if (!IsFirstScanComplete())") >= 1,
        "timer remains for rescans": (
            "iAppIdler->Start(KIdleStartDelay, htcleoIdleDelay," in text
        ),
        "completion handoff": text.count("InitiateStoringOfAppList();") >= 2,
        "stage 1140": text.count("0x00001140u") == 1,
        "stage 1141": text.count("0x00001141u") == 1,
        "stage 1142": text.count("0x00001142u") == 1,
        "stage 1143": text.count("0x00001143u") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AppArc synchronous first-scan verification failed: "
            + ", ".join(failed)
        )

    print(
        "HTCLEO_APPARC_FIRST_SCAN_SYNCHRONOUS=installed "
        "stages=1140-1143 later-rescans=stock"
    )


if __name__ == "__main__":
    main()
