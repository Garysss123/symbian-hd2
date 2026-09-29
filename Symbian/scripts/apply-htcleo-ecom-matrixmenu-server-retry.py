#!/usr/bin/env python3
"""Reconnect ECom once for MatrixMenu after KErrServerTerminated."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY_V1"

FUNCTION_START = "TAny* REComSession::ResolveAndCreateImplL(TInt aServiceId,"
FUNCTION_NVG = "\tconst TBool htcleoNvg = (aInterfaceUid.iUid == 0x1028653B);\n"
FUNCTION_NEW = FUNCTION_NVG + r'''	// HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY_V1
	const TBool htcleoMatrixMenu =
		(RProcess().SecureId().iId == 0x101F4CD2u);
'''

SEND_ANCHOR = r'''	TInt htcleoSendResult = SendReceive(aServiceId, TIpcArgs(&uids,&matchStrExtInfBuf,matchType,&dllPkg));
	if(htcleoNvg) HtcleoEcomLog(0x00000308u, htcleoSendResult, (TUint32)dllInfo.iName.Length());
	User::LeaveIfError(htcleoSendResult);
'''

SEND_NEW = r'''    if(htcleoMatrixMenu)
        HtcleoEcomLog(0x00000310u, aServiceId,
            (TUint32)aInterfaceUid.iUid);
    TInt htcleoSendResult = SendReceive(aServiceId,
        TIpcArgs(&uids,&matchStrExtInfBuf,matchType,&dllPkg));
    if(htcleoNvg) HtcleoEcomLog(0x00000308u, htcleoSendResult, (TUint32)dllInfo.iName.Length());
    if(htcleoMatrixMenu)
        HtcleoEcomLog(0x00000311u, htcleoSendResult,
            (TUint32)aInterfaceUid.iUid);
    if(htcleoMatrixMenu && htcleoSendResult == KErrServerTerminated)
        {
        HtcleoEcomLog(0x00000312u, htcleoSendResult,
            (TUint32)aInterfaceUid.iUid);
        ReallyClose();
        TRAPD(htcleoReconnectResult, ConstructL());
        HtcleoEcomLog(0x00000313u, htcleoReconnectResult,
            (TUint32)aInterfaceUid.iUid);
        if(htcleoReconnectResult == KErrNone)
            {
            htcleoSendResult = SendReceive(aServiceId,
                TIpcArgs(&uids,&matchStrExtInfBuf,matchType,&dllPkg));
            }
        else
            {
            htcleoSendResult = htcleoReconnectResult;
            }
        HtcleoEcomLog(0x00000314u, htcleoSendResult,
            (TUint32)aInterfaceUid.iUid);
        }
    User::LeaveIfError(htcleoSendResult);
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def install(text: str) -> str:
    if MARKER in text:
        return text
    start = text.find(FUNCTION_START)
    if start < 0:
        raise SystemExit("central overload: start not found")
    nvg = text.find(FUNCTION_NVG, start)
    if nvg < 0:
        raise SystemExit("central overload: nvg anchor not found")
    text = text[:nvg] + FUNCTION_NEW + text[nvg + len(FUNCTION_NVG) :]
    text = replace_once(text, SEND_ANCHOR, SEND_NEW, "SendReceive boundary")
    return text


def verify(text: str) -> None:
    list_retry = "HTCLEO_ECOM_MATRIXMENU_LIST_RETRY_V1" in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "MatrixMenu scope": (
            text.count("RProcess().SecureId().iId == 0x101F4CD2u")
            == (2 if list_retry else 1)
        ),
        "single dead-session retry": (
            text.count("htcleoSendResult == KErrServerTerminated") == 1
            and text.count("ReallyClose();") >= 2
            and text.count("TRAPD(htcleoReconnectResult, ConstructL())") == 1
            and text.count("htcleoSendResult = SendReceive(aServiceId") == 2
        ),
        "request identity trace": all(
            text.count(f"0x000003{stage}u") == 1
            for stage in ("10", "11", "12", "13", "14")
        ),
        "no timer or blanket normalization": (
            "User::After" not in SEND_NEW
            and "htcleoSendResult = KErrNone" not in SEND_NEW
        ),
        "fatal leave retained": text.count("User::LeaveIfError(htcleoSendResult)") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom MatrixMenu retry verification failed: " + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    path = (
        args.root
        / "sf/os/ossrv/lowlevellibsandfws/pluginfw/Framework/frame/EComSession.cpp"
    )
    text = path.read_text(encoding="utf-8")
    text = install(text)
    verify(text)
    path.write_text(text, encoding="utf-8")
    print(
        "HTCLEO_ECOM_MATRIXMENU_SERVER_RETRY="
        "sid-101f4cd2-keerrserverterminated-reconnect-once-310-314"
    )


if __name__ == "__main__":
    main()
