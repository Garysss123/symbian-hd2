#ifndef HTCLEO_ABOUT_PAINT1032_INL
#define HTCLEO_ABOUT_PAINT1032_INL
#ifndef HTCLEO_ABOUT1032_TEST
#include <w32std.h>
#endif
static inline TBool HtcleoAboutStatusScope1032(TUint32 aSid,TBool aPortrait)
    {return aSid==0x10005a22u && aPortrait;}

// Use the caller's actual control coordinates, not a nominal theme bitmap.
// The caller retains this damage clip for its content, then cancels it.
static inline TBool HtcleoAboutPaintBegin1032(CWindowGc& aGc,
    const TRect& aBounds,const TRect& aDamage)
    {
    if(aBounds.IsEmpty() || aDamage.IsEmpty())return EFalse;
    TRect clip(aDamage);clip.Intersection(aBounds);
    if(clip.IsEmpty())return EFalse;
    aGc.SetClippingRect(clip);
    TRgb background(KRgbBlack);background.SetAlpha(255);
    aGc.SetPenStyle(CGraphicsContext::ENullPen);
    aGc.SetBrushStyle(CGraphicsContext::ESolidBrush);
    aGc.SetBrushColor(background);
    aGc.DrawRect(aBounds);
    aGc.SetPenStyle(CGraphicsContext::ESolidPen);
    aGc.SetBrushStyle(CGraphicsContext::ENullBrush);
    aGc.SetPenColor(KRgbWhite);
    return ETrue;
    }
#endif
