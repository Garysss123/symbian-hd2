#!/usr/bin/env python3
"""Trace the repaired MMC ASSP-disengage and first completion callback.

Iteration 371 proved EA09, immediately before ASSPDisengage().  The HTC PSL
then called ReportASSPDisengaged() after the generic scheduler had detached
iSessionP, causing a NULL dereference.  The platform fix removes that redundant
report; this transform retires EA01-EA0A and places ten returning EB01-EB0A
checkpoints from the repaired virtual call through the first second-stage
initialisation Engage().  The only physical UDF remains the durable FAT-log
boundary in ESTART.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10"
MARKER = "HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def reporter(stage: str, phase: int, indent: str = "\t") -> str:
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
            raise SystemExit("V10 and V11 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V11 marker")
    path.write_text(text, encoding="utf-8")


def retire_v10_stack(text: str) -> str:
    indents = {
        "EA01": "\t",
        "EA02": "\t",
        "EA03": "\t",
        "EA04": "\t",
        "EA05": "\t",
        "EA06": "\t\t",
        "EA07": "\t",
        "EA08": "\t",
        "EA09": "\t\t",
    }
    for stage, indent in indents.items():
        block = reporter(stage, 5, indent)
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} call shape")

    ea0a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 5)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea0a0000u);\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    if ea0a in text:
        text = replace_once(text, ea0a, "", "retire EA0A")
    elif "0xea0a0000u" in text:
        raise SystemExit("unrecognized EA0A call shape")
    return text


def install_stack(path: pathlib.Path) -> None:
    text = retire_v10_stack(path.read_text(encoding="utf-8"))
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb010000u)" in text:
        path.write_text(text, encoding="utf-8")
        return

    text = replace_once(
        text,
        "\tif( sessP->iState & KMMCSessStateASSPEngaged )\n"
        "\t\t{\n"
        "\t\tASSPDisengage();\n"
        "\t\t}\n\n"
        "\tsessP->iState = 0;\n",
        "\tif( sessP->iState & KMMCSessStateASSPEngaged )\n"
        "\t\t{\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 5)\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 6;\n"
        "#endif\n"
        + reporter("EB01", 6, "\t\t")
        + "\t\tASSPDisengage();\n"
        + reporter("EB02", 6, "\t\t")
        + "\t\t}\n\n"
        "\tsessP->iState = 0;\n"
        + reporter("EB03", 6),
        "EB01-EB03 ASSP disengage and state clear",
    )
    text = replace_once(
        text,
        "\t\t\tSchedDisengage();\t\t\t\t\t// calls iWorkSet.Remove\n"
        "\t\t\tsessP->iMMCExitCode |= iCompleteAllExitCode;\n",
        "\t\t\tSchedDisengage();\t\t\t\t\t// calls iWorkSet.Remove\n"
        + reporter("EB04", 6, "\t\t\t")
        + "\t\t\tsessP->iMMCExitCode |= iCompleteAllExitCode;\n",
        "EB04 SchedDisengage return",
    )
    text = replace_once(
        text,
        "\t\t\t\t// call media driver completion routine or StackSessionCBST().\n"
        "\t\t\t\tsessP->iCallBack.CallBack();\n",
        "\t\t\t\t// call media driver completion routine or StackSessionCBST().\n"
        + reporter("EB05", 6, "\t\t\t\t")
        + "\t\t\t\tsessP->iCallBack.CallBack();\n",
        "EB05 callback boundary",
    )
    text = replace_once(
        text,
        "TInt DMMCStack::StackSessionCB()\n"
        "\t{\n"
        "\tOstTraceFunctionEntry1( DMMCSTACK_STACKSESSIONCB_ENTRY, this );\n",
        "TInt DMMCStack::StackSessionCB()\n"
        "\t{\n"
        + reporter("EB06", 6)
        + "\tOstTraceFunctionEntry1( DMMCSTACK_STACKSESSIONCB_ENTRY, this );\n",
        "EB06 StackSessionCB entry",
    )
    text = replace_once(
        text,
        "\tTMMCErr mmcError = iStackSession->MMCExitCode();\n"
        "\tiStackState &= ~KMMCStackStateInitInProgress;\n\n"
        "\tTInt  errCode   = KErrNone;\n",
        "\tTMMCErr mmcError = iStackSession->MMCExitCode();\n"
        "\tiStackState &= ~KMMCStackStateInitInProgress;\n"
        + reporter("EB07", 6)
        + "\n\tTInt  errCode   = KErrNone;\n",
        "EB07 first-stage result fetch",
    )
    text = replace_once(
        text,
        "\t\t\t}\t// else ( !iCardArray->CardsPresent() )\n"
        "\t\t}\n\n"
        "\tif(errCode == KErrNone)\n",
        "\t\t\t}\t// else ( !iCardArray->CardsPresent() )\n"
        "\t\t}\n\n"
        + reporter("EB08", 6)
        + "\tif(errCode == KErrNone)\n",
        "EB08 card scan complete",
    )
    text = replace_once(
        text,
        "\t\tiAutoUnlockSession.iCardP = NULL;\n"
        "\t\tiAutoUnlockSession.SetupCIMInitStackAfterUnlock();\n"
        "\t\terrCode = iAutoUnlockSession.Engage();\n"
        "\t\t}\n",
        "\t\tiAutoUnlockSession.iCardP = NULL;\n"
        "\t\tiAutoUnlockSession.SetupCIMInitStackAfterUnlock();\n"
        + reporter("EB09", 6, "\t\t")
        + "\t\terrCode = iAutoUnlockSession.Engage();\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 6)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb0a0000u);\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t\t}\n"
        "#endif\n"
        "\t\t}\n",
        "EB09/EB0A second-stage Engage",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = "\n".join(
        paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "pbusmedia", "spbus", "stack")
    )
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V11 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea0" in sources:
        raise SystemExit("a retired EA0x call remains")
    for index in range(1, 11):
        stage = f"eb0{index:x}"
        if sources.count(f"HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"ASSP-disengage checkpoint missing or duplicated: {stage}")
    if paths["stack"].read_text(encoding="utf-8").count(
        "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb0"
    ) != 10:
        raise SystemExit("all ten ASSP-disengage checkpoints must be in stack.cpp")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in sources:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-htcleo-mmc-assp-disengage-progress.py KERNEL_SOURCE")
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
    print("HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS=10")


if __name__ == "__main__":
    main()
