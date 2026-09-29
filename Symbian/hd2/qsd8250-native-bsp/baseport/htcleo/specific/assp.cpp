/*
 * Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
 * Modifications Copyright (c) 2026 HTC Leo Symbian port contributors.
 * Licensed under the Eclipse Public License v1.0.
 */

#include <htcleo_priv.h>
#include <hal_data.h>

Htcleo* Htcleo::Variant = NULL;
GLDEF_D Htcleo TheVariant;

extern TInt HtcleoWFIIdle();

DECLARE_STANDARD_ASSP()

EXPORT_C Asic* VariantInitialise()
    {
    return &TheVariant;
    }

void Htcleo::Idle()
    {
    TInt irq = NKern::DisableAllInterrupts();
    HtcleoWFIIdle();
    NKern::RestoreInterrupts(irq);
    }

TUint32 Htcleo::NanoWaitCalibration()
    {
    /* Conservative value until the boot clock is queried from QSD hardware. */
    return 4;
    }

TInt Htcleo::VariantHal(TInt aFunction, TAny* a1, TAny* /* a2 */)
    {
    switch (aFunction)
        {
        case EVariantHalVariantInfo:
            {
            TVariantInfoV01Buf infoBuf;
            TVariantInfoV01& info = infoBuf();
            const TUint clockKHz = 998400u;
            info.iRomVersion = Epoc::RomHeader().iVersion;
            info.iMachineUniqueId = (TInt64(0x4854434c) << 32) | 0x51445338u;
            info.iLedCapabilities = 0;
            info.iProcessorClockInKHz = clockKHz;
            info.iSpeedFactor = clockKHz / 25u;
            Kern::InfoCopy(*(TDes8*)a1, infoBuf);
            break;
            }

        case EVariantHalDebugPortSet:
            {
            const TUint32 port = (TUint32)a1;
            if (port != (TUint32)KNullDebugPort && port != 0u)
                return KErrNotSupported;
            THtcleo::MarkDebugPortOff();
            Kern::SuperPage().iDebugPort = port;
            break;
            }

        case EVariantHalDebugPortGet:
            {
            const TUint32 port = Kern::SuperPage().iDebugPort;
            kumemput32(a1, &port, sizeof(port));
            break;
            }

        case EVariantHalSwitches:
        case EVariantHalLedMaskGet:
            {
            const TUint32 value = 0;
            kumemput32(a1, &value, sizeof(value));
            break;
            }

        case EVariantHalLedMaskSet:
            break;

        case EVariantHalCustomRestartReason:
            {
            const TInt reason = Kern::SuperPage().iHwStartupReason;
            kumemput32(a1, &reason, sizeof(reason));
            break;
            }

        case EVariantHalCustomRestart:
            __KERNEL_CAPABILITY_CHECK(
                if (!Kern::CurrentThreadHasCapability(
                        ECapabilityPowerMgmt,
                        __PLATSEC_DIAGNOSTIC_STRING(
                            "Checked by Hal function EVariantHalCustomRestart")))
                    return KErrPermissionDenied;
            )
            Kern::Restart(0);
            break;

        default:
            return KErrNotSupported;
        }

    return KErrNone;
    }

TPtr8 Htcleo::MachineConfiguration()
    {
    return TPtr8((TUint8*)&Kern::MachineConfig(), 40, 40);
    }

EXPORT_C Htcleo::Htcleo()
    : iDebugPortBase(0), iTimerQ(NULL)
    {
    }

EXPORT_C TMachineStartupType Htcleo::StartupReason()
    {
    return EStartupColdReset;
    }

EXPORT_C void Htcleo::Init1()
    {
    HtcleoInterrupt::Init1();
    }

EXPORT_C void Htcleo::Init3()
    {
    NTimerQ& timerQ = *(NTimerQ*)NTimerQ::TimerAddress();
    timerQ.iRounding = -5;
    iTimerQ = &timerQ;

    /* Keep both GPT and VIC master stopped until the handler is installed. */
    WriteReg(KHwBaseVic, EVicMasterEnable, 0u);
    /* HTC Leo's Linux QSD8K timer setup selects the 32.768 kHz GPT source
     * with the board-specific divider value 3 before clearing the timer. */
    WriteReg(KHwBaseCsr, EGptDivider, 3u);
    WriteReg(KHwBaseCsr, EGptEnable, 0u);
    WriteReg(KHwBaseCsr, EGptClear, 1u);
    WriteReg(KHwBaseCsr, EGptCount, 0u);
    QsdDrainWriteBuffer();

    TInt result = Interrupt::Bind(EIntGpt, HtcleoInterrupt::MsTimerTick, &timerQ);
    if (result == KErrNone)
        result = Interrupt::Enable(EIntGpt);
    if (result != KErrNone)
        Kern::Fault("HTCLeoTick", result);

    WriteReg(KHwBaseVic, EVicIntClear0, 1u << EIntGpt);
    WriteReg(KHwBaseCsr, EGptMatch, K1000HzTickMatchLoad);
    WriteReg(KHwBaseCsr, EGptEnable, 3u); /* enable + clear-on-match */
    QsdDrainWriteBuffer();
    WriteReg(KHwBaseVic, EVicMasterEnable, 3u);
    QsdDrainWriteBuffer();

    THtcleo::Init3();
    HtcleoInterrupt::Init3();
    }

EXPORT_C void Htcleo::DebugInit()
    {
    iDebugPortBase = 0;
    }

EXPORT_C void Htcleo::DebugOutput(TUint /* aChar */)
    {
    /* Intentionally silent until QSD UART clock and pinmux ownership is safe. */
    }

EXPORT_C TInt Htcleo::MsTickPeriod()
    {
    return KMsTickPeriod;
    }

EXPORT_C TInt Htcleo::SystemTimeInSecondsFrom2000(TInt& aTime)
    {
    aTime = 0;
    return KErrNone;
    }

EXPORT_C TInt Htcleo::SetSystemTimeInSecondsFrom2000(TInt /* aTime */)
    {
    return KErrNone;
    }
