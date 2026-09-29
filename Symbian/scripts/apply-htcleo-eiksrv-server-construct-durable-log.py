#!/usr/bin/env python3
"""Install a fail-open durable trace inside the Eikon UI server DLL.

Iteration 455 proves eiksrvs.exe completes CEikServEnv::ConstructL and enters
CEikServAppUiServer::NewL, but that call does not return.  NewL lives in
eiksrv.dll, so this transform brackets its allocation, ConstructL, StartL and
environment handoff, then densely traces the stock ConstructL dependencies.
It does not change leave, retry, startup, scheduler or display policy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKSRV_SERVER_CONSTRUCT_DURABLE_LOG_V1"
MACRO = "__HTCLEO_EIKSRV_SERVER_CONSTRUCT_LOG__"
STAGES = (
    "E720", "E721", "E722", "E723", "E724", "E725", "E726", "E727",
    "E730", "E731", "E732", "E733", "E734", "E735", "E736", "E737",
    "E738", "E739", "E73A", "E73B", "E73C", "E73D", "E73E", "E73F",
    "E740", "E741", "E742", "E743", "E744", "E745", "E746", "E747",
    "E748", "E749", "E74A", "E74B", "E74C", "E74D", "E74E", "E74F",
    "E750", "E751", "E752", "E753", "E754", "E755", "E756", "E757",
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_EIKSRV_SERVER_CONSTRUCT_LOG__
#include <f32file.h>

// HTCLEO_EIKSRV_SERVER_CONSTRUCT_DURABLE_LOG_V1
static void HtcleoEikSrvDeepLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikSrvDeepLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikSrvDeepLogPath, "C:\\Symbian3\\EIKSRV.TXT");
    r = fs.MkDirAll(KHtcleoEikSrvDeepLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoEikSrvDeepLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoEikSrvDeepLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position < (128 * 64))
        {
        _LIT8(KHtcleoEikSrvDeepPrefix, "HTCLEO_EIKSRV ");
        TBuf8<96> record;
        record.Append(KHtcleoEikSrvDeepPrefix);
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
#else
inline void HtcleoEikSrvDeepLog(TUint32, TInt, TUint32) {}
#endif

'''


def verify(source: str, mmp: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "log path": source.count("C:\\\\Symbian3\\\\EIKSRV.TXT") == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "newl": source.count("CEikServAppUiServer* CEikServAppUiServer::NewL()") == 1,
        "constructl": source.count("void CEikServAppUiServer::ConstructL()") == 1,
    }
    for stage in STAGES:
        checks[f"stage {stage}"] = (
            source.count(f"HtcleoEikSrvDeepLog(0x0000{stage}u") == 1
        )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("epocroot", type=Path)
    args = parser.parse_args()

    component = args.epocroot / "sf/mw/classicui/commonuisupport/uikon"
    source_path = component / "srvsrc/eiksrv.cpp"
    mmp_path = component / "group/eiksrv.mmp"
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = replace_once(
            source,
            '#include <graphics/cone/coedefkeys.h>\n',
            '#include <graphics/cone/coedefkeys.h>\n' + LOGGER,
            "logger insertion",
        )
        source = replace_once(
            source,
            """EXPORT_C CEikServAppUiServer* CEikServAppUiServer::NewL()
\t{
\tCEikServAppUiServer *pS=new CEikServAppUiServer();
    __ASSERT_ALWAYS(pS!=NULL,PanicServer(EEikSrvSvrCreateServer));
\tCleanupStack::PushL(pS);
\tpS->ConstructL();
\tpS->StartL(EIKAPPUI_SERVER_NAME);
\tCleanupStack::Pop();
\tstatic_cast<CEikServEnv*>(CEikonEnv::Static())->SetEikServer(pS);
\treturn pS;
\t}
""",
            """EXPORT_C CEikServAppUiServer* CEikServAppUiServer::NewL()
\t{
\tHtcleoEikSrvDeepLog(0x0000E720u, KErrNone, 0u);
\tCEikServAppUiServer *pS=new CEikServAppUiServer();
\tHtcleoEikSrvDeepLog(0x0000E721u, KErrNone, pS ? 1u : 0u);
    __ASSERT_ALWAYS(pS!=NULL,PanicServer(EEikSrvSvrCreateServer));
\tCleanupStack::PushL(pS);
\tHtcleoEikSrvDeepLog(0x0000E722u, KErrNone, 0u);
\tpS->ConstructL();
\tHtcleoEikSrvDeepLog(0x0000E723u, KErrNone, 0u);
\tHtcleoEikSrvDeepLog(0x0000E724u, KErrNone, 0u);
\tpS->StartL(EIKAPPUI_SERVER_NAME);
\tHtcleoEikSrvDeepLog(0x0000E725u, KErrNone, 0u);
\tCleanupStack::Pop();
\tHtcleoEikSrvDeepLog(0x0000E726u, KErrNone, 0u);
\tstatic_cast<CEikServEnv*>(CEikonEnv::Static())->SetEikServer(pS);
\tHtcleoEikSrvDeepLog(0x0000E727u, KErrNone, 0u);
\treturn pS;
\t}
""",
            "NewL",
        )
        source = replace_once(
            source,
            """void CEikServAppUiServer::ConstructL()
\t{
\tCEikonEnv& eikonEnv=*CEikonEnv::Static();
\tif (eikonEnv.WsSession().FindWindowGroupIdentifier(0,__EIKON_SERVER_NAME,0)==KErrNotFound)
\t\t{
""",
            """void CEikServAppUiServer::ConstructL()
\t{
\tHtcleoEikSrvDeepLog(0x0000E730u, KErrNone, 0u);
\tCEikonEnv& eikonEnv=*CEikonEnv::Static();
\tHtcleoEikSrvDeepLog(0x0000E731u, KErrNone, 0u);
\tconst TInt htcleoExistingServer = eikonEnv.WsSession().FindWindowGroupIdentifier(0,__EIKON_SERVER_NAME,0);
\tHtcleoEikSrvDeepLog(0x0000E732u, htcleoExistingServer, 0u);
\tif (htcleoExistingServer==KErrNotFound)
\t\t{
\t\tHtcleoEikSrvDeepLog(0x0000E733u, KErrNone, 0u);
""",
            "ConstructL entry",
        )
        source = replace_once(
            source,
            """\t\tTResourceReader resourceReader;
\t\teikonEnv.CreateResourceReaderLC(resourceReader, R_EIK_FEP_DEFAULT_DATA);
""",
            """\t\tTResourceReader resourceReader;
\t\tHtcleoEikSrvDeepLog(0x0000E734u, KErrNone, 0u);
\t\teikonEnv.CreateResourceReaderLC(resourceReader, R_EIK_FEP_DEFAULT_DATA);
\t\tHtcleoEikSrvDeepLog(0x0000E735u, KErrNone, 0u);
""",
            "resource reader",
        )
        source = replace_once(
            source,
            """\t\tconst TBool onState = resourceReader.ReadUint8();
\t\t
\t\t// write the "ERepositoryKeyMask_DefaultSetting" settings to the KUidFepFrameworkRepository repository
\t\tCRepository* const repository = CRepository::NewLC(TUid::Uid(KUidFepFrameworkRepository));
\t\tUser::LeaveIfError(repository->StartTransaction(CRepository::EConcurrentReadWriteTransaction));
\t\trepository->CleanupCancelTransactionPushL();
\t\tCFepGenericGlobalSettings::WriteOnStateAndBroadcastL(*repository, onState, ERepositoryKeyMask_DefaultSetting);
\t\tUser::LeaveIfError(repository->Set(ERepositoryKey_DefaultFepId, defaultFep));
\t\tCFepGenericGlobalSettings::WriteOnOrOffKeyDataAndBroadcastL(*repository, TFepOnOrOffKeyData(onKeyCharacterCodeForFoldedMatch, onKeyModifierMask, onKeyModifierValues), ERepositoryKey_DefaultOnKeyData);
\t\tCFepGenericGlobalSettings::WriteOnOrOffKeyDataAndBroadcastL(*repository, TFepOnOrOffKeyData(offKeyCharacterCodeForFoldedMatch, offKeyModifierMask, offKeyModifierValues), ERepositoryKey_DefaultOffKeyData);
\t\tCleanupStack::Pop(); // repository->CleanupCancelTransactionPushL
\t\tTUint32 notUsed = 0;
\t\tUser::LeaveIfError(repository->CommitTransaction(notUsed)); // should never leave with KErrLocked as the "ERepositoryKeyMask_DefaultSetting" settings are only ever written to here
\t\tCleanupStack::PopAndDestroy(repository);
\t\tCleanupStack::PopAndDestroy(); // resourceReader
""",
            """\t\tconst TBool onState = resourceReader.ReadUint8();
\t\tHtcleoEikSrvDeepLog(0x0000E736u, KErrNone, onState ? 1u : 0u);
\t\t
\t\t// write the "ERepositoryKeyMask_DefaultSetting" settings to the KUidFepFrameworkRepository repository
\t\tHtcleoEikSrvDeepLog(0x0000E737u, KErrNone, 0u);
\t\tCRepository* const repository = CRepository::NewLC(TUid::Uid(KUidFepFrameworkRepository));
\t\tHtcleoEikSrvDeepLog(0x0000E738u, KErrNone, repository ? 1u : 0u);
\t\tconst TInt htcleoTransactionResult = repository->StartTransaction(CRepository::EConcurrentReadWriteTransaction);
\t\tHtcleoEikSrvDeepLog(0x0000E739u, htcleoTransactionResult, 0u);
\t\tUser::LeaveIfError(htcleoTransactionResult);
\t\trepository->CleanupCancelTransactionPushL();
\t\tHtcleoEikSrvDeepLog(0x0000E73Au, KErrNone, 0u);
\t\tCFepGenericGlobalSettings::WriteOnStateAndBroadcastL(*repository, onState, ERepositoryKeyMask_DefaultSetting);
\t\tHtcleoEikSrvDeepLog(0x0000E73Bu, KErrNone, 0u);
\t\tconst TInt htcleoSetResult = repository->Set(ERepositoryKey_DefaultFepId, defaultFep);
\t\tHtcleoEikSrvDeepLog(0x0000E73Cu, htcleoSetResult, 0u);
\t\tUser::LeaveIfError(htcleoSetResult);
\t\tHtcleoEikSrvDeepLog(0x0000E73Du, KErrNone, 0u);
\t\tCFepGenericGlobalSettings::WriteOnOrOffKeyDataAndBroadcastL(*repository, TFepOnOrOffKeyData(onKeyCharacterCodeForFoldedMatch, onKeyModifierMask, onKeyModifierValues), ERepositoryKey_DefaultOnKeyData);
\t\tHtcleoEikSrvDeepLog(0x0000E73Eu, KErrNone, 0u);
\t\tCFepGenericGlobalSettings::WriteOnOrOffKeyDataAndBroadcastL(*repository, TFepOnOrOffKeyData(offKeyCharacterCodeForFoldedMatch, offKeyModifierMask, offKeyModifierValues), ERepositoryKey_DefaultOffKeyData);
\t\tHtcleoEikSrvDeepLog(0x0000E73Fu, KErrNone, 0u);
\t\tCleanupStack::Pop(); // repository->CleanupCancelTransactionPushL
\t\tTUint32 notUsed = 0;
\t\tHtcleoEikSrvDeepLog(0x0000E740u, KErrNone, 0u);
\t\tconst TInt htcleoCommitResult = repository->CommitTransaction(notUsed);
\t\tHtcleoEikSrvDeepLog(0x0000E741u, htcleoCommitResult, notUsed);
\t\tUser::LeaveIfError(htcleoCommitResult); // should never leave with KErrLocked as the "ERepositoryKeyMask_DefaultSetting" settings are only ever written to here
\t\tCleanupStack::PopAndDestroy(repository);
\t\tCleanupStack::PopAndDestroy(); // resourceReader
\t\tHtcleoEikSrvDeepLog(0x0000E742u, KErrNone, 0u);
""",
            "repository sequence",
        )
        source = replace_once(
            source,
            '\t\t_LIT(KLitFepswitchExe, "z:\\\\sys\\\\bin\\\\Fepswitch.exe");\n',
            '\t\t_LIT(KLitFepswitchExe, "z:\\\\sys\\\\bin\\\\Fepswitch.exe");\n'
            '\t\tHtcleoEikSrvDeepLog(0x0000E743u, KErrNone, 0u);\n',
            "fepswitch create entry",
        )
        source = replace_once(
            source,
            '\t\tconst TInt fepSwitchLoadErr = fepswitchProcess.Create(KLitFepswitchExe, KNullDesC, TUidType(TUid::Uid(0x1000007a), TUid::Null(), TUid::Uid(0x10272617)));\n',
            '\t\tconst TInt fepSwitchLoadErr = fepswitchProcess.Create(KLitFepswitchExe, KNullDesC, TUidType(TUid::Uid(0x1000007a), TUid::Null(), TUid::Uid(0x10272617)));\n'
            '\t\tHtcleoEikSrvDeepLog(0x0000E744u, fepSwitchLoadErr, 0u);\n',
            "fepswitch create result",
        )
        source = replace_once(
            source,
            '\t\t\tfepswitchProcess.Rendezvous(requestStatus);\n',
            '\t\t\tHtcleoEikSrvDeepLog(0x0000E745u, KErrNone, 0u);\n'
            '\t\t\tfepswitchProcess.Rendezvous(requestStatus);\n'
            '\t\t\tHtcleoEikSrvDeepLog(0x0000E746u, KErrNone, 0u);\n',
            "fepswitch rendezvous",
        )
        source = replace_once(
            source,
            '\t\t\tfepswitchProcess.Resume();\n',
            '\t\t\tfepswitchProcess.Resume();\n'
            '\t\t\tHtcleoEikSrvDeepLog(0x0000E747u, KErrNone, 0u);\n',
            "fepswitch resume",
        )
        source = replace_once(
            source,
            '\t\t\tUser::WaitForRequest(requestStatus);\n',
            '\t\t\tUser::WaitForRequest(requestStatus);\n'
            '\t\t\tHtcleoEikSrvDeepLog(0x0000E748u, requestStatus.Int(), 0u);\n',
            "fepswitch wait",
        )
        source = replace_once(
            source,
            '\t\t\tCleanupStack::PopAndDestroy(&fepswitchProcess);\n',
            '\t\t\tCleanupStack::PopAndDestroy(&fepswitchProcess);\n'
            '\t\t\tHtcleoEikSrvDeepLog(0x0000E749u, KErrNone, 0u);\n',
            "fepswitch close",
        )
        source = replace_once(
            source,
            """\t\tTFileName myDrive;
\t\tDll::FileName(myDrive); // we want the drive-component, in order to load EiksrvUi.dll from the same drive as we're on
\t\tUser::LeaveIfError(parse.SetNoWild(KEiksrvUiDllName,&myDrive,NULL));
\t\tTUidType uidType(KDynamicLibraryUid,KSharedLibraryUid,TUid::Uid(KEiksrvUiDllValue));
\t\tRLibrary lib;
\t\tUser::LeaveIfError(lib.Load(KEiksrvUiDllName,parse.FullName(),uidType));
\t\tCleanupClosePushL(lib);
\t\tCreateCEikServAppUiBase appUi = (CreateCEikServAppUiBase)lib.Lookup(1);
\t\tCEikAppUi* self = (*appUi)();
\t\tUser::LeaveIfNull(self);
\t\tstatic_cast<CEikServEnv&>(eikonEnv).SetUiDll(lib);
\t\tCleanupStack::Pop(); // lib
\t\tself->ConstructL(); // no leaving function may between the creation of "self" and this ConstructL call, as ownership of "this" is transferred to the CCoeEnv at the *start* of CEikServAppUiBase::ConstructL (hence also why "CleanupStack::PushL(self)" is not and should not be done)
\t\t
\t\t//create CEikDebugPreferences object
\t\tiDebugPreferences = CEikDebugPreferences::NewL();
\t\tTRAP_IGNORE(iDebugPreferences->RestoreL(eikonEnv.FsSession()));
""",
            """\t\tTFileName myDrive;
\t\tHtcleoEikSrvDeepLog(0x0000E74Au, KErrNone, 0u);
\t\tDll::FileName(myDrive); // we want the drive-component, in order to load EiksrvUi.dll from the same drive as we're on
\t\tconst TInt htcleoParseResult = parse.SetNoWild(KEiksrvUiDllName,&myDrive,NULL);
\t\tHtcleoEikSrvDeepLog(0x0000E74Bu, htcleoParseResult, 0u);
\t\tUser::LeaveIfError(htcleoParseResult);
\t\tTUidType uidType(KDynamicLibraryUid,KSharedLibraryUid,TUid::Uid(KEiksrvUiDllValue));
\t\tRLibrary lib;
\t\tHtcleoEikSrvDeepLog(0x0000E74Cu, KErrNone, 0u);
\t\tconst TInt htcleoLoadResult = lib.Load(KEiksrvUiDllName,parse.FullName(),uidType);
\t\tHtcleoEikSrvDeepLog(0x0000E74Du, htcleoLoadResult, 0u);
\t\tUser::LeaveIfError(htcleoLoadResult);
\t\tCleanupClosePushL(lib);
\t\tCreateCEikServAppUiBase appUi = (CreateCEikServAppUiBase)lib.Lookup(1);
\t\tHtcleoEikSrvDeepLog(0x0000E74Eu, KErrNone, appUi ? 1u : 0u);
\t\tHtcleoEikSrvDeepLog(0x0000E74Fu, KErrNone, 0u);
\t\tCEikAppUi* self = (*appUi)();
\t\tHtcleoEikSrvDeepLog(0x0000E750u, KErrNone, self ? 1u : 0u);
\t\tUser::LeaveIfNull(self);
\t\tstatic_cast<CEikServEnv&>(eikonEnv).SetUiDll(lib);
\t\tCleanupStack::Pop(); // lib
\t\tHtcleoEikSrvDeepLog(0x0000E751u, KErrNone, 0u);
\t\tself->ConstructL(); // no leaving function may between the creation of "self" and this ConstructL call, as ownership of "this" is transferred to the CCoeEnv at the *start* of CEikServAppUiBase::ConstructL (hence also why "CleanupStack::PushL(self)" is not and should not be done)
\t\tHtcleoEikSrvDeepLog(0x0000E752u, KErrNone, 0u);
\t\t
\t\t//create CEikDebugPreferences object
\t\tHtcleoEikSrvDeepLog(0x0000E753u, KErrNone, 0u);
\t\tiDebugPreferences = CEikDebugPreferences::NewL();
\t\tHtcleoEikSrvDeepLog(0x0000E754u, KErrNone, iDebugPreferences ? 1u : 0u);
\t\tTRAP_IGNORE(iDebugPreferences->RestoreL(eikonEnv.FsSession()));
\t\tHtcleoEikSrvDeepLog(0x0000E755u, KErrNone, 0u);
""",
            "UI DLL sequence",
        )
        source = replace_once(
            source,
            """#endif
\t\t}
\t}
\t
CEikServAppUiServer::~CEikServAppUiServer()
""",
            """#endif
\t\tHtcleoEikSrvDeepLog(0x0000E756u, KErrNone, 0u);
\t\t}
\tHtcleoEikSrvDeepLog(0x0000E757u, KErrNone, 0u);
\t}
\t
CEikServAppUiServer::~CEikServAppUiServer()
""",
            "ConstructL tail",
        )

    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(source, mmp)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    print("HTCLEO_EIKSRV_SERVER_CONSTRUCT_LOG=installed stages=E720-E757")


if __name__ == "__main__":
    main()
