#!/usr/bin/env python3
"""Move ten returning checkpoints after the proven MMC DoPowerUpSM boundary.

Iteration 367 reached E60A exactly.  Retire E601-E60A and install E701-E70A
across the rest of CIMUpdateAcqSM, the internal stack-session callback, and
DPBusSocket::PowerUpSequenceComplete.  The first Caps power-up arm remains
one-shot and the only physical UDF remains the durable FAT-log boundary.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_INIT_PROGRESS_V6"
MARKER = "HTCLEO_MMC_POST_POWERUP_PROGRESS_V7"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def reporter(stage: str, indent: str = "\t") -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == 1)\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u);\n"
        "#endif\n"
    )


def dynamic_reporter(stage: str, value: str, indent: str = "\t") -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == 1)\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u | "
        f"(TUint32({value}) & 0xffffu));\n"
        "#endif\n"
    )


def migrate_estart(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        if OLD_MARKER in text:
            raise SystemExit("V6 and V7 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V7 marker")
    path.write_text(text, encoding="utf-8")


def retire_v6_stack(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    for stage, indent in (
        ("E601", "\t"),
        ("E602", "\t"),
        ("E603", "\t"),
        ("E604", "\t"),
        ("E605", "\t"),
        ("E606", "\t"),
        ("E607", "\t\t"),
        ("E608", "\t\t"),
        ("E609", "\t\t"),
    ):
        block = reporter(stage, indent)
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} call shape")
    final = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe60a0000u);\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t\t}\n"
        "#endif\n"
    )
    if final in text:
        text = replace_once(text, final, "", "retire E60A")
    elif "0xe60a0000u" in text:
        raise SystemExit("unrecognized E60A call shape")
    return text


def install_stack(path: pathlib.Path) -> None:
    text = retire_v6_stack(path)
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe7010000u)" in text:
        path.write_text(text, encoding="utf-8")
        return
    text = replace_once(
        text,
        "\t\tMergeConfig(&s);\t// This might take some time, but we are running in DFC here\n"
        "\t\t// Reinstate config bits after the merge\n"
        "\t\tiConfig.RemoveMode( KMMCModeEnablePreemption | KMMCModeCardControlled );\n"
        "\t\tSMF_INVOKES( InitClockOnSMST, EStClockOn )",
        "\t\tMergeConfig(&s);\t// This might take some time, but we are running in DFC here\n"
        "\t\t// Reinstate config bits after the merge\n"
        "\t\tiConfig.RemoveMode( KMMCModeEnablePreemption | KMMCModeCardControlled );\n"
        + reporter("E701", "\t\t")
        + "\t\tSMF_INVOKES( InitClockOnSMST, EStClockOn )",
        "E701 before InitClockOnSM",
    )
    text = replace_once(
        text,
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_CIMUPDATEACQSM4, \"EStClockOn\" );\n"
        "\t\t// Check if there are any cards present in the stack\n",
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_CIMUPDATEACQSM4, \"EStClockOn\" );\n"
        + reporter("E702", "\t\t")
        + "\t\t// Check if there are any cards present in the stack\n",
        "E702 InitClockOnSM completed",
    )
    text = replace_once(
        text,
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_CIMUPDATEACQSM5, \"EStStartInterrogation\" );\n"
        "\t\t// NB: RCAs are not unlocked here. They will be unlocked one by one during the update of card info array.\n"
        "\t\tSMF_INVOKES( AcquireStackSMST, EStCheckStack )\n",
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_CIMUPDATEACQSM5, \"EStStartInterrogation\" );\n"
        "\t\t// NB: RCAs are not unlocked here. They will be unlocked one by one during the update of card info array.\n"
        + reporter("E703", "\t\t")
        + "\t\tSMF_INVOKES( AcquireStackSMST, EStCheckStack )\n",
        "E703 before AcquireStackSM",
    )
    for stage, trace, following, label in (
        (
            "E704",
            "DMMCSTACK_CIMUPDATEACQSM6",
            "\t\t// Check that all known cards are still present by issuing select/deselect\n",
            "AcquireStackSM completed",
        ),
        (
            "E705",
            "DMMCSTACK_CIMUPDATEACQSM7",
            "\t\t// Call a licencee-specific state machine to allow card capabilities to be modified.\n",
            "CheckStackSM completed",
        ),
        (
            "E706",
            "DMMCSTACK_CIMUPDATEACQSM8",
            "\t\tTUint maxClk;\n",
            "ModifyCardCapabilitySM completed",
        ),
        (
            "E707",
            "DMMCSTACK_CIMUPDATEACQSM9",
            "\t\ts.iState &= ~(KMMCSessStateInProgress | KMMCSessStateCritical);\n",
            "CIMUpdateAcq finish",
        ),
    ):
        state_name = {
            "E704": "EStCheckStack",
            "E705": "EStCardCap",
            "E706": "EStIssueDSR",
            "E707": "EStFinishUp",
        }[stage]
        old = (
            f"\t\tOstTrace0( TRACE_INTERNALS, {trace}, \"{state_name}\" );\n"
            + following
        )
        new = (
            f"\t\tOstTrace0( TRACE_INTERNALS, {trace}, \"{state_name}\" );\n"
            + reporter(stage, "\t\t")
            + following
        )
        text = replace_once(text, old, new, f"{stage} {label}")
    text = replace_once(
        text,
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_CIMINITSTACKSM3, \"EStInitDone\" );\n"
        "\t\ts.iState &= ~KMMCSessStateInProgress;",
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_CIMINITSTACKSM3, \"EStInitDone\" );\n"
        + reporter("E708", "\t\t")
        + "\t\ts.iState &= ~KMMCSessStateInProgress;",
        "E708 CIMInitStackSM completed",
    )
    text = replace_once(
        text,
        "\tTMMCErr mmcError = iStackSession->MMCExitCode();\n"
        "\tiStackState &= ~KMMCStackStateInitInProgress;\n",
        "\tTMMCErr mmcError = iStackSession->MMCExitCode();\n"
        + dynamic_reporter("E709", "mmcError")
        + "\tiStackState &= ~KMMCStackStateInitInProgress;\n",
        "E709 StackSessionCB entry/result",
    )
    path.write_text(text, encoding="utf-8")


def install_spbus(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70a0000u" in text:
        return
    block = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 1)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70a0000u | "
        "(TUint32(anError) & 0xffffu));\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text,
        "\tOstTraceFunctionEntry1( DPBUSSOCKET_POWERUPSEQUENCECOMPLETE_ENTRY, this );\n",
        "\tOstTraceFunctionEntry1( DPBUSSOCKET_POWERUPSEQUENCECOMPLETE_ENTRY, this );\n"
        + block,
        "E70A PowerUpSequenceComplete",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = "\n".join(
        paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "pbusmedia", "spbus", "stack")
    )
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V7 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe60" in sources:
        raise SystemExit("a retired E60x call remains")
    for index in range(1, 11):
        stage = f"e70{index:x}"
        if sources.count(f"HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"post-power-up checkpoint missing or duplicated: {stage}")
    if sources.count("HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe70") != 10:
        raise SystemExit("post-power-up checkpoint count is not ten")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in sources:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: apply-htcleo-mmc-post-powerup-progress.py KERNEL_SOURCE"
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
    install_spbus(paths["spbus"])
    verify(paths)
    print("HTCLEO_MMC_POST_POWERUP_PROGRESS=10")


if __name__ == "__main__":
    main()
