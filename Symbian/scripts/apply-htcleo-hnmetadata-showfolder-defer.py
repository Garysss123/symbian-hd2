#!/usr/bin/env python3
"""Defer the optional MatrixMenu show-folder CenRep observer on HTC Leo.

Iteration 530 proves every preceding CHnMdModel dependency succeeds and blocks
only while constructing CHnRepositoryShowFolderObserver.  That observer exists
solely to react to a later KMenuShowFolder setting change.  Keep the member NULL
and record an explicit KErrNotSupported result; initial metadata, widget-type
observation, suite evaluation and all core UI calls remain unchanged.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HNMETADATA_SHOWFOLDER_UI_FIRST_DEFER_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    return replace_once(
        source,
        """    HtcleoMdLog(0x4D44012Bu, KErrNone, 0u);
    iRepositoryShowFolderObserver = CHnRepositoryShowFolderObserver::NewL( &iCmnPtrs, KCRUidMenu, KMenuShowFolder );
    HtcleoMdLog(0x4D44012Cu, KErrNone,
        iRepositoryShowFolderObserver ? 1u : 0u);
""",
        """    HtcleoMdLog(0x4D44012Bu, KErrNone, 0u);
    // HTCLEO_HNMETADATA_SHOWFOLDER_UI_FIRST_DEFER_V1
    // Optional runtime show-folder notifications are deferred until after the
    // first visible shell milestone.  NULL is already destructor-safe.
    iRepositoryShowFolderObserver = NULL;
    HtcleoMdLog(0x4D44012Cu, KErrNotSupported, 0x53464F4Cu);
""",
        "show-folder observer boundary",
    )


def verify(source: str) -> None:
    checks = {
        "single marker": source.count(MARKER) == 1,
        "explicit null": source.count("iRepositoryShowFolderObserver = NULL;") == 1,
        "explicit result": source.count(
            "HtcleoMdLog(0x4D44012Cu, KErrNotSupported, 0x53464F4Cu);"
        ) == 1,
        "blocking constructor retired": (
            "iRepositoryShowFolderObserver = CHnRepositoryShowFolderObserver::NewL("
            not in source
        ),
        "widget observer retained": source.count(
            "iRepositoryWidgetTypeObserver = CHnRepositoryWidgetTypeObserver::NewL("
        ) == 1,
        "destructor retained": source.count(
            "delete iRepositoryShowFolderObserver;"
        ) == 1,
        "no timer display or fake success": (
            "User::After" not in source[source.index(MARKER) - 300 : source.index(MARKER) + 500]
            and "HalFunction" not in source[source.index(MARKER) - 300 : source.index(MARKER) + 500]
            and "KErrNone, 0x53464F4C" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("show-folder defer verification failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source_path = (
        args.root
        / "sf/app/homescreen/menufw/hierarchynavigator/"
        "hnmetadatamodel/src/hnmdmodel.cpp"
    )
    if not source_path.is_file():
        raise SystemExit("missing HN metadata model source")
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_HNMETADATA_SHOWFOLDER=deferred "
        "stage=4D44012C detail=53464F4C policy=ui-first"
    )


if __name__ == "__main__":
    main()
