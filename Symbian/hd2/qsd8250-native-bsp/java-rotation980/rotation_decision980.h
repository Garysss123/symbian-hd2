#ifndef ROTATION_DECISION980_H
#define ROTATION_DECISION980_H
// Observation only. These bits explain the existing979 predicate, not a new policy.
inline unsigned Rotation980BlockMask(bool requested,bool ready,bool full,bool scaling,
    bool originalSize,bool targetSize,int width,int height,int x,int y,bool accelerated,
    bool egl,bool alf,bool direct,bool custom,bool partial)
    {
    return (!requested?1u:0u)|(!ready?2u:0u)|(!full?4u:0u)|(scaling?8u:0u)|
        (originalSize?16u:0u)|(targetSize?32u:0u)|(width!=480?64u:0u)|
        (height!=800?128u:0u)|((x||y)?256u:0u)|(accelerated?512u:0u)|
        (egl?1024u:0u)|(alf?2048u:0u)|(direct?4096u:0u)|(custom?8192u:0u)|
        (partial?16384u:0u);
    }

struct TRotationDecision980
    {
    int ctorManifest,ctorOrientation,manifest,orientation;
    unsigned requested,ready,block,flags;
    int x,y,viewW,viewH,contentW,contentH,bitmapW,bitmapH,windowW,windowH;
    int originalW,originalH,targetW,targetH;
    int halX,halY,panelW,panelH,mode,modeW,modeH,rotation,copy;
    };
#endif
