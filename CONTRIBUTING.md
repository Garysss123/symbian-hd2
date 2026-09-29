# Contributing to the experimental port

This is an early public source snapshot, not a supported flashing distribution.
Start with a focused issue describing the device, exact build, reproduction steps,
and what was actually observed. A photograph or a short redacted diagnostic can
be useful; do not upload full phone logs, personal SD data, credentials or games.

Keep one behavioral change per experiment. Preserve the latest known working
baseline, note which module and dependency changed, and distinguish host checks
from real-device results. Never call a build-only result a hardware pass.

Do not remove the fatal red diagnostic or the remaining timer/log producers for
cosmetic cleanup. Probe retirement needs same-build symbol/byte review. Likewise,
do not globally rotate every Java game because two JADs had incorrect metadata.

Before submitting code, state its source and license and retain upstream notices.
Do not submit proprietary SDK/JVM binaries, firmware, ROMs, game packages or ripped
artwork. A review of the initially withheld hardware reference modules would need
separate source/provenance evidence, not a blanket license header change.
