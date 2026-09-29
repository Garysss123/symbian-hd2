#!/usr/bin/env python3
"""Keep MatrixMenu's two-phase GetList payload in its server session."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MCS_GETLIST_SESSION_BUFFER_V1"
SUPERSEDED_MARKER = "HTCLEO_MCS_GETLIST_SESSION_BUFFER_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(header: str, source: str) -> tuple[str, str]:
    if MARKER in header or MARKER in source:
        return header, source

    header = replace_once(
        header,
        "    CObjectIx* iOperationIx; ///< Operation index. Owned.\n",
        "    CObjectIx* iOperationIx; ///< Operation index. Owned.\n"
        "    // HTCLEO_MCS_GETLIST_SESSION_BUFFER_V1\n"
        "    RBuf8 iHtcleoGetListOutput; ///< MatrixMenu two-phase IPC payload.\n",
        "session output member",
    )

    source = replace_once(
        source,
        "CMenuSrvSession::~CMenuSrvSession()\n    {\n",
        "CMenuSrvSession::~CMenuSrvSession()\n    {\n"
        "    iHtcleoGetListOutput.Close();\n",
        "session output cleanup",
    )

    size_start = source.index("        case EMenuGetListSize:")
    data_start = source.index("        case EMenuGetListData:", size_start)
    size_block = r'''        case EMenuGetListSize:
            {
            __ASSERT_ALWAYS( iSharedEng, PanicClientL( aMessage ) );
            TInt deslen = aMessage.GetDesLength( KGetListDescriptorPos );
            HBufC8* buffer = HBufC8::NewLC( deslen );
            TPtr8 tempDes = buffer->Des( );
            aMessage.Read( KGetListDescriptorPos, tempDes );
            TInt size = iSharedEng->GetListSizeL( *buffer );
            // HTCLEO_MCS_GETLIST_SESSION_BUFFER_V1
            // The stock engine owns one shared output buffer across all
            // sessions.  A live timer allows another request between Size and
            // Data.  Snapshot only MatrixMenu's real serialized result into
            // this CSession2 instance, then release the shared buffer.
            if (aMessage.SecureId().iId == 0x101F4CD2u)
                {
                const TDesC8& htcleoSharedOutput =
                    iSharedEng->GetListDataL();
                iHtcleoGetListOutput.Close();
                iHtcleoGetListOutput.CreateL(htcleoSharedOutput.Length());
                iHtcleoGetListOutput.Copy(htcleoSharedOutput);
                iSharedEng->CloseOutputBuffer();
                size = iHtcleoGetListOutput.Length();
                }
            TPckg<TInt> sizeDes( size );
            aMessage.WriteL( KGetListReturnPos, sizeDes );
            CleanupStack::PopAndDestroy( buffer );
            break;
            }   

'''
    source = source[:size_start] + size_block + source[data_start:]

    data_start = source.index("        case EMenuGetListData:")
    next_case = source.index("        case EMenuItemGetAttribute:", data_start)
    data_block = r'''        case EMenuGetListData:
            {
            __ASSERT_ALWAYS( iSharedEng, PanicClientL( aMessage ) );
            if (iHtcleoGetListOutput.MaxLength() > 0)
                {
                aMessage.WriteL( KGetListDescriptorPos,
                    iHtcleoGetListOutput );
                iHtcleoGetListOutput.Close();
                }
            else
                {
                aMessage.WriteL( KGetListDescriptorPos,
                    iSharedEng->GetListDataL() );
                iSharedEng->CloseOutputBuffer();
                }
            break;
            }              
                        
'''
    source = source[:data_start] + data_block + source[next_case:]
    return header, source


def verify(header: str, source: str) -> None:
    checks = {
        "markers": header.count(MARKER) == 1 and source.count(MARKER) == 1,
        "session member": header.count("RBuf8 iHtcleoGetListOutput;") == 1,
        "cleanup": source.count("iHtcleoGetListOutput.Close();") == 3,
        "MatrixMenu scope": source.count("0x101F4CD2u") == 1,
        "real shared payload copied": (
            source.count("iSharedEng->GetListDataL()") == 2
            and source.count("iHtcleoGetListOutput.Copy(htcleoSharedOutput)") == 1
        ),
        "reported session length": (
            source.count("size = iHtcleoGetListOutput.Length();") == 1
        ),
        "session data write": (
            source.count("iHtcleoGetListOutput );") == 1
            and source.count("iHtcleoGetListOutput.MaxLength() > 0") == 1
        ),
        "stock fallback retained": (
            source.count("iSharedEng->CloseOutputBuffer();") == 3
        ),
        "two protocol cases": (
            source.count("case EMenuGetListSize:") == 1
            and source.count("case EMenuGetListData:") == 1
        ),
        "no wait or fabrication": all(
            token not in source
            for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MCS GetList session-buffer verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/homescreensrv/menucontentsrv"
    header_path = component / "srvinc/menusrvsession.h"
    source_path = component / "srvsrc/menusrvsession.cpp"
    for path in (header_path, source_path):
        if not path.is_file():
            raise SystemExit(f"missing MenuContent session source: {path}")
    header = header_path.read_text(encoding="latin-1")
    source = source_path.read_text(encoding="latin-1")
    if SUPERSEDED_MARKER in header and SUPERSEDED_MARKER in source:
        print(
            "HTCLEO_MCS_GETLIST_SESSION_BUFFER="
            "superseded-by-all-session-v2"
        )
        return
    header, source = install(header, source)
    verify(header, source)
    header_path.write_text(header, encoding="latin-1")
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MCS_GETLIST_SESSION_BUFFER="
        "matrixmenu-per-session-size-data-snapshot-real-payload"
    )


if __name__ == "__main__":
    main()
