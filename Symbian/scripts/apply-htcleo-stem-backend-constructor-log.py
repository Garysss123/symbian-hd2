#!/usr/bin/env python3
"""Add fail-open durable checkpoints to the STEM OpenC backend constructor.

The ROM maps ``stem_backend.dll`` to ``sys\\bin\\backend.dll``.  Hardware
iteration 424 proved that its process-attach entrypoint is called but does not
return.  The image has exactly one C++ initializer: the global
``CLocalSystemInterface backend`` in localif.cpp.  This transform rebuilds that
same component from source and records every potentially blocking constructor
boundary in the already established ECOMLOG.TXT stream.

The logger uses only native RFs/RFile APIs, is fail-open, has no retry, delay,
display output or writable global state, and preserves all constructor return
values and fail-closed panics.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


MARKER = "HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG_V1"
HEADER_MARKER = "HTCLEO_STEM_BACKEND_FINDTIMER_EXPORT_FIX_V1"
MACRO = "__HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__"


LOGGER = r'''// HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG_V1
#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__
#include <f32file.h>

static void HtcleoStemBackendLog(TUint32 aStage, TInt aResult,
	TUint32 aDetail) __attribute__((noinline));

static void HtcleoStemBackendLog(TUint32 aStage, TInt aResult,
	TUint32 aDetail)
	{
	RFs fs;
	TInt r = fs.Connect();
	if (r != KErrNone)
		return;

	_LIT(KHtcleoStemLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoStemLogPath, "C:\\Symbian3\\ECOMLOG.TXT");
	r = fs.MkDirAll(KHtcleoStemLogDir);
	if (r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	r = file.Open(fs, KHtcleoStemLogPath, EFileWrite | EFileShareAny);
	if (r == KErrNotFound || r == KErrPathNotFound)
		r = file.Replace(fs, KHtcleoStemLogPath,
			EFileWrite | EFileShareAny);
	else if (r == KErrNone)
		r = file.Seek(ESeekEnd, position);

	if (r == KErrNone && position < (128 * 43))
		{
		_LIT8(KHtcleoStemLogPrefix, "HTCLEO_ECOM ");
		TBuf8<64> record;
		record.Append(KHtcleoStemLogPrefix);
		record.AppendNumFixedWidth((TUint)(position / 43), EHex, 2);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(_L8("\r\n"));
		r = file.Write(record);
		if (r == KErrNone)
			(void)file.Flush();
		}

	file.Close();
	fs.Close();
	}
#endif

'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label} anchor count is {text.count(old)}, expected 1")
    return text.replace(old, new, 1)


def verify_mmp(path: Path, root: Path) -> None:
    text = path.read_text(encoding="utf-8")
    source_root = f"{root.as_posix()}/sf/"
    host_include = (
        f'#include "{source_root}'
        'os/ossrv/genericopenlibs/openenvcore/libc/group/libcflags.mmpi"'
    )
    checks = {
        "target": text.count("TARGET            stem_backend.dll") == 1,
        "macro": text.count(f"MACRO {MACRO}") == 1,
        "prebuilt feature parity":
        text.count("MACRO SYMBIAN_OE_POSIX_SIGNALS") == 1
        and text.count("MACRO SYMBIAN_OE_LIBRT") == 1,
        "host preprocessor include": text.count(host_include) == 1,
        "host export definitions": text.count("DEFFILE") == 5
        and text.count(f"DEFFILE\t\t\t{source_root}") == 5,
        "raptor EPOC source roots": text.count("/sf/") >= 17,
        "no duplicated host root": f"{root.as_posix()}{root.as_posix()}" not in text,
        "efsrv": text.count("efsrv.lib") == 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("STEM backend MMP verification failed: " + ", ".join(failed))


def verify_source(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    stages = tuple(f"0x0000D1{index:02X}u" for index in range(1, 0x25))
    timezone_defer = "HTCLEO_STEM_BACKEND_TIMEZONE_DEFER_V1" in text
    checks = {
        "marker": text.count(MARKER) == 1,
        "logger definition": text.count("static void HtcleoStemBackendLog(") == 2,
        "one path": text.count("C:\\\\Symbian3\\\\ECOMLOG.TXT") == 1,
        "fixed record": text.count("128 * 43") == 1,
        "all stages": all(text.count(stage) == 1 for stage in stages),
        "stage count": text.count("HtcleoStemBackendLog(0x0000D1")
        == 36 + int(timezone_defer),
        "optional timezone stage": not timezone_defer
        or text.count("0x0000D125u") == 1,
        "no delay": "User::After" not in LOGGER,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "STEM backend constructor-log verification failed: "
            + ", ".join(failed)
        )


def install_mmp(path: Path, root: Path) -> None:
    text = path.read_text(encoding="utf-8")
    source_root = f"{root.as_posix()}/sf/"
    # Earlier host-path normalization must remain idempotent: ``/sf/`` is
    # also the suffix of the normalized path, so protect it before replacing
    # legacy absolute EPOC paths.  Collapse any interrupted older run first.
    repeated_root = rf"(?:{re.escape(root.as_posix())})+/sf/"
    text = re.sub(repeated_root, source_root, text)
    if f"MACRO {MACRO}" not in text:
        text = replace_once(
            text,
            "LANG            SC\n",
            f"LANG            SC\nMACRO {MACRO}\n",
            "MMP language",
        )
    feature_anchor = f"MACRO {MACRO}\n"
    plain_feature_macros = (
        "MACRO SYMBIAN_OE_POSIX_SIGNALS\n"
        "MACRO SYMBIAN_OE_LIBRT\n"
    )
    # Both symbols arrive pre-defined through bldvariant.hrh.  An MMP is run
    # through cpp before Raptor parses MACRO directives, so an unguarded
    # ``MACRO SYMBIAN_...`` would expand to an empty name.  Temporarily undef
    # them while emitting the compiler flags, then restore them for the MMP's
    # later conditional source/DEFFILE selection.
    feature_macros = (
        "#undef SYMBIAN_OE_POSIX_SIGNALS\n"
        "#undef SYMBIAN_OE_LIBRT\n"
        + plain_feature_macros
        + "#define SYMBIAN_OE_POSIX_SIGNALS 1\n"
        "#define SYMBIAN_OE_LIBRT 1\n"
    )
    if plain_feature_macros in text and feature_macros not in text:
        text = text.replace(plain_feature_macros, feature_macros, 1)
    elif "MACRO SYMBIAN_OE_POSIX_SIGNALS" not in text:
        text = replace_once(
            text,
            feature_anchor,
            feature_anchor + feature_macros,
            "STEM backend feature macros",
        )
    # Raptor resolves MMP SOURCEPATH/USERINCLUDE/DEFFILE paths beginning in
    # /sf against EPOCROOT.  Only the C preprocessor's quoted #include needs a
    # real host path; converting all directives would make Raptor prepend the
    # EPOCROOT twice.
    text = text.replace(source_root, "/sf/")
    legacy_include = (
        '#include "/sf/os/ossrv/genericopenlibs/openenvcore/'
        'libc/group/libcflags.mmpi"'
    )
    host_include = legacy_include.replace('"/sf/', f'"{source_root}')
    text = text.replace(legacy_include, host_include)
    text = re.sub(
        r"(DEFFILE\s+)/sf/",
        lambda match: match.group(1) + source_root,
        text,
    )
    path.write_text(text, encoding="utf-8")
    verify_mmp(path, root)


def install_source(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        verify_source(path)
        return

    text = replace_once(
        text,
        '#include "link.h"\n',
        '#include "link.h"\n' + LOGGER,
        "logger include",
    )

    text = replace_once(
        text,
        "\t\t{\n#ifdef SYMBIAN_OE_POSIX_SIGNALS\n"
        "\t\tiSignalsInitialized = EFalse;",
        "\t\t{\n#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D101u, KErrNone, 0u);\n#endif\n"
        "#ifdef SYMBIAN_OE_POSIX_SIGNALS\n"
        "\t\tiSignalsInitialized = EFalse;",
        "constructor entry",
    )

    signal_calls = (
        ("iSigInitWaitMutex.CreateLocal();", "D102"),
        ("iSigInitWaitSemaphore.CreateLocal(0);", "D103"),
        ("iBlockedSAMutex.CreateLocal();", "D104"),
        ("iSignalWaiterMutex.CreateLocal();", "D105"),
        ("iSignalInitSemaphore.CreateLocal(0);", "D106"),
    )
    for call, stage in signal_calls:
        text = replace_once(
            text,
            f"\t\t{call}\n",
            "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
            f"\t\tHtcleoStemBackendLog(0x0000{stage}u, {call[:-1]}, 0u);\n"
            "#else\n"
            f"\t\t{call}\n"
            "#endif\n",
            f"signal call {stage}",
        )

    text = replace_once(
        text,
        "\t\tconst TInt KMaxHeapSize = 1048576 ; // 1MB\n"
        "\t\tiPrivateHeap = UserHeap::ChunkHeap(NULL, KMinHeapSize, KMaxHeapSize);",
        "\t\tconst TInt KMaxHeapSize = 1048576 ; // 1MB\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D107u, KErrNone, (TUint32)KMaxHeapSize);\n"
        "#endif\n"
        "\t\tiPrivateHeap = UserHeap::ChunkHeap(NULL, KMinHeapSize, KMaxHeapSize);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D108u,\n"
        "\t\t\tiPrivateHeap ? KErrNone : KErrNoMemory,\n"
        "\t\t\t(TUint32)iPrivateHeap);\n"
        "#endif",
        "private heap",
    )

    text = replace_once(
        text,
        "\t\tRHeap* oldHeap = User::SwitchHeap(iPrivateHeap);\n\n"
        "\t\tTInt err = iFids.Init(iPrivateHeap);",
        "\t\tRHeap* oldHeap = User::SwitchHeap(iPrivateHeap);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D109u, KErrNone, (TUint32)oldHeap);\n"
        "#endif\n\n"
        "\t\tTInt err = iFids.Init(iPrivateHeap);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D10Au, err, (TUint32)iPrivateHeap);\n"
        "#endif",
        "heap switch and fid init",
    )

    text = replace_once(
        text,
        "\t\t\tCRedirDesc* redirMedia = new CRedirDesc();\n",
        "\t\t\tCRedirDesc* redirMedia = new CRedirDesc();\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\tHtcleoStemBackendLog(0x0000D10Bu,\n"
        "\t\t\t\tredirMedia ? KErrNone : KErrNoMemory,\n"
        "\t\t\t\t(TUint32)redirMedia);\n"
        "#endif\n",
        "redirect descriptor",
    )
    text = replace_once(
        text,
        "\t\t\t\tCStdErrDesc* errMedia = new CStdErrDesc();\n",
        "\t\t\t\tCStdErrDesc* errMedia = new CStdErrDesc();\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\t\tHtcleoStemBackendLog(0x0000D10Cu,\n"
        "\t\t\t\t\terrMedia ? KErrNone : KErrNoMemory,\n"
        "\t\t\t\t\t(TUint32)errMedia);\n"
        "#endif\n",
        "stderr descriptor",
    )
    text = replace_once(
        text,
        "\t\t\t\t\tiFids.Default(redirMedia, errMedia);\n",
        "\t\t\t\t\tiFids.Default(redirMedia, errMedia);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\t\t\tHtcleoStemBackendLog(0x0000D10Du, KErrNone, 3u);\n"
        "#endif\n",
        "default descriptors",
    )

    text = replace_once(
        text,
        "\t\tiTimerOverrunsMutex.CreateLocal(); //use backend heap\n",
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D10Eu,\n"
        "\t\t\tiTimerOverrunsMutex.CreateLocal(), 0u); //use backend heap\n"
        "#else\n"
        "\t\tiTimerOverrunsMutex.CreateLocal(); //use backend heap\n"
        "#endif\n",
        "timer mutex",
    )

    text = replace_once(
        text,
        "\t\tUser::SwitchHeap(oldHeap);\n\n"
        "\t\tif (!err)",
        "\t\tUser::SwitchHeap(oldHeap);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D10Fu, err, (TUint32)oldHeap);\n"
        "\t\tHtcleoStemBackendLog(0x0000D110u, err, 0u);\n"
        "#endif\n\n"
        "\t\tif (!err)",
        "restore heap",
    )
    text = replace_once(
        text,
        "\t\t\terr=iFs.Connect();\n",
        "\t\t\terr=iFs.Connect();\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\tHtcleoStemBackendLog(0x0000D111u, err, 0u);\n"
        "#endif\n",
        "RFs connect",
    )
    text = replace_once(
        text,
        "\t\t\t\terr = iFs.ShareAuto();\n",
        "\t\t\t\terr = iFs.ShareAuto();\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\t\tHtcleoStemBackendLog(0x0000D112u, err, 0u);\n"
        "#endif\n",
        "RFs share",
    )
    text = replace_once(
        text,
        "\t\t\t}\n\n\t\tif (!err)\n\t\t\t{\n"
        "\t\t\terr = PosixFilesystem::SetDefaultDir(iFs);",
        "\t\t\t}\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D113u, err, 0u);\n"
        "#endif\n\n\t\tif (!err)\n\t\t\t{\n"
        "\t\t\terr = PosixFilesystem::SetDefaultDir(iFs);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\tHtcleoStemBackendLog(0x0000D114u, err, 0u);\n"
        "#endif",
        "default directory",
    )
    text = replace_once(
        text,
        "\t\t\t}\n\n\t\t//Cache the session path",
        "\t\t\t}\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D115u, err, 0u);\n"
        "#endif\n\n\t\t//Cache the session path",
        "default directory merge",
    )
    text = replace_once(
        text,
        "\t\t\terr = iFs.SessionPath(iSessionPath);\n",
        "\t\t\terr = iFs.SessionPath(iSessionPath);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\t\tHtcleoStemBackendLog(0x0000D116u, err,\n"
        "\t\t\t\t(TUint32)iSessionPath.Length());\n"
        "#endif\n",
        "session path",
    )
    text = replace_once(
        text,
        "\n\n\t\tif(err == KErrNone)\n\t\t\t{\t\n"
        "\t\t\t//Create Server Locks",
        "\n#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D117u, err,\n"
        "\t\t\t(TUint32)iSessionPath.Length());\n"
        "#endif\n\n\t\tif(err == KErrNone)\n\t\t\t{\t\n"
        "\t\t\t//Create Server Locks",
        "session path merge",
    )

    lock_calls = (
        ("\t\t\terr |= iSSLock.CreateLocal();\n", "iSSLock", "D118"),
        ("\t\t\terr |= iCSLock.CreateLocal();\n", "iCSLock", "D119"),
        ("\t\t\terr |= iTLDListLock.CreateLocal();\n", "iTLDListLock", "D11A"),
        ("\t\t\terr |= iSessionPathLock.CreateLocal();\n", "iSessionPathLock", "D11B"),
        ("\t\t\terr |=  iASelectLock.CreateLocal();\n", "iASelectLock", "D11C"),
        ("\t        err |= iDefConnLock.CreateLocal();\n", "iDefConnLock", "D11D"),
    )
    for old, name, stage in lock_calls:
        new = (
            "\t\t\t{\n"
            f"\t\t\tTInt htcleoResult = {name}.CreateLocal();\n"
            "\t\t\terr |= htcleoResult;\n"
            "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
            f"\t\t\tHtcleoStemBackendLog(0x0000{stage}u, htcleoResult,\n"
            "\t\t\t\t(TUint32)err);\n"
            "#endif\n"
            "\t\t\t}\n"
        )
        text = replace_once(text, old, new, f"lock {name}")

    text = replace_once(
        text,
        "\t\t\t}\n\n        if(err == KErrNone)\n            {",
        "\t\t\t}\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D11Eu, err, 0u);\n"
        "\t\tHtcleoStemBackendLog(0x0000D11Fu, err, 0u);\n"
        "#endif\n\n        if(err == KErrNone)\n            {",
        "lock merge",
    )
    text = replace_once(
        text,
        "            err = iTzServer.Connect();\n",
        "            err = iTzServer.Connect();\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "            HtcleoStemBackendLog(0x0000D120u, err, 0u);\n"
        "#endif\n",
        "timezone connect",
    )
    text = replace_once(
        text,
        "                err = iTzServer.ShareAuto();\n",
        "                err = iTzServer.ShareAuto();\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "                HtcleoStemBackendLog(0x0000D121u, err, 0u);\n"
        "#endif\n",
        "timezone share",
    )
    text = replace_once(
        text,
        "            }\n\n\n\t\t//Panic if any of the above operation returns with error",
        "            }\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D122u, err, 0u);\n"
        "\t\tHtcleoStemBackendLog(0x0000D123u, err, 0u);\n"
        "#endif\n\n\n\t\t//Panic if any of the above operation returns with error",
        "timezone merge",
    )
    text = replace_once(
        text,
        "\t\tiCleanup.StorePtrs(iPrivateHeap, &iFs, &iSs, &iCs, &iSSLock, &iCSLock,&iDefConnLock,&iASelectLock);\n\n"
        "\t\t}",
        "\t\tiCleanup.StorePtrs(iPrivateHeap, &iFs, &iSs, &iCs, &iSSLock, &iCSLock,&iDefConnLock,&iASelectLock);\n"
        "#ifdef __HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG__\n"
        "\t\tHtcleoStemBackendLog(0x0000D124u, KErrNone, 0u);\n"
        "#endif\n\n\t\t}",
        "constructor exit",
    )

    path.write_text(text, encoding="utf-8")
    verify_source(path)


def install_header(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if HEADER_MARKER not in text:
        text = replace_once(
            text,
            "\tTInt FindTimer(const TInt& aTimerId);\n",
            "\tIMPORT_C TInt FindTimer(const TInt& aTimerId); "
            f"// {HEADER_MARKER}\n",
            "FindTimer frozen export declaration",
        )
        path.write_text(text, encoding="utf-8")
    installed = path.read_text(encoding="utf-8")
    if installed.count(HEADER_MARKER) != 1 or installed.count(
        "IMPORT_C TInt FindTimer(const TInt& aTimerId);"
    ) != 1:
        raise SystemExit("STEM backend FindTimer export verification failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    mmp = root / "sf/incubator/stemkit/breakdeps/backend.mmp"
    source = (
        root
        / "sf/os/ossrv/genericopenlibs/openenvcore/backend/src/corebackend/localif.cpp"
    )
    header = root / "sf/os/ossrv/genericopenlibs/openenvcore/backend/inc/sysif.h"
    if not mmp.is_file() or not source.is_file() or not header.is_file():
        raise SystemExit(
            f"missing STEM backend source: {mmp} / {source} / {header}"
        )

    install_mmp(mmp, root)
    install_header(header)
    install_source(source)
    print(
        "HTCLEO_STEM_BACKEND_CONSTRUCTOR_LOG=installed "
        "stages=D101-D124 path=C:\\Symbian3\\ECOMLOG.TXT"
    )


if __name__ == "__main__":
    main()
