#!/usr/bin/env python3
"""Request a bounded Type2A controller re-arm when Matrix regains focus."""
from __future__ import annotations

import argparse
from pathlib import Path

V2 = "HTCLEO_MATRIXMENU_REDUNDANT_FOCUS_FASTPATH_V2"
V3 = "HTCLEO_MATRIXMENU_FOCUS_CHROME_ACTIVATION_V3"
MARKER = "HTCLEO_MATRIXMENU_FOCUS_TOUCH_REARM_V4"

BLOCK = r'''    // HTCLEO_MATRIXMENU_FOCUS_TOUCH_REARM_V4
    // 748/749 keep polling valid Type2A packets after focus3 but generate no
    // new points/events. Queue only a re-arm request here; the kernel HAL does
    // no I2C and its existing polling DFC remains the sole controller owner.
    if ( type == EEventFocusGained && htcleoRuntimeState == 0x0Fu )
        {
        iHasFocus = ETrue;
        const TInt before = UserSvr::HalFunction(
            EHalGroupPlatformSpecific2, 11, 0, 0);
        const TInt requestResult = UserSvr::HalFunction(
            EHalGroupPlatformSpecific2, 10, 0, 0);
        const TInt after = UserSvr::HalFunction(
            EHalGroupPlatformSpecific2, 11, 0, 0);
        HtcleoMenuLog(0x4D4D1268u, requestResult,
            ((TUint32)(before & 0xffff) << 16) |
            (TUint32)(after & 0xffff));
        return;
        }'''

OLD_HEARTBEAT = (
    "    HtcleoMenuLog(0x4D4D01FFu, (TInt)state, "
    "0x414C4956u); // ALIV"
)
NEW_HEARTBEAT = r'''    // Report re-arm completion in the existing low-rate heartbeat;
    // 0x52 RR CC EE = request, completion, signed result low byte.
    const TInt rearmRequest = UserSvr::HalFunction(
        EHalGroupPlatformSpecific2, 11, 0, 0);
    const TInt rearmComplete = UserSvr::HalFunction(
        EHalGroupPlatformSpecific2, 12, 0, 0);
    const TInt rearmResult = UserSvr::HalFunction(
        EHalGroupPlatformSpecific2, 13, 0, 0);
    const TUint32 heartbeatDetail = rearmRequest > 0 ?
        0x52000000u |
        ((TUint32)(rearmRequest & 0xff) << 16) |
        ((TUint32)(rearmComplete & 0xff) << 8) |
        (TUint32)(rearmResult & 0xff) : 0x414C4956u;
    HtcleoMenuLog(0x4D4D01FFu, (TInt)state, heartbeatDetail);'''


def patch(text: str) -> str:
    if MARKER not in text:
        marker = V3 if V3 in text else V2 if V2 in text else None
        if not marker:
            raise SystemExit("Matrix focus predecessor V2/V3 missing")
        start = text.index("    // " + marker)
        end = text.index(
            "\n\n    // HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1", start
        )
        text = text[:start] + BLOCK + text[end:]
    if "#include <e32svr.h>" not in text:
        text = text.replace(
            "#include <e32cmn.h>\n",
            "#include <e32cmn.h>\n#include <e32svr.h>\n#include <u32hal.h>\n",
            1,
        )
    if OLD_HEARTBEAT in text:
        if text.count(OLD_HEARTBEAT) != 1:
            raise SystemExit("Matrix heartbeat anchor duplicated")
        text = text.replace(OLD_HEARTBEAT, NEW_HEARTBEAT, 1)
    verify(text)
    return text


def verify(text: str) -> None:
    if text.count(MARKER) != 1 or V2 in text or V3 in text:
        raise SystemExit("Matrix focus re-arm marker mismatch")
    start = text.index("    // " + MARKER)
    end = text.index(
        "\n\n    // HTCLEO_MATRIXMENU_FOCUS_RESTORE_ATTRIBUTION_V1", start
    )
    body = text[start:end]
    for token in (
        "type == EEventFocusGained && htcleoRuntimeState == 0x0Fu",
        "iHasFocus = ETrue;", "EHalGroupPlatformSpecific2, 10",
        "EHalGroupPlatformSpecific2, 11", "0x4D4D1268u", "return;",
    ):
        if token not in body:
            raise SystemExit("Matrix focus re-arm operation missing")
    for forbidden in (
        "RefreshUiPanesL", "MakeVisible", "DrawNow", "Finish",
        "SetOrdinal", "HandleFocusGainedL", "User::After", "RTimer",
        "RequestComplete", "HtcleoI2c", "RefreshIconsL",
    ):
        if forbidden in body:
            raise SystemExit("Matrix focus re-arm expanded beyond HAL request")
    if text.count(NEW_HEARTBEAT) != 1 or OLD_HEARTBEAT in text:
        raise SystemExit("Matrix re-arm heartbeat evidence missing")
    if text.count("#include <e32svr.h>") != 1 or text.count("#include <u32hal.h>") != 1:
        raise SystemExit("Matrix HAL headers missing/duplicated")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    text = patch(path.read_text(encoding="latin-1"))
    if patch(text) != text:
        raise SystemExit("Matrix focus re-arm is not idempotent")
    path.write_text(text, encoding="latin-1")
    print("HTCLEO_MATRIX_FOCUS_TOUCH_REARM=async-hal10-dfc-owned-d0-00-01-heartbeat-52rrccee")


if __name__ == "__main__":
    main()
