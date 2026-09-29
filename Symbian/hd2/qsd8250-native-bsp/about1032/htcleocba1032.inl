#ifndef HTCLEO_CBA1032_INL
#define HTCLEO_CBA1032_INL
#include "htcleocba1007.inl"
static inline TBool HtcleoCbaScope1032(TUint32 aSid,TBool aPortrait,
    TBool aTouch,TBool aEmbedded,TBool aDialog,const TRect& aNominal,
    const TSize& aPhysical)
    {
    return HtcleoCbaScope1007(aSid,aPortrait,aTouch,aEmbedded,aDialog,aNominal,aPhysical) ||
        (aSid==0x10005a22u && HtcleoCbaScope1001(0x101f4cd2u,aPortrait,
            aTouch,aEmbedded,aDialog,aNominal,aPhysical));
    }
#endif
