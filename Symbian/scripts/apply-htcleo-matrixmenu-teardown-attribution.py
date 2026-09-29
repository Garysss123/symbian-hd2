#!/usr/bin/env python3
"""Attribute the MatrixMenu grid/window teardown without changing lifetime."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(
    client: str,
    cliwin: str,
    grid: str,
    appui: str,
) -> tuple[str, str, str, str]:
    marker_counts = [
        client.count(MARKER),
        cliwin.count(MARKER),
        grid.count(MARKER),
        appui.count(MARKER),
    ]
    if marker_counts == [1, 1, 1, 1]:
        return client, cliwin, grid, appui
    if any(marker_counts):
        raise SystemExit(
            "partial teardown attribution install: " + repr(marker_counts)
        )

    client = replace_once(
        client,
        "CWsClient::~CWsClient()\n\t{\n",
        "CWsClient::~CWsClient()\n"
        "\t{\n"
        "\t// HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
        "\tif (SecureId().iId==0x101F4CD2u)\n"
        "\t\t{\n"
        "\t\tHtcleoWsLog(0x0000046Du,\n"
        "\t\t\tstatic_cast<TInt>(iClient.ExitType()),\n"
        "\t\t\tstatic_cast<TUint32>(iClient.ExitReason()));\n"
        "\t\t}\n",
        "WServ client destructor",
    )

    cliwin = replace_once(
        cliwin,
        "CWsClientWindow::~CWsClientWindow()\n"
        "\t{\n"
        "\tif (gHtcleoPublishedGridWindow==this)\n"
        "\t\tgHtcleoPublishedGridWindow=NULL;\n",
        "CWsClientWindow::~CWsClientWindow()\n"
        "\t{\n"
        "\t// HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
        "\tif (gHtcleoPublishedGridWindow==this)\n"
        "\t\t{\n"
        "\t\tHtcleoMatrixMenuWsLog(WsOwner(), iClientHandle,\n"
        "\t\t\t0x0000046Cu, KErrNone,\n"
        "\t\t\tstatic_cast<TUint32>(reinterpret_cast<TUint>(this)));\n"
        "\t\tgHtcleoPublishedGridWindow=NULL;\n"
        "\t\t}\n",
        "published grid window destructor",
    )

    grid = replace_once(
        grid,
        "CMmGridContainer::~CMmGridContainer()\n"
        "    {\n"
        "    delete iGrid;\n"
        "    }\n",
        "CMmGridContainer::~CMmGridContainer()\n"
        "    {\n"
        "    // HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
        "    HtcleoMmwLog(0x4D570182u, KErrNone,\n"
        "        static_cast<TUint32>(reinterpret_cast<TUint>(this)));\n"
        "    delete iGrid;\n"
        "    }\n",
        "MMWidgets grid container destructor",
    )

    appui = replace_once(
        appui,
        "CMmAppUi::~CMmAppUi()\n"
        "    {\n"
        "    DEBUG((\"_Mm_:CMmAppUi::~CMmAppUi IN\"));\n",
        "CMmAppUi::~CMmAppUi()\n"
        "    {\n"
        "    // HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
        "    HtcleoMenuLog(0x4D4D1250u, iGarbage.Count(),\n"
        "        static_cast<TUint32>(reinterpret_cast<TUint>(iCurrentContainer)));\n"
        "    DEBUG((\"_Mm_:CMmAppUi::~CMmAppUi IN\"));\n",
        "MatrixMenu AppUi destructor",
    )
    appui = replace_once(
        appui,
        "void CMmAppUi::ResetContainerMap()\n"
        "    {\n"
        "    THashMapIter< TInt, CMmWidgetContainer* > iterator( iContainerMap );\n",
        "void CMmAppUi::ResetContainerMap()\n"
        "    {\n"
        "    HtcleoMenuLog(0x4D4D1251u, iContainerMap.Count(),\n"
        "        static_cast<TUint32>(reinterpret_cast<TUint>(iCurrentContainer)));\n"
        "    THashMapIter< TInt, CMmWidgetContainer* > iterator( iContainerMap );\n",
        "MatrixMenu ResetContainerMap",
    )
    appui = replace_once(
        appui,
        "    if ( aMessage.Find( KRootWithPref ) != KErrNotFound )\n"
        "        {\n"
        "        RemoveFromStack( iCurrentContainer );\n",
        "    if ( aMessage.Find( KRootWithPref ) != KErrNotFound )\n"
        "        {\n"
        "        HtcleoMenuLog(0x4D4D1252u, aMessage.Length(),\n"
        "            static_cast<TUint32>(reinterpret_cast<TUint>(iCurrentContainer)));\n"
        "        RemoveFromStack( iCurrentContainer );\n",
        "MatrixMenu root message reset",
    )
    appui = replace_once(
        appui,
        "            case ESuiteModelDestroyed:\n"
        "                {\n"
        "                iCurrentContainer->PrepareForGarbage();\n",
        "            case ESuiteModelDestroyed:\n"
        "                {\n"
        "                HtcleoMenuLog(0x4D4D1253u, KErrNone,\n"
        "                    static_cast<TUint32>(reinterpret_cast<TUint>(iCurrentContainer)));\n"
        "                iCurrentContainer->PrepareForGarbage();\n",
        "MatrixMenu suite destroyed",
    )
    appui = replace_once(
        appui,
        "void CMmAppUi::ResetToInitialStateL()\n"
        "    {\n"
        "    if (iDummyContainer)\n",
        "void CMmAppUi::ResetToInitialStateL()\n"
        "    {\n"
        "    HtcleoMenuLog(0x4D4D1254u, KErrNone,\n"
        "        static_cast<TUint32>(reinterpret_cast<TUint>(iCurrentContainer)));\n"
        "    if (iDummyContainer)\n",
        "MatrixMenu reset initial state",
    )
    appui = replace_once(
        appui,
        "        iCurrentSuiteModel = aModel;\n"
        "        ShowSuiteL();\n"
        "        iGarbage.ResetAndDestroy();\n",
        "        iCurrentSuiteModel = aModel;\n"
        "        ShowSuiteL();\n"
        "        HtcleoMenuLog(0x4D4D1255u, iGarbage.Count(),\n"
        "            static_cast<TUint32>(reinterpret_cast<TUint>(iCurrentContainer)));\n"
        "        iGarbage.ResetAndDestroy();\n",
        "MatrixMenu post-ShowSuite garbage collection",
    )
    return client, cliwin, grid, appui


def verify(client: str, cliwin: str, grid: str, appui: str) -> None:
    combined = "\n".join((client, cliwin, grid, appui))
    checks = {
        "four source markers": combined.count(MARKER) == 4,
        "window teardown stage": combined.count("0x0000046Cu") == 1,
        "client exit stage": combined.count("0x0000046Du") == 1,
        "grid destructor stage": combined.count("0x4D570182u") == 1,
        "AppUi destructor stage": combined.count("0x4D4D1250u") == 1,
        "container map reset stage": combined.count("0x4D4D1251u") == 1,
        "root message stage": combined.count("0x4D4D1252u") == 1,
        "suite destroyed stage": combined.count("0x4D4D1253u") == 1,
        "initial reset stage": combined.count("0x4D4D1254u") == 1,
        "garbage collection stage": combined.count("0x4D4D1255u") == 1,
        "lifetime logic retained": (
            cliwin.count("gHtcleoPublishedGridWindow=NULL") == 1
            and appui.count("iGarbage.ResetAndDestroy();") >= 3
            and appui.count("ResetContainerMap();") >= 3
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu teardown attribution verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    wserv = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    matrixmenu = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    mmgrid = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/mmwidgets/src/mmgridcontainer.cpp"
    )
    paths = (
        wserv / "openwfc/CLIENT.CPP",
        wserv / "openwfc/cliwin.cpp",
        mmgrid,
        matrixmenu,
    )
    texts = [path.read_text(encoding="utf-8") for path in paths]
    installed = install(*texts)
    verify(*installed)
    for path, text in zip(paths, installed):
        path.write_text(text, encoding="utf-8")

    print(
        "HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION="
        "wserv-window-client-mmwidgets-container-appui-reset-gc-046c-046d-0182-1250-1255"
    )


if __name__ == "__main__":
    main()
