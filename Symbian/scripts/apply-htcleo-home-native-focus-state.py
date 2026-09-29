#!/usr/bin/env python3
"""Synchronize Home Xn foreground state with the native WServ focus path."""
from __future__ import annotations
import argparse
from pathlib import Path

MARKER = "HTCLEO_HOME_NATIVE_FOCUS_STATE_V1"
POINTER_MARKER = "HTCLEO_HOME_POINTER_FOREGROUND_TRACE_V1"


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Home native focus anchor missing/duplicated: {old[:95]!r}")
    return text.replace(old, new, 1)


def patch_listener(text: str) -> str:
    if MARKER in text:
        return text
    text = once(text, '#include "xnuistatelistener.h"\n',
                '#include "xnuistatelistener.h"\n'
                'extern void HtcleoXnGeometryLog(TUint32, TInt, TUint32);\n')
    start = text.index("void CXnUiStateListener::MonitorWsMessage(")
    end = text.index("\n    }\n", start) + len("\n    }\n")
    body = text[start:end]
    body = once(body, "    TInt type( aEvent.Type() );",
        "    TInt type( aEvent.Type() );\n"
        "    // HTCLEO_HOME_NATIVE_FOCUS_STATE_V1\n"
        "    const TBool htcleoNativeFocus =\n"
        "        RProcess().SecureId().iId == 0x102750F0u &&\n"
        "        (type == EEventFocusLost || type == EEventFocusGained);\n"
        "    if (htcleoNativeFocus)\n"
        "        HtcleoXnGeometryLog(0x48581800u, type,\n"
        "            ((TUint32)iForegroundStatus << 16) |\n"
        "            ((TUint32)iForegroundType & 0xffffu));")
    body = once(body,
        "    else if ( type == EEventFocusGained )\n        {\n",
        "    else if ( type == EEventFocusGained )\n        {\n"
        "        // HD2 shell handoff uses real WServ ordinal/focus events,\n"
        "        // while its SGC full/partial notification route is deferred.\n"
        "        // FocusLost already set Background. Pair the genuine native\n"
        "        // gain with that loss so Xn does not silently reject gestures.\n"
        "        // Reuse the existing partial/full decision and observer path.\n"
        "        if (htcleoNativeFocus)\n"
        "            iForegroundType = KAknFullOrPartialForegroundGained;\n")
    body = once(body, "    if ( status != iForegroundStatus )",
        "    if (htcleoNativeFocus)\n"
        "        HtcleoXnGeometryLog(0x48581801u, iForegroundStatus,\n"
        "            (TUint32)iForegroundType);\n"
        "    if ( status != iForegroundStatus )")
    # Both captures and pointer gating live in observers; retain their real
    # callback, including ResetGrabbing on loss/partial foreground.
    close = body.rfind("\n    }")
    body = body[:close] + "\n    if (htcleoNativeFocus)\n" \
        "        HtcleoXnGeometryLog(0x48581802u, type,\n" \
        "            (TUint32)iForegroundStatus);" + body[close:]
    return text[:start] + body + text[end:]


def patch_view(text: str) -> str:
    if POINTER_MARKER in text:
        return text
    signature = "void CXnViewControlAdapter::HandlePointerEventL( \n    const TPointerEvent& aPointerEvent )\n    {"
    text = once(text, signature,
        "extern void HtcleoXnGeometryLog(TUint32, TInt, TUint32);\n\n" +
        signature + "\n"
        "    // HTCLEO_HOME_POINTER_FOREGROUND_TRACE_V1\n"
        "    // Edge-only evidence; no per-drag writes or input fabrication.\n"
        "    if (RProcess().SecureId().iId == 0x102750F0u &&\n"
        "        (aPointerEvent.iType == TPointerEvent::EButton1Down ||\n"
        "         aPointerEvent.iType == TPointerEvent::EButton1Up))\n"
        "        HtcleoXnGeometryLog(0x48581810u, aPointerEvent.iType,\n"
        "            (TUint32)iForegroundStatus);")
    return text


def verify(listener: str, view: str) -> None:
    if listener.count(MARKER) != 1 or view.count(POINTER_MARKER) != 1:
        raise SystemExit("Home native focus markers missing")
    start = listener.index("void CXnUiStateListener::MonitorWsMessage(")
    end = listener.index("\n    }\n", start)
    body = listener[start:end]
    if not (body.index("else if ( type == EEventFocusGained )") <
            body.index("if (htcleoNativeFocus)\n            iForegroundType =") <
            body.index("if ( iForegroundType == KAknFullOrPartialForegroundGained )")):
        raise SystemExit("native state sync must be restricted to genuine focus gain")
    for token in ("RProcess().SecureId().iId == 0x102750F0u",
                  "else if ( type == EEventFocusLost )",
                  "iForegroundStatus = MXnUiStateObserver::EBackground;",
                  "iAppUiAdapter.IsPartialForeground()",
                  "if ( status != iForegroundStatus )",
                  "NotifyForegroundChanged( iForegroundStatus );"):
        if token not in body:
            raise SystemExit("Home native focus lost a stock transition/observer")
    for stage in ("0x48581800u", "0x48581801u", "0x48581802u"):
        if body.count(stage) != 1:
            raise SystemExit("low-rate focus evidence missing")
    if "if ( iForegroundStatus != EBackground )" not in view or "ResetGrabbing();" not in view:
        raise SystemExit("background input protection/capture cleanup must remain")
    if any(token in body for token in ("GetFocusWindowGroup", "SetOrdinal", "User::After", "RProperty::Set", "RunL()")):
        raise SystemExit("focus-state compatibility must not drive WServ or add waits")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src"
    listener_path = base / "xnuistatelistener.cpp"
    view_path = base / "xnviewcontroladapter.cpp"
    listener = patch_listener(listener_path.read_text(encoding="utf-8"))
    view = patch_view(view_path.read_text(encoding="utf-8"))
    verify(listener, view)
    listener_path.write_text(listener, encoding="utf-8")
    view_path.write_text(view, encoding="utf-8")
    print("HTCLEO_HOME_NATIVE_FOCUS_STATE=home-only-wserv-gain-sync-xn-partial-aware-1800-1802-edge1810")


if __name__ == "__main__":
    main()
