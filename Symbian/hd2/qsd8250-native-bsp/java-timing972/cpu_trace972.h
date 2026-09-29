#ifndef CPU_TRACE972_H
#define CPU_TRACE972_H
#include <e32atomics.h>
#include <logger.h>
#include "java_geometry970.h"
#include "cpu_metrics972.h"

static volatile TUint32 gCpuOwner972=0;
static volatile TUint32 gCpuOther972=0;
static volatile TUint32 gCpuDone972=0;
static const void* gCpuCanvas972=0;
static TInt gCpuHalRc972=0;
static TInt gCpuHalUs972=0;
static TCpuMetrics972 gCpuMetrics972={0};
__ASSERT_COMPILE(sizeof(TCpuMetrics972)==64 && sizeof(TUint32)==4);

inline TUint32 CpuBegin972(const void* canvas,TBool eligible)
    {
    if(!eligible || __e32_atomic_load_acq32(&gCpuDone972))return 0;
    const TUint32 tid=(TUint32)RThread().Id().Id();TUint32 expected=0;
    if(__e32_atomic_cas_ord32(&gCpuOwner972,&expected,tid))
        {
        gCpuCanvas972=canvas;
        gCpuHalRc972=HAL::Get(HALData::ENanoTickPeriod,gCpuHalUs972);
        gCpuMetrics972.Configure(gCpuHalRc972==0 && gCpuHalUs972>0?
            (unsigned)gCpuHalUs972:0u);
        }
    if(gCpuOwner972!=tid)
        {__e32_atomic_store_rel32(&gCpuOther972,1);return 0;}
    if(gCpuCanvas972!=canvas || gCpuMetrics972.emitted)return 0;
    return gCpuMetrics972.Begin(User::NTickCount());
    }

inline TUint32 CpuToken972(const void* canvas)
    {
    if(__e32_atomic_load_acq32(&gCpuDone972))return 0;
    if(gCpuOwner972!=(TUint32)RThread().Id().Id() || gCpuCanvas972!=canvas)return 0;
    if(!gCpuMetrics972.active)return 0;
    return gCpuMetrics972.active;
    }

inline void CpuPhase972(TUint32 token,TUint32 phase,TUint32 ticks)
    {gCpuMetrics972.Add(token,phase,ticks);}

inline void CpuEnd972(TUint32 token,const void* canvas,TBool async,
    TSize view,TSize content,TSize bitmap,TSize window,TUint32 flags)
    {
    if(!token || CpuToken972(canvas)!=token)return;
    const TUint32 elapsed=User::NTickCount()-gCpuMetrics972.start;
    const TUint32 why=gCpuMetrics972.Reason(token,elapsed);
    const TCpuMetrics972 sample=gCpuMetrics972;
    if(!gCpuMetrics972.End(token,elapsed) || !why || !gCpuMetrics972.Publish())return;
    __e32_atomic_store_rel32(&gCpuDone972,1);
    java::util::Logger::Log(EUtils,EError,
        "J9CPU972 n=%u owner=%u rc=%d us=%d gap=%u native=%u previous=%u update=%u draw=%u finish=%u overlap=%u other=%u why=%u async=%u vw=%d vh=%d cw=%d ch=%d bw=%d bh=%d ww=%d wh=%d flags=%u",
        sample.serial,(TUint32)gCpuOwner972,gCpuHalRc972,gCpuHalUs972,
        sample.gap,elapsed,sample.reportedPreviousElapsed,sample.update,
        sample.draw,sample.finish,sample.overlap,(TUint32)__e32_atomic_load_acq32(&gCpuOther972),why,
        async?1u:0u,view.iWidth,view.iHeight,content.iWidth,content.iHeight,
        bitmap.iWidth,bitmap.iHeight,window.iWidth,window.iHeight,flags);
    }
#endif
