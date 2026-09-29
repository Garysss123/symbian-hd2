#!/usr/bin/env python3
"""Accept a missing renderer only for Xn nonvisual action nodes.

Hardware 709 proves CreateFactoryControlL leaves with KErrServerTerminated
before the central ECom list handler is entered.  Trap the real PluginsL call
inside the already tracked xn3layoutengine and preserve an empty factory list
only for HomeScreen actions/action/event nodes.  Visual node failures remain
fatal and observable.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN_V1"
PREREQUISITE = "HTCLEO_XN_ODT_VIEW_LOAD_TRACE_V1"

OLD = "    iEcomHandler.PluginsL( interfaceUid, aName, *factories );\n"

NEW = r'''    // HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN_V1
    const TBool htcleoHomeNonvisualFactory =
        (RProcess().SecureId().iId == 0x102750f0u &&
         interfaceUid.iUid == 0x20019592u &&
         (aName.Compare(_L8("actions")) == 0 ||
          aName.Compare(_L8("action")) == 0 ||
          aName.Compare(_L8("event")) == 0));
    HtcleoXnLoadUiLog(0x485815A8u, KErrNone,
        HtcleoXnNodeTag(aName));
    TRAPD(htcleoFactoryListError,
        iEcomHandler.PluginsL( interfaceUid, aName, *factories ));
    HtcleoXnLoadUiLog(0x485815A9u, htcleoFactoryListError,
        (TUint32)interfaceUid.iUid);
    if (htcleoHomeNonvisualFactory &&
        htcleoFactoryListError == KErrServerTerminated)
        {
        // No renderer is the stock-valid state for these general nodes.
        factories->Container().Reset();
        HtcleoXnLoadUiLog(0x485815AAu, htcleoFactoryListError,
            HtcleoXnNodeTag(aName));
        htcleoFactoryListError = KErrNone;
        }
    User::LeaveIfError(htcleoFactoryListError);
    HtcleoXnLoadUiLog(0x485815ABu, factories->Container().Count(),
        HtcleoXnNodeTag(aName));
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("nonvisual factory fail-open requires ODT view trace")
    if text.count(OLD) != 1:
        raise SystemExit("CreateFactoryControlL PluginsL anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    zero_factory_general = "HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE_V1" in text
    metadata_extended = "HTCLEO_XN_METADATA_FACTORY_FAILOPEN_V1" in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "real call trapped once": (
            text.count("TRAPD(htcleoFactoryListError,") == 1
            and text.count(
                "iEcomHandler.PluginsL( interfaceUid, aName, *factories )"
            ) == 1
            and text.count("User::LeaveIfError(htcleoFactoryListError)") == 1
        ),
        "exact SID/interface": (
            text.count("RProcess().SecureId().iId == 0x102750f0u")
            == (2 if zero_factory_general else 1)
            and text.count("interfaceUid.iUid == 0x20019592u") == 1
        ),
        "three nonvisual types": (
            all(
                text.count(f'aName.Compare(_L8("{name}")) == 0') == 1
                for name in ("actions", "action", "event")
            )
            or (
                metadata_extended
                and all(
                    text.count(f"aName == {name}") == 1
                    for name in (
                        "KActionsNodeName",
                        "KActionNodeName",
                        "KEventNodeName",
                    )
                )
            )
        ),
        "visual failures retained": all(
            token not in NEW for token in ('_L8("text")', '_L8("image")', '_L8("view")')
        ),
        "stages": all(
            text.count(f"0x485815{stage}u") == 1
            for stage in ("A8", "A9", "AA", "AB")
        ),
        "no timing or display": all(
            token not in NEW for token in ("User::After", "RTimer", "HalFunction")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Xn nonvisual factory fail-open verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / (
        "sf/app/homescreen/idlehomescreen/xmluirendering/"
        "uiengine/src/xnodtparser.cpp"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_XN_NONVISUAL_FACTORY_FAILOPEN="
        "homescreen-20019592-actions-action-event-serverterminated-empty"
    )


if __name__ == "__main__":
    main()
