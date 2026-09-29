#!/usr/bin/env python3
"""Expose HomeScreen's existing Post-Coe and SGC checkpoints in HSXML.

Live-read iteration 683 evidence reaches Eikon B60A but not B60B, bracketing
the virtual KEikPostCoeAppUiConstructL callback.  The Avkon implementation
already contains B530-B547 and C500-C52C checkpoints.  Extend only the
HomeScreen logger range so those existing checkpoints use the one-MiB HSXML
stream.  No result, branch, timing, layout, SGC, WServ, or leave behavior is
changed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(source: str) -> str:
    return replace_once(
        source,
        "    if (htcleoLogHomeScreen &&\n"
        "        (aStage < 0x0000B500u || aStage > 0x0000B520u))\n"
        "        {\n"
        "        return;\n"
        "        }\n",
        "    // HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE_V1\n"
        "    const TBool htcleoHomeBaseStage =\n"
        "        aStage >= 0x0000B500u && aStage <= 0x0000B520u;\n"
        "    const TBool htcleoHomePostCoeStage =\n"
        "        aStage >= 0x0000B530u && aStage <= 0x0000B547u;\n"
        "    const TBool htcleoHomeSgcStage =\n"
        "        aStage >= 0x0000C500u && aStage <= 0x0000C52Cu;\n"
        "    if (htcleoLogHomeScreen &&\n"
        "        !htcleoHomeBaseStage && !htcleoHomePostCoeStage &&\n"
        "        !htcleoHomeSgcStage)\n"
        "        {\n"
        "        return;\n"
        "        }\n",
        "HomeScreen trace range",
    )


def verify(source: str, sgc_source: str) -> None:
    app_stages = list(range(0xB530, 0xB536)) + list(range(0xB540, 0xB548))
    sgc_stages = list(range(0xC500, 0xC505)) + list(range(0xC510, 0xC52D))
    checks = {
        "marker": source.count(MARKER) == 1,
        "three bounded ranges": (
            source.count("aStage >= 0x0000B500u") == 1
            and source.count("aStage <= 0x0000B520u") == 1
            and source.count("aStage >= 0x0000B530u") == 1
            and source.count("aStage <= 0x0000B547u") == 1
            and source.count("aStage >= 0x0000C500u") == 1
            and source.count("aStage <= 0x0000C52Cu") == 1
        ),
        "shared HomeScreen sink retained": (
            source.count(r'C:\\Symbian3\\HSXML.TXT') == 1
            and source.count('"HTCLEO_HAB  "') == 1
            and source.count("1048576 - 128") == 1
        ),
        "all Post-Coe checkpoints retained": all(
            source.count(f"0x0000{stage:04X}u") >= 1
            for stage in app_stages
        ),
        "all SGC checkpoints retained": all(
            sgc_source.count(f"0x0000{stage:04X}u") >= 1
            for stage in sgc_stages
        ),
        "single writer no flush": (
            source.count("file.Write(record)") == 1
            and "file.Flush();" not in source
        ),
        "behavior neutral": (
            "User::After" not in source
            and (
                "HalFunction" not in source
                or (
                    (
                        source.count("HTCLEO_AVKON_FOCUS_TOUCH_REARM_V1")
                        + source.count("HTCLEO_AVKON_POST_FOCUS_TOUCH_REARM_V2")
                    ) == 1
                    and source.count("UserSvr::HalFunction") == 3
                )
            )
            and "htcleoHomeSgcResult" not in source
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/mw/classicui/uifw/AvKon/src"
    source_path = component / "AknAppUi.cpp"
    sgc_path = component / "aknsgcc.cpp"
    source = source_path.read_text(encoding="latin-1")
    if MARKER not in source:
        source = install(source)
    sgc_source = sgc_path.read_text(encoding="latin-1")
    verify(source, sgc_source)
    source_path.write_text(source, encoding="latin-1")
    print(
        "HTCLEO_AKNAPPUI_HOMESCREEN_POSTCOE_TRACE="
        "HSXML-1m-B530-B547-C500-C52C-behavior-neutral"
    )


if __name__ == "__main__":
    main()
