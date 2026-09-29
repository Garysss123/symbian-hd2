#!/usr/bin/env python3
"""Install fail-open Hitchcock DLL process-attach tracing.

Iteration 436 proves that the first eight process-attach entrypoints return and
that the ninth entrypoint is exactly the start of ``hitchcock.dll``.  Keep the
stock GCCE DLL startup semantics, but define the target's ``_E32Dll_Body`` so
the existing CUSTLOG stream records the export-table and static-initializer
boundaries.  No screen probe, delay, retry, or error bypass is introduced.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MARKER = "HTCLEO_HITCHCOCK_ENTRYPOINT_DURABLE_LOG_V1"
ABI_MARKER = "HTCLEO_HITCHCOCK_FROZEN_EXPORT_COMPAT_V1"
MACRO = "__HTCLEO_HITCHCOCK_ENTRYPOINT_LOG__"
SOURCE_NAME = "htcleohitchcockentrytrace.cpp"


SOURCE = r'''// HTCLEO_HITCHCOCK_ENTRYPOINT_DURABLE_LOG_V1
#include <e32base.h>
#include <f32file.h>
#include <u32std.h>
#include "HuiFxScalarParameter.h"
#include "HuiFxColorParameter.h"

#ifdef __HTCLEO_HITCHCOCK_ENTRYPOINT_LOG__

// The frozen EABI exposes the scalar and colour template RTTI/vtables.  GCCE
// otherwise emits them only as weak COMDAT symbols, which old elf2e32 refuses
// to bind to the frozen DEF.  These ABI-identical out-of-line destructor
// specialisations provide each instantiation with a strong key function.
template <>
EXPORT_C CHuiFxGenericParameter<TReal32, RHuiFxScalarTimeLine,
    EParameterTypeScalar>::~CHuiFxGenericParameter()
    {
    delete iTimeLine;
    iTimeLine = NULL;
    }

template <>
EXPORT_C CHuiFxGenericParameter<TRgb, RHuiFxColorTimeLine,
    EParameterTypeColor>::~CHuiFxGenericParameter()
    {
    delete iTimeLine;
    iTimeLine = NULL;
    }

static void HtcleoHitchcockAttachLog(TUint32 aStage, TInt aResult,
                                      TUint32 aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;

    _LIT(KHtcleoCustLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoCustLogPath, "C:\\Symbian3\\CUSTLOG.TXT");
    r = fs.MkDirAll(KHtcleoCustLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    r = file.Open(fs, KHtcleoCustLogPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound || r == KErrPathNotFound)
        r = file.Replace(fs, KHtcleoCustLogPath,
                         EFileWrite | EFileShareAny);
    else if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);

    if (r == KErrNone && position < (512 * 67))
        {
        _LIT8(KHtcleoCustPrefix, "HTCLEO_CUST ");
        TBuf8<96> record;
        record.Append(KHtcleoCustPrefix);
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(User::TickCount(), EHex, 8);
        record.Append(_L8("\r\n"));
        r = file.Write(record);
        if (r == KErrNone)
            r = file.Flush();
        }
    file.Close();
    fs.Close();
    }

extern "C"
    {
    void __DLL_Export_Table__(void);
    void __cpp_initialize__aeabi_(void);
    __WEAK__ void run_static_dtors(void);

#if defined(__GCCE__)
    static int HtcleoAddressIsInCodeSegment(void* aAddress)
        {
        void* codeSegmentBase;
        void* codeSegmentLimit;
        asm(".extern Image$$ER_RO$$Base");
        asm(".extern Image$$ER_RO$$Limit");
        asm("htcleo_code_segment_limit:");
        asm(".word Image$$ER_RO$$Limit");
        asm("htcleo_code_segment_base:");
        asm(".word Image$$ER_RO$$Base");
        asm("ldr %[result], htcleo_code_segment_base"
            : [result] "=r" (codeSegmentBase));
        asm("ldr %[result], htcleo_code_segment_limit"
            : [result] "=r" (codeSegmentLimit));
        return aAddress >= codeSegmentBase && aAddress < codeSegmentLimit;
        }
#endif

    GLDEF_C TInt __wrap__E32Dll_Body(TInt aReason)
        {
        HtcleoHitchcockAttachLog(0x0000CC00u, aReason, 0u);
        if (aReason == KModuleEntryReasonProcessAttach)
            {
            HtcleoHitchcockAttachLog(0x0000CC01u, KErrNone, 0u);
            __DLL_Export_Table__();
            HtcleoHitchcockAttachLog(0x0000CC02u, KErrNone, 0u);
            HtcleoHitchcockAttachLog(0x0000CC03u, KErrNone, 0u);
            __cpp_initialize__aeabi_();
            HtcleoHitchcockAttachLog(0x0000CC04u, KErrNone, 0u);
            }
        else if (aReason == KModuleEntryReasonProcessDetach)
            {
#if defined(__GCCE__)
            if (HtcleoAddressIsInCodeSegment((void*)run_static_dtors))
                run_static_dtors();
#endif
            }
        HtcleoHitchcockAttachLog(0x0000CC05u, KErrNone,
                                  (TUint32)aReason);
        return KErrNone;
        }
    }

#endif
'''


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def ensure_patch(path: Path, old: str, new: str, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"{label}: missing file: {path}")
    text = path.read_text(encoding="utf-8").replace("\r", "")
    if new in text:
        return
    text = replace_once(text, old, new, label)
    path.write_text(text, encoding="utf-8", newline="\n")


def install_frozen_export_compatibility(root: Path) -> tuple[Path, ...]:
    api_source = (
        root
        / "sf/mw/uiaccelerator/uiaccelerator_plat/"
          "alf_core_toolkit_api/inc/uiacceltk"
    )
    api_export = root / "epoc32/include/platform/mw/uiacceltk"
    component_inc = (
        root
        / "sf/mw/uiaccelerator/uiacceltk/hitchcock/coretoolkit/inc"
    )

    flow_old = """    TBool ChildSize(TInt aOrdinal, TSize& aSize);
    
    TBool ChildPos(TInt aOrdinal, TPoint& aPos);

    TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);
"""
    flow_new = f"""    // {ABI_MARKER}
#ifdef {MACRO}
    IMPORT_C TBool ChildSize(TInt aOrdinal, TSize& aSize);
    IMPORT_C TBool ChildPos(TInt aOrdinal, TPoint& aPos);
    IMPORT_C TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);
#else
    TBool ChildSize(TInt aOrdinal, TSize& aSize);
    TBool ChildPos(TInt aOrdinal, TPoint& aPos);
    TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);
#endif
"""
    viewport_old = "    TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);\n"
    viewport_new = f"""    // {ABI_MARKER}
#ifdef {MACRO}
    IMPORT_C TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);
#else
    TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);
#endif
"""
    curve_old = "    TInt ChildRect(TInt aOrdinal, THuiRealRect& aRect);\n"
    curve_new = viewport_new
    texture_old = "        ~CTextureEntry();\n"
    texture_new = f"""        // {ABI_MARKER}
#ifdef {MACRO}
        IMPORT_C ~CTextureEntry();
#else
        ~CTextureEntry();
#endif
"""
    fx_old = """class CHuiFxGenericParameter: /*public CBase,*/ public MHuiFxParameter
"""
    fx_new = f"""// {ABI_MARKER}
#ifdef {MACRO}
class __attribute__((visibility(\"default\"))) CHuiFxGenericParameter:
    /*public CBase,*/ public MHuiFxParameter
#else
class CHuiFxGenericParameter: /*public CBase,*/ public MHuiFxParameter
#endif
"""

    patches = (
        (api_source / "HuiFlowLayout.h", flow_old, flow_new, "flow source ABI"),
        (api_export / "HuiFlowLayout.h", flow_old, flow_new, "flow export ABI"),
        (
            api_source / "huiviewportlayout.h",
            viewport_old,
            viewport_new,
            "viewport source ABI",
        ),
        (
            api_export / "huiviewportlayout.h",
            viewport_old,
            viewport_new,
            "viewport export ABI",
        ),
        (
            api_source / "HuiCurvePathLayout.h",
            curve_old,
            curve_new,
            "curve source ABI",
        ),
        (
            api_export / "HuiCurvePathLayout.h",
            curve_old,
            curve_new,
            "curve export ABI",
        ),
        (
            api_source / "HuiTextureManager.h",
            texture_old,
            texture_new,
            "texture source ABI",
        ),
        (
            api_export / "HuiTextureManager.h",
            texture_old,
            texture_new,
            "texture export ABI",
        ),
        (
            component_inc / "HuiFxParameter.h",
            fx_old,
            fx_new,
            "FX template ABI",
        ),
    )
    for path, old, new, label in patches:
        ensure_patch(path, old, new, label)
    return tuple(path for path, _, _, _ in patches)


def verify(
    mmp_path: Path, source_path: Path, abi_paths: tuple[Path, ...]
) -> None:
    mmp = mmp_path.read_text(encoding="utf-8").replace("\r", "")
    source = source_path.read_text(encoding="utf-8").replace("\r", "")
    stages = tuple(f"0x0000CC0{index}u" for index in range(6))
    checks = {
        "marker": source.count(MARKER) == 1,
        "target macro": mmp.count(f"MACRO          {MACRO}") == 1,
        "source membership": mmp.count(f"SOURCE          {SOURCE_NAME}") == 1,
        "obsolete ignored MMP option absent": "OPTION GCCE -fpermissive" not in mmp,
        "one wrapped body definition": source.count(
            "__wrap__E32Dll_Body(TInt aReason)"
        ) == 1,
        "two strong FX ABI specialisations": source.count(
            "::~CHuiFxGenericParameter()"
        ) == 2,
        "stock export call": source.count("__DLL_Export_Table__();") == 1,
        "stock initializer call": source.count("__cpp_initialize__aeabi_();") == 1,
        "stock GCCE dtor guard": source.count(
            "HtcleoAddressIsInCodeSegment((void*)run_static_dtors)"
        ) == 1,
        "six stages": all(source.count(stage) == 1 for stage in stages),
        "established path": source.count("C:\\\\Symbian3\\\\CUSTLOG.TXT") == 1,
        "no timing change": "User::After" not in source
        and "User::WaitForRequest" not in source,
        "no screen probe": "HalFunction" not in source and "UDF" not in source,
        "frozen ABI compatibility": all(
            path.read_text(encoding="utf-8").count(ABI_MARKER) == 1
            for path in abi_paths
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(
            "Hitchcock entrypoint trace verification failed: "
            + ", ".join(failed)
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()

    component = (
        args.root
        / "sf/mw/uiaccelerator/uiacceltk/hitchcock/coretoolkit"
    )
    mmp_path = component / "group/coretoolkit.mmp"
    source_path = component / "src" / SOURCE_NAME
    if not mmp_path.is_file():
        raise SystemExit(f"missing Hitchcock MMP: {mmp_path}")
    abi_paths = install_frozen_export_compatibility(args.root)

    mmp = mmp_path.read_text(encoding="utf-8").replace("\r", "")
    # SBSv2 deliberately ignores OPTION GCCE.  The isolated Raptor
    # hitchcock_permissive variant supplies this compiler compatibility flag.
    if "OPTION GCCE -fpermissive\n" in mmp:
        mmp = mmp.replace("OPTION GCCE -fpermissive\n", "", 1)
        mmp_path.write_text(mmp, encoding="utf-8", newline="\n")
    if source_path.is_file() and MARKER in source_path.read_text(
        encoding="utf-8"
    ):
        if source_path.read_text(encoding="utf-8").replace("\r", "") != SOURCE:
            source_path.write_text(SOURCE, encoding="utf-8", newline="\n")
        verify(mmp_path, source_path, abi_paths)
        print(
            "HTCLEO_HITCHCOCK_ENTRYPOINT_LOG=installed stages=CC00-CC05 "
            "frozen_abi=13"
        )
        return

    mmp = replace_once(
        mmp,
        "MACRO           SERIES_60\n",
        "MACRO           SERIES_60\n"
        f"MACRO          {MACRO}\n",
        "Hitchcock target options",
    )
    mmp = replace_once(
        mmp,
        '#include "huitk_base.mmp"\n',
        f"SOURCEPATH      ../src\nSOURCE          {SOURCE_NAME}\n\n"
        '#include "huitk_base.mmp"\n',
        "Hitchcock source membership",
    )
    mmp_path.write_text(mmp, encoding="utf-8", newline="\n")
    source_path.write_text(SOURCE, encoding="utf-8", newline="\n")
    verify(mmp_path, source_path, abi_paths)
    print(
        "HTCLEO_HITCHCOCK_ENTRYPOINT_LOG=installed stages=CC00-CC05 "
        "frozen_abi=13"
    )


if __name__ == "__main__":
    main()
