#!/usr/bin/env python3
"""Install bounded durable tracing across StartC32 and c32start.exe.

Iteration 468 reaches E7D7 in CEikServAppUiBase::InitializeL but never reaches
E7D8, proving the synchronous StartC32 call does not return.  Trace both sides
of that existing protocol without changing its process, rendezvous, property,
module-loading, binding, error, or timing policy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER_ROOT = "HTCLEO_C32ROOT_DURABLE_LOG_V1"
MARKER_START = "HTCLEO_C32START_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


ROOT_LOGGER = r'''
#include <f32file.h>

// HTCLEO_C32ROOT_DURABLE_LOG_V1
static void HtcleoC32RootLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    // This trace is for the EikSrv call proven by iteration 468.  Do not let
    // later StartC32 callers replace or append unrelated records.
    if (RProcess().SecureId().iId != 0x10003A4Au)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoC32RootDir, "C:\\Symbian3\\");
    _LIT(KHtcleoC32RootPath, "C:\\Symbian3\\C32ROOT.TXT");
    r = fs.MkDirAll(KHtcleoC32RootDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    if (aStage == 0x0000C700u)
        {
        r = file.Replace(fs, KHtcleoC32RootPath,
            EFileWrite | EFileShareAny);
        }
    else
        {
        r = file.Open(fs, KHtcleoC32RootPath,
            EFileWrite | EFileShareAny);
        if (r == KErrNotFound || r == KErrPathNotFound)
            {
            r = file.Replace(fs, KHtcleoC32RootPath,
                EFileWrite | EFileShareAny);
            }
        else if (r == KErrNone)
            {
            r = file.Seek(ESeekEnd, position);
            }
        }

    if (r == KErrNone && position < (256 * 64))
        {
        _LIT8(KHtcleoC32RootPrefix, "HTCLEO_C32ROOT ");
        TBuf8<96> record;
        record.Append(KHtcleoC32RootPrefix);
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
        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            }
        }
    file.Close();
    fs.Close();
    }

'''


START_LOGGER = r'''

// HTCLEO_C32START_DURABLE_LOG_V1
static void HtcleoC32StartLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoC32StartDir, "C:\\Symbian3\\");
    _LIT(KHtcleoC32StartPath, "C:\\Symbian3\\C32START.TXT");
    r = fs.MkDirAll(KHtcleoC32StartDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    static TBool firstRecord = ETrue;
    RFile file;
    TInt position = 0;
    if (firstRecord && aStage == 0x0000C800u)
        {
        r = file.Replace(fs, KHtcleoC32StartPath,
            EFileWrite | EFileShareAny);
        }
    else
        {
        r = file.Open(fs, KHtcleoC32StartPath,
            EFileWrite | EFileShareAny);
        if (r == KErrNotFound || r == KErrPathNotFound)
            {
            r = file.Replace(fs, KHtcleoC32StartPath,
                EFileWrite | EFileShareAny);
            }
        else if (r == KErrNone)
            {
            r = file.Seek(ESeekEnd, position);
            }
        }

    if (r == KErrNone && position < (512 * 64))
        {
        _LIT8(KHtcleoC32StartPrefix, "HTCLEO_C32START ");
        TBuf8<96> record;
        record.Append(KHtcleoC32StartPrefix);
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
        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            firstRecord = EFalse;
            }
        }
    file.Close();
    fs.Close();
    }

static TUint32 HtcleoC32Hash8(const TDesC8& aText)
    {
    TUint32 hash = 2166136261u;
    for (TInt i = 0; i < aText.Length(); ++i)
        {
        hash ^= (TUint8)aText[i];
        hash *= 16777619u;
        }
    return hash;
    }

static TUint32 HtcleoC32Hash16(const TDesC& aText)
    {
    TUint32 hash = 2166136261u;
    for (TInt i = 0; i < aText.Length(); ++i)
        {
        const TUint16 value = aText[i];
        hash ^= (TUint8)(value & 0xffu);
        hash *= 16777619u;
        hash ^= (TUint8)(value >> 8);
        hash *= 16777619u;
        }
    return hash;
    }

'''


def transform_root(source: str) -> str:
    if MARKER_ROOT in source:
        # Symbian DLLs cannot contain initialized writable data.  Early local
        # compile validation caught the first-record flag before packaging;
        # the unique C700 entry itself is the safe replace condition.
        source = source.replace("    static TBool firstRecord = ETrue;\n", "")
        source = source.replace(
            "    if (firstRecord && aStage == 0x0000C700u)\n",
            "    if (aStage == 0x0000C700u)\n",
        )
        source = source.replace("            firstRecord = EFalse;\n", "")
        return source

    source = replace_once(
        source,
        "#include <e32property.h>\n",
        "#include <e32property.h>\n" + ROOT_LOGGER,
        "c32root logger",
    )
    source = replace_once(
        source,
        """    {

\t__FLOG_DECLARATION_VARIABLE;
\t__FLOG_OPEN(KSubsys, KComponent);
\t__FLOG_1(_L("DoStartC32(\\\"%S\\\")"), &aCMISuppressionList);

    TInt propertyResult = KErrNone;
""",
        """    {

\t__FLOG_DECLARATION_VARIABLE;
\t__FLOG_OPEN(KSubsys, KComponent);
\t__FLOG_1(_L("DoStartC32(\\\"%S\\\")"), &aCMISuppressionList);
    HtcleoC32RootLog(0x0000C700u, KErrNone, (TUint32)aFinishedState);

    TInt propertyResult = KErrNone;
""",
        "c32root entry",
    )
    source = replace_once(
        source,
        """\tTInt result = configurationProperty.Attach(KUidSystemCategory, KUidC32StartPropertyKey.iUid);\t
\tif(result == KErrNone)
\t\t{
\t\tresult = configurationProperty.Get(propertyValue);
\t\t}

\tif(result!=KErrNone || propertyValue==EReset)
""",
        """\tTInt result = configurationProperty.Attach(KUidSystemCategory, KUidC32StartPropertyKey.iUid);\t
    HtcleoC32RootLog(0x0000C701u, result, (TUint32)propertyValue);
\tif(result == KErrNone)
\t\t{
\t\tresult = configurationProperty.Get(propertyValue);
\t\t}
    HtcleoC32RootLog(0x0000C702u, result, (TUint32)propertyValue);

\tif(result!=KErrNone || propertyValue==EReset)
""",
        "c32root property attach",
    )
    source = replace_once(
        source,
        """\t\t{
\t\tRProcess C32Start;
\t\tresult = C32Start.Create(KCommC32StartExe, aCMISuppressionList);

\t\tif (result == KErrNone)
\t\t\t{
\t\t\t__FLOG(_L("StartC32 - Starting C32Start.exe"));
\t\t\tTRequestStatus status;
\t\t\tC32Start.Rendezvous(status);
\t\t\tC32Start.Resume();
\t\t\t__FLOG(_L("StartC32 - waiting for C32Start.exe to complete init."));

\t\t\tUser::WaitForRequest(status);
""",
        """\t\t{
        HtcleoC32RootLog(0x0000C703u, result, (TUint32)propertyValue);
\t\tRProcess C32Start;
\t\tresult = C32Start.Create(KCommC32StartExe, aCMISuppressionList);
        HtcleoC32RootLog(0x0000C704u, result, 0u);

\t\tif (result == KErrNone)
\t\t\t{
\t\t\t__FLOG(_L("StartC32 - Starting C32Start.exe"));
\t\t\tTRequestStatus status;
            HtcleoC32RootLog(0x0000C705u, KErrNone, 0u);
\t\t\tC32Start.Rendezvous(status);
            HtcleoC32RootLog(0x0000C706u, status.Int(), 0u);
\t\t\tC32Start.Resume();
            HtcleoC32RootLog(0x0000C707u, KErrNone, 0u);
\t\t\t__FLOG(_L("StartC32 - waiting for C32Start.exe to complete init."));

            HtcleoC32RootLog(0x0000C708u, status.Int(), 0u);
\t\t\tUser::WaitForRequest(status);
            HtcleoC32RootLog(0x0000C709u, status.Int(), 0u);
""",
        "c32root process rendezvous",
    )
    source = replace_once(
        source,
        """\t\tpropertyResult = configurationProperty.Get(propertyValue);

\t\tif(propertyResult != KErrNone)
\t\t\t{
\t\t\tTRequestStatus status;
\t\t\tC32Start.Rendezvous(status);
\t\t\tpropertyResult = configurationProperty.Get(propertyValue);

\t\t\tif(propertyResult == KErrNone)
\t\t\t\t{
\t\t\t\tC32Start.RendezvousCancel(status);
\t\t\t\t}
\t\t\tUser::WaitForRequest(status);
\t\t\t}
\t\tC32Start.Close();
\t\t}
""",
        """\t\tpropertyResult = configurationProperty.Get(propertyValue);
        HtcleoC32RootLog(0x0000C70Au, propertyResult, (TUint32)propertyValue);

\t\tif(propertyResult != KErrNone)
\t\t\t{
\t\t\tTRequestStatus status;
            HtcleoC32RootLog(0x0000C70Bu, propertyResult, 0u);
\t\t\tC32Start.Rendezvous(status);
\t\t\tpropertyResult = configurationProperty.Get(propertyValue);
            HtcleoC32RootLog(0x0000C70Cu, propertyResult, (TUint32)propertyValue);

\t\t\tif(propertyResult == KErrNone)
\t\t\t\t{
\t\t\t\tC32Start.RendezvousCancel(status);
                HtcleoC32RootLog(0x0000C70Du, status.Int(), 0u);
\t\t\t\t}
\t\t\tUser::WaitForRequest(status);
            HtcleoC32RootLog(0x0000C70Eu, status.Int(), 0u);
\t\t\t}
\t\tC32Start.Close();
\t\t}
    HtcleoC32RootLog(0x0000C70Fu, propertyResult, (TUint32)propertyValue);
""",
        "c32root property discovery",
    )
    source = replace_once(
        source,
        """\tTRequestStatus propertyStatus = KErrNone;

\twhile(propertyStatus == KErrNone && propertyValue < aFinishedState)
\t\t{
\t\t__FLOG_1(_L("StartC32 - Published configuration sequence is %d."), propertyValue);
\t\tconfigurationProperty.Subscribe(propertyStatus);

\t\tif(configurationProperty.Get(propertyValue) == KErrNone && propertyValue>= aFinishedState)
\t\t\t{
\t\t\t__FLOG(_L("StartC32 - Cancelling subscription."));
\t\t\tconfigurationProperty.Cancel();
\t\t\tUser::WaitForRequest(propertyStatus);\t// absorb signal
\t\t\t__FLOG(_L("StartC32 - Absorbed signal."));
\t\t\tbreak;
\t\t\t}
\t\tUser::WaitForRequest(propertyStatus);
\t\t}

\t__FLOG_1(_L("StartC32 - Published configuration sequence is %d."), propertyValue);
""",
        """\tTRequestStatus propertyStatus = KErrNone;
    TInt htcleoPropertyIteration = 0;

\twhile(propertyStatus == KErrNone && propertyValue < aFinishedState)
\t\t{
\t\t__FLOG_1(_L("StartC32 - Published configuration sequence is %d."), propertyValue);
        HtcleoC32RootLog(0x0000C710u, propertyStatus.Int(),
            ((TUint32)htcleoPropertyIteration << 16) | ((TUint32)propertyValue & 0xffffu));
\t\tconfigurationProperty.Subscribe(propertyStatus);
        HtcleoC32RootLog(0x0000C711u, propertyStatus.Int(),
            (TUint32)htcleoPropertyIteration);

        const TInt htcleoPropertyGetResult = configurationProperty.Get(propertyValue);
        HtcleoC32RootLog(0x0000C712u, htcleoPropertyGetResult,
            (TUint32)propertyValue);
\t\tif(htcleoPropertyGetResult == KErrNone && propertyValue>= aFinishedState)
\t\t\t{
\t\t\t__FLOG(_L("StartC32 - Cancelling subscription."));
\t\t\tconfigurationProperty.Cancel();
            HtcleoC32RootLog(0x0000C713u, propertyStatus.Int(),
                (TUint32)propertyValue);
\t\t\tUser::WaitForRequest(propertyStatus);\t// absorb signal
            HtcleoC32RootLog(0x0000C714u, propertyStatus.Int(),
                (TUint32)propertyValue);
\t\t\t__FLOG(_L("StartC32 - Absorbed signal."));
\t\t\tbreak;
\t\t\t}
        HtcleoC32RootLog(0x0000C715u, propertyStatus.Int(),
            (TUint32)propertyValue);
\t\tUser::WaitForRequest(propertyStatus);
        HtcleoC32RootLog(0x0000C716u, propertyStatus.Int(),
            (TUint32)propertyValue);
        ++htcleoPropertyIteration;
\t\t}

    HtcleoC32RootLog(0x0000C717u, propertyStatus.Int(),
        (TUint32)propertyValue);
\t__FLOG_1(_L("StartC32 - Published configuration sequence is %d."), propertyValue);
""",
        "c32root property wait",
    )
    source = replace_once(
        source,
        """\tconfigurationProperty.Close();
\t__FLOG(_L("StartC32 - Root Server configured"));

\t__FLOG_CLOSE;
    return result;
""",
        """\tconfigurationProperty.Close();
    HtcleoC32RootLog(0x0000C718u, result, (TUint32)propertyValue);
\t__FLOG(_L("StartC32 - Root Server configured"));

\t__FLOG_CLOSE;
    HtcleoC32RootLog(0x0000C719u, result, (TUint32)propertyValue);
    return result;
""",
        "c32root return",
    )
    return source


def transform_start(source: str) -> str:
    if MARKER_START in source:
        return source

    source = replace_once(
        source,
        "#include <es_mbman.h>\n",
        "#include <es_mbman.h>\n" + START_LOGGER,
        "c32start logger",
    )
    source = replace_once(
        source,
        """void CBindingRef::RunL()
/** This function is invoked on completion of a bind
and is used to trigger further bindings by calling NotifyBindCompletion
in the controller object which will deal with correct behaviour.
*/
\t{
\tif(iStatus.Int()==KErrNone)
""",
        """void CBindingRef::RunL()
/** This function is invoked on completion of a bind
and is used to trigger further bindings by calling NotifyBindCompletion
in the controller object which will deal with correct behaviour.
*/
\t{
    HtcleoC32StartLog(0x0000C874u, iStatus.Int(), 0u);
\tif(iStatus.Int()==KErrNone)
""",
        "binding completion entry",
    )
    source = replace_once(
        source,
        """\tiStartProcess.NotifyBindCompletion(*this);
\t}

CBindingRef::~CBindingRef()
""",
        """\tiStartProcess.NotifyBindCompletion(*this);
    HtcleoC32StartLog(0x0000C875u, iStatus.Int(), 0u);
\t}

CBindingRef::~CBindingRef()
""",
        "binding completion return",
    )
    source = replace_once(
        source,
        """\t__FLOG_1(_L8("CModuleRef::LoadingCPM - %S"), &iParams.iParams.iName);

\tiState = ELoading;

\tSetPriority(EPriorityHigh);

\tiRootServer.LoadCpm(iStatus, iParams, *iIniData);
\tSetActive();
""",
        """\t__FLOG_1(_L8("CModuleRef::LoadingCPM - %S"), &iParams.iParams.iName);
    const TUint32 htcleoModuleHash = HtcleoC32Hash8(iParams.iParams.iName);
    HtcleoC32StartLog(0x0000C870u, (TInt)iState, htcleoModuleHash);

\tiState = ELoading;

\tSetPriority(EPriorityHigh);

\tiRootServer.LoadCpm(iStatus, iParams, *iIniData);
    HtcleoC32StartLog(0x0000C871u, iStatus.Int(), htcleoModuleHash);
\tSetActive();
""",
        "module load submit",
    )
    source = replace_once(
        source,
        """\t{
\tconst TInt result=iStatus.Int();
\tif(result==KErrNone)
""",
        """\t{
\tconst TInt result=iStatus.Int();
    const TUint32 htcleoModuleHash = HtcleoC32Hash8(iParams.iParams.iName);
    HtcleoC32StartLog(0x0000C872u, result, htcleoModuleHash);
\tif(result==KErrNone)
""",
        "module RunL entry",
    )
    source = replace_once(
        source,
        """\t\t}
\t}

void CModuleRef::DoCancel()
""",
        """\t\t}
    HtcleoC32StartLog(0x0000C873u, result, htcleoModuleHash);
\t}

void CModuleRef::DoCancel()
""",
        "module RunL return",
    )
    source = replace_once(
        source,
        """void CCommsProcessStarter::NotifyLoadCompletion(CModuleRef& /*aModule*/)
/** Called by each CModuleRef when they have finished loading, and calls
bindIfReady() on them.
*/
\t{
\tiModulesLoading--;
""",
        """void CCommsProcessStarter::NotifyLoadCompletion(CModuleRef& aModule)
/** Called by each CModuleRef when they have finished loading, and calls
bindIfReady() on them.
*/
\t{
    HtcleoC32StartLog(0x0000C876u, iModulesLoading,
        HtcleoC32Hash8(aModule.Name()));
\tiModulesLoading--;
""",
        "notify load entry",
    )
    source = replace_once(
        source,
        """\t\t}
\t}

void CCommsProcessStarter::NotifyBindCompletion(CBindingRef& /*aBinding*/)
""",
        """\t\t}
    HtcleoC32StartLog(0x0000C877u, iModulesLoading,
        ((TUint32)iBindCount << 16) | ((TUint32)iUnloadedModuleIdx & 0xffffu));
\t}

void CCommsProcessStarter::NotifyBindCompletion(CBindingRef& /*aBinding*/)
""",
        "notify load return",
    )
    source = replace_once(
        source,
        """\t{
\tiBindCount--;

\tif(iBindCount==0)
""",
        """\t{
    HtcleoC32StartLog(0x0000C878u, iBindCount,
        (TUint32)iUnloadedModuleIdx);
\tiBindCount--;

\tif(iBindCount==0)
""",
        "notify bind",
    )
    source = replace_once(
        source,
        """\tiScaledStartupState = ((iStartupStateObserver->GetState() + 1) * (TUint) KC32StartupStateScalingFactor) - 1;
\tContinueLoading();
""",
        """\tiScaledStartupState = ((iStartupStateObserver->GetState() + 1) * (TUint) KC32StartupStateScalingFactor) - 1;
    HtcleoC32StartLog(0x0000C879u, KErrNone, iScaledStartupState);
\tContinueLoading();
""",
        "startup state change",
    )
    source = replace_once(
        source,
        """\tconst TInt modulesCount = iModules.Count();
\t__FLOG_6(_L8("ContinueLoading: Scaled start-up state 0x%x (%u), %d loads pending, %d binds pending, load pos %d of %d"), iScaledStartupState, iScaledStartupState, iModulesLoading, iBindCount, iUnloadedModuleIdx, modulesCount);

\tif(iModulesLoading > 0 || iBindCount > 0)
\t\t{
\t\treturn;\t// as these complete they'll attempt to continue loading
\t\t}
""",
        """\tconst TInt modulesCount = iModules.Count();
\t__FLOG_6(_L8("ContinueLoading: Scaled start-up state 0x%x (%u), %d loads pending, %d binds pending, load pos %d of %d"), iScaledStartupState, iScaledStartupState, iModulesLoading, iBindCount, iUnloadedModuleIdx, modulesCount);
    HtcleoC32StartLog(0x0000C860u, iModulesLoading,
        ((TUint32)iBindCount << 24) |
        (((TUint32)iUnloadedModuleIdx & 0xfffu) << 12) |
        ((TUint32)modulesCount & 0xfffu));

\tif(iModulesLoading > 0 || iBindCount > 0)
\t\t{
        HtcleoC32StartLog(0x0000C861u, iModulesLoading,
            (TUint32)iBindCount);
\t\treturn;\t// as these complete they'll attempt to continue loading
\t\t}
""",
        "continue loading entry",
    )
    source = replace_once(
        source,
        """\t\t\tif(mod->State()==ENotLoaded && ((mod->IsOnDemand() && !mod->Message().IsNull()) || !mod->IsOnDemand()))
\t\t\t\t{
\t\t\t\tmod->Load();
\t\t\t\tif(allModsOnDemand)
""",
        """\t\t\tif(mod->State()==ENotLoaded && ((mod->IsOnDemand() && !mod->Message().IsNull()) || !mod->IsOnDemand()))
\t\t\t\t{
                HtcleoC32StartLog(0x0000C862u, iUnloadedModuleIdx,
                    HtcleoC32Hash8(mod->Name()));
\t\t\t\tmod->Load();
                HtcleoC32StartLog(0x0000C863u, iUnloadedModuleIdx,
                    HtcleoC32Hash8(mod->Name()));
\t\t\t\tif(allModsOnDemand)
""",
        "continue module submit",
    )
    source = replace_once(
        source,
        """\t\t\t++iUnloadedModuleIdx;
\t\t\t}


\tif(iUnloadedModuleIdx == modulesCount && allModsOnDemand)
""",
        """\t\t\t++iUnloadedModuleIdx;
\t\t\t}
    HtcleoC32StartLog(0x0000C864u, iModulesLoading,
        ((TUint32)iUnloadedModuleIdx << 16) | ((TUint32)modulesCount & 0xffffu));


\tif(iUnloadedModuleIdx == modulesCount && allModsOnDemand)
""",
        "continue batch result",
    )
    source = replace_once(
        source,
        """\t\t\tiPublicationLevel = EPublishedComplete;
\t\t\tiConfigurationProperty.Set(EConfigurationComplete);

\t\t\t}
""",
        """\t\t\tiPublicationLevel = EPublishedComplete;
            const TInt htcleoCompletePublishResult =
                iConfigurationProperty.Set(EConfigurationComplete);
            HtcleoC32StartLog(0x0000C865u, htcleoCompletePublishResult,
                (TUint32)EConfigurationComplete);

\t\t\t}
""",
        "publish complete",
    )
    source = replace_once(
        source,
        """\t\tiPublicationLevel = EPublishedCore;
\t\tiConfigurationProperty.Set(ECoreComponentsStarted);

\t\t}
\t}
""",
        """\t\tiPublicationLevel = EPublishedCore;
        const TInt htcleoCorePublishResult =
            iConfigurationProperty.Set(ECoreComponentsStarted);
        HtcleoC32StartLog(0x0000C866u, htcleoCorePublishResult,
            (TUint32)ECoreComponentsStarted);

\t\t}
    HtcleoC32StartLog(0x0000C867u, iModulesLoading,
        ((TUint32)iUnloadedModuleIdx << 16) | ((TUint32)modulesCount & 0xffffu));
\t}
""",
        "continue return",
    )
    source = replace_once(
        source,
        """\t{
\t__FLOG(_L8("CBindingRef::ReadConfigAndStartAllL"));

\t// start the configurator server
\tTRAPD(err, iConfiguratorServer = CRsConfiguratorServer::NewL(*this));
""",
        """\t{
\t__FLOG(_L8("CBindingRef::ReadConfigAndStartAllL"));
    HtcleoC32StartLog(0x0000C840u, KErrNone, 0u);

\t// start the configurator server
\tTRAPD(err, iConfiguratorServer = CRsConfiguratorServer::NewL(*this));
    HtcleoC32StartLog(0x0000C841u, err,
        iConfiguratorServer ? 1u : 0u);
""",
        "read config entry",
    )
    source = replace_once(
        source,
        """\tTAutoClose<RFs> fs;
\tTInt result;
\tif(KErrNone!=(result=fs.iObj.Connect()))
""",
        """\tTAutoClose<RFs> fs;
\tTInt result;
    result = fs.iObj.Connect();
    HtcleoC32StartLog(0x0000C842u, result, 0u);
\tif(KErrNone!=result)
""",
        "read config fs connect",
    )
    source = replace_once(
        source,
        """\tTBuf<KMaxPath> privatePath;
\tUser::LeaveIfError(fs.iObj.PrivatePath(privatePath));
""",
        """\tTBuf<KMaxPath> privatePath;
    const TInt htcleoPrivatePathResult = fs.iObj.PrivatePath(privatePath);
    HtcleoC32StartLog(0x0000C843u, htcleoPrivatePathResult,
        HtcleoC32Hash16(privatePath));
\tUser::LeaveIfError(htcleoPrivatePathResult);
""",
        "read config private path",
    )
    source = replace_once(
        source,
        """\tresult = ff.FindWildByDir(KC32StartIniFile, privatePath, iniFileList);
\tCleanupStack::PushL(iniFileList);
""",
        """\tresult = ff.FindWildByDir(KC32StartIniFile, privatePath, iniFileList);
    HtcleoC32StartLog(0x0000C844u, result, 0u);
\tCleanupStack::PushL(iniFileList);
""",
        "read config ini search",
    )
    source = replace_once(
        source,
        """#ifdef SYMBIAN_NETWORKING_CFTRANSPORT
\tcmiList->UniqueWildScanAcrossDrivesL(privatePath, KC32WildCard);\t\t// masking of CMI files on basis of module names Y->A:Z
#else
\tcmiList->WildScanAcrossDrivesL(privatePath, KC32WildCard);\t\t// masking of CMI files on basis of module names Y->A:Z
#endif

\tif(cmiList->Count()==0)
""",
        """    HtcleoC32StartLog(0x0000C845u, KErrNone,
        HtcleoC32Hash16(privatePath));
#ifdef SYMBIAN_NETWORKING_CFTRANSPORT
\tcmiList->UniqueWildScanAcrossDrivesL(privatePath, KC32WildCard);\t\t// masking of CMI files on basis of module names Y->A:Z
#else
\tcmiList->WildScanAcrossDrivesL(privatePath, KC32WildCard);\t\t// masking of CMI files on basis of module names Y->A:Z
#endif
    HtcleoC32StartLog(0x0000C846u, KErrNone,
        (TUint32)cmiList->Count());

\tif(cmiList->Count()==0)
""",
        "CMI scan",
    )
    source = replace_once(
        source,
        """\twhile((result = iRootServer.EnumerateModules(modulePos, name)) == KErrNone)
\t\t{
\t\t++totalModules;
\t\t}
\t__ASSERT_DEBUG(result == KErrEof, User::Panic(KSpecAssert_RootSrvc32start, 2));
""",
        """\twhile((result = iRootServer.EnumerateModules(modulePos, name)) == KErrNone)
\t\t{
\t\t++totalModules;
\t\t}
    HtcleoC32StartLog(0x0000C847u, result, (TUint32)totalModules);
\t__ASSERT_DEBUG(result == KErrEof, User::Panic(KSpecAssert_RootSrvc32start, 2));
""",
        "root module enumeration",
    )
    source = replace_once(
        source,
        """\tiDeathWatcher = CDeathWatcher::NewL(*this);
#ifndef SYMBIAN_ZERO_COPY_NETWORKING
""",
        """\tiDeathWatcher = CDeathWatcher::NewL(*this);
    HtcleoC32StartLog(0x0000C848u, KErrNone,
        iDeathWatcher ? 1u : 0u);
#ifndef SYMBIAN_ZERO_COPY_NETWORKING
""",
        "death watcher",
    )
    source = replace_once(
        source,
        """  \tresult = iRootServer.SetMBufPoolSize(iInitMBufPoolSize, iMaxMBufPoolSize);
  \tif(result==KErrInUse)
""",
        """  \tresult = iRootServer.SetMBufPoolSize(iInitMBufPoolSize, iMaxMBufPoolSize);
    HtcleoC32StartLog(0x0000C849u, result,
        ((TUint32)iInitMBufPoolSize << 16) |
        ((TUint32)iMaxMBufPoolSize & 0xffffu));
  \tif(result==KErrInUse)
""",
        "mbuf pool",
    )
    source = replace_once(
        source,
        """\t// We have a list of filenames, process them...
\tfor (TInt i=0; i<cmiList->Count(); i++)
\t\t{
\t\tconst TDesC& cmiEntry = (*cmiList)[i].iName;
\t\tfullentry.Set(cmiEntry, &ff.File(), NULL);
""",
        """\t// We have a list of filenames, process them...
    HtcleoC32StartLog(0x0000C84Au, KErrNone,
        (TUint32)cmiList->Count());
\tfor (TInt i=0; i<cmiList->Count(); i++)
\t\t{
\t\tconst TDesC& cmiEntry = (*cmiList)[i].iName;
        const TUint32 htcleoCmiHash = HtcleoC32Hash16(cmiEntry);
        HtcleoC32StartLog(0x0000C84Bu, i, htcleoCmiHash);
\t\tfullentry.Set(cmiEntry, &ff.File(), NULL);
""",
        "CMI loop entry",
    )
    source = replace_once(
        source,
        """\t\t\t); //)TRAP\t//lint !e429\t// custody taken of pBinding

\t\t__FLOG_STMT(
""",
        """\t\t\t); //)TRAP\t//lint !e429\t// custody taken of pBinding
        HtcleoC32StartLog(0x0000C84Cu, result, htcleoCmiHash);

\t\t__FLOG_STMT(
""",
        "CMI loop result",
    )
    source = replace_once(
        source,
        """\tCleanupStack::PopAndDestroy(cmiList);
\tfs.Pop();

\tiModulesLoading = 0;
""",
        """    HtcleoC32StartLog(0x0000C84Du, iModules.Count(),
        (TUint32)iBindings.Count());
\tCleanupStack::PopAndDestroy(cmiList);
\tfs.Pop();

\tiModulesLoading = 0;
""",
        "CMI loop completion",
    )
    source = replace_once(
        source,
        """\tRDebug::Printf("\\n");

\tContinueLoading();
\t}
""",
        """\tRDebug::Printf("\\n");

    HtcleoC32StartLog(0x0000C84Eu, iModules.Count(),
        (TUint32)iScaledStartupState);
\tContinueLoading();
    HtcleoC32StartLog(0x0000C84Fu, iModulesLoading,
        (TUint32)iUnloadedModuleIdx);
\t}
""",
        "read config return",
    )
    source = replace_once(
        source,
        """    TBool alreadyRunning = aRootServer.Connect() == KErrNone;

    //If we couldnt connect, we need to launch c32exe.exe
""",
        """    HtcleoC32StartLog(0x0000C820u, KErrNone, 0u);
    const TInt htcleoInitialConnectResult = aRootServer.Connect();
    TBool alreadyRunning = htcleoInitialConnectResult == KErrNone;
    HtcleoC32StartLog(0x0000C821u, htcleoInitialConnectResult,
        alreadyRunning ? 1u : 0u);

    //If we couldnt connect, we need to launch c32exe.exe
""",
        "configurator initial connect",
    )
    source = replace_once(
        source,
        """\t\tRProcess rootServerExe;
\t\tTInt result = rootServerExe.Create(KRootServerExe, KNullDesC);
\t\tif (result == KErrNone)
""",
        """\t\tRProcess rootServerExe;
        HtcleoC32StartLog(0x0000C822u, KErrNone, 0u);
\t\tTInt result = rootServerExe.Create(KRootServerExe, KNullDesC);
        HtcleoC32StartLog(0x0000C823u, result, 0u);
\t\tif (result == KErrNone)
""",
        "root server create",
    )
    source = replace_once(
        source,
        """\t\t\trootServerExe.SetPriority(KRootServerDefaultPriority);
\t\t\trootServerExe.Rendezvous(status);
\t\t\trootServerExe.Resume();
\t\t\t__FLOG(_L8("wait for RS to complete init."));

\t\t\tUser::WaitForRequest(status);
\t\t\trootServerExe.Close();
""",
        """\t\t\trootServerExe.SetPriority(KRootServerDefaultPriority);
\t\t\trootServerExe.Rendezvous(status);
            HtcleoC32StartLog(0x0000C824u, status.Int(), 0u);
\t\t\trootServerExe.Resume();
            HtcleoC32StartLog(0x0000C825u, KErrNone, 0u);
\t\t\t__FLOG(_L8("wait for RS to complete init."));

\t\t\tUser::WaitForRequest(status);
            HtcleoC32StartLog(0x0000C826u, status.Int(), 0u);
\t\t\trootServerExe.Close();
""",
        "root server rendezvous",
    )
    source = replace_once(
        source,
        """\t    result = aRootServer.Connect();
\t    if(result!=KErrNone)
""",
        """\t    result = aRootServer.Connect();
        HtcleoC32StartLog(0x0000C827u, result, 0u);
\t    if(result!=KErrNone)
""",
        "configurator reconnect",
    )
    source = replace_once(
        source,
        """\tif(!aRootServer.IsCallerConfigurationAuthority())
\t\t{
""",
        """    const TBool htcleoIsAuthority =
        aRootServer.IsCallerConfigurationAuthority();
    HtcleoC32StartLog(0x0000C828u, KErrNone,
        htcleoIsAuthority ? 1u : 0u);
\tif(!htcleoIsAuthority)
\t\t{
""",
        "configurator authority",
    )
    source = replace_once(
        source,
        """\tpCCommsStartProcess = CCommsProcessStarter::NewLC(aRootServer, aProperty);
\t__FLOG_STMT(
""",
        """\tpCCommsStartProcess = CCommsProcessStarter::NewLC(aRootServer, aProperty);
    HtcleoC32StartLog(0x0000C829u, KErrNone,
        pCCommsStartProcess ? 1u : 0u);
\t__FLOG_STMT(
""",
        "configurator starter",
    )
    source = replace_once(
        source,
        """    pCCommsStartProcess->ReadConfigAndStartAllL(aCMISuppressions);
\tCleanupStack::Pop(pCCommsStartProcess);
\treturn KErrNone;
""",
        """    HtcleoC32StartLog(0x0000C82Au, KErrNone, 0u);
    pCCommsStartProcess->ReadConfigAndStartAllL(aCMISuppressions);
    HtcleoC32StartLog(0x0000C82Bu, KErrNone, 0u);
\tCleanupStack::Pop(pCCommsStartProcess);
    HtcleoC32StartLog(0x0000C82Cu, KErrNone, 0u);
\treturn KErrNone;
""",
        "configurator read config",
    )
    source = replace_once(
        source,
        """    {

\t// Renaming is very cosmetic so we ignore the result
""",
        """    {
    HtcleoC32StartLog(0x0000C800u, KErrNone, 0u);

\t// Renaming is very cosmetic so we ignore the result
""",
        "c32start entry",
    )
    source = replace_once(
        source,
        """\tresult = configurationProperty.Define(KUidSystemCategory, KUidC32StartPropertyKey.iUid, RProperty::EInt, readPolicy, writePolicy);
\t__ASSERT_ALWAYS(result == KErrNone || result == KErrAlreadyExists, User::Panic(KPanicSource, EPanicPubSub));
\tresult = configurationProperty.Attach(KUidSystemCategory, KUidC32StartPropertyKey.iUid);
\t__ASSERT_ALWAYS(result == KErrNone, User::Panic(KPanicSource, EPanicPubSub));
""",
        """\tresult = configurationProperty.Define(KUidSystemCategory, KUidC32StartPropertyKey.iUid, RProperty::EInt, readPolicy, writePolicy);
    HtcleoC32StartLog(0x0000C801u, result, 0u);
\t__ASSERT_ALWAYS(result == KErrNone || result == KErrAlreadyExists, User::Panic(KPanicSource, EPanicPubSub));
\tresult = configurationProperty.Attach(KUidSystemCategory, KUidC32StartPropertyKey.iUid);
    HtcleoC32StartLog(0x0000C802u, result, 0u);
\t__ASSERT_ALWAYS(result == KErrNone, User::Panic(KPanicSource, EPanicPubSub));
""",
        "c32start property",
    )
    source = replace_once(
        source,
        """\tCTrapCleanup* cleanupStack = CTrapCleanup::New();
\tif(!cleanupStack)
""",
        """\tCTrapCleanup* cleanupStack = CTrapCleanup::New();
    HtcleoC32StartLog(0x0000C803u, KErrNone,
        cleanupStack ? 1u : 0u);
\tif(!cleanupStack)
""",
        "c32start cleanup",
    )
    source = replace_once(
        source,
        """\tCActiveScheduler* pA = new CActiveScheduler;
\t__ASSERT_ALWAYS(pA != NULL, User::Panic(KPanicSource, ENoMemory));
\tCActiveScheduler::Install(pA);
""",
        """\tCActiveScheduler* pA = new CActiveScheduler;
    HtcleoC32StartLog(0x0000C804u, KErrNone, pA ? 1u : 0u);
\t__ASSERT_ALWAYS(pA != NULL, User::Panic(KPanicSource, ENoMemory));
\tCActiveScheduler::Install(pA);
""",
        "c32start scheduler",
    )
    source = replace_once(
        source,
        """    TInt suppressionBufLength;
\tsuppressionBufLength = User::CommandLineLength();
\tHBufC* suppressionBuf = HBufC::NewMax(suppressionBufLength);
""",
        """    TInt suppressionBufLength;
\tsuppressionBufLength = User::CommandLineLength();
    HtcleoC32StartLog(0x0000C805u, KErrNone,
        (TUint32)suppressionBufLength);
\tHBufC* suppressionBuf = HBufC::NewMax(suppressionBufLength);
""",
        "c32start command line",
    )
    source = replace_once(
        source,
        """\t// we indicate we are running and busy configuring so caller can start watching the progress property
\tRProcess::Rendezvous(KErrNone);\t// we indicate we are done as property is important to caller!

    TRAP(result, result = InitConfiguratorL(pCCommsStartProcess, rootServerSession, configurationProperty, suppressions));
""",
        """\t// we indicate we are running and busy configuring so caller can start watching the progress property
    HtcleoC32StartLog(0x0000C806u, KErrNone, 0u);
\tRProcess::Rendezvous(KErrNone);\t// we indicate we are done as property is important to caller!
    HtcleoC32StartLog(0x0000C807u, KErrNone, 0u);

    HtcleoC32StartLog(0x0000C808u, KErrNone, 0u);
    TRAP(result, result = InitConfiguratorL(pCCommsStartProcess, rootServerSession, configurationProperty, suppressions));
    HtcleoC32StartLog(0x0000C809u, result, 0u);
""",
        "c32start init call",
    )
    source = replace_once(
        source,
        """\tif(result==KErrNone)
\t\t{
\t\tCActiveScheduler::Start();
\t\t}
""",
        """\tif(result==KErrNone)
\t\t{
        HtcleoC32StartLog(0x0000C80Au, result, 0u);
\t\tCActiveScheduler::Start();
        HtcleoC32StartLog(0x0000C80Bu, result, 0u);
\t\t}
""",
        "c32start scheduler start",
    )
    source = replace_once(
        source,
        """\t__UHEAP_MARKEND;

\treturn KErrNone;
""",
        """\t__UHEAP_MARKEND;

    HtcleoC32StartLog(0x0000C80Cu, KErrNone, 0u);
\treturn KErrNone;
""",
        "c32start return",
    )
    return source


def transform_root_mmp(mmp: str) -> str:
    if "LIBRARY         efsrv.lib" not in mmp:
        mmp = replace_once(
            mmp,
            "LIBRARY\t        euser.lib commsfw.lib\n",
            "LIBRARY\t        euser.lib commsfw.lib\n"
            "LIBRARY         efsrv.lib\n",
            "c32root efsrv import",
        )
    return mmp


def verify(root: str, start: str, root_mmp: str) -> None:
    checks = {
        "root marker": root.count(MARKER_ROOT) == 1,
        "root path": root.count("C:\\\\Symbian3\\\\C32ROOT.TXT") == 1,
        "root SID gate": root.count("0x10003A4Au") == 1,
        "root StartC32": root.count("EXPORT_C TInt StartC32()") == 1,
        "root process create": root.count(
            "C32Start.Create(KCommC32StartExe, aCMISuppressionList)"
        ) == 1,
        "root efsrv import": root_mmp.count("LIBRARY         efsrv.lib") == 1,
        "start marker": start.count(MARKER_START) == 1,
        "start path": start.count("C:\\\\Symbian3\\\\C32START.TXT") == 1,
        "start E32Main": start.count("TInt E32Main()") == 1,
        "start config read": start.count(
            "pCCommsStartProcess->ReadConfigAndStartAllL(aCMISuppressions)"
        ) == 1,
        "start root process": start.count(
            "rootServerExe.Create(KRootServerExe, KNullDesC)"
        ) == 1,
        "start module load": start.count(
            "iRootServer.LoadCpm(iStatus, iParams, *iIniData)"
        ) == 1,
    }
    root_stages = [f"C7{x:02X}" for x in range(0x1A)]
    start_stages = (
        [f"C80{x:X}" for x in range(0xD)]
        + [f"C82{x:X}" for x in range(0xD)]
        + [f"C84{x:X}" for x in range(0x10)]
        + [f"C86{x:X}" for x in range(0x8)]
        + [f"C87{x:X}" for x in range(0xA)]
    )
    for stage in root_stages:
        checks[f"root stage {stage}"] = (
            root.count(f"HtcleoC32RootLog(0x0000{stage}u") == 1
        )
    for stage in start_stages:
        checks[f"start stage {stage}"] = (
            start.count(f"HtcleoC32StartLog(0x0000{stage}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("C32 trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()
    component = args.epocroot / (
        "sf/os/commsfw/commsprocess/commsrootserverconfig"
    )
    root_path = component / "rootsrv/c32root.cpp"
    start_path = component / "configurator/src/c32start.cpp"
    root_mmp_path = component / "group/c32root.mmp"
    root = root_path.read_text(encoding="latin-1")
    start = start_path.read_text(encoding="latin-1")
    root_mmp = root_mmp_path.read_text(encoding="latin-1")
    root = transform_root(root)
    start = transform_start(start)
    root_mmp = transform_root_mmp(root_mmp)
    verify(root, start, root_mmp)
    root_path.write_text(root, encoding="latin-1")
    start_path.write_text(start, encoding="latin-1")
    root_mmp_path.write_text(root_mmp, encoding="latin-1")
    print(
        "HTCLEO_C32_STARTUP_DURABLE_LOG=installed "
        "root=C700-C719 start=C800-C879 policy=unchanged"
    )


if __name__ == "__main__":
    main()
