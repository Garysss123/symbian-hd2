#!/usr/bin/env python3
"""Install fail-open durable tracing in the standard display render-stage DLL.

Iteration 427 proved WServ enters ``CScreen::ConstructL`` but does not return.
This transform keeps the original render-stage selection and error semantics,
while the sole DLL writer appends fixed records to ``C:\\Symbian3\\DSPRLOG.TXT``.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MACRO = "__HTCLEO_DISPLAY_DURABLE_LOG__"
MARKER = "HTCLEO_DISPLAY_DURABLE_LOG_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def declaration() -> str:
    return f'''
#ifdef {MACRO}
void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail);
#else
static inline void HtcleoDsprLog(TUint32, TInt, TUint32) {{}}
#endif
'''


def logger_body() -> str:
    return r'''
#ifdef __HTCLEO_DISPLAY_DURABLE_LOG__
// HTCLEO_DISPLAY_DURABLE_LOG_V1
void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
                         __attribute__((noinline));

void HtcleoDsprLog(TUint32 aStage, TInt aResult, TUint32 aDetail)
	{
	RFs fs;
	TInt r = fs.Connect();
	if(r != KErrNone)
		{
		return;
		}

	_LIT(KHtcleoDsprLogDir, "C:\\Symbian3\\");
	_LIT(KHtcleoDsprLogPath, "C:\\Symbian3\\DSPRLOG.TXT");
	r = fs.MkDirAll(KHtcleoDsprLogDir);
	if(r != KErrNone && r != KErrAlreadyExists)
		{
		fs.Close();
		return;
		}

	RFile file;
	TInt position = 0;
	if(aStage == 0x00001000u)
		{
		r = file.Replace(fs, KHtcleoDsprLogPath, EFileWrite | EFileShareAny);
		}
	else
		{
		r = file.Open(fs, KHtcleoDsprLogPath, EFileWrite | EFileShareAny);
		if(r == KErrNotFound || r == KErrPathNotFound)
			{
			r = file.Replace(fs, KHtcleoDsprLogPath, EFileWrite | EFileShareAny);
			}
		else if(r == KErrNone)
			{
			r = file.Seek(ESeekEnd, position);
			}
		}

	// Fixed 42-byte records; sequence derives from the append offset so the
	// E32 DLL has no writable logging globals.
	if(r == KErrNone && position < (256 * 42))
		{
		_LIT8(KHtcleoDsprPrefix, "HTCLEO_DSP ");
		TBuf8<64> record;
		record.Append(KHtcleoDsprPrefix);
		record.AppendNumFixedWidth((TUint)(position / 42), EHex, 2);
		record.Append(' ');
		record.AppendNumFixedWidth(aStage, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
		record.Append(' ');
		record.AppendNumFixedWidth(aDetail, EHex, 8);
		record.Append(_L8("\r\n"));
		r = file.Write(record);
		if(r == KErrNone)
			{
			r = file.Flush();
			}
		}

	file.Close();
	fs.Close();
	}
#else
void HtcleoDsprLog(TUint32, TInt, TUint32) {}
#endif

'''


def patch_plugin(source: str) -> str:
    if MARKER in source:
        return source
    source = replace_once(
        source,
        '#include <ecom/implementationproxy.h>\n',
        '#include <ecom/implementationproxy.h>\n'
        f'#ifdef {MACRO}\n#include <f32file.h>\n#endif\n',
        "plugin f32 include",
    )
    source = replace_once(
        source,
        '#include "fbrenderstagefactory.h"\n\n',
        '#include "fbrenderstagefactory.h"\n' + logger_body(),
        "plugin logger body",
    )
    source = replace_once(
        source,
        '\t{\n\taTableCount = (sizeof(KImplementationTable) / sizeof(TImplementationProxy));\n\treturn KImplementationTable;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001000u, KErrNone, 0u);\n'
        '\taTableCount = (sizeof(KImplementationTable) / sizeof(TImplementationProxy));\n'
        '\tHtcleoDsprLog(0x00001001u, KErrNone, (TUint32)aTableCount);\n'
        '\treturn KImplementationTable;\n\t}\n',
        "implementation proxy",
    )
    return source


def patch_display_factory(source: str) -> str:
    if "0x00001031u" in source:
        return source
    source = replace_once(source, '#include "panic.h"\n', '#include "panic.h"\n' + declaration(), "display factory declaration")
    source = replace_once(
        source,
        'CDisplayRenderStageFactory* CDisplayRenderStageFactory::CreateL()\n\t{\n\treturn new(ELeave) CDisplayRenderStageFactory;\n\t}\n',
        'CDisplayRenderStageFactory* CDisplayRenderStageFactory::CreateL()\n\t{\n'
        '\tHtcleoDsprLog(0x00001010u, KErrNone, 0u);\n'
        '\tCDisplayRenderStageFactory* factory = new(ELeave) CDisplayRenderStageFactory;\n'
        '\tHtcleoDsprLog(0x00001011u, KErrNone, (TUint32)(factory != NULL));\n'
        '\treturn factory;\n\t}\n',
        "display factory CreateL",
    )
    source = replace_once(
        source,
        '\t{\n\tBaseConstructL(aEnv);\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001020u, KErrNone, 0u);\n'
        '\tBaseConstructL(aEnv);\n'
        '\tHtcleoDsprLog(0x00001021u, KErrNone, 0u);\n\t}\n',
        "display factory ConstructL",
    )
    source = replace_once(
        source,
        '\t{\n\tCDisplayRenderStage* stage = CDisplayRenderStage::NewL(&Env(), aScreen, aScreenNumber);\n\treturn stage;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001030u, KErrNone, (TUint32)aScreenNumber);\n'
        '\tCDisplayRenderStage* stage = CDisplayRenderStage::NewL(&Env(), aScreen, aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001031u, KErrNone, (TUint32)(stage != NULL));\n'
        '\treturn stage;\n\t}\n',
        "display final-stage factory",
    )
    return source


def patch_display_stage(source: str) -> str:
    if "0x00001212u" in source:
        return source
    source = replace_once(source, '#include <bitdev.h>\n', '#include <bitdev.h>\n' + declaration(), "display stage declaration")
    source = replace_once(
        source,
        '\t{\n\tCDisplayRenderStage* stage = new(ELeave) CDisplayRenderStage(aScreenNumber);\n\tCleanupStack::PushL(stage);\n\tstage->ConstructL(aEnv, aScreen, aScreenNumber);\n\tCleanupStack::Pop(stage);\n\treturn stage;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001100u, KErrNone, (TUint32)aScreenNumber);\n'
        '\tCDisplayRenderStage* stage = new(ELeave) CDisplayRenderStage(aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001101u, KErrNone, (TUint32)(stage != NULL));\n'
        '\tCleanupStack::PushL(stage);\n'
        '\tHtcleoDsprLog(0x00001102u, KErrNone, 0u);\n'
        '\tstage->ConstructL(aEnv, aScreen, aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001103u, KErrNone, 0u);\n'
        '\tCleanupStack::Pop(stage);\n'
        '\tHtcleoDsprLog(0x00001104u, KErrNone, (TUint32)(stage != NULL));\n'
        '\treturn stage;\n\t}\n',
        "display stage NewL",
    )
    source = replace_once(
        source,
        '\t{\n\tBaseConstructL();\n\t\n\tMWsIniFile* iniFile',
        '\t{\n\tHtcleoDsprLog(0x00001200u, KErrNone, (TUint32)aScreenNumber);\n'
        '\tBaseConstructL();\n'
        '\tHtcleoDsprLog(0x00001201u, KErrNone, 0u);\n\t\n'
        '\tMWsIniFile* iniFile',
        "display ConstructL entry",
    )
    source = replace_once(
        source,
        '\tMWsIniFile* iniFile = aEnv->ObjectInterface<MWsIniFile>();\n\tSTD_ASSERT_ALWAYS(iniFile, EPluginPanicIniFileMissing);',
        '\tMWsIniFile* iniFile = aEnv->ObjectInterface<MWsIniFile>();\n'
        '\tHtcleoDsprLog(0x00001202u, KErrNone, (TUint32)(iniFile != NULL));\n'
        '\tSTD_ASSERT_ALWAYS(iniFile, EPluginPanicIniFileMissing);',
        "display ini interface",
    )
    source = replace_once(
        source,
        '\t//Initialise display policy and strategy segments\n\tiDisplayPolicy = CDisplayPolicy::NewL(aEnv,aScreen, aScreenNumber);\n\tiDisplayPolicyEnabled = iDisplayPolicy->PolicyEnabled();\n\t// initialize compositor\n\tiOpenWfcWrapper = COpenWfcWrapper::NewL(aScreenNumber, iDisplayPolicy);',
        '\t//Initialise display policy and strategy segments\n'
        '\tHtcleoDsprLog(0x00001203u, KErrNone, 0u);\n'
        '\tiDisplayPolicy = CDisplayPolicy::NewL(aEnv,aScreen, aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001204u, KErrNone, (TUint32)(iDisplayPolicy != NULL));\n'
        '\tiDisplayPolicyEnabled = iDisplayPolicy->PolicyEnabled();\n'
        '\tHtcleoDsprLog(0x00001205u, KErrNone, (TUint32)iDisplayPolicyEnabled);\n'
        '\t// initialize compositor\n'
        '\tHtcleoDsprLog(0x00001206u, KErrNone, 0u);\n'
        '\tiOpenWfcWrapper = COpenWfcWrapper::NewL(aScreenNumber, iDisplayPolicy);\n'
        '\tHtcleoDsprLog(0x00001207u, KErrNone, (TUint32)(iOpenWfcWrapper != NULL));',
        "display policy and OpenWFC",
    )
    source = replace_once(
        source,
        '\tiOpenWfcWrapperDisplayControl = iOpenWfcWrapper->GetInterface<MWsDisplayControl>();\n\tif(iOpenWfcWrapperDisplayControl)',
        '\tiOpenWfcWrapperDisplayControl = iOpenWfcWrapper->GetInterface<MWsDisplayControl>();\n'
        '\tHtcleoDsprLog(0x00001208u, KErrNone, (TUint32)(iOpenWfcWrapperDisplayControl != NULL));\n'
        '\tif(iOpenWfcWrapperDisplayControl)',
        "display control interface",
    )
    source = replace_once(
        source,
        '\t\tCleanupStack::PopAndDestroy(&resolutions);\n\t\t}\n\t\n\t\n\tUser::LeaveIfError(SgDriver::Open());\n\tUser::LeaveIfError(CDirectGdiDriver::Open());',
        '\t\tCleanupStack::PopAndDestroy(&resolutions);\n\t\t}\n'
        '\tHtcleoDsprLog(0x00001209u, KErrNone, (TUint32)(iOpenWfcWrapperDisplayControl != NULL));\n\t\n\t\n'
        '\tTInt htcleoResult = SgDriver::Open();\n'
        '\tHtcleoDsprLog(0x0000120Au, htcleoResult, 0u);\n'
        '\tUser::LeaveIfError(htcleoResult);\n'
        '\thtcleoResult = CDirectGdiDriver::Open();\n'
        '\tHtcleoDsprLog(0x0000120Bu, htcleoResult, 0u);\n'
        '\tUser::LeaveIfError(htcleoResult);',
        "display graphics drivers",
    )
    source = replace_once(
        source,
        '\tiDGdiDriver = CDirectGdiDriver::Static();\n\tUser::LeaveIfNull(iDGdiDriver);\n\t\n\t//Initialize the target \n\tCreateRenderTargetL(aScreenNumber, iniFile);',
        '\tiDGdiDriver = CDirectGdiDriver::Static();\n'
        '\tHtcleoDsprLog(0x0000120Cu, KErrNone, (TUint32)(iDGdiDriver != NULL));\n'
        '\tUser::LeaveIfNull(iDGdiDriver);\n\t\n'
        '\t//Initialize the target \n'
        '\tHtcleoDsprLog(0x0000120Du, KErrNone, 0u);\n'
        '\tCreateRenderTargetL(aScreenNumber, iniFile);\n'
        '\tHtcleoDsprLog(0x0000120Eu, KErrNone, (TUint32)(iRenderTarget != NULL));',
        "display target creation",
    )
    source = replace_once(
        source,
        '\tconst TSurfaceId& uiSurface = iRenderTarget->SurfaceId();\n\tUser::LeaveIfError(iOpenWfcWrapper->SetUiSurface(uiSurface));\n\t\n\tUser::LeaveIfError(iSurfaceUpdateSession.Connect());',
        '\tconst TSurfaceId& uiSurface = iRenderTarget->SurfaceId();\n'
        '\thtcleoResult = iOpenWfcWrapper->SetUiSurface(uiSurface);\n'
        '\tHtcleoDsprLog(0x0000120Fu, htcleoResult, 0u);\n'
        '\tUser::LeaveIfError(htcleoResult);\n\t\n'
        '\thtcleoResult = iSurfaceUpdateSession.Connect();\n'
        '\tHtcleoDsprLog(0x00001210u, htcleoResult, 0u);\n'
        '\tUser::LeaveIfError(htcleoResult);',
        "display surface connections",
    )
    source = replace_once(
        source,
        '\tiDisplayPolicy->SetCompositionInfo(displayConfig,displayConfig);\t//1 to 1 mapping\n\t\n\n\t\n\t// initialize the debug bar',
        '\tiDisplayPolicy->SetCompositionInfo(displayConfig,displayConfig);\t//1 to 1 mapping\n'
        '\tHtcleoDsprLog(0x00001211u, KErrNone, 0u);\n\t\n\n\t\n'
        '\t// initialize the debug bar',
        "display composition policy",
    )
    source = replace_once(
        source,
        '#endif\n\t}\n\nvoid CDisplayRenderStage::CreateRenderTargetL',
        '#endif\n\tHtcleoDsprLog(0x00001212u, KErrNone, 0u);\n\t}\n\n'
        'void CDisplayRenderStage::CreateRenderTargetL',
        "display ConstructL return",
    )
    return source


def patch_openwfc(source: str) -> str:
    if "0x00001320u" in source:
        return source
    source = replace_once(source, '#include <graphics/eglsynchelper.h>\n', '#include <graphics/eglsynchelper.h>\n' + declaration(), "OpenWFC declaration")
    source = replace_once(
        source,
        '\t{\n\tCOpenWfcWrapper* wrapper = new (ELeave) COpenWfcWrapper(aDisplayPolicy);\n\tCleanupStack::PushL(wrapper);\n\twrapper->ConstructL(aScreenNo);\n\tCleanupStack::Pop(wrapper);\n\treturn wrapper;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001300u, KErrNone, (TUint32)aScreenNo);\n'
        '\tCOpenWfcWrapper* wrapper = new (ELeave) COpenWfcWrapper(aDisplayPolicy);\n'
        '\tHtcleoDsprLog(0x00001301u, KErrNone, (TUint32)(wrapper != NULL));\n'
        '\tCleanupStack::PushL(wrapper);\n'
        '\tHtcleoDsprLog(0x00001302u, KErrNone, 0u);\n'
        '\twrapper->ConstructL(aScreenNo);\n'
        '\tHtcleoDsprLog(0x00001303u, KErrNone, 0u);\n'
        '\tCleanupStack::Pop(wrapper);\n'
        '\tHtcleoDsprLog(0x00001304u, KErrNone, (TUint32)(wrapper != NULL));\n'
        '\treturn wrapper;\n\t}\n',
        "OpenWFC NewL",
    )
    source = replace_once(
        source,
        'void COpenWfcWrapper::ConstructL(TInt aScreenId)\n\t{\n#ifdef _DEBUG',
        'void COpenWfcWrapper::ConstructL(TInt aScreenId)\n\t{\n'
        '\tHtcleoDsprLog(0x00001310u, KErrNone, (TUint32)aScreenId);\n'
        '#ifdef _DEBUG',
        "OpenWFC ConstructL entry",
    )
    source = replace_once(
        source,
        '    iScreenNumber = aScreenId;\n    WFCint filterList[] = { WFC_DEVICE_FILTER_SCREEN_NUMBER, iScreenNumber, WFC_NONE};\n\n    iEGLDisplay = eglGetDisplay(EGL_DEFAULT_DISPLAY);\n    eglInitialize(iEGLDisplay, NULL, NULL);\n        \n    WFCint dev = 0;\n    if ((wfcEnumerateDevices(&dev, 1, filterList) == 1) &&\n        (dev != WFC_INVALID_HANDLE))',
        '    iScreenNumber = aScreenId;\n'
        '    WFCint filterList[] = { WFC_DEVICE_FILTER_SCREEN_NUMBER, iScreenNumber, WFC_NONE};\n'
        '    HtcleoDsprLog(0x00001311u, KErrNone, (TUint32)iScreenNumber);\n\n'
        '    HtcleoDsprLog(0x00001312u, KErrNone, 0u);\n'
        '    iEGLDisplay = eglGetDisplay(EGL_DEFAULT_DISPLAY);\n'
        '    HtcleoDsprLog(0x00001313u, KErrNone, (TUint32)(iEGLDisplay != EGL_NO_DISPLAY));\n'
        '    EGLBoolean htcleoEglResult = eglInitialize(iEGLDisplay, NULL, NULL);\n'
        '    HtcleoDsprLog(0x00001314u, (TInt)htcleoEglResult, 0u);\n        \n'
        '    WFCint dev = 0;\n'
        '    WFCint htcleoDeviceCount = wfcEnumerateDevices(&dev, 1, filterList);\n'
        '    HtcleoDsprLog(0x00001315u, (TInt)htcleoDeviceCount, (TUint32)dev);\n'
        '    if ((htcleoDeviceCount == 1) &&\n        (dev != WFC_INVALID_HANDLE))',
        "OpenWFC EGL and enumeration",
    )
    source = replace_once(
        source,
        '        // clean previous errors\n        wfcGetError(iDevice);\n    \n        // Let\'s get the device handle, opening in the same time the device\n        iDevice = wfcCreateDevice(dev, NULL);',
        '        // clean previous errors\n'
        '        WFCErrorCode htcleoPreviousError = wfcGetError(iDevice);\n'
        '        HtcleoDsprLog(0x00001316u, (TInt)htcleoPreviousError, 0u);\n    \n'
        '        // Let\'s get the device handle, opening in the same time the device\n'
        '        HtcleoDsprLog(0x00001317u, KErrNone, (TUint32)dev);\n'
        '        iDevice = wfcCreateDevice(dev, NULL);\n'
        '        HtcleoDsprLog(0x00001318u, KErrNone, (TUint32)iDevice);',
        "OpenWFC device creation",
    )
    source = replace_once(
        source,
        '        iOnScreenContext = wfcCreateOnScreenContext(iDevice, iScreenNumber, NULL);\n        if (iOnScreenContext==NULL)',
        '        HtcleoDsprLog(0x00001319u, KErrNone, (TUint32)iScreenNumber);\n'
        '        iOnScreenContext = wfcCreateOnScreenContext(iDevice, iScreenNumber, NULL);\n'
        '        HtcleoDsprLog(0x0000131Au, KErrNone, (TUint32)iOnScreenContext);\n'
        '        if (iOnScreenContext==NULL)',
        "OpenWFC context creation",
    )
    source = replace_once(
        source,
        '        wfcSetContextAttribi(iDevice, iOnScreenContext, WFC_CONTEXT_ROTATION, WFC_ROTATION_0);\n        wfcSetContextAttribi(iDevice, iOnScreenContext, WFC_CONTEXT_BG_COLOR, KRgbaBlack);\n        \n        iContextDisplayControl = NULL;\n        \n        User::LeaveIfNull(iJobManager = COpenWfcJobManger::NewL(*this, iDevice, iOnScreenContext, iScreenNumber));',
        '        wfcSetContextAttribi(iDevice, iOnScreenContext, WFC_CONTEXT_ROTATION, WFC_ROTATION_0);\n'
        '        wfcSetContextAttribi(iDevice, iOnScreenContext, WFC_CONTEXT_BG_COLOR, KRgbaBlack);\n'
        '        HtcleoDsprLog(0x0000131Bu, KErrNone, 0u);\n        \n'
        '        iContextDisplayControl = NULL;\n        \n'
        '        HtcleoDsprLog(0x0000131Cu, KErrNone, 0u);\n'
        '        iJobManager = COpenWfcJobManger::NewL(*this, iDevice, iOnScreenContext, iScreenNumber);\n'
        '        HtcleoDsprLog(0x0000131Du, KErrNone, (TUint32)(iJobManager != NULL));\n'
        '        User::LeaveIfNull(iJobManager);',
        "OpenWFC attributes and job manager",
    )
    source = replace_once(
        source,
        '    else\n        {\n        // we cannot continue because we cannot find a device for the given screenId',
        '    else\n        {\n'
        '        HtcleoDsprLog(0xE0001315u, KErrArgument, (TUint32)dev);\n'
        '        // we cannot continue because we cannot find a device for the given screenId',
        "OpenWFC no-device branch",
    )
    source = replace_once(
        source,
        '    iSurfaceManager.Open();\n\n    iSourceMap.Reserve(iInitialSourceMapSize);\n    }',
        '    iSurfaceManager.Open();\n'
        '    HtcleoDsprLog(0x0000131Eu, KErrNone, 0u);\n\n'
        '    iSourceMap.Reserve(iInitialSourceMapSize);\n'
        '    HtcleoDsprLog(0x0000131Fu, KErrNone, (TUint32)iInitialSourceMapSize);\n'
        '    HtcleoDsprLog(0x00001320u, KErrNone, 0u);\n'
        '    }',
        "OpenWFC final setup",
    )
    return source


def patch_render_target(source: str) -> str:
    if "0x00001614u" in source:
        return source
    source = replace_once(source, '#include "utils.h"\n', '#include "utils.h"\n' + declaration(), "render target declaration")
    source = replace_once(
        source,
        'void RWsOffScreenImageTarget::OpenL(TUint32 aUsage, TSgCpuAccess aCpuAccess, TUidPixelFormat aPixelFormat, const TSize& aSize, TInt aScreenNumber)\n\t{\n\tCDirectGdiDriver* theDGdiDriver = CDirectGdiDriver::Static();',
        'void RWsOffScreenImageTarget::OpenL(TUint32 aUsage, TSgCpuAccess aCpuAccess, TUidPixelFormat aPixelFormat, const TSize& aSize, TInt aScreenNumber)\n\t{\n\tHtcleoDsprLog(0x00001600u, (TInt)aPixelFormat,\n'
        '\t\t((TUint32)(aSize.iWidth & 0xFFFF) << 16) | (TUint32)(aSize.iHeight & 0xFFFF));\n'
        '\tCDirectGdiDriver* theDGdiDriver = CDirectGdiDriver::Static();\n'
        '\tHtcleoDsprLog(0x00001601u, KErrNone, (TUint32)(theDGdiDriver != NULL));',
        "offscreen target OpenL entry",
    )
    source = replace_once(
        source,
        '\tiImageInfos[CRenderTarget::EInvertedAspectRatio].iSizeInPixels.SetSize(aSize.iHeight, aSize.iWidth);\n\n\tconst TInt KImageCount = 1;\n\tUser::LeaveIfError(RSgImageCollection::Create(iImageInfos, KImageCount, iImageCollections, CRenderTarget::EAspectRatioCount));',
        '\tiImageInfos[CRenderTarget::EInvertedAspectRatio].iSizeInPixels.SetSize(aSize.iHeight, aSize.iWidth);\n'
        '\tHtcleoDsprLog(0x00001602u, KErrNone, (TUint32)aScreenNumber);\n\n'
        '\tconst TInt KImageCount = 1;\n'
        '\tTInt htcleoResult = RSgImageCollection::Create(iImageInfos, KImageCount, iImageCollections, CRenderTarget::EAspectRatioCount);\n'
        '\tHtcleoDsprLog(0x00001603u, htcleoResult, (TUint32)CRenderTarget::EAspectRatioCount);\n'
        '\tUser::LeaveIfError(htcleoResult);',
        "SG collection creation",
    )
    source = replace_once(
        source,
        '\tfor(TInt ii = 0; ii < CRenderTarget::EAspectRatioCount; ii++)\n\t\t{\n\t\tUser::LeaveIfError(iImageCollections[ii].GetInfo(iImageInfos[ii])); //should be the same as requested, this is just belt and braces\n\t\tUser::LeaveIfError(iImageCollections[ii].OpenImage(0, iImages[ii]));\n\t\tiImageTargets[ii] = RDirectGdiImageTarget(*theDGdiDriver);\n\t\tUser::LeaveIfError(iImageTargets[ii].Create(iImages[ii]));\n\t\t}\n\t}',
        '\tfor(TInt ii = 0; ii < CRenderTarget::EAspectRatioCount; ii++)\n\t\t{\n'
        '\t\tHtcleoDsprLog(0x00001610u, KErrNone, (TUint32)ii);\n'
        '\t\thtcleoResult = iImageCollections[ii].GetInfo(iImageInfos[ii]); //should be the same as requested, this is just belt and braces\n'
        '\t\tHtcleoDsprLog(0x00001611u, htcleoResult, (TUint32)ii);\n'
        '\t\tUser::LeaveIfError(htcleoResult);\n'
        '\t\thtcleoResult = iImageCollections[ii].OpenImage(0, iImages[ii]);\n'
        '\t\tHtcleoDsprLog(0x00001612u, htcleoResult, (TUint32)ii);\n'
        '\t\tUser::LeaveIfError(htcleoResult);\n'
        '\t\tiImageTargets[ii] = RDirectGdiImageTarget(*theDGdiDriver);\n'
        '\t\thtcleoResult = iImageTargets[ii].Create(iImages[ii]);\n'
        '\t\tHtcleoDsprLog(0x00001613u, htcleoResult, (TUint32)ii);\n'
        '\t\tUser::LeaveIfError(htcleoResult);\n'
        '\t\t}\n'
        '\tHtcleoDsprLog(0x00001614u, KErrNone, (TUint32)CRenderTarget::EAspectRatioCount);\n\t}',
        "offscreen target loop",
    )
    source = replace_once(
        source,
        '\t{\n\tCRenderTarget* self=new(ELeave) CRenderTarget();\n\tCleanupStack::PushL(self);\n\tself->ConstructL(aIniFile, aUsage, aCpuAccess, aDisplayMode, aSize, aScreenNumber);\n\tCleanupStack::Pop(self);\n\treturn self;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001500u, (TInt)aDisplayMode, (TUint32)aScreenNumber);\n'
        '\tCRenderTarget* self=new(ELeave) CRenderTarget();\n'
        '\tHtcleoDsprLog(0x00001501u, KErrNone, (TUint32)(self != NULL));\n'
        '\tCleanupStack::PushL(self);\n'
        '\tHtcleoDsprLog(0x00001502u, KErrNone, 0u);\n'
        '\tself->ConstructL(aIniFile, aUsage, aCpuAccess, aDisplayMode, aSize, aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001503u, KErrNone, 0u);\n'
        '\tCleanupStack::Pop(self);\n'
        '\tHtcleoDsprLog(0x00001504u, KErrNone, (TUint32)(self != NULL));\n'
        '\treturn self;\n\t}\n',
        "render target NewL",
    )
    source = replace_once(
        source,
        '\t{\n\tCDirectGdiDriver* theDGdiDriver = CDirectGdiDriver::Static();\n\tif(!theDGdiDriver)',
        '\t{\n\tHtcleoDsprLog(0x00001510u, (TInt)aDisplayMode, (TUint32)aScreenNumber);\n'
        '\tCDirectGdiDriver* theDGdiDriver = CDirectGdiDriver::Static();\n'
        '\tHtcleoDsprLog(0x00001511u, KErrNone, (TUint32)(theDGdiDriver != NULL));\n'
        '\tif(!theDGdiDriver)',
        "render target ConstructL entry",
    )
    source = replace_once(
        source,
        '\tiTarget.OpenL(aUsage, aCpuAccess, SgUtils::DisplayModeToPixelFormat(aDisplayMode), aSize, aScreenNumber);\n\tiDirectGdiGcWrapper = CDirectGdiGcWrapper::NewL();\n\tUser::LeaveIfError(iDirectGdiGcWrapper->DirectGdiGc().Activate(iTarget.iImageTargets[iCurrentAspectRatio]));',
        '\tHtcleoDsprLog(0x00001512u, KErrNone, (TUint32)aDisplayMode);\n'
        '\tiTarget.OpenL(aUsage, aCpuAccess, SgUtils::DisplayModeToPixelFormat(aDisplayMode), aSize, aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001513u, KErrNone, 0u);\n'
        '\tiDirectGdiGcWrapper = CDirectGdiGcWrapper::NewL();\n'
        '\tHtcleoDsprLog(0x00001514u, KErrNone, (TUint32)(iDirectGdiGcWrapper != NULL));\n'
        '\tTInt htcleoResult = iDirectGdiGcWrapper->DirectGdiGc().Activate(iTarget.iImageTargets[iCurrentAspectRatio]);\n'
        '\tHtcleoDsprLog(0x00001515u, htcleoResult, (TUint32)iCurrentAspectRatio);\n'
        '\tUser::LeaveIfError(htcleoResult);',
        "render target core construction",
    )
    source = replace_once(
        source,
        '#endif\n\t}\n\nTAny* CRenderTarget::ResolveObjectInterface',
        '#endif\n\tHtcleoDsprLog(0x00001516u, KErrNone, 0u);\n\t}\n\n'
        'TAny* CRenderTarget::ResolveObjectInterface',
        "render target ConstructL return",
    )
    return source


def patch_display_policy(source: str) -> str:
    if "0x00001705u" in source:
        return source
    source = replace_once(source, '#include "panic.h"\n', '#include "panic.h"\n' + declaration(), "display policy declaration")
    source = replace_once(
        source,
        '\t{\n\tCDisplayPolicy* self = new (ELeave)CDisplayPolicy();\n\tCleanupStack::PushL(self);\n\tself->ConstructL(aEnv,aScreen,aScreenNumber);\n\treturn self;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001700u, KErrNone, (TUint32)aScreenNumber);\n'
        '\tCDisplayPolicy* self = new (ELeave)CDisplayPolicy();\n'
        '\tHtcleoDsprLog(0x00001701u, KErrNone, (TUint32)(self != NULL));\n'
        '\tCleanupStack::PushL(self);\n'
        '\tself->ConstructL(aEnv,aScreen,aScreenNumber);\n'
        '\tHtcleoDsprLog(0x00001702u, KErrNone, 0u);\n'
        '\treturn self;\n\t}\n',
        "display policy NewLC",
    )
    source = replace_once(
        source,
        '\t{\n\tiScreenIniFile=aEnv->ObjectInterface<MWsIniFile>();\n\tif (iScreenIniFile)',
        '\t{\n\tHtcleoDsprLog(0x00001703u, KErrNone, (TUint32)aScreenNumber);\n'
        '\tiScreenIniFile=aEnv->ObjectInterface<MWsIniFile>();\n'
        '\tHtcleoDsprLog(0x00001704u, KErrNone, (TUint32)(iScreenIniFile != NULL));\n'
        '\tif (iScreenIniFile)',
        "display policy ConstructL entry",
    )
    source = replace_once(
        source,
        '\tiScreen=aScreen;\n\t}\n\nvoid CDisplayPolicy::NewAppModesAvailable',
        '\tiScreen=aScreen;\n'
        '\tHtcleoDsprLog(0x00001705u, KErrNone, (TUint32)iUiScaling);\n'
        '\t}\n\nvoid CDisplayPolicy::NewAppModesAvailable',
        "display policy ConstructL return",
    )
    return source


def patch_fb_factory(source: str) -> str:
    if "0x00001805u" in source:
        return source
    source = replace_once(source, '#include "panic.h"\n', '#include "panic.h"\n' + declaration(), "flicker factory declaration")
    source = replace_once(
        source,
        'CFbRenderStageFactory* CFbRenderStageFactory::CreateL()\n\t{\n\treturn new(ELeave) CFbRenderStageFactory;\n\t}\n',
        'CFbRenderStageFactory* CFbRenderStageFactory::CreateL()\n\t{\n'
        '\tHtcleoDsprLog(0x00001800u, KErrNone, 0u);\n'
        '\tCFbRenderStageFactory* factory = new(ELeave) CFbRenderStageFactory;\n'
        '\tHtcleoDsprLog(0x00001801u, KErrNone, (TUint32)(factory != NULL));\n'
        '\treturn factory;\n\t}\n',
        "flicker factory CreateL",
    )
    source = replace_once(
        source,
        '\t{\n\tBaseConstructL(aEnv);\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001802u, KErrNone, 0u);\n'
        '\tBaseConstructL(aEnv);\n'
        '\tHtcleoDsprLog(0x00001803u, KErrNone, 0u);\n\t}\n',
        "flicker factory ConstructL",
    )
    source = replace_once(
        source,
        '\t{\n\tCFbRenderStage* stage = CFbRenderStage::NewL(&Env(), aScreen, aScreenRedraw, aNextStage);\n\treturn stage;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001804u, KErrNone, (TUint32)(aNextStage != NULL));\n'
        '\tCFbRenderStage* stage = CFbRenderStage::NewL(&Env(), aScreen, aScreenRedraw, aNextStage);\n'
        '\tHtcleoDsprLog(0x00001805u, KErrNone, (TUint32)(stage != NULL));\n'
        '\treturn stage;\n\t}\n',
        "flicker factory stage",
    )
    return source


def patch_fb_stage(source: str) -> str:
    if "0x00001828u" in source:
        return source
    source = replace_once(source, '#include <graphics/sgutils.h>\n', '#include <graphics/sgutils.h>\n' + declaration(), "flicker stage declaration")
    source = replace_once(
        source,
        '\t{\n\tCFbRenderStage* stage = new(ELeave) CFbRenderStage;\n\tCleanupStack::PushL(stage);\n\tstage->ConstructL(aEnv, aScreen, aScreenRedraw, aNextStage);\n\tCleanupStack::Pop(stage);\n\treturn stage;\n\t}\n',
        '\t{\n\tHtcleoDsprLog(0x00001810u, KErrNone, (TUint32)(aNextStage != NULL));\n'
        '\tCFbRenderStage* stage = new(ELeave) CFbRenderStage;\n'
        '\tHtcleoDsprLog(0x00001811u, KErrNone, (TUint32)(stage != NULL));\n'
        '\tCleanupStack::PushL(stage);\n'
        '\tstage->ConstructL(aEnv, aScreen, aScreenRedraw, aNextStage);\n'
        '\tHtcleoDsprLog(0x00001812u, KErrNone, 0u);\n'
        '\tCleanupStack::Pop(stage);\n'
        '\tHtcleoDsprLog(0x00001813u, KErrNone, (TUint32)(stage != NULL));\n'
        '\treturn stage;\n\t}\n',
        "flicker stage NewL",
    )
    source = replace_once(
        source,
        '\t{\n\tBaseConstructL();\n\tiNextScreenDevice = aNextStage->ObjectInterface<MWsScreenDevice>();',
        '\t{\n\tHtcleoDsprLog(0x00001820u, KErrNone, (TUint32)(aNextStage != NULL));\n'
        '\tBaseConstructL();\n'
        '\tHtcleoDsprLog(0x00001821u, KErrNone, 0u);\n'
        '\tiNextScreenDevice = aNextStage->ObjectInterface<MWsScreenDevice>();',
        "flicker ConstructL entry",
    )
    source = replace_once(
        source,
        '\tMWsIniFile* iniFile = aEnv->ObjectInterface<MWsIniFile>();\n\tSTD_ASSERT_ALWAYS(iniFile, EPluginPanicIniFileMissing);',
        '\tMWsIniFile* iniFile = aEnv->ObjectInterface<MWsIniFile>();\n'
        '\tHtcleoDsprLog(0x00001822u, KErrNone,\n'
        '\t\t((TUint32)(iNextScreenDevice != NULL) << 2) |\n'
        '\t\t((TUint32)(iNextScene != NULL) << 1) | (TUint32)(iniFile != NULL));\n'
        '\tSTD_ASSERT_ALWAYS(iniFile, EPluginPanicIniFileMissing);',
        "flicker interfaces",
    )
    source = replace_once(
        source,
        '\tSTD_ASSERT_DEBUG(displayMode!=ENone, EPluginPanicNoDisplayModeFound);\n\t\n\tconst TUint32 usage',
        '\tSTD_ASSERT_DEBUG(displayMode!=ENone, EPluginPanicNoDisplayModeFound);\n'
        '\tHtcleoDsprLog(0x00001823u, (TInt)displayMode, (TUint32)(iDisplayControl != NULL));\n\t\n'
        '\tconst TUint32 usage',
        "flicker display mode",
    )
    source = replace_once(
        source,
        '\tiRenderTarget = CRenderTarget::NewL(iniFile, usage, cpuAccess, displayMode, size, iNextScreenDevice->ScreenNumber());\n\t\n\t//initialize drawable sources',
        '\tHtcleoDsprLog(0x00001824u, KErrNone, (TUint32)iNextScreenDevice->ScreenNumber());\n'
        '\tiRenderTarget = CRenderTarget::NewL(iniFile, usage, cpuAccess, displayMode, size, iNextScreenDevice->ScreenNumber());\n'
        '\tHtcleoDsprLog(0x00001825u, KErrNone, (TUint32)(iRenderTarget != NULL));\n\t\n'
        '\t//initialize drawable sources',
        "flicker render target",
    )
    source = replace_once(
        source,
        '\t\t}\n\t\n\tiController = CRenderStageController::NewL(this);',
        '\t\t}\n'
        '\tHtcleoDsprLog(0x00001826u, KErrNone, (TUint32)CRenderTarget::EAspectRatioCount);\n\t\n'
        '\tiController = CRenderStageController::NewL(this);\n'
        '\tHtcleoDsprLog(0x00001827u, KErrNone, (TUint32)(iController != NULL));',
        "flicker drawable sources",
    )
    source = replace_once(
        source,
        '\tSetNext(aNextStage);\n\t}\n\t\nCFbRenderStage::CFbRenderStage()',
        '\tSetNext(aNextStage);\n'
        '\tHtcleoDsprLog(0x00001828u, KErrNone, (TUint32)(iUpdateRegion != NULL));\n'
        '\t}\n\t\nCFbRenderStage::CFbRenderStage()',
        "flicker ConstructL return",
    )
    return source


def verify(files: dict[str, str], mmp: str) -> None:
    combined = "".join(files.values())
    required = (
        0x1000, 0x1001, 0x1010, 0x1011, 0x1020, 0x1021, 0x1030, 0x1031,
        0x1100, 0x1101, 0x1102, 0x1103, 0x1104,
        *range(0x1200, 0x1213),
        0x1300, 0x1301, 0x1302, 0x1303, 0x1304, *range(0x1310, 0x1321),
        0x1500, 0x1501, 0x1502, 0x1503, 0x1504, *range(0x1510, 0x1517),
        0x1600, 0x1601, 0x1602, 0x1603, 0x1610, 0x1611, 0x1612, 0x1613, 0x1614,
        0x1700, 0x1701, 0x1702, 0x1703, 0x1704, 0x1705,
        0x1800, 0x1801, 0x1802, 0x1803, 0x1804, 0x1805,
        0x1810, 0x1811, 0x1812, 0x1813,
        0x1820, 0x1821, 0x1822, 0x1823, 0x1824, 0x1825, 0x1826, 0x1827, 0x1828,
    )
    bad_sites = []
    for stage in required:
        actual = combined.count(f"0x{stage:08X}u")
        expected = 2 if stage == 0x1000 else 1
        if actual != expected:
            bad_sites.append(f"0x{stage:08X}u:{actual}/{expected}")
    checks = {
        "marker": files["stdplugin.cpp"].count(MARKER) == 1,
        "single writer": combined.count("C:\\\\Symbian3\\\\DSPRLOG.TXT") == 1,
        "fixed prefix": combined.count("HTCLEO_DSP ") == 1,
        "write and flush": files["stdplugin.cpp"].count("file.Write(record)") == 1
        and files["stdplugin.cpp"].count("file.Flush()") == 1,
        "no writable logger global": "gHtcleoDspr" not in combined,
        "target macro": mmp.count(f"macro {MACRO}") == 1,
        "efsrv import": mmp.count("LIBRARY     efsrv.lib") == 1,
        "required sites" + ("[" + ",".join(bad_sites) + "]" if bad_sites else ""):
            not bad_sites,
        "fatal no-device site": combined.count("0xE0001315u") == 1,
        "no added delay": "User::After" not in combined,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("display durable-log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    component = args.root / "sf/os/graphics/windowing/windowserverplugins/openwfc"
    paths = {
        "stdplugin.cpp": component / "src/stdplugin.cpp",
        "displayrenderstagefactory.cpp": component / "src/displayrenderstagefactory.cpp",
        "displayrenderstage.cpp": component / "src/displayrenderstage.cpp",
        "openwfcwrapper.cpp": component / "src/openwfcwrapper.cpp",
        "rendertarget.cpp": component / "src/rendertarget.cpp",
        "displaypolicy.cpp": component / "src/displaypolicy.cpp",
        "fbrenderstagefactory.cpp": component / "src/fbrenderstagefactory.cpp",
        "fbrenderstage.cpp": component / "src/fbrenderstage.cpp",
    }
    mmp_path = component / "group/stdplugin.mmp"
    for path in (*paths.values(), mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing display render-stage source: {path}")

    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    files["stdplugin.cpp"] = patch_plugin(files["stdplugin.cpp"])
    files["displayrenderstagefactory.cpp"] = patch_display_factory(files["displayrenderstagefactory.cpp"])
    files["displayrenderstage.cpp"] = patch_display_stage(files["displayrenderstage.cpp"])
    files["openwfcwrapper.cpp"] = patch_openwfc(files["openwfcwrapper.cpp"])
    files["rendertarget.cpp"] = patch_render_target(files["rendertarget.cpp"])
    files["displaypolicy.cpp"] = patch_display_policy(files["displaypolicy.cpp"])
    files["fbrenderstagefactory.cpp"] = patch_fb_factory(files["fbrenderstagefactory.cpp"])
    files["fbrenderstage.cpp"] = patch_fb_stage(files["fbrenderstage.cpp"])

    mmp = mmp_path.read_text(encoding="utf-8")
    if f"macro {MACRO}" not in mmp:
        mmp = replace_once(
            mmp,
            "macro SYMBIAN_GRAPHICS_GCE\n",
            f"macro SYMBIAN_GRAPHICS_GCE\nmacro {MACRO}\n",
            "display target macro",
        )
    if "LIBRARY     efsrv.lib" not in mmp:
        mmp = replace_once(
            mmp,
            "LIBRARY     euser.lib\n",
            "LIBRARY     euser.lib\nLIBRARY     efsrv.lib\n",
            "display file-server import",
        )

    verify(files, mmp)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print("HTCLEO_DISPLAY_DURABLE_LOG=installed path=C:\\Symbian3\\DSPRLOG.TXT capacity=256")


if __name__ == "__main__":
    main()
