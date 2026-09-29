#!/usr/bin/env python3
"""Commit native Home viewport to its owning windows, preserving stock CBA."""

from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_XN_CLIENT_WINDOW_COMMIT_V1"
BACKGROUND_MARKER = "HTCLEO_XN_BACKGROUND_CLIENT_WINDOW_V1"
WALLPAPER_MARKER = "HTCLEO_HOME_GRASS_WALLPAPER_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Xn window anchor mismatch: {old[:100]!r}")
    return text.replace(old, new, 1)


COMMIT = r'''
    // HTCLEO_XN_CLIENT_WINDOW_COMMIT_V1
    if (htcleoCommitLayout && nextPhase == XnLayoutPhase::ENone)
        {
        const TRect viewport(ClientRect());
        HtcleoXnGeometryLog(0x48581726u,
            iCurrentViewControlAdapter && iCurrentViewControlAdapter->OwnsWindow(),
            HtcleoXnPackPoint(TPoint(viewport.Width(), viewport.Height())));
        if (!viewport.IsEmpty() && viewport.Width() == 480 &&
            viewport.iTl.iY >= 0 && viewport.iBr.iY <= 800 &&
            iCurrentViewControlAdapter &&
            iCurrentViewControlAdapter->OwnsWindow())
            {
            CXnControlAdapter& view = *iCurrentViewControlAdapter;
            HtcleoXnGeometryLog(0x48581720u,
                (TInt)HtcleoXnPackPoint(viewport.iTl),
                HtcleoXnPackPoint(viewport.iBr));
            // CCoeControl::Rect() starts at zero for an owning window.
            // Read the actual RWindow extent instead of treating Rect as
            // a screen rectangle or adding the status offset to each child.
            const TRect before(view.Window().Position(), view.Window().Size());
            HtcleoXnGeometryLog(0x48581721u,
                (TInt)HtcleoXnPackPoint(before.iTl),
                HtcleoXnPackPoint(before.iBr));
            if (before != viewport)
                {
                view.SetRect(viewport);
                view.DrawDeferred();
                }
            const TRect after(view.Window().Position(), view.Window().Size());
            HtcleoXnGeometryLog(0x48581722u,
                (TInt)HtcleoXnPackPoint(after.iTl),
                HtcleoXnPackPoint(after.iBr));

            CXnBackgroundManager& bg = iAppUiAdapter.ViewAdapter().BgManager();
            const TRect bgBefore(bg.Position(), bg.Size());
            HtcleoXnGeometryLog(0x48581723u,
                (TInt)HtcleoXnPackPoint(bgBefore.iTl),
                HtcleoXnPackPoint(bgBefore.iBr));
            if (bgBefore != viewport)
                bg.SetRect(viewport);
            // Paint the real skin/default background over the entire client
            // before the normal view render. StatusPane and CBA are outside it.
            bg.MakeVisible(ETrue);
            const TRect bgAfter(bg.DrawableWindow()->Position(), bg.DrawableWindow()->Size());
            HtcleoXnGeometryLog(0x48581724u,
                (TInt)HtcleoXnPackPoint(bgAfter.iTl),
                HtcleoXnPackPoint(bgAfter.iBr));
            }
        }
'''


def patch_engine(text: str) -> str:
    if MARKER in text:
        return text.replace(
            "bg.Window().Position(), bg.Window().Size()",
            "bg.DrawableWindow()->Position(), bg.DrawableWindow()->Size()")
    if "HTCLEO_XN_NATIVE_PANEL_CONTRACT_V1" not in text:
        raise SystemExit("native Home geometry prerequisite missing")
    text = once(text,
        "TInt CXnUiEngineImpl::RunLayoutL( CXnNode* aNode )\n    {\n",
        "TInt CXnUiEngineImpl::RunLayoutL( CXnNode* aNode )\n    {\n"
        "    const TBool htcleoCommitLayout = HtcleoXnHd2Geometry() &&\n"
        "        (iLayoutControl & XnLayoutControl::EViewDirty);\n")
    text = once(text,
        "    CleanupStack::PopAndDestroy( &laidOutList );\n    return nextPhase;",
        COMMIT + "    CleanupStack::PopAndDestroy( &laidOutList );\n    return nextPhase;")
    return once(text,
        '''    AknLayoutUtils::LayoutMetricsRect( AknLayoutUtils::EScreen, bgRect );
    iAppUiAdapter.ViewAdapter().BgManager().SetRect( bgRect );''',
        '''    AknLayoutUtils::LayoutMetricsRect( AknLayoutUtils::EScreen, bgRect );
    if (HtcleoXnHd2Geometry())
        bgRect = ClientRect();
    iAppUiAdapter.ViewAdapter().BgManager().SetRect( bgRect );''')


def patch_background(text: str) -> str:
    if BACKGROUND_MARKER in text:
        return text
    # Rect() remains window-local. ParentAbsolute skin contexts require the
    # owning window's screen position separately; do not move bitmap bounds.
    text = once(text, "    iBgContext->SetRect( iRect );",
        '''    // HTCLEO_XN_BACKGROUND_CLIENT_WINDOW_V1
    if (RProcess().SecureId().iId == 0x102750f0u)
        iBgContext->SetParentPos(Position());
    iBgContext->SetRect( iRect );''')
    text = once(text, "      iStoreWallpaper( ETrue )",
                "      iStoreWallpaper( ETrue ), iHtcleoWallpaper(NULL)")
    text = once(text, "    CreateWindowL();",
        r'''    // HTCLEO_HOME_GRASS_WALLPAPER_V1: cached bitmap, no runtime JPEG decoder.
    if (RProcess().SecureId().iId == 0x102750f0u)
        {
        iHtcleoWallpaper = new CFbsBitmap;
        TInt loadResult = KErrNoMemory;
        if (iHtcleoWallpaper)
            {
            _LIT(KWallpaper, "C:\\Symbian3\\HOMEBG.MBM");
            loadResult = iHtcleoWallpaper->Load(KWallpaper, 0);
            if (loadResult != KErrNone)
                {
                delete iHtcleoWallpaper;
                iHtcleoWallpaper = NULL;
                }
            }
        HtcleoXnGeometryLog(0x48581740u, loadResult, 0u);
        if (iHtcleoWallpaper)
            {
            const TSize size = iHtcleoWallpaper->SizeInPixels();
            HtcleoXnGeometryLog(0x48581741u, size.iWidth, (TUint32)size.iHeight);
            }
        }
    CreateWindowL();''')
    text = once(text, '#include "xnbackgroundmanager.h"\n',
        '#include "xnbackgroundmanager.h"\n'
        'extern void HtcleoXnGeometryLog(TUint32, TInt, TUint32);\n')
    text = once(text, "    delete iBgImage;\n    delete iBgImagePath;",
                "    delete iBgImage;\n    delete iHtcleoWallpaper;\n    delete iBgImagePath;")
    text = once(text, "    CCoeControl::MakeVisible( aVisible );",
        '''    if (aVisible && RProcess().SecureId().iId == 0x102750f0u)
        {
        const TRect viewport(iViewManager.UiEngine().ClientRect());
        if (!viewport.IsEmpty() && viewport.Width() == 480 &&
            viewport.iTl.iY >= 0 && viewport.iBr.iY <= 800)
            {
            if (TRect(Position(), Size()) != viewport)
                SetRect(viewport);
            }
        else
            {
            // Construction may precede the first valid client rectangle.
            // First committed view layout will show the background normally.
            aVisible = EFalse;
            }
        }
    CCoeControl::MakeVisible( aVisible );''')
    text = once(text, "    // Draw bg image\n    if( wallpaper )",
        '''    // Draw bg image
    // User-selected Nokia grass/sky wallpaper, shared by all Home pages.
    if (RProcess().SecureId().iId == 0x102750f0u)
        {
        HtcleoDrawWallpaper(SystemGc(), Rect(), aRect);
        }
    else if( wallpaper )''')
    helper = r'''
void CXnBackgroundManager::HtcleoDrawWallpaper(CWindowGc& aGc,
    const TRect& aBounds, const TRect& aDamage) const
    {
    TRect damage(aDamage);
    damage.Intersection(aBounds);
    if (damage.IsEmpty())
        return;
    if (!iHtcleoWallpaper || aBounds.IsEmpty())
        {
        aGc.Clear(damage);
        return;
        }
    const TSize size(iHtcleoWallpaper->SizeInPixels());
    if (size.iWidth <= 0 || size.iHeight <= 0)
        return;
    TRect crop(TPoint(0, 0), size);
    // Cover the viewport without distorting the original wallpaper.
    if (size.iWidth * aBounds.Height() > size.iHeight * aBounds.Width())
        {
        const TInt width = size.iHeight * aBounds.Width() / aBounds.Height();
        crop.iTl.iX = (size.iWidth - width) / 2;
        crop.iBr.iX = crop.iTl.iX + width;
        }
    else
        {
        const TInt height = size.iWidth * aBounds.Height() / aBounds.Width();
        crop.iTl.iY = (size.iHeight - height) / 2;
        crop.iBr.iY = crop.iTl.iY + height;
        }
    aGc.SetClippingRect(damage);
    aGc.DrawBitmap(aBounds, iHtcleoWallpaper, crop);
    aGc.CancelClippingRect();
    }

'''
    return text + helper


def patch_background_header(text: str) -> str:
    if "HtcleoDrawWallpaper" in text:
        return text
    text = once(text, "    ~CXnBackgroundManager();",
        "    ~CXnBackgroundManager();\n"
        "    void HtcleoDrawWallpaper(CWindowGc&, const TRect&, const TRect&) const;")
    return once(text, "    TBool iStoreWallpaper;",
                "    TBool iStoreWallpaper;\n    CFbsBitmap* iHtcleoWallpaper;")


def patch_view_control(text: str) -> str:
    if "HTCLEO_HOME_GRASS_VIEW_BACKGROUND_V1" in text:
        return text
    text = once(text, '#include "xnviewcontroladapter.h"\n',
        '#include "xnviewcontroladapter.h"\n'
        '#include "xnviewadapter.h"\n#include "xnbackgroundmanager.h"\n')
    return once(text, "    SystemGc().Clear( aRect );",
        '''    // HTCLEO_HOME_GRASS_VIEW_BACKGROUND_V1
    // Draw the cached wallpaper in the actual view as well as the background;
    // the CPU display path has no reliable alpha composition between them.
    const TBool htcleoHome = RProcess().SecureId().iId == 0x102750f0u;
    if (htcleoHome)
        iAppUi.ViewAdapter().BgManager().HtcleoDrawWallpaper(SystemGc(), Rect(), aRect);
    else
        SystemGc().Clear( aRect );''')


def verify(engine: str, background: str, view_control: str, header: str) -> None:
    checks = {
        "commit marker": engine.count(MARKER) == 1,
        "background marker": background.count(BACKGROUND_MARKER) == 1,
        "actual owning extent": engine.count(
            "const TRect before(view.Window().Position(), view.Window().Size());") == 1,
        "no child offset": "node->BorderRect().Move" not in COMMIT,
        "no CBA mutation": all(token not in COMMIT for token in
            ("Cba()", "SetBoundingRect", "SetCommand", "SetSoftKeyImage")),
        "skin position": background.count("iBgContext->SetParentPos(Position());") == 1,
        "local bitmap rect": "iRect = Rect();" in background,
        "stock skin draw": "AknsDrawUtils::Background( skin, iBgContext, this, SystemGc(), aRect );" in background,
        "user wallpaper": background.count(WALLPAPER_MARKER) == 1
            and view_control.count("HTCLEO_HOME_GRASS_VIEW_BACKGROUND_V1") == 1
            and header.count("CFbsBitmap* iHtcleoWallpaper;") == 1
            and background.count("iHtcleoWallpaper->Load(KWallpaper, 0)") == 1,
        "one bitmap cache": "iHtcleoWallpaper(NULL)" in background
            and "delete iHtcleoWallpaper;" in background
            and "iHtcleoWallpaper->Load" not in view_control,
        "viewport": "bgRect = ClientRect();" in engine
            and "TRect(Position(), Size()) != viewport" in background,
        "stages": all(engine.count(f"0x485817{suffix:02X}u") == 1
                      for suffix in range(0x20, 0x25)),
    }
    failed = [key for key, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Xn client-window verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    src = args.root / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src"
    engine_path = src / "xnuiengineimpl.cpp"
    background_path = src / "xnbackgroundmanager.cpp"
    view_control_path = src / "xnviewcontroladapter.cpp"
    header_path = src.parent / "inc/xnbackgroundmanager.h"
    engine = patch_engine(engine_path.read_text(encoding="utf-8"))
    background = patch_background(background_path.read_text(encoding="utf-8"))
    view_control = patch_view_control(view_control_path.read_text(encoding="utf-8"))
    header = patch_background_header(header_path.read_text(encoding="utf-8"))
    verify(engine, background, view_control, header)
    engine_path.write_text(engine, encoding="utf-8")
    background_path.write_text(background, encoding="utf-8")
    view_control_path.write_text(view_control, encoding="utf-8")
    header_path.write_text(header, encoding="utf-8")
    print("HTCLEO_XN_CLIENT_WINDOW_COMMIT=owning-view-and-background-client-bounds-cached-grass-wallpaper")


if __name__ == "__main__":
    main()
