#!/usr/bin/env python3
"""Commit MatrixMenu's synchronous first container as the foreground task.

The HTC Leo UI-first path constructs and draws the real five-item container
before CEikonEnv enters its scheduler.  Hardware iteration 587 proves that no
MatrixMenu WS/focus/foreground event is delivered after scheduler entry, while
the first real frame is replaced by the background composition about one
second later.  Complete the stock foreground action explicitly at the end of
ConstructL: use MatrixMenu's real root window group, unhide the real task,
restore its real status/CBA panes, redraw the existing real container and wait
for WServ to consume that command buffer.  No timer, fake item, dummy window,
pixel synthesis or error normalization is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1"
ORDINAL_ONLY_MARKER = "HTCLEO_MATRIXMENU_FOREGROUND_ORDINAL_NO_SYSTEM_EVENT_V1"
PREREQUISITES = (
    "HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER_V1",
    "HTCLEO_MATRIXMENU_PRECONTAINER_SUITE_INIT_DEFER_V1",
    "HTCLEO_MATRIXMENU_RUNTIME_EVENT_TRACE_V1",
)


OLD = r'''    RProperty::Define( KMMenuPSCat, KMMenuLastViewKey, RProperty::EText );
    HtcleoMenuLog(0x4D4D0312u, KErrNone, 0u);

    MMPERF(("CMmAppUi::ConstructL - HN ready"));'''


NEW = r'''    RProperty::Define( KMMenuPSCat, KMMenuLastViewKey, RProperty::EText );
    HtcleoMenuLog(0x4D4D0312u, KErrNone, 0u);

    // HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT_V1
    // The synchronous first-container path runs before the normal foreground
    // event.  Commit the existing real task/window group and real panes once;
    // later runtime foreground changes retain their stock handlers.
    RWsSession& htcleoWs = iCoeEnv->WsSession();
    const TInt htcleoRootWg = CEikonEnv::Static()->RootWin().Identifier();
    const TInt htcleoFocusBefore = htcleoWs.GetFocusWindowGroup();
    HtcleoMenuLog(0x4D4D0350u, htcleoFocusBefore,
        (TUint32)htcleoRootWg);

    TApaTask htcleoTask(htcleoWs);
    htcleoTask.SetWgId(htcleoRootWg);
    const TBool htcleoTaskExists = htcleoTask.Exists();
    HtcleoMenuLog(0x4D4D0351u,
        htcleoTaskExists ? KErrNone : KErrNotFound,
        (TUint32)htcleoRootWg);
    if (!htcleoTaskExists)
        {
        User::Leave(KErrNotFound);
        }

    HideApplicationFromFSW(EFalse);
    isHiddenFromFS = EFalse;
    htcleoTask.BringToForeground();

    StatusPane()->MakeVisible(ETrue);
    Cba()->MakeVisible(ETrue);
    RefreshUiPanesL();
    HtcleoMenuLog(0x4D4D0352u, KErrNone,
        (StatusPane()->IsVisible() ? 1u : 0u)
        | (Cba()->IsVisible() ? 2u : 0u));

    iCurrentContainer->MakeVisible(ETrue);
    iCurrentContainer->DrawNow();
    HtcleoMenuLog(0x4D4D0353u, KErrNone,
        iCurrentContainer->IsVisible() ? 1u : 0u);
    const TInt htcleoForegroundFinish = htcleoWs.Finish();
    HtcleoMenuLog(0x4D4D0354u, htcleoForegroundFinish,
        (TUint32)htcleoWs.GetFocusWindowGroup());
    User::LeaveIfError(htcleoForegroundFinish);

    MMPERF(("CMmAppUi::ConstructL - HN ready"));'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu AppUi source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        if text.count(OLD) != 1:
            raise SystemExit(
                "MatrixMenu foreground commit: expected one ConstructL tail, "
                f"found {text.count(OLD)}"
            )
        text = text.replace(OLD, NEW, 1)

    ordinal_only = ORDINAL_ONLY_MARKER in text
    stages = range(0x0350, 0x0355)
    checks = {
        "prerequisites": all(text.count(item) == 1 for item in PREREQUISITES),
        "single marker": text.count(MARKER) == 1,
        "real root window group": text.count(
            "CEikonEnv::Static()->RootWin().Identifier()"
        ) >= 1,
        "real task foreground": (
            text.count("TApaTask htcleoTask(htcleoWs);") == 1
            and (
                (
                    not ordinal_only
                    and text.count("htcleoTask.BringToForeground();") == 1
                )
                or (
                    ordinal_only
                    and "htcleoTask.BringToForeground();" not in text
                    and text.count(
                        "htcleoWs.SetWindowGroupOrdinalPosition(htcleoRootWg, 0)"
                    ) == 1
                )
            )
        ),
        "task unhidden": (
            text.count("HideApplicationFromFSW(EFalse);") >= 1
            and text.count("isHiddenFromFS = EFalse;") >= 1
        ),
        "real panes": (
            NEW.count("StatusPane()->MakeVisible(ETrue);") == 1
            and NEW.count("Cba()->MakeVisible(ETrue);") == 1
            and NEW.count("RefreshUiPanesL();") == 1
        ),
        "real container redraw": (
            NEW.count("iCurrentContainer->MakeVisible(ETrue);") == 1
            and NEW.count("iCurrentContainer->DrawNow();") == 1
        ),
        "fail closed finish": (
            NEW.count("htcleoWs.Finish();") == 1
            and NEW.count("User::LeaveIfError(htcleoForegroundFinish);") == 1
        ),
        "stages": all(
            NEW.count(f"0x4D4D{stage:04X}u") == 1 for stage in stages
        ),
        "no fake wait or pixels": all(
            token not in NEW
            for token in (
                "User::After",
                "RTimer",
                "TRAP_IGNORE",
                "HalFunction",
                "TransferPixels",
                "CreateWindowL",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu foreground-commit verification failed: "
            + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")
    if ordinal_only:
        print(
            "HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT="
            "real-root-wg-ordinal-no-system-event-panes-container-0350-0355"
        )
    else:
        print(
            "HTCLEO_MATRIXMENU_STARTUP_FOREGROUND_COMMIT="
            "real-root-task-panes-container-finish-0350-0354"
        )


if __name__ == "__main__":
    main()
