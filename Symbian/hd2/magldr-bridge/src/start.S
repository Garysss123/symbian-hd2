/*
 * MAGLDR Linux-zImage-compatible entry stub for HTC HD2.
 *
 * Entry contract follows the 32-bit ARM Linux boot protocol:
 *   r0 = 0
 *   r1 = machine type (2524 for HTC Leo)
 *   r2 = physical ATAG list
 *
 * This first milestone intentionally stops after validating the payload.
 */

    .syntax unified
    .arch armv5te
    .arm

    .section .start, "ax", %progbits
    .global _start
    .type _start, %function

_start:
    /* The legacy ARM zImage header expected by MAGLDR. */
    mov     r0, r0
    mov     r0, r0
    mov     r0, r0
    mov     r0, r0
    mov     r0, r0
    mov     r0, r0
    mov     r0, r0
    mov     r0, r0
    b       1f
    .word   0x016f2818
    .word   0x00000000
    /* Patched to the final raw image size by the build script. */
    .word   0x00000000

1:
    /* Disable IRQ/FIQ, but preserve MAGLDR's MMU/cache state for now. */
    mrs     r3, cpsr
    orr     r3, r3, #0xc0
    msr     cpsr_c, r3

    /* Save the boot protocol arguments across stack setup. */
    mov     r4, r0
    mov     r5, r1
    mov     r6, r2
    ldr     sp, =0x11807000

    mov     r0, r4
    mov     r1, r5
    mov     r2, r6
    bl      hd2_bridge_main

2:
    b       2b

    .size _start, . - _start
