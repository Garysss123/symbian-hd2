#!/usr/bin/env python3
"""Replace the Syborg hardware layer in a prepared full S60 ROM recipe.

The input must already have been normalised by prepare-full-rom-oby.py.  This
stage deliberately keeps the complete S60/Avkon payload and changes only the
machine-dependent boot/kernel/display/startup entries.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys


HTCLEO_VARID = "0x0c0b0001"
NATIVE_RELEASE = pathlib.PurePosixPath("/root/symbian/epoc32/release/armv5/urel")
FULL_RELEASE = pathlib.PurePosixPath("/root/symbian3-full/epoc32/release/armv5/urel")
FULL_DATA_Z = pathlib.PurePosixPath("/root/symbian3-full/epoc32/data/z")
HTCLEO_BSP = pathlib.PurePosixPath("/root/symbian/sf/adapt/htcleo")
PROJECT_ROOT = pathlib.PurePosixPath("/path/to/hd2-legacy-lab")
NONCELLULAR_CONFIG = PROJECT_ROOT / "Symbian/config/htcleo-noncellular"
HTCLEO_DEFAULT_SKIN_REPOSITORY = PROJECT_ROOT / (
    "Symbian/output/qsd8250-native-full-rom/"
    "htcleo-personalisation-101F876F.txt"
)
NVG_RESOURCE = pathlib.PurePosixPath(
    "/root/symbian3-full/epoc32/data/z/resource/plugins/nvgrenderstage.rsc"
)
LIBXML_SAX_BINARY = FULL_RELEASE / "xmlenginesaxplugin.dll"
LIBXML_SAX_RESOURCE = FULL_DATA_Z / "resource/plugins/xmlenginesaxplugin.rsc"
DEFAULT_SKIN_UID = "200259e6"
DEFAULT_SKIN_IMPORT = pathlib.PurePosixPath(
    "/root/symbian3-full/epoc32/data/z/private/10207114/import/200259E6"
)
DEFAULT_SKIN_RESOURCE = pathlib.PurePosixPath(
    "/root/symbian3-full/epoc32/data/z/resource/skins/200259E6"
)
PROFILE_PATH = pathlib.Path(__file__).resolve().parents[1] / (
    "config/htcleo-noncellular-profile.json"
)
PRODUCT_PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def profile_set(name: str) -> set[str]:
    values = PRODUCT_PROFILE.get(name)
    if not isinstance(values, list) or not values:
        raise SystemExit(f"invalid or empty product-profile list: {name}")
    normalized = {str(value).replace("/", "\\").lower() for value in values}
    if len(normalized) != len(values):
        raise SystemExit(f"duplicate product-profile destination: {name}")
    return normalized


PERMANENT_PRE_ESTART_NON_AUTOSTART = profile_set(
    "permanent_pre_estart_non_autostart"
)
TEMPORARY_PRE_ESTART_DEFERRED = profile_set(
    "temporary_pre_estart_deferred"
)
RESTORED_PRE_ESTART_EXTENSIONS = profile_set(
    "restored_pre_estart_extensions"
)
NONCELLULAR_PROVIDER_DESTINATIONS = profile_set(
    "noncellular_provider_destinations"
)
REQUIRED_RUNTIME_DESTINATIONS = profile_set("required_runtime_destinations")
DISABLED_RUNTIME_DESTINATIONS = profile_set("disabled_runtime_destinations")
RETAINED_CLIENT_COMPATIBILITY_DESTINATIONS = profile_set(
    "retained_client_compatibility_destinations"
)


def oby(kind: str, source: pathlib.PurePosixPath, destination: str,
        suffix: str = "") -> str:
    tagged = f"{kind}[{HTCLEO_VARID}]" if kind in {
        "primary", "variant", "extension", "device"
    } else kind
    return f'{tagged}={source} \t"{destination}"{suffix}'


REPLACEMENTS = {
    "sys\\bin\\ekern.exe": oby(
        "primary", NATIVE_RELEASE / "_htcleo_ekern.exe",
        "sys\\bin\\ekern.exe", "\tcode-align 0x4000"),
    "sys\\bin\\btracex.ldd": oby(
        "extension", NATIVE_RELEASE / "_htcleo_btracex.ldd",
        "sys\\bin\\btracex.ldd"),
    # Preserve ETel/SMS client ABI while preventing their C32 modules from
    # starting automatically in the non-cellular product profile.
    "private\\101f7988\\etel.cmi": oby(
        "data", NONCELLULAR_CONFIG / "etel.cmi",
        "private\\101f7988\\etel.cmi"),
    "private\\101f7988\\esock_smswap.cmi": oby(
        "data", NONCELLULAR_CONFIG / "esock_smswap.cmi",
        "private\\101f7988\\esock_smswap.cmi"),
    "private\\10202be9\\101f876f.txt": oby(
        "data", HTCLEO_DEFAULT_SKIN_REPOSITORY,
        "private\\10202be9\\101f876f.txt"),
    # Iteration 360 proved that the current all-at-once compatibility recipe
    # regresses before ESTART.  Preserve the complete-ROM payload and layout,
    # but do not auto-start the three debug-only extensions in the final
    # non-cellular product profile.  This is not a return to Syborg code.
    "sys\\bin\\exmoncommon.dll": oby(
        "device", NATIVE_RELEASE / "_htcleo_exmoncommon.dll",
        "sys\\bin\\exmoncommon.dll"),
    "sys\\bin\\exmondebug.dll": oby(
        "device", NATIVE_RELEASE / "_htcleo_exmondebug.dll",
        "sys\\bin\\exmondebug.dll"),
    "sys\\bin\\kdebug.dll": oby(
        "device", NATIVE_RELEASE / "kdebug.dll",
        "sys\\bin\\kdebug.dll"),
    # ELOCD is hardware-neutral, but it must be rebuilt with the same EKA2
    # source/ABI as the native media PDDs (not the older PDK export table).
    "sys\\bin\\elocd.ldd": oby(
        "extension", NATIVE_RELEASE / "elocd.ldd", "sys\\bin\\elocd.ldd"),
    "sys\\bin\\kasyborg.dll": oby(
        "variant", NATIVE_RELEASE / "_htcleo_kahtcleo.dll",
        "sys\\bin\\kahtcleo.dll"),
    "sys\\bin\\evfp.dll": oby(
        "extension", FULL_RELEASE / "evfp.dll", "sys\\bin\\evfp.dll"),
    "sys\\bin\\lcd.dll": oby(
        "extension", NATIVE_RELEASE / "_htcleo_lcd.dll", "sys\\bin\\lcd.dll"),
    "sys\\bin\\display0.ldd": oby(
        "device", NATIVE_RELEASE / "display.ldd", "sys\\bin\\display0.ldd"),
    "sys\\bin\\euart1.pdd": oby(
        "device", NATIVE_RELEASE / "_htcleo_euart1.pdd",
        "sys\\bin\\euart1.pdd"),
    "sys\\bin\\ecomm.ldd": oby(
        "device", NATIVE_RELEASE / "ecomm.ldd", "sys\\bin\\ecomm.ldd"),
    # Gate 14 and the persistent CBA are now hardware-proven.  Restore only the
    # required Type2A touch driver to normal kernel auto-extension loading for
    # Gate 15.  IRAM remained independently deferred so that iteration
    # has one attributable hardware change.
    "sys\\bin\\epointer.dll": oby(
        "extension", NATIVE_RELEASE / "_htcleo_epointer.dll",
        "sys\\bin\\epointer.dll"),
    "sys\\bin\\medint.pdd": oby(
        "device", NATIVE_RELEASE / "_htcleo_medint.pdd",
        "sys\\bin\\medint.pdd"),
    "sys\\bin\\ekeyb.dll": oby(
        # Gate21/1016: start the already-built native key driver at boot.
        "extension", NATIVE_RELEASE / "_htcleo_ekeyb.dll",
        "sys\\bin\\ekeyb.dll"),
    "sys\\bin\\soundsc.pdd": oby(
        "device", NATIVE_RELEASE / "_htcleo_soundsc.pdd",
        "sys\\bin\\soundsc.pdd"),
    "sys\\bin\\esoundsc.ldd": oby(
        "device", NATIVE_RELEASE / "esoundsc.ldd",
        "sys\\bin\\esoundsc.ldd"),
    "sys\\bin\\exstart.dll": oby(
        "extension", NATIVE_RELEASE / "exstart.dll", "sys\\bin\\exstart.dll"),
    "sys\\bin\\euser.dll": oby(
        "file", NATIVE_RELEASE / "_htcleo_euser.dll", "sys\\bin\\euser.dll"),
    "sys\\bin\\hal.dll": oby(
        "file", NATIVE_RELEASE / "_htcleo_hal.dll", "sys\\bin\\hal.dll"),
    "sys\\bin\\ekdata.dll": oby(
        "file", NATIVE_RELEASE / "_htcleo_ekdata.dll", "sys\\bin\\ekdata.dll"),
    "sys\\bin\\efile.exe": oby(
        "secondary", NATIVE_RELEASE / "efile.exe", "sys\\bin\\efile.exe"),
    # FAT is now source-built with the first-C MountL checkpoints.  Mapping it
    # explicitly also prevents the older PDK efat32.fsy from silently serving
    # as sys\bin\elocal.fsy after a successful native build.
    "sys\\bin\\elocal.fsy": oby(
        "file", NATIVE_RELEASE / "efat32.fsy", "sys\\bin\\elocal.fsy"),
    "sys\\bin\\estart.exe": oby(
        "file", NATIVE_RELEASE / "e32strt.exe", "sys\\bin\\estart.exe"),
    "sys\\data\\estart.txt": oby(
        "data", HTCLEO_BSP / "baseport/htcleo/rom/estart.txt",
        "sys\\data\\estart.txt"),
    "sys\\bin\\surfacemanagerdriver.ldd": oby(
        "extension", FULL_RELEASE / "surfacemanagerdriver.ldd",
        "sys\\bin\\surfacemanagerdriver.ldd"),
    # The PDK's libWFC.dll and libwfchwsyborg.dll are byte-identical.  Use the
    # hardware-neutral filename directly and remove the Syborg-only alias.
    "sys\\bin\\libwfchwsyborg.dll": oby(
        "file", FULL_RELEASE / "libWFC.dll", "sys\\bin\\libwfc.dll"),
    # The Syborg platform header expands ECOM_PLUGIN(file, resource) with
    # ``file,file`` and therefore drops the NVG implementation resource from
    # the already-expanded STEM recipe.  Replace the rebuilt implementation
    # explicitly and add its real registration resource below.
    "sys\\bin\\nvgrenderstage.dll": oby(
        "file", FULL_RELEASE / "nvgrenderstage.dll",
        "sys\\bin\\nvgrenderstage.dll"),
    # Iteration 414 source-builds the ECom client with UID-attributed durable
    # logging around the exact NVG implementation request.  The ABI and
    # registry server remain unchanged; only this client DLL is replaced.
    "sys\\bin\\ecom.dll": oby(
        "file", FULL_RELEASE / "ecom.dll", "sys\\bin\\ecom.dll"),
    # Iteration 425 rebuilds the exact STEM OpenC backend selected by the
    # complete ROM.  Its frozen 176-export ABI is retained; only fail-open
    # constructor checkpoints are added to the established ECOMLOG stream.
    "sys\\bin\\backend.dll": oby(
        "file", FULL_RELEASE / "stem_backend.dll", "sys\\bin\\backend.dll"),
    # Iteration 437 source-builds Hitchcock with its frozen 1-2011 export
    # prefix intact and adds durable process-attach/static-initializer stages.
    # The destination and every consumer-facing ordinal remain unchanged.
    "sys\\bin\\hitchcock.dll": oby(
        "file", FULL_RELEASE / "hitchcock.dll", "sys\\bin\\hitchcock.dll"),
    # Iteration 438 source-builds the process selected by the
    # KUikonUidPluginInterfaceNotifiers registration.  UID/SID/capabilities
    # and runtime destination stay unchanged; AKNCAP.TXT only records the
    # exact E32Main/application/document/AppUi construction frontier.
    "sys\\bin\\akncapserver.exe": oby(
        "file", FULL_RELEASE / "akncapserver.exe",
        "sys\\bin\\akncapserver.exe"),
    # Iteration 443 replaces the shared Eikon core only after proving that
    # frozen ordinals 1-594 retain their exact ABI. The ten appended GCCE
    # constructor aliases occupy new ordinals 595-604 and shift no consumer.
    # Runtime tracing is SID-gated to AknCapServer and performs only one
    # fail-open P&S Set per reached pre-factory boundary.
    "sys\\bin\\eikcore.dll": oby(
        "file", FULL_RELEASE / "eikcore.dll", "sys\\bin\\eikcore.dll"),
}


HTCLEO_SD_MEDIA_ENTRIES = [
    oby("extension", NATIVE_RELEASE / "_htcleo_epbussdiov.dll",
        "sys\\bin\\mmc.dll"),
    oby("extension", NATIVE_RELEASE / "epbussd.dll",
        "sys\\bin\\epbusm.dll"),
    oby("extension", NATIVE_RELEASE / "emmcptn.dll",
        "sys\\bin\\emmcptn.dll"),
    oby("extension", NATIVE_RELEASE / "medmmc.pdd",
        "sys\\bin\\medmmc.pdd"),
]


# CenRep 0x101F876F key 0x14 selects product skin 0x200259E6.  The prepared
# STEM recipe contains Haze/Jing and the Series60 fallback, but silently omits
# this selected Symbian skin.  Append the three stock assets at the end so all
# existing executable addresses/layout stay stable while AknSkins can resolve
# the real MatrixMenu background.
HTCLEO_DEFAULT_SKIN_ENTRIES = [
    oby("data", DEFAULT_SKIN_IMPORT / "Symbian.skn",
        f"private\\10207114\\import\\{DEFAULT_SKIN_UID}\\symbian.skn"),
    oby("data", DEFAULT_SKIN_RESOURCE / "Symbian.mbm",
        f"resource\\skins\\{DEFAULT_SKIN_UID}\\symbian.mbm"),
    oby("data", DEFAULT_SKIN_RESOURCE / "Symbian.mif",
        f"resource\\skins\\{DEFAULT_SKIN_UID}\\symbian.mif"),
]


# ChspsXMLHandler explicitly resolves variant "libxml2".  The Syborg STEM
# recipe carries only the legacy expat parser, so retain Nokia's stock SAX
# implementation and ECom resource as a required HomeScreen runtime pair.
HTCLEO_LIBXML_SAX_ENTRIES = [
    oby("file", LIBXML_SAX_BINARY, "sys\\bin\\xmlenginesaxplugin.dll"),
    oby("data", LIBXML_SAX_RESOURCE,
        "resource\\plugins\\xmlenginesaxplugin.rsc"),
]


# The PDK STEM recipe used for the original QEMU target does not include the
# Active Idle shell at all.  Gate 16 needs the stock Homescreen process behind
# MatrixMenu so the existing Back CBA action can send MatrixMenu to the
# background and reveal a real shell, rather than a blank framebuffer.
HTCLEO_HOMESCREEN_ENTRIES = [
    oby("file", FULL_RELEASE / "ailaunch.exe", "sys\\bin\\ailaunch.exe"),
    oby("file", FULL_RELEASE / "homescreen.exe", "sys\\bin\\homescreen.exe"),
    oby("file", FULL_RELEASE / "aiutils.dll", "sys\\bin\\aiutils.dll"),
    oby("file", FULL_RELEASE / "aiidleint.dll", "sys\\bin\\aiidleint.dll"),
    oby("file", FULL_RELEASE / "aifw.dll", "sys\\bin\\aifw.dll"),
    oby("file", FULL_RELEASE / "swiutils.dll", "sys\\bin\\swiutils.dll"),
    oby("data", FULL_DATA_Z / "resource/apps/homescreen.rsc",
        "resource\\apps\\homescreen.rsc"),
    oby("data", FULL_DATA_Z / "resource/apps/homescreen.r01",
        "resource\\apps\\homescreen.r01"),
    oby("data", FULL_DATA_Z / "resource/apps/homescreen_aif.mif",
        "resource\\apps\\homescreen_aif.mif"),
    oby("data", FULL_DATA_Z / "private/10003a3f/apps/homescreen_reg.rsc",
        "private\\10003a3f\\apps\\homescreen_reg.rsc"),
    # The original Syborg STEM image omitted the actual Active Idle product.
    # These binaries are the recursively resolved E32 import closure for the
    # XML controller, native fallback controller, HSPS/CPS services and the
    # non-cellular shell integrations used by the stock Symbian^3 HomeScreen.
    # Phone-facing libraries below are load dependencies of the stock native
    # fallback controller; their services remain non-autostart in HTCLEO.
    *[
        oby("file", FULL_RELEASE / name, f"sys\\bin\\{name}")
        for name in (
            "actionhandlerplugins.dll",
            "actionhandlerservice.dll",
            "Ai3NatiUi.dll",
            "ai3xmluimain.dll",
            "aicontainer.dll",
            "aiwsplugin.dll",
            "AKNSWALLPAPERUTILS.dll",
            "akntouchgesturefw.dll",
            "BrowserLauncher.dll",
            "bsclient.dll",
            "bsengine.exe",
            "bsservice.dll",
            "CbsMcnClient.dll",
            "ccclientsession.dll",
            "ccserver.exe",
            "ccsrvapi.dll",
            "chfactorysettingsplugin.dll",
            "chswiplugin.dll",
            "contentharvester.exe",
            "contentharvesterclient.dll",
            "ContentListingFramework.dll",
            "cpclient.dll",
            "cpserver.exe",
            "cpstorage.dll",
            "cpswrapper.dll",
            "cputils.dll",
            "extrenderingplugin.dll",
            "FileList.dll",
            "gsecomplugin.dll",
            "gsframework.dll",
            "harvesterclient.dll",
            "hsccapiclient.dll",
            "hsccproviderclient.dll",
            "hscontentcontrol.dll",
            "hscontentinfo.dll",
            "hspluginsettings.dll",
            "hspsclient.dll",
            "hspsclientsession.dll",
            "hspsdefinitionengine.dll",
            "hspsdefinitionengineinterface.dll",
            "hspsdefrep.dll",
            "hspsdomdocument.dll",
            "hspsodt.dll",
            "hspsprovider.dll",
            "hspsrequestclient.dll",
            "hspsresource.dll",
            "hspsresult.dll",
            "hspsservice.dll",
            "hspsthemeserver.exe",
            "hspswrapper.dll",
            "hswidgetpublisher.dll",
            "mcsextendedmenu.dll",
            "mcsplugin.dll",
            "mcspluginhandler.dll",
            "mcspluginsettings.dll",
            "mdccommon.dll",
            "mdeclient.dll",
            "MediaFileList.dll",
            "MemMan.dll",
            "MGFetch.dll",
            "networkhandling.dll",
            "Pbk2CommonUI.dll",
            "Pbk2Presentation.dll",
            "PbkExt.dll",
            "PbkView.dll",
            "PcsUtils.dll",
            "phoneclient.dll",
            "phonecntfinder.dll",
            "phonesettings.dll",
            "pluginvalidator.dll",
            "PsServerClientAPI.dll",
            "rfs.dll",
            "sapidataplugin.dll",
            "SpdCtrl.dll",
            "vmbx.dll",
            "VPbkEng.dll",
            "VPbkEngUtils.dll",
            "widgetmanager.dll",
            "wrtdataplugin.dll",
            "xn3animationfactory.dll",
            "xn3bitmapfactory.dll",
            "xn3clockfactory.dll",
            "xn3domdocument.dll",
            "xn3domvisitor.dll",
            "xn3ecomelementproxy.dll",
            "xn3layoutengine.dll",
            "xn3menufactory.dll",
            "xn3newstickerfactory.dll",
            "xn3nppluginfactory.dll",
            "xn3odt.dll",
            "xn3popupfactory.dll",
            "xn3resource.dll",
            "xn3texteditorfactory.dll",
            "xn3textfactory.dll",
            "xn3utils.dll",
            "xn3viewfactory.dll",
            "xn3volumecontrolfactory.dll",
        )
    ],
    # ECom registrations and English resources paired with the closure above.
    *[
        oby("data", FULL_DATA_Z / source, destination)
        for source, destination in (
            ("resource/plugins/ai3xmluimain.rsc", "resource\\plugins\\ai3xmluimain.rsc"),
            ("resource/plugins/ai3natiui.rsc", "resource\\plugins\\ai3natiui.rsc"),
            ("resource/plugins/aicontainer.rsc", "resource\\plugins\\aicontainer.rsc"),
            ("resource/apps/ai3xmlui.r01", "resource\\apps\\ai3xmlui.r01"),
            ("resource/apps/xnuiengine.r01", "resource\\apps\\xnuiengine.r01"),
            ("resource/apps/xnwallpaperview.r01", "resource\\apps\\xnwallpaperview.r01"),
            ("resource/apps/ainativeui.r01", "resource\\apps\\ainativeui.r01"),
            ("resource/plugins/xn3textfactory.rsc", "resource\\plugins\\xn3textfactory.rsc"),
            ("resource/plugins/xn3viewfactory.rsc", "resource\\plugins\\xn3viewfactory.rsc"),
            ("resource/plugins/xn3bitmapfactory.rsc", "resource\\plugins\\xn3bitmapfactory.rsc"),
            ("resource/plugins/xn3menufactory.rsc", "resource\\plugins\\xn3menufactory.rsc"),
            ("resource/plugins/xn3domvisitor.rsc", "resource\\plugins\\xn3domvisitor.rsc"),
            ("resource/plugins/xn3popupfactory.rsc", "resource\\plugins\\xn3popupfactory.rsc"),
            ("resource/plugins/xn3newstickerfactory.rsc", "resource\\plugins\\xn3newstickerfactory.rsc"),
            ("resource/plugins/xn3volumecontrolfactory.rsc", "resource\\plugins\\xn3volumecontrolfactory.rsc"),
            ("resource/plugins/xn3clockfactory.rsc", "resource\\plugins\\xn3clockfactory.rsc"),
            ("resource/plugins/xn3nppluginfactory.rsc", "resource\\plugins\\xn3nppluginfactory.rsc"),
            ("resource/plugins/xn3texteditorfactory.rsc", "resource\\plugins\\xn3texteditorfactory.rsc"),
            ("resource/plugins/xn3animationfactory.rsc", "resource\\plugins\\xn3animationfactory.rsc"),
            ("resource/plugins/hspsdefinitionengine.rsc", "resource\\plugins\\hspsdefinitionengine.rsc"),
            ("resource/plugins/hspsprovider.rsc", "resource\\plugins\\hspsprovider.rsc"),
            ("resource/plugins/cpclient.rsc", "resource\\plugins\\cpclient.rsc"),
            ("resource/plugins/chswiplugin.rsc", "resource\\plugins\\chswiplugin.rsc"),
            ("resource/plugins/chfactorysettingsplugin.rsc", "resource\\plugins\\chfactorysettingsplugin.rsc"),
            ("resource/plugins/actionhandlerplugins.rsc", "resource\\plugins\\actionhandlerplugins.rsc"),
            ("resource/plugins/actionhandlerservice.rsc", "resource\\plugins\\actionhandlerservice.rsc"),
            ("resource/plugins/bsservice.rsc", "resource\\plugins\\bsservice.rsc"),
            ("resource/plugins/widgetmanager.rsc", "resource\\plugins\\widgetmanager.rsc"),
            ("resource/plugins/mcsprovider.rsc", "resource\\plugins\\mcsprovider.rsc"),
            ("resource/plugins/mcsplugin.rsc", "resource\\plugins\\mcsplugin.rsc"),
            ("resource/plugins/mcspluginhandler.rsc", "resource\\plugins\\mcspluginhandler.rsc"),
            ("resource/plugins/mcspluginsettings.rsc", "resource\\plugins\\mcspluginsettings.rsc"),
            ("resource/plugins/sapidataplugin.rsc", "resource\\plugins\\sapidataplugin.rsc"),
            ("resource/plugins/wrtdataplugin.rsc", "resource\\plugins\\wrtdataplugin.rsc"),
        )
    ],
]


REMOVED_DESTINATIONS = {
    "sys\\bin\\svphostfsdriver.ldd",
    "sys\\bin\\svphostfsy.fsy",
    "sys\\bin\\svphostfs.exe",
    "sys\\bin\\svpsnapdriver.ldd",
    "sys\\bin\\snapapp.exe",
    "sys\\bin\\mednvmemory.pdd",
}

# Preserve the established 0x03a00000 ROM window when source-built UI
# components are larger than their historical RVCT binaries.  This is only a
# bundled media test sample; no player, codec, framework or user file is
# removed.  The final product goal does not require vendor QA sample media.
GOAL_IRRELEVANT_SPACE_RECLAIM_DESTINATIONS = {
    "private\\20011383\\mp3-250kb.mp3",
}


DESTINATION = re.compile(r'"([^"\r\n]+)"\s*(?:\s|$)')


def destination(line: str) -> str | None:
    quoted = DESTINATION.findall(line)
    if not quoted:
        return None
    return quoted[-1].replace("/", "\\").lower()


def active(line: str) -> bool:
    stripped = line.lstrip()
    return bool(stripped) and not stripped.upper().startswith("REM")


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} PREPARED_INPUT OUTPUT")

    source = pathlib.Path(sys.argv[1])
    output = pathlib.Path(sys.argv[2])
    text = source.read_text(encoding="utf-8", errors="strict").replace("\r", "")
    result: list[str] = []
    removed: list[str] = []
    space_reclaimed: set[str] = set()
    disabled_omitted: set[str] = set()
    replaced: set[str] = set()

    for raw in text.splitlines():
        if re.match(r"^romname=", raw, re.IGNORECASE):
            result.append("romname=htcleo_symbian3_full_native.img")
            continue
        if re.match(r"^bootbinary\s*=", raw, re.IGNORECASE):
            result.append(
                "bootbinary=/root/symbian/epoc32/release/armv5/"
                "_htcleo_bootloader_bootrom.bin"
            )
            continue

        dest = destination(raw)
        if dest in DISABLED_RUNTIME_DESTINATIONS:
            removed.append(raw)
            disabled_omitted.add(dest)
            result.append("REM HTCLEO disabled optional network startup/protocol: " + raw)
            continue
        if dest in REPLACEMENTS:
            result.append(REPLACEMENTS[dest])
            replaced.add(dest)
            if dest == "sys\\bin\\elocd.ldd":
                result.extend(HTCLEO_SD_MEDIA_ENTRIES)
            if dest == "sys\\bin\\nvgrenderstage.dll":
                result.append(oby(
                    "data", NVG_RESOURCE,
                    "resource\\plugins\\nvgrenderstage.rsc"
                ))
            continue
        if dest in REMOVED_DESTINATIONS:
            removed.append(raw)
            result.append("REM HTCLEO permanently omitted emulator-only component: " + raw)
            continue
        if dest in GOAL_IRRELEVANT_SPACE_RECLAIM_DESTINATIONS:
            removed.append(raw)
            space_reclaimed.add(dest)
            result.append(
                "REM HTCLEO omitted goal-irrelevant bundled media test sample: "
                + raw
            )
            continue
        if re.match(r"^\s*alias\b", raw, re.IGNORECASE) and \
                "libwfchwsyborg.dll" in raw.lower():
            removed.append(raw)
            result.append("REM HTCLEO removed obsolete Syborg libWFC alias: " + raw)
            continue

        result.append(re.sub("0x0b0a0001", HTCLEO_VARID, raw,
                             flags=re.IGNORECASE))

    existing_destinations = {
        destination(line) for line in result if active(line)
    }
    if disabled_omitted != DISABLED_RUNTIME_DESTINATIONS:
        raise SystemExit("disabled optional runtime resource set missing/changed")
    if existing_destinations & DISABLED_RUNTIME_DESTINATIONS:
        raise SystemExit("disabled optional runtime resource remains active")
    if space_reclaimed != GOAL_IRRELEVANT_SPACE_RECLAIM_DESTINATIONS:
        raise SystemExit(
            "goal-irrelevant ROM reclaim mismatch: "
            f"expected={sorted(GOAL_IRRELEVANT_SPACE_RECLAIM_DESTINATIONS)} "
            f"removed={sorted(space_reclaimed)}"
        )
    if existing_destinations & GOAL_IRRELEVANT_SPACE_RECLAIM_DESTINATIONS:
        raise SystemExit("goal-irrelevant ROM sample remains active")
    for skin_entry in HTCLEO_DEFAULT_SKIN_ENTRIES:
        skin_destination = destination(skin_entry)
        if skin_destination in existing_destinations:
            raise SystemExit(
                f"default skin destination already present: {skin_destination}"
            )
        result.append(skin_entry)
        existing_destinations.add(skin_destination)

    for parser_entry in HTCLEO_LIBXML_SAX_ENTRIES:
        parser_destination = destination(parser_entry)
        parser_source_match = re.match(r"^[^=]+=([^\s]+)", parser_entry)
        if not parser_source_match or not pathlib.Path(
                parser_source_match.group(1)).is_file():
            raise SystemExit(
                "libxml SAX source missing: "
                f"{parser_source_match.group(1) if parser_source_match else parser_entry}"
            )
        if parser_destination in existing_destinations:
            raise SystemExit(
                f"libxml SAX destination already present: {parser_destination}"
            )
        result.append(parser_entry)
        existing_destinations.add(parser_destination)

    for homescreen_entry in HTCLEO_HOMESCREEN_ENTRIES:
        homescreen_destination = destination(homescreen_entry)
        homescreen_source_match = re.match(r"^[^=]+=([^\s]+)", homescreen_entry)
        if not homescreen_source_match or not pathlib.Path(
                homescreen_source_match.group(1)).is_file():
            raise SystemExit(
                "homescreen source missing: "
                f"{homescreen_source_match.group(1) if homescreen_source_match else homescreen_entry}"
            )
        if homescreen_destination in existing_destinations:
            raise SystemExit(
                "homescreen destination already present: "
                f"{homescreen_destination}"
            )
        result.append(homescreen_entry)
        existing_destinations.add(homescreen_destination)

    missing = sorted(set(REPLACEMENTS) - replaced)
    if missing:
        raise SystemExit("missing expected full-ROM entries: " + ", ".join(missing))

    active_lines = [line for line in result if active(line)]
    active_text = "\n".join(active_lines).lower()
    if "0x0b0a0001" in active_text:
        raise SystemExit("old Syborg VARID remains in active recipe")
    if "_syborg_" in active_text or "/syborg/" in active_text or \
            "libwfchwsyborg" in active_text:
        raise SystemExit("active Syborg hardware reference remains in recipe")
    if "romlinearbase=0x12200000" not in active_text:
        raise SystemExit("full-ROM linear base contract was lost")

    active_by_destination: dict[str, list[str]] = {}
    for line in active_lines:
        if (dest := destination(line)) is not None:
            active_by_destination.setdefault(dest, []).append(line)

    for name in sorted(PERMANENT_PRE_ESTART_NON_AUTOSTART |
                       TEMPORARY_PRE_ESTART_DEFERRED):
        matching = active_by_destination.get(name, [])
        if (len(matching) != 1 or not matching[0].lower().startswith(
                f"device[{HTCLEO_VARID}]="
        )):
            raise SystemExit(
                f"pre-ESTART profile entry must be one inert ROM file: {name}"
            )

    for name in sorted(RESTORED_PRE_ESTART_EXTENSIONS):
        matching = active_by_destination.get(name, [])
        if (len(matching) != 1 or not matching[0].lower().startswith(
                f"extension[{HTCLEO_VARID}]="
        )):
            raise SystemExit(
                f"restored pre-ESTART extension is not active exactly once: {name}"
            )

    for name in sorted(NONCELLULAR_PROVIDER_DESTINATIONS):
        matching = active_by_destination.get(name, [])
        if len(matching) != 1 or not re.match(
                r"^(?:file|data)=", matching[0], re.IGNORECASE):
            raise SystemExit(
                f"cellular provider must remain packaged but non-autostart: {name}"
            )

    for group_name, names in (
        ("required runtime", REQUIRED_RUNTIME_DESTINATIONS),
        ("retained client compatibility",
         RETAINED_CLIENT_COMPATIBILITY_DESTINATIONS),
    ):
        for name in sorted(names):
            if len(active_by_destination.get(name, [])) != 1:
                raise SystemExit(f"{group_name} destination count != 1: {name}")

    nvg_resource_lines = active_by_destination.get(
        "resource\\plugins\\nvgrenderstage.rsc", []
    )
    if len(nvg_resource_lines) != 1 or str(NVG_RESOURCE) not in nvg_resource_lines[0]:
        raise SystemExit("NVGRenderStage ECom registration resource count/source mismatch")

    for skin_entry in HTCLEO_DEFAULT_SKIN_ENTRIES:
        skin_destination = destination(skin_entry)
        matching = active_by_destination.get(skin_destination or "", [])
        if len(matching) != 1:
            raise SystemExit(
                f"default product skin destination count != 1: {skin_destination}"
            )

    for homescreen_entry in HTCLEO_HOMESCREEN_ENTRIES:
        homescreen_destination = destination(homescreen_entry)
        matching = active_by_destination.get(homescreen_destination or "", [])
        if len(matching) != 1:
            raise SystemExit(
                "homescreen destination count != 1: "
                f"{homescreen_destination}"
            )

    for parser_entry in HTCLEO_LIBXML_SAX_ENTRIES:
        parser_destination = destination(parser_entry)
        matching = active_by_destination.get(parser_destination or "", [])
        if len(matching) != 1:
            raise SystemExit(
                "libxml SAX destination count != 1: "
                f"{parser_destination}"
            )

    required_sources = [
        pathlib.Path(str(path)) for path in (
            pathlib.PurePosixPath("/root/symbian/epoc32/release/armv5/") /
                "_htcleo_bootloader_bootrom.bin",
            NATIVE_RELEASE / "_htcleo_ekern.exe",
            NATIVE_RELEASE / "_htcleo_kahtcleo.dll",
            NATIVE_RELEASE / "_htcleo_euser.dll",
            NATIVE_RELEASE / "_htcleo_lcd.dll",
            NATIVE_RELEASE / "_htcleo_exmoncommon.dll",
            NATIVE_RELEASE / "_htcleo_exmondebug.dll",
            NATIVE_RELEASE / "kdebug.dll",
            NATIVE_RELEASE / "_htcleo_euart1.pdd",
            NATIVE_RELEASE / "ecomm.ldd",
            NATIVE_RELEASE / "elocd.ldd",
            NATIVE_RELEASE / "_htcleo_epointer.dll",
            NATIVE_RELEASE / "_htcleo_medint.pdd",
            NATIVE_RELEASE / "_htcleo_ekeyb.dll",
            NATIVE_RELEASE / "_htcleo_soundsc.pdd",
            NATIVE_RELEASE / "esoundsc.ldd",
            NATIVE_RELEASE / "_htcleo_hal.dll",
            NATIVE_RELEASE / "_htcleo_ekdata.dll",
            NATIVE_RELEASE / "display.ldd",
            NATIVE_RELEASE / "efile.exe",
            NATIVE_RELEASE / "efat32.fsy",
            NATIVE_RELEASE / "e32strt.exe",
            NATIVE_RELEASE / "exstart.dll",
            FULL_RELEASE / "evfp.dll",
            FULL_RELEASE / "elocd.ldd",
            FULL_RELEASE / "surfacemanagerdriver.ldd",
            FULL_RELEASE / "libWFC.dll",
            FULL_RELEASE / "nvgrenderstage.dll",
            FULL_RELEASE / "ecom.dll",
            FULL_RELEASE / "stem_backend.dll",
            FULL_RELEASE / "hitchcock.dll",
            FULL_RELEASE / "akncapserver.exe",
            FULL_RELEASE / "eikcore.dll",
            NVG_RESOURCE,
            LIBXML_SAX_BINARY,
            LIBXML_SAX_RESOURCE,
            DEFAULT_SKIN_IMPORT / "Symbian.skn",
            DEFAULT_SKIN_RESOURCE / "Symbian.mbm",
            DEFAULT_SKIN_RESOURCE / "Symbian.mif",
            FULL_RELEASE / "ailaunch.exe",
            FULL_RELEASE / "homescreen.exe",
            FULL_RELEASE / "aiutils.dll",
            FULL_RELEASE / "aiidleint.dll",
            FULL_RELEASE / "aifw.dll",
            FULL_RELEASE / "swiutils.dll",
            FULL_DATA_Z / "resource/apps/homescreen.rsc",
            FULL_DATA_Z / "resource/apps/homescreen.r01",
            FULL_DATA_Z / "resource/apps/homescreen_aif.mif",
            FULL_DATA_Z / "private/10003a3f/apps/homescreen_reg.rsc",
            NATIVE_RELEASE / "_htcleo_epbussdiov.dll",
            NATIVE_RELEASE / "epbussd.dll",
            NATIVE_RELEASE / "emmcptn.dll",
            NATIVE_RELEASE / "medmmc.pdd",
            HTCLEO_BSP / "baseport/htcleo/rom/estart.txt",
            NONCELLULAR_CONFIG / "etel.cmi",
            NONCELLULAR_CONFIG / "esock_smswap.cmi",
            HTCLEO_DEFAULT_SKIN_REPOSITORY,
        )
    ]
    absent = [str(path) for path in required_sources if not path.is_file()]
    if absent:
        raise SystemExit("missing required artifacts:\n" + "\n".join(absent))

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(result) + "\n", encoding="utf-8")
    output.with_suffix(output.suffix + ".removed").write_text(
        "\n".join(removed) + "\n", encoding="utf-8"
    )
    output.with_suffix(output.suffix + ".product-profile.json").write_text(
        json.dumps(PRODUCT_PROFILE, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"HTCLEO_FULL_RECIPE_OK replaced={len(replaced)} "
        f"removed={len(removed)} profile={PRODUCT_PROFILE['profile']} "
        f"space_reclaim={len(space_reclaimed)} "
        f"lines={len(result)} output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
