// HTCLEO_LOGLESS_LIVENESS_V1 -- one diagnostic badge, not a UI milestone.
// Included inside the touch extension's namespace, after its RAM counters.
// One 1-second NTimer ISR callback: no files, server IPC, heap, blocking locks,
// or busy waits. Uses only bounded pixel work and the ISR-safe NTimer rearm.
// K = callback count; P = touch DFC polls; U = file-free user pulse;
// F = completed KCT2 writes, with trailing I/O phase0/1/2/3.
static volatile TUint32 gHtcleoLifeKernel;
static volatile TUint32 gHtcleoLifeUser;
static volatile TUint32 gHtcleoLifeFileDone;
static volatile TUint32 gHtcleoLifeFilePhase;
static volatile TInt gHtcleoLifeFileError;
static TInt gHtcleoLifePeriod;

static const TUint8 KHtcleoLifeHex[16][7] = {
    {14,17,19,21,25,17,14}, {4,12,4,4,4,4,14},
    {14,17,1,2,4,8,31}, {30,1,1,14,1,1,30},
    {2,6,10,18,31,2,2}, {31,16,16,30,1,1,30},
    {14,16,16,30,17,17,14}, {31,1,2,4,8,8,8},
    {14,17,17,14,17,17,14}, {14,17,17,15,1,1,14},
    {14,17,17,31,17,17,17}, {30,17,17,30,17,17,30},
    {14,17,16,16,16,17,14}, {30,17,17,17,17,17,30},
    {31,16,16,30,16,16,31}, {31,16,16,30,16,16,16}
};
static const TUint8 KHtcleoLifeLabels[4][7] = {
    {17,18,20,24,20,18,17}, // K
    {30,17,17,30,16,16,16}, // P
    {17,17,17,17,17,17,14}, // U
    {31,16,16,30,16,16,16}  // F
};

static void HtcleoLifeGlyph(TInt aX, const TUint8* aRows, TUint16 aColour)
    {
    volatile TUint16* const frame =
        reinterpret_cast<volatile TUint16*>(KHwBaseFrameBuffer);
    for (TInt y = 0; y < 7; ++y)
        for (TInt x = 0; x < 5; ++x)
            {
            const TUint16 pixel = (aRows[y] & (1u << (4-x))) ? aColour : 0u;
            const TInt offset = (4 + y*2) * 480 + aX + x*2;
            frame[offset] = pixel;
            frame[offset+1] = pixel;
            frame[offset+480] = pixel;
            frame[offset+481] = pixel;
            }
    }

#include "htcleo_crashnotice.inl"

static void __attribute__((noinline)) HtcleoPaintLifeBadge()
    {
    if (gHtcleoCrashNotified) return;
    // Use only the established native full-screen RGB565 legacy scanout.
    // Never replace another buffer address, size, stride, or display state.
    if (ReadReg(KHwBaseMdp, 0x90008u) != KHwPhysFrameBuffer ||
        ReadReg(KHwBaseMdp, 0x90004u) != ((800u << 16) | 480u) ||
        ReadReg(KHwBaseMdp, 0x9000cu) != 960u)
        return;
    const TUint32 values[4] = {gHtcleoLifeKernel, gHtcleoTouchSamples,
        gHtcleoLifeUser, gHtcleoLifeFileDone};
    const TUint16 colours[4] = {0x07e0u, 0x07ffu, 0xffe0u, 0xf81fu};
    for (TInt field = 0; field < 4; ++field)
        {
        const TInt left = 4 + field*72;
        HtcleoLifeGlyph(left, KHtcleoLifeLabels[field], colours[field]);
        for (TInt digit = 0; digit < 4; ++digit)
            HtcleoLifeGlyph(left + (digit+1)*12,
                KHtcleoLifeHex[(values[field] >> ((3-digit)*4)) & 15u],
                colours[field]);
        }
    HtcleoLifeGlyph(284, KHtcleoLifeHex[gHtcleoLifeFilePhase & 15u],
        gHtcleoLifeFilePhase == 3u ? 0xf800u : 0xffffu);
    HtcleoLifeGlyph(308, KHtcleoCrashH, 0xffffu);
    HtcleoLifeGlyph(320, KHtcleoLifeHex[HtcleoCrashHookOwned() ? 1 : 0], 0xffffu);
    // HTCLEO_SW_EXCEPTION_BADGE_V1_BEGIN
    HtcleoLifeGlyph(344, KHtcleoSwS, 0xffffu);
    HtcleoLifeGlyph(356, KHtcleoLifeHex[gHtcleoSwWords && gHtcleoSwWords[25]==1u ? 1 : 0], 0xffffu);
    // HTCLEO_SW_EXCEPTION_BADGE_V1_END
    QsdDrainWriteBuffer();
    // MDDI is command-mode: RAM writes alone do NOT prove visible updates.
    // Use the established MdpRefresh DMA-P doorbell, without resetting its
    // configuration/interrupts. This adds one native refresh per second.
    WriteReg(KHwBaseMdp, 0x44u, 0u);
    QsdDrainWriteBuffer();
    }

static void HtcleoLifeTimer(TAny* aPtr)
    {
    ++gHtcleoLifeKernel;
    HtcleoPaintLifeBadge();
    // Any-context OneShot with no DFC argument means ISR callback, separate
    // from the existing touch timer's DfcQue0 callback. Never change that timer.
    (void)static_cast<NTimer*>(aPtr)->OneShot(gHtcleoLifePeriod);
    }

static void HtcleoStartLifeProbe(NTimer& aTimer)
    {
    __ASSERT_COMPILE(KFrameBufferWidth == 480 && KFrameBufferHeight == 800);
    __ASSERT_COMPILE(KFrameBufferStride == 960);
    // Validate the already-installed bootstrap mapping once, in thread context.
    // No new physical mapping or alias is created by this probe.
    if (Epoc::LinearToPhysical(KHwBaseFrameBuffer) != KHwPhysFrameBuffer)
        return;
    gHtcleoLifePeriod = NKern::TimerTicks(1000);
    if (gHtcleoLifePeriod > 0)
        {
        HtcleoInstallCrashNotice();
        (void)aTimer.OneShot(gHtcleoLifePeriod);
        }
    }

static TInt HtcleoLifeDiagnosticHal(TAny* aCommand, TAny* aValue)
    {
    if (Kern::CurrentThread().iOwningProcess->iS.iSecureId != 0x200286e3u)
        return KErrPermissionDenied;
    const TUint32 value = static_cast<TUint32>(reinterpret_cast<TUint>(aValue));
    // UP, naturally aligned words, one publisher per field; ISR is the reader.
    switch (reinterpret_cast<TUint>(aCommand))
        {
        case 0: gHtcleoLifeUser = value; break;
        case 1: gHtcleoLifeFilePhase = 1u; break;
        case 2: gHtcleoLifeFileDone = value; gHtcleoLifeFilePhase = 2u; break;
        case 3: gHtcleoLifeFileError = (TInt)value; gHtcleoLifeFilePhase = 3u; break;
        default: return KErrNotSupported;
        }
    return KErrNone;
    }
