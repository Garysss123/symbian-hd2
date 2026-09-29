#!/usr/bin/env python3
"""Make the cellular online/offline helper optional on HTC Leo bring-up."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_AI3XML_ONLINEOFFLINE_OPTIONAL_V1"
TRACE_MARKER = "HTCLEO_AI3XMLUIMAIN_STARTUP_TRACE_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_appui(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    if text.count(TRACE_MARKER) != 1:
        raise SystemExit("appui: startup trace prerequisite is missing or duplicated")

    text = replace_once(
        text,
        f"// {TRACE_MARKER}\n",
        f"// {TRACE_MARKER}\n// {MARKER}\n",
        "appui marker",
    )
    text = replace_once(
        text,
        """    HtcleoAi3XmlLog(0x485801A1u, KErrNone, 0u);
    iHelper = COnlineOfflineHelper::NewL( iUiCtl );
    HtcleoAi3XmlLog(0x485801A2u, KErrNone, (TUint32)iHelper);
""",
        """    HtcleoAi3XmlLog(0x485801A1u, KErrNone, 0u);
    iHelper = NULL;
    TRAPD( htcleoOnlineOfflineError,
        iHelper = COnlineOfflineHelper::NewL( iUiCtl ) );
    HtcleoAi3XmlLog(0x485801A2u, htcleoOnlineOfflineError,
        (TUint32)iHelper);
    if ( htcleoOnlineOfflineError != KErrNone &&
         htcleoOnlineOfflineError != KErrNotFound &&
         htcleoOnlineOfflineError != KErrServerTerminated )
        {
        User::Leave( htcleoOnlineOfflineError );
        }
""",
        "optional helper construction",
    )
    text = replace_once(
        text,
        """    if( aItemType == KOnline )
        {
        return iHelper->ShowOnlineItem();
        }
    else if( aItemType == KOffline )
        {
        return iHelper->ShowOfflineItem();
        }
""",
        """    if( aItemType == KOnline )
        {
        return iHelper ? iHelper->ShowOnlineItem() : EFalse;
        }
    else if( aItemType == KOffline )
        {
        return iHelper ? iHelper->ShowOfflineItem() : EFalse;
        }
""",
        "online/offline menu guards",
    )
    text = replace_once(
        text,
        """void CAppUi::SetOnlineStateL( TBool aOnline )
    {       
    iHelper->ProcessOnlineStateL( aOnline );        
    }
""",
        """void CAppUi::SetOnlineStateL( TBool aOnline )
    {
    if ( iHelper )
        {
        iHelper->ProcessOnlineStateL( aOnline );
        }
    }
""",
        "online state guard",
    )
    return text


def patch_contentpublisher(text: str) -> str:
    if text.count(MARKER) == 1:
        return text
    text = replace_once(
        text,
        '#include "onlineofflinehelper.h"\n',
        '#include "onlineofflinehelper.h"\n\n'
        f'// {MARKER}\n',
        "content publisher marker",
    )
    text = replace_once(
        text,
        """    if ( aPubInfo == KNetwork )
        {
        _LIT( KOffline, "hs_offline" );
        CLiwDefaultMap *outDataMap = CLiwDefaultMap::NewLC();
""",
        """    if ( aPubInfo == KNetwork )
        {
        CAppUi* appUi = iUiController.AppUi();
        COnlineOfflineHelper* helper = appUi ? appUi->Helper() : NULL;
        if ( !helper )
            {
            return;
            }
        _LIT( KOffline, "hs_offline" );
        CLiwDefaultMap *outDataMap = CLiwDefaultMap::NewLC();
""",
        "network publisher helper guard",
    )
    text = replace_once(
        text,
        """            iUiController.AppUi()->Helper()->HandleConnectionQueryL(variant.AsDes());
""",
        """            helper->HandleConnectionQueryL(variant.AsDes());
""",
        "guarded connection query",
    )
    return text


def verify(appui: str, publisher: str) -> None:
    checks = {
        "appui marker": appui.count(MARKER) == 1,
        "publisher marker": publisher.count(MARKER) == 1,
        "trace prerequisite": appui.count(TRACE_MARKER) == 1,
        "single helper factory": appui.count("COnlineOfflineHelper::NewL") == 1,
        "trapped helper factory": appui.count("TRAPD( htcleoOnlineOfflineError,") == 1,
        "not-found policy": appui.count(
            "htcleoOnlineOfflineError != KErrNotFound"
        ) == 1,
        "server-terminated policy": appui.count(
            "htcleoOnlineOfflineError != KErrServerTerminated"
        ) == 1,
        "raw helper result trace": appui.count(
            "HtcleoAi3XmlLog(0x485801A2u, htcleoOnlineOfflineError,"
        ) == 1,
        "online menu guard": appui.count(
            "iHelper ? iHelper->ShowOnlineItem() : EFalse"
        ) == 1,
        "offline menu guard": appui.count(
            "iHelper ? iHelper->ShowOfflineItem() : EFalse"
        ) == 1,
        "state guard": appui.count("if ( iHelper )") == 1,
        "publisher early guard": publisher.count("if ( !helper )") == 1,
        "publisher guarded call": publisher.count(
            "helper->HandleConnectionQueryL"
        ) == 1,
        "old unguarded publisher call gone": (
            "AppUi()->Helper()->HandleConnectionQueryL" not in publisher
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ai3xml online/offline optional audit failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    component = args.root / "sf/app/homescreen/idlehomescreen/xmluicontroller"
    appui_path = component / "src/appui.cpp"
    publisher_path = component / "src/contentpublisher.cpp"
    for path in (appui_path, publisher_path):
        if not path.is_file():
            raise SystemExit(f"missing XML controller source: {path}")

    appui = patch_appui(appui_path.read_text(encoding="latin-1"))
    publisher = patch_contentpublisher(
        publisher_path.read_text(encoding="latin-1")
    )
    appui_path.write_text(appui, encoding="latin-1")
    publisher_path.write_text(publisher, encoding="latin-1")
    verify(appui, publisher)
    print(
        "HTCLEO_AI3XML_ONLINEOFFLINE_POLICY="
        "notfound-or-serverterminated-null-hide-cellular-menu"
    )


if __name__ == "__main__":
    main()
