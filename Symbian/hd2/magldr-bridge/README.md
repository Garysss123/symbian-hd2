# HTC HD2 MAGLDR bridge

This component preserves MAGLDR's familiar Linux SD boot contract while
handing control to a native Symbian EKA2 ROM.

Stage 001 is intentionally a hand-off diagnostic, not a Symbian boot attempt.
It uses the framebuffer and MDP state left by MAGLDR to display four bands:

1. red — bridge entry reached;
2. yellow — machine type is HTC Leo (2524);
3. green — a valid `ATAG_INITRD2` payload was found;
4. cyan — the payload has the expected initial ARM branch of a Symbian ROM.

Magenta in a band means that stage failed. All four expected colours mean the
MAGLDR contract is understood and the next build can replace the Syborg ROM
with a QSD8250-linked EKA2 ROM.

`initrd.gz` in the generated package is deliberately a raw ROM image despite
its historical filename. MAGLDR supplies it through `ATAG_INITRD2`; the bridge
does not use a Linux initramfs.

The framebuffer/MDP addresses are hardware facts derived from the locally
validated HTC Leo Linux BSP. No Linux source is linked into this bridge.

