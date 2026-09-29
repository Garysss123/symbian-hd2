#!/usr/bin/env python3
"""Trace MatrixMenu's SetCombinedPaneVisibilityL() frontier.

Iteration 520 completes stack-sensitive CDL layout and creates all ten status
pane containers, then reaches B670 before SetCombinedPaneVisibilityL() but not
B671 after it.  Add MatrixMenu-only close-only stages without changing parent
windows, backgrounds, visibility, or leave behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCOCTL_COMBINED_PANE_VISIBILITY_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        "void CEikStatusPaneBase::SetCombinedPaneVisibilityL( TBool aVisible )\n"
        "    {\n"
        "    CEikStatusPaneContainer* combinedPane =",
        "void CEikStatusPaneBase::SetCombinedPaneVisibilityL( TBool aVisible )\n"
        "    {\n"
        "    // " + MARKER + "\n"
        "    HtcleoStatusPaneLog(0x0000B700u, KErrNone, (TUint32)aVisible);\n"
        "    CEikStatusPaneContainer* combinedPane =",
        "B700 combined-pane visibility entry",
    )
    source = replace_once(
        source,
        "        Find( TUid::Uid( EEikStatusPaneUidCombined ) );\n"
        "    if ( combinedPane )",
        "        Find( TUid::Uid( EEikStatusPaneUidCombined ) );\n"
        "    HtcleoStatusPaneLog(0x0000B701u, KErrNone,\n"
        "        (TUint32)(combinedPane != NULL));\n"
        "    if ( combinedPane )",
        "B701 combined-pane lookup",
    )
    source = replace_once(
        source,
        "        CCoeControl* combinedPaneControl = combinedPane->Control();\n"
        "        \n"
        "        TBool transparencyEnabled( IsTransparent() );",
        "        HtcleoStatusPaneLog(0x0000B702u, KErrNone,\n"
        "            (TUint32)(combinedPane != NULL));\n"
        "        CCoeControl* combinedPaneControl = combinedPane->Control();\n"
        "        HtcleoStatusPaneLog(0x0000B703u, KErrNone,\n"
        "            (TUint32)(combinedPaneControl != NULL));\n"
        "        \n"
        "        TBool transparencyEnabled( IsTransparent() );",
        "B702-B703 combined control",
    )
    source = replace_once(
        source,
        "        // component controls.\n"
        "        TInt count( combinedPaneControl->CountComponentControls() );\n\n"
        "        TBool isFaded( IsFaded() );",
        "        // component controls.\n"
        "        HtcleoStatusPaneLog(0x0000B704u, KErrNone, 0u);\n"
        "        TInt count( combinedPaneControl->CountComponentControls() );\n"
        "        HtcleoStatusPaneLog(0x0000B705u, KErrNone, (TUint32)count);\n\n"
        "        TBool isFaded( IsFaded() );\n"
        "        HtcleoStatusPaneLog(0x0000B706u, KErrNone,\n"
        "            (((TUint32)transparencyEnabled & 0xffffu) << 16) |\n"
        "            ((TUint32)isFaded & 0xffffu));",
        "B704-B706 component count and flags",
    )
    source = replace_once(
        source,
        "        for ( TInt i = 0; i < count; ++i )\n"
        "            {\n"
        "            CEikStatusPaneContainer* subPane =\n"
        "                static_cast<CEikStatusPaneContainer*>(\n"
        "                    combinedPaneControl->ComponentControl( i ) );\n"
        "            if ( subPane )",
        "        for ( TInt i = 0; i < count; ++i )\n"
        "            {\n"
        "            HtcleoStatusPaneLog(0x0000B707u, KErrNone,\n"
        "                (((TUint32)i & 0xffffu) << 16) |\n"
        "                ((TUint32)count & 0xffffu));\n"
        "            CEikStatusPaneContainer* subPane =\n"
        "                static_cast<CEikStatusPaneContainer*>(\n"
        "                    combinedPaneControl->ComponentControl( i ) );\n"
        "            HtcleoStatusPaneLog(0x0000B708u, KErrNone,\n"
        "                (TUint32)(subPane != NULL));\n"
        "            if ( subPane )",
        "B707-B708 sub-pane lookup",
    )
    source = replace_once(
        source,
        "                if ( aVisible )\n"
        "                    {\n"
        "                    subPane->SetParentWindowL( NULL,",
        "                HtcleoStatusPaneLog(0x0000B709u, KErrNone,\n"
        "                    (((TUint32)i & 0xffffu) << 16) |\n"
        "                    ((TUint32)aVisible & 0xffffu));\n"
        "                if ( aVisible )\n"
        "                    {\n"
        "                    subPane->SetParentWindowL( NULL,",
        "B709 parent-window entry",
    )
    source = replace_once(
        source,
        "                    subPane->SetBackground( transparencyEnabled ? NULL :\n"
        "                                                                  iExtension );\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }",
        "                    subPane->SetBackground( transparencyEnabled ? NULL :\n"
        "                                                                  iExtension );\n"
        "                    }\n"
        "                HtcleoStatusPaneLog(0x0000B70Au, KErrNone,\n"
        "                    (TUint32)i);\n"
        "                HtcleoStatusPaneLog(0x0000B70Bu, KErrNone,\n"
        "                    (TUint32)aVisible);\n"
        "                }\n"
        "            HtcleoStatusPaneLog(0x0000B70Cu, KErrNone, (TUint32)i);\n"
        "            }\n"
        "        }\n"
        "    HtcleoStatusPaneLog(0x0000B70Du, KErrNone,\n"
        "        (TUint32)(combinedPane != NULL));\n"
        "    }",
        "B70A-B70D combined visibility return",
    )
    return source


def verify(source: str) -> None:
    expected = range(0xB700, 0xB70E)
    checks = {
        "marker": source.count(MARKER) == 1,
        "stages": all(
            source.count(f"0x0000{stage:04X}u") == 1 for stage in expected
        ),
        "parent visible retained": source.count(
            "subPane->SetParentWindowL( NULL,"
        )
        == 1,
        "parent hidden retained": source.count(
            "subPane->SetParentWindowL(\n"
            "                        iParentWindowGroup,"
        )
        == 1,
        "no bypass": "if ( combinedPane && combinedPane->Control() )" not in source,
        "bounded capacity": (
            source.count("position <= ((512 * 64) - 64)") == 1
            or source.count("htcleoStatusPaneCapacity - 128") == 1
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "combined-pane visibility trace verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    path = args.root / "sf/mw/classicui/uifw/EikStd/coctlsrc/eikspane.cpp"
    source = path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    if source != path.read_text(encoding="latin-1"):
        path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCOCTL_COMBINED_PANE_VISIBILITY_LOG=installed "
        "scope=matrixmenu+homescreen stages=B700-B70D behavior=retained"
    )


if __name__ == "__main__":
    main()
