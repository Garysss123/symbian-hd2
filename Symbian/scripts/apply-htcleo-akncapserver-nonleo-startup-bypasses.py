#!/usr/bin/env python3
"""Skip AknCap startup work that is absent or nonessential on HTC Leo.

The HTC HD2 has no optical navigation sensor, hardware slider/grip, or Nokia
product-specific HAL contract.  Its SD card is fixed boot media for this port,
and the UI-first product profile does not require MMC password prompts or
discreet notification popups.  The optional AlternateFS ECom lookup is also
unneeded because the stock built-in fast-swap control remains as the fallback.

This transform removes only those call sites.  The MMC server IPC paths are
also guarded so a client receives KErrNotSupported (or a harmless cancel/exit)
instead of dereferencing the intentionally absent requester.  It deliberately
retains WServ, FEP, status pane/SGC, key capture, active-idle properties, OOM
protection, ALF, the built-in task switcher, ready publication and rendezvous.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ENTRY_MARKER = "HTCLEO_AKNCAPSERVER_NONLEO_STARTUP_BYPASSES_V1"
KEY_MARKER = "HTCLEO_AKNCAPSERVER_NO_HWRM_SLIDE_OBSERVER_V1"
SERVER_MARKER = "HTCLEO_AKNCAPSERVER_NO_MMC_PASSWORD_IPC_GUARD_V1"


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def install_entry(source: str) -> str:
    source = replace_once(
        source,
        "        DoProductSpecificHalFunction();",
        f"""        // {ENTRY_MARKER}
        // ProductSpecificHalParams.txt belongs to the Nokia reference target.
        // HTC Leo has no compatible product-specific HAL contract.""",
        "product-specific HAL call",
    )
    source = replace_once(
        source,
        "    iMMCUnlock = CAknMMCPasswordRequester::NewL();",
        """    // HTCLEO_AKNCAPSERVER_FIXED_BOOT_MEDIA_NO_MMC_PASSWORD_V1
    // The port boots from a fixed, unlocked SD card; no hot-removal/password UI.
    iMMCUnlock = NULL;""",
        "MMC password requester",
    )
    source = replace_once(
        source,
        "    CAknCapServerDiscreetPopupHandler::CreateDiscreetPopupHandlerL();",
        """    // HTCLEO_AKNCAPSERVER_NO_DISCREET_POPUP_V1
    // Optional notification popups are outside the UI/touch bring-up target.""",
        "discreet popup handler",
    )
    source = replace_once(
        source,
        "    LoadAlternateFsPlugin();",
        """    // HTCLEO_AKNCAPSERVER_BUILTIN_FASTSWAP_ONLY_V1
    // Skip optional AlternateFS ECom discovery; retain built-in FSW below.""",
        "AlternateFS plugin lookup",
    )
    source = replace_once(
        source,
        "\tProcessInitFlipStatus();",
        """    // HTCLEO_AKNCAPSERVER_NO_SLIDER_FLIP_HAL_V1
    // HTC Leo has no hardware slider/cover switch.""",
        "initial slider/flip HAL call",
    )
    return source


def install_key_filter(source: str) -> str:
    return replace_once(
        source,
        "    TRAP_IGNORE( iSlideStatusObserver = CAknSlideStatusNotifier::NewL( this ) );",
        f"""    // {KEY_MARKER}
    // HTC Leo has no HWRM grip/slide property producer.
    iSlideStatusObserver = NULL;""",
        "HWRM slide observer",
    )


def install_server(source: str) -> str:
    source = replace_once(
        source,
        "        iAppUi->MMCUnlock()->ClientExit( clientId );",
        f"""        // {SERVER_MARKER}
        // The fixed boot card has no password requester on HTC Leo.
        if (iAppUi->MMCUnlock())
            {{
            iAppUi->MMCUnlock()->ClientExit( clientId );
            }}""",
        "MMC client-exit guard",
    )
    source = replace_once(
        source,
        """        EnsureAppUiValidityL();
        iAppUi->MMCUnlock()->StartL(aMessage.Int1(), aMessage.Int2(), aMessage, aClientId);""",
        """        EnsureAppUiValidityL();
        if (!iAppUi->MMCUnlock())
            {
            aMessage.Complete(KErrNotSupported);
            return;
            }
        iAppUi->MMCUnlock()->StartL(aMessage.Int1(), aMessage.Int2(), aMessage, aClientId);""",
        "MMC request guard",
    )
    source = replace_once(
        source,
        """        if (!err)
            {
            iAppUi->MMCUnlock()->Cancel(aClientId);
            }""",
        """        if (!err && iAppUi->MMCUnlock())
            {
            iAppUi->MMCUnlock()->Cancel(aClientId);
            }""",
        "MMC cancel guard",
    )
    return source


def verify(entry: str, key_filter: str, server: str) -> None:
    checks = {
        "single entry marker": entry.count(ENTRY_MARKER) == 1,
        "product HAL call removed": entry.count(
            "        DoProductSpecificHalFunction();"
        )
        == 0,
        "MMC requester call removed": entry.count(
            "iMMCUnlock = CAknMMCPasswordRequester::NewL();"
        )
        == 0,
        "discreet popup call removed": entry.count(
            "CAknCapServerDiscreetPopupHandler::CreateDiscreetPopupHandlerL();"
        )
        == 0,
        "AlternateFS call removed": entry.count("    LoadAlternateFsPlugin();") == 0,
        "built-in FSW retained": entry.count(
            "iFSControl= new (ELeave) CAknFastSwapWindowControl(*this);"
        )
        == 1,
        "flip HAL call removed": entry.count("ProcessInitFlipStatus();") == 0,
        "flip helper retained": entry.count(
            "void CAknCapAppServerAppUi::ProcessInitFlipStatus()"
        )
        == 1,
        "single key marker": key_filter.count(KEY_MARKER) == 1,
        "slide observer call removed": key_filter.count(
            "CAknSlideStatusNotifier::NewL( this )"
        )
        == 0,
        "key filter retained": key_filter.count(
            "void CAknServKeyFilter::ConstructL( CAknCapAppServerAppUi& aAppUi )"
        )
        == 1,
        "single MMC IPC guard marker": server.count(SERVER_MARKER) == 1,
        "MMC start is guarded": server.count("if (!iAppUi->MMCUnlock())") == 1,
        "MMC cancel is guarded": server.count(
            "if (!err && iAppUi->MMCUnlock())"
        )
        == 1,
        "MMC client exit is guarded": server.count(
            "if (iAppUi->MMCUnlock())"
        )
        == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HTCLEO non-Leo startup bypass verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    component = args.root / "sf/mw/classicui/uifw/AknGlobalUI/AknCapServer/src"
    entry_path = component / "AknCapServerEntry.cpp"
    key_path = component / "aknKeyFilter.cpp"
    server_path = component / "AknCapServer.cpp"
    entry = entry_path.read_text(encoding="utf-8")
    key_filter = key_path.read_text(encoding="utf-8")
    server = server_path.read_text(encoding="utf-8")

    if ENTRY_MARKER not in entry:
        entry = install_entry(entry)
    if KEY_MARKER not in key_filter:
        key_filter = install_key_filter(key_filter)
    if SERVER_MARKER not in server:
        server = install_server(server)
    verify(entry, key_filter, server)

    entry_path.write_text(entry, encoding="utf-8")
    key_path.write_text(key_filter, encoding="utf-8")
    server_path.write_text(server, encoding="utf-8")
    print(
        "HTCLEO_AKNCAPSERVER_NONLEO_STARTUP=skipped "
        "items=product-hal,mmc-password-with-ipc-guard,discreet-popup,alternatefs-ecom," 
        "slider-flip-hal,hwrm-slide-observer builtin-fsw=retained"
    )


if __name__ == "__main__":
    main()
