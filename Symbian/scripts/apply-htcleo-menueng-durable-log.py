#!/usr/bin/env python3
"""Add close-only tracing to the core MenuContent XML/tree loader.

Iteration 536 proves CMenuSrvEng reaches its timer but never returns from
CMenuEng::NewL.  Every operation traced here is part of the real menu tree and
therefore remains fail-closed.  The trace only distinguishes local setup,
XCFW construction, RAM/ROM XML parsing and the nested scheduler boundary.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MENUENG_DURABLE_LOG_V1"
MMP_MARKER = "HTCLEO_MENUENG_FROZEN_ABI_CLOSURE_V1"
HEADER_MARKER = "HTCLEO_MENUENG_NUMATTRIBUTES_LOCAL_ABI_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''

// HTCLEO_MENUENG_DURABLE_LOG_V1
static void HtcleoMenuEngLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x200113DDu)
        {
        return;
        }
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }
    _LIT(KHtcleoMenuEngDir, "C:\\Symbian3\\");
    _LIT(KHtcleoMenuEngPath, "C:\\Symbian3\\MCSLOG.TXT");
    r = fs.MkDirAll(KHtcleoMenuEngDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }
    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoMenuEngPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoMenuEngPath, EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }
    if (r == KErrNone && position <= ((256 * 64) - 64))
        {
        _LIT8(KHtcleoMenuEngPrefix, "HTCLEO_MCS ");
        TBuf8<96> record;
        record.Append(KHtcleoMenuEngPrefix);
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


def install(text: str) -> str:
    text = replace_once(
        text,
        '_LIT( KMenuTempExtension, ".$$$" );\n',
        '_LIT( KMenuTempExtension, ".$$$" );\n' + LOGGER,
        "logger insertion",
    )
    text = replace_once(
        text,
        """void CMenuEng::ConstructL( const TDesC& aName )
    {
    ValidateNameL( aName );
    iName.CreateL( aName );
    User::LeaveIfError( iFs.Connect() );
    // Keep temp file and the RAM file name as members -
    // we use these all the time.
    TFileName fname;
    GetFileNameL( fname, ETempFile );
    iTempFileName.CreateL( fname );
    GetFileNameL( fname, ERamFile );
    iRamFileName.CreateL( fname );
    iObjectFactory = CMenuEngObjectFactoryProxy::NewL( *this );
    iEngine = CXCFWEngine::NewL( this );
    iEngine->RegisterObjectFactoryL( iObjectFactory );
    SelfComplete( KErrNone ); \t// Start processing asynchronously.
    ActiveWaitForFileLoadL();\t//we need to wait until parsing is complete
    }
""",
        """void CMenuEng::ConstructL( const TDesC& aName )
    {
    HtcleoMenuEngLog(0x4D450100u, KErrNone, (TUint32)aName.Length());
    ValidateNameL( aName );
    HtcleoMenuEngLog(0x4D450101u, KErrNone, 0u);
    iName.CreateL( aName );
    HtcleoMenuEngLog(0x4D450102u, KErrNone, 0u);
    const TInt htcleoFsResult = iFs.Connect();
    HtcleoMenuEngLog(0x4D450103u, htcleoFsResult, 0u);
    User::LeaveIfError( htcleoFsResult );
    // Keep temp file and the RAM file name as members -
    // we use these all the time.
    TFileName fname;
    GetFileNameL( fname, ETempFile );
    HtcleoMenuEngLog(0x4D450104u, KErrNone,
        fname.Length() ? (TUint32)fname[0] : 0u);
    iTempFileName.CreateL( fname );
    HtcleoMenuEngLog(0x4D450105u, KErrNone, (TUint32)iTempFileName.Length());
    GetFileNameL( fname, ERamFile );
    HtcleoMenuEngLog(0x4D450106u, KErrNone,
        fname.Length() ? (TUint32)fname[0] : 0u);
    iRamFileName.CreateL( fname );
    HtcleoMenuEngLog(0x4D450107u, KErrNone, (TUint32)iRamFileName.Length());
    HtcleoMenuEngLog(0x4D450108u, KErrNone, 0u);
    iObjectFactory = CMenuEngObjectFactoryProxy::NewL( *this );
    HtcleoMenuEngLog(0x4D450109u, KErrNone, iObjectFactory ? 1u : 0u);
    HtcleoMenuEngLog(0x4D45010Au, KErrNone, 0u);
    iEngine = CXCFWEngine::NewL( this );
    HtcleoMenuEngLog(0x4D45010Bu, KErrNone, iEngine ? 1u : 0u);
    HtcleoMenuEngLog(0x4D45010Cu, KErrNone, 0u);
    iEngine->RegisterObjectFactoryL( iObjectFactory );
    HtcleoMenuEngLog(0x4D45010Du, KErrNone, 0u);
    SelfComplete( KErrNone ); // Start processing asynchronously.
    HtcleoMenuEngLog(0x4D45010Eu, KErrNone, 0u);
    ActiveWaitForFileLoadL(); // we need to wait until parsing is complete
    HtcleoMenuEngLog(0x4D45010Fu, KErrNone, 0u);
    }
""",
        "CMenuEng ConstructL",
    )
    text = replace_once(
        text,
        """void CMenuEng::ActiveWaitForFileLoadL()
    {
    iActiveWait = new( ELeave ) CActiveSchedulerWait();
    if ( !iActiveWait->IsStarted() )
        {
        iActiveWait->Start();
        }
    //now we check if file was properly loaded
    TInt root(0);
    RootFolderL( root );
    if( !root && ( iState != EDead ) )
    \t{
    \t//there was problem with Ram file(probably file was empty), lets load Rom file
    \tiState = ELoadRamFile;
        if ( !iActiveWait->IsStarted() )
            {
            iActiveWait->Start();
            }
    \t}
    }
""",
        """void CMenuEng::ActiveWaitForFileLoadL()
    {
    HtcleoMenuEngLog(0x4D450200u, KErrNone, (TUint32)iState);
    iActiveWait = new( ELeave ) CActiveSchedulerWait();
    HtcleoMenuEngLog(0x4D450201u, KErrNone, iActiveWait ? 1u : 0u);
    if ( !iActiveWait->IsStarted() )
        {
        HtcleoMenuEngLog(0x4D450202u, KErrNone, 0u);
        iActiveWait->Start();
        HtcleoMenuEngLog(0x4D450203u, KErrNone, (TUint32)iState);
        }
    // now we check if file was properly loaded
    TInt root(0);
    TRAPD(htcleoRootResult, RootFolderL( root ));
    HtcleoMenuEngLog(0x4D450204u, htcleoRootResult, (TUint32)root);
    User::LeaveIfError(htcleoRootResult);
    if( !root && ( iState != EDead ) )
    \t{
    \t// there was problem with Ram file, try the ROM file
    \tiState = ELoadRamFile;
        HtcleoMenuEngLog(0x4D450205u, KErrNone, (TUint32)iState);
        if ( !iActiveWait->IsStarted() )
            {
            HtcleoMenuEngLog(0x4D450206u, KErrNone, 0u);
            iActiveWait->Start();
            HtcleoMenuEngLog(0x4D450207u, KErrNone, (TUint32)iState);
            }
    \t}
    HtcleoMenuEngLog(0x4D450208u, KErrNone, (TUint32)root);
    }
""",
        "active wait",
    )
    text = replace_once(
        text,
        """void CMenuEng::RunL()
    {
    switch( iState )
""",
        """void CMenuEng::RunL()
    {
    HtcleoMenuEngLog(0x4D450300u, iStatus.Int(), (TUint32)iState);
    switch( iState )
""",
        "RunL entry",
    )
    text = replace_once(
        text,
        """            iState = ELoadRamFile;
            LoadRamFileL();
            break;
""",
        """            iState = ELoadRamFile;
            HtcleoMenuEngLog(0x4D450310u, KErrNone, (TUint32)iState);
            LoadRamFileL();
            HtcleoMenuEngLog(0x4D450311u, KErrNone, (TUint32)iState);
            break;
""",
        "RunL initial RAM load",
    )
    text = replace_once(
        text,
        """                iObserver.EngineTreeReloaded();
                iState = ELoadRomFile;
                LoadRomFileL();
""",
        """                HtcleoMenuEngLog(0x4D450320u, iStatus.Int(), 0u);
                iObserver.EngineTreeReloaded();
                HtcleoMenuEngLog(0x4D450321u, KErrNone, 0u);
                iState = ELoadRomFile;
                HtcleoMenuEngLog(0x4D450322u, KErrNone, (TUint32)iState);
                LoadRomFileL();
                HtcleoMenuEngLog(0x4D450323u, KErrNone, (TUint32)iState);
""",
        "RunL ROM fallback",
    )
    text = replace_once(
        text,
        """        case ELoadRomFile:
            {
            // Error loading ROM tree is fatal. Nothing we can do.
            User::LeaveIfError( iStatus.Int() );
""",
        """        case ELoadRomFile:
            {
            // Error loading ROM tree is fatal. Nothing we can do.
            HtcleoMenuEngLog(0x4D450330u, iStatus.Int(), (TUint32)iState);
            User::LeaveIfError( iStatus.Int() );
            HtcleoMenuEngLog(0x4D450331u, KErrNone, 0u);
""",
        "RunL ROM completion",
    )
    text = replace_once(
        text,
        """TInt CMenuEng::RunError( TInt aError )
    {
    switch( iState )
""",
        """TInt CMenuEng::RunError( TInt aError )
    {
    HtcleoMenuEngLog(0x4D450350u, aError, (TUint32)iState);
    switch( iState )
""",
        "RunError entry",
    )
    text = replace_once(
        text,
        """void CMenuEng::HandleEngineEventL( TXCFWEngineEvent aEvent )
    {
    switch ( aEvent )
""",
        """void CMenuEng::HandleEngineEventL( TXCFWEngineEvent aEvent )
    {
    HtcleoMenuEngLog(0x4D450400u, KErrNone, (TUint32)aEvent);
    switch ( aEvent )
""",
        "engine event entry",
    )
    text = replace_once(
        text,
        """void CMenuEng::HandleEngineErrorL( TInt aErrorCode )
    {
    // Reset object factory in all cases.
""",
        """void CMenuEng::HandleEngineErrorL( TInt aErrorCode )
    {
    HtcleoMenuEngLog(0x4D450450u, aErrorCode, (TUint32)iState);
    // Reset object factory in all cases.
""",
        "engine error entry",
    )
    text = replace_once(
        text,
        """void CMenuEng::LoadRamFileL()
    {
    __ASSERT_DEBUG( ELoadRamFile == iState, User::Invariant() );
    __ASSERT_DEBUG( !iTree, User::Invariant() );
    iTree = CXCFWTree::NewL();
    // Legacy xml format supported only if the xml is from rom:
    iObjectFactory->SupportLegacyFormat( EFalse );
    iEngine->LoadL( *iTree, iRamFileName );
    }
""",
        """void CMenuEng::LoadRamFileL()
    {
    HtcleoMenuEngLog(0x4D450500u, KErrNone, (TUint32)iState);
    __ASSERT_DEBUG( ELoadRamFile == iState, User::Invariant() );
    __ASSERT_DEBUG( !iTree, User::Invariant() );
    iTree = CXCFWTree::NewL();
    HtcleoMenuEngLog(0x4D450501u, KErrNone, iTree ? 1u : 0u);
    // Legacy xml format supported only if the xml is from rom:
    iObjectFactory->SupportLegacyFormat( EFalse );
    HtcleoMenuEngLog(0x4D450502u, KErrNone, (TUint32)iRamFileName.Length());
    iEngine->LoadL( *iTree, iRamFileName );
    HtcleoMenuEngLog(0x4D450503u, KErrNone, 0u);
    }
""",
        "RAM file load",
    )
    text = replace_once(
        text,
        """void CMenuEng::LoadRomFileL()
    {
    __ASSERT_DEBUG( ELoadRomFile == iState, User::Invariant() );
    // ROM file name is not kept as member - it is used only once.
    TFileName fname;
    GetFileNameL( fname, ERomFile );
\tdelete iIdManager; iIdManager = NULL;
    delete iTree; iTree = NULL;
    iTree = CXCFWTree::NewL();
    // Legacy xml format supported only if the xml is from rom:
    iObjectFactory->SupportLegacyFormat( ETrue );
    iEngine->LoadL( *iTree, fname );
    }
""",
        """void CMenuEng::LoadRomFileL()
    {
    HtcleoMenuEngLog(0x4D450510u, KErrNone, (TUint32)iState);
    __ASSERT_DEBUG( ELoadRomFile == iState, User::Invariant() );
    // ROM file name is not kept as member - it is used only once.
    TFileName fname;
    GetFileNameL( fname, ERomFile );
    HtcleoMenuEngLog(0x4D450511u, KErrNone,
        fname.Length() ? (TUint32)fname[0] : 0u);
\tdelete iIdManager; iIdManager = NULL;
    delete iTree; iTree = NULL;
    HtcleoMenuEngLog(0x4D450512u, KErrNone, 0u);
    iTree = CXCFWTree::NewL();
    HtcleoMenuEngLog(0x4D450513u, KErrNone, iTree ? 1u : 0u);
    // Legacy xml format supported only if the xml is from rom:
    iObjectFactory->SupportLegacyFormat( ETrue );
    HtcleoMenuEngLog(0x4D450514u, KErrNone, (TUint32)fname.Length());
    iEngine->LoadL( *iTree, fname );
    HtcleoMenuEngLog(0x4D450515u, KErrNone, 0u);
    }
""",
        "ROM file load",
    )
    return text


def patch_mmp(text: str) -> str:
    return replace_once(
        text,
        "LIBRARY         centralrepository.lib\n",
        """LIBRARY         centralrepository.lib

// HTCLEO_MENUENG_FROZEN_ABI_CLOSURE_V1
DEFFILE         mcsmenueng.def
""",
        "frozen MenuEng DEF",
    )


def patch_header(text: str) -> str:
    return replace_once(
        text,
        "    IMPORT_C TInt NumAttributes() const;\n",
        """    // HTCLEO_MENUENG_NUMATTRIBUTES_LOCAL_ABI_V1
    TInt NumAttributes() const;
""",
        "local NumAttributes ABI",
    )


def verify(text: str, mmp: str, header: str) -> None:
    expected_sid_count = (
        2 if "HTCLEO_MENUENG_FIRST_CHANGE_RAM_COMMIT_V1" in text else 1
    )
    checks = {
        "marker": text.count(MARKER) == 1,
        "MCSLOG path": text.count("C:\\\\Symbian3\\\\MCSLOG.TXT") == 1,
        "server SID": text.count("0x200113DDu") == expected_sid_count,
        "real RAM load": text.count("iEngine->LoadL( *iTree, iRamFileName )") == 1,
        "real ROM load": text.count("iEngine->LoadL( *iTree, fname )") == 1,
        "real object factory": text.count("CMenuEngObjectFactoryProxy::NewL") == 1,
        "real XCFW engine": text.count("CXCFWEngine::NewL") == 1,
        "nested wait retained": text.count("iActiveWait->Start();") == 2,
        "no fixed delay": "User::After" not in text,
        "no display probe": "HalFunction" not in text,
        "frozen ABI marker": mmp.count(MMP_MARKER) == 1,
        "frozen DEF": mmp.count("DEFFILE         mcsmenueng.def") == 1,
        "local ABI marker": header.count(HEADER_MARKER) == 1,
        "unfrozen import retired": "IMPORT_C TInt NumAttributes() const" not in header,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("MenuEng trace verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/engsrc/menueng.cpp"
    )
    mmp_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/group/mcsmenueng.mmp"
    )
    header_path = (
        args.root
        / "sf/mw/homescreensrv/menucontentsrv/enginc/menuengobject.h"
    )
    if not source_path.is_file() or not mmp_path.is_file() or not header_path.is_file():
        raise SystemExit("missing MenuContent engine source")
    source = source_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    header = header_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    if MMP_MARKER not in mmp:
        mmp = patch_mmp(mmp)
    else:
        mmp = mmp.replace(
            "DEFFILE         mcsmenuengu.def",
            "DEFFILE         mcsmenueng.def",
        )
    if HEADER_MARKER not in header:
        header = patch_header(header)
    verify(source, mmp, header)
    source_path.write_text(source, encoding="latin-1")
    mmp_path.write_text(mmp, encoding="latin-1")
    header_path.write_text(header, encoding="latin-1")
    print(
        "HTCLEO_MENUENG_DURABLE_LOG=installed "
        "stages=4D450100-4D450515 behavior=unchanged"
    )


if __name__ == "__main__":
    main()
