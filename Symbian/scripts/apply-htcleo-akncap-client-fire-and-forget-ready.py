#!/usr/bin/env python3
"""Return from the AknCap launcher without an unreliable readiness wait.

Hardware iteration 490 proves that the child publishes the retained property,
while the parent stops after Resume in the first timer-backed polling yield.
Keep the child and property diagnostics, but follow the stock AppArc lifetime
model: resume the native server, close only the caller's handles, and return.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3"
START_ANCHOR = r'''    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1
    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2
'''
END_ANCHOR = r'''    User::LeaveIfError(htcleoAknReadyResult);
'''

NEW_WAIT = r'''    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1
    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2
    // HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3
    // Iteration 490 proves that the child reaches Set(1), but the parent stops
    // after Resume in the first timer-backed polling yield.  Preserve the
    // property as post-construction evidence, but do not make launcher return
    // depend on an async request, timer or polling loop.  Closing these caller
    // handles does not terminate the resumed process, matching stock AppArc.
    TInt htcleoAknReadyResult = RProperty::Define(
        KHtcleoAknReadyCategory, KHtcleoAknReadyKey, RProperty::EInt,
        KHtcleoAknReadyReadPolicy, KHtcleoAknReadyWritePolicy);
    if(htcleoAknReadyResult == KErrAlreadyExists)
        {
        htcleoAknReadyResult = KErrNone;
        }
    HtcleoApaLaunchLog(0x0000A20Bu, htcleoAknReadyResult,
        KHtcleoAknReadyKey);
    if(htcleoAknReadyResult != KErrNone)
        {
        htcleoAknThread.Close();
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknReadyResult);
        }

    htcleoAknReadyResult = RProperty::Set(
        KHtcleoAknReadyCategory, KHtcleoAknReadyKey, 0);
    HtcleoApaLaunchLog(0x0000A20Cu, htcleoAknReadyResult, 0u);
    if(htcleoAknReadyResult != KErrNone)
        {
        htcleoAknThread.Close();
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknReadyResult);
        }

    RProperty htcleoAknReadyProperty;
    htcleoAknReadyResult = htcleoAknReadyProperty.Attach(
        KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
    HtcleoApaLaunchLog(0x0000A20Du, htcleoAknReadyResult, 0u);
    if(htcleoAknReadyResult != KErrNone)
        {
        htcleoAknThread.Close();
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknReadyResult);
        }

    TInt htcleoAknReadyValue = 0;
    htcleoAknReadyResult = htcleoAknReadyProperty.Get(htcleoAknReadyValue);
    HtcleoApaLaunchLog(0x0000A20Eu, htcleoAknReadyResult,
        (TUint32)htcleoAknReadyValue);
    if(htcleoAknReadyResult != KErrNone)
        {
        htcleoAknReadyProperty.Close();
        htcleoAknThread.Close();
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknReadyResult);
        }

    HtcleoApaLaunchLog(0x0000A20Fu, KErrNone, 1u);
    htcleoAknProcess.Resume();
    HtcleoApaLaunchLog(0x0000A004u, KErrNone, 1u);

    // A210 now means that the launcher deliberately crossed the no-wait
    // boundary.  A211 is one opportunistic, non-gating post-Resume read.
    HtcleoApaLaunchLog(0x0000A210u, KErrNone, 0u);
    const TInt htcleoAknPostResumeRead =
        htcleoAknReadyProperty.Get(htcleoAknReadyValue);
    HtcleoApaLaunchLog(0x0000A211u, htcleoAknPostResumeRead,
        (TUint32)htcleoAknReadyValue);

    htcleoAknReadyProperty.Close();
    HtcleoApaLaunchLog(0x0000A212u, KErrNone,
        (TUint32)htcleoAknProcess.ExitType());
    HtcleoApaLaunchLog(0x0000A005u, KErrNone, (TUint32)dummy.Id());
    const TExitCategoryName htcleoAknExitCategory =
        htcleoAknThread.ExitCategory();
    HtcleoApaLaunchLog(0x0000A201u, htcleoAknThread.ExitReason(),
        (TUint32)htcleoAknExitCategory.Length());
    HtcleoApaLaunchLog(0x0000A202u, (TInt)htcleoAknThread.ExitType(),
        HtcleoPackApaExitCategory(htcleoAknExitCategory, 0));
    HtcleoApaLaunchLog(0x0000A203u, KErrNone,
        HtcleoPackApaExitCategory(htcleoAknExitCategory, 4));
    HtcleoApaLaunchLog(0x0000A204u, KErrNone,
        HtcleoPackApaExitCategory(htcleoAknExitCategory, 8));
    HtcleoApaLaunchLog(0x0000A205u, KErrNone,
        HtcleoPackApaExitCategory(htcleoAknExitCategory, 12));
    htcleoAknThread.Close();
    htcleoAknProcess.Close();
'''


def verify(source: str) -> None:
    first_get = source.find(
        "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
    )
    second_get = source.rfind(
        "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
    )
    resume = source.find("htcleoAknProcess.Resume();")
    checks = {
        "single fire-and-forget marker": source.count(MARKER) == 1,
        "property predecessors retained": (
            source.count("HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1") == 2
            and source.count("HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2") == 1
        ),
        "no async readiness requests": (
            "htcleoAknReadyProperty.Subscribe(" not in source
            and "htcleoAknProcess.Logon(" not in source
            and "htcleoAknProcess.LogonCancel(" not in source
            and "WaitForRequest(htcleoAknReadyStatus" not in source
        ),
        "no timer or poll loop": (
            "User::After(10000);" not in source
            and "KHtcleoAknReadyPollLimit" not in source
            and "for(; htcleoAknPollCount" not in source
        ),
        "persistent property signal": (
            source.count("RProperty::Define(") == 1
            and source.count("RProperty::Set(") == 1
            and source.count("htcleoAknReadyProperty.Attach(") == 1
            and "RProperty::Delete(" not in source
        ),
        "two nonblocking reads bracket resume": (
            source.count(
                "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
            ) == 2
            and 0 <= first_get < resume < second_get
        ),
        "no readiness result gate after resume": (
            "htcleoAknReadyValue != 1" not in source
            and "LeaveIfError(htcleoAknReadyResult)" not in source
        ),
        "resume and close model": (
            source.count("htcleoAknProcess.Resume();") == 1
            and resume < source.rfind("htcleoAknThread.Close();")
            and resume < source.rfind("htcleoAknProcess.Close();")
        ),
        "stages retained": all(
            source.count(f"HtcleoApaLaunchLog(0x{stage:08X}u") == 1
            for stage in range(0xA20B, 0xA213)
        ),
        "historic success stages retained": all(
            source.count(f"HtcleoApaLaunchLog(0x{stage:08X}u") == 1
            for stage in (0xA004, 0xA005, 0xA006)
        ),
        "no display probe": (
            "EHalGroupPlatformSpecific1, 2" not in source
            and "c6400000" not in source.lower()
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknCap fire-and-forget verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/clientsrc/"
          "AknCapServerClient.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing AknCap client input: {source_path}")

    source = source_path.read_text(encoding="utf-8")
    if MARKER not in source:
        if source.count(START_ANCHOR) != 1:
            raise SystemExit("AknCap fire-and-forget start anchor is not unique")
        start = source.index(START_ANCHOR)
        end = source.find(END_ANCHOR, start)
        if end < 0:
            raise SystemExit("AknCap fire-and-forget end anchor is missing")
        end += len(END_ANCHOR)
        source = source[:start] + NEW_WAIT + source[end:]

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET=installed "
        "stages=A20B-A212 wait=none timer=none property=retained"
    )


if __name__ == "__main__":
    main()
