# Symbian for HTC HD2

An experimental **Symbian^3 / EKA2 port for the HTC HD2 (HTC Leo, QSD8250)**.
This is real Symbian running on the device, not an Android theme or an emulator.

**First public source snapshot, aligned with the personal Beta 1 / iteration 1035
milestone (2026-09-30).** This is a curated port-source and research-recipe release,
not the complete Symbian SDK, a ready-to-flash ROM, or a self-contained reproducible
1035 build. See [build boundaries](docs/BUILDING.md) before using any recipe.

## What has been observed on hardware

| Area | Status |
| --- | --- |
| MAGLDR SD boot to full S60/Avkon Home and MatrixMenu | Working on HD2; the 1034 baseline also booted on a second HD2 |
| SD-backed C: data, touch, application menu | Working in tested workflows; 33 Games entries visible and scrollable |
| Windows key | Home/Menu switching; long press opens the task switcher |
| Back key | Screen off/on; fixed wake brightness accepted |
| About phone | Readable black-background information view accepted |
| Ordinary colored debug row | Removed in 1035; separate system-fatal red display retained |
| Java games | Some playable; compatibility is incomplete, not all 33 games work |
| UNO Spin | 1035 landscape correction accepted by the tester |
| GT Racing 2 | Same metadata correction prepared; **not retested in 1035** |

These are user-observed milestones, not exhaustive reliability guarantees. Ongoing
repeated-reboot and long-term tests on the second device are not a completed pass.
See [status and limitations](docs/STATUS.md).

## What is here

- QSD8250/HTC Leo EKA2 BSP source, including bootstrap, interrupt/timer, display,
  SDCC, touch/key and diagnostic integration.
- Selected Home/Avkon/About/backlight/Java compatibility helpers and build metadata.
- Symbian adaptation patches and historical source-transformation/build recipes.
- MAGLDR handoff bridge source (not the MAGLDR bootloader).
- A hash-locked example of the 1035 normal-glyph postlink retirement, and the
  explanation of the JAD-only landscape correction.

The `Symbian/` layout keeps the original source relationships. Numbered helpers
and diagnostic patches include research history: their presence does **not** mean
every probe is active in Beta 1. Do not apply all patches indiscriminately.

## What is deliberately not here

No ROM image, PDK/SDK binaries, compiler, proprietary JVM, commercial JAR/SIS games,
game icons, extracted Nokia/Ovi artwork, wallpaper, personal SD contents, runtime
logs, credentials, card identifiers, private backups, or unrelated OS project history.

Two Linux-reference adaptation areas (the QDSP audio implementation and common
`qsd8k_hal.cpp` hardware primitives) are withheld from this first source snapshot
pending a separate provenance/license review. No placeholder is provided. This
is one concrete reason this export cannot build the complete device image alone.

The personal Beta 1 runtime ZIP is **not** a public GitHub release asset. It contains
separately obtained dependencies and games not licensed by this repository.

## Getting started

1. Read [BUILDING.md](docs/BUILDING.md) for external prerequisites and the distinction
   between source checks, component builds and a complete ROM.
2. Read [PROVENANCE.md](docs/PROVENANCE.md) and the preserved file headers.
3. Run the non-device source check: `python3 tools/check-source-tree.py`.
4. Consult [1035 changes](docs/1035-CHANGES.md) before rebuilding the touch module.

Nothing in the supported source check flashes a device, writes an SD card, or starts
hardware tests. Historical recipes are not an unattended build/install interface.
Use a spare, backed-up device and card for development.

## 繁體中文摘要

這是 HTC HD2 的真正 Symbian^3 / EKA2 移植原始碼首發。Beta 1 已有可操作的
Home、MatrixMenu、觸控與實體 Home/Menu、熄／亮螢幕，以及部分 Java 遊戲。
1035 已移除正常畫面頂端四色字樣，保留系統級 crash 紅碼；UNO Spin 橫向已驗收，
GT Racing 2 本次未測。正常關機、完整 Settings、網路／音訊及全部遊戲相容性
並未完成。此 repo 不含 ROM、商業遊戲、SDK/JVM 二進位或手機 log，也不是
clone 後就能一鍵重建完整1035的套件。既有可回退備份與此公開 source 分開管理。
