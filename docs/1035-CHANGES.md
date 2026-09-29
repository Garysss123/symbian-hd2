# 1035: quiet normal display and per-game landscape metadata

## Normal glyph retirement, not logging removal

The regular `HtcleoLifeGlyph` used by the small top debug row is separate from
`HtcleoCrashGlyphLine` / `HtcleoCrashGlyph` / `HtcleoCrashNoticePaint`.
The release retired exactly 20 normal framebuffer `STRH` instructions to ARM NOPs.
It did not remove the one-second timer, sampling, HAL observations, display refresh,
file-log producers, or the system-fatal renderer. Instruction timing is not claimed
to be cycle-identical after removing stores.

The original E32 was 15,060 bytes, SHA-256
`5e809535d9d02dd75c36cbbce33e671c13436f56a53e25d75c4c2b693a080f76`.
After retirement it remained 15,060 bytes, SHA-256
`56133702ced1047ef44516c39ab31fe75e3daf8eb26d1856de907e505232a527`.

The standalone example accepts exactly that original, verifies all original words
and the complete expected output hash, and creates a new file without overwrite:

```sh
python3 tools/retire-life-glyph-1035.py original-epointer.dll retired-epointer.dll
```

Neither binary is distributed. This command does not update a ROM, linked debug
ELF, package manifest or card. The actual 1035 release separately kept its debug
ELF consistent and verified the full ROM had no other changes beyond the same
20 words and its mathematically required header checksum. That full private build
context is not recreated by this example. Never transplant the offsets to a
different build; its hash guard intentionally refuses that.

## UNO Spin and GT Racing 2

The previously deployed JAD metadata forced portrait `360,640` although these two
tested titles rendered landscape. The correction is only:

```text
Nokia-MIDlet-Original-Display-Size: 640,360
Nokia-MIDlet-Target-Display-Size: 640,360
Nokia-MIDlet-App-Orientation: landscape
```

The JAR, launcher, icon, VM and shared canvas implementation were unchanged.
The existing canvas helper maps landscape pixels and inverse touch coordinates
together; this is not a global rotation of Home/MatrixMenu. A scan of the other
deployed descriptors did not justify rotating every unknown game.

UNO Spin's 1035 result was accepted by the user. GT Racing 2 was not retested in
that round. No commercial JAR, JAD package or extracted icon is included here.
