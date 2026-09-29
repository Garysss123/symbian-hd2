#!/bin/sh
# Rebuild only the native epointer kernel extension, never the whole BSP.
set -eu
project=/path/to/hd2-legacy-lab/Symbian
export EPOCROOT=/root/symbian/
export SBS_HOME=/root/symbian/linux_build/sbsv2/raptor
export SBS_GCCE441BIN=/root/gcce-native-4.4.1/bin
export PERL5LIB=/root/symbian/linux_build/cross-plat-dev-utils
export PERL_USE_UNSAFE_INC=1
src="$project/hd2/qsd8250-native-bsp/baseport/htcleo/input"
stage="$EPOCROOT/sf/adapt/htcleo/baseport/htcleo"
output="$project/output/qsd8250-native-full-rom"
python3 "$project/scripts/test-htcleo-thread-state-hal.py" "$stage/input"
python3 "$project/scripts/test-htcleo-logless-liveness.py"
python3 "$project/scripts/test-htcleo-crash-notice.py"
cp "$src/htcleo_touch.cpp" "$stage/input/htcleo_touch.cpp"
cp "$src/htcleo_threadstate.inl" "$stage/input/htcleo_threadstate.inl"
cp "$src/htcleo_liveness.inl" "$stage/input/htcleo_liveness.inl"
cp "$src/htcleo_crashnotice.inl" "$stage/input/htcleo_crashnotice.inl"
"$SBS_HOME/bin/sbs" --configpath="$project/config" \
    -b "$stage/bld.inf" -p htcleo_touch.mmp \
    -c arm.v5.urel.gcce4_4_1.surge.hd2_roalign --noexport -j 2
binary="$EPOCROOT/epoc32/release/armv5/urel/_htcleo_epointer.dll"
test -s "$binary"
"$EPOCROOT/epoc32/tools/elf2e32" --dump=hseit --e32input="$binary" \
    >"$output/THREAD-STATE-PDD-E32.txt"
sha256sum "$binary" >"$output/epointer-thread-state-urel.sha256"
sha256sum "$binary" >"$project/output/qsd8250-native-bsp/htcleo-touch-urel.sha256"
obj=$(find "$EPOCROOT/epoc32/build/htcleo" \
    -path '*/_htcleo_epointer_dll/armv5/urel/htcleo_touch.o' -type f)
test "$(printf '%s\n' "$obj" | wc -l)" -eq 1
"$SBS_GCCE441BIN/arm-none-symbianelf-objdump" -dr "$obj" \
    >"$output/THREAD-STATE-PDD.disasm"
grep -q 'HtcleoReadThreadState' "$output/THREAD-STATE-PDD.disasm"
grep -q 'ObjectFromHandle' "$output/THREAD-STATE-PDD.disasm"
grep -q 'ThreadGetUserContext' "$output/THREAD-STATE-PDD.disasm"
grep -q 'InfoCopy' "$output/THREAD-STATE-PDD.disasm"
echo 'HTCLEO_THREAD_STATE_HAL=21-readonly-v2-endpoint-readyqueue-timeslice-context'
