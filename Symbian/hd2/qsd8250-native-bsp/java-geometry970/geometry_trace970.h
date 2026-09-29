#ifndef GEOMETRY_TRACE970_H
#define GEOMETRY_TRACE970_H
#include <e32atomics.h>
#include <logger.h>
#include "java_geometry970.h"

// One native geometry record per process, only at a visible fullscreen paint.
// Observation storage does not change a Canvas object or its public ABI.
static volatile TUint32 gGeometry970Recorded=0;
inline void JavaGeometryTrace970(TSize view,TSize content,TSize bitmap,
    TSize window,TUint32 flags)
    {
    TUint32 expected=0;
    if (!__e32_atomic_cas_ord32(&gGeometry970Recorded,&expected,1)) return;
    TInt width=0,height=0;
    const TInt xr=HAL::Get(HALData::EDisplayXPixels,width);
    const TInt yr=HAL::Get(HALData::EDisplayYPixels,height);
    java::util::Logger::Log(EUtils,EError,
        "J9GEO970 vw=%d vh=%d cw=%d ch=%d bw=%d bh=%d ww=%d wh=%d px=%d py=%d xr=%d yr=%d flags=%u",
        view.iWidth,view.iHeight,content.iWidth,content.iHeight,
        bitmap.iWidth,bitmap.iHeight,window.iWidth,window.iHeight,
        width,height,xr,yr,flags);
    }
#endif
