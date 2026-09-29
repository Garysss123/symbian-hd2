#!/usr/bin/env python3
"""Let WServ accept the already-working HTCLEO Type2A raw pointer events."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_WSERV_TYPE2A_POINTER_ENABLE_V1"

INCLUDE_ANCHOR = '#include <e32hal.h>\n'
INCLUDES = '#include <e32hal.h>\n#include <e32svr.h>\n#include <u32hal.h>\n'

LOGGER_ANCHOR = 'TTimeIntervalMicroSeconds32 TWsPointer::iDoubleClickMaxInterval;\n'
LOGGER_BLOCK = (
    'extern void HtcleoWsLog(TUint32 aStage, TInt aResult, '
    'TUint32 aDetail);\n\n'
    + LOGGER_ANCHOR
)

INIT_ANCHOR = r'''	TMachineInfoV1Buf machineInfo;
	UserHal::MachineInfo(machineInfo);
	iXyInputType=machineInfo().iXYInputType;
	
'''

INIT_BLOCK = r'''	TMachineInfoV1Buf machineInfo;
	UserHal::MachineInfo(machineInfo);
	iXyInputType=machineInfo().iXYInputType;

	// HTCLEO_WSERV_TYPE2A_POINTER_ENABLE_V1
	// The native Type2A extension is loaded before WServ and already reports
	// successful real samples through its diagnostic HAL.  Some legacy PDK
	// machine metadata still says EXYInputNone, which makes WServ discard every
	// otherwise valid raw pointer event in PreProcessDriverEvent().  Correct
	// only that stale metadata case; other machines and input types stay stock.
	const TXYInputType htcleoReportedInputType = iXyInputType;
	TInt htcleoTouchStage = KErrNotFound;
	if (iXyInputType == EXYInputNone)
		{
		htcleoTouchStage = UserSvr::HalFunction(
			EHalGroupPlatformSpecific2, 0, 0, 0);
		if ((static_cast<TUint32>(htcleoTouchStage) & 0xff000000u) ==
			0x54000000u)
			{
			iXyInputType = EXYInputPointer;
			}
		}
	HtcleoWsLog(0x00000450u, static_cast<TInt>(htcleoReportedInputType),
		static_cast<TUint32>(htcleoTouchStage));
	HtcleoWsLog(0x00000451u, static_cast<TInt>(iXyInputType),
		static_cast<TUint32>(htcleoTouchStage));
	
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    if text.count(INCLUDE_ANCHOR) != 1:
        raise SystemExit("WServ Type2A include anchor missing or duplicated")
    if text.count(LOGGER_ANCHOR) != 1:
        raise SystemExit("WServ Type2A logger anchor missing or duplicated")
    if text.count(INIT_ANCHOR) != 1:
        raise SystemExit("WServ Type2A machine-info anchor missing or duplicated")
    text = text.replace(INCLUDE_ANCHOR, INCLUDES, 1)
    text = text.replace(LOGGER_ANCHOR, LOGGER_BLOCK, 1)
    return text.replace(INIT_ANCHOR, INIT_BLOCK, 1)


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "includes": (
            text.count("#include <e32svr.h>") == 1
            and text.count("#include <u32hal.h>") == 1
        ),
        "scope": (
            text.count("iXyInputType == EXYInputNone") == 1
            and text.count("iXyInputType = EXYInputPointer") == 1
        ),
        "real Type2A gate": (
            text.count("EHalGroupPlatformSpecific2, 0, 0, 0") == 1
            and text.count("0x54000000u") == 1
        ),
        "traces": (
            text.count("0x00000450u") == 1
            and text.count("0x00000451u") == 1
        ),
        "stock drop retained": text.count("if (!XyInput())") == 1,
        "no fabricated event or wait": all(
            token not in INIT_BLOCK
            for token in ("Kern::AddEvent", "event.Set", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "WServ Type2A pointer-enable verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    source = (
        args.root
        / "sf/os/graphics/windowing/windowserver/nga/SERVER/POINTER.CPP"
    )
    text = source.read_text(encoding="latin-1")
    text = install(text)
    verify(text)
    source.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_WSERV_TYPE2A_POINTER_ENABLE="
        "stale-none-to-pointer-only-with-live-type2a-hal-traced-0450-0451"
    )


if __name__ == "__main__":
    main()
