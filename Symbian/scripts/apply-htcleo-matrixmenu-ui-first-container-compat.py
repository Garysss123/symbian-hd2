#!/usr/bin/env python3
"""Create MatrixMenu's first real container without optional shell chrome.

Iteration 547 proves that the real suite model exists, then stops inside the
stock HandleSuiteModelInitializedL() before it creates a container.  That
handler combines status-pane/CBA visibility with the application-start
full-screen transition, so iteration 547 cannot attribute the stop to any one
of them.

Keep the real HN suite model, template library, widget factory, model binding,
control stack, drawing calls and status pane.  Defer the cosmetic startup
transition and the combined handler wrapper for this first synchronous
presentation, then explicitly make the real status pane visible after the menu
has drawn.  The stock callback remains available after foreground gain; a
narrow hidden-start guard prevents the queued initial callback from repeating
the incompatible wrapper after the real container has already been installed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_UI_FIRST_CONTAINER_COMPAT_V1"
PREREQUISITE = "HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER_V1"


OLD_EFFECT = r'''    iIsKastorEffectStarted = EFalse;
    StartLayoutSwitchFullScreen( AknTransEffect::EApplicationStart );
    HtcleoMenuLog(0x4D4D0305u, KErrNone, 0u);'''


NEW_EFFECT = r'''    iIsKastorEffectStarted = EFalse;
    // HTCLEO_MATRIXMENU_UI_FIRST_CONTAINER_COMPAT_V1
    // The startup full-screen transition can permanently cover the first
    // real window on HTC Leo.  It is cosmetic and is deferred until after the
    // first visible shell milestone.
    HtcleoMenuLog(0x4D4D0305u, KErrNotSupported, 0x5452414Eu);'''


OLD_CONTAINER = r'''    if (!iCurrentContainer)
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
    HtcleoMenuLog(0x4D4D0318u, KErrNone, 1u);'''


NEW_CONTAINER = r'''    if (!iCurrentContainer)
        {
        HtcleoMenuLog(0x4D4D0315u, KErrNone, 0u);
        iCurrentSuiteModel = htcleoInitialSuite;
        HtcleoMenuLog(0x4D4D0320u, KErrNone,
            (TUint32)iCurrentSuiteModel->WidgetType());

        CMmWidgetContainer* htcleoInitialContainer = NULL;
        HtcleoMenuLog(0x4D4D0321u, KErrNone, 0u);
        TBool htcleoContainerCreated = CreateNewContainerL(
            iCurrentSuiteModel, htcleoInitialContainer);
        HtcleoMenuLog(0x4D4D0322u,
            htcleoContainerCreated ? KErrNone : KErrNotSupported,
            htcleoInitialContainer ? 1u : 0u);
        if (!htcleoContainerCreated || !htcleoInitialContainer)
            {
            User::Leave(KErrNotSupported);
            }

        iCurrentContainer = htcleoInitialContainer;
        HtcleoMenuLog(0x4D4D0323u, KErrNone, 1u);
        iCurrentContainer->Widget()->View()->SetDisableRedraw(ETrue);
        HtcleoMenuLog(0x4D4D0324u, KErrNone, 1u);
        iCurrentContainer->SetSuiteModelL(iCurrentSuiteModel);
        HtcleoMenuLog(0x4D4D0325u, KErrNone, 1u);
        iCurrentContainer->SetEmptyTextL(iCurrentSuiteModel->EmptyText());
        HtcleoMenuLog(0x4D4D0326u, KErrNone, 1u);
        iCurrentContainer->SetHasFocusL(ETrue);
        iCurrentContainer->SetObserver(this);
        HtcleoMenuLog(0x4D4D0327u, KErrNone, 1u);
        AddToStackL(iCurrentContainer);
        HtcleoMenuLog(0x4D4D0328u, KErrNone, 1u);
        iCurrentContainer->SetRect(ClientRect());
        HtcleoMenuLog(0x4D4D0329u, KErrNone, 1u);
        iCurrentContainer->MakeVisible(ETrue);
        HtcleoMenuLog(0x4D4D032Au, KErrNone, 1u);
        iCurrentContainer->Widget()->View()->SetDisableRedraw(EFalse);
        HtcleoMenuLog(0x4D4D032Bu, KErrNone, 1u);
        iCurrentContainer->DrawNow();
        HtcleoMenuLog(0x4D4D032Cu, KErrNone, 1u);
        HtcleoMenuLog(0x4D4D0332u, KErrNone, 1u);
        StatusPane()->MakeVisible(ETrue);
        HtcleoMenuLog(0x4D4D0333u, KErrNone, 1u);
        HtcleoMenuLog(0x4D4D0316u, KErrNone, 1u);
        }
    if (!iCurrentContainer)
        {
        User::Leave(KErrNotReady);
        }
    HtcleoMenuLog(0x4D4D0317u, KErrNone, 1u);
    iCurrentContainer->DrawView();
    HtcleoMenuLog(0x4D4D0318u, KErrNone, 1u);'''


OLD_HANDLER = r'''void CMmAppUi::HandleSuiteModelInitializedL( CHnSuiteModel* aModel )
    {

    StatusPane()->MakeVisible( ETrue );'''


NEW_HANDLER = r'''void CMmAppUi::HandleSuiteModelInitializedL( CHnSuiteModel* aModel )
    {

    // The synchronous HTC Leo first-container path has already installed the
    // same real model while the application is hidden from FSW.  Avoid replaying
    // the incompatible startup chrome wrapper for only this queued callback.
    if (isHiddenFromFS && aModel == iCurrentSuiteModel && iCurrentContainer)
        {
        HtcleoMenuLog(0x4D4D0330u, KErrNone, 1u);
        iCurrentContainer->MakeVisible(ETrue);
        iCurrentContainer->DrawNow();
        HtcleoMenuLog(0x4D4D0331u, KErrNone, 1u);
        return;
        }

    StatusPane()->MakeVisible( ETrue );'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(source, OLD_EFFECT, NEW_EFFECT, "startup effect")
    source = replace_once(source, OLD_CONTAINER, NEW_CONTAINER, "first container")
    source = replace_once(source, OLD_HANDLER, NEW_HANDLER, "queued callback")
    return source


def verify(source: str) -> None:
    presentation_successor = (
        "HTCLEO_MATRIXMENU_ROM_PRESENTATION_FALLBACK_V1" in source
    )
    block_start = source.index(
        "// HTCLEO_MATRIXMENU_SYNCHRONOUS_FIRST_CONTAINER_V1"
    )
    block_end = source.index(
        "// HTCLEO_MATRIXMENU_POSTINIT_UI_FIRST_DEFER_V1", block_start
    )
    direct_block = source[block_start:block_end]
    checks = {
        "prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "startup effect retired": (
            source.count("StartLayoutSwitchFullScreen( AknTransEffect::EApplicationStart );") == 0
            and source.count("0x4D4D0305u, KErrNotSupported, 0x5452414Eu") == 1
        ),
        "stock handler absent from synchronous block": (
            "HandleSuiteModelInitializedL(htcleoInitialSuite);" not in source
        ),
        "real widget factory": direct_block.count("CreateNewContainerL(") == 1,
        "real model binding": direct_block.count("SetSuiteModelL(iCurrentSuiteModel);") == 1,
        "control stack": direct_block.count("AddToStackL(iCurrentContainer);") == 1,
        "real drawing": (
            direct_block.count("iCurrentContainer->MakeVisible(ETrue);") == 1
            and (
                direct_block.count("iCurrentContainer->DrawNow();") == 1
                or direct_block.count(
                    "iCurrentContainer->Widget()->DrawNow(htcleoFullGridRect);"
                ) == 1
            )
            and direct_block.count("iCurrentContainer->DrawView();") == 1
        ),
        "fine stages": all(
            source.count(f"0x4D4D{stage:04X}u") == 1
            for stage in list(range(0x0320, 0x032D))
            + [0x0330, 0x0331, 0x0332, 0x0333]
        ),
        "real status pane retained": (
            direct_block.count("StatusPane()->MakeVisible(ETrue);") == 1
        ),
        "queued callback guard": (
            source.count("isHiddenFromFS && aModel == iCurrentSuiteModel && iCurrentContainer") == 1
        ),
        "fail closed": (
            direct_block.count("User::Leave(")
            == (5 if presentation_successor else 3)
            and "TRAP" not in direct_block
            and "KErrNone : KErrNotSupported" in direct_block
        ),
        "no dummy or display probe": (
            "iDummyContainer" not in direct_block
            and "HalFunction" not in direct_block
            and "User::After" not in direct_block
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
        "HTCLEO_MATRIXMENU_UI_FIRST_CONTAINER_COMPAT="
        "real-widget-statuspane-0320-0333-no-startup-effect"
    )


if __name__ == "__main__":
    main()
