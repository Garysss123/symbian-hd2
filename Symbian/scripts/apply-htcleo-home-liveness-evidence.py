#!/usr/bin/env python3
"""Keep low-rate Home heartbeat schedulable and attribute Home WServ exits."""
from __future__ import annotations
import argparse
from pathlib import Path

HB_MARKER = "HTCLEO_HOME_HEARTBEAT_STANDARD_PRIORITY_V1"
EXIT_MARKER = "HTCLEO_WSERV_HOME_EXIT_ATTRIBUTION_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Home liveness anchor missing/duplicated: {old[:90]!r}")
    return text.replace(old, new, 1)


def patch_framework(text: str) -> str:
    if HB_MARKER in text:
        return text
    if "#include <e32property.h>" not in text:
        text = "#include <e32property.h>\n" + text
    text = once(text,
        "    HtcleoHomeLog(0x484F01FFu, KErrNone, 0x414C4956u); // ALIV",
        "    // Publish from the UI scheduler, without synchronous file I/O.\n"
        "    const TUid category = { 0x102750F0 };\n"
        "    const TUint key = 0x7F484201u;\n"
        "    TInt sequence = 0;\n"
        "    TInt result = RProperty::Get(category, key, sequence);\n"
        "    if (result == KErrNone)\n"
        "        result = RProperty::Set(category, key,\n"
        "            sequence >= 0x7ffffffe ? 1 : sequence + 1);\n"
        "    if (result != KErrNone)\n"
        "        HtcleoHomeLog(0x484F01FFu, result, 0x50554641u); // publish failure only")
    return once(text,
        "        iHtcleoHeartbeat = CPeriodic::NewL( CActive::EPriorityIdle );",
        "        // HTCLEO_HOME_HEARTBEAT_STANDARD_PRIORITY_V1\n"
        "        // WServ samples the counter every5s and writes the record.\n"
        "        // Standard priority avoids Idle-only starvation, but cannot\n"
        "        // preempt a blocked UI RunL. No success-path file I/O here.\n"
        "        const TUid category = { 0x102750F0 };\n"
        "        _LIT_SECURITY_POLICY_PASS(readPolicy);\n"
        "        _LIT_SECURITY_POLICY_S0(writePolicy, 0x102750F0);\n"
        "        TInt publishResult = RProperty::Define(category, 0x7F484201u,\n"
        "            RProperty::EInt, readPolicy, writePolicy);\n"
        "        if (publishResult == KErrNone || publishResult == KErrAlreadyExists)\n"
        "            publishResult = RProperty::Set(category, 0x7F484201u, 0);\n"
        "        HtcleoHomeLog(0x484F01FDu, publishResult, 0x7F484201u);\n"
        "        iHtcleoHeartbeat = CPeriodic::NewL( CActive::EPriorityStandard );")


def patch_client(text: str) -> str:
    if EXIT_MARKER in text:
        return text
    return once(text,
        "\t// HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
        "\tif (SecureId().iId==0x101F4CD2u)\n\t\t{\n",
        "\t// HTCLEO_MATRIXMENU_TEARDOWN_ATTRIBUTION_V1\n"
        "\t// HTCLEO_WSERV_HOME_EXIT_ATTRIBUTION_V1\n"
        "\tconst TUint32 htcleoExitSid = SecureId().iId;\n"
        "\tif (htcleoExitSid==0x101F4CD2u || htcleoExitSid==0x102750F0u)\n"
        "\t\t{\n"
        "\t\t// A live client may close an auxiliary WS session. The existing\n"
        "\t\t// ExitType/Reason records, not this marker alone, classify death.\n"
        "\t\tHtcleoWsLog(0x00000478u, (TInt)htcleoExitSid,\n"
        "\t\t\t(TUint32)iClient.Id().Id());\n")


def patch_logger(text: str) -> str:
    if "aStage == 0x00000478u" in text:
        return text
    return once(text,
        "\tconst TBool htcleoHeartbeat = aStage == 0x00000477u;",
        "\tconst TBool htcleoHeartbeat =\n"
        "\t\taStage == 0x00000477u || aStage == 0x00000478u ||\n"
        "\t\taStage == 0x0000047Au;")


def patch_event(text: str) -> str:
    if "HTCLEO_WSERV_HOME_HEARTBEAT_SAMPLE_V1" in text:
        return text
    if "#include <e32property.h>" not in text:
        text = "#include <e32property.h>\n" + text
    return once(text,
        "\tself->iHtcleoProbeTicks = (self->iHtcleoProbeTicks + 1) & 0x3fffffff;",
        "\t// HTCLEO_WSERV_HOME_HEARTBEAT_SAMPLE_V1\n"
        "\t// Independent writer: a missing Home callback cannot silence WServ.\n"
        "\tconst TUid homeCategory = { 0x102750F0 };\n"
        "\tTInt homeSequence = 0;\n"
        "\tconst TInt homeRead = RProperty::Get(homeCategory, 0x7F484201u, homeSequence);\n"
        "\tHtcleoWsLog(0x0000047Au, homeRead, (TUint32)homeSequence);\n"
        "\tself->iHtcleoProbeTicks = (self->iHtcleoProbeTicks + 1) & 0x3fffffff;")


def verify(framework: str, client: str, logger: str, event: str) -> None:
    if framework.count(HB_MARKER) != 1 or client.count(EXIT_MARKER) != 1:
        raise SystemExit("Home liveness markers missing")
    if framework.count("iHtcleoHeartbeat = CPeriodic::NewL( CActive::EPriorityStandard );") != 1:
        raise SystemExit("Home heartbeat priority mismatch")
    if "iHtcleoHeartbeat->Start( 5000000, 5000000," not in framework:
        raise SystemExit("heartbeat cadence changed")
    if "htcleoExitSid==0x101F4CD2u || htcleoExitSid==0x102750F0u" not in client:
        raise SystemExit("exit logging scope must stay at two shell SIDs")
    if (client.count("0x00000478u") != 1 or
            client.count("iClient.ExitType()") != 1 or
            client.count("iClient.ExitCategory()") != 1 or
            "aStage == 0x00000478u" not in logger):
        raise SystemExit("owner identity or complete exit classification missing")
    if "KCapacity = 1048576" not in logger:
        raise SystemExit("preserve the independent1MiB WServ log")
    if "HTCLEO_WSERV_HOME_HEARTBEAT_SAMPLE_V1" not in event or "0x0000047Au" not in event:
        raise SystemExit("independent Home heartbeat sample missing")
    if "aStage == 0x0000047Au" not in logger or "if (result != KErrNone)\n        HtcleoHomeLog(0x484F01FFu" not in framework:
        raise SystemExit("successful Home heartbeat must publish without file logging")
    if "RProperty::Set(category, key," not in framework or "_LIT_SECURITY_POLICY_S0(writePolicy, 0x102750F0)" not in framework:
        raise SystemExit("Home heartbeat publication/ownership missing")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    paths = [
        args.root / "sf/mw/homescreensrv/idlefw/src/framework/aifw.cpp",
        args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/CLIENT.CPP",
        args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/openwfc/WSTOP.CPP",
        args.root / "sf/os/graphics/windowing/windowserver/nga/SERVER/EVENT.CPP",
    ]
    contents = [fn(path.read_text(encoding="utf-8")) for fn, path in
                zip((patch_framework, patch_client, patch_logger, patch_event), paths)]
    verify(*contents)
    for path, content in zip(paths, contents):
        path.write_text(content, encoding="utf-8")
    print("HTCLEO_HOME_LIVENESS=5s-standard-ui-property-counter-wserv-047a-shell-exit-sid-tid-0478")


if __name__ == "__main__":
    main()
