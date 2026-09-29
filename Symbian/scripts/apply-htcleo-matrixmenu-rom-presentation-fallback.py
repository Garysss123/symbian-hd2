#!/usr/bin/env python3
"""Use the ROM-declared first MatrixMenu presentation while metadata is pending.

Iteration 548 proves that the real HN suite model exists but WidgetType() is
EUnspecified because CHnItemsOrder has not yet been marked ready by the
asynchronous metadata collector.  The shipped folder-suite resource explicitly
declares `type="grid|list"` and
`template="logical_template_3|list_single_hc_apps_pane"`; grid and
logical_template_3 are therefore the ROM's first-choice presentation.

For only this initial HTC Leo UI-first path, retain the real suite and item
models, select those ROM-declared first values, and mark the already-returned
structural item evaluations ready.  This exposes the real model through its
normal gated WidgetType()/GetTemplate() accessors so the stock real container
factory can continue.  No dummy container, fabricated menu item, trapped error
or display probe is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_ROM_PRESENTATION_FALLBACK_V1"
PREREQUISITE = "HTCLEO_MATRIXMENU_UI_FIRST_CONTAINER_COMPAT_V1"


OLD = r'''        HtcleoMenuLog(0x4D4D0320u, KErrNone,
            (TUint32)iCurrentSuiteModel->WidgetType());

        CMmWidgetContainer* htcleoInitialContainer = NULL;'''


NEW = r'''        HtcleoMenuLog(0x4D4D0320u, KErrNone,
            (TUint32)iCurrentSuiteModel->WidgetType());

        // HTCLEO_MATRIXMENU_ROM_PRESENTATION_FALLBACK_V1
        // foldersuite_touch/suite.xml declares grid and logical_template_3
        // first.  Use those real ROM defaults only while the asynchronous
        // metadata collector has not yet opened the readiness gate.
        CHnItemsOrder* htcleoInitialOrder =
            iCurrentSuiteModel->GetItemsOrder();
        if (!htcleoInitialOrder)
            {
            User::Leave(KErrCorrupt);
            }
        TInt htcleoModelItemCount = htcleoInitialOrder->GetModelItemCount();
        HtcleoMenuLog(0x4D4D0340u,
            iCurrentSuiteModel->WidgetType(),
            ((TUint32)(htcleoModelItemCount & 0xFFFF) << 16)
                | (TUint32)(htcleoInitialOrder->Count() & 0xFFFF));
        _LIT8(KHtcleoInitialGridTemplate, "logical_template_3");
        if (iCurrentSuiteModel->WidgetType() == EUnspecified)
            {
            iCurrentSuiteModel->SetWidgetType(EGridWidget);
            iCurrentSuiteModel->SetTemplateL(KHtcleoInitialGridTemplate);
            for (TInt htcleoModelIndex = 0;
                    htcleoModelIndex < htcleoModelItemCount;
                    ++htcleoModelIndex)
                {
                htcleoInitialOrder->ItemEvaluated(htcleoModelIndex);
                }
            htcleoInitialOrder->SuiteEvaluated();
            }
        HtcleoMenuLog(0x4D4D0341u,
            iCurrentSuiteModel->WidgetType(),
            htcleoInitialOrder->IsSuiteReadyToShow() ? 1u : 0u);
        HtcleoMenuLog(0x4D4D0342u,
            iCurrentSuiteModel->GetTemplate().Length(),
            (TUint32)htcleoInitialOrder->Count());
        if (!htcleoInitialOrder->IsSuiteReadyToShow()
                || iCurrentSuiteModel->WidgetType() != EGridWidget
                || iCurrentSuiteModel->GetTemplate().Compare(
                    KHtcleoInitialGridTemplate) != 0)
            {
            User::Leave(KErrCorrupt);
            }

        CMmWidgetContainer* htcleoInitialContainer = NULL;'''


def install(source: str) -> str:
    count = source.count(OLD)
    if count != 1:
        raise SystemExit(f"presentation anchor: expected one, found {count}")
    return source.replace(OLD, NEW, 1)


def verify(source: str) -> None:
    block_start = source.index(MARKER)
    block_end = source.index(
        "CMmWidgetContainer* htcleoInitialContainer = NULL;", block_start
    )
    block = source[block_start:block_end]
    checks = {
        "prerequisite": source.count(PREREQUISITE) == 1,
        "single marker": source.count(MARKER) == 1,
        "rom first widget": block.count("SetWidgetType(EGridWidget);") == 1,
        "rom first template": (
            block.count('"logical_template_3"') == 1
            and block.count("SetTemplateL(KHtcleoInitialGridTemplate);") == 1
        ),
        "real readiness gate": (
            block.count("GetModelItemCount()") == 1
            and block.count("ItemEvaluated(htcleoModelIndex)") == 1
            and block.count("SuiteEvaluated()") == 1
            and block.count("IsSuiteReadyToShow()") == 2
        ),
        "stages": all(
            source.count(f"0x4D4D{stage:04X}u") == 1
            for stage in range(0x0340, 0x0343)
        ),
        "fail closed": (
            block.count("User::Leave(KErrCorrupt);") == 2
            and "TRAP" not in block
            and "KErrNotSupported" not in block
        ),
        "no dummy or probe": (
            "iDummyContainer" not in block
            and "HalFunction" not in block
            and "User::After" not in block
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
    else:
        old_scope = r'''        if (iCurrentSuiteModel->WidgetType() == EUnspecified)
            {
            _LIT8(KHtcleoInitialGridTemplate, "logical_template_3");'''
        new_scope = r'''        _LIT8(KHtcleoInitialGridTemplate, "logical_template_3");
        if (iCurrentSuiteModel->WidgetType() == EUnspecified)
            {'''
        if old_scope in source:
            source = source.replace(old_scope, new_scope, 1)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_ROM_PRESENTATION_FALLBACK="
        "foldersuite-first-grid-logical-template-3-0340-0342"
    )


if __name__ == "__main__":
    main()
