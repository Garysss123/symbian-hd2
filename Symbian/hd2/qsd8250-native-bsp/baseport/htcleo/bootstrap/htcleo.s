;/*
;* Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
;* All rights reserved.
;* This component and the accompanying materials are made available
;* under the terms of the License "Eclipse Public License v1.0"
;* which accompanies this distribution, and is available
;* at the URL "http://www.eclipse.org/legal/epl-v10.html".
;*
;* Initial Contributors:
;* Nokia Corporation - initial contribution.
;*
;* Contributors:
;*
;* Description:
;*
;*/
		
		GBLL	__VARIANT_S__       ; indicates that this is platform-specific code
		GBLL	__HTCLEO_S__		; indicates which source file this is

		INCLUDE	bootcpu.inc
		INCLUDE htcleo.inc
;
;*******************************************************************************
;
        IMPORT	ResetEntry
;
;*******************************************************************************
;
        AREA |Boot$$Code|, CODE, READONLY, ALIGN=6
;
;*******************************************************************************
; Initialise Hardware
;	Determine the hardware configuration
;	Determine the reset reason. If it is wakeup from a low power mode, perform
;		whatever reentry sequence is required and jump back to the kernel.
;	Set up the memory controller so that at least some RAM is available
;	Set R10 to point to the super page or to a temporary version of the super page
;		with at least the following fields valid:
;		iBootTable, iCodeBase, iActiveVariant, iCpuId
;	Initialise the debug serial port
;
; Enter with:
;	R12 points to TRomHeader
;	NO STACK
;	R14 = return address (as usual)
;
; All registers may be modified by this call
;*******************************************************************************
	EXPORT	InitialiseHardware
InitialiseHardware	ROUT
		mov		r13, lr							    ; save return address

		adrl	r1, ParameterTable	        ; pass address of parameter table
		bl		InitCpu				        ; initialise CPU/MMU registers
						
;*******************************************************************************
; DoInitialise Hardware
;	Initialise CPU registers
;	Determine the hardware configuration
;	Determine the reset reason. If it is wakeup from a low power mode, perform
;		whatever reentry sequence is required and jump back to the kernel.
;	Set up the memory controller so that at least some RAM is available
;	Set R10 to point to the super page or to a temporary version of the super page
;		with at least the following fields valid:
;		iBootTable, iCodeBase, iActiveVariant, iCpuId
;	In debug builds initialise the debug serial port
;
; Enter with:
;	R12 points to TRomHeader
;	NO STACK
;	R13 = return address (as usual)
;
; All registers may be modified by this call
;*******************************************************************************
DoInitialiseHardware	ROUT
		
		bl		InitDebugPort

		ldr		r7, =CFG_HWVD					; variant number

		ldr		r10, =KHwTemporarySuperPage	; safe RAM above the full ROM

; Set up the required super page values
		str		r7, [r10, #SSuperPageBase_iActiveVariant]

		mov		r1, #0
		str		r1, [r10, #SSuperPageBase_iHwStartupReason]	; reset reason (from hardware)

		add		r1, r10, #CpuPageOffset
		str		r1, [r10, #SSuperPageBase_iMachineData]
		bl		GetBootTableAddress
		str		r0, [r10, #SSuperPageBase_iBootTable]		; set the boot function table
		str		r12, [r10, #SSuperPageBase_iCodeBase]		; set the base address of bootstrap code
		mrc		p15, 0, r0, c0, c0, 0						; read CPU ID from CP15 (remove if no CP15)
		str		r0, [r10, #SSuperPageBase_iCpuId]

		mov		r0, r13
		add		sp, r10, #CpuBootStackTop		            ; set up a boot stack
		push    {r0}						                ; save return address
		bl		DoInitHw2						            ; any extra CPU-dependent stuff
				
		ldr		r7, [r10, #SSuperPageBase_iActiveVariant]
		DWORD	r7, "ActiveVariant"

		pop     {pc}						                ; return

;*******************************************************************************
DoInitHw2	ROUT
		mrc		p15, 0, r0, c0, c0, 0
		DWORD	r0, "MMUID"
		mrc		p15, 0, r0, c0, c0, 1
		DWORD	r0, "CacheType"
		mrc		p15, 0, r0, c0, c0, 2
		DWORD	r0, "TCMType"
		mrc		p15, 0, r0, c0, c0, 3
		DWORD	r0, "TLBType"
        bx      lr

;*******************************************************************************
; Get a pointer to the list of hardware banks
;
; The pointer returned should point to a list of hardware banks declared with
; the HW_MAPPING and/or HW_MAPPING_EXT macros. A zero word terminates the list.
; For the direct memory model, all hardware on the system should be mapped here
; and the mapping will set linear address = physical address.
; For the moving or multiple model, only the hardware required to boot the kernel
; and do debug tracing needs to be mapped here. The linear addresses used will
; start at KPrimaryIOBase and step up as required with the order of banks in
; the list being maintained in the linear addresses used.
;
; HW_MAPPING PB, SIZE, MULT
;	This declares a block of I/O with physical base PB and address range SIZE
;	blocks each of which has a size determined by MULT. The page size used for
;	the mapping is determined by MULT. The linear address base of the mapping
;	will be the next free linear address rounded up to the size specified by
;	MULT.
;	The permissions used for the mapping are the standard I/O permissions (BTP_Hw).
;
; HW_MAPPING_EXT PB, SIZE, MULT
;	This declares a block of I/O with physical base PB and address range SIZE
;	blocks each of which has a size determined by MULT. The page size used for
;	the mapping is determined by MULT. The linear address base of the mapping
;	will be the next free linear address rounded up to the size specified by
;	MULT.
;	The permissions used for the mapping are determined by a BTP_ENTRY macro
;	immediately following this macro in the HW bank list or by a DCD directive
;	specifying a different standard permission type.
;
; Configurations without an MMU need not implement this function.
;
; Enter with :
;		R10 points to super page
;		R12 points to ROM header
;		R13 points to valid stack
;
; Leave with :
;		R0 = pointer
;		Nothing else modified
;*******************************************************************************
	EXPORT	GetHwBanks
GetHwBanks	ROUT
		adr		r0, %FT1
		bx      lr
1
		; Preserve the verified first eight mappings.  New native peripherals
		; are append-only so their addition cannot move SDCC/shared-RAM/clock.
		HW_MAPPING		KHwPhysVic,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysCsr,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysUart3,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysMdp,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysFrameBuffer,		KFrameBufferPageCount,	HW_MULT_4K
		HW_MAPPING		KHwPhysSdcc2,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysSharedRam,		1,	HW_MULT_1M
		HW_MAPPING		KHwPhysClockCtl,		1,	HW_MULT_1M
		HW_MAPPING		KHwPhysGpio1,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysGpio2,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysI2c,			1,	HW_MULT_1M
		HW_MAPPING		KHwPhysSirc,			1,	HW_MULT_1M

		DCD     0   ; terminator

;*******************************************************************************
; Notify an unrecoverable error during the boot process
;
; Enter with:
;	R14 = address at which fault detected
;
; Don't return
;*******************************************************************************
	EXPORT	Fault
Fault	ROUT
		b		BasicFaultHandler	; generic handler dumps registers via debug
									; serial port

;*******************************************************************************
; Reboot the system
;
; Enter with:
;		R0 = reboot reason code
;
; Don't return (of course)
;*******************************************************************************
	ALIGN	32, 0
	EXPORT	RestartEntry
RestartEntry	ROUT
		GETCPSR	r1
		orr		r1, #0xC0
		SETCPSR	r1						; disable IRQ and FIQ
RestartWait
		mov		r0, #0
		mcr		p15, 0, r0, c7, c0, 4		; safe halt until reset support exists
		b		RestartWait

;*******************************************************************************
; Get a pointer to the list of RAM banks
;
; The pointer returned should point to a list of {BASE; MAXSIZE;} pairs, where
; BASE is the physical base address of the bank and MAXSIZE is the maximum
; amount of RAM which may be present in that bank. MAXSIZE should be a power of
; 2 and BASE should be a multiple of MAXSIZE. The generic code will examine the
; specified range of addresses and determine the actual amount of RAM if any
; present in the bank. The list is terminated by an entry with zero size.
;
; The pointer returned will usually be to constant data, but could equally well
; point to RAM if dynamic determination of the list is required.
;
; Enter with :
;		R10 points to super page
;		R12 points to ROM header
;		R13 points to valid stack
;
; Leave with :
;		R0 = pointer
;		Nothing else modified
;*******************************************************************************
	EXPORT	GetRamBanks
GetRamBanks	ROUT
		push    {r1-r3,lr}
		ldr		r1, =KHwRomBaseAddr
		ldr		r3, [r12, #TRomHeader_iRomSize]
		add		r1, r1, r3			; first byte after the full ROM
		ldr		r3, =0x000fffff
		add		r1, r1, r3
		bic		r1, r1, r3			; align usable RAM to the next MiB
		ldr		r2, =KHwRamEndAddr
		sub		r2, r2, r1
		orr		r1, #RAM_VERBATIM		; do not destructively probe loaded RAM
		mov		r3, #0
		mov		lr, #0
		add		r0, r10, #CpuPageOffset
		stm		r0, {r1-r3,lr}			; bank pair followed by terminator
		pop     {r1-r3,pc}

;*******************************************************************************
; Get a pointer to the list of ROM banks
;
; The pointer returned should point to a list of entries of SRomBank structures,
; usually declared with the ROM_BANK macro.
; The list is terminated by a zero size entry (four zero words)
;
; ROM_BANK	PB, SIZE, LB, W, T, RS, SS
; PB = physical base address of bank
; SIZE = size of bank
; LB = linear base if override required - usually set this to 0
; W = bus width (ROM_WIDTH_8, ROM_WIDTH_16, ROM_WIDTH_32)
; T = type (see TRomType enum in kernboot.h)
; RS = random speed
; SS = sequential speed
;
; Only PB, SIZE, LB are used by the rest of the bootstrap.
; The information given here can be modified by the SetupRomBank call, if
; dynamic detection and sizing of ROMs is required.
;
; Enter with :
;		R10 points to super page
;		R12 points to ROM header
;		R13 points to valid stack
;
; Leave with :
;		R0 = pointer
;		Nothing else modified
;*******************************************************************************
	EXPORT	GetRomBanks
GetRomBanks	ROUT
	        adr		r0, RomBanksFlashTable
	        bx      lr

RomBanksFlashTable
		ROM_BANK	KHwRomBaseAddr, KHwRomMaxSize, 0, ROM_WIDTH_32, ERomTypeXIPFlash, 0, 0
		DCD		0,0,0,0			; terminator

;*******************************************************************************
; Set up RAM bank
;
; Do any additional RAM controller initialisation for each RAM bank which wasn't
; done by InitialiseHardware.
; Called twice for each RAM bank :-
;	First with R3 = 0xFFFFFFFF before bank has been probed
;	Then, if RAM is present, with R3 indicating validity of each byte lane, ie
;	R3 bit 0=1 if D0-7 are valid, bit1=1 if D8-15 are valid etc.
; For each call R1 specifies the bank physical base address.
;
; Enter with :
;		R10 points to super page
;		R12 points to ROM header
;		R13 points to stack
;		R1 = physical base address of bank
;		R3 = width (bottom 4 bits indicate validity of byte lanes)
;			 0xffffffff = preliminary initialise
;
; Leave with :
;		No registers modified
;*******************************************************************************
	EXPORT	SetupRamBank
SetupRamBank	ROUT
		bx      lr

;*******************************************************************************
; Set up ROM bank
;
; Do any required autodetection and autosizing of ROMs and any additional memory
; controller initialisation for each ROM bank which wasn't done by
; InitialiseHardware.
;
; The first time this function is called R11=0 and R0 points to the list of
; ROM banks returned by the BTF_RomBanks call. This allows any preliminary setup
; before autodetection begins.
;
; This function is subsequently called once for each ROM bank with R11 pointing
; to the current information held about that ROM bank (SRomBank structure).
; The structure pointed to by R11 should be updated with the size and width
; determined. The size should be set to zero if there is no ROM present in the
; bank.
;
; Enter with :
;		R10 points to super page
;		R12 points to ROM header
;		R13 points to stack
;		R11 points to SRomBank info for this bank
;		R11 = 0 for preliminary initialise (all banks)
;
; Leave with :
;		Update SRomBank info with detected size/width
;		Set the size field to 0 if the ROM bank is absent
;		Can modify R0-R4 but not other registers
;
;*******************************************************************************
	EXPORT	SetupRomBank
SetupRomBank	ROUT						    ; only get here if running from ROM
		cmp		r11, #0
		bxeq	lr						        ; don't do anything for preliminary
		ldm	    r11, {r0,r1}				    ; r0 = base, r1 = size
        lsr     r0, pc, #20
        lsl     r0, #20                         ; r0 = image base
   		ldr		r1, [r12, #TRomHeader_iRomSize] ; r1 = size of ROM block
		stm 	r11, {r0,r1}
        bx      lr

;*******************************************************************************
; Reserve physical memory
;
; Reserve any physical RAM needed for platform-specific purposes before the
; bootstrap begins allocating RAM for page tables/kernel data etc.
;
; There are two methods for this:
;	1.	The function ExciseRamArea may be used. This will remove a contiguous
;		region of physical RAM from the RAM bank list. That region will never
;		again be identified as RAM.
;	2.	A list of excluded physical address ranges may be written at [R11].
;		This should be a list of (base,size) pairs terminated by a (0,0) entry.
;		This RAM will still be identified as RAM by the kernel but will not
;		be allocated by the bootstrap and will subsequently be marked as
;		allocated by the kernel immediately after boot.
;
; Enter with :
;		R10 points to super page
;		R11 indicates where preallocated RAM list should be written.
;		R12 points to ROM header
;		R13 points to stack
;
; Leave with :
;		R0-R3 may be modified. Other registers should be preserved.
;*******************************************************************************
	EXPORT	ReservePhysicalMemory
ReservePhysicalMemory	ROUT
		bx      lr

;*******************************************************************************
; Do final platform-specific initialisation before booting the kernel
;
; Typical uses for this call would be:
;	1.	Mapping cache flushing areas
;	2.	Setting up pointers to routines in the bootstrap which are used by
;		the variant or drivers (eg idle code).
;
; Enter with :
;		R10 points to super page
;		R11 points to TRomImageHeader for the kernel
;		R12 points to ROM header
;		R13 points to stack
;
; Leave with :
;		R0-R9 may be modified. Other registers should be preserved.
;
;*******************************************************************************
	EXPORT	FinalInitialise
FinalInitialise ROUT
		bx      lr

;*******************************************************************************
; Debug port write routine associated with debug port in the super page
; Enter with :
;		R0  character to be written
;		R12 points to rom header
;		R13 points to valid stack
;
; Leave with :
;		nothing modified 
;*******************************************************************************
	EXPORT	DoWriteC
DoWriteC	ROUT
	IF	CFG_DebugBootRom
		push    {r1,lr}
		bl		GetDebugPortBase			; r1 = base address of UART registers
	
		str		r0, [r1, #4]				; Store to data register

		pop     {r1,pc}
	ELSE
		bx      lr
	ENDIF

;*******************************************************************************
; Initialise the debug port
;
; Enter with :
;		R12 points to ROM header
;		There is no valid stack
;
; Leave with :
;		R0-R2 modified
;		Other registers unmodified
;*******************************************************************************
InitDebugPort	ROUT
		; UART clock and TLMM ownership are not assumed across MAGLDR hand-off.
		mov		r0, #0
		mov		r1, #0
		bx		lr

;*******************************************************************************
; Get the base address of the debug UART
;
; Enter with :
;		R12 points to ROM header
;		There may be no stack
;
; Leave with :
;		R1 = base address of port, 0 for JTAG
;		Z flag set for JTAG, clear for non-JTAG
;		No other registers modified
;*******************************************************************************
GetDebugPortBase	ROUT
		movs	r1, #0
		bx      lr

;*******************************************************************************
; Return parameter specified by R0 (see TBootParam enum)
;
; Enter with :
;		R0 = parameter number
;
; Leave with :
;		If parameter value is supplied, R0 = value and N flag clear
;		If parameter value is not supplied, N flag set. In this case the
;		parameter may be defaulted or the system may fault.
;		R0, R1 modified. No other registers modified.
;
;*******************************************************************************
GetParameters ROUT
		adr		r1, ParameterTable
		b		FindParameter

ParameterTable
		DCD		-1								; terminator

;*******************************************************************************
; BOOT FUNCTION TABLE
;*******************************************************************************
GetBootTableAddress	ROUT
		adr		r0, HtcleoBootTable
        bx      lr

HtcleoBootTable
		DCD	DoWriteC					; output a debug character
		DCD	GetRamBanks					; get list of RAM banks
		DCD	SetupRamBank				; set up a RAM bank
		DCD	GetRomBanks					; get list of ROM banks
		DCD	SetupRomBank				; set up a ROM bank
		DCD	GetHwBanks					; get list of HW banks
		DCD	ReservePhysicalMemory		; reserve physical RAM if required
		DCD	GetParameters				; get addresses for direct memory model
		DCD	FinalInitialise				; Final initialisation before booting the kernel
		DCD	HandleAllocRequest			; allocate memory (usually in generic code)
		DCD	GetPdeValue					; usually in generic code
		DCD	GetPteValue					; usually in generic code
		DCD	PageTableUpdate				; usually in generic code
		DCD	EnableMmu					; Enable the MMU (usually in generic code)

; These entries specify the standard MMU permissions for various areas
		
	IF  CFG_MMMultiple
;	IF  CFG_MMFlexible
	    IF CFG_ARMV7
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RORO, MEMORY_FULLY_CACHED,       	1,  1,  0,  0   ; ROM
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, MEMORY_FULLY_CACHED,       	0,  1,  0,  0   ; kernel data/stack/heap
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, MEMORY_FULLY_CACHED,       	0,  1,  0,  0   ; super page/CPU page
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, MEMORY_FULLY_CACHED,  	0,  1,  0,  0   ; page directory/tables
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RONO, MEMORY_FULLY_CACHED,       	1,  1,  0,  0   ; exception vectors
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, MEMORY_STRONGLY_ORDERED,      0,  1,  0,  0   ; hardware registers
		DCD         0                                                           ; unused (minicache flush)
		DCD         0                                                           ; unused (maincache flush)
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, MEMORY_FULLY_CACHED,       	0,  1,  0,  0   ; page table info
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWRW, MEMORY_FULLY_CACHED,       	1,  1,  0,  0   ; user RAM
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RONO, MEMORY_STRONGLY_ORDERED,      1,  1,  0,  0   ; temporary identity mapping
		BTP_ENTRY   CLIENT_DOMAIN, UNC_PERM,  MEMORY_STRONGLY_ORDERED,      0,  1,  0,  0   ; uncached
	    ENDIF	
	    IF CFG_ARMV6
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RORO, CACHE_WBWA,       1,  1,  0,  0       ; ROM
	        BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, CACHE_WBWA,       0,  1,  0,  0       ; kernel data/stack/heap
	        BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, CACHE_WBWA,       0,  1,  0,  0       ; super page/CPU page
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, CACHE_WBWA,		0,  1,  0,  0       ; page directory/tables
	        BTP_ENTRY   CLIENT_DOMAIN, PERM_RONO, CACHE_WTRA,       1,  1,  0,  0       ; exception vectors
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, CACHE_SO,         0,  1,  0,  0       ; hardware registers
		DCD			0										; unused (minicache flush)
		DCD			0										; unused (maincache flush)
	        BTP_ENTRY   CLIENT_DOMAIN, PERM_RWNO, CACHE_WBWA,       0,  1,  0,  0       ; page table info
	        BTP_ENTRY   CLIENT_DOMAIN, PERM_RWRW, CACHE_WBWA,       1,  1,  0,  0       ; user RAM
		BTP_ENTRY   CLIENT_DOMAIN, PERM_RONO, CACHE_SO,         1,  1,  0,  0       ; temporary identity mapping
	        BTP_ENTRY   CLIENT_DOMAIN, UNC_PERM,  CACHE_SO,         0,  1,  0,  0       ; uncached
	    ENDIF
	ENDIF
	IF CFG_MMMoving
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RORO, CACHE_WT		; ROM
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RWNO, CACHE_WB		; kernel data/stack/heap
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RWNO, CACHE_WB		; super page/CPU page
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RWNO, CACHE_WT		; page directory/tables
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RORO, CACHE_WT		; exception vectors
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RWRO, CACHE_NCNB	; hardware registers
		DCD			0										; unused (minicache flush)
		DCD			0										; unused (maincache flush)
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RWNO, CACHE_WB		; page table info
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RWRW, CACHE_WB		; user RAM
		BTP_ENTRY	CLIENT_DOMAIN, PERM_RORO, CACHE_NCNB	; temporary identity mapping
		BTP_ENTRY	CLIENT_DOMAIN, UNC_PERM,  CACHE_NCNB	; uncached
	ENDIF

	END
