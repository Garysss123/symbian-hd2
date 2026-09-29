#!/usr/bin/env python3
"""Bound failed HomeScreen restart storms without hiding the real error."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HOMESCREEN_BOUNDED_RESTART_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "const TInt KSleepOnRetry = 250000; // 250ms\n",
        "// HTCLEO_HOMESCREEN_BOUNDED_RESTART_V1\n"
        "const TInt KSleepOnRetry = 1000000; // 1s compatibility backoff\n"
        "const TInt KHtcleoMaxStartupCrashes = 3;\n",
        "restart constants",
    )
    text = replace_once(
        text,
        """    {    
    TInt crashCount = 0;
    TInt error = RProperty::Get( KPSCategoryUid,
                                 KPSCrashCountKey,
                                 crashCount );""",
        """    {
    HtcleoHomeLog(0x484F0240u, aExitReason, (TUint32)aExitType);
    TInt crashCount = 0;
    TInt error = RProperty::Get( KPSCategoryUid,
                                 KPSCrashCountKey,
                                 crashCount );
    HtcleoHomeLog(0x484F0241u, error, (TUint32)crashCount);""",
        "process-ended entry",
    )
    text = replace_once(
        text,
        """            error = RProperty::Set( KPSCategoryUid,
                                    KPSCrashCountKey,
                                    crashCount );                          
            }
        
        if( error == KErrNone )
            {      
            User::After( KSleepOnRetry ); 
            Activate();
            }
        else
            {           
            ShutdownApp( error );
            }""",
        """            error = RProperty::Set( KPSCategoryUid,
                                    KPSCrashCountKey,
                                    crashCount );
            HtcleoHomeLog(0x484F0242u, error, (TUint32)crashCount);
            }
        
        if( error == KErrNone &&
            crashCount < KHtcleoMaxStartupCrashes )
            {
            User::After( KSleepOnRetry );
            HtcleoHomeLog(0x484F0243u, KErrNone, (TUint32)crashCount);
            Activate();
            }
        else if( error == KErrNone )
            {
            // Keep ailaunch and its shutdown observer alive, but stop the
            // child storm so MatrixMenu and WServ can continue booting.
            HtcleoHomeLog(0x484F0244u, KErrOverflow,
                (TUint32)crashCount);
            }
        else
            {
            HtcleoHomeLog(0x484F0245u, error, (TUint32)crashCount);
            ShutdownApp( error );
            }""",
        "bounded restart",
    )
    return text


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "one-second backoff": text.count("KSleepOnRetry = 1000000") == 1,
        "three-crash bound": (
            text.count("KHtcleoMaxStartupCrashes = 3") == 1
            and text.count("crashCount < KHtcleoMaxStartupCrashes") == 1
        ),
        "stages": all(
            text.count(f"0x484F{stage:04X}u") == 1
            for stage in range(0x0240, 0x0246)
        ),
        "real monitor retained": text.count("InitProcessMonitorL( process.Id() )") == 1,
        "real process retained": text.count("process.Create( KHsExeName, KNullDesC )") == 1,
        "no normalized child result": "aExitReason = KErrNone" not in text,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen bounded restart verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/mw/homescreensrv/idlefw/hslaunch/src/hslaunch.cpp"
    if not path.is_file():
        raise SystemExit(f"missing ailaunch source: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_HOMESCREEN_RESTART_POLICY="
        "max-three-crashes-one-second-backoff-preserve-error"
    )


if __name__ == "__main__":
    main()
