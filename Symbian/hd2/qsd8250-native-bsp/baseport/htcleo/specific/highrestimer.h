/*
 * QSD8250 high-resolution timer policy.
 *
 * Do not advertise HAS_HIGH_RES_TIMER yet: the bootloader may leave the DGT
 * clock in an unknown state. EKA2 will use its tick-based fallback until the
 * dedicated QSD clock setup is source-verified.
 */
#ifndef __HIGHRESTIMER_H__
#define __HIGHRESTIMER_H__
#endif
