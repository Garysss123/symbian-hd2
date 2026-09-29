// HTCLEO_CRASH_NOTICE_V1. Resident extension subscriber to the EXISTING
// BTrace::ECtrlSystemCrashed notification; no core instruction or source patch.
// Normal trace records and all control requests are forwarded unchanged.
static BTrace::THandler gHtcleoPreviousTrace;
static BTrace::TControlFunction gHtcleoPreviousControl;
static TScheduler* gHtcleoCrashScheduler;
static volatile TUint32 gHtcleoCrashNotified;
static TBool gHtcleoCrashInstalled;
static const TUint8 KHtcleoCrashH[7] = {17,17,17,31,17,17,17};

// HTCLEO_SW_EXCEPTION_INCLUDE_V1
#include "htcleo_swexception.inl"

static TBool HtcleoTraceForward(TUint32 h, TUint32 h2, const TUint32 context,
    const TUint32 a1, const TUint32 a2, const TUint32 a3,
    const TUint32 extra, const TUint32 pc)
    {
    return gHtcleoPreviousTrace ?
        gHtcleoPreviousTrace(h,h2,context,a1,a2,a3,extra,pc) : EFalse;
    }

static TBool HtcleoCrashHookOwned()
    {
    // This indicates ownership of the forwarding TRACE handler. SetHandlers
    // installs the pair atomically; a later replacement is not fought/retried.
    return gHtcleoCrashScheduler &&
        gHtcleoCrashScheduler->iBTraceHandler == HtcleoTraceForward;
    }

// HTCLEO_FATAL_GLYPH_OUTLINE_V1_BEGIN
static void __attribute__((noinline)) HtcleoCrashGlyphLine(volatile TUint16* dest,TUint32 row)
    {
    for(TUint32 mask=16u;mask;mask>>=1)
        {
        const TUint16 pixel=row&mask?0xffffu:0x7800u;
        *dest++=pixel;*dest++=pixel;*dest++=pixel;
        }
    }

static void __attribute__((noinline)) HtcleoCrashGlyph(TInt left, TInt top, const TUint8* glyph)
    {
    volatile TUint16* const frame = reinterpret_cast<volatile TUint16*>(KHwBaseFrameBuffer);
    for (TInt y=0; y<7; ++y)
        for(TInt dy=0;dy<3;++dy)
            HtcleoCrashGlyphLine(frame+(top+y*3+dy)*480+left,glyph[y]);
    }
// HTCLEO_FATAL_GLYPH_OUTLINE_V1_END

static void HtcleoCrashRow(TInt y, const TUint32* values, const TUint8 labels[2][7])
    {
    for (TInt column=0; column<2; ++column)
        {
        const TInt x = 8 + column*240;
        HtcleoCrashGlyph(x,y,labels[column]);
        for (TInt digit=0; digit<8; ++digit)
            HtcleoCrashGlyph(x+(digit+1)*18,y,
                KHtcleoLifeHex[(values[column] >> ((7-digit)*4)) & 15u]);
        }
    QsdDrainWriteBuffer();
    WriteReg(KHwBaseMdp,0x44u,0u);
    QsdDrainWriteBuffer();
    }

// HTCLEO_SW_EXCEPTION_PAINT_V1_BEGIN
static void HtcleoSwExceptionPaint(const TUint32* subject,const TUint32* category)
    {
    if(subject[0]!=0x10202be9u || (subject[5]&15u)!=15u) return;
    TUint32 values[16];
    HtcleoSwExceptionValues(subject,category,values);
    volatile TUint16* const frame=reinterpret_cast<volatile TUint16*>(KHwBaseFrameBuffer);
    for(TInt y=258;y<482;++y)
        for(TInt x=0;x<480;++x) frame[y*480+x]=0x7800u;
    // Footer0..7 retained;8/9/A=LRs,B=metadata result,C=UCB candidate,
    // D=type-info pointer;2/3=unwind callsite/PR,E/F=fnstart/EHT cache.
    // Reuse the original bounded renderer;these are not a decoded backtrace.
    for(TInt i=0;i<8;++i)
        HtcleoCrashRow(258+i*28,values+i*2,&KHtcleoLifeHex[i*2]);
    }
// HTCLEO_SW_EXCEPTION_PAINT_V1_END

// HTCLEO_CRASH_SUBJECT_V1_BEGIN
static void __attribute__((noinline)) HtcleoCrashSubjectPaint(const TUint32* aOuter)
    {
    // Native UP DThread::Exit runs in the exiting thread's context. Decode
    // that subject ONLY for the verified outer KERN4 non-exception path.
    // No live-kernel APIs, descriptor dispatch, heap, locks or extra sampling.
#ifdef __SMP__
#error HTCLEO crash subject requires the verified native UP scheduler ABI
#endif
    __ASSERT_COMPILE(KMaxExitCategoryName == 16);
    __ASSERT_COMPILE(sizeof(TBufC<KMaxExitCategoryName>) == 20);
    __ASSERT_COMPILE(sizeof(TBufC8<KMaxExitCategoryName>) == 20);
    TUint32 subject[6] = {0xffffffffu,0xffffffffu,0xffffffffu,0u,0xffffffffu,0u};
    TUint32 category[4] = {0x3f3f3f3fu,0x3f3f3f3fu,0x3f3f3f3fu,0x3f3f3f3fu};
    const TUint8* categoryBytes = NULL;
    TUint32 categoryLength = 0u;
    if (aOuter[0] == 4u && aOuter[1] == 0x7fffffffu &&
        aOuter[4] == 0x4b45524eu && aOuter[5] == 0u && gHtcleoCrashScheduler)
        {
        subject[5] = 1u;
        const NThreadBase* nt = gHtcleoCrashScheduler->iCurrentThread;
        const TLinAddr address = reinterpret_cast<TLinAddr>(nt);
        if (nt && !(address & 3u) && address >= _FOFF(DThread,iNThread))
            {
            const DThread* thread = reinterpret_cast<const DThread*>(
                address - _FOFF(DThread,iNThread));
            if (thread->iContainerID == EThread+1)
                {
                subject[1] = thread->iId;
                subject[3] = thread->iFlags;
                subject[4] = (TUint32)thread->iExitReason;
                subject[5] |= 2u | ((TUint32)thread->iExitType << 8);
                const DProcess* owner = thread->iOwningProcess;
                if (owner && !(reinterpret_cast<TLinAddr>(owner) & 3u) &&
                    owner->iContainerID == EProcess+1)
                    {
                    subject[0] = owner->iS.iSecureId;
                    subject[2] = owner->iId;
                    subject[5] |= 4u;
                    }
                // In __KERNEL_MODE__, TBufC is the 8-bit inline EBufC form,
                // NOT the userland Unicode descriptor. Native e32cmn.h ABI.
                const TUint32* desc = reinterpret_cast<const TUint32*>(&thread->iExitCategory);
                const TUint32 packed = desc[0];
                if ((packed >> 28) == 0u && (packed & 0x0fffffffu) <= 16u)
                    {
                    categoryLength = packed & 0x0fffffffu;
                    categoryBytes = reinterpret_cast<const TUint8*>(desc+1);
                    subject[5] |= 8u;
                    }
                }
            }
        }
    static const TUint8 identity[2][7] = {
        {15,16,16,14,1,1,30}, {31,4,4,4,4,4,4} // S process SID / T thread ID
    };
    static const TUint8 process[2][7] = {
        {14,4,4,4,4,4,14}, {14,17,16,23,17,17,14} // I process ID / G thread flags
    };
    static const TUint8 exit[2][7] = {
        {17,17,10,4,10,17,17}, {17,17,17,17,17,10,4} // X original reason / V validity+type
    };
    HtcleoCrashRow(90,subject,identity);
    HtcleoCrashRow(118,subject+2,process);
    HtcleoCrashRow(146,subject+4,exit); // send identity before reading category payload
    if (categoryBytes)
        {
        for (TInt i=0; i<4; ++i) category[i] = 0u;
        for (TUint i=0; i<categoryLength; ++i)
            category[i/4] |= (TUint32)categoryBytes[i] << ((3-(i&3))*8);
        }
    static const TUint8 nameFirst[2][7] = {
        {14,17,17,31,17,17,17}, {30,17,17,30,17,17,30} // A / B exit category bytes0-7
    };
    static const TUint8 nameLast[2][7] = {
        {30,17,17,17,17,17,30}, {7,2,2,2,18,18,12} // D / J exit category bytes8-15
    };
    HtcleoCrashRow(174,category,nameFirst);
    HtcleoCrashRow(202,category+2,nameLast);
    const TUint32 counters[2] = {gHtcleoLifeKernel,gHtcleoLifeUser};
    static const TUint8 time[2][7] = {
        {17,18,20,24,20,18,17}, {17,17,17,17,17,17,14} // K / U full RAM counters at crash
    };
    HtcleoCrashRow(230,counters,time);
    HtcleoSwExceptionPaint(subject,category); //HTCLEO_SW_EXCEPTION_SUBJECT_V1
    }
// HTCLEO_CRASH_SUBJECT_V1_END

static void __attribute__((noinline)) HtcleoCrashNoticePaint()
    {
    // The notification is post-crash. NO live-kernel APIs, lock operations,
    // allocation, descriptor methods, tracing or interrupt re-enabling here.
    if (gHtcleoCrashNotified) return;
    gHtcleoCrashNotified = 1u; // also prevents the normal badge overwriting red
    if (ReadReg(KHwBaseMdp,0x90008u) != KHwPhysFrameBuffer ||
        ReadReg(KHwBaseMdp,0x90004u) != ((800u<<16)|480u) ||
        ReadReg(KHwBaseMdp,0x9000cu) != 960u)
        return;
    volatile TUint16* const frame = reinterpret_cast<volatile TUint16*>(KHwBaseFrameBuffer);
    for (TInt y=0; y<258; ++y)
        for (TInt x=0; x<480; ++x) frame[y*480+x] = 0x7800u;
    TUint32 data[6] = {0xffffffffu,0xffffffffu,0u,0u,0x3f3f3f3fu,0x3f3f3f3fu};
    const SFullArmRegSet* regs = gHtcleoCrashScheduler ?
        static_cast<const SFullArmRegSet*>(gHtcleoCrashScheduler->i_Regs) : NULL;
    if (regs && !((TLinAddr)regs & 3u))
        {
        data[0] = regs->iCrashArgs[1];
        data[1] = (TUint32)regs->iExcCode;
        data[2] = regs->iN.iR15;
        data[3] = regs->iN.iFlags;
        }
    static const TUint8 first[2][7] = {
        {31,16,16,30,16,16,16}, {31,16,16,30,16,16,31} // F reason / E exception kind
    };
    static const TUint8 second[2][7] = {
        {30,17,17,30,16,16,16}, {30,17,17,30,20,18,17} // P saved PC / R saved CPSR
    };
    HtcleoCrashRow(6,data,first);
    HtcleoCrashRow(34,data+2,second); // preserve primary evidence before category decode

    // Kern::Fault constructs a TPtrC8, and NotifyCrash stores its descriptor
    // address in iCrashArgs[0]. Decode only this exact two-word descriptor form.
    // Raw reads avoid TDes::Ptr() dispatch/panic paths in a stopped system.
    if (regs && !((TLinAddr)regs & 3u) && regs->iExcCode >= 0 &&
        regs->iCrashArgs[0] && !(regs->iCrashArgs[0] & 3u))
        {
        const TUint32* descriptor = reinterpret_cast<const TUint32*>(regs->iCrashArgs[0]);
        const TUint32 packed = descriptor[0];
        const TUint32 length = packed & 0x0fffffffu;
        if ((packed >> 28) == 1u && length <= 1024u && descriptor[1])
            {
            data[4] = data[5] = 0u;
            const TUint8* text = reinterpret_cast<const TUint8*>(descriptor[1]);
            for (TUint i=0; i<length && i<8u; ++i)
                data[4+i/4] |= (TUint32)text[i] << ((3-(i&3))*8);
            }
        }
    static const TUint8 third[2][7] = {
        {14,17,16,16,16,17,14}, {17,25,25,21,19,19,17} // C / N category first/next4
    };
    HtcleoCrashRow(62,data+4,third);
    HtcleoCrashSubjectPaint(data);
    }

static TInt HtcleoCrashControl(BTrace::TControl function, TAny* a1, TAny* a2)
    {
    if (function == BTrace::ECtrlSystemCrashed) HtcleoCrashNoticePaint();
    return gHtcleoPreviousControl ? gHtcleoPreviousControl(function,a1,a2) : KErrNotSupported;
    }

static void HtcleoInstallCrashNotice()
    {
    if (gHtcleoCrashInstalled) return;
    __ASSERT_COMPILE(sizeof(SFullArmRegSet) == 1024);
    __ASSERT_COMPILE(_FOFF(SFullArmRegSet,iExcCode) == 1008);
    __ASSERT_COMPILE(_FOFF(SFullArmRegSet,iCrashArgs) == 1012);
    gHtcleoCrashScheduler = TScheduler::Ptr();
    if (gHtcleoCrashScheduler->iBTraceHandler == HtcleoTraceForward) return;
    BTrace::SetHandlers(HtcleoTraceForward,HtcleoCrashControl,
        gHtcleoPreviousTrace,gHtcleoPreviousControl);
    gHtcleoCrashInstalled = ETrue;
    HtcleoInstallSwExceptionObserver(); //HTCLEO_SW_EXCEPTION_INSTALL_V1
    }
