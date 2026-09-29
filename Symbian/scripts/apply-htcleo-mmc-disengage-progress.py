#!/usr/bin/env python3
"""Trace the MMC completion DFC/disengage gap after iteration 369 E808.

Retire E801-E80A and place ten returning E901-E90A checkpoints around
EffectiveModes(), SchedGetOnDFC(), and SchedDisengage().  The trace is armed
without drawing when CIMInitStackSM reaches EStInitDone, so shared scheduler
helpers cannot report during earlier MMC activity.  E90A disarms the returning
channel; the only physical UDF remains the durable FAT-log boundary in ESTART.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8"
MARKER = "HTCLEO_MMC_DISENGAGE_PROGRESS_V9"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def reporter(stage: str, phase: int = 4, indent: str = "\t") -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == {phase})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u);\n"
        "#endif\n"
    )


def migrate_estart(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        if OLD_MARKER in text:
            raise SystemExit("V8 and V9 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V9 marker")
    path.write_text(text, encoding="utf-8")


def retire_v8_stack(text: str) -> str:
    e801 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe8010000u);\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 3;\n"
        "\t\t\t}\n"
        "#endif\n"
    )
    arm_v9 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 4;\n"
        "#endif\n"
    )
    if e801 in text:
        text = replace_once(text, e801, arm_v9, "retire E801 and arm V9")
    elif "0xe8010000u" in text:
        raise SystemExit("unrecognized E801 call shape")
    elif arm_v9 not in text:
        raise SystemExit("neither V8 activation nor V9 activation found")

    for stage in ("E802", "E803", "E804", "E805", "E806", "E807", "E808", "E809"):
        block = reporter(stage, 3, {
            "E802": "\t\t",
            "E803": "\t\t\t",
            "E804": "\t",
            "E805": "\t",
            "E806": "\t\t",
            "E807": "\t",
            "E808": "\t\t\t",
            "E809": "\t\t\t",
        }[stage])
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} call shape")

    e80a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\t\tif (gHtcleoLocalMediaPowerupTrace == 3)\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe80a0000u);\n"
        "\t\t\t\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t\t\t\t}\n"
        "#endif\n"
    )
    if e80a in text:
        text = replace_once(text, e80a, "", "retire E80A")
    elif "0xe80a0000u" in text:
        raise SystemExit("unrecognized E80A call shape")
    return text


def install_stack(path: pathlib.Path) -> None:
    text = retire_v8_stack(path.read_text(encoding="utf-8"))
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe9010000u)" in text:
        path.write_text(text, encoding="utf-8")
        return

    text = replace_once(
        text,
        "\t\tif( iCompleteAllExitCode || sessP->iDoComplete )\n"
        "\t\t\t{\n"
        "\t\t\tif( (EffectiveModes(sessP->iConfig) & KMMCModeCompleteInStackDFC) != 0 &&\n"
        "\t\t\t\t SchedGetOnDFC() )\n",
        "\t\tif( iCompleteAllExitCode || sessP->iDoComplete )\n"
        "\t\t\t{\n"
        + reporter("E901", 4, "\t\t\t")
        + "\t\t\tconst TUint32 htcleoCompletionModes = EffectiveModes(sessP->iConfig);\n"
        + reporter("E902", 4, "\t\t\t")
        + "\t\t\tif( (htcleoCompletionModes & KMMCModeCompleteInStackDFC) != 0 &&\n"
        "\t\t\t\t SchedGetOnDFC() )\n",
        "E901/E902 around EffectiveModes",
    )

    text = replace_once(
        text,
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:sgd\"));\n\n"
        "\tif( iDFCRunning )\n"
        "\t    {\n",
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:sgd\"));\n"
        + reporter("E903", 4)
        + "\n\tif( iDFCRunning )\n"
        "\t    {\n"
        + reporter("E904", 4, "\t\t"),
        "E903 entry and E904 DFC-running path",
    )
    text = replace_once(
        text,
        "\tif( (iStackState & KMMCStackStateWaitingDFC) == 0 )\n"
        "\t\t{\n"
        "\t\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:sgd:q\"));\n",
        "\tif( (iStackState & KMMCStackStateWaitingDFC) == 0 )\n"
        "\t\t{\n"
        "\t\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:sgd:q\"));\n"
        + reporter("E905", 4, "\t\t"),
        "E905 before DFC queue",
    )
    text = replace_once(
        text,
        "\t\telse\n"
        "\t\t\tiStackDFC.Enque();\n"
        "\t\t}\n\n"
        "\tOstTraceFunctionExitExt( DMMCSTACK_SCHEDGETONDFC_EXIT2, this, (TInt) ESchedLoop);\n",
        "\t\telse\n"
        "\t\t\tiStackDFC.Enque();\n"
        + reporter("E906", 4, "\t\t")
        + "\t\t}\n\n"
        "\tOstTraceFunctionExitExt( DMMCSTACK_SCHEDGETONDFC_EXIT2, this, (TInt) ESchedLoop);\n",
        "E906 after DFC queue",
    )
    text = replace_once(
        text,
        "\t\t\t\t// SchedGetOnDfc() will return EFalse, and the callback will be called.\n"
        "\t\t\t\tiCompReq = ETrue;\n",
        "\t\t\t\t// SchedGetOnDfc() will return EFalse, and the callback will be called.\n"
        + reporter("E907", 4, "\t\t\t\t")
        + "\t\t\t\tiCompReq = ETrue;\n",
        "E907 completion pass observed queued DFC",
    )
    text = replace_once(
        text,
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:sd\"));\n\n"
        "\tDMMCSession* sessP = iWorkSet.Remove();\n\n"
        "\tSchedDoAbort( sessP );\n",
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:sd\"));\n"
        + reporter("E908", 4)
        + "\n\tDMMCSession* sessP = iWorkSet.Remove();\n\n"
        "\tSchedDoAbort( sessP );\n"
        + reporter("E909", 4),
        "E908 entry and E909 after SchedDoAbort",
    )
    e90a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 4)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe90a0000u);\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text,
        "\tsessP->iState = 0;\n"
        "\tOstTraceFunctionExit1( DMMCSTACK_SCHEDDISENGAGE_EXIT, this );\n",
        "\tsessP->iState = 0;\n"
        + e90a
        + "\tOstTraceFunctionExit1( DMMCSTACK_SCHEDDISENGAGE_EXIT, this );\n",
        "E90A SchedDisengage complete",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = "\n".join(
        paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "pbusmedia", "spbus", "stack")
    )
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V9 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe80" in sources:
        raise SystemExit("a retired E80x call remains")
    for index in range(1, 11):
        stage = f"e90{index:x}"
        if sources.count(f"HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"DFC/disengage checkpoint missing or duplicated: {stage}")
    if paths["stack"].read_text(encoding="utf-8").count(
        "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe90"
    ) != 10:
        raise SystemExit("all ten DFC/disengage checkpoints must be in stack.cpp")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in sources:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-htcleo-mmc-disengage-progress.py KERNEL_SOURCE")
    root = pathlib.Path(sys.argv[1]).resolve()
    paths = {
        "estart": root / "userlibandfileserver/fileserver/estart/estart.cpp",
        "estart_main": root / "userlibandfileserver/fileserver/estart/estartmain.cpp",
        "locmedia": root / "kernel/eka/drivers/locmedia/locmedia.cpp",
        "pbusmedia": root / "kernel/eka/drivers/pbus/pbusmedia.cpp",
        "spbus": root / "kernel/eka/drivers/pbus/spbus.cpp",
        "stack": root / "kernel/eka/drivers/pbus/mmc/stack.cpp",
    }
    for path in paths.values():
        if not path.is_file():
            raise SystemExit(f"missing source input: {path}")
    migrate_estart(paths["estart"])
    install_stack(paths["stack"])
    verify(paths)
    print("HTCLEO_MMC_DISENGAGE_PROGRESS=10")


if __name__ == "__main__":
    main()
