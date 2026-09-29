#!/usr/bin/env python3
"""Do not persistently delete real HomeScreen views on transient ECom loss."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XNROOT_TRANSIENT_VIEW_PRESERVE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    text = replace_once(
        text,
        "                // Initial view failed                \n"
        "                iManager.RemoveFaultyView( plugin );",
        "                // HTCLEO_XNROOT_TRANSIENT_VIEW_PRESERVE_V1\n"
        "                // A restarted ECom server is not evidence that the real\n"
        "                // HSPS view is corrupt.  Return this transient result and\n"
        "                // preserve all persistent view IDs for the next process.\n"
        "                if ( err == KErrServerTerminated )\n"
        "                    {\n"
        "                    HtcleoXnLoadUiLog(0x4858152Eu, err,\n"
        "                        (TUint32)iPluginsData.Count());\n"
        "                    return err;\n"
        "                    }\n"
        "\n"
        "                // Initial view failed                \n"
        "                iManager.RemoveFaultyView( plugin );",
        "initial view preservation",
    )
    return replace_once(
        text,
        "            // View failed, remove it    \n"
        "            iManager.RemoveFaultyView( plugin );",
        "            if ( htcleoFallbackError == KErrServerTerminated )\n"
        "                {\n"
        "                HtcleoXnLoadUiLog(0x4858152Fu,\n"
        "                    htcleoFallbackError,\n"
        "                    (TUint32)iPluginsData.Count());\n"
        "                return htcleoFallbackError;\n"
        "                }\n"
        "\n"
        "            // View failed, remove it    \n"
        "            iManager.RemoveFaultyView( plugin );",
        "fallback view preservation",
    )


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "initial guard": text.count("if ( err == KErrServerTerminated )") == 1,
        "fallback guard": text.count("if ( htcleoFallbackError == KErrServerTerminated )") == 1,
        "stages": text.count("0x4858152Eu") == 1 and text.count("0x4858152Fu") == 1,
        "stock removals retained": text.count("iManager.RemoveFaultyView( plugin )") == 2,
        "stock deletes retained": text.count("delete plugin;") >= 2,
        "transient propagated": text.count("return err;") >= 2 and text.count("return htcleoFallbackError;") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Xn root transient-view verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/app/homescreen/idlehomescreen/xmluirendering/"
        "uiengine/src/xnrootdata.cpp"
    )
    text = install(path.read_text(encoding="utf-8"))
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_XNROOT_TRANSIENT_VIEW_PRESERVE="
        "keerrserverterminated-no-persistent-remove"
    )


if __name__ == "__main__":
    main()
