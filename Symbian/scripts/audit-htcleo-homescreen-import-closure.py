#!/usr/bin/env python3
"""Resolve the stock HomeScreen E32 import closure against a prepared ROM."""

from __future__ import annotations

import argparse
import re
import subprocess
from collections import deque
from pathlib import Path, PureWindowsPath


SEEDS = (
    "ailaunch.exe",
    "homescreen.exe",
    "aiutils.dll",
    "aiidleint.dll",
    "aifw.dll",
    "swiutils.dll",
    "ai3xmluimain.dll",
    "Ai3NatiUi.dll",
    "aicontainer.dll",
    "xn3ecomelementproxy.dll",
    "xn3layoutengine.dll",
    "cpswrapper.dll",
    "hspswrapper.dll",
    "xn3utils.dll",
    "xn3domdocument.dll",
    "xn3odt.dll",
    "xn3resource.dll",
    "hscontentcontrol.dll",
    "extrenderingplugin.dll",
    "xn3textfactory.dll",
    "xn3viewfactory.dll",
    "xn3bitmapfactory.dll",
    "xn3menufactory.dll",
    "xn3domvisitor.dll",
    "xn3popupfactory.dll",
    "xn3newstickerfactory.dll",
    "xn3volumecontrolfactory.dll",
    "xn3clockfactory.dll",
    "xn3nppluginfactory.dll",
    "xn3texteditorfactory.dll",
    "xn3animationfactory.dll",
    # HomeScreen Plugin Service (HSPS) runtime closure.
    "hspsdomdocument.dll",
    "hspsresource.dll",
    "hspsresult.dll",
    "hspsodt.dll",
    "hspsdefrep.dll",
    "hspsdefinitionengineinterface.dll",
    "hspsdefinitionengine.dll",
    "hspsclient.dll",
    "hspsclientsession.dll",
    "hspsrequestclient.dll",
    "hspsthemeserver.exe",
    "hspsservice.dll",
    "hspsprovider.dll",
    "hspluginsettings.dll",
    "hswidgetpublisher.dll",
    # Content Publishing and Content Control services used by the XML shell.
    "cpclient.dll",
    "cpserver.exe",
    "cpstorage.dll",
    "cputils.dll",
    "contentharvesterclient.dll",
    "contentharvester.exe",
    "pluginvalidator.dll",
    "chswiplugin.dll",
    "chfactorysettingsplugin.dll",
    "ccclientsession.dll",
    "ccsrvapi.dll",
    "hsccapiclient.dll",
    "hsccproviderclient.dll",
    "hscontentinfo.dll",
    "ccserver.exe",
    # Shell lifecycle and non-cellular menu/widget integrations.
    "actionhandlerplugins.dll",
    "actionhandlerservice.dll",
    "bsservice.dll",
    "bsengine.exe",
    "widgetmanager.dll",
    "mcsprovider.dll",
    "mcsplugin.dll",
    "mcspluginhandler.dll",
    "mcspluginsettings.dll",
    "aiwsplugin.dll",
    "sapidataplugin.dll",
    "wrtdataplugin.dll",
)

DESTINATION = re.compile(r'"([^"\r\n]+)"\s*(?:\s|$)')
IMPORT = re.compile(r"^\d+ imports from ([^\s{\[]+).*[.]dll$", re.MULTILINE)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("recipe", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    release = args.root / "epoc32/release/armv5/urel"
    elf2e32 = args.root / "epoc32/tools/elf2e32"
    if not release.is_dir() or not elf2e32.is_file() or not args.recipe.is_file():
        raise SystemExit("HomeScreen closure inputs are missing")

    available = {
        path.name.lower(): path
        for path in release.iterdir()
        if path.is_file()
    }
    present: set[str] = set()
    for line in args.recipe.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lstrip().lower().startswith("rem"):
            continue
        quoted = DESTINATION.findall(line)
        if quoted:
            present.add(PureWindowsPath(quoted[-1]).name.lower())

    queue: deque[str] = deque(name.lower() for name in SEEDS)
    visited: set[str] = set()
    required: dict[str, tuple[Path, str]] = {}
    unresolved: set[tuple[str, str]] = set()

    while queue:
        name = queue.popleft()
        if name in visited:
            continue
        visited.add(name)
        path = available.get(name)
        if path is None:
            unresolved.add((name, "seed-or-import"))
            continue
        if name not in present:
            required[name] = (path, "seed" if name in {s.lower() for s in SEEDS} else "import")
        proc = subprocess.run(
            [str(elf2e32), "--dump=i", f"--e32input={path}"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for imported in IMPORT.findall(proc.stdout):
            imported_name = imported.lower() + ".dll"
            if imported_name not in present and imported_name not in visited:
                if imported_name not in available:
                    unresolved.add((imported_name, name))
                else:
                    queue.append(imported_name)

    lines = [
        "STATUS=HTCLEO_HOMESCREEN_IMPORT_CLOSURE_OK" if not unresolved
        else "STATUS=HTCLEO_HOMESCREEN_IMPORT_CLOSURE_UNRESOLVED",
        f"SEEDS={len(SEEDS)}",
        f"VISITED={len(visited)}",
        f"ROM_PRESENT={len(visited) - len(required)}",
        f"ADD_BINARIES={len(required)}",
        f"UNRESOLVED={len(unresolved)}",
        "",
        "# disposition\tfilename\tsource",
    ]
    for name, (path, reason) in sorted(required.items()):
        lines.append(f"ADD_{reason.upper()}\t{name}\t{path}")
    for name, parent in sorted(unresolved):
        lines.append(f"UNRESOLVED\t{name}\t{parent}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:7]))
    if unresolved:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
