#!/usr/bin/env bash
set -euo pipefail

real_compiler="${SBS_GCCE441BIN:-/root/gcce-native-4.4.1/bin}/arm-none-symbianelf-g++"
"$real_compiler" "$@"

output=""
previous=""
for argument in "$@"; do
    if [[ "$previous" == "-o" ]]; then
        output="$argument"
        previous=""
        continue
    fi
    if [[ "$argument" == "-o" ]]; then
        previous="-o"
    elif [[ "$argument" == -o* ]]; then
        output="${argument#-o}"
    fi
done

if [[ -n "$output" && "$(basename "$output")" == \
        "htcleohitchcockentrytrace.o" ]]; then
    python3 \
        /path/to/hd2-legacy-lab/Symbian/scripts/promote-htcleo-hitchcock-frozen-template-abi.py \
        "$output"
fi
