#!/usr/bin/env python3
"""Retire the obsolete MatrixMenu post-subscribe HN refresh callback.

The HTCLEO ready-property path now blocks SendAllRequestsL only until the real
MenuContent commit is visible, after which the stock first metadata query runs.
The older CAsyncCallBack therefore performs a duplicate full query after the UI
is already live.  Keep notification subscription and the first real query, but
do not allocate or queue the superseded callback.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNMETADATA_REDUNDANT_ASYNC_REFRESH_RETIRED_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(requests: str, request: str) -> tuple[str, str]:
    if MARKER in request:
        return requests, request

    if "HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1" not in requests:
        raise SystemExit("ready-property prerequisite is missing")
    if "User::WaitForRequest(htcleoReadyStatus);" not in requests:
        raise SystemExit("ready-property completion wait is missing")

    request = replace_once(
        request,
        "// HTCLEO_HNMETADATA_NOTIFY_USER_INPUT_REFRESH_V1\n",
        "// HTCLEO_HNMETADATA_NOTIFY_USER_INPUT_REFRESH_V1\n"
        f"// {MARKER}\n",
        "retirement marker",
    )

    request = replace_once(
        request,
        """    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        iHtcleoInitialRefresh = new (ELeave) CAsyncCallBack(
            TCallBack(HtcleoInitialRefresh, this), CActive::EPriorityUserInput);
        HtcleoMdNotifyLog(0x4D44050Cu, KErrNone, 1u);
        }
""",
        """    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        // The ready-property gate now lets the stock first query run only
        // after MenuContent has committed.  Do not allocate the obsolete
        // thread-handle-backed duplicate-refresh callback.
        HtcleoMdNotifyLog(0x4D440513u, KErrNone, 0x4E4F4342u);
        }
""",
        "callback allocation",
    )

    request = replace_once(
        request,
        """        if (iHtcleoInitialRefresh && !iHtcleoInitialRefreshIssued)
            {
            iHtcleoInitialRefreshIssued = ETrue;
            iHtcleoInitialRefresh->CallBack();
            HtcleoMdNotifyLog(0x4D440508u, KErrNone, 1u);
            }
""",
        """        // Subscription succeeded.  The original first query resumes
        // after SendAllRequestsL's ready-property gate, so a second query must
        // not be queued here.
        iHtcleoInitialRefreshIssued = ETrue;
        HtcleoMdNotifyLog(0x4D440514u, KErrNone, 0x4E4F4342u);
""",
        "callback queue",
    )

    requests = requests.replace(
        "RequestNotifyL schedules a subscribe-then-requery on\n"
        "                // success so an AppArc event cannot be lost in this window.",
        "RequestNotifyL preserves the real subscription; the\n"
        "                // ready-property gate then releases the stock first query.",
    )
    return requests, request


def verify(requests: str, request: str) -> None:
    checks = {
        "marker": request.count(MARKER) == 1,
        "ready-property prerequisite": (
            requests.count("HTCLEO_MCS_HN_READY_PROPERTY_SUBSCRIBE_V1") == 2
            and requests.count("User::WaitForRequest(htcleoReadyStatus);") == 1
        ),
        "no callback allocation": "new (ELeave) CAsyncCallBack" not in request,
        "no callback queue": "iHtcleoInitialRefresh->CallBack();" not in request,
        "retired construction stage": request.count("0x4D440513u") == 1,
        "subscription continuation stage": request.count("0x4D440514u") == 1,
        "subscription result preserved": (
            request.count("User::LeaveIfError(htcleoNotifyResult);") == 1
        ),
        "first-query callback is unreachable only": (
            request.count("TInt CHnMdNotifyRequest::HtcleoInitialRefresh(") == 1
            and request.count("void CHnMdNotifyRequest::HtcleoInitialRefreshL()") == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("HN redundant refresh retirement failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    component = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel"
    )
    requests_path = component / "src/hnmdnotifyrequests.cpp"
    request_path = component / "src/hnmdnotifyrequest.cpp"

    requests = requests_path.read_text(encoding="utf-8")
    request = request_path.read_text(encoding="utf-8")
    requests, request = install(requests, request)
    verify(requests, request)
    requests_path.write_text(requests, encoding="utf-8")
    request_path.write_text(request, encoding="utf-8")
    print("HTCLEO_HNMETADATA_REDUNDANT_ASYNC_REFRESH_RETIRED_OK")


if __name__ == "__main__":
    main()
