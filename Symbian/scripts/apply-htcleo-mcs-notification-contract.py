#!/usr/bin/env python3
"""Keep MCS transport failures distinct from positive content-change masks."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MCS_NOTIFICATION_CONTRACT_V1"
CALLBACK_MARKER = "HTCLEO_MCS_NOTIFICATION_CALLBACK_LIFETIME_V1"

LOGGER = r'''
#include <f32file.h>

static void HtcleoMcsNotificationLog(TInt aStatus, TInt aPhase)
    {
    if (RProcess().SecureId().iId != 0x101F4CD2u)
        return;
    RFs fs;
    if (fs.Connect() != KErrNone)
        return;
    _LIT(KPath, "C:\\Symbian3\\MCSLOG.TXT");
    RFile file;
    TInt position = 0;
    TInt result = file.Open(fs, KPath, EFileWrite | EFileShareAny);
    if (result == KErrNotFound)
        result = file.Create(fs, KPath, EFileWrite | EFileShareAny);
    if (result == KErrNone)
        result = file.Seek(ESeekEnd, position);
    if (result == KErrNone && position <= 1048576 - 128)
        {
        TBuf8<128> record;
        record.Append(_L8("HTCLEO_MCN "));
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aStatus, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aPhase, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::NTickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        file.Write(record);
        }
    file.Close();
    fs.Close();
    }

'''

RUNL = r'''void CMCSReqNotification::RunL()
    {
    // HTCLEO_MCS_NOTIFICATION_CONTRACT_V1
    // The server completes Notify only with a positive event mask. Zero is
    // our initial self-completion; a negative result is a terminal error.
    const TInt event = iStatus.Int();
    if (!iIsNotification && event == KErrNone)
        {
        iIsNotification = ETrue;
        iStatus = KRequestPending;
        iNotifier.Notify(iFolderId, iEvents, iStatus);
        SetActive();
        HtcleoMcsNotificationLog(event, 0); // initial arm only
        return;
        }

    MMCSCallback* callback = iCallback;
    if (event <= KErrNone)
        {
        const TInt error = event < KErrNone ? event : KErrCorrupt;
        // Detach before notifying: Stopped/Canceled can release this owner.
        iCallback = NULL;
        iIsNotification = EFalse;
        iNotifier.Close();
        HtcleoMcsNotificationLog(event, 2); // raw terminal completion
        if (callback)
            callback->NotifyResultL(error, NULL);
        return; // no member access after an external callback
        }

    TInt folderId = iFolderId; // callback must not borrow an AO member
    iStatus = KRequestPending;
    iNotifier.Notify(iFolderId, iEvents, iStatus);
    SetActive();
    HtcleoMcsNotificationLog(event, 1); // real mask, subscription rearmed
    if (callback)
        callback->NotifyResultL(event, &folderId);
    // Safe tail: the callback may delete this AO. Its destructor cancels the
    // already-armed request; never rearm or touch this after callback return.
    }
'''


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"MCS notification anchor missing/duplicated: {old[:80]!r}")
    return text.replace(old, new, 1)


def patch_request(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(text, '#include "mcsconstants.h"\n',
                        '#include "mcsconstants.h"\n' + LOGGER)
    start = text.index("void CMCSReqNotification::RunL()")
    end = text.index("\n    }", start) + len("\n    }")
    text = text[:start] + RUNL.rstrip() + text[end:]
    # A terminal result detached the callback, so subsequent owner teardown
    # must not send a second cancellation through a freed callback object.
    text = replace_once(text, "    if ( !IsActive() )\n",
                        "    if ( !IsActive() || !iCallback )\n")
    text = replace_once(text,
        "        TRAP_IGNORE( iCallback->NotifyResultL( KErrCancel, NULL ));",
        "        MMCSCallback* callback = iCallback;\n"
        "        iCallback = NULL;\n"
        "        Cancel();\n"
        "        TRAP_IGNORE( callback->NotifyResultL( KErrCancel, NULL ));")
    return text


def patch_callback(text: str) -> str:
    if CALLBACK_MARKER in text:
        return text
    start = text.index("void CMCSCallback::NotifyResultL(")
    end = text.index("\n\t}\n", start) + len("\n\t}\n")
    section = text[start:end]
    condition = "iCmd != ERequestNotification || \n\t        (iCmd == ERequestNotification  && aErrCode == KErrCancel)"
    section = replace_once(section,
        "\tCLiwGenericParamList* outParams= NULL;",
        "\t// " + CALLBACK_MARKER + "\n"
        "\t// Snapshot before external code can delete the service/callback.\n"
        "\tconst TBool releaseCallback = iCmd != ERequestNotification || aErrCode < KErrNone;\n"
        "\tCLiwGenericParamList* outParams= NULL;")
    section = replace_once(section, condition, "releaseCallback")
    section = replace_once(section,
        "iCmd != ERequestNotification || (iCmd == ERequestNotification\n\t\t\t&& aErrCode == KErrCancel)",
        "releaseCallback")
    text = text[:start] + section + text[end:]
    # Defense at the translation boundary as well as at the AO: even an old
    # caller passing a folder pointer with a negative status cannot clear it.
    case_start = text.index("\t\tcase ERequestNotification:")
    case_end = text.index("\t\tcase EAddORChange:", case_start)
    case = text[case_start:case_end]
    case = replace_once(case, "if (aResult)", "if (aResult && aErrCode > KErrNone)")
    case = replace_once(case, "if (event)", "if (event > KErrNone)")
    return text[:case_start] + case + text[case_end:]


def verify(request: str, callback: str) -> None:
    if request.count(MARKER) != 1 or callback.count(CALLBACK_MARKER) != 1:
        raise SystemExit("MCS notification contract markers missing")
    start = request.index("void CMCSReqNotification::RunL()")
    end = request.index("\n    }", start)
    body = request[start:end]
    terminal = body[body.index("if (event <= KErrNone)"):body.index("TInt folderId")]
    if "Notify(" in terminal or "SetActive()" in terminal:
        raise SystemExit("terminal notifier must not rearm")
    if "callback->NotifyResultL(error, NULL);" not in terminal:
        raise SystemExit("transport error must not carry a fake folder event")
    positive = body[body.index("TInt folderId"):]
    if not (positive.index("iNotifier.Notify(") < positive.index("SetActive();") <
            positive.index("callback->NotifyResultL(event, &folderId);")):
        raise SystemExit("positive notification must rearm before external callback")
    tail = positive.split("callback->NotifyResultL(event, &folderId);", 1)[1]
    if any(token in tail for token in ("iNotifier.", "iCallback", "SetActive", "iStatus")):
        raise SystemExit("member access after possibly destructive callback")
    if callback.count("if(releaseCallback)") != 1 or callback.count("if (releaseCallback)") != 1:
        raise SystemExit("callback cleanup must use the saved terminal decision")
    if "if (aResult && aErrCode > KErrNone)" not in callback:
        raise SystemExit("negative notification error can still become a change mask")
    if "1048576 - 128" not in request or "HTCLEO_MCN " not in request:
        raise SystemExit("bounded raw notification evidence missing")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/homescreensrv/homescreensrv_plat/sapi_menucontent"
    request_path = base / "mcsservice/src/mcsrequestnotification.cpp"
    callback_path = base / "src/mcscallback.cpp"
    request = patch_request(request_path.read_text(encoding="latin-1"))
    callback = patch_callback(callback_path.read_text(encoding="latin-1"))
    verify(request, callback)
    request_path.write_text(request, encoding="latin-1")
    callback_path.write_text(callback, encoding="latin-1")
    print("HTCLEO_MCS_NOTIFICATION_CONTRACT=positive-mask-terminal-negative-safe-callback-tail-MCN-1m")


if __name__ == "__main__":
    main()
