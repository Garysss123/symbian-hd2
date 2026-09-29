# Build boundaries and prerequisites

## Verified here versus external inputs

The initial public snapshot is useful for reviewing and continuing the HD2 port.
It is **not an independently reproducible full Beta 1 ROM build**. A complete
source-only rebuild from a fresh clone has not been performed. The historical
full-ROM recipe relies on staged SDK sources, accumulated release objects and
binary inputs that are intentionally not redistributed.

External prerequisites used by the project:

- Symbian^3 PDK 3.0.4 build 1144 sources/resources and the applicable binary inputs.
- SymbianSource EKA2 and Qemu/Syborg GCC branch source trees; the HD2 uses its own
  BSP, not QEMU hardware at runtime.
- Linux/WSL build environment, Raptor/SBSv2, Perl and Python 3.
- Sourcery G++ Lite for SymbianOS GCCE 4.4.1 / binutils 2.19.51 (ARM Symbian EABI).
- A separate bare-metal ARM toolchain for the MAGLDR bridge.
- Separately obtained Java VM dependencies for full Java operation. Public JRT
  source is not the same thing as a complete, redistributable JVM.

Supply dependencies lawfully under their own licenses. This project does not
grant rights to the PDK release binaries, compiler, firmware, VM, games or art.

## Source check (safe, no device access)

```sh
python3 tools/check-source-tree.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

The source check verifies the release file manifest, rejects binary/private-data
payload types, and checks Python syntax without creating bytecode. Unit tests
exercise the small postlink tool's refusal paths. They do not demonstrate a ROM
boot or certify runtime behavior.

## Research recipes

`Symbian/scripts/phase4-build-htcleo-native-bsp.sh` and
`Symbian/scripts/phase4-build-htcleo-full-rom.sh` preserve research build history.
Their resolvable local source-transform dependencies are included where safe.
`docs/RECIPE-DEPENDENCIES.json` lists the selected recipes and omitted/unresolved
references; it is not a claim that all external SDK dependencies are present.

The recipes still refer to lab SDK staging layouts such as `/root/symbian`,
`/root/symbian3-full`, `/root/symbian-oss`, and `/root/gcce-native-4.4.1`.
The original workstation checkout path is generalized to `/path/to/hd2-legacy-lab`.
Review/adapt those paths to a disposable workspace before any build. Never run
the recipes against an only copy of a working SDK. Some historical recipes
mutate SDK staging files; copying source is not authorization to deploy their output.

Known export gaps include the explicitly withheld QDSP/common HAL modules,
SDK-specific generated source/objects, licensed release dependencies, build caches,
ROM/resource material, and the complete historical packaging chain. SD writers,
collectors, package assemblers and private backup tools are excluded intentionally.
No one-command hardware deployment is provided.

## Hardware contracts that must not be guessed

- Physical/runtime ROM base: `0x12200000`. Full-ROM layout matters; do not reuse
  absolute addresses from early Mini ROM experiments.
- RGB565 panel: 480 x 800; the working display path is not evidence of a complete
  accelerated GPU driver.
- Kernel interrupt-handler signatures and return values are part of the ABI.
- Match exports/import ordinals to the exact SDK and ROM, not just a filename.
- Preserve verified SD data, filesystem metadata, code-signature/hash receipts,
  and identity-bound deployment checks in any separate deployment tool.
- Do not remove logging/timers merely to tidy source: some removals historically
  changed timing. 1035 removes pixel stores only, not the timer or log producers.

## When rebuilding the touch module

The ordinary debug-row source is intentionally preserved as the reviewed source
snapshot. 1035 used a separately audited postlink retirement of 20 pixel stores.
Recompilation changes layout and invalidates fixed offsets. Re-audit symbols,
callers and the fatal path, then perform a new guarded retirement. The bundled
`tools/retire-life-glyph-1035.py` accepts **one exact historical E32 hash only**;
it is not a generic patcher and refuses freshly different builds.
