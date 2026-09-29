#include "compat_canvas992.h"
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);exit(1);}++checks;}while(0)
static unsigned long checks=0;
static void render(int w,int h,int orientation,unsigned bpp)
    {
    TCompatCanvas992 p;CHECK(Compat992Plan(w,h,w,h,false,orientation,480,800,p));
    const unsigned ss=(w+7)*bpp+8,ds=480*bpp+16;
    std::vector<unsigned char> src(ss*(h+3),0x35),dst(ds*800+32,0xa6);
    for(int y=0;y<h;++y)for(int x=0;x<w;++x)for(unsigned c=0;c<bpp;++c)
        src[y*ss+x*bpp+c]=(unsigned char)((x*13+y*7+c*29)&255);
    const std::vector<unsigned char> prior=src;
    CHECK(Compat992Copy(p,&src[0],src.size(),ss,w+7,h+3,&dst[16],ds*800,ds,bpp));
    CHECK(src==prior);
    for(int py=0;py<800;++py)for(int px=0;px<480;++px)
        {
        int x,y;CHECK(Compat992Pointer(p,px,py,x,y));
        for(unsigned c=0;c<bpp;++c)
            {
            unsigned char expected=(x<0 || x>=w || y<0 || y>=h)?0:src[y*ss+x*bpp+c];
            if(bpp==4 && c==3)expected=255;
            CHECK(dst[16+py*ds+px*bpp+c]==expected);
            }
        }
    for(unsigned i=0;i<16;++i)CHECK(dst[i]==0xa6 && dst[16+ds*800+i]==0xa6);
    for(unsigned y=0;y<800;++y)for(unsigned i=480*bpp;i<ds;++i)CHECK(dst[16+y*ds+i]==0xa6);
    CHECK(!Compat992Copy(p,&src[0],1,ss,w+7,h+3,&dst[16],ds*800,ds,bpp));
    CHECK(!Compat992Copy(p,&src[0],src.size(),ss,w+7,h+3,&dst[16],ds*800-1,ds,bpp));
    CHECK(!Compat992Copy(p,&src[0],src.size(),ss,w-1,h+3,&dst[16],ds*800,ds,bpp));
    CHECK(!Compat992Copy(p,&src[0],src.size(),ss,w+7,h+3,&src[1],src.size()-1,ds,bpp));
    int x,y;CHECK(Compat992Pointer(p,INT_MIN,INT_MAX,x,y));CHECK(x<0 && y<0);
    }
int main()
    {
    TCompatCanvas992 p;
    CHECK(Compat992Plan(640,360,640,360,false,0,480,800,p));
    CHECK(p.rotate==1 && p.viewWidth==800 && p.viewHeight==450 && p.top==15 && p.left==0);
    CHECK(Compat992Plan(240,320,240,320,false,0,480,800,p));
    CHECK(p.rotate==0 && p.viewWidth==480 && p.viewHeight==640 && p.top==80);
    CHECK(!Compat992Plan(0,0,0,0,false,0,480,800,p)); // native Asphalt/Climate
    CHECK(!Compat992Plan(640,360,0,0,false,0,480,800,p)); // Java would pre-downscale
    CHECK(!Compat992Plan(640,360,480,270,false,0,480,800,p));
    CHECK(!Compat992Plan(640,360,640,360,true,0,480,800,p));
    CHECK(!Compat992Plan(640,360,640,360,false,0,360,640,p));
    CHECK(!Compat992Plan(1025,360,1025,360,false,0,480,800,p));
    CHECK(!Compat992Plan(1,360,1,360,false,0,480,800,p));
    CHECK(!Compat992Plan(640,360,640,360,false,3,480,800,p));
    CHECK(Compat992Sample(-1,640,800)<0);
    CHECK(Compat992Sample(800,640,800)>=640);
    const int cases[][3]={{640,360,0},{240,320,0},{240,400,0},{800,480,2},{640,360,1},{1024,768,0},{360,640,0}};
    for(unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);++i)
        for(unsigned bpp=2;bpp<=4;++bpp)render(cases[i][0],cases[i][1],cases[i][2],bpp);
    printf("COMPAT992_HOST_PASS checks=%lu cases=21\n",checks);return 0;
    }
