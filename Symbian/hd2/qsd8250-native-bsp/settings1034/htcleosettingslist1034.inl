#ifndef HTCLEO_SETTINGS_LIST1034_INL
#define HTCLEO_SETTINGS_LIST1034_INL
// Temporary background ownership, not a persistent skin/selection flag change.
// The native view still draws every real row, highlight, icon and empty text.
struct THtcleoSettingsListState1034
    {
    CListItemDrawer* iDrawer;
    TInt iFlags;
    };
static void HtcleoSettingsListRestore1034(TAny* aPtr)
    {
    THtcleoSettingsListState1034* s=static_cast<THtcleoSettingsListState1034*>(aPtr);
    const TInt mask=CListItemDrawer::EDrawWholeBackground | CListItemDrawer::EBackgroundDrawn;
    s->iDrawer->ClearFlags(mask);
    s->iDrawer->SetFlags(s->iFlags & mask);
    }
static inline TBool HtcleoSettingsListBegin1034(TBool aScope,
    CWindowGc* aGc,CListItemDrawer* aDrawer,const TRect& aBounds,
    const TRect& aDamage,THtcleoSettingsListState1034& aState)
    {
    if(!aScope || !aGc || !aDrawer || aBounds.IsEmpty() || aDamage.IsEmpty())return EFalse;
    TRect clip(aDamage);clip.Intersection(aBounds);
    if(clip.IsEmpty())return EFalse;
    aState.iDrawer=aDrawer;aState.iFlags=aDrawer->Flags();
    CleanupStack::PushL(TCleanupItem(HtcleoSettingsListRestore1034,&aState));
    HtcleoAboutPaintBegin1032(*aGc,aBounds,aDamage);
    aGc->CancelClippingRect(); // Native list/item clipping remains authoritative.
    aDrawer->SetFlags(CListItemDrawer::EDrawWholeBackground | CListItemDrawer::EBackgroundDrawn);
    return ETrue;
    }
#endif
