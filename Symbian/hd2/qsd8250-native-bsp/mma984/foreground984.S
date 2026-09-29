.syntax unified
.arch armv5t
.thumb
.macro ThumbCall target
    .set delta\@, (\target - (0x19804 + (. - ForegroundOwner984) + 4))
    .hword (0xf000 | ((delta\@ >> 12) & 0x7ff))
    .hword (0xf800 | ((delta\@ >> 1) & 0x7ff))
.endm
.section .text,"ax",%progbits
.global ForegroundOwner984
.type ForegroundOwner984,%function
.thumb_func
ForegroundOwner984:
    @ Same58-byte function, entry, prologue, frame and return as stock19804.
    push {r3,r4,r5,r6,r7,lr}
    movs r4,r1
    movs r1,r2
    movs r2,r3
    movs r5,r0
    @ Equivalent null-preserving event-source+20 adjustment saves4bytes.
    movs r0,r4
    ldr r3,[sp,#24]
    beq 1f
    adds r0,#20
1:  ThumbCall 0x19318
    movs r6,r0
    blx CleanupPushL
    movs r0,r6
    ThumbCall 0x19472
    @ NewL now constructs with NULL; adopt only after full success.
    str r6,[r0,#12]
    movs r7,r0
    blx CleanupPop
    movs r1,r7
    movs r0,r4
    ThumbCall 0xcc90
    lsrs r0,r6,#2
    str r0,[r5]
    nop
    pop {r3,r4,r5,r6,r7,pc}
.size ForegroundOwner984,.-ForegroundOwner984
