#!/usr/bin/env python3
"""Make MatrixMenu ECom list queries survive a terminated server session."""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_ECOM_MATRIXMENU_LIST_RETRY_V1"
FUNCTION_START = "void REComSession::ListImplementationsL(\n"
FUNCTION_SCOPE_ANCHOR = "\tconst TBool htcleoFeatMgrTrace =\n"
FUNCTION_SCOPE_NEW = r'''	// HTCLEO_ECOM_MATRIXMENU_LIST_RETRY_V1
	const TBool htcleoMatrixMenuList =
		(RProcess().SecureId().iId == 0x101F4CD2u);
	const TBool htcleoFeatMgrTrace =
'''

SEND_ANCHOR = '''\tTInt error= SendReceive(aServiceId,aArgs);\n'''

SEND_NEW = r'''	if(htcleoMatrixMenuList)
		HtcleoEcomLog(0x00000315u, aServiceId,
			(TUint32)aInterfaceUid.iUid);
	TInt error= SendReceive(aServiceId,aArgs);
	if(htcleoMatrixMenuList)
		HtcleoEcomLog(0x00000316u, error,
			(TUint32)aInterfaceUid.iUid);
	if(htcleoMatrixMenuList && error == KErrServerTerminated)
		{
		HtcleoEcomLog(0x00000317u, error,
			(TUint32)aInterfaceUid.iUid);
		ReallyClose();
		TRAPD(htcleoListReconnectResult, ConstructL());
		HtcleoEcomLog(0x00000318u, htcleoListReconnectResult,
			(TUint32)aInterfaceUid.iUid);
		if(htcleoListReconnectResult == KErrNone)
			{
			error = SendReceive(aServiceId,aArgs);
			}
		else
			{
			error = htcleoListReconnectResult;
			}
		HtcleoEcomLog(0x00000319u, error,
			(TUint32)aInterfaceUid.iUid);
		}
	if(htcleoMatrixMenuList && error == KErrServerTerminated)
		{
		// ListImplementationsL already defines no implementation as a valid
		// empty-list result.  MatrixMenu can therefore retain its normal
		// non-effect/non-plugin fallback without terminating the UI process.
		HtcleoEcomLog(0x0000031Au, error,
			(TUint32)aInterfaceUid.iUid);
		error = KEComErrNoInterfaceIdentified;
		}
'''


def install(text: str) -> str:
    if MARKER in text:
        return text
    start = text.find(FUNCTION_START)
    if start < 0:
        raise SystemExit("central ListImplementationsL: start not found")
    # Select the internal overload, not one of the exported wrappers.
    start = text.find("TInt aServiceId", start)
    if start < 0:
        raise SystemExit("central ListImplementationsL: service id not found")
    scope = text.find(FUNCTION_SCOPE_ANCHOR, start)
    if scope < 0:
        raise SystemExit("central ListImplementationsL: scope anchor not found")
    text = (
        text[:scope]
        + FUNCTION_SCOPE_NEW
        + text[scope + len(FUNCTION_SCOPE_ANCHOR) :]
    )
    send = text.find(SEND_ANCHOR, scope)
    if send < 0:
        raise SystemExit("central ListImplementationsL: SendReceive not found")
    text = text[:send] + SEND_NEW + text[send + len(SEND_ANCHOR) :]
    return text


def verify(text: str) -> None:
    home_screen_extended = "HTCLEO_ECOM_HOMESCREEN_LIST_RETRY_V1" in text
    menubar_extended = (
        "HTCLEO_ECOM_HOMESCREEN_MENUBAR_LIST_RETRY_V1" in text
    )
    checks = {
        "marker": text.count(MARKER) == 1,
        "MatrixMenu scope": (
            text.count("RProcess().SecureId().iId == 0x101F4CD2u") == 2
        ),
        "list retry once": (
            (
                (
                    not home_screen_extended
                    and text.count(
                        "htcleoMatrixMenuList && error == KErrServerTerminated"
                    ) == 2
                )
                or (
                    home_screen_extended
                    and text.count(
                        "htcleoUiShellList && error == KErrServerTerminated"
                    ) == (1 if menubar_extended else 2)
                )
            )
            and (
                not menubar_extended
                or text.count(
                    "htcleoUiShellListFailOpen && "
                    "error == KErrServerTerminated"
                ) == 1
            )
            and text.count("TRAPD(htcleoListReconnectResult, ConstructL())") == 1
            and text.count("error = SendReceive(aServiceId,aArgs)") == 1
        ),
        "natural empty-list fallback": (
            text.count("error = KEComErrNoInterfaceIdentified") == 1
            and text.count("0x0000031Au") == 1
        ),
        "trace stages": all(
            text.count(f"0x000003{stage}u") == 1
            for stage in ("15", "16", "17", "18", "19", "1A")
        ),
        "no timer": "User::After" not in SEND_NEW,
        "other errors retained": text.count("User::Leave(error)") >= 2,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "ECom MatrixMenu list retry verification failed: " + ", ".join(failed)
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
        "HTCLEO_ECOM_MATRIXMENU_LIST_RETRY="
        "sid-101f4cd2-reconnect-once-terminated-to-empty-315-31a"
    )


if __name__ == "__main__":
    main()
