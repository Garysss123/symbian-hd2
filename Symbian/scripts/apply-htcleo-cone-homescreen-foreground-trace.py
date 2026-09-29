#!/usr/bin/env python3
"""Trace the real HomeScreen FocusGained path through CONE.

The 719 hardware result reaches CAknAppUiBase::HandleWsEventL and then dies
inside CCoeAppUi::HandleWsEventL before returning.  This transform adds only
SID-gated, close-only breadcrumbs around the finite focus path and around each
registered foreground observer.  It does not trap, skip, retry, delay, or
change any focus decision.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_CONE_HOMESCREEN_FOREGROUND_TRACE_V1"
PUMP_PREREQUISITE = "HTCLEO_CONE_EVENT_PUMP_DURABLE_TRACE_V1"
HOME_PREREQUISITE = "HTCLEO_CONE_HOMESCREEN_AO_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


APPUI_OLD = '''\tcase EEventFocusLost:
\tcase EEventFocusGained:
\t\t{
\t\tTBool foreground=(type==EEventFocusGained);
\t\tif (foreground)
\t\t\t{
\t\t\tiCoeEnv->NotifyForegroundObserversOfGainingForeground();
\t\t\t}
\t\telse
\t\t\t{
\t\t\tiCoeEnv->NotifyForegroundObserversOfLosingForeground();
\t\t\t}
\t\tCCoeControl* topFocusable=TopFocusableControl();
\t\tHandleForegroundEventL(foreground);
\t\tif (!topFocusable)
\t\t\tSetAndDrawFocus(foreground);
\t\telse if(IsControlOnStack(topFocusable))
\t\t\t{
\t\t\tTBool isFocused=topFocusable->IsFocused();
\t\t\tif ((foreground && !isFocused) || (!foreground && isFocused))
\t\t\t\ttopFocusable->SetFocus(foreground,EDrawNow);
\t\t\t}
\t\tbreak;
\t\t}'''


APPUI_NEW = '''\tcase EEventFocusLost:
\tcase EEventFocusGained:
\t\t{
\t\tconst TBool htcleoHomeFocusTrace =
\t\t\t(RProcess().SecureId().iId == 0x102750F0u);
\t\tTBool foreground=(type==EEventFocusGained);
\t\tif (htcleoHomeFocusTrace)
\t\t\tHtcleoConeLog(0x434F0500u, foreground, (TUint32)aDestination);
\t\tif (foreground)
\t\t\t{
\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\tHtcleoConeLog(0x434F0501u, KErrNone, 0u);
\t\t\tiCoeEnv->NotifyForegroundObserversOfGainingForeground();
\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\tHtcleoConeLog(0x434F0502u, KErrNone, 0u);
\t\t\t}
\t\telse
\t\t\t{
\t\t\tiCoeEnv->NotifyForegroundObserversOfLosingForeground();
\t\t\t}
\t\tCCoeControl* topFocusable=TopFocusableControl();
\t\tif (htcleoHomeFocusTrace)
\t\t\tHtcleoConeLog(0x434F0503u, KErrNone, (TUint32)topFocusable);
\t\tif (htcleoHomeFocusTrace)
\t\t\tHtcleoConeLog(0x434F0504u, foreground, (TUint32)this);
\t\tHandleForegroundEventL(foreground);
\t\tif (htcleoHomeFocusTrace)
\t\t\tHtcleoConeLog(0x434F0505u, foreground, (TUint32)this);
\t\tif (htcleoHomeFocusTrace)
\t\t\tHtcleoConeLog(0x434F0506u, topFocusable ? 1 : 0,
\t\t\t\t(TUint32)topFocusable);
\t\tif (!topFocusable)
\t\t\t{
\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\tHtcleoConeLog(0x434F0507u, foreground, 0u);
\t\t\tSetAndDrawFocus(foreground);
\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\tHtcleoConeLog(0x434F0508u, foreground, 0u);
\t\t\t}
\t\telse
\t\t\t{
\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\tHtcleoConeLog(0x434F0509u, KErrNone,
\t\t\t\t\t(TUint32)topFocusable);
\t\t\tconst TBool htcleoOnStack=IsControlOnStack(topFocusable);
\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\tHtcleoConeLog(0x434F050Au, htcleoOnStack,
\t\t\t\t\t(TUint32)topFocusable);
\t\t\tif (htcleoOnStack)
\t\t\t\t{
\t\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\t\tHtcleoConeLog(0x434F050Bu, KErrNone,
\t\t\t\t\t\t(TUint32)topFocusable);
\t\t\t\tTBool isFocused=topFocusable->IsFocused();
\t\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\t\tHtcleoConeLog(0x434F050Cu, isFocused,
\t\t\t\t\t\t(TUint32)topFocusable);
\t\t\t\tif ((foreground && !isFocused) || (!foreground && isFocused))
\t\t\t\t\t{
\t\t\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\t\t\tHtcleoConeLog(0x434F050Du, foreground,
\t\t\t\t\t\t\t(TUint32)topFocusable);
\t\t\t\t\ttopFocusable->SetFocus(foreground,EDrawNow);
\t\t\t\t\tif (htcleoHomeFocusTrace)
\t\t\t\t\t\tHtcleoConeLog(0x434F050Eu, foreground,
\t\t\t\t\t\t\t(TUint32)topFocusable);
\t\t\t\t\t}
\t\t\t\t}
\t\t\t}
\t\tif (htcleoHomeFocusTrace)
\t\t\tHtcleoConeLog(0x434F050Fu, foreground, 0u);
\t\tbreak;
\t\t}'''


OBSERVER_OLD = '''void CCoeEnvExtra::NotifyForegroundObserversOfGainingForeground()
\t{
\tfor (TInt i=iArrayOfForegroundObservers.Count()-1; i>=0; --i)
\t\t{
\t\tstatic_cast<MCoeForegroundObserver*>(iArrayOfForegroundObservers[i])->HandleGainingForeground();
\t\t}
\t}'''


OBSERVER_NEW = '''void CCoeEnvExtra::NotifyForegroundObserversOfGainingForeground()
\t{
\tconst TBool htcleoHomeObserverTrace =
\t\t(RProcess().SecureId().iId == 0x102750F0u);
\tconst TInt htcleoObserverCount=iArrayOfForegroundObservers.Count();
\tif (htcleoHomeObserverTrace)
\t\tHtcleoConeLog(0x434F0520u, htcleoObserverCount, 0u);
\tfor (TInt i=htcleoObserverCount-1; i>=0; --i)
\t\t{
\t\tMCoeForegroundObserver* htcleoObserver=
\t\t\tstatic_cast<MCoeForegroundObserver*>(iArrayOfForegroundObservers[i]);
\t\tif (htcleoHomeObserverTrace)
\t\t\tHtcleoConeLog(0x434F0521u, i, (TUint32)htcleoObserver);
\t\tconst TUint32 htcleoObserverVtable = htcleoObserver
\t\t\t? *reinterpret_cast<const TUint32*>(htcleoObserver) : 0u;
\t\tif (htcleoHomeObserverTrace)
\t\t\tHtcleoConeLog(0x434F0522u, i, htcleoObserverVtable);
\t\thtcleoObserver->HandleGainingForeground();
\t\tif (htcleoHomeObserverTrace)
\t\t\tHtcleoConeLog(0x434F0523u, i, (TUint32)htcleoObserver);
\t\t}
\tif (htcleoHomeObserverTrace)
\t\tHtcleoConeLog(0x434F0524u, htcleoObserverCount, 0u);
\t}'''


def install_appui(text: str) -> str:
    text = replace_once(
        text,
        '#include "COEVWMAN.H"\n',
        '#include "COEVWMAN.H"\n\n'
        f'// {MARKER}\n'
        'void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n',
        "CONE AppUi logger declaration",
    )
    return replace_once(text, APPUI_OLD, APPUI_NEW, "CONE focus dispatch")


def install_extra(text: str) -> str:
    text = replace_once(
        text,
        '#include "coedefkeys.h"\n',
        '#include "coedefkeys.h"\n\n'
        f'// {MARKER}\n'
        'void HtcleoConeLog(TUint32 aStage, TInt aResult, TUint32 aDetail);\n',
        "foreground observer logger declaration",
    )
    return replace_once(
        text, OBSERVER_OLD, OBSERVER_NEW, "foreground observer loop"
    )


def verify(appui: str, extra: str, main: str) -> None:
    joined = appui + extra
    checks = {
        "markers": appui.count(MARKER) == 1 and extra.count(MARKER) == 1,
        "logger prerequisite": (
            main.count(PUMP_PREREQUISITE) == 1
            and main.count(HOME_PREREQUISITE) == 1
        ),
        "logger declarations": joined.count("void HtcleoConeLog(") == 2,
        "outer stages": all(
            appui.count(f"0x{stage:08X}u") == 1
            for stage in range(0x434F0500, 0x434F0510)
        ),
        "observer stages": all(
            extra.count(f"0x{stage:08X}u") == 1
            for stage in range(0x434F0520, 0x434F0525)
        ),
        "real observer callback retained": extra.count(
            "htcleoObserver->HandleGainingForeground();"
        ) == 1,
        "real virtual foreground retained": appui.count(
            "HandleForegroundEventL(foreground);"
        ) == 1,
        "real focus operations retained": (
            appui.count("SetAndDrawFocus(foreground);") == 1
            and appui.count(
                "topFocusable->SetFocus(foreground,EDrawNow);"
            ) == 1
        ),
        "HomeScreen only": joined.count("0x102750F0u") == 2,
        "no behavior bypass": all(
            token not in APPUI_NEW + OBSERVER_NEW
            for token in (
                "TRAP_IGNORE",
                "User::After",
                "RTimer",
                "RequestComplete",
                "return;",
            )
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "HomeScreen CONE foreground trace audit failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    base = args.root / "sf/mw/classicui/lafagnosticuifoundation/cone/src"
    appui_path = base / "COEAUI.CPP"
    extra_path = base / "CoeEnvExtra.cpp"
    main_path = base / "COEMAIN.CPP"
    for path in (appui_path, extra_path, main_path):
        if not path.is_file():
            raise SystemExit(f"missing CONE source: {path}")
    appui = appui_path.read_text(encoding="latin-1")
    extra = extra_path.read_text(encoding="latin-1")
    main_source = main_path.read_text(encoding="latin-1")
    if MARKER not in appui:
        appui = install_appui(appui)
    if MARKER not in extra:
        extra = install_extra(extra)
    verify(appui, extra, main_source)
    appui_path.write_text(appui, encoding="latin-1")
    extra_path.write_text(extra, encoding="latin-1")
    print(
        "HTCLEO_CONE_HOMESCREEN_FOREGROUND_TRACE="
        "HSCONE-1m-0500-050f-observers-0520-0524-behavior-neutral"
    )


if __name__ == "__main__":
    main()
