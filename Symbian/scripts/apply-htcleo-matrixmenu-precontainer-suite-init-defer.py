#!/usr/bin/env python3
"""Defer only the reentrant startup suite callback before a real container."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_PRECONTAINER_SUITE_INIT_DEFER_V1"


ANCHOR = r'''    // The synchronous HTC Leo first-container path has already installed the
    // same real model while the application is hidden from FSW.  Avoid replaying
    // the incompatible startup chrome wrapper for only this queued callback.
    if (isHiddenFromFS && aModel == iCurrentSuiteModel && iCurrentContainer)
        {'''


PATCHED = r'''    // HTCLEO_MATRIXMENU_PRECONTAINER_SUITE_INIT_DEFER_V1
    // The provider now completes the real five-item model synchronously while
    // ConstructL is still inside InitializeL.  Do not enter ShowSuiteL before
    // the retained synchronous first-container block has a real container.
    if (isHiddenFromFS && !iCurrentContainer)
        {
        HtcleoMenuLog(0x4D4D0334u, KErrNotReady,
            aModel ? (TUint32)aModel->GetItemModelsCount() : 0xFFFFFFFFu);
        return;
        }

    // The synchronous HTC Leo first-container path has already installed the
    // same real model while the application is hidden from FSW.  Avoid replaying
    // the incompatible startup chrome wrapper for only this queued callback.
    if (isHiddenFromFS && aModel == iCurrentSuiteModel && iCurrentContainer)
        {'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if text.count(ANCHOR) != 1:
        raise SystemExit(
            "MatrixMenu pre-container defer: expected one anchor, "
            f"found {text.count(ANCHOR)}"
        )
    return text.replace(ANCHOR, PATCHED, 1)


def verify(text: str) -> None:
    marker_at = text.find(MARKER)
    early_at = text.find("if (isHiddenFromFS && !iCurrentContainer)", marker_at)
    existing_at = text.find(
        "if (isHiddenFromFS && aModel == iCurrentSuiteModel && iCurrentContainer)",
        early_at,
    )
    checks = {
        "marker": text.count(MARKER) == 1,
        "stage": text.count("0x4D4D0334u") == 1,
        "narrow pre-container guard": (
            text.count("if (isHiddenFromFS && !iCurrentContainer)") == 1
            and marker_at < early_at < existing_at
        ),
        "existing ready callback retained": text.count(
            "if (isHiddenFromFS && aModel == iCurrentSuiteModel && iCurrentContainer)"
        ) == 1,
        "real model path retained": all(
            token in text
            for token in (
                "HandleSuiteModelInitializedL( aModel );",
                "iCurrentSuiteModel = aModel;",
                "ShowSuiteL();",
                "CreateNewContainerL(",
                "iCurrentContainer->SetSuiteModelL(iCurrentSuiteModel);",
            )
        ),
        "no fake or wait": all(
            token not in text
            for token in ("User::After", "RTimer", "AppendL( htcleo")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu pre-container suite-init verification failed: "
            + ", ".join(failed)
        )


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
    text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_PRECONTAINER_SUITE_INIT="
        "defer-hidden-startup-callback-0334-real-sync-container-retained"
    )


if __name__ == "__main__":
    main()
