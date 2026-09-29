#!/usr/bin/env python3
"""Keep theme refresh visual-only once Matrix has a real populated UI model."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MATRIXMENU_SKIN_REFRESH_NO_REQUERY_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Matrix visual-only skin refresh anchor mismatch: {old[:100]!r}")
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    if MARKER in text:
        return text
    anchor = '''void CMmAppUi::SkinConfigurationChanged(
        const TAknsSkinStatusConfigurationChangeReason aReason)
    {'''
    text = once(text, anchor, anchor + '''
    HtcleoMenuLog(0x4D4D1460u, (TInt)aReason,
        (iCurrentContainer ? 1u : 0u) | (iCurrentSuiteModel ? 2u : 0u));''')
    anchor = '''void CMmAppUi::RefreshIconsL()
    {
    iSkinChangeNeeded = EFalse;'''
    text = once(text, anchor, anchor + '''
    // HTCLEO_MATRIXMENU_SKIN_REFRESH_NO_REQUERY_V1
    // Both callers are skin-change/focus refreshes, not app-list changes.
    // A late theme notification must not recreate HN/LIW GetList services
    // while the existing real model and client window are already usable.
    // Resource invalidation below is retained so cached widgets can redraw.
    const TBool htcleoVisualOnly = iCurrentContainer && iCurrentSuiteModel;
    HtcleoMenuLog(0x4D4D1461u, KErrNone, htcleoVisualOnly ? 1u : 0u);
    if (!htcleoVisualOnly)
        {''')
    start = text.index("void CMmAppUi::RefreshIconsL()")
    end = text.index("void CMmAppUi::HandleHighlightOffsetL(", start)
    section = text[start:end]
    section = once(section, '''    CleanupStack::PopAndDestroy(paramList);
    if( iCurrentContainer )''', '''    CleanupStack::PopAndDestroy(paramList);
        }
    else
        {
        // Only automatic skin-driven requery is deferred. AppArc scanning,
        // explicit folder navigation and app-list updates retain their paths.
        HtcleoMenuLog(0x4D4D1462u, KErrNotSupported, 0x534B494Eu);
        }
    if( iCurrentContainer )''')
    section = once(section, '''        iCurrentContainer->HandleResourceChange( KAknsMessageSkinChange );
        }''', '''        HtcleoMenuLog(0x4D4D1463u, KErrNone, 0u);
        iCurrentContainer->HandleResourceChange( KAknsMessageSkinChange );
        HtcleoMenuLog(0x4D4D1464u, KErrNone, 0u);
        }
    HtcleoMenuLog(0x4D4D1465u, KErrNone, 0u);''')
    return text[:start] + section + text[end:]


def verify(text: str) -> None:
    if text.count(MARKER) != 1:
        raise SystemExit("visual-only skin refresh marker missing")
    for stage in range(0x1460, 0x1466):
        if text.count(f"0x4D4D{stage:04X}u") != 1:
            raise SystemExit("skin refresh boundary marker missing/duplicated")
    start = text.index("void CMmAppUi::RefreshIconsL()")
    end = text.index("void CMmAppUi::HandleHighlightOffsetL(", start)
    section = text[start:end]
    if "const TBool htcleoVisualOnly = iCurrentContainer && iCurrentSuiteModel;" not in section:
        raise SystemExit("existing real model/client guard missing")
    if not (section.index("if (!htcleoVisualOnly)") < section.index("CLiwGenericParamList::NewLC()")
            < section.index("HandleRequestL(*paramList)") < section.index("\n    else\n")
            < section.index("HandleResourceChange( KAknsMessageSkinChange )")):
        raise SystemExit("preserve fallback query and all visual resource invalidation")
    if text.count("RefreshIconsL()") != 3:
        raise SystemExit("skin refresh caller set changed")
    for retained in ("iSkinSrvSession.EnableSkinChangeNotify();", "SetAllDefinitionSets(htcleoHazePid)",
                     "htcleoNotifyFinish", "0x4D4D1450u", "0x4D4D01FFu"):
        if retained not in text:
            raise SystemExit(f"required existing behavior missing: {retained}")
    if any(call in section for call in ("SetOrdinal", "StartApp", "User::After", "ResetToRootL")):
        raise SystemExit("skin refresh must not change navigation or scheduling")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    text = patch(path.read_text(encoding="latin-1"))
    verify(text)
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_MATRIX_SKIN_REFRESH=existing-model-resource-invalidation-no-hn-requery-1460-1465")


if __name__ == "__main__":
    main()
