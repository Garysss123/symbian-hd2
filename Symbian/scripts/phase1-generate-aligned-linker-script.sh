#!/bin/sh
# GCCE 4.4-172's built-in armsymbian script permits the read-only LOAD
# segment to end at an odd address. elf2e32 appends its 32-bit export table
# immediately after that segment and then rejects its own unaligned E32
# relocation. Materialize the original linker script and put real padding
# inside .rodata, so it contributes to the LOAD segment's file size.
set -eu

ld=/root/gcce-native-4.4.1/bin/arm-none-symbianelf-ld
out=/root/symbian-phase1/armsymbian-aligned.xs
raw=/root/symbian-phase1/armsymbian-default.verbose

"$ld" --verbose >"$raw"
awk '
    /^=+$/ { separators++; next }
    separators == 1 { print }
    separators == 2 { exit }
' "$raw" | sed \
    '/^[[:space:]]*\.rodata[[:space:]]*:/ s/ }$/ . = ALIGN(4); }/' \
    >"$out"

grep -n -B1 -A1 '^[[:space:]]*\.rodata[[:space:]]*:' "$out"
test -s "$out"
