# Source provenance and redistribution boundary

This repository contains a curated snapshot from an experimental HTC Leo port,
not the entire original lab tree or its Git history. Original copyright notices
are preserved. The port is unofficial and is not endorsed by Nokia, HTC,
Qualcomm, the former Symbian Foundation, or the game publishers.

## Symbian upstream

Primary upstream references:

- [SymbianSource EKA2/kernelhwsrv](https://github.com/SymbianSource/oss.FCL.sf.os.kernelhwsrv)
- [SymbianSource Qemu/Syborg adaptation](https://github.com/SymbianSource/oss.FCL.sf.adapt.Qemu)
- [SymbianSource classicui](https://github.com/SymbianSource/oss.FCL.sf.mw.classicui)
- [SymbianSource Java runtime framework](https://github.com/SymbianSource/oss.FCL.sf.app.JRT)

The checked local source references were kernelhwsrv `BRANCH_GCC_SURGE`
`e0036b02d8a5b370c89e7d4245d856de365e330a`, Qemu GCC tree
`59747f31a442657782b1c58682c9a9e20fe9c495`, and classicui
`dcea899751dfa099dcca7a5508cf32eab64afa7a`. These are provenance anchors, not a
promise that checking out these three commits recreates all SDK staging inputs.

Nokia/Symbian-derived files retain their Eclipse Public License 1.0 notices.
The unmodified license text is included under `LICENSES/EPL-1.0.html`, from the
[Eclipse Foundation](https://www.eclipse.org/legal/epl/epl-v10.html).
Consult the root license notice for the treatment of newly authored port code.

## HTC/Linux hardware references

The project consulted HTC Leo Linux board and QSD8x50 register/protocol definitions.
Those references have their own licenses; a numeric hardware contract is not a
license grant for another project's implementation. The original Linux repository
is not vendored here. For this initial snapshot, `sound/**` and
`specific/qsd8k_hal.cpp` are withheld pending a separate provenance/license review
instead of silently relabeling Linux-derived material. The remaining comments
identifying hardware-reference paths are preserved.

## Excluded distribution material

PDK release binaries, SDK tools, proprietary JVM code, firmware, commercial game
JAR/SIS packages, extracted icons and Nokia/Ovi artwork are not covered by this
repository's license and are not included. Neither are personal SD images,
runtime logs, device IDs, account credentials or unrelated Android/Maemo/XNU work.

`SOURCE-MANIFEST.sha256` describes this public snapshot. Local archival evidence
and the private runtime Beta 1 ZIP are separate and are not uploaded as releases.
