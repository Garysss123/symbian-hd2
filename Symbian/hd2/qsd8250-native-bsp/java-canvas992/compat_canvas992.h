#ifndef COMPAT_CANVAS992_H
#define COMPAT_CANVAS992_H
#include <stddef.h>

// Fixed logical 2D Canvas -> HD2 portrait panel. No game UID, sensor or OS mode.
struct TCompatCanvas992
    {
    int width,height,rotate,viewWidth,viewHeight,left,top;
    };

inline bool Compat992Plan(int w,int h,int targetW,int targetH,bool scaleOnOrient,
    int orientation,int panelW,int panelH,TCompatCanvas992& p)
    {
    p.width=p.height=p.rotate=p.viewWidth=p.viewHeight=p.left=p.top=0;
    // A bounded existing-JAD opt-in. Native/adaptive apps (0,0) stay unchanged.
    // The stock Java Graphics layer only stops pre-downscaling when its target
    // equals the logical size. Never sample logical pixels from a shrunk image.
    if(w<2 || h<2 || w>1024 || h>1024 || targetW!=w || targetH!=h || scaleOnOrient ||
        orientation<0 || orientation>2 || panelW!=480 || panelH!=800)return false;
    p.width=w;p.height=h;
    // 0: fixed logical orientation, 1: explicit portrait, 2: explicit landscape.
    p.rotate=orientation==2 || (orientation==0 && w>h);
    const int sw=p.rotate?800:480,sh=p.rotate?480:800;
    if(sw*h<=sh*w){p.viewWidth=sw;p.viewHeight=sw*h/w;}
    else{p.viewHeight=sh;p.viewWidth=sh*w/h;}
    if(p.viewWidth<1 || p.viewHeight<1)return false;
    p.left=(sw-p.viewWidth)/2;p.top=(sh-p.viewHeight)/2;
    return true;
    }

inline bool Compat992Valid(const TCompatCanvas992& p)
    {
    TCompatCanvas992 check;
    if(!Compat992Plan(p.width,p.height,p.width,p.height,false,p.rotate?2:1,480,800,check))return false;
    return p.rotate==check.rotate && p.viewWidth==check.viewWidth &&
        p.viewHeight==check.viewHeight && p.left==check.left && p.top==check.top;
    }

inline int Compat992Sample(int pixel,int logical,int view)
    {
    // Pixel-centre nearest neighbour, also used by touch. Preserve off-screen
    // coordinates as off-screen, including the negative fractional boundary.
    if(pixel<-32768)return -1;
    if(pixel>32767)return logical;
    const int n=(pixel*2+1)*logical,d=view*2;
    return n>=0?n/d:-((-n+d-1)/d);
    }

inline bool Compat992Pointer(const TCompatCanvas992& p,int px,int py,int& x,int& y)
    {
    if(!Compat992Valid(p))return false;
    if(px<-32768 || py<-32768 || px>32767 || py>32767)
        {x=-1;y=-1;return true;}
    const int vx=p.rotate?py:px,vy=p.rotate?479-px:py;
    x=Compat992Sample(vx-p.left,p.width,p.viewWidth);
    y=Compat992Sample(vy-p.top,p.height,p.viewHeight);
    return true;
    }

inline bool Compat992Copy(const TCompatCanvas992& p,
    const unsigned char* source,unsigned sourceBytes,unsigned sourceStride,
    unsigned sourceWidth,unsigned sourceHeight,unsigned char* dest,
    unsigned destBytes,unsigned destStride,unsigned bpp)
    {
    if(!Compat992Valid(p) || !source || !dest || (bpp!=2 && bpp!=3 && bpp!=4) ||
        sourceWidth<(unsigned)p.width || sourceHeight<(unsigned)p.height ||
        sourceWidth>0x7fffffffu/bpp || sourceStride<sourceWidth*bpp ||
        sourceStride>0x7fffffffu/(unsigned)p.height ||
        sourceBytes<sourceStride*(unsigned)p.height || destStride<480*bpp ||
        destStride>0x7fffffffu/800 || destBytes<destStride*800)return false;
    const size_t s=reinterpret_cast<size_t>(source),d=reinterpret_cast<size_t>(dest);
    if((s<=d && d-s<sourceStride*(unsigned)p.height) ||
        (d<s && s-d<destStride*800u))return false;

    // A 960-byte row lookup avoids a division per presented pixel. The source
    // is read-only; the physical output is opaque, including all black bars.
    short lookup[480];
    for(int px=0;px<480;++px)
        {
        const int at=p.rotate?479-px-p.top:px-p.left;
        const int limit=p.rotate?p.viewHeight:p.viewWidth;
        lookup[px]=at<0 || at>=limit?-1:(short)Compat992Sample(at,
            p.rotate?p.height:p.width,limit);
        }
    for(int py=0;py<800;++py)
        {
        const int at=p.rotate?py-p.left:py-p.top;
        const int limit=p.rotate?p.viewWidth:p.viewHeight;
        const int row=at<0 || at>=limit?-1:Compat992Sample(at,
            p.rotate?p.width:p.height,limit);
        unsigned char* out=dest+py*destStride;
        for(int px=0;px<480;++px)
            {
            unsigned char* pixel=out+px*bpp;
            if(row<0 || lookup[px]<0)
                {for(unsigned c=0;c<bpp;++c)pixel[c]=0;}
            else
                {
                const unsigned sx=p.rotate?(unsigned)row:(unsigned)lookup[px];
                const unsigned sy=p.rotate?(unsigned)lookup[px]:(unsigned)row;
                const unsigned char* in=source+sy*sourceStride+sx*bpp;
                for(unsigned c=0;c<bpp;++c)pixel[c]=in[c];
                }
            if(bpp==4)pixel[3]=255;
            }
        }
    return true;
    }
#endif
