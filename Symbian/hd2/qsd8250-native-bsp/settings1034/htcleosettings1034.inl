#ifndef HTCLEO_SETTINGS1034_INL
#define HTCLEO_SETTINGS1034_INL
#include "htcleocba1032.inl"
#include "htcleoaboutpaint1032.inl"
static inline TBool HtcleoSettingsScope1034(TUint32 aSid,TBool aPortrait)
    {return aSid==0x100058ecu && aPortrait;}
static inline TBool HtcleoDarkStatusScope1034(TUint32 aSid,TBool aPortrait)
    {return HtcleoAboutStatusScope1032(aSid,aPortrait) || HtcleoSettingsScope1034(aSid,aPortrait);}
static inline TBool HtcleoCbaScope1034(TUint32 aSid,TBool aPortrait,
    TBool aTouch,TBool aEmbedded,TBool aDialog,const TRect& aNominal,
    const TSize& aPhysical)
    {
    return HtcleoCbaScope1032(aSid,aPortrait,aTouch,aEmbedded,aDialog,aNominal,aPhysical) ||
        (aSid==0x100058ecu && HtcleoCbaScope1001(0x101f4cd2u,aPortrait,
            aTouch,aEmbedded,aDialog,aNominal,aPhysical));
    }
#endif
