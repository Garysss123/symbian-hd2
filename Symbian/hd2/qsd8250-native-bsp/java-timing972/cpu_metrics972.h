#ifndef CPU_METRICS972_H
#define CPU_METRICS972_H
// Observation only: no Canvas state, clock, callback or completion is changed.
struct TCpuMetrics972
    {
    unsigned serial,lastBegin,start,gap,update,draw,finish,active,overlap;
    unsigned emitted,lastReport,gapLimit,slowLimit,heartbeatLimit;
    unsigned previousElapsed,reportedPreviousElapsed;
    void Configure(unsigned us)
        {
        if(!us){gapLimit=slowLimit=heartbeatLimit=0;return;}
        gapLimit=slowLimit=1u+(2500000u-1u)/us;
        heartbeatLimit=1u+(15000000u-1u)/us;
        }
    unsigned Begin(unsigned now)
        {
        if(emitted || serial==0xffffffffu)return 0;
        if(active){++overlap;return 0;}
        if(!serial)lastReport=now;
        gap=serial?now-lastBegin:0;lastBegin=now;
        reportedPreviousElapsed=previousElapsed;
        ++serial;active=serial;start=now;update=draw=finish=overlap=0;
        return active;
        }
    void Add(unsigned token,unsigned phase,unsigned ticks)
        {
        if(!token || active!=token)return;
        if(phase==1)update+=ticks;
        else if(phase==2)draw+=ticks;
        else if(phase==3)finish+=ticks;
        }
    unsigned Reason(unsigned token,unsigned elapsed) const
        {
        if(!token || active!=token || emitted)return 0;
        if(!gapLimit)return 8u; // HAL unavailable; report raw ticks, not ms.
        unsigned why=0;
        if(serial>1 && gap>=gapLimit)why|=1u;
        if(elapsed>=slowLimit)why|=2u;
        if(lastBegin-lastReport>=heartbeatLimit)why|=4u;
        return why;
        }
    bool End(unsigned token,unsigned elapsed)
        {
        if(!token || active!=token)return false;
        active=0;previousElapsed=elapsed;return true;
        }
    bool Publish()
        {if(emitted)return false;emitted=1;return true;}
    };
#endif
