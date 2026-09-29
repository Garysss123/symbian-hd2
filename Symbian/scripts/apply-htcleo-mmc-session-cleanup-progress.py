#!/usr/bin/env python3
"""Trace MMC session cleanup after iteration 370 E909.

Retire E901-E90A and place ten returning EA01-EA0A checkpoints between the
proven SchedDoAbort return and the end of SchedDisengage().  The returning
channel is promoted to phase 5 at the proven boundary and disarmed by EA0A.
The only physical UDF remains the durable FAT-log boundary in ESTART.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_DISENGAGE_PROGRESS_V9"
MARKER = "HTCLEO_MMC_SESSION_CLEANUP_PROGRESS_V10"


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
            raise SystemExit("V9 and V10 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V10 marker")
    path.write_text(text, encoding="utf-8")


def retire_v9_stack(text: str) -> str:
    indents = {
        "E901": "\t\t\t",
        "E902": "\t\t\t",
        "E903": "\t",
        "E904": "\t\t",
        "E905": "\t\t",
        "E906": "\t\t",
        "E907": "\t\t\t\t",
        "E908": "\t",
    }
    for stage, indent in indents.items():
        block = reporter(stage, 4, indent)
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} call shape")

    e909 = reporter("E909", 4)
    arm_v10 = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 4)\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 5;\n"
        "#endif\n"
    )
    if e909 in text:
        text = replace_once(text, e909, arm_v10, "retire E909 and arm V10")
    elif "0xe9090000u" in text:
        raise SystemExit("unrecognized E909 call shape")
    elif arm_v10 not in text:
        raise SystemExit("neither E909 activation nor V10 activation found")

    e90a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 4)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe90a0000u);\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    if e90a in text:
        text = replace_once(text, e90a, "", "retire E90A")
    elif "0xe90a0000u" in text:
        raise SystemExit("unrecognized E90A call shape")
    return text


def install_stack(path: pathlib.Path) -> None:
    text = retire_v9_stack(path.read_text(encoding="utf-8"))
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea010000u)" in text:
        path.write_text(text, encoding="utf-8")
        return

    text = replace_once(
        text,
        "\tif( sessP == iSessionP )\n"
        "\t\tiSessionP = NULL;\n",
        reporter("EA01", 5)
        + "\tif( sessP == iSessionP )\n"
        "\t\tiSessionP = NULL;\n"
        + reporter("EA02", 5),
        "EA01/EA02 current-session detach",
    )
    text = replace_once(
        text,
        "\tif( sessP->iCardP != NULL && sessP->iCardP->iUsingSessionP == sessP )\n"
        "\t\tsessP->iCardP->iUsingSessionP = NULL;\n",
        reporter("EA03", 5)
        + "\tif( sessP->iCardP != NULL && sessP->iCardP->iUsingSessionP == sessP )\n"
        "\t\tsessP->iCardP->iUsingSessionP = NULL;\n"
        + reporter("EA04", 5),
        "EA03/EA04 card-owner cleanup",
    )
    text = replace_once(
        text,
        "\t// iAutoUnlockSession may attach to more than once card, so need to iterate \n"
        "\t// through all cards and clear their session pointers if they match sessP\n"
        "\tif (sessP == &iAutoUnlockSession)\n"
        "\t\t{\n",
        "\t// iAutoUnlockSession may attach to more than once card, so need to iterate \n"
        "\t// through all cards and clear their session pointers if they match sessP\n"
        + reporter("EA05", 5)
        + "\tif (sessP == &iAutoUnlockSession)\n"
        "\t\t{\n"
        + reporter("EA06", 5, "\t\t"),
        "EA05/EA06 auto-unlock cleanup entry",
    )
    text = replace_once(
        text,
        "\t\t\t}\n"
        "\t\t}\n\n"
        "\tif( sessP->iState & KMMCSessStateASSPEngaged )\n"
        "\t\tASSPDisengage();\n\n"
        "\tsessP->iState = 0;\n",
        "\t\t\t}\n"
        "\t\t}\n"
        + reporter("EA07", 5)
        + "\n"
        + reporter("EA08", 5)
        + "\tif( sessP->iState & KMMCSessStateASSPEngaged )\n"
        "\t\t{\n"
        + reporter("EA09", 5, "\t\t")
        + "\t\tASSPDisengage();\n"
        "\t\t}\n\n"
        "\tsessP->iState = 0;\n"
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 5)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea0a0000u);\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n",
        "EA07-EA0A auto-unlock and ASSP cleanup",
    )
    path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = "\n".join(
        paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "pbusmedia", "spbus", "stack")
    )
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V10 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xe90" in sources:
        raise SystemExit("a retired E90x call remains")
    for index in range(1, 11):
        stage = f"ea0{index:x}"
        if sources.count(f"HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"session-cleanup checkpoint missing or duplicated: {stage}")
    if paths["stack"].read_text(encoding="utf-8").count(
        "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xea0"
    ) != 10:
        raise SystemExit("all ten session-cleanup checkpoints must be in stack.cpp")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in sources:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply-htcleo-mmc-session-cleanup-progress.py KERNEL_SOURCE")
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
    print("HTCLEO_MMC_SESSION_CLEANUP_PROGRESS=10")


if __name__ == "__main__":
    main()
