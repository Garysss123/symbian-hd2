#!/usr/bin/env python3
"""Install fail-open durable tracing around AknSkinSrv startup.

Iteration 458 reaches ``AknsUtils::InitSkinSupportL`` but neither returns nor
leaves.  This transform brackets the client session/startup path and the
server's pre-Rendezvous construction path in the one DLL shared by both
processes.  It changes no retry, timeout, scheduler, rendezvous, skin, or
display policy.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


MARKER = "HTCLEO_AKNSKINSRV_DURABLE_LOG_V1"
FALLBACK_MARKER = "HTCLEO_AKNSKINSRV_FALLBACK_MERGE_TRACE_V1"
RESTORE_MARKER = "HTCLEO_AKNSKINSRV_RESTORE_DEFAULT_TRACE_V1"
BOOT_DRM_DEFER_MARKER = "HTCLEO_AKNSKINSRV_BOOT_DRM_DEFER_V1"
SETTINGS_MARKER = "HTCLEO_AKNSKINSRV_SETTINGS_DEFAULT_TRACE_V1"
CAPACITY_MARKER = "HTCLEO_AKNSKIN_LOG_CAPACITY_256_V1"
MXML_COMPAT_MARKER = "HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_COMPAT_V1"
CASE_COMPAT_MARKER = "HTCLEO_AKNSKINSRV_CASE_ALIAS_COMPAT_V1"
SVG_HEADER_COMPAT_MARKER = "HTCLEO_SVG_SAVE_DOM_QUALIFICATION_COMPAT_V1"
EABI_DEF_MARKER = "HTCLEO_AKNSKINSRV_EABI_FROZEN_DEF_V1"
EABI_DEF_BACKUP = "AKNSKINSRVU.DEF.htcleo-armcc-original"
MACRO = "__HTCLEO_AKNSKINSRV_DURABLE_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


LOGGER = r'''
#ifdef __HTCLEO_AKNSKINSRV_DURABLE_LOG__
#include <f32file.h>

// HTCLEO_AKNSKINSRV_DURABLE_LOG_V1
void HtcleoAknSkinLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                         __attribute__((noinline));

void HtcleoAknSkinLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoAknSkinLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoAknSkinLogPath, "C:\\Symbian3\\SKINLOG.TXT");
    r = fs.MkDirAll(KHtcleoAknSkinLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoAknSkinLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoAknSkinLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    // HTCLEO_AKNSKIN_LOG_CAPACITY_256_V1
    if (r == KErrNone && position < (256 * 64))
        {
        _LIT8(KHtcleoAknSkinPrefix, "HTCLEO_SKIN ");
        TBuf8<80> record;
        record.Append(KHtcleoAknSkinPrefix);
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
            (void)file.Flush();
            }
        }

    file.Close();
    fs.Close();
    }
#else
void HtcleoAknSkinLog(TUint32, TInt, TUint32) {}
#endif

'''


CLIENT_DECL = r'''
#ifdef __HTCLEO_AKNSKINSRV_DURABLE_LOG__
extern void HtcleoAknSkinLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
inline void HtcleoAknSkinLog(TUint32, TInt, TUint32) {}
#endif

'''

SETTINGS_DECL = r'''
// HTCLEO_AKNSKINSRV_SETTINGS_DEFAULT_TRACE_V1
#ifdef __HTCLEO_AKNSKINSRV_DURABLE_LOG__
extern void HtcleoAknSkinLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
inline void HtcleoAknSkinLog(TUint32, TInt, TUint32) {}
#endif

'''


MXML_COMPAT = r'''/* Build-only compatibility for the incomplete public SVG SDK. */
#ifndef HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_COMPAT_H
#define HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_COMPAT_H

// HTCLEO_MXMLATTRIBUTES_FORWARD_DECL_COMPAT_V1
// SVGListener.h exposes this type only by reference.  The public tree omits
// its defining header, so a forward declaration is sufficient and preserves
// the SVG listener ABI without removing wallpaper/SVG support.
class MXMLAttributes;

#endif
'''


def ensure_mxml_compat(component: Path) -> None:
    path = component / "srvinc/MXMLAttributes.h"
    if path.exists():
        current = path.read_text(encoding="utf-8")
        if MXML_COMPAT_MARKER not in current:
            raise SystemExit(f"unexpected existing compatibility header: {path}")
        return
    path.write_text(MXML_COMPAT, encoding="utf-8", newline="\n")


def ensure_case_aliases(component: Path) -> None:
    aliases = {
        "srvinc/ImageConversion.h": "imageconversion.h",
        "srvinc/ICLExifImageFrame.h": "iclexifimageframe.h",
        "srvinc/icl/Icl_UIDS.hrh": "icl/icl_uids.hrh",
    }
    for relative, target in aliases.items():
        path = component / relative
        expected = (
            f"// {CASE_COMPAT_MARKER} target={target}\n"
            f"#include <{target}>\n"
        )
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current != expected:
                raise SystemExit(f"unexpected existing case alias: {path}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8", newline="\n")


def ensure_svg_engine_header(root: Path, component: Path) -> None:
    upstream = root / "epoc32/include/platform/mw/SVGEngineInterfaceImpl.h"
    shadow = component / "srvinc/SVGEngineInterfaceImpl.h"
    source = upstream.read_text(encoding="utf-8")
    old = "IMPORT_C MSvgError* CSvgEngineInterfaceImpl::SaveSvgDom"
    if source.count(old) != 1:
        raise SystemExit(
            "SVG SaveSvgDom qualification anchor changed: "
            f"expected one, found {source.count(old)}"
        )
    expected = source.replace(
        old,
        f"// {SVG_HEADER_COMPAT_MARKER}\n"
        "        IMPORT_C MSvgError* SaveSvgDom",
        1,
    )
    if shadow.exists():
        current = shadow.read_text(encoding="utf-8")
        if current != expected:
            raise SystemExit(f"unexpected existing SVG shadow header: {shadow}")
        return
    shadow.write_text(expected, encoding="utf-8", newline="\n")


def ensure_import_dso_case_aliases(root: Path) -> None:
    libdir = root / "epoc32/release/armv5/lib"
    aliases = {
        "drmhelper.dso": "DRMHelper.dso",
        "ImageConversion.dso": "imageconversion.dso",
        "BitmapTransforms.dso": "bitmaptransforms.dso",
        "SvgEngine.dso": "SVGEngine.dso",
        "CentralRepository.dso": "centralrepository.dso",
        "CenRepNotifHandler.dso": "cenrepnotifhandler.dso",
        "PlatformEnv.dso": "platformenv.dso",
    }
    for destination_name, source_name in aliases.items():
        source = libdir / source_name
        destination = libdir / destination_name
        if not source.is_file():
            raise SystemExit(f"missing source import DSO: {source}")
        if destination.exists():
            if destination.read_bytes() != source.read_bytes():
                raise SystemExit(f"import DSO case alias differs: {destination}")
            continue
        shutil.copy2(source, destination)


def ensure_eabi_frozen_def_alias(component: Path) -> None:
    """Feed GCCE's frozen ABI through Raptor's hard-wired BMARM path."""
    source = component / "EABI/AKNSKINSRVU.DEF"
    destination = component / "BMARM/AKNSKINSRVU.DEF"
    backup = component / "BMARM" / EABI_DEF_BACKUP
    expected = source.read_bytes()
    if not backup.exists():
        backup.write_bytes(destination.read_bytes())
    if backup.read_bytes() == expected:
        raise SystemExit("BMARM backup unexpectedly equals the EABI frozen DEF")
    if destination.read_bytes() != expected:
        destination.write_bytes(expected)
    obsolete_alias = component / "group/HTCLEO_AKNSKINSRV_GCCE.DEF"
    if obsolete_alias.exists():
        if obsolete_alias.read_bytes() != expected:
            raise SystemExit(f"obsolete EABI alias differs: {obsolete_alias}")
        obsolete_alias.unlink()


def transform_core(source: str) -> str:
    if MARKER not in source:
        source = replace_once(
            source,
            '#include "AknsDebug.h"\n',
            '#include "AknsDebug.h"\n' + LOGGER,
            "core logger",
        )

        source = replace_once(
            source,
            '''GLDEF_C TInt StartServer()
    {
    AKNS_TRACE_INFO("CAknsSrv/StartServer ENTERED");
    
    TInt ret( KErrNone );

    // Launch server process
    RProcess server;
    ret = server.Create( KAknSkinSrvExe, KNullDesC,
''',
            '''GLDEF_C TInt StartServer()
    {
    AKNS_TRACE_INFO("CAknsSrv/StartServer ENTERED");
    HtcleoAknSkinLog(0x0000B800u, KErrNone, 0u);
    
    TInt ret( KErrNone );

    // Launch server process
    RProcess server;
    HtcleoAknSkinLog(0x0000B801u, KErrNone, 0u);
    ret = server.Create( KAknSkinSrvExe, KNullDesC,
''',
            "StartServer entry/create",
        )
        source = replace_once(
            source,
            '''        EOwnerThread );

    if( ret != KErrNone )
''',
            '''        EOwnerThread );
    HtcleoAknSkinLog(0x0000B802u, ret, 0u);

    if( ret != KErrNone )
''',
            "StartServer create result",
        )
        source = replace_once(
            source,
            '''\t// Sync server startup
\tTRequestStatus rendezvousStatus;
\tserver.Rendezvous(rendezvousStatus);
\t
\t// Check the rendezvous status before resuming
''',
            '''\t// Sync server startup
\tTRequestStatus rendezvousStatus;
    HtcleoAknSkinLog(0x0000B803u, KErrNone, 0u);
\tserver.Rendezvous(rendezvousStatus);
    HtcleoAknSkinLog(0x0000B804u, rendezvousStatus.Int(),
        rendezvousStatus == KRequestPending ? 1u : 0u);
\t
\t// Check the rendezvous status before resuming
''',
            "StartServer rendezvous registration",
        )
        source = replace_once(
            source,
            '''\t\tAKNS_TRACE_INFO("CAknsSrv/StartServer: resuming server process");
\t\tserver.Resume(); // Resume process
\t\t}
\t
\tAKNS_TRACE_INFO("CAknsSrv/StartServer: wait for server");
\t
\t// Wait for server start (or death)
\tUser::WaitForRequest(rendezvousStatus);
\t
\t// We can't use status alone since it might be 0 in case of a panic
''',
            '''\t\tAKNS_TRACE_INFO("CAknsSrv/StartServer: resuming server process");
        HtcleoAknSkinLog(0x0000B805u, KErrNone, 0u);
\t\tserver.Resume(); // Resume process
        HtcleoAknSkinLog(0x0000B806u, KErrNone, 0u);
\t\t}
\t
\tAKNS_TRACE_INFO("CAknsSrv/StartServer: wait for server");
\t
\t// Wait for server start (or death)
    HtcleoAknSkinLog(0x0000B807u, rendezvousStatus.Int(), 0u);
\tUser::WaitForRequest(rendezvousStatus);
    HtcleoAknSkinLog(0x0000B808u, rendezvousStatus.Int(),
        (TUint32)server.ExitType());
\t
\t// We can't use status alone since it might be 0 in case of a panic
''',
            "StartServer wait",
        )
        source = replace_once(
            source,
            '''\tAKNS_TRACE_INFO("CAknsSrv/StartServer EXIT");
\t
\t// Return the status code
    return rendezvousStatus.Int();
''',
            '''\tAKNS_TRACE_INFO("CAknsSrv/StartServer EXIT");
    HtcleoAknSkinLog(0x0000B809u, rendezvousStatus.Int(), 0u);
\t
\t// Return the status code
    return rendezvousStatus.Int();
''',
            "StartServer return",
        )

        source = replace_once(
            source,
            '''EXPORT_C TInt CAknsSrv::ThreadStart()
    {
    // Rename own thread
    User::RenameThread(KAknSkinSrvName);

    CAknsSrv* server = NULL;
    CTrapCleanup* cleanup = CTrapCleanup::New();
    CActiveScheduler* scheduler = new CAknsSrvScheduler;
''',
            '''EXPORT_C TInt CAknsSrv::ThreadStart()
    {
    HtcleoAknSkinLog(0x0000C800u, KErrNone, 0u);
    // Rename own thread
    User::RenameThread(KAknSkinSrvName);
    HtcleoAknSkinLog(0x0000C801u, KErrNone, 0u);

    CAknsSrv* server = NULL;
    CTrapCleanup* cleanup = CTrapCleanup::New();
    CActiveScheduler* scheduler = new CAknsSrvScheduler;
    HtcleoAknSkinLog(0x0000C802u,
        (cleanup && scheduler) ? KErrNone : KErrNoMemory,
        (cleanup ? 1u : 0u) | (scheduler ? 2u : 0u));
''',
            "ThreadStart entry",
        )
        source = replace_once(
            source,
            '''        CActiveScheduler::Install( scheduler );
        server = CAknsSrv::New( startFailed );   // Adds server in scheduler
        }
''',
            '''        CActiveScheduler::Install( scheduler );
        HtcleoAknSkinLog(0x0000C803u, KErrNone, 0u);
        HtcleoAknSkinLog(0x0000C804u, KErrNone, 0u);
        server = CAknsSrv::New( startFailed );   // Adds server in scheduler
        HtcleoAknSkinLog(0x0000C805u, server ? KErrNone : KErrNoMemory,
            startFailed ? 1u : 0u);
        }
''',
            "ThreadStart New",
        )
        source = replace_once(
            source,
            '''        // Prevent killing skin  server from other processes
        User::SetProcessCritical(User::ESystemCritical);
        User::SetCritical(User::ESystemCritical);

        // Signal that we've started
        RProcess::Rendezvous(KErrNone);

        // Start fielding requests from clients
        CActiveScheduler::Start();
''',
            '''        // Prevent killing skin  server from other processes
        HtcleoAknSkinLog(0x0000C806u, KErrNone, 0u);
        User::SetProcessCritical(User::ESystemCritical);
        User::SetCritical(User::ESystemCritical);

        // Signal that we've started
        HtcleoAknSkinLog(0x0000C807u, KErrNone, 0u);
        RProcess::Rendezvous(KErrNone);
        HtcleoAknSkinLog(0x0000C808u, KErrNone, 0u);

        // Start fielding requests from clients
        HtcleoAknSkinLog(0x0000C809u, KErrNone, 0u);
        CActiveScheduler::Start();
''',
            "ThreadStart rendezvous",
        )

        source = replace_once(
            source,
            '''CAknsSrv* CAknsSrv::New( TBool &aStartFailed )
    {
    AKNS_TRACE_INFO("CAknsSrv::New STARTED");

\taStartFailed = EFalse;
\t
    CAknsSrv* server = new CAknsSrv();
''',
            '''CAknsSrv* CAknsSrv::New( TBool &aStartFailed )
    {
    AKNS_TRACE_INFO("CAknsSrv::New STARTED");
    HtcleoAknSkinLog(0x0000D800u, KErrNone, 0u);

\taStartFailed = EFalse;
\t
    CAknsSrv* server = new CAknsSrv();
    HtcleoAknSkinLog(0x0000D801u,
        server ? KErrNone : KErrNoMemory, server ? 1u : 0u);
''',
            "New entry",
        )
        source = replace_once(
            source,
            '''        if ( server->Start( KAknSkinSrvName ) != KErrNone )
            {
''',
            '''        HtcleoAknSkinLog(0x0000D802u, KErrNone, 0u);
        TInt htcleoStartResult = server->Start( KAknSkinSrvName );
        HtcleoAknSkinLog(0x0000D803u, htcleoStartResult, 0u);
        if ( htcleoStartResult != KErrNone )
            {
''',
            "New server Start",
        )
        source = replace_once(
            source,
            '''    server->iBitmapStore = new CAknsSrvBitmapStore;
    if( !server->iBitmapStore )
''',
            '''    server->iBitmapStore = new CAknsSrvBitmapStore;
    HtcleoAknSkinLog(0x0000D804u,
        server->iBitmapStore ? KErrNone : KErrNoMemory, 0u);
    if( !server->iBitmapStore )
''',
            "New bitmap store",
        )
        source = replace_once(
            source,
            '''    server->iChunkMaintainer =
        new CAknsSrvChunkMaintainer(server->iBitmapStore);
    if( !server->iChunkMaintainer )
''',
            '''    server->iChunkMaintainer =
        new CAknsSrvChunkMaintainer(server->iBitmapStore);
    HtcleoAknSkinLog(0x0000D805u,
        server->iChunkMaintainer ? KErrNone : KErrNoMemory, 0u);
    if( !server->iChunkMaintainer )
''',
            "New chunk maintainer",
        )
        source = replace_once(
            source,
            '''    TInt err = server->iFsSession.Connect();
    AKNS_TRACE_INFO1("CAknsSrv::New RFs connected, ret=%d", err);

    AKNS_TRACE_INFO("CAknsSrv::New server up, connecting shared data");

    TInt errorCode( KErrNone );
    TRAP( errorCode, (server->iSettings=CAknsSrvSettings::NewL(server, server->iFsSession )) );
''',
            '''    HtcleoAknSkinLog(0x0000D806u, KErrNone, 0u);
    TInt err = server->iFsSession.Connect();
    HtcleoAknSkinLog(0x0000D807u, err, 0u);
    AKNS_TRACE_INFO1("CAknsSrv::New RFs connected, ret=%d", err);

    AKNS_TRACE_INFO("CAknsSrv::New server up, connecting shared data");

    TInt errorCode( KErrNone );
    HtcleoAknSkinLog(0x0000D808u, KErrNone, 0u);
    TRAP( errorCode, (server->iSettings=CAknsSrvSettings::NewL(server, server->iFsSession )) );
    HtcleoAknSkinLog(0x0000D809u, errorCode,
        server->iSettings ? 1u : 0u);
''',
            "New RFs/settings",
        )
        source = replace_once(
            source,
            '''    TRAPD( exlListErr, server->iExclusionList =
        CAknsSrvExclusionList::NewL() );
    AKNS_TRACE_INFO1("CAknsSrv::New Exclusion list init, ret=%d", exlListErr);
''',
            '''    HtcleoAknSkinLog(0x0000D80Au, KErrNone, 0u);
    TRAPD( exlListErr, server->iExclusionList =
        CAknsSrvExclusionList::NewL() );
    HtcleoAknSkinLog(0x0000D80Bu, exlListErr,
        server->iExclusionList ? 1u : 0u);
    AKNS_TRACE_INFO1("CAknsSrv::New Exclusion list init, ret=%d", exlListErr);
''',
            "New exclusion create",
        )
        source = replace_once(
            source,
            '''        TRAP( exlListErr, server->iExclusionList->LoadDefaultListFromFileL( server->iFsSession ) );
        AKNS_TRACE_INFO1("CAknsSrv::New Exclusion list loaded, ret=%d", exlListErr);
''',
            '''        TRAP( exlListErr, server->iExclusionList->LoadDefaultListFromFileL( server->iFsSession ) );
        HtcleoAknSkinLog(0x0000D80Cu, exlListErr, 0u);
        AKNS_TRACE_INFO1("CAknsSrv::New Exclusion list loaded, ret=%d", exlListErr);
''',
            "New exclusion load",
        )
        source = replace_once(
            source,
            '''    err = server->iFbsSession.Connect();
    AKNS_TRACE_INFO1("CAknsSrv::New FBS connected, ret=%d", err);

    TRAP( errorCode, server->iSettings->InstallAdditionalWatchersL() );
    AKNS_TRACE_INFO1("CAknsSrv::New Additional watchers installed, ret=%d", errorCode);
    
    server->InitSlidesetEnableAppUid();

    TRAP_IGNORE( server->InitMaxImageSizeL() );
    
    TRAP( errorCode,server->iWallpaperCache = CAknsSrvWallpaperCache::NewL( KAknsWallpaperCacheSize ) );
    
    AKNS_TRACE_INFO("CAknsSrv::New PrepareMergedSkinContentL");
    TRAPD( mergeErr, server->PrepareMergedSkinContentL() );
''',
            '''    HtcleoAknSkinLog(0x0000D80Du, KErrNone, 0u);
    err = server->iFbsSession.Connect();
    HtcleoAknSkinLog(0x0000D80Eu, err, 0u);
    AKNS_TRACE_INFO1("CAknsSrv::New FBS connected, ret=%d", err);

    TRAP( errorCode, server->iSettings->InstallAdditionalWatchersL() );
    HtcleoAknSkinLog(0x0000D80Fu, errorCode, 0u);
    AKNS_TRACE_INFO1("CAknsSrv::New Additional watchers installed, ret=%d", errorCode);
    
    server->InitSlidesetEnableAppUid();
    HtcleoAknSkinLog(0x0000D810u, KErrNone, 0u);

    TRAP_IGNORE( server->InitMaxImageSizeL() );
    HtcleoAknSkinLog(0x0000D811u, KErrNone, 0u);
    
    TRAP( errorCode,server->iWallpaperCache = CAknsSrvWallpaperCache::NewL( KAknsWallpaperCacheSize ) );
    HtcleoAknSkinLog(0x0000D812u, errorCode,
        server->iWallpaperCache ? 1u : 0u);
    
    AKNS_TRACE_INFO("CAknsSrv::New PrepareMergedSkinContentL");
    HtcleoAknSkinLog(0x0000D813u, KErrNone, 0u);
    TRAPD( mergeErr, server->PrepareMergedSkinContentL() );
    HtcleoAknSkinLog(0x0000D814u, mergeErr, 0u);
''',
            "New post-FBS services",
        )
        source = replace_once(
            source,
            '''    TRAP(err, server->iBackupSession = CBaBackupSessionWrapper::NewL() );
    AKNS_TRACE_INFO1("CAknsSrv::New Backup session wrapper created, ret=%d", err);
''',
            '''    HtcleoAknSkinLog(0x0000D815u, KErrNone, 0u);
    TRAP(err, server->iBackupSession = CBaBackupSessionWrapper::NewL() );
    HtcleoAknSkinLog(0x0000D816u, err,
        server->iBackupSession ? 1u : 0u);
    AKNS_TRACE_INFO1("CAknsSrv::New Backup session wrapper created, ret=%d", err);
''',
            "New backup session",
        )
        source = replace_once(
            source,
            '''        TRAP(err, server->iBackupSession->RegisterBackupOperationObserverL(
            *(server->iSettings) ) );
        AKNS_TRACE_INFO1("CAknsSrv::New Backup observer registered, ret=%d", err);
''',
            '''        HtcleoAknSkinLog(0x0000D817u, KErrNone, 0u);
        TRAP(err, server->iBackupSession->RegisterBackupOperationObserverL(
            *(server->iSettings) ) );
        HtcleoAknSkinLog(0x0000D818u, err, 0u);
        AKNS_TRACE_INFO1("CAknsSrv::New Backup observer registered, ret=%d", err);
''',
            "New backup observer",
        )
        source = replace_once(
            source,
            '''    TRAP( err, server->iBackupNotifier = CAknsSrvActiveDataOwner::NewL( server->iFsSession ) );
    AKNS_TRACE_INFO1("CAknsSrv::New Backup notifier created, ret=%d", err);

    AKNS_TRACE_INFO("CAknsSrv::New COMPLETED");

    TRAP(err,server->iInstallObserver = CAknsSrvFileObserver::NewL(server));
    server->iInstallObserver->IssueRequest();
''',
            '''    HtcleoAknSkinLog(0x0000D819u, KErrNone, 0u);
    TRAP( err, server->iBackupNotifier = CAknsSrvActiveDataOwner::NewL( server->iFsSession ) );
    HtcleoAknSkinLog(0x0000D81Au, err,
        server->iBackupNotifier ? 1u : 0u);
    AKNS_TRACE_INFO1("CAknsSrv::New Backup notifier created, ret=%d", err);

    AKNS_TRACE_INFO("CAknsSrv::New COMPLETED");
    HtcleoAknSkinLog(0x0000D81Bu, KErrNone, 0u);

    TRAP(err,server->iInstallObserver = CAknsSrvFileObserver::NewL(server));
    HtcleoAknSkinLog(0x0000D81Cu, err,
        server->iInstallObserver ? 1u : 0u);
    server->iInstallObserver->IssueRequest();
''',
            "New final services",
        )
        source = replace_once(
            source,
            '''    server->iWallpaperType = server->iSettings->WallpaperType();

    
    return server;
''',
            '''    server->iWallpaperType = server->iSettings->WallpaperType();
    HtcleoAknSkinLog(0x0000D81Du, KErrNone, 0u);

    
    return server;
''',
            "New return",
        )
    if FALLBACK_MARKER not in source:
        source = replace_once(
            source,
            '''    HtcleoAknSkinLog(0x0000D814u, mergeErr, 0u);
    if( mergeErr != KErrNone )
        {
        AKNS_TRACE_ERROR1("CAknsSrv::New MERGE ERROR %i", mergeErr);
        server->SetDefaultSkinActive();
        server->RestoreDefaultSDSettings();
        TRAP( mergeErr, server->PrepareMergedSkinContentL() );
        AKNS_TRACE_INFO1("CAknsSrv::New FALLBACK MERGE, ret=%d", mergeErr);
        __ASSERT_DEBUG( mergeErr==KErrNone, User::Panic(
            KAknSkinSrvPanicCategory, EAknsSrvFatalMergeFailure ) );
        }
''',
            '''    HtcleoAknSkinLog(0x0000D814u, mergeErr, 0u);
    if( mergeErr != KErrNone )
        {
        // HTCLEO_AKNSKINSRV_FALLBACK_MERGE_TRACE_V1
        HtcleoAknSkinLog(0x0000D840u, mergeErr, 0u);
        AKNS_TRACE_ERROR1("CAknsSrv::New MERGE ERROR %i", mergeErr);
        HtcleoAknSkinLog(0x0000D841u, KErrNone, 0u);
        server->SetDefaultSkinActive();
        HtcleoAknSkinLog(0x0000D842u, KErrNone, 0u);
        HtcleoAknSkinLog(0x0000D843u, KErrNone, 0u);
        server->RestoreDefaultSDSettings();
        HtcleoAknSkinLog(0x0000D844u, KErrNone, 0u);
        HtcleoAknSkinLog(0x0000D845u, KErrNone, 0u);
        TRAP( mergeErr, server->PrepareMergedSkinContentL() );
        HtcleoAknSkinLog(0x0000D846u, mergeErr, 0u);
        AKNS_TRACE_INFO1("CAknsSrv::New FALLBACK MERGE, ret=%d", mergeErr);
        HtcleoAknSkinLog(0x0000D847u, mergeErr, 0u);
        __ASSERT_DEBUG( mergeErr==KErrNone, User::Panic(
            KAknSkinSrvPanicCategory, EAknsSrvFatalMergeFailure ) );
        HtcleoAknSkinLog(0x0000D848u, mergeErr, 0u);
        }
''',
            "New fallback merge",
        )
    if RESTORE_MARKER not in source:
        source = replace_once(
            source,
            '''void CAknsSrv::RestoreDefaultSDSettings(TBool aExcludeWP)
    {
    AKNS_TRACE_ERROR("CAknsSrv::Skin not found, or other error encountered! Trying to restore default SD settings.");
    if (!iUSBAttached)
        {
        RemoveAutomatedContent();
        }
    iSettings->WriteAllToDefault(aExcludeWP);
    }
''',
            '''void CAknsSrv::RestoreDefaultSDSettings(TBool aExcludeWP)
    {
    // HTCLEO_AKNSKINSRV_RESTORE_DEFAULT_TRACE_V1
    HtcleoAknSkinLog(0x0000D860u, KErrNone,
        (aExcludeWP ? 1u : 0u) | (iUSBAttached ? 2u : 0u) |
        (iBootFinished ? 4u : 0u));
    AKNS_TRACE_ERROR("CAknsSrv::Skin not found, or other error encountered! Trying to restore default SD settings.");
    if (!iUSBAttached)
        {
        HtcleoAknSkinLog(0x0000D861u, KErrNone, 0u);
        RemoveAutomatedContent();
        HtcleoAknSkinLog(0x0000D862u, KErrNone, 0u);
        }
    HtcleoAknSkinLog(0x0000D863u, KErrNone, 0u);
    iSettings->WriteAllToDefault(aExcludeWP);
    HtcleoAknSkinLog(0x0000D864u, KErrNone, 0u);
    HtcleoAknSkinLog(0x0000D865u, KErrNone, 0u);
    }
''',
            "RestoreDefaultSDSettings",
        )
        source = replace_once(
            source,
            '''void CAknsSrv::RemoveAutomatedContent()
    {
    // Remove all automated content
    CheckAndCreateDRMHelper();
    if (!iBootFinished)
        {
        return;
        }
''',
            '''void CAknsSrv::RemoveAutomatedContent()
    {
    HtcleoAknSkinLog(0x0000D870u, KErrNone,
        (iBootFinished ? 1u : 0u) | (iDrmHelper ? 2u : 0u) |
        (iSkinContentUri ? 4u : 0u) | (iIdleWPContentUri ? 8u : 0u) |
        (iSkinContentUri2 ? 16u : 0u) | (iIdleWPContentUri2 ? 32u : 0u));
    // Remove all automated content
    HtcleoAknSkinLog(0x0000D871u, KErrNone, 0u);
    CheckAndCreateDRMHelper();
    HtcleoAknSkinLog(0x0000D872u, KErrNone, iDrmHelper ? 1u : 0u);
    if (!iBootFinished)
        {
        HtcleoAknSkinLog(0x0000D873u, KErrNone, 0u);
        return;
        }
    HtcleoAknSkinLog(0x0000D874u, KErrNone, 0u);
''',
            "RemoveAutomatedContent entry",
        )
        source = replace_once(
            source,
            '''    if (iIdleWPContentUri2)
        {
        iDrmHelper->SetAutomatedType(CDRMHelper::EAutomatedTypeWallpaper);
        iDrmHelper->RemoveAutomated( *iIdleWPContentUri2 );
        delete iIdleWPContentUri2;
        iIdleWPContentUri2 = NULL;
        }
    }
''',
            '''    if (iIdleWPContentUri2)
        {
        iDrmHelper->SetAutomatedType(CDRMHelper::EAutomatedTypeWallpaper);
        iDrmHelper->RemoveAutomated( *iIdleWPContentUri2 );
        delete iIdleWPContentUri2;
        iIdleWPContentUri2 = NULL;
        }
    HtcleoAknSkinLog(0x0000D875u, KErrNone, 0u);
    }
''',
            "RemoveAutomatedContent return",
        )
        source = replace_once(
            source,
            '''void CAknsSrv::CheckAndCreateDRMHelper()
    {
    if( iDrmHelper )
        {
        return;
        }

    AKNS_TRACE_INFO("CAknsSrv::CheckAndCreateDRMHelper No helper, creating");

    TRAPD(helperErr, iDrmHelper = CDRMHelper::NewL() );
    if( helperErr || (!iDrmHelper) )
        {
        AKNS_TRACE_ERROR("CAknsSrv::CheckAndCreateDRMHelper FATAL DRMHELPER FAILURE!");
        User::Panic( KAknSkinSrvPanicCategory, EAknsSrvFatalDRMFailure );
        }

    AKNS_TRACE_INFO("CAknsSrv::CheckAndCreateDRMHelper COMPLETED");
    }
''',
            '''void CAknsSrv::CheckAndCreateDRMHelper()
    {
    HtcleoAknSkinLog(0x0000D880u, KErrNone, iDrmHelper ? 1u : 0u);
    if( iDrmHelper )
        {
        HtcleoAknSkinLog(0x0000D881u, KErrNone, 1u);
        return;
        }

    AKNS_TRACE_INFO("CAknsSrv::CheckAndCreateDRMHelper No helper, creating");

    HtcleoAknSkinLog(0x0000D882u, KErrNone, 0u);
    TRAPD(helperErr, iDrmHelper = CDRMHelper::NewL() );
    HtcleoAknSkinLog(0x0000D883u, helperErr, iDrmHelper ? 1u : 0u);
    if( helperErr || (!iDrmHelper) )
        {
        HtcleoAknSkinLog(0x0000D884u, helperErr, 0u);
        AKNS_TRACE_ERROR("CAknsSrv::CheckAndCreateDRMHelper FATAL DRMHELPER FAILURE!");
        User::Panic( KAknSkinSrvPanicCategory, EAknsSrvFatalDRMFailure );
        }

    AKNS_TRACE_INFO("CAknsSrv::CheckAndCreateDRMHelper COMPLETED");
    HtcleoAknSkinLog(0x0000D885u, KErrNone, 0u);
    }
''',
            "CheckAndCreateDRMHelper",
        )
    if BOOT_DRM_DEFER_MARKER not in source:
        source = replace_once(
            source,
            '''    // Remove all automated content
    HtcleoAknSkinLog(0x0000D871u, KErrNone, 0u);
    CheckAndCreateDRMHelper();
    HtcleoAknSkinLog(0x0000D872u, KErrNone, iDrmHelper ? 1u : 0u);
    if (!iBootFinished)
        {
        HtcleoAknSkinLog(0x0000D873u, KErrNone, 0u);
        return;
        }
    HtcleoAknSkinLog(0x0000D874u, KErrNone, 0u);
''',
            '''    // Remove all automated content
    HtcleoAknSkinLog(0x0000D871u, KErrNone, 0u);
    if (!iBootFinished)
        {
        // HTCLEO_AKNSKINSRV_BOOT_DRM_DEFER_V1
        HtcleoAknSkinLog(0x0000D873u, KErrNone, 0u);
        return;
        }
    HtcleoAknSkinLog(0x0000D874u, KErrNone, 0u);
    CheckAndCreateDRMHelper();
    HtcleoAknSkinLog(0x0000D872u, KErrNone, iDrmHelper ? 1u : 0u);
''',
            "early-boot DRM helper deferral",
        )
    return source


def transform_client(source: str) -> str:
    if "HTCLEO_AKNSKINSRV_CLIENT_TRACE_V1" not in source:
        source = replace_once(
            source,
            '#include "AknsDebug.h"\n',
            '#include "AknsDebug.h"\n'
            '// HTCLEO_AKNSKINSRV_CLIENT_TRACE_V1\n' + CLIENT_DECL,
            "client logger declaration",
        )
        source = replace_once(
            source,
            '''    AKNS_TRACE_INFO("RAknsSrvSession::Connect ENTERED");

    if( iHandle )
''',
            '''    AKNS_TRACE_INFO("RAknsSrvSession::Connect ENTERED");
    HtcleoAknSkinLog(0x0000A800u, KErrNone,
        (iHandle ? 1u : 0u) | (aObserver ? 2u : 0u));

    if( iHandle )
''',
            "Connect entry",
        )
        source = replace_once(
            source,
            '''    iMemberData = new TAknsSrvClientMemberData;
    if (!iMemberData)
''',
            '''    iMemberData = new TAknsSrvClientMemberData;
    HtcleoAknSkinLog(0x0000A801u,
        iMemberData ? KErrNone : KErrNoMemory, 0u);
    if (!iMemberData)
''',
            "Connect allocation",
        )
        source = replace_once(
            source,
            '''    TInt err( KErrNone );

    for ( TInt tries = 0; tries < KAknSkinSrvConnectionTries ; tries++ )
''',
            '''    TInt err( KErrNone );
    HtcleoAknSkinLog(0x0000A802u, KErrNone, 0u);

    for ( TInt tries = 0; tries < KAknSkinSrvConnectionTries ; tries++ )
''',
            "Connect loop",
        )
        source = replace_once(
            source,
            '''        AKNS_TRACE_INFO("RAknsSrvSession::Connect Creating session");
        
        err = CreateSession( KAknSkinSrvName, Version(),
            KAknSkinSrvDefaultMessageSlots );
        
        AKNS_TRACE_INFO1("RAknsSrvSession::Connect Session create ret %d", err);
''',
            '''        AKNS_TRACE_INFO("RAknsSrvSession::Connect Creating session");
        HtcleoAknSkinLog(0x0000A810u, KErrNone, (TUint32)tries);
        
        err = CreateSession( KAknSkinSrvName, Version(),
            KAknSkinSrvDefaultMessageSlots );
        HtcleoAknSkinLog(0x0000A811u, err, (TUint32)tries);
        
        AKNS_TRACE_INFO1("RAknsSrvSession::Connect Session create ret %d", err);
''',
            "Connect CreateSession",
        )
        source = replace_once(
            source,
            '''        AKNS_TRACE_INFO("RAknsSrvSession::Connect Trying to start the server");

        err = StartServer();    // try start a new server

        AKNS_TRACE_INFO1("RAknsSrvSession::Connect StartServer ret %d", err);
''',
            '''        AKNS_TRACE_INFO("RAknsSrvSession::Connect Trying to start the server");
        HtcleoAknSkinLog(0x0000A812u, err, (TUint32)tries);

        err = StartServer();    // try start a new server
        HtcleoAknSkinLog(0x0000A813u, err, (TUint32)tries);

        AKNS_TRACE_INFO1("RAknsSrvSession::Connect StartServer ret %d", err);
''',
            "Connect StartServer",
        )
        source = replace_once(
            source,
            '''    if (err != KErrNone)
        {
''',
            '''    HtcleoAknSkinLog(0x0000A814u, err, 0u);
    if (err != KErrNone)
        {
''',
            "Connect loop result",
        )
        source = replace_once(
            source,
            '''    if( iMemberData->iObserver)
        {
        AKNS_TRACE_INFO("RAknsSrvSession::Connect Observer required");
''',
            '''    if( iMemberData->iObserver)
        {
        AKNS_TRACE_INFO("RAknsSrvSession::Connect Observer required");
        HtcleoAknSkinLog(0x0000A820u, KErrNone, 1u);
''',
            "Connect observer",
        )
        source = replace_once(
            source,
            '''        // Set the notify handler also on the server side;
        SendReceive( EAknSkinSrvSetNotifyHandler, TIpcArgs( iMemberData->iHandler) );
        EventHandled();
        }

    AKNS_TRACE_INFO("RAknsSrvSession::Connect COMPLETED");
''',
            '''        // Set the notify handler also on the server side;
        HtcleoAknSkinLog(0x0000A821u, KErrNone, 0u);
        TInt htcleoNotifyResult = SendReceive( EAknSkinSrvSetNotifyHandler,
            TIpcArgs( iMemberData->iHandler) );
        HtcleoAknSkinLog(0x0000A822u, htcleoNotifyResult, 0u);
        HtcleoAknSkinLog(0x0000A823u, KErrNone, 0u);
        EventHandled();
        HtcleoAknSkinLog(0x0000A824u, KErrNone, 0u);
        }

    AKNS_TRACE_INFO("RAknsSrvSession::Connect COMPLETED");
    HtcleoAknSkinLog(0x0000A82Fu, KErrNone, 0u);
''',
            "Connect notification and return",
        )
    return source


def transform_settings(source: str) -> str:
    if SETTINGS_MARKER not in source:
        source = replace_once(
            source,
            '#include "AknsDebug.h"\n',
            '#include "AknsDebug.h"\n' + SETTINGS_DECL,
            "settings logger declaration",
        )
        source = replace_once(
            source,
            '''void CAknsSrvSettings::WriteAllToDefault(TBool aExcludeWP)
    {
    WriteSkinToDefault();
    if (!aExcludeWP)
        {
        WriteIdleBackgroundToDefault();
        }
    }
''',
            '''void CAknsSrvSettings::WriteAllToDefault(TBool aExcludeWP)
    {
    HtcleoAknSkinLog(0x0000D890u, KErrNone, aExcludeWP ? 1u : 0u);
    HtcleoAknSkinLog(0x0000D891u, KErrNone, 0u);
    WriteSkinToDefault();
    HtcleoAknSkinLog(0x0000D892u, KErrNone, 0u);
    if (!aExcludeWP)
        {
        HtcleoAknSkinLog(0x0000D893u, KErrNone, 0u);
        WriteIdleBackgroundToDefault();
        HtcleoAknSkinLog(0x0000D894u, KErrNone, 0u);
        }
    HtcleoAknSkinLog(0x0000D895u, KErrNone, 0u);
    }
''',
            "WriteAllToDefault",
        )
        source = replace_once(
            source,
            '''void CAknsSrvSettings::WriteSkinToDefault()
    {
    TAknsPkgID defaultSkin = DefaultSkinPID();
    iActiveSkinPID.Set( defaultSkin );

    TAknsPkgIDBuf buf;
    defaultSkin.CopyToDes( buf );
    iSkinsRepository->Set(KPslnActiveSkinUid, buf);
    // Active skin location
    iSkinsRepository->Set(KPslnActiveSkinLocation, 0);
    }
''',
            '''void CAknsSrvSettings::WriteSkinToDefault()
    {
    HtcleoAknSkinLog(0x0000D8A0u, KErrNone, 0u);
    TAknsPkgID defaultSkin = DefaultSkinPID();
    HtcleoAknSkinLog(0x0000D8A1u, KErrNone, 0u);
    iActiveSkinPID.Set( defaultSkin );
    HtcleoAknSkinLog(0x0000D8A2u, KErrNone, 0u);

    TAknsPkgIDBuf buf;
    defaultSkin.CopyToDes( buf );
    HtcleoAknSkinLog(0x0000D8A3u, KErrNone, 0u);
    HtcleoAknSkinLog(0x0000D8A4u, KErrNone, 0u);
    iSkinsRepository->Set(KPslnActiveSkinUid, buf);
    HtcleoAknSkinLog(0x0000D8A5u, KErrNone, 0u);
    // Active skin location
    HtcleoAknSkinLog(0x0000D8A6u, KErrNone, 0u);
    iSkinsRepository->Set(KPslnActiveSkinLocation, 0);
    HtcleoAknSkinLog(0x0000D8A7u, KErrNone, 0u);
    }
''',
            "WriteSkinToDefault",
        )
        source = replace_once(
            source,
            '''void CAknsSrvSettings::WriteIdleBackgroundToDefault()
    {
    TAknsPkgIDBuf buf;
    DefaultSkinPID().CopyToDes(buf);
    iSkinsRepository->Set(KPslnIdleBackgroundImageUid, buf);
    iSkinsRepository->Set(KPslnIdleBackgroundImagePath, KNullDesC());
    iSkinsRepository->Set(KPslnWallpaperType, 0);
    }
''',
            '''void CAknsSrvSettings::WriteIdleBackgroundToDefault()
    {
    HtcleoAknSkinLog(0x0000D8B0u, KErrNone, 0u);
    TAknsPkgIDBuf buf;
    DefaultSkinPID().CopyToDes(buf);
    HtcleoAknSkinLog(0x0000D8B1u, KErrNone, 0u);
    HtcleoAknSkinLog(0x0000D8B2u, KErrNone, 0u);
    iSkinsRepository->Set(KPslnIdleBackgroundImageUid, buf);
    HtcleoAknSkinLog(0x0000D8B3u, KErrNone, 0u);
    HtcleoAknSkinLog(0x0000D8B4u, KErrNone, 0u);
    iSkinsRepository->Set(KPslnIdleBackgroundImagePath, KNullDesC());
    HtcleoAknSkinLog(0x0000D8B5u, KErrNone, 0u);
    HtcleoAknSkinLog(0x0000D8B6u, KErrNone, 0u);
    iSkinsRepository->Set(KPslnWallpaperType, 0);
    HtcleoAknSkinLog(0x0000D8B7u, KErrNone, 0u);
    HtcleoAknSkinLog(0x0000D8B8u, KErrNone, 0u);
    }
''',
            "WriteIdleBackgroundToDefault",
        )
    return source


def transform_mmp(source: str) -> str:
    if MACRO not in source:
        source = replace_once(
            source,
            "VENDORID        VID_DEFAULT\n",
            "VENDORID        VID_DEFAULT\n\n"
            "MACRO           __HTCLEO_AKNSKINSRV_DURABLE_LOG__\n",
            "AknSkinSrv macro",
        )
    compatibility_note = (
        f"// {EABI_DEF_MARKER}\n"
        "// Raptor hard-wires this legacy target to BMARM even for GCCE.\n"
        "// The build transform preserves that ARMCC DEF as a backup and\n"
        "// aliases this selected path to the released 199-entry EABI DEF.\n"
    )
    if EABI_DEF_MARKER not in source:
        source = replace_once(
            source,
            "UID             0x1000008D 0x10005A35\n",
            "UID             0x1000008D 0x10005A35\n\n"
            + compatibility_note,
            "AknSkinSrv EABI frozen DEF",
        )
    else:
        start = source.index(f"// {EABI_DEF_MARKER}")
        end = source.index("\n", source.index("DEFFILE", start)) + 1 \
            if "DEFFILE" in source[start:] else start
        if end != start:
            source = source[:start] + compatibility_note + source[end:]
    return source


def verify(root: Path) -> None:
    component = root / "sf/mw/uiresources/skins/AknSkins"
    core = (component / "srvsrc/AknsSrv.cpp").read_text(encoding="utf-8")
    client = (component / "srvsrc/AknsSrvClient.cpp").read_text(encoding="utf-8")
    settings = (component / "srvsrc/AknsSrvSettings.cpp").read_text(
        encoding="utf-8"
    )
    mmp = (component / "group/AknSkinSrv.mmp").read_text(encoding="utf-8")
    mxml_compat = (component / "srvinc/MXMLAttributes.h").read_text(
        encoding="utf-8"
    )
    case_aliases = {
        "ImageConversion": (
            component / "srvinc/ImageConversion.h",
            "imageconversion.h",
        ),
        "ICLExifImageFrame": (
            component / "srvinc/ICLExifImageFrame.h",
            "iclexifimageframe.h",
        ),
        "Icl_UIDS": (
            component / "srvinc/icl/Icl_UIDS.hrh",
            "icl/icl_uids.hrh",
        ),
    }
    svg_shadow = (component / "srvinc/SVGEngineInterfaceImpl.h").read_text(
        encoding="utf-8"
    )
    eabi_def = (component / "EABI/AKNSKINSRVU.DEF").read_bytes()
    eabi_alias = (component / "BMARM/AKNSKINSRVU.DEF").read_bytes()
    armcc_backup = (component / "BMARM" / EABI_DEF_BACKUP).read_bytes()

    checks = {
        "core marker": core.count(MARKER) == 1,
        "fallback merge marker": core.count(FALLBACK_MARKER) == 1,
        "restore default marker": core.count(RESTORE_MARKER) == 1,
        "early-boot DRM helper deferral": (
            core.count(BOOT_DRM_DEFER_MARKER) == 1
            and core.index("if (!iBootFinished)",
                           core.index(BOOT_DRM_DEFER_MARKER) - 256)
            < core.index("CheckAndCreateDRMHelper();",
                         core.index(BOOT_DRM_DEFER_MARKER))
        ),
        "settings default marker": settings.count(SETTINGS_MARKER) == 1,
        "capacity marker": core.count(CAPACITY_MARKER) == 1,
        "log path": core.count("C:\\\\Symbian3\\\\SKINLOG.TXT") == 1,
        "client marker": client.count("HTCLEO_AKNSKINSRV_CLIENT_TRACE_V1") == 1,
        "MMP macro": mmp.count(MACRO) == 1,
        "EABI frozen DEF": (
            mmp.count(EABI_DEF_MARKER) == 1
            and "DEFFILE" not in mmp
            and eabi_alias == eabi_def
            and armcc_backup != eabi_def
        ),
        "efsrv library": mmp.lower().count("library         efsrv.lib") == 1,
        "MXML forward declaration": (
            mxml_compat.count(MXML_COMPAT_MARKER) == 1
            and mxml_compat.count("class MXMLAttributes;") == 1
        ),
        "SVG SaveSvgDom qualification": (
            svg_shadow.count(SVG_HEADER_COMPAT_MARKER) == 1
            and "CSvgEngineInterfaceImpl::SaveSvgDom" not in svg_shadow
            and svg_shadow.count("IMPORT_C MSvgError* SaveSvgDom") == 1
        ),
    }
    for name, (path, target) in case_aliases.items():
        alias = path.read_text(encoding="utf-8")
        checks[f"case alias {name}"] = (
            alias.count(CASE_COMPAT_MARKER) == 1
            and alias.count(f"#include <{target}>") == 1
        )
    stages = {
        "client": ["A800", "A801", "A802", "A810", "A811", "A812", "A813",
                   "A814", "A820", "A821", "A822", "A823", "A824", "A82F"],
        "launcher": ["B800", "B801", "B802", "B803", "B804", "B805", "B806",
                     "B807", "B808", "B809"],
        "thread": ["C800", "C801", "C802", "C803", "C804", "C805", "C806",
                   "C807", "C808", "C809"],
        "server": [f"D8{i:02X}" for i in range(0x00, 0x1E)],
        "fallback": [f"D8{i:02X}" for i in range(0x40, 0x49)],
        "restore": ([f"D8{i:02X}" for i in range(0x60, 0x66)]
                    + [f"D8{i:02X}" for i in range(0x70, 0x76)]
                    + [f"D8{i:02X}" for i in range(0x80, 0x86)]),
        "settings": ([f"D8{i:02X}" for i in range(0x90, 0x96)]
                     + [f"D8A{i:X}" for i in range(0x00, 0x08)]
                     + [f"D8B{i:X}" for i in range(0x00, 0x09)]),
    }
    for group, values in stages.items():
        combined = {
            "client": client,
            "settings": settings,
        }.get(group, core)
        for stage in values:
            checks[f"{group} {stage}"] = combined.count(f"0x0000{stage}u") == 1

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/uiresources/skins/AknSkins"
    core_path = component / "srvsrc/AknsSrv.cpp"
    client_path = component / "srvsrc/AknsSrvClient.cpp"
    settings_path = component / "srvsrc/AknsSrvSettings.cpp"
    mmp_path = component / "group/AknSkinSrv.mmp"

    ensure_mxml_compat(component)
    ensure_case_aliases(component)
    ensure_svg_engine_header(args.root, component)
    ensure_import_dso_case_aliases(args.root)
    ensure_eabi_frozen_def_alias(component)

    core = transform_core(core_path.read_text(encoding="utf-8"))
    client = transform_client(client_path.read_text(encoding="utf-8"))
    settings = transform_settings(settings_path.read_text(encoding="utf-8"))
    mmp = transform_mmp(mmp_path.read_text(encoding="utf-8"))
    core_path.write_text(core, encoding="utf-8", newline="\n")
    client_path.write_text(client, encoding="utf-8", newline="\n")
    settings_path.write_text(settings, encoding="utf-8", newline="\n")
    mmp_path.write_text(mmp, encoding="utf-8", newline="\n")
    verify(args.root)
    print("HTCLEO_AKNSKINSRV_DURABLE_LOG=installed "
          "stages=A800-D81D,D840-D8B8 boot_drm_defer=1")


if __name__ == "__main__":
    main()
