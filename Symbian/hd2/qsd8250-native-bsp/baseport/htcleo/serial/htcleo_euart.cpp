/* Native PIO ECOMM PDD for the QSD8250 UART3 controller. */

#include <d32comm.h>
#include <comm.h>
#include <kernel/kern_priv.h>
#include "htcleo.h"
#include "htcleo_qsd8k.h"

namespace
    {
    _LIT(KPddName, "Comm.HTCLEO");
    const TInt KMinimumLddMajorVersion = 1;
    const TInt KMinimumLddMinorVersion = 1;
    const TInt KMinimumLddBuild = 122;
    const TInt KUartIrq = 11;
    const TInt KPollLimit = 3000000;

    const TUint KMr1 = 0x00u;
    const TUint KMr2 = 0x04u;
    const TUint KCsrSr = 0x08u;
    const TUint KTfRf = 0x0cu;
    const TUint KCrMisr = 0x10u;
    const TUint KImrIsr = 0x14u;
    const TUint KSrTxReady = 1u << 2;
    const TUint KSrRxReady = 1u << 0;
    const TUint KImrTxLevel = 1u << 0;
    const TUint KImrRxLevel = 1u << 4;

    class DDriverHtcleoComm : public DPhysicalDevice
        {
    public:
        DDriverHtcleoComm();
        TInt Install();
        void GetCaps(TDes8& aCaps) const;
        TInt Create(DBase*& aChannel, TInt aUnit, const TDesC8* aInfo,
                    const TVersion& aVersion);
        TInt Validate(TInt aUnit, const TDesC8* aInfo,
                      const TVersion& aVersion);
        };

    class DHtcleoComm : public DComm
        {
    public:
        DHtcleoComm();
        ~DHtcleoComm();
        TInt DoCreate(TInt aUnit);
        TInt Start();
        void Stop(TStopMode aMode);
        void Break(TBool aState);
        void EnableTransmit();
        TUint Signals() const;
        void SetSignals(TUint aSetMask, TUint aClearMask);
        TInt ValidateConfig(const TCommConfigV01& aConfig) const;
        void Configure(TCommConfigV01& aConfig);
        void Caps(TDes8& aCaps) const;
        TInt DisableIrqs();
        void RestoreIrqs(TInt aLevel);
        TDfcQue* DfcQ(TInt aUnit);
        void CheckConfig(TCommConfigV01& aConfig);
        static void Isr(TAny* aPtr);
    private:
        void SetInterruptMask(TUint aMask);
        static TUint BaudCode(TBps aRate);
    private:
        TInt iUnit;
        TInt iInterruptId;
        TUint iInterruptMask;
        TUint iSignals;
        TBool iInInterrupt;
        };

    void FillCaps(TDes8& aCaps)
        {
        TCommCaps2 caps;
        TCommCapsV02& c = caps();
        c.iRate = KCapsBps1200 | KCapsBps2400 | KCapsBps4800 |
            KCapsBps9600 | KCapsBps19200 | KCapsBps38400 |
            KCapsBps57600 | KCapsBps115200;
        c.iDataBits = KCapsData5 | KCapsData6 | KCapsData7 | KCapsData8;
        c.iStopBits = KCapsStop1 | KCapsStop2;
        c.iParity = KCapsParityNone | KCapsParityEven | KCapsParityOdd |
            KCapsParitySpace;
        c.iHandshake = 0;
        c.iSignals = 0;
        c.iSIR = 0;
        c.iNotificationCaps = 0;
        c.iFifo = KCapsHasFifo;
        c.iRoleCaps = 0;
        c.iFlowControlCaps = 0;
        aCaps = caps.Left(Min(caps.Length(), aCaps.MaxLength()));
        }

    DDriverHtcleoComm::DDriverHtcleoComm()
        {
        iUnitsMask = 1;
        iVersion = TVersion(KCommsMajorVersionNumber,
                            KCommsMinorVersionNumber,
                            KCommsBuildVersionNumber);
        }

    TInt DDriverHtcleoComm::Install()
        {
        return SetName(&KPddName);
        }

    void DDriverHtcleoComm::GetCaps(TDes8& aCaps) const
        {
        FillCaps(aCaps);
        }

    TInt DDriverHtcleoComm::Validate(TInt aUnit, const TDesC8*,
                                     const TVersion& aVersion)
        {
        if (aUnit != 0 || !Kern::QueryVersionSupported(iVersion, aVersion) ||
                !Kern::QueryVersionSupported(aVersion,
                    TVersion(KMinimumLddMajorVersion,
                             KMinimumLddMinorVersion,
                             KMinimumLddBuild)))
            return KErrNotSupported;
        return KErrNone;
        }

    TInt DDriverHtcleoComm::Create(DBase*& aChannel, TInt aUnit,
                                   const TDesC8*, const TVersion&)
        {
        DHtcleoComm* channel = new DHtcleoComm;
        if (!channel)
            return KErrNoMemory;
        const TInt r = channel->DoCreate(aUnit);
        if (r != KErrNone)
            {
            delete channel;
            return r;
            }
        aChannel = channel;
        return KErrNone;
        }

    DHtcleoComm::DHtcleoComm()
        : iUnit(0), iInterruptId(-1), iInterruptMask(0), iSignals(0),
          iInInterrupt(EFalse)
        {
        }

    DHtcleoComm::~DHtcleoComm()
        {
        if (iInterruptId >= 0)
            Interrupt::Unbind(iInterruptId);
        }

    TInt DHtcleoComm::DoCreate(TInt aUnit)
        {
        iUnit = aUnit;
        const TInt r = Interrupt::Bind(KUartIrq, Isr, this);
        if (r == KErrNone)
            iInterruptId = KUartIrq;
        return r;
        }

    void DHtcleoComm::SetInterruptMask(TUint aMask)
        {
        iInterruptMask = aMask;
        WriteReg(KHwBaseUart3, KImrIsr, aMask);
        QsdDrainWriteBuffer();
        }

    TInt DHtcleoComm::Start()
        {
        iTransmitting = EFalse;
        iSignals = 0;
        iLdd->UpdateSignals(iSignals);
        SetInterruptMask(KImrRxLevel);
        return Interrupt::Enable(iInterruptId);
        }

    void DHtcleoComm::Stop(TStopMode)
        {
        SetInterruptMask(0u);
        if (iInterruptId >= 0)
            Interrupt::Disable(iInterruptId);
        WriteReg(KHwBaseUart3, KCrMisr, (1u << 3) | (1u << 1));
        QsdDrainWriteBuffer();
        iTransmitting = EFalse;
        }

    void DHtcleoComm::Break(TBool aState)
        {
        WriteReg(KHwBaseUart3, KCrMisr,
                 (aState ? 5u : 6u) << 4);
        QsdDrainWriteBuffer();
        }

    void DHtcleoComm::EnableTransmit()
        {
        const TBool wasTransmitting = static_cast<TBool>(reinterpret_cast<TUint>(
            NKern::SafeSwap(reinterpret_cast<TAny*>(ETrue),
                            reinterpret_cast<TAny*&>(iTransmitting))));
        if (wasTransmitting)
            return;
        TInt value = 0;
        for (;;)
            {
            value = TransmitIsr();
            if (value < 0)
                {
                iTransmitting = EFalse;
                break;
                }
            TInt poll;
            for (poll = 0; poll < KPollLimit; ++poll)
                if (ReadReg(KHwBaseUart3, KCsrSr) & KSrTxReady)
                    break;
            if (poll == KPollLimit)
                {
                iTransmitting = EFalse;
                break;
                }
            WriteReg(KHwBaseUart3, KTfRf, static_cast<TUint>(value));
            }
        TInt irq = 0;
        if (!iInInterrupt)
            {
            NKern::Lock();
            irq = NKern::DisableAllInterrupts();
            }
        CheckTxBuffer();
        if (!iInInterrupt)
            {
            NKern::RestoreInterrupts(irq);
            NKern::Unlock();
            }
        if (value >= 0)
            SetInterruptMask(iInterruptMask | KImrTxLevel);
        }

    TUint DHtcleoComm::Signals() const { return 0; }
    void DHtcleoComm::SetSignals(TUint, TUint) {}
    void DHtcleoComm::CheckConfig(TCommConfigV01&) {}
    void DHtcleoComm::Caps(TDes8& aCaps) const { FillCaps(aCaps); }
    TInt DHtcleoComm::DisableIrqs() { return NKern::DisableInterrupts(1); }
    void DHtcleoComm::RestoreIrqs(TInt aLevel) { NKern::RestoreInterrupts(aLevel); }
    TDfcQue* DHtcleoComm::DfcQ(TInt aUnit)
        { return aUnit == iUnit ? Kern::DfcQue0() : 0; }

    TInt DHtcleoComm::ValidateConfig(const TCommConfigV01& aConfig) const
        {
        if (BaudCode(aConfig.iRate) == 0xffffffffu)
            return KErrNotSupported;
        if (aConfig.iDataBits < EData5 || aConfig.iDataBits > EData8 ||
                aConfig.iStopBits > EStop2 || aConfig.iParity > EParitySpace)
            return KErrNotSupported;
        return KErrNone;
        }

    TUint DHtcleoComm::BaudCode(TBps aRate)
        {
        switch (aRate)
            {
            case EBps1200: return 0x44u;
            case EBps2400: return 0x55u;
            case EBps4800: return 0x77u;
            case EBps9600: return 0x99u;
            case EBps19200: return 0xbbu;
            case EBps38400: return 0xddu;
            case EBps57600: return 0xeeu;
            case EBps115200: return 0xffu;
            default: return 0xffffffffu;
            }
        }

    void DHtcleoComm::Configure(TCommConfigV01& aConfig)
        {
        /* Linux configures UART3_CLK (id 33) at 7.3728 MHz.  Use the shared
         * QSD8K clock wrapper so the ProcComm opcodes stay identical to the
         * HTC Linux enum (SET_RATE=24, ENABLE=20) and remain bounded. */
        (void)HtcleoClockSetRate(33u, 7372800u);
        (void)HtcleoClockEnable(33u, ETrue);

        SetInterruptMask(0u);
        WriteReg(KHwBaseUart3, KCrMisr, 1u << 4);
        WriteReg(KHwBaseUart3, KCrMisr, 2u << 4);
        WriteReg(KHwBaseUart3, KCrMisr, 3u << 4);
        WriteReg(KHwBaseUart3, KMr1, 0u);
        TUint mr2 = (static_cast<TUint>(aConfig.iDataBits) << 4);
        mr2 |= (aConfig.iStopBits == EStop2) ? (3u << 2) : (1u << 2);
        switch (aConfig.iParity)
            {
            case EParityOdd: mr2 |= 1u; break;
            case EParityEven: mr2 |= 2u; break;
            case EParitySpace: mr2 |= 3u; break;
            default: break;
            }
        WriteReg(KHwBaseUart3, KMr2, mr2);
        WriteReg(KHwBaseUart3, KCsrSr, BaudCode(aConfig.iRate));
        WriteReg(KHwBaseUart3, KCrMisr, (1u << 2) | 1u);
        QsdDrainWriteBuffer();
        }

    void DHtcleoComm::Isr(TAny* aPtr)
        {
        DHtcleoComm& self = *static_cast<DHtcleoComm*>(aPtr);
        self.iInInterrupt = ETrue;
        const TUint status = ReadReg(KHwBaseUart3, KCsrSr);
        if (status & KSrRxReady)
            {
            TUint received[64];
            TInt count = 0;
            TInt xonState = 0;
            while (count < 64 && (ReadReg(KHwBaseUart3, KCsrSr) & KSrRxReady))
                {
                const TUint ch = ReadReg(KHwBaseUart3, KTfRf) & 0xffu;
                if (ch == self.iLdd->iRxXonChar) xonState = 1;
                else if (ch == self.iLdd->iRxXoffChar) xonState = -1;
                else received[count++] = ch;
                }
            self.ReceiveIsr(received, count, xonState);
            }
        if ((status & KSrTxReady) && self.iTransmitting)
            self.EnableTransmit();
        self.iInInterrupt = EFalse;
        Interrupt::Clear(self.iInterruptId);
        }
    }

DECLARE_STANDARD_PDD()
    {
    return new DDriverHtcleoComm;
    }
