#!/usr/bin/env python3
"""Trace MatrixMenu's Eikon BaseConstruct tail and defer its duplicate screen event IPC.

Iteration 514 completes MatrixMenu's first Post-Coe layout pass (C52A/C52C,
B542-B547 and B532-B535) and a following SGC HandleChangeL, but Avkon never
reaches B519 after CEikAppUi::BaseConstructL.  The only remaining synchronous
WServ request in that short Eikon tail is its second EnableScreenChangeEvents
call.  MatrixMenu already skipped the equivalent Avkon request on HTCLEO's
fixed panel.  Extend the existing B600-B615 durable trace to MatrixMenu and
defer only this duplicate final request for that SID.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKAPPUI_MATRIXMENU_FINAL_SCREEN_CHANGE_DEFER_V1"
MATRIXMENU_SID = "0x101F4CD2u"


LOGGER_OLD = r'''    // eikcore.dll is shared; only the EikSrv process owns this stream.
    if (RProcess().SecureId().iId != 0x10003A4A)
        {
        return;
        }
'''

LOGGER_NEW = r'''    // eikcore.dll is shared; keep this stream limited to the two
    // currently hardware-bracketed UI processes.
    const TUint32 htcleoEikBaseSid = RProcess().SecureId().iId;
    if (htcleoEikBaseSid != 0x10003A4Au &&
        htcleoEikBaseSid != 0x101F4CD2u)
        {
        return;
        }
'''


FLUSH_OLD = r'''        r = file.Write(record);
        if (r == KErrNone)
            {
            file.Flush();
            }
'''

FLUSH_NEW = r'''        r = file.Write(record);
        // HTCLEO_EIKAPPUI_MATRIXMENU_LOG_CLOSE_ONLY_V1
        // Avoid turning the diagnostic stream into another synchronous
        // file-server frontier.  Close below releases the completed write.
'''


SCREEN_OLD = r'''    HtcleoEikAppUiBaseLog(0x0000B614u, KErrNone, 0u);
	const TInt htcleoEikScreenChangeResult =
        iCoeEnv->RootWin().EnableScreenChangeEvents();
    HtcleoEikAppUiBaseLog(0x0000B615u, htcleoEikScreenChangeResult,
        0x53434E32u);
'''

SCREEN_NEW = r'''    HtcleoEikAppUiBaseLog(0x0000B614u, KErrNone, 0u);
    // HTCLEO_EIKAPPUI_MATRIXMENU_FINAL_SCREEN_CHANGE_DEFER_V1
    // MatrixMenu already selected the fixed 480x800 panel and skipped the
    // equivalent Avkon subscription.  Do not issue the duplicate synchronous
    // WServ request here; all other processes retain the stock request.
    const TBool htcleoDeferFinalScreenChange =
        RProcess().SecureId().iId == 0x101F4CD2u;
    TInt htcleoEikScreenChangeResult = KErrNotSupported;
    if (!htcleoDeferFinalScreenChange)
        {
        htcleoEikScreenChangeResult =
            iCoeEnv->RootWin().EnableScreenChangeEvents();
        }
    HtcleoEikAppUiBaseLog(0x0000B615u, htcleoEikScreenChangeResult,
        0x53434E32u);
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "matrixmenu logger SID": source.count(
            "htcleoEikBaseSid != 0x101F4CD2u"
        ) == 1,
        "matrixmenu defer SID": source.count(
            "RProcess().SecureId().iId == 0x101F4CD2u;"
        ) == 1,
        "close-only marker": source.count(
            "HTCLEO_EIKAPPUI_MATRIXMENU_LOG_CLOSE_ONLY_V1"
        ) == 1,
        "no explicit log flush": "file.Flush();" not in source,
        "stock call retained": source.count(
            "iCoeEnv->RootWin().EnableScreenChangeEvents();"
        ) == 1,
        "explicit unsupported result": source.count(
            "TInt htcleoEikScreenChangeResult = KErrNotSupported;"
        ) == 1,
        "result checkpoint retained": source.count("0x0000B615u") == 1,
        "detail retained": source.count("0x53434E32u") == 1,
        "no timer": "User::After" not in (LOGGER_NEW + FLUSH_NEW + SCREEN_NEW),
        "no display probe": "HalFunction" not in (
            LOGGER_NEW + FLUSH_NEW + SCREEN_NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "EikAppUi MatrixMenu final screen-change verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    source_path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKAPPUI.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = replace_once(
            source, LOGGER_OLD, LOGGER_NEW, "MatrixMenu EIKBASE logger scope"
        )
        source = replace_once(
            source, FLUSH_OLD, FLUSH_NEW, "MatrixMenu EIKBASE close-only log"
        )
        source = replace_once(
            source, SCREEN_OLD, SCREEN_NEW, "final screen-change request"
        )

    verify(source)
    if source != source_path.read_text(encoding="latin-1"):
        source_path.write_text(source, encoding="latin-1")

    print(
        "HTCLEO_EIKAPPUI_MATRIXMENU_FINAL_SCREEN_CHANGE_DEFER=installed "
        "log=B600-B615-eiksrv-matrixmenu-close-only "
        "screen-change=matrixmenu-deferred-keerrnotsupported"
    )


if __name__ == "__main__":
    main()
