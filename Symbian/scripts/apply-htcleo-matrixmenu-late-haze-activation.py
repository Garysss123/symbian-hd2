#!/usr/bin/env python3
"""Activate the stock Haze skin only after MatrixMenu has a stable frame.

Removing the persisted personalisation repository regresses before UI because
the startup custom command blocks in SetColorPaletteL.  Keep that known-good
repository for early boot, then use the stock Skin Server API after the first
real MatrixMenu frame to select Haze.  Every error is fail-open so the stable
594/595 UI remains available.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION_V1"

OLD = r'''    HtcleoMenuLog(0x4D4D0310u, KErrNotSupported, 0x534B494Eu);
    iAppkeyHandler = CMmAppkeyHandler::NewL();'''

NEW = r'''    // HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION_V1
    const TInt htcleoSkinConnectResult = iSkinSrvSession.Connect(this);
    HtcleoMenuLog(0x4D4D0360u, htcleoSkinConnectResult, 0x48415A45u);

    TInt htcleoHazeResult = KErrNotReady;
    if (htcleoSkinConnectResult == KErrNone)
        {
        TAknsPkgID htcleoHazePid;
        htcleoHazePid.Set(TUid::Uid(0x2000B12D));
        htcleoHazeResult =
            iSkinSrvSession.SetAllDefinitionSets(htcleoHazePid);
        }
    HtcleoMenuLog(0x4D4D0361u, htcleoHazeResult, 0x2000B12Du);
    HtcleoMenuLog(0x4D4D0310u, htcleoHazeResult, 0x534B494Eu);

    if (htcleoHazeResult == KErrNone && iCurrentContainer)
        {
        iCurrentContainer->HandleResourceChange(KAknsMessageSkinChange);
        iCurrentContainer->DrawNow();
        const TInt htcleoHazeFinish = iCoeEnv->WsSession().Finish();
        HtcleoMenuLog(0x4D4D0362u, htcleoHazeFinish, 0x48415A45u);
        }
    iAppkeyHandler = CMmAppkeyHandler::NewL();'''


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
        count = text.count(OLD)
        if count != 1:
            raise SystemExit(
                "late Haze activation: expected one post-init anchor, "
                f"found {count}"
            )
        text = text.replace(OLD, NEW, 1)

    checks = {
        "single marker": text.count(MARKER) == 1,
        "one skin connection": text.count(
            "iSkinSrvSession.Connect(this)"
        ) == 1,
        "stock Haze PID": (
            text.count("TUid::Uid(0x2000B12D)") == 1
            and text.count("SetAllDefinitionSets(htcleoHazePid)") == 1
        ),
        "fail-open predicates": (
            text.count("htcleoSkinConnectResult == KErrNone") == 1
            and text.count("htcleoHazeResult == KErrNone") == 1
            and "LeaveIfError(htcleoHaze" not in text
        ),
        "real redraw": (
            text.count(
                "iCurrentContainer->HandleResourceChange("
                "KAknsMessageSkinChange);"
            ) == 1
            and text.count("iCurrentContainer->DrawNow();") >= 3
            and text.count("htcleoHazeFinish") == 2
        ),
        "stages": all(
            text.count(f"0x4D4D{stage:04X}u") == 1
            for stage in (0x0360, 0x0361, 0x0362)
        ),
        "no timer or fabricated UI": all(
            token not in NEW
            for token in (
                "User::After",
                "RTimer",
                "WaitForRequest",
                "CreateWindow",
                "Mem::Fill",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "MatrixMenu late Haze verification failed: " + ", ".join(failed)
        )
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_MATRIXMENU_LATE_HAZE_ACTIVATION="
        "post-first-frame-connect-setall-2000b12d-redraw-failopen-0360-0362"
    )


if __name__ == "__main__":
    main()
