#!/usr/bin/env python3
"""Preserve composed HTC Leo UI across the scheduler-entry root blank layer.

Hardware 589-593 proves the CPU fallback copies individual render-target
updates faithfully, but it does not perform OpenWFC z-composition.  At
MatrixMenu scheduler entry the final all-white root-layer update is therefore
copied over the already visible status and icon layers.  Hardware 594 proves
the one-rect 360x640 signature; hardware 602 proves a two-rect 480x800 scaled
root and hardware 603 proves status-pane scaling can coalesce that root to one
480x800 rect.  Suppress only those exact signatures.  All nonblank, partial,
non-MatrixMenu and later updates remain real.
"""

from __future__ import annotations

import argparse
from pathlib import Path


V1_MARKER = "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V1"
V2_MARKER = "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V2"
MARKER = "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V3"

ANCHOR = r'''        result = KErrNone;
        if (htcleoRectCount > 0)
            {'''

REPLACEMENT = r'''        // HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD_V3
        TUint32 htcleoDestinationBeforeHash = 0u;
        TUint32 htcleoDestinationBeforeNonWhite = 0u;
        HtcleoSparseFrameSignature(
            static_cast<const TUint8*>(screenInfo.iScreenAddress),
            480 * 800 * 2,
            htcleoDestinationBeforeHash,
            htcleoDestinationBeforeNonWhite);
        const TBool htcleoLegacySchedulerRoot =
            htcleoRectCount == 1
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(360, 640);
        const TBool htcleoScaledSchedulerRoot =
            (htcleoRectCount == 1 || htcleoRectCount == 2)
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(480, 800);
        const TBool htcleoRetireSchedulerBlankLayer =
            htcleoUiStageResult == KErrNone
            && (TUint32)htcleoUiStage == 0x4D4D1013u
            && htcleoSourceNonWhite == 0u
            && htcleoDestinationBeforeNonWhite > 0u
            && (htcleoLegacySchedulerRoot || htcleoScaledSchedulerRoot);
        HtcleoDsprLog(0x00001934u,
            htcleoRetireSchedulerBlankLayer ? 1 : 0,
            htcleoDestinationBeforeNonWhite);

        result = KErrNone;
        if (htcleoRetireSchedulerBlankLayer)
            {
            // Preserve the already accumulated real UI layers.
            }
        else if (htcleoRectCount > 0)
            {'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/os/graphics/windowing/windowserverplugins/openwfc"
        / "src/displayrenderstage.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing display render stage: {path}")
    text = path.read_text(encoding="utf-8")
    if V1_MARKER in text:
        text = text.replace(V1_MARKER, MARKER, 1)
        old_bounds = r'''        const TBool htcleoRetireSchedulerBlankLayer =
            htcleoUiStageResult == KErrNone
            && (TUint32)htcleoUiStage == 0x4D4D1013u
            && htcleoSourceNonWhite == 0u
            && htcleoDestinationBeforeNonWhite > 0u
            && htcleoRectCount == 1
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(360, 640);
'''
        new_bounds = r'''        const TBool htcleoLegacySchedulerRoot =
            htcleoRectCount == 1
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(360, 640);
        const TBool htcleoScaledSchedulerRoot =
            htcleoRectCount == 2
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(480, 800);
        const TBool htcleoRetireSchedulerBlankLayer =
            htcleoUiStageResult == KErrNone
            && (TUint32)htcleoUiStage == 0x4D4D1013u
            && htcleoSourceNonWhite == 0u
            && htcleoDestinationBeforeNonWhite > 0u
            && (htcleoLegacySchedulerRoot || htcleoScaledSchedulerRoot);
'''
        if text.count(old_bounds) != 1:
            raise SystemExit("scheduler blank-layer V1 bounds mismatch")
        text = text.replace(old_bounds, new_bounds, 1)
    if V2_MARKER in text:
        text = text.replace(V2_MARKER, MARKER, 1)
        old_scaled = r'''        const TBool htcleoScaledSchedulerRoot =
            htcleoRectCount == 2
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(480, 800);
'''
        new_scaled = r'''        const TBool htcleoScaledSchedulerRoot =
            (htcleoRectCount == 1 || htcleoRectCount == 2)
            && htcleoBounds.iTl == TPoint(0, 0)
            && htcleoBounds.Size() == TSize(480, 800);
'''
        if text.count(old_scaled) != 1:
            raise SystemExit("scheduler blank-layer V2 scaled-root mismatch")
        text = text.replace(old_scaled, new_scaled, 1)
    if MARKER in text and "htcleoSchedulerBlankGuardUsed" in text:
        migrations = {
            "        static TBool htcleoSchedulerBlankGuardUsed = EFalse;\n": "",
            "            !htcleoSchedulerBlankGuardUsed\n"
            "            && htcleoUiStageResult == KErrNone\n":
                "            htcleoUiStageResult == KErrNone\n",
            "            htcleoSchedulerBlankGuardUsed = ETrue;\n":
                "            // Preserve the already accumulated real UI layers.\n",
        }
        for old, new in migrations.items():
            if text.count(old) != 1:
                raise SystemExit(
                    "scheduler blank-layer state migration anchor mismatch"
                )
            text = text.replace(old, new, 1)
    if MARKER not in text:
        count = text.count(ANCHOR)
        if count != 1:
            raise SystemExit(
                "scheduler blank-layer guard: expected one anchor, "
                f"found {count}"
            )
        text = text.replace(ANCHOR, REPLACEMENT, 1)

    checks = {
        "single marker": text.count(MARKER) == 1,
        "old markers absent": (
            V1_MARKER not in text and V2_MARKER not in text
        ),
        "exact scheduler stage": text.count("0x4D4D1013u") == 1,
        "no DLL writable state": "htcleoSchedulerBlankGuardUsed" not in text,
        "blank-over-nonblank predicate": (
            text.count("htcleoSourceNonWhite == 0u") == 1
            and text.count("htcleoDestinationBeforeNonWhite > 0u") == 1
        ),
        "exact legacy root bounds": (
            text.count("htcleoRectCount == 1") == 2
            and text.count("htcleoBounds.iTl == TPoint(0, 0)") == 2
            and text.count("htcleoBounds.Size() == TSize(360, 640)") == 1
        ),
        "exact scaled root bounds": (
            text.count(
                "(htcleoRectCount == 1 || htcleoRectCount == 2)"
            ) == 1
            and text.count("htcleoRectCount == 2") == 1
            and text.count("htcleoBounds.Size() == TSize(480, 800)") == 1
            and text.count(
                "htcleoLegacySchedulerRoot || htcleoScaledSchedulerRoot"
            ) == 1
        ),
        "guard stage": text.count("0x00001934u") == 1,
        "real transfer retained": text.count("SgUtils::TransferPixels(") == 2,
        "post-copy signature retained": text.count("0x00001931u") == 1,
        "no fabricated draw or wait": all(
            token not in REPLACEMENT
            for token in (
                "Mem::Fill",
                "DrawNow",
                "MakeVisible",
                "User::After",
                "RTimer",
                "WaitForRequest",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "scheduler blank-layer guard verification failed: "
            + ", ".join(failed)
        )
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_DISPLAY_SCHEDULER_BLANK_LAYER_GUARD="
        "matrixmenu-1013-white-legacy360x640-or-scaled1or2rect480x800-retire-1934"
    )


if __name__ == "__main__":
    main()
