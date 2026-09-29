#!/usr/bin/env python3
"""Install and verify the iteration-361 pre-ESTART location reporters.

The kernel tree is persistent between builds, so this transformer is deliberately
idempotent and fails closed on any partially matching or unexpected source.
"""

from __future__ import annotations

import pathlib
import sys


MARKER = "HTCLEO_EXTENSION_PROGRESS_LOCATION_PROBE"


REPORTER = r'''
#if defined(__CPU_QSD8250__) && defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)
/* HTCLEO_EXTENSION_PROGRESS_LOCATION_PROBE
 *
 * One returning reporter shared by every pre-ESTART extension boundary.
 * The top row is the actual runtime entry point.  The bottom row is:
 *   A00000nn  VariantInit0/data pass
 *   B00000nn  ExtensionInit0 pass
 *   C00000nn  ExtensionInit1 pass
 * The last completed paint remains visible if the following entry never
 * returns.  No iteration identifier is embedded in the ROM.
 */
static void HtcleoDrawExtensionProgressHexRow(volatile TUint16* aFb,
                                               TUint32 aValue,
                                               TUint aStartY)
	{
	const TUint KWidth = 480;
	const TUint KStartX = 48;
	const TUint16 KYellow = 0xffe0;
	for (TUint digit = 0; digit < 8; ++digit)
		{
		const TUint nibble = (aValue >> ((7 - digit) * 4)) & 0x0fu;
		const TBool segA = nibble == 0 || nibble == 2 || nibble == 3 || nibble == 5 ||
			nibble == 6 || nibble == 7 || nibble == 8 || nibble == 9 ||
			nibble == 10 || nibble == 12 || nibble == 14 || nibble == 15;
		const TBool segB = nibble == 0 || nibble == 1 || nibble == 2 || nibble == 3 ||
			nibble == 4 || nibble == 7 || nibble == 8 || nibble == 9 || nibble == 10;
		const TBool segC = nibble == 0 || nibble == 1 || nibble == 3 || nibble == 4 ||
			nibble == 5 || nibble == 6 || nibble == 7 || nibble == 8 ||
			nibble == 9 || nibble == 10 || nibble == 11 || nibble == 13;
		const TBool segD = nibble == 0 || nibble == 2 || nibble == 3 || nibble == 5 ||
			nibble == 6 || nibble == 8 || nibble == 9 || nibble == 11 ||
			nibble == 12 || nibble == 13 || nibble == 14;
		const TBool segE = nibble == 0 || nibble == 2 || nibble == 6 || nibble == 8 ||
			nibble == 10 || nibble == 11 || nibble == 12 || nibble == 13 ||
			nibble == 14 || nibble == 15;
		const TBool segF = nibble == 0 || nibble == 4 || nibble == 5 || nibble == 6 ||
			nibble == 8 || nibble == 9 || nibble == 10 || nibble == 11 ||
			nibble == 12 || nibble == 14 || nibble == 15;
		const TBool segG = nibble == 2 || nibble == 3 || nibble == 4 || nibble == 5 ||
			nibble == 6 || nibble == 8 || nibble == 9 || nibble == 10 ||
			nibble == 11 || nibble == 13 || nibble == 14 || nibble == 15;
		for (TUint py = 0; py < 112; ++py)
			{
			for (TUint px = 0; px < 42; ++px)
				{
				const TBool lit =
					(segA && py < 8 && px >= 7 && px < 35) ||
					(segB && px >= 34 && px < 42 && py >= 7 && py < 56) ||
					(segC && px >= 34 && px < 42 && py >= 56 && py < 105) ||
					(segD && py >= 104 && px >= 7 && px < 35) ||
					(segE && px < 8 && py >= 56 && py < 105) ||
					(segF && px < 8 && py >= 7 && py < 56) ||
					(segG && py >= 52 && py < 60 && px >= 7 && px < 35);
				if (lit)
					aFb[(aStartY + py) * KWidth + KStartX + digit * 48 + px] = KYellow;
				}
			}
		}
	}

static void HtcleoExtensionProgressLocationScreenProbe(TUint32 aEntry,
                                                        TUint32 aStage)
	{
	const TUint KWidth = 480;
	const TUint KHeight = 800;
	const TUint16 KWhite = 0xffff;
	const TUint16 KDarkBlue = 0x0010;
	const TUint16 KDarkGreen = 0x0200;
	const TUint16 KDarkPurple = 0x4008;
	TUint16 background = KDarkPurple;
	if ((aStage & 0xf0000000u) == 0xa0000000u)
		background = KDarkBlue;
	else if ((aStage & 0xf0000000u) == 0xb0000000u)
		background = KDarkGreen;
	volatile TUint16* const fb = (volatile TUint16*)0xc6400000u;
	for (TUint y = 0; y < KHeight; ++y)
		for (TUint x = 0; x < KWidth; ++x)
			fb[y * KWidth + x] =
				(x < 8 || x >= KWidth - 8 || y < 8 || y >= KHeight - 8 ||
				 (y >= 396 && y < 404)) ? KWhite : background;
	HtcleoDrawExtensionProgressHexRow(fb, aEntry, 176);
	HtcleoDrawExtensionProgressHexRow(fb, aStage, 512);
	__e32_io_completion_barrier();
	}
#endif
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def install_putils(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER not in text:
        text = replace_once(
            text,
            '\nvoid PP::Panic(TPlatPanic aPanic)\n',
            REPORTER + '\nvoid PP::Panic(TPlatPanic aPanic)\n',
            "putils reporter insertion",
        )
        text = replace_once(
            text,
            '\t__KTRACE_OPT(KBOOT,Kern::Printf("Calling entrypoint %08x(VariantInit0)", ep));\n'
            '\tTInt r = ep(KModuleEntryReasonVariantInit0);\n',
            '\t__KTRACE_OPT(KBOOT,Kern::Printf("Calling entrypoint %08x(VariantInit0)", ep));\n'
            '#if defined(__CPU_QSD8250__) && defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n'
            '\tHtcleoExtensionProgressLocationScreenProbe((TUint32)ep,\n'
            '\t\t0xa0000000u | (TUint32(K::ExtensionCount) & 0x00ffffffu));\n'
            '#endif\n'
            '\tTInt r = ep(KModuleEntryReasonVariantInit0);\n',
            "VariantInit0 call boundary",
        )
        text = replace_once(
            text,
            '\t__KTRACE_OPT(KBOOT,Kern::Printf("InitExt0 %08x ep=%08x", &a, ep));\n'
            '\tTInt r = (*ep)(KModuleEntryReasonExtensionInit0);\n',
            '\t__KTRACE_OPT(KBOOT,Kern::Printf("InitExt0 %08x ep=%08x", &a, ep));\n'
            '#if defined(__CPU_QSD8250__) && defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n'
            '\tHtcleoExtensionProgressLocationScreenProbe((TUint32)ep,\n'
            '\t\t0xb0000000u | (TUint32(K::ExtensionArray->Count()) & 0x00ffffffu));\n'
            '#endif\n'
            '\tTInt r = (*ep)(KModuleEntryReasonExtensionInit0);\n',
            "ExtensionInit0 call boundary",
        )
        text = replace_once(
            text,
            '\t\t__KTRACE_OPT(KBOOT,Kern::Printf("InitExt1: calling entrypoint %08x", ep));\n'
            '\t\tTInt r = ep(KModuleEntryReasonExtensionInit1);\n',
            '\t\t__KTRACE_OPT(KBOOT,Kern::Printf("InitExt1: calling entrypoint %08x", ep));\n'
            '#if defined(__CPU_QSD8250__) && defined(__HTCLEO_LOW_ROM_PD_FIX_PROBE__)\n'
            '\t\tHtcleoExtensionProgressLocationScreenProbe((TUint32)ep,\n'
            '\t\t\t0xc0000000u | (TUint32(i) & 0x00ffffffu));\n'
            '#endif\n'
            '\t\tTInt r = ep(KModuleEntryReasonExtensionInit1);\n',
            "ExtensionInit1 call boundary",
        )
        path.write_text(text, encoding="utf-8")

    checks = {
        MARKER: 1,
        "HtcleoExtensionProgressLocationScreenProbe(": 4,
        "0xa0000000u |": 1,
        "0xb0000000u |": 1,
        "0xc0000000u |": 1,
    }
    text = path.read_text(encoding="utf-8")
    for token, expected in checks.items():
        actual = text.count(token)
        if actual != expected:
            raise SystemExit(
                f"putils verification failed for {token!r}: {actual} != {expected}"
            )


def install_estart(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    old = 'asm volatile("mov r0,#0\\n\\t.word 0xe7f000f0"'
    new = (
        '// In ARM state, PC reads as this SUB address + 8; subtracting 4 yields\n'
        '\t// the address of the immediately following UDF word exactly.\n'
        '\tasm volatile("sub r0,pc,#4\\n\\t.word 0xe7f000f0"'
    )
    if old in text:
        text = replace_once(text, old, new, "ESTART runtime-location UDF")
        path.write_text(text, encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    if text.count('sub r0,pc,#4\\n\\t.word 0xe7f000f0') != 1:
        raise SystemExit("ESTART exact runtime-location UDF is absent or duplicated")
    if text.count("0xe7f000f0") != 1 or "mov r0,#0" in text:
        raise SystemExit("ESTART still contains a stale or duplicate screen UDF")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-htcleo-extension-progress-probes.py KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    install_putils(root / "kernel/eka/memmodel/epoc/putils.cpp")
    install_estart(
        root / "userlibandfileserver/fileserver/estart/estartmain.cpp"
    )
    print("HTCLEO_EXTENSION_PROGRESS_LOCATION_PROBES=OK")


if __name__ == "__main__":
    main()
