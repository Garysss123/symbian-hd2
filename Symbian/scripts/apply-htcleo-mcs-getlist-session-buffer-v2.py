#!/usr/bin/env python3
"""Make the GetList Size/Data payload session-owned for every client."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD_MARKER = "HTCLEO_MCS_GETLIST_SESSION_BUFFER_V1"
MARKER = "HTCLEO_MCS_GETLIST_SESSION_BUFFER_V2"
ATOMIC_MARKER = "HTCLEO_MCS_GETLIST_ATOMIC_TRANSFER_V1"


SIZE_BLOCK = r'''        case EMenuGetListSize:
            {
            __ASSERT_ALWAYS( iSharedEng, PanicClientL( aMessage ) );
            // HTCLEO_MCS_GETLIST_SESSION_BUFFER_V2
            HtcleoMcsLog(0x4D430170u, KErrNone,
                (TUint32)aMessage.SecureId().iId);
            TInt deslen = aMessage.GetDesLength( KGetListDescriptorPos );
            HBufC8* buffer = HBufC8::NewLC( deslen );
            TPtr8 tempDes = buffer->Des( );
            aMessage.Read( KGetListDescriptorPos, tempDes );
            TInt size = iSharedEng->GetListSizeL( *buffer );
            const TDesC8& htcleoSharedOutput =
                iSharedEng->GetListDataL();
            HtcleoMcsLog(0x4D430171u, size,
                (TUint32)htcleoSharedOutput.Length());
            iHtcleoGetListOutput.Close();
            iHtcleoGetListOutput.CreateL(htcleoSharedOutput.Length());
            iHtcleoGetListOutput.Copy(htcleoSharedOutput);
            iSharedEng->CloseOutputBuffer();
            size = iHtcleoGetListOutput.Length();
            HtcleoMcsLog(0x4D430172u, size,
                (TUint32)iHtcleoGetListOutput.MaxLength());
            TPckg<TInt> sizeDes( size );
            aMessage.WriteL( KGetListReturnPos, sizeDes );
            CleanupStack::PopAndDestroy( buffer );
            break;
            }   

'''


DATA_BLOCK = r'''        case EMenuGetListData:
            {
            __ASSERT_ALWAYS( iSharedEng, PanicClientL( aMessage ) );
            HtcleoMcsLog(0x4D430173u,
                iHtcleoGetListOutput.Length(),
                (TUint32)aMessage.SecureId().iId);
            if (iHtcleoGetListOutput.MaxLength() > 0)
                {
                HtcleoMcsLog(0x4D430174u, KErrNone,
                    (TUint32)iHtcleoGetListOutput.Length());
                aMessage.WriteL( KGetListDescriptorPos,
                    iHtcleoGetListOutput );
                iHtcleoGetListOutput.Close();
                }
            else
                {
                const TDesC8& htcleoFallbackOutput =
                    iSharedEng->GetListDataL();
                HtcleoMcsLog(0x4D430175u, KErrNotReady,
                    (TUint32)htcleoFallbackOutput.Length());
                aMessage.WriteL( KGetListDescriptorPos,
                    htcleoFallbackOutput );
                iSharedEng->CloseOutputBuffer();
                }
            break;
            }              
                        
'''


def replace_case(text: str, start_token: str, next_token: str, block: str) -> str:
    start = text.index(start_token)
    end = text.index(next_token, start)
    return text[:start] + block + text[end:]


def install(header: str, source: str) -> tuple[str, str]:
    if MARKER in header and MARKER in source:
        return header, source
    if header.count(OLD_MARKER) != 1 or source.count(OLD_MARKER) != 1:
        raise SystemExit("MCS session-buffer V2 requires exactly one V1 marker")
    header = header.replace(OLD_MARKER, MARKER)
    source = source.replace(OLD_MARKER, MARKER)
    if "void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);" not in source:
        anchor = "#include <s32strm.h>\n"
        if source.count(anchor) != 1:
            raise SystemExit("MCS session-buffer V2 logger anchor missing")
        source = source.replace(
            anchor,
            anchor
            + "\nvoid HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n",
            1,
        )
    source = replace_case(
        source, "        case EMenuGetListSize:",
        "        case EMenuGetListData:", SIZE_BLOCK
    )
    source = replace_case(
        source, "        case EMenuGetListData:",
        "        case EMenuItemGetAttribute:", DATA_BLOCK
    )
    return header, source


def verify(header: str, source: str) -> None:
    checks = {
        "markers": header.count(MARKER) == 1 and source.count(MARKER) == 1,
        "old markers absent": OLD_MARKER not in header and OLD_MARKER not in source,
        "session member": header.count("RBuf8 iHtcleoGetListOutput;") == 1,
        "all-session copy": (
            source.count("iHtcleoGetListOutput.Copy(htcleoSharedOutput)") == 1
            and "if (aMessage.SecureId().iId == 0x101F4CD2u)" not in source
        ),
        "length stages": all(
            source.count(f"0x4D430{stage:03X}u") == 1
            for stage in range(0x170, 0x176)
        ),
        "caller SID recorded": source.count("aMessage.SecureId().iId") == (
            3 if ATOMIC_MARKER in source else 2
        ),
        "session data path": (
            source.count("iHtcleoGetListOutput.MaxLength() > 0") == 1
            and source.count("iHtcleoGetListOutput );") == 1
        ),
        "stock fallback retained": (
            source.count("htcleoFallbackOutput") == 3
            and source.count("iSharedEng->CloseOutputBuffer();") == 3
        ),
        "logger declaration": source.count(
            "void HtcleoMcsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);"
        ) == 1,
        "no wait or fabrication": all(
            token not in source
            for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS GetList session-buffer V2 verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    header_path = component / "srvinc/menusrvsession.h"
    source_path = component / "srvsrc/menusrvsession.cpp"
    header = header_path.read_text(encoding="latin-1")
    source = source_path.read_text(encoding="latin-1")
    header, source = install(header, source)
    verify(header, source)
    header_path.write_text(header, encoding="latin-1")
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MCS_GETLIST_SESSION_BUFFER="
        "all-session-size-data-snapshot-real-payload-traced-170-175"
    )


if __name__ == "__main__":
    main()
