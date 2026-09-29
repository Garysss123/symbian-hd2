#!/usr/bin/env python3
"""Return an empty ECom list for the optional FeatureInfo interface only."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_FEATUREINFO_EMPTY_LIST_COMPAT_V1"
INTERFACE_UID = "0x10205057u"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def verify(text: str) -> None:
    checks = {
        "compat marker": text.count(MARKER) == 1,
        "FeatureInfo UID gate": text.count(
            f"aInterfaceUid.iUid == {INTERFACE_UID}"
        ) == 1,
        "empty-list checkpoint": text.count("0x0000F401u") == 1,
        "targeted empty return": text.count(
            "HtcleoEcomServerLog(0x0000F401u, KErrNone,\n"
            "\t\t\t\t\t(TUint32)aImplementationData.Count());\n"
            "\t\t\t\treturn;"
        ) == 1,
        "non-target leave preserved": text.count(
            "User::Leave(KEComErrNoInterfaceIdentified);"
        ) == 1,
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
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/RegistryData.cpp"
    )
    if not source.is_file():
        raise SystemExit(f"missing source: {source}")

    text = source.read_text(encoding="latin-1")
    if MARKER not in text:
        old = (
            "\t\tif(index == KErrNotFound)\n"
            "\t\t\t{\n"
            "\t\t\tHtcleoEcomServerLog(0x0000F3ECu,\n"
            "\t\t\t\tKEComErrNoInterfaceIdentified, 0u);\n"
            "\t\t\tUser::Leave(KEComErrNoInterfaceIdentified);\n"
            "\t\t\t}\n"
        )
        new = (
            "\t\tif(index == KErrNotFound)\n"
            "\t\t\t{\n"
            "\t\t\tHtcleoEcomServerLog(0x0000F3ECu,\n"
            "\t\t\t\tKEComErrNoInterfaceIdentified, 0u);\n"
            f"\t\t\t// {MARKER}\n"
            "\t\t\t// Feature Manager explicitly supports a product with no\n"
            "\t\t\t// adaptation plug-ins.  Preserve stock ECom errors for every\n"
            "\t\t\t// other interface, but represent this one optional interface\n"
            "\t\t\t// as the empty list expected by its existing count==0 path.\n"
            f"\t\t\tif(aInterfaceUid.iUid == {INTERFACE_UID})\n"
            "\t\t\t\t{\n"
            "\t\t\t\tHtcleoEcomServerLog(0x0000F401u, KErrNone,\n"
            "\t\t\t\t\t(TUint32)aImplementationData.Count());\n"
            "\t\t\t\treturn;\n"
            "\t\t\t\t}\n"
            "\t\t\tUser::Leave(KEComErrNoInterfaceIdentified);\n"
            "\t\t\t}\n"
        )
        text = replace_once(text, old, new, "RegistryData no-interface branch")

    verify(text)
    source.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_ECOM_FEATUREINFO_EMPTY_LIST_COMPAT=installed "
        "interface=0x10205057 result=empty-list"
    )


if __name__ == "__main__":
    main()
