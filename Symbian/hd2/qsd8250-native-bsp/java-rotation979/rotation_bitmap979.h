#ifndef ROTATION_BITMAP979_H
#define ROTATION_BITMAP979_H
#include <fbs.h>
#include "rotation_policy979.h"

inline TInt Rotation979Bytes(TDisplayMode mode)
    {
    switch(mode)
        {
        case EColor64K:return 2;
        case EColor16M:return 3;
        case EColor16MU:case EColor16MA:case EColor16MAP:return 4;
        default:return 0;
        }
    }

inline TInt Rotation979Bitmap(CFbsBitmap& source,CFbsBitmap& dest)
    {
    const TSize sourceSize=source.SizeInPixels();
    const TSize destSize=dest.SizeInPixels();
    const TDisplayMode mode=source.DisplayMode();
    const TInt bpp=Rotation979Bytes(mode);
    const TInt sourceStride=source.DataStride();
    const TInt destStride=dest.DataStride();
    if(!bpp || dest.DisplayMode()!=mode || destSize!=TSize(480,800) ||
       sourceSize.iWidth<800 || sourceSize.iHeight<480 || sourceStride<=0 ||
       destStride<=0 || sourceStride>0x7fffffff/480 || destStride>0x7fffffff/800)
        return KErrNotSupported;
    // Gather metadata before data access; no allocations, leaves or UI calls
    // occur while the bitmap storage is pinned. Source is not modified.
    source.BeginDataAccess();
    dest.BeginDataAccess();
    const TUint8* in=reinterpret_cast<const TUint8*>(source.DataAddress());
    TUint8* out=reinterpret_cast<TUint8*>(dest.DataAddress());
    const TBool ok=Rotation979Copy(in,sourceStride*480,sourceStride,
        sourceSize.iWidth,sourceSize.iHeight,out,destStride*800,destStride,bpp);
    dest.EndDataAccess();
    source.EndDataAccess(ETrue);
    return ok?KErrNone:KErrCorrupt;
    }
#endif
