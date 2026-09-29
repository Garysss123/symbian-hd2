#!/usr/bin/env python3
"""Install fail-open durable tracing in the source-built OpenWFC engine.

Iteration 428 proved that ``wfcCreateOnScreenContext`` returns a null handle and
that the wrapper observes ``WFC_ERROR_OUT_OF_MEMORY``.  The public API maps every
internal context-construction failure to that one error, so this transform logs
the unmodified internal path to ``C:\\Symbian3\\WFCLOG.TXT``.
"""

from __future__ import annotations

import argparse
from pathlib import Path


MACRO = "__HTCLEO_WFC_CONTEXT_LOG__"
RGB565_OUTPUT_MACRO = "SUPPORT_565_OUTPUT"
MARKER = "HTCLEO_WFC_CONTEXT_DURABLE_LOG_V1"
TYPEDEF_COMPAT_MACRO = "__KHRONOS_TYPES_H__"
DISPCTX_COMPAT_MARKER = "HTCLEO_OWF_DISPCTX_TYPEDEF_COMPAT_V1"
STREAM_COMPAT_MARKER = "HTCLEO_WFC_NATIVE_STREAM_TYPEDEF_COMPAT_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


HEADER = r'''#ifndef HTCLEO_WFC_CONTEXT_LOG_H
#define HTCLEO_WFC_CONTEXT_LOG_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef __HTCLEO_WFC_CONTEXT_LOG__
void HtcleoWfcLog(unsigned int aStage, int aResult, unsigned int aDetail);
#else
#define HtcleoWfcLog(aStage, aResult, aDetail) ((void)0)
#endif

#ifdef __cplusplus
}
#endif

#endif
'''


LOGGER = r'''// HTCLEO_WFC_CONTEXT_DURABLE_LOG_V1
#include <e32base.h>
#include <f32file.h>
#include "htcleowfclog.h"

extern "C" void HtcleoWfcLog(unsigned int aStage, int aResult,
                              unsigned int aDetail)
    {
    RFs fs;
    TInt r = fs.Connect();
    if (r != KErrNone)
        return;

    _LIT(KHtcleoWfcLogDir, "C:\\Symbian3\\");
    _LIT(KHtcleoWfcLogPath, "C:\\Symbian3\\WFCLOG.TXT");
    r = fs.MkDirAll(KHtcleoWfcLogDir);
    if (r != KErrNone && r != KErrAlreadyExists)
        {
        fs.Close();
        return;
        }

    RFile file;
    TInt position = 0;
    if (aStage == 0x00002000u)
        r = file.Replace(fs, KHtcleoWfcLogPath, EFileWrite | EFileShareAny);
    else
        {
        r = file.Open(fs, KHtcleoWfcLogPath, EFileWrite | EFileShareAny);
        if (r == KErrNotFound || r == KErrPathNotFound)
            r = file.Replace(fs, KHtcleoWfcLogPath, EFileWrite | EFileShareAny);
        else if (r == KErrNone)
            r = file.Seek(ESeekEnd, position);
        }

    if (r == KErrNone && position < (256 * 42))
        {
        _LIT8(KHtcleoWfcPrefix, "HTCLEO_WFC ");
        TBuf8<64> record;
        record.Append(KHtcleoWfcPrefix);
        record.AppendNumFixedWidth((TUint)(position / 42), EHex, 2);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aStage, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aResult, EHex, 8);
        record.Append(' ');
        record.AppendNumFixedWidth((TUint32)aDetail, EHex, 8);
        record.Append(_L8("\r\n"));
        r = file.Write(record);
        if (r == KErrNone)
            (void)file.Flush();
        }
    file.Close();
    fs.Close();
    }
'''


def add_include(source: str, anchor: str, label: str) -> str:
    if '#include "htcleowfclog.h"' in source:
        return source
    return replace_once(source, anchor, anchor + '#include "htcleowfclog.h"\n', label)


def patch_context(source: str) -> str:
    if "0x00002033u" in source:
        return source
    source = add_include(source, '#include "wfcpipeline.h"\n', "context log include")
    source = replace_once(
        source,
        'static WFC_CONTEXT*\nWFC_Context_Initialize(WFC_CONTEXT* context,\n                       WFC_DEVICE* device,\n                       WFCNativeStreamType stream,\n                       WFCContextType type,\n                       WFCint screenNum)\n{\n    void*                   scratch[SCRATCH_BUFFER_COUNT];',
        'static WFC_CONTEXT*\nWFC_Context_Initialize(WFC_CONTEXT* context,\n                       WFC_DEVICE* device,\n                       WFCNativeStreamType stream,\n                       WFCContextType type,\n                       WFCint screenNum)\n{\n    HtcleoWfcLog(0x00002000u, (int)type, (unsigned int)screenNum);\n    void*                   scratch[SCRATCH_BUFFER_COUNT];',
        "context initialize entry",
    )
    source = replace_once(
        source,
        '    ++nextContextHandle;\n\n    context->displayContext = OWF_DisplayContext_Create(screenNum);',
        '    ++nextContextHandle;\n    HtcleoWfcLog(0x00002001u, (int)context->handle, (unsigned int)screenNum);\n\n'
        '    HtcleoWfcLog(0x00002002u, 0, (unsigned int)screenNum);\n'
        '    context->displayContext = OWF_DisplayContext_Create(screenNum);\n'
        '    HtcleoWfcLog(0x00002003u, (int)(context->displayContext != NULL), 0u);',
        "display context boundary",
    )
    source = replace_once(
        source,
        '    context->eglPrivateSignalSync = (TFPtrEglPrivateSignalSyncNok) eglGetProcAddress("egl_Private_SignalSyncNOK");\n    if (! context->eglPrivateSignalSync)',
        '    context->eglPrivateSignalSync = (TFPtrEglPrivateSignalSyncNok) eglGetProcAddress("egl_Private_SignalSyncNOK");\n'
        '    HtcleoWfcLog(0x00002004u, (int)(context->eglPrivateSignalSync != NULL), 0u);\n'
        '    if (! context->eglPrivateSignalSync)',
        "egl private signal",
    )
    source = replace_once(
        source,
        '        if (!OWF_Screen_GetHeader(screenNum, &screen))\n        {',
        '        HtcleoWfcLog(0x00002010u, 0, (unsigned int)screenNum);\n'
        '        WFCboolean htcleoHeaderOk = OWF_Screen_GetHeader(screenNum, &screen);\n'
        '        HtcleoWfcLog(0x00002011u, (int)htcleoHeaderOk,\n'
        '            ((unsigned int)screen.normal.width << 16) |\n'
        '            ((unsigned int)screen.normal.height & 0xffffu));\n'
        '        if (!htcleoHeaderOk)\n        {',
        "screen header boundary",
    )
    source = replace_once(
        source,
        '        stream = owfNativeStreamCreateImageStream(width,\n                                                  height,\n                                                  &imageFormat,\n                                                  1);\n\n        if (stream)',
        '        HtcleoWfcLog(0x00002012u, (int)normalSize,\n'
        '            ((unsigned int)width << 16) | ((unsigned int)height & 0xffffu));\n'
        '        HtcleoWfcLog(0x00002013u, (int)imageFormat.pixelFormat, 1u);\n'
        '        stream = owfNativeStreamCreateImageStream(width,\n'
        '                                                  height,\n'
        '                                                  &imageFormat,\n'
        '                                                  1);\n'
        '        HtcleoWfcLog(0x00002014u, (int)(stream != WFC_INVALID_HANDLE),\n'
        '            (unsigned int)stream);\n\n'
        '        if (stream)',
        "target stream boundary",
    )
    source = replace_once(
        source,
        '            owfNativeStreamRemoveReference(stream);\n        }',
        '            owfNativeStreamRemoveReference(stream);\n'
        '            HtcleoWfcLog(0x00002015u, 0,\n'
        '                ((unsigned int)context->targetWidth << 16) |\n'
        '                ((unsigned int)context->targetHeight & 0xffffu));\n'
        '        }',
        "target stream installed",
    )
    source = replace_once(
        source,
        '    nbufs = SCRATCH_BUFFER_COUNT-1;\n    for (ii = 0; ii < nbufs; ii++)\n    {\n        scratch[ii] = OWF_Image_AllocData(context->displayContext, MAX_SOURCE_WIDTH,\n                MAX_SOURCE_HEIGHT,\n                OWF_IMAGE_ARGB_INTERNAL);\n        fail = fail || (scratch[ii] == NULL);\n    }',
        '    nbufs = SCRATCH_BUFFER_COUNT-1;\n'
        '    HtcleoWfcLog(0x00002020u, (int)nbufs,\n'
        '        ((unsigned int)MAX_SOURCE_WIDTH << 16) | (unsigned int)MAX_SOURCE_HEIGHT);\n'
        '    for (ii = 0; ii < nbufs; ii++)\n    {\n'
        '        scratch[ii] = OWF_Image_AllocData(context->displayContext, MAX_SOURCE_WIDTH,\n'
        '                MAX_SOURCE_HEIGHT,\n'
        '                OWF_IMAGE_ARGB_INTERNAL);\n'
        '        HtcleoWfcLog(0x00002021u, (int)(scratch[ii] != NULL), (unsigned int)ii);\n'
        '        fail = fail || (scratch[ii] == NULL);\n    }',
        "scratch color buffers",
    )
    source = replace_once(
        source,
        '    scratch[nbufs] = OWF_Image_AllocData(context->displayContext, MAX_SOURCE_WIDTH,\n                                         MAX_SOURCE_HEIGHT,\n                                         OWF_IMAGE_L32);\n    fail = fail || (scratch[nbufs] == NULL);\n    \n    err2 = OWF_MessageQueue_Init(&context->composerQueue);\n    fail = fail || (err2 != 0);',
        '    scratch[nbufs] = OWF_Image_AllocData(context->displayContext, MAX_SOURCE_WIDTH,\n'
        '                                         MAX_SOURCE_HEIGHT,\n'
        '                                         OWF_IMAGE_L32);\n'
        '    HtcleoWfcLog(0x00002022u, (int)(scratch[nbufs] != NULL), (unsigned int)nbufs);\n'
        '    fail = fail || (scratch[nbufs] == NULL);\n    \n'
        '    err2 = OWF_MessageQueue_Init(&context->composerQueue);\n'
        '    HtcleoWfcLog(0x00002023u, (int)err2, (unsigned int)fail);\n'
        '    fail = fail || (err2 != 0);',
        "scratch alpha and queue",
    )
    source = replace_once(
        source,
        '    if (fail)\n    {\n        OWF_MessageQueue_Destroy(&context->composerQueue);',
        '    HtcleoWfcLog(0x00002024u, (int)fail, 0u);\n'
        '    if (fail)\n    {\n'
        '        OWF_MessageQueue_Destroy(&context->composerQueue);',
        "scratch failure summary",
    )
    source = replace_once(
        source,
        '    for (ii = 0; ii < SCRATCH_BUFFER_COUNT; ii++)\n    {\n        context->scratchBuffer[ii] = scratch[ii];\n    }\n\n    if (!WFC_Pipeline_CreateState(context) || !WFC_Context_CreateState(context))\n         {\n         DPRINT(("WFC_Context_Initialize(): Could not create pipeline state object"));\n         return NULL;\n         }',
        '    for (ii = 0; ii < SCRATCH_BUFFER_COUNT; ii++)\n    {\n'
        '        context->scratchBuffer[ii] = scratch[ii];\n    }\n'
        '    HtcleoWfcLog(0x00002025u, 0, (unsigned int)SCRATCH_BUFFER_COUNT);\n\n'
        '    WFCboolean htcleoPipelineOk = WFC_Pipeline_CreateState(context);\n'
        '    HtcleoWfcLog(0x00002026u, (int)htcleoPipelineOk, 0u);\n'
        '    if (!htcleoPipelineOk)\n'
        '         {\n'
        '         DPRINT(("WFC_Context_Initialize(): Could not create pipeline state object"));\n'
        '         return NULL;\n'
        '         }\n'
        '    WFCboolean htcleoContextStateOk = WFC_Context_CreateState(context);\n'
        '    HtcleoWfcLog(0x00002027u, (int)htcleoContextStateOk, 0u);\n'
        '    if (!htcleoContextStateOk)\n'
        '         {\n'
        '         DPRINT(("WFC_Context_Initialize(): Could not create context state object"));\n'
        '         return NULL;\n'
        '         }',
        "pipeline and context state",
    )
    source = replace_once(
        source,
        '    if (    OWF_Semaphore_Init(&context->compositionSemaphore, 1)\n        ||  OWF_Semaphore_Init(&context->commitSemaphore, 1)\n        ||  OWF_Mutex_Init(&context->updateFlagMutex)\n        ||  OWF_Mutex_Init(&context->sceneMutex)\n        \n        )\n        {\n        DPRINT(("WFC_Context_Initialize(): Could not create mutexes and semaphores!"));\n        return NULL;\n        }',
        '    OWFint htcleoSyncError = OWF_Semaphore_Init(&context->compositionSemaphore, 1);\n'
        '    HtcleoWfcLog(0x00002028u, (int)htcleoSyncError, 0u);\n'
        '    if (htcleoSyncError) return NULL;\n'
        '    htcleoSyncError = OWF_Semaphore_Init(&context->commitSemaphore, 1);\n'
        '    HtcleoWfcLog(0x00002029u, (int)htcleoSyncError, 0u);\n'
        '    if (htcleoSyncError) return NULL;\n'
        '    htcleoSyncError = OWF_Mutex_Init(&context->updateFlagMutex);\n'
        '    HtcleoWfcLog(0x0000202Au, (int)htcleoSyncError, 0u);\n'
        '    if (htcleoSyncError) return NULL;\n'
        '    htcleoSyncError = OWF_Mutex_Init(&context->sceneMutex);\n'
        '    HtcleoWfcLog(0x0000202Bu, (int)htcleoSyncError, 0u);\n'
        '    if (htcleoSyncError)\n'
        '        {\n'
        '        DPRINT(("WFC_Context_Initialize(): Could not create mutexes and semaphores!"));\n'
        '        return NULL;\n'
        '        }',
        "context synchronization objects",
    )
    source = replace_once(
        source,
        '    attribStatus= WFC_Context_InitializeAttributes(context, type);\n\n    if (attribStatus!=ATTR_ERROR_NONE)',
        '    attribStatus= WFC_Context_InitializeAttributes(context, type);\n'
        '    HtcleoWfcLog(0x0000202Cu, (int)attribStatus, 0u);\n\n'
        '    if (attribStatus!=ATTR_ERROR_NONE)',
        "context attributes",
    )
    source = replace_once(
        source,
        '    context->nodePool = OWF_Pool_Create(sizeof(OWF_NODE),\n                                        CONTEXT_NODE_POOL_SIZE);\n    if (!( context->scenePool &&',
        '    context->nodePool = OWF_Pool_Create(sizeof(OWF_NODE),\n'
        '                                        CONTEXT_NODE_POOL_SIZE);\n'
        '    HtcleoWfcLog(0x00002030u,\n'
        '        (int)(((context->scenePool != NULL) << 2) |\n'
        '              ((context->elementPool != NULL) << 1) |\n'
        '              (context->nodePool != NULL)),\n'
        '        (unsigned int)CONTEXT_ELEMENT_POOL_SIZE);\n'
        '    if (!( context->scenePool &&',
        "context pools",
    )
    source = replace_once(
        source,
        '    context->workScene = WFC_Scene_Create(context);\n    context->committedScene = WFC_Scene_Create(context);\n    context->snapshotScene = NULL;',
        '    context->workScene = WFC_Scene_Create(context);\n'
        '    context->committedScene = WFC_Scene_Create(context);\n'
        '    context->snapshotScene = NULL;\n'
        '    HtcleoWfcLog(0x00002031u,\n'
        '        (int)(((context->workScene != NULL) << 1) |\n'
        '              (context->committedScene != NULL)), 0u);',
        "context scenes",
    )
    source = replace_once(
        source,
        '    context->composerThread = OWF_Thread_Create(WFC_Context_ComposerThread,\n                                                context);\n    if (!(context->composerThread))',
        '    context->composerThread = OWF_Thread_Create(WFC_Context_ComposerThread,\n'
        '                                                context);\n'
        '    HtcleoWfcLog(0x00002032u, (int)(context->composerThread != NULL), 0u);\n'
        '    if (!(context->composerThread))',
        "composer thread",
    )
    source = replace_once(
        source,
        '    return context;\n}\n\n/*---------------------------------------------------------------------------\n *  Create new context on device',
        '    HtcleoWfcLog(0x00002033u, 0, (unsigned int)context->handle);\n'
        '    return context;\n}\n\n'
        '/*---------------------------------------------------------------------------\n *  Create new context on device',
        "context initialize return",
    )
    return source


def patch_display_context(source: str) -> str:
    if "0x00002105u" in source:
        return source
    source = add_include(source, '#include <graphics/symbianstream.h>\n', "display context log include")
    source = replace_once(
        source,
        'OWF_DISPCTX OWF_DisplayContext_Create(TInt screenNum)\n    {\n    TInt priorityTableSize',
        'OWF_DISPCTX OWF_DisplayContext_Create(TInt screenNum)\n    {\n'
        '    HtcleoWfcLog(0x00002100u, 0, (unsigned int)screenNum);\n'
        '    TInt priorityTableSize',
        "display context entry",
    )
    source = replace_once(
        source,
        '    OWFDisplayContext *pDispCtx = new OWFDisplayContext;\n    if (!pDispCtx)',
        '    OWFDisplayContext *pDispCtx = new OWFDisplayContext;\n'
        '    HtcleoWfcLog(0x00002101u, (int)(pDispCtx != NULL), 0u);\n'
        '    if (!pDispCtx)',
        "display context allocation",
    )
    source = replace_once(
        source,
        '        TInt err = SymbianStreamRegisterScreenNotifications(screenNum, priority, KInternalVersion);\n        if (!(err == KErrNone || err == KErrNotReady || err == KErrAlreadyExists))',
        '        TInt err = SymbianStreamRegisterScreenNotifications(screenNum, priority, KInternalVersion);\n'
        '        HtcleoWfcLog(0x00002102u, (int)err, (unsigned int)priority);\n'
        '        if (!(err == KErrNone || err == KErrNotReady || err == KErrAlreadyExists))',
        "stream notification registration",
    )
    source = replace_once(
        source,
        '        pDispCtx->iDisplayContext = COwfcDisplayDevice::SingletonInstance();\n        if (!pDispCtx->iDisplayContext)',
        '        pDispCtx->iDisplayContext = COwfcDisplayDevice::SingletonInstance();\n'
        '        HtcleoWfcLog(0x00002103u, (int)(pDispCtx->iDisplayContext != NULL), 0u);\n'
        '        if (!pDispCtx->iDisplayContext)',
        "display singleton",
    )
    source = replace_once(
        source,
        '        TInt err = pDispCtx->iDisplayContext->OpenScreen(screenNum);\n        if (err != KErrNone)',
        '        TInt err = pDispCtx->iDisplayContext->OpenScreen(screenNum);\n'
        '        HtcleoWfcLog(0x00002104u, (int)err, (unsigned int)screenNum);\n'
        '        if (err != KErrNone)',
        "display open screen",
    )
    source = replace_once(
        source,
        '    return static_cast<OWF_DISPCTX>(pDispCtx);\n    }',
        '    HtcleoWfcLog(0x00002105u, 0, (unsigned int)(pDispCtx != NULL));\n'
        '    return static_cast<OWF_DISPCTX>(pDispCtx);\n    }',
        "display context return",
    )
    return source


def patch_screen(source: str) -> str:
    if "0x00002233u" in source:
        return source
    source = add_include(source, '#include "owfdisplaycontext.h"\n', "screen log include")
    source = replace_once(
        source,
        'COwfcDisplayDevice* COwfcDisplayDevice::SingletonInstance()\n    {\n    if (!gDisplayDeviceInstancePtr)',
        'COwfcDisplayDevice* COwfcDisplayDevice::SingletonInstance()\n    {\n'
        '    HtcleoWfcLog(0x00002200u, 0, (unsigned int)(gDisplayDeviceInstancePtr != NULL));\n'
        '    if (!gDisplayDeviceInstancePtr)',
        "display singleton entry",
    )
    source = replace_once(
        source,
        '        TInt err = User::LoadLogicalDevice(KDisplayChannelLdd);\n        if (err != KErrNone && err != KErrAlreadyExists)',
        '        TInt err = User::LoadLogicalDevice(KDisplayChannelLdd);\n'
        '        HtcleoWfcLog(0x00002201u, (int)err, 0u);\n'
        '        if (err != KErrNone && err != KErrAlreadyExists)',
        "display ldd load",
    )
    source = replace_once(
        source,
        '        gDisplayDeviceInstancePtr = new COwfcDisplayDevice;\n        if (!gDisplayDeviceInstancePtr)',
        '        gDisplayDeviceInstancePtr = new COwfcDisplayDevice;\n'
        '        HtcleoWfcLog(0x00002202u, (int)(gDisplayDeviceInstancePtr != NULL), 0u);\n'
        '        if (!gDisplayDeviceInstancePtr)',
        "display singleton allocation",
    )
    source = replace_once(
        source,
        '    return gDisplayDeviceInstancePtr;\n    }',
        '    HtcleoWfcLog(0x00002203u, 0, (unsigned int)(gDisplayDeviceInstancePtr != NULL));\n'
        '    return gDisplayDeviceInstancePtr;\n    }',
        "display singleton return",
    )
    source = replace_once(
        source,
        'void COWFScreenDisplayInfo::ConstructL()\n    {\n    User::LeaveIfError(iDispChan.Open(iScreenNumber));',
        'void COWFScreenDisplayInfo::ConstructL()\n    {\n'
        '    HtcleoWfcLog(0x00002210u, 0, (unsigned int)iScreenNumber);\n'
        '    TInt htcleoOpenError = iDispChan.Open(iScreenNumber);\n'
        '    HtcleoWfcLog(0x00002211u, (int)htcleoOpenError, (unsigned int)iScreenNumber);\n'
        '    User::LeaveIfError(htcleoOpenError);',
        "display channel open",
    )
    source = replace_once(
        source,
        '    RDisplayChannel::TDisplayInfo info = pkgInfo();\n    switch(info.iPixelFormat)',
        '    RDisplayChannel::TDisplayInfo info = pkgInfo();\n'
        '    HtcleoWfcLog(0x00002212u, (int)info.iPixelFormat,\n'
        '        ((unsigned int)info.iNormal.iWidth << 16) |\n'
        '        ((unsigned int)info.iNormal.iHeight & 0xffffu));\n'
        '    HtcleoWfcLog(0x00002213u, (int)info.iNumCompositionBuffers,\n'
        '        (unsigned int)info.iBitsPerPixel);\n'
        '    switch(info.iPixelFormat)',
        "display channel info",
    )
    source = replace_once(
        source,
        '        User::LeaveIfError(iDispChan.GetCompositionBufferInfo(ii, address->iChunk, address->iOffset));\n        address->iAddress = address->iChunk.Base() + address->iOffset;',
        '        TInt htcleoBufferError = iDispChan.GetCompositionBufferInfo(ii, address->iChunk, address->iOffset);\n'
        '        HtcleoWfcLog(0x00002214u, (int)htcleoBufferError,\n'
        '            ((unsigned int)ii << 16) | ((unsigned int)address->iOffset & 0xffffu));\n'
        '        User::LeaveIfError(htcleoBufferError);\n'
        '        address->iAddress = address->iChunk.Base() + address->iOffset;',
        "composition buffer info",
    )
    source = replace_once(
        source,
        '        }\n    }\n\nCOWFScreenDisplayInfo* COWFScreenDisplayInfo::NewL',
        '        }\n'
        '    HtcleoWfcLog(0x00002215u, 0, (unsigned int)iCompositionBuffer.Count());\n'
        '    }\n\n'
        'COWFScreenDisplayInfo* COWFScreenDisplayInfo::NewL',
        "screen info construct return",
    )
    source = replace_once(
        source,
        'TInt COwfcDisplayDevice::OpenScreen(TInt aScreen)\n    {\n    if (!OWF_Screen_Valid(aScreen))',
        'TInt COwfcDisplayDevice::OpenScreen(TInt aScreen)\n    {\n'
        '    HtcleoWfcLog(0x00002220u, 0, (unsigned int)aScreen);\n'
        '    if (!OWF_Screen_Valid(aScreen))',
        "open screen entry",
    )
    source = replace_once(
        source,
        '    TRAP(err, info = COWFScreenDisplayInfo::NewL(aScreen));\n    if (err == KErrNone)',
        '    TRAP(err, info = COWFScreenDisplayInfo::NewL(aScreen));\n'
        '    HtcleoWfcLog(0x00002221u, (int)err, (unsigned int)(info != NULL));\n'
        '    if (err == KErrNone)',
        "screen info NewL",
    )
    source = replace_once(
        source,
        '        err = iScreenDisplayInfo.Append(info);\n        if (err != KErrNone)',
        '        err = iScreenDisplayInfo.Append(info);\n'
        '        HtcleoWfcLog(0x00002222u, (int)err,\n'
        '            (unsigned int)iScreenDisplayInfo.Count());\n'
        '        if (err != KErrNone)',
        "screen info append",
    )
    source = replace_once(
        source,
        '    return err;\n    }\n\nOWFboolean COWFScreenDisplayInfo::Blit',
        '    HtcleoWfcLog(0x00002223u, (int)err, (unsigned int)aScreen);\n'
        '    return err;\n    }\n\n'
        'OWFboolean COWFScreenDisplayInfo::Blit',
        "open screen return",
    )
    source = replace_once(
        source,
        'OWF_API_CALL OWFboolean OWF_Screen_GetHeader(OWFint screen, OWF_SCREEN* header)\n    {\n    COWFScreenDisplayInfo* info;\n    if (!GetDisplayInfo(screen, info))',
        'OWF_API_CALL OWFboolean OWF_Screen_GetHeader(OWFint screen, OWF_SCREEN* header)\n    {\n'
        '    HtcleoWfcLog(0x00002230u, 0, (unsigned int)screen);\n'
        '    COWFScreenDisplayInfo* info;\n'
        '    OWFboolean htcleoInfoOk = GetDisplayInfo(screen, info);\n'
        '    HtcleoWfcLog(0x00002231u, (int)htcleoInfoOk,\n'
        '        (unsigned int)(info != NULL));\n'
        '    if (!htcleoInfoOk)',
        "screen header entry",
    )
    source = replace_once(
        source,
        '    info->GetScreenInfo(header);\n    return OWF_TRUE;',
        '    info->GetScreenInfo(header);\n'
        '    HtcleoWfcLog(0x00002232u, 0,\n'
        '        ((unsigned int)header->normal.width << 16) |\n'
        '        ((unsigned int)header->normal.height & 0xffffu));\n'
        '    HtcleoWfcLog(0x00002233u, 0, (unsigned int)header->normal.stride);\n'
        '    return OWF_TRUE;',
        "screen header return",
    )
    return source


def patch_stream(source: str) -> str:
    if "0x00002316u" in source:
        return source
    source = add_include(source, '#include "owfnativestream.h"\n', "stream log include")
    source = replace_once(
        source,
        'static RSurfaceManager& SurfaceManagerSingleton()\n        {\n        static RSurfaceManager surfaceManager;\n        static int err=surfaceManager.Open();\n        return surfaceManager;',
        'static RSurfaceManager& SurfaceManagerSingleton()\n        {\n'
        '        static RSurfaceManager surfaceManager;\n'
        '        static int err=surfaceManager.Open();\n'
        '        HtcleoWfcLog(0x00002300u, err, 0u);\n'
        '        return surfaceManager;',
        "surface manager singleton",
    )
    source = replace_once(
        source,
        '        {\n        TSurfaceId surface = TSurfaceId::CreateNullId();\n        RSurfaceManager::TSurfaceCreationAttributesBuf bf;',
        '        {\n'
        '        HtcleoWfcLog(0x00002310u, (int)format->pixelFormat,\n'
        '            ((unsigned int)width << 16) | ((unsigned int)height & 0xffffu));\n'
        '        TSurfaceId surface = TSurfaceId::CreateNullId();\n'
        '        RSurfaceManager::TSurfaceCreationAttributesBuf bf;',
        "surface create entry",
    )
    source = replace_once(
        source,
        '        TInt err=SurfaceManagerSingleton().CreateSurface(bf, surface);\n        if (err<0)',
        '        HtcleoWfcLog(0x00002311u, (int)b.iStride,\n'
        '            ((unsigned int)b.iBuffers << 16) | (unsigned int)b.iPixelFormat);\n'
        '        TInt err=SurfaceManagerSingleton().CreateSurface(bf, surface);\n'
        '        HtcleoWfcLog(0x00002312u, (int)err, (unsigned int)!surface.IsNull());\n'
        '        if (err<0)',
        "surface manager CreateSurface",
    )
    source = replace_once(
        source,
        '        return surface;\n        }\n\nstatic void WipeWriteBuffer',
        '        HtcleoWfcLog(0x00002313u, 0, (unsigned int)!surface.IsNull());\n'
        '        return surface;\n        }\n\n'
        'static void WipeWriteBuffer',
        "surface create return",
    )
    source = replace_once(
        source,
        '        {\n        TSurfaceId surface;\n        \n        surface = createSurface(width, height, format, nbufs);',
        '        {\n'
        '        HtcleoWfcLog(0x00002314u, (int)nbufs,\n'
        '            ((unsigned int)width << 16) | ((unsigned int)height & 0xffffu));\n'
        '        TSurfaceId surface;\n        \n'
        '        surface = createSurface(width, height, format, nbufs);\n'
        '        HtcleoWfcLog(0x00002315u, 0, (unsigned int)!surface.IsNull());',
        "image stream surface",
    )
    source = replace_once(
        source,
        '        SymbianStreamType ns=NULL;  //No more error checking required...\n        SymbianStreamAcquire(&surface,&ns);\n        \n        SurfaceManagerSingleton().CloseSurface(surface);',
        '        SymbianStreamType ns=NULL;\n'
        '        TInt htcleoAcquireError = SymbianStreamAcquire(&surface,&ns);\n'
        '        HtcleoWfcLog(0x00002316u, (int)htcleoAcquireError,\n'
        '            (unsigned int)(ns != NULL));\n        \n'
        '        SurfaceManagerSingleton().CloseSurface(surface);',
        "symbian stream acquire",
    )
    return source


def patch_mmp(mmp: str) -> str:
    if f"MACRO {MACRO}" not in mmp:
        mmp = replace_once(
            mmp,
            '#include "openwfc.mmh"\n\nTARGET                 libWFC.dll',
            '#include "openwfc.mmh"\n\n'
            f'MACRO {MACRO}\n'
            'SOURCEPATH             ../composition/src\n'
            'SOURCE                 htcleowfclog.cpp\n'
            'LIBRARY                efsrv.lib\n\n'
            'TARGET                 libWFC.dll',
            "OpenWFC logging target",
        )
    if f"MACRO {TYPEDEF_COMPAT_MACRO}" not in mmp:
        mmp = replace_once(
            mmp,
            f"MACRO {MACRO}\n",
            f"MACRO {MACRO}\nMACRO {TYPEDEF_COMPAT_MACRO}\n",
            "GCCE Khronos typedef compatibility",
        )
    if "MACRO WFC_API_CALL=EXPORT_C" not in mmp:
        if "OPTION GCCE -fvisibility=default\n" in mmp:
            mmp = replace_once(
                mmp,
                "OPTION GCCE -fvisibility=default\n",
                "MACRO WFC_API_CALL=EXPORT_C\n",
                "GCCE OpenWFC API export declarations",
            )
        else:
            mmp = replace_once(
                mmp,
                f"MACRO {TYPEDEF_COMPAT_MACRO}\n",
                f"MACRO {TYPEDEF_COMPAT_MACRO}\n"
                "MACRO WFC_API_CALL=EXPORT_C\n",
                "GCCE OpenWFC API export declarations",
            )
    if f"MACRO {RGB565_OUTPUT_MACRO}" not in mmp:
        mmp = replace_once(
            mmp,
            "MACRO WFC_API_CALL=EXPORT_C\n",
            "MACRO WFC_API_CALL=EXPORT_C\n"
            f"MACRO {RGB565_OUTPUT_MACRO}\n",
            "HTCLEO RGB565 display-output compatibility",
        )
    return mmp


def patch_dispctx_typedef(header: str, label: str) -> str:
    if DISPCTX_COMPAT_MARKER in header:
        return header
    return replace_once(
        header,
        "typedef void*   OWF_DISPCTX;",
        f"/* {DISPCTX_COMPAT_MARKER} */\n"
        "#ifndef __HTCLEO_OWF_DISPCTX_DEFINED__\n"
        "#define __HTCLEO_OWF_DISPCTX_DEFINED__\n"
        "typedef void*   OWF_DISPCTX;\n"
        "#endif",
        label,
    )


def patch_stream_typedef(header: str) -> str:
    if STREAM_COMPAT_MARKER in header:
        return header
    return replace_once(
        header,
        "typedef WFCHandle           WFCNativeStreamType;",
        f"/* {STREAM_COMPAT_MARKER} */\n"
        "#ifndef _WFCPLATFORM_H_\n"
        "typedef WFCHandle           WFCNativeStreamType;\n"
        "#endif",
        "native stream public typedef compatibility",
    )


def verify(
    files: dict[str, str],
    compat_files: dict[str, str],
    mmp: str,
    header: str,
    logger: str,
) -> None:
    combined = "\n".join(files.values())
    required = [
        "00002000", "00002033", "00002100", "00002105",
        "00002200", "00002233", "00002300", "00002316",
    ]
    missing = [stage for stage in required if f"0x{stage}u" not in combined]
    checks = {
        "target macro": mmp.count(f"MACRO {MACRO}") == 1,
        "Khronos typedef guard macro":
            mmp.count(f"MACRO {TYPEDEF_COMPAT_MACRO}") == 1,
        "GCCE API export declarations":
            mmp.count("MACRO WFC_API_CALL=EXPORT_C") == 1,
        "RGB565 display output":
            mmp.count(f"MACRO {RGB565_OUTPUT_MACRO}") == 1,
        "no ineffective visibility option":
            "OPTION GCCE -fvisibility=default" not in mmp,
        "logger source": mmp.count("SOURCE                 htcleowfclog.cpp") == 1,
        "efsrv import": mmp.count("LIBRARY                efsrv.lib") == 1,
        "single writer marker": logger.count(MARKER) == 1,
        "single path": logger.count("WFCLOG.TXT") == 1,
        "fixed capacity": "position < (256 * 42)" in logger,
        "C linkage": 'extern "C" void HtcleoWfcLog' in logger,
        "header macro": MACRO in header,
        "required stages" + ("[" + ",".join(missing) + "]" if missing else ""):
            not missing,
        "display-context typedef guards":
            sum(text.count(DISPCTX_COMPAT_MARKER)
                for text in compat_files.values()) == 2,
        "native-stream typedef guard":
            sum(text.count(STREAM_COMPAT_MARKER)
                for text in compat_files.values()) == 1,
        "no delay": "User::After" not in combined and "User::After" not in logger,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit("OpenWFC durable-log verification failed: " + ", ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="full PDK EPOCROOT")
    args = parser.parse_args()
    component = args.root / "sf/os/graphics/graphicscomposition/openwfcompositionengine"
    paths = {
        "wfccontext.c": component / "composition/src/wfccontext.c",
        "owfdisplaycontext.cpp": component / "adaptation/src/Platform/Graphics/symbian/owfdisplaycontext.cpp",
        "owfscreen_displaychannel.cpp": component / "adaptation/src/Platform/Graphics/symbian/owfscreen_displaychannel.cpp",
        "owfnativestreamstub.cpp": component / "adaptation/src/Platform/Graphics/symbian/owfnativestreamstub.cpp",
    }
    compat_paths = {
        "owfimage.h": component / "common/include/owfimage.h",
        "owfdisplaycontextgeneral.h":
            component / "adaptation/include/owfdisplaycontextgeneral.h",
        "owfnativestream.h": component / "adaptation/include/owfnativestream.h",
    }
    header_path = component / "composition/include/htcleowfclog.h"
    logger_path = component / "composition/src/htcleowfclog.cpp"
    mmp_path = component / "group/openwfc.mmp"
    for path in (*paths.values(), *compat_paths.values(), mmp_path):
        if not path.is_file():
            raise SystemExit(f"missing OpenWFC source: {path}")

    files = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    files["wfccontext.c"] = patch_context(files["wfccontext.c"])
    files["owfdisplaycontext.cpp"] = patch_display_context(files["owfdisplaycontext.cpp"])
    files["owfscreen_displaychannel.cpp"] = patch_screen(files["owfscreen_displaychannel.cpp"])
    files["owfnativestreamstub.cpp"] = patch_stream(files["owfnativestreamstub.cpp"])
    compat_files = {
        name: path.read_text(encoding="utf-8")
        for name, path in compat_paths.items()
    }
    compat_files["owfimage.h"] = patch_dispctx_typedef(
        compat_files["owfimage.h"], "common image display-context typedef"
    )
    compat_files["owfdisplaycontextgeneral.h"] = patch_dispctx_typedef(
        compat_files["owfdisplaycontextgeneral.h"],
        "adaptation display-context typedef",
    )
    compat_files["owfnativestream.h"] = patch_stream_typedef(
        compat_files["owfnativestream.h"]
    )
    mmp = patch_mmp(mmp_path.read_text(encoding="utf-8"))

    verify(files, compat_files, mmp, HEADER, LOGGER)
    for name, path in paths.items():
        path.write_text(files[name], encoding="utf-8")
    for name, path in compat_paths.items():
        path.write_text(compat_files[name], encoding="utf-8")
    header_path.write_text(HEADER, encoding="utf-8")
    logger_path.write_text(LOGGER, encoding="utf-8")
    mmp_path.write_text(mmp, encoding="utf-8")
    print("HTCLEO_OPENWFC_CONTEXT_LOG=installed path=C:\\Symbian3\\WFCLOG.TXT capacity=256")


if __name__ == "__main__":
    main()
