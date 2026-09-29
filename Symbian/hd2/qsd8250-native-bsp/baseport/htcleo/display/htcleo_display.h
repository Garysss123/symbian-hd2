/*
* Copyright (c) 2009 Nokia Corporation and/or its subsidiary(-ies).
* All rights reserved.
* This component and the accompanying materials are made available
* under the terms of the License "Eclipse Public License v1.0"
* which accompanies this distribution, and is available
* at the URL "http://www.eclipse.org/legal/epl-v10.html".
*
* Initial Contributors:
* Nokia Corporation - initial contribution.
*
* Contributors:
*
* Accenture Ltd - Htcleo framebuffer improvements, now auto determines frame size from board model, performance and memory improvements
*
* Description: Minimalistic frame buffer driver
*
*/

#ifndef _HTCLEO_DISPLAY_H
#define _HTCLEO_DISPLAY_H

#include <display.h>

#include <videodriver.h>
#include <system.h>

/* Keep early display code silent; UART is intentionally not initialised. */
//#define __HTCLEO_DISPLAY_DEBUG

#ifdef __HTCLEO_DISPLAY_DEBUG

#define  __GCE_DEBUG_PRINT(a) 		Kern::Printf(a)
#define  __GCE_DEBUG_PRINT2(a,b) 	Kern::Printf(a,b)

#else

#define  __GCE_DEBUG_PRINT(a)
#define  __GCE_DEBUG_PRINT2(a,b)

#endif

// Macro to calculate the screen buffer size
// aBpp is the number of bits-per-pixel, aPpl is the number of pixels per line and aLpp number of lines per panel
#define FRAME_BUFFER_SIZE(aBpp,aPpl,aLpp)	((aBpp/8)*aPpl*aLpp)	

_LIT(KLitLcd,"HTCLEO_FB");


const TInt	KConfigLcdWidthInTwips     = 1996;
const TInt	KConfigLcdHeightInTwips    = 3550;

const TBool KConfigIsMono              = 0;
const TBool KConfigIsPalettized        = 0;
const TInt  KCOnfigOffsetToFirstPixel  = 0;
const TBool KConfigPixelOrderRGB       = 1;
const TBool KConfigPixelOrderLandscape = 0;
const TInt  KConfigLcdDisplayMode      = 0;

const TInt KConfigOffsetToFirstPixel =0;

const TInt  KConfigLcdNumberOfDisplayModes = 1;


const TInt  KConfigBitsPerPixel        = 16;


const TInt   KVSyncDfcPriority							= 7 ;   //priority of DFC within the queue (0 to 7, where 7 is highest)

/********************************************************************/
/* Class Definition                                                 */
/********************************************************************/
/**
 * This class defines a callback mechanism that is used by a resource user to specify its callback. It contains a
 * function pointer and data pointer. The function pointer specifies the user callback function to be invoked by the
 * resource while the data pointer specifies the data to be passed to the callback function.
 */
class TLcdUserCallBack
    {
public:
    // The constructor for the callback mechanism.
    TLcdUserCallBack(TInt (*aFunction)(TUint aResID, TAny* aPtr), TAny* aPtr)

        {
        iCbFn = aFunction;
        iDataPtr = aPtr;
        }

public:
    // The callback function pointer.
    TInt (*iCbFn)(TUint aResID, TAny* aPtr);

    // Pointer to the data structure to be passed to the callback function.
    TAny *iDataPtr;
    };

class DLcdPowerHandler : public DPowerHandler
{
public: // from DPowerHandler
  void PowerDown(TPowerState);
  void PowerUp();
public:	// to prevent a race condition with WServer trying to power up/down at the same time
  void PowerUpDfc();
  void PowerDownDfc();
public:
  DLcdPowerHandler();
  TInt Create();
  void DisplayOn();
  void DisplayOff();
  TInt HalFunction(TInt aFunction, TAny* a1, TAny* a2);

  void PowerUpLcd(TBool aSecure);
  void PowerDownLcd();

  void ScreenInfo(TScreenInfoV01& aInfo);
  void WsSwitchOnScreen();
  void WsSwitchOffScreen();
  void HandleMsg(TMessageBase* aMsg);
  void SwitchDisplay(TBool aSecure);

private:
  TInt GetCurrentDisplayModeInfo(TVideoInfoV01& aInfo, TBool aSecure);
  TInt GetSpecifiedDisplayModeInfo(TInt aMode, TVideoInfoV01& aInfo);
  TInt SetDisplayMode(TInt aMode);
  TInt AllocateFrameBuffer();

public:
    IMPORT_C static    TInt    RegisterCallback(TLcdUserCallBack* aCbPtr);
    IMPORT_C static    void    DeRegisterCallback(TLcdUserCallBack* aCbPtr);
  
private:
  TBool iDisplayOn;
  DPlatChunkHw* iChunk;
  DPlatChunkHw* iSecureChunk;
  TBool iWsSwitchOnScreen;
  TBool iSecureDisplay;

public:
  TDfcQue* iDfcQ;
  TMessageQue iMsgQ;					// to prevent a race condition with Power Manager trying to power up/down at the same time
  TDfc iPowerUpDfc;
  TDfc iPowerDownDfc;	

private:
  NFastMutex iLock;
  TPhysAddr ivRamPhys;
  TPhysAddr iSecurevRamPhys;
  TLcdUserCallBack * iAppCallBk[2];

public:
  TVideoInfoV01 iVideoInfo;
  TVideoInfoV01 iSecureVideoInfo;
  TInt			iSize;
  TLinAddr iPortAddr;
  TPhysAddr		iCompositionPhysical;
  static   DLcdPowerHandler 	* pLcd;

enum {
    FB_ID               = 0,
    FB_BASE             = 1,
    FB_HEIGHT           = 2,
    FB_WIDTH            = 3,
    FB_ORIENTATION      = 4,
    FB_BLANK            = 5,
    FB_INT_MASK         = 6,
    /* begin new interface */
    FB_INTERRUPT_CAUSE  = 7,
    FB_BPP              = 8,
    FB_COLOR_ORDER      = 9,
    FB_BYTE_ORDER       = 10,
    FB_PIXEL_ORDER      = 11,
    FB_ROW_PITCH        = 12,
    FB_ENABLED          = 13,
    FB_PALETTE_START    = 0x400 >> 2,
    FB_PALETTE_END   = FB_PALETTE_START+256-1,
    /* end new interface */
    };

#define FB_INT_VSYNC            (1U << 0)
#define FB_INT_BASE_UPDATE_DONE (1U << 1)

};

class DDisplayPddHtcleo : public DDisplayPdd
	{

	public:
	DDisplayPddHtcleo();
	~DDisplayPddHtcleo();
    
  	/**  
    Called by the LDD to handle the device specific part of switching to Legacy mode.
 
	@return KErrNone if successful; or one of the other system wide error codes.
    */    
    virtual TInt  SetLegacyMode();
        
     /**
     Called by the LDD to handle the device specific part of switching to GCE mode.
     
     @return KErrNone if successful; or one of the other system wide error codes.
     */       
    virtual TInt  SetGceMode();
    
     /**
     Called by the LDD to handle the device specific part of setting the rotation.
     
     @return KErrNone if successful; or one of the other system wide error codes.
     */       
	virtual TInt  SetRotation(RDisplayChannel::TDisplayRotation aRotation);

     /**
     Called by the LDD to handle the device specific part of posting a User Buffer.
     
     @return KErrNone if successful; or one of the other system wide error codes.
     */ 	
	virtual TInt  PostUserBuffer(TBufferNode* aNode);
	
     /**
     Called by the LDD to handle the device specific part of posting a Composition Buffer
     
     @return KErrNone if successful; or one of the other system wide error codes.
     */ 		
	virtual TInt  PostCompositionBuffer(TBufferNode* aNode);
        
     /**
     Called by the LDD to handle the device specific part of posting the Legacy Buffuer
     
     @return KErrNone if successful; or one of the other system wide error codes.
     */   
    virtual TInt  PostLegacyBuffer();
    
    /**
     Called by the LDD to handle device specific cleanup operations when a channel is closed.
          
     @return KErrNone if successful; or one of the other system wide error codes.
     */  
    virtual TInt  CloseMsg();
            
     /**
     Called by the LDD to handle device specific initialisation tasks when a channel is opened.
     
     @param aUnit The screen/hardware unit number.
     @return KErrNone if successful; or one of the other system wide error codes.
     */    
    virtual TInt  CreateChannelSetup(TInt aUnit);
          
     /**
     Called by the LDD in order to detect whether a post operation is pending. This type of 
     information is specific to the actual physical device.
     
     @return ETrue if a Post operation is pending otherwise EFalse.
     */       
   	virtual TBool  PostPending();
    
    /**
     Called by the LDD to retrieve the DFC Queue created in the PDD.      
     
     @param aUnit The screen/hardware unit number.
     @return A pointer to the TDfcQue object created in the PDD.
     */    
    virtual TDfcQue* DfcQ(TInt  aUnit);    
            
public:
	static void VSyncDfcFn(TAny* aChannel);

private:
	TDfcQue* 		iDfcQ;

    //generic  display info
	TVideoInfoV01    	iScreenInfo;

    //Pointer to a buffer in the Pending state
    TBufferNode*     	iPendingBuffer;

     //Pointer to a buffer in the Active state
    TBufferNode*     	iActiveBuffer;

    DChunk * 		 	iChunk;
    TLcdUserCallBack*   iLcdCallback;

 public:
	TDfc 		     	iVSyncDfc;
	};


/**
 PDD Factory class
 */

class DDisplayPddFactory : public DPhysicalDevice
	{
public:
	DDisplayPddFactory();

	virtual TInt Install();
	virtual void GetCaps(TDes8& aDes) const;
	virtual TInt Create(DBase*& aChannel, TInt aUnit, const TDesC8* aInfo, const TVersion& aVer);
	virtual TInt Validate(TInt aDeviceType, const TDesC8* anInfo, const TVersion& aVer);
	};

#endif
