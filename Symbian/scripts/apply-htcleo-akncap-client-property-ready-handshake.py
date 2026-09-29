#!/usr/bin/env python3
"""Replace the broken AknCap process rendezvous with a P&S readiness wait.

Iteration 488 proves that the exact RProcess handle can remain open while the
child calls RProcess::Rendezvous(KErrNone), yet the request never completes on
HTCLEO.  Keep the already-proven native create/environment sequence, but wait
on an integer RProperty subscribed before Resume.  A process Logon request is
the failure side of the wait so a dead child cannot leave CLE blocked forever.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1"

INCLUDE_ANCHOR = '#include <AknNotifierControllerUtilities.h>\n'
CONSTANTS = r'''#include <AknNotifierControllerUtilities.h>
#include <e32property.h>

// HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1
const TUid KHtcleoAknReadyCategory = {0x10207218};
const TUint KHtcleoAknReadyKey = 0x7f044302u;
_LIT_SECURITY_POLICY_PASS(KHtcleoAknReadyReadPolicy);
_LIT_SECURITY_POLICY_PASS(KHtcleoAknReadyWritePolicy);
'''

OLD_WAIT = r'''    TRequestStatus requestStatusForRendezvous;
    htcleoAknProcess.Rendezvous(requestStatusForRendezvous);
    const TBool htcleoAknRendezvousPending =
        (requestStatusForRendezvous == KRequestPending);
    HtcleoApaLaunchLog(0x0000A208u, requestStatusForRendezvous.Int(),
        (TUint32)htcleoAknProcess.Id().Id());
    if(htcleoAknRendezvousPending)
        {
        htcleoAknProcess.Resume();
        }
    else
        {
        htcleoAknProcess.Kill(requestStatusForRendezvous.Int());
        }
    HtcleoApaLaunchLog(0x0000A004u, KErrNone,
        (TUint32)htcleoAknRendezvousPending);
    HtcleoApaLaunchLog(0x0000A209u, requestStatusForRendezvous.Int(),
        (TUint32)htcleoAknThread.ExitType());

    User::WaitForRequest(requestStatusForRendezvous);
    const TInt htcleoAknRendezvousResult = requestStatusForRendezvous.Int();
    HtcleoApaLaunchLog(0x0000A20Au, htcleoAknRendezvousResult,
        (TUint32)htcleoAknProcess.ExitType());
    HtcleoApaLaunchLog(0x0000A005u, htcleoAknRendezvousResult,
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
    htcleoAknThread.Close();
    htcleoAknProcess.Close();
    User::LeaveIfError(htcleoAknRendezvousResult);
'''

NEW_WAIT = r'''    // HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1
    // The child is still suspended, so reset and subscribe before Resume; a
    // previous boot can never satisfy this request with a stale value.
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

    TRequestStatus htcleoAknReadyStatus;
    htcleoAknReadyProperty.Subscribe(htcleoAknReadyStatus);
    HtcleoApaLaunchLog(0x0000A20Eu, htcleoAknReadyStatus.Int(),
        (TUint32)htcleoAknProcess.Id().Id());

    TRequestStatus htcleoAknDeathStatus;
    htcleoAknProcess.Logon(htcleoAknDeathStatus);
    HtcleoApaLaunchLog(0x0000A20Fu, htcleoAknDeathStatus.Int(),
        (TUint32)htcleoAknProcess.Id().Id());
    if(htcleoAknDeathStatus != KRequestPending)
        {
        htcleoAknReadyProperty.Cancel();
        User::WaitForRequest(htcleoAknReadyStatus);
        User::WaitForRequest(htcleoAknDeathStatus);
        htcleoAknReadyResult = htcleoAknDeathStatus.Int();
        if(htcleoAknReadyResult == KErrNone)
            {
            htcleoAknReadyResult = KErrDied;
            }
        htcleoAknReadyProperty.Close();
        (void)RProperty::Delete(
            KHtcleoAknReadyCategory, KHtcleoAknReadyKey);
        htcleoAknThread.Close();
        htcleoAknProcess.Kill(htcleoAknReadyResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknReadyResult);
        }

    htcleoAknProcess.Resume();
    HtcleoApaLaunchLog(0x0000A004u, KErrNone, 1u);
    User::WaitForRequest(htcleoAknReadyStatus, htcleoAknDeathStatus);
    HtcleoApaLaunchLog(0x0000A210u, htcleoAknReadyStatus.Int(),
        (TUint32)htcleoAknDeathStatus.Int());

    TInt htcleoAknReadyValue = 0;
    if(htcleoAknReadyStatus == KRequestPending)
        {
        // Child death won the wait. Cancel and consume the P&S request before
        // any stack-owned TRequestStatus leaves scope.
        htcleoAknReadyProperty.Cancel();
        User::WaitForRequest(htcleoAknReadyStatus);
        htcleoAknReadyResult = htcleoAknDeathStatus.Int();
        if(htcleoAknReadyResult == KErrNone)
            {
            htcleoAknReadyResult = KErrDied;
            }
        }
    else
        {
        htcleoAknReadyResult = htcleoAknReadyStatus.Int();
        if(htcleoAknDeathStatus == KRequestPending)
            {
            htcleoAknProcess.LogonCancel(htcleoAknDeathStatus);
            User::WaitForRequest(htcleoAknDeathStatus);
            }
        else
            {
            User::WaitForRequest(htcleoAknDeathStatus);
            if(htcleoAknReadyResult == KErrNone)
                {
                htcleoAknReadyResult = KErrDied;
                }
            }
        if(htcleoAknReadyResult == KErrNone)
            {
            htcleoAknReadyResult = htcleoAknReadyProperty.Get(
                htcleoAknReadyValue);
            if(htcleoAknReadyResult == KErrNone &&
                htcleoAknReadyValue != 1)
                {
                htcleoAknReadyResult = KErrNotReady;
                }
            }
        }
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
    property_poll = "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2" in source
    property_fire = "HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3" in source
    checks = {
        "two scoped markers": source.count(MARKER) == 2,
        "property include": source.count("#include <e32property.h>") == 1,
        "single ready key": source.count(
            "KHtcleoAknReadyKey = 0x7f044302u"
        ) == 1,
        "old process rendezvous removed": (
            "htcleoAknProcess.Rendezvous(" not in source
        ),
        "single subscribe": source.count(
            "htcleoAknReadyProperty.Subscribe(htcleoAknReadyStatus)"
        ) == (0 if property_poll else 1),
        "subscribe before resume": (
            source.index("htcleoAknReadyProperty.Get(htcleoAknReadyValue)")
            < source.index("htcleoAknProcess.Resume();")
            if property_poll
            else source.index("htcleoAknReadyProperty.Subscribe(")
            < source.index("htcleoAknProcess.Resume();")
        ),
        "death guard": (
            source.count("htcleoAknProcess.Logon(htcleoAknDeathStatus)")
            == (0 if property_poll else 1)
            and source.count(
                "htcleoAknProcess.LogonCancel(htcleoAknDeathStatus)"
            ) == (0 if property_poll else 1)
        ),
        "two-status wait": source.count(
            "User::WaitForRequest(htcleoAknReadyStatus, htcleoAknDeathStatus)"
        ) == (0 if property_poll else 1),
        "value verified or deliberately non-gating": (
            "htcleoAknReadyValue != 1" in source
            if not property_fire
            else "htcleoAknReadyValue != 1" not in source
        ),
        "requests consumed": source.count(
            "User::WaitForRequest(htcleoAknReadyStatus);"
        ) == (0 if property_poll else 2),
        "new stages": all(
            source.count(f"HtcleoApaLaunchLog(0x{stage:08X}u") == 1
            for stage in range(0xA20B, 0xA213)
        ),
        "historic success stages retained": all(
            source.count(f"HtcleoApaLaunchLog(0x{stage:08X}u") == 1
            for stage in (0xA004, 0xA005, 0xA006)
        ),
        "diagnostic thread id initialized": source.count(
            "TThreadId dummy(0);"
        ) == 1,
        "bounded timing only": (
            source.count("User::After(500000)") == 1
            and source.count("User::After(10000)") == (
                0 if property_fire else 1 if property_poll else 0
            )
        ),
        "no display probe": (
            "EHalGroupPlatformSpecific1, 2" not in source
            and "c6400000" not in source.lower()
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "AknCap property readiness verification failed: "
            + ", ".join(failed)
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
        if source.count(INCLUDE_ANCHOR) != 1:
            raise SystemExit("AknCap property include anchor is not unique")
        if source.count(OLD_WAIT) != 1:
            raise SystemExit(
                "AknCap property wait anchor: expected one, found "
                + str(source.count(OLD_WAIT))
            )
        source = source.replace(INCLUDE_ANCHOR, CONSTANTS, 1)
        source = source.replace(OLD_WAIT, NEW_WAIT, 1)

    # The older durable-log transform declared this value uninitialized.  It
    # is normally assigned after a successful thread Open, but initialize its
    # failure-path log detail as part of this successor transform.
    source = source.replace("TThreadId dummy;\n", "TThreadId dummy(0);\n")

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE=installed "
        "stages=A20B-A212"
    )


if __name__ == "__main__":
    main()
