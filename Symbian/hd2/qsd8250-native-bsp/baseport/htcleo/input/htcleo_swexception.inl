// HTCLEO_SW_EXCEPTION_OBSERVER_V4. Passive,last CenRep software-event snapshot.
// Bounded104-byte boot-lifetime heap buffer;no additional static RAM allocation.
// Never handles an exception. No user writes,files,trace output,wait/retry/timer.
#ifdef __SMP__
#error HTCLEO software-exception observer requires the verified native UP ABI
#endif
// Replaces the former cached crash-register-slot pointer;its address is read
// directly from the already-cached scheduler without any kernel API.
static volatile TUint32* gHtcleoSwWords;
static const TUint8 KHtcleoSwS[7]={15,16,16,14,1,1,30};

static TUint HtcleoSwExceptionEvent(
    TKernelEvent aEvent,TAny* a1,TAny*,TAny* aPrivate)
    {
    if(aEvent!=EEventSwExc || !aPrivate) return DKernelEventHandler::ERunNext;
    DThread& thread=Kern::CurrentThread();
    DProcess* owner=thread.iOwningProcess;
    if(thread.iThreadType!=EThreadUser || !owner || owner->iS.iSecureId!=0x10202be9u)
        return DKernelEventHandler::ERunNext;
    volatile TUint32* words=static_cast<TUint32*>(aPrivate);
    NKern::LockSystem();
    if(words[0]==1u) {NKern::UnlockSystem();return DKernelEventHandler::ERunNext;}
    words[0]=1u; //partial snapshots are never presented as valid context
    NKern::UnlockSystem();
    // Word1 is reserved;the old unrendered count does not gate any capture.
    words[2]=owner->iS.iSecureId;words[3]=owner->iId;
    words[4]=thread.iId;words[5]=(TUint32)(TLinAddr)a1;words[6]=NKern::TickCount();
    for(TInt i=8;i<25;++i) words[i]=0xffffffffu;
    words[12]=words[21]=(TUint32)KErrNotReady;
    TUint32 regs[18];TUint32 mask=0;
    __ASSERT_COMPILE(sizeof(TArmRegSet)<=sizeof(regs));
    // Native API supports current-thread exec context and clears its output.
    NKern::ThreadGetUserContext(&thread.iNThread,regs,mask);words[7]=mask;
    for(TInt i=0;i<3;++i)
        {
        const TInt index=15-i; //retain PC/LR/SP;unused CPSR was never displayed
        if(mask&(1u<<index)) words[8+i]=regs[index];
        }
    const TLinAddr base=(TLinAddr)thread.iUserStackRunAddress;
    const TLinAddr sp=(TLinAddr)words[10];
    // Same-ROM RaiseException:32-byte frame,saved caller LR at SP+24.
    // 924 proved abort->default terminate. Eight raw words include saved LRs
    // atSP+44 and+52. The pinned call_terminate_handler keeps its UCB in r4.
    if((mask&(1u<<13)) && words[9]==0x122f1a10u && !(sp&3u) && thread.iUserStackSize>=56 &&
        sp>=base && sp-base<=(TUint32)thread.iUserStackSize-56u)
        {
        TUint32 caller[8];
        const TInt r=Kern::ThreadRawRead(&thread,(const TAny*)(sp+24u),caller,sizeof(caller));
        words[12]=(TUint32)r;
        if(r==KErrNone)
            {
            for(TInt i=0;i<8;++i) words[13+i]=caller[i];
            const TUint32 ucb=caller[2];
            // Never treat an arbitrary r4 as an exception pointer. This exact
            // same-ROM chain and native ARM exception class must both match.
            if(words[5]==20u && caller[0]==0x1243f4edu && caller[3]==0x1243f56fu &&
                caller[5]==0x12440277u && caller[7]==0x124402d5u &&
                ucb>=32u && ucb<=0x7fffffa0u && !(ucb&7u))
                {
                TUint32 e[32];
                TInt result=Kern::ThreadRawRead(&thread,(const TAny*)(TLinAddr)(ucb-32u),e,sizeof(e));
                if(result==KErrNone)
                    {
                    if(e[8]==0x004d5241u && e[9]==0x002b2b43u)
                        {
                        // Same128-byte read. Cache positions are NOT asserted
                        // faultPCs;EHT may be stale after a failed next lookup.
                        words[17]=e[12];words[19]=e[13];
                        words[22]=e[0];words[23]=e[26];words[24]=e[27];
                        }
                    else result=KErrNotSupported;
                    }
                words[21]=(TUint32)result;
                }
            }
        }
    QsdDrainWriteBuffer();words[0]=2u;
    return DKernelEventHandler::ERunNext; //not EExcHandled or ETraceHandled
    }

static void HtcleoInstallSwExceptionObserver()
    {
    // TBool is native32-bit TInt;the existing nonzero installed guard retains
    // its meaning. Bit1 only prevents another observer allocation attempt.
    __ASSERT_COMPILE(sizeof(TBool)==4);
    if(gHtcleoCrashInstalled&2) return;
    gHtcleoCrashInstalled|=2;
    NKern::ThreadEnterCS();
    TUint32* words=static_cast<TUint32*>(Kern::AllocZ(26*sizeof(TUint32)));
    if(words)
        {
        DKernelEventHandler* handler=new DKernelEventHandler(HtcleoSwExceptionEvent,words);
        if(handler && handler->Add()==KErrNone)
            {words[25]=1u;QsdDrainWriteBuffer();gHtcleoSwWords=words;}
        else
            {if(handler) handler->Close();Kern::Free(words);}
        }
    NKern::ThreadLeaveCS();
    }

static void HtcleoSwExceptionValues(
    const TUint32* subject,const TUint32* category,TUint32* values)
    {
    // Post-crash RAM reads only. Fields2/3 now show unwind cache,not userPC/LR.
    // Interpret cache only on successful metadata capture,not a guessed backtrace.
    for(TInt i=0;i<16;++i) values[i]=0xffffffffu;
    values[1]=0u;
    const volatile TUint32* words=gHtcleoSwWords;
    if(!words) return;
    TUint32 valid=words[25]==1u?1u:0u;
    if(words[0]==2u) valid|=2u;
    if((subject[5]&15u)==15u && subject[0]==0x10202be9u &&
        words[2]==subject[0] && words[3]==subject[2] && words[4]==subject[1]) valid|=4u;
    if(subject[4]==3u && ((subject[5]>>8)&255u)==2u &&
        category[0]==0x55534552u && category[1]==0x2d455845u &&
        category[2]==0x43000000u && category[3]==0u) valid|=8u;
    values[1]=valid|(words[7]<<8);
    if(valid!=15u) return;
    static const TUint8 fields[16]={5,0,17,19,10,13,12,6,16,18,20,21,15,22,23,24};
    for(TInt i=0;i<16;++i) if(i!=1) values[i]=words[fields[i]];
    if(values[11]!=0u) values[2]=values[3]=0xffffffffu;
    }
