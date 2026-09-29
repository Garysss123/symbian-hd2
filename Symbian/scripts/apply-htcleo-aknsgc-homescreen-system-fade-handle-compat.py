#!/usr/bin/env python3
"""Avoid HomeScreen system-fade IPC through a zero AknSrv session handle.

Iteration 720 maps the final foreground observer to CAknFadeStack and proves
its HandleGainingForeground callback does not return.  The callback's first
unprotected external operation is CAknSgcClient::IsSystemFaded(), whose stock
non-AknSrv branch sends synchronous IPC without checking iAknSrv.Handle().
This transform retains the real server path and uses the existing local
ESystemFaded flag only when HomeScreen has no live session.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_HANDLE_COMPAT_V1"
PREREQUISITE = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_KEYBLOCK_COMPAT_V1"
ROUTE_PREREQUISITE = "HTCLEO_AKNAPPUI_HOMESCREEN_FOCUS_LOG_ROUTE_V2"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


SET_OLD = '''void CAknSgcClient::DoSetSystemFaded(TBool aFade)
\t{
\tif (iFlags[EInAknSrv])
\t\t{
\t\tif (!COMPARE_BOOLS(iFlags[ESystemFaded], aFade))
\t\t\t{
\t\t\tif (aFade)
\t\t\t\t{
\t\t\t\tRedrawServerStatusPane();
\t\t\t\t}
\t\t\t}
\t\tiEikonEnv->WsSession().SetSystemFaded(aFade);
\t\tiFlags.Assign(ESystemFaded, aFade);\t
\t\t}
\telse
\t\t{
\t\tiAknSrv.SetSystemFaded(aFade);
\t\t}
\t}'''


SET_NEW = '''void CAknSgcClient::DoSetSystemFaded(TBool aFade)
\t{
\tconst TBool htcleoHomeSystemFade =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tconst TInt htcleoAknSrvHandle = iAknSrv.Handle();
\tif (htcleoHomeSystemFade)
\t\tHtcleoAknAppUiBaseLog(0x0000C57Cu, aFade,
\t\t\t(TUint32)htcleoAknSrvHandle);
\tif (iFlags[EInAknSrv])
\t\t{
\t\tif (!COMPARE_BOOLS(iFlags[ESystemFaded], aFade))
\t\t\t{
\t\t\tif (aFade)
\t\t\t\t{
\t\t\t\tRedrawServerStatusPane();
\t\t\t\t}
\t\t\t}
\t\tiEikonEnv->WsSession().SetSystemFaded(aFade);
\t\tiFlags.Assign(ESystemFaded, aFade);\t
\t\t}
\telse if (htcleoHomeSystemFade && htcleoAknSrvHandle == 0)
\t\t{
\t\t// There is no server endpoint on which system fade can take effect.
\t\t// Preserve the requested state locally until a real session exists.
\t\tiFlags.Assign(ESystemFaded, aFade);
\t\tHtcleoAknAppUiBaseLog(0x0000C57Du,
\t\t\tiFlags[ESystemFaded], (TUint32)htcleoAknSrvHandle);
\t\t}
\telse
\t\t{
\t\tif (htcleoHomeSystemFade)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C57Eu, aFade,
\t\t\t\t(TUint32)htcleoAknSrvHandle);
\t\tiAknSrv.SetSystemFaded(aFade);
\t\tif (htcleoHomeSystemFade)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C57Fu, aFade,
\t\t\t\t(TUint32)htcleoAknSrvHandle);
\t\t}
\t}'''


GET_OLD = '''TBool CAknSgcClient::DoIsSystemFaded() const
\t{
\tif (iFlags[EInAknSrv])
\t\t{
\t\treturn iFlags[ESystemFaded];
\t\t}
\telse
\t\t{
\t\tTBool fade;
\t\tiAknSrv.IsSystemFaded(fade);
\t\treturn fade;
\t\t}
\t}'''


GET_NEW = '''TBool CAknSgcClient::DoIsSystemFaded() const
\t{
\tconst TBool htcleoHomeSystemFade =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tconst TInt htcleoAknSrvHandle = iAknSrv.Handle();
\tif (htcleoHomeSystemFade)
\t\tHtcleoAknAppUiBaseLog(0x0000C577u,
\t\t\tiFlags[EInAknSrv], (TUint32)htcleoAknSrvHandle);
\tif (iFlags[EInAknSrv])
\t\t{
\t\tif (htcleoHomeSystemFade)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C578u,
\t\t\t\tiFlags[ESystemFaded], 0u);
\t\treturn iFlags[ESystemFaded];
\t\t}
\telse if (htcleoHomeSystemFade && htcleoAknSrvHandle == 0)
\t\t{
\t\tHtcleoAknAppUiBaseLog(0x0000C579u,
\t\t\tiFlags[ESystemFaded], (TUint32)htcleoAknSrvHandle);
\t\treturn iFlags[ESystemFaded];
\t\t}
\telse
\t\t{
\t\tTBool fade = EFalse;
\t\tif (htcleoHomeSystemFade)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C57Au, KErrNone,
\t\t\t\t(TUint32)htcleoAknSrvHandle);
\t\tiAknSrv.IsSystemFaded(fade);
\t\tif (htcleoHomeSystemFade)
\t\t\tHtcleoAknAppUiBaseLog(0x0000C57Bu, fade,
\t\t\t\t(TUint32)htcleoAknSrvHandle);
\t\treturn fade;
\t\t}
\t}'''


def install(text: str) -> str:
    text = replace_once(
        text,
        f"// {PREREQUISITE}\n",
        f"// {PREREQUISITE}\n// {MARKER}\n",
        "system fade compatibility marker",
    )
    text = replace_once(text, SET_OLD, SET_NEW, "DoSetSystemFaded")
    return replace_once(text, GET_OLD, GET_NEW, "DoIsSystemFaded")


def verify(text: str, route_text: str) -> None:
    checks = {
        "marker": text.count(MARKER) == 1,
        "prerequisite": text.count(PREREQUISITE) == 1,
        "logger route": route_text.count(ROUTE_PREREQUISITE) == 1,
        "stages": all(
            text.count(f"0x0000C{stage:03X}u") == 1
            for stage in range(0x577, 0x580)
        ),
        "two HomeScreen gates": text.count(
            "RProcess().SecureId().iId == 0x102750F0u"
        ) == 2,
        "two zero-handle guards": text.count(
            "htcleoHomeSystemFade && htcleoAknSrvHandle == 0"
        ) == 2,
        "local state retained": (
            text.count("iFlags.Assign(ESystemFaded, aFade);") >= 2
            and text.count("return iFlags[ESystemFaded];") >= 2
        ),
        "real server IPC retained": (
            text.count("iAknSrv.SetSystemFaded(aFade);") == 1
            and text.count("iAknSrv.IsSystemFaded(fade);") == 1
        ),
        "no fabricated session or timing": all(
            token not in SET_NEW + GET_NEW
            for token in (
                "SetHandle",
                "CreateSession",
                "User::After",
                "RTimer",
                "TRAP_IGNORE",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen system-fade handle compatibility audit failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/classicui/uifw/AvKon/src"
    path = base / "aknsgcc.cpp"
    route_path = base / "AknAppUi.cpp"
    for source_path in (path, route_path):
        if not source_path.is_file():
            raise SystemExit(f"missing Avkon source: {source_path}")
    text = path.read_text(encoding="latin-1")
    route_text = route_path.read_text(encoding="latin-1")
    if MARKER not in text:
        text = install(text)
    verify(text, route_text)
    path.write_text(text, encoding="latin-1")
    print(
        "HTCLEO_AKNSGC_HOMESCREEN_SYSTEM_FADE_HANDLE_COMPAT="
        "handle0-local-state-C577-C57F-real-session-stock"
    )


if __name__ == "__main__":
    main()
