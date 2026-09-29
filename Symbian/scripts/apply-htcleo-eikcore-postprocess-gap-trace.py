#!/usr/bin/env python3
"""Split the AknCap E310->E311 pre-factory gap without changing control flow.

The existing ``HtcleoEikCorePreFactoryTrace`` helper is SID-gated and writes
only the boot-local AknCap trace property.  These extra checkpoints isolate
the server-required and background-window operations that run after
``CEikProcess::NewL`` and before the application factory boundary.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCORE_POSTPROCESS_GAP_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    source = replace_once(
        source,
        '\t// Start application as "application server"?\n'
        "\tconst TUint serverDifferentiator = aCommandLine.ServerRequired();\n"
        "\tif (serverDifferentiator)\n"
        "\t\tiEikonEnvFlags.Set(EStartedAsServerApp);",
        f"\t// {MARKER}\n"
        '\t// Start application as "application server"?\n'
        "\tHtcleoEikCorePreFactoryTrace(0xE312u, KErrNone);\n"
        "\tconst TUint serverDifferentiator = aCommandLine.ServerRequired();\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE313u, serverDifferentiator);\n"
        "\tif (serverDifferentiator)\n"
        "\t\t{\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE314u, KErrNone);\n"
        "\t\tiEikonEnvFlags.Set(EStartedAsServerApp);\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE315u, KErrNone);\n"
        "\t\t}",
        "server-required checkpoints",
    )
    source = replace_once(
        source,
        "\t// Push the application to the background?\n"
        "\tif (!startAppInForeground)\n"
        "\t\t{\n"
        "\t\tiRootWin.SetOrdinalPosition(-1000);\n"
        "\t\tiRootWin.EnableReceiptOfFocus(ETrue);\n"
        "\t\tif (RProcess().Priority() <= EPriorityForeground)\n"
        "\t\t\tRThread().SetProcessPriority(EPriorityBackground); \n"
        "\t\t}\n\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE311u, serverDifferentiator);",
        "\t// Push the application to the background?\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE316u, startAppInForeground);\n"
        "\tif (!startAppInForeground)\n"
        "\t\t{\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE317u, KErrNone);\n"
        "\t\tiRootWin.SetOrdinalPosition(-1000);\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE318u, KErrNone);\n"
        "\t\tiRootWin.EnableReceiptOfFocus(ETrue);\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE319u, KErrNone);\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE31Au, KErrNone);\n"
        "\t\tif (RProcess().Priority() <= EPriorityForeground)\n"
        "\t\t\t{\n"
        "\t\t\tHtcleoEikCorePreFactoryTrace(0xE31Bu, KErrNone);\n"
        "\t\t\tRThread().SetProcessPriority(EPriorityBackground);\n"
        "\t\t\tHtcleoEikCorePreFactoryTrace(0xE31Cu, KErrNone);\n"
        "\t\t\t}\n"
        "\t\tHtcleoEikCorePreFactoryTrace(0xE31Du, KErrNone);\n"
        "\t\t}\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE31Eu, startAppInForeground);\n\n"
        "\tHtcleoEikCorePreFactoryTrace(0xE311u, serverDifferentiator);",
        "background-window checkpoints",
    )
    return source


def verify(source: str) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "original E310": source.count(
            "HtcleoEikCorePreFactoryTrace(0xE310u"
        )
        == 1,
        "original E311": source.count(
            "HtcleoEikCorePreFactoryTrace(0xE311u"
        )
        == 1,
        "new stages": all(
            source.count(f"HtcleoEikCorePreFactoryTrace(0x{stage:04X}u") == 1
            for stage in range(0xE312, 0xE31F)
        ),
        "stock server query": source.count(
            "aCommandLine.ServerRequired()"
        )
        >= 1,
        "stock ordinal": source.count("iRootWin.SetOrdinalPosition(-1000)")
        >= 1,
        "stock focus": source.count("iRootWin.EnableReceiptOfFocus(ETrue)")
        >= 1,
        "stock priority": source.count(
            "RThread().SetProcessPriority(EPriorityBackground)"
        )
        >= 1,
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
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKENV.CPP"
    )
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    verify(source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_EIKCORE_POSTPROCESS_GAP_TRACE=installed "
        "stages=E312-E31E property-only behavior-unchanged"
    )


if __name__ == "__main__":
    main()
