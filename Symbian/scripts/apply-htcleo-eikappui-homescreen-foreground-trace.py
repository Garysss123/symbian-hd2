#!/usr/bin/env python3
"""Trace HomeScreen's Eikon foreground/fade path without changing it."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_TRACE_V1"
PREREQUISITE = "HTCLEO_EIKAPPUI_HOMESCREEN_BASECONSTRUCT_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


FADE_OLD = '''EXPORT_C void CEikAppUi::SetFadedL(TBool aFaded)
\t{
\tconst TInt message=(aFaded? KEikMessageFadeAllWindows : KEikMessageUnfadeWindows);
\tHandleResourceChangeL(message);
\tHandleStackedControlsResourceChange(message);
\tiCoeEnv->RootWin().SetFaded(aFaded,RWindowTreeNode::EFadeIncludeChildren);
\t}'''


FADE_NEW = '''EXPORT_C void CEikAppUi::SetFadedL(TBool aFaded)
\t{
\tconst TBool htcleoHomeFadeTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tconst TInt message=(aFaded? KEikMessageFadeAllWindows : KEikMessageUnfadeWindows);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E380u, aFaded, (TUint32)message);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E381u, KErrNone, (TUint32)message);
\tHandleResourceChangeL(message);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E382u, KErrNone, (TUint32)message);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E383u, KErrNone, (TUint32)message);
\tHandleStackedControlsResourceChange(message);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E384u, KErrNone, (TUint32)message);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E385u,
\t\t\tiCoeEnv->RootWin().Identifier(),
\t\t\t(TUint32)iCoeEnv->WsSession().Handle());
\tiCoeEnv->RootWin().SetFaded(aFaded,RWindowTreeNode::EFadeIncludeChildren);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E386u, KErrNone, aFaded);
\tif (htcleoHomeFadeTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E387u, KErrNone, (TUint32)this);
\t}'''


WS_OLD = '''EXPORT_C void CEikAppUi::HandleWsEventL(const TWsEvent& aEvent, CCoeControl* aDestination)
/** Handles window server events.
@see CCoeAppUi::HandleWsEventL

@param aEvent The window server event that occurred. 
@param aDestination The control associated with the event. */
\t{
\tswitch (aEvent.Type())'''


WS_NEW = '''EXPORT_C void CEikAppUi::HandleWsEventL(const TWsEvent& aEvent, CCoeControl* aDestination)
/** Handles window server events.
@see CCoeAppUi::HandleWsEventL

@param aEvent The window server event that occurred. 
@param aDestination The control associated with the event. */
\t{
\tconst TBool htcleoHomeWsTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tif (htcleoHomeWsTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E370u, aEvent.Type(),
\t\t\t(TUint32)aDestination);
\tswitch (aEvent.Type())'''


FG_OLD = '''EXPORT_C void CEikAppUi::HandleForegroundEventL(TBool aForeground)
/** Handles changes to the application when it switches to or from 
the foreground. 

For instance it handles changes to the cursor visibility and to the 
fade state.

This function is called from HandleWsEventL() when an event 
occurs of type EEventFocusLost or EEventFocusGained.

Any application overriding this should first call this base implementation.

@param aForeground ETrue to switch to the foreground. EFalse to switch from 
the foreground.. */
\t{
\tif (LafAppUi::FadeWhenInBackground())
\t\tSetFadedL(!aForeground);
\t
\tif (aForeground)
\t\tiEikonEnv->VirtualCursor().HandleAppToForeground(*iEikonEnv);
\t}'''


FG_NEW = '''EXPORT_C void CEikAppUi::HandleForegroundEventL(TBool aForeground)
/** Handles changes to the application when it switches to or from 
the foreground. 

For instance it handles changes to the cursor visibility and to the 
fade state.

This function is called from HandleWsEventL() when an event 
occurs of type EEventFocusLost or EEventFocusGained.

Any application overriding this should first call this base implementation.

@param aForeground ETrue to switch to the foreground. EFalse to switch from 
the foreground.. */
\t{
\tconst TBool htcleoHomeForegroundTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tif (htcleoHomeForegroundTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E373u, aForeground, (TUint32)this);
\tconst TBool htcleoFadeWhenBackground = LafAppUi::FadeWhenInBackground();
\tif (htcleoHomeForegroundTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E374u, htcleoFadeWhenBackground, 0u);
\tif (htcleoFadeWhenBackground)
\t\t{
\t\tif (htcleoHomeForegroundTrace)
\t\t\tHtcleoEikAppUiBaseLog(0x0000E375u, !aForeground, 0u);
\t\tSetFadedL(!aForeground);
\t\tif (htcleoHomeForegroundTrace)
\t\t\tHtcleoEikAppUiBaseLog(0x0000E376u, !aForeground, 0u);
\t\t}
\t
\tif (aForeground)
\t\t{
\t\tif (htcleoHomeForegroundTrace)
\t\t\tHtcleoEikAppUiBaseLog(0x0000E377u, KErrNone,
\t\t\t\t(TUint32)iEikonEnv);
\t\tiEikonEnv->VirtualCursor().HandleAppToForeground(*iEikonEnv);
\t\tif (htcleoHomeForegroundTrace)
\t\t\tHtcleoEikAppUiBaseLog(0x0000E378u, KErrNone,
\t\t\t\t(TUint32)iEikonEnv);
\t\t}
\tif (htcleoHomeForegroundTrace)
\t\tHtcleoEikAppUiBaseLog(0x0000E379u, KErrNone, (TUint32)this);
\t}'''


def install(text: str) -> str:
    text = replace_once(
        text,
        f"// {PREREQUISITE}\n",
        f"// {PREREQUISITE}\n// {MARKER}\n",
        "Eikon foreground marker",
    )
    text = replace_once(text, FADE_OLD, FADE_NEW, "SetFadedL")
    text = replace_once(text, WS_OLD, WS_NEW, "HandleWsEventL entry")
    text = replace_once(
        text,
        "\tCCoeAppUi::HandleWsEventL(aEvent, aDestination);\n\t}\n\n"
        "EXPORT_C void CEikAppUi::ProcessMessageL",
        "\tif (htcleoHomeWsTrace)\n"
        "\t\tHtcleoEikAppUiBaseLog(0x0000E371u, aEvent.Type(),\n"
        "\t\t\t(TUint32)aDestination);\n"
        "\tCCoeAppUi::HandleWsEventL(aEvent, aDestination);\n"
        "\tif (htcleoHomeWsTrace)\n"
        "\t\tHtcleoEikAppUiBaseLog(0x0000E372u, aEvent.Type(),\n"
        "\t\t\t(TUint32)aDestination);\n"
        "\t}\n\nEXPORT_C void CEikAppUi::ProcessMessageL",
        "CCoe event dispatch",
    )
    return replace_once(text, FG_OLD, FG_NEW, "foreground handler")


def verify(text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "WS stages": all(
            text.count(f"0x0000E{stage:03X}u") == 1
            for stage in range(0x370, 0x373)
        ),
        "foreground stages": all(
            text.count(f"0x0000E{stage:03X}u") == 1
            for stage in range(0x373, 0x37A)
        ),
        "fade stages": all(
            text.count(f"0x0000E{stage:03X}u") == 1
            for stage in range(0x380, 0x388)
        ),
        "real base dispatch retained": text.count(
            "CCoeAppUi::HandleWsEventL(aEvent, aDestination);"
        ) == 1,
        "real fade calls retained": (
            text.count("HandleResourceChangeL(message);") >= 1
            and text.count("HandleStackedControlsResourceChange(message);") >= 1
            and text.count(
                "iCoeEnv->RootWin().SetFaded(aFaded,RWindowTreeNode::EFadeIncludeChildren);"
            ) == 1
        ),
        "real cursor retained": text.count(
            "iEikonEnv->VirtualCursor().HandleAppToForeground(*iEikonEnv);"
        ) == 1,
        "HomeScreen only": text.count("0x102750F0u") >= 3,
        "no bypass or timer": all(
            token not in FADE_NEW + FG_NEW
            for token in ("TRAP_IGNORE", "User::After", "RTimer")
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen Eikon foreground trace audit failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/mw/classicui/commonuisupport/uikon/coresrc/EIKAPPUI.CPP"
    )
    if not path.is_file():
        raise SystemExit(f"missing Eikon AppUi source: {path}")
    text = path.read_text(encoding="latin-1")
    if MARKER not in text:
        text = install(text)
    verify(text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_EIKAPPUI_HOMESCREEN_FOREGROUND_TRACE="
        "HSXML-E370-E379-fade-E380-E387-behavior-neutral"
    )


if __name__ == "__main__":
    main()
