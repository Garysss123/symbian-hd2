#!/usr/bin/env python3
"""Make Feature Manager's existing zero-plugin branch reachable on ECom."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_FEATMGRSERVER_ZERO_PLUGIN_COMPAT_V1"
INCLUDE = "#include <ecom/ecomerrorcodes.h>"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(text: str) -> None:
    checks = {
        "compat marker": text.count(MARKER) == 1,
        "error-code include": text.count(INCLUDE) == 1,
        "no-interface comparison": (
            text.count("listResult == KEComErrNoInterfaceIdentified") == 1
        ),
        "empty-list normalization": text.count("listResult = KErrNone;") == 2,
        "stock leave remains": text.count("User::LeaveIfError(listResult);") == 1,
        "stock zero-count branch remains": text.count("if (count == 0)") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source = (
        args.root
        / "sf/os/persistentdata/featuremgmt/featuremgr/src/serverexe/featmgrserver.cpp"
    )
    if not source.is_file():
        raise SystemExit(f"missing source: {source}")

    text = source.read_text(encoding="latin-1")
    if MARKER not in text:
        if INCLUDE not in text:
            text = replace_once(
                text,
                "#include <ecom/ecom.h>\n",
                "#include <ecom/ecom.h>\n" + INCLUDE + "\n",
                "ECom include",
            )
        text = replace_once(
            text,
            "    HtcleoFeatMgrServerTrace(0xE644u, listResult);\n"
            "    User::LeaveIfError(listResult);\n",
            "    HtcleoFeatMgrServerTrace(0xE644u, listResult);\n"
            f"    // {MARKER}\n"
            "    // A product is allowed to have no adaptation plug-ins.  ECom\n"
            "    // reports that state as a leave, while the stock code below\n"
            "    // already has an explicit zero-count path.  Normalize only this\n"
            "    // one result so the intended path can execute; preserve every\n"
            "    // other resolver, registry and leave result unchanged.\n"
            "    if (listResult == KEComErrNoInterfaceIdentified)\n"
            "        {\n"
            "        listResult = KErrNone;\n"
            "        }\n"
            "    User::LeaveIfError(listResult);\n",
            "ListImplementations result",
        )

    verify(text)
    source.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_FEATMGRSERVER_ZERO_PLUGIN_COMPAT=installed "
        "result=KEComErrNoInterfaceIdentified-to-empty-list"
    )


if __name__ == "__main__":
    main()
