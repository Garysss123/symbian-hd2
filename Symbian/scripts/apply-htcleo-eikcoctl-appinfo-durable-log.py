#!/usr/bin/env python3
"""Trace MatrixMenu/HomeScreen CEikAppUiFactory::ReadAppInfoResourceL paths.

Iteration 515 proves that MatrixMenu enters CEikAppUi::ReadAppInfoResourceL
after EIKBASE B60E but never reaches B60F.  The implementation is in
eikcoctl.dll, not eikcore.dll.  Add close-only B620-B631 checkpoints without
changing any resource, control, WServ, SGC, or failure behavior.  Iteration
686 routes the same already-proven checkpoints for HomeScreen into HSXML.TXT.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKCOCTL_MATRIXMENU_APPINFO_DURABLE_LOG_V1"
HOMESCREEN_MARKER = "HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_TRACE_V1"
ABS_COMPAT_MARKER = "HTCLEO_GCCE_EIKCOCTL_INTEGER_ABS_COMPAT_V1"
INLINE_EXPORT_MARKER = "HTCLEO_GCCE_EIKCOCTL_INLINE_EXPORT_COMPAT_V1"
TOUCH_DTOR_EXPORT_MARKER = "HTCLEO_GCCE_EIKCOCTL_TOUCH_DTOR_EXPORT_COMPAT_V1"
PICTO_RTTI_EXPORT_MARKER = "HTCLEO_GCCE_EIKCOCTL_PICTO_RTTI_EXPORT_COMPAT_V1"
MACRO = "__HTCLEO_EIKCOCTL_APPINFO_LOG__"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HELPER = r'''

#ifdef __HTCLEO_EIKCOCTL_APPINFO_LOG__
#include <f32file.h>

// HTCLEO_EIKCOCTL_MATRIXMENU_APPINFO_DURABLE_LOG_V1
static void HtcleoEikAppInfoLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (RProcess().SecureId().iId != 0x101F4CD2u)
        {
        return;
        }

    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        {
        return;
        }

    _LIT(KHtcleoEikBaseLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoEikBaseLogPath, "C:\\Symbian3\\EIKBASE.TXT");
    r = fs.MkDirAll(KHtcleoEikBaseLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoEikBaseLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        {
        r = file.Replace(fs, KHtcleoEikBaseLogPath,
            EFileWrite | EFileShareAny);
        }
    else if (r == KErrNone)
        {
        r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position <= ((512 * 64) - 64))
        {
        _LIT8(KHtcleoEikBasePrefix, "HTCLEO_EIKBASE ");
        TBuf8<96> record;
        record.Append(KHtcleoEikBasePrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        file.Write(record);
        }
    file.Close();
    fs.Close();
    }
#else
inline void HtcleoEikAppInfoLog(TUint32, TInt, TUint32) {}
#endif
'''


def install(source: str) -> str:
    source = replace_once(
        source,
        "#include <aknappui.h>\n",
        "#include <aknappui.h>\n" + HELPER,
        "app-info logger helper",
    )
    source = replace_once(
        source,
        "    const TInt resourceFileOffset=(aResourceFileOffset)? aResourceFileOffset : aAppUi->Application()->ResourceFileOffset();\n"
        "    SEikAppInfo appInfo;",
        "    const TInt resourceFileOffset=(aResourceFileOffset)? aResourceFileOffset : aAppUi->Application()->ResourceFileOffset();\n"
        "    HtcleoEikAppInfoLog(0x0000B620u, KErrNone, (TUint32)resourceFileOffset);\n"
        "    SEikAppInfo appInfo;",
        "B620 entry",
    )
    source = replace_once(
        source,
        "    CCoeEnv::Static()->ReadResourceAsDes8L(ptr,EAppInfoResourceOffset+resourceFileOffset);\n    \n"
        "    if (!iExtension)",
        "    CCoeEnv::Static()->ReadResourceAsDes8L(ptr,EAppInfoResourceOffset+resourceFileOffset);\n"
        "    HtcleoEikAppInfoLog(0x0000B621u, (TInt)appInfo.iStatusPaneId,\n"
        "        (((TUint32)appInfo.iMenuBarId & 0xffffu) << 16) |\n"
        "        ((TUint32)appInfo.iCbaId & 0xffffu));\n    \n"
        "    HtcleoEikAppInfoLog(0x0000B622u, KErrNone,\n"
        "        (TUint32)appInfo.iExtensionId);\n"
        "    if (!iExtension)",
        "B621-B622 resource return",
    )
    source = replace_once(
        source,
        "    iExtension->ReadAppInfoResourceExtensionL(appInfo.iExtensionId);\n\n"
        "    if (appInfo.iMenuBarId)",
        "    iExtension->ReadAppInfoResourceExtensionL(appInfo.iExtensionId);\n"
        "    HtcleoEikAppInfoLog(0x0000B623u, KErrNone,\n"
        "        (TUint32)appInfo.iExtensionId);\n\n"
        "    HtcleoEikAppInfoLog(0x0000B624u, KErrNone,\n"
        "        (TUint32)appInfo.iMenuBarId);\n"
        "    if (appInfo.iMenuBarId)",
        "B623-B624 extension/menu",
    )
    source = replace_once(
        source,
        "        }\n    TRect boundingRect=ClientRect(); // make toolband stretch to the screen width by default",
        "        }\n"
        "    HtcleoEikAppInfoLog(0x0000B625u, KErrNone,\n"
        "        (TUint32)appInfo.iMenuBarId);\n"
        "    HtcleoEikAppInfoLog(0x0000B626u, KErrNone, 0u);\n"
        "    TRect boundingRect=ClientRect(); // make toolband stretch to the screen width by default\n"
        "    HtcleoEikAppInfoLog(0x0000B627u, KErrNone,\n"
        "        (((TUint32)boundingRect.Width() & 0xffffu) << 16) |\n"
        "        ((TUint32)boundingRect.Height() & 0xffffu));",
        "B625-B627 menu/client rect",
    )
    source = replace_once(
        source,
        "    // !!! Toolbar / CBA decision should be made in the LAF.\n"
        "    CEikonEnv* eikEnv = CEikonEnv::Static();\n"
        "    if (eikEnv->StatusPaneCoreResId() != 0)",
        "    // !!! Toolbar / CBA decision should be made in the LAF.\n"
        "    CEikonEnv* eikEnv = CEikonEnv::Static();\n"
        "    HtcleoEikAppInfoLog(0x0000B628u, KErrNone,\n"
        "        (TUint32)eikEnv->StatusPaneCoreResId());\n"
        "    if (eikEnv->StatusPaneCoreResId() != 0)",
        "B628 status pane entry",
    )
    source = replace_once(
        source,
        "        iStatusPane = CEikStatusPane::NewL(*eikEnv, &eikEnv->RootWin(), eikEnv->StatusPaneCoreResId(), appInfo.iStatusPaneId);\n"
        "        CAknSgcClient::HandleChangeL(); // has to be called after iStatusPane is assigned",
        "        iStatusPane = CEikStatusPane::NewL(*eikEnv, &eikEnv->RootWin(), eikEnv->StatusPaneCoreResId(), appInfo.iStatusPaneId);\n"
        "        HtcleoEikAppInfoLog(0x0000B629u, KErrNone,\n"
        "            iStatusPane != NULL);\n"
        "        HtcleoEikAppInfoLog(0x0000B62Au, KErrNone, 0u);\n"
        "        CAknSgcClient::HandleChangeL(); // has to be called after iStatusPane is assigned\n"
        "        HtcleoEikAppInfoLog(0x0000B62Bu, KErrNone, 0u);",
        "B629-B62B status pane/SGC",
    )
    source = replace_once(
        source,
        "    if (appInfo.iCbaId)\n        {",
        "    HtcleoEikAppInfoLog(0x0000B62Cu, KErrNone,\n"
        "        (TUint32)appInfo.iCbaId);\n"
        "    if (appInfo.iCbaId)\n        {",
        "B62C CBA entry",
    )
    source = replace_once(
        source,
        "//      iToolBar->SetBoundingRect(boundingRect);\n        }\n"
        "    if (appInfo.iToolBarId)",
        "//      iToolBar->SetBoundingRect(boundingRect);\n        }\n"
        "    HtcleoEikAppInfoLog(0x0000B62Du, KErrNone,\n"
        "        iExtension->iCba != NULL);\n"
        "    HtcleoEikAppInfoLog(0x0000B62Eu, KErrNone,\n"
        "        (TUint32)appInfo.iToolBarId);\n"
        "    if (appInfo.iToolBarId)",
        "B62D-B62E CBA/toolbar",
    )
    source = replace_once(
        source,
        "        iToolBar->SetBoundingRect(boundingRect);\n        }\n"
        "    if (aAppUi->ContainerAppUi())",
        "        iToolBar->SetBoundingRect(boundingRect);\n        }\n"
        "    HtcleoEikAppInfoLog(0x0000B62Fu, KErrNone,\n"
        "        iToolBar != NULL);\n"
        "    HtcleoEikAppInfoLog(0x0000B630u, KErrNone,\n"
        "        (TUint32)appInfo.iToolBandId);\n"
        "    if (aAppUi->ContainerAppUi())",
        "B62F-B630 toolbar/tail",
    )
    source = replace_once(
        source,
        "    if (iTitleBand) // put title band in front\n"
        "        iTitleBand->DrawableWindow()->SetOrdinalPosition(0);\n    \n    }\n\nvoid CEikAppUiFactory::LaunchPopupMenuL(",
        "    if (iTitleBand) // put title band in front\n"
        "        iTitleBand->DrawableWindow()->SetOrdinalPosition(0);\n"
        "    HtcleoEikAppInfoLog(0x0000B631u, KErrNone, 0u);\n    \n    }\n\nvoid CEikAppUiFactory::LaunchPopupMenuL(",
        "B631 completion",
    )
    return source


def install_homescreen_route(source: str) -> str:
    source = replace_once(
        source,
        "    if (RProcess().SecureId().iId != 0x101F4CD2u)\n"
        "        {\n"
        "        return;\n"
        "        }",
        "    // HTCLEO_EIKCOCTL_HOMESCREEN_APPINFO_TRACE_V1\n"
        "    const TUint32 htcleoEikAppInfoSid = RProcess().SecureId().iId;\n"
        "    const TBool htcleoEikAppInfoHome =\n"
        "        (htcleoEikAppInfoSid == 0x102750F0u);\n"
        "    if (htcleoEikAppInfoSid != 0x101F4CD2u &&\n"
        "        !htcleoEikAppInfoHome)\n"
        "        {\n"
        "        return;\n"
        "        }",
        "HomeScreen SID route",
    )
    source = replace_once(
        source,
        '    _LIT(KHtcleoEikBaseLogPath, "C:\\\\Symbian3\\\\EIKBASE.TXT");',
        '    _LIT(KHtcleoEikBaseLogPath, "C:\\\\Symbian3\\\\EIKBASE.TXT");\n'
        '    _LIT(KHtcleoEikHomeLogPath, "C:\\\\Symbian3\\\\HSXML.TXT");',
        "HomeScreen log path",
    )
    source = replace_once(
        source,
        "    r = file.Open(fs, KHtcleoEikBaseLogPath, EFileWrite | EFileShareAny);",
        "    if (htcleoEikAppInfoHome)\n"
        "        {\n"
        "        r = file.Open(fs, KHtcleoEikHomeLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "        }\n"
        "    else\n"
        "        {\n"
        "        r = file.Open(fs, KHtcleoEikBaseLogPath,\n"
        "            EFileWrite | EFileShareAny);\n"
        "        }",
        "HomeScreen open route",
    )
    source = replace_once(
        source,
        "        r = file.Replace(fs, KHtcleoEikBaseLogPath,\n"
        "            EFileWrite | EFileShareAny);",
        "        if (htcleoEikAppInfoHome)\n"
        "            {\n"
        "            r = file.Replace(fs, KHtcleoEikHomeLogPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "            }\n"
        "        else\n"
        "            {\n"
        "            r = file.Replace(fs, KHtcleoEikBaseLogPath,\n"
        "                EFileWrite | EFileShareAny);\n"
        "            }",
        "HomeScreen replace route",
    )
    source = replace_once(
        source,
        "    if (r == KErrNone && position <= ((512 * 64) - 64))",
        "    const TInt htcleoEikAppInfoCapacity = htcleoEikAppInfoHome ?\n"
        "        (1024 * 1024) : (512 * 64);\n"
        "    if (r == KErrNone &&\n"
        "        position <= (htcleoEikAppInfoCapacity - 128))",
        "HomeScreen one-MiB capacity",
    )
    source = replace_once(
        source,
        "        record.Append(KHtcleoEikBasePrefix);",
        "        if (htcleoEikAppInfoHome)\n"
        "            {\n"
        "            record.Append(_L8(\"HTCLEO_HEI  \"));\n"
        "            }\n"
        "        else\n"
        "            {\n"
        "            record.Append(KHtcleoEikBasePrefix);\n"
        "            }",
        "HomeScreen prefix route",
    )
    return source


def install_gcce_compat(source: str) -> str:
    return replace_once(
        source,
        "        if ( abs( iPrevOffset ) < iViewRect.Height() + iItemHeight",
        "        // HTCLEO_GCCE_EIKCOCTL_INTEGER_ABS_COMPAT_V1: the released "
        "source used the C-runtime spelling.\n"
        "        if ( Abs( iPrevOffset ) < iViewRect.Height() + iItemHeight",
        "GCCE integer Abs compatibility",
    )


def install_inline_export_compat(source: str) -> str:
    return replace_once(
        source,
        "EXPORT_C inline const CFont* CTextListItemDrawer::Font(TInt aItemIndex) const",
        "// HTCLEO_GCCE_EIKCOCTL_INLINE_EXPORT_COMPAT_V1: keep the frozen "
        "export strong under GCCE.\n"
        "EXPORT_C const CFont* CTextListItemDrawer::Font(TInt aItemIndex) const",
        "GCCE inline frozen-export compatibility",
    )


def install_touch_dtor_export_compat(header: str) -> str:
    return replace_once(
        header,
        "    ~CAknTouchPane();",
        "    // HTCLEO_GCCE_EIKCOCTL_TOUCH_DTOR_EXPORT_COMPAT_V1\n"
        "    IMPORT_C ~CAknTouchPane();",
        "GCCE touch-pane destructor frozen-export compatibility",
    )


def install_picto_rtti_export_compat(header: str) -> str:
    return replace_once(
        header,
        "        class TAknEdwinPictographDrawer : public MAknPictographAnimatorCallBack",
        "        // HTCLEO_GCCE_EIKCOCTL_PICTO_RTTI_EXPORT_COMPAT_V1\n"
        "        class __attribute__((visibility(\"default\"))) "
        "TAknEdwinPictographDrawer : public MAknPictographAnimatorCallBack",
        "GCCE pictograph RTTI frozen-export compatibility",
    )


def verify(
    source: str,
    mmp: str,
    physics: str,
    list_item_source: str,
    touch_header: str,
    edwin_header: str,
) -> None:
    checks = {
        "marker": source.count(MARKER) == 1,
        "HomeScreen route marker": source.count(HOMESCREEN_MARKER) == 1,
        "matrixmenu and HomeScreen SIDs": (
            source.count("htcleoEikAppInfoSid != 0x101F4CD2u") == 1
            and source.count("htcleoEikAppInfoSid == 0x102750F0u") == 1
        ),
        "durable path": source.count(r"C:\\Symbian3\\EIKBASE.TXT") == 1,
        "HomeScreen durable path": source.count(r"C:\\Symbian3\\HSXML.TXT") == 1,
        "bounded close-only logger": (
            source.count("htcleoEikAppInfoCapacity - 128") == 1
            and source.count("(1024 * 1024) : (512 * 64)") == 1
            and "file.Flush();" not in HELPER
        ),
        "HomeScreen prefix": source.count('HTCLEO_HEI  ') == 1,
        "all stages": all(
            source.count(f"0x0000{stage:04X}u") == 1
            for stage in range(0xB620, 0xB632)
        ),
        "resource read retained": source.count(
            "CCoeEnv::Static()->ReadResourceAsDes8L(ptr,EAppInfoResourceOffset+resourceFileOffset);"
        ) == 1,
        "extension retained": source.count(
            "iExtension->ReadAppInfoResourceExtensionL(appInfo.iExtensionId);"
        ) == 1,
        "menu retained": source.count(
            "iMenuBar->ConstructL(aAppUi,appInfo.iHotKeysId,appInfo.iMenuBarId);"
        ) == 1,
        "status pane retained": source.count(
            "iStatusPane = CEikStatusPane::NewL(*eikEnv, &eikEnv->RootWin(), eikEnv->StatusPaneCoreResId(), appInfo.iStatusPaneId);"
        ) == 1,
        "SGC retained": source.count("CAknSgcClient::HandleChangeL();") >= 2,
        "CBA retained": source.count(
            "iExtension->iCba = CEikButtonGroupContainer::NewL(CEikButtonGroupContainer::ECba,"
        ) == 1,
        "macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "GCCE integer Abs compatibility": (
            physics.count(ABS_COMPAT_MARKER) == 1
            and "if ( abs( iPrevOffset )" not in physics
            and physics.count("if ( Abs( iPrevOffset )") == 1
        ),
        "GCCE strong inline frozen export": (
            list_item_source.count(INLINE_EXPORT_MARKER) == 1
            and "EXPORT_C inline const CFont* CTextListItemDrawer::Font"
            not in list_item_source
            and list_item_source.count(
                "EXPORT_C const CFont* CTextListItemDrawer::Font"
            )
            == 1
        ),
        "GCCE touch destructor frozen export": (
            touch_header.count(TOUCH_DTOR_EXPORT_MARKER) == 1
            and touch_header.count("IMPORT_C ~CAknTouchPane();") == 1
        ),
        "GCCE pictograph RTTI frozen export": (
            edwin_header.count(PICTO_RTTI_EXPORT_MARKER) == 1
            and edwin_header.count(
                'class __attribute__((visibility("default"))) '
                "TAknEdwinPictographDrawer"
            )
            == 1
        ),
        "no timer": "User::After" not in HELPER,
        "no display probe": "HalFunction" not in HELPER,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "EikCoCtl app-info durable log verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()

    component = args.root / "sf/mw/classicui/uifw/EikStd"
    source_path = component / "coctlsrc/EIKCOLIB.CPP"
    physics_path = component / "coctlsrc/aknstyluspopupmenuphysicshandler.cpp"
    list_item_path = component / "coctlsrc/EIKLBI.CPP"
    mmp_path = component / "coctlsrc/EIKCOCTL.MMP"
    touch_header_path = args.root / "epoc32/include/mw/akntouchpane.h"
    edwin_header_path = args.root / "epoc32/include/mw/eikedwin.h"
    source = source_path.read_text(encoding="latin-1")
    physics = physics_path.read_text(encoding="latin-1")
    list_item_source = list_item_path.read_text(encoding="latin-1")
    mmp = mmp_path.read_text(encoding="latin-1")
    touch_header = touch_header_path.read_text(encoding="latin-1")
    edwin_header = edwin_header_path.read_text(encoding="latin-1")

    if MARKER not in source:
        source = install(source)
    if HOMESCREEN_MARKER not in source:
        source = install_homescreen_route(source)
    if ABS_COMPAT_MARKER not in physics:
        physics = install_gcce_compat(physics)
    if INLINE_EXPORT_MARKER not in list_item_source:
        list_item_source = install_inline_export_compat(list_item_source)
    if TOUCH_DTOR_EXPORT_MARKER not in touch_header:
        touch_header = install_touch_dtor_export_compat(touch_header)
    if PICTO_RTTI_EXPORT_MARKER not in edwin_header:
        edwin_header = install_picto_rtti_export_compat(edwin_header)
    if f"MACRO          {MACRO}" not in mmp:
        mmp += f"\nMACRO          {MACRO}\n"

    verify(
        source,
        mmp,
        physics,
        list_item_source,
        touch_header,
        edwin_header,
    )
    if source != source_path.read_text(encoding="latin-1"):
        source_path.write_text(source, encoding="latin-1")
    if physics != physics_path.read_text(encoding="latin-1"):
        physics_path.write_text(physics, encoding="latin-1")
    if list_item_source != list_item_path.read_text(encoding="latin-1"):
        list_item_path.write_text(list_item_source, encoding="latin-1")
    if mmp != mmp_path.read_text(encoding="latin-1"):
        mmp_path.write_text(mmp, encoding="latin-1")
    if touch_header != touch_header_path.read_text(encoding="latin-1"):
        touch_header_path.write_text(touch_header, encoding="latin-1")
    if edwin_header != edwin_header_path.read_text(encoding="latin-1"):
        edwin_header_path.write_text(edwin_header, encoding="latin-1")
    print(
        "HTCLEO_EIKCOCTL_APPINFO_DURABLE_LOG=installed "
        "scope=matrixmenu+homescreen stages=B620-B631 close-only hsxml-1m"
    )


if __name__ == "__main__":
    main()
