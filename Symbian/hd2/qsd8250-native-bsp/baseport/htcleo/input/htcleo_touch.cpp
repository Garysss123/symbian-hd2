/* HTC Leo TYPE_2A capacitive touch controller. */

#include <kernel/kern_priv.h>
#include <e32event.h>
#include <e32hal.h>
#include <e32atomics.h>
#include <e32btrace.h>
#include <kernel/arm/arm_types.h>
#include "htcleo.h"
#include "htcleo_qsd8k.h"
#include "htcleo_threadstate.inl"

namespace
    {
    const TUint8 KTouchAddress = 0x15u;
    const TUint KTouchPollTicks = 20u;
    const TUint32 KTouchHighFallbackPolls = 10u;
    const TUint32 KTouchFocusRearmDelayPolls = 25u;
    const TUint32 KTouchPollingArmedStage = 0x54000302u;

    volatile TUint32 gHtcleoTouchStage;
    volatile TInt gHtcleoTouchResult;
    volatile TUint32 gHtcleoTouchDetail;
    volatile TUint32 gHtcleoTouchSamples;
    volatile TUint32 gHtcleoTouchEvents;
    volatile TUint32 gHtcleoTouchLastXY;
    volatile TUint32 gHtcleoTouchLatchedRaw;
    volatile TUint32 gHtcleoTouchLatchedXY;
    volatile TUint32 gHtcleoTouchRawFirst;
    volatile TUint32 gHtcleoTouchRawSecond;
    volatile TUint32 gHtcleoTouchPoints;
    volatile TUint32 gHtcleoTouchRawTransitions;
    volatile TUint32 gHtcleoTouchReadyReads;
    volatile TUint32 gHtcleoTouchNotReadySkips;
    volatile TUint32 gHtcleoTouchHighPolls;
    volatile TUint32 gHtcleoTouchFallbackReads;
    volatile TUint32 gHtcleoTouchFallbackContacts;
    volatile TInt gHtcleoTouchFallbackResult;
    // Matrix focus may expose a valid-packet/no-points controller state.
    // User-side HAL requests only publish a latch; the existing polling DFC
    // remains the sole I2C owner and performs the bounded re-arm write.
    volatile TUint32 gHtcleoTouchRearmRequest;
    volatile TUint32 gHtcleoTouchRearmComplete;
    volatile TInt gHtcleoTouchRearmResult = KErrNotReady;
    volatile TUint32 gHtcleoTouchRearmPending;
    volatile TUint32 gHtcleoTouchRearmDelay;

#include "htcleo_liveness.inl"

    inline TBool HtcleoTouchBeforeFirstSample()
        {
        return gHtcleoTouchStage == KTouchPollingArmedStage &&
               gHtcleoTouchSamples == 0u;
        }

    inline TUint32 HtcleoTouchVicState()
        {
        const TUint32 enabled = ReadReg(KHwBaseVic, EVicIntEn0);
        const TUint32 irq = ReadReg(KHwBaseVic, EVicIrqStatus0);
        const TUint32 raw = ReadReg(KHwBaseVic, EVicRawStatus0);
        return ((enabled & 0xffu) << 24) |
               ((irq & 0xffu) << 16) |
               (raw & 0xffffu);
        }

    inline TUint32 HtcleoTouchGptState()
        {
        const TUint32 enabled = ReadReg(KHwBaseCsr, EGptEnable);
        const TUint32 divider = ReadReg(KHwBaseCsr, EGptDivider);
        const TUint32 count = ReadReg(KHwBaseCsr, EGptCount);
        return ((enabled & 0xffu) << 24) |
               ((divider & 0xffu) << 16) |
               (count & 0xffffu);
        }

    inline void HtcleoTouchTrace(TUint32 aStage, TInt aResult,
                                 TUint32 aDetail)
        {
        gHtcleoTouchStage = aStage;
        gHtcleoTouchResult = aResult;
        gHtcleoTouchDetail = aDetail;
        }

    inline void HtcleoTouchResetResult(TInt aResult, TUint32 aDetail)
        {
        HtcleoTouchTrace(0x54000109u, aResult, aDetail);
        }

    static TInt TouchDiagnosticHal(TAny*, TInt aFunction, TAny* a1, TAny* a2)
        {
        switch (aFunction)
            {
            case 0: return static_cast<TInt>(gHtcleoTouchStage);
            case 1:
                return HtcleoTouchBeforeFirstSample() ?
                    static_cast<TInt>(HtcleoTouchVicState()) :
                    gHtcleoTouchResult;
            case 2:
                return HtcleoTouchBeforeFirstSample() ?
                    static_cast<TInt>(HtcleoTouchGptState()) :
                    static_cast<TInt>(gHtcleoTouchLatchedRaw ?
                        gHtcleoTouchLatchedRaw : gHtcleoTouchDetail);
            case 3: return static_cast<TInt>(gHtcleoTouchSamples);
            case 4: return static_cast<TInt>(gHtcleoTouchEvents);
            case 5:
                return HtcleoTouchBeforeFirstSample() ?
                    static_cast<TInt>(NKern::TickCount()) :
                    static_cast<TInt>(gHtcleoTouchLatchedRaw ?
                        gHtcleoTouchLatchedXY : gHtcleoTouchLastXY);
            case 6: return static_cast<TInt>(gHtcleoTouchRawFirst);
            case 7: return static_cast<TInt>(gHtcleoTouchRawSecond);
            case 8: return static_cast<TInt>(gHtcleoTouchPoints);
            case 9: return static_cast<TInt>(gHtcleoTouchRawTransitions);
            case 10:
                {
                const TUint32 request =
                    __e32_atomic_load_acq32(&gHtcleoTouchRearmRequest) + 1u;
                __e32_atomic_store_rel32(&gHtcleoTouchRearmRequest, request);
                return KErrNone;
                }
            case 11:
                return static_cast<TInt>(
                    __e32_atomic_load_acq32(&gHtcleoTouchRearmRequest));
            case 12:
                return static_cast<TInt>(
                    __e32_atomic_load_acq32(&gHtcleoTouchRearmComplete));
            case 13: return gHtcleoTouchRearmResult;
            case 14: return static_cast<TInt>(gHtcleoTouchReadyReads);
            case 15: return static_cast<TInt>(gHtcleoTouchNotReadySkips);
            case 16: return static_cast<TInt>(gHtcleoTouchRearmPending);
            case 17: return static_cast<TInt>(gHtcleoTouchRearmDelay);
            case 18: return static_cast<TInt>(gHtcleoTouchFallbackReads);
            case 19: return static_cast<TInt>(gHtcleoTouchFallbackContacts);
            case 20: return gHtcleoTouchFallbackResult;
            case 21: return HtcleoReadThreadState(a1, a2);
            case 22: return HtcleoLifeDiagnosticHal(a1, a2);
            default: return KErrNotSupported;
            }
        }

    class DHtcleoTouch
        {
    public:
        DHtcleoTouch();
        TInt Create();
        static void Poll(TAny* aPtr);
        static TInt DigitiserHal(TAny* aPtr, TInt aFunction,
                                 TAny* a1, TAny* a2);
        TInt DigitiserHalFunction(TInt aFunction, TAny* a1, TAny* a2);
        static TInt MouseHal(TAny* aPtr, TInt aFunction,
                             TAny* a1, TAny* a2);
        TInt MouseHalFunction(TInt aFunction, TAny* a1, TAny* a2);
    private:
        TInt ResetAndDetect();
        TInt ResetPanelOnce(TInt aCycle, TBool& aIrqLow);
        void Sample();
        static TInt Scale(TInt aValue, TInt aMin, TInt aMax, TInt aScreen);
    private:
        NTimer iTimer;
        NTimer iLifeTimer;
        TDfc iPollDfc;
        TBool iPointerOn;
        TBool iPressed;
        TInt iX;
        TInt iY;
        TInt iOrientation;
        };

    DHtcleoTouch::DHtcleoTouch()
        : iTimer(NULL, this), iLifeTimer(HtcleoLifeTimer, &iLifeTimer), iPollDfc(Poll, this, 1),
          iPointerOn(ETrue), iPressed(EFalse), iX(0), iY(0),
          iOrientation(0)
        {
        }

    TInt DHtcleoTouch::ResetPanelOnce(TInt aCycle, TBool& aIrqLow)
        {
        HtcleoTouchTrace(0x54000108u, KErrNone,
                         static_cast<TUint32>(aCycle));
        const TUint32 lowPins[] = { 108u, 160u, 82u, 27u };
        const TBool lowValues[] = { ETrue, EFalse, EFalse, EFalse };
        for (TUint i = 0; i < sizeof(lowPins) / sizeof(lowPins[0]); ++i)
            {
            const TInt r = HtcleoGpioWrite(lowPins[i], lowValues[i]);
            if (r != KErrNone)
                {
                HtcleoTouchResetResult(r, lowPins[i]);
                return r;
                }
            }
        Kern::NanoWait(10000000u);

        TInt r = HtcleoGpioWrite(82u, ETrue);
        if (r == KErrNone)
            r = HtcleoGpioWrite(27u, ETrue);
        if (r == KErrNone)
            r = HtcleoGpioWrite(160u, ETrue);
        if (r != KErrNone)
            {
            HtcleoTouchResetResult(r, 160u);
            return r;
            }

        TBool powerHigh = EFalse;
        for (TInt i = 0; i < 20; ++i)
            {
            r = HtcleoGpioRead(160u, powerHigh);
            if (r != KErrNone || powerHigh)
                break;
            (void)HtcleoGpioWrite(160u, ETrue);
            Kern::NanoWait(1000000u);
            }
        if (r != KErrNone || !powerHigh)
            {
            const TInt result = r == KErrNone ? KErrTimedOut : r;
            HtcleoTouchResetResult(result, 160u);
            return result;
            }
        Kern::NanoWait(20000000u);

        aIrqLow = EFalse;
        for (TInt i = 0; i < 50; ++i)
            {
            TBool high = ETrue;
            r = HtcleoGpioRead(92u, high);
            if (r != KErrNone)
                break;
            if (!high)
                {
                aIrqLow = ETrue;
                break;
                }
            Kern::NanoWait(10000000u);
            }
        if (r != KErrNone)
            {
            HtcleoTouchResetResult(r, 92u);
            return r;
            }

        TBool selectHigh = ETrue;
        for (TInt i = 0; i < 20; ++i)
            {
            r = HtcleoGpioWrite(108u, EFalse);
            if (r == KErrNone)
                r = HtcleoGpioRead(108u, selectHigh);
            if (r != KErrNone || !selectHigh)
                break;
            Kern::NanoWait(1000000u);
            }
        if (r != KErrNone || selectHigh)
            {
            const TInt result = r == KErrNone ? KErrTimedOut : r;
            HtcleoTouchResetResult(result, 108u);
            return result;
            }
        Kern::NanoWait(300000000u);
        HtcleoTouchResetResult(
            aIrqLow ? KErrNone : KErrTimedOut,
            (static_cast<TUint32>(aCycle) << 16) | 92u);
        return KErrNone;
        }

    TInt DHtcleoTouch::ResetAndDetect()
        {
        HtcleoTouchTrace(0x54000100u, KErrNone, 0u);
        const TUint32 outputs[] = { 160u, 108u, 82u, 27u };
        for (TUint i = 0; i < sizeof(outputs) / sizeof(outputs[0]); ++i)
            {
            TInt r = HtcleoTlmmConfigure(outputs[i], 0u, ETrue,
                                         EHtcleoNoPull, 0u);
            if (r != KErrNone && r != KErrTimedOut)
                {
                HtcleoTouchTrace(0x54000101u, r, outputs[i]);
                return r;
                }
            r = HtcleoGpioDirection(outputs[i], ETrue, EFalse);
            if (r != KErrNone)
                {
                HtcleoTouchTrace(0x54000102u, r, outputs[i]);
                return r;
                }
            }
        TInt r = HtcleoTlmmConfigure(92u, 0u, EFalse, EHtcleoPullUp, 3u);
        if (r != KErrNone && r != KErrTimedOut)
            {
            HtcleoTouchTrace(0x54000103u, r, 92u);
            return r;
            }
        r = HtcleoGpioDirection(92u, EFalse, EFalse);
        if (r != KErrNone)
            {
            HtcleoTouchTrace(0x54000104u, r, 92u);
            return r;
            }

        TUint8 id[4] = { 0, 0, 0, 0 };
        TUint32 i2cDiagnostic = 0u;
        TInt i2cInitialiseResult = KErrNone;
        TBool detected = EFalse;
        for (TInt cycle = 0; cycle < 3; ++cycle)
            {
            TBool irqLow = EFalse;
            r = ResetPanelOnce(cycle, irqLow);
            if (r != KErrNone)
                return r;
            if (irqLow)
                HtcleoTouchTrace(0x54000106u, KErrNone, 92u);
            else
                HtcleoTouchTrace(0x54000107u, KErrTimedOut, 92u);

            i2cInitialiseResult = HtcleoI2cInitialise();
            if (i2cInitialiseResult != KErrNone)
                {
                r = i2cInitialiseResult;
                continue;
                }
            id[0] = id[1] = id[2] = id[3] = 0u;
            i2cDiagnostic = 0u;
            r = HtcleoI2cRead(KTouchAddress, id, 4, 17, &i2cDiagnostic);
            if (r == KErrNone && id[0] == 0x55u)
                {
                detected = ETrue;
                break;
                }
            }
        if (i2cInitialiseResult != KErrNone)
            {
            HtcleoTouchTrace(0x54000200u, i2cInitialiseResult, 0u);
            return i2cInitialiseResult;
            }
        HtcleoTouchTrace(0x54000200u, KErrNone, 0u);
        TUint32 idDetail =
            (static_cast<TUint32>(id[0]) << 24) |
            (static_cast<TUint32>(id[1]) << 16) |
            (static_cast<TUint32>(id[2]) << 8) |
            static_cast<TUint32>(id[3]);
        if (r != KErrNone)
            idDetail = i2cDiagnostic;
        HtcleoTouchTrace(0x54000201u, r, idDetail);
        if (r != KErrNone)
            return r;
        if (!detected)
            {
            HtcleoTouchTrace(0x54000202u, KErrNotFound, idDetail);
            return KErrNotFound;
            }
        const TUint8 init[] = { 0xd0u, 0x00u, 0x01u };
        i2cDiagnostic = 0u;
        r = HtcleoI2cWrite(KTouchAddress, init, sizeof(init), 17,
                           &i2cDiagnostic);
        HtcleoTouchTrace(0x54000203u, r,
            r == KErrNone ? 0xd00001u : i2cDiagnostic);
        return r;
        }

    TInt DHtcleoTouch::Create()
        {
        HtcleoTouchTrace(0x54000300u, KErrNone, 0u);
        TInt r = ResetAndDetect();
        if (r != KErrNone)
            return r;
        /* HTCLEO_TYPE2A_DIGITISER_HAL_V1
         * This is a capacitive touchscreen, not a desktop mouse.  Registering
         * it as EHalGroupMouse makes MachineInfo report EXYInputMouse and keeps
         * Avkon's pen/touch paths disabled even though Kern::AddEvent succeeds.
         */
        r = Kern::AddHalEntry(EHalGroupDigitiser, DigitiserHal, this);
        HtcleoTouchTrace(0x54000301u, r, 0u);
        if (r != KErrNone)
            return r;
        /* HTCLEO_TYPE2A_DUAL_HAL_COMPAT_V1
         * Keep the real digitiser identity used by Avkon, but retain the
         * legacy mouse HAL contract that the original working HD2 polling
         * path exposed.  Some pre-digitiser Symbian components still query
         * this group while the raw events themselves remain pen events.
         */
        r = Kern::AddHalEntry(EHalGroupMouse, MouseHal, this);
        HtcleoTouchTrace(0x54000305u, r, 0u);
        if (r != KErrNone)
            return r;
        iPollDfc.SetDfcQ(Kern::DfcQue0());
        const TInt timerResult = iTimer.OneShot(KTouchPollTicks, iPollDfc);
        HtcleoTouchTrace(KTouchPollingArmedStage, timerResult, KTouchPollTicks);
        if (timerResult == KErrNone) HtcleoStartLifeProbe(iLifeTimer);
        return timerResult;
        }

    TInt DHtcleoTouch::Scale(TInt aValue, TInt aMin, TInt aMax, TInt aScreen)
        {
        if (aValue < aMin) aValue = aMin;
        if (aValue > aMax) aValue = aMax;
        return ((aValue - aMin) * (aScreen - 1)) / (aMax - aMin);
        }

    void DHtcleoTouch::Sample()
        {
        TUint8 packet[9];
        TUint32 i2cDiagnostic = 0u;
        const TInt readResult =
            HtcleoI2cRead(KTouchAddress, packet, sizeof(packet), 1,
                          &i2cDiagnostic);
        if (readResult != KErrNone)
            {
            HtcleoTouchTrace(0x54000401u, readResult,
                             i2cDiagnostic);
            return;
            }
        if (packet[0] != 0x5au)
            {
            HtcleoTouchTrace(0x54000402u, KErrCorrupt,
                (static_cast<TUint32>(packet[0]) << 24) |
                (gHtcleoTouchSamples & 0x00ffffffu));
            return;
            }
        const TUint points = (packet[8] >> 1) & 3u;
        const TUint32 rawFirst =
            (static_cast<TUint32>(packet[1]) << 24) |
            (static_cast<TUint32>(packet[2]) << 16) |
            (static_cast<TUint32>(packet[3]) << 8) |
            static_cast<TUint32>(packet[8]);
        const TUint32 rawSecond =
            (static_cast<TUint32>(packet[4]) << 24) |
            (static_cast<TUint32>(packet[5]) << 16) |
            (static_cast<TUint32>(packet[6]) << 8) |
            static_cast<TUint32>(packet[7]);
        /* HTCLEO_TYPE2A_RAW_PACKET_SNAPSHOT_V1: diagnostics only. */
        if (rawFirst != gHtcleoTouchRawFirst ||
            rawSecond != gHtcleoTouchRawSecond)
            ++gHtcleoTouchRawTransitions;
        gHtcleoTouchRawFirst = rawFirst;
        gHtcleoTouchRawSecond = rawSecond;
        gHtcleoTouchPoints = points;
        if (points != 0u)
            gHtcleoTouchLatchedRaw = rawFirst;
        HtcleoTouchTrace(0x54000403u, KErrNone,
            rawFirst);
        if (points == 0u)
            gHtcleoTouchLastXY = rawSecond;
        const TBool pressed = points != 0u;
        TRawEvent event;
        if (pressed)
            {
            const TInt rawX = packet[2] | ((packet[1] & 0xf0u) << 4);
            const TInt rawY = packet[3] | ((packet[1] & 0x0fu) << 8);
            iX = Scale(rawX, 6, 576, 480);
            iY = Scale(rawY, 6, 952, 800);
            gHtcleoTouchLastXY =
                (static_cast<TUint32>(iX & 0xffff) << 16) |
                static_cast<TUint32>(iY & 0xffff);
            gHtcleoTouchLatchedXY = gHtcleoTouchLastXY;
            event.Set(iPressed ? TRawEvent::EPointerMove :
                      TRawEvent::EButton1Down, iX, iY);
            const TInt addResult = Kern::AddEvent(event);
            if (addResult == KErrNone)
                ++gHtcleoTouchEvents;
            HtcleoTouchTrace(iPressed ? 0x54000502u : 0x54000501u,
                             addResult, gHtcleoTouchLastXY);
            }
        else if (iPressed)
            {
            event.Set(TRawEvent::EButton1Up, iX, iY);
            const TInt addResult = Kern::AddEvent(event);
            if (addResult == KErrNone)
                ++gHtcleoTouchEvents;
            HtcleoTouchTrace(0x54000503u, addResult,
                             gHtcleoTouchLastXY);
            }
        iPressed = pressed;
        }

    void DHtcleoTouch::Poll(TAny* aPtr)
        {
        DHtcleoTouch* self = static_cast<DHtcleoTouch*>(aPtr);
        ++gHtcleoTouchSamples;
        // HTCLEO_TYPE2A_FOCUS_REARM_V1
        // Never perform I2C from the synchronous HAL caller. Coalesce repeated
        // requests and execute on the normal polling DFC before its next read.
        const TUint32 rearmRequest =
            __e32_atomic_load_acq32(&gHtcleoTouchRearmRequest);
        const TUint32 rearmComplete =
            __e32_atomic_load_acq32(&gHtcleoTouchRearmComplete);
        if (rearmRequest != rearmComplete)
            {
            // HTCLEO_TYPE2A_FOCUS_REARM_DELAYED_V2
            // Avkon posts the request while its focus callback is still on
            // the stack. Delay the physical enable write by a bounded number
            // of the existing DFC polls so every foreground side effect has
            // completed. A newer request replaces and restarts the delay.
            if (gHtcleoTouchRearmPending != rearmRequest)
                {
                gHtcleoTouchRearmPending = rearmRequest;
                gHtcleoTouchRearmDelay = KTouchFocusRearmDelayPolls;
                gHtcleoTouchRearmResult = KErrNotReady;
                HtcleoTouchTrace(0x54000307u, KErrNotReady,
                    (rearmRequest << 8) | KTouchFocusRearmDelayPolls);
                }
            if (gHtcleoTouchRearmDelay != 0u)
                --gHtcleoTouchRearmDelay;
            if (gHtcleoTouchRearmDelay == 0u)
                {
                const TUint8 init[] = { 0xd0u, 0x00u, 0x01u };
                TUint32 diagnostic = 0u;
                const TInt rearmResult = HtcleoI2cWrite(
                    KTouchAddress, init, sizeof(init), 17, &diagnostic);
                gHtcleoTouchRearmResult = rearmResult;
                HtcleoTouchTrace(0x54000306u, rearmResult,
                    rearmResult == KErrNone ? rearmRequest : diagnostic);
                __e32_atomic_store_rel32(
                    &gHtcleoTouchRearmComplete, rearmRequest);
                }
            }
        /* HTCLEO_TYPE2A_IRQ_READY_GATED_POLL_V1
         * Keep the GPIO92 low-level data-ready path. The Linux reference also
         * provides an unconditional timer-read mode; a bounded slow read below
         * tests for real packets when the observed GPIO remains high. */
        TBool irqHigh = ETrue;
        const TInt irqResult = HtcleoGpioRead(92u, irqHigh);
        if (irqResult != KErrNone)
            {
            gHtcleoTouchHighPolls = 0u;
            gHtcleoTouchFallbackResult = KErrNone;
            /* Preserve the prior polling behavior if the already-configured
             * GPIO read itself fails; the error remains visible in stage 405. */
            HtcleoTouchTrace(0x54000405u, irqResult, 92u);
            ++gHtcleoTouchReadyReads;
            self->Sample();
            }
        else if (!irqHigh)
            {
            gHtcleoTouchHighPolls = 0u;
            gHtcleoTouchFallbackResult = KErrNone;
            ++gHtcleoTouchReadyReads;
            self->Sample();
            }
        else
            {
            ++gHtcleoTouchNotReadySkips;
            // HTCLEO_TYPE2A_HIGH_LEVEL_FALLBACK_V1
            // At most one additional real read per ten high polls (~200ms).
            // Use the same parser, one-attempt read and AddEvent path. No
            // controller reset, enable command, new timer or synthetic input.
            if (++gHtcleoTouchHighPolls >= KTouchHighFallbackPolls)
                {
                gHtcleoTouchHighPolls = 0u;
                const TUint32 eventsBefore = gHtcleoTouchEvents;
                const TUint32 transitionsBefore = gHtcleoTouchRawTransitions;
                ++gHtcleoTouchFallbackReads;
                self->Sample();
                gHtcleoTouchFallbackResult = gHtcleoTouchResult;
                // A repeated stale packet or an AddEvent failure is not
                // evidence that this fallback recovered fresh contact data.
                if (gHtcleoTouchFallbackResult == KErrNone &&
                    gHtcleoTouchEvents != eventsBefore &&
                    gHtcleoTouchRawTransitions != transitionsBefore &&
                    gHtcleoTouchPoints != 0u)
                    ++gHtcleoTouchFallbackContacts;
                }
            // Leave evidence visible to the existing 5s WServ heartbeat.
            // 406 means a fresh fallback contact has been seen in this boot;
            // it is not a claim of current contact or sustained UI operation.
            if (gHtcleoTouchFallbackResult != KErrNone)
                HtcleoTouchTrace(0x54000407u, gHtcleoTouchFallbackResult,
                    gHtcleoTouchFallbackReads);
            else if (gHtcleoTouchFallbackContacts != 0u)
                HtcleoTouchTrace(0x54000406u, KErrNone,
                    gHtcleoTouchFallbackContacts);
            else
                HtcleoTouchTrace(0x54000404u, KErrNone,
                    gHtcleoTouchNotReadySkips);
            }
        TInt timerResult = self->iTimer.Again(KTouchPollTicks);
        if (timerResult == KErrArgument)
            timerResult = self->iTimer.OneShot(KTouchPollTicks,
                                               self->iPollDfc);
        if (timerResult != KErrNone)
            HtcleoTouchTrace(0x54000304u, timerResult, KTouchPollTicks);
        }

    TInt DHtcleoTouch::DigitiserHal(TAny* aPtr, TInt aFunction,
                                    TAny* a1, TAny* a2)
        {
        return static_cast<DHtcleoTouch*>(aPtr)->DigitiserHalFunction(
            aFunction, a1, a2);
        }

    TInt DHtcleoTouch::DigitiserHalFunction(TInt aFunction, TAny* a1,
                                             TAny* a2)
        {
        switch (aFunction)
            {
            case EDigitiserHalXYInfo:
                {
                TPckgBuf<TDigitiserInfoV01> info;
                info().iDigitiserSize.iWidth = 480;
                info().iDigitiserSize.iHeight = 800;
                info().iOffsetToDisplay.iX = 0;
                info().iOffsetToDisplay.iY = 0;
                Kern::InfoCopy(*static_cast<TDes8*>(a1), info);
                return KErrNone;
                }
            case EDigitiserHalXYState:
                kumemput32(a1, &iPointerOn, sizeof(iPointerOn));
                return KErrNone;
            case EDigitiserHalSetXYState:
                iPointerOn = static_cast<TBool>(reinterpret_cast<TUint>(a1));
                return KErrNone;
            case EDigitiserOrientation:
                {
                if (static_cast<TBool>(reinterpret_cast<TUint>(a2)))
                    iOrientation = static_cast<TInt>(
                        reinterpret_cast<TUint>(a1));
                else
                    kumemput32(a1, &iOrientation, sizeof(iOrientation));
                return KErrNone;
                }
            default:
                return KErrNotSupported;
            }
        }

    TInt DHtcleoTouch::MouseHal(TAny* aPtr, TInt aFunction,
                                TAny* a1, TAny* a2)
        {
        return static_cast<DHtcleoTouch*>(aPtr)->MouseHalFunction(
            aFunction, a1, a2);
        }

    TInt DHtcleoTouch::MouseHalFunction(TInt aFunction, TAny* a1, TAny*)
        {
        switch (aFunction)
            {
            case EMouseHalMouseState:
                kumemput32(a1, &iPointerOn, sizeof(iPointerOn));
                return KErrNone;
            case EMouseHalSetMouseState:
                iPointerOn = static_cast<TBool>(reinterpret_cast<TUint>(a1));
                return KErrNone;
            case EMouseHalMouseInfo:
                {
                TPckgBuf<TMouseInfoV01> info;
                info().iMouseButtons = 1;
                info().iMouseAreaSize.iWidth = 480;
                info().iMouseAreaSize.iHeight = 800;
                info().iOffsetToDisplay.iX = 0;
                info().iOffsetToDisplay.iY = 0;
                Kern::InfoCopy(*static_cast<TDes8*>(a1), info);
                return KErrNone;
                }
            default:
                return KErrNotSupported;
            }
        }
    }

DECLARE_STANDARD_EXTENSION()
    {
    const TInt diagnosticResult = Kern::AddHalEntry(
        EHalGroupPlatformSpecific2, TouchDiagnosticHal, 0);
    HtcleoTouchTrace(0x54000001u, diagnosticResult, 0u);
    DHtcleoTouch* touch = new DHtcleoTouch;
    if (touch)
        {
        const TInt r = touch->Create();
        if (r == KErrNone)
            return KErrNone;
        delete touch;
        }
    else
        {
        HtcleoTouchTrace(0x54000002u, KErrNoMemory, 0u);
        }
    /* B8/68 are explicitly unsupported by the available HTC source, and an
     * absent 2A controller must not prevent the system from booting. */
    return KErrNone;
    }
