#!/usr/bin/env python3
"""Reconnect the MatrixMenu CDL client once after server loss.

Iteration 511 proves that MatrixMenu completes CAknSgcClient construction and
the local packed-layout path, then leaves from CAknEnv::LoadAknLayoutL with
KErrServerTerminated.  LoadAknLayoutL's first leaving dependency is the CDL
server-backed FindInstancesLC request.  Recreate the process-local CDL engine
and repeat the stock requirements/load sequence once, only for MatrixMenu and
only for KErrNotFound/KErrServerTerminated.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNENV_MATRIXMENU_CDL_RECONNECT_V1"

OLD = r'''    HtcleoAknEnvMenuLog(0x4D4DA014u, KErrNone, 0u);
    LoadAknLayoutL();
    HtcleoAknEnvMenuLog(0x4D4DA015u, KErrNone, 0u);
'''

NEW = r'''    HtcleoAknEnvMenuLog(0x4D4DA014u, KErrNone, 0u);
    // HTCLEO_AKNENV_MATRIXMENU_CDL_RECONNECT_V1
    const TBool htcleoMatrixMenuCdlRecovery =
        RProcess().SecureId().iId == 0x101f4cd2u;
    if (!htcleoMatrixMenuCdlRecovery)
        {
        LoadAknLayoutL();
        }
    else
        {
        TInt htcleoLayoutError = KErrNone;
        TRAP(htcleoLayoutError, LoadAknLayoutL());
        HtcleoAknEnvMenuLog(0x4D4DA01Bu, htcleoLayoutError, 0u);
        if (htcleoLayoutError == KErrNotFound ||
            htcleoLayoutError == KErrServerTerminated)
            {
            HtcleoAknEnvMenuLog(0x4D4DA01Cu, htcleoLayoutError,
                iCdlEngRef ? 1u : 0u);
            delete iCdlEngRef;
            iCdlEngRef = NULL;
            TInt htcleoCdlCreateError = KErrNone;
            TRAP(htcleoCdlCreateError,
                iCdlEngRef = CdlEngine::CreateCdlEngineL());
            HtcleoAknEnvMenuLog(0x4D4DA01Du, htcleoCdlCreateError,
                iCdlEngRef ? 1u : 0u);
            if (htcleoCdlCreateError == KErrNone)
                {
                TRAP(htcleoLayoutError,
                    SetLayoutRequirementsL();
                    LoadAknLayoutL());
                }
            else
                {
                htcleoLayoutError = htcleoCdlCreateError;
                }
            HtcleoAknEnvMenuLog(0x4D4DA01Eu,
                htcleoLayoutError, iCdlEngRef ? 1u : 0u);
            }
        User::LeaveIfError(htcleoLayoutError);
        }
    HtcleoAknEnvMenuLog(0x4D4DA015u, KErrNone, 0u);
'''


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "matrixmenu only": source.count(
            "RProcess().SecureId().iId == 0x101f4cd2u"
        ) >= 1,
        "narrow recovery": (
            source.count("htcleoLayoutError == KErrNotFound") == 1
            and source.count(
                "htcleoLayoutError == KErrServerTerminated"
            ) == 1
        ),
        "single engine recreation": source.count(
            "iCdlEngRef = CdlEngine::CreateCdlEngineL()"
        ) == 2,
        "single retry requirements": source.count(
            "SetLayoutRequirementsL();"
        ) == 2,
        "stages": all(
            source.count(f"0x4D4DA0{stage}u") == 1
            for stage in ("1B", "1C", "1D", "1E")
        ),
        "stock non-menu load": source.count("LoadAknLayoutL()") >= 2,
        "real error re-leaves": source.count(
            "User::LeaveIfError(htcleoLayoutError);"
        ) == 1,
        "no timer display or fake success": (
            "User::After" not in NEW
            and "RTimer" not in NEW
            and "HalFunction" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu CDL reconnect verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AvKon/src/aknenv.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing Avkon input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu CDL reconnect anchor: expected one, "
                f"found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNENV_MATRIXMENU_CDL_RECONNECT="
        "notfound-or-terminated recreate-engine-once"
    )


if __name__ == "__main__":
    main()
