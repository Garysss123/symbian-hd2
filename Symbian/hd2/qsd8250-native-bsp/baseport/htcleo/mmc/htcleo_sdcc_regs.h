/*
 * HTC Leo / QSD8250 SDCC2 hardware contract.
 *
 * This is an original clean-room description of numeric hardware facts.  The
 * values were cross-checked against the archived HTC Leo platform sources and
 * the project's earlier read-only SDCC diagnostics.  No Linux implementation
 * code is copied or linked into the Symbian build.
 */

#ifndef HTCLEO_SDCC_REGS_H
#define HTCLEO_SDCC_REGS_H

#include <e32def.h>

namespace HtcleoSdcc
    {
    const TUint32 KSdcc2PhysicalBase = 0xA0400000u;
    const TUint32 KSdcc2LinearBase   = 0xC6500000u;
    const TUint32 KClockPhysicalBase = 0xA8600000u;
    const TUint32 KClockLinearBase   = 0xC6700000u;
    const TUint32 KSharedRamPhysicalBase = 0x00100000u;
    const TUint32 KSharedRamLinearBase   = 0xC6600000u;
    const TUint32 KCsrLinearBase         = 0xC6100000u;

    enum TRegister
        {
        EPower       = 0x000,
        EClock       = 0x004,
        EArgument    = 0x008,
        ECommand     = 0x00C,
        ERespCommand = 0x010,
        EResponse0   = 0x014,
        EDataTimer   = 0x024,
        EDataLength  = 0x028,
        EDataControl = 0x02C,
        EDataCount   = 0x030,
        EStatus      = 0x034,
        EClear       = 0x038,
        EMask0       = 0x03C,
        EFifo        = 0x080
        };

    const TUint32 KSectorBytes = 512u;
    const TUint32 KFifoBytes   = 64u;

    const TUint32 KStatusCommandCrcFail = 1u << 0;
    const TUint32 KStatusDataCrcFail    = 1u << 1;
    const TUint32 KStatusCommandTimeout = 1u << 2;
    const TUint32 KStatusDataTimeout    = 1u << 3;
    const TUint32 KStatusTxUnderrun     = 1u << 4;
    const TUint32 KStatusRxOverrun      = 1u << 5;
    const TUint32 KStatusCommandEnd     = 1u << 6;
    const TUint32 KStatusDataEnd        = 1u << 8;
    const TUint32 KStatusTxHalfEmpty    = 1u << 14;
    const TUint32 KStatusTxEmpty        = 1u << 18;
    const TUint32 KStatusRxAvailable    = 1u << 21;

    enum TCardCommand
        {
        ECmdGoIdle          = 0,
        ECmdSendIfCond      = 8,
        ECmdAllSendCid      = 2,
        ECmdSendRelativeAdr = 3,
        ECmdSelectCard      = 7,
        ECmdAppCommand      = 55,
        EAcmdSdSendOpCond   = 41,
        ECmdReadSingleBlock = 17,
        ECmdWriteBlock      = 24
        };

    inline volatile TUint32& Register(TRegister aRegister)
        {
        return *reinterpret_cast<volatile TUint32*>(
            KSdcc2LinearBase + static_cast<TUint32>(aRegister));
        }

    inline volatile TUint32& ClockRegister(TUint32 aOffset)
        {
        return *reinterpret_cast<volatile TUint32*>(KClockLinearBase + aOffset);
        }

    inline TBool IsBringupCommand(TUint32 aCommand)
        {
        return aCommand == ECmdGoIdle ||
               aCommand == ECmdSendIfCond ||
               aCommand == ECmdAllSendCid ||
               aCommand == ECmdSendRelativeAdr ||
               aCommand == ECmdSelectCard ||
               aCommand == ECmdAppCommand ||
               aCommand == EAcmdSdSendOpCond ||
               aCommand == ECmdReadSingleBlock ||
               aCommand == ECmdWriteBlock;
        }
    }

#endif // HTCLEO_SDCC_REGS_H
