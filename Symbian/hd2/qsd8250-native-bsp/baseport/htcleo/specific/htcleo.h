/*
 * Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
 * Modifications Copyright (c) 2026 HTC Leo Symbian port contributors.
 * Licensed under the Eclipse Public License v1.0.
 */

#ifndef __HTCLEO_H__
#define __HTCLEO_H__

#include <e32const.h>
#include <platform.h>
#include <e32hal.h>
#include <assp.h>
#include <kern_priv.h>
#include <mmboot.h>

#ifndef __HTCLEO__
#define __HTCLEO__
#endif

/*
 * The bootstrap maps these physical banks, in this exact order, starting at
 * KPrimaryIOBase.  Keep this list in lock-step with bootstrap/htcleo.s.
 */
const TUint KHwBaseVic            = KPrimaryIOBase + 0x00000000u; /* AC000000 */
const TUint KHwBaseCsr            = KPrimaryIOBase + 0x00100000u; /* AC100000 */
const TUint KHwBaseUart3          = KPrimaryIOBase + 0x00200000u; /* A9C00000 */
const TUint KHwBaseMdp            = KPrimaryIOBase + 0x00300000u; /* AA200000 */
const TUint KHwBaseFrameBuffer    = KPrimaryIOBase + 0x00400000u; /* 03839000 */
const TUint KHwBaseSdcc2          = KPrimaryIOBase + 0x00500000u; /* A0400000 */
const TUint KHwBaseSharedRam      = KPrimaryIOBase + 0x00600000u; /* 00100000 */
const TUint KHwBaseClockCtl       = KPrimaryIOBase + 0x00700000u; /* A8600000 */
const TUint KHwBaseGpio1          = KPrimaryIOBase + 0x00800000u; /* A9000000 */
const TUint KHwBaseGpio2          = KPrimaryIOBase + 0x00900000u; /* A9100000 */
const TUint KHwBaseI2c            = KPrimaryIOBase + 0x00a00000u; /* A9900000 */
const TUint KHwBaseSirc           = KPrimaryIOBase + 0x00b00000u; /* AC200000 */

const TPhysAddr KHwPhysVic         = 0xac000000u;
const TPhysAddr KHwPhysCsr         = 0xac100000u;
const TPhysAddr KHwPhysUart3       = 0xa9c00000u;
const TPhysAddr KHwPhysMdp         = 0xaa200000u;
const TPhysAddr KHwPhysFrameBuffer = 0x03839000u;
const TPhysAddr KHwPhysSdcc2       = 0xa0400000u;
const TPhysAddr KHwPhysSharedRam   = 0x00100000u;
const TPhysAddr KHwPhysClockCtl    = 0xa8600000u;
const TPhysAddr KHwPhysGpio1       = 0xa9000000u;
const TPhysAddr KHwPhysGpio2       = 0xa9100000u;
const TPhysAddr KHwPhysI2c         = 0xa9900000u;
const TPhysAddr KHwPhysSirc        = 0xac200000u;

const TUint KFrameBufferWidth     = 480u;
const TUint KFrameBufferHeight    = 800u;
const TUint KFrameBufferStride    = KFrameBufferWidth * 2u;
const TUint KFrameBufferBytes     = KFrameBufferStride * KFrameBufferHeight;

const TInt KMsTickPeriod          = 1000; /* microseconds */
const TUint KQsdGptMatch          = 32u;  /* 32768 Hz / 32 ~= 1.024 ms */

enum THtcleoInterruptId
    {
    EIntGpt = 7,
    EIntTimer1 = EIntGpt
    };

enum TQsdVicRegister
    {
    EVicIntSelect0   = 0x000,
    EVicIntSelect1   = 0x004,
    EVicIntEn0       = 0x010,
    EVicIntEnClear0  = 0x020,
    EVicIntEnClear1  = 0x024,
    EVicIntEnSet0    = 0x030,
    EVicIntEnSet1    = 0x034,
    EVicIntType0     = 0x040,
    EVicIntType1     = 0x044,
    EVicIntPolarity0 = 0x050,
    EVicIntPolarity1 = 0x054,
    EVicMasterEnable = 0x068,
    EVicConfig       = 0x06c,
    EVicIrqStatus0   = 0x080,
    EVicRawStatus0   = 0x0a0,
    EVicIntClear0    = 0x0b0,
    EVicIntClear1    = 0x0b4,
    EVicIrqVector    = 0x0d0,
    EVicIrqVectorPending = 0x0d4
    };

enum TQsdGptRegister
    {
    EGptMatch  = 0x00,
    EGptCount  = 0x04,
    EGptEnable = 0x08,
    EGptClear  = 0x0c,
    EGptDivider = 0x20
    };

class THtcleo
    {
public:
    enum TState
        {
        EEnable,
        EDisable
        };
    enum TTimerMode
        {
        ETimerModePeriodic,
        ETimerModeOneShot
        };

    static void Init3();

    IMPORT_C static void EnableTimerInterrupt(TUint aTimerBase);
    IMPORT_C static void DisableTimerInterrupt(TUint aTimerBase);
    IMPORT_C static void SetTimerLoad(TUint aTimerBase, TUint32 aValue);
    IMPORT_C static TUint TimerLoad(TUint aTimerBase);
    IMPORT_C static TUint TimerValue(TUint aTimerBase);
    IMPORT_C static void ClearTimerInt(TUint aTimerBase);
    IMPORT_C static TBool IsTimerEnabled(TUint aTimerBase);
    IMPORT_C static void EnableTimer(TUint aTimerBase, TState aState);
    IMPORT_C static TTimerMode TimerMode(TUint aTimerBase);
    IMPORT_C static void SetTimerMode(TUint aTimerBase, TTimerMode aValue);

    IMPORT_C static void EnableInt(TUint anId);
    IMPORT_C static void DisableInt(TUint anId);

    IMPORT_C static TInt VideoRamSize();
    IMPORT_C static TPhysAddr VideoRamPhys();
    IMPORT_C static TPhysAddr VideoRamPhysSecure();

    IMPORT_C static TUint32 DebugPortAddr();
    IMPORT_C static void MarkDebugPortOff();
    };

static inline TUint32 ReadReg(TUint32 aBase, TUint32 aOffset)
    {
    return *(volatile TUint32*)(aBase + aOffset);
    }

static inline void WriteReg(TUint32 aBase, TUint32 aOffset, TUint32 aValue)
    {
    *(volatile TUint32*)(aBase + aOffset) = aValue;
    }

static inline void QsdDrainWriteBuffer()
    {
    TUint32 zero = 0;
    __asm__ __volatile__("mcr p15, 0, %0, c7, c10, 4" : : "r"(zero) : "memory");
    }

#endif /* __HTCLEO_H__ */
