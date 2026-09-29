/*
 * Shared, bounded QSD8x50 primitives for HTC Leo native drivers.
 *
 * These APIs deliberately expose only operations whose register/proc_comm
 * contracts are present in the checked-in HTC Leo Linux sources.  Every poll
 * is finite so an absent modem service or peripheral cannot hang EKA2 boot.
 */

#ifndef __HTCLEO_QSD8K_H__
#define __HTCLEO_QSD8K_H__

#include <e32def.h>
#include <e32err.h>

enum THtcleoGpioPull
    {
    EHtcleoNoPull = 0,
    EHtcleoPullDown = 1,
    EHtcleoKeeper = 2,
    EHtcleoPullUp = 3
    };

extern "C"
    {
    IMPORT_C TInt HtcleoProcComm(TUint32 aCommand,
                                 TUint32& aData1,
                                 TUint32& aData2);
    IMPORT_C TInt HtcleoTlmmConfigure(TUint32 aGpio,
                                     TUint32 aFunction,
                                     TBool aOutput,
                                     THtcleoGpioPull aPull,
                                     TUint32 aDrive);
    IMPORT_C TInt HtcleoGpioDirection(TUint32 aGpio,
                                     TBool aOutput,
                                     TBool aInitialValue);
    IMPORT_C TInt HtcleoGpioWrite(TUint32 aGpio, TBool aValue);
    IMPORT_C TInt HtcleoGpioRead(TUint32 aGpio, TBool& aValue);
    IMPORT_C TInt HtcleoI2cInitialise();
    IMPORT_C TInt HtcleoI2cWrite(TUint8 aAddress,
                                 const TUint8* aData,
                                 TInt aLength,
                                 TInt aAttempts,
                                 TUint32* aDiagnostic);
    IMPORT_C TInt HtcleoI2cRead(TUint8 aAddress,
                                TUint8* aData,
                                TInt aLength,
                                TInt aAttempts,
                                TUint32* aDiagnostic);
    IMPORT_C TInt HtcleoI2cWriteRead(TUint8 aAddress,
                                     const TUint8* aWrite,
                                     TInt aWriteLength,
                                     TUint8* aRead,
                                     TInt aReadLength);
    IMPORT_C TInt HtcleoClockSetRate(TUint32 aClockId, TUint32 aRateHz);
    IMPORT_C TInt HtcleoClockEnable(TUint32 aClockId, TBool aEnable);
    IMPORT_C TInt HtcleoDexCommand(TUint32 aCommand,
                                  TUint32* aData1,
                                  TUint32* aData2);
    IMPORT_C TInt HtcleoDexHeadsetAmplifier(TBool aEnable);
    }

#endif /* __HTCLEO_QSD8K_H__ */
