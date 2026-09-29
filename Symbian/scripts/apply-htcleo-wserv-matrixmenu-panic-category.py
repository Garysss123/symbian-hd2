#!/usr/bin/env python3
"""Record MatrixMenu's full Symbian panic category in the durable WServ log."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY_V1"

ANCHOR = r'''		HtcleoWsLog(0x0000046Du,
			static_cast<TInt>(iClient.ExitType()),
			static_cast<TUint32>(iClient.ExitReason()));
'''

REPLACEMENT = ANCHOR + r'''		// HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY_V1
		const TExitCategoryName htcleoExitCategory=iClient.ExitCategory();
		HtcleoWsLog(0x0000046Eu, htcleoExitCategory.Length(),
			static_cast<TUint32>(iClient.ExitReason()));
		for (TInt htcleoCategoryIndex=0; htcleoCategoryIndex<8;
				++htcleoCategoryIndex)
			{
			const TInt htcleoCharOffset=htcleoCategoryIndex*2;
			TUint32 htcleoPackedCategory=0u;
			if (htcleoCharOffset<htcleoExitCategory.Length())
				htcleoPackedCategory=
					static_cast<TUint32>(htcleoExitCategory[htcleoCharOffset]) << 16;
			if (htcleoCharOffset+1<htcleoExitCategory.Length())
				htcleoPackedCategory|=
					static_cast<TUint32>(htcleoExitCategory[htcleoCharOffset+1]);
			HtcleoWsLog(0x0000046Fu+
				static_cast<TUint32>(htcleoCategoryIndex),
				htcleoCategoryIndex, htcleoPackedCategory);
			}
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if "HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1" not in text:
        raise SystemExit("panic category trace requires teardown attribution first")
    count = text.count(ANCHOR)
    if count != 1:
        raise SystemExit(f"client exit anchor: expected one, found {count}")
    return text.replace(ANCHOR, REPLACEMENT, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "exit category": text.count("iClient.ExitCategory()") == 1,
        "category length": text.count("0x0000046Eu") == 1,
        "eight packed pairs": (
            text.count("htcleoCategoryIndex<8") == 1
            and text.count("0x0000046Fu+") == 1
        ),
        "full descriptor bound": text.count("TExitCategoryName htcleoExitCategory") == 1,
        "original exit trace retained": text.count("0x0000046Du") == 1,
        "reason retained": text.count("iClient.ExitReason()") == 2,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu panic category verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/CLIENT.CPP"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_WSERV_MATRIXMENU_PANIC_CATEGORY="
        "full-16-char-utf16-pairs-046e-0476"
    )


if __name__ == "__main__":
    main()
