# Beta 1 status — 2026-09-30

The tested target is HTC HD2/Leo with MAGLDR SD boot and a full Symbian^3 / EKA2
userspace. This source release documents iteration 1035, whose ROM was built from
1034 without relocating the full image: only 20 normal-glyph instructions and the
required ROM header checksum changed. Games received two JAD metadata updates.

## Accepted observations

- Home/MatrixMenu UI, classic grass Home wallpaper and separate menu background.
- Menu registration/scrolling with 33 Games entries; app visibility is not gameplay.
- About information: readable dark background and native CBA.
- Physical Windows key Home/Menu/long-press switcher, and Back-key screen off/on.
- Fixed wake brightness (perceived slightly brighter than boot, accepted).
- Ordinary colored top-row text absent in 1035; UNO Spin landscape normal.
- A separate HD2 booted the 1034 Beta 1 baseline. Its long-term tests continue.

Previously accepted playable games include Asphalt 6, Climate Mission, Plants vs.
Zombies, Asphalt 4 and Angry Birds Seasons 2; UNO Spin is now added. These tests do
not establish save/load, sound, exit, every level or indefinite stability.

## Open / partial

- GT Racing 2's landscape JAD correction was not retested in 1035.
- Normal shutdown is unfinished and paused. Power-button support is not a safe
  shutdown claim. Do not rely on it to flush application state.
- Settings is partial: status/CBA proportions improved but content remains white.
- Task switcher behavior/close controls and some UI return latency remain imperfect.
- Many Java titles still fail or hang; original Angry Birds/Space level loading,
  Doodle Jump loading, some crashes and language variants remain unresolved.
- Complete networking/Wi-Fi, audio, modem/phone, camera and sensors are not claimed.
- Long-term/repeated-reboot stability is being evaluated, not certified.
- X-plore and Qt widgets are outside the required archival scope.

The fatal red panel remains a system-crash diagnostic, not a normal shutdown screen.
No intentional fatal crash was induced just to re-prove it after 1035. Its code was
preserved and audited separately from the normal liveness glyph renderer.
