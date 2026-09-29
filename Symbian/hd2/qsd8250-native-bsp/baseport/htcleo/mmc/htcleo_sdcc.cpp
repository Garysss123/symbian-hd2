/*
 * HTC Leo / QSD8250 SDCC2 platform layer for the EKA2 SD stack.
 *
 * The generic Symbian SD protocol and MEDMMC layers remain unmodified.  This
 * file owns only the HTC Leo GPIO/power/clock bridge and bounded PIO command
 * transport.  No DMA or NAND registers are used.
 */

#include <kernel/kern_priv.h>
#include <drivers/mmccd_ifc.h>
#include <drivers/sdcard.h>
#include <variantmediadef.h>
#include "htcleo_sdcc_regs.h"

namespace
    {
    // Last completed SDCC transport operation, exposed read-only through the
    // platform-specific HAL for the single ESTART screen probe.  Encoding is
    // DCCRSSSS: CC=command, R=transport result class, SSSS=raw STATUS[15:0].
    volatile TUint32 gHtcleoSdccDiagnostic = 0xdfe00000u;
    // Last pre-command power-up result.  D9SSRRRR encodes the power-up stage
    // (SS) and the absolute Symbian error (RRRR).  This remains separate from
    // command transport so cleanup/power-down cannot erase the first failure.
    volatile TUint32 gHtcleoSdccPowerUpDiagnostic = 0xd9ff0000u;
    volatile TInt gHtcleoSdccLastPowerResult = KErrNotReady;
    volatile TUint32 gHtcleoSdccIssueCount = 0u;
    const TUint32 KProcAppCommand = 0x00u;
    const TUint32 KProcAppStatus  = 0x04u;
    const TUint32 KProcAppData1   = 0x08u;
    const TUint32 KProcAppData2   = 0x0cu;
    const TUint32 KProcMdmStatus  = 0x14u;
    const TUint32 KProcReady      = 1u;
    const TUint32 KProcDone       = 1u;
    const TUint32 KProcSuccess    = 3u;
    const TUint32 KProcGpioConfig = 37u;
    // HTC Leo's WinCE-derived modem firmware does not accept the generic
    // CLKCTL RPC used by later Qualcomm boards.  The proven Leo Linux BSP
    // uses the secondary clock-regime commands and firmware clock IDs.
    const TUint32 KProcClockRegimeEnable = 50u;
    const TUint32 KProcClockRegimeSelectSpeed = 58u;
    const TUint32 KProcVregSwitch = 30u;
    const TUint32 KProcVregSetLevel = 31u;
    const TUint32 KProcLeoSdcc2Clock = 67u;
    const TUint32 KProcLeoSdcc2PClock = 16u;
    const TUint32 KProcGp6 = 23u;
    const TUint32 KClockGlobalEnable = 0x000u;
    const TUint32 KClockGlobalSdcc2Gate = 1u << 8;

    // OCR bit 16 is the standard 2.8-2.9 V window.  GP6 is programmed to
    // 2850 mV below, so advertising the old 3.2-3.4 V mask (bits 20/21)
    // made the generic SD stack negotiate a range the socket does not supply.
    const TUint32 KHtcleoSdOcr2850 = 0x00010000u;

    const TUint32 KCmdResponse = 1u << 6;
    const TUint32 KCmdLongResponse = 1u << 7;
    const TUint32 KCmdEnable = 1u << 10;
    const TUint32 KCmdProgramEnable = 1u << 11;
    const TUint32 KCmdData = 1u << 12;
    const TUint32 KDataEnable = 1u;
    const TUint32 KDataRead = 1u << 1;
    const TUint32 KDataReadPending = 1u << 20;
    const TUint32 KClockEnable = 1u << 8;
    const TUint32 KClockWideBus = 1u << 11;
    const TUint32 KClockFlowEnable = 1u << 12;
    const TUint32 KClockFeedback = 1u << 15;
    const TUint32 KAllClear = 0x07ffffffu;
    const TUint32 KCommandTerminal = (1u << 0) | (1u << 2) |
                                     (1u << 6) | (1u << 7);
    const TUint32 KDataErrors = (1u << 1) | (1u << 3) |
                                (1u << 4) | (1u << 5);
    const TUint32 KDataEnd = 1u << 8;
    const TUint32 KRxAvailable = 1u << 21;
    const TUint32 KTxHalfEmpty = 1u << 14;
    const TUint32 KProgramDone = 1u << 23;
    const TInt KPollLimit = 3000000;
    const TInt KBufferBytes = 256 * 1024;

    inline volatile TUint32& ProcReg(TUint32 aOffset)
        {
        return *reinterpret_cast<volatile TUint32*>(
            HtcleoSdcc::KSharedRamLinearBase + aOffset);
        }

    inline void Barrier()
        {
        TUint32 zero = 0;
        __asm__ __volatile__("mcr p15, 0, %0, c7, c10, 4" : : "r"(zero) : "memory");
        }

    inline void ControllerWriteDelay()
        {
        // The QSD8x50 Linux SDCC driver waits at least two to three MCLK
        // cycles after core-register writes.  At the 144 kHz identification
        // clock, 50 us is safely beyond that requirement.
        Barrier();
        Kern::NanoWait(50000u);
        }

    __attribute__((noinline)) TMMCErr RecordCommandResult(
                                TUint32 aCommand, TUint32 aArgument,
                                TUint32 aReason, TUint32 aStatus,
                                TMMCErr aResult)
        {
        gHtcleoSdccDiagnostic = 0xd0000000u |
            ((aCommand & 0x3fu) << 20) |
            ((aReason & 0x0fu) << 16) |
            (aStatus & 0xffffu);
        Barrier();
        return aResult;
        }

    void RecordPowerUpResult(TUint32 aStage, TInt aResult)
        {
        const TUint32 magnitude = static_cast<TUint32>(
            aResult < 0 ? -aResult : aResult) & 0xffffu;
        gHtcleoSdccPowerUpDiagnostic = 0xd9000000u |
            ((aStage & 0xffu) << 16) | magnitude;
        Barrier();
        }

    // Iteration 431 permanently retires the framebuffer progress renderer.
    // Function 0/1 remain read-only SD diagnostics; function 2 is deliberately
    // unsupported so unrelated post-WServ HAL traffic can never repaint the
    // display or masquerade as a boot checkpoint.
    TInt DiagnosticHal(TAny*, TInt aFunction, TAny*, TAny*)
        {
        if (aFunction == 0)
            return static_cast<TInt>(gHtcleoSdccDiagnostic != 0xdfe00000u
                ? gHtcleoSdccDiagnostic : gHtcleoSdccPowerUpDiagnostic);
        if (aFunction == 1)
            {
            DPBusSocket* socket = DPBusSocket::SocketFromId(0);
            if (!socket)
                return static_cast<TInt>(0xd8f00000u);
            const TUint32 socketState = static_cast<TUint32>(socket->State()) & 0xfu;
            const TUint32 cardPresent = socket->CardIsPresent() ? 1u : 0u;
            const TUint32 mediaState = static_cast<TUint32>(socket->MediaState()) & 0xfu;
            const TUint32 psuState = socket->iVcc
                ? (static_cast<TUint32>(socket->iVcc->iState) & 0xfu) : 0xfu;
            return static_cast<TInt>(0xd8000000u | (socketState << 20) |
                (cardPresent << 16) | (mediaState << 12) | (psuState << 8));
            }
        return KErrNotSupported;
        }

    TInt ProcComm(TUint32 aCommand, TUint32& aData1, TUint32& aData2)
        {
        TInt count;
        for (count = 0; count < KPollLimit; ++count)
            {
            if (ProcReg(KProcMdmStatus) == KProcReady)
                break;
            }
        if (count == KPollLimit)
            return KErrTimedOut;

        ProcReg(KProcAppCommand) = aCommand;
        ProcReg(KProcAppData1) = aData1;
        ProcReg(KProcAppData2) = aData2;
        Barrier();
        *reinterpret_cast<volatile TUint32*>(
            HtcleoSdcc::KCsrLinearBase + 0x418u) = 1u;
        Barrier();

        for (count = 0; count < KPollLimit; ++count)
            {
            if (ProcReg(KProcAppCommand) == KProcDone)
                break;
            }
        if (count == KPollLimit)
            return KErrTimedOut;
        if (ProcReg(KProcAppStatus) != KProcSuccess)
            return KErrGeneral;
        aData1 = ProcReg(KProcAppData1);
        aData2 = ProcReg(KProcAppData2);
        ProcReg(KProcAppCommand) = 0u;
        Barrier();
        return KErrNone;
        }

    TUint32 GpioConfig(TUint32 aGpio, TUint32 aFunction,
                       TUint32 aDrive, TBool aPullUp)
        {
        const TUint32 output = 1u;
        const TUint32 pull = aPullUp ? 3u : 0u;
        return ((aGpio & 0x3ffu) << 4) | (aFunction & 0xfu) |
               (output << 14) |
               (pull << 15) | ((aDrive & 0xfu) << 17);
        }

    TInt ConfigurePins(TBool aOn)
        {
        const TUint32 onConfigs[] =
            {
            GpioConfig(62u, 1u, 3u, EFalse),
            GpioConfig(63u, 1u, 3u, ETrue),
            GpioConfig(64u, 1u, 1u, ETrue),
            GpioConfig(65u, 1u, 1u, ETrue),
            GpioConfig(66u, 1u, 1u, ETrue),
            GpioConfig(67u, 1u, 1u, ETrue)
            };
        const TUint32 offConfigs[] =
            {
            GpioConfig(62u, 0u, 1u, EFalse),
            GpioConfig(63u, 0u, 1u, EFalse),
            GpioConfig(64u, 0u, 1u, EFalse),
            GpioConfig(65u, 0u, 1u, EFalse),
            GpioConfig(66u, 0u, 1u, EFalse),
            GpioConfig(67u, 0u, 1u, EFalse)
            };
        const TUint32* configs = aOn ? onConfigs : offConfigs;
        for (TInt i = 0; i < 6; ++i)
            {
            TUint32 data1 = configs[i];
            TUint32 data2 = 0u;
            TInt r = ProcComm(KProcGpioConfig, data1, data2);
            if (r != KErrNone)
                return r;
            }
        return KErrNone;
        }

    TInt SetPower(TBool aOn)
        {
        TUint32 data1 = KProcGp6;
        TUint32 data2 = aOn ? 1u : 0u;
        if (!aOn)
            {
            (void)ConfigurePins(EFalse);
            return ProcComm(KProcVregSwitch, data1, data2);
            }

        // Match the proven HTC Leo board sequence: enable GP6, mux the
        // SDCC2 pins, then select the card voltage.
        TInt r = ProcComm(KProcVregSwitch, data1, data2);
        if (r != KErrNone)
            return r;
        r = ConfigurePins(ETrue);
        if (r != KErrNone)
            return r;
        data1 = KProcGp6;
        data2 = 2850u;
        return ProcComm(KProcVregSetLevel, data1, data2);
        }

    TUint32 HtcleoClockSpeed(TUint32 aRate)
        {
        if (aRate > 50000000u) return 14u;
        if (aRate > 49152000u) return 13u;
        if (aRate > 45000000u) return 12u;
        if (aRate > 40000000u) return 11u;
        if (aRate > 35000000u) return 10u;
        if (aRate > 30000000u) return 9u;
        if (aRate > 25000000u) return 8u;
        if (aRate > 20000000u) return 7u;
        if (aRate > 15000000u) return 6u;
        if (aRate > 10000000u) return 5u;
        if (aRate > 5000000u) return 4u;
        if (aRate > 400000u) return 3u;
        if (aRate > 144000u) return 2u;
        return 1u;
        }

    TInt SetClockRate(TUint32 aRate)
        {
        TUint32 data1 = KProcLeoSdcc2PClock;
        TUint32 data2 = 0u;
        TInt r = ProcComm(KProcClockRegimeEnable, data1, data2);
        if (r != KErrNone)
            return r;
        data1 = KProcLeoSdcc2Clock;
        data2 = HtcleoClockSpeed(aRate);
        r = ProcComm(KProcClockRegimeSelectSpeed, data1, data2);
        if (r != KErrNone)
            return r;
        data1 = KProcLeoSdcc2Clock;
        data2 = 0u;
        r = ProcComm(KProcClockRegimeEnable, data1, data2);
        if (r != KErrNone)
            return r;

        // Leo's firmware RPC leaves the QSD global SDC2 gate clear on this
        // boot path. Preserve the other gates and latch only SDC2 bit 8, as
        // established by the earlier read-only state-03 diagnostic.
        volatile TUint32& global =
            HtcleoSdcc::ClockRegister(KClockGlobalEnable);
        global = global | KClockGlobalSdcc2Gate;
        Barrier();
        return (global & KClockGlobalSdcc2Gate) ? KErrNone : KErrGeneral;
        }

    inline void PutBigEndian(TUint8* aTarget, TUint32 aValue)
        {
        aTarget[0] = static_cast<TUint8>(aValue >> 24);
        aTarget[1] = static_cast<TUint8>(aValue >> 16);
        aTarget[2] = static_cast<TUint8>(aValue >> 8);
        aTarget[3] = static_cast<TUint8>(aValue);
        }
    }

class DHtcleoSdStack : public DSDStack
    {
public:
    DHtcleoSdStack(TInt aBus, DMMCSocket* aSocket)
        : DSDStack(aBus, aSocket), iBuffer(0), iBufferLength(0),
          iCurrentClock(0), iClockBusWidth(0),
          iAddressedCard(KBroadcastToAllCards) {}
    TInt Init();
    virtual TInt ProgramPeriodInMilliSeconds() const { return 1; }
    virtual void AdjustPartialRead(const TMMCard*, TUint32 aStart,
        TUint32 aEnd, TUint32* aPhysStart, TUint32* aPhysEnd) const;
    virtual void GetBufferInfo(TUint8** aBuffer, TInt* aLength);
    virtual void MachineInfo(TMMCMachineInfo& aInfo);
    virtual void AddressCard(TInt aCard) { iAddressedCard = aCard; }
private:
    virtual void SetBusConfigDefaults(TMMCBusConfig& aConfig, TUint aClock);
    virtual void SetBusWidth(TUint32 aBusWidth);
    virtual void InitClockOff();
    void ResetController1024();
    virtual void ASSPReset();
    virtual void ASSPDisengage();
    virtual void DoPowerDown();
    virtual TMMCErr DoPowerUpSM();
    virtual TMMCErr InitClockOnSM();
    virtual TMMCErr IssueMMCCommandSM();
    TMMCErr TransferData(TMMCCommandDesc& aCommand);
    TMMCErr ApplyClock();
private:
    TUint8* iBuffer;
    TInt iBufferLength;
    TUint32 iCurrentClock;
    TUint32 iClockBusWidth;
    TInt iAddressedCard;
    };

TInt DHtcleoSdStack::Init()
    {
    iCardArray = new TSDCardArray(this);
    if (!iCardArray)
        return KErrNoMemory;
    TInt r = DMMCStack::Init();
    if (r != KErrNone)
        return r;
    iBuffer = static_cast<TUint8*>(Kern::Alloc(KBufferBytes));
    if (!iBuffer)
        return KErrNoMemory;
    iBufferLength = KBufferBytes;
    return KErrNone;
    }

void DHtcleoSdStack::AdjustPartialRead(const TMMCard*, TUint32 aStart,
    TUint32 aEnd, TUint32* aPhysStart, TUint32* aPhysEnd) const
    {
    *aPhysStart = aStart & ~3u;
    *aPhysEnd = (aEnd + 3u) & ~3u;
    }

void DHtcleoSdStack::GetBufferInfo(TUint8** aBuffer, TInt* aLength)
    {
    *aBuffer = iBuffer;
    *aLength = iBufferLength;
    }

void DHtcleoSdStack::MachineInfo(TMMCMachineInfo& aInfo)
    {
    aInfo.iTotalSockets = 1;
    aInfo.iTotalMediaChanges = 0;
    aInfo.iTotalPrimarySupplies = 0;
    aInfo.iFlags = TMMCMachineInfo::ESupportsR7 |
                   TMMCMachineInfo::EMaxTransferLength_256K;
    aInfo.iBaseBusNumber = 0;
    }

void DHtcleoSdStack::SetBusConfigDefaults(TMMCBusConfig& aConfig, TUint aClock)
    {
    aConfig.iBusClock = aClock < 25000u ? aClock : 25000u;
    aConfig.iResponseTimeOut = 100000u;
    aConfig.iDataTimeOut = 500000u;
    aConfig.iBusyTimeOut = 1000000u;
    }

void DHtcleoSdStack::SetBusWidth(TUint32 aBusWidth)
    {
    iClockBusWidth = (aBusWidth == EBusWidth4) ? KClockWideBus : 0u;
    HtcleoSdcc::Register(HtcleoSdcc::EClock) =
        KClockEnable | KClockFlowEnable | KClockFeedback | iClockBusWidth;
    ControllerWriteDelay();
    }

TMMCErr DHtcleoSdStack::ApplyClock()
    {
    TUint32 rate = BusConfig().iBusClock * 1000u;
    if (rate < 144000u)
        rate = 144000u;
    if (rate > 25000000u)
        rate = 25000000u;
    if (rate != iCurrentClock)
        {
        if (SetClockRate(rate) != KErrNone)
            return KMMCErrHardware;
        iCurrentClock = rate;
        }
    HtcleoSdcc::Register(HtcleoSdcc::EClock) =
        KClockEnable | KClockFlowEnable | KClockFeedback | iClockBusWidth;
    ControllerWriteDelay();
    return KMMCErrNone;
    }

void DHtcleoSdStack::InitClockOff()
    {
    HtcleoSdcc::Register(HtcleoSdcc::EClock) = 0u;
    ControllerWriteDelay();
    }

void DHtcleoSdStack::ResetController1024()
    {
    HtcleoSdcc::Register(HtcleoSdcc::EMask0) = 0u;
    HtcleoSdcc::Register(HtcleoSdcc::EDataControl) = 0u;
    ControllerWriteDelay();
    HtcleoSdcc::Register(HtcleoSdcc::ECommand) = 0u;
    ControllerWriteDelay();
    HtcleoSdcc::Register(HtcleoSdcc::EClear) = KAllClear;
    ControllerWriteDelay();
    }

void DHtcleoSdStack::ASSPReset()
    {
    // PIL session-abort contract: preserve the active-session notification.
    ResetController1024();
    ReportASSPDisengaged();
    }

void DHtcleoSdStack::ASSPDisengage()
    {
    HtcleoSdcc::Register(HtcleoSdcc::EMask0) = 0u;
    Barrier();
    // DMMCStack::SchedDisengage() detaches iSessionP before invoking this
    // hook, then clears the removed session's state immediately after the
    // hook returns.  ReportASSPDisengaged() operates on iSessionP, so calling
    // it here dereferences NULL on the completion path.  The generic stack
    // already owns the corresponding KMMCSessStateASSPEngaged cleanup.
    }

void DHtcleoSdStack::DoPowerDown()
    {
    // Whole-controller shutdown has no guaranteed current session. Do not
    // reuse ASSPReset(), whose completion report dereferences iSessionP.
    ResetController1024();
    HtcleoSdcc::Register(HtcleoSdcc::EPower) = 0u;
    HtcleoSdcc::Register(HtcleoSdcc::EClock) = 0u;
    Barrier();
    (void)SetPower(EFalse);
    iCurrentClock = 0u;
    ReportPowerDown();
    }

TMMCErr DHtcleoSdStack::DoPowerUpSM()
    {
    // This function is invoked as a child through SMF_INVOKES. Successful
    // completion must use SMF_END so Machine().Pop() returns control to the
    // parent CIMUpdateAcqSM state frame.
    enum states
        {
        EStBegin = 0,
        EStEnd
        };
    SMF_BEGIN

    RecordPowerUpResult(1u, KErrNone);
    TInt r = MMCSocket()->iVcc->SetState(EPsuOnCurLimit);
    RecordPowerUpResult(1u, r);
    if (r != KErrNone)
        return KMMCErrHardware;
    RecordPowerUpResult(2u, gHtcleoSdccLastPowerResult);
    if (gHtcleoSdccLastPowerResult != KErrNone)
        return KMMCErrHardware;
    r = ConfigurePins(ETrue);
    RecordPowerUpResult(3u, r);
    if (r != KErrNone)
        return KMMCErrHardware;
    r = SetClockRate(144000u);
    RecordPowerUpResult(4u, r);
    if (r != KErrNone)
        return KMMCErrHardware;
    iCurrentClock = 144000u;
    HtcleoSdcc::Register(HtcleoSdcc::EMask0) = 0u;
    HtcleoSdcc::Register(HtcleoSdcc::EClear) = KAllClear;
    HtcleoSdcc::Register(HtcleoSdcc::EClock) =
        KClockEnable | KClockFlowEnable | KClockFeedback | iClockBusWidth;
    ControllerWriteDelay();
    HtcleoSdcc::Register(HtcleoSdcc::EPower) = 2u;
    Barrier();
    Kern::NanoWait(1000000u);
    HtcleoSdcc::Register(HtcleoSdcc::EPower) = 3u;
    Barrier();
    Kern::NanoWait(1000000u);
    ReportPowerUp();
    RecordPowerUpResult(0xfeu, KErrNone);

    SMF_END
    }

TMMCErr DHtcleoSdStack::InitClockOnSM()
    {
    // Like DoPowerUpSM, this is an SMF_INVOKES child. A successful direct
    // return would strand the parent's state frame instead of popping it.
    enum states
        {
        EStBegin = 0,
        EStEnd
        };
    SMF_BEGIN

    ReportASSPEngaged();
    const TMMCErr r = ApplyClock();
    if (r != KMMCErrNone)
        return r;

    SMF_END
    }

TMMCErr DHtcleoSdStack::TransferData(TMMCCommandDesc& aCommand)
    {
    TUint32 remaining = aCommand.iTotalLength;
    TUint8* memory = aCommand.iDataMemoryP;
    TInt polls = 0;
    while (remaining && polls++ < KPollLimit)
        {
        const TUint32 status = HtcleoSdcc::Register(HtcleoSdcc::EStatus);
        if (status & KDataErrors)
            return (status & (1u << 3)) ? KMMCErrDataTimeOut : KMMCErrDataCRC;
        if (aCommand.iSpec.iDirection == EDirRead && (status & KRxAvailable))
            {
            const TUint32 value = *reinterpret_cast<volatile TUint32*>(
                HtcleoSdcc::KSdcc2LinearBase + HtcleoSdcc::EFifo);
            const TUint32 count = remaining < 4u ? remaining : 4u;
            for (TUint32 i = 0; i < count; ++i)
                memory[i] = static_cast<TUint8>(value >> (i * 8));
            memory += count;
            remaining -= count;
            }
        else if (aCommand.iSpec.iDirection == EDirWrite && (status & KTxHalfEmpty))
            {
            TUint32 value = 0u;
            const TUint32 count = remaining < 4u ? remaining : 4u;
            for (TUint32 i = 0; i < count; ++i)
                value |= static_cast<TUint32>(memory[i]) << (i * 8);
            *reinterpret_cast<volatile TUint32*>(
                HtcleoSdcc::KSdcc2LinearBase + HtcleoSdcc::EFifo) = value;
            memory += count;
            remaining -= count;
            }
        }
    if (remaining)
        return KMMCErrDataTimeOut;
    for (polls = 0; polls < KPollLimit; ++polls)
        {
        const TUint32 status = HtcleoSdcc::Register(HtcleoSdcc::EStatus);
        if (status & KDataErrors)
            return (status & (1u << 3)) ? KMMCErrDataTimeOut : KMMCErrDataCRC;
        if (status & KDataEnd)
            return KMMCErrNone;
        }
    return KMMCErrDataTimeOut;
    }

TMMCErr DHtcleoSdStack::IssueMMCCommandSM()
    {
    enum states
        {
        EStBegin = 0,
        EStEnd
        };
    TMMCCommandDesc& command = Command();
    ++gHtcleoSdccIssueCount;

    SMF_BEGIN

    ReportASSPEngaged();
    TMMCErr r = ApplyClock();
    if (r != KMMCErrNone)
        SMF_RETURN(RecordCommandResult(command.iCommand, command.iArgument,
                                       1u, 0u, r))

    HtcleoSdcc::Register(HtcleoSdcc::ECommand) = 0u;
    ControllerWriteDelay();
    HtcleoSdcc::Register(HtcleoSdcc::EDataControl) = 0u;
    ControllerWriteDelay();
    HtcleoSdcc::Register(HtcleoSdcc::EClear) = KAllClear;
    ControllerWriteDelay();

    const TBool hasData = command.iSpec.iDirection == EDirRead ||
                          command.iSpec.iDirection == EDirWrite;
    if (hasData)
        {
        const TUint32 blockLength = command.BlockLength();
        if (!blockLength || blockLength > 4096u)
            SMF_RETURN(RecordCommandResult(command.iCommand, command.iArgument,
                                           2u, 0u,
                                           KMMCErrNotSupported))
        HtcleoSdcc::Register(HtcleoSdcc::EDataTimer) = 0xffffffffu;
        HtcleoSdcc::Register(HtcleoSdcc::EDataLength) = command.iTotalLength;
        // Qualcomm's MSM7x00/QSD8x50 SDCC encodes the actual byte count in
        // DATACTRL[15:4], unlike the logarithmic PL180 encoding.
        TUint32 control = (blockLength << 4) | KDataEnable;
        if (command.iSpec.iDirection == EDirRead)
            control |= KDataRead | KDataReadPending;
        HtcleoSdcc::Register(HtcleoSdcc::EDataControl) = control;
        }

    TUint32 encoded = static_cast<TUint32>(command.iCommand) | KCmdEnable;
    if (command.iSpec.iResponseType != ERespTypeNone)
        encoded |= KCmdResponse;
    if (command.iSpec.iResponseType == ERespTypeR2)
        encoded |= KCmdLongResponse;
    const TBool hasBusyResponse =
        command.iSpec.iResponseType == ERespTypeR1B;
    if (hasBusyResponse)
        encoded |= KCmdProgramEnable;
    if (hasData)
        encoded |= KCmdData;
    HtcleoSdcc::Register(HtcleoSdcc::EArgument) = command.iArgument;
    Barrier();
    HtcleoSdcc::Register(HtcleoSdcc::ECommand) = encoded;
    Barrier();

    TUint32 status = 0u;
    TInt polls;
    for (polls = 0; polls < KPollLimit; ++polls)
        {
        status = HtcleoSdcc::Register(HtcleoSdcc::EStatus);
        if (status & KCommandTerminal)
            break;
        }
    if (polls == KPollLimit)
        SMF_RETURN(RecordCommandResult(command.iCommand, command.iArgument,
                                       3u, status,
                                       KMMCErrResponseTimeOut))
    if (status & (1u << 2))
        {
        // CMD7 with RCA zero is the generic stack's deliberate de-select-all
        // operation. It expects no response and clears this timeout itself.
        const TUint32 reason =
            command.iCommand == 7u && TUint32(command.iArgument) == 0u
                ? 0x0eu : 4u;
        SMF_RETURN(RecordCommandResult(command.iCommand, command.iArgument,
                                       reason, status,
                                       KMMCErrResponseTimeOut))
        }
    if ((status & (1u << 0)) && command.iSpec.iResponseType != ERespTypeR3)
        SMF_RETURN(RecordCommandResult(command.iCommand, command.iArgument,
                                       5u, status,
                                       KMMCErrResponseCRC))

    if (command.iSpec.iResponseType == ERespTypeR2)
        {
        PutBigEndian(command.iResponse + 0, *reinterpret_cast<volatile TUint32*>(HtcleoSdcc::KSdcc2LinearBase + 0x14u));
        PutBigEndian(command.iResponse + 4, *reinterpret_cast<volatile TUint32*>(HtcleoSdcc::KSdcc2LinearBase + 0x18u));
        PutBigEndian(command.iResponse + 8, *reinterpret_cast<volatile TUint32*>(HtcleoSdcc::KSdcc2LinearBase + 0x1cu));
        PutBigEndian(command.iResponse + 12, *reinterpret_cast<volatile TUint32*>(HtcleoSdcc::KSdcc2LinearBase + 0x20u));
        }
    else if (command.iSpec.iResponseType != ERespTypeNone)
        PutBigEndian(command.iResponse,
            HtcleoSdcc::Register(HtcleoSdcc::EResponse0));

    if (hasBusyResponse)
        {
        for (polls = 0; polls < KPollLimit; ++polls)
            {
            status = HtcleoSdcc::Register(HtcleoSdcc::EStatus);
            if (status & KProgramDone)
                break;
            }
        if (polls == KPollLimit)
            SMF_RETURN(RecordCommandResult(command.iCommand, command.iArgument,
                                           9u, status,
                                           KMMCErrBusyTimeOut))
        }

    if (hasData)
        {
        r = TransferData(command);
        status = HtcleoSdcc::Register(HtcleoSdcc::EStatus);
        TUint32 reason = 8u;
        if (r == KMMCErrNone)
            reason = 0u;
        else if (r == KMMCErrDataTimeOut)
            reason = 6u;
        else if (r == KMMCErrDataCRC)
            reason = 7u;
        r = RecordCommandResult(command.iCommand, command.iArgument,
                                reason, status, r);
        if (r != KMMCErrNone)
            SMF_RETURN(r)
        }
    else
        (void)RecordCommandResult(command.iCommand, command.iArgument,
                                  0u, status, KMMCErrNone);

    SMF_END
    }

class DHtcleoSdPsu : public DMMCPsu
    {
public:
    DHtcleoSdPsu(TInt aPsu, TInt aMediaChange) : DMMCPsu(aPsu, aMediaChange) {}
    virtual void DoSetState(TPBusPsuState aState)
        { gHtcleoSdccLastPowerResult = SetPower(aState != EPsuOff); }
    virtual void DoCheckVoltage() { ReceiveVoltageCheckResult(KErrNone); }
    virtual void PsuInfo(TPBusPsuInfo& aInfo)
        {
        aInfo.iVoltageSupported = KHtcleoSdOcr2850;
        aInfo.iMaxCurrentInMicroAmps = 0;
        aInfo.iVoltCheckInterval = 0;
        aInfo.iVoltCheckMethod = EPsuChkComparator;
        aInfo.iNotLockedTimeOut = 0;
        aInfo.iInactivityTimeOut = 0;
        }
    };

class THtcleoSdController : public TMMCardControllerInterface
    {
public:
    virtual DMMCSocket* NewSocket(TInt aNumber, TMMCPasswordStore* aStore)
        { return new DMMCSocket(aNumber, aStore); }
    virtual DMMCStack* NewStack(TInt aNumber, DMMCSocket* aSocket)
        { return new DHtcleoSdStack(aNumber, aSocket); }
    virtual DMMCMediaChange* NewMediaChange(TInt aNumber)
        { return new DMMCEmbeddedMediaChange(aNumber); }
    virtual DMMCPsu* NewVcc(TInt aNumber, TInt aMediaChange)
        { return new DHtcleoSdPsu(aNumber, aMediaChange); }
    virtual TInt Init() { return KErrNone; }
    virtual TInt MediaChangeID(TInt) { return 0; }
    virtual TInt VccID(TInt) { return 0; }
    virtual TBool IsMMCSocket(TInt aSocket, SMediaDeviceInfo& aInfo);
    };

static const TInt KDriveNumbers[MMC0_DRIVECOUNT] = { MMC0_DRIVELIST };
_LIT(KSdSocketName, MMC0_DRIVENAME);

TBool THtcleoSdController::IsMMCSocket(TInt aSocket, SMediaDeviceInfo& aInfo)
    {
    if (aSocket != 0)
        return EFalse;
    aInfo.iDevice = MEDIA_DEVICE_MMC;
    aInfo.iDriveCount = MMC0_DRIVECOUNT;
    aInfo.iDriveList = KDriveNumbers;
    aInfo.iNumMedia = MMC0_NUMMEDIA;
    aInfo.iDeviceName = &KSdSocketName;
    return ETrue;
    }

DECLARE_STANDARD_EXTENSION()
    {
    TInt r = Kern::AddHalEntry(EHalGroupPlatformSpecific1, DiagnosticHal, 0);
    if (r != KErrNone)
        return r;
    THtcleoSdController* controller = new THtcleoSdController;
    if (!controller)
        return KErrNoMemory;
    r = controller->Create();
    if (r == KErrNone)
        {
        // The ROM itself was loaded from this SD slot.  Until the board package
        // gains a real card-detect GPIO contract, do not let the generic socket
        // remain in CardAbsent and reject every request before power-up.
        DPBusSocket* socket = DPBusSocket::SocketFromId(0);
        if (socket && socket->iState == EPBusCardAbsent)
            socket->iState = EPBusOff;
        }
    return r;
    }
