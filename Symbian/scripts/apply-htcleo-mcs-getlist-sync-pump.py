#!/usr/bin/env python3
"""Synchronously pump MatrixMenu's real MCS GetList before LIW callback return."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER_V1 = "HTCLEO_MCS_GETLIST_SYNC_PUMP_V1"
MARKER_V2 = "HTCLEO_MCS_GETLIST_SYNC_PUMP_V2"
MARKER_V3 = "HTCLEO_MCS_GETLIST_SYNC_PUMP_V3"
MARKER_V4 = "HTCLEO_MCS_GETLIST_SYNC_PUMP_V4"
MARKER_V5 = "HTCLEO_MCS_GETLIST_SYNC_PUMP_V5"
MARKER = "HTCLEO_MCS_GETLIST_SYNC_PUMP_V6"
COUNT_MARKER = "HTCLEO_MCS_GETLIST_RETURN_COUNT_PROPERTY_V1"
ICON_MARKER = "HTCLEO_MCS_GETLIST_ICON_ITEM_FAILOPEN_V1"
ICON_RESET_MARKER = "HTCLEO_MCS_GETLIST_ICON_ERROR_RESET_V1"
OUTER_MARKER = "HTCLEO_MCS_GETLIST_OUTER_ERROR_RAW_RESULT_V1"
SYNC_RESULT_MARKER = "HTCLEO_MCS_GETLIST_SYNC_RESULT_PROPERTY_V1"


INCLUDE_ANCHOR = '#include "mcsbitmapbuffer.h"\n'
INCLUDE_PATCHED = '#include "mcsbitmapbuffer.h"\n#include <e32property.h>\n'


OLD_SPACES = r'''        CActiveScheduler::Add ( this );
        ActivateRequest( KErrNone );'''


OLD_TABS = "\t\tCActiveScheduler::Add ( this );\n\t\tActivateRequest( KErrNone );"


NEW = r'''        // HTCLEO_MCS_GETLIST_SYNC_PUMP_V6
        // The HTCLEO early UI scheduler does not dispatch this provider AO.
        // For MatrixMenu only, perform the existing real synchronous MCS IPC,
        // then use the stock icon conversion and LIW callback path.  The
        // notifier removes and deletes this object, so this is a strict tail.
        if (RProcess().SecureId().iId == 0x101F4CD2u)
            {
            TInt htcleoGetListResult = KErrNone;
            TRAP(htcleoGetListResult, GetListL());
            // HTCLEO_MCS_GETLIST_SYNC_RESULT_PROPERTY_V1
            const TUid htcleoSyncCategory = { 0x101F4CD2 };
            const TUint htcleoSyncErrorKey = 0x7F4D4303u;
            RProperty::Set(htcleoSyncCategory, htcleoSyncErrorKey,
                htcleoGetListResult);
            NotifyRequestResultL(htcleoGetListResult);
            return;
            }
        CActiveScheduler::Add ( this );
        ActivateRequest( KErrNone );'''


COUNT_ANCHOR = r'''   	const CLiwList* resultTemp = returnVal->Value().AsList();
		AppendIconsL( resultTemp , resultList );'''


COUNT_PATCHED = r'''   	const CLiwList* resultTemp = returnVal->Value().AsList();

        // HTCLEO_MCS_GETLIST_RETURN_COUNT_PROPERTY_V1
        // Publish the exact real list length before icon conversion.  HN may
        // use it only as a bounded fallback if LIW later loses ReturnValue's
        // path metadata; the list itself is never fabricated or replaced.
        if (RProcess().SecureId().iId == 0x101F4CD2u && resultTemp)
            {
            const TUid htcleoCountCategory = { 0x101F4CD2 };
            const TUint htcleoCountKey = 0x7F4D4302u;
            const TSecurityPolicy htcleoCountPolicy(
                TSecurityPolicy::EAlwaysPass);
            TInt htcleoCountResult = RProperty::Define(
                htcleoCountCategory, htcleoCountKey, RProperty::EInt,
                htcleoCountPolicy, htcleoCountPolicy);
            if (htcleoCountResult == KErrAlreadyExists)
                {
                htcleoCountResult = KErrNone;
                }
            if (htcleoCountResult == KErrNone)
                {
                RProperty::Set(htcleoCountCategory, htcleoCountKey,
                    resultTemp->Count());
                }
            }
		AppendIconsL( resultTemp , resultList );'''


# Match only the unique statement, independent of tabs in the PDK source.
COUNT_ANCHOR = "const CLiwList* resultTemp = returnVal->Value().AsList();"
COUNT_PATCHED = r'''const CLiwList* resultTemp = returnVal->Value().AsList();

        // HTCLEO_MCS_GETLIST_RETURN_COUNT_PROPERTY_V1
        // Publish the exact real list length before icon conversion.  HN may
        // use it only as a bounded fallback if LIW later loses ReturnValue's
        // path metadata; the list itself is never fabricated or replaced.
        if (RProcess().SecureId().iId == 0x101F4CD2u && resultTemp)
            {
            const TUid htcleoCountCategory = { 0x101F4CD2 };
            const TUint htcleoCountKey = 0x7F4D4302u;
            const TSecurityPolicy htcleoCountPolicy(
                TSecurityPolicy::EAlwaysPass);
            TInt htcleoCountResult = RProperty::Define(
                htcleoCountCategory, htcleoCountKey, RProperty::EInt,
                htcleoCountPolicy, htcleoCountPolicy);
            if (htcleoCountResult == KErrAlreadyExists)
                {
                htcleoCountResult = KErrNone;
                }
            if (htcleoCountResult == KErrNone)
                {
                RProperty::Set(htcleoCountCategory, htcleoCountKey,
                    resultTemp->Count());
                }
            }'''


def install(text: str) -> str:
    if MARKER_V1 in text and MARKER_V2 not in text:
        text = text.replace(MARKER_V1, MARKER_V2)
    if MARKER_V2 in text and MARKER_V3 not in text:
        text = text.replace(MARKER_V2, MARKER_V3)
    if MARKER_V3 in text and MARKER_V4 not in text:
        text = text.replace(MARKER_V3, MARKER_V4)
    if MARKER_V4 in text and MARKER_V5 not in text:
        text = text.replace(MARKER_V4, MARKER_V5)
    if MARKER_V5 in text and MARKER not in text:
        text = text.replace(MARKER_V5, MARKER)
    if MARKER not in text:
        matches = [old for old in (OLD_SPACES, OLD_TABS) if text.count(old)]
        if len(matches) != 1 or text.count(matches[0]) != 1:
            raise SystemExit(
                "MCS GetList sync pump: expected one AO activation, "
                f"found {sum(text.count(old) for old in (OLD_SPACES, OLD_TABS))}"
            )
        text = text.replace(matches[0], NEW, 1)
    if COUNT_MARKER in text:
        if text.count(COUNT_PATCHED) != 1:
            raise SystemExit("MCS GetList count retirement: block mismatch")
        text = text.replace(COUNT_PATCHED, COUNT_ANCHOR, 1)
        if text.count("#include <e32property.h>\n") != 1:
            raise SystemExit("MCS GetList count retirement: include mismatch")
        text = text.replace("#include <e32property.h>\n", "", 1)
    if "#include <e32property.h>" not in text:
        if text.count(INCLUDE_ANCHOR) != 1:
            raise SystemExit("MCS icon fail-open: include anchor missing")
        text = text.replace(INCLUDE_ANCHOR, INCLUDE_PATCHED, 1)
    if ICON_RESET_MARKER not in text:
        reset_anchor = "RDesReadStream stream( iSerializedOutputList );"
        reset_patch = r'''// HTCLEO_MCS_GETLIST_ICON_ERROR_RESET_V1
    if (RProcess().SecureId().iId == 0x101F4CD2u)
        {
        const TUid htcleoIconCategory = { 0x101F4CD2 };
        const TUint htcleoIconErrorKey = 0x7F4D4303u;
        RProperty::Set(htcleoIconCategory, htcleoIconErrorKey, KErrNone);
        }
    RDesReadStream stream( iSerializedOutputList );'''
        if text.count(reset_anchor) != 1:
            raise SystemExit("MCS icon fail-open: reset anchor missing")
        text = text.replace(reset_anchor, reset_patch, 1)
    if ICON_MARKER not in text:
        load_anchor = "        TRAP_IGNORE( icon = McsIconUtility::GetItemIconL( map )  );"
        load_patch = r'''        // HTCLEO_MCS_GETLIST_ICON_ITEM_FAILOPEN_V1
        TInt htcleoIconLoadResult = KErrNone;
        if (RProcess().SecureId().iId == 0x101F4CD2u)
            {
            TRAP(htcleoIconLoadResult,
                icon = McsIconUtility::GetItemIconL( map ));
            if (htcleoIconLoadResult != KErrNone)
                {
                const TUid htcleoIconCategory = { 0x101F4CD2 };
                const TUint htcleoIconErrorKey = 0x7F4D4303u;
                RProperty::Set(htcleoIconCategory, htcleoIconErrorKey,
                    htcleoIconLoadResult);
                }
            }
        else
            {
            TRAP_IGNORE(icon = McsIconUtility::GetItemIconL( map ));
            }'''
        if text.count(load_anchor) != 1:
            raise SystemExit("MCS icon fail-open: load anchor missing")
        text = text.replace(load_anchor, load_patch, 1)

        function_start = text.index("void CMCSGetListImpl::AppendIconL")
        block_start = text.index("        if ( icon )", function_start)
        block_end = text.index("\n\t\tCleanupStack::PopAndDestroy( map );", block_start)
        old_block = text[block_start:block_end]
        new_block = r'''        if ( icon )
               {
               CleanupStack::PushL( icon );
               if (RProcess().SecureId().iId == 0x101F4CD2u)
                   {
                   TInt htcleoBitmapResult = KErrNone;
                   TRAP(htcleoBitmapResult,
                       GetMaskAndBitmapL( *aMap, icon ));
                   if (htcleoBitmapResult != KErrNone)
                       {
                       const TUid htcleoIconCategory = { 0x101F4CD2 };
                       const TUint htcleoIconErrorKey = 0x7F4D4303u;
                       RProperty::Set(htcleoIconCategory,
                           htcleoIconErrorKey, htcleoBitmapResult);
                       }
                   }
               else
                   {
                   GetMaskAndBitmapL( *aMap, icon );
                   }
               CleanupStack::PopAndDestroy( icon );
               }
        else if (RProcess().SecureId().iId == 0x101F4CD2u &&
                 htcleoIconLoadResult == KErrNone)
               {
               const TUid htcleoIconCategory = { 0x101F4CD2 };
               const TUint htcleoIconErrorKey = 0x7F4D4303u;
               RProperty::Set(htcleoIconCategory, htcleoIconErrorKey,
                   KErrNotFound);
               }'''
        text = text[:block_start] + new_block + text[block_end:]
    if OUTER_MARKER not in text:
        outer_patch = r'''        if ( aReason == KErrNone )
            {
            // HTCLEO_MCS_GETLIST_OUTER_ERROR_RAW_RESULT_V1
            TInt htcleoAppendResult = KErrNone;
            TRAP(htcleoAppendResult,
                HandleAppendIconsL( outParamList ));
            if (RProcess().SecureId().iId == 0x101F4CD2u)
                {
                if (htcleoAppendResult != KErrNone)
                    {
                    const TUid htcleoIconCategory = { 0x101F4CD2 };
                    const TUint htcleoIconErrorKey = 0x7F4D4303u;
                    RProperty::Set(htcleoIconCategory,
                        htcleoIconErrorKey, htcleoAppendResult);
                    }
                // InternalizeL may already have populated the real raw
                // ReturnValue before later icon conversion left.  Preserve
                // only that existing data; never fabricate a parameter.
                aReason = (htcleoAppendResult != KErrNone &&
                    outParamList->Count() > 0) ? KErrNone :
                    htcleoAppendResult;
                }
            else
                {
                aReason = htcleoAppendResult;
                }
            }'''
        outer_call = "TRAP(aReason, HandleAppendIconsL( outParamList ));"
        if text.count(outer_call) != 1:
            raise SystemExit("MCS icon fail-open: outer call mismatch")
        notify_start = text.index("void CMCSGetListImpl::NotifyRequestResultL")
        call_at = text.index(outer_call, notify_start)
        outer_start = text.rfind(
            "if ( aReason == KErrNone )", notify_start, call_at
        )
        outer_end = text.index("}", call_at) + 1
        if outer_start < notify_start or outer_end <= call_at:
            raise SystemExit("MCS icon fail-open: outer block boundary missing")
        # Preserve the source indentation immediately before the if token.
        line_start = text.rfind("\n", notify_start, outer_start) + 1
        text = text[:line_start] + outer_patch + text[outer_end:]
    if SYNC_RESULT_MARKER not in text:
        sync_anchor = r'''            TRAP(htcleoGetListResult, GetListL());
            NotifyRequestResultL(htcleoGetListResult);'''
        sync_patch = r'''            TRAP(htcleoGetListResult, GetListL());
            // HTCLEO_MCS_GETLIST_SYNC_RESULT_PROPERTY_V1
            const TUid htcleoSyncCategory = { 0x101F4CD2 };
            const TUint htcleoSyncErrorKey = 0x7F4D4303u;
            RProperty::Set(htcleoSyncCategory, htcleoSyncErrorKey,
                htcleoGetListResult);
            NotifyRequestResultL(htcleoGetListResult);'''
        if text.count(sync_anchor) != 1:
            raise SystemExit("MCS GetList sync result: anchor missing")
        text = text.replace(sync_anchor, sync_patch, 1)
    return text


def verify(text: str) -> None:
    marker_at = text.find(MARKER)
    notify_at = text.find("NotifyRequestResultL(htcleoGetListResult);", marker_at)
    return_at = text.find("return;", notify_at)
    stock_add_at = text.find("CActiveScheduler::Add ( this );", return_at)
    checks = {
        "marker": text.count(MARKER) == 1,
        "old markers absent": (
            MARKER_V1 not in text
            and MARKER_V2 not in text
            and MARKER_V3 not in text
            and MARKER_V4 not in text
            and MARKER_V5 not in text
        ),
        "MatrixMenu scoped": text.count("0x101F4CD2u") == 6,
        "real synchronous overload": (
            text.count("TRAP(htcleoGetListResult, GetListL());") == 1
        ),
        "stock callback tail": (
            text.count("NotifyRequestResultL(htcleoGetListResult);") == 1
            and marker_at < notify_at < return_at < stock_add_at
        ),
        "other clients stock": (
            text.count("CActiveScheduler::Add ( this );") == 1
            and text.count("ActivateRequest( KErrNone );") == 1
        ),
        "real IPC retained": (
            text.count(
                "iMCS.GetListL( iSerializedInputList, iSerializedOutputList );"
            )
            == 1
        ),
        "callback count property retired": (
            COUNT_MARKER not in text
            and "0x7F4D4302u" not in text
            and "RProperty::Define(" not in text
        ),
        "per-item icon fail-open": (
            text.count(ICON_MARKER) == 1
            and text.count(ICON_RESET_MARKER) == 1
            and text.count("0x7F4D4303u") == 6
            and text.count("TRAP(htcleoIconLoadResult") == 1
            and text.count("TRAP(htcleoBitmapResult") == 1
            and text.count("#include <e32property.h>") == 1
        ),
        "outer error and raw result preservation": (
            text.count(OUTER_MARKER) == 1
            and text.count("TRAP(htcleoAppendResult") == 1
            and text.count("outParamList->Count() > 0") == 1
            and text.count("htcleoIconErrorKey, htcleoAppendResult);") == 1
            and text.count("aReason = htcleoAppendResult;") == 1
        ),
        "sync result property": (
            text.count(SYNC_RESULT_MARKER) == 1
            and text.count("htcleoSyncErrorKey = 0x7F4D4303u") == 1
            and text.count("htcleoGetListResult);") == 2
        ),
        "no fake or wait": all(
            token not in text
            for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS GetList sync-pump verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/homescreensrv/homescreensrv_plat/sapi_menucontent/mcsservice/src/mcsgetlistimpl.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MCS GetList implementation: {path}")
    text = path.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MCS_GETLIST_SYNC_PUMP="
        "matrixmenu-real-ipc-per-item-icon-failopen-outer-error-"
        "raw-result-preserve-sync-result-property-safe-tail"
    )


if __name__ == "__main__":
    main()
