# Symbian for HTC HD2

An experimental **Symbian^3 / EKA2 port for the HTC HD2 (HTC Leo, QSD8250)**.
This is real Symbian running on the device, not an Android theme or an emulator.

**Public source snapshot for Beta 1.** This is a curated port-source and research-recipe release,
not the complete Symbian SDK, a ready-to-flash ROM, or a self-contained reproducible
system build. See [build boundaries](docs/BUILDING.md) before using any recipe.

## What has been observed on hardware

| Area | Status |
| --- | --- |
| MAGLDR SD boot to full S60/Avkon Home and MatrixMenu | Working on tested HD2 hardware |
| SD-backed C: data, touch, application menu | Working in tested workflows, with a scrollable application menu |
| Windows key | Home/Menu switching; long press opens the task switcher |
| Back key | Screen off/on with fixed wake brightness |
| About phone | Readable black-background information view |
| Ordinary colored debug row | Hidden during normal use; separate system-fatal red display retained |
| J2ME games | Multiple games tested and confirmed playable |

These observations cover tested workflows, not exhaustive reliability guarantees.
Game compatibility varies by title, and long-term stability testing is ongoing.
See [status and limitations](docs/STATUS.md).

## What is here

- QSD8250/HTC Leo EKA2 BSP source, including bootstrap, interrupt/timer, display,
  SDCC, touch/key and diagnostic integration.
- Selected Home/Avkon/About/backlight/Java compatibility helpers and build metadata.
- Symbian adaptation patches and historical source-transformation/build recipes.
- MAGLDR handoff bridge source (not the MAGLDR bootloader).
- A hash-locked example of removing the normal debug overlay, and notes on
  JAD-based screen orientation.

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
4. Consult the [display and orientation notes](docs/1035-CHANGES.md) before rebuilding the touch module.

Nothing in the supported source check flashes a device, writes an SD card, or starts
hardware tests. Historical recipes are not an unattended build/install interface.
Use a spare, backed-up device and card for development.

## 繁體中文摘要

這是 HTC HD2 的真正 Symbian^3 / EKA2 移植原始碼首發。Beta 1 已有可操作的
Home、MatrixMenu、觸控、實體 Home/Menu 鍵與熄／亮螢幕功能。
J2ME 已實測多款遊戲可正常遊玩。正常畫面頂端四色除錯文字已移除，保留系統級
crash 紅碼。正常關機、完整 Settings、網路／音訊及全部遊戲相容性
並未完成。此 repo 不含 ROM、商業遊戲、SDK/JVM 二進位或手機 log，也不是
clone 後就能一鍵重建完整系統的套件。既有可回退備份與此公開 source 分開管理。
