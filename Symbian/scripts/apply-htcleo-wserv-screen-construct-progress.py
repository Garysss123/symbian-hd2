#!/usr/bin/env python3
"""Add fail-open WSLOG checkpoints through first-screen construction.

Iteration 427 proved WServ reaches InitScreenL stage 0x21 and then remains
inside CScreen::ConstructL.  These checkpoints stay in the existing sole
WServ writer and bracket CScreen, CScreenRedraw and render-stage-chain setup
without changing error handling, waits or plugin selection.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MACRO = "__HTCLEO_WSERV_DURABLE_LOG__"
SCREEN_MARKER = "HTCLEO_WSERV_SCREEN_CONSTRUCT_PROGRESS_V1_SCREEN"
REDRAW_MARKER = "HTCLEO_WSERV_SCREEN_CONSTRUCT_PROGRESS_V1_REDRAW"
MANAGER_MARKER = "HTCLEO_WSERV_SCREEN_CONSTRUCT_PROGRESS_V1_MANAGER"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def declaration(marker: str) -> str:
    return f'''\n#ifdef {MACRO}
// {marker}
extern void HtcleoWsLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoWsLog(TUint32, TInt, TUint32) {{}}
#endif
'''


def patch_screen(source: str) -> str:
    if SCREEN_MARKER in source:
        return source
    source = replace_once(
        source,
        "GLREF_D CDebugLogBase *wsDebugLog;\n",
        "GLREF_D CDebugLogBase *wsDebugLog;\n" + declaration(SCREEN_MARKER),
        "screen logger declaration",
    )
    source = replace_once(
        source,
        "void CScreen::ConstructL(const TRect& aDigitiserArea, TInt aScreenNumber)\n\t{\n\tiScreenNumber = aScreenNumber ;",
        "void CScreen::ConstructL(const TRect& aDigitiserArea, TInt aScreenNumber)\n\t{\n"
        "\tHtcleoWsLog(0x00000100u, KErrNone, (TUint32)aScreenNumber);\n"
        "\tiScreenNumber = aScreenNumber ;",
        "screen ConstructL entry",
    )
    source = replace_once(
        source,
        "\tiRedraw = CScreenRedraw::NewL(*this);\n\tiScreenDevice = iRedraw->ObjectInterface<MWsScreenDevice>();",
        "\tHtcleoWsLog(0x00000101u, KErrNone, (TUint32)aScreenNumber);\n"
        "\tiRedraw = CScreenRedraw::NewL(*this);\n"
        "\tHtcleoWsLog(0x00000102u, KErrNone, (TUint32)(iRedraw != NULL));\n"
        "\tiScreenDevice = iRedraw->ObjectInterface<MWsScreenDevice>();\n"
        "\tHtcleoWsLog(0x00000103u, KErrNone, (TUint32)(iScreenDevice != NULL));",
        "screen redraw and device",
    )
    source = replace_once(
        source,
        "\tiScene = iRedraw->ObjectInterface<MWsScene>();\n\tWS_ASSERT_ALWAYS(iScene, EWsPanicSceneMissing);",
        "\tiScene = iRedraw->ObjectInterface<MWsScene>();\n"
        "\tHtcleoWsLog(0x00000104u, KErrNone, (TUint32)(iScene != NULL));\n"
        "\tWS_ASSERT_ALWAYS(iScene, EWsPanicSceneMissing);",
        "screen scene interface",
    )
    source = replace_once(
        source,
        "\tiDeviceMap = CGraphicsDeviceMap::NewL(*iScreenDevice);\n\n\tiDisplayControl",
        "\tiDeviceMap = CGraphicsDeviceMap::NewL(*iScreenDevice);\n"
        "\tHtcleoWsLog(0x00000105u, KErrNone, (TUint32)(iDeviceMap != NULL));\n\n"
        "\tiDisplayControl",
        "screen device map",
    )
    source = replace_once(
        source,
        "\tiDisplayPolicy = MWsScreen::ObjectInterface<MWsDisplayPolicy>();\n\n\n\t// initialize",
        "\tiDisplayPolicy = MWsScreen::ObjectInterface<MWsDisplayPolicy>();\n"
        "\tHtcleoWsLog(0x00000106u, KErrNone,\n"
        "\t\t((TUint32)(iDisplayControl != NULL) << 2) |\n"
        "\t\t((TUint32)(iDisplayMapping != NULL) << 1) |\n"
        "\t\t(TUint32)(iDisplayPolicy != NULL));\n\n"
        "\t// initialize",
        "screen display interfaces",
    )
    source = replace_once(
        source,
        "\tLoadScreenSizesL(iScreenDevice->SizeInPixels());\n\tiFallbackMap = CFallbackMap::NewL(this);",
        "\tLoadScreenSizesL(iScreenDevice->SizeInPixels());\n"
        "\tHtcleoWsLog(0x00000107u, KErrNone, (TUint32)iNumScreenSizeModes);\n"
        "\tiFallbackMap = CFallbackMap::NewL(this);\n"
        "\tHtcleoWsLog(0x00000108u, KErrNone, (TUint32)(iFallbackMap != NULL));",
        "screen sizes and fallback",
    )
    source = replace_once(
        source,
        "\tLoadScreenSizeProperties(iScreenDevice->DisplayMode());\n\n\tif (iDisplayPolicy)",
        "\tLoadScreenSizeProperties(iScreenDevice->DisplayMode());\n"
        "\tHtcleoWsLog(0x00000109u, KErrNone, (TUint32)iScreenSizeMode);\n\n"
        "\tif (iDisplayPolicy)",
        "screen size properties",
    )
    source = replace_once(
        source,
        "\t\tiDisplayPolicy->NewAppModesAvailable();\n\t\t}\n\t\n\tiDigitiserArea",
        "\t\tiDisplayPolicy->NewAppModesAvailable();\n\t\t}\n"
        "\tHtcleoWsLog(0x0000010Au, KErrNone, (TUint32)(iDisplayPolicy != NULL));\n\t\n"
        "\tiDigitiserArea",
        "screen display policy",
    )
    source = replace_once(
        source,
        "\tSetInitialScreenSizeModeAndRotation(); //get the first/lowest valid mode.  Also calls SetDigitiserAreas\n\t\n\tApplyRemainingWsiniSettingsL();",
        "\tSetInitialScreenSizeModeAndRotation(); //get the first/lowest valid mode.  Also calls SetDigitiserAreas\n"
        "\tHtcleoWsLog(0x0000010Bu, KErrNone, (TUint32)iScreenSizeMode);\n\t\n"
        "\tApplyRemainingWsiniSettingsL();\n"
        "\tHtcleoWsLog(0x0000010Cu, KErrNone, 0u);",
        "screen mode and settings",
    )
    source = replace_once(
        source,
        "\tiRootWindow = new (ELeave) CWsRootWindow(NULL, this);\n\tiRootWindow->ConstructL();",
        "\tiRootWindow = new (ELeave) CWsRootWindow(NULL, this);\n"
        "\tHtcleoWsLog(0x0000010Du, KErrNone, (TUint32)(iRootWindow != NULL));\n"
        "\tiRootWindow->ConstructL();\n"
        "\tHtcleoWsLog(0x0000010Eu, KErrNone, 0u);",
        "screen root window",
    )
    source = replace_once(
        source,
        "\tiSpriteManager = CWsSpriteManager::NewL();\n\n\tInitializeSceneL();\n\tInitializeUiElementsL();",
        "\tiSpriteManager = CWsSpriteManager::NewL();\n"
        "\tHtcleoWsLog(0x0000010Fu, KErrNone, (TUint32)(iSpriteManager != NULL));\n\n"
        "\tInitializeSceneL();\n"
        "\tHtcleoWsLog(0x00000110u, KErrNone, 0u);\n"
        "\tInitializeUiElementsL();\n"
        "\tHtcleoWsLog(0x00000111u, KErrNone, 0u);",
        "screen scene and UI",
    )
    source = replace_once(
        source,
        "\tiSurfaceMap = new (ELeave) CRegisteredSurfaceMap(*iScene);\n\t\n\t//if the interface",
        "\tiSurfaceMap = new (ELeave) CRegisteredSurfaceMap(*iScene);\n"
        "\tHtcleoWsLog(0x00000112u, KErrNone, (TUint32)(iSurfaceMap != NULL));\n\t\n"
        "\t//if the interface",
        "screen surface map",
    )
    source = replace_once(
        source,
        "\t\tiConfigChangeNotifier->IssueNotificationRequest();\n\t\t}\n\tdoSetScreenMode(iScreenSizeMode,ETrue);\n\t}",
        "\t\tiConfigChangeNotifier->IssueNotificationRequest();\n\t\t}\n"
        "\tHtcleoWsLog(0x00000113u, KErrNone, (TUint32)(iDisplayControl != NULL));\n"
        "\tdoSetScreenMode(iScreenSizeMode,ETrue);\n"
        "\tHtcleoWsLog(0x00000114u, KErrNone, (TUint32)iScreenSizeMode);\n\t}",
        "screen final mode",
    )
    return source


def patch_redraw(source: str) -> str:
    if REDRAW_MARKER in source:
        return source
    source = replace_once(
        source,
        "GLREF_D CDebugLogBase *wsDebugLog;\n",
        "GLREF_D CDebugLogBase *wsDebugLog;\n" + declaration(REDRAW_MARKER),
        "redraw logger declaration",
    )
    source = replace_once(
        source,
        "CScreenRedraw * CScreenRedraw::NewL(CScreen& aScreen)\n\t{\n\tCScreenRedraw * self = new (ELeave) CScreenRedraw(aScreen);",
        "CScreenRedraw * CScreenRedraw::NewL(CScreen& aScreen)\n\t{\n"
        "\tHtcleoWsLog(0x00000200u, KErrNone, (TUint32)aScreen.ScreenNumber());\n"
        "\tCScreenRedraw * self = new (ELeave) CScreenRedraw(aScreen);\n"
        "\tHtcleoWsLog(0x00000201u, KErrNone, (TUint32)(self != NULL));",
        "redraw NewL entry",
    )
    source = replace_once(
        source,
        "\tself->ConstructL();\n\tCleanupStack::Pop(self);\n\treturn self;",
        "\tself->ConstructL();\n"
        "\tHtcleoWsLog(0x00000202u, KErrNone, 0u);\n"
        "\tCleanupStack::Pop(self);\n"
        "\tHtcleoWsLog(0x00000203u, KErrNone, (TUint32)(self != NULL));\n"
        "\treturn self;",
        "redraw NewL return",
    )
    source = replace_once(
        source,
        "void CScreenRedraw::ConstructL()\n\t{\n\t\n\tLEAVE_LOG_INSTALL_C;",
        "void CScreenRedraw::ConstructL()\n\t{\n"
        "\tHtcleoWsLog(0x00000210u, KErrNone, (TUint32)iScreen.ScreenNumber());\n\t\n"
        "\tLEAVE_LOG_INSTALL_C;\n"
        "\tHtcleoWsLog(0x00000211u, KErrNone, 0u);",
        "redraw ConstructL entry",
    )
    source = replace_once(
        source,
        "\tiRenderStages = CRenderStageManager::ConnectL(\n",
        "\tHtcleoWsLog(0x00000212u, KErrNone, 0u);\n"
        "\tiRenderStages = CRenderStageManager::ConnectL(\n",
        "redraw connect pre",
    )
    source = replace_once(
        source,
        "\t\t\t\t\t\t);\n\t\n\tLEAVE_LOG_UNINSTALL_C;",
        "\t\t\t\t\t\t);\n"
        "\tHtcleoWsLog(0x00000213u, KErrNone, (TUint32)(iRenderStages != NULL));\n\t\n"
        "\tLEAVE_LOG_UNINSTALL_C;\n"
        "\tHtcleoWsLog(0x00000214u, KErrNone, 0u);",
        "redraw connect post",
    )
    source = replace_once(
        source,
        "\tiRenderStageTextCursor = static_cast<MWsTextCursor*>(iRenderStages->ResolveObjectInterface(KMWsTextCursor));\n\tWS_ASSERT_ALWAYS(iRenderStageTextCursor, EWsPanicTextCursorInterfaceMissing);",
        "\tiRenderStageTextCursor = static_cast<MWsTextCursor*>(iRenderStages->ResolveObjectInterface(KMWsTextCursor));\n"
        "\tHtcleoWsLog(0x00000215u, KErrNone, (TUint32)(iRenderStageTextCursor != NULL));\n"
        "\tWS_ASSERT_ALWAYS(iRenderStageTextCursor, EWsPanicTextCursorInterfaceMissing);\n"
        "\tHtcleoWsLog(0x00000216u, KErrNone, 0u);",
        "redraw cursor interface",
    )
    return source


def patch_manager(source: str) -> str:
    if MANAGER_MARKER in source:
        return source
    source = replace_once(
        source,
        "GLREF_D CDebugLogBase *wsDebugLog;\n",
        "GLREF_D CDebugLogBase *wsDebugLog;\n" + declaration(MANAGER_MARKER),
        "manager logger declaration",
    )
    source = replace_once(
        source,
        "LOCAL_C\tCWsRenderStage *ConstructRenderStageChain(HBufC* reversedRenderStageList, TInt aScreenNumber, MWsScreen *aScreen, MWsScreenRedraw *aScreenRedraw)\n\t{\n\tTInt err = KErrNone;",
        "LOCAL_C\tCWsRenderStage *ConstructRenderStageChain(HBufC* reversedRenderStageList, TInt aScreenNumber, MWsScreen *aScreen, MWsScreenRedraw *aScreenRedraw)\n\t{\n"
        "\tHtcleoWsLog(0x00000310u, KErrNone, (TUint32)reversedRenderStageList->Length());\n"
        "\tTInt err = KErrNone;",
        "manager chain entry",
    )
    source = replace_once(
        source,
        "\tCWsPluginManager * pluginMgr = CWsTop::PluginManager();\n\n\tif (!pluginMgr)",
        "\tCWsPluginManager * pluginMgr = CWsTop::PluginManager();\n"
        "\tHtcleoWsLog(0x00000311u, KErrNone, (TUint32)(pluginMgr != NULL));\n\n"
        "\tif (!pluginMgr)",
        "manager plugin manager",
    )
    source = replace_once(
        source,
        "\tTLex lex(*reversedRenderStageList);\n\n\twhile (true)",
        "\tTLex lex(*reversedRenderStageList);\n"
        "\tTUint32 htcleoStageIndex = 0u;\n\n"
        "\twhile (true)",
        "manager stage index",
    )
    source = replace_once(
        source,
        "\t\tTPtrC ptr = lex.NextToken();\n\t\tif (ptr.Length() > 0)",
        "\t\tTPtrC ptr = lex.NextToken();\n"
        "\t\tTUint32 htcleoToken = ((TUint32)(ptr.Length() ? ptr[0] : 0) << 16) |\n"
        "\t\t\t((TUint32)ptr.Length() & 0xFFFFu);\n"
        "\t\tHtcleoWsLog(0x00000320u, (TInt)htcleoStageIndex, htcleoToken);\n"
        "\t\tif (ptr.Length() > 0)",
        "manager token",
    )
    source = replace_once(
        source,
        "\t\t\tMWsRenderStageFactory * factory = pluginMgr->FindNamedImplementation<MWsRenderStageFactory>(ptr);\n\t\t\tif (factory)",
        "\t\t\tMWsRenderStageFactory * factory = pluginMgr->FindNamedImplementation<MWsRenderStageFactory>(ptr);\n"
        "\t\t\tHtcleoWsLog(0x00000321u, (TInt)(factory != NULL), htcleoStageIndex);\n"
        "\t\t\tif (factory)",
        "manager factory lookup",
    )
    source = replace_once(
        source,
        "\t\t\t\t\tstage = NULL;\n\t\t\t\t\tTRAP(err, stage = factory->CreateFinalRenderStageL(aScreen, aScreenRedraw, aScreenNumber));\n\t\t\t\t\tif (err)",
        "\t\t\t\t\tstage = NULL;\n"
        "\t\t\t\t\tHtcleoWsLog(0x00000322u, KErrNone, htcleoStageIndex);\n"
        "\t\t\t\t\tTRAP(err, stage = factory->CreateFinalRenderStageL(aScreen, aScreenRedraw, aScreenNumber));\n"
        "\t\t\t\t\tHtcleoWsLog(0x00000323u, err,\n"
        "\t\t\t\t\t\t(htcleoStageIndex << 16) | (TUint32)(stage != NULL));\n"
        "\t\t\t\t\tif (err)",
        "manager final stage call",
    )
    source = replace_once(
        source,
        "\t\t\t\t\tstage = NULL;\n\t\t\t\t\tTRAP(err, stage = factory->CreateRenderStageL(aScreen, aScreenRedraw, savedStage));\n\t\t\t\t\tif (err)",
        "\t\t\t\t\tstage = NULL;\n"
        "\t\t\t\t\tHtcleoWsLog(0x00000324u, KErrNone, htcleoStageIndex);\n"
        "\t\t\t\t\tTRAP(err, stage = factory->CreateRenderStageL(aScreen, aScreenRedraw, savedStage));\n"
        "\t\t\t\t\tHtcleoWsLog(0x00000325u, err,\n"
        "\t\t\t\t\t\t(htcleoStageIndex << 16) | (TUint32)(stage != NULL));\n"
        "\t\t\t\t\tif (err)",
        "manager nonfinal stage call",
    )
    source = replace_once(
        source,
        "\t\t\t\t\tsavedStage = stage;\n\t\t\t\t\t}",
        "\t\t\t\t\tsavedStage = stage;\n"
        "\t\t\t\t\tHtcleoWsLog(0x00000326u, KErrNone,\n"
        "\t\t\t\t\t\t(htcleoStageIndex << 16) | (TUint32)(savedStage != NULL));\n"
        "\t\t\t\t\t}",
        "manager saved stage",
    )
    source = replace_once(
        source,
        "\t\t\tif (err)\n\t\t\t\t{\n\t\t\t\tif (wsDebugLog)",
        "\t\t\tif (err)\n\t\t\t\t{\n"
        "\t\t\t\tHtcleoWsLog(0x00000327u, err, htcleoStageIndex);\n"
        "\t\t\t\tif (wsDebugLog)",
        "manager error",
    )
    source = replace_once(
        source,
        "\t\t\t\t}\n\t\t\t}\n\t\telse\n\t\t\t{\n\t\t\tbreak;",
        "\t\t\t\t}\n"
        "\t\t\t++htcleoStageIndex;\n"
        "\t\t\t}\n"
        "\t\telse\n"
        "\t\t\t{\n"
        "\t\t\tHtcleoWsLog(0x00000328u, KErrNone, htcleoStageIndex);\n"
        "\t\t\tbreak;",
        "manager loop tail",
    )
    source = replace_once(
        source,
        "\treturn savedStage;\n\t}\n\nCWsRenderStage *CRenderStageManager::ConnectL",
        "\tHtcleoWsLog(0x00000329u, err, (TUint32)(savedStage != NULL));\n"
        "\treturn savedStage;\n\t}\n\n"
        "CWsRenderStage *CRenderStageManager::ConnectL",
        "manager chain return",
    )
    source = replace_once(
        source,
        "CWsRenderStage *CRenderStageManager::ConnectL(TInt aScreenNumber, MWsScreen *aScreen, MWsScreenRedraw *aScreenRedraw)\n\t{\n\tTPtrC stagesString;",
        "CWsRenderStage *CRenderStageManager::ConnectL(TInt aScreenNumber, MWsScreen *aScreen, MWsScreenRedraw *aScreenRedraw)\n\t{\n"
        "\tHtcleoWsLog(0x00000300u, KErrNone, (TUint32)aScreenNumber);\n"
        "\tTPtrC stagesString;",
        "manager Connect entry",
    )
    source = replace_once(
        source,
        "\t\trenderStageList = &KDefaultRenderStages();\n\t\t}\n\t\n\tLEAVE_LOG_INSTALL_C;",
        "\t\trenderStageList = &KDefaultRenderStages();\n\t\t}\n"
        "\tHtcleoWsLog(0x00000301u, (TInt)customStages, (TUint32)renderStageList->Length());\n\t\n"
        "\tLEAVE_LOG_INSTALL_C;",
        "manager list selection",
    )
    source = replace_once(
        source,
        "\tHBufC* reversedRenderStageList = ReverseListLC(renderStageList);\n\tCWsRenderStage *firstRenderStage;",
        "\tHBufC* reversedRenderStageList = ReverseListLC(renderStageList);\n"
        "\tHtcleoWsLog(0x00000302u, KErrNone, (TUint32)reversedRenderStageList->Length());\n"
        "\tCWsRenderStage *firstRenderStage;",
        "manager reverse list",
    )
    source = replace_once(
        source,
        "\tfirstRenderStage = ConstructRenderStageChain(reversedRenderStageList, aScreenNumber, aScreen, aScreenRedraw);\n\t\n\tCleanupStack::PopAndDestroy(reversedRenderStageList);",
        "\tfirstRenderStage = ConstructRenderStageChain(reversedRenderStageList, aScreenNumber, aScreen, aScreenRedraw);\n"
        "\tHtcleoWsLog(0x00000303u, KErrNone, (TUint32)(firstRenderStage != NULL));\n\t\n"
        "\tCleanupStack::PopAndDestroy(reversedRenderStageList);",
        "manager chain post",
    )
    source = replace_once(
        source,
        "\tLEAVE_LOG_UNINSTALL_C;\n\t\n\treturn firstRenderStage;",
        "\tLEAVE_LOG_UNINSTALL_C;\n"
        "\tHtcleoWsLog(0x00000304u, KErrNone, (TUint32)(firstRenderStage != NULL));\n\t\n"
        "\treturn firstRenderStage;",
        "manager Connect return",
    )
    return source


def verify(screen: str, redraw: str, manager: str) -> None:
    screen_stages = tuple(range(0x100, 0x115))
    redraw_stages = (0x200, 0x201, 0x202, 0x203, 0x210, 0x211, 0x212, 0x213, 0x214, 0x215, 0x216)
    manager_stages = (0x300, 0x301, 0x302, 0x303, 0x304, 0x310, 0x311,
                      0x320, 0x321, 0x322, 0x323, 0x324, 0x325, 0x326,
                      0x327, 0x328, 0x329)
    checks = {
        "screen marker": screen.count(SCREEN_MARKER) == 1,
        "redraw marker": redraw.count(REDRAW_MARKER) == 1,
        "manager marker": manager.count(MANAGER_MARKER) == 1,
        "screen stages": all(screen.count(f"0x{stage:08X}u") == 1 for stage in screen_stages),
        "redraw stages": all(redraw.count(f"0x{stage:08X}u") == 1 for stage in redraw_stages),
        "manager stages": all(manager.count(f"0x{stage:08X}u") == 1 for stage in manager_stages),
        "no added waits": all("User::After" not in item for item in (screen, redraw, manager)),
        "same stage calls": manager.count("CreateFinalRenderStageL(") == 1
        and manager.count("CreateRenderStageL(") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("WServ screen progress verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    base = args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER"
    screen_path = base / "openwfc/screen.cpp"
    redraw_path = base / "openwfc/ScreenRedraw.cpp"
    manager_path = base / "renderstagemanager.cpp"
    for path in (screen_path, redraw_path, manager_path):
        if not path.is_file():
            raise SystemExit(f"missing WServ source: {path}")

    screen = patch_screen(screen_path.read_text(encoding="utf-8"))
    redraw = patch_redraw(redraw_path.read_text(encoding="utf-8"))
    manager = patch_manager(manager_path.read_text(encoding="utf-8"))
    verify(screen, redraw, manager)
    screen_path.write_text(screen, encoding="utf-8")
    redraw_path.write_text(redraw, encoding="utf-8")
    manager_path.write_text(manager, encoding="utf-8")
    print("HTCLEO_WSERV_SCREEN_PROGRESS=installed screen=21 redraw=11 manager=17")


if __name__ == "__main__":
    main()
