#ifndef COMPAT_BITMAP992_H
#define COMPAT_BITMAP992_H
#include <fbs.h>
#include "compat_canvas992.h"
#include "rotation_bitmap979.h"

inline TInt Compat992Bitmap(const TCompatCanvas992& plan,CFbsBitmap& source,CFbsBitmap& dest)
    {
    const TSize src=source.SizeInPixels(),dst=dest.SizeInPixels();
    const TInt bpp=Rotation979Bytes(source.DisplayMode());
    const TInt ss=source.DataStride(),ds=dest.DataStride();
    if(!Compat992Valid(plan) || !bpp || dest.DisplayMode()!=source.DisplayMode() ||
        dst!=TSize(480,800) || src.iWidth<plan.width || src.iHeight<plan.height ||
        ss<=0 || ds<=0 || ss>0x7fffffff/plan.height || ds>0x7fffffff/800)
        return KErrNotSupported;
    source.BeginDataAccess();dest.BeginDataAccess();
    const TBool ok=Compat992Copy(plan,reinterpret_cast<const TUint8*>(source.DataAddress()),
        ss*plan.height,ss,src.iWidth,src.iHeight,
        reinterpret_cast<TUint8*>(dest.DataAddress()),ds*800,ds,bpp);
    dest.EndDataAccess();source.EndDataAccess(ETrue);
    return ok?KErrNone:KErrCorrupt;
    }
#endif
