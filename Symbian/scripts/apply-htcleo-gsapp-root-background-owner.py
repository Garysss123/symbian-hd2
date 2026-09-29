#!/usr/bin/env python3
"""848: root-private native list/view subclass owns one background fill."""
import argparse
import hashlib
from pathlib import Path

REL=Path('sf/mw/gsprofilesrv/gssettingsuis/Gs/GSApplication/Src/GSMainContainer.cpp')
BASE_SOURCE='20695b9341dede21eac0d9331c79794ea6dfc6a934d5a96ec5014db32fdfde0b'
MARKER='HTCLEO_GS_ROOT_BACKGROUND_OWNER_848'
ANCHOR='//CONSTANTS\n'
OLD_NEW='    iListBox = new( ELeave ) CAknSingleLargeStyleListBox;\n'
NEW_NEW='    iListBox = new( ELeave ) CHtcleoGsRootListBox;\n'
BLOCK='''
// HTCLEO_GS_ROOT_BACKGROUND_OWNER_848
static const TInt KHtcleoGsBackgroundMask =
    CListItemDrawer::EDrawWholeBackground | CListItemDrawer::EBackgroundDrawn;

struct THtcleoGsBackgroundFlags
    {
    CListItemDrawer* iDrawer;
    TInt iSaved;
    };

static void HtcleoGsRestoreBackgroundFlags(TAny* aState)
    {
    THtcleoGsBackgroundFlags* state =
        static_cast<THtcleoGsBackgroundFlags*>(aState);
    state->iDrawer->ClearFlags(KHtcleoGsBackgroundMask);
    state->iDrawer->SetFlags(state->iSaved & KHtcleoGsBackgroundMask);
    }

// Keep Avkon's filtering/empty-list/selection model. Only Draw is overridden.
class CHtcleoGsRootListView : public CAknColumnListBoxView
    {
public:
    virtual void Draw(const TRect* aRect = NULL) const
        {
        CListItemDrawer* drawer = ItemDrawer();
        if (!drawer || !iGc || RedrawDisabled() || !IsVisible() ||
            iViewRect.IsEmpty())
            {
            CColumnListBoxView::Draw(aRect);
            return;
            }
        THtcleoGsBackgroundFlags state = { drawer, drawer->Flags() };
        // Native leave cleanup restores just our two temporary bits; native
        // selection/single-click/ENativeImplementation updates are preserved.
        CleanupStack::PushL(TCleanupItem(HtcleoGsRestoreBackgroundFlags, &state));
        drawer->SetFlags(KHtcleoGsBackgroundMask);
        iGc->SetPenStyle(CGraphicsContext::ENullPen);
        iGc->SetBrushStyle(CGraphicsContext::ESolidBrush);
        iGc->SetBrushColor(BackColor());
        iGc->DrawRect(iViewRect);
        iGc->SetPenStyle(CGraphicsContext::ESolidPen);
        iGc->SetBrushStyle(CGraphicsContext::ENullBrush);
        // Native foreground drawing remains authoritative. The stock view
        // honours BackgroundDrawingSuppressed for item/unused-area clears.
        CColumnListBoxView::Draw(aRect);
        CleanupStack::PopAndDestroy();
        }
    };

class CHtcleoGsRootListBox : public CAknSingleLargeStyleListBox
    {
protected:
    virtual CListBoxView* MakeViewClassInstanceL()
        {
        return new(ELeave) CHtcleoGsRootListView;
        }
    };

__ASSERT_COMPILE(sizeof(CHtcleoGsRootListView) == sizeof(CAknColumnListBoxView));
__ASSERT_COMPILE(sizeof(CHtcleoGsRootListBox) == sizeof(CAknSingleLargeStyleListBox));
// HTCLEO_GS_ROOT_BACKGROUND_OWNER_848_END
'''

def transform(text,restore=False):
    if MARKER in text or NEW_NEW in text:
        if text.count(BLOCK)!=1 or text.count(NEW_NEW)!=1:
            raise ValueError('partial root-background owner overlay')
        text=text.replace(BLOCK,'',1).replace(NEW_NEW,OLD_NEW,1)
    if hashlib.sha256(text.encode('latin-1')).hexdigest()!=BASE_SOURCE:
        raise ValueError('background owner requires exact847 root source')
    if not restore:
        if text.count(ANCHOR)!=1 or text.count(OLD_NEW)!=1:raise ValueError('ambiguous root class/factory anchor')
        text=text.replace(ANCHOR,ANCHOR+BLOCK,1).replace(OLD_NEW,NEW_NEW,1)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--restore',action='store_true');a=p.parse_args()
    path=a.root/REL;old=path.read_text(encoding='latin-1');new=transform(old,a.restore)
    if transform(new,True)!=transform(old,True):raise ValueError('background owner inverse failed')
    if old!=new:path.write_text(new,encoding='latin-1')
    print('HTCLEO_GS_ROOT_BACKGROUND_OWNER='+('restored' if a.restore else 'private-Avkon-view-fill-once-native-foreground-temporary-mask-cleanup-no-geometry-or-filelog'))

if __name__=='__main__':main()
