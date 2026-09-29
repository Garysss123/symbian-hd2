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

; Include to enable tracing
;	GBLL	CFG_DebugBootRom

; Include one of these to select the CPU
;	GBLL	CFG_CPU_ARM926J
;	GBLL	CFG_CPU_ARM1136
	GBLL    CFG_CPU_CORTEX_A8N
;	GBLL	CFG_CPU_ARM1136_ERRATUM_399234_FIXED
;	GBLL    CFG_CPU_ARM1136_ERRATUM_411920_FIXED
; Include the following lines if this is a bootloader bootstrap
;	GBLL	CFG_BootLoader

; If you want to supply a custom set of initial vectors (including reset vector) include the following line
;	GBLL	CFG_CustomVectors
;
; and provide a custom_vectors.inc file

; On ARM architecture 6 processors, include the following line to override the threshold
; on total physical RAM size at which the multiple memory model switches into large address space mode
; i.e. size>threshold -> 2Gb per process, size<=threshold -> 1Gb per process
; Defaults to 32Mb.
;	INIT_NUMERIC_CONSTANT	CFG_ARMV6_LARGE_CONFIG_THRESHOLD, <value>

; For the direct memory model only, include the following line if you wish the exception vectors at the
; start of the bootstrap to be used at all times. This is only relevant if an MMU is present - this option
; is mandatory if not.
;	GBLL	CFG_UseBootstrapVectors
;
; If the above option is in use (including if no MMU is present) the following symbol should be defined
; to specify the offset from the bootstrap to the kernel image.
;	INIT_NUMERIC_CONSTANT	KernelCodeOffset, 0x4000

; Include the following line if you wish to include the ROM autodetection code based on data bus
; capacitance and image repeats.
;	GBLL	CFG_AutoDetectROM

; Include the following line to minimise the initial kernel heap size
; On the direct memory model the size of the kernel data area (super page to end of kernel heap) 
; is rounded up to the next 1Mb if this is not included, 4K if it is.
; On the moving and multiple models, the size of the initial kernel heap area is rounded up to
; the next 64K if this is not included, 4K if it is.
;	GBLL	CFG_MinimiseKernelHeap

; On the moving or multiple memory models, include either or both of the following lines to
; specify the size of the initial kernel heap
;	INIT_NUMERIC_CONSTANT	CFG_KernelHeapMultiplier, <multiplier>
;	INIT_NUMERIC_CONSTANT	CFG_KernelHeapBaseSize, <base>
;
; The initial kernel heap size is MAX( <base> + <multiplier> * N / 16, value specified in ROMBUILD )
; where N is the total physical RAM size in pages.
; <base> defaults to 24K and <multiplier> defaults to 9*16 (ie 9 bytes per page).

; Specific stuff for integrator
;	GBLL	CFG_Integrator_DontSetClock
; ROMBUILD hardware discriminator: layer 0x0c, parent 0x0b, one-bit mask.
; A textual "HTC" value is invalid because the low 16 bits must be one bit.
	INIT_NUMERIC_CONSTANT	CFG_HWVD, 0x0C0B0001

; MAGLDR/HaRET already place the full ROM at its final physical address
; (0x12200000), so the flash-to-RAM bootstrap path must remain disabled.
    

	END
