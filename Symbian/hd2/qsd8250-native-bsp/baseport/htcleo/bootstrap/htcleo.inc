; Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
; Modifications Copyright (c) 2026 HTC Leo Symbian port contributors.
; Licensed under the Eclipse Public License v1.0.

;---------------------------------------------------------------------------
; MAGLDR/HaRET memory contract used by the verified full-ROM experiments.
;---------------------------------------------------------------------------

KHwRomBaseAddr          EQU     0x12200000
KHwRomMaxSize           EQU     0x08000000
KHwRamEndAddr           EQU     0x2fc00000
KHwTemporarySuperPage   EQU     0x2fbfd000
KHwTemporaryStackTop    EQU     0x2fbff000

;---------------------------------------------------------------------------
; QSD8250 physical peripherals.  Order must match the C++ linear constants.
;---------------------------------------------------------------------------

KHwPhysVic              EQU     0xac000000
KHwPhysCsr              EQU     0xac100000
KHwPhysUart3            EQU     0xa9c00000
KHwPhysMdp              EQU     0xaa200000
KHwPhysFrameBuffer      EQU     0x03839000
KHwPhysSdcc2            EQU     0xa0400000
KHwPhysSharedRam        EQU     0x00100000
KHwPhysClockCtl         EQU     0xa8600000
KHwPhysGpio1            EQU     0xa9000000
KHwPhysGpio2            EQU     0xa9100000
KHwPhysI2c              EQU     0xa9900000
KHwPhysSirc             EQU     0xac200000
KFrameBufferPageCount   EQU     188             ; ceil(480*800*2 / 4096)

;---------------------------------------------------------------------------
; Linear addresses assigned by GetHwBanks under MM_MULTIPLE.
;---------------------------------------------------------------------------

KHwLinBaseVic           EQU     KPrimaryIOBase + 0x00000000
KHwLinBaseCsr           EQU     KPrimaryIOBase + 0x00100000
KHwLinBaseUart3         EQU     KPrimaryIOBase + 0x00200000
KHwLinBaseMdp           EQU     KPrimaryIOBase + 0x00300000
KHwLinBaseFrameBuffer   EQU     KPrimaryIOBase + 0x00400000
KHwLinBaseSdcc2         EQU     KPrimaryIOBase + 0x00500000
KHwLinBaseSharedRam     EQU     KPrimaryIOBase + 0x00600000
KHwLinBaseClockCtl      EQU     KPrimaryIOBase + 0x00700000
KHwLinBaseGpio1         EQU     KPrimaryIOBase + 0x00800000
KHwLinBaseGpio2         EQU     KPrimaryIOBase + 0x00900000
KHwLinBaseI2c           EQU     KPrimaryIOBase + 0x00a00000
KHwLinBaseSirc          EQU     KPrimaryIOBase + 0x00b00000

        END
