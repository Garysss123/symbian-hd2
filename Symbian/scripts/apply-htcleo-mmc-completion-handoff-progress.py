#!/usr/bin/env python3
"""Trace the MMC state-machine completion handoff after iteration 368 E708.

Retire E701-E70A and place ten returning E801-E80A checkpoints between
CIMInitStackSM EStInitDone and the internal StackSession callback.  The trace
is promoted from phase 1 to phase 3 at E801 so shared scheduler code cannot
report during earlier MMC activity.  E80A disarms the returning channel; the
only physical UDF remains the durable FAT-log boundary in ESTART.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_POST_POWERUP_PROGRESS_V7"
MARKER = "HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS_V8"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def reporter(stage: str, phase: int = 1, indent: str = "\t") -> str:
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
            raise SystemExit("V7 and V8 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V8 marker")
    path.write_text(text, encoding="utf-8")


def retire_v7_stack(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    for stage in ("E701", "E702", "E703", "E704", "E705", "E706", "E707", "E708"):
        block = reporter(stage, 1, "\t\t")
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} call shape")
    e709 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe7090000u | "
        "(TUint32(mmcError) & 0xffffu));\n"
        "#endif\n"
    )
    if e709 in text:
        text = replace_once(text, e709, "", "retire E709")
    elif "0xe7090000u" in text:
        raise SystemExit("unrecognized E709 call shape")
    return text


def retire_v7_spbus(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    e70a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70a0000u | "
        "(TUint32(anError) & 0xffffu));\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    if e70a in text:
        text = replace_once(text, e70a, "", "retire E70A")
    elif "0xe70a0000u" in text:
        raise SystemExit("unrecognized E70A call shape")
    path.write_text(text, encoding="utf-8")


def install_stack(path: pathlib.Path) -> None:
    text = retire_v7_stack(path)
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe8010000u)" in text:
        path.write_text(text, encoding="utf-8")
        return

    e801 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe8010000u);\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 3;\n"
        "\t\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text,
        "\t\ts.iState &= ~KMMCSessStateInProgress;\t// now we won't be restarted\n"
        "\t\tSchedGetOnDFC();\t\t\t\t\t\t// StackSessionCB must be on DFC\n",
        "\t\ts.iState &= ~KMMCSessStateInProgress;\t// now we won't be restarted\n"
        + e801
        + "\t\tSchedGetOnDFC();\t\t\t\t\t\t// StackSessionCB must be on DFC\n"
        + reporter("E802", 3, "\t\t"),
        "E801/E802 around SchedGetOnDFC",
    )
    text = replace_once(
        text,
        "\t\t\tconst TMMCErr signal = iStack[iSP].iFunction(iContextP);\n\n"
        "\t\t\tif (signal)\n",
        "\t\t\tconst TMMCErr signal = iStack[iSP].iFunction(iContextP);\n"
        + reporter("E803", 3, "\t\t\t")
        + "\n\t\t\tif (signal)\n",
        "E803 state-machine function returned",
    )
    text = replace_once(
        text,
        "\tOstTraceFunctionExit1( TMMCSTATEMACHINE_DISPATCH_EXIT2, this );\n"
        "\treturn( KMMCErrBypass | iExitCode );\n",
        "\tOstTraceFunctionExit1( TMMCSTATEMACHINE_DISPATCH_EXIT2, this );\n"
        + reporter("E804", 3)
        + "\treturn( KMMCErrBypass | iExitCode );\n",
        "E804 Dispatch completion",
    )
    text = replace_once(
        text,
        "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n\n"
        "\tiStackState &= ~KMMCStackStateReScheduled;\n",
        "\tTMMCErr exitCode = iSessionP->iMachine.Dispatch();\n"
        + reporter("E805", 3)
        + "\n\tiStackState &= ~KMMCStackStateReScheduled;\n",
        "E805 SchedSession Dispatch returned",
    )
    text = replace_once(
        text,
        "\tif( exitCode )\n"
        "\t\tMarkComplete( iSessionP, (exitCode & ~KMMCErrBypass) );\n",
        "\tif( exitCode )\n"
        "\t\t{\n"
        "\t\tMarkComplete( iSessionP, (exitCode & ~KMMCErrBypass) );\n"
        + reporter("E806", 3, "\t\t")
        + "\t\t}\n",
        "E806 MarkComplete returned",
    )
    text = replace_once(
        text,
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:scp\"));\n\n"
        "\tiCompReq = EFalse;\n",
        "\t__KTRACE_OPT(KPBUS1,Kern::Printf(\"=mst:scp\"));\n"
        + reporter("E807", 3)
        + "\n\tiCompReq = EFalse;\n",
        "E807 SchedCompletionPass entry",
    )
    text = replace_once(
        text,
        "\t\tif( iCompleteAllExitCode || sessP->iDoComplete )\n"
        "\t\t\t{\n"
        "\t\t\tif( (EffectiveModes(sessP->iConfig) & KMMCModeCompleteInStackDFC) != 0 &&\n",
        "\t\tif( iCompleteAllExitCode || sessP->iDoComplete )\n"
        "\t\t\t{\n"
        + reporter("E808", 3, "\t\t\t")
        + "\t\t\tif( (EffectiveModes(sessP->iConfig) & KMMCModeCompleteInStackDFC) != 0 &&\n",
        "E808 completed session selected",
    )
    text = replace_once(
        text,
        "\t\t\tSchedDisengage();\t\t\t\t\t// calls iWorkSet.Remove\n"
        "\t\t\tsessP->iMMCExitCode |= iCompleteAllExitCode;\n",
        "\t\t\tSchedDisengage();\t\t\t\t\t// calls iWorkSet.Remove\n"
        + reporter("E809", 3, "\t\t\t")
        + "\t\t\tsessP->iMMCExitCode |= iCompleteAllExitCode;\n",
        "E809 SchedDisengage returned",
    )
    e80a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\t\t\tif (gHtcleoLocalMediaPowerupTrace == 3)\n"
        "\t\t\t\t\t{\n"
        "\t\t\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe80a0000u);\n"
        "\t\t\t\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t\t\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text,
        "\t\t\tif(doCallback)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t// call media driver completion routine or StackSessionCBST().\n"
        "\t\t\t\tsessP->iCallBack.CallBack();\n",
        "\t\t\tif(doCallback)\n"
        "\t\t\t\t{\n"
        "\t\t\t\t// call media driver completion routine or StackSessionCBST().\n"
        + e80a
        + "\t\t\t\tsessP->iCallBack.CallBack();\n",
        "E80A before internal completion callback",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = "\n".join(
        paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "pbusmedia", "spbus", "stack")
    )
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V8 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70" in sources:
        raise SystemExit("a retired E70x call remains")
    for index in range(1, 11):
        stage = f"e80{index:x}"
        if sources.count(f"HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"completion-handoff checkpoint missing or duplicated: {stage}")
    if paths["stack"].read_text(encoding="utf-8").count(
        "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe80"
    ) != 10:
        raise SystemExit("all ten completion-handoff checkpoints must be in stack.cpp")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in sources:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: apply-htcleo-mmc-completion-handoff-progress.py KERNEL_SOURCE"
        )
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
    if MARKER not in paths["estart"].read_text(encoding="utf-8"):
        migrate_estart(paths["estart"])
    install_stack(paths["stack"])
    retire_v7_spbus(paths["spbus"])
    verify(paths)
    print("HTCLEO_MMC_COMPLETION_HANDOFF_PROGRESS=10")


if __name__ == "__main__":
    main()
