#!/usr/bin/env python3
"""Trace MMC second-stage completion through local-media driver opening.

Iteration 372 reached EB0A exactly: InitStackAfterUnlock was engaged after the
ASSPDisengage lifecycle repair.  Retire EB01-EB0A and place ten returning
EC01-EC0A checkpoints from that asynchronous state machine through its callback,
PBUS-on notification and the first local-media StartOpenMediaDrivers return.
The only physical UDF remains the durable FAT-log boundary in ESTART.
"""

from __future__ import annotations

import pathlib
import sys


OLD_MARKER = "HTCLEO_MMC_ASSP_DISENGAGE_PROGRESS_V11"
MARKER = "HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS_V12"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one source match, found {count}")
    return text.replace(old, new, 1)


def reporter(stage: str, phase: int = 7, indent: str = "\t") -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == {phase})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u);\n"
        "#endif\n"
    )


def dynamic_reporter(
    stage: str, value: str, phase: int = 7, indent: str = "\t"
) -> str:
    return (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        f"{indent}if (gHtcleoLocalMediaPowerupTrace == {phase})\n"
        f"{indent}\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage.lower()}0000u | "
        f"(TUint32({value}) & 0xffffu));\n"
        "#endif\n"
    )


def migrate_estart(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        if OLD_MARKER in text:
            raise SystemExit("V11 and V12 ESTART markers coexist")
        return
    text = replace_once(text, OLD_MARKER, MARKER, "ESTART V12 marker")
    path.write_text(text, encoding="utf-8")


def retire_v11_stack(text: str) -> str:
    for stage, indent in (
        ("EB01", "\t\t"),
        ("EB02", "\t\t"),
        ("EB03", "\t"),
        ("EB04", "\t\t\t"),
        ("EB05", "\t\t\t\t"),
        ("EB06", "\t"),
        ("EB07", "\t"),
        ("EB08", "\t"),
        ("EB09", "\t\t"),
    ):
        block = reporter(stage, 6, indent)
        if block in text:
            text = replace_once(text, block, "", f"retire {stage}")
        elif f"0x{stage.lower()}0000u" in text:
            raise SystemExit(f"unrecognized {stage} call shape")

    eb0a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 6)\n"
        "\t\t\t{\n"
        "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb0a0000u);\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t\t}\n"
        "#endif\n"
    )
    promoted = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\t\tif (gHtcleoLocalMediaPowerupTrace == 6)\n"
        "\t\t\tgHtcleoLocalMediaPowerupTrace = 7;\n"
        "#endif\n"
    )
    if eb0a in text:
        text = replace_once(text, eb0a, promoted, "retire/promote EB0A")
    elif "0xeb0a0000u" in text:
        raise SystemExit("unrecognized EB0A call shape")
    elif promoted not in text:
        raise SystemExit("EB0A promotion boundary is absent")
    return text


def install_stack(path: pathlib.Path) -> None:
    text = retire_v11_stack(path.read_text(encoding="utf-8"))
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec010000u)" in text:
        path.write_text(text, encoding="utf-8")
        return

    text = replace_once(
        text,
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_INITSTACKAFTERUNLOCKSM2, \"EStBegin\" );\n",
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_INITSTACKAFTERUNLOCKSM2, \"EStBegin\" );\n"
        + reporter("EC01", 7, "\t\t"),
        "EC01 InitStackAfterUnlock begin",
    )
    text = replace_once(
        text,
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_INITSTACKAFTERUNLOCKSM4, \"EStGetExtendedCSD\" );\n",
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_INITSTACKAFTERUNLOCKSM4, \"EStGetExtendedCSD\" );\n"
        + reporter("EC02", 7, "\t\t"),
        "EC02 first unlocked card examined",
    )
    text = replace_once(
        text,
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_INITSTACKAFTERUNLOCKSM19, \"EStExit\" );\n"
        "\t\tm.ResetTraps();\n",
        "\t\tOstTrace0( TRACE_INTERNALS, DMMCSTACK_INITSTACKAFTERUNLOCKSM19, \"EStExit\" );\n"
        + reporter("EC03", 7, "\t\t")
        + "\t\tm.ResetTraps();\n",
        "EC03 InitStackAfterUnlock exit",
    )
    text = replace_once(
        text,
        "\t\t\t\tSetBusConfigDefaults( iMasterConfig.iBusConfig, maxClk );\n"
        "\t\t\t\tDoSetClock(maxClk);\n"
        "\t\t\t\t}\n\n"
        "\t\t\tif(doCallback)\n",
        "\t\t\t\tSetBusConfigDefaults( iMasterConfig.iBusConfig, maxClk );\n"
        "\t\t\t\tDoSetClock(maxClk);\n"
        "\t\t\t\t}\n"
        + reporter("EC04", 7, "\t\t\t")
        + "\n\t\t\tif(doCallback)\n",
        "EC04 second-stage completion callback boundary",
    )
    text = replace_once(
        text,
        "\tTInt epocErr = iAutoUnlockSession.EpocErrorCode();\n\n"
        "\t// Calling PowerUpSequenceComplete() with an error may result in the media driver being closed",
        "\tTInt epocErr = iAutoUnlockSession.EpocErrorCode();\n"
        + dynamic_reporter("EC05", "epocErr", 7)
        + "\n\t// Calling PowerUpSequenceComplete() with an error may result in the media driver being closed",
        "EC05 AutoUnlockCB result",
    )
    ec0a = (
        "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
        "\tif (gHtcleoLocalMediaPowerupTrace == 7)\n"
        "\t\t{\n"
        "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0a0000u);\n"
        "\t\tgHtcleoLocalMediaPowerupTrace = 2;\n"
        "\t\t}\n"
        "#endif\n"
    )
    text = replace_once(
        text,
        "\tiSocket->PowerUpSequenceComplete(epocErr);\n"
        "\tiStackState |= KMMCStackStateRunning;\n",
        "\tiSocket->PowerUpSequenceComplete(epocErr);\n"
        + ec0a
        + "\tiStackState |= KMMCStackStateRunning;\n",
        "EC0A PBUS completion returned",
    )
    path.write_text(text, encoding="utf-8")


def install_spbus(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec060000u" not in text:
        text = replace_once(
            text,
            "\tOstTraceFunctionEntry1( DPBUSSOCKET_POWERUPSEQUENCECOMPLETE_ENTRY, this );\n",
            "\tOstTraceFunctionEntry1( DPBUSSOCKET_POWERUPSEQUENCECOMPLETE_ENTRY, this );\n"
            + dynamic_reporter("EC06", "anError", 7),
            "EC06 DPBusSocket PowerUpSequenceComplete",
        )
        path.write_text(text, encoding="utf-8")


def install_pbusmedia(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec070000u" not in text:
        text = replace_once(
            text,
            "\t\t\tcase EPBusOn:\n"
            "\t\t\t\t// bus is now powered up\n"
            "\t\t\t\tif (iState==EPoweringUp1 || iState==EPoweringUp2)\n"
            "\t\t\t\t\tPowerUpComplete(anError);\n",
            "\t\t\tcase EPBusOn:\n"
            "\t\t\t\t// bus is now powered up\n"
            "\t\t\t\tif (iState==EPoweringUp1 || iState==EPoweringUp2)\n"
            "\t\t\t\t\t{\n"
            + dynamic_reporter("EC07", "anError", 7, "\t\t\t\t\t")
            + "\t\t\t\t\tPowerUpComplete(anError);\n"
            "\t\t\t\t\t}\n",
            "EC07 PBUS-on local-media callback",
        )
        path.write_text(text, encoding="utf-8")


def install_locmedia(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "gHtcleoFirstCapsMediaOpenTrace" not in text:
        text = replace_once(
            text,
            "#define HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(aStage) do { } while (0)\n"
            "#endif\n\n"
            "#include \"OstTraceDefinitions.h\"\n",
            "#define HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(aStage) do { } while (0)\n"
            "#endif\n\n"
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "static volatile TUint32 gHtcleoFirstCapsMediaOpenTrace = 0;\n"
            "#endif\n\n"
            "#include \"OstTraceDefinitions.h\"\n",
            "local-media first-Caps gate",
        )
        text = replace_once(
            text,
            "\tOstTrace1( TRACE_FLOW, DPRIMARYMEDIABASE_HANDLEMSG_ENTRY, \"> DPrimaryMediaBase::HandleMsg;m=%x;\", (TUint) &m);\n",
            "\tOstTrace1( TRACE_FLOW, DPRIMARYMEDIABASE_HANDLEMSG_ENTRY, \"> DPrimaryMediaBase::HandleMsg;m=%x;\", (TUint) &m);\n"
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\tif (m.iValue == DLocalDrive::ECaps && gHtcleoFirstCapsMediaOpenTrace == 0)\n"
            "\t\tgHtcleoFirstCapsMediaOpenTrace = 1;\n"
            "#endif\n",
            "arm first-Caps local-media gate",
        )

    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec080000u" not in text:
        text = replace_once(
            text,
            "\tOstTraceFunctionEntry1( DPRIMARYMEDIABASE_POWERUPCOMPLETE_ENTRY, this );\n",
            "\tOstTraceFunctionEntry1( DPRIMARYMEDIABASE_POWERUPCOMPLETE_ENTRY, this );\n"
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\tif (gHtcleoFirstCapsMediaOpenTrace == 1)\n"
            "\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec080000u | (TUint32(anError) & 0xffffu));\n"
            "#endif\n",
            "EC08 local-media PowerUpComplete entry",
        )
        text = replace_once(
            text,
            "\t\tStartOpenMediaDrivers();\n"
            "\t\t}\n"
            "\telse if (iState==EPoweringUp2)\n",
            "\t\tStartOpenMediaDrivers();\n"
            "#if defined(__HTCLEO_LOCALMEDIA_CAPS_PROGRESS__)\n"
            "\t\tif (gHtcleoFirstCapsMediaOpenTrace == 1)\n"
            "\t\t\t{\n"
            "\t\t\tHTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec090000u);\n"
            "\t\t\tgHtcleoFirstCapsMediaOpenTrace = 2;\n"
            "\t\t\t}\n"
            "#endif\n"
            "\t\t}\n"
            "\telse if (iState==EPoweringUp2)\n",
            "EC09 StartOpenMediaDrivers return",
        )
        path.write_text(text, encoding="utf-8")


def verify(paths: dict[str, pathlib.Path]) -> None:
    estart = paths["estart"].read_text(encoding="utf-8")
    sources = "\n".join(
        paths[name].read_text(encoding="utf-8")
        for name in ("locmedia", "pbusmedia", "spbus", "stack")
    )
    if estart.count(MARKER) != 1 or OLD_MARKER in estart:
        raise SystemExit("V12 ESTART marker state is invalid")
    if "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xeb0" in sources:
        raise SystemExit("a retired EB0x call remains")
    for index in range(1, 11):
        stage = f"ec0{index:x}"
        if sources.count(f"HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0x{stage}0000u") != 1:
            raise SystemExit(f"second-stage/media-open checkpoint missing: {stage}")
    if paths["stack"].read_text(encoding="utf-8").count(
        "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0"
    ) != 6:
        raise SystemExit("stack EC checkpoint count is not six")
    if paths["locmedia"].read_text(encoding="utf-8").count(
        "HTCLEO_LOCALMEDIA_POWERUP_PROGRESS(0xec0"
    ) != 2:
        raise SystemExit("locmedia EC checkpoint count is not two")
    main = paths["estart_main"].read_text(encoding="utf-8")
    if main.count("0xe7f000f0") != 1 or "0xe7f000f0" in sources:
        raise SystemExit("physical UDF invariant failed")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "usage: apply-htcleo-mmc-second-stage-media-open-progress.py KERNEL_SOURCE"
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
    migrate_estart(paths["estart"])
    install_stack(paths["stack"])
    install_spbus(paths["spbus"])
    install_pbusmedia(paths["pbusmedia"])
    install_locmedia(paths["locmedia"])
    verify(paths)
    print("HTCLEO_MMC_SECOND_STAGE_MEDIA_OPEN_PROGRESS=10")


if __name__ == "__main__":
    main()
