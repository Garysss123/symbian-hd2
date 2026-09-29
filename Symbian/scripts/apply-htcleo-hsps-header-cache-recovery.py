#!/usr/bin/env python3
"""804: release HSPS header-update pending state on existing Leave paths."""
import argparse
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
REL=Path('sf/mw/homescreensrv/homescreenpluginsrv/hspsmanager/src')
NAME='hspsthemeserver.cpp'
BASE_SHA='3c3615acdfc5f006e347272533966d0bd6121e94d6af382e9f82ea31b3217282'
OLD="void ChspsThemeServer::UpdateHeaderListCacheL()\n    {\n    if ( iHeaderListPending )\n        {\n#ifdef HSPS_LOG_ACTIVE        \n        iLogBus->LogText( _L( \"ChspsThemeServer::UpdateHeaderListCacheL(): already updating the cache\" ) );\n#endif                \n        }\n    else\n        {\n        iHeaderListPending = ETrue;\n        \n#ifdef _hsps_PERFORMANCE_TEST_\n        TTime start_time;        \n        start_time = ChspsTimeMon::StartTiming(_L(\"timer started\")); \n#endif    \n        \n        // Get headers from the Plug-in Repository\n        CArrayPtrSeg<ChspsODT>* headerList =  new (ELeave)CArrayPtrSeg<ChspsODT>(KHeaderListGranularity);\n        CleanupStack::PushL( headerList );\n                \n        // Reset search mask\n        iCacheMask->SetRootUid( 0 );\n        iCacheMask->SetProviderUid( 0 );\n        iCacheMask->SetThemeUid( 0 );\n        \n        TInt err = DoUpdateHeaderListCache( *headerList );\n        User::LeaveIfError( err );\n                                \n        if ( headerList->Count() > 0 )\n            {\n            // Destroys all objects whose pointers form the elements of the array, \n            // before resetting the array.\n            iHeaderListCache->ResetAndDestroy();\n                        \n            TInt count = headerList->Count() - 1;\n            for (TInt i = count; i >= 0; --i)\n                {\n                // Update the cache array (ownership is transferred)\n                TRAP( err, iHeaderListCache->InsertL(0, headerList->At(i)) );\n                                                   \n                // If allocation failed\n                if ( err )\n                    {\n                    break;\n                    }\n                \n                // Complete the ownership transfer\n                headerList->Delete(i);                        \n                }\n            }\n\n        // Destroys all objects whose pointers form the elements of the array, \n        // before resetting the array.\n        headerList->ResetAndDestroy();\n        CleanupStack::PopAndDestroy( headerList );\n\n        // calculating service time\n#ifdef _hsps_PERFORMANCE_TEST_        \n        ChspsTimeMon::StopTiming( start_time, _L( \"ChspsThemeServer::UpdateHeaderListCache(): - timer stopped\" ) );\n#endif       \n                        \n        iHeaderListPending = EFalse;\n        }      \n    }\n"
NEW='#include "htcleohspsheadercache.inl"\n'

def transform(text,restore=False):
    if NEW in text:
        if text.count(NEW)!=1:raise ValueError('duplicate header-cache overlay')
        text=text.replace(NEW,OLD,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SHA:
        raise ValueError('header-cache recovery requires exact801 server source')
    if text.count(OLD)!=1:raise ValueError('native header-cache method drift')
    return text if restore else text.replace(OLD,NEW,1)

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL/NAME;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if not a.restore and (transform(new)!=new or transform(new,True)!=transform(old,True)):
        raise ValueError('header-cache inverse/idempotence failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    if not a.restore:
        asset=HERE.parent/'hd2/qsd8250-native-bsp/diagnostics/htcleohspsheadercache.inl'
        path.with_name(asset.name).write_bytes(asset.read_bytes())
    print('HTCLEO_HSPS_HEADER_CACHE='+('restored' if a.restore else 'native-load-error-preserved-leave-safe-pending-guard-first12'))

if __name__=='__main__':main()
