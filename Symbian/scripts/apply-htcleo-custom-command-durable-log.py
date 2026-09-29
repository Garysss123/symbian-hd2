#!/usr/bin/env python3
"""Install an exact AknCapServer custom-command state-machine trace.

Iteration 432 proves that the UI-services list dispatches command index 7
(``akncustcmds.dll`` ordinal 1), while neither the caller-side APASTART log nor
the APSEXE-side APALOG is created.  This transform records the existing
``CCmdCustomCommand`` loader/factory/initialise/execute state machine and the
small ``CAknCapServerStart`` body without changing retry, completion, leave or
error policy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


SSM_MARKER = "HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG_V1"
AKN_MARKER = "HTCLEO_AKN_CUSTOM_COMMAND_DURABLE_LOG_V1"
SSM_ABI_MARKER = "HTCLEO_GCCE_PRIVATE_TIMER_EXPORT_ABI_V1"
SSM_MACRO = "__HTCLEO_SSM_CUSTOM_COMMAND_DURABLE_LOG__"
AKN_MACRO = "__HTCLEO_AKN_CUSTOM_COMMAND_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def logger_block(marker: str, macro: str, function: str) -> str:
    return f'''\
#ifdef {macro}
// {marker}
static void {function}(TUint32 aStage, TInt aResult, TUint32 aDetail)
\t{{
\tRFs fs;
\tTInt r = fs.Connect();
\tif(r != KErrNone)
\t\t{{
\t\treturn;
\t\t}}

\t_LIT(KHtcleoCustLogDir, "C:\\\\Symbian3\\\\");
\t_LIT(KHtcleoCustLogPath, "C:\\\\Symbian3\\\\CUSTLOG.TXT");
\tr = fs.MkDirAll(KHtcleoCustLogDir);
\tif(r != KErrNone && r != KErrAlreadyExists)
\t\t{{
\t\tfs.Close();
\t\treturn;
\t\t}}

\tRFile file;
\tTInt position = 0;
\tr = file.Open(fs, KHtcleoCustLogPath, EFileWrite | EFileShareAny);
\tif(r == KErrNotFound || r == KErrPathNotFound)
\t\t{{
\t\tr = file.Replace(fs, KHtcleoCustLogPath,
\t\t\tEFileWrite | EFileShareAny);
\t\t}}
\telse if(r == KErrNone)
\t\t{{
\t\tr = file.Seek(ESeekEnd, position);
\t\t}}
\tif(r == KErrNone && position >= (512 * 67))
\t\t{{
\t\tfile.Close();
\t\tfs.Close();
\t\treturn;
\t\t}}

\tif(r == KErrNone)
\t\t{{
\t\t_LIT8(KHtcleoCustPrefix, "HTCLEO_CUST ");
\t\tTBuf8<96> record;
\t\trecord.Append(KHtcleoCustPrefix);
\t\trecord.AppendNumFixedWidth((TUint32)position, EHex, 8);
\t\trecord.Append(' ');
\t\trecord.AppendNumFixedWidth(aStage, EHex, 8);
\t\trecord.Append(' ');
\t\trecord.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
\t\trecord.Append(' ');
\t\trecord.AppendNumFixedWidth(aDetail, EHex, 8);
\t\trecord.Append(' ');
\t\trecord.AppendNumFixedWidth(User::TickCount(), EHex, 8);
\t\trecord.Append(_L8("\\r\\n"));
\t\tr = file.Write(record);
\t\tif(r == KErrNone)
\t\t\t{{
\t\t\tr = file.Flush();
\t\t\t}}
\t\tfile.Close();
\t\t}}
\tfs.Close();
\t}}
#else
inline void {function}(TUint32, TInt, TUint32) {{}}
#endif
'''


def verify(
    ssm: str,
    ssm_header: str,
    ssm_mmp: str,
    akn: str,
    akn_mmp: str,
) -> None:
    checks = {
        "SSM marker": ssm.count(SSM_MARKER) == 1,
        "Akn marker": akn.count(AKN_MARKER) == 1,
        "one CUST path in each module":
            ssm.count("C:\\\\Symbian3\\\\CUSTLOG.TXT") == 1
            and akn.count("C:\\\\Symbian3\\\\CUSTLOG.TXT") == 1,
        "exact Akn gate":
            ssm.count('aInfo->FileName().CompareF(KHtcleoAknCustCmdDll)') == 1
            and ssm.count("aInfo->Ordinal() == 1") == 1,
        "SSM stages": all(
            ssm.count(f"0x0000C{suffix}u") >= 1
            for suffix in (
                "000", "001", "010", "011", "012", "013", "014",
                "015", "016", "017", "018", "019", "020", "021",
                "022", "023", "024", "025", "029", "030", "031",
                "032", "033", "040", "041", "042", "043", "044",
                "045", "046", "0E0",
            )
        ),
        "Akn stages": all(
            akn.count(f"0x0000D{suffix}u") == 1
            for suffix in (
                "010", "011", "020", "021", "022", "023", "024",
                "025", "030",
            )
        ),
        "SSM MMP macro": ssm_mmp.count(f"MACRO          {SSM_MACRO}") == 1,
        "SSM GCCE private RTTI compatibility":
            ssm_header.count(SSM_ABI_MARKER) == 1,
        "SSM frozen ABI remains strict":
            "NOSTRICTDEF" not in ssm_mmp
            and ssm_mmp.count("deffile\t\t\tssmcmd_v1.def") == 1
            and ssm_mmp.count("deffile\t\t\tssmcmd.def") == 1,
        "Akn MMP macro": akn_mmp.count(f"MACRO          {AKN_MACRO}") == 1,
        "Akn efsrv": akn_mmp.lower().count("library         efsrv.lib") == 1,
        "no added wait or delay":
            logger_block(SSM_MARKER, SSM_MACRO, "HtcleoCustomCmdLog").count(
                "User::WaitForRequest"
            ) == 0
            and logger_block(AKN_MARKER, AKN_MACRO, "HtcleoAknCustomLog").count(
                "User::After"
            ) == 0,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("custom-command durable-log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    ssm_component = (
        args.root
        / "sf/os/devicesrv/sysstatemgmt/systemstatemgr/cmd"
    )
    ssm_path = ssm_component / "src/cmdcustomcommand.cpp"
    ssm_header_path = ssm_component / "inc/cmdmultiplewait.h"
    ssm_mmp_path = ssm_component / "group/ssmcmd.mmp"
    akn_component = (
        args.root
        / "sf/mw/classicui/uifw/AknGlobalUI/akncustcmds"
    )
    akn_path = akn_component / "src/akncapserverstart.cpp"
    akn_mmp_path = akn_component / "group/akncustcmds.mmp"
    for path in (
        ssm_path,
        ssm_header_path,
        ssm_mmp_path,
        akn_path,
        akn_mmp_path,
    ):
        if not path.is_file():
            raise SystemExit(f"missing custom-command source/MMP: {path}")

    ssm = ssm_path.read_text(encoding="utf-8").replace("\r", "")
    ssm_header = ssm_header_path.read_text(encoding="utf-8").replace("\r", "")
    ssm_mmp = ssm_mmp_path.read_text(encoding="utf-8").replace("\r", "")
    akn = akn_path.read_text(encoding="utf-8").replace("\r", "")
    akn_mmp = akn_mmp_path.read_text(encoding="utf-8").replace("\r", "")

    if SSM_MARKER not in ssm:
        ssm = replace_once(
            ssm,
            '#include "ssmpanic.h"\n',
            '#include "ssmpanic.h"\n\n'
            + logger_block(SSM_MARKER, SSM_MACRO, "HtcleoCustomCmdLog")
            + '''\

static TBool HtcleoIsAknStartCommand(const CSsmCustomCommandInfo* aInfo)
\t{
\t_LIT(KHtcleoAknCustCmdDll, "akncustcmds.dll");
\treturn aInfo && aInfo->Ordinal() == 1 &&
\t\taInfo->FileName().CompareF(KHtcleoAknCustCmdDll) == 0;
\t}
''',
            "SSM logger include",
        )
        ssm = replace_once(
            ssm,
            '''\
void CCmdCustomCommand::Execute(TRequestStatus& aStatus)
\t{
\taStatus = KRequestPending;
''',
            '''\
void CCmdCustomCommand::Execute(TRequestStatus& aStatus)
\t{
\tconst TBool htcleoTrace = HtcleoIsAknStartCommand(iInfo);
\tif(htcleoTrace)
\t\t{
\t\tHtcleoCustomCmdLog(0x0000C000u, KErrNone,
\t\t\t((TUint32)iInfo->Retries() << 16) | (TUint32)iInfo->Unloading());
\t\t}
\taStatus = KRequestPending;
''',
            "CCmdCustomCommand Execute entry",
        )
        ssm = replace_once(
            ssm,
            '''\
\tCompleteRequest(iStatus, KErrNone);
\tSetActive();
\t}
''',
            '''\
\tCompleteRequest(iStatus, KErrNone);
\tSetActive();
\tif(htcleoTrace)
\t\t{
\t\tHtcleoCustomCmdLog(0x0000C001u, iStatus.Int(), (TUint32)iAction);
\t\t}
\t}
''',
            "CCmdCustomCommand Execute return",
        )
        ssm = replace_once(
            ssm,
            '''\
void CCmdCustomCommand::RunL()
\t{
\tswitch(iAction)
''',
            '''\
void CCmdCustomCommand::RunL()
\t{
\tconst TBool htcleoTrace = HtcleoIsAknStartCommand(iInfo);
\tif(htcleoTrace)
\t\t{
\t\tHtcleoCustomCmdLog(0x0000C010u, iStatus.Int(),
\t\t\t((TUint32)iAttempts << 16) | (TUint32)iAction);
\t\t}
\tswitch(iAction)
''',
            "CCmdCustomCommand RunL entry",
        )
        ssm = replace_once(
            ssm,
            '''\
\t\tcase EPrepareDll:
\t\t\t{
\t\t\tPrepareCustomCmdL();
\t\t\tbreak;
''',
            '''\
\t\tcase EPrepareDll:
\t\t\t{
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C011u, KErrNone, 0u);
\t\t\tPrepareCustomCmdL();
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C019u, KErrNone, (TUint32)iAction);
\t\t\tbreak;
''',
            "RunL prepare branch",
        )
        ssm = replace_once(
            ssm,
            '''\
\t\tcase EInitialiseDll:
\t\t\t{
\t\t\tInitialiseCmdL();
\t\t\tbreak;
''',
            '''\
\t\tcase EInitialiseDll:
\t\t\t{
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C020u, KErrNone, 0u);
\t\t\tInitialiseCmdL();
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C029u, KErrNone, (TUint32)iAction);
\t\t\tbreak;
''',
            "RunL initialise branch",
        )
        ssm = replace_once(
            ssm,
            '''\
\t\tcase EExecuteMethod:
\t\t\t{
\t\t\tSSMLOGLEAVEIFNULL(iCustomCommand);
\t\t\tiCustomCommand->Execute(iInfo->Params(), iStatus);
\t\t\tMoveToNextStateL(KErrNone, EClose, EFalse);\t// custom command will complete this request
\t\t\tbreak;
''',
            '''\
\t\tcase EExecuteMethod:
\t\t\t{
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C030u, KErrNone, iCustomCommand ? 1u : 0u);
\t\t\tSSMLOGLEAVEIFNULL(iCustomCommand);
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C031u, iStatus.Int(), 0u);
\t\t\tiCustomCommand->Execute(iInfo->Params(), iStatus);
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C032u, iStatus.Int(), 0u);
\t\t\tMoveToNextStateL(KErrNone, EClose, EFalse);\t// custom command will complete this request
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C033u, iStatus.Int(), (TUint32)iAction);
\t\t\tbreak;
''',
            "RunL execute branch",
        )
        ssm = replace_once(
            ssm,
            '''\
\t\tcase EClose:
\t\t\t{
\t\t\tTInt err = iStatus.Int();
\t\t\tif (err != KErrNone)
\t\t\t\t{
\t\t\t\t// custom cmd call failed so try it again
\t\t\t\tMoveToNextStateL(err, EExecuteMethod);
\t\t\t\t}
\t\t\telse
\t\t\t\t{
\t\t\t\tSSMLOGLEAVEIFNULL(iCustomCommand);
\t\t\t\tiCustomCommand->Close();
\t\t\t\tCompleteDeferredExecuteRequest(KErrNone);\t\t// success
\t\t\t\t}
\t\t\tbreak;
''',
            '''\
\t\tcase EClose:
\t\t\t{
\t\t\tTInt err = iStatus.Int();
\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C040u, err, (TUint32)iAttempts);
\t\t\tif (err != KErrNone)
\t\t\t\t{
\t\t\t\t// custom cmd call failed so try it again
\t\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C041u, err, (TUint32)iAttempts);
\t\t\t\tMoveToNextStateL(err, EExecuteMethod);
\t\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C042u, err, (TUint32)iAction);
\t\t\t\t}
\t\t\telse
\t\t\t\t{
\t\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C043u, KErrNone, iCustomCommand ? 1u : 0u);
\t\t\t\tSSMLOGLEAVEIFNULL(iCustomCommand);
\t\t\t\tiCustomCommand->Close();
\t\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C044u, KErrNone, 0u);
\t\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C045u, KErrNone, 0u);
\t\t\t\tCompleteDeferredExecuteRequest(KErrNone);\t\t// success
\t\t\t\tif(htcleoTrace) HtcleoCustomCmdLog(0x0000C046u, KErrNone, 0u);
\t\t\t\t}
\t\t\tbreak;
''',
            "RunL close branch",
        )
        ssm = replace_once(
            ssm,
            '''\
TInt CCmdCustomCommand::RunError(TInt aError)
\t{
\tCompleteDeferredExecuteRequest(aError);
''',
            '''\
TInt CCmdCustomCommand::RunError(TInt aError)
\t{
\tif(HtcleoIsAknStartCommand(iInfo))
\t\t{
\t\tHtcleoCustomCmdLog(0x0000C0E0u, aError,
\t\t\t((TUint32)iAttempts << 16) | (TUint32)iAction);
\t\t}
\tCompleteDeferredExecuteRequest(aError);
''',
            "RunError",
        )
        ssm = replace_once(
            ssm,
            '''\
\t\tDEBUGPRINT2(_L("Loading library %S..."), &iInfo->FileName());
\t\terr = iLibrary.Load(iInfo->FileName());
\t\tif (err == KErrNone)
''',
            '''\
\t\tDEBUGPRINT2(_L("Loading library %S..."), &iInfo->FileName());
\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C012u, KErrNone, 0u);
\t\terr = iLibrary.Load(iInfo->FileName());
\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C013u, err, (TUint32)iLibrary.Handle());
\t\tif (err == KErrNone)
''',
            "library load",
        )
        ssm = replace_once(
            ssm,
            '''\
\t\tDEBUGPRINT2A("Looking up ordinal %d...", iInfo->Ordinal());
\t\tTLibraryFunction function = iLibrary.Lookup(iInfo->Ordinal());
\t\tif (function)
\t\t\t{\t
\t\t\t// cast the pointer to our custom cmd type
\t\t\tCustomCmdFunctionType customCmdFunction = reinterpret_cast<CustomCmdFunctionType>(function);
\t\t\tiCustomCommand = (*customCmdFunction)();
\t\t\tif (iCustomCommand)
''',
            '''\
\t\tDEBUGPRINT2A("Looking up ordinal %d...", iInfo->Ordinal());
\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C014u, KErrNone, (TUint32)iInfo->Ordinal());
\t\tTLibraryFunction function = iLibrary.Lookup(iInfo->Ordinal());
\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C015u, KErrNone, function ? 1u : 0u);
\t\tif (function)
\t\t\t{\t
\t\t\t// cast the pointer to our custom cmd type
\t\t\tCustomCmdFunctionType customCmdFunction = reinterpret_cast<CustomCmdFunctionType>(function);
\t\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C016u, KErrNone, 0u);
\t\t\tiCustomCommand = (*customCmdFunction)();
\t\t\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C017u, KErrNone, iCustomCommand ? 1u : 0u);
\t\t\tif (iCustomCommand)
''',
            "ordinal and factory",
        )
        ssm = replace_once(
            ssm,
            '''\
\tMoveToNextStateL(err, EInitialiseDll);
\t}

void CCmdCustomCommand::WriteHandleToFileL''',
            '''\
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C018u, err, (TUint32)iLoaded);
\tMoveToNextStateL(err, EInitialiseDll);
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C019u, err, (TUint32)iAction);
\t}

void CCmdCustomCommand::WriteHandleToFileL''',
            "prepare state completion",
        )
        ssm = replace_once(
            ssm,
            '''\
\tiCmdEnv = CSsmCustomCommandEnv::NewL(iUtilProvider->RfsL());
\tTInt err = iCustomCommand->Initialize(iCmdEnv);
\tif (err!=KErrNone)
''',
            '''\
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C021u, KErrNone, 0u);
\tiCmdEnv = CSsmCustomCommandEnv::NewL(iUtilProvider->RfsL());
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C022u, KErrNone, iCmdEnv ? 1u : 0u);
\tTInt err = iCustomCommand->Initialize(iCmdEnv);
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C023u, err, 0u);
\tif (err!=KErrNone)
''',
            "custom initialise",
        )
        ssm = replace_once(
            ssm,
            '''\
\tMoveToNextStateL(err, EExecuteMethod);
\t}

/**
 Sets the command up''',
            '''\
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C024u, err, (TUint32)iAttempts);
\tMoveToNextStateL(err, EExecuteMethod);
\tif(HtcleoIsAknStartCommand(iInfo)) HtcleoCustomCmdLog(0x0000C025u, err, (TUint32)iAction);
\t}

/**
 Sets the command up''',
            "initialise state completion",
        )

    if SSM_ABI_MARKER not in ssm_header:
        ssm_header = replace_once(
            ssm_header,
            "\tclass CMultipleWaitTimer : public CTimer\n",
            "\t// " + SSM_ABI_MARKER + "\n"
            "\t// The frozen PDK EABI exports this nested class's RTTI and\n"
            "\t// vtable. GCCE otherwise marks both hidden and elf2e32 rejects\n"
            "\t// the strict frozen DEF, so retain their original visibility.\n"
            "\tclass __attribute__((visibility(\"default\"))) "
            "CMultipleWaitTimer : public CTimer\n",
            "SSM private timer visibility",
        )

    if f"MACRO          {SSM_MACRO}" not in ssm_mmp:
        ssm_mmp += f"\nMACRO          {SSM_MACRO}\n"
    ssm_mmp = ssm_mmp.replace("\nNOSTRICTDEF\n", "\n")
    ssm_mmp = ssm_mmp.replace(
        "deffile\t\t\tssmcmd_v1u.def",
        "deffile\t\t\tssmcmd_v1.def",
    )
    ssm_mmp = ssm_mmp.replace(
        "deffile\t\t\tssmcmdu.def",
        "deffile\t\t\tssmcmd.def",
    )

    if AKN_MARKER not in akn:
        akn = replace_once(
            akn,
            '#include "akncapserverstart.h"\n',
            '#include "akncapserverstart.h"\n\n'
            + logger_block(AKN_MARKER, AKN_MACRO, "HtcleoAknCustomLog"),
            "Akn logger include",
        )
        akn = replace_once(
            akn,
            '''\
TInt CAknCapServerStart::Initialize( CSsmCustomCommandEnv* /*aCmdEnv*/ )
    {
    return KErrNone;
''',
            '''\
TInt CAknCapServerStart::Initialize( CSsmCustomCommandEnv* /*aCmdEnv*/ )
    {
    HtcleoAknCustomLog(0x0000D010u, KErrNone, 0u);
    HtcleoAknCustomLog(0x0000D011u, KErrNone, 0u);
    return KErrNone;
''',
            "Akn Initialize",
        )
        akn = replace_once(
            akn,
            '''\
    aRequest = KRequestPending;

    TRAP_IGNORE( SetColorPaletteL() );
    TRAPD( err, RAknUiServer::StartAknCapserverL() );
''',
            '''\
    HtcleoAknCustomLog(0x0000D020u, KErrNone, 0u);
    aRequest = KRequestPending;

    TRAPD( htcleoPaletteResult, SetColorPaletteL() );
    HtcleoAknCustomLog(0x0000D021u, htcleoPaletteResult, 0u);
    HtcleoAknCustomLog(0x0000D022u, KErrNone, 0u);
    TRAPD( err, RAknUiServer::StartAknCapserverL() );
    HtcleoAknCustomLog(0x0000D023u, err, 0u);
''',
            "Akn Execute body",
        )
        akn = replace_once(
            akn,
            '''\
    TRequestStatus* request = &aRequest;
    User::RequestComplete( request, err );
    }
''',
            '''\
    TRequestStatus* request = &aRequest;
    HtcleoAknCustomLog(0x0000D024u, err, 0u);
    User::RequestComplete( request, err );
    HtcleoAknCustomLog(0x0000D025u, err, 0u);
    }
''',
            "Akn RequestComplete",
        )
        akn = replace_once(
            akn,
            '''\
void CAknCapServerStart::Close()
    {
    // Nothing to do.
''',
            '''\
void CAknCapServerStart::Close()
    {
    HtcleoAknCustomLog(0x0000D030u, KErrNone, 0u);
    // Nothing to do.
''',
            "Akn Close",
        )

    if f"MACRO          {AKN_MACRO}" not in akn_mmp:
        akn_mmp = replace_once(
            akn_mmp,
            "LIBRARY         euser.lib\n",
            "LIBRARY         euser.lib\n"
            "LIBRARY         efsrv.lib\n"
            f"MACRO          {AKN_MACRO}\n",
            "Akn MMP dependencies",
        )

    verify(ssm, ssm_header, ssm_mmp, akn, akn_mmp)
    ssm_path.write_text(ssm, encoding="utf-8")
    ssm_header_path.write_text(ssm_header, encoding="utf-8")
    ssm_mmp_path.write_text(ssm_mmp, encoding="utf-8")
    akn_path.write_text(akn, encoding="utf-8")
    akn_mmp_path.write_text(akn_mmp, encoding="utf-8")
    print("HTCLEO_CUSTOM_COMMAND_LOG=installed ssm=C000-C0E0 akn=D010-D030")


if __name__ == "__main__":
    main()
