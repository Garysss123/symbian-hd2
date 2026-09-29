# HTC Leo / QSD8250 native Symbian BSP

This package replaces the former Syborg-binary overlay path with source-built
EKA2 hardware support for the HTC HD2.  It is intentionally paired with the
existing **full S60/Avkon ROM** at `romlinearbase=0x12200000`; a Mini ROM is not
a device-test baseline because changing ROM contents changes the runtime layout.

## Implemented source contracts

- ARMv7-compatible multiple memory model (`__CPU_CORTEX_A8N__`) with a scoped
  QSD8250 cache-policy compatibility patch.
- MAGLDR/HaRET RAM-resident ROM hand-off at physical `0x12200000`.
- Dynamic usable-RAM start computed from `TRomHeader::iRomSize`, rounded to the
  next MiB, so a 50+ MiB full ROM is never exposed to the RAM allocator.
- QSD8x50 VIC mapping and 64-entry EKA2 interrupt dispatch.
- QSD GPT IRQ 7 at 32.768 kHz, programmed for the EKA2 millisecond tick.
- HTC Leo RGB565 framebuffer, display HAL, NGA display channel and MDP31 refresh
  path, including composition/user/legacy buffer posting.
- Generic EStart and an HTCLEO-prefixed `ekdata.dll`; neither starts Syborg
  HostFS nor requests QEMU keyboard or media devices.
- ROMBUILD-valid hardware discriminator `0x0c0b0001` (layer `0x0c`, parent
  `0x0b`, one-bit variant mask).
- UART output remains deliberately disabled until clock and TLMM ownership are
  source-verified; no stale Syborg register semantics remain.

The bootstrap hardware-bank order is an ABI between `bootstrap/htcleo.s` and
`specific/htcleo.h`:

| Physical | Linear | Function |
|---:|---:|---|
| `0xAC000000` | `0xC6000000` | VIC |
| `0xAC100000` | `0xC6100000` | CSR/GPT |
| `0xA9C00000` | `0xC6200000` | UART3 (reserved) |
| `0xAA200000` | `0xC6300000` | MDP |
| `0x03839000` | `0xC6400000` | 480×800 RGB565 framebuffer |

## Build

From WSL:

```sh
/path/to/hd2-legacy-lab/Symbian/scripts/phase4-build-htcleo-native-bsp.sh udeb
/path/to/hd2-legacy-lab/Symbian/scripts/phase4-build-htcleo-native-bsp.sh urel
```

The script links this package at `/root/symbian/sf/adapt/htcleo`, applies only
the idempotent Scorpion `CTR.L1Ip` source patch, and verifies these initial
artifacts:

```text
_htcleo_bootloader_bootrom.bin
_htcleo_ekern.exe
_htcleo_kahtcleo.dll
_htcleo_euser.dll
_htcleo_ekdata.dll
e32strt.exe
exstart.dll
_htcleo_lcd.dll
_htcleo_hal.dll
display.ldd
```

No SD-card deployment is performed by this build.

The complete S60/Avkon image is built and audited with:

```sh
/path/to/hd2-legacy-lab/Symbian/scripts/phase4-build-htcleo-full-rom.sh
```

Its local output is `output/qsd8250-native-full-rom`; the builder replaces the
Syborg hardware layer only, preserves `romlinearbase=0x12200000`, runs
type-safe ROM linking, and then runs the fail-closed native full-ROM audit.

## Remaining after the first native full-ROM build

The local build proves that boot, kernel, variant, VIC, GPT, LCD/HAL, EStart and
the complete S60/Avkon payload form one type-safe ROM.  It does not prove an HD2
device boot or UI repaint; that is the next controlled device test.  Storage,
touch, audio, radio, camera and USB remain later BSP layers and do not justify
returning to raw address probing.
