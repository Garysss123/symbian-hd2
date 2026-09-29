#!/usr/bin/env python3
"""Map qHD fixed layout lengths and reserve the real HomeScreen chrome."""

from __future__ import annotations

import argparse
from pathlib import Path

MARKER = "HTCLEO_XN_HD2_CLIENT_GEOMETRY_V1"
GUARD_MARKER = "HTCLEO_XN_NATIVE_PANEL_CONTRACT_V1"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"Xn geometry anchor mismatch: {old[:100]!r}")
    return text.replace(old, new, 1)


HELPERS = r'''
// HTCLEO_XN_HD2_CLIENT_GEOMETRY_V1
static TBool HtcleoXnHd2Geometry()
    {
    // HTCLEO_XN_NATIVE_PANEL_CONTRACT_V1
    // This transform belongs to the native HTCLEO ROM (physical 480x800).
    // WServ exposes an application screen mode, not panel identity. Querying
    // its SizeInPixels here also flushes IPC for every layout property.
    return RProcess().SecureId().iId == 0x102750f0u &&
        CCoeEnv::Static() != NULL;
    }

// Bounded layout transitions only; never a per-node/per-frame file trace.
void HtcleoXnGeometryLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
    {
    if (!HtcleoXnHd2Geometry())
        return;
    RFs fs;
    if (fs.Connect() != KErrNone)
        return;
    _LIT(KPath, "C:\\Symbian3\\HSXML.TXT");
    RFile file;
    TInt r = file.Open(fs, KPath, EFileWrite | EFileShareAny);
    if (r == KErrNotFound)
        r = file.Replace(fs, KPath, EFileWrite | EFileShareAny);
    TInt position = 0;
    if (r == KErrNone)
        r = file.Seek(ESeekEnd, position);
    if (r == KErrNone && position <= 1048576 - 128)
        {
        TBuf8<128> record;
        record.Append(_L8("HTCLEO_HGEO "));
        record.AppendNumFixedWidth((TUint32)position, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth(aDetail, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RProcess().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)RThread().Id().Id(), EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)User::NTickCount(), EHex, 8);
        record.Append('\n');
        (void)file.Write(record);
        }
    file.Close();
    fs.Close();
    }

static TUint32 HtcleoXnPackPoint(const TPoint& aPoint)
    {
    return ((TUint32)(aPoint.iX & 0xffff) << 16) |
        (TUint32)(aPoint.iY & 0xffff);
    }

'''

CLIENT = r'''void CXnUiEngineImpl::SetClientRectL( TRect aRect, TBool aDrawNow )
    {
    // HTCLEO_XN_HD2_REAL_CBA_INSET_V1
    if (HtcleoXnHd2Geometry())
        {
        CEikButtonGroupContainer* cba = iAppUiAdapter.Cba();
        if (cba)
            {
            // Rect is the already scaled, real screen-space CBA rectangle.
            // Do not scale this origin or the existing status-pane reduction.
            const TRect cbaRect(cba->Rect());
            if (!cbaRect.IsEmpty() && cbaRect.Width() == 480 &&
                cbaRect.iBr.iY == 800 && cbaRect.iTl.iY > aRect.iTl.iY &&
                cbaRect.Height() <= 160)
                aRect.iBr.iY = Min(aRect.iBr.iY, cbaRect.iTl.iY);
            }
        if (iClientRect != aRect)
            HtcleoXnGeometryLog(0x48581702u,
                (TInt)HtcleoXnPackPoint(aRect.iTl),
                HtcleoXnPackPoint(aRect.iBr));
        }
'''

RENDER = r'''    iAppUiAdapter.EffectManager()->UiRendered();

    // HTCLEO_XN_HD2_CBA_RENDER_COMMIT_V1
    // CPU presentation needs the real foreground chrome drawn after content.
    CCoeEnv* htcleoEnv = CCoeEnv::Static();
    if (HtcleoXnHd2Geometry() &&
        htcleoEnv->WsSession().GetFocusWindowGroup() ==
            htcleoEnv->RootWin().Identifier())
        {
        CEikButtonGroupContainer* cba = iAppUiAdapter.Cba();
        if (cba && cba->IsVisible())
            cba->MakeVisible(ETrue);
        }
'''


def patch_engine(text: str) -> str:
    if MARKER in text:
        text = text.replace("#include <EIKBTGPC.H>", "#include <eikbtgpc.h>")
        text = text.replace(
            "    static TInt count = 0;\n    if (count >= 24 || !HtcleoXnHd2Geometry())\n"
            "        return;\n    ++count;",
            "    if (!HtcleoXnHd2Geometry())\n        return;")
        # Migrate an unbuilt candidate without introducing writable DLL data.
        for stage in ("00", "01"):
            old = f'''                    static TBool logged = EFalse;
                    if (!logged && value > 1)
                        {{
                        logged = ETrue;
                        HtcleoXnGeometryLog(0x485817{stage}u,
                            static_cast<TInt>(value), (TUint32)pixels);
                        }}
'''
            text = text.replace(old, "")
        if GUARD_MARKER not in text:
            text = replace_once(text,
                '''static TBool HtcleoXnHd2Geometry()
    {
    CCoeEnv* env = CCoeEnv::Static();
    return RProcess().SecureId().iId == 0x102750f0u &&
        env && env->ScreenDevice()->SizeInPixels() == TSize(480, 800);
    }''',
                HELPERS[HELPERS.index("static TBool HtcleoXnHd2Geometry()"):
                        HELPERS.index("// Bounded layout transitions")].rstrip())
            text = replace_once(text,
                '''            const TRect screen(TPoint(0, 0),
                CCoeEnv::Static()->ScreenDevice()->SizeInPixels());
            cba->SetBoundingRect(screen);
            cba->MakeVisible(ETrue);''',
                '''            // Keep the existing physical CBA, already mapped by EikStd.
            cba->MakeVisible(ETrue);''')
            text = replace_once(text,
                '''    if (HtcleoXnHd2Geometry())
        {
        CEikButtonGroupContainer* cba = iAppUiAdapter.Cba();
        if (cba)
            {
            // Keep the existing physical CBA, already mapped by EikStd.''',
                '''    if (HtcleoXnHd2Geometry())
        {
        // One diagnostic query per activation, never per geometry property.
        const TSize logical = CCoeEnv::Static()->ScreenDevice()->SizeInPixels();
        HtcleoXnGeometryLog(0x48581712u,
            (TInt)HtcleoXnPackPoint(TPoint(logical.iWidth, logical.iHeight)),
            0x01e00320u);
        CEikButtonGroupContainer* cba = iAppUiAdapter.Cba();
        if (cba)
            {
            // Keep the existing physical CBA, already mapped by EikStd.''')
        return text
    text = replace_once(text, '#include <eikapp.h>\n',
                        '#include <eikapp.h>\n#include <eikbtgpc.h>\n#include <f32file.h>\n')
    text = replace_once(text, "// CONSTANTS\n", HELPERS + "// CONSTANTS\n")
    # Restrict the conversion to the two geometry-only property resolvers.
    # Percentage and dynamically computed Xn unit values are already physical.
    for axis, numerator, denominator, stage in (
        ("Horizontal", 480, 360, "00"), ("Vertical", 800, 640, "01")
    ):
        definition = text.index(f"// {axis}ValueToPixelsL()")
        start = text.index(
            f"static TInt {axis}ValueToPixelsL( CXnDomPropertyValue* aValue,\n",
            definition)
        end = text.index("\n    return 0;\n    }", start)
        section = text[start:end]
        anchor = "                return static_cast< TInt >( value );"
        addition = f'''                if (HtcleoXnHd2Geometry())
                    {{
                    const TReal mapped = value * {numerator}.0 / {denominator}.0;
                    const TInt pixels = static_cast<TInt>(
                        mapped + (mapped >= 0 ? 0.5 : -0.5));
                    return pixels;
                    }}
{anchor}'''
        section = replace_once(section, anchor, addition)
        text = text[:start] + section + text[end:]
    text = replace_once(text,
        "void CXnUiEngineImpl::SetClientRectL( TRect aRect, TBool aDrawNow )\n    {\n", CLIENT)
    text = replace_once(text,
        "    iAppUiAdapter.EffectManager()->UiRendered();\n", RENDER)
    # This is before the real SetClientRectL / ForceRenderUIL in view activation.
    text = replace_once(text,
        "    ReportScreenDeviceChangeL();\n            \n    SetClientRectL( iAppUiAdapter.ClientRect(), EFalse );",
        '''    ReportScreenDeviceChangeL();
    if (HtcleoXnHd2Geometry())
        {
        // One diagnostic query per activation, never per geometry property.
        const TSize logical = CCoeEnv::Static()->ScreenDevice()->SizeInPixels();
        HtcleoXnGeometryLog(0x48581712u,
            (TInt)HtcleoXnPackPoint(TPoint(logical.iWidth, logical.iHeight)),
            0x01e00320u);
        CEikButtonGroupContainer* cba = iAppUiAdapter.Cba();
        if (cba)
            {
            // Keep the existing physical CBA, already mapped by EikStd.
            cba->MakeVisible(ETrue);
            HtcleoXnGeometryLog(0x48581703u,
                (TInt)HtcleoXnPackPoint(cba->Rect().iTl),
                HtcleoXnPackPoint(cba->Rect().iBr));
            }
        }
    SetClientRectL( iAppUiAdapter.ClientRect(), EFalse );''')
    return text


FOCUS = r'''    // HTCLEO_XN_FIRST_VIEW_FOCUS_COMMIT_V1
    // Match the stock default-view timer's one-time exact-root handoff.
    // Later user-driven focus changes are never undone by this startup guard.
    if (!iFlags.IsSet(EHtcleoFirstViewCommitted) &&
        RProcess().SecureId().iId == 0x102750f0u)
        {
        iFlags.Set(EHtcleoFirstViewCommitted);
        CCoeEnv* env = CCoeEnv::Static();
        const TInt root = env->RootWin().Identifier();
        const TInt before = env->WsSession().GetFocusWindowGroup();
        HtcleoXnGeometryLog(0x48581710u, before, (TUint32)root);
        if (before != root)
            {
            env->WsSession().SetWindowGroupOrdinalPosition(root, 0);
            env->WsSession().Finish();
            }
        HtcleoXnGeometryLog(0x48581711u,
            env->WsSession().GetFocusWindowGroup(), (TUint32)root);
        CEikButtonGroupContainer* cba = iAppUiAdapter.Cba();
        if (cba)
            cba->MakeVisible(ETrue);
        }

'''


def patch_view(text: str) -> str:
    if "EHtcleoFirstViewCommitted\n" not in text:
        text = replace_once(text, "    EIsDestructionRunning\n",
                            "    EIsDestructionRunning,\n    EHtcleoFirstViewCommitted\n")
    if "HTCLEO_XN_FIRST_VIEW_FOCUS_COMMIT_V1" in text:
        text = text.replace(
            "    static TBool htcleoFirstViewCommitted = EFalse;\n"
            "    if (!htcleoFirstViewCommitted &&",
            "    if (!iFlags.IsSet(EHtcleoFirstViewCommitted) &&")
        text = text.replace("        htcleoFirstViewCommitted = ETrue;",
                            "        iFlags.Set(EHtcleoFirstViewCommitted);")
        return text
    # Use an internal DLL symbol, not a new E32 export.
    text = replace_once(text, '#include "xnviewadapter.h"\n',
        '#include "xnviewadapter.h"\n'
        'extern void HtcleoXnGeometryLog(TUint32, TInt, TUint32);\n')
    return replace_once(text,
        '    __TIME_ENDMARK( "CXnViewAdapter::DoActivateL, done", time );',
        FOCUS + '    __TIME_ENDMARK( "CXnViewAdapter::DoActivateL, done", time );')


def verify(engine: str, view: str) -> None:
    guard_start = engine.index("static TBool HtcleoXnHd2Geometry()")
    guard = engine[guard_start:engine.index("\n    }", guard_start)]
    checks = {
        "geometry marker": engine.count(MARKER) == 1,
        "native panel contract": engine.count(GUARD_MARKER) == 1
            and "ScreenDevice()->SizeInPixels()" not in guard,
        "logical size trace": engine.count("0x48581712u") == 1,
        "existing CBA": "cba->SetBoundingRect(screen);" not in engine,
        "axis conversions": engine.count("value * 480.0 / 360.0") == 1
            and engine.count("value * 800.0 / 640.0") == 1,
        "real CBA": engine.count("HTCLEO_XN_HD2_REAL_CBA_INSET_V1") == 1
            and "Min(aRect.iBr.iY, cbaRect.iTl.iY)" in engine,
        "focus once": view.count("HTCLEO_XN_FIRST_VIEW_FOCUS_COMMIT_V1") == 1
            and view.count("iFlags.Set(EHtcleoFirstViewCommitted);") == 1,
        "render commit": engine.count("HTCLEO_XN_HD2_CBA_RENDER_COMMIT_V1") == 1,
        "no replacement shell": "iApplicationRect =" not in engine,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("Xn HD2 geometry verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    src = args.root / "sf/app/homescreen/idlehomescreen/xmluirendering/uiengine/src"
    engine_path = src / "xnuiengineimpl.cpp"
    view_path = src / "xnviewadapter.cpp"
    engine = patch_engine(engine_path.read_text(encoding="utf-8"))
    view = patch_view(view_path.read_text(encoding="utf-8"))
    verify(engine, view)
    engine_path.write_text(engine, encoding="utf-8")
    view_path.write_text(view, encoding="utf-8")
    print("HTCLEO_XN_HD2_CLIENT_GEOMETRY=native-panel-contract-no-per-property-ipc-real-cba-inset-first-view-focus")


if __name__ == "__main__":
    main()
