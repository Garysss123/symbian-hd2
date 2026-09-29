#ifndef JAVA_GEOMETRY970_H
#define JAVA_GEOMETRY970_H
#include <e32std.h>
#include <gdi.h>
#include <hal.h>
#include <hal_data.h>
#include <layoutmetadata.cdl.h>
#include "geometry_policy970.h"

inline TRect JavaApplicationRect970(const TRect& original, TBool portrait)
    {
    if (!portrait || original.iTl != TPoint(0,0) ||
        original.iBr != TPoint(360,640)) return original;
    TInt width=0, height=0;
    const TInt xr=HAL::Get(HALData::EDisplayXPixels,width);
    const TInt yr=HAL::Get(HALData::EDisplayYPixels,height);
    if (Geometry970NominalRect(original.iTl.iX,original.iTl.iY,
            original.iBr.iX,original.iBr.iY,width,height,xr,yr,portrait))
        return TRect(TPoint(0,0),TSize(width,height));
    return original;
    }

inline TSize JavaFrameBufferSize970(const TSize& original, TBool portrait)
    {
    if (!portrait || original != TSize(360,640)) return original;
    TInt width=0, height=0;
    const TInt xr=HAL::Get(HALData::EDisplayXPixels,width);
    const TInt yr=HAL::Get(HALData::EDisplayYPixels,height);
    if (Geometry970NominalSize(original.iWidth,original.iHeight,
            width,height,xr,yr,portrait)) return TSize(width,height);
    return original;
    }
#endif
