#!/usr/bin/env python3
"""Keep the MCS server resident while retaining per-engine timed cleanup."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_SERVER_PERSISTENT_LIFETIME_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text

    text = replace_once(
        text,
        "void CMenuSrv::EngineDeleted()\n"
        "    {\n"
        "    if ( 1 >= iEngines->Count() )\n"
        "        {\n"
        "        // Last engine is being deleted now.\n"
        "        // Exit now, without delay: the engines had the timeout.\n"
        "        //\n"
        "        // Engine count is 1 when the engine has been created and added.\n"
        "        // Engine count is 0 in case of leave in GetEngineL().\n"
        "        iExitTimer->Cancel();\n"
        "        CActiveScheduler* currentScheduler = CActiveScheduler::Current();\n"
        "        // No more sessions; schedule self-deletion.\n"
        "        if (currentScheduler)\n"
        "            {\n"
        "            iExitTimer->After( TTimeIntervalMicroSeconds32( 0 ) );\n"
        "            }\n"
        "        }\n"
        "    }",
        "void CMenuSrv::EngineDeleted()\n"
        "    {\n"
        "    // HTCLEO_MCS_SERVER_PERSISTENT_LIFETIME_V1\n"
        "    // Engines still own their stock delayed cleanup.  Keep only the\n"
        "    // server process resident so a later UI client cannot race the\n"
        "    // final process exit and receive KErrServerTerminated.\n"
        "    if ( 1 >= iEngines->Count() )\n"
        "        {\n"
        "        iExitTimer->Cancel();\n"
        "        HtcleoMcsLog(0x4D430151u, KErrNone,\n"
        "            (TUint32)iEngines->Count());\n"
        "        }\n"
        "    }",
        "last-engine shutdown",
    )
    return replace_once(
        text,
        "    iExitTimer->Cancel();\n"
        "    iExitTimer->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );\n"
        "    iObjectConIx = CObjectConIx::NewL();",
        "    iExitTimer->Cancel();\n"
        "    // Do not arm the process-level startup exit timer on HTCLEO.\n"
        "    // Per-engine KMenuSrvExitDelay timers remain unchanged.\n"
        "    HtcleoMcsLog(0x4D430152u, KErrNone, 0u);\n"
        "    iObjectConIx = CObjectConIx::NewL();",
        "startup shutdown timer",
    )


def verify(text: str, engine: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "persistent stages": (
            text.count("0x4D430151u") == 1
            and text.count("0x4D430152u") == 1
        ),
        "process exit timers retired": (
            "iExitTimer->After( TTimeIntervalMicroSeconds32( 0 ) );" not in text
            and "iExitTimer->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );" not in text
        ),
        "engine timeout retained": (
            engine.count(
                "iTimedClose->After( TTimeIntervalMicroSeconds32( KMenuSrvExitDelay ) );"
            ) == 1
        ),
        "server machinery retained": (
            text.count("iExitTimer = CTimeout::NewL") == 1
            and text.count("CActiveScheduler::Stop()") == 1
            and text.count("iExitTimer->Cancel()") >= 3
        ),
        "no delay or fabricated result": (
            "User::After" not in text
            and "KErrServerTerminated = KErrNone" not in text
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MCS persistent-server verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/menusrv.cpp"
    )
    engine_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/srvsrc/menusrveng.cpp"
    )
    text = install(path.read_text(encoding="utf-8"))
    verify(text, engine_path.read_text(encoding="utf-8"))
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_MCS_SERVER_LIFETIME="
        "process-persistent-engine-expiry-retained-151-152"
    )


if __name__ == "__main__":
    main()
