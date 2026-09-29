#!/usr/bin/env python3
"""Draw the shared wallpaper across MatrixMenu client, including empty cells."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_MMWIDGETS_FULL_CLIENT_WALLPAPER_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"MM wallpaper anchor mismatch: {old[:100]!r}")
    return text.replace(old, new, 1)


LOAD = r'''    // HTCLEO_MMWIDGETS_FULL_CLIENT_WALLPAPER_V1
    if (RProcess().SecureId().iId == 0x101f4cd2u)
        {
        iHtcleoWallpaper = new CFbsBitmap;
        TInt result = KErrNoMemory;
        if (iHtcleoWallpaper)
            {
            _LIT(KWallpaper, "C:\\Symbian3\\HOMEBG.MBM");
            result = iHtcleoWallpaper->Load(KWallpaper, 0);
            if (result != KErrNone)
                {
                delete iHtcleoWallpaper;
                iHtcleoWallpaper = NULL;
                }
            }
        HtcleoMmwLog(0x4D570240u, result, 0u);
        if (iHtcleoWallpaper)
            {
            const TSize size = iHtcleoWallpaper->SizeInPixels();
            HtcleoMmwLog(0x4D570241u, size.iWidth, (TUint32)size.iHeight);
            }
        }
'''

DRAW = r'''
TBool CMmListBoxItemDrawer::HtcleoDrawWallpaper(CWindowGc& aGc,
    const TRect& aClient, const TRect& aDamage) const
    {
    if (!iHtcleoWallpaper || aClient.IsEmpty())
        return EFalse;
    TRect damage(aDamage);
    damage.Intersection(aClient);
    if (damage.IsEmpty())
        return ETrue;
    const TSize size(iHtcleoWallpaper->SizeInPixels());
    if (size.iWidth <= 0 || size.iHeight <= 0)
        return EFalse;
    TRect crop(TPoint(0, 0), size);
    if (size.iWidth * aClient.Height() > size.iHeight * aClient.Width())
        {
        const TInt width = size.iHeight * aClient.Width() / aClient.Height();
        crop.iTl.iX = (size.iWidth - width) / 2;
        crop.iBr.iX = crop.iTl.iX + width;
        }
    else
        {
        const TInt height = size.iWidth * aClient.Height() / aClient.Width();
        crop.iTl.iY = (size.iHeight - height) / 2;
        crop.iBr.iY = crop.iTl.iY + height;
        }
    aGc.SetClippingRect(damage);
    aGc.DrawBitmap(aClient, iHtcleoWallpaper, crop);
    aGc.CancelClippingRect();
    return ETrue;
    }
'''


def patch_drawer(text: str) -> str:
    if MARKER in text:
        return text
    text = once(text,
        "  iFont(aFont), iLeftOverAreaUnderAnimatedItem(EFalse)",
        "  iFont(aFont), iLeftOverAreaUnderAnimatedItem(EFalse), iHtcleoWallpaper(NULL)")
    text = once(text, "    iFloatingItems.Close();",
                "    delete iHtcleoWallpaper;\n    iFloatingItems.Close();")
    text = once(text, "void CMmListBoxItemDrawer::ConstructL()\n    {\n",
                "void CMmListBoxItemDrawer::ConstructL()\n    {\n" + LOAD)
    text = once(text,
        "void CMmListBoxItemDrawer::DrawBackground( const TRect& aItemTextRect ) const\n    {\n",
        """void CMmListBoxItemDrawer::DrawBackground( const TRect& aItemTextRect ) const
    {
    if (iWidget && IsRedrawItemBackgroundEnabled() &&
        HtcleoDrawWallpaper(*iGc, iWidget->Rect(), aItemTextRect))
        return;
""")
    text = once(text,
        """    CFormattedCellListBoxItemDrawer::DrawEmptyItem( aItemIndex, aItemRectPos,
        aViewIsDimmed );""",
        """    if (!iWidget || !HtcleoDrawWallpaper(*iGc, iWidget->Rect(), r))
        CFormattedCellListBoxItemDrawer::DrawEmptyItem( aItemIndex, aItemRectPos,
            aViewIsDimmed );""")
    text = once(text, "    iWidget = aView;",
        """    iWidget = aView;
    if (iWidget && iHtcleoWallpaper)
        HtcleoMmwLog(0x4D570242u,
            (iWidget->Rect().iTl.iX << 16) | (iWidget->Rect().iTl.iY & 0xffff),
            ((TUint32)iWidget->Rect().Width() << 16) |
            (TUint32)(iWidget->Rect().Height() & 0xffff));""")
    return text + DRAW


def patch_header(text: str) -> str:
    if "HtcleoDrawWallpaper(" not in text:
        text = once(text, "    CEikListBox* Widget() const;",
            "    CEikListBox* Widget() const;\n"
            "    TBool HtcleoDrawWallpaper(CWindowGc&, const TRect&, const TRect&) const;")
        text = once(text, "    mutable TBool iIsSwapFloating;",
                    "    mutable TBool iIsSwapFloating;\n    CFbsBitmap* iHtcleoWallpaper;")
    return text


def patch_grid(text: str) -> str:
    if "HTCLEO_MMGRID_FULL_CLIENT_WALLPAPER_V1" in text:
        return text
    return once(text, "    iView->Draw(&aRect);",
        """    // HTCLEO_MMGRID_FULL_CLIENT_WALLPAPER_V1
    // ClearMargins above uses the old skin. Cover it with the same client
    // wallpaper used by ViewRect and empty cells before drawing real items.
    iMmDrawer->HtcleoDrawWallpaper(*gc, Rect(), aRect);
    iView->Draw(&aRect);""")


def patch_container(text: str) -> str:
    if "HTCLEO_MMCONTAINER_FULL_CLIENT_WALLPAPER_V1" in text:
        return text
    text = once(text,
        """void CMmWidgetContainer::Draw( const TRect& /*aRect*/) const
    {
    // do nothing
    }""",
        """void CMmWidgetContainer::Draw( const TRect& aRect) const
    {
    // HTCLEO_MMCONTAINER_FULL_CLIENT_WALLPAPER_V1
    if (iWidget && iWidget->View() && iWidget->View()->ItemDrawer())
        {
        CMmListBoxItemDrawer* drawer = static_cast<CMmListBoxItemDrawer*>(
            iWidget->View()->ItemDrawer());
        drawer->HtcleoDrawWallpaper(SystemGc(), Rect(), aRect);
        }
    }""")
    return once(text,
        "        TRect rect = iCoeEnv->ScreenDevice()->SizeInPixels();",
        """        TRect rect = RProcess().SecureId().iId == 0x101f4cd2u ?
            Rect() : TRect(iCoeEnv->ScreenDevice()->SizeInPixels());""")


def verify(drawer: str, header: str, grid: str, container: str) -> None:
    checks = {
        "cache": drawer.count(MARKER) == 1 and "iHtcleoWallpaper(NULL)" in drawer
            and drawer.count("iHtcleoWallpaper->Load(KWallpaper, 0)") == 1
            and header.count("CFbsBitmap* iHtcleoWallpaper;") == 1,
        "grid": grid.count("HTCLEO_MMGRID_FULL_CLIENT_WALLPAPER_V1") == 1,
        "container": container.count("HTCLEO_MMCONTAINER_FULL_CLIENT_WALLPAPER_V1") == 1,
        "empty cells": "HtcleoDrawWallpaper(*iGc, iWidget->Rect(), r)" in drawer,
        "no forced panel rect": "480, 800" not in DRAW,
        "no draw-time I/O": "Load(" not in DRAW and "file." not in DRAW,
        "stock real icons": "DrawFloatingItems( r );" in drawer and "iView->Draw(&aRect);" in grid,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise SystemExit("MM wallpaper verification failed: " + ", ".join(failed))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    args = p.parse_args()
    mm = args.root / "sf/app/homescreen/menufw/menufwui/mmwidgets"
    paths = [mm / "src/mmlistboxitemdrawer.cpp", mm / "inc/mmlistboxitemdrawer.h",
             mm / "src/mmgrid.cpp", mm / "src/mmwidgetcontainer.cpp"]
    transforms = [patch_drawer, patch_header, patch_grid, patch_container]
    sources = [fn(path.read_text(encoding="utf-8")) for fn, path in zip(transforms, paths)]
    verify(*sources)
    for path, source in zip(paths, sources):
        path.write_text(source, encoding="utf-8")
    print("HTCLEO_MATRIX_WALLPAPER=cached-HOMEBG-full-client-grid-and-empty-cells-no-chrome-change")


if __name__ == "__main__":
    main()
