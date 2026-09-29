#!/usr/bin/env python3
"""Fail open optional HN item notification subscriptions for MatrixMenu.

Iteration 534 proves item 0 and item 1 complete, while item 2 leaves before its
query collector is created.  In CHnMdItem::EvaluateItemItselfL the only call in
that interval is SendAllRequestsL().  Notification subscriptions keep menu data
fresh after startup but are not the initial data query.  On MatrixMenu only,
normalize KErrServerTerminated from a subscription to an explicit disabled
notification and continue to the mandatory initial query.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNMETADATA_NOTIFY_UI_FIRST_COMPAT_V1"
RECONNECT_REQUERY_MARKER = "HTCLEO_HNMETADATA_NOTIFY_RECONNECT_REQUERY_V1"
STANDARD_REFRESH_MARKER = "HTCLEO_HNMETADATA_NOTIFY_STANDARD_REFRESH_V1"
LIFETIME_TRACE_MARKER = "HTCLEO_HNMETADATA_NOTIFY_LIFETIME_TRACE_V1"
CALLBACK_ENTRY_MARKER = "HTCLEO_HNMETADATA_NOTIFY_CALLBACK_ENTRY_V1"
HIGH_REFRESH_MARKER = "HTCLEO_HNMETADATA_NOTIFY_HIGH_REFRESH_V1"
USER_INPUT_REFRESH_MARKER = "HTCLEO_HNMETADATA_NOTIFY_USER_INPUT_REFRESH_V1"
REDUNDANT_REFRESH_RETIRED_MARKER = (
    "HTCLEO_HNMETADATA_REDUNDANT_ASYNC_REFRESH_RETIRED_V1"
)


LOGGER = r'''
#include <f32file.h>

// HTCLEO_HNMETADATA_NOTIFY_UI_FIRST_COMPAT_V1
void HtcleoMdNotifyLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101F4CD2u)
        {
        return;
        }
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }
    _LIT(KHtcleoMdNotifyDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMdNotifyPath, "C:\\Symbian3\\MDLOG.TXT");
    r = fs.MkDirAll(KHtcleoMdNotifyDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }
    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMdNotifyPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMdNotifyPath, EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoMdNotifyPrefix, "HTCLEO_MD ");
        TBuf8<96> record;
        record.Append(KHtcleoMdNotifyPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        file.Write(record);
        }
    file.Close();
    fs.Close();
    }
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "#include <e32base.h>\n",
        "#include <e32base.h>\n" + LOGGER,
        "notification logger",
    )
    source = replace_once(
        source,
        """void CHnMdNotifyRequests::SendAllRequestsL( CLiwGenericParamList& aParams,
        TInt aCmdOptions )
    {
    for (int i=0; i<Count(); i++)
        {
        NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions );
        }
    iSent = ETrue;
    }
""",
        """void CHnMdNotifyRequests::SendAllRequestsL( CLiwGenericParamList& aParams,
        TInt aCmdOptions )
    {
    HtcleoMdNotifyLog(0x4D440500u, KErrNone, (TUint32)Count());
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        for (int i=0; i<Count(); i++)
            {
            HtcleoMdNotifyLog(0x4D440501u, KErrNone, (TUint32)i);
            TRAPD(htcleoNotifyError,
                NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions ));
            HtcleoMdNotifyLog(0x4D440502u, htcleoNotifyError,
                (TUint32)i);
            if (htcleoNotifyError == KErrServerTerminated)
                {
                HtcleoMdNotifyLog(0x4D440503u, KErrNotSupported,
                    0x4E4F5449u);
                continue;
                }
            User::LeaveIfError(htcleoNotifyError);
            HtcleoMdNotifyLog(0x4D440504u, KErrNone, (TUint32)i);
            }
        iSent = ETrue;
        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;
        }
    for (int i=0; i<Count(); i++)
        {
        NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions );
        }
    iSent = ETrue;
    }
""",
        "SendAllRequestsL",
    )
    return source


SEND_ALL_V1 = r'''void CHnMdNotifyRequests::SendAllRequestsL( CLiwGenericParamList& aParams,
        TInt aCmdOptions )
    {
    HtcleoMdNotifyLog(0x4D440500u, KErrNone, (TUint32)Count());
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        for (int i=0; i<Count(); i++)
            {
            HtcleoMdNotifyLog(0x4D440501u, KErrNone, (TUint32)i);
            TRAPD(htcleoNotifyError,
                NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions ));
            HtcleoMdNotifyLog(0x4D440502u, htcleoNotifyError,
                (TUint32)i);
            if (htcleoNotifyError == KErrServerTerminated)
                {
                HtcleoMdNotifyLog(0x4D440503u, KErrNotSupported,
                    0x4E4F5449u);
                continue;
                }
            User::LeaveIfError(htcleoNotifyError);
            HtcleoMdNotifyLog(0x4D440504u, KErrNone, (TUint32)i);
            }
        iSent = ETrue;
        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;
        }
    for (int i=0; i<Count(); i++)
        {
        NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions );
        }
    iSent = ETrue;
    }'''


SEND_ALL_V2 = r'''void CHnMdNotifyRequests::SendAllRequestsL( CLiwGenericParamList& aParams,
        TInt aCmdOptions )
    {
    HtcleoMdNotifyLog(0x4D440500u, KErrNone, (TUint32)Count());
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        for (int i=0; i<Count(); i++)
            {
            HtcleoMdNotifyLog(0x4D440501u, KErrNone, (TUint32)i);
            TRAPD(htcleoNotifyError,
                NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions ));
            HtcleoMdNotifyLog(0x4D440502u, htcleoNotifyError,
                (TUint32)i);
            if (htcleoNotifyError == KErrServerTerminated)
                {
                // The LIW provider may have inherited the first transient
                // MenuContent session.  Drop that dead handler and reconnect
                // once; RequestNotifyL schedules a subscribe-then-requery on
                // success so an AppArc event cannot be lost in this window.
                NotifyRequest(i).HtcleoResetServiceHandler();
                HtcleoMdNotifyLog(0x4D440506u, KErrNone, (TUint32)i);
                TRAP(htcleoNotifyError,
                    NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions ));
                HtcleoMdNotifyLog(0x4D440507u, htcleoNotifyError,
                    (TUint32)i);
                }
            if (htcleoNotifyError == KErrServerTerminated)
                {
                HtcleoMdNotifyLog(0x4D440503u, KErrNotSupported,
                    0x4E4F5449u);
                continue;
                }
            User::LeaveIfError(htcleoNotifyError);
            HtcleoMdNotifyLog(0x4D440504u, KErrNone, (TUint32)i);
            }
        iSent = ETrue;
        HtcleoMdNotifyLog(0x4D440505u, KErrNone, (TUint32)Count());
        return;
        }
    for (int i=0; i<Count(); i++)
        {
        NotifyRequest(i).RequestNotifyL( aParams, aCmdOptions );
        }
    iSent = ETrue;
    }'''


REQUEST_INCLUDE = '#include "hnmdnotifyrequest.h"\n'
REQUEST_INCLUDE_UPGRADED = r'''#include "hnmdnotifyrequest.h"

// HTCLEO_HNMETADATA_NOTIFY_RECONNECT_REQUERY_V1
// HTCLEO_HNMETADATA_NOTIFY_STANDARD_REFRESH_V1
void HtcleoMdNotifyLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
'''


REQUEST_DESTRUCTOR = r'''CHnMdNotifyRequest::~CHnMdNotifyRequest()
    {
    delete iItemId;
    delete iService;
    delete iSh;
    }'''


REQUEST_DESTRUCTOR_UPGRADED = r'''CHnMdNotifyRequest::~CHnMdNotifyRequest()
    {
    if (iHtcleoInitialRefresh)
        {
        iHtcleoInitialRefresh->Cancel();
        }
    delete iHtcleoInitialRefresh;
    iHtcleoInitialRefresh = NULL;
    delete iItemId;
    delete iService;
    delete iSh;
    }'''


REQUEST_DESTRUCTOR_TRACED = r'''CHnMdNotifyRequest::~CHnMdNotifyRequest()
    {
    HtcleoMdNotifyLog(0x4D44050Au,
        iHtcleoInitialRefreshIssued ? 1 : 0,
        ((iHtcleoInitialRefresh && iHtcleoInitialRefresh->IsActive()) ? 1u : 0u)
            | (iSh ? 2u : 0u));
    if (iHtcleoInitialRefresh)
        {
        iHtcleoInitialRefresh->Cancel();
        }
    delete iHtcleoInitialRefresh;
    iHtcleoInitialRefresh = NULL;
    delete iItemId;
    delete iService;
    delete iSh;
    }'''


REQUEST_CONSTRUCT_TAIL = r'''    iService = CHnMdService::NewL( aElement );
    iSh = NULL;
    }'''


REQUEST_CONSTRUCT_TAIL_UPGRADED = r'''    iService = CHnMdService::NewL( aElement );
    iSh = NULL;
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        iHtcleoInitialRefresh = new (ELeave) CAsyncCallBack(
            TCallBack(HtcleoInitialRefresh, this), CActive::EPriorityStandard);
        }
    }'''


REQUEST_CONSTRUCT_TAIL_TRACED = r'''    iService = CHnMdService::NewL( aElement );
    iSh = NULL;
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        iHtcleoInitialRefresh = new (ELeave) CAsyncCallBack(
            TCallBack(HtcleoInitialRefresh, this), CActive::EPriorityStandard);
        HtcleoMdNotifyLog(0x4D44050Cu, KErrNone, 1u);
        }
    }'''


REQUEST_CONSTRUCTOR = r'''CHnMdNotifyRequest::CHnMdNotifyRequest(THnMdCommonPointers* aCmnPtrs) 
    : iCmnPtrs(aCmnPtrs)
    {
    }'''


REQUEST_CONSTRUCTOR_UPGRADED = r'''CHnMdNotifyRequest::CHnMdNotifyRequest(THnMdCommonPointers* aCmnPtrs) 
    : iCmnPtrs(aCmnPtrs), iHtcleoInitialRefresh(NULL),
      iHtcleoInitialRefreshIssued(EFalse)
    {
    }'''


REQUEST_NOTIFY = r'''void CHnMdNotifyRequest::RequestNotifyL( CLiwGenericParamList& aParams, 
        TInt aCmdOptions )
    {
    if ( iSh == NULL )
        {
        CLiwGenericParamList* constructor =
            iService->EvaluateConstructorL( aParams );
        CleanupStack::PushL(constructor);
        CLiwGenericParamList* command = iService->EvaluateCommandL( aParams );
        CleanupStack::PushL( command );
    
        // Create service
        iSh = CHnServiceHandler::NewL( 
                iService->GetServiceName(), 
                iService->GetInterfaceName(), 
                iService->GetCommand().GetCommandName(),
                EServiceModeAsynchronous,
                constructor, 
                command );
    
        CleanupStack::Pop( command );
        CleanupStack::Pop( constructor );
        }
    iSh->ExecuteL( this, aCmdOptions ); 
    }'''


REQUEST_NOTIFY_UPGRADED = r'''void CHnMdNotifyRequest::RequestNotifyL( CLiwGenericParamList& aParams, 
        TInt aCmdOptions )
    {
    if ( iSh == NULL )
        {
        CLiwGenericParamList* constructor =
            iService->EvaluateConstructorL( aParams );
        CleanupStack::PushL(constructor);
        CLiwGenericParamList* command = iService->EvaluateCommandL( aParams );
        CleanupStack::PushL( command );
    
        // Create service
        iSh = CHnServiceHandler::NewL( 
                iService->GetServiceName(), 
                iService->GetInterfaceName(), 
                iService->GetCommand().GetCommandName(),
                EServiceModeAsynchronous,
                constructor, 
                command );
    
        CleanupStack::Pop( command );
        CleanupStack::Pop( constructor );
        }
    const TInt htcleoNotifyResult = iSh->ExecuteL( this, aCmdOptions );
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        User::LeaveIfError(htcleoNotifyResult);
        if (iHtcleoInitialRefresh && !iHtcleoInitialRefreshIssued)
            {
            iHtcleoInitialRefreshIssued = ETrue;
            iHtcleoInitialRefresh->CallBack();
            HtcleoMdNotifyLog(0x4D440508u, KErrNone, 1u);
            }
        }
    }'''


REQUEST_HELPERS = r'''
// ---------------------------------------------------------------------------
// HTC Leo notification reconnect and subscribe-then-requery helpers.
// ---------------------------------------------------------------------------
void CHnMdNotifyRequest::HtcleoResetServiceHandler()
    {
    delete iSh;
    iSh = NULL;
    iHtcleoInitialRefreshIssued = EFalse;
    }

void CHnMdNotifyRequest::HtcleoInitialRefreshL()
    {
    CLiwGenericParamList* params = CLiwGenericParamList::NewL();
    CleanupStack::PushL(params);
    HandleNotifyL(0, KLiwEventInProgress, *params, *params);
    CleanupStack::PopAndDestroy(params);
    }

TInt CHnMdNotifyRequest::HtcleoInitialRefresh(TAny* aSelf)
    {
    CHnMdNotifyRequest* self = static_cast<CHnMdNotifyRequest*>(aSelf);
    TRAPD(htcleoRefreshError, self->HtcleoInitialRefreshL());
    HtcleoMdNotifyLog(0x4D440509u, htcleoRefreshError, 0u);
    return KErrNone;
    }
'''


RESET_HANDLER = r'''void CHnMdNotifyRequest::HtcleoResetServiceHandler()
    {
    delete iSh;
    iSh = NULL;
    iHtcleoInitialRefreshIssued = EFalse;
    }'''


RESET_HANDLER_TRACED = r'''void CHnMdNotifyRequest::HtcleoResetServiceHandler()
    {
    HtcleoMdNotifyLog(0x4D44050Bu, KErrNone,
        iHtcleoInitialRefreshIssued ? 1u : 0u);
    delete iSh;
    iSh = NULL;
    iHtcleoInitialRefreshIssued = EFalse;
    }'''


CALLBACK_BODY = r'''TInt CHnMdNotifyRequest::HtcleoInitialRefresh(TAny* aSelf)
    {
    CHnMdNotifyRequest* self = static_cast<CHnMdNotifyRequest*>(aSelf);
    TRAPD(htcleoRefreshError, self->HtcleoInitialRefreshL());
    HtcleoMdNotifyLog(0x4D440509u, htcleoRefreshError, 0u);
    return KErrNone;
    }'''


CALLBACK_BODY_TRACED = r'''TInt CHnMdNotifyRequest::HtcleoInitialRefresh(TAny* aSelf)
    {
    CHnMdNotifyRequest* self = static_cast<CHnMdNotifyRequest*>(aSelf);
    HtcleoMdNotifyLog(0x4D44050Du, KErrNone,
        self && self->iHtcleoInitialRefreshIssued ? 1u : 0u);
    TRAPD(htcleoRefreshError, self->HtcleoInitialRefreshL());
    HtcleoMdNotifyLog(0x4D440509u, htcleoRefreshError, 0u);
    return KErrNone;
    }'''


HEADER_REQUEST_DECL = r'''     void RequestNotifyL( CLiwGenericParamList& aParams,
             TInt aCmdOptions = 0 );'''


HEADER_REQUEST_DECL_UPGRADED = r'''     void RequestNotifyL( CLiwGenericParamList& aParams,
             TInt aCmdOptions = 0 );

     // Rebuild a dead LIW provider once after KErrServerTerminated.
     void HtcleoResetServiceHandler();'''


HEADER_CONSTRUCTOR_DECL = r'''    CHnMdNotifyRequest(THnMdCommonPointers* aCmnPtrs);'''


HEADER_CONSTRUCTOR_DECL_UPGRADED = r'''    CHnMdNotifyRequest(THnMdCommonPointers* aCmnPtrs);

    static TInt HtcleoInitialRefresh(TAny* aSelf);
    void HtcleoInitialRefreshL();'''


HEADER_FIELDS = r'''    CHnServiceHandler* iSh; 
    
    };'''


HEADER_FIELDS_UPGRADED = r'''    CHnServiceHandler* iSh; 

    // One idle-priority subscribe-then-requery closes the initial AppArc race.
    CAsyncCallBack* iHtcleoInitialRefresh;
    TBool iHtcleoInitialRefreshIssued;
    
    };'''


def upgrade_reconnect_requery(
    requests: str, request: str, request_header: str
) -> tuple[str, str, str]:
    if RECONNECT_REQUERY_MARKER not in request:
        if "static void HtcleoMdNotifyLog(" in requests:
            requests = replace_once(
                requests,
                "static void HtcleoMdNotifyLog(",
                "void HtcleoMdNotifyLog(",
                "export notification logger",
            )
        requests = replace_once(
            requests, SEND_ALL_V1, SEND_ALL_V2, "retry dead notification provider"
        )
        request = replace_once(
            request, REQUEST_INCLUDE, REQUEST_INCLUDE_UPGRADED, "request marker"
        )
        request = replace_once(
            request,
            REQUEST_DESTRUCTOR,
            REQUEST_DESTRUCTOR_UPGRADED,
            "refresh callback cleanup",
        )
        request = replace_once(
            request,
            REQUEST_CONSTRUCT_TAIL,
            REQUEST_CONSTRUCT_TAIL_UPGRADED,
            "refresh callback construction",
        )
        request = replace_once(
            request,
            REQUEST_CONSTRUCTOR,
            REQUEST_CONSTRUCTOR_UPGRADED,
            "refresh callback initialization",
        )
        request = replace_once(
            request,
            REQUEST_NOTIFY,
            REQUEST_NOTIFY_UPGRADED,
            "subscribe-then-requery",
        )
        request = replace_once(
            request,
            "// ---------------------------------------------------------------------------\n// \n// ---------------------------------------------------------------------------\n//     \nTInt CHnMdNotifyRequest::HandleNotifyL",
            REQUEST_HELPERS
            + "\n// ---------------------------------------------------------------------------\n// \n// ---------------------------------------------------------------------------\n//     \nTInt CHnMdNotifyRequest::HandleNotifyL",
            "request helpers",
        )
        request_header = replace_once(
            request_header,
            HEADER_REQUEST_DECL,
            HEADER_REQUEST_DECL_UPGRADED,
            "reset declaration",
        )
        request_header = replace_once(
            request_header,
            HEADER_CONSTRUCTOR_DECL,
            HEADER_CONSTRUCTOR_DECL_UPGRADED,
            "refresh declarations",
        )
        request_header = replace_once(
            request_header,
            HEADER_FIELDS,
            HEADER_FIELDS_UPGRADED,
            "refresh state",
        )
    if STANDARD_REFRESH_MARKER not in request:
        request = replace_once(
            request,
            "// HTCLEO_HNMETADATA_NOTIFY_RECONNECT_REQUERY_V1\n",
            "// HTCLEO_HNMETADATA_NOTIFY_RECONNECT_REQUERY_V1\n"
            "// HTCLEO_HNMETADATA_NOTIFY_STANDARD_REFRESH_V1\n",
            "standard refresh marker",
        )
        request = replace_once(
            request,
            "CActive::EPriorityIdle",
            "CActive::EPriorityStandard",
            "standard refresh priority",
        )
    if LIFETIME_TRACE_MARKER not in request:
        request = replace_once(
            request,
            "// HTCLEO_HNMETADATA_NOTIFY_STANDARD_REFRESH_V1\n",
            "// HTCLEO_HNMETADATA_NOTIFY_STANDARD_REFRESH_V1\n"
            "// HTCLEO_HNMETADATA_NOTIFY_LIFETIME_TRACE_V1\n",
            "lifetime trace marker",
        )
        request = replace_once(
            request,
            REQUEST_DESTRUCTOR_UPGRADED,
            REQUEST_DESTRUCTOR_TRACED,
            "notify request destructor trace",
        )
        request = replace_once(
            request,
            REQUEST_CONSTRUCT_TAIL_UPGRADED,
            REQUEST_CONSTRUCT_TAIL_TRACED,
            "notify request construction trace",
        )
        request = replace_once(
            request,
            RESET_HANDLER,
            RESET_HANDLER_TRACED,
            "notify request reset trace",
        )
    if CALLBACK_ENTRY_MARKER not in request:
        request = replace_once(
            request,
            "// HTCLEO_HNMETADATA_NOTIFY_LIFETIME_TRACE_V1\n",
            "// HTCLEO_HNMETADATA_NOTIFY_LIFETIME_TRACE_V1\n"
            "// HTCLEO_HNMETADATA_NOTIFY_CALLBACK_ENTRY_V1\n",
            "callback entry marker",
        )
        request = replace_once(
            request,
            CALLBACK_BODY,
            CALLBACK_BODY_TRACED,
            "notify callback entry trace",
        )
    if HIGH_REFRESH_MARKER not in request:
        request = replace_once(
            request,
            "// HTCLEO_HNMETADATA_NOTIFY_CALLBACK_ENTRY_V1\n",
            "// HTCLEO_HNMETADATA_NOTIFY_CALLBACK_ENTRY_V1\n"
            "// HTCLEO_HNMETADATA_NOTIFY_HIGH_REFRESH_V1\n",
            "high refresh marker",
        )
        request = replace_once(
            request,
            "CActive::EPriorityStandard",
            "CActive::EPriorityHigh",
            "high refresh priority",
        )
    if USER_INPUT_REFRESH_MARKER not in request:
        request = replace_once(
            request,
            "// HTCLEO_HNMETADATA_NOTIFY_HIGH_REFRESH_V1\n",
            "// HTCLEO_HNMETADATA_NOTIFY_HIGH_REFRESH_V1\n"
            "// HTCLEO_HNMETADATA_NOTIFY_USER_INPUT_REFRESH_V1\n",
            "user-input refresh marker",
        )
        request = replace_once(
            request,
            "CActive::EPriorityHigh",
            "CActive::EPriorityUserInput",
            "user-input refresh priority",
        )
    return requests, request, request_header


def verify(source: str, request: str, request_header: str) -> None:
    combined = source + request
    refresh_retired = REDUNDANT_REFRESH_RETIRED_MARKER in request
    if refresh_retired:
        expected = [
            stage
            for stage in range(0x4D440500, 0x4D44050E)
            if stage not in (0x4D440508, 0x4D44050C)
        ] + [0x4D440513, 0x4D440514]
    else:
        expected = list(range(0x4D440500, 0x4D44050E))
    missing = [
        f"0x{stage:08X}u"
        for stage in expected
        if combined.count(f"0x{stage:08X}u") != 1
    ]
    checks = {
        "single marker": source.count(MARKER) == 1,
        "reconnect marker": request.count(RECONNECT_REQUERY_MARKER) == 1,
        "standard refresh marker": request.count(STANDARD_REFRESH_MARKER) == 1,
        "lifetime trace marker": request.count(LIFETIME_TRACE_MARKER) == 1,
        "callback entry marker": request.count(CALLBACK_ENTRY_MARKER) == 1,
        "high refresh marker": request.count(HIGH_REFRESH_MARKER) == 1,
        "user-input refresh marker": request.count(USER_INPUT_REFRESH_MARKER) == 1,
        "path": source.count(r"C:\\Symbian3\\MDLOG.TXT") == 1,
        "logger exported": (
            source.count("void HtcleoMdNotifyLog(") == 1
            and "static void HtcleoMdNotifyLog(" not in source
            and request.count("void HtcleoMdNotifyLog(") == 1
        ),
        "SID gates": (
            source.count("0x101F4CD2u") == 2
            and request.count("0x101F4CD2u") == (
                3 if "HTCLEO_HNMETADATA_INITIAL_NOTIFICATION_COALESCE_V1"
                in request else 2)
        ),
        "bounded close-only": (
            (
                source.count("position <= ((256 * 64) - 64)")
                + source.count("position <= ((16384 * 64) - 64)")
            ) == 1
            and source.count("file.Write(record);") == 1
            and "file.Flush" not in source
        ),
        "specific normalization": (
            source.count("htcleoNotifyError == KErrServerTerminated") == 2
            and source.count("0x4E4F5449u") == 1
            and source.count("User::LeaveIfError(htcleoNotifyError);") == 1
            and source.count("HtcleoResetServiceHandler();") == 1
        ),
        "stock path retained": source.count(
            "NotifyRequest(i).RequestNotifyL("
        ) == 3,
        "sent retained": source.count("iSent = ETrue;") == 2,
        "subscription continuation": (
            request.count("const TInt htcleoNotifyResult = iSh->ExecuteL") == 1
            and request.count("User::LeaveIfError(htcleoNotifyResult);") == 1
            and request.count("HtcleoInitialRefreshL()") == 2
            and request.count("void CHnMdNotifyRequest::HtcleoResetServiceHandler()") == 1
            and request_header.count("void HtcleoResetServiceHandler();") == 1
            and request_header.count("CAsyncCallBack* iHtcleoInitialRefresh;") == 1
            and request_header.count("TBool iHtcleoInitialRefreshIssued;") == 1
            and (
                (
                    not refresh_retired
                    and request.count("iHtcleoInitialRefresh->CallBack();") == 1
                    and request.count("CActive::EPriorityUserInput") == 1
                )
                or (
                    refresh_retired
                    and "iHtcleoInitialRefresh->CallBack();" not in request
                    and "new (ELeave) CAsyncCallBack" not in request
                    and request.count("0x4D440513u") == 1
                    and request.count("0x4D440514u") == 1
                )
            )
            and "CActive::EPriorityHigh" not in request
            and "CActive::EPriorityStandard" not in request
            and "CActive::EPriorityIdle" not in request
        ),
        "lifetime trace": (
            request.count("0x4D44050Au") == 1
            and request.count("0x4D44050Bu") == 1
            and request.count("0x4D44050Du") == 1
            and request.count("iHtcleoInitialRefresh->IsActive()") == 1
            and (
                (not refresh_retired and request.count("0x4D44050Cu") == 1)
                or (refresh_retired and "0x4D44050Cu" not in request)
            )
        ),
        "no timed delay or display": (
            "User::After" not in combined and "HalFunction" not in combined
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if missing:
        failed.append("missing/duplicate stages=" + ",".join(missing))
    if failed:
        raise SystemExit("HN notification compatibility failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/src/hnmdnotifyrequests.cpp"
    )
    request_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/src/hnmdnotifyrequest.cpp"
    )
    request_header_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/inc/hnmdnotifyrequest.h"
    )
    if (
        not source_path.is_file()
        or not request_path.is_file()
        or not request_header_path.is_file()
    ):
        raise SystemExit("missing HN notification source")
    source = source_path.read_text(encoding="latin-1")
    request = request_path.read_text(encoding="latin-1")
    request_header = request_header_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    source, request, request_header = upgrade_reconnect_requery(
        source, request, request_header
    )
    verify(source, request, request_header)
    source_path.write_text(source, encoding="latin-1")
    request_path.write_text(request, encoding="latin-1")
    request_header_path.write_text(request_header, encoding="latin-1")
    if REDUNDANT_REFRESH_RETIRED_MARKER in request:
        print(
            "HTCLEO_HNMETADATA_NOTIFY_POLICY=ui-first reconnect-once-"
            "ready-gated-stock-first-query callback-retired"
        )
    else:
        print(
            "HTCLEO_HNMETADATA_NOTIFY_POLICY=ui-first reconnect-once-"
            "subscribe-then-requery stages=4D440500-4D440509"
        )


if __name__ == "__main__":
    main()
