#!/usr/bin/env python3
"""Build and draw MatrixMenu's real first container synchronously.

Iteration 546 proves that real CCoeAppUi::ActivateTopViewL() returns, but
MatrixMenu registers no Avkon views, so CCoeViewManager may legitimately do
nothing.  MatrixMenu's actual UI is created when its HN suite-initialized
callback calls HandleSuiteModelInitializedL() -> ShowSuiteL() ->
CreateNewContainerL() -> HandlePresentationChangeL().  The scheduler frontier
prevents that callback even though CHnEngine::InitializeL() and the real suite
model have already completed synchronously.

Immediately after InitializeL(), obtain the real last suite model.  If the
callback has not already created a container, call the stock handler directly.
Then size, show and DrawNow the resulting real container.  Model, template,
widget, WServ rendering and all leaving behavior remain real and fail-closed;
there is no dummy UI or fabricated success.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER_V1"
PREREQUISITE = "HTCLEO_MATRIXMENU_HNENGINE_RESULT_TRACE_V1"


OLD = r'''    InitializeL();
    HtcleoMenuLog(0x4D4D030Eu, KErrNone, 0u);

    // HTCLEO_MATRIXMENU_POSTINIT_UI_FIRST_DEFER_V1'''


NEW = r'''    InitializeL();
    HtcleoMenuLog(0x4D4D030Eu, KErrNone, 0u);

    // HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER_V1
    HtcleoMenuLog(0x4D4D0313u, KErrNone, 0u);
    CHnSuiteModel* htcleoInitialSuite = iHNInterface->GetLastSuiteModelL();
    HtcleoMenuLog(0x4D4D0314u,
        htcleoInitialSuite ? KErrNone : KErrNotReady,
        iCurrentContainer ? 1u : 0u);
    if (!htcleoInitialSuite)
        {
        User::Leave(KErrNotReady);
        }
    if (!iCurrentContainer)
        {
        HtcleoMenuLog(0x4D4D0315u, KErrNone, 0u);
        HandleSuiteModelInitializedL(htcleoInitialSuite);
        HtcleoMenuLog(0x4D4D0316u,
            iCurrentContainer ? KErrNone : KErrNotReady,
            iCurrentContainer ? 1u : 0u);
        }
    if (!iCurrentContainer)
        {
        User::Leave(KErrNotReady);
        }
    HtcleoMenuLog(0x4D4D0317u, KErrNone, 1u);
    iCurrentContainer->SetRect(ClientRect());
    iCurrentContainer->MakeVisible(ETrue);
    iCurrentContainer->DrawNow();
    HtcleoMenuLog(0x4D4D0318u, KErrNone, 1u);

    // HTCLEO_MATRIXMENU_POSTINIT_UI_FIRST_DEFER_V1'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"post-InitializeL anchor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    successor = "HTCLEO_MATRIXMENU_UI_FIRST_CONTAINER_COMPAT_V1" in source
    checks = {
        "HN prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "real suite lookup": source.count(
            "iHNInterface->GetLastSuiteModelL()"
        ) >= 1,
        "stock suite handler or direct successor": source.count(
            "HandleSuiteModelInitializedL(htcleoInitialSuite);"
        ) == (0 if successor else 1),
        "duplicate callback guard": source.count("if (!iCurrentContainer)") >= 2,
        "real container draw": (
            source.count("iCurrentContainer->SetRect(ClientRect());") >= 1
            and source.count("iCurrentContainer->MakeVisible(ETrue);") >= 1
            and (
                source.count("iCurrentContainer->DrawNow();") >= 1
                or source.count(
                    "iCurrentContainer->Widget()->DrawNow(htcleoFullGridRect);"
                ) == 1
            )
        ),
        "all stages": all(
            source.count(f"0x4D4D{stage:04X}u") == 1
            for stage in range(0x0313, 0x0319)
        ),
        "fail closed": (
            NEW.count("User::Leave(KErrNotReady);") == 2
            and "TRAP_IGNORE" not in NEW
            and "KErrNotSupported" not in NEW
        ),
        "no dummy or display probe": (
            "iDummyContainer" not in NEW
            and "HalFunction" not in NEW
            and "User::After" not in NEW
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER="
        "real-suite-handler-show-draw-0313-0318"
    )


if __name__ == "__main__":
    main()
