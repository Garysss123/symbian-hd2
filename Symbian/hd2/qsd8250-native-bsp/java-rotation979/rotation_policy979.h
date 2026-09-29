#ifndef ROTATION_POLICY979_H
#define ROTATION_POLICY979_H
#include <stddef.h>
// CPU-only presentation contract. Logical (x,y) -> physical (479-y,x).
// No dependency on a game UID, file name, timer, or gravity sensor.
inline bool Rotation979Eligible(bool requested,bool ready,bool fullscreen,
    bool scaling,int width,int height,bool accelerated,bool egl,bool pixelSource,
    bool directContent,bool partialKeyboard)
    {
    return requested && ready && fullscreen && !scaling && width==480 &&
        height==800 && !accelerated && !egl && !pixelSource && !directContent &&
        !partialKeyboard;
    }

inline void Rotation979Pointer(int physicalX,int physicalY,int& logicalX,int& logicalY)
    {
    // Keep out-of-bounds drag coordinates out of bounds; do not clamp them.
    logicalX=physicalY;logicalY=479-physicalX;
    }

inline bool Rotation979Copy(const unsigned char* source,unsigned sourceBytes,
    unsigned sourceStride,unsigned sourceWidth,unsigned sourceHeight,
    unsigned char* dest,unsigned destBytes,unsigned destStride,unsigned bpp)
    {
    if(!source || !dest || source==dest || (bpp!=2 && bpp!=3 && bpp!=4) ||
       sourceWidth<800 || sourceHeight<480 || sourceWidth>0x7fffffffu/bpp ||
       sourceStride<sourceWidth*bpp || destStride<480*bpp ||
       sourceStride>0x7fffffffu/480 || destStride>0x7fffffffu/800 ||
       sourceBytes<sourceStride*480 || destBytes<destStride*800)return false;
    // Different start pointers can still alias. Compare address differences,
    // avoiding undefined unrelated-pointer ordering and end-address overflow.
    const size_t sourceAddress=reinterpret_cast<size_t>(source);
    const size_t destAddress=reinterpret_cast<size_t>(dest);
    if((sourceAddress<=destAddress && destAddress-sourceAddress<sourceStride*480u) ||
       (destAddress<sourceAddress && sourceAddress-destAddress<destStride*800u))
        return false;
    // Destination-row order; use bytes to avoid unaligned ARM accesses.
    for(unsigned py=0;py<800;++py)
        {
        unsigned char* out=dest+py*destStride;
        for(unsigned px=0;px<480;++px)
            {
            const unsigned char* in=source+(479-px)*sourceStride+py*bpp;
            for(unsigned channel=0;channel<bpp;++channel)out[px*bpp+channel]=in[channel];
            }
        }
    return true;
    }
#endif
