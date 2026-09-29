#!/usr/bin/env python3
"""Replace the lost async AknCap readiness wait with bounded polling.

Iteration 489 proves that the child successfully publishes property value 1,
but neither the subscribed property request nor the process Logon request wakes
the parent two-status wait.  Keep the proven property and child signal, remove
only the unreliable async requests, and synchronously poll the value while a
short User::After yields the CPU to the suspended-then-resumed child.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2"
START_ANCHOR = r'''    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1
    // The child is still suspended, so reset and subscribe before Resume; a
'''
END_ANCHOR = r'''    User::LeaveIfError(htcleoAknReadyResult);
'''

NEW_WAIT = r'''    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1
    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2
    // The child is still suspended, so reset the readiness value before
    // Resume.  Hardware iteration 489 proves Set(1) succeeds in the child but
    // the parent-side Subscribe/Logon two-request wait never wakes.  Poll the
    // same property synchronously and use a bounded 10 ms yield between reads.
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
        (void)RProperty::Delete(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
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
        (void)RProperty::Delete(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
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
        (void)RProperty::Delete(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
        htcleoAknThread.Close();
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknReadyResult);
        }

    const TInt KHtcleoAknReadyPollLimit = 1000;
    HtcleoApaLaunchLog(0x0000A20Fu, KErrNone,
        (TUint32)KHtcleoAknReadyPollLimit);
    htcleoAknProcess.Resume();
    HtcleoApaLaunchLog(0x0000A004u, KErrNone, 1u);

    TInt htcleoAknPollCount = 0;
    for(; htcleoAknPollCount < KHtcleoAknReadyPollLimit;
        ++htcleoAknPollCount)
        {
        htcleoAknReadyResult =
            htcleoAknReadyProperty.Get(htcleoAknReadyValue);
        if(htcleoAknReadyResult != KErrNone || htcleoAknReadyValue == 1)
            {
            break;
            }
        if(htcleoAknProcess.ExitType() != EExitPending)
            {
            htcleoAknReadyResult = KErrDied;
            break;
            }
        User::After(10000);
        }
    if(htcleoAknReadyResult == KErrNone && htcleoAknReadyValue != 1)
        {
        htcleoAknReadyResult = KErrTimedOut;
        }
    HtcleoApaLaunchLog(0x0000A210u, htcleoAknReadyResult,
        (TUint32)htcleoAknPollCount);
    HtcleoApaLaunchLog(0x0000A211u, htcleoAknReadyResult,
        (TUint32)htcleoAknReadyValue);

    htcleoAknReadyProperty.Close();
    const TInt htcleoAknReadyDelete = RProperty::Delete(
        KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
    HtcleoApaLaunchLog(0x0000A212u, htcleoAknReadyDelete,
        (TUint32)htcleoAknProcess.ExitType());
    HtcleoApaLaunchLog(0x0000A005u, htcleoAknReadyResult,
        (TUint32)dummy.Id());
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
    if(htcleoAknReadyResult != KErrNone &&
        htcleoAknProcess.ExitType() == EExitPending)
        {
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        }
    htcleoAknThread.Close();
    htcleoAknProcess.Close();
    User::LeaveIfError(htcleoAknReadyResult);
'''


def verify(source: str) -> None:
    property_fire = "HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3" in source
    checks = {
        "single poll marker": source.count(MARKER) == 1,
        "property handshake retained": source.count(
            "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1"
        ) == 2,
        "async subscribe removed": "htcleoAknReadyProperty.Subscribe(" not in source,
        "async logon removed": "htcleoAknProcess.Logon(" not in source,
        "async logon cancel removed": "htcleoAknProcess.LogonCancel(" not in source,
        "two-status wait removed": (
            "WaitForRequest(htcleoAknReadyStatus" not in source
        ),
        "bounded poll or fire-and-forget successor": (
            source.count("KHtcleoAknReadyPollLimit = 1000")
            == (0 if property_fire else 1)
        ),
        "ten millisecond yield retired by successor": (
            source.count("User::After(10000);")
            == (0 if property_fire else 1)
        ),
        "two property reads": source.count(
            "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
        ) == 2,
        "process death poll retired by successor": source.count(
            "htcleoAknProcess.ExitType() != EExitPending"
        ) == (0 if property_fire else 1),
        "value gate retired by successor": source.count(
            "htcleoAknReadyValue != 1"
        ) == (0 if property_fire else 1),
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
            "AknCap property polling verification failed: " + ", ".join(failed)
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
            raise SystemExit("AknCap property poll start anchor is not unique")
        start = source.index(START_ANCHOR)
        end = source.find(END_ANCHOR, start)
        if end < 0:
            raise SystemExit("AknCap property poll end anchor is missing")
        end += len(END_ANCHOR)
        source = source[:start] + NEW_WAIT + source[end:]

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL=installed "
        "stages=A20B-A212 limit=1000 yield_us=10000"
    )


if __name__ == "__main__":
    main()
