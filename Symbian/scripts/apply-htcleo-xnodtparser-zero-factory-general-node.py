#!/usr/bin/env python3
"""Restore general-node semantics when Xn has zero rendering factories.

On a complete Nokia registry the rendering factory chain marks nonvisual
action nodes as not needing a component.  HTCLEO currently receives an empty
factory list, leaving the stock default true and incorrectly sending
actionshandler/actions/action/event through control creation.  Correct only
that zero-factory, HomeScreen, source-proven set.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE_V1"
PREREQUISITE = "HTCLEO_XN_ODT_VIEW_LOAD_TRACE_V1"

OLD = r'''    TBool componentNodeImplNeeded = ETrue;
    // invoke factory chain
'''

NEW = r'''    TBool componentNodeImplNeeded = ETrue;
    // HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE_V1
    const TBool htcleoZeroFactoryGeneralNode =
        (RProcess().SecureId().iId == 0x102750f0u && count == 0 &&
         (name == KActionsHandlerNodeName ||
          name == KActionsNodeName ||
          name == KActionNodeName ||
          name == KEventNodeName));
    HtcleoXnLoadUiLog(0x48581577u, count,
        HtcleoXnNodeTag(name));
    if (htcleoZeroFactoryGeneralNode)
        {
        componentNodeImplNeeded = EFalse;
        HtcleoXnLoadUiLog(0x48581578u, KErrNone,
            HtcleoXnNodeTag(name));
        }
    // invoke factory chain
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if PREREQUISITE not in text:
        raise SystemExit("zero-factory general-node fix requires ODT trace")
    if text.count(OLD) != 1:
        raise SystemExit("componentNodeImplNeeded anchor mismatch")
    return text.replace(OLD, NEW, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "exact scope": (
            text.count("RProcess().SecureId().iId == 0x102750f0u") == 2
            and text.count("count == 0") == 1
        ),
        "exact general nodes": all(
            NEW.count(f"name == {name}") == 1
            for name in (
                "KActionsHandlerNodeName",
                "KActionsNodeName",
                "KActionNodeName",
                "KEventNodeName",
            )
        ),
        "real stock fallback": (
            text.count("componentNodeImplNeeded = EFalse;") == 1
            and text.count("return ConstructGeneralNodeL( aSource );") == 2
        ),
        "stages": all(
            text.count(f"0x485815{stage}u") == 1 for stage in ("77", "78")
        ),
        "no visual node names": all(
            token not in NEW for token in (
                "KTextNodeName",
                "KImageNodeName",
                "KViewNodeName",
                "KClockNodeName",
            )
        ),
        "no timing or display": all(
            token not in NEW for token in ("User::After", "RTimer", "HalFunction")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Xn zero-factory general-node verification failed: "
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
        "HTCLEO_XN_ZERO_FACTORY_GENERAL_NODE="
        "homescreen-actionshandler-actions-action-event-count0"
    )


if __name__ == "__main__":
    main()
