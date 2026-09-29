#!/usr/bin/env python3
"""Keep AknCap's process handle alive until its readiness rendezvous completes.

Iteration 487 proves that AknCap explicitly calls RProcess::Rendezvous(KErrNone)
after construction, while the request created inside RApaLsSession::StartApp
remains pending.  The stock AppArc helper closes its only RProcess handle
immediately after Resume.  Reproduce that small native-launch sequence locally
for AknCap so the registering handle remains open through WaitForRequest.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNCAP_CLIENT_HELD_PROCESS_RENDEZVOUS_V4"

OLD = r'''    TRequestStatus requestStatusForRendezvous;
    const TInt htcleoStartAppResult = apa.StartApp(*cmdLine, dummy, &requestStatusForRendezvous);
    HtcleoApaLaunchLog(0x0000A004u, htcleoStartAppResult, 0u);
    User::LeaveIfError(htcleoStartAppResult);

    // HTCLEO_AKNCAP_THREAD_EXIT_CATEGORY_LOG_V3
    RThread htcleoAknThread;
    const TInt htcleoAknThreadOpenResult = htcleoAknThread.Open(dummy);
    HtcleoApaLaunchLog(0x0000A200u, htcleoAknThreadOpenResult,
        (TUint32)dummy.Id());
    User::WaitForRequest(requestStatusForRendezvous);
    const TInt htcleoAknRendezvousResult = requestStatusForRendezvous.Int();
    HtcleoApaLaunchLog(0x0000A005u, htcleoAknRendezvousResult, (TUint32)dummy.Id());
    if(htcleoAknThreadOpenResult == KErrNone)
        {
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
        }
    htcleoAknThread.Close();
    User::LeaveIfError(htcleoAknRendezvousResult);
'''

NEW = r'''    // HTCLEO_AKNCAP_CLIENT_HELD_PROCESS_RENDEZVOUS_V4
    // RApaLsSession::StartApp closes its local RProcess handle immediately
    // after Resume.  That is valid on the reference kernel, but iteration 487
    // proves that this port loses the resulting process-rendezvous completion.
    // This target is a known native executable, so reproduce AppArc's native
    // create/environment/main-thread/rendezvous sequence and retain the exact
    // registering handle until the child reports post-construction readiness.
    RProcess htcleoAknProcess;
    const TUidType htcleoAknUidType(KNullUid, KNullUid, KNullUid);
    const TInt htcleoAknCreateResult = htcleoAknProcess.CreateWithStackOverride(
        KAknCapServerExecutable, KNullDesC, htcleoAknUidType, 0,
        EOwnerProcess);
    HtcleoApaLaunchLog(0x0000A206u, htcleoAknCreateResult, 0u);
    User::LeaveIfError(htcleoAknCreateResult);

    TRAPD(htcleoAknEnvironmentResult,
        cmdLine->SetProcessEnvironmentL(htcleoAknProcess));
    HtcleoApaLaunchLog(0x0000A207u, htcleoAknEnvironmentResult,
        (TUint32)htcleoAknProcess.Id().Id());
    if(htcleoAknEnvironmentResult != KErrNone)
        {
        htcleoAknProcess.Kill(htcleoAknEnvironmentResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknEnvironmentResult);
        }

    TFullName htcleoAknThreadName(htcleoAknProcess.Name());
    _LIT(KHtcleoAknMainThreadSuffix, "::Main");
    htcleoAknThreadName.Append(KHtcleoAknMainThreadSuffix);

    // HTCLEO_AKNCAP_THREAD_EXIT_CATEGORY_LOG_V3
    RThread htcleoAknThread;
    const TInt htcleoAknThreadOpenResult =
        htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread);
    if(htcleoAknThreadOpenResult == KErrNone)
        {
        dummy = htcleoAknThread.Id();
        }
    HtcleoApaLaunchLog(0x0000A200u, htcleoAknThreadOpenResult,
        (TUint32)dummy.Id());
    if(htcleoAknThreadOpenResult != KErrNone)
        {
        htcleoAknProcess.Kill(htcleoAknThreadOpenResult);
        htcleoAknProcess.Close();
        User::Leave(htcleoAknThreadOpenResult);
        }

    TRequestStatus requestStatusForRendezvous;
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


def verify(source: str) -> None:
    property_ready = (
        "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_HANDSHAKE_V1" in source
    )
    property_poll = "HTCLEO_AKNCAP_CLIENT_PROPERTY_READY_POLL_V2" in source
    property_fire = "HTCLEO_AKNCAP_CLIENT_FIRE_AND_FORGET_V3" in source
    checks = {
        "single marker": source.count(MARKER) == 1,
        "stock StartApp removed from AknCap path": (
            "apa.StartApp(*cmdLine, dummy, &requestStatusForRendezvous)"
            not in source
        ),
        "single held process create": source.count(
            "htcleoAknProcess.CreateWithStackOverride("
        )
        == 1,
        "process environment preserved": source.count(
            "cmdLine->SetProcessEnvironmentL(htcleoAknProcess)"
        )
        == 1,
        "main thread opened before resume": (
            source.index("htcleoAknThread.Open(htcleoAknThreadName, EOwnerThread)")
            < source.index("htcleoAknProcess.Resume();")
        ),
        "readiness registered before resume": (
            (
                not property_ready
                and source.index(
                    "htcleoAknProcess.Rendezvous(requestStatusForRendezvous)"
                ) < source.index("htcleoAknProcess.Resume();")
            )
            or (
                property_ready and not property_poll
                and "htcleoAknProcess.Rendezvous(" not in source
                and source.index("htcleoAknReadyProperty.Subscribe(")
                < source.index("htcleoAknProcess.Resume();")
            )
            or (
                property_poll
                and "htcleoAknProcess.Rendezvous(" not in source
                and source.index(
                    "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
                ) < source.index("htcleoAknProcess.Resume();")
            )
        ),
        "handle retained through wait": (
            (
                source.index("User::WaitForRequest(requestStatusForRendezvous);")
                if not property_ready
                else (
                    source.index("HtcleoApaLaunchLog(0x0000A210u")
                    if property_fire
                    else source.index("for(; htcleoAknPollCount")
                    if property_poll
                    else source.index(
                        "User::WaitForRequest(htcleoAknReadyStatus, "
                        "htcleoAknDeathStatus)"
                    )
                )
            )
            < source.rindex("htcleoAknProcess.Close();")
        ),
        "single readiness winner wait": (
            source.count("User::WaitForRequest(requestStatusForRendezvous);")
            == 1
            if not property_ready
            else (
                (
                    "WaitForRequest(htcleoAknReadyStatus" not in source
                    and source.count(
                        "htcleoAknReadyProperty.Get(htcleoAknReadyValue)"
                    ) == 2
                )
                if property_poll
                else source.count(
                    "User::WaitForRequest(htcleoAknReadyStatus, "
                    "htcleoAknDeathStatus)"
                ) == 1
            )
        ),
        "bounded timing only": (
            source.count("User::After(500000)") == 1
            and source.count("User::After(10000)") == (
                0 if property_fire else 1 if property_poll else 0
            )
        ),
        "historical result stages retained": all(
            source.count(f"HtcleoApaLaunchLog(0x{stage:08X}u") == 1
            for stage in (0xA004, 0xA005, 0xA006, 0xA200, 0xA201,
                          0xA202, 0xA203, 0xA204, 0xA205)
        ),
        "held-process create stages retained": all(
            source.count(f"HtcleoApaLaunchLog(0x{stage:08X}u") == 1
            for stage in (
                (0xA206, 0xA207)
                if property_ready
                else range(0xA206, 0xA20B)
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
            "AknCap held-process rendezvous verification failed: "
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
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                f"AknCap held-process anchor: expected one, found {count}"
            )
        source = source.replace(OLD, NEW, 1)

    verify(source)
    source_path.write_text(source, encoding="utf-8")
    print(
        "HTCLEO_AKNCAP_CLIENT_HELD_PROCESS_RENDEZVOUS=installed "
        "stages=A206-A20A"
    )


if __name__ == "__main__":
    main()
