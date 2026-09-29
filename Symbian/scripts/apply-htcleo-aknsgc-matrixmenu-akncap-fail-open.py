#!/usr/bin/env python3
"""Let MatrixMenu use Avkon's existing local-layout path without AknCap IPC.

Iteration 510 proves that the AknCap process remains alive and sees its own
AppServer registration, while MatrixMenu still receives KErrNotFound from the
global registry.  CAknSgcClient already has a stock no-handle branch that
builds the packed layout locally (used by EikSrv); the only fatal barrier is
the unconditional LeaveIfError immediately after iAknSrv.Connect().

Fail open only for MatrixMenu SID 0x101f4cd2 and only for the two transient
server-lifetime errors already handled by the client.  Keep the null handle,
record the real error, and let the existing local-layout branch run.  Other
processes and all other errors retain stock behaviour.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNSGC_MATRIXMENU_AKNCAP_FAIL_OPEN_V1"

OLD = '''\tconst TInt aknServerError = iAknSrv.Connect();
\tHtcleoAknSgcMenuLog(0x4D4DA124u, aknServerError, 0u);
\tUser::LeaveIfError(aknServerError);
\tHtcleoAknSgcMenuLog(0x4D4DA125u, KErrNone, 0u);
'''

NEW = '''\tconst TInt aknServerError = iAknSrv.Connect();
\tHtcleoAknSgcMenuLog(0x4D4DA124u, aknServerError, 0u);
\t// HTCLEO_AKNSGC_MATRIXMENU_AKNCAP_FAIL_OPEN_V1
\t// MatrixMenu can construct its layout from the existing no-handle branch.
\t// Preserve the real connection error and never fabricate an IPC handle.
\tconst TBool htcleoMatrixMenuAknCapFailOpen =
\t\t(RProcess().SecureId().iId == 0x101f4cd2u &&
\t\t(aknServerError == KErrNotFound ||
\t\t aknServerError == KErrServerTerminated));
\tHtcleoAknSgcMenuLog(0x4D4DA133u, aknServerError,
\t\thtcleoMatrixMenuAknCapFailOpen ? 1u : 0u);
\tif (!htcleoMatrixMenuAknCapFailOpen)
\t\t{
\t\tUser::LeaveIfError(aknServerError);
\t\t}
\tHtcleoAknSgcMenuLog(0x4D4DA125u, KErrNone,
\t\thtcleoMatrixMenuAknCapFailOpen ? 1u : 0u);
'''


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "exact MatrixMenu SID": source.count(
            "RProcess().SecureId().iId == 0x101f4cd2u"
        ) >= 1,
        "narrow errors": (
            source.count("aknServerError == KErrNotFound") == 1
            and source.count("aknServerError == KErrServerTerminated") == 1
        ),
        "real error retained": source.count(
            "HtcleoAknSgcMenuLog(0x4D4DA133u, aknServerError,"
        ) == 1,
        "stock leave retained": source.count(
            "User::LeaveIfError(aknServerError);"
        ) == 1,
        "stock local layout retained": source.count(
            "packedBuf = iLayoutConfig->CreatePackedBufL();"
        ) == 1,
        "no fake handle": "SetHandle" not in NEW,
        "no timer or display": (
            "User::After" not in NEW
            and "RTimer" not in NEW
            and "HalFunction" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu AknCap fail-open verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/mw/classicui/uifw/AvKon/src/aknsgcc.cpp"
    )
    if not source_path.is_file():
        raise SystemExit(f"missing Avkon input: {source_path}")

    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        count = source.count(OLD)
        if count != 1:
            raise SystemExit(
                "MatrixMenu AknCap fail-open anchor: expected one, "
                f"found {count}"
            )
        source = source.replace(OLD, NEW, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNSGC_MATRIXMENU_AKNCAP_FAIL_OPEN="
        "sid-101f4cd2 notfound-or-terminated local-layout"
    )


if __name__ == "__main__":
    main()
