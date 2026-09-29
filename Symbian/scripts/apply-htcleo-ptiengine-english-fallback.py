#!/usr/bin/env python3
"""Keep MatrixMenu alive with the stock English keymap or no FEP."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_PTIENGINE_MATRIXMENU_ENGLISH_FALLBACK_V1"
MMP_LIBRARY_OLD = "library\t\tEUSER.LIB BAFL.LIB EFSRV.LIB ECOM.LIB ESTOR.LIB"
MMP_LIBRARY_NEW = "library\t\teuser.lib bafl.lib efsrv.lib ecom.lib estor.lib"

CONST_OLD = "//const TInt KPtiKeymappingsDefaultImplementation = 0x10281897;"
CONST_NEW = "const TInt KPtiKeymappingsDefaultImplementation = 0x10281897;"

LIST_OLD = r'''	CPtiKeyMapDataFactory::ListImplementationsL(dataImpl);
   
	for (TInt i = 0; i < dataImpl.Count(); i++)
	    {
        ShutDownKeymapFactory();
	    iKeyMapDataFactory = CPtiKeyMapDataFactory::CreateImplementationL(TUid::Uid(dataImpl[i]));	  	    	   
	    ListDataFactoryLanguagesL(iKeyMapDataFactory, dataImpl[i], aLanguageList);	     
	    }
		
	if (!iFactoryBindings.Count())
	    {
	    // Cannot function without keymapping data.
	    User::Leave(KErrCorrupt);
	    } 
'''

LIST_NEW = r'''	CPtiKeyMapDataFactory::ListImplementationsL(dataImpl);

	// HTCLEO_PTIENGINE_MATRIXMENU_ENGLISH_FALLBACK_V1
	const TBool htcleoMatrixMenuPti =
		(RProcess().SecureId().iId == 0x101F4CD2u);
	if(htcleoMatrixMenuPti && dataImpl.Count() == 0)
		{
		// ITUT_01 is the shipped English keymap implementation.  Prefer a
		// functioning English FEP over treating an unavailable ECom list as
		// corrupt engine state.
		dataImpl.AppendL(KPtiKeymappingsDefaultImplementation);
		}
   
	for (TInt i = 0; i < dataImpl.Count(); i++)
	    {
        ShutDownKeymapFactory();
		TInt htcleoFactoryResult = KErrNone;
		TRAP(htcleoFactoryResult,
			iKeyMapDataFactory = CPtiKeyMapDataFactory::CreateImplementationL(
				TUid::Uid(dataImpl[i]));
			ListDataFactoryLanguagesL(iKeyMapDataFactory, dataImpl[i],
				aLanguageList));
		if(htcleoFactoryResult != KErrNone && !htcleoMatrixMenuPti)
			{
			User::Leave(htcleoFactoryResult);
			}
	    }
		
	if (!iFactoryBindings.Count())
	    {
		if(htcleoMatrixMenuPti)
			{
			// Text input remains unavailable, but a missing optional FEP must
			// not terminate the MatrixMenu UI.  Gate 17 will restore it.
			CleanupStack::PopAndDestroy(&dataImpl);
			return;
			}
	    // Cannot function without keymapping data.
	    User::Leave(KErrCorrupt);
	    } 
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(text, CONST_OLD, CONST_NEW, "English UID constant")
    start = text.find("\tCPtiKeyMapDataFactory::ListImplementationsL(dataImpl);")
    if start < 0:
        raise SystemExit("InitializeL keymap block: start not found")
    end = text.find("    // Write language->dll mapping data", start)
    if end < 0:
        raise SystemExit("InitializeL keymap block: end not found")
    text = text[:start] + LIST_NEW + "\n" + text[end:]
    return text


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "English implementation": (
            text.count("KPtiKeymappingsDefaultImplementation = 0x10281897") == 1
            and text.count("dataImpl.AppendL(KPtiKeymappingsDefaultImplementation)") == 1
        ),
        "MatrixMenu scope": (
            text.count("RProcess().SecureId().iId == 0x101F4CD2u") == 1
        ),
        "factory leave trapped": (
            text.count("TRAP(htcleoFactoryResult,") == 1
            and text.count("!htcleoMatrixMenuPti") == 1
        ),
        "UI-only final fallback": (
            text.count("CleanupStack::PopAndDestroy(&dataImpl)") == 1
            and text.count("User::Leave(KErrCorrupt)") >= 1
        ),
        "stock other-process failure": text.count("User::Leave(htcleoFactoryResult)") == 1,
        "no timer": "User::After" not in LIST_NEW,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "PtiEngine English fallback verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/inputmethods/textinput/ptienginev2/src/PtiDefaultCore.cpp"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    mmp_path = (
        args.root
        / "sf/mw/inputmethods/textinput/ptienginev2/group/ptienginev2.mmp"
    )
    mmp = mmp_path.read_text(encoding="utf-8")
    if MMP_LIBRARY_OLD in mmp:
        mmp = mmp.replace(MMP_LIBRARY_OLD, MMP_LIBRARY_NEW, 1)
    if mmp.count(MMP_LIBRARY_NEW) != 1 or MMP_LIBRARY_OLD in mmp:
        raise SystemExit("PtiEngine GCCE library-case verification failed")
    mmp_path.write_text(mmp, encoding="utf-8")
    print(
        "HTCLEO_PTIENGINE_MATRIXMENU_ENGLISH_FALLBACK="
        "itut01-10281897-trapped-final-no-fep-gate17"
    )


if __name__ == "__main__":
    main()
