#!/usr/bin/env python3
"""Coalesce each initial MCS notification already covered by the first snapshot."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_HNMETADATA_INITIAL_NOTIFICATION_COALESCE_V1"

OLD_SIGNATURE = '''TInt CHnMdNotifyRequest::HandleNotifyL( TInt /* aCmdId */, TInt aEventId ,
        CLiwGenericParamList& /* aEventParamList */,
        const CLiwGenericParamList& /* aInParamList */)
    {
    TInt err( KErrNone );'''

NEW_SIGNATURE = '''TInt CHnMdNotifyRequest::HandleNotifyL( TInt /* aCmdId */, TInt aEventId ,
        CLiwGenericParamList& /* aEventParamList */,
        const CLiwGenericParamList& /* aInParamList */)
    {
    TInt err( KErrNone );

    // HTCLEO_HNMETADATA_INITIAL_NOTIFICATION_COALESCE_V1
    // RequestNotifyL subscribes only after the initial real GetList snapshot
    // has resumed behind the MenuContent commit gate. The first callback for
    // this subscription describes that already-consumed initial state. Do not
    // synchronously construct another HN/LIW GetList service on the UI thread.
    // Clear the per-subscription flag so every later real change reevaluates.
    if (RProcess().SecureId().iId == 0x101F4CD2u &&
            aEventId == KLiwEventInProgress &&
            iHtcleoInitialRefreshIssued)
        {
        iHtcleoInitialRefreshIssued = EFalse;
        // No file-backed evidence before this UI-thread callback returns.
        return err;
        }'''


def patch(text: str) -> str:
    if MARKER in text:
        text = text.replace(
            "        CLiwGenericParamList& aEventParamList,\n",
            "        CLiwGenericParamList& /* aEventParamList */,\n",
            1,
        )
        text = text.replace(
            "        HtcleoMdNotifyLog(0x4D440515u, KErrNone,\n"
            "            (TUint32)aEventParamList.Count());\n",
            "        // No file-backed evidence before this UI-thread callback returns.\n",
            1,
        )
        return text
    if text.count(OLD_SIGNATURE) != 1:
        raise SystemExit("HN initial-notification coalesce anchor missing/duplicated")
    return text.replace(OLD_SIGNATURE, NEW_SIGNATURE, 1)


def verify(text: str) -> None:
    if text.count(MARKER) != 1:
        raise SystemExit("HN notification coalesce marker missing")
    if "0x4D440515u" in text:
        raise SystemExit("file-backed coalesce stage must be retired")
    start = text.index("TInt CHnMdNotifyRequest::HandleNotifyL(")
    end = text.index("\n    }\n", start) + len("\n    }\n")
    section = text[start:end]
    if "HtcleoMdNotifyLog(" in section:
        raise SystemExit("coalesce return path must contain no file logger")
    required = (
        "aEventId == KLiwEventInProgress",
        "iHtcleoInitialRefreshIssued)",
        "iHtcleoInitialRefreshIssued = EFalse;",
        "iCmnPtrs->iModelEventObserver->HandleModelEventL( KReevaluateMdEvent",
    )
    if any(token not in section for token in required):
        raise SystemExit("initial coalesce or later reevaluation path changed")
    if not (section.index("iHtcleoInitialRefreshIssued = EFalse;") <
            section.index("return err;") <
            section.index("if ( aEventId == KLiwEventInProgress )") <
            section.index("HandleModelEventL( KReevaluateMdEvent")):
        raise SystemExit("first-only coalesce must precede retained later callback")
    if text.count("iHtcleoInitialRefreshIssued = ETrue;") != 1:
        raise SystemExit("subscription must still arm exactly one first-callback coalesce")
    if text.count("iHtcleoInitialRefreshIssued = EFalse;") < 2:
        raise SystemExit("coalesce/reset paths must both clear subscription state")
    if any(token in NEW_SIGNATURE for token in
           ("HtcleoMdNotifyLog(", "User::After", "RTimer", "CPeriodic",
            "SetOrdinal", "DrawNow", "StartApp")):
        raise SystemExit("notification coalesce must not affect timing/navigation/UI")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/hierarchynavigator/hnmetadatamodel/src/hnmdnotifyrequest.cpp"
    text = patch(path.read_text(encoding="latin-1"))
    verify(text)
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_HNMETADATA_INITIAL_NOTIFICATION=first-per-subscription-coalesced-no-filelog-later-real-changes-retained")


if __name__ == "__main__":
    main()
