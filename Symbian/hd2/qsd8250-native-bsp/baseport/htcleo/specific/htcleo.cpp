/*
 * Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
 * Modifications Copyright (c) 2026 HTC Leo Symbian port contributors.
 * Licensed under the Eclipse Public License v1.0.
 */

#include <htcleo_priv.h>

void THtcleo::Init3()
    {
    }

EXPORT_C TBool THtcleo::IsTimerEnabled(TUint aTimerBase)
    {
    return (ReadReg(aTimerBase, EGptEnable) & 1u) != 0;
    }

EXPORT_C void THtcleo::EnableTimerInterrupt(TUint /* aTimerBase */)
    {
    /* The GPT interrupt gate is the VIC enable bit on QSD8x50. */
    }

EXPORT_C void THtcleo::DisableTimerInterrupt(TUint aTimerBase)
    {
    WriteReg(aTimerBase, EGptEnable, 0u);
    QsdDrainWriteBuffer();
    }

EXPORT_C void THtcleo::EnableTimer(TUint aTimerBase, TState aState)
    {
    WriteReg(aTimerBase, EGptEnable,
             aState == EEnable ? 3u : 0u); /* enable + clear-on-match */
    QsdDrainWriteBuffer();
    }

EXPORT_C THtcleo::TTimerMode THtcleo::TimerMode(TUint /* aTimerBase */)
    {
    return ETimerModePeriodic;
    }

EXPORT_C void THtcleo::SetTimerMode(TUint /* aTimerBase */,
                                    TTimerMode /* aValue */)
    {
    /* QSD GPT periodic operation is selected by enable bit 1. */
    }

EXPORT_C TUint32 THtcleo::DebugPortAddr()
    {
    /* UART clocks/pinmux are not assumed to survive MAGLDR hand-off. */
    return (TUint32)KNullDebugPort;
    }

EXPORT_C void THtcleo::MarkDebugPortOff()
    {
    TheVariant.iDebugPortBase = 0;
    }

EXPORT_C TInt THtcleo::VideoRamSize()
    {
    return (TInt)KFrameBufferBytes;
    }

EXPORT_C TPhysAddr THtcleo::VideoRamPhys()
    {
    return KHwPhysFrameBuffer;
    }

EXPORT_C TPhysAddr THtcleo::VideoRamPhysSecure()
    {
    return 0;
    }
