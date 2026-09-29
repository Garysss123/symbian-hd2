#!/usr/bin/env python3
"""Restore the shared Avkon re-arm to the proven focus-entry placement."""
from __future__ import annotations

import argparse
from pathlib import Path


V1 = "HTCLEO_AVKON_FOCUS_TOUCH_REARM_V1"
V2 = "HTCLEO_AVKON_POST_FOCUS_TOUCH_REARM_V2"

ENTRY_BLOCK = '''            // HTCLEO_AVKON_FOCUS_TOUCH_REARM_V1
            // HTC Leo TYPE_2A stops asserting new reports after a foreground
            // owner transition. Queue a coalesced request only; HAL10 performs
            // no I2C and the native polling DFC remains the sole bus owner.
            const TInt htcleoRearmBefore = UserSvr::HalFunction(
                EHalGroupPlatformSpecific2, 11, 0, 0);
            const TInt htcleoRearmRequestResult = UserSvr::HalFunction(
                EHalGroupPlatformSpecific2, 10, 0, 0);
            const TInt htcleoRearmAfter = UserSvr::HalFunction(
                EHalGroupPlatformSpecific2, 11, 0, 0);
            if (htcleoHomeFocusTrace)
                HtcleoAknAppUiBaseLog(0x0000C594u,
                    htcleoRearmRequestResult,
                    ((TUint32)(htcleoRearmBefore & 0xffff) << 16) |
                    (TUint32)(htcleoRearmAfter & 0xffff));
'''


def patch(text: str) -> str:
    if V1 in text:
        verify(text)
        return text
    if text.count(V2) != 1:
        raise SystemExit("Avkon post-focus predecessor missing or duplicated")
    start = text.index("            // " + V2)
    end = text.index("            break;", start)
    text = text[:start] + text[end:]
    anchor = (
        "        case EEventFocusGained:\n"
        "            {\n"
        "            if (htcleoHomeFocusTrace)\n"
    )
    if text.count(anchor) != 1:
        raise SystemExit("Avkon focus-entry anchor missing or duplicated")
    text = text.replace(
        anchor,
        "        case EEventFocusGained:\n"
        "            {\n" + ENTRY_BLOCK
        + "            if (htcleoHomeFocusTrace)\n",
        1,
    )
    verify(text)
    return text


def verify(text: str) -> None:
    if text.count(V1) != 1 or V2 in text:
        raise SystemExit("Avkon focus-entry re-arm marker mismatch")
    if text.count("#include <e32svr.h>") != 1 or text.count("#include <u32hal.h>") != 1:
        raise SystemExit("Avkon HAL headers missing or duplicated")
    focus_start = text.index("        case EEventFocusGained:")
    start = text.index("            // " + V1, focus_start)
    c568 = text.index("0x0000C568u", start)
    body = text[start:c568]
    if body.count("UserSvr::HalFunction") != 3:
        raise SystemExit("Avkon entry re-arm must use exactly three HAL calls")
    for token in (
        "EHalGroupPlatformSpecific2, 10", "EHalGroupPlatformSpecific2, 11",
        "0x0000C594u", "htcleoRearmRequestResult",
    ):
        if token not in body:
            raise SystemExit("Avkon focus-entry re-arm operation incomplete")
    for forbidden in (
        "HtcleoI2c", "ResetAndDetect", "User::After", "RTimer",
        "WaitForRequest", "LeaveIfError", "RequestComplete", "SetOrdinal",
        "DrawNow", "Finish()",
    ):
        if forbidden in body:
            raise SystemExit("Avkon entry re-arm expanded beyond async HAL request")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = args.root / "sf/mw/classicui/uifw/AvKon/src/AknAppUi.cpp"
    text = patch(path.read_text(encoding="latin-1"))
    if patch(text) != text:
        raise SystemExit("Avkon focus-entry re-arm is not idempotent")
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_AVKON_FOCUS_TOUCH_REARM="
        "shared-all-avkon-focusgained-hal10-async-failopen-c594"
    )


if __name__ == "__main__":
    main()
