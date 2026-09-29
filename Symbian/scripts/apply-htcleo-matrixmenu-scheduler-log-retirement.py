#!/usr/bin/env python3
"""Remove Matrix's synchronous scheduler diagnostics; retain a 5s UI heartbeat."""
from __future__ import annotations
import argparse
from pathlib import Path

CONE_MARKER = "HTCLEO_MATRIXMENU_CONE_FILE_TRACE_RETIRED_V1"
AO_MARKER = "HTCLEO_MATRIXMENU_READY_AO_TRACE_RETIRED_V1"
HB_MARKER = "HTCLEO_MATRIXMENU_LOW_RATE_HEARTBEAT_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Matrix scheduler retirement anchor mismatch: {old[:96]!r}")
    return text.replace(old, new, 1)


def patch_cone(text: str) -> str:
    if CONE_MARKER in text:
        return text
    return once(text, "\tif (htcleoSid != 0x101F4CD2u)\n", '''\t// HTCLEO_MATRIXMENU_CONE_FILE_TRACE_RETIRED_V1
\t// Do not perform file IPC inside WaitForAnyRequest/event/redraw dispatch.
\t// MENU activation boundaries and a low-rate UI-thread heartbeat remain.
\tif (htcleoSid == 0x101F4CD2u)
\t\treturn;
\tif (htcleoSid != 0x101F4CD2u)
''')


def patch_ao(text: str) -> str:
    if AO_MARKER in text:
        return text
    return once(text, "    const TUint32 htcleoSid = RProcess().SecureId().iId;", '''    const TUint32 htcleoSid = RProcess().SecureId().iId;
    // HTCLEO_MATRIXMENU_READY_AO_TRACE_RETIRED_V1
    // 730 ends between diagnostic log calls, before the real AO dispatch.
    // Retire the Matrix queue walk itself; never consume IPC completions here.
    if (htcleoSid == 0x101F4CD2u)
        return;''')


HEARTBEAT = '''TInt CMmAppUi::HtcleoHeartbeatTick(TAny* aSelf)
    {
    CMmAppUi* self = static_cast<CMmAppUi*>(aSelf);
    const TUint32 state = (self->iCurrentContainer ? 1u : 0u)
        | (self->iCurrentSuiteModel ? 2u : 0u)
        | ((self->iCurrentContainer && self->iCurrentContainer->IsVisible()) ? 4u : 0u)
        | (self->IsForeground() ? 8u : 0u);
    HtcleoMenuLog(0x4D4D01FFu, (TInt)state, 0x414C4956u); // ALIV
    return ETrue;
    }

'''


def patch_appui(text: str) -> str:
    if HB_MARKER in text:
        return text
    text = once(text, "CMmAppUi::CMmAppUi()\n    {", "CMmAppUi::CMmAppUi()\n    : iHtcleoHeartbeat(NULL)\n    {")
    text = once(text, "CMmAppUi::~CMmAppUi()\n    {", '''CMmAppUi::~CMmAppUi()
    {
    delete iHtcleoHeartbeat;
    iHtcleoHeartbeat = NULL;''')
    text = once(text, '    MMPERF(("CMmAppUi::ConstructL - HN ready"));', '''    // HTCLEO_MATRIXMENU_LOW_RATE_HEARTBEAT_V1
    // Diagnostic creation failure must not prevent the real UI from starting.
    if (!iHtcleoHeartbeat)
        {
        TRAPD(heartbeatError,
            iHtcleoHeartbeat = CPeriodic::NewL(CActive::EPriorityLow));
        HtcleoMenuLog(0x4D4D01FEu, heartbeatError, 5000000u);
        if (iHtcleoHeartbeat)
            iHtcleoHeartbeat->Start(5000000, 5000000,
                TCallBack(HtcleoHeartbeatTick, this));
        }
    MMPERF(("CMmAppUi::ConstructL - HN ready"));''')
    return once(text, "TBool CMmAppUi::IsRootdisplayedL()", HEARTBEAT + "TBool CMmAppUi::IsRootdisplayedL()")


def patch_header(text: str) -> str:
    if "CPeriodic* iHtcleoHeartbeat;" in text:
        return text
    return once(text, "    CAknStylusPopUpMenu* iPopupMenu;", '''    CAknStylusPopUpMenu* iPopupMenu;

    // Owned diagnostic AO, cancelled/deleted with the application UI.
    CPeriodic* iHtcleoHeartbeat;
    static TInt HtcleoHeartbeatTick(TAny* aSelf);''')


def patch_logger(text: str) -> str:
    marker = "HTCLEO_MATRIXMENU_HEARTBEAT_NO_FRAME_BREADCRUMB_V1"
    if marker in text:
        return text
    start = text.index("    // HTCLEO_MATRIXMENU_FRAME_STAGE_BREADCRUMB_V1")
    end = text.index("    RFs fs;", start)
    old = text[start:end]
    new = '''    // HTCLEO_MATRIXMENU_HEARTBEAT_NO_FRAME_BREADCRUMB_V1
    // Heartbeats must not overwrite the stage used by rendering compatibility.
    const TBool heartbeatRecord =
        aStage == 0x4D4D01FEu || aStage == 0x4D4D01FFu;
    if (!heartbeatRecord)
        {
''' + "".join("    " + line + "\n" for line in old.splitlines()) + "        }\n"
    text = text[:start] + new + text[end:]
    return once(text, "        if (r == KErrNone)\n            {\n            file.Flush();", "        if (r == KErrNone && !heartbeatRecord)\n            {\n            file.Flush();")


def verify(cone: str, ao: str, appui: str, header: str, logger: str) -> None:
    if cone.count(CONE_MARKER) != 1 or ao.count(AO_MARKER) != 1 or appui.count(HB_MARKER) != 1:
        raise SystemExit("Matrix scheduler retirement marker check failed")
    cs = cone.index(CONE_MARKER)
    if not (cone.index("if (htcleoSid == 0x101F4CD2u)", cs) < cone.index("RFs fs;", cs)):
        raise SystemExit("Matrix CONE trace must return before filesystem access")
    if not (ao.index(AO_MARKER) < ao.index("TDblQueIter<CActive> iterator")):
        raise SystemExit("Matrix ready-AO diagnostic must return before queue scan")
    if "iHtcleoHeartbeat->Start(5000000, 5000000," not in appui:
        raise SystemExit("heartbeat must remain low rate")
    if (appui.count("delete iHtcleoHeartbeat;") != 1 or
            appui.count(": iHtcleoHeartbeat(NULL)") != 1 or
            header.count("CPeriodic* iHtcleoHeartbeat;") != 1):
        raise SystemExit("heartbeat ownership/init/cleanup missing")
    if "if (!heartbeatRecord)" not in logger or "r == KErrNone && !heartbeatRecord" not in logger:
        raise SystemExit("heartbeat must preserve frame-stage property and skip explicit Flush")
    if "position <= ((16384 * 64) - 64)" not in logger:
        raise SystemExit("keep 1 MiB log capacity")
    if any(x in HEARTBEAT for x in ("SetOrdinal", "Draw", "Finish", "GetFocusWindowGroup", "User::After")):
        raise SystemExit("heartbeat must observe, not drive or query the UI")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    cone_base = args.root / "sf/mw/classicui/lafagnosticuifoundation/cone/src"
    matrix_base = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu"
    paths = [cone_base / "COEMAIN.CPP", cone_base / "htcleoschedulertrace.cpp",
             matrix_base / "src/mmappui.cpp", matrix_base / "inc/mmappui.h",
             matrix_base / "src/htcleomenulog.cpp"]
    patchers = [patch_cone, patch_ao, patch_appui, patch_header, patch_logger]
    contents = [fn(path.read_text(encoding="latin-1")) for fn, path in zip(patchers, paths)]
    verify(*contents)
    for path, content in zip(paths, contents):
        path.write_text(content, encoding="latin-1")
    print("HTCLEO_MATRIX_SCHEDULER_LOG_RETIREMENT=cone-and-ready-ao-no-file-io-in-matrix-dispatch")
    print("HTCLEO_MATRIX_HEARTBEAT=menulog-01fe-arm-01ff-aliv-5s-ui-thread-1m-no-frame-property-no-flush")


if __name__ == "__main__":
    main()
