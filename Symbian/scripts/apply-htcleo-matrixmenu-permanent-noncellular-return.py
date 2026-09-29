#!/usr/bin/env python3
"""Remove phone/video-call lookup from MatrixMenu's return-to-shell path."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MATRIXMENU_PERMANENT_NONCELLULAR_RETURN_V1"


def patch(text: str) -> str:
    if MARKER in text:
        return text
    start = text.index("void CMmAppUi::ShowHomescreenL(")
    end = text.index("void CMmAppUi::PrepareHomescreenForMatrixExitL()", start)
    section = text[start:end].replace("    TInt idleid(0);\n", "", 1)
    first = section.index("        case EExitToPhone:")
    last = section.index("        default:", first)
    section = section[:first] + '''        case EExitToPhone:
            {
            // HTCLEO_MATRIXMENU_PERMANENT_NONCELLULAR_RETURN_V1
            // Keep the legacy exit enum, but this product has no Phone target.
            HtcleoMenuLog(0x4D4D1434u, KErrNone, EExitToIdle);
            ShowHomescreenL( EExitToIdle );
            HtcleoMenuLog(0x4D4D1435u, KErrNone, EExitToIdle);
            }
            break;
''' + section[last:]
    section = section.replace("            ShowHomescreenL( EExitToPhone );",
                              "            ShowHomescreenL( EExitToIdle );")
    text = text[:start] + section + text[end:]
    start = text.index("void CMmAppUi::PrepareHomescreenForMatrixExitL()")
    end = text.index("\n    }\n", start) + len("\n    }\n")
    return text[:start] + '''void CMmAppUi::PrepareHomescreenForMatrixExitL()
    {
    // No phone task search, video-call property, or secondary phone branch.
    ShowHomescreenL( EExitToIdle );
    }
''' + text[end:]


def verify(text: str) -> None:
    start = text.index("void CMmAppUi::ShowHomescreenL(")
    end = text.index("void CMmAppUi::OpenAppL(", start)
    section = text[start:end]
    if text.count(MARKER) != 1:
        raise SystemExit("noncellular return marker missing")
    forbidden = ("KPhoneAppUid", "KVideoCallAppUid", "KUikVideoCallTopApp",
                 "CAknTaskList", "CApaWindowGroupName", "CreateActivateViewEventL")
    if any(token in section for token in forbidden):
        raise SystemExit("cellular UI dependency remains in Matrix return path")
    if "OpenAppL( TUid::Uid( appToShowUid ) );" not in section:
        raise SystemExit("real Home launch path missing")
    if "appToShowUid = 0x102750F0;" not in section:
        raise SystemExit("fixed Home fallback missing")
    if any(section.count(f"0x4D4D{stage:04X}u") != 1
           for stage in (0x1430, 0x1431, 0x1432, 0x1433, 0x1434, 0x1435, 0x1436, 0x143F)):
        raise SystemExit("existing return attribution changed")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    args = p.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    text = patch(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print("HTCLEO_MATRIX_NONCELLULAR_RETURN=permanent-direct-home-no-phone-or-video-task-lookup")


if __name__ == "__main__":
    main()
