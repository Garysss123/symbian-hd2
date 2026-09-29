#!/usr/bin/env python3
"""Redraw MatrixMenu only after the Haze deployment notification arrives.

Hardware 597 proves Connect, SetAllDefinitionSets and the immediate Finish all
return success, but the two synchronous frames still use the old skin cache.
Explicitly enable server notifications and finish a real redraw from the
ConfigurationDeployed callback, after the application skin instance has had a
chance to discard its old cache.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_HAZE_NOTIFY_REDRAW_V1"

ENABLE_OLD = r'''    if (htcleoSkinConnectResult == KErrNone)
        {
        TAknsPkgID htcleoHazePid;'''

ENABLE_NEW = r'''    if (htcleoSkinConnectResult == KErrNone)
        {
        // HTCLEO_MATRIXMENU_HAZE_NOTIFY_REDRAW_V1
        iSkinSrvSession.EnableSkinChangeNotify();
        HtcleoMenuLog(0x4D4D0363u, KErrNone, 0x4E4F5449u);
        TAknsPkgID htcleoHazePid;'''

DEPLOYED_OLD = r'''        case EAknsSkinStatusConfigurationDeployed://    = 2,
            {
            iSkinChangeInProgress = EFalse;
            if (IsForeground())
                {
                TRAPD( err, RefreshIconsL());
                if (!err)
                    {
                    iSkinChangeNeeded = ETrue;
                    }
                }
            }
            break;'''

DEPLOYED_NEW = r'''        case EAknsSkinStatusConfigurationDeployed://    = 2,
            {
            iSkinChangeInProgress = EFalse;
            if (IsForeground())
                {
                TRAPD( err, RefreshIconsL());
                HtcleoMenuLog(0x4D4D0364u, err, 0x4445504Cu);
                if (!err)
                    {
                    iSkinChangeNeeded = ETrue;
                    if (iCurrentContainer)
                        {
                        iCurrentContainer->DrawNow();
                        const TInt htcleoNotifyFinish =
                            iCoeEnv->WsSession().Finish();
                        HtcleoMenuLog(0x4D4D0365u,
                            htcleoNotifyFinish, 0x4445504Cu);
                        }
                    }
                }
            }
            break;'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/app/homescreen/menufw/menufwui/matrixmenu/src/mmappui.cpp"
    )
    if not path.is_file():
        raise SystemExit(f"missing MatrixMenu AppUi source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        text = replace_once(
            text, ENABLE_OLD, ENABLE_NEW, "enable skin-change notification"
        )
        text = replace_once(
            text, DEPLOYED_OLD, DEPLOYED_NEW, "deployed callback redraw"
        )

    checks = {
        "single marker": text.count(MARKER) == 1,
        "notifications enabled": text.count(
            "iSkinSrvSession.EnableSkinChangeNotify();"
        ) == 1,
        "deployed callback retained": text.count(
            "EAknsSkinStatusConfigurationDeployed"
        ) == 1,
        "real icon refresh": text.count("RefreshIconsL()") == 3,
        "callback draw and finish": (
            text.count("htcleoNotifyFinish") == 2
            and text.count("iCurrentContainer->DrawNow();") >= 4
        ),
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in (0x0363, 0x0364, 0x0365)
        ),
        "late Haze retained": (
            text.count("SetAllDefinitionSets(htcleoHazePid)") == 1
            and text.count("0x2000B12D") >= 2
        ),
        "callback fail-open": (
            "LeaveIfError(htcleoNotify" not in text
            and "LeaveIfError(err)" not in DEPLOYED_NEW
        ),
        "no timer or fake pixels": all(
            token not in ENABLE_NEW + DEPLOYED_NEW
            for token in (
                "User::After",
                "RTimer",
                "WaitForRequest",
                "Mem::Fill",
                "CreateWindow",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu Haze notification redraw verification failed: "
            + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_HAZE_NOTIFY_REDRAW="
        "enable-notify-deployed-refresh-draw-finish-0363-0365"
    )


if __name__ == "__main__":
    main()
